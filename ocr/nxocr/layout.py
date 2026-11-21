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


def top_of(line):
    return min(w.box[1] for w in line.words)


def main_text(page, ratio=0.8, tail=0.0, after=0.4):
    """A Page without the apparatus.

    Lines set smaller than `ratio` of the main text height
    are dropped. With `tail`, a stricter rule follows: the
    apparatus is always at the bottom, so once two lines in
    a row, in the lower part of the page (below the share
    `after` of it), are smaller than `tail` of the main
    height, those and everything under them is dropped.
    """
    from .engine import Page

    top = main_height(page)
    lines = sorted(page.lines, key=top_of)
    if tail and lines:
        floor = after * top_of(lines[-1])
        for i in range(len(lines) - 1):
            pair = lines[i : i + 2]
            if top_of(lines[i]) < floor:
                continue
            if all(
                line_height(ln) < tail * top for ln in pair
            ):
                lines = lines[:i]
                break
    keep = [
        ln for ln in lines if line_height(ln) >= ratio * top
    ]
    return Page(keep)
