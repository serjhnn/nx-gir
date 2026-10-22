"""Grabar helpers: abbreviations of old manuscripts.

The list is grabar/abbreviations.tsv; see the notes at
its top for the sources.
"""

from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
ABBREVIATIONS = ROOT / "grabar" / "abbreviations.tsv"

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
    readings, then joined prepositions; [] if none."""
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
