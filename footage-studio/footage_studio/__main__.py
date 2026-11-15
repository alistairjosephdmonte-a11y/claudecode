"""Command line entry point.

    python3 -m footage_studio                 open the app (what the Mac app does)
    python3 -m footage_studio samples DIR     write sample clips into DIR
    python3 -m footage_studio tag DIR --demo  tag with fake tags, no API key
    python3 -m footage_studio tag DIR         tag with AI (asks for the key and consent)
    python3 -m footage_studio file DIR        file clips into Sorted/ (opt-in)
    python3 -m footage_studio undo DIR        put every filed clip back
"""

import argparse
import getpass
import os
import sys

from . import filing, media, pipeline, presets, samples, tagging
from .library import Library


def _require_ffmpeg():
    missing = media.missing_tools()
    if missing:
        sys.exit(f"ERROR: {' and '.join(missing)} not found. On a Mac: brew install ffmpeg")


def cmd_tag(args):
    _require_ffmpeg()
    library = Library(args.folder)
    preset = args.preset or library.settings["preset"]
    buckets = (presets.PRESETS[preset] if args.preset else library.settings["buckets"])
    library.save_settings(preset, buckets)
    if args.demo:
        tagger = tagging.DemoTagger()
    else:
        todo, _ = pipeline.plan(library, "ai", args.rescan)
        count = min(len(todo), args.limit) if args.limit else len(todo)
        print("BEFORE ANYTHING IS SENT:")
        print("  " + tagging.egress_summary(count))
        try:
            answer = input(f"  Type '{tagging.CONSENT_PHRASE}' to continue: ").strip().lower()
        except EOFError:
            answer = ""
        if answer != tagging.CONSENT_PHRASE:
            sys.exit("Stopped. Nothing was sent.")
        # The key is read from a hidden prompt (or an already-set environment
        # variable) and is never taken as an argument, so it cannot end up in
        # shell history. It is held in memory only.
        key = os.environ.get("ANTHROPIC_API_KEY") or getpass.getpass("  Anthropic API key (hidden): ")
        try:
            tagger = tagging.AnthropicTagger(key, answer)
        except tagging.FatalTaggingError as e:
            sys.exit(f"Stopped. Nothing was sent. {e}")
    summary = pipeline.run_tagging(library, tagger, preset, library.settings["buckets"],
                                   limit=args.limit, rescan=args.rescan)
    print(f"Manifest: {library.manifest_path}")
    if summary["error"]:
        sys.exit(1)


def cmd_file(args):
    try:
        filing.file_clips(Library(args.folder))
    except filing.FilingError as e:
        sys.exit(f"ERROR: {e}")


def cmd_undo(args):
    filing.undo(Library(args.folder))


def cmd_samples(args):
    _require_ffmpeg()
    made = samples.make_samples(args.folder, args.count)
    print(f"Wrote {len(made)} sample clips (plus one broken clip) to {args.folder}")


def cmd_app(args):
    from . import server
    server.main(open_browser=not args.no_browser, port=args.port)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="footage_studio", description="Footage Studio")
    parser.set_defaults(func=cmd_app, no_browser=False, port=None)
    sub = parser.add_subparsers(dest="command")
    app = sub.add_parser("app", help="open the app window (default)")
    app.add_argument("--no-browser", action="store_true")
    app.add_argument("--port", type=int)
    app.set_defaults(func=cmd_app)
    tag = sub.add_parser("tag", help="tag a project folder")
    tag.add_argument("folder")
    tag.add_argument("--preset", choices=sorted(presets.PRESETS))
    tag.add_argument("--demo", action="store_true", help="fake tags, no API key, nothing sent")
    tag.add_argument("--limit", type=int, help="tag at most N clips (test run)")
    tag.add_argument("--rescan", action="store_true", help="re-tag clips that are already tagged")
    tag.set_defaults(func=cmd_tag)
    for name, func, text in (("file", cmd_file, "file tagged clips into Sorted/ (undoable)"),
                             ("undo", cmd_undo, "put every filed clip back")):
        p = sub.add_parser(name, help=text)
        p.add_argument("folder")
        p.set_defaults(func=func)
    smp = sub.add_parser("samples", help="write synthetic sample clips")
    smp.add_argument("folder")
    smp.add_argument("--count", type=int, default=9)
    smp.set_defaults(func=cmd_samples)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
