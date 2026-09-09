"""Turn a transcript into the thing you actually wanted: a summary or an answer."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import CLAUDE_MODEL

# Well below any context limit, and small enough that the model stays sharp
# across the whole window rather than skimming.
MAP_THRESHOLD = 320_000
MAP_PIECE = 220_000

SUMMARY_TASK = """\
You are reading the transcript of a video. It came from automatic speech
recognition, so expect mis-heard words, missing punctuation and no speaker
labels; read through those errors rather than commenting on them.

Write a briefing for someone deciding whether they need to watch this video.
Use Markdown:

## TL;DR
Three or four sentences on what this video is and what it argues or teaches.

## Key points
The substantive claims, findings, steps or arguments, as bullets. Be specific:
prefer actual numbers, names, tools and conclusions over vague gestures at
topics. Aim for 5-12 bullets, ordered by importance rather than by when they
were said.

## Details worth keeping
Anything concrete a viewer would want to write down: commands, figures,
recommendations, references, caveats. Omit this section if there is nothing
worth keeping.

## Skip it if
One or two lines on who would get nothing from this video.

Do not pad. If the transcript is thin, say so plainly and keep it short.
"""

QUESTION_TASK = """\
You are reading the transcript of a video. It came from automatic speech
recognition, so expect mis-heard words and missing punctuation; read through
those errors rather than commenting on them.

Answer this question using the transcript:

{question}

Lead with the direct answer, then support it with what the video actually says,
quoting briefly where a quote carries more than a paraphrase would. If the
transcript only partly covers the question, answer the part it covers and say
plainly what it does not address. If it does not address the question at all,
say so instead of guessing.
"""

REDUCE_TASK = """\
Below are notes taken from consecutive parts of one long video transcript.
Merge them into a single briefing covering the whole video, following exactly
this structure:

## TL;DR
## Key points
## Details worth keeping
## Skip it if

Remove repetition across the parts, keep specifics (numbers, names, tools),
and order key points by importance rather than by when they appeared.
"""


# Claude follows a language name far more reliably than an ISO code.
LANGUAGE_NAMES = {
    "cs": "Czech", "sk": "Slovak", "en": "English", "de": "German",
    "fr": "French", "es": "Spanish", "it": "Italian", "pl": "Polish",
    "ru": "Russian", "uk": "Ukrainian", "pt": "Portuguese", "nl": "Dutch",
    "sv": "Swedish", "da": "Danish", "no": "Norwegian", "fi": "Finnish",
    "hu": "Hungarian", "ro": "Romanian", "bg": "Bulgarian", "hr": "Croatian",
    "sr": "Serbian", "sl": "Slovenian", "el": "Greek", "tr": "Turkish",
    "ar": "Arabic", "he": "Hebrew", "hi": "Hindi", "ja": "Japanese",
    "ko": "Korean", "zh": "Chinese", "vi": "Vietnamese", "th": "Thai",
    "id": "Indonesian", "ca": "Catalan", "et": "Estonian", "lv": "Latvian",
    "lt": "Lithuanian",
}


def language_name(code: str | None) -> str | None:
    if not code:
        return None
    code = code.split("-")[0].lower()
    return LANGUAGE_NAMES.get(code, code)


def _language_clause(code: str | None) -> str:
    """Instruct the model to answer in the video's own language."""
    name = language_name(code)
    if not name or name == "English":
        return ""
    return (
        f"\n\nWrite your entire response in {name}, the language of the video. "
        f"Translate the section headings into {name} too. Keep technical terms, "
        "product names and proper nouns in their original form.\n"
    )


class SummarizerError(RuntimeError):
    pass


class ClaudeSummarizer:
    """Shells out to the Claude Code CLI, reusing whatever auth it already has."""

    name = "claude-cli"

    def __init__(self, model: str = CLAUDE_MODEL, timeout: int = 900):
        self.model = model
        self.timeout = timeout
        if not shutil.which("claude"):
            raise SummarizerError(
                "the 'claude' CLI is not on PATH; install Claude Code or pass --no-summary"
            )

    def _ask(self, task: str, body: str) -> str:
        cmd = ["claude", "-p", task]
        if self.model:
            cmd += ["--model", self.model]
        try:
            proc = subprocess.run(
                cmd, input=body, capture_output=True, text=True, timeout=self.timeout
            )
        except subprocess.TimeoutExpired as exc:
            raise SummarizerError(f"claude timed out after {self.timeout}s") from exc
        if proc.returncode != 0:
            raise SummarizerError(f"claude failed: {(proc.stderr or '').strip()[:400]}")
        out = proc.stdout.strip()
        if not out:
            raise SummarizerError("claude returned nothing")
        return out

    def run(self, transcript: str, question: str | None = None,
            progress=lambda _m: None, language: str | None = None) -> str:
        # Summaries follow the video's language; a question is answered in
        # whatever language it was asked in, which Claude handles on its own.
        task = (
            QUESTION_TASK.format(question=question) if question
            else SUMMARY_TASK + _language_clause(language)
        )
        if len(transcript) <= MAP_THRESHOLD:
            return self._ask(task, transcript)

        parts = _split_text(transcript, MAP_PIECE)
        progress(f"transcript is long; summarising in {len(parts)} passes")
        notes = []
        for i, part in enumerate(parts, 1):
            progress(f"pass {i}/{len(parts)}")
            notes.append(self._ask(task, part))
        if question:
            # Each pass answered from partial evidence; reconcile into one answer.
            joined = "\n\n---\n\n".join(
                f"### Notes from part {i}\n{n}" for i, n in enumerate(notes, 1)
            )
            return self._ask(
                QUESTION_TASK.format(question=question)
                + "\nThe text below is partial answers from consecutive parts of the "
                  "transcript. Reconcile them into one answer, dropping repetition.",
                joined,
            )
        progress("merging passes")
        return self._ask(
            REDUCE_TASK + _language_clause(language),
            "\n\n---\n\n".join(f"### Part {i}\n{n}" for i, n in enumerate(notes, 1)),
        )


def _split_text(text: str, size: int) -> list[str]:
    """Split on paragraph or sentence boundaries, never mid-word."""
    words = text.split()
    parts, current, length = [], [], 0
    for word in words:
        if length + len(word) + 1 > size and current:
            parts.append(" ".join(current))
            current, length = [], 0
        current.append(word)
        length += len(word) + 1
    if current:
        parts.append(" ".join(current))
    return parts


def get_summarizer(model: str = CLAUDE_MODEL) -> ClaudeSummarizer:
    return ClaudeSummarizer(model=model)
