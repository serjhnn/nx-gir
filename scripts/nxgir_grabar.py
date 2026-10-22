"""Grabar helpers: abbreviations of old manuscripts
and a vocabulary.

The lists are in grabar/; see the notes at the top of
each file for the sources.
"""

import functools
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
ABBREVIATIONS = ROOT / "grabar" / "abbreviations.tsv"
VOCABULARY = ROOT / "grabar" / "vocabulary.tsv"
FORMS = ROOT / "grabar" / "forms.tsv"

# kind -> heading, in the order they are listed
KINDS = {
    "sacred": "Sacred names (nomina sacra)",
    "word": "Words",
    "part": "One letter for part of a word",
    "name": "Names",
    "ending": "Word endings",
}
SOURCES = {
    "A": "Abrahamyan 1959, pp. 111-114",
    "W": "Wiktionary «՟»",
    "N": "nx-gir, not in a published source",
}
# prepositions written joined to the next word. They
# are not abbreviated, so a short word may carry one:
# յա՟մ = յ + ամենայն, իվ՟ր = ի վերայ. ի and յ are one
# word: յ before a vowel, ի (printed apart) before a
# consonant. This is a grammar rule, not an entry of
# the sources.
PREFIXES = {
    "յ": "in, into, from (before a vowel)",
    "ի": "in, into, from (before a consonant)",
    "զ": "marks a definite object",
    "ց": "to, up to, until",
}
# printed as a word of its own
APART = {"ի"}
VOWELS = set("աեէըիոօ")
# the pativ mark ՟ and the stress, exclamation and
# question marks are not part of the letters
MARKS = str.maketrans("", "", "՟՛՜՞")


class Abbr(NamedTuple):
    short: str
    full: str
    meaning: str
    kind: str
    sources: tuple
    example: str = ""

    def examples(self):
        """[(phrase, meaning)] from the example column."""
        out = []
        for ex in filter(None, self.example.split("; ")):
            text, _, meaning = ex.partition(": ")
            out.append((text, meaning))
        return out


def key(word):
    """Letters only, any case: ա՟ծ and ԱԾ -> ած."""
    return word.translate(MARKS).casefold()


def load(path=ABBREVIATIONS):
    """[Abbr] from the TSV file, in file order."""
    out = []
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        short, full, meaning, kind, src, *ex = line.split(
            "\t"
        )
        out.append(
            Abbr(
                short,
                full,
                meaning,
                kind,
                tuple(src.split()),
                *ex,
            )
        )
    return out


def expand(word, table=None):
    """[(full form, Abbr)] that a short word may stand
    for: whole words first, then endings."""
    table = load() if table is None else table
    k = key(word)
    out = [
        (a.full, a)
        for a in table
        if a.kind != "ending" and key(a.short) == k
    ]
    endings = sorted(
        (a for a in table if a.kind == "ending"),
        key=lambda a: -len(a.short),
    )
    for a in endings:
        end = key(a.short.lstrip("-"))
        if k.endswith(end) and len(k) > len(end):
            stem = word.translate(MARKS)[: -len(end)]
            out.append((stem + a.full.lstrip("-"), a))
            break  # the longest ending only
    return out


class Prefixed(NamedTuple):
    full: str
    prefix: str
    abbr: Abbr


def expand_prefix(word, table=None):
    """[Prefixed] for a short word that is a joined
    preposition and a whole-word abbreviation:
    յամ -> յամենայն (յ + ամ), իվր -> ի վերայ
    (ի + վր). Rests of one letter
    are skipped, they match too much."""
    table = load() if table is None else table
    plain = word.translate(MARKS)
    k = key(plain)
    out = []
    for pre in PREFIXES:
        rest = k[len(pre) :]
        if not k.startswith(pre) or len(rest) < 2:
            continue
        for a in table:
            if a.kind == "ending" or key(a.short) != rest:
                continue
            first = a.full[0].casefold()
            if pre == "յ" and first not in VOWELS:
                continue
            if pre == "ի" and first in VOWELS:
                continue
            space = " " if pre in APART else ""
            full = plain[: len(pre)] + space + a.full
            out.append(Prefixed(full, pre, a))
    return out


def search(query, table=None):
    """[Abbr] whose short or full form or meaning
    contains query."""
    table = load() if table is None else table
    q = key(query)
    return [
        a
        for a in table
        if q in key(a.short)
        or q in key(a.full)
        or q in a.meaning.casefold()
    ]


def lines(table, width=80):
    """The list as text, grouped by kind; a meaning
    that does not fit width goes on its own line."""
    out = []
    for kind, heading in KINDS.items():
        rows = [a for a in table if a.kind == kind]
        if not rows:
            continue
        if out:
            out.append("")
        out.append(heading)
        w = max(len(a.short) for a in rows)
        for a in rows:
            line = f"  {a.short:<{w}}  {a.full}"
            more = f"  · {a.meaning}"
            if len(line + more) < width:
                out.append(line + more)
            else:
                out += [line, f"    {more.strip()}"]
            out += example_lines(a, "    ")
    return out


def example_lines(a, indent="  "):
    """Lines of a's examples: e.g. text: "meaning"."""
    return [
        f'{indent}e.g. {text}: "{meaning}"'
        for text, meaning in a.examples()
    ]


def sources_line():
    """Sources: A = ..., W = ..."""
    return "Sources: " + "; ".join(
        f"{k} = {v}" for k, v in SOURCES.items()
    )


def explain(word, table=None):
    """Lines saying what a short word may stand for:
    readings, then joined prepositions; [] if none.
    For the meaning of a word see define()."""
    table = load() if table is None else table
    out = []
    for full, a in expand(word, table):
        out.append(f"{word} → {full}")
        out.append(f"  {a.meaning}")
        out += example_lines(a, "  ")
        if "N" in a.sources:
            out.append("  not in a published source yet")
    if out:
        return out
    for full, pre, a in expand_prefix(word, table):
        out.append(f"{word} → {full}")
        out.append(f"  {pre}- {PREFIXES[pre]}")
        out.append(f"  + {a.short} = {a.full}")
        out.append(f"    {a.meaning}")
    return out


# the article joined to the end of a word: a grammar
# rule, like PREFIXES
ARTICLES = {
    "ս": "the article: this (by me)",
    "դ": "the article: that (by you)",
    "ն": "the article: the, that",
}


class Word(NamedTuple):
    word: str
    pos: str
    meanings: tuple


def tsv(path):
    """Rows of a TSV file, without comments."""
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            yield line.split("\t")


@functools.cache
def vocabulary(words=VOCABULARY, forms=FORMS):
    """({key: [Word]}, {form key: [headword]})."""
    heads, inflected = {}, {}
    for word, pos, meanings in tsv(words):
        w = Word(word, pos, tuple(meanings.split(" | ")))
        heads.setdefault(key(word), []).append(w)
    for form, word in tsv(forms):
        inflected.setdefault(key(form), []).append(word)
    return heads, inflected


def readings(k):
    """Ways to read the letters k: (rest, notes) with
    a joined preposition or article taken off; as is
    first."""
    out = [(k, ())]
    ends = [(k, ())]
    if len(k) > 2 and k[-1] in ARTICLES:
        a = k[-1]
        ends.append((k[:-1], (f"-{a} {ARTICLES[a]}",)))
        out.append(ends[-1])
    for pre in PREFIXES:
        if pre in APART:
            continue
        for rest, notes in ends:
            if rest.startswith(pre) and len(rest) > 2:
                note = f"{pre}- {PREFIXES[pre]}"
                out.append((rest[1:], (note, *notes)))
    return out


def lookup(word, vocab=None):
    """[(Word, notes)] for word: the headword, the
    headword of an inflected form, then the same with
    a joined preposition or article taken off."""
    heads, inflected = vocab or vocabulary()
    for k, notes in readings(key(word)):
        found = list(heads.get(k, []))
        for head in inflected.get(k, []):
            for w in heads.get(key(head), []):
                if w not in found:
                    found.append(w)
        if found:
            return [(w, notes) for w in found]
    return []


def define(word, vocab=None):
    """Lines saying what word means; [] if it is not
    in the vocabulary."""
    found = lookup(word, vocab)
    if not found:
        return []
    out = []
    for w, _ in found:
        out.append(f"{w.word} · {w.pos}")
        out += [f"  {m}" for m in w.meanings]
    notes = found[0][1]
    if notes:
        out.append(f"{word}:")
        out += [f"  {n}" for n in notes]
    out.append("Source: Wiktionary (CC BY-SA)")
    return out
