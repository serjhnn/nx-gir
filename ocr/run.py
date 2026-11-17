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
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from nxocr import (  # noqa: E402
    engine,
    evaluate,
    lines,
    locate,
    pages,
    prep,
    train,
)

CACHE = HERE / "cache"
MODELS = HERE / "models"
BASE = CACHE / "base"
SYSTEM_TESSDATA = Path(
    "/usr/share/tesseract-ocr/5/tessdata"
)
BASE_URL = (
    "https://raw.githubusercontent.com/tesseract-ocr/"
    "tessdata_best/main/hye.traineddata"
)


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
    ap.add_argument("--tessdata")


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


def prepared(pdf, n, a):
    from PIL import Image

    path = pages.render(pdf, n, CACHE, a.dpi)
    return prep.prepare(Image.open(path), make_prep(a))


def ocr_page(pdf, n, a, img=None):
    img = img or prepared(pdf, n, a)
    return engine.recognize(
        img,
        a.lang,
        a.psm,
        a.tessdata or default_tessdata(a),
    )


def default_tessdata(a):
    """ocr/models, when it holds the language asked for."""
    if (MODELS / f"{a.lang}.traineddata").exists():
        return MODELS
    return None


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


def cmd_base(a):
    import urllib.request

    BASE.mkdir(parents=True, exist_ok=True)
    out = BASE / "hye.traineddata"
    if not out.exists():
        urllib.request.urlretrieve(BASE_URL, out)
    # the configs (lstm.train, ...) a tessdata folder needs
    for name in ("configs", "tessconfigs"):
        src = SYSTEM_TESSDATA / name
        if src.exists() and not (BASE / name).exists():
            shutil.copytree(src, BASE / name)
    print(out, out.stat().st_size, "bytes")


def cmd_samples(a):
    """Line images + text, split into train and eval."""
    from PIL import Image  # noqa: F401

    base = BASE / "hye.traineddata"
    chars = lines.model_chars(base)
    texts = [
        p.read_text()
        for p in sorted(Path(a.ref).glob("*.txt"))
    ]
    ref = locate.Reference(texts)
    nums = pages.parse_range(a.pages, pages.count(a.pdf))
    out = Path(a.out)
    found = {}
    for n in nums:
        img = prepared(a.pdf, n, a)
        page = ocr_page(a.pdf, n, a, img)
        start, got = lines.split_lines(
            page, ref, chars, a.max_cer, img.size
        )
        found[n] = (start, got, img)
        print(
            f"page {n:4d}  {len(got):3d} lines", flush=True
        )
    # a page scanned twice must not be in both sets
    held = [
        v[0]
        for n, v in found.items()
        if v[0] is not None and train.fold(n, nums[0])
    ]
    total = {"train": 0, "eval": 0, "leak": 0}
    for n, (start, got, img) in found.items():
        if start is None:
            continue
        test = train.fold(n, nums[0])
        near = any(abs(start - h) < 300 for h in held)
        if near and not test:
            total["leak"] += len(got)
            continue
        part = "eval" if test else "train"
        for k, smp in enumerate(got):
            train.write_sample(
                out / part,
                f"p{n:04d}-{k:02d}",
                img.crop(smp.box),
                smp.text,
            )
            total[part] += 1
    print(total)
    for part in ("train", "eval"):
        k = train.make_lstmf(out / part, BASE)
        print(part, k, "lstmf")


def cmd_train(a):
    base = BASE / "hye.traineddata"
    lstm = BASE / "hye.lstm"
    train.extract_lstm(base, lstm)
    work = Path(a.out) / "run"
    prefix = train.fine_tune(
        base,
        lstm,
        Path(a.out) / "train",
        Path(a.out) / "eval",
        work,
        a.steps,
        a.rate,
    )
    MODELS.mkdir(exist_ok=True)
    target = MODELS / f"{a.name}.traineddata"
    train.finalize(prefix, base, target)
    print(target, target.stat().st_size, "bytes")


def cmd_eval(a):
    texts = [
        p.read_text()
        for p in sorted(Path(a.ref).glob("*.txt"))
    ]
    ref = locate.Reference(texts)
    total = pages.count(a.pdf)
    nums = pages.parse_range(a.pages, total)
    if a.heldout:
        nums = [n for n in nums if train.fold(n, nums[0])]
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
    e.add_argument("--heldout", action="store_true")
    add_prep_args(e)
    e.set_defaults(func=cmd_eval)
    b = sub.add_parser("base")
    b.set_defaults(func=cmd_base)
    m = sub.add_parser("samples")
    m.add_argument("pdf")
    m.add_argument("--ref", required=True)
    m.add_argument("--pages", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--max-cer", type=float, default=0.5)
    add_prep_args(m)
    m.set_defaults(func=cmd_samples)
    t = sub.add_parser("train")
    t.add_argument("--out", required=True)
    t.add_argument("--name", default="hye_grabar")
    t.add_argument("--steps", type=int, default=3000)
    t.add_argument("--rate", type=float, default=0.0002)
    t.set_defaults(func=cmd_train)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
