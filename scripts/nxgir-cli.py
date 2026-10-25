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
BOOKS_DIR = ROOT / "books"
# folders shown in the bookshelf, in this order
SHELVES = (BOOKS_DIR, DATA_DIR)
# notes about a shelf, not books: left off the list
NOT_BOOKS = {"SOURCES.md", "README.md"}
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


def shelf_files():
    """[(name, size, path)] for every file in books/
    and data/; name is the path inside its folder."""
    out = []
    for root in SHELVES:
        if not root.is_dir():
            continue
        files = sorted(
            p
            for p in root.rglob("*")
            if p.is_file() and p.name not in NOT_BOOKS
        )
        out += [
            (str(p.relative_to(root)), p.stat().st_size, p)
            for p in files
        ]
    return out


def cmd_bookshelf(args):
    """Browse the books in books/ and data/."""
    if not any(root.is_dir() for root in SHELVES):
        print(
            f"no books/ or data/ folder in {ROOT}",
            file=sys.stderr,
        )
        return 1
    files = shelf_files()
    tty = sys.stdin.isatty() and sys.stdout.isatty()
    if tty and not args.plain:
        import nxgir_browse

        nxgir_browse.browse(files, "bookshelf")
        return 0
    if not files:
        print("no books found")
        return 0
    for name, size, _ in files:
        print(f"{size:>8}  {name}")
    return 0


def cmd_banner(args):
    """Print the logo."""
    banner(args.lang)
    return 0


def cmd_abbr(args):
    """List manuscript abbreviations, or expand one."""
    import shutil

    import nxgir_grabar as grabar

    table = grabar.load()
    width = shutil.get_terminal_size().columns
    if not args.word:
        print("\n".join(grabar.lines(table, width)))
        print()
        print(grabar.sources_line())
        return 0
    hits = grabar.expand(args.word, table)
    for full, a in hits:
        line = f"{args.word} → {full}"
        more = f"  · {a.meaning}"
        if len(line + more) < width:
            print(line + more)
        else:
            print(f"{line}\n{more}")
        for line in grabar.example_lines(a):
            print(line)
        if "N" in a.sources:
            print("  not in a published source yet")
    if hits:
        return 0
    joined = grabar.expand_prefix(args.word, table)
    for full, pre, a in joined:
        print(f"{args.word} → {full}")
        print(f"  {pre}- {grabar.PREFIXES[pre]}")
        print(f"  + {a.short} = {a.full} · {a.meaning}")
    if joined:
        print("joined preposition: a grammar rule,")
        print("not an entry of the sources")
        return 0
    found = grabar.search(args.word, table)
    if not found:
        print(f"no abbreviation found: {args.word}")
        return 1
    print("\n".join(grabar.lines(found, width)))
    return 0


def cmd_word(args):
    """Say what a Grabar word means."""
    import nxgir_grabar as grabar

    lang = "hy" if args.hy else "en"
    lines = grabar.define(args.word, lang=lang)
    if not lines:
        print(f"not in the vocabulary: {args.word}")
        return 1
    print("\n".join(lines))
    return 0


def cmd_notes(args):
    """Print the notes written in the reader."""
    import shutil
    import textwrap

    from nxgir_state import State

    st = State.load()
    books = sorted(
        k
        for k, b in st.books.items()
        if st.notes(k) and (args.book or "") in k
    )
    if not books:
        if args.book:
            print(f"no notes for: {args.book}")
            return 1
        print("no notes yet (O in the reader adds one)")
        return 0
    width = min(shutil.get_terminal_size().columns, 80)
    for n, book in enumerate(books):
        if n:
            print()
        print(book)
        for note in st.notes(book):
            line = note["pos"][0] + 1
            date = note.get("date", "")
            print(
                f"  line {line}"
                + (f" · {date}" * bool(date))
            )
            if note.get("quote"):
                print(f"  «{note['quote']}»")
            for t in textwrap.wrap(
                note["text"], max(width - 4, 20)
            ):
                print(f"    {t}")
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
        "bookshelf", help="browse books/ and data/"
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
    p = sub.add_parser(
        "notes",
        help="print the notes written in the reader",
    )
    p.add_argument(
        "book",
        nargs="?",
        help="only books whose path has this text",
    )
    p.set_defaults(func=cmd_notes)
    p = sub.add_parser("grabar", help="Grabar helpers")
    tools = p.add_subparsers(dest="tool", required=True)
    p = tools.add_parser(
        "abbr",
        help="manuscript abbreviations (expand a word,"
        " or list them all)",
    )
    p.add_argument(
        "word",
        nargs="?",
        help="a short form (ած, ԱԾ, ա՟ծ) or any text",
    )
    p.set_defaults(func=cmd_abbr)
    p = tools.add_parser(
        "word",
        help="what a word means (from Wiktionary;"
        " inflected forms work too)",
    )
    p.add_argument("word", help="e.g. լուսնի, զլուսինն")
    p.add_argument(
        "--hy",
        action="store_true",
        help="the meaning in Armenian (from the"
        " Armenian Wiktionary)",
    )
    p.set_defaults(func=cmd_word)
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
