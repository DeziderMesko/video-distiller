"""Parakeet with its encoder on a DirectML GPU (native Windows only).

sherpa-onnx's PyPI wheels are built without DirectML, so this module redoes
the part of sherpa-onnx that Parakeet needs, around an onnxruntime-directml
encoder session. It matches sherpa-onnx v1.13.7 step for step, and on a test
video gives the same transcript word for word:

- features: kaldi-native-fbank, 128 mel bins, with the settings from
  offline-recognizer-transducer-nemo-impl.h, then NeMo's per_feature
  normalisation (math.cc: population std, plus 1e-5);
- encoder: DirectML;
- decoding: greedy RNN-T, as in offline-transducer-greedy-search-nemo-decoder.cc.
  The model is RNN-T, not TDT (its url metadata has no "tdt"). The decoder
  and joiner are tiny and stay on the CPU.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import numpy as np

from .config import SAMPLE_RATE

# Encoder frames are 8 feature frames of 10 ms each.
FRAME_SECONDS = 0.08
# sherpa-onnx's cap on tokens emitted without advancing a frame.
MAX_SYMBOLS_PER_FRAME = 10
# Encoder frames scored per joiner call. The next token is usually a frame or
# two away, so start small and widen only across runs of blanks; scoring one
# frame per call spent twice as long in Python overhead.
MIN_WINDOW, MAX_WINDOW = 8, 128
# Pad features to a multiple of this many frames, so DirectML sees a few input
# shapes rather than a new one, and a fresh warm-up, for every chunk.
BUCKET_FRAMES = 1000


class DirectMLError(RuntimeError):
    pass


def _fbank_options():
    import kaldi_native_fbank as knf

    opts = knf.FbankOptions()
    opts.frame_opts.dither = 0
    opts.frame_opts.snip_edges = False
    opts.frame_opts.samp_freq = SAMPLE_RATE
    opts.frame_opts.frame_shift_ms = 10
    opts.frame_opts.frame_length_ms = 25
    opts.frame_opts.remove_dc_offset = False
    opts.frame_opts.preemph_coeff = 0.97
    opts.frame_opts.window_type = "povey"
    opts.frame_opts.round_to_power_of_two = True
    opts.mel_opts.num_bins = 128
    opts.mel_opts.low_freq = 0
    opts.mel_opts.high_freq = -400
    opts.mel_opts.is_librosa = True
    return opts


def features(samples: np.ndarray, opts) -> np.ndarray:
    """Normalised log-mel features, shape (frames, 128)."""
    import kaldi_native_fbank as knf

    fb = knf.OnlineFbank(opts)
    fb.accept_waveform(SAMPLE_RATE, samples.tolist())
    fb.input_finished()
    x = np.stack([fb.get_frame(i) for i in range(fb.num_frames_ready)]).astype(np.float32)
    mean = x.mean(axis=0)
    std = np.sqrt(((x - mean) ** 2).mean(axis=0))
    return (x - mean) / (std + 1e-5)


class Parakeet:
    """The three sherpa-onnx fp32 Parakeet files, encoder on the GPU."""

    def __init__(self, model_dir: Path):
        try:
            import kaldi_native_fbank  # noqa: F401
            import onnxruntime as ort
        except ImportError as exc:
            raise DirectMLError(
                "the parakeet-dml backend needs onnxruntime-directml and "
                "kaldi-native-fbank: pip install -e '.[directml]'"
            ) from exc
        if "DmlExecutionProvider" not in ort.get_available_providers():
            raise DirectMLError(
                "onnxruntime has no DirectML provider here; install "
                "onnxruntime-directml (not plain onnxruntime) on native Windows"
            )

        so = ort.SessionOptions()
        # DirectML requires both of these.
        so.enable_mem_pattern = False
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.log_severity_level = 3
        self.encoder = ort.InferenceSession(
            str(model_dir / "encoder.onnx"), so, providers=["DmlExecutionProvider"]
        )
        if self.encoder.get_providers()[0] != "DmlExecutionProvider":
            raise DirectMLError("the encoder did not load on the DirectML GPU")

        small = ort.SessionOptions()
        small.intra_op_num_threads = 1
        small.log_severity_level = 3
        cpu = ["CPUExecutionProvider"]
        self.decoder = ort.InferenceSession(str(model_dir / "decoder.onnx"), small, providers=cpu)
        self.joiner = ort.InferenceSession(str(model_dir / "joiner.onnx"), small, providers=cpu)
        self._decoder_inputs = [i.name for i in self.decoder.get_inputs()]

        self.tokens: dict[int, str] = {}
        for line in (model_dir / "tokens.txt").read_text(encoding="utf-8").splitlines():
            sym, idx = line.rsplit(" ", 1)
            self.tokens[int(idx)] = sym
        self.blank = max(self.tokens)  # <blk> is the last token
        self._opts = _fbank_options()

    def encode(self, samples: np.ndarray) -> np.ndarray:
        """Encoder output for one chunk, shape (1024, frames)."""
        x = features(samples, self._opts)
        n = x.shape[0]
        padded = -(-n // BUCKET_FRAMES) * BUCKET_FRAMES
        feats = np.zeros((1, x.shape[1], padded), dtype=np.float32)
        feats[0, :, :n] = x.T
        enc, enc_len = self.encoder.run(
            None, {"audio_signal": feats, "length": np.array([n], dtype=np.int64)}
        )
        return enc[0, :, :int(enc_len[0])]

    def _step(self, token: int, states):
        names = self._decoder_inputs
        out = self.decoder.run(None, {
            names[0]: np.array([[token]], dtype=np.int32),
            names[1]: np.array([1], dtype=np.int32),
            names[2]: states[0],
            names[3]: states[1],
        })
        return out[0], (out[2], out[3])

    def decode(self, enc: np.ndarray) -> tuple[list[str], list[float]]:
        """Greedy RNN-T over one chunk: BPE tokens and their start times.

        Scoring a window of frames against one decoder state is the same
        search as scoring them one by one: blanks leave the decoder state
        alone, so the first non-blank frame in the window is the one a
        frame-by-frame loop would have stopped at.
        """
        zeros = np.zeros((2, 1, 640), dtype=np.float32)
        dec_out, states = self._step(self.blank, (zeros, zeros))
        tokens: list[str] = []
        stamps: list[float] = []
        t, emitted_here, size, frames = 0, 0, MIN_WINDOW, enc.shape[1]
        while t < frames:
            window = enc[None, :, t:t + size]
            logits = self.joiner.run(
                None, {"encoder_outputs": window, "decoder_outputs": dec_out}
            )[0]
            best = logits[0, :, 0, :].argmax(axis=-1)
            hits = np.nonzero(best != self.blank)[0]
            if len(hits) == 0:
                t += window.shape[2]
                emitted_here = 0
                size = min(size * 2, MAX_WINDOW)
                continue
            size = MIN_WINDOW
            first = int(hits[0])
            if first > 0:
                t += first
                emitted_here = 0
            token = int(best[first])
            tokens.append(self.tokens[token])
            stamps.append(t * FRAME_SECONDS)
            dec_out, states = self._step(token, states)
            emitted_here += 1
            if emitted_here >= MAX_SYMBOLS_PER_FRAME:
                t += 1
                emitted_here = 0
        return tokens, stamps

    def transcribe(self, paths: list[Path], read: Callable[[Path], np.ndarray],
                   on_chunk: Callable[[int], None] = lambda _i: None,
                   ) -> list[tuple[list[str], list[float]]]:
        """Decode each chunk; the GPU encodes chunk i+1 while the CPU decodes chunk i.

        onnxruntime releases the GIL while it runs, so one helper thread is
        enough to keep both busy. Chunks are read as they are needed, so a
        long video is never in memory all at once.
        """
        results: list[tuple[list[str], list[float]]] = []
        if not paths:
            return results
        with ThreadPoolExecutor(1) as pool:
            pending = pool.submit(lambda p: self.encode(read(p)), paths[0])
            for i in range(len(paths)):
                on_chunk(i)
                enc = pending.result()
                if i + 1 < len(paths):
                    pending = pool.submit(lambda p: self.encode(read(p)), paths[i + 1])
                results.append(self.decode(enc))
        return results
