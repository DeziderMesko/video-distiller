"""Turn a transcript into the thing you actually wanted: a summary or an answer."""

from __future__ import annotations

import shutil
import subprocess

from .config import CLAUDE_MODEL

# Well below any context limit, and small enough that the model stays sharp
# across the whole window rather than skimming.
MAP_THRESHOLD = 320_000
MAP_PIECE = 220_000

# ASR reliably mangles names. Left alone, the model faithfully repeats the
# mis-hearing ("Pavel Caculin" for Tsatsouline), which then looks like a fact.
# The transcript arrives as "[HH:MM:SS] text" lines, so the model can say when
# something came up. Post-processing turns the markers into links into the video.
TIMESTAMPS = """\
Each transcript line is prefixed with the time it was spoken, as [HH:MM:SS].

Every bullet under "Key points" must end with the timestamp where that point is
discussed, copied verbatim in [HH:MM:SS] form -- the moment the point is
actually made, not where the topic is merely mentioned in passing. If a point is
developed across separate stretches of the video, give the two or three most
useful timestamps rather than a range. Bullets under "Details worth keeping"
should carry a timestamp too wherever one applies.

Do not put timestamps in the TL;DR or in "Skip it if". Never write a timestamp
that does not appear in the transcript, and never adjust one to look tidier.
If the transcript carries no timestamps, omit them everywhere.
"""

NAME_REPAIR = """\
Speech recognition mangles proper nouns worst of all: people, brands, products,
places, and field-specific jargon. Before you write, work out who and what is
actually being discussed, and use the real spelling rather than the recogniser's
phonetic guess. Spell each name the same way throughout.

A name is settled -- correct it -- when the transcript pairs it with something
identifiable: a book or product it is known for, an organisation, a field, a
collaborator. If someone is described as the author of a named book, the
author of that book is who is meant, however the recogniser spelled it.

Use each person's standard international spelling, not a phonetic rendering,
and keep that spelling even when you are writing in another language. Only
leave a name alone when context genuinely fails to settle it: then keep the
transcript's form and mark it "(sic)". Never invent a fact that is not in the
transcript merely to justify a name.
"""

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

""" + NAME_REPAIR + TIMESTAMPS

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

Transcript lines are prefixed with [HH:MM:SS]. Cite the timestamp for each
claim you make, copied verbatim, so the viewer can jump straight to it. Never
write a timestamp that is not in the transcript.

""" + NAME_REPAIR

REDUCE_TASK = """\
Below are notes taken from consecutive parts of one long video transcript.
Merge them into a single briefing covering the whole video, following exactly
this structure:

## TL;DR
## Key points
## Details worth keeping
## Skip it if

Remove repetition across the parts, keep specifics (numbers, names, tools),
and order key points by importance rather than by when they appeared. Preserve
the [HH:MM:SS] timestamps exactly as the notes give them.

""" + NAME_REPAIR


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


# Asking for name repair inline, among a dozen other demands, is unreliable:
# it worked before timestamps were added to the prompt and stopped afterwards.
# A short second pass over the finished summary has one job and does it.
NAME_PASS = """\
The text below is a summary written from an automatic speech recognition
transcript, so its proper nouns may be phonetic mis-hearings: people, brands,
products, places, technical terms.

Return the text with mis-heard proper nouns corrected to their real, standard
international spelling -- including when the text is written in another
language, where a phonetic rendering can look deceptively legitimate. Use the
surrounding context to identify who or what is meant: someone described as the
author of a named book is the author of that book, however the name is spelled.

Change nothing else. Preserve every heading, bullet, timestamp, link, number
and turn of phrase exactly as given, in the same language. Do not add, remove
or reword anything. If a name is genuinely ambiguous, leave it as it is. If
nothing needs correcting, return the text unchanged.

Output only the resulting text, with no preamble or commentary.
"""


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
            # Some failures, an expired login among them, arrive on stdout.
            reason = (proc.stderr or "").strip() or (proc.stdout or "").strip()
            raise SummarizerError(
                f"claude failed (exit {proc.returncode}): {reason[:400] or 'no output'}"
            )
        out = proc.stdout.strip()
        if not out:
            raise SummarizerError("claude returned nothing")
        return out

    def _repair_names(self, text: str, progress) -> str:
        """Second pass dedicated to fixing mis-heard proper nouns."""
        try:
            fixed = self._ask(NAME_PASS, text)
        except SummarizerError:
            return text                       # a failed polish must not lose the summary
        # A pass that mangles the structure is worse than one that does nothing.
        if not 0.5 < len(fixed) / max(len(text), 1) < 1.5:
            progress("name-repair pass returned something unexpected; keeping original")
            return text

        # Asked for the text alone, the model sometimes still reports on its
        # work first ("The text checks out -- no corrections needed"). Anchor on
        # the original opening line: drop anything before it, and if it is gone
        # altogether the structure was rewritten, so keep what we had.
        opening = text.lstrip().split("\n", 1)[0].strip()
        if not fixed.lstrip().startswith(opening):
            position = fixed.find(opening)
            if position < 0:
                progress("name-repair pass altered the structure; keeping original")
                return text
            progress("dropped a preamble from the name-repair pass")
            fixed = fixed[position:]
        return fixed

    def run(self, transcript: str, question: str | None = None,
            progress=lambda _m: None, language: str | None = None,
            repair_names: bool = True) -> str:
        # Summaries follow the video's language; a question is answered in
        # whatever language it was asked in, which Claude handles on its own.
        task = (
            QUESTION_TASK.format(question=question) if question
            else SUMMARY_TASK + _language_clause(language)
        )
        if len(transcript) <= MAP_THRESHOLD:
            out = self._ask(task, transcript)
            if repair_names:
                progress("checking proper nouns")
                out = self._repair_names(out, progress)
            return out

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
            out = self._ask(
                QUESTION_TASK.format(question=question)
                + "\nThe text below is partial answers from consecutive parts of the "
                  "transcript. Reconcile them into one answer, dropping repetition.",
                joined,
            )
            return self._repair_names(out, progress) if repair_names else out
        progress("merging passes")
        out = self._ask(
            REDUCE_TASK + _language_clause(language),
            "\n\n---\n\n".join(f"### Part {i}\n{n}" for i, n in enumerate(notes, 1)),
        )
        if repair_names:
            progress("checking proper nouns")
            out = self._repair_names(out, progress)
        return out


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
