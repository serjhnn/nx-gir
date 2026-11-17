"""Line samples for training: a line image and its text.

The typed text has no line breaks that match the scan,
so each line the engine found is aligned to the typed
text and takes the stretch it covers. Lines that do not
align well, or hold characters the model does not know,
are left out: a wrong label teaches more harm than a
missing one.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import metrics
from .textnorm import key


@dataclass
class Sample:
    page: int
    index: int
    box: tuple  # left, top, right, bottom
    text: str  # the typed line
    cer: float  # OCR line against the typed line


def model_chars(traineddata):
    """Characters of a model's unicharset (plus space)."""
    out = Path(traineddata).with_suffix(".lstm-unicharset")
    subprocess.run(
        [
            "combine_tessdata",
            "-e",
            str(traineddata),
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    chars = {" "}
    rows = out.read_text(encoding="utf8").split("\n")[1:]
    for row in rows:
        if row:
            chars.add(row.split()[0])
    return chars


def line_box(line, pad=6, size=None):
    xs = [w.box[0] for w in line.words]
    ys = [w.box[1] for w in line.words]
    xe = [w.box[0] + w.box[2] for w in line.words]
    ye = [w.box[1] + w.box[3] for w in line.words]
    box = (
        min(xs) - pad,
        min(ys) - pad,
        max(xe) + pad,
        max(ye) + pad,
    )
    if size:
        w, h = size
        box = (
            max(box[0], 0),
            max(box[1], 0),
            min(box[2], w),
            min(box[3], h),
        )
    return box


def split_lines(
    page, ref, chars=None, max_cer=0.5, size=None
):
    """(reference start, samples) for one OCR page."""
    lines, texts = [], []
    for ln in page.lines:
        k = "".join(key(w.text) for w in ln.words)
        if k:
            lines.append(ln)
            texts.append(k)
    joined = "".join(texts)
    if len(joined) < 20:
        return None, []
    span = ref.locate(joined)
    if span is None:
        return None, []
    window = ref.text[span[0] : span[1]]
    items, start, _ = metrics.ops(joined, window, True)
    # reference position of every OCR character
    place, b = [], start
    for op, _, _ in items:
        if op == "+":
            b += 1
            continue
        place.append(b)
        if op != "-":
            b += 1
    place.append(b)
    out, a = [], 0
    for n, (ln, k) in enumerate(zip(lines, texts)):
        lo, hi = place[a], place[a + len(k)]
        a += len(k)
        if hi <= lo:
            continue
        text = ref.original(span[0] + lo, span[0] + hi)
        text = " ".join(text.split())
        rkey = key(text)
        if not rkey or not text:
            continue
        if chars and any(c not in chars for c in text):
            continue
        cer = metrics.distance(k, rkey) / len(rkey)
        if cer > max_cer:
            continue
        out.append(
            Sample(0, n, line_box(ln, size=size), text, cer)
        )
    return span[0], out
