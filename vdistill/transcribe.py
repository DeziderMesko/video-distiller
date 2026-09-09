"""Speech-to-text backends. Parakeet is the default; Whisper is the escape hatch."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from .audio import Chunk
from .config import (
    DEFAULT_ONNX_PRECISION,
    DEFAULT_PARAKEET_MODEL,
    DEFAULT_WHISPER_MODEL,
    SAMPLE_RATE,
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


Progress = Callable[[str], None]


class Backend(Protocol):
    name: str
    model_id: str

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
        return Transcript(text, segments, self.name, self.model_id)

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

        encoder, decoder, joiner = (str(root / f) for f in files[:3])
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
        return Transcript(text, segments, self.name, f"{self.model_id} [{self.precision}]")


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
    """Rebuild sentence-level segments from BPE tokens and their timestamps."""
    if not tokens or len(tokens) != len(stamps):
        return []
    segments: list[Segment] = []
    words: list[str] = []
    start = stamps[0]
    for token, when in zip(tokens, stamps):
        # SentencePiece marks a word boundary with U+2581.
        words.append(token.replace("\u2581", " "))
        if token.rstrip().endswith((".", "?", "!")):
            body = "".join(words).strip()
            if body:
                segments.append(Segment(start, when, body))
            words, start = [], when
    tail = "".join(words).strip()
    if tail:
        segments.append(Segment(start, stamps[-1], tail))
    return segments


class WhisperBackend:
    """faster-whisper (CTranslate2). The non-English path; Parakeet is English-only."""

    name = "whisper"

    # int8 CTranslate2 repacks. The fp16 turbo repos are 1622 MB for the same
    # model, and plain "large-v3" is 3091 MB, so name the int8 builds explicitly.
    ALIASES = {
        "turbo": "Zoont/faster-whisper-large-v3-turbo-int8-ct2",          # 818 MB
        "large-v3-turbo": "Zoont/faster-whisper-large-v3-turbo-int8-ct2",
        "large-v3": "Systran/faster-whisper-large-v3",                    # 3091 MB
    }

    def __init__(self, model_id: str = DEFAULT_WHISPER_MODEL, threads: int | None = None,
                 language: str | None = None):
        self.model_id = self.ALIASES.get(model_id, model_id)
        self._threads = threads or os.cpu_count() or 4
        self._language = language
        self._model = None

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
                cpu_threads=self._threads,
            )
        except Exception as exc:
            raise TranscriptionError(f"could not load {self.model_id}: {exc}") from exc
        return self._model

    def transcribe(self, chunks: list[Chunk], progress: Progress) -> Transcript:
        model = self._load(progress)
        pieces = []
        for i, chunk in enumerate(chunks, 1):
            progress(f"transcribing chunk {i}/{len(chunks)} ({chunk.duration:.0f}s)")
            segs, _ = model.transcribe(
                str(chunk.path), language=self._language, vad_filter=True
            )
            found = [Segment(s.start, s.end, s.text.strip()) for s in segs]
            pieces.append((chunk.offset, found, " ".join(s.text for s in found)))
        text, segments = _merge(pieces)
        return Transcript(text, segments, self.name, self.model_id)


def get_backend(name: str, model: str | None = None, language: str | None = None) -> Backend:
    if name == "parakeet-onnx":
        return ParakeetOnnxBackend(model or DEFAULT_ONNX_PRECISION)
    if name == "parakeet":
        return ParakeetBackend(model or DEFAULT_PARAKEET_MODEL)
    if name == "whisper":
        return WhisperBackend(model or DEFAULT_WHISPER_MODEL, language=language)
    raise TranscriptionError(
        f"unknown ASR backend {name!r} (try: parakeet-onnx, parakeet, whisper)"
    )
