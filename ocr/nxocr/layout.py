"""Page layout: keep the main text, drop the rest.

Critical editions print the variants of the manuscripts
(an apparatus, with letters like `ABCDI`) under the text
in smaller type. The typed book has only the main text,
so the apparatus must not be read as part of it. The
lines are told apart by their height: the main text is
the common size on the page, the apparatus is smaller.
"""

from statistics import median


def line_height(line):
    """Median word height of a line."""
    hs = [w.box[3] for w in line.words if w.box[3] > 0]
    return median(hs) if hs else 0


def main_height(page, share=0.75):
    """The height of the main text: the tall end of the
    lines (a high percentile, so a page of mostly small
    print is still told from its tall lines)."""
    hs = sorted(line_height(ln) for ln in page.lines)
    hs = [h for h in hs if h > 0]
    if not hs:
        return 0
    return hs[min(int(len(hs) * share), len(hs) - 1)]


def main_text(page, ratio=0.8):
    """A Page without the lines set smaller than
    `ratio` of the main text height."""
    from .engine import Page

    top = main_height(page)
    keep = [
        ln
        for ln in page.lines
        if line_height(ln) >= ratio * top
    ]
    return Page(keep)
