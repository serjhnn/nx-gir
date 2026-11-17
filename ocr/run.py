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
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from nxocr import (  # noqa: E402
    engine,
    evaluate,
    layout,
    lines,
    llm,
    locate,
    pages,
    post,
    prep,
    textnorm,
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
    ap.add_argument("--trim", action="store_true")
    ap.add_argument("--binarize", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--lang", default="hye")
    ap.add_argument("--psm", type=int, default=6)
    ap.add_argument("--layout", type=float, default=0)
    ap.add_argument("--tail", type=float, default=0)
    ap.add_argument("--tessdata")


def add_post_args(ap):
    ap.add_argument("--costs")
    ap.add_argument("--adapt")
    ap.add_argument("--adapt-weight", type=int, default=3)
    ap.add_argument(
        "--skip-book", action="append", default=[]
    )
    ap.add_argument("--max-conf", type=float, default=80)
    ap.add_argument("--max-cost", type=float, default=1.2)
    ap.add_argument("--min-count", type=int, default=2)
    ap.add_argument("--margin", type=float, default=0.3)
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--context", action="store_true")
    ap.add_argument("--llm", metavar="MODEL")
    ap.add_argument("--llm-files", metavar="DIR")
    ap.add_argument("--llm-conf", type=float, default=80)
    ap.add_argument("--llm-batch", type=int, default=8)
    ap.add_argument("--llm-hints", action="store_true")
    ap.add_argument("--weight", type=float, default=4.0)
    ap.add_argument("--gain", type=float, default=1.0)
    ap.add_argument("--ctx-conf", type=float, default=101)
    ap.add_argument("--ctx-cost", type=float, default=1.6)


def make_prep(a):
    return prep.Prep(
        top=a.top,
        bottom=a.bottom,
        left=a.side,
        right=a.side,
        deskew=a.deskew,
        trim=a.trim,
        binarize=a.binarize,
        scale=a.scale,
    )


def prepared(pdf, n, a):
    from PIL import Image

    path = pages.render(pdf, n, CACHE, a.dpi)
    return prep.prepare(Image.open(path), make_prep(a))


def apply_layout(page, a):
    return layout.main_text(page, a.layout, a.tail)


def ocr_page(pdf, n, a, img=None, raw=False):
    img = img or prepared(pdf, n, a)
    page = engine.recognize(
        img,
        a.lang,
        a.psm,
        a.tessdata or default_tessdata(a),
    )
    if a.layout and not raw:
        page = apply_layout(page, a)
    return page


def default_tessdata(a):
    """ocr/models, when it holds the language asked for."""
    if (MODELS / f"{a.lang}.traineddata").exists():
        return MODELS
    return None


def cached_page(pdf, n, a):
    """OCR page, kept in cache/pages until the model
    or the settings change."""
    import pickle

    model = MODELS / f"{a.lang}.traineddata"
    stamp = (
        model.stat().st_mtime_ns if model.exists() else 0
    )
    name = (
        f"{Path(pdf).stem}-{a.lang}-{stamp}-{a.psm}-{a.dpi}"
        f"-{a.top}-{a.bottom}-{a.scale}-{a.binarize}"
        f"-{a.deskew}-{a.trim}-{n}.pkl"
    )
    path = CACHE / "pages" / name
    if path.exists():
        page = pickle.loads(path.read_bytes())
    else:
        # the raw page is kept: the layout is applied after
        page = ocr_page(pdf, n, a, raw=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(page))
    return apply_layout(page, a) if a.layout else page


def cmd_page(a):
    """OCR one page. The text is the engine's own; word
    list suggestions go to --review, and change the text
    only with --apply."""
    img = prepared(a.pdf, a.page, a)
    page = ocr_page(a.pdf, a.page, a, img)
    changes = []
    if a.suggest or a.apply or a.review:
        a.post = True
        lex, costs = load_post(a)
        changes = apply_post(a, page, lex, costs, a.apply)
    if a.llm or a.llm_files:
        lex = costs = None
        if a.llm_hints:
            lex, costs = load_post(a)
        got, _ = llm_page(
            a, llm_backend(a), page, img, lex, costs
        )
        if a.apply:
            for c in got:
                page.lines[c.line].words[
                    c.word
                ].text = c.new
        changes += got
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
    if a.review:
        Path(a.review).write_text(
            post.review(changes, a.page, head=True)
        )
    elif changes:
        sys.stderr.write(post.review(changes, a.page))
    if changes:
        done = "applied" if a.apply else "suggested"
        print(f"{len(changes)} {done}", file=sys.stderr)


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


_CTX = {}


def _init_sampler(a, chars, ref):
    import os

    # one thread per Tesseract: the pages run in parallel
    os.environ["OMP_THREAD_LIMIT"] = "1"
    _CTX.update(a=a, chars=chars, ref=ref)


def _sample_page(n):
    """(page, start, [(Sample, image)]) for a page."""
    a = _CTX["a"]
    img = prepared(a.pdf, n, a)
    page = ocr_page(a.pdf, n, a, img)
    start, got = lines.split_lines(
        page,
        _CTX["ref"],
        _CTX["chars"],
        a.max_cer,
        img.size,
    )
    return n, start, [(s, img.crop(s.box)) for s in got]


def cmd_samples(a):
    """Line images + text, split into train and eval."""
    from concurrent.futures import ProcessPoolExecutor

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
    with ProcessPoolExecutor(
        a.jobs,
        initializer=_init_sampler,
        initargs=(a, chars, ref),
    ) as pool:
        for n, start, got in pool.map(_sample_page, nums):
            found[n] = (start, got)
            print(
                f"page {n:4d}  {len(got):3d} lines",
                flush=True,
            )
    # a page scanned twice must not be in both sets
    held = [
        v[0]
        for n, v in found.items()
        if v[0] is not None and train.fold(n, nums[0])
    ]
    total = {"train": 0, "eval": 0, "leak": 0}
    for n, (start, got) in found.items():
        if start is None:
            continue
        test = train.fold(n, nums[0])
        near = any(abs(start - h) < 300 for h in held)
        if near and not test:
            total["leak"] += len(got)
            continue
        part = "eval" if test else "train"
        for k, (smp, crop) in enumerate(got):
            train.write_sample(
                out / part,
                f"p{n:04d}-{k:02d}",
                crop,
                smp.text,
            )
            total[part] += 1
    print(total)
    for part in ("train", "eval"):
        k = train.make_lstmf(out / part, BASE)
        print(part, k, "lstmf")


def cmd_train(a):
    base = BASE / "hye.traineddata"
    # start from the stock model, or from one of ours
    start = (
        MODELS / f"{a.start}.traineddata"
        if a.start
        else base
    )
    lstm = CACHE / f"start-{a.start or 'hye'}.lstm"
    train.extract_lstm(start, lstm)
    work = Path(a.out) / f"run-{a.name}"
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


def eval_pages(a):
    """Page numbers asked for, by --heldout and --half."""
    nums = pages.parse_range(a.pages, pages.count(a.pdf))
    first = nums[0]
    if a.heldout or a.half:
        nums = [n for n in nums if train.fold(n, first)]
    if a.half:
        nums = [
            n
            for n in nums
            if train.half(n, first) == a.half
        ]
    return pages.spread(nums, a.sample)


def adapt_texts(a, ref):
    """The typed book without the held-out pages.

    Its words and word pairs teach the models the book's
    own language. The held-out pages (dev and test) are cut
    out, with some slack, so no page is scored against
    text it was in.
    """
    nums = pages.parse_range(a.pages, pages.count(a.pdf))
    spans = []
    for n in nums:
        if not train.fold(n, nums[0]):
            continue
        page = cached_page(a.pdf, n, a)
        k = "".join(
            textnorm.key(w.text) for w in page.words()
        )
        span = ref.locate(k)
        if span:
            spans.append(span)
    return ref.without(spans)


def load_post(a, ref=None):
    import json

    skip = tuple(a.skip_book)
    extra = ()
    if a.adapt:
        texts = [
            p.read_text()
            for p in sorted(Path(a.adapt).glob("*.txt"))
        ]
        ref = locate.Reference(texts)
        # no pages given (page): a new page, no masking
        parts = (
            adapt_texts(a, ref)
            if getattr(a, "pages", None)
            else texts
        )
        extra = [(t, a.adapt_weight) for t in parts]
    lex = post.Lexicon.from_repo(
        ROOT, skip=skip, extra=extra
    )
    data = []
    if a.costs:
        data = json.loads(Path(a.costs).read_text())
        data = data["confusions"]
    return lex, post.Costs(data)


def post_params(a):
    return post.Params(
        max_conf=a.max_conf,
        max_cost=a.max_cost,
        min_count=a.min_count,
        margin=a.margin,
        names=a.names,
    )


def context_params(a):
    return post.ContextParams(
        max_conf=a.ctx_conf,
        max_cost=a.ctx_cost,
        weight=a.weight,
        gain=a.gain,
        names=a.names,
    )


def apply_post(a, page, lex, costs, apply=True):
    """The steps asked for (--post, --context) on a page.

    With apply (what eval does, on a copy, to measure what
    the suggestions are worth) the text is changed.
    """
    changes = []
    if a.post:
        changes += post.correct(
            page, lex, costs, post_params(a), apply
        )
    if a.context:
        changes += post.context(
            page, lex, costs, context_params(a), apply
        )
    return changes


def llm_backend(a):
    if a.llm_files:
        return llm.Files(a.llm_files)
    return llm.Anthropic(a.llm, cache=CACHE / "llm")


def llm_page(a, backend, page, img, lex=None, costs=None):
    """(Corrections, lines sent) of the LLM pass."""
    images = {}
    for n, ln in enumerate(page.lines):
        if any(w.conf < a.llm_conf for w in ln.words):
            box = lines.line_box(ln, size=img.size)
            images[n] = llm.png_bytes(img.crop(box))
    return llm.suggest(
        page,
        backend,
        a.llm_conf,
        lex,
        costs,
        images,
        a.llm_batch,
    )


def cmd_eval(a):
    import copy

    texts = [
        p.read_text()
        for p in sorted(Path(a.ref).glob("*.txt"))
    ]
    ref = locate.Reference(texts)
    nums = eval_pages(a)
    ocr = {n: cached_page(a.pdf, n, a) for n in nums}
    results = []
    for n in nums:
        res = evaluate.score_page(n, ocr[n].words(), ref)
        results.append(res)
        state = (
            f"CER {res.cer:6.1%}"
            if res.placed
            else "unplaced"
        )
        print(f"page {n:4d}  {state}", flush=True)
    s = evaluate.summary(results)
    report(s, a)
    if a.llm or a.llm_files:
        eval_llm(a, nums, ocr, ref, results)
    if not (a.post or a.context):
        return
    lex, costs = load_post(a)
    after, changes = [], []
    for n in nums:
        page = copy.deepcopy(ocr[n])
        changes += apply_post(a, page, lex, costs)
        after.append(
            evaluate.score_page(n, page.words(), ref)
        )
    t = evaluate.summary(after)
    fixed, broke = evaluate.compare(results, after)
    print()
    print("if every suggestion were applied (not done):")
    print(f"CER {t['cer']:.1%}   WER {t['wer']:.1%}")
    print(
        f"{len(changes)} words changed: {fixed} fixed,"
        f" {broke} broken"
    )
    for c in changes[: a.show]:
        print(
            f"  {c.old} -> {c.new}"
            f"  ({c.cost:.1f}, {c.conf:.0f})"
        )


def tune_context(a, lex, costs, ocr, base, ref, nums):
    import copy
    import itertools

    print(
        "weight gain conf cost   CER     WER   chg fix brk"
    )
    grid = itertools.product(
        (2.0, 4.0, 6.0),
        (0.5, 1.0, 2.0, 3.0),
        (90, 101),
        (1.2, 1.6),
    )
    for weight, gain, conf, cost in grid:
        p = post.ContextParams(
            max_conf=conf,
            max_cost=cost,
            weight=weight,
            gain=gain,
        )
        after, n_ch = [], 0
        for n in nums:
            page = copy.deepcopy(ocr[n])
            n_ch += len(post.context(page, lex, costs, p))
            after.append(
                evaluate.score_page(n, page.words(), ref)
            )
        t = evaluate.summary(after)
        f, b = evaluate.compare(base, after)
        print(
            f"{weight:6.1f} {gain:4.1f} {conf:4d}"
            f" {cost:4.1f}"
            f" {t['cer']:6.2%} {t['wer']:6.2%}"
            f" {n_ch:4d} {f:3d} {b:3d}",
            flush=True,
        )


def cmd_proxy(a):
    """Known-word rate and confidence, no typed text."""
    nums = eval_pages(a)
    lex, _ = load_post(a)
    known = total = low = words = 0
    conf = 0.0
    for n in nums:
        page = cached_page(a.pdf, n, a)
        ws = page.words()
        k, t = evaluate.known_rate(ws, lex)
        known += k
        total += t
        words += len(ws)
        conf += sum(w.conf for w in ws)
        low += sum(w.conf < 80 for w in ws)
    print(f"{len(nums)} pages, {words} words")
    print(f"known {known / max(total, 1):.1%} of {total}")
    print(f"mean confidence {conf / max(words, 1):.1f}")
    print(f"under 80: {low / max(words, 1):.1%}")


def eval_llm(a, nums, ocr, ref, before):
    """What the LLM pass is worth if all is applied."""
    import copy

    backend = llm_backend(a)
    lex = costs = None
    if a.llm_hints:
        lex, costs = load_post(a)
    after, changes, sent, total, flagged, words = (
        [],
        [],
        0,
        0,
        0,
        0,
    )
    for n in nums:
        page = copy.deepcopy(ocr[n])
        img = prepared(a.pdf, n, a)
        got, k = llm_page(a, backend, page, img, lex, costs)
        for c in got:
            page.lines[c.line].words[c.word].text = c.new
        changes += got
        sent += k
        total += len(page.lines)
        for ln in page.lines:
            words += len(ln.words)
            flagged += sum(
                w.conf < a.llm_conf for w in ln.words
            )
        after.append(
            evaluate.score_page(n, page.words(), ref)
        )
    s0 = evaluate.summary(before)
    t = evaluate.summary(after)
    fixed, broke = evaluate.compare(before, after)
    print()
    print(f"LLM pass ({a.llm}), if every change were made:")
    print(
        f"lines sent {sent} of {total}, words under"
        f" {a.llm_conf:.0f}: {flagged / max(words, 1):.1%}"
    )
    print(f"CER {s0['cer']:.2%} -> {t['cer']:.2%}")
    print(f"WER {s0['wer']:.2%} -> {t['wer']:.2%}")
    print(
        f"{len(changes)} words changed: {fixed} fixed,"
        f" {broke} made wrong"
    )
    u = backend.usage
    print(
        f"tokens in {u['input']}, out {u['output']},"
        f" calls {u['calls']} (cached {u['cached']})"
    )
    if getattr(backend, "pending", None):
        print(
            f"{len(backend.pending)} requests have no"
            f" answer yet, in {a.llm_files}:"
            " those lines are as read"
        )
    for c in changes[: a.show]:
        print(f"  {c.old} -> {c.new}  ({c.conf:.0f})")


def cmd_tune(a):
    """Grid of settings on the dev pages."""
    import copy
    import itertools

    texts = [
        p.read_text()
        for p in sorted(Path(a.ref).glob("*.txt"))
    ]
    ref = locate.Reference(texts)
    nums = eval_pages(a)
    ocr = {n: cached_page(a.pdf, n, a) for n in nums}
    base = [
        evaluate.score_page(n, ocr[n].words(), ref)
        for n in nums
    ]
    s0 = evaluate.summary(base)
    print(
        f"before: CER {s0['cer']:.2%} WER {s0['wer']:.2%}"
    )
    lex, costs = load_post(a)
    if a.context:
        tune_context(a, lex, costs, ocr, base, ref, nums)
        return
    grid = itertools.product(
        (80, 90, 101),
        (0.8, 1.2, 1.6),
        (1, 2, 4),
        (0.0, 0.3),
        (False, True),
    )
    print(
        "conf cost minn margin names"
        "   CER     WER   chg fix brk"
    )
    for conf, cost, mn, margin, names in grid:
        p = post.Params(conf, cost, mn, margin, names)
        after, n_ch = [], 0
        for n in nums:
            page = copy.deepcopy(ocr[n])
            n_ch += len(post.correct(page, lex, costs, p))
            after.append(
                evaluate.score_page(n, page.words(), ref)
            )
        t = evaluate.summary(after)
        f, b = evaluate.compare(base, after)
        print(
            f"{conf:4d} {cost:4.1f} {mn:4d} {margin:6.1f}"
            f" {int(names):5d}"
            f" {t['cer']:6.2%} {t['wer']:6.2%}"
            f" {n_ch:4d} {f:3d} {b:3d}",
            flush=True,
        )


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
    worst = sorted(
        s["per_page"], key=lambda r: -r[2] / max(r[1], 1)
    )[:3]
    print("worst pages:", [r[0] for r in worst])
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
    p.add_argument("--suggest", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--review")
    add_post_args(p)
    add_prep_args(p)
    p.set_defaults(func=cmd_page)
    e = sub.add_parser("eval")
    e.add_argument("pdf")
    e.add_argument("--ref", required=True)
    e.add_argument("--pages", required=True)
    e.add_argument("--sample", type=int, default=0)
    e.add_argument("--json")
    e.add_argument("--heldout", action="store_true")
    e.add_argument("--half", choices=("dev", "test"))
    add_post_args(e)
    e.add_argument("--post", action="store_true")
    e.add_argument("--show", type=int, default=25)
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
    m.add_argument("--jobs", type=int, default=4)
    add_prep_args(m)
    m.set_defaults(func=cmd_samples)
    t = sub.add_parser("train")
    t.add_argument("--out", required=True)
    t.add_argument("--name", default="hye_grabar")
    t.add_argument("--steps", type=int, default=3000)
    t.add_argument("--rate", type=float, default=0.0002)
    t.add_argument("--start")
    t.set_defaults(func=cmd_train)
    q = sub.add_parser("proxy")
    q.add_argument("pdf")
    q.add_argument("--pages", required=True)
    q.add_argument("--sample", type=int, default=0)
    q.add_argument("--heldout", action="store_true")
    q.add_argument("--half")
    add_post_args(q)
    add_prep_args(q)
    q.set_defaults(func=cmd_proxy)
    u = sub.add_parser("tune")
    u.add_argument("pdf")
    u.add_argument("--ref", required=True)
    u.add_argument("--pages", required=True)
    u.add_argument("--sample", type=int, default=0)
    u.add_argument("--heldout", action="store_true")
    u.add_argument("--half", default="dev")
    add_post_args(u)
    add_prep_args(u)
    u.set_defaults(func=cmd_tune)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
