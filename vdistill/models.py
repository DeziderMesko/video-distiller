"""Fetch and cache ONNX model files, without dragging in huggingface_hub."""

from __future__ import annotations

import shutil
import urllib.error
import urllib.request
from pathlib import Path

from .config import HF_ENDPOINT
from .config import MODEL_DIR as CACHE_DIR


class ModelFetchError(RuntimeError):
    pass


def ensure(repo: str, files: list[str], progress=lambda _m: None) -> Path:
    """Download `files` from an HF repo into a local cache. Returns the directory."""
    target = CACHE_DIR / repo.replace("/", "__")
    target.mkdir(parents=True, exist_ok=True)

    for name in files:
        dest = target / name
        if dest.exists() and dest.stat().st_size > 0:
            continue
        url = f"{HF_ENDPOINT}/{repo}/resolve/main/{name}?download=true"
        progress(f"downloading {name}")
        _download(url, dest, progress)
    return target


def _download(url: str, dest: Path, progress) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "video-distiller"})
    try:
        with urllib.request.urlopen(request) as response, tmp.open("wb") as out:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            step = max(total // 20, 1) if total else 0
            next_mark = step
            while chunk := response.read(1 << 20):
                out.write(chunk)
                done += len(chunk)
                if step and done >= next_mark:
                    progress(f"  {dest.name}: {done / 1e6:.0f}/{total / 1e6:.0f} MB")
                    next_mark += step
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        tmp.unlink(missing_ok=True)
        raise ModelFetchError(f"could not download {url}: {exc}") from exc
    shutil.move(str(tmp), str(dest))
