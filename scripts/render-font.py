#!/usr/bin/env python3
"""Make nxGir Bolorgir, the reader's calligraphic
font, from Noto Serif Armenian.

Each letter of Noto is drawn big, made wider and
lower, thinned to its middle line, and written
again with a broad pen held at an angle (the
thick and thin come from the angle, as with a
reed pen); the picture is traced back to curves
(potrace) and saved as a font. The font is under
the SIL OFL 1.1, as Noto is (`web/fonts/README.md`).

Needs numpy, scipy, scikit-image, Pillow,
fonttools, brotli and potracer (pip), only here:

    python3 scripts/render-font.py
    python3 scripts/render-font.py --sample a.png

Writes web/fonts/bolorgir-400-normal.woff2.
"""

import argparse
import math
from pathlib import Path

import numpy as np
import potrace
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import (
    T2CharStringPen,
)
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.signal import fftconvolve
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "web" / "fonts"
OUT = FONTS / "bolorgir-400-normal.woff2"
ARMENIAN = FONTS / "noto-armenian-400-normal.woff2"
LATIN = FONTS / "noto-latin-400-normal.woff2"

FAMILY = "nxGir Bolorgir"
PS_NAME = "nxGirBolorgir-Regular"
VERSION = "1.000"
COPYRIGHT = (
    "Copyright 2022 The Noto Project Authors"
    " (https://github.com/notofonts/armenian);"
    " Copyright 2026 the nxGir project"
)
LICENSE = (
    "This Font Software is licensed under the SIL"
    " Open Font License, Version 1.1."
)
LICENSE_URL = "https://openfontlicense.org"

UPM = 1000
S = 600  # pixels per em while drawing
U = UPM / S  # font units per pixel

# the pen: as the manuscript sample
WIDE = 1.12  # letters wider
LOW = 0.82  # and lower
PEN = 0.15  # pen width, em
THIN = 0.025  # the pen's thin side, em
ANGLE = 35  # degrees
SLANT = 3  # degrees
TRACK = 50  # units added between letters
DOT = 0.02  # a mark smaller than this, em², is
# kept whole (dots), not drawn with the pen

# Latin and punctuation taken from Noto Serif
LATIN_CHARS = [
    *range(0x21, 0x7F),
    0xAB,
    0xB7,
    0xBB,
    0x2013,
    0x2014,
    0x2018,
    0x2019,
    0x201C,
    0x201D,
    0x2026,
]
N8 = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]


def chars():
    """{codepoint: source font} to draw."""
    out = {}
    cm = TTFont(LATIN).getBestCmap()
    for c in LATIN_CHARS:
        if c in cm:
            out[c] = LATIN
    cm = TTFont(ARMENIAN).getBestCmap()
    for c in cm:
        if 0x530 <= c <= 0x58F or c >= 0xFB13:
            out[c] = ARMENIAN
    return out


def advance(font, c):
    gl = font.getBestCmap()[c]
    return font["hmtx"][gl][0]


def neighbours(sk, y, x):
    return [
        (y + dy, x + dx)
        for dy, dx in N8
        if sk[y + dy, x + dx]
    ]


def prune(sk, length):
    """Cut branches shorter than length pixels,
    the spurs that serifs leave."""
    sk = sk.copy()
    for _ in range(3):
        removed = False
        ys, xs = np.nonzero(sk)
        for y, x in zip(ys, xs):
            if not sk[y, x]:
                continue
            if len(neighbours(sk, y, x)) != 1:
                continue
            path = [(y, x)]
            prev, cur = None, (y, x)
            while len(path) <= length:
                nb = [
                    p
                    for p in neighbours(sk, *cur)
                    if p != prev and p not in path
                ]
                if len(nb) != 1:
                    break
                prev, cur = cur, nb[0]
                if len(neighbours(sk, *cur)) > 2:
                    break
                path.append(cur)
            fork = len(neighbours(sk, *cur)) > 2
            if fork and len(path) <= length:
                for p in path:
                    sk[p] = False
                removed = True
        if not removed:
            break
    return sk


def nib():
    """The pen, anti-aliased: a thin rectangle."""
    width, thin = PEN * S, THIN * S
    n = int(width) + 6
    yy, xx = np.mgrid[-n : n + 1, -n : n + 1] * 1.0
    a = math.radians(ANGLE)
    u = xx * math.cos(a) - yy * math.sin(a)
    v = xx * math.sin(a) + yy * math.cos(a)
    along = np.clip(width / 2 - abs(u) + 0.5, 0, 1)
    across = np.clip(thin / 2 - abs(v) + 0.5, 0, 1)
    return along * across


def write(text, path, pen):
    """The letter or letters, written with the pen:
    (coverage, x of the origin, y of the baseline),
    in pixels."""
    font = ImageFont.truetype(str(path), S)
    pad = S
    w = int(font.getlength(text)) + 2 * pad
    h = 3 * S
    base = 2 * S
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text(
        (pad, base),
        text,
        font=font,
        fill=255,
        anchor="ls",
    )
    nw, nh = int(w * WIDE), int(h * LOW)
    im = im.resize((nw, nh), Image.BICUBIC)
    img = np.array(im) > 127
    if not img.any():
        return None, pad * WIDE, base * LOW
    img = ndimage.gaussian_filter(img * 1.0, S / 67)
    img = img > 0.5
    img = ndimage.binary_closing(
        img, iterations=max(1, S // 100)
    )
    sk = prune(skeletonize(img), S // 9)
    cov = fftconvolve(sk * 1.0, pen, mode="same")
    return (
        np.maximum(np.clip(cov, 0, 1), dots(img)),
        pad * WIDE,
        base * LOW,
    )


def dots(img):
    """Small marks (the dots of ։ and ., ՝ ՛) kept
    whole and a little fuller: their middle line
    is a point, which the pen would draw as a
    hairline."""
    lab, n = ndimage.label(img)
    if not n:
        return np.zeros(img.shape)
    area = ndimage.sum(img, lab, range(1, n + 1))
    small = np.isin(
        lab, 1 + np.nonzero(area < DOT * S * S)[0]
    )
    grown = ndimage.binary_dilation(
        small, iterations=int(PEN * S / 5)
    )
    return ndimage.gaussian_filter(grown * 1.0, 1.5)


def trace(cov, ox, base):
    """Curves of the ink, in font units."""
    # potracer reads True as white paper
    bm = potrace.Bitmap(cov <= 0.5)
    plist = bm.trace(
        turdsize=8, alphamax=1.0, opttolerance=0.3
    )
    k = math.tan(math.radians(SLANT))

    def unit(p):
        x = (p.x - ox) * U
        y = (base - p.y) * U
        return (round(x + y * k + TRACK / 2), round(y))

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


def draw(contours, width):
    pen = T2CharStringPen(width, None)
    for segs in contours:
        for s in segs:
            if s[0] == "move":
                pen.moveTo(s[1])
            elif s[0] == "line":
                pen.lineTo(s[1])
            else:
                pen.curveTo(*s[1:])
        pen.closePath()
    return pen.getCharString()


class Pen:
    """Letters written with the pen, one at a time:
    (contours, advance width) in font units."""

    def __init__(self):
        self.nib = nib()
        self.srcs = {
            p: TTFont(p) for p in (ARMENIAN, LATIN)
        }
        self.chars = chars()

    def space(self):
        adv = advance(self.srcs[ARMENIAN], 0x20)
        return round(adv * WIDE)

    def glyph(self, c):
        path = self.chars[c]
        adv = advance(self.srcs[path], c)
        width = round(adv * WIDE) + TRACK if adv else 0
        cov, ox, base = write(chr(c), path, self.nib)
        if cov is None:
            return [], width
        return trace(cov, ox, base), width


def build(out=OUT):
    pen = Pen()
    glyphs = {}
    for c in sorted(pen.chars):
        glyphs[c] = pen.glyph(c)
        print(chr(c), len(glyphs[c][0]), flush=True)
    save(out, glyphs, pen.space())


def save(
    out,
    glyphs,
    space,
    family=FAMILY,
    ps_name=PS_NAME,
    copyright=COPYRIGHT,
):
    """Write the font: glyphs is {codepoint:
    (contours, advance width)}."""
    order = [".notdef", "space"]
    cmap = {0x20: "space", 0xA0: "space"}
    metrics = {".notdef": (500, 0), "space": (space, 0)}
    strings = {
        ".notdef": draw([], 500),
        "space": draw([], space),
    }
    top, bottom = 0, 0
    for c, (contours, width) in sorted(glyphs.items()):
        name = f"uni{c:04X}"
        for segs in contours:
            for s in segs:
                for p in s[1:]:
                    top = max(top, p[1])
                    bottom = min(bottom, p[1])
        order.append(name)
        cmap[c] = name
        strings[name] = draw(contours, width)
        metrics[name] = (width, 0)
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(
        ps_name,
        {"FullName": family, "version": VERSION},
        strings,
        {},
    )
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=top, descent=bottom)
    fb.setupNameTable(
        {
            "copyright": copyright,
            "familyName": family,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"{ps_name};{VERSION}",
            "fullName": family,
            "version": f"Version {VERSION}",
            "psName": ps_name,
            "licenseDescription": LICENSE,
            "licenseInfoURL": LICENSE_URL,
        }
    )
    fb.setupOS2(
        sTypoAscender=top,
        sTypoDescender=bottom,
        sTypoLineGap=0,
        usWinAscent=top,
        usWinDescent=-bottom,
        achVendID="NXGR",
    )
    fb.setupPost()
    fb.font.flavor = "woff2"
    fb.save(str(out))
    print(out, out.stat().st_size, "bytes")


def sample(png, text):
    """A line in the new font, to look at."""
    font = ImageFont.truetype(str(OUT), 90)
    w = int(font.getlength(text)) + 80
    im = Image.new("L", (w, 170), 255)
    ImageDraw.Draw(im).text(
        (40, 120),
        text,
        font=font,
        fill=0,
        anchor="ls",
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
