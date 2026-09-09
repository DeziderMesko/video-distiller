"""Paths and tunable defaults, overridable by environment."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.environ.get("VDISTILL_DATA_DIR", PROJECT_ROOT / "data"))
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
