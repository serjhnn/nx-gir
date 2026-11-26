#!/usr/bin/env python3
"""Make nxGir Dzeragir, a font in the hand of the
scribe of Walters Ms. W.541 (Gospels, early 17th
century), from the letters in sources/w541/.

The small letters found in the manuscript are
traced from their pictures (each the average of up
to 14 copies, sources/w541/README.md); the rest
(the capitals, the rare small letters, digits,
Latin letters and punctuation) are written with
the pen of scripts/render-font.py, set to the
scribe's weight and slant. OFL, like Noto.

Needs what scripts/render-font.py needs:

    python3 scripts/render-scan-font.py
    python3 scripts/render-scan-font.py --sample a.png

Writes web/fonts/dzeragir-400-normal.woff2.
"""

import argparse
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "w541"
OUT = ROOT / "web" / "fonts" / "dzeragir-400-normal.woff2"

FAMILY = "nxGir Dzeragir"
PS_NAME = "nxGirDzeragir-Regular"
COPYRIGHT = (
    "Copyright 2026 the nxGir project; the small"
    " letters after Walters Art Museum Ms. W.541"
    " (CC0); the rest made from Noto Serif"
    " Armenian, Copyright 2022 The Noto Project"
    " Authors (https://github.com/notofonts/armenian)"
)

PX = 120  # pixels per x-height in the pictures
BASE = 288  # the baseline row in the pictures
XH = 450  # the x-height in font units
SIDE = 55  # space each side of a letter, units
SPACE = 270

# the pen for the letters not in the manuscript
PEN = dict(
    PEN=0.14,
    THIN=0.03,
    ANGLE=20,
    SLANT=8,
    WIDE=1.0,
    LOW=0.84,
    TRACK=60,
)


def render_font():
    """scripts/render-font.py as a module."""
    path = ROOT / "scripts" / "render-font.py"
    spec = importlib.util.spec_from_file_location(
        "render_font", path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k, v in PEN.items():
        setattr(mod, k, v)
    mod.U = mod.UPM / mod.S
    return mod


def letters():
    """{codepoint: picture path} from letters.tsv."""
    out = {}
    for line in (
        (SRC / "letters.tsv").read_text().split("\n")
    ):
        if not line or line.startswith("#"):
            continue
        ch, name = line.split("\t")[:2]
        out[ord(ch)] = SRC / "letters" / name
    return out


def no_specks(ink):
    """Only the parts bigger than 1% of the ink."""
    lab, n = ndimage.label(ink)
    if n < 2:
        return ink
    size = ndimage.sum(ink, lab, range(1, n + 1))
    keep = 1 + np.nonzero(size > 0.01 * size.sum())[0]
    return np.isin(lab, keep)


def scanned(rf, path):
    """Trace a letter picture: (contours, width)."""
    ink = np.array(Image.open(path).convert("L")) < 128
    ink = no_specks(ink)
    u = XH / PX
    # the width is the body's, in the middle of the
    # x-height: tails on the baseline and hooks on
    # top reach over the neighbours, as written
    band = ink[BASE - int(0.9 * PX) : BASE - int(0.3 * PX)]
    xs = np.nonzero(band.any(0))[0]
    if not len(xs):
        xs = np.nonzero(ink.any(0))[0]
    left, right = xs[0], xs[-1] + 1
    # the pen module's trace: x from origin ox, y up
    # from base, in its units (UPM / S per pixel)
    rf.U = u
    rf.SLANT = 0
    rf.TRACK = 0
    contours = rf.trace(ink * 1.0, left - SIDE / u, BASE)
    rf.U = rf.UPM / rf.S
    rf.SLANT = PEN["SLANT"]
    rf.TRACK = PEN["TRACK"]
    width = round((right - left) * u + 2 * SIDE)
    return contours, width


def build():
    rf = render_font()
    pen = rf.Pen()
    scan = letters()
    glyphs = {}
    for c in sorted(set(pen.chars) | set(scan)):
        if c in scan:
            glyphs[c] = scanned(rf, scan[c])
            how = "scan"
        else:
            glyphs[c] = pen.glyph(c)
            how = "pen"
        print(chr(c), how, flush=True)
    rf.save(
        OUT,
        glyphs,
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
