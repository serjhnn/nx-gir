#!/usr/bin/env python3
"""Score the model runs against the references.

    python3 benchmark/score.py            all models
    python3 benchmark/score.py opus sonnet
    python3 benchmark/score.py --worst 5  worst lines

A run is runs/<model>/<case>.txt: the model's reply
to cases/<case>/prompt.txt. Writes results/scores.json
and results/summary.md. The baseline row is the
Grabar copied as the answer: the floor.

Numbers (0-100, higher is better):
  chrF   character 6-grams of the whole text, F-score
         with recall weighted twice as much (as in
         sacreBLEU, our own code), spaces and
         punctuation left out, `եւ` read as `և`
  line   the same for each line, averaged; only when
         the line count is right
  word   F1 of the bag of words
  copy   share of the words (4 letters or more) that
         are also in the Grabar: untranslated words
The references are made by Claude, so a model that
writes like Claude scores higher. Use the numbers to
find the bad runs, and the human review (review.py)
to rank the good ones.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = re.compile("եւ|Եւ|ԵՒ")
LATIN = re.compile("[A-Za-z]")
MARKS = "«»[]"
FENCE = "```"


def normalize(text):
    """Reformed spelling of the one letter pair."""
    return (
        text.replace("եւ", "և")
        .replace("Եւ", "Եվ")
        .replace("ԵՒ", "ԵՎ")
    )


def words(text):
    return re.findall(r"\w+", normalize(text).lower())


def grams(letters, n):
    return Counter(
        letters[i : i + n]
        for i in range(len(letters) - n + 1)
    )


def chrf(hyp, ref, order=6, beta=2.0):
    """The chrF score of two texts, 0-100."""
    h = "".join(words(hyp))
    r = "".join(words(ref))
    prec, rec = [], []
    for n in range(1, order + 1):
        gh, gr = grams(h, n), grams(r, n)
        if not gh and not gr:
            continue
        hit = sum((gh & gr).values())
        prec.append(hit / sum(gh.values()) if gh else 0)
        rec.append(hit / sum(gr.values()) if gr else 0)
    if not prec:
        return 100.0
    p, r = sum(prec) / len(prec), sum(rec) / len(rec)
    if p + r == 0:
        return 0.0
    b2 = beta * beta
    return 100 * (1 + b2) * p * r / (b2 * p + r)


def word_f1(hyp, ref):
    gh, gr = Counter(words(hyp)), Counter(words(ref))
    hit = sum((gh & gr).values())
    if not hit:
        return 0.0
    p = hit / sum(gh.values())
    r = hit / sum(gr.values())
    return 100 * 2 * p * r / (p + r)


def copy_rate(hyp, src):
    known = set(words(src))
    ws = [w for w in words(hyp) if len(w) >= 4]
    if not ws:
        return 0.0
    return 100 * sum(w in known for w in ws) / len(ws)


def clean(reply):
    """The reply as lines: no code fence, no end blanks."""
    lines = reply.lstrip("﻿").rstrip().split("\n")
    fenced = False
    if lines and lines[0].startswith(FENCE):
        lines, fenced = lines[1:], True
    if lines and lines[-1].startswith(FENCE):
        lines, fenced = lines[:-1], True
    return [ln.rstrip() for ln in lines], fenced


def locked(line):
    return (
        line.startswith("[") and line.endswith("]")
    ) or line.startswith("ԳԼՈՒԽ")


def structure(src, out):
    """The rule checks; counts of what is wrong."""
    same = len(src) == len(out)
    blank = same and all(
        (a == "") == (b == "") for a, b in zip(src, out)
    )
    bad_lock = sum(
        1
        for i, ln in enumerate(src)
        if locked(ln) and (not same or out[i] != ln)
    )
    text = "\n".join(out)
    marks = sum(text.count(m) for m in MARKS) - sum(
        "\n".join(src).count(m) for m in MARKS
    )
    no_end = None
    if same:
        no_end = sum(
            1
            for a, b in zip(src, out)
            if a.endswith("։") and not b.endswith("։")
        )
    return {
        "lines": len(out),
        "lines_ok": same,
        "blank_ok": blank,
        "locked_bad": bad_lock,
        "old_spelling": len(OLD.findall(text)),
        "latin": len(LATIN.findall(text)),
        "extra_marks": max(marks, 0),
        "no_end": no_end,
    }


def passed(st):
    return (
        st["lines_ok"]
        and st["blank_ok"]
        and st["locked_bad"] == 0
        and st["old_spelling"] == 0
        and st["latin"] == 0
        and st["extra_marks"] == 0
    )


def line_scores(src, ref, out):
    """chrF of each non-blank line, or [] if misaligned."""
    if len(out) != len(ref):
        return []
    return [
        (i, chrf(b, a))
        for i, (a, b) in enumerate(zip(ref, out))
        if a or b
    ]


def score_run(case, out_lines, fenced):
    src = (case / "source.txt").read_text()
    ref = (case / "reference.txt").read_text()
    s_lines = src.rstrip("\n").split("\n")
    r_lines = ref.rstrip("\n").split("\n")
    text = "\n".join(out_lines)
    st = structure(s_lines, out_lines)
    each = line_scores(s_lines, r_lines, out_lines)
    mean = (
        sum(v for _, v in each) / len(each)
        if each
        else None
    )
    return {
        "structure_ok": passed(st),
        "fenced": fenced,
        **st,
        "chrf": chrf(text, ref),
        "line": mean,
        "word": word_f1(text, ref),
        "copy": copy_rate(text, src),
        "worst": sorted(each, key=lambda t: t[1])[:20],
    }


def cases():
    return sorted(
        p for p in (HERE / "cases").iterdir() if p.is_dir()
    )


def run_model(name, folder):
    """Scores of one model: {case id: result or None}."""
    out = {}
    for case in cases():
        if name == "(copy source)":
            text = (case / "source.txt").read_text()
        else:
            path = folder / f"{case.name}.txt"
            text = (
                path.read_text() if path.exists() else None
            )
        if text is None:
            out[case.name] = None
            continue
        lines, fenced = clean(text)
        out[case.name] = score_run(case, lines, fenced)
    return out


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def fmt(v):
    return "-" if v is None else f"{v:.1f}"


def summarize(results):
    """The markdown tables of all models."""
    ids = [c.name for c in cases()]
    cols = "model | cases | rules ok | chrF"
    cols += " | line | word | copy"
    head = f"| {cols} |\n"
    out = [head, "|---|--:|--:|--:|--:|--:|--:|\n"]
    for model, res in results.items():
        got = [r for r in res.values() if r]
        ok = sum(r["structure_ok"] for r in got)
        row = [
            model,
            f"{len(got)}/{len(ids)}",
            f"{ok}/{len(got)}",
        ]
        for key in ("chrf", "line", "word", "copy"):
            row.append(fmt(mean(r[key] for r in got)))
        out.append("| " + " | ".join(row) + " |\n")
    out.append("\n## chrF per case\n\n")
    out.append("| case | " + " | ".join(results) + " |\n")
    out.append("|---|" + "--:|" * len(results) + "\n")
    for cid in ids:
        row = [cid]
        for res in results.values():
            r = res[cid]
            mark = (
                ""
                if r is None or r["structure_ok"]
                else "*"
            )
            row.append(
                "-" if r is None else fmt(r["chrf"]) + mark
            )
        out.append("| " + " | ".join(row) + " |\n")
    out.append(
        "\n`*` a rule is broken (see scores.json).\n"
    )
    return "".join(out)


def print_worst(results, count):
    for model, res in results.items():
        for cid, r in res.items():
            if not r or not r["worst"]:
                continue
            bad = ", ".join(
                f"{i + 1}:{v:.0f}"
                for i, v in r["worst"][:count]
            )
            print(f"{model} {cid} worst lines: {bad}")


def main():
    args = sys.argv[1:]
    worst = 0
    if "--worst" in args:
        i = args.index("--worst")
        worst = int(args[i + 1])
        del args[i : i + 2]
    runs = HERE / "runs"
    names = args or sorted(
        p.name for p in runs.iterdir() if p.is_dir()
    )
    results = {
        "(copy source)": run_model("(copy source)", None)
    }
    for name in names:
        results[name] = run_model(name, runs / name)
    summary = summarize(results)
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "summary.md").write_text(summary)
    (out / "scores.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1)
    )
    print(summary)
    if worst:
        print_worst(results, worst)


if __name__ == "__main__":
    main()
