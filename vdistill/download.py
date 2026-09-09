"""Fetch audio (and only audio) for a video URL."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


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


def probe(url: str) -> VideoInfo:
    """Read a video's metadata without downloading anything."""
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
