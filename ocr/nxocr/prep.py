"""Page preparation: crop, straighten, binarize.

Everything works on a grey page as a numpy array
(0 black, 255 white).
"""

from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class Prep:
    top: float = 0.0  # share of the height cut at the top
    bottom: float = 0.0
    left: float = 0.0
    right: float = 0.0
    deskew: bool = False
    binarize: bool = False
    window: int = 31  # Sauvola window, in pixels
    k: float = 0.2
    scale: float = 1.0


def crop(img, p):
    w, h = img.size
    box = (
        int(w * p.left),
        int(h * p.top),
        int(w * (1 - p.right)),
        int(h * (1 - p.bottom)),
    )
    return img.crop(box)


def skew_angle(img, span=3.0, step=0.25):
    """Angle (degrees) that makes the text rows sharpest.

    The best angle gives the largest variance of the
    row sums of the dark pixels (rows alternate between
    ink and white space).
    """
    small = img.copy()
    small.thumbnail((700, 700))
    best, best_score = 0.0, -1.0
    for tenth in np.arange(-span, span + step, step):
        r = small.rotate(
            tenth, resample=Image.BILINEAR, fillcolor=255
        )
        dark = 255 - np.asarray(r, dtype=np.float32)
        score = float(np.var(dark.sum(axis=1)))
        if score > best_score:
            best, best_score = float(tenth), score
    return best


def sauvola(arr, window=31, k=0.2, r=128.0):
    """Local threshold (Sauvola) with integral images."""
    a = arr.astype(np.float64)
    pad = window // 2
    ap = np.pad(a, pad, mode="reflect")
    s = np.cumsum(np.cumsum(ap, axis=0), axis=1)
    s2 = np.cumsum(np.cumsum(ap * ap, axis=0), axis=1)
    s = np.pad(s, ((1, 0), (1, 0)))
    s2 = np.pad(s2, ((1, 0), (1, 0)))
    h, w = a.shape
    n = window * window

    def box(t):
        return (
            t[window : window + h, window : window + w]
            - t[0:h, window : window + w]
            - t[window : window + h, 0:w]
            + t[0:h, 0:w]
        )

    mean = box(s) / n
    var = np.maximum(box(s2) / n - mean * mean, 0)
    thr = mean * (1 + k * (np.sqrt(var) / r - 1))
    return np.where(a > thr, 255, 0).astype(np.uint8)


def prepare(img, p):
    """Apply the steps; returns a grey PIL image."""
    img = img.convert("L")
    img = crop(img, p)
    if p.deskew:
        angle = skew_angle(img)
        if abs(angle) > 0.01:
            img = img.rotate(
                angle,
                resample=Image.BICUBIC,
                fillcolor=255,
                expand=False,
            )
    if p.scale != 1.0:
        size = (
            int(img.width * p.scale),
            int(img.height * p.scale),
        )
        img = img.resize(size, Image.LANCZOS)
    if p.binarize:
        arr = sauvola(np.asarray(img), p.window, p.k)
        img = Image.fromarray(arr)
    return img
