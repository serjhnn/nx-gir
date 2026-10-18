#!/usr/bin/env python3
"""Download a Bible book in Grabar as a text file.

Source: the Venice 1895 Armenian Bible (ed. Arsen
Bagratuni, public domain) as published at
bible.armeniancathedral.org. Usage:

    scripts/fetch-bible.py CODE CHAPTERS TITLE OUT

e.g. scripts/fetch-bible.py Mt 28 \\
    "Աւետարան ըստ Մատթէոսի" books/.../1-matthew.txt

Cleanup: the site's ":" and "`" become the Armenian
full stop ։ and comma ՝, footnote markers like [12]
and the `` closing a footnoted passage are removed,
and a stop doubled around a marker is kept once. Each
chapter starts with a heading Գլուխ Ա, Գլուխ Բ, ….
A report of what was changed goes to stderr.
"""

import re
import sys
import time
import urllib.request
from html.parser import HTMLParser

URL = "https://bible.armeniancathedral.org/book/t{}_{}.htm"
HEADERS = {
    "Accept": "text/html,*/*",
    "User-Agent": "nx-gir/0 (+github.com/serjhnn/nx-gir)",
}
ONES = "ԱԲԳԴԵԶԷԸԹ"
TENS = "ԺԻԼԽԾԿՀՁՂ"


def armenian_number(n):
    """1-99 in Armenian letters: 11 -> ԺԱ."""
    tens = TENS[n // 10 - 1] if n >= 10 else ""
    ones = ONES[n % 10 - 1] if n % 10 else ""
    return tens + ones


class Verses(HTMLParser):
    """Text of each <td class='arm'> cell, without the
    tooltip <span>s. Some cells leave a span open, so
    the tooltip count starts at 0 in every cell."""

    def __init__(self):
        super().__init__()
        self.cells = []
        self.cur = None
        self.depth = 0
        self.tip = 0  # open tooltip spans

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        if tag == "td" and cls == "arm":
            self.cur, self.depth, self.tip = [], 1, 0
        elif self.cur is not None:
            if tag == "td":
                self.depth += 1
            elif tag == "span" and cls.startswith(
                "tooltip"
            ):
                self.tip += 1

    def handle_endtag(self, tag):
        if self.cur is None:
            return
        if tag == "span" and self.tip:
            self.tip -= 1
        if tag == "td":
            self.depth -= 1
            if self.depth == 0:
                self.cells.append("".join(self.cur))
                self.cur = None

    def handle_data(self, data):
        if self.cur is not None and not self.tip:
            self.cur.append(data)


def fetch(code, chapter):
    req = urllib.request.Request(
        URL.format(code, chapter), headers=HEADERS
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    p = Verses()
    p.feed(html)
    return [re.sub(r"\s+", " ", c).strip() for c in p.cells]


def clean(text, notes):
    """One verse in Armenian marks, markers removed."""
    n = len(re.findall(r"\[\d+\]", text))
    if n:
        notes["footnote markers"] += n
    text = re.sub(r"\[\d+\]", "", text).replace("``", "")
    text = text.replace(":", "։")
    text = text.replace("`", "՝")
    if "։։" in text:
        notes["doubled full stops"] += 1
        text = text.replace("։։", "։")
    return re.sub(r"\s+", " ", text).strip()


def main(argv):
    if len(argv) != 4:
        sys.exit(__doc__)
    code, chapters, title, out = argv
    notes = {"footnote markers": 0, "doubled full stops": 0}
    parts = [title, ""]
    total = 0
    for c in range(1, int(chapters) + 1):
        parts += ["", f"Գլուխ {armenian_number(c)}", ""]
        nums = []
        for cell in fetch(code, c):
            m = re.match(rf"{c}:(\d+) (.*)", cell)
            if not m:
                print(
                    f"skipped in {c}: {cell[:40]}",
                    file=sys.stderr,
                )
                continue
            nums.append(int(m.group(1)))
            parts.append(clean(m.group(2), notes))
        missing = sorted(
            set(range(1, max(nums) + 1)) - set(nums)
        )
        if missing:
            print(
                f"{code} {c}: no verse {missing}",
                file=sys.stderr,
            )
        total += len(nums)
        time.sleep(0.5)  # be gentle with the site
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts).strip() + "\n")
    print(
        f"{out}: {chapters} chapters, {total} verses; "
        + ", ".join(f"{v} {k}" for k, v in notes.items()),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
