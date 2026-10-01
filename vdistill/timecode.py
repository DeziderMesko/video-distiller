"""Seconds as text. Dependency-free, so scripts/ can import it without the venv."""

from __future__ import annotations


def stamp(seconds: float) -> str:
    """The fixed-width HH:MM:SS used for [HH:MM:SS] transcript markers."""
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def duration(seconds: float | None) -> str:
    """A length for people to read: H:MM:SS, or M:SS under an hour."""
    if seconds is None:
        return "?"
    minutes, secs = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"
