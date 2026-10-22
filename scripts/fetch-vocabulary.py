#!/usr/bin/env python3
"""Build the Grabar vocabulary from Wiktionary.

Source: the Old Armenian entries of the English
Wiktionary, as extracted by kaikki.org (wiktextract).
Their text is under CC BY-SA 4.0. Usage:

    scripts/fetch-vocabulary.py [JSONL]

Without JSONL the extract is downloaded. Writes
grabar/vocabulary.tsv (word, part of speech, meanings)
and grabar/forms.tsv (an inflected form and its
headword, from the declension and conjugation tables).
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

URL = (
    "https://kaikki.org/dictionary/Old%20Armenian/"
    "kaikki.org-dictionary-OldArmenian.jsonl"
)
HEADERS = {
    "User-Agent": "nx-gir/0 (+github.com/serjhnn/nx-gir)",
}
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "grabar"
TABLES = {"declension", "conjugation"}
# a form is Armenian letters (and marks) only: no
# tags, templates, phrases or transliterations
FORM_RE = re.compile("[\u0531-\u0587]+")

HEAD = """\
# Old Armenian (Grabar) vocabulary, from the English
# Wiktionary as extracted by kaikki.org on {date}
# ({url}).
# Text under CC BY-SA 4.0: Wiktionary contributors,
# https://en.wiktionary.org/wiki/<word>#Old_Armenian
# Built by scripts/fetch-vocabulary.py; do not edit by
# hand, run the script again.
#
"""


def clean(text):
    return " ".join(text.split())


def entries(rows):
    """[(word, pos, meanings)] and {(form, word)}."""
    words, forms = [], set()
    for r in rows:
        word = r.get("word", "")
        glosses = []
        for s in r.get("senses", []):
            g = "; ".join(map(clean, s.get("glosses", [])))
            if g and g not in glosses:
                glosses.append(g)
        if not word or not glosses:
            continue
        words.append((word, r.get("pos", ""), glosses))
        for f in r.get("forms", []):
            form = f.get("form", "")
            if f.get("source") not in TABLES:
                continue
            if not form or form == word:
                continue
            if not FORM_RE.fullmatch(form):
                continue
            forms.add((form, word))
    return words, forms


def write(words, forms, date):
    head = HEAD.format(date=date, url=URL)
    with open(OUT / "vocabulary.tsv", "w") as f:
        f.write(head)
        f.write("# Columns: word, pos, meanings")
        f.write(" (split by ' | ')\n#\n")
        for word, pos, glosses in words:
            line = " | ".join(glosses)
            f.write(f"{word}\t{pos}\t{line}\n")
    with open(OUT / "forms.tsv", "w") as f:
        f.write(head)
        f.write("# Columns: form, word (a headword")
        f.write(" of vocabulary.tsv)\n#\n")
        for form, word in sorted(forms):
            f.write(f"{form}\t{word}\n")


def main(argv):
    if len(argv) > 1:
        text = Path(argv[1]).read_text(encoding="utf-8")
    else:
        req = urllib.request.Request(URL, headers=HEADERS)
        with urllib.request.urlopen(req) as r:
            text = r.read().decode("utf-8")
    rows = [json.loads(x) for x in text.splitlines() if x]
    words, forms = entries(rows)
    write(words, forms, time.strftime("%Y-%m-%d"))
    print(
        f"{len(words)} words, {len(forms)} forms",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
