"""The data directory: one folder per video, transcript kept beside its source URL."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR
from .download import VideoInfo
from .timecode import duration, stamp
from .transcribe import Transcript

INDEX = "index.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Entry:
    """One distilled video on disk."""

    dir: Path
    info: VideoInfo
    language: str = ""

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

    @property
    def transcript_timed(self) -> Path:
        return self.dir / "transcript.timed.txt"

    def read_transcript(self, timed: bool = False) -> str:
        """The transcript text. `timed` prefers the [HH:MM:SS] segment form,
        which is what lets a summary say when something was discussed."""
        if timed and self.transcript_timed.exists():
            return self.transcript_timed.read_text(encoding="utf-8")
        if not self.transcript_txt.exists():
            raise FileNotFoundError(f"no transcript at {self.transcript_txt}")
        return self.transcript_txt.read_text(encoding="utf-8")

    @property
    def has_timestamps(self) -> bool:
        return self.transcript_timed.exists()


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
        header.append(f"Duration: {stamp(info.duration)}")
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

    timed = target / "transcript.timed.txt"
    if transcript.segments:
        timed.write_text(
            "\n".join(f"[{stamp(s.start)}] {s.text}" for s in transcript.segments) + "\n",
            encoding="utf-8",
        )
    else:
        # A --force re-run without timings must not leave the previous run's
        # timed text behind: summaries read it in preference to transcript.txt.
        timed.unlink(missing_ok=True)

    meta = {
        "source_url": info.url,
        "video_id": info.video_id,
        "title": info.title,
        "uploader": info.uploader,
        "duration_seconds": info.duration,
        "upload_date": info.upload_date,
        "backend": transcript.backend,
        "model": transcript.model,
        "language": transcript.language,
        "transcribed_at": _now(),
        "audio_retained": False,
    }
    (target / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _append_index(meta, root)
    return Entry(dir=target, info=info, language=transcript.language)


def save_output(entry: Entry, text: str, question: str | None) -> Path:
    """Store a summary, or one answer among many."""
    if question is None:
        path = entry.summary_md
        head = f"# Summary: {entry.info.title}\n\nSource: {entry.info.url}\n\n---\n\n"
    else:
        answers = entry.dir / "answers"
        answers.mkdir(exist_ok=True)
        path = answers / f"{_answer_name(question)}.md"
        head = (
            f"# {question}\n\n"
            f"Video: {entry.info.title}\nSource: {entry.info.url}\n"
            f"Asked: {_now()}\n\n---\n\n"
        )
    body = link_timestamps(escape_tildes(text.strip()), entry.info.url)
    path.write_text(head + body + "\n", encoding="utf-8")
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
    return Entry(dir=directory, info=info, language=meta.get("language", ""))


def _append_index(meta: dict, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    with (root / INDEX).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, ensure_ascii=False) + "\n")


_STAMP_RE = re.compile(r"\[(\d{1,2}):([0-5]\d):([0-5]\d)\]")
_LINK_RE = re.compile(r"\]\([^)]*\)")


def escape_tildes(text: str) -> str:
    """A summary saying "~$100 ... ~$2000" gets everything between the two
    prices struck through: GitHub Markdown reads a single ~x~ as strikethrough,
    and "~" is how the model writes "approximately". Escape them, except inside
    link targets, where a backslash would break the URL."""
    parts, last = [], 0
    for match in _LINK_RE.finditer(text):
        parts.append(text[last:match.start()].replace("~", "\\~"))
        parts.append(match.group(0))
        last = match.end()
    parts.append(text[last:].replace("~", "\\~"))
    return "".join(parts)


def check_timestamps(text: str, transcript: str,
                     duration: float | None = None) -> tuple[str, int]:
    """Make every [HH:MM:SS] in a summary one the transcript actually has.

    Told not to, the model still interpolates between segment starts. A time
    it made up is replaced by the start of the segment it falls in -- the
    finest place the transcript can honestly point to -- and one past the end
    of the recording, or with no timed transcript at all, is dropped.
    Returns the text and how many stamps were changed."""
    def seconds(match: re.Match) -> int:
        h, m, s = (int(g) for g in match.groups())
        return h * 3600 + m * 60 + s

    starts = sorted({seconds(m) for m in _STAMP_RE.finditer(transcript)})
    known = set(starts)
    changed = 0

    def replace(match: re.Match) -> str:
        nonlocal changed
        space, stamp = match.group(1), _STAMP_RE.match(match.group(2))
        when = seconds(stamp)
        if when in known:
            return match.group(0)
        changed += 1
        if not starts or (duration and when > duration):
            return ""                         # the space before it goes too
        earlier = [s for s in starts if s <= when]
        return f"{space}[{stamp(earlier[-1] if earlier else starts[0])}]"

    text = re.sub(r"([ \t]*)(" + _STAMP_RE.pattern + ")", replace, text)
    if changed:
        # Two neighbouring guesses can land on the same segment start.
        text = re.sub(r"(\[\d\d:\d\d:\d\d\])(?:[ \t]*\1)+", r"\1", text)
    return text, changed


def link_timestamps(text: str, url: str) -> str:
    """Turn [HH:MM:SS] markers into links that jump into the video."""
    if not url or not any(h in url for h in ("youtube.com", "youtu.be")):
        return text
    joiner = "&" if "?" in url else "?"

    def replace(match: re.Match) -> str:
        h, m, sec = (int(g) for g in match.groups())
        total = h * 3600 + m * 60 + sec
        return f"[{duration(total)}]({url}{joiner}t={total}s)"

    return _STAMP_RE.sub(replace, text)


def _slugify(text: str, limit: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit].strip("-")
    return slug or "answer"


def _answer_name(question: str) -> str:
    """Readable, but unique per question: the slug alone is ASCII-only and
    truncated, so a Cyrillic question, or two sharing their first 60
    characters, would overwrite each other's answer."""
    digest = hashlib.sha1(question.strip().encode("utf-8")).hexdigest()[:8]
    return f"{_slugify(question)}-{digest}"


def _wrap(text: str, width: int = 88) -> str:
    """Soft-wrap the transcript so it reads in a terminal and diffs sanely."""
    import textwrap

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()] or [text.strip()]
    return "\n\n".join(textwrap.fill(p, width=width) for p in paragraphs)
