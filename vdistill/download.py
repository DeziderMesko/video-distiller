"""Fetch audio (and only audio) for a video URL."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from .audio import duration_of


class DownloadFailed(RuntimeError):
    pass


@dataclass
class VideoInfo:
    """What we know about a video, independent of where the audio landed."""

    video_id: str
    title: str
    url: str
    uploader: str | None
    duration: float | None
    upload_date: str | None

    @property
    def slug(self) -> str:
        keep = [c if c.isalnum() else "-" for c in self.title.lower()]
        words = "".join(keep).split("-")
        stem = "-".join(w for w in words if w)[:60].strip("-")
        return f"{stem}-{self.video_id}" if stem else self.video_id


def local_file(url: str) -> Path | None:
    """The file a "URL" points at, if it is really a path on this machine."""
    if "://" in url and not url.startswith("file://"):
        return None
    path = Path(unquote(urlparse(url).path) if url.startswith("file://") else url)
    path = path.expanduser()
    return path.resolve() if path.is_file() else None


def _local_info(path: Path) -> VideoInfo:
    """Metadata for a recording that never had a web page. The id is a hash of
    the content, so the same file is recognised wherever it is moved to."""
    # probe() and fetch_audio() both ask in one run; read the file only once.
    stat = path.stat()
    return _hashed_info(path, stat.st_size, stat.st_mtime_ns)


@lru_cache(maxsize=8)
def _hashed_info(path: Path, _size: int, _mtime_ns: int) -> VideoInfo:
    """Keyed on size and mtime as well, so an edited file is hashed afresh."""
    digest = hashlib.sha1()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    try:
        duration = duration_of(path)
    except Exception:
        duration = None
    return VideoInfo(
        video_id=f"local-{digest.hexdigest()[:10]}",
        title=path.stem,
        url=path.as_uri(),
        uploader=None,
        duration=duration,
        upload_date=None,
    )


def probe(url: str) -> VideoInfo:
    """Read a video's metadata without downloading anything."""
    local = local_file(url)
    if local is not None:
        return _local_info(local)
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as exc:
        raise DownloadFailed(f"could not read {url}: {exc}") from exc

    if info.get("_type") == "playlist":
        entries = [e for e in (info.get("entries") or []) if e]
        if not entries:
            raise DownloadFailed(f"{url} is an empty playlist")
        info = entries[0]

    return VideoInfo(
        video_id=info.get("id") or "unknown",
        title=info.get("title") or "untitled",
        url=info.get("webpage_url") or url,
        uploader=info.get("uploader") or info.get("channel"),
        duration=info.get("duration"),
        upload_date=info.get("upload_date"),
    )


def fetch_audio(url: str, dest_dir: Path, quiet: bool = False) -> tuple[VideoInfo, Path]:
    """Download the best audio-only stream. Returns metadata and the file path."""
    local = local_file(url)
    if local is not None:
        # Used in place: it is the user's file, not ours to copy or delete.
        return _local_info(local), local
    dest_dir.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(dest_dir / "source.%(ext)s"),
        "quiet": quiet,
        "no_warnings": quiet,
        "noprogress": quiet,
        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = Path(ydl.prepare_filename(info))
    except DownloadError as exc:
        raise DownloadFailed(f"download failed for {url}: {exc}") from exc

    if not path.exists():
        # yt-dlp occasionally remuxes to a different extension than it predicted.
        candidates = sorted(dest_dir.glob("source.*"))
        if not candidates:
            raise DownloadFailed(f"yt-dlp reported success but wrote nothing for {url}")
        path = candidates[0]

    meta = VideoInfo(
        video_id=info.get("id") or "unknown",
        title=info.get("title") or "untitled",
        url=info.get("webpage_url") or url,
        uploader=info.get("uploader") or info.get("channel"),
        duration=info.get("duration"),
        upload_date=info.get("upload_date"),
    )
    return meta, path


def discard_audio(*paths: Path) -> None:
    """Delete downloaded/derived audio. Safe to call on things already gone."""
    for path in paths:
        if path is None:
            continue
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
