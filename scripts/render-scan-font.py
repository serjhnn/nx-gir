#!/usr/bin/env python3
"""Make nxGir Dzeragir, a font in the hand of the
scribe of Walters Ms. W.541 (Gospels, early 17th
century), from the letters in sources/w541/.

Every letter is the scribe's: traced from its
picture, the average of its copies in the
manuscript (sources/w541/README.md). The capitals,
which the text hardly has, are his small letters
drawn bigger; և is his ե and ւ side by side, ։ two
of his dots. What he never wrote (Latin letters,
digits, most punctuation) is not in the font: the
reader shows it in its next font. OFL.

Needs numpy, scipy, Pillow, fonttools, brotli and
potracer (pip), only here:

    python3 scripts/render-scan-font.py
    python3 scripts/render-scan-font.py --sample a.png

Writes web/fonts/dzeragir-400-normal.woff2.
"""

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "w541"
OUT = ROOT / "web" / "fonts" / "dzeragir-400-normal.woff2"

FAMILY = "nxGir Dzeragir"
PS_NAME = "nxGirDzeragir-Regular"
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
CAP = 1.2  # capitals: the small letter, bigger
COLON = 0.55  # ։ the upper dot, in x-heights


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
    """{character: picture path} from letters.tsv."""
    out = {}
    text = (SRC / "letters.tsv").read_text()
    for line in text.split("\n"):
        if not line or line.startswith("#"):
            continue
        ch, name = line.split("\t")[:2]
        out[ch] = SRC / "letters" / name
    return out


def no_specks(ink):
    """Only the parts bigger than 1% of the ink."""
    lab, n = ndimage.label(ink)
    if n < 2:
        return ink
    size = ndimage.sum(ink, lab, range(1, n + 1))
    keep = 1 + np.nonzero(size > 0.01 * size.sum())[0]
    return np.isin(lab, keep)


def trace(ink, ox):
    """Curves of the ink in font units, x from the
    column ox, y up from the baseline."""

    def unit(p):
        return (
            round((p.x - ox) * U),
            round((BASE - p.y) * U),
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


def scanned(path):
    """A letter from its picture: (contours, width).
    The width is the body's, in the middle of the
    x-height: tails on the baseline and hooks on top
    reach over the neighbours, as written."""
    ink = np.array(Image.open(path).convert("L")) < 128
    ink = no_specks(ink)
    band = ink[BASE - int(0.9 * PX) : BASE - int(0.3 * PX)]
    xs = np.nonzero(band.any(0))[0]
    if not len(xs):
        xs = np.nonzero(ink.any(0))[0]
    left, right = xs[0], xs[-1] + 1
    contours = trace(ink, left - SIDE / U)
    width = round((right - left) * U + 2 * SIDE)
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


def glyphs():
    """{codepoint: (contours, width)}."""
    out = {}
    for ch, path in letters().items():
        out[ord(ch)] = scanned(path)
    for c in range(0x561, 0x587):
        if c in out:
            cont, w = out[c]
            out[c - 0x30] = (
                moved(cont, k=CAP),
                round(w * CAP),
            )
    if 0x565 in out and 0x582 in out:
        e, ew = out[0x565]
        v, vw = out[0x582]
        out[0x587] = (e + moved(v, dx=ew), ew + vw)
    if 0x2E in out:
        dot, dw = out[0x2E]
        up = moved(dot, dy=round(COLON * XH))
        out[0x589] = (dot + up, dw)
    return out


def build():
    g = glyphs()
    for c in sorted(g):
        print(chr(c), end=" ")
    print()
    render_font().save(
        OUT,
        g,
        SPACE,
        family=FAMILY,
        ps_name=PS_NAME,
        copyright=COPYRIGHT,
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
    a = ap.parse_args()
    if a.sample:
        sample(a.sample, a.text)
    else:
        build()


if __name__ == "__main__":
    main()
