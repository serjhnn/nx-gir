#!/usr/bin/env python3
"""Download a book from Digilib as text files.

Digilib (digilib.am) is the Armenian digital library of
the American University of Armenia; its classical
section has typed texts of Grabar works. Usage:

    scripts/fetch-digilib.py [--by-id] ID TITLE OUT [CACHE]

e.g. scripts/fetch-digilib.py 1476 \\
    "Գիրք քարոզութեան որ կոչի Ձմեռան հատոր" \\
    books/grabar/grigor-tatevatsi/2-dzmeran-hator

ID is the number in the book's address
(digilib.am/book/1476/...). OUT is a folder; the book
is written into it in parts of about PART characters,
01.txt, 02.txt, …, each starting with TITLE · n/total.
Each section of the book becomes a heading line
followed by its paragraphs, one per line. The text
of each section is kept in CACHE (default
.digilib-cache/ID), so an interrupted run continues
where it stopped. A section with the very same text as
the one before it (Digilib does that for a heading
with no text, Թովմա Մեծոփեցի's appendix) keeps its
heading and has no text. A report goes to stderr.

Digilib lists the sections of some books sorted by
title, not in reading order (Movses Khorenatsi: the
chapter Ա of all three books, then Բ, …). With
--by-id the sections are put in the order of their
numbers in the addresses, which is the book's own.
"""

import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SITE = "https://www.digilib.am"
HEADERS = {
    "Accept": "text/html,*/*",
    "User-Agent": "nx-gir/0 (+github.com/serjhnn/nx-gir)",
}
DELAY = 3.0  # seconds between requests
# characters per file: a big book is cut into parts so
# that the reader stays quick on a phone
PART = 150_000


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(
                req, timeout=180
            ) as r:
                return r.read().decode("utf-8")
        except OSError as e:
            if attempt == 3:
                raise
            print(f"retry {url[:60]}: {e}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))


def section(url, path):
    """Paragraphs of the section at url; saved in path
    (the pages are big, so only their text is kept)."""
    if path.exists():
        return path.read_text(encoding="utf-8").split("\n")
    text = Text()
    text.feed(get(url))
    paras = text.paragraphs()
    path.write_text("\n".join(paras), encoding="utf-8")
    time.sleep(DELAY)
    return paras


class Sections(HTMLParser):
    """[(url, title)] of the links to a book's sections,
    in page order."""

    def __init__(self, book):
        super().__init__()
        self.pat = re.compile(rf"/book/{book}/\d+/(\d+)/")
        self.found = []
        self.seen = set()
        self.cur = None

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href") or ""
        m = self.pat.search(href)
        if tag == "a" and m and m.group(1) not in self.seen:
            self.seen.add(m.group(1))
            self.cur = [href, []]

    def handle_endtag(self, tag):
        if tag == "a" and self.cur:
            href, parts = self.cur
            title = " ".join("".join(parts).split())
            self.found.append((href, title.lstrip("﻿")))
            self.cur = None

    def handle_data(self, data):
        if self.cur:
            self.cur[1].append(data)


# tags that start or end a paragraph
BREAKS = {"br", "p", "div", "h1", "h2", "h3", "h4", "li"}


class Text(HTMLParser):
    """Paragraphs of the reader box (the first div with
    class WordLabel)."""

    def __init__(self):
        super().__init__()
        self.depth = 0  # divs open inside the box
        self.done = False
        self.lines = [[]]

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        if self.done:
            return
        if self.depth:
            if tag == "div":
                self.depth += 1
            if tag in BREAKS:
                self.lines.append([])
        elif tag == "div" and "WordLabel" in cls:
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth and tag in BREAKS:
            self.lines.append([])
        if self.depth and tag == "div":
            self.depth -= 1
            self.done = not self.depth

    def handle_data(self, data):
        if self.depth:
            self.lines[-1].append(data)

    def paragraphs(self):
        out = []
        for parts in self.lines:
            line = " ".join("".join(parts).split())
            line = line.replace("﻿", "")
            if line:
                out.append(line)
        return out


def split(sections, size):
    """Group [(heading, paragraphs)] into parts of about
    size characters; a section is never cut."""
    parts, cur, n = [], [], 0
    for head, paras in sections:
        length = len(head) + sum(len(p) for p in paras)
        if cur and n + length > size:
            parts.append(cur)
            cur, n = [], 0
        cur.append((head, paras))
        n += length
    return parts + [cur] if cur else parts


def blank_repeats(sections):
    """Sections with the very same paragraphs as the one
    before them (Digilib shows the text above again
    for a heading with none of its own) lose them."""
    out = []
    last = None
    for head, paras in sections:
        if paras and paras == last:
            paras = []
        elif paras:
            last = paras
        out.append((head, paras))
    return out


def section_id(href):
    """The section number in a Digilib address
    (/book/286/291/6043/...), as a number."""
    return int(href.split("/")[6])


def main(argv):
    by_id = "--by-id" in argv
    argv = [a for a in argv if a != "--by-id"]
    if len(argv) not in (3, 4):
        sys.exit(__doc__)
    book, title, out = argv[:3]
    cache = Path(
        argv[3]
        if len(argv) == 4
        else f".digilib-cache/{book}"
    )
    cache.mkdir(parents=True, exist_ok=True)
    toc = Sections(book)
    toc.feed(get(f"{SITE}/book/{book}/"))
    print(f"{len(toc.found)} sections", file=sys.stderr)
    sections = []
    found = list(enumerate(toc.found, 1))
    if by_id:
        found.sort(key=lambda x: section_id(x[1][0]))
    for k, (n, (href, head)) in enumerate(found, 1):
        url = urllib.parse.urljoin(SITE, href)
        paras = section(url, cache / f"{n:04}.txt")
        paras = [p for p in paras if p]
        if paras and paras[0] == head:
            paras = paras[1:]  # the heading is repeated
        sections.append((head, paras))
        if k % 25 == 0:
            print(f"{n}/{len(toc.found)}", file=sys.stderr)
    sections = blank_repeats(sections)
    empty = [h for h, paras in sections if not paras]
    folder = Path(out)
    folder.mkdir(parents=True, exist_ok=True)
    parts = split(sections, PART)
    for i, part in enumerate(parts, 1):
        lines = [f"{title} · {i}/{len(parts)}", ""]
        for head, paras in part:
            lines += ["", head, ""] + paras
        path = folder / f"{i:02}.txt"
        path.write_text(
            "\n".join(lines).strip() + "\n",
            encoding="utf-8",
        )
    print(
        f"{out}: {len(toc.found)} sections in"
        f" {len(parts)} parts, {len(empty)} without text",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
