#!/usr/bin/env python3
"""nx-gir command-line interface."""

import argparse
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


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


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nxgir", description="Terminal reader for Grabar (Classical Armenian) texts."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ls", help="list files in the data folder").set_defaults(func=cmd_ls)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
