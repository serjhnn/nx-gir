"""Find where a page's text lies in a typed reference.

The typed books have no page marks, so the page is
placed by voting: short letter sequences of the OCR
that occur in the reference vote for an offset.
Works for any book, however garbled the OCR is (a
few intact sequences are enough).
"""

from collections import Counter, defaultdict

from .textnorm import key


class Reference:
    """The typed text of a book, as one key string."""

    def __init__(self, texts, k=6, common=20):
        self.k = k
        self.raw = "\n".join(texts)
        # key string, and for each key char its place in raw
        keys, self.orig = [], []
        for i, ch in enumerate(self.raw):
            part = key(ch)
            keys.append(part)
            self.orig.extend([i] * len(part))
        self.text = "".join(keys)
        self.index = defaultdict(list)
        for i in range(len(self.text) - k + 1):
            self.index[self.text[i : i + k]].append(i)
        self.common = common

    def original(self, start, end):
        """The typed text for key positions start..end.

        Runs from the first key char to just before the
        key char at `end`: marks and spaces between the
        lines go with the earlier line.
        """
        a = self.orig[start]
        if end >= len(self.orig):
            b = len(self.raw)
        else:
            b = self.orig[end]
        return self.raw[a:b].strip()

    def locate(self, page_key, slack=150, min_votes=8):
        """(start, end) of the page stretch, or None."""
        k = self.k
        votes = Counter()
        for i in range(len(page_key) - k + 1):
            hits = self.index.get(page_key[i : i + k], ())
            if not hits or len(hits) > self.common:
                continue
            for pos in hits:
                votes[(pos - i) // 32] += 1
        if not votes:
            return None
        best, _ = votes.most_common(1)[0]
        n = sum(
            votes[b] for b in (best - 1, best, best + 1)
        )
        if n < min_votes:
            return None
        off = best * 32 + 16
        start = max(0, off - slack)
        end = min(
            len(self.text), off + len(page_key) + slack
        )
        return start, end
