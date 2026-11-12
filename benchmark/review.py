#!/usr/bin/env python3
"""A blind human review of the runs.

    python3 benchmark/review.py make [--ref] [model ...]
    python3 benchmark/review.py reveal

`make` writes review/sheet.md: for each case, each
Grabar line with the translations under it, named A,
B, C ... in a different order for each case, so you
cannot tell the models apart. `--ref` also shows the
reference. It writes review/key.json (which letter is
which model) and review/ratings.tsv, to fill in:

    case  letter  accuracy  fluency  spelling  note

each score from 1 (bad) to 5 (very good):
  accuracy  the meaning of the Grabar kept, nothing
            added or left out
  fluency   reads as good modern Eastern Armenian
  spelling  reformed spelling, rules of the prompt

`reveal` reads the ratings and prints the mean score
of each model (review/review.md). Do not open
key.json before you have rated.
"""

import json
import random
import sys
from pathlib import Path

import score

HERE = Path(__file__).resolve().parent
OUT = HERE / "review"
CRITERIA = ("accuracy", "fluency", "spelling")


def lines_of(path):
    text = path.read_text().rstrip("\n")
    return score.clean(text)[0]


def models_with_runs(case, names):
    """Models that have a run for this case."""
    runs = HERE / "runs"
    return [
        n
        for n in names
        if (runs / n / f"{case}.txt").exists()
    ]


def section(case, names, show_ref):
    """The sheet text of one case, and its key."""
    folder = HERE / "cases" / case
    src = lines_of(folder / "source.txt")
    ref = lines_of(folder / "reference.txt")
    order = models_with_runs(case, names)
    random.Random(f"nxgir-{case}").shuffle(order)
    key = {chr(65 + i): m for i, m in enumerate(order)}
    runs = {
        k: lines_of(HERE / "runs" / m / f"{case}.txt")
        for k, m in key.items()
    }
    out = [f"\n## {case}\n"]
    block = []
    for i, line in enumerate(src):
        if not line:
            continue
        out.append(f"\n{i + 1}. {line}\n")
        if show_ref:
            out.append(f"\nR: {ref[i]}\n")
        for k, text in runs.items():
            if len(text) == len(src):
                out.append(f"\n{k}: {text[i]}\n")
    for k, text in runs.items():
        if len(text) != len(src):
            block.append(f"\n### {k}: wrong line count\n\n")
            block.append("\n".join(text) + "\n")
    return "".join(out + block), key


def make(args):
    show_ref = "--ref" in args
    names = [a for a in args if a != "--ref"]
    runs = HERE / "runs"
    names = names or sorted(
        p.name for p in runs.iterdir() if p.is_dir()
    )
    OUT.mkdir(exist_ok=True)
    sheet = ["# Review sheet\n\nRate in ratings.tsv.\n"]
    keys, rows = {}, []
    for case in score.cases():
        text, key = section(case.name, names, show_ref)
        sheet.append(text)
        keys[case.name] = key
        for k in key:
            rows.append(f"{case.name}\t{k}\t\t\t\t")
    (OUT / "sheet.md").write_text("".join(sheet))
    (OUT / "key.json").write_text(
        json.dumps(keys, indent=1)
    )
    head = "case\tletter\taccuracy\tfluency\tspelling\tnote"
    (OUT / "ratings.tsv").write_text(
        head + "\n" + "\n".join(rows) + "\n"
    )
    print("written to", OUT)


def reveal():
    keys = json.loads((OUT / "key.json").read_text())
    got = {}
    lines = (OUT / "ratings.tsv").read_text().split("\n")
    for ln in lines[1:]:
        cells = ln.split("\t")
        if len(cells) < 5 or not all(cells[2:5]):
            continue
        model = keys[cells[0]][cells[1]]
        got.setdefault(model, []).append(
            [float(c) for c in cells[2:5]]
        )
    head = "| model | rated | " + " | ".join(CRITERIA)
    out = [
        head + " | mean |\n",
        "|---|--:|--:|--:|--:|--:|\n",
    ]
    for model, rows in sorted(got.items()):
        means = [
            sum(r[i] for r in rows) / len(rows)
            for i in range(3)
        ]
        cells = [f"{m:.2f}" for m in means]
        total = f"{sum(means) / 3:.2f}"
        out.append(
            f"| {model} | {len(rows)} | "
            + " | ".join(cells)
            + f" | {total} |\n"
        )
    text = "".join(out)
    (OUT / "review.md").write_text(text)
    print(text)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in (
        "make",
        "reveal",
    ):
        raise SystemExit(__doc__)
    if sys.argv[1] == "make":
        make(sys.argv[2:])
    else:
        reveal()


if __name__ == "__main__":
    main()
