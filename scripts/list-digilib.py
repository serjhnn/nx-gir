#!/usr/bin/env python3
"""List every book on Digilib, and guess which are in
Grabar.

    scripts/list-digilib.py [OUT]

Walks the whole library (digilib.am/am/library/all),
opens each book and a section from its middle (past
any modern foreword), and counts words typical of
Grabar against words typical of the modern language,
Eastern or Western. OUT (default notes/digilib.tsv)
gets one line per book; its head explains the fields.
Each book's result is kept in .digilib-cache/list/,
so an interrupted run continues where it stopped.
"""

import collections
import importlib.util
import json
import re
import sys
import time
import urllib.parse
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "fetch_digilib", ROOT / "scripts/fetch-digilib.py"
)
fd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fd)

SITE = fd.SITE
DELAY = 1.0  # seconds between requests
CACHE = ROOT / ".digilib-cache/list"
SORTS = (
    f"{SITE}/am/library/all",
    f"{SITE}/am/library/?sort=af",
    f"{SITE}/am/library/?sort=fa",
)

# words found often in Grabar and hardly ever in the
# modern language
GRABAR = set(
    "ամենայն նորա նոցա նմա նոքա նոսա սորա սոցա "
    "զի քանզի որպէս իբրեւ ասէ ասեն եղեւ ընդ յետ "
    "զնա զնոսա իւր իւրեանց մեք յայնժամ վասն "
    "յորժամ որոց որում ոչ ի յ".split()
)
# and the other way round (Eastern and Western)
MODERN = set(
    "կը կ պիտի ու համար հետ որը որոնք այդ շատ "
    "հիմա նրա նրանց իր իրենց մենք ենք էք արդէն "
    "դեռ նաեւ մասին միջոցով կողմից պէտք եմ ես "
    "այն է էր".split()
)
# modern plural and locative endings
ENDINGS = ("ները", "ների", "ում", "երը", "երի")
WORDS = 20  # fewer words than this: no verdict
# marker words needed for a verdict: more for
# modern, as Middle Armenian (medieval songs) shares
# its words (ու, կու)
MIN = 5
MIN_MODERN = 10


def score(text):
    """(Armenian words, Grabar markers, modern markers,
    Latin or Cyrillic words)."""
    words = re.findall(r"[\u0531-\u0587]+", text.lower())
    other = re.findall(r"[A-Za-z\u0400-\u04ff]{2,}", text)
    count = collections.Counter(words)
    g = sum(count[w] for w in GRABAR)
    m = sum(count[w] for w in MODERN)
    m += sum(
        n for w, n in count.items() if w.endswith(ENDINGS)
    )
    return len(words), g, m, len(other)


def judge(n, g, m, other=0):
    """The kind for the counts of score()."""
    if other >= WORDS and other > n:
        return "other language"
    if n < WORDS:
        return "no text"
    if g + m >= MIN and g >= 2 * m:
        return "grabar"
    if m >= MIN_MODERN and m >= 2 * g:
        return "modern"
    return "unclear"


def kind(text):
    """'grabar', 'modern', 'unclear', 'other
    language' or 'no text'."""
    return judge(*score(text))


def verdict(first, middle):
    """The book's kind from the text on its own page
    (often a foreword) and from a middle section."""
    a, b = kind(first), kind(middle)
    if b == "no text":
        return a
    if {a, b} == {"grabar", "modern"}:
        return "mixed"
    return b


def text(html):
    t = fd.Text()
    t.feed(html)
    return " ".join(t.paragraphs())


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s).replace("﻿", "")
    return " ".join(s.split())


def details(html):
    """Title, author, section and theme from a book's
    page."""
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    out = {"title": clean(m.group(1)) if m else ""}
    for key, label in (
        ("author", "Հեղինակ"),
        ("section", "Բաժին"),
        ("theme", "Թեմա"),
    ):
        m = re.search(
            rf'rm7">{label}</div>\s*'
            r'<div class="btn-group[^"]*">(.*?)</div>',
            html,
            re.S,
        )
        names = []
        if m:
            for a in re.findall(
                r"<a[^>]*>(.*?)</a>", m.group(1), re.S
            ):
                names.append(clean(a))
        out[key] = "; ".join(n for n in names if n)
    return out


def ids(html):
    """Book numbers linked from a listing page."""
    found = re.findall(r"/book/(\d+)/", html)
    return list(dict.fromkeys(found))


def fetch(url):
    html = fd.get(url)
    time.sleep(DELAY)
    return html


def book(n):
    """The cached result for book n."""
    path = CACHE / f"{n}.json"
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    html = fetch(f"{SITE}/book/{n}/")
    info = details(html)
    first = text(html)
    toc = fd.Sections(n)
    toc.feed(html)
    info["sections"] = len(toc.found)
    middle = ""
    mid = len(toc.found) // 2
    # sections can be short (a law, a heading): join
    # a few until there are words enough
    for href, _ in toc.found[mid : mid + 6]:
        url = urllib.parse.urljoin(SITE, href)
        middle += " " + text(fetch(url))
        n, _, _, other = score(middle)
        if max(n, other) >= WORDS:
            break
    n, g, m, o = score(middle or first)
    info.update(
        kind=verdict(first, middle),
        grabar=g,
        modern=m,
        words=n,
        other=o,
    )
    path.write_text(
        json.dumps(info, ensure_ascii=False), "utf-8"
    )
    return info


def library():
    """Every book number, page by page."""
    path = CACHE / "ids.json"
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    found = []
    # the pages stop at 44 (later ones repeat it), so
    # read the list in three orders: the default, A-Z
    # and Z-A; ?p=1 is a server error, page 1 has no p
    for base in SORTS:
        p = 1
        while True:
            url = base
            if p > 1:
                url += (
                    "&" if "?" in url else "?"
                ) + f"p={p}"
            new = [
                i for i in ids(fetch(url)) if i not in found
            ]
            if not new and p > 1:
                break
            found += new
            print(f"{url}: {len(found)}", file=sys.stderr)
            p += 1
    path.write_text(json.dumps(found), "utf-8")
    return found


def ours():
    """Book numbers already in books/ (from
    books/SOURCES.md)."""
    src = (ROOT / "books/SOURCES.md").read_text("utf-8")
    return set(re.findall(r"digilib\.am/book/(\d+)", src))


HEAD = """\
# Every book on Digilib (digilib.am), the digital
# library of the American University of Armenia,
# written by scripts/list-digilib.py on {date}.
# kind: the language of a section from the middle of
#   the book, guessed by counting words typical of
#   Grabar against words of the modern language:
#   grabar; modern (Eastern or Western); mixed (a
#   modern foreword before a Grabar text, or the
#   reverse); unclear (often Middle Armenian:
#   medieval songs, chronicles); other language
#   (English, French, Russian...); no text (no
#   typed text on Digilib: most of these, with 0
#   sections, are scans offered as PDF). A guess:
#   check a book before fetching it.
# grabar, modern: the marker words counted.
# ours: yes if the book is in books/ already.
# sections: the parts of the book on Digilib.
id\tkind\tgrabar\tmodern\tours\tauthor\ttitle\t\
section\ttheme\tsections\tlink
"""


def main(argv):
    if len(argv) > 1:
        sys.exit(__doc__)
    out = Path(argv[0] if argv else "notes/digilib.tsv")
    CACHE.mkdir(parents=True, exist_ok=True)
    have = ours()
    numbers = library()
    rows = []
    for i, n in enumerate(numbers, 1):
        try:
            b = book(n)
        except OSError as e:
            print(f"book {n}: {e}", file=sys.stderr)
            continue
        rows.append(
            [
                n,
                b["kind"],
                b["grabar"],
                b["modern"],
                "yes" if n in have else "",
                b["author"],
                b["title"],
                b["section"],
                b["theme"],
                b["sections"],
                f"{SITE}/book/{n}/",
            ]
        )
        if i % 50 == 0:
            print(f"{i}/{len(numbers)}", file=sys.stderr)
    rows.sort(key=lambda r: int(r[0]))
    date = time.strftime("%Y-%m-%d")
    lines = [HEAD.format(date=date).rstrip("\n")]
    for r in rows:
        cells = [str(c).replace("\t", " ") for c in r]
        lines.append("\t".join(cells))
    out.write_text("\n".join(lines) + "\n", "utf-8")
    kinds = collections.Counter(r[1] for r in rows)
    print(
        f"{len(rows)} books: {dict(kinds)}", file=sys.stderr
    )


if __name__ == "__main__":
    main(sys.argv[1:])
