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
    trim: bool = False  # cut off the binding and what lies
    # beyond it (see trim_edges)


def dark_runs(share):
    """(start, end) of the runs of True in a list."""
    runs, start = [], None
    for i, flag in enumerate(share):
        if flag and start is None:
            start = i
        if not flag and start is not None:
            runs.append((start, i))
            start = None
    if start is not None:
        runs.append((start, len(share)))
    return runs


def trim_edges(img, dark=110, line=0.5, zone=0.4):
    """Cut a page scanned in a spread at its binding.

    A book pressed open shows a long black line (the edge
    of the page or the binding), and beyond it a strip of
    the facing page, whose text would be read as part of
    this page. A column that is dark for `line` of the
    height, in the outer `zone` of the page, is such a line:
    the page is cut at the innermost one on each side. The
    same for the rows at the top and bottom. A page with
    no such line is returned as it is.
    """
    arr = np.asarray(img.convert("L")) < dark
    h, w = arr.shape
    cols = arr.mean(axis=0) > line
    left, right = 0, w
    for a, b in dark_runs(cols):
        if b <= w * zone:
            left = max(left, b)
        if a >= w * (1 - zone):
            right = min(right, a)
    rows = arr.mean(axis=1) > line
    top, bottom = 0, h
    for a, b in dark_runs(rows):
        if b <= h * 0.15:
            top = max(top, b)
        if a >= h * 0.85:
            bottom = min(bottom, a)
    if right - left < w * 0.3 or bottom - top < h * 0.3:
        return img
    if (left, top, right, bottom) == (0, 0, w, h):
        return img
    return img.crop((left, top, right, bottom))


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
    if p.trim:
        img = trim_edges(img)
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
