"""Paths and tunable defaults, overridable by environment."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _dotenv(path: Path) -> dict[str, str]:
    """VDISTILL_* settings from a KEY=VALUE file; blank lines and # comments skipped."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    values = {}
    for line in lines:
        key, sep, value = line.strip().partition("=")
        if sep and key.strip().startswith("VDISTILL_"):
            values[key.strip()] = value.strip().strip("\"'")
    return values


# Machine-specific settings -- above all where results live, which is outside
# the repo -- go in a git-ignored .env beside pyproject.toml. It is read here
# rather than from a shell profile so every way of running vdistill sees it;
# a real environment variable still wins.
for _key, _value in _dotenv(PROJECT_ROOT / ".env").items():
    os.environ.setdefault(_key, _value)

DATA_DIR = Path(os.environ.get("VDISTILL_DATA_DIR", PROJECT_ROOT / "data")).expanduser()
WORK_DIR = Path(os.environ.get("VDISTILL_WORK_DIR", PROJECT_ROOT / "work"))

# ASR wants 16 kHz mono; everything downstream assumes it.
SAMPLE_RATE = 16_000

# Full-context attention makes memory grow with the square of chunk length.
# 300 s keeps a 0.6B model comfortable on a CPU box with ~16 GB RAM.
CHUNK_SECONDS = float(os.environ.get("VDISTILL_CHUNK_SECONDS", 300))
# How far from the ideal cut point we will hunt for a silence to cut on.
CHUNK_SLACK_SECONDS = 45.0

SILENCE_NOISE_DB = -30
SILENCE_MIN_DURATION = 0.35

# Transcript segments end at a sentence, but also at a pause this long or once
# they run this long, so that a summary always has something close to cite.
SEGMENT_PAUSE_SECONDS = 1.0
SEGMENT_MAX_SECONDS = 30.0

DEFAULT_ASR_BACKEND = os.environ.get("VDISTILL_ASR_BACKEND", "parakeet-onnx")
DEFAULT_PARAKEET_MODEL = os.environ.get(
    "VDISTILL_PARAKEET_MODEL", "nvidia/parakeet-unified-en-0.6b"
)
DEFAULT_WHISPER_MODEL = os.environ.get("VDISTILL_WHISPER_MODEL", "turbo")

CLAUDE_MODEL = os.environ.get("VDISTILL_CLAUDE_MODEL", "")

# int8 is 663 MB and faster on CPU; fp32 is 2.5 GB for a little more accuracy.
DEFAULT_ONNX_PRECISION = os.environ.get("VDISTILL_ONNX_PRECISION", "int8")

# How many 30 s Whisper windows to decode at once. Higher fills more cores at
# the cost of memory; 8 is comfortable on a 16-core box with 16 GB.
WHISPER_BATCH_SIZE = int(os.environ.get("VDISTILL_WHISPER_BATCH", 8))

# Chunks decoded concurrently. A single CTranslate2 stream plateaus around four
# cores, so parallel chunks -- not more threads per chunk -- is what fills a box.
WHISPER_WORKERS = int(os.environ.get("VDISTILL_WHISPER_WORKERS", 4))
