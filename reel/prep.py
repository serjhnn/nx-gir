"""Makes the pictures and data of the fonts reel.

Writes reel/build/ (kept in git): the letters and the
red capitals of W.541 as ink on transparent ground,
the page with its pieces of ink, and the two fonts.
Run from the repository root:

    python3 reel/prep.py
"""

import glob
import json
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "sources/w541/"
OUT = "reel/build/"
FONTS = ["dzeragir", "bolorgir"]
BROWN = (34, 24, 18)
RED = (178, 40, 32)
# the page, without the ruler and the next page
CROP = (48, 30, 735, 1060)


def ink(src, dst, rgb, crop=True):
    """Black on white to rgb on transparent."""
    g = np.asarray(Image.open(src).convert("L"))
    im = np.zeros(g.shape + (4,), np.uint8)
    im[..., :3] = rgb
    im[..., 3] = 255 - g
    o = Image.fromarray(im)
    if crop:
        o = o.crop(o.getbbox())
    o.save(dst)
    return o.size


def name(f):
    return os.path.basename(f)[:-4]


def letters():
    out = []
    for f in sorted(glob.glob(SRC + "letters/*.png")):
        if name(f) == "002e":  # the dot
            continue
        ink(f, f"{OUT}l{name(f)}.png", BROWN, False)
        out.append(name(f))
    return out


def capitals():
    out = []
    for f in sorted(glob.glob(SRC + "capitals/*.png")):
        w, h = ink(f, f"{OUT}c{name(f)}.png", RED)
        out.append([name(f), w, h])
    return out


def pieces(pg):
    """Boxes of the black ink's pieces on the page."""
    r = np.asarray(pg)[..., 0].astype(float)
    lab, _ = ndimage.label(r < 95)
    boxes = []
    for y, x in ndimage.find_objects(lab):
        h, w = y.stop - y.start, x.stop - x.start
        if h * w < 40 or h > 80 or w > 120:
            continue
        boxes.append([x.start, y.start, w, h])
    return boxes


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in FONTS:
        n = f"{f}-400-normal.woff2"
        shutil.copy("web/fonts/" + n, OUT + n)
    pg = Image.open(SRC + "page-163.jpg")
    pg = pg.convert("RGB").crop(CROP)
    pg.save(OUT + "page.jpg", quality=92)
    data = {
        "L": letters(),
        "C": capitals(),
        "boxes": pieces(pg),
        "pw": pg.size[0],
        "ph": pg.size[1],
    }
    with open(OUT + "data.js", "w") as f:
        f.write("window.DATA = ")
        json.dump(data, f)
        f.write(";\n")
    n = len(data["boxes"])
    print(f"{OUT}: {n} pieces of ink")


if __name__ == "__main__":
    main()
