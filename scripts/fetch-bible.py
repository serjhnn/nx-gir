#!/usr/bin/env python3
"""Download a Bible book in Armenian as a text file.

Source: the Venice 1895 Armenian Bible (ed. Arsen
Bagratuni, public domain) as published at
bible.armeniancathedral.org; with --1994, the
Eastern Armenian translation of Holy Etchmiadzin
(1994) from the same site. Usage:

    scripts/fetch-bible.py [--1994] CODE CHAPTERS \\
        TITLE OUT

e.g. scripts/fetch-bible.py Mt 28 \\
    "Աւետարան ըստ Մատթէոսի" books/.../1-matthew.txt

CHAPTERS is a count (28: chapters 1-28), a range
(1-3) or one chapter (118-118, written without a
chapter heading). Psalms use the Armenian (Greek)
numbering: Ps 118 is "Blessed are the undefiled".

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

SITE = "https://bible.armeniancathedral.org/"
URL = SITE + "book/t{}_{}.htm"
# the 1994 text: a JavaScript list on the site
URL_1994 = SITE + "_addon/main/t{}_{}.js"
HEADERS = {
    "Accept": "text/html,*/*",
    "User-Agent": "nx-gir/0 (+github.com/serjhnn/nx-gir)",
}
ONES = "ԱԲԳԴԵԶԷԸԹ"
TENS = "ԺԻԼԽԾԿՀՁՂ"
HUNDREDS = "ՃՄՅՆՇՈՉՊՋ"


def armenian_number(n):
    """1-999 in Armenian letters: 118 -> ՃԺԸ."""
    out = ""
    for digit, letters in (
        (n // 100, HUNDREDS),
        (n // 10 % 10, TENS),
        (n % 10, ONES),
    ):
        if digit:
            out += letters[digit - 1]
    return out


def chapter_range(arg):
    """'28' -> 1..28, '118-118' -> 118..118."""
    first, _, last = arg.partition("-")
    if not last:
        first, last = "1", first
    return range(int(first), int(last) + 1)


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


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def fetch(code, chapter):
    """The verses as "chapter:verse text"."""
    p = Verses()
    p.feed(get(URL.format(code, chapter)))
    return [re.sub(r"\s+", " ", c).strip() for c in p.cells]


def verses_1994(js, chapter):
    """The verses of the list arm_txt_1994 = [
    '1 text', ...] as "chapter:verse text"."""
    m = re.search(
        r"arm_txt_1994\s*=\s*\[(.*?)\n\s*\];", js, re.S
    )
    if not m:
        return []
    out = []
    for s in re.findall(r"'((?:[^'\\]|\\.)*)'", m[1]):
        s = re.sub(r"\\(.)", r"\1", s)
        out.append(f"{chapter}:" + s.strip())
    return out


def fetch_1994(code, chapter):
    js = get(URL_1994.format(code, chapter))
    return verses_1994(js, chapter)


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
    get_verses = fetch
    if argv[:1] == ["--1994"]:
        get_verses, argv = fetch_1994, argv[1:]
    if len(argv) != 4:
        sys.exit(__doc__)
    code, chapters, title, out = argv
    notes = {"footnote markers": 0, "doubled full stops": 0}
    parts = [title, ""]
    total = 0
    span = chapter_range(chapters)
    for c in span:
        if len(span) > 1:
            n = armenian_number(c)
            parts += ["", f"Գլուխ {n}", ""]
        nums = []
        for cell in get_verses(code, c):
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
        f"{out}: {len(span)} chapters, "
        f"{total} verses; "
        + ", ".join(f"{v} {k}" for k, v in notes.items()),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
