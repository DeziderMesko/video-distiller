# video-distiller

Point it at a video URL. It downloads the audio, transcribes it locally with
[Parakeet Unified EN 0.6B](https://huggingface.co/nvidia/parakeet-unified-en-0.6b),
deletes the audio, and hands you either a summary or the answer to your
question. The transcript stays in the data directory next to the URL it came from.

```bash
vdistill "https://www.youtube.com/watch?v=..."
vdistill "https://www.youtube.com/watch?v=..." -q "does he explain how the cache is invalidated?"
vdistill ~/Downloads/meeting-recording.m4a     # a local file works too, and is left in place
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

### Where results go

Transcripts and summaries are kept out of this repository. Point
`VDISTILL_DATA_DIR` at a folder of your own in a `.env` file beside
`pyproject.toml` (git-ignored, and read by vdistill itself, so it applies however
you run it; a real environment variable overrides it):

```bash
echo 'VDISTILL_DATA_DIR=/mnt/e/video-distiller' > .env
```

Without it, results fall back to `data/` in the repo, which is git-ignored too.

## Commands

| Command | What it does |
| --- | --- |
| `vdistill <url>` | download → transcribe → delete audio → summarise |
| `vdistill <url> -q "..."` | same, but answers your question instead of summarising |
| `vdistill ask <id\|url> -q "..."` | ask again against a stored transcript, no re-download |
| `vdistill list` | everything distilled so far |
| `vdistill show <id> [--transcript]` | print a stored summary or transcript |

Useful flags: `--keep-audio`, `--chunk-seconds 180` (lower it if memory is
tight), `--no-summary`, `--data-dir`, `--backend`, `--summary-language`,
`--max-minutes 25` (transcribe only the start of a long video; the summary is
told it is partial).

Each run reports how fast transcription went, e.g. `transcribed 11.7 min in
41 s (17.1x realtime)`, and stores it in `meta.json` as `transcribe_seconds`,
`transcribed_audio_seconds` and `realtime_factor`.

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
| `parakeet-dml` | same Parakeet, fp32 ONNX, encoder on a DirectML GPU | 2515 MB | English only |

For comparison, what we are *not* downloading: the fp32 ONNX Parakeet (2515 MB),
the fp16 Whisper turbo repos that most guides point at (1622 MB), and plain
`large-v3` (3091 MB).

Models download lazily on first use, into `~/.cache/vdistill/models` (Parakeet)
and `~/.cache/huggingface` (Whisper). Nothing is fetched until you actually pick
that backend, so installing the package costs no disk.

`parakeet-dml` is the one exception to "quantised only": DirectML cannot run
int8 graphs. See [GPU on Windows](#gpu-on-windows-parakeet-dml).

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

`INDEX.md`, in the data directory, is a table of everything distilled so far,
linking to each summary and transcript. Rebuild it after adding videos:

```bash
python scripts/build_index.py
```

To hand a subset to someone else as a standalone public repository:

```bash
python scripts/export_public.py ../millennium-machines-transcripts
```

## What lands in the data directory

```
some-video-title-dQw4w9WgXcQ/
├── meta.json             # source URL, title, channel, duration, ASR model used
├── transcript.txt        # the transcript, with the source URL in its header
├── transcript.timed.txt  # same text, one line per segment, [HH:MM:SS] prefixed
├── transcript.json       # text plus segment timings, for anything programmatic
├── summary.md
└── answers/
    └── does-he-explain-how-the-cache-is-invalidated.md
```

`index.jsonl` gets one line per transcription run.

## How it works

1. **Download** — `yt-dlp` takes the best audio-only stream. Video is never fetched.
   A local file is read in place instead: never copied, never deleted.
2. **Normalise** — ffmpeg decodes to 16 kHz mono PCM.
3. **Chunk** — anything over ~5 minutes is split. Cut points come from ffmpeg's
   `silencedetect`, snapped to the nearest pause, so splits rarely land
   mid-word. This also caps memory, since attention cost grows with the square
   of chunk length.
4. **Transcribe** — each chunk goes through Parakeet; segment timestamps are
   shifted back onto the original timeline.
5. **Delete** — audio is removed once the transcript is safely on disk, and
   also when transcription fails, so `work/` does not fill up.
6. **Distil** — the transcript goes to Claude for a summary or an answer. Very
   long transcripts are summarised in passes and then merged.

## Speed

Inside WSL everything runs on the CPU: an AMD RX 580 (Polaris/gfx803) can't
be reached from there. ROCm dropped that architecture years ago, and WSL2 GPU
passthrough for AMD needs RDNA3. On native Windows, though, DirectML does run
on it. That is what `parakeet-dml` uses (see below).

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

On the 26.5 min Plasticity video, with every variant fed the same audio:

| Setup | Throughput | Transcript vs fp32 at 60 s chunks |
| --- | --- | --- |
| `parakeet-onnx` int8, 300 s chunks (default) | 11.2x | ~20 words differ |
| `parakeet-onnx` int8, 60 s chunks | 20.2x | ~21 words differ |
| `parakeet-onnx` fp32, 60 s chunks | 16.8x | (reference) |
| `parakeet-dml`, RX 580, 60 s chunks | **49.9x** | identical, timestamps too |

Most int8/fp32 differences are punctuation or filler words, but int8 also
garbled terms that matter, such as "Edge Align" ("a line") and the
discount code "lead10" ("leed10"). Shorter chunks changed only filler words.

## GPU on Windows (`parakeet-dml`)

sherpa-onnx's wheels are built without DirectML, so `vdistill/directml.py`
redoes what sherpa-onnx does for Parakeet: the same kaldi-native-fbank
features and NeMo normalisation, then greedy RNN-T decoding. Around that sits
an `onnxruntime-directml` encoder session, and the GPU encodes the next chunk
while the CPU decodes the current one. It defaults to 60 s chunks, because
the DirectML encoder slows sharply on long inputs (~95x realtime at 60 s,
~15x at 300 s).

Setup: give it a Windows Python 3.12 venv of its own, holding only what it
needs. It reads the code straight from the WSL checkout through a `.pth` file
(paths are examples):

```bat
py -3.12 -m venv E:\vdistill-win\envs\dml
E:\vdistill-win\envs\dml\Scripts\pip install onnxruntime-directml kaldi-native-fbank yt-dlp numpy
echo \\wsl.localhost\<distro>\path\to\video-distiller> E:\vdistill-win\envs\dml\Lib\site-packages\vdistill-src.pth
```

Keep faster-whisper out of that env. It pulls in plain `onnxruntime`, which
uses the same `onnxruntime` import name as `onnxruntime-directml` and
silently replaces it.

Then run vdistill with `--backend parakeet-dml`, or set
`VDISTILL_ASR_BACKEND=parakeet-dml`. It is English only. For other languages,
run Whisper from WSL. Set `VDISTILL_DATA_DIR` and `VDISTILL_MODEL_DIR` as real
environment variables: the repo's `.env` holds WSL paths, and a real variable
wins over it. Summaries need the Windows `claude` CLI to be logged in.
