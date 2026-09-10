#!/usr/bin/env python3
"""Build a shareable, public-facing copy of the Millennium Machines transcripts.

The private data/ directory is the working store; this renders a subset of it
into a standalone repository that can be handed to the channel author. Re-run
it whenever new episodes land -- it rewrites the tree from scratch.

    python scripts/export_public.py ../millennium-machines-transcripts
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# Ordered: the first pattern that matches a title wins.
SERIES = [
    ("tiny-box-miley-enclosure", "Tiny Box Miley Enclosure",
     re.compile(r"Tiny Box Miley Enclosure", re.I)),
    ("ldo-miley-v2-production-kit", "LDO Miley V2.0 — full production kit",
     re.compile(r"full production kit", re.I)),
    ("ldo-miley-v2-pre-production-kit", "Milo/Miley V2.0 — LDO pre-production kit",
     re.compile(r"[Pp]re[- ]production kit", re.I)),
    ("electronics-box", "Millennium Electronics Box",
     re.compile(r"Electronics Box", re.I)),
    ("launch-party", "Milo/Miley V2.0 launch party",
     re.compile(r"Launch Party", re.I)),
]

CHANNEL = "Millennium Machine Works"


@dataclass
class Episode:
    meta: dict
    directory: Path
    series_key: str
    series_name: str
    number: int | None

    @property
    def title(self) -> str:
        # Strip the hashtag tail the channel appends to every title.
        return re.split(r"\s+#", self.meta["title"])[0].strip()

    @property
    def stem(self) -> str:
        if self.number is not None:
            return f"ep{self.number:02d}-{self.meta['video_id']}"
        return self.meta["video_id"]


def hms(seconds: float | None) -> str:
    if not seconds:
        return "?"
    seconds = int(seconds)
    return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def published(meta: dict) -> str:
    raw = meta.get("upload_date") or ""
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}" if len(raw) == 8 else "?"


def collect() -> list[Episode]:
    episodes: list[Episode] = []
    for meta_path in sorted(DATA.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        title = meta.get("title", "")
        if CHANNEL.lower() not in (meta.get("uploader") or "").lower():
            continue
        for key, name, pattern in SERIES:
            if pattern.search(title):
                number = re.search(r"Ep\s*(\d+)", title, re.I)
                episodes.append(Episode(
                    meta, meta_path.parent, key, name,
                    int(number.group(1)) if number else None,
                ))
                break
    episodes.sort(key=lambda e: (
        [k for k, _, _ in SERIES].index(e.series_key), e.number or 0
    ))
    return episodes


def summary_body(directory: Path) -> str | None:
    path = directory / "summary.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    _, sep, body = text.partition("---\n\n")   # drop our own file header
    return (body if sep else text).strip()


def render_episode(ep: Episode) -> str:
    meta, out = ep.meta, []
    out.append(f"# {ep.title}\n")
    out.append(f"**Watch:** {meta['source_url']}  ")
    out.append(f"**Channel:** {meta.get('uploader') or CHANNEL}  ")
    out.append(f"**Length:** {hms(meta.get('duration_seconds'))}  ")
    out.append(f"**Streamed:** {published(meta)}\n")
    out.append("> Automatic transcript — see the [repository README](../../README.md)")
    out.append("> for how it was made and what it gets wrong.\n")

    body = summary_body(ep.directory)
    if body:
        out.append("## Summary\n")
        # Demote the summary's own headings so they nest under this page.
        out.append(re.sub(r"^## ", "### ", body, flags=re.M) + "\n")

    timed = ep.directory / "transcript.timed.txt"
    plain = ep.directory / "transcript.txt"
    out.append("## Transcript\n")
    if timed.exists():
        out.append("```text")
        out.append(timed.read_text(encoding="utf-8").strip())
        out.append("```")
    elif plain.exists():
        text = plain.read_text(encoding="utf-8")
        _, sep, rest = text.partition("---\n")
        out.append((rest if sep else text).strip())
    return "\n".join(out) + "\n"


def render_index(episodes: list[Episode]) -> str:
    total = sum(e.meta.get("duration_seconds") or 0 for e in episodes)
    out = [
        "# Millennium Machines — stream transcripts\n",
        f"Searchable transcripts and summaries of {len(episodes)} livestreams from the",
        f"[{CHANNEL}](https://www.youtube.com/@millenniummachineworksoffi3032) YouTube",
        f"channel — **{hms(total)}** of video in total.\n",
        "This is an unofficial, fan-made archive, published so the streams can be",
        "searched and referenced by text. Every page links back to the original video,",
        "and the videos themselves remain the channel's work.\n",
    ]
    for key, name, _ in SERIES:
        group = [e for e in episodes if e.series_key == key]
        if not group:
            continue
        out.append(f"\n## {name}\n")
        out.append("| Episode | Length | Streamed | Transcript | Video |")
        out.append("| --- | --- | --- | --- | --- |")
        for ep in group:
            label = f"Ep{ep.number}" if ep.number else "—"
            out.append(
                f"| {label} | {hms(ep.meta.get('duration_seconds'))} "
                f"| {published(ep.meta)} "
                f"| [{ep.title[:52]}](transcripts/{key}/{ep.stem}.md) "
                f"| [watch]({ep.meta['source_url']}) |"
            )
    out.append("""
## How these were made

Audio only was downloaded from each public video, transcribed locally with
NVIDIA's [Parakeet Unified EN 0.6B](https://huggingface.co/nvidia/parakeet-unified-en-0.6b)
speech model, and then summarised. The audio was deleted afterwards; nothing
here is a copy of the video or its sound.

**Expect errors.** This is machine transcription of live, informal speech over
shop noise. Proper nouns suffer most — part names, supplier names and people's
names are the least reliable text on these pages. Timestamps in each summary
link to the exact second in the original video, so anything that matters can be
checked against what was actually said.

Corrections are welcome — open an issue or a pull request.
""")
    return "\n".join(out)


def main() -> int:
    target = Path(sys.argv[1]).expanduser().resolve()
    episodes = collect()
    if not episodes:
        print("no episodes matched", file=sys.stderr)
        return 1

    tree = target / "transcripts"
    if tree.exists():
        shutil.rmtree(tree)                    # rebuild cleanly each run
    for ep in episodes:
        directory = tree / ep.series_key
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{ep.stem}.md").write_text(render_episode(ep), encoding="utf-8")

    target.mkdir(parents=True, exist_ok=True)
    (target / "README.md").write_text(render_index(episodes), encoding="utf-8")
    print(f"exported {len(episodes)} episodes to {target}")
    for key, name, _ in SERIES:
        n = sum(1 for e in episodes if e.series_key == key)
        if n:
            print(f"  {n:2d}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
