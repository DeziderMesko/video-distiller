"""Speech-to-text backends. Parakeet is the default; Whisper is the escape hatch."""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from .audio import Chunk
from .config import (
    CHUNK_SECONDS,
    DML_CHUNK_SECONDS,
    DEFAULT_ONNX_PRECISION,
    WHISPER_BATCH_SIZE,
    WHISPER_WORKERS,
    DEFAULT_PARAKEET_MODEL,
    DEFAULT_WHISPER_MODEL,
    SAMPLE_RATE,
    SEGMENT_MAX_SECONDS,
    SEGMENT_PAUSE_SECONDS,
)


class TranscriptionError(RuntimeError):
    pass


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    text: str
    segments: list[Segment] = field(default_factory=list)
    backend: str = ""
    model: str = ""
    language: str = ""
    # Wall-clock seconds spent transcribing, and how much audio that covered.
    elapsed: float = 0.0
    audio_seconds: float = 0.0


Progress = Callable[[str], None]


class Backend(Protocol):
    name: str
    model_id: str
    # The chunk length this backend works best with, unless the user picks one.
    chunk_seconds: float

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript: ...


def _merge(pieces: list[tuple[float, list[Segment], str]]) -> tuple[str, list[Segment]]:
    segments: list[Segment] = []
    texts: list[str] = []
    for offset, segs, text in pieces:
        segments.extend(
            Segment(s.start + offset, s.end + offset, s.text) for s in segs
        )
        if text.strip():
            texts.append(text.strip())
    return " ".join(texts), segments


class ParakeetBackend:
    """NVIDIA NeMo Parakeet (FastConformer + RNN-T)."""

    name = "parakeet"
    chunk_seconds = CHUNK_SECONDS

    def __init__(self, model_id: str = DEFAULT_PARAKEET_MODEL, threads: int | None = None):
        self.model_id = model_id
        self._threads = threads or os.cpu_count() or 4
        self._model = None

    def _load(self, progress: Progress):
        if self._model is not None:
            return self._model
        try:
            import torch
            import nemo.collections.asr as nemo_asr
        except ImportError as exc:
            raise TranscriptionError(
                "the parakeet backend needs NeMo: pip install 'nemo_toolkit[asr]'"
            ) from exc

        torch.set_num_threads(self._threads)
        progress(f"loading {self.model_id} (first run downloads ~2.5 GB)")
        try:
            model = nemo_asr.models.ASRModel.from_pretrained(model_name=self.model_id)
        except Exception as exc:
            raise TranscriptionError(f"could not load {self.model_id}: {exc}") from exc
        model.eval()
        # This checkpoint ships validation_ds: null, which NeMo 3.x dereferences
        # unguarded while building the transcribe dataloader.
        if getattr(model.cfg, "validation_ds", None) is None:
            from omegaconf import DictConfig, open_dict

            with open_dict(model.cfg):
                model.cfg.validation_ds = DictConfig({})
        self._model = model
        return model

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript:
        model = self._load(progress)
        pieces = []
        for i, chunk in enumerate(chunks, 1):
            progress(f"transcribing chunk {i}/{len(chunks)} ({chunk.duration:.0f}s)")
            text, segs = self._one(model, chunk.path)
            pieces.append((chunk.offset, segs, text))
        text, segments = _merge(pieces)
        return Transcript(text, segments, self.name, self.model_id, "en")

    def _one(self, model, path: Path) -> tuple[str, list[Segment]]:
        import torch

        with torch.inference_mode():
            try:
                out = model.transcribe([str(path)], timestamps=True, verbose=False)
            except TypeError:
                # Older NeMo builds have no timestamps kwarg.
                out = model.transcribe([str(path)], verbose=False)
        hyp = out[0] if isinstance(out, (list, tuple)) and out else out
        if isinstance(hyp, (list, tuple)) and hyp:  # some versions nest by decoder
            hyp = hyp[0]

        text = getattr(hyp, "text", hyp if isinstance(hyp, str) else "")
        segments: list[Segment] = []
        stamps = getattr(hyp, "timestamp", None) or {}
        for entry in stamps.get("segment", []) or []:
            body = (entry.get("segment") or entry.get("text") or "").strip()
            if body:
                segments.append(
                    Segment(float(entry.get("start", 0.0)), float(entry.get("end", 0.0)), body)
                )
        return text, segments


class ParakeetOnnxBackend:
    """Parakeet via sherpa-onnx. int8 weights, no torch, ~660 MB on disk."""

    name = "parakeet-onnx"
    chunk_seconds = CHUNK_SECONDS

    REPOS = {
        "int8": "csukuangfj2/sherpa-onnx-nemo-parakeet-unified-en-0.6b-int8-non-streaming",
        "fp32": "csukuangfj2/sherpa-onnx-nemo-parakeet-unified-en-0.6b-non-streaming",
    }
    FILES = {
        "int8": ["encoder.int8.onnx", "decoder.int8.onnx", "joiner.int8.onnx", "tokens.txt"],
        "fp32": ["encoder.onnx", "encoder.weights", "decoder.onnx", "joiner.onnx", "tokens.txt"],
    }

    def __init__(self, model_id: str = "int8", threads: int | None = None):
        if model_id in self.REPOS:
            self.precision, self.model_id = model_id, self.REPOS[model_id]
        else:
            # Allow an explicit repo id; guess precision from its name.
            self.precision = "int8" if "int8" in model_id else "fp32"
            self.model_id = model_id
        self._threads = threads or os.cpu_count() or 4
        self._rec = None

    def _load(self, progress: Progress):
        if self._rec is not None:
            return self._rec
        try:
            import sherpa_onnx
        except ImportError as exc:
            raise TranscriptionError(
                "the parakeet-onnx backend needs sherpa-onnx: pip install sherpa-onnx"
            ) from exc
        from .models import ModelFetchError, ensure

        repo = self.model_id if "/" in self.model_id else self.REPOS[self.precision]
        files = self.FILES[self.precision]
        progress(f"preparing {repo}")
        try:
            root = ensure(repo, files, progress)
        except ModelFetchError as exc:
            raise TranscriptionError(str(exc)) from exc

        # fp32 keeps its encoder weights in a side file, so pick by name, not position.
        encoder, decoder, joiner = (
            str(root / next(f for f in files if f.startswith(part) and f.endswith(".onnx")))
            for part in ("encoder", "decoder", "joiner")
        )
        self._rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            tokens=str(root / "tokens.txt"),
            num_threads=self._threads,
            sample_rate=SAMPLE_RATE,
            feature_dim=80,
            decoding_method="greedy_search",
            model_type="nemo_transducer",
        )
        return self._rec

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript:
        rec = self._load(progress)
        pieces = []
        for i, chunk in enumerate(chunks, 1):
            progress(f"transcribing chunk {i}/{len(chunks)} ({chunk.duration:.0f}s)")
            samples = read_wav(chunk.path)
            stream = rec.create_stream()
            stream.accept_waveform(SAMPLE_RATE, samples)
            rec.decode_stream(stream)
            result = stream.result
            segs = _segment_tokens(
                list(result.tokens or []), list(result.timestamps or [])
            )
            pieces.append((chunk.offset, segs, result.text))
        text, segments = _merge(pieces)
        return Transcript(text, segments, self.name,
                          f"{self.model_id} [{self.precision}]", "en")


def read_wav(path: Path):
    """Read a 16 kHz mono PCM WAV as float32 in [-1, 1]."""
    import wave

    import numpy as np

    with wave.open(str(path), "rb") as wav:
        if wav.getframerate() != SAMPLE_RATE or wav.getnchannels() != 1:
            raise TranscriptionError(f"{path} is not 16 kHz mono; audio.to_wav missed it")
        raw = wav.readframes(wav.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype("float32") / 32768.0


def _segment_tokens(tokens: list[str], stamps: list[float]) -> list[Segment]:
    """Rebuild sentence-level segments from BPE tokens and their timestamps.

    Parakeet sometimes stops punctuating for minutes on end, and splitting on
    sentence ends alone then turned a whole 300 s chunk into one segment -- a
    summary had nothing finer to cite and started inventing times in between.
    So a pause, or a segment grown too long, ends one too, at a word boundary.
    """
    if not tokens or len(tokens) != len(stamps):
        return []
    segments: list[Segment] = []
    words: list[str] = []
    start = prev = stamps[0]

    def close(end: float) -> None:
        body = "".join(words).strip()
        if body:
            segments.append(Segment(start, end, body))

    for token, when in zip(tokens, stamps):
        # A word starts with a space as sherpa-onnx returns tokens, or with
        # SentencePiece's own U+2581 marker.
        if words and token.startswith((" ", "\u2581")) and (
            when - prev >= SEGMENT_PAUSE_SECONDS or when - start >= SEGMENT_MAX_SECONDS
        ):
            close(prev)
            words, start = [], when
        if not words:
            start = when
        words.append(token.replace("\u2581", " "))
        prev = when
        if token.rstrip().endswith((".", "?", "!")):
            close(when)
            words = []
    close(stamps[-1])
    return segments


class ParakeetDmlBackend:
    """Parakeet fp32 with its encoder on a DirectML GPU; native Windows only.

    sherpa-onnx wheels lack DirectML, so vdistill.directml does the features and
    decoding itself. Same model files and same words as parakeet-onnx at fp32.
    """

    name = "parakeet-dml"
    chunk_seconds = DML_CHUNK_SECONDS

    def __init__(self, model_id: str = "fp32"):
        if model_id not in ("fp32", ParakeetOnnxBackend.REPOS["fp32"]):
            raise TranscriptionError("parakeet-dml only runs the fp32 Parakeet export")
        self.model_id = ParakeetOnnxBackend.REPOS["fp32"]
        self._model = None

    def _load(self, progress: Progress):
        if self._model is not None:
            return self._model
        if os.name != "nt":
            raise TranscriptionError(
                "parakeet-dml needs native Windows (DirectML); use parakeet-onnx here"
            )
        from .directml import DirectMLError, Parakeet
        from .models import ModelFetchError, ensure

        progress(f"preparing {self.model_id}")
        try:
            root = ensure(self.model_id, ParakeetOnnxBackend.FILES["fp32"], progress)
        except ModelFetchError as exc:
            raise TranscriptionError(str(exc)) from exc
        try:
            self._model = Parakeet(root)
        except DirectMLError as exc:
            raise TranscriptionError(str(exc)) from exc
        return self._model

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript:
        model = self._load(progress)

        def report(i: int) -> None:
            progress(f"transcribing chunk {i + 1}/{len(chunks)} ({chunks[i].duration:.0f}s)")

        results = model.transcribe([c.path for c in chunks], read_wav, report)
        pieces = []
        for chunk, (tokens, stamps) in zip(chunks, results):
            text = "".join(tokens).replace("\u2581", " ").strip()
            pieces.append((chunk.offset, _segment_tokens(tokens, stamps), text))
        text, segments = _merge(pieces)
        return Transcript(text, segments, self.name,
                          f"{self.model_id} [fp32, directml]", "en")


class WhisperBackend:
    """faster-whisper (CTranslate2). The non-English path; Parakeet is English-only."""

    name = "whisper"
    chunk_seconds = CHUNK_SECONDS

    # int8 CTranslate2 repacks. The fp16 turbo repos are 1622 MB for the same
    # model, and plain "large-v3" is 3091 MB, so name the int8 builds explicitly.
    ALIASES = {
        "turbo": "Zoont/faster-whisper-large-v3-turbo-int8-ct2",          # 818 MB
        "large-v3-turbo": "Zoont/faster-whisper-large-v3-turbo-int8-ct2",
        "large-v3": "Systran/faster-whisper-large-v3",                    # 3091 MB
    }

    def __init__(self, model_id: str = DEFAULT_WHISPER_MODEL, threads: int | None = None,
                 language: str | None = None, batch_size: int = WHISPER_BATCH_SIZE,
                 workers: int = WHISPER_WORKERS):
        self.model_id = self.ALIASES.get(model_id, model_id)
        cores = threads or os.cpu_count() or 4
        # One CTranslate2 stream saturates about four cores and no more, so the
        # way to use a 16-core box is several chunks at once, not more threads
        # on one chunk. Split the cores between workers rather than oversubscribe.
        self._workers = max(1, min(workers, cores))
        self._threads = max(1, cores // self._workers)
        self._language = language
        self._batch_size = batch_size
        self._detected = ""
        self._model = None
        self._pipeline = None

    def _load(self, progress: Progress):
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TranscriptionError(
                "the whisper backend needs faster-whisper: pip install faster-whisper"
            ) from exc
        progress(f"loading whisper {self.model_id}")
        try:
            self._model = WhisperModel(
                self.model_id, device="cpu", compute_type="int8",
                cpu_threads=self._threads, num_workers=self._workers,
            )
        except Exception as exc:
            raise TranscriptionError(f"could not load {self.model_id}: {exc}") from exc

        # Batching the 30 s windows is what actually fills the cores; a single
        # sequential decode leaves most of a 16-core box idle.
        try:
            from faster_whisper import BatchedInferencePipeline

            self._pipeline = BatchedInferencePipeline(model=self._model)
        except Exception:
            self._pipeline = None
            progress("batched pipeline unavailable; falling back to sequential decode")
        return self._model

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript:
        model = self._load(progress)
        if self._workers > 1 and len(chunks) > 1:
            progress(
                f"transcribing {len(chunks)} chunks, {self._workers} at a time "
                f"({self._threads} threads each)"
            )
        done = 0
        lock = threading.Lock()

        def one(chunk: Chunk):
            nonlocal done
            found = self._decode(model, chunk.path)
            with lock:
                done += 1
                progress(f"  {done}/{len(chunks)} chunks done")
            return chunk.offset, found, " ".join(s.text for s in found)

        workers = min(self._workers, len(chunks))
        if workers > 1:
            # CTranslate2 releases the GIL during compute, and the model is
            # built with matching num_workers, so threads genuinely run parallel.
            with ThreadPoolExecutor(max_workers=workers) as pool:
                pieces = list(pool.map(one, chunks))
        else:
            pieces = [one(chunk) for chunk in chunks]

        text, segments = _merge(pieces)
        return Transcript(text, segments, self.name, self.model_id,
                          self._language or self._detected or "")

    def _decode(self, model, path: Path) -> list[Segment]:
        """Greedy, context-free decode -- matches how Parakeet is run, and
        avoids the repetition loops that condition_on_previous_text invites."""
        options = dict(
            language=self._language,
            beam_size=1,
            best_of=1,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
        )
        if self._pipeline is not None:
            segs, info = self._pipeline.transcribe(
                str(path), batch_size=self._batch_size, **options
            )
        else:
            segs, info = model.transcribe(str(path), **options)
        if not self._detected:
            self._detected = getattr(info, "language", "") or ""
        return [Segment(s.start, s.end, s.text.strip()) for s in segs]


def get_backend(name: str, model: str | None = None, language: str | None = None) -> Backend:
    if name == "parakeet-onnx":
        return ParakeetOnnxBackend(model or DEFAULT_ONNX_PRECISION)
    if name == "parakeet-dml":
        return ParakeetDmlBackend(model or "fp32")
    if name == "parakeet":
        return ParakeetBackend(model or DEFAULT_PARAKEET_MODEL)
    if name == "whisper":
        return WhisperBackend(model or DEFAULT_WHISPER_MODEL, language=language)
    raise TranscriptionError(
        f"unknown ASR backend {name!r} (try: parakeet-onnx, parakeet-dml, parakeet, whisper)"
    )
