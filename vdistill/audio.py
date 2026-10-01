"""ffmpeg wrangling: normalise to ASR-ready WAV and split on silence."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import (
    CHUNK_SECONDS,
    CHUNK_SLACK_SECONDS,
    SAMPLE_RATE,
    SILENCE_MIN_DURATION,
    SILENCE_NOISE_DB,
)


class AudioError(RuntimeError):
    pass


@dataclass
class Chunk:
    """A slice of the source audio, plus where it sits on the original timeline."""

    path: Path
    offset: float
    duration: float


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-5:]
        raise AudioError(f"{cmd[0]} failed: " + " | ".join(tail))
    return proc


def to_wav(src: Path, dest: Path) -> Path:
    """Decode anything ffmpeg understands into 16 kHz mono PCM."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(src),
        "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-c:a", "pcm_s16le",
        str(dest),
    ])
    return dest


def duration_of(path: Path) -> float:
    proc = _run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ])
    try:
        return float(proc.stdout.strip())
    except ValueError as exc:
        raise AudioError(f"could not read duration of {path}") from exc


def find_silences(path: Path) -> list[tuple[float, float]]:
    """Return (start, end) of every detected silent stretch."""
    proc = subprocess.run(
        [
            "ffmpeg", "-i", str(path),
            "-af", f"silencedetect=noise={SILENCE_NOISE_DB}dB:d={SILENCE_MIN_DURATION}",
            "-f", "null", "-",
        ],
        capture_output=True, text=True,
    )
    log = proc.stderr or ""
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*(-?[\d.]+)", log)]
    return [(s, e) for s, e in zip(starts, ends) if e > s]


def _cut_points(total: float, silences: list[tuple[float, float]],
                target: float, slack: float) -> list[float]:
    """Pick cut times near each target, preferring the middle of a silence."""
    midpoints = sorted((s + e) / 2 for s, e in silences)
    points: list[float] = []
    cursor = 0.0
    while total - cursor > target + slack:
        ideal = cursor + target
        window = [m for m in midpoints
                  if abs(m - ideal) <= slack and m > cursor + target * 0.4]
        # Fall back to a blind cut if this stretch has no pause to hide in.
        cut = min(window, key=lambda m: abs(m - ideal)) if window else ideal
        points.append(cut)
        cursor = cut
    return points


def split(path: Path, out_dir: Path, target: float = CHUNK_SECONDS,
          slack: float = CHUNK_SLACK_SECONDS) -> list[Chunk]:
    """Split audio into ASR-sized chunks, cutting during pauses where possible."""
    total = duration_of(path)
    if total <= target + slack:
        return [Chunk(path=path, offset=0.0, duration=total)]

    points = _cut_points(total, find_silences(path), target, slack)
    # On the sample grid, so neighbouring chunks neither overlap nor leave a gap.
    bounds = [round(t * SAMPLE_RATE) / SAMPLE_RATE for t in (0.0, *points, total)]
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks: list[Chunk] = []
    for i, (start, end) in enumerate(zip(bounds, bounds[1:])):
        piece = out_dir / f"chunk_{i:04d}.wav"
        # -ss before -i seeks the input instead of decoding up to the cut, which
        # made splitting quadratic in length; on PCM WAV it is sample-exact.
        _run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{start:.7f}", "-t", f"{end - start:.7f}", "-i", str(path),
            "-c:a", "pcm_s16le", str(piece),
        ])
        chunks.append(Chunk(path=piece, offset=start, duration=end - start))
    return chunks
