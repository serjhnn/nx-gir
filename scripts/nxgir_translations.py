"""Who made and reviewed the translations of nx-gir,
and their license: books/TRANSLATIONS.tsv (its head
explains the fields). The web reader and the book
pages of the site show credit() under each listed
translation. Tested in tests/test_translations.py.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS = ROOT / "books" / "TRANSLATIONS.tsv"
LICENSE = "CC BY-SA 4.0"
LICENSE_URL = (
    "https://creativecommons.org/licenses/by-sa/4.0/"
)
STATUSES = ("machine", "review", "reviewed")
# translations in books/ that are not ours, so not
# listed and not under LICENSE
NOT_OURS = ("ashkharhabar/bible/",)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# the credit line, by status; {who} are the
# reviewers, {v} the verb "է", or "են" for more
# than one
TEXTS = {
    "machine": (
        "Թարգմանությունը՝ Նախագիր · մեքենայական"
        " (Claude), դեռ չխմբագրված"
    ),
    "review": (
        "Թարգմանությունը՝ Նախագիր · մեքենայական"
        " (Claude), խմբագրում {v}՝ {who}"
    ),
    "reviewed": (
        "Թարգմանությունը՝ Նախագիր · Claude,"
        " խմբագրել {v}՝ {who}"
    ),
}


class TranslationsError(ValueError):
    """A bad line in TRANSLATIONS.tsv."""


def read(path=TRANSLATIONS):
    """The table as {path: {status, reviewers,
    date}}, in its order; lines starting with # are
    comments. None or a missing file: {}."""
    out = {}
    if not path or not Path(path).is_file():
        return out
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line[0] == "#":
                continue
            out.update([parse(line, f"{path}:{n}")])
    return out


def parse(line, where):
    """One line: (path, {status, reviewers,
    date})."""
    cols = line.split("\t")
    if len(cols) != 4:
        raise TranslationsError(
            f"{where}: not 4 fields split by tabs"
        )
    key, status, who, date = (c.strip() for c in cols)
    key = key.strip("/")
    if not key:
        raise TranslationsError(f"{where}: no path")
    if status not in STATUSES:
        raise TranslationsError(
            f"{where}: status not in {STATUSES}"
        )
    names = [w.strip() for w in who.split(",")]
    names = [w for w in names if w]
    if (status == "machine") != (not names):
        raise TranslationsError(
            f"{where}: reviewers only, and always,"
            " when not machine"
        )
    if not DATE_RE.fullmatch(date):
        raise TranslationsError(
            f"{where}: date not YYYY-MM-DD"
        )
    return key, {
        "status": status,
        "reviewers": names,
        "date": date,
    }


def find(table, name):
    """The line of table for a book name: its own,
    or the longest folder it is in; None if not
    listed."""
    best = None
    for key in table:
        if name == key or name.startswith(key + "/"):
            if best is None or len(key) > len(best):
                best = key
    return table[best] if best is not None else None


def text(entry):
    """The credit line of an entry, without the
    license."""
    who = entry["reviewers"]
    return TEXTS[entry["status"]].format(
        who=", ".join(who),
        v="են" if len(who) > 1 else "է",
    )


def credit(table, name):
    """What the reader shows under a translation:
    {status, reviewers, date, text, license, url},
    or None for a book not listed."""
    entry = find(table, name)
    if entry is None:
        return None
    return {
        **entry,
        "text": text(entry),
        "license": LICENSE,
        "url": LICENSE_URL,
    }
