"""Whisper large-v3-turbo with its encoder on a DirectML GPU (native Windows only).

The ONNX export from onnx-community runs the encoder; everything around it is
done here, the way openai-whisper does it, but cut down to how vdistill runs
Whisper anyway (greedy, temperature 0, no fallback, no conditioning on earlier
text):

- every chunk is at most one 30 s window, cut at a pause by audio.split, so
  there is no long-form seeking between windows;
- features: log-mel, 128 bins, n_fft 400, hop 160, Slaney mel scale, the audio
  zero-padded to 30 s, as WhisperFeatureExtractor computes them;
- decoding: greedy with openai-whisper's timestamp rules, so each chunk comes
  back as timed segments;
- Silero VAD silences everything that isn't speech before Whisper hears it,
  as faster-whisper's vad_filter does, because Whisper invents words over
  music ("Muzika", "Závětlá" four times over a jingle). The audio is zeroed
  rather than cut out, so timestamps need no remapping; a chunk with no
  speech at all is skipped. Whisper can still invent lines in the silenced
  stretch at the start of a window ("Česká televize zrušena" three times over
  a jingle), so a segment that barely touches detected speech is dropped;
- a window is also dropped as silence when its no-speech probability is above
  0.6 and its average log-probability below -1, the test faster-whisper applies.

On an RX 580 the encoder takes ~1.2 s a window and one decoder step ~17 ms on
the CPU, so the GPU encodes the next windows while CPU threads decode the
ones before, several windows to a batch.
"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import numpy as np

from .config import SAMPLE_RATE

N_FFT, HOP, N_MELS = 400, 160, 128
WINDOW_SECONDS = 30
WINDOW_SAMPLES = WINDOW_SECONDS * SAMPLE_RATE
TIME_PRECISION = 0.02           # seconds per timestamp token
MAX_INITIAL_TIMESTAMP = 1.0     # the first timestamp may not be later than this
MAX_TOKENS = 448                # the decoder's context, prompt included
NO_SPEECH_THRESHOLD = 0.6
LOGPROB_THRESHOLD = -1.0

# Silero VAD, with faster-whisper's defaults.
VAD_FRAME, VAD_CONTEXT = 512, 64   # samples per step, and carried over from the last
VAD_THRESHOLD = 0.5                # speech starts above this ...
VAD_NEG_THRESHOLD = 0.35           # ... and ends below this
VAD_MIN_SPEECH = 0.25              # seconds; shorter bursts are noise
VAD_MIN_SILENCE = 2.0              # seconds; shorter gaps stay inside the speech
VAD_PAD = 0.4                      # seconds kept either side of speech
# A decoded segment must lie at least this much inside detected speech.
MIN_SPEECH_OVERLAP = 0.2


class WhisperDMLError(RuntimeError):
    pass


def _hz_to_mel(f):
    """Slaney mel scale: linear below 1 kHz, logarithmic above."""
    f = np.asarray(f, dtype=np.float64)
    f_sp, min_log_hz = 200.0 / 3, 1000.0
    min_log_mel, logstep = min_log_hz / f_sp, np.log(6.4) / 27.0
    return np.where(f >= min_log_hz,
                    min_log_mel + np.log(np.maximum(f, min_log_hz) / min_log_hz) / logstep,
                    f / f_sp)


def _mel_to_hz(m):
    m = np.asarray(m, dtype=np.float64)
    f_sp, min_log_hz = 200.0 / 3, 1000.0
    min_log_mel, logstep = min_log_hz / f_sp, np.log(6.4) / 27.0
    return np.where(m >= min_log_mel, min_log_hz * np.exp(logstep * (m - min_log_mel)), f_sp * m)


def mel_filters() -> np.ndarray:
    """(128, 201) Slaney-normalised triangular filters, as librosa and HF build them."""
    fft_freqs = np.linspace(0, SAMPLE_RATE / 2, 1 + N_FFT // 2)
    mel_f = _mel_to_hz(np.linspace(_hz_to_mel(0.0), _hz_to_mel(SAMPLE_RATE / 2), N_MELS + 2))
    fdiff = np.diff(mel_f)
    ramps = mel_f[:, None] - fft_freqs[None, :]
    lower = -ramps[:-2] / fdiff[:-1, None]
    upper = ramps[2:] / fdiff[1:, None]
    weights = np.maximum(0, np.minimum(lower, upper))
    weights *= (2.0 / (mel_f[2:] - mel_f[:-2]))[:, None]
    return weights


def log_mel(samples: np.ndarray, filters: np.ndarray) -> np.ndarray:
    """(128, 3000) features for one window; shorter audio is zero-padded to 30 s."""
    x = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    n = min(len(samples), WINDOW_SAMPLES)
    x[:n] = samples[:n]
    x = np.pad(x, N_FFT // 2, mode="reflect")
    window = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)  # periodic Hann
    frames = np.lib.stride_tricks.sliding_window_view(x, N_FFT)[::HOP]
    power = np.abs(np.fft.rfft(frames * window, axis=1)) ** 2
    mel = filters @ power.T
    log = np.log10(np.maximum(mel, 1e-10))[:, :-1]
    log = np.maximum(log, log.max() - 8.0)
    return ((log + 4.0) / 4.0).astype(np.float32)


def _byte_decoder() -> dict[str, int]:
    """Inverse of GPT-2's byte-to-printable-character map used by byte-level BPE."""
    bs = (list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1))
          + list(range(ord("®"), ord("ÿ") + 1)))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


class Tokenizer:
    def __init__(self, root: Path):
        data = json.loads((root / "tokenizer.json").read_text(encoding="utf-8"))
        self._pieces = {i: t for t, i in data["model"]["vocab"].items()}
        self.special = {a["content"]: a["id"] for a in data["added_tokens"]}
        self._bytes = _byte_decoder()
        self.eot = self.special["<|endoftext|>"]
        self.sot = self.special["<|startoftranscript|>"]
        self.transcribe = self.special["<|transcribe|>"]
        self.no_timestamps = self.special["<|notimestamps|>"]
        self.no_speech = self.special["<|nospeech|>"]
        self.timestamp_begin = self.special["<|0.00|>"]
        if self.timestamp_begin != self.no_timestamps + 1:
            raise WhisperDMLError("unexpected Whisper vocabulary layout")

    def decode(self, ids: list[int]) -> str:
        raw = bytearray()
        for i in ids:
            if i < self.eot:
                raw.extend(self._bytes[ch] for ch in self._pieces[i])
        return raw.decode("utf-8", errors="replace")


class SileroVad:
    def __init__(self, path: Path):
        import onnxruntime as ort

        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        self.session = ort.InferenceSession(str(path), so, providers=["CPUExecutionProvider"])

    def speech_probs(self, samples: np.ndarray) -> np.ndarray:
        """Probability of speech for each 512-sample (32 ms) frame."""
        frames = -(-len(samples) // VAD_FRAME)
        x = np.zeros(frames * VAD_FRAME, dtype=np.float32)
        x[:len(samples)] = samples
        state = np.zeros((2, 1, 128), dtype=np.float32)
        context = np.zeros((1, VAD_CONTEXT), dtype=np.float32)
        sr = np.array(SAMPLE_RATE, dtype=np.int64)
        probs = np.empty(frames, dtype=np.float32)
        for i in range(frames):
            chunk = np.concatenate([context, x[None, i * VAD_FRAME:(i + 1) * VAD_FRAME]], axis=1)
            out, state = self.session.run(None, {"input": chunk, "state": state, "sr": sr})
            probs[i] = out[0, 0]
            context = chunk[:, -VAD_CONTEXT:]
        return probs

    def speech_spans(self, samples: np.ndarray) -> list[tuple[float, float]]:
        """(start, end) seconds of speech, padded and merged across short gaps."""
        probs = self.speech_probs(samples)
        step = VAD_FRAME / SAMPLE_RATE
        spans, start = [], None
        for i, p in enumerate(probs):
            if start is None and p >= VAD_THRESHOLD:
                start = i
            elif start is not None and p < VAD_NEG_THRESHOLD:
                spans.append((start * step, i * step))
                start = None
        if start is not None:
            spans.append((start * step, len(probs) * step))
        spans = [s for s in spans if s[1] - s[0] >= VAD_MIN_SPEECH]
        merged: list[list[float]] = []
        for a, b in spans:
            if merged and a - merged[-1][1] < VAD_MIN_SILENCE:
                merged[-1][1] = b
            else:
                merged.append([a, b])
        total = len(samples) / SAMPLE_RATE
        return [(max(0.0, a - VAD_PAD), min(total, b + VAD_PAD)) for a, b in merged]


class Whisper:
    """Encoder on the DirectML GPU, CPU decoders working through batches."""

    def __init__(self, root: Path, workers: int = 2, threads_per_worker: int = 8,
                 batch_size: int = 8, vad: Path | None = None):
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise WhisperDMLError(
                "the whisper-dml backend needs onnxruntime-directml: "
                "pip install -e '.[directml]'"
            ) from exc
        if "DmlExecutionProvider" not in ort.get_available_providers():
            raise WhisperDMLError(
                "onnxruntime has no DirectML provider here; install "
                "onnxruntime-directml (not plain onnxruntime) on native Windows"
            )

        so = ort.SessionOptions()
        so.enable_mem_pattern = False  # DirectML requires both of these
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.log_severity_level = 3
        self.encoder = ort.InferenceSession(
            str(root / "onnx" / "encoder_model.onnx"), so, providers=["DmlExecutionProvider"]
        )
        if self.encoder.get_providers()[0] != "DmlExecutionProvider":
            raise WhisperDMLError("the encoder did not load on the DirectML GPU")

        # Several batches decode at once, each on its share of the cores.
        dec = ort.SessionOptions()
        dec.intra_op_num_threads = threads_per_worker
        dec.log_severity_level = 3
        self.decoder = ort.InferenceSession(
            str(root / "onnx" / "decoder_model_merged.onnx"), dec,
            providers=["CPUExecutionProvider"],
        )
        self._outputs = [o.name for o in self.decoder.get_outputs()]
        self._empty_past = {
            i.name: np.zeros((1, i.shape[1], 0, i.shape[3]), dtype=np.float32)
            for i in self.decoder.get_inputs() if i.name.startswith("past_key_values")
        }
        self.workers = workers
        self.batch_size = batch_size

        self.tok = Tokenizer(root)
        gen = json.loads((root / "generation_config.json").read_text(encoding="utf-8"))
        self.lang_to_id: dict[str, int] = gen["lang_to_id"]
        vocab = len(self.tok._pieces) + len(self.tok.special)
        self._suppress = np.zeros(vocab, dtype=bool)
        self._suppress[gen["suppress_tokens"]] = True
        # Every special token except end-of-text and the timestamps.
        self._suppress[self.tok.eot + 1:self.tok.timestamp_begin] = True
        self._begin_suppress = list(gen["begin_suppress_tokens"])
        self._filters = mel_filters()
        self.vad = SileroVad(vad) if vad else None

    # -- the model ---------------------------------------------------------

    def features(self, samples: np.ndarray):
        """Log-mel features with non-speech silenced, and the speech spans;
        None when there is no speech."""
        spans = [(0.0, len(samples) / SAMPLE_RATE)]
        if self.vad is not None:
            spans = self.vad.speech_spans(samples)
            if not spans:
                return None
            keep = np.zeros(len(samples), dtype=bool)
            for a, b in spans:
                keep[int(a * SAMPLE_RATE):int(b * SAMPLE_RATE)] = True
            samples = np.where(keep, samples, 0.0).astype(np.float32)
        return log_mel(samples, self._filters), spans

    def encode(self, mel: np.ndarray) -> np.ndarray:
        return self.encoder.run(None, {"input_features": mel[None]})[0]

    def _step(self, ids: np.ndarray, enc: np.ndarray, past: dict | None):
        """One decoder call for a batch: ids (batch, n), enc (batch, 1500, 1280)."""
        feeds = {
            "input_ids": ids.astype(np.int64),
            "encoder_hidden_states": enc,
            "use_cache_branch": np.array([past is not None]),
        }
        if past is None:
            feeds.update({k: np.repeat(v, len(ids), axis=0) for k, v in self._empty_past.items()})
        else:
            feeds.update(past)
        out = dict(zip(self._outputs, self.decoder.run(None, feeds)))
        new_past = {k.replace("present", "past_key_values"): v
                    for k, v in out.items() if k.startswith("present")}
        if past is not None:
            # The cached branch returns empty cross-attention entries: the
            # encoder's keys and values from the first step have to be kept.
            new_past.update({k: v for k, v in past.items() if ".encoder." in k})
        return out["logits"], new_past

    def detect_language(self, enc: np.ndarray) -> str:
        logits, _ = self._step(np.array([[self.tok.sot]]), enc, None)
        codes = list(self.lang_to_id)
        best = int(np.argmax(logits[0, 0][[self.lang_to_id[c] for c in codes]]))
        return codes[best].strip("<|>")

    # -- decoding ----------------------------------------------------------

    def _apply_rules(self, logits: np.ndarray, sampled: list[int]) -> None:
        """openai-whisper's SuppressTokens, SuppressBlank and ApplyTimestampRules."""
        tb = self.tok.timestamp_begin
        logits[self._suppress[:len(logits)]] = -np.inf
        if not sampled:
            logits[self._begin_suppress] = -np.inf
            logits[:tb] = -np.inf  # a window opens with a timestamp ...
            logits[tb + round(MAX_INITIAL_TIMESTAMP / TIME_PRECISION) + 1:] = -np.inf  # ... an early one
            return
        last_ts = sampled[-1] >= tb
        penultimate_ts = len(sampled) < 2 or sampled[-2] >= tb
        if last_ts:
            if penultimate_ts:
                logits[tb:] = -np.inf          # a closed pair is followed by text
            else:
                logits[:self.tok.eot] = -np.inf  # an open timestamp needs its partner
        stamps = [t for t in sampled if t >= tb]
        if stamps:
            # Timestamps never go backwards, and a segment can't be empty.
            floor = stamps[-1] if last_ts and not penultimate_ts else stamps[-1] + 1
            logits[tb:floor] = -np.inf
        logprobs = logits - np.logaddexp.reduce(logits)
        if np.logaddexp.reduce(logprobs[tb:]) > logprobs[:tb].max():
            logits[:tb] = -np.inf  # a timestamp is likelier than any word

    def decode(self, encs: list[np.ndarray], language: str, durations: list[float],
               ) -> list[list[tuple[float, float, str]]]:
        """Greedy decode of a batch of windows: (start, end, text) per window.

        One step reads the decoder's weights once for the whole batch, which
        is what makes batching pay on a CPU: decoding is bound by memory
        traffic (the 51866-token output projection alone is 265 MB), so
        threads decoding windows separately only queue for the same memory.
        All windows start from the same prompt and take one token a step, so
        their caches stay the same length; a finished window just leaves.
        """
        prompt = [self.tok.sot, self.lang_to_id[f"<|{language}|>"], self.tok.transcribe]
        n = len(encs)
        enc = np.concatenate(encs)
        logits, past = self._step(np.array([prompt] * n), enc, None)
        no_speech = [_softmax(logits[b, 0].astype(np.float64))[self.tok.no_speech]
                     for b in range(n)]
        last = logits[:, -1]
        sampled: list[list[int]] = [[] for _ in range(n)]
        sum_logprob = [0.0] * n
        active = list(range(n))
        while active:
            keep, tokens = [], []
            for row, b in enumerate(active):
                scores = last[row].astype(np.float64)
                self._apply_rules(scores, sampled[b])
                token = int(np.argmax(scores))
                sum_logprob[b] += float(scores[token] - np.logaddexp.reduce(scores))
                if token == self.tok.eot:
                    continue
                sampled[b].append(token)
                if len(prompt) + len(sampled[b]) < MAX_TOKENS:
                    keep.append(row)
                    tokens.append(token)
            if not keep:
                break
            if len(keep) < len(active):
                past = {k: v[keep] for k, v in past.items()}
                enc = enc[keep]
                active = [active[r] for r in keep]
            out, past = self._step(np.array(tokens)[:, None], enc, past)
            last = out[:, -1]

        results = []
        for b in range(n):
            avg_logprob = sum_logprob[b] / (len(sampled[b]) + 1)
            if no_speech[b] > NO_SPEECH_THRESHOLD and avg_logprob < LOGPROB_THRESHOLD:
                results.append([])
            else:
                results.append(self._segments(sampled[b], durations[b]))
        return results

    def _segments(self, sampled: list[int], duration: float) -> list[tuple[float, float, str]]:
        tb = self.tok.timestamp_begin
        segments = []
        start, text = 0.0, []
        for t in sampled:
            if t >= tb:
                when = min((t - tb) * TIME_PRECISION, duration)
                if text:
                    segments.append((start, when, self.tok.decode(text).strip()))
                    text = []
                start = when
            else:
                text.append(t)
        if text:  # ran out of tokens before a closing timestamp
            segments.append((start, duration, self.tok.decode(text).strip()))
        return [s for s in segments if s[2]]

    def transcribe(self, paths: list[Path], durations: list[float],
                   read: Callable[[Path], np.ndarray], language: str | None,
                   on_chunk: Callable[[int], None] = lambda _i: None,
                   ) -> tuple[list[list[tuple[float, float, str]]], str]:
        """The GPU encodes windows in order. A helper thread reads the next
        chunk and runs VAD and the features meanwhile, and CPU threads decode
        finished windows in batches.

        Batches waiting to be decoded are capped, so a long video does not
        pile up gigabytes of encoder output when the decoders fall behind.
        """
        results: list[list[tuple[float, float, str]]] = [[] for _ in paths]
        if not paths:
            return results, language or ""
        waiting = threading.BoundedSemaphore(self.workers * 2)
        futures = []
        spans: dict[int, list[tuple[float, float]]] = {}

        def job(indices, encs):
            try:
                return indices, self.decode(encs, language, [durations[i] for i in indices])
            finally:
                waiting.release()

        def submit(indices, encs):
            waiting.acquire()
            futures.append(pool.submit(job, indices, encs))

        with ThreadPoolExecutor(1) as ahead, ThreadPoolExecutor(self.workers) as pool:
            pending = ahead.submit(lambda p: self.features(read(p)), paths[0])
            indices: list[int] = []
            encs: list[np.ndarray] = []
            for i in range(len(paths)):
                on_chunk(i)
                prepared = pending.result()
                if i + 1 < len(paths):
                    pending = ahead.submit(lambda p: self.features(read(p)), paths[i + 1])
                if prepared is None:
                    continue  # no speech in this chunk
                mel, spans[i] = prepared
                enc = self.encode(mel)
                if language is None:
                    language = self.detect_language(enc)
                indices.append(i)
                encs.append(enc)
                if len(encs) == self.batch_size:
                    submit(indices, encs)
                    indices, encs = [], []
            if encs:
                submit(indices, encs)
            for f in futures:
                done, found = f.result()
                for i, segs in zip(done, found):
                    results[i] = [seg for seg in segs if _in_speech(seg, spans[i])]
        return results, language or ""


def _in_speech(segment: tuple[float, float, str], spans: list[tuple[float, float]]) -> bool:
    start, end, _ = segment
    overlap = sum(max(0.0, min(end, b) - max(start, a)) for a, b in spans)
    return overlap >= MIN_SPEECH_OVERLAP * max(end - start, 0.1)


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()
