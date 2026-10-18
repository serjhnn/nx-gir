#!/usr/bin/env python3
"""nx-gir command-line interface.

Run with a command (e.g. `nxgir ls`) to execute it once, or with no
arguments to open the interactive nxgir shell.
"""

import argparse
import shlex
import sys
from pathlib import Path

try:
    import readline  # noqa: F401  (enables line editing and history in input())
except ImportError:
    pass

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROMPT = "nxgir> "


def cmd_ls(args):
    """List files in the data folder."""
    if not DATA_DIR.is_dir():
        print(f"data folder not found: {DATA_DIR}", file=sys.stderr)
        return 1
    files = sorted(p for p in DATA_DIR.rglob("*") if p.is_file())
    if not files:
        print("no files in data folder")
        return 0
    for path in files:
        print(f"{path.stat().st_size:>8}  {path.relative_to(DATA_DIR)}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nxgir", description="Terminal reader for Grabar (Classical Armenian) texts."
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("ls", help="list files in the data folder").set_defaults(func=cmd_ls)
    return parser


def run(argv):
    """Parse and run one command. Returns an exit code instead of exiting."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:  # argparse exits on --help and on errors
        return e.code if isinstance(e.code, int) else 1
    if args.command is None:
        parser.print_help()
        return 0
    return args.func(args)


def shell():
    """Interactive nxgir shell."""
    print("nx-gir shell. Type 'help' for commands, 'exit' to quit.")
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
