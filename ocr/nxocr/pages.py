"""Page images from a PDF (pdftoppm) or a folder."""

import subprocess
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def render(pdf, page, out_dir, dpi=300):
    """Render one PDF page (1-based) to a grey PNG.

    Cached: an existing file is reused.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"{Path(pdf).stem}-{dpi}"
    path = Path(f"{stem}-{page:04d}.png")
    if not path.exists():
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-r",
                str(dpi),
                "-gray",
                "-png",
                "-singlefile",
                str(pdf),
                str(path.with_suffix("")),
            ],
            check=True,
        )
    return path


def count(pdf):
    """Number of pages of a PDF."""
    out = subprocess.run(
        ["pdfinfo", str(pdf)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise ValueError("no page count")


def parse_range(spec, total=None):
    """`26-156,160` -> [26, ..., 156, 160]."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    if total:
        out = [p for p in out if 1 <= p <= total]
    return out


def spread(pages, n):
    """n pages spread evenly over the list."""
    if n <= 0 or n >= len(pages):
        return list(pages)
    step = len(pages) / n
    return [
        pages[int(i * step + step / 2)] for i in range(n)
    ]
