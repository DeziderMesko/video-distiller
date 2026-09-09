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
tight), `--no-summary`, `--data-dir`, `--backend`.

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

The int8 ONNX default is the fast path instead: it runs well above realtime on a
multi-core CPU, so a one-hour video transcribes in a few minutes.

Whisper Large v3 Turbo is a heavier model than Parakeet and will work the CPU
harder, but it only has 4 decoder layers (that's the "turbo") and int8 keeps it
practical. It is used only when you ask for a non-English language.
