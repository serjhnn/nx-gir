"""Post-correction with word lists.

A word the OCR read that is not in the lexicon, and is
close to exactly one word that is, is replaced by it.
The lexicon is the Wiktionary lists in `grabar/` and the
typed books in `books/grabar/` (a book can be left out,
so the book being tested is not in its own lexicon).

Close means a weighted edit distance: a swap the engine
is known to make (`ղ` for `զ`) costs less than any other.
The weights come from the confusions that `eval` records.
Every change is returned as a Correction, so each one can
be reviewed; nothing is changed without a trace.

Cautious on purpose: about 6% of Smbat's words are not in
any list (names, rare forms), and a "correction" of one of
those is a new error. So a word is left alone when it is
capitalized (a name), when the engine is sure of it, when
no candidate is close enough, or when two are equally
close.
"""

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from . import textnorm

LETTERS = "Ա-Ֆա-և"
TOKEN = re.compile(
    f"^([^{LETTERS}]*)([{LETTERS}]+)([^{LETTERS}]*)$"
)


@dataclass
class Params:
    max_conf: float = 80.0  # only words under this
    max_cost: float = 1.2  # edit cost allowed
    min_count: int = 2  # candidate must be this common
    margin: float = 0.3  # best must beat the next by this
    names: bool = False  # also correct capitalized words
    max_dist: int = 2  # plain edit distance of candidates
    weight: float = 0.1  # prefer common words (log10)


@dataclass
class Correction:
    line: int
    word: int
    old: str
    new: str
    cost: float
    conf: float


class Lexicon:
    """Word counts, and the close words of a word."""

    def __init__(
        self, counts, max_dist=2, long=7, common=3
    ):
        self.counts = counts
        self.max_dist = max_dist
        self.long = long
        # words at distance 2 are only looked for among the
        # common long words: the index would be too big
        self.index = defaultdict(list)
        for word in counts:
            for v in deletes(word, 1):
                self.index[v].append(word)
            if (
                max_dist > 1
                and len(word) >= long
                and counts[word] >= common
            ):
                for v in deletes(word, 2):
                    self.index[v].append(word)

    @classmethod
    def from_repo(cls, root, skip=(), **kw):
        root = Path(root)
        counts = Counter()
        for path in (root / "books" / "grabar").rglob(
            "*.txt"
        ):
            if any(s in path.parts for s in skip):
                continue
            counts.update(textnorm.words(path.read_text()))
        for name in ("vocabulary", "forms"):
            for line in open(
                root / "grabar" / f"{name}.tsv"
            ):
                if line.startswith("#") or not line.strip():
                    continue
                for w in textnorm.words(
                    line.split("\t")[0]
                ):
                    counts[w] = max(counts[w], 1)
        return cls(counts, **kw)

    def __contains__(self, word):
        return word in self.counts

    def near(self, word, max_dist=2):
        """Words within the plain edit distance."""
        found = set()
        for v in [word] + deletes(word, 1):
            found.update(self.index.get(v, ()))
        if max_dist > 1 and len(word) >= self.long - 2:
            for v in deletes(word, 2):
                found.update(self.index.get(v, ()))
        found.discard(word)
        return found


def deletes(word, n):
    """Variants with n letters removed (n is 1 or 2)."""
    out = set()
    for i in range(len(word)):
        one = word[:i] + word[i + 1 :]
        if n == 1:
            out.add(one)
        else:
            for j in range(len(one)):
                out.add(one[:j] + one[j + 1 :])
    return list(out)


class Costs:
    """Cost of each edit, from recorded confusions.

    A pair (ocr, typed) seen n times costs
    1 - 0.6 * min(1, n / 10); the rest cost 1.
    """

    def __init__(self, confusions=()):
        self.sub, self.ins, self.dele = {}, {}, {}
        for x, y, n in confusions:
            c = 1 - 0.6 * min(1.0, n / 10)
            if x and y:
                self.sub[(x, y)] = min(
                    c, self.sub.get((x, y), 1)
                )
            elif y:  # typed has it, the OCR missed it
                self.ins[y] = min(c, self.ins.get(y, 1))
            elif x:  # the OCR added a letter
                self.dele[x] = min(c, self.dele.get(x, 1))

    def distance(self, a, b):
        """Weighted edit distance of OCR word a to b."""
        prev = [0.0]
        for ch in b:
            prev.append(prev[-1] + self.ins.get(ch, 1))
        for x in a:
            row = [prev[0] + self.dele.get(x, 1)]
            for j, y in enumerate(b, 1):
                sub = (
                    0 if x == y else self.sub.get((x, y), 1)
                )
                row.append(
                    min(
                        prev[j - 1] + sub,
                        prev[j] + self.dele.get(x, 1),
                        row[j - 1] + self.ins.get(y, 1),
                    )
                )
            prev = row
        return prev[-1]


def best(core, lex, costs, p):
    """(word, cost) of the one close word, or None."""
    scored = []
    for cand in lex.near(core, p.max_dist):
        n = lex.counts[cand]
        if n < p.min_count:
            continue
        cost = costs.distance(core, cand)
        if cost > p.max_cost:
            continue
        scored.append(
            (cost - p.weight * math.log10(n), cost, cand)
        )
    if not scored:
        return None
    scored.sort()
    if (
        len(scored) > 1
        and scored[1][0] - scored[0][0] < p.margin
    ):
        return None
    return scored[0][2], scored[0][1]


def fragments(page, lex):
    """Halves of a word split at a line end."""
    skip = set()
    for n in range(len(page.lines) - 1):
        a, b = page.lines[n].words, page.lines[n + 1].words
        if not a or not b:
            continue
        x = textnorm.key(a[-1].text)
        y = textnorm.key(b[0].text)
        if x and y and x + y in lex and x not in lex:
            skip.add((n, len(a) - 1))
            skip.add((n + 1, 0))
    return skip


def correct(page, lex, costs, p=None):
    """Correct a Page in place; returns the Corrections."""
    p = p or Params()
    skip = fragments(page, lex)
    out = []
    for n, line in enumerate(page.lines):
        for m, w in enumerate(line.words):
            if (n, m) in skip or w.conf >= p.max_conf:
                continue
            tok = TOKEN.match(w.text)
            if not tok:
                continue
            pre, core, post = tok.groups()
            if core[0].isupper() and not p.names:
                continue
            word = core.casefold().replace("և", "եւ")
            if word in lex or len(word) < 3:
                continue
            got = best(word, lex, costs, p)
            if got is None:
                continue
            new, cost = got
            if core[0].isupper():
                new = new[0].upper() + new[1:]
            out.append(
                Correction(
                    n,
                    m,
                    w.text,
                    pre + new + post,
                    cost,
                    w.conf,
                )
            )
            w.text = pre + new + post
    return out
