"""Command line for video-distiller."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, store
from .config import CHUNK_SECONDS, DATA_DIR, DEFAULT_ASR_BACKEND
from .timecode import duration


def _log(message: str) -> None:
    print(f"  → {message}", file=sys.stderr, flush=True)


def _quiet(_message: str) -> None:
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vdistill",
        description="Transcribe a video (by URL or local file) and get the answer you came for.",
    )
    parser.add_argument("--version", action="version", version=f"vdistill {__version__}")
    subs = parser.add_subparsers(dest="command")

    run = subs.add_parser("run", help="distill a video from its URL (default command)")
    run.add_argument("url", help="video URL, or the path of a local recording")
    run.add_argument("-q", "--question",
                     help="ask this instead of producing a general summary")
    run.add_argument("--backend", default=DEFAULT_ASR_BACKEND,
                     choices=["parakeet-onnx", "parakeet", "whisper"], help="ASR engine")
    run.add_argument("--model", help="override the ASR model id")
    run.add_argument("--language", help="force a language (whisper backend only)")
    run.add_argument("--chunk-seconds", type=float, default=CHUNK_SECONDS,
                     help="target chunk length; lower it if you run out of memory")
    run.add_argument("--keep-audio", action="store_true",
                     help="keep the converted WAV instead of deleting it")
    run.add_argument("--max-minutes", type=float, metavar="N",
                     help="transcribe only the first N minutes")
    run.add_argument("--no-summary", action="store_true",
                     help="stop after the transcript")
    run.add_argument("--force", action="store_true",
                     help="re-download and re-transcribe even if already stored")
    run.add_argument("--summary-language", metavar="CODE",
                     help="language for the summary (default: the video's own)")
    run.add_argument("--data-dir", type=Path, default=DATA_DIR)
    run.add_argument("--quiet", action="store_true")

    ask = subs.add_parser("ask", help="ask a stored transcript, without re-downloading")
    ask.add_argument("target", help="video id, source URL, or folder name in the data directory")
    ask.add_argument("-q", "--question", help="omit to regenerate the summary")
    ask.add_argument("--summary-language", metavar="CODE",
                     help="language for the summary (default: the video's own)")
    ask.add_argument("--data-dir", type=Path, default=DATA_DIR)
    ask.add_argument("--quiet", action="store_true")

    listing = subs.add_parser("list", help="show what has been distilled so far")
    listing.add_argument("--data-dir", type=Path, default=DATA_DIR)

    show = subs.add_parser("show", help="print a stored transcript or summary")
    show.add_argument("target")
    show.add_argument("--transcript", action="store_true",
                      help="print the transcript instead of the summary")
    show.add_argument("--data-dir", type=Path, default=DATA_DIR)

    return parser


def cmd_run(args) -> int:
    from .pipeline import distill

    progress = _quiet if args.quiet else _log
    result = distill(
        url=args.url,
        question=args.question,
        backend_name=args.backend,
        model=args.model,
        language=args.language,
        chunk_seconds=args.chunk_seconds,
        keep_audio=args.keep_audio,
        max_seconds=args.max_minutes * 60 if args.max_minutes else None,
        summarize=not args.no_summary,
        force=args.force,
        summary_language=args.summary_language,
        data_dir=args.data_dir,
        progress=progress,
    )
    if result.output:
        print()
        print(result.output)
    else:
        print(result.entry.transcript_txt)
    return 0


def cmd_ask(args) -> int:
    from .pipeline import answer

    entry = store.load(args.target, root=args.data_dir)
    if entry is None:
        print(f"nothing stored for {args.target!r}; run 'vdistill list' to see what is",
              file=sys.stderr)
        return 1
    text, _ = answer(entry, args.question, progress=_quiet if args.quiet else _log,
                     language=args.summary_language)
    print()
    print(text)
    return 0


def cmd_list(args) -> int:
    entries = store.all_entries(root=args.data_dir)
    if not entries:
        print("nothing distilled yet")
        return 0
    for entry in entries:
        marks = []
        if entry.summary_md.exists():
            marks.append("summary")
        answers = entry.dir / "answers"
        if answers.is_dir():
            count = len(list(answers.glob("*.md")))
            if count:
                marks.append(f"{count} answer{'s' if count > 1 else ''}")
        extra = f"  [{', '.join(marks)}]" if marks else ""
        print(f"{entry.info.video_id}  {duration(entry.info.duration):>8}  "
              f"{entry.info.title[:64]}{extra}")
        print(f"{'':>10}  {entry.info.url}")
    return 0


def cmd_show(args) -> int:
    entry = store.load(args.target, root=args.data_dir)
    if entry is None:
        print(f"nothing stored for {args.target!r}", file=sys.stderr)
        return 1
    path = entry.transcript_txt if args.transcript else entry.summary_md
    if not path.exists():
        print(f"{path} does not exist", file=sys.stderr)
        return 1
    print(path.read_text(encoding="utf-8"))
    return 0


def _flags(parser: argparse.ArgumentParser) -> tuple[set[str], set[str]]:
    """Every flag the parser and its subcommands accept, and which of those
    consume a following value."""
    seen, valued = set(), set()
    for action in parser._actions:
        seen.update(action.option_strings)
        if action.nargs != 0 and not isinstance(
            action, (argparse._StoreTrueAction, argparse._StoreFalseAction,
                     argparse._HelpAction, argparse._VersionAction)
        ):
            valued.update(action.option_strings)
        # choices is None on most actions, a list on things like --backend,
        # and a dict of sub-parsers on the subcommand action.
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            for sub in choices.values():
                if isinstance(sub, argparse.ArgumentParser):
                    sub_seen, sub_valued = _flags(sub)
                    seen |= sub_seen
                    valued |= sub_valued
    return seen, valued


def _protect_leading_dash(argv: list[str], parser: argparse.ArgumentParser) -> list[str]:
    """YouTube ids use the base64url alphabet, so plenty of them begin with a
    dash and argparse reads them as flags. Move the first such token to the end
    behind a "--" so `vdistill ask -OHCU9msaxs -q ...` means what it looks like.
    Putting it last matters: "--" makes everything after it positional."""
    seen, valued = _flags(parser)
    for i, token in enumerate(argv):
        if not token.startswith("-") or token == "--" or token in seen:
            continue
        if token.lstrip("-").replace(".", "", 1).isdigit():
            continue                      # a negative number, not an id
        if i and argv[i - 1] in valued:
            continue                      # the value of the preceding flag
        return argv[:i] + argv[i + 1:] + ["--", token]
    return argv


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    # `vdistill <url>` should work without typing `run`.
    commands = {"run", "ask", "list", "show"}
    if argv and argv[0] not in commands and argv[0] not in _flags(parser)[0]:
        argv.insert(0, "run")
    argv = _protect_leading_dash(argv, parser)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    handlers = {"run": cmd_run, "ask": cmd_ask, "list": cmd_list, "show": cmd_show}
    try:
        return handlers[args.command](args)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
