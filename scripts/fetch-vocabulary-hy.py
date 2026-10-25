#!/usr/bin/env python3
"""Build the Armenian meanings of Grabar words.

Source: the Armenian Wiktionary (hy.wiktionary.org),
from its dump on dumps.wikimedia.org. Its text is
under CC BY-SA 4.0. Usage:

    scripts/fetch-vocabulary-hy.py [DUMP]

DUMP is a pages-articles .xml.bz2 (or .xml) file;
without it the latest dump is downloaded (40 MB).
Writes grabar/vocabulary-hy.tsv.

The entries are modern Armenian, in the reformed
spelling. A Grabar word gets an entry when:

- a headword of grabar/vocabulary.tsv is the entry's
  title or its classical spelling ({{why|...}}), or
  is, after simple spelling rules (reform()), the
  entry's title; or
- the word is the classical spelling ({{why|...}}) of
  an entry.
"""

import bz2
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nxgir_grabar import VOCABULARY, key, tsv  # noqa: E402

URL = (
    "https://dumps.wikimedia.org/hywiktionary/latest/"
    "hywiktionary-latest-pages-articles.xml.bz2"
)
HEADERS = {
    "User-Agent": "nx-gir/0 (+github.com/serjhnn/nx-gir)",
}
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "grabar" / "vocabulary-hy.tsv"
POS_TPL = "Կաղապար:-hy-"
REDIRECT = re.compile(
    r"#ՎԵՐԱՀՂՈՒՄ\s*\[\[:?Կաղապար:-hy-(.+?)-\]\]"
)
H2 = re.compile(r"<h2>(.*?)</h2>", re.S)
LANG = re.compile(r"\{\{-([a-z]+)-\}\}")
POS = re.compile(r"\{\{-hy-(.+?)-\}\}")
WHY = re.compile(r"\{\{why\|([^}|]+)")
INNER = re.compile(r"\{\{([^{}]*)\}\}")
LINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")
REF = re.compile(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", re.S)
TAG = re.compile(r"<[^>]+>")
ARMENIAN = re.compile("[Ա-և][Ա-և. ․]*")
# examples and their authors: left out
EXAMPLES = {"օրն", "օրինակ", "Հեղինակ"}
LETTER = re.compile("[Ա-և]")
WORD = re.compile("[Ա-և]+")

HEAD = """\
# Armenian meanings of Grabar words, from the Armenian
# Wiktionary (dump downloaded on {date}, {url}).
# Text under CC BY-SA 4.0: Wiktionary contributors,
# https://hy.wiktionary.org/wiki/<entry>
# The entries are modern Armenian (reformed spelling);
# entry is the Wiktionary title for word.
# Built by scripts/fetch-vocabulary-hy.py; do not edit
# by hand, run the script again.
#
# Columns: word, entry, pos, meanings (split by ' | ')
#
"""


def reform(word):
    """word in the reformed spelling, roughly: յոյս ->
    հոյս, իւր -> յուր, ճաշեմ -> ճաշել. Only used to
    find an entry for a word that has none as is."""
    w = word.replace("իւ", "յու").replace("եա", "յա")
    w = re.sub("^յ", "հ", w)
    w = re.sub("^ո(?!ւ)", "վո", w)
    w = re.sub("(?<=.)է", "ե", w)
    w = re.sub("եւ", "և", w)
    w = re.sub("(?<!ո)ւ", "վ", w)
    w = re.sub("եմ$", "ել", w)
    w = re.sub("իմ$", "վել", w)
    w = re.sub("ամ$", "ալ", w)
    return w


def template(body):
    """The text a template stands for: its word for
    {{ընդգծել|word}}, a label like 'փխբ.' for a label
    template ({{փխբ}}, {{հնց|es}}); else nothing."""
    name, *args = [x.strip() for x in body.split("|")]
    if name == "ընդգծել":
        return args[0] if args else ""
    if name in EXAMPLES:
        return ""
    short = all(re.fullmatch("[a-z]{0,3}", a) for a in args)
    if (
        short
        and ARMENIAN.fullmatch(name)
        and len(name) < 16
    ):
        return name if name[-1] in ".․" else name + "."
    return ""


def clean(line):
    """Plain text of a definition line, or ''."""
    t = REF.sub("", line)
    while True:
        t2 = INNER.sub(lambda m: template(m.group(1)), t)
        if t2 == t:
            break
        t = t2
    t = LINK.sub(r"\1", t)
    t = TAG.sub("", t).replace("'''", "").replace("''", "")
    t = re.sub(r"\(\s*\)", "", t)
    t = " ".join(t.split()).strip(" ,;:")
    return t if LETTER.search(t) else ""


def senses(text):
    """[(pos code, [meanings])] of the Armenian part
    of a page, and its classical spellings."""
    out, pos, hy = [], None, False
    for line in text.splitlines():
        s = line.strip()
        m = LANG.match(s)
        if m:
            hy, pos = m.group(1) == "hy", None
            continue
        m = POS.match(s)
        if m and hy:
            pos = m.group(1)
            out.append((pos, []))
            continue
        if s.startswith("="):
            pos = None
        elif pos and re.match(r"#[^#:*]", s):
            t = clean(s[1:])
            if t and t not in out[-1][1]:
                out[-1][1].append(t)
    out = [(p, ms) for p, ms in out if ms]
    why = [w.strip() for w in WHY.findall(text)]
    why = [w for w in why if WORD.fullmatch(w)]
    return out, why if out else []


def pos_name(tpl_text, tpls, seen=()):
    """Part of speech shown by a -hy-X- template."""
    m = REDIRECT.search(tpl_text)
    if m and m.group(1) not in seen:
        nxt = tpls.get(m.group(1), "")
        return pos_name(nxt, tpls, (*seen, m.group(1)))
    m = H2.search(tpl_text)
    if not m:
        return ""
    name = clean(m.group(1)).removeprefix("Հայերեն ")
    if name in ("Բացատրություն", ""):
        return ""
    return name[0].lower() + name[1:]


def read(stream):
    """{title: (senses, why)} and {pos code: text}."""
    pages, tpls = {}, {}
    for _, el in ET.iterparse(stream):
        if el.tag.rsplit("}", 1)[-1] != "page":
            continue
        title = text = ""
        for c in el.iter():
            tag = c.tag.rsplit("}", 1)[-1]
            if tag == "title":
                title = c.text or ""
            elif tag == "text":
                text = c.text or ""
        if title.startswith(POS_TPL):
            tpls[title[len(POS_TPL) : -1]] = text
        elif ":" not in title and "{{-hy-}}" in text:
            got, why = senses(text)
            if got:
                pages[title] = (got, why)
        el.clear()
    return pages, tpls


def match(pages, heads):
    """[(word, entry)]: entries for each Grabar
    headword, then the classical spellings."""
    by_key = {}
    for title, (_, why) in pages.items():
        for w in (title, *why):
            by_key.setdefault(key(w), []).append(title)
    out = []
    for h in heads:
        found = by_key.get(key(h))
        if not found:
            r = key(reform(key(h)))
            found = [t for t in by_key.get(r, ())]
        out += [(h, t) for t in dict.fromkeys(found or ())]
    known = {key(h) for h in heads}
    for title, (_, why) in pages.items():
        for w in dict.fromkeys(why):
            if key(w) not in known:
                out.append((w, title))
    return list(dict.fromkeys(out))


def write(rows, pages, names, date):
    with open(OUT, "w") as f:
        f.write(HEAD.format(date=date, url=URL))
        for word, title in rows:
            for code, ms in pages[title][0]:
                pos = names.get(code, "")
                line = " | ".join(ms)
                f.write(f"{word}\t{title}\t{pos}\t{line}\n")


def main(argv):
    if len(argv) > 1:
        path = argv[1]
        opener = bz2.open if path.endswith(".bz2") else open
        stream = opener(path, "rb")
    else:
        req = urllib.request.Request(URL, headers=HEADERS)
        stream = bz2.open(urllib.request.urlopen(req))
    with stream:
        pages, tpls = read(stream)
    names = {c: pos_name(t, tpls) for c, t in tpls.items()}
    heads = list(
        dict.fromkeys(r[0] for r in tsv(VOCABULARY))
    )
    rows = match(pages, heads)
    write(rows, pages, names, time.strftime("%Y-%m-%d"))
    found = len({w for w, _ in rows} & set(heads))
    print(
        f"{len(rows)} rows; {found} of {len(heads)}"
        " Grabar headwords have an entry",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
