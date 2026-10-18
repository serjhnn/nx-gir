#!/usr/bin/env python3
"""nx-gir command-line interface.

Run with a command (e.g. `nxgir ls`) to execute it
once, or with no arguments to open the interactive
nxgir shell.
"""

import argparse
import os
import shlex
import sys
from pathlib import Path

try:
    # enables line editing and history in input()
    import readline  # noqa: F401
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROMPT = "nxgir> "

LOGO_HY = r"""
 ____                          __
/_/ / __  ____         ____ _ / /_    ____
 / / / / / __ \  ____ / __ `// __ \  / __ \
/ /_/ / / / / / /___// /_/ // / / / / / / /
\__,_/ /_/ / /__     \__, // / /_/ / / /_/
          /____/       /_//_/     /_/
""".strip("\n").splitlines()

LOGO_HY_BLOCK = r"""
  ▄▄▄                              ▄▄
 ▀███                              ██
   ██   ▄▄  ▄▄ ▄▄▄        ▄▄▄ ▄▄   ██ ▄▄▄  ▄▄ ▄▄▄
   ██   ██  ███▀██▄      ▄██▀███   ███▀███ ███████
   ██   ██  ██▀  ██ ▄▄▄▄ ██   ██   ██▀  ██ ███  ██
   ██  ▄██  ██   ██ ▀██▀ ██   ██   ██   ██ ███  ██
   ███▄███  ██   ██      ▀██▄███▄▄ ██   ██ ███  ██
    ▀▀▀▀▀▀  ▀▀   ██       ▀▀▀▀██▀▀ ██   ▀▀ ███  ▀▀
                 ███▄         ██   ██      ███
                 ▀▀▀          ▀▀   ▀▀      ▀▀
""".strip("\n").splitlines()

LOGO_EN = r"""
         _  __            _
   ____ | |/ /     ____ _(_)____
  / __ \|   /_____/ __ `/ / ___/
 / / / /   /_____/ /_/ / / /
/_/ /_/_/|_|     \__, /_/_/
                /____/
""".strip("\n").splitlines()

LOGOS = {
    "hy": LOGO_HY,
    "hy-block": LOGO_HY_BLOCK,
    "en": LOGO_EN,
}
DEFAULT_LOGO = "hy"

# Gradient endpoints (RGB), top to bottom.
RED = (200, 16, 46)
GOLD = (255, 196, 0)


def use_color():
    """True when stdout is a terminal that wants color."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def gradient(lines, start, end):
    """Color lines row by row, start to end."""
    span = max(len(lines) - 1, 1)
    out = []
    for row, line in enumerate(lines):
        t = row / span
        r, g, b = (
            round(a + (b - a) * t)
            for a, b in zip(start, end)
        )
        color = f"\033[38;2;{r};{g};{b}m"
        out.append(f"{color}{line}\033[0m")
    return out


def banner(lang=None):
    """Print the logo: 'hy', 'hy-block' or 'en'."""
    if lang is None:
        lang = os.environ.get("NXGIR_BANNER", "")
    lines = LOGOS.get(lang, LOGOS[DEFAULT_LOGO])
    if use_color():
        lines = gradient(lines, RED, GOLD)
    print("\n".join(lines))
    print()


def cmd_ls(args):
    """List files in the data folder."""
    if not DATA_DIR.is_dir():
        print(
            f"data folder not found: {DATA_DIR}",
            file=sys.stderr,
        )
        return 1
    files = sorted(
        p for p in DATA_DIR.rglob("*") if p.is_file()
    )
    if not files:
        print("no files in data folder")
        return 0
    for path in files:
        size = path.stat().st_size
        name = path.relative_to(DATA_DIR)
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
    sub.add_parser(
        "ls", help="list files in the data folder"
    ).set_defaults(func=cmd_ls)
    p = sub.add_parser("banner", help="print the logo")
    p.add_argument(
        "lang",
        nargs="?",
        default="hy",
        choices=sorted(LOGOS),
        help=(
            "hy = Armenian (default),"
            " hy-block = Armenian blocks,"
            " en = Latin"
        ),
    )
    p.set_defaults(func=cmd_banner)
    return parser


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
    banner()
    print(
        "nx-gir shell. Type 'help' for commands,"
        " 'exit' to quit."
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
