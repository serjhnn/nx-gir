#!/usr/bin/env python3
"""nx-gir command-line interface.

Run with a command (e.g. `nxgir bookshelf`) to run it
once, or with no arguments to open the interactive
nxgir shell, where Tab completes commands.
"""

import argparse
import os
import shlex
import sys
from pathlib import Path

import nxgir_logo as logo

try:
    # line editing, history and Tab in input()
    import readline
except ImportError:
    readline = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROMPT = "nxgir> "


def use_color():
    """True when stdout is a terminal that wants color."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def gradient(lines):
    """Color lines row by row, top to bottom."""
    colors = logo.row_colors(len(lines))
    return [
        f"\033[38;2;{r};{g};{b}m{line}\033[0m"
        for line, (r, g, b) in zip(lines, colors)
    ]


def banner(lang=None):
    """Print the logo (a key of logo.LOGOS)."""
    if lang is None:
        lang = os.environ.get("NXGIR_BANNER", "")
    lines = logo.LOGOS.get(
        lang, logo.LOGOS[logo.DEFAULT_LOGO]
    )
    if use_color():
        lines = gradient(lines)
    print("\n".join(lines))
    print()


def data_files():
    """[(name, size, path)] for every file in data/."""
    files = sorted(
        p for p in DATA_DIR.rglob("*") if p.is_file()
    )
    return [
        (str(p.relative_to(DATA_DIR)), p.stat().st_size, p)
        for p in files
    ]


def cmd_bookshelf(args):
    """Browse the books in the data folder."""
    if not DATA_DIR.is_dir():
        print(
            f"data folder not found: {DATA_DIR}",
            file=sys.stderr,
        )
        return 1
    files = data_files()
    tty = sys.stdin.isatty() and sys.stdout.isatty()
    if tty and not args.plain:
        import nxgir_browse

        nxgir_browse.browse(files, "bookshelf")
        return 0
    if not files:
        print("no files in data folder")
        return 0
    for name, size, _ in files:
        print(f"{size:>8}  {name}")
    return 0


def cmd_banner(args):
    """Print the logo."""
    banner(args.lang)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nxgir",
        description=(
            "Terminal reader for Grabar"
            " (Classical Armenian) texts."
        ),
    )
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser(
        "bookshelf", help="browse the books in data/"
    )
    p.add_argument(
        "--plain",
        action="store_true",
        help="print the list instead of browsing",
    )
    p.set_defaults(func=cmd_bookshelf)
    p = sub.add_parser("banner", help="print the logo")
    p.add_argument(
        "lang",
        nargs="?",
        default=logo.DEFAULT_LOGO,
        choices=list(logo.LOGOS),
        help=", ".join(
            f"{k} = {v}"
            for k, v in logo.DESCRIPTIONS.items()
        ),
    )
    p.set_defaults(func=cmd_banner)
    return parser


SHELL_WORDS = ["help", "exit", "quit"]


def arguments(parser):
    """{command: [words it takes]} from the parser."""
    sub = next(
        a
        for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)
    )
    table = {}
    for name, p in sub.choices.items():
        words = []
        for a in p._actions:
            if a.option_strings:
                words += [
                    o
                    for o in a.option_strings
                    if o.startswith("--") and o != "--help"
                ]
            elif a.choices:
                words += list(a.choices)
        table[name] = words
    return table


def completions(before, text):
    """Words completing text; before is the line in
    front of it (e.g. "banner " and "hy")."""
    table = arguments(build_parser())
    done = before.split()
    if not done:
        options = sorted(table) + SHELL_WORDS
    elif done[0] in table and len(done) == 1:
        options = table[done[0]]
    else:
        options = []
    return [o for o in options if o.startswith(text)]


def setup_completion():
    """Tab completion in the shell (needs readline)."""
    if readline is None:
        return

    def complete(text, state):
        line = readline.get_line_buffer()
        before = line[: readline.get_begidx()]
        options = completions(before, text)
        if state < len(options):
            return options[state] + " "
        return None

    readline.set_completer(complete)
    readline.set_completer_delims(" ")
    if "libedit" in (readline.__doc__ or ""):
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")


def run(argv):
    """Parse and run one command.

    Returns an exit code instead of exiting.
    """
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse exits on --help and on errors
        return e.code if isinstance(e.code, int) else 1
    if args.command is None:
        parser.print_help()
        return 0
    return args.func(args)


def shell():
    """Interactive nxgir shell."""
    setup_completion()
    banner()
    print(
        "nx-gir shell. Type 'help' for commands,"
        " Tab to complete, 'exit' to quit."
    )
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue
        try:
            argv = shlex.split(line)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            continue
        if not argv:
            continue
        if argv[0] in ("exit", "quit", "q"):
            return 0
        if argv[0] in ("help", "?"):
            argv = ["--help"]
        run(argv)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        return shell()
    return run(argv)


if __name__ == "__main__":
    sys.exit(main())
