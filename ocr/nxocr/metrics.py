"""Edit distance, error rates and alignment.

Distances use numpy: one row at a time, with the
insertion step done by a running minimum.
"""

import numpy as np


def codes(text):
    return np.array([ord(c) for c in text], dtype=np.int32)


def matrix(a, b, free_start=False):
    """Edit distance table of a (rows) against b.

    With free_start the first row is zeros: a may start
    anywhere in b.
    """
    n, m = len(a), len(b)
    ca, cb = codes(a), codes(b)
    idx = np.arange(m + 1, dtype=np.int32)
    first = np.zeros(m + 1, np.int32) if free_start else idx
    table = np.empty((n + 1, m + 1), np.int32)
    table[0] = first
    for i in range(1, n + 1):
        prev = table[i - 1]
        row = np.empty(m + 1, np.int32)
        row[0] = i
        cost = (cb != ca[i - 1]).astype(np.int32)
        row[1:] = np.minimum(prev[:-1] + cost, prev[1:] + 1)
        # insertions: row[j] = min(row[j], row[j-1] + 1)
        row = np.minimum.accumulate(row - idx) + idx
        table[i] = row
    return table


def distance(a, b):
    if not a or not b:
        return max(len(a), len(b))
    return int(matrix(a, b)[-1, -1])


def ops(a, b, free_ends=False):
    """Alignment of a to b: list of (op, x, y).

    op is `=`, `~` (substitution), `-` (a has an extra
    character: x) or `+` (a lacks one: y). With free_ends
    only a stretch of b is used; the rest costs nothing.
    Returns (ops, start, end): the stretch of b.
    """
    table = matrix(a, b, free_start=free_ends)
    i = len(a)
    if free_ends:
        j = int(np.argmin(table[i]))
    else:
        j = len(b)
    end = j
    out = []
    while i > 0:
        here = table[i, j]
        if j > 0 and i > 0:
            same = a[i - 1] == b[j - 1]
            if here == table[i - 1, j - 1] + (not same):
                out.append(
                    (
                        "=" if same else "~",
                        a[i - 1],
                        b[j - 1],
                    )
                )
                i, j = i - 1, j - 1
                continue
        if here == table[i - 1, j] + 1:
            out.append(("-", a[i - 1], ""))
            i -= 1
        else:
            out.append(("+", "", b[j - 1]))
            j -= 1
    if not free_ends:
        while j > 0:
            out.append(("+", "", b[j - 1]))
            j -= 1
    out.reverse()
    return out, j, end


def errors(items):
    return sum(1 for op, _, _ in items if op != "=")


def rate(errs, total):
    return errs / total if total else 0.0


def word_distance(a, b):
    """Edit distance between two word lists."""
    if not a or not b:
        return max(len(a), len(b))
    ids = {}
    ca = [ids.setdefault(w, len(ids)) for w in a]
    cb = [ids.setdefault(w, len(ids)) for w in b]
    n, m = len(ca), len(cb)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        row = [i] + [0] * m
        for j in range(1, m + 1):
            cost = ca[i - 1] != cb[j - 1]
            row[j] = min(
                prev[j - 1] + cost,
                prev[j] + 1,
                row[j - 1] + 1,
            )
        prev = row
    return prev[m]
