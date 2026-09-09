"""The data/ folder: one directory per video, transcript kept beside its source URL."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR
from .download import VideoInfo
from .transcribe import Transcript

INDEX = "index.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stamp(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass
class Entry:
    """One distilled video on disk."""

    dir: Path
    info: VideoInfo

    @property
    def transcript_txt(self) -> Path:
        return self.dir / "transcript.txt"

    @property
    def transcript_json(self) -> Path:
        return self.dir / "transcript.json"

    @property
    def summary_md(self) -> Path:
        return self.dir / "summary.md"

    @property
    def meta_json(self) -> Path:
        return self.dir / "meta.json"

    def read_transcript(self) -> str:
        if not self.transcript_txt.exists():
            raise FileNotFoundError(f"no transcript at {self.transcript_txt}")
        return self.transcript_txt.read_text(encoding="utf-8")


def entry_dir(info: VideoInfo, root: Path = DATA_DIR) -> Path:
    return root / info.slug


def save_transcript(info: VideoInfo, transcript: Transcript,
                    root: Path = DATA_DIR) -> Entry:
    """Write transcript, timestamped segments and metadata. URL travels with the text."""
    target = entry_dir(info, root)
    target.mkdir(parents=True, exist_ok=True)

    header = [
        f"# {info.title}",
        f"Source: {info.url}",
    ]
    if info.uploader:
        header.append(f"Channel: {info.uploader}")
    if info.duration:
        header.append(f"Duration: {_stamp(info.duration)}")
    header += [
        f"Transcribed: {_now()} using {transcript.model} ({transcript.backend})",
        "",
        "---",
        "",
    ]
    body = _wrap(transcript.text)
    (target / "transcript.txt").write_text("\n".join(header) + body + "\n", encoding="utf-8")

    (target / "transcript.json").write_text(
        json.dumps(
            {
                "source_url": info.url,
                "video_id": info.video_id,
                "title": info.title,
                "backend": transcript.backend,
                "model": transcript.model,
                "transcribed_at": _now(),
                "text": transcript.text,
                "segments": [asdict(s) for s in transcript.segments],
            },
            indent=2, ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    if transcript.segments:
        (target / "transcript.timed.txt").write_text(
            "\n".join(f"[{_stamp(s.start)}] {s.text}" for s in transcript.segments) + "\n",
            encoding="utf-8",
        )

    meta = {
        "source_url": info.url,
        "video_id": info.video_id,
        "title": info.title,
        "uploader": info.uploader,
        "duration_seconds": info.duration,
        "upload_date": info.upload_date,
        "backend": transcript.backend,
        "model": transcript.model,
        "transcribed_at": _now(),
        "audio_retained": False,
    }
    (target / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _append_index(meta, root)
    return Entry(dir=target, info=info)


def save_output(entry: Entry, text: str, question: str | None) -> Path:
    """Store a summary, or one answer among many."""
    if question is None:
        path = entry.summary_md
        head = f"# Summary: {entry.info.title}\n\nSource: {entry.info.url}\n\n---\n\n"
    else:
        answers = entry.dir / "answers"
        answers.mkdir(exist_ok=True)
        path = answers / f"{_slugify(question)}.md"
        head = (
            f"# {question}\n\n"
            f"Video: {entry.info.title}\nSource: {entry.info.url}\n"
            f"Asked: {_now()}\n\n---\n\n"
        )
    path.write_text(head + text.strip() + "\n", encoding="utf-8")
    return path


def load(identifier: str, root: Path = DATA_DIR) -> Entry | None:
    """Find a stored video by directory name, video id or source URL."""
    if not root.exists():
        return None
    direct = root / identifier
    if direct.is_dir() and (direct / "meta.json").exists():
        return _entry_from(direct)
    for meta_path in sorted(root.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if identifier in (meta.get("video_id"), meta.get("source_url")):
            return _entry_from(meta_path.parent)
    return None


def all_entries(root: Path = DATA_DIR) -> list[Entry]:
    if not root.exists():
        return []
    return [_entry_from(p.parent) for p in sorted(root.glob("*/meta.json"))]


def _entry_from(directory: Path) -> Entry:
    meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    info = VideoInfo(
        video_id=meta.get("video_id", ""),
        title=meta.get("title", directory.name),
        url=meta.get("source_url", ""),
        uploader=meta.get("uploader"),
        duration=meta.get("duration_seconds"),
        upload_date=meta.get("upload_date"),
    )
    return Entry(dir=directory, info=info)


def _append_index(meta: dict, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with (root / INDEX).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, ensure_ascii=False) + "\n")


def _slugify(text: str, limit: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit].strip("-")
    return slug or "answer"


def _wrap(text: str, width: int = 88) -> str:
    """Soft-wrap the transcript so it reads in a terminal and diffs sanely."""
    import textwrap

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()] or [text.strip()]
    return "\n\n".join(textwrap.fill(p, width=width) for p in paragraphs)
