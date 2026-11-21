"""Search across the library (see notes/search.md).

The books of grabar/ and their translations in
ashkharhabar/ (not the Bible, for now) are indexed
by word: every word under its loose key (loose()),
which folds the classical spelling and the reformed
one together, so թագավոր finds թագաւոր. Under the
key, each spelling found and the lines it is in.

This module only builds the index and serves it as
data; the search itself is in web/app.js, the same
for `nxgir web` (/api/search, /api/search-parts,
/api/lines) and for the Pages site, which has the
same answers as files (build-site.py):

    data/search/parts.json      parts()
    data/search/<n>.json        the entries of the
        keys in bucket n (bucket() of build-site.py)
    data/lines/<part>/<k>.json  chunk(): 100 lines

An entry is {spelling: [[part, line, +line, ...],
...]}: for each part (its number in parts()) its
lines, 1-based, the first one as it is and the
others as the step from the one before. A word in
more than COMMON lines is {"*": lines}: too common
to search alone (եւ, ի, որ ...).
"""

import json
import re

from nxgir_reader import WORD_RE, normalize

# the folders searched, in the order of the filters
TOPS = ("grabar", "ashkharhabar")
# authors left out: the Bible, for now
LEFT_OUT = ("bible",)
# a word in more lines than this is too common
COMMON = 5000
# lines in one file of data/lines/
CHUNK = 100
# the first line of a part of a long book:
# "title · 2/24" (as PART_RE in nxgir_web.py)
PART_RE = re.compile(r"^(.+) · (\d+)/(\d+)$")

# classical spellings and the reformed ones, folded
# to one key; the order matters (իւ before ւ)
FOLDS = (
    ("իւ", "յու"),
    ("եա", "յա"),
    ("եօ", "յո"),
)
YW_RE = re.compile(r"(?<!ո)ւ")
# յ at the start, before a vowel: յորժամ, հորժամ
Y_RE = re.compile(r"^յ(?=[աեէըիոօ])")


def loose(word):
    """Key of a word for search: normalize(), then
    the classical spelling folded into the reformed
    one: ւ → վ (not in ու), իւ → յու, եա → յա,
    եօ → յո, է → ե, օ → ո, and յ at the start before
    a vowel → հ. As loose() in web/app.js."""
    k = normalize(word)
    for a, b in FOLDS:
        k = k.replace(a, b)
    k = YW_RE.sub("վ", k)
    k = k.replace("է", "ե").replace("օ", "ո")
    return Y_RE.sub("հ", k)


def searched(name):
    """True for a part that is searched: in one of
    TOPS, not by an author LEFT_OUT."""
    top, _, rest = name.partition("/")
    who = rest.partition("/")[0]
    return (
        top in TOPS
        and "/" in rest
        and (who not in LEFT_OUT)
    )


def chunk(text, k):
    """Lines k*CHUNK+1 to (k+1)*CHUNK of a text, the
    file data/lines/<part>/<k>.json."""
    lines = text.splitlines()
    return lines[k * CHUNK : (k + 1) * CHUNK]


class Index:
    """The words of some parts: build it with add(),
    one part after the other, then ask entry()."""

    def __init__(self):
        self.parts = []
        # key -> spelling -> part -> [line, ...]
        self.words = {}
        self.cache = {}

    def add(self, name, text):
        p = len(self.parts)
        self.parts.append(name)
        words, cache = self.words, self.cache
        for n, line in enumerate(text.splitlines(), 1):
            seen = set()
            for w in WORD_RE.findall(line):
                s = normalize(w)
                if s in seen:
                    continue
                seen.add(s)
                k = cache.get(s)
                if k is None:
                    k = cache[s] = loose(w)
                by = words.setdefault(k, {})
                by.setdefault(s, {}).setdefault(
                    p, []
                ).append(n)

    def freeze(self):
        """Keep each key's entry as compact JSON text,
        to take less memory (a phone): add() no more
        after this."""
        for k, by in self.words.items():
            self.words[k] = json.dumps(
                encode(by),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        self.cache = {}

    def keys(self):
        return self.words.keys()

    def entry(self, key):
        """The entry of a loose key, as in the module
        docstring; None for a word not found."""
        by = self.words.get(key)
        if by is None:
            return None
        if isinstance(by, str):
            return json.loads(by)
        return encode(by)


def encode(by):
    """An entry from {spelling: {part: [line, ...]}}
    (see the module docstring)."""
    lines = set()
    for parts in by.values():
        for p, ns in parts.items():
            lines.update((p, n) for n in ns)
    if len(lines) > COMMON:
        return {"*": len(lines)}
    out = {}
    for s, parts in sorted(by.items()):
        rows = []
        for p, ns in sorted(parts.items()):
            rows.append(
                [p, ns[0]]
                + [b - a for a, b in zip(ns, ns[1:])]
            )
        out[s] = rows
    return out


def build(items):
    """An Index of [(name, text)], the parts that are
    searched()."""
    index = Index()
    for name, text in items:
        if searched(name):
            index.add(name, text)
    index.freeze()
    return index


def part_place(name, first):
    """(book key, part number) of a part: the book
    is the folder of a part of a long book (first
    line "title · n/N"), or the file itself; the key
    is its path under its top folder, the same for
    a book and its translation."""
    rest = name.partition("/")[2]
    m = PART_RE.match(first)
    if m:
        return rest.rpartition("/")[0], int(m.group(2))
    return rest, 1


def parts(index, first_lines, names):
    """The parts of the index and their books and
    authors, for the results: {"parts": [[name, book,
    n]], "books": [[key, name, author]], "authors":
    [[folder, name]]}, book and author as their
    number in their list. Authors and books are in
    the order of LIBRARY.tsv (names, {path: name}),
    then the others by name. first_lines: {part
    name: its first line}."""
    order = {k: i for i, k in enumerate(names)}
    places = {}
    titles = {}
    for name in index.parts:
        first = first_lines.get(name, "")
        key, n = part_place(name, first)
        places[name] = (key, n)
        m = PART_RE.match(first)
        title = m.group(1) if m else first
        if name.startswith(TOPS[0] + "/") or (
            key not in titles
        ):
            titles[key] = title.strip() or key

    def rank(k):
        return (k not in order, order.get(k, 0), k)

    authors = sorted(
        {k.partition("/")[0] for k, _ in places.values()},
        key=rank,
    )
    a_num = {a: i for i, a in enumerate(authors)}
    books = sorted(
        {k for k, _ in places.values()},
        key=lambda k: (
            a_num[k.partition("/")[0]],
            *rank(k),
        ),
    )
    b_num = {b: i for i, b in enumerate(books)}
    return {
        "parts": [
            [name, b_num[places[name][0]], places[name][1]]
            for name in index.parts
        ],
        "books": [
            [
                b,
                names.get(b) or titles[b],
                a_num[b.partition("/")[0]],
            ]
            for b in books
        ],
        "authors": [[a, names.get(a, a)] for a in authors],
    }
