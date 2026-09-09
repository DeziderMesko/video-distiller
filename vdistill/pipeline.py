"""The whole trip: URL -> audio -> transcript -> answer -> audio deleted."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import audio as audio_mod
from . import download, store
from .config import CHUNK_SECONDS, DATA_DIR, WORK_DIR
from .store import Entry
from .transcribe import Transcript, get_backend


@dataclass
class Result:
    entry: Entry
    transcript: Transcript
    output: str | None
    output_path: Path | None
    audio_kept: Path | None


def distill(
    url: str,
    question: str | None = None,
    backend_name: str = "parakeet",
    model: str | None = None,
    language: str | None = None,
    chunk_seconds: float = CHUNK_SECONDS,
    keep_audio: bool = False,
    summarize: bool = True,
    force: bool = False,
    summary_language: str | None = None,
    data_dir: Path = DATA_DIR,
    work_dir: Path = WORK_DIR,
    progress=lambda _m: None,
) -> Result:
    if not force:
        existing = _already_done(url, data_dir, progress)
        if existing is not None:
            output, output_path = (None, None)
            if summarize:
                output, output_path = answer(
                    existing, question, progress=progress, language=summary_language
                )
            return Result(existing, _stored_transcript(existing), output, output_path, None)

    backend_name, model = _pick_backend(backend_name, language, model, progress)
    backend = get_backend(backend_name, model, language)

    progress(f"fetching audio from {url}")
    # A unique staging dir keeps concurrent runs from clobbering each other.
    staging = Path(tempfile.mkdtemp(prefix="dl-", dir=_ensure(work_dir)))
    info, source = download.fetch_audio(url, staging, quiet=True)
    scratch = work_dir / info.video_id
    length = f" ({info.duration/60:.1f} min)" if info.duration else ""
    progress(f"got: {info.title}{length}")

    try:
        progress("converting to 16 kHz mono")
        wav = audio_mod.to_wav(source, scratch / "audio.wav")

        chunks = audio_mod.split(wav, scratch / "chunks", target=chunk_seconds)
        if len(chunks) > 1:
            progress(f"split into {len(chunks)} chunks at natural pauses")

        transcript = backend.transcribe(chunks, progress)
        if not transcript.text.strip():
            raise RuntimeError("transcription produced no text; keeping audio")

        entry = store.save_transcript(info, transcript, root=data_dir)
        progress(f"transcript saved to {entry.transcript_txt}")
    except Exception:
        # Transcription failed: leave the audio behind so a retry is cheap.
        progress(f"failed before a transcript existed; audio kept in {scratch}")
        raise

    kept: Path | None = None
    if keep_audio:
        kept = scratch / "audio.wav"
        shutil.rmtree(scratch / "chunks", ignore_errors=True)
        download.discard_audio(staging)
        progress(f"audio kept at {kept}")
        _mark_audio(entry, True)
    else:
        download.discard_audio(staging, scratch)
        progress("audio deleted")

    output = output_path = None
    if summarize:
        output, output_path = answer(
            entry, question, progress=progress, language=summary_language
        )

    return Result(entry, transcript, output, output_path, kept)


def answer(entry: Entry, question: str | None, model: str = "",
           progress=lambda _m: None, language: str | None = None) -> tuple[str, Path]:
    """Summarise, or answer a question, against an already-stored transcript."""
    from .summarize import get_summarizer, language_name

    # Default to the language the video was actually spoken in.
    lang = language or entry.language
    if question:
        progress("answering your question")
    else:
        name = language_name(lang)
        progress(f"summarising in {name}" if name else "summarising")
    # The timed form is what lets the summary point at where things were said.
    text = get_summarizer(model).run(
        entry.read_transcript(timed=True), question, progress=progress, language=lang
    )
    path = store.save_output(entry, text, question)
    progress(f"saved to {path}")
    return text, path


def _mark_audio(entry: Entry, kept: bool) -> None:
    import json

    meta = json.loads(entry.meta_json.read_text(encoding="utf-8"))
    meta["audio_retained"] = kept
    entry.meta_json.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _ensure(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _already_done(url: str, data_dir: Path, progress) -> Entry | None:
    """Reuse a stored transcript rather than downloading the same video twice."""
    entry = store.load(url, root=data_dir)
    if entry is None:
        try:
            info = download.probe(url)
        except Exception:
            return None
        entry = store.load(info.video_id, root=data_dir)
    if entry is None or not entry.transcript_txt.exists():
        return None
    progress(f"already transcribed: {entry.info.title} (--force to redo)")
    return entry


def _stored_transcript(entry: Entry) -> Transcript:
    import json

    data = json.loads(entry.transcript_json.read_text(encoding="utf-8"))
    return Transcript(
        text=data.get("text", ""),
        segments=[],
        backend=data.get("backend", ""),
        model=data.get("model", ""),
        language=data.get("language", ""),
    )


def _pick_backend(name: str, language: str | None, model: str | None,
                  progress) -> tuple[str, str | None]:
    """Parakeet only speaks English; asking for another language implies Whisper."""
    if language and language.split("-")[0].lower() != "en" and name.startswith("parakeet"):
        progress(f"--language {language} is not English; switching to the whisper backend")
        # A Parakeet-only precision alias means nothing to Whisper.
        if model in {"int8", "fp32"}:
            model = None
        return "whisper", model
    return name, model
