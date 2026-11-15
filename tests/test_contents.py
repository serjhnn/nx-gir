"""The rule for every new book: the Contents (☰) of its
parts must work. A long part with no entries fails this
test; fix it in contents() of nxgir_reader.py (a rule
for its headings, with a test), never in the text.
Only a work with no headings at all may be listed in
NO_CONTENTS, with the reason."""

from pathlib import Path

from nxgir_reader import contents

ROOT = Path(__file__).resolve().parent.parent
# parts at least so long need a Contents
LONG = 150
# parts that have no headings: one psalm, running text,
# a poem in stanzas marked [1], [2], ...
NO_CONTENTS = {
    "grabar/bible/old-testament/psalm-118.txt": "a psalm",
    "ashkharhabar/bible/old-testament/psalm-118.txt": (
        "a psalm"
    ),
    "grabar/anania-shirakatsi/9-patmutyun/01.txt": (
        "running text, marked [1], [2]"
    ),
    "grabar/nerses-shnorhali/2-voghb-edesioy/01.txt": (
        "a poem in stanzas, marked [1], [2]"
    ),
    "grabar/hetum-patmich/2-zhamanakagrutyun/01.txt": (
        "a chronicle by years, in four sections marked [1]"
    ),
}
# chronicles in sections marked [1], [2], ... with no
# headings of their own (Digilib's numbers only)
NUMBERED_ONLY = {
    "grabar/grigor-daranaghtsi/1-zhamanakagrutyun": (
        "01 02 03 04 05"
    ),
    "grabar/hovhannes-drasxanakertsi/1-patmutiun-hayots": (
        "01 02"
    ),
}
for _folder, _parts in NUMBERED_ONLY.items():
    for _n in _parts.split():
        NO_CONTENTS[f"{_folder}/{_n}.txt"] = (
            "a chronicle in sections marked [1], [2]"
        )


def long_parts():
    for p in sorted((ROOT / "books").rglob("*.txt")):
        lines = p.read_text("utf-8").splitlines()
        if len(lines) >= LONG:
            name = p.relative_to(ROOT / "books").as_posix()
            yield name, lines


def test_every_long_part_has_a_contents():
    missing = [
        n
        for n, lines in long_parts()
        if not contents(lines) and n not in NO_CONTENTS
    ]
    assert not missing, (
        "no Contents for "
        + ", ".join(missing)
        + ": add the form of its headings to contents()"
        " in nxgir_reader.py (see CLAUDE.md)"
    )


def test_no_contents_list_is_current():
    # a part that now has a Contents leaves the list
    now = {n: lines for n, lines in long_parts()}
    for name in NO_CONTENTS:
        assert name in now, f"{name}: gone or short"
        assert not contents(now[name]), (
            f"{name} has a Contents now: remove it from"
            " NO_CONTENTS"
        )
