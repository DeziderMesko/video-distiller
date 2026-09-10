# video-distiller

Point it at a video URL. It downloads the audio, transcribes it locally with
[Parakeet Unified EN 0.6B](https://huggingface.co/nvidia/parakeet-unified-en-0.6b),
deletes the audio, and hands you either a summary or the answer to your
question. The transcript stays in `data/` next to the URL it came from.

```bash
vdistill "https://www.youtube.com/watch?v=..."
vdistill "https://www.youtube.com/watch?v=..." -q "does he explain how the cache is invalidated?"
```

## Install

Needs `ffmpeg` on PATH and Python 3.10+.

```bash
uv venv --python 3.12
uv pip install -e .
```

That's the whole default install — `sherpa-onnx` and `yt-dlp`, no PyTorch. The
model (663 MB) downloads on first use into `~/.cache/vdistill/models`.

Summaries shell out to the `claude` CLI, reusing the Claude Code login you
already have, so there's no extra API key. Use `--no-summary` for transcripts only.

## Commands

| Command | What it does |
| --- | --- |
| `vdistill <url>` | download → transcribe → delete audio → summarise |
| `vdistill <url> -q "..."` | same, but answers your question instead of summarising |
| `vdistill ask <id\|url> -q "..."` | ask again against a stored transcript, no re-download |
| `vdistill list` | everything distilled so far |
| `vdistill show <id> [--transcript]` | print a stored summary or transcript |

Useful flags: `--keep-audio`, `--chunk-seconds 180` (lower it if memory is
tight), `--no-summary`, `--data-dir`, `--backend`, `--summary-language`.

### Output language

Summaries are written in the language the video is spoken in — a Czech podcast
gets a Czech summary, section headings included. The language is detected during
transcription and stored in `meta.json`. Override it with
`--summary-language en` (on `run` or `ask`).

Questions are different: `-q` is answered in whatever language you asked in, so
you can ask an English question about a Czech video and get an English answer.

### Timestamps

Every bullet under "Key points" carries the time it was discussed, rendered as a
link that jumps straight into the video:

```markdown
- Most "HIIT" circuits are not actually high intensity [15:59](https://youtube.com/watch?v=...&t=959s)
```

The summariser is fed `transcript.timed.txt` (one `[HH:MM:SS]`-prefixed line per
segment) rather than the flat text, so the times come from the transcript rather
than being estimated. Answers to `-q` questions cite timestamps too. Videos
transcribed without segment timings simply get no timestamps.

### Mis-heard names

ASR mangles proper nouns more than anything else, and a summary that repeats the
mis-hearing turns it into an apparent fact — a Czech run rendered Pavel
Tsatsouline as "Pavel Caculin".

Asking for this inline, alongside every other instruction, proved unreliable: it
worked until timestamps were added to the same prompt and then stopped. So name
repair is a **separate pass** over the finished summary, whose only job is to fix
proper nouns and leave everything else — headings, bullets, timestamps, wording,
language — byte for byte alone. The result is size-checked, and a pass that fails
or returns something malformed leaves the original summary untouched.

Genuinely ambiguous names are left as transcribed rather than guessed at.

## Backends

Every option below is a *quantised* build. Vendors publish fp32/fp16 reference
weights that are 2-4x larger for the same model, and this project deliberately
does not default to those — sizes below are measured from the Hugging Face API,
not estimated.

| `--backend` | Model | Download | Languages |
| --- | --- | --- | --- |
| `parakeet-onnx` *(default)* | Parakeet Unified EN 0.6B, int8 ONNX | **663 MB** | English only |
| `whisper` | Whisper Large v3 Turbo, int8 CT2 | **818 MB** | 100 |
| `parakeet` | same Parakeet, fp32 NeMo | 2474 MB | English only |

For comparison, what we are *not* downloading: the fp32 ONNX Parakeet (2515 MB),
the fp16 Whisper turbo repos that most guides point at (1622 MB), and plain
`large-v3` (3091 MB).

Models download lazily on first use, into `~/.cache/vdistill/models` (Parakeet)
and `~/.cache/huggingface` (Whisper). Nothing is fetched until you actually pick
that backend, so installing the package costs no disk.

### Czech, Slovak and other non-English

```bash
uv pip install -e ".[whisper]"
vdistill "<url>" --language cs
```

Passing a non-English `--language` switches to Whisper automatically, since
Parakeet is English-only in every packaging — you don't have to pass
`--backend whisper` as well. `--model turbo` (the default), `large-v3` and any
CTranslate2 repo id also work.

## Index

[`INDEX.md`](INDEX.md) is a table of everything distilled so far, linking to
each summary and transcript. Rebuild it after adding videos:

```bash
python scripts/build_index.py
```

To hand a subset to someone else as a standalone public repository:

```bash
python scripts/export_public.py ../milo-transcripts
```

## What lands in data/

```
data/some-video-title-dQw4w9WgXcQ/
├── meta.json             # source URL, title, channel, duration, ASR model used
├── transcript.txt        # the transcript, with the source URL in its header
├── transcript.timed.txt  # same text, one line per segment, [HH:MM:SS] prefixed
├── transcript.json       # text plus segment timings, for anything programmatic
├── summary.md
└── answers/
    └── does-he-explain-how-the-cache-is-invalidated.md
```

`data/index.jsonl` gets one line per transcription run.

## How it works

1. **Download** — `yt-dlp` takes the best audio-only stream. Video is never fetched.
2. **Normalise** — ffmpeg decodes to 16 kHz mono PCM.
3. **Chunk** — anything over ~5 minutes is split. Cut points come from ffmpeg's
   `silencedetect`, snapped to the nearest pause, so splits rarely land
   mid-word. This also caps memory, since attention cost grows with the square
   of chunk length.
4. **Transcribe** — each chunk goes through Parakeet; segment timestamps are
   shifted back onto the original timeline.
5. **Delete** — audio is removed once the transcript is safely on disk. If
   transcription fails the audio is deliberately kept in `work/`, so retrying is cheap.
6. **Distil** — the transcript goes to Claude for a summary or an answer. Very
   long transcripts are summarised in passes and then merged.

## Speed

This is CPU-only, and that is the right call on this machine: an AMD RX 580
(Polaris/gfx803) cannot accelerate it. ROCm dropped that architecture years ago,
no current PyTorch build targets it, ROCm-on-Windows covers RDNA2/3 only, and
WSL2 GPU passthrough for AMD needs RDNA3. DirectML technically runs on Polaris
but pins you to an old torch that NeMo rejects, and it handles RNN-T's
sequential decode loop badly.

Measured on this 16-core box:

| Backend | Throughput | Example |
| --- | --- | --- |
| `parakeet-onnx` | **~9x realtime** | a 2 h video in 13m22s |
| `whisper` (turbo int8, 4 workers) | **~5x realtime** | a 71 min podcast in ~14 min |

Whisper is the slower of the two because `large-v3-turbo` is a full-size
32-layer encoder attached to a deliberately small 4-layer decoder. The encoder
dominates, which has two consequences worth knowing:

- Decoder-side tuning barely matters. Dropping beam search from 5 to 1 and
  enabling batched inference measured **1.10x** on a 120 s Czech clip -- worth
  keeping, but not the win it looks like.
- Core utilisation is everything. A single CTranslate2 stream plateaus at about
  four cores, so a sequential run used only 359% of the 1600% available. Running
  four chunks concurrently at four threads each measured **1.94x** (2.63x ->
  5.10x realtime) with byte-identical output. Tune with
  `VDISTILL_WHISPER_WORKERS`.
