#!/usr/bin/env python3
"""OCR tooling for scanned books.

    python3 ocr/run.py page PDF N [--out FILE]
    python3 ocr/run.py eval PDF --ref DIR --pages 26-156
                       [--sample 10] [--binarize] ...

page: OCR one page, print the text (low-confidence
      words marked with ?).
eval: OCR pages that are already typed in DIR (.txt
      files) and score them: character and word error
      rates, the confusions, and the share of words an
      LLM would have to re-read (the triage).
Page images are cached in ocr/cache/ (not in git).
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from nxocr import (  # noqa: E402
    engine,
    evaluate,
    locate,
    pages,
    prep,
)

CACHE = HERE / "cache"


def add_prep_args(ap):
    ap.add_argument("--top", type=float, default=0.10)
    ap.add_argument("--bottom", type=float, default=0.07)
    ap.add_argument("--side", type=float, default=0.0)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--deskew", action="store_true")
    ap.add_argument("--binarize", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--lang", default="hye")
    ap.add_argument("--psm", type=int, default=6)


def make_prep(a):
    return prep.Prep(
        top=a.top,
        bottom=a.bottom,
        left=a.side,
        right=a.side,
        deskew=a.deskew,
        binarize=a.binarize,
        scale=a.scale,
    )


def ocr_page(pdf, n, a):
    from PIL import Image

    path = pages.render(pdf, n, CACHE, a.dpi)
    img = prep.prepare(Image.open(path), make_prep(a))
    return engine.recognize(img, a.lang, a.psm)


def cmd_page(a):
    page = ocr_page(a.pdf, a.page, a)
    out = []
    for ln in page.lines:
        out.append(
            " ".join(
                w.text + ("?" if w.conf < a.mark else "")
                for w in ln.words
            )
        )
    text = "\n".join(out) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    else:
        sys.stdout.write(text)


def cmd_eval(a):
    texts = [
        p.read_text()
        for p in sorted(Path(a.ref).glob("*.txt"))
    ]
    ref = locate.Reference(texts)
    total = pages.count(a.pdf)
    nums = pages.parse_range(a.pages, total)
    nums = pages.spread(nums, a.sample)
    results = []
    for n in nums:
        page = ocr_page(a.pdf, n, a)
        res = evaluate.score_page(n, page.words(), ref)
        results.append(res)
        state = (
            f"CER {res.cer:6.1%}"
            if res.placed
            else "unplaced"
        )
        print(f"page {n:4d}  {state}", flush=True)
    s = evaluate.summary(results)
    report(s, a)


def report(s, a):
    print()
    print(f"pages {s['placed']}/{s['pages']} placed")
    print(f"CER {s['cer']:.1%}   WER {s['wer']:.1%}")
    print("below  re-read  errors caught  precision")
    for r in s["triage"]:
        print(
            f"{r['below']:5d}  {r['reread']:7.1%}"
            f"  {r['caught']:13.1%}  {r['precision']:9.1%}"
        )
    print("top confusions (OCR -> typed):")
    for (x, y), c in s["confusions"].most_common(15):
        print(f"  {x or '∅'} -> {y or '∅'}  {c}")
    if a.json:
        data = dict(s)
        data["confusions"] = [
            [x, y, c]
            for (x, y), c in s["confusions"].most_common()
        ]
        Path(a.json).write_text(
            json.dumps(data, ensure_ascii=False, indent=1)
            + "\n"
        )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("page")
    p.add_argument("pdf")
    p.add_argument("page", type=int)
    p.add_argument("--out")
    p.add_argument("--mark", type=float, default=60)
    add_prep_args(p)
    p.set_defaults(func=cmd_page)
    e = sub.add_parser("eval")
    e.add_argument("pdf")
    e.add_argument("--ref", required=True)
    e.add_argument("--pages", required=True)
    e.add_argument("--sample", type=int, default=0)
    e.add_argument("--json")
    add_prep_args(e)
    e.set_defaults(func=cmd_eval)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
