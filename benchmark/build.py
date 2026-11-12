#!/usr/bin/env python3
"""Copy the benchmark chunks from books/ to cases/.

    python3 benchmark/build.py          write cases/
    python3 benchmark/build.py --check  only compare

Each case gets source.txt (Grabar), reference.txt
(modern Armenian) and prompt.txt (prompt.md, a line
of three dashes, source.txt), ready to paste into
any chat. The files are frozen: run this again only
to add a case or to take newer corrections.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOKS = HERE.parent / "books"
DASHES = "\n---\n\n"


def read_cases():
    """The rows of cases.tsv as dicts."""
    keys = "id grabar modern first last kind ref"
    rows = []
    for ln in (HERE / "cases.tsv").read_text().split("\n"):
        if ln.startswith("#") or not ln.strip():
            continue
        row = dict(zip(keys.split(), ln.split("\t")))
        row["first"] = int(row["first"])
        row["last"] = int(row["last"])
        rows.append(row)
    return rows


def chunk(path, first, last):
    """Lines first..last (1-based) of a book file."""
    lines = (BOOKS / path).read_text().split("\n")
    return lines[first - 1 : last]


def blanks(lines):
    return [i for i, ln in enumerate(lines) if not ln]


def build_case(row):
    """The files of one case, as {name: text}."""
    a, b = row["first"], row["last"]
    src = chunk(row["grabar"], a, b)
    ref = chunk(row["modern"], a, b)
    if len(src) != len(ref) or blanks(src) != blanks(ref):
        raise SystemExit(f"{row['id']}: lines differ")
    if src[0] == "" or src[-1] == "":
        raise SystemExit(f"{row['id']}: blank edge")
    source = "\n".join(src) + "\n"
    prompt = (HERE / "prompt.md").read_text()
    return {
        "source.txt": source,
        "reference.txt": "\n".join(ref) + "\n",
        "prompt.txt": prompt + DASHES + source,
    }


def main():
    check = "--check" in sys.argv
    stale = 0
    for row in read_cases():
        folder = HERE / "cases" / row["id"]
        for name, text in build_case(row).items():
            path = folder / name
            old = (
                path.read_text() if path.exists() else None
            )
            if old != text:
                stale += 1
                if check:
                    print(
                        "differs:", path.relative_to(HERE)
                    )
            if not check:
                folder.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    if check:
        print(stale or "all", "differ" if stale else "same")
    else:
        print("cases written")


if __name__ == "__main__":
    main()
