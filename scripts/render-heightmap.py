#!/usr/bin/env python3
"""Render web/img/map/height.png: the relief of the
3D map (web/map3d.js), guessed from the painted
picture web/img/map/base.webp, as it is art and
not a projection (notes/map.md): the painted
ranges and peaks (RIDGES, set by eye) go up, the
strokes of the painting make them rough, the blue
of the lakes and the sea stays flat.

A grey picture, 384x256, white the highest. Needs
Pillow and numpy. Run again after changing the
picture:

    scripts/render-heightmap.py
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "web" / "img" / "map"
SIZE = (384, 256)

# the painted mountains, set by eye on the picture
# like the pins: a ridge from x1, y1 to x2, y2
# (percent of the picture, as in map/places.tsv),
# its half width (percent of the width) and height
# (0 to 1); a point is a ridge with x1 = x2
RIDGES = [
    (24, 4, 50, 6, 7, 0.55),  # the north range
    (50, 6, 72, 5, 7, 0.5),
    (72, 5, 96, 6, 7, 0.5),
    (0, 70, 14, 78, 7, 0.5),  # the south-west
    (14, 78, 30, 90, 6, 0.45),
    (14, 96, 40, 90, 7, 0.45),  # the south
    (44, 98, 60, 96, 5, 0.35),
    (76, 98, 100, 90, 6, 0.45),
    (62, 60, 74, 64, 6, 0.55),  # the east massif
    (66, 64, 86, 76, 7, 0.55),
    (78, 58, 88, 72, 5, 0.45),
    (55, 57, 55, 57, 4, 0.4),  # the castle hill
    (72, 39, 86, 45, 5, 0.3),  # the east hills
    (51.8, 33, 51.8, 33, 10, 1.0),  # Masis
    (59, 37, 59, 37, 4.5, 0.55),  # little Masis
    (42, 23.5, 42, 23.5, 7, 0.7),  # Aragats
    (25, 40, 25, 40, 3, 0.2),  # the castle rock
]


def blur(a, r):
    """a (0 to 1) blurred by r pixels."""
    im = Image.fromarray(np.uint8(a * 255))
    im = im.filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, float) / 255


def ridges(shape):
    """The height of RIDGES, 0 to 1."""
    hh, w = shape
    ys, xs = np.mgrid[0:hh, 0:w]
    ys = ys / w * 100  # in percent of the width
    xs = xs / w * 100
    k = hh / w  # y in percent of the height to it
    out = np.zeros(shape)
    for x1, y1, x2, y2, rad, top in RIDGES:
        ax, ay = x1, y1 * k
        dx, dy = x2 - x1, (y2 - y1) * k
        n = dx * dx + dy * dy
        t = 0.0
        if n:
            t = ((xs - ax) * dx + (ys - ay) * dy) / n
            t = np.clip(t, 0, 1)
        d = np.hypot(xs - ax - t * dx, ys - ay - t * dy)
        cone = np.clip(1 - d / rad, 0, 1) ** 1.5
        out = np.maximum(out, top * cone)
    return out


def detail(rgb):
    """The strokes of the painting, 0 to 1: rough
    where it is drawn in detail."""
    lum = rgb.mean(-1)
    m = blur(lum, 1.5)
    rough = np.abs(lum - m)
    return np.clip(blur(rough * 6, 1), 0, 1)


def water(rgb):
    """1 where the picture is water."""
    r, b = rgb[..., 0], rgb[..., 2]
    return blur(np.clip((b - r) * 4, 0, 1), 1.5)


def main():
    im = Image.open(MAP / "base.webp").convert("RGB")
    im = im.resize(SIZE, Image.LANCZOS)
    rgb = np.asarray(im, float) / 255
    hill = ridges(rgb.shape[:2])
    h = 0.08 + 0.85 * hill
    h += detail(rgb) * (0.04 + 0.25 * hill)
    h *= 1 - water(rgb)
    h = blur(np.clip(h, 0, 1), 0.8)
    out = MAP / "height.png"
    Image.fromarray(np.uint8(h * 255)).save(
        out, optimize=True
    )
    print(out.relative_to(ROOT), out.stat().st_size)


if __name__ == "__main__":
    main()
