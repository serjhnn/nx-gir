"""Score OCR of a page against the typed text.

For each page: the OCR text is placed in the reference
(locate), aligned to it (metrics.ops), and the errors
counted per character and per word. Word results with
the engine's confidence give the triage numbers: how
much text must be re-read to catch how many errors.
"""

from collections import Counter
from dataclasses import dataclass, field

from . import metrics
from .textnorm import key


@dataclass
class PageResult:
    page: int
    chars: int = 0  # reference characters compared
    errors: int = 0
    words: int = 0
    word_errors: int = 0
    placed: bool = True
    flags: list = field(default_factory=list)  # (conf, ok)
    confusions: Counter = field(default_factory=Counter)

    @property
    def cer(self):
        return metrics.rate(self.errors, self.chars)


def word_keys(words):
    """Key of each OCR word, with its index, no empties."""
    out = []
    for idx, w in enumerate(words):
        k = key(w.text)
        if k:
            out.append((idx, k))
    return out


def score_page(page_no, words, ref):
    """Score one page; `words` are engine Words."""
    res = PageResult(page_no)
    pairs = word_keys(words)
    text = "".join(k for _, k in pairs)
    if len(text) < 20:
        res.placed = False
        return res
    span = ref.locate(text)
    if span is None:
        res.placed = False
        return res
    window = ref.text[span[0] : span[1]]
    items, start, end = metrics.ops(text, window, True)
    res.chars = end - start
    res.errors = metrics.errors(items)
    # which OCR word each character belongs to
    owner = []
    for n, (_, k) in enumerate(pairs):
        owner.extend([n] * len(k))
    bad = set()
    pos = 0
    for op, x, y in items:
        if op != "=":
            res.confusions[(x, y)] += 1
        if op == "+":
            bad.add(owner[min(pos, len(owner) - 1)])
        else:
            if op != "=":
                bad.add(owner[pos])
            pos += 1
    res.words = len(pairs)
    res.word_errors = len(bad)
    for n, (idx, _) in enumerate(pairs):
        res.flags.append((words[idx].conf, n not in bad))
    return res


def triage(results, thresholds=(50, 60, 70, 80, 90)):
    """For each confidence threshold: the share of words
    below it (what an LLM would be asked to re-read) and
    the share of all wrong words that are among them."""
    flags = [f for r in results for f in r.flags]
    wrong = [f for f in flags if not f[1]]
    rows = []
    for t in thresholds:
        low = [f for f in flags if f[0] < t]
        caught = [f for f in low if not f[1]]
        rows.append(
            {
                "below": t,
                "reread": metrics.rate(
                    len(low), len(flags)
                ),
                "caught": metrics.rate(
                    len(caught), len(wrong)
                ),
                "precision": metrics.rate(
                    len(caught), len(low)
                ),
            }
        )
    return rows


def compare(before, after):
    """(fixed, broke): words that became right or wrong.

    Both are lists of PageResult for the same pages, the
    after one made from corrected words (same words, same
    order).
    """
    fixed = broke = 0
    for b, a in zip(before, after):
        if len(b.flags) != len(a.flags):
            continue
        for (_, ok1), (_, ok2) in zip(b.flags, a.flags):
            fixed += (not ok1) and ok2
            broke += ok1 and (not ok2)
    return fixed, broke


def summary(results):
    placed = [r for r in results if r.placed]
    chars = sum(r.chars for r in placed)
    errs = sum(r.errors for r in placed)
    words = sum(r.words for r in placed)
    wer = sum(r.word_errors for r in placed)
    conf = Counter()
    for r in placed:
        conf.update(r.confusions)
    return {
        "pages": len(results),
        "placed": len(placed),
        "cer": metrics.rate(errs, chars),
        "wer": metrics.rate(wer, words),
        "triage": triage(placed),
        "per_page": [
            [r.page, r.chars, r.errors] for r in placed
        ],
        "confusions": conf,
    }
