#!/usr/bin/env python3
"""Make web/og-image.png: the picture a link to
nxgir.am shows on LinkedIn and other sites (the
og:image in web/index.html), 1200x630.

It is the poster docs/og-poster.png (art, made
by hand: change that, not this), scaled to the
width and cut evenly at the top and bottom.
LinkedIn crops the sides (a Featured link shows
about the middle 960px): keep the poster's words
there. Needs Pillow (for this script only):

    scripts/render-og.py
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "og-poster.png"
OUT = ROOT / "web" / "og-image.png"
W, H = 1200, 630


def fit(im):
    """im scaled to cover W x H, cut to it in the
    middle."""
    k = max(W / im.width, H / im.height)
    w, h = round(im.width * k), round(im.height * k)
    im = im.resize((w, h), Image.LANCZOS)
    x, y = (w - W) // 2, (h - H) // 2
    return im.crop((x, y, x + W, y + H))


def main():
    im = fit(Image.open(SRC).convert("RGB"))
    im.save(OUT, optimize=True)
    kb = OUT.stat().st_size // 1024
    print(f"{OUT.relative_to(ROOT)}: {kb} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
