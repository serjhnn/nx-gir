#!/usr/bin/env python3
"""Make nxGir Dzeragir, a font in the hand of the
scribe of Walters Ms. W.541 (Gospels, early 17th
century), from the letters in sources/w541/.

Every letter is the scribe's: traced from its
picture, the average of its copies in the
manuscript (sources/w541/README.md). The capitals
are the red initials that open his sentences
(sources/w541/capitals/), all scaled alike; those
not found yet are his small letters drawn bigger.
և is his own sign, ։ two of his dots.
Punctuation he does not give and the digits are
drawn with a round pen of his weight
(sources/w541/marks/). What he never wrote (Latin
letters) is not in the font: the reader shows it
in its next font.
Typed ե and ւ become his և (liga), as he writes
them. OFL.

Needs numpy, scipy, Pillow, fonttools, brotli and
potracer (pip), only here:

    python3 scripts/render-scan-font.py
    python3 scripts/render-scan-font.py --sample a.png
    python3 scripts/render-scan-font.py --thin 10 \\
        --out /tmp/thin.woff2  # a lighter weight

Writes web/fonts/dzeragir-400-normal.woff2 and the
thin one, dzeragirthin-400-normal.woff2 (THIN).
"""

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "w541"
OUT = ROOT / "web" / "fonts" / "dzeragir-400-normal.woff2"

FAMILY = "nxGir Dzeragir"
PS_NAME = "nxGirDzeragir-Regular"
# the thin one: the same letters, THIN pixels off
# each side of the strokes
THIN = 10
OUT_THIN = OUT.with_name("dzeragirthin-400-normal.woff2")
FAMILY_THIN = "nxGir Dzeragir Thin"
PS_THIN = "nxGirDzeragirThin-Regular"
COPYRIGHT = (
    "Copyright 2026 the nxGir project; the letters"
    " after Walters Art Museum Ms. W.541 (CC0)"
)

PX = 120  # pixels per x-height in the pictures
BASE = 288  # the baseline row in the pictures
XH = 450  # the x-height in font units
U = XH / PX  # font units per pixel
SIDE = 55  # space each side of a letter, units
SPACE = 340
MARK_SIDE = 15  # space each side of a drawn mark
CAP = 1.2  # capitals not found: the small letter,
# bigger
# the initials, all scaled alike: the middle one this
# many x-heights tall, none outside CAP_MIN..CAP_MAX
CAP_H = 2.3
CAP_MIN, CAP_MAX = 1.9, 2.6
COLON = 0.55  # ։ the upper dot, in x-heights
CORE = 3  # a thinned letter keeps this much round
# its middle line, in pixels, so hairlines stay

# the scribe writes ե and ւ as one sign, և
FEATURES = """
languagesystem DFLT dflt;
languagesystem armn dflt;
feature liga {
  sub uni0565 uni0582 by uni0587;
} liga;
"""


def render_font():
    """scripts/render-font.py as a module, for its
    save()."""
    path = ROOT / "scripts" / "render-font.py"
    spec = importlib.util.spec_from_file_location(
        "render_font", path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def letters():
    """{character: picture path}: the scribe's letters
    (letters.tsv), then the marks drawn in his weight
    that the manuscript does not give (marks.tsv)."""
    out = {}
    for tsv, folder in (
        ("letters.tsv", "letters"),
        ("marks.tsv", "marks"),
    ):
        path = SRC / tsv
        if not path.exists():
            continue
        for line in path.read_text().split("\n"):
            if not line or line.startswith("#"):
                continue
            ch, name = line.split("\t")[:2]
            out.setdefault(ch, SRC / folder / name)
    return out


def no_specks(ink):
    """Only the parts bigger than 1% of the ink."""
    lab, n = ndimage.label(ink)
    if n < 2:
        return ink
    size = ndimage.sum(ink, lab, range(1, n + 1))
    keep = 1 + np.nonzero(size > 0.01 * size.sum())[0]
    return np.isin(lab, keep)


def trace(ink, ox, base=BASE):
    """Curves of the ink in font units, x from the
    column ox, y up from the baseline (row base)."""

    def unit(p):
        return (
            round((p.x - ox) * U),
            round((base - p.y) * U),
        )

    bm = potrace.Bitmap(~ink)  # True is paper
    plist = bm.trace(
        turdsize=8, alphamax=1.0, opttolerance=0.3
    )
    out = []
    for curve in plist:
        segs = [("move", unit(curve.start_point))]
        for s in curve.segments:
            if s.is_corner:
                segs.append(("line", unit(s.c)))
                segs.append(("line", unit(s.end_point)))
            else:
                segs.append(
                    (
                        "curve",
                        unit(s.c1),
                        unit(s.c2),
                        unit(s.end_point),
                    )
                )
        out.append(segs)
    return out


def disk(r):
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    return xx * xx + yy * yy <= r * r


def thinned(ink, px):
    """The strokes px pixels thinner each side; the
    middle line kept, so thin ends do not vanish."""
    if not px:
        return ink
    core = skeletonize(ink)
    core = ndimage.binary_dilation(core, disk(CORE))
    shaved = ndimage.binary_erosion(ink, disk(px))
    out = (shaved | core) & ink
    return ndimage.gaussian_filter(out * 1.0, 1.2) > 0.5


def scanned(path, thin=0, side=SIDE):
    """A letter from its picture: (contours, width).
    The width is the body's, in the middle of the
    x-height: tails on the baseline and hooks on top
    reach over the neighbours, as written. thin:
    pixels taken off each side of the strokes (the
    width stays the full letter's)."""
    ink = np.array(Image.open(path).convert("L")) < 128
    ink = no_specks(ink)
    band = ink[BASE - int(0.9 * PX) : BASE - int(0.3 * PX)]
    xs = np.nonzero(band.any(0))[0]
    if not len(xs):
        xs = np.nonzero(ink.any(0))[0]
    left, right = xs[0], xs[-1] + 1
    contours = trace(thinned(ink, thin), left - side / U)
    width = round((right - left) * U + 2 * side)
    return contours, width


def capitals():
    """{character: picture path}: the initials
    (capitals.tsv)."""
    out = {}
    path = SRC / "capitals.tsv"
    if not path.exists():
        return out
    for line in path.read_text().split("\n"):
        if line and not line.startswith("#"):
            ch, name = line.split("\t")[:2]
            out[ch] = SRC / "capitals" / name
    return out


def cap_scale(pics):
    """Pixels of each initial's picture to pixels of
    the letters' pictures: one factor for all, so the
    middle initial is CAP_H x-heights tall, then each
    kept within CAP_MIN..CAP_MAX."""
    hs = {
        ch: Image.open(p).size[1] for ch, p in pics.items()
    }
    k = CAP_H * PX / float(np.median(list(hs.values())))
    lo, hi = CAP_MIN * PX, CAP_MAX * PX
    return {
        ch: min(max(h * k, lo), hi) / h
        for ch, h in hs.items()
    }


def stroke(ink):
    """The width of the thick strokes: twice the
    distance to the edge along the middle line, 85th
    percentile, in pixels."""
    d = ndimage.distance_transform_edt(ink)
    return float(np.percentile(2 * d[skeletonize(ink)], 85))


def widened(ink, g):
    """Every stroke g times as wide: the middle line
    drawn again with disks g times its own radius,
    so the hairlines stay thin beside the stems."""
    d = ndimage.distance_transform_edt(ink)
    sk = skeletonize(ink)
    r = np.round(d * g).astype(int)
    pad = int(r.max()) + 2
    out = np.zeros(
        (ink.shape[0] + 2 * pad, ink.shape[1] + 2 * pad),
        bool,
    )
    for rad in np.unique(r[sk]):
        pts = np.zeros_like(out)
        ys, xs = np.nonzero(sk & (r == rad))
        pts[ys + pad, xs + pad] = True
        far = ndimage.distance_transform_edt(~pts)
        out |= far <= max(int(rad), 1)
    out = ndimage.gaussian_filter(out * 1.0, 1.5) > 0.5
    return out[pad:-pad, pad:-pad] | ink


def initial(path, k, weight, thin=0):
    """A capital from its initial: scaled by k, on
    the baseline, the width its whole ink. The red
    initials are drawn finer than the black text;
    their strokes are widened to his weight (the
    thick strokes of the small letters)."""
    im = Image.open(path).convert("L")
    w, h = im.size
    im = im.resize(
        (round(w * k), round(h * k)), Image.LANCZOS
    )
    ink = np.pad(no_specks(np.array(im) < 128), 40)
    ink = widened(ink, weight / stroke(ink))
    ys = np.nonzero(ink.any(1))[0]
    xs = np.nonzero(ink.any(0))[0]
    base = ys[-1] + 1
    contours = trace(
        thinned(ink, thin), xs[0] - SIDE / U, base
    )
    width = round((xs[-1] + 1 - xs[0]) * U + 2 * SIDE)
    return contours, width


def moved(contours, dx=0, dy=0, k=1.0):
    """Contours scaled by k from the origin, then
    moved."""
    out = []
    for segs in contours:
        out.append(
            [
                (s[0],)
                + tuple(
                    (round(x * k + dx), round(y * k + dy))
                    for x, y in s[1:]
                )
                for s in segs
            ]
        )
    return out


def glyphs(thin=0):
    """{codepoint: (contours, width)}."""
    out = {}
    for ch, path in letters().items():
        # marks sit close to the letter before them;
        # digits and the drawn letters (օ) are spaced
        # as letters
        mark = path.parent.name == "marks"
        tight = mark and not ch.isalnum()
        side = MARK_SIDE if tight else SIDE
        out[ord(ch)] = scanned(path, thin, side)
    pics = capitals()
    weight = float(
        np.median(
            [
                stroke(
                    np.array(Image.open(p).convert("L"))
                    < 128
                )
                for p in letters().values()
                if p.parent.name == "letters"
            ]
        )
    )
    for ch, k in cap_scale(pics).items():
        out[ord(ch)] = initial(pics[ch], k, weight, thin)
    for c in range(0x561, 0x587):
        if c in out and c - 0x30 not in out:
            cont, w = out[c]
            out[c - 0x30] = (
                moved(cont, k=CAP),
                round(w * CAP),
            )
    # և is the scribe's own sign (letters.tsv); only
    # without it, his ե and ւ side by side
    if 0x587 not in out and 0x565 in out and 0x582 in out:
        e, ew = out[0x565]
        v, vw = out[0x582]
        out[0x587] = (e + moved(v, dx=ew), ew + vw)
    if 0x2E in out:
        dot, dw = out[0x2E]
        up = moved(dot, dy=round(COLON * XH))
        out[0x589] = (dot + up, dw)
        out[0x3A] = out[0x589]  # : as his ։
    return out


def build(thin=0, out=None, family=FAMILY, ps=PS_NAME):
    g = glyphs(thin)
    for c in sorted(g):
        print(chr(c), end=" ")
    print()
    render_font().save(
        out or OUT,
        g,
        SPACE,
        family=family,
        ps_name=ps,
        copyright=COPYRIGHT,
        features=FEATURES if 0x587 in g else "",
    )


def sample(png, text):
    font = ImageFont.truetype(str(OUT), 90)
    w = int(font.getlength(text)) + 80
    im = Image.new("L", (w, 190), 255)
    ImageDraw.Draw(im).text(
        (40, 130), text, font=font, fill=0, anchor="ls"
    )
    im.save(png)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", metavar="PNG")
    ap.add_argument(
        "--text", default="Նախագիր թագաւոր վարդապետ։"
    )
    ap.add_argument(
        "--thin",
        type=int,
        default=0,
        metavar="PX",
        help="take PX pixels off each side of the"
        " strokes (a lighter weight)",
    )
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.sample:
        sample(a.sample, a.text)
    else:
        if a.thin or a.out:
            build(thin=a.thin, out=a.out)
        else:  # both fonts of the reader
            build()
            build(THIN, OUT_THIN, FAMILY_THIN, PS_THIN)


if __name__ == "__main__":
    main()
