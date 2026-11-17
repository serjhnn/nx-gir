"""Recognition with Tesseract, with confidences.

`recognize()` returns a Page of lines; every word has
the engine's confidence (0-100). The engines are meant
to be swapped: anything with the same Page shape (a
fine-tuned model, an LLM reading low-confidence lines)
can replace it in the pipeline.
"""

import csv
import io
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Word:
    text: str
    conf: float
    box: tuple = (0, 0, 0, 0)  # left, top, width, height


@dataclass
class Line:
    words: list = field(default_factory=list)

    @property
    def text(self):
        return " ".join(w.text for w in self.words)

    @property
    def conf(self):
        if not self.words:
            return 0.0
        return sum(w.conf for w in self.words) / len(
            self.words
        )


@dataclass
class Page:
    lines: list = field(default_factory=list)

    @property
    def text(self):
        return "\n".join(ln.text for ln in self.lines)

    def words(self):
        return [w for ln in self.lines for w in ln.words]


def parse_tsv(tsv):
    """Tesseract's TSV output -> Page."""
    page = Page()
    cur, last = None, None
    reader = csv.DictReader(
        io.StringIO(tsv),
        delimiter="\t",
        quoting=csv.QUOTE_NONE,
    )
    for row in reader:
        if row["level"] != "5":
            continue
        text = (row["text"] or "").strip()
        if not text:
            continue
        ident = (
            row["block_num"],
            row["par_num"],
            row["line_num"],
        )
        if ident != last:
            cur = Line()
            page.lines.append(cur)
            last = ident
        box = tuple(
            int(row[k])
            for k in ("left", "top", "width", "height")
        )
        cur.words.append(
            Word(text, float(row["conf"]), box)
        )
    return page


def recognize(
    img, lang="hye", psm=6, tessdata=None, extra=()
):
    """OCR a PIL image with the `tesseract` program."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "page.png"
        img.save(path)
        cmd = ["tesseract", str(path), "stdout"]
        if tessdata:
            cmd += ["--tessdata-dir", str(tessdata)]
        cmd += [
            "-l",
            lang,
            "--psm",
            str(psm),
            "-c",
            "tessedit_create_tsv=1",
            *extra,
        ]
        out = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
    return parse_tsv(out.stdout)
