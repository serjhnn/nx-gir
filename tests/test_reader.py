from nxgir_reader import (
    WORD_RE,
    find,
    layout,
    normalize,
    references,
    vertical,
)

JOHN = (
    "Ի սկզբանէ էր Բանն, եւ Բանն էր առ Աստուած, "
    "եւ Աստուած էր Բանն։\n"
    "Նա էր ի սկզբանէ առ Աստուած։\n"
    "Եւ լոյսն ի խաւարի լուսաւորէր։"
)


def words_of(text):
    return [m.group() for m in WORD_RE.finditer(text)]


def test_words_skip_punctuation():
    assert words_of("Բանն, եւ Բանն։") == [
        "Բանն",
        "եւ",
        "Բանն",
    ]


def test_marks_stay_inside_words():
    assert words_of("ո՞վ ես դու") == ["ո՞վ", "ես", "դու"]
    assert words_of("ա՟ծ") == ["ա՟ծ"]


def test_normalize():
    assert normalize("Բանն") == normalize("բանն")
    assert normalize("ո՞վ") == "ով"
    assert normalize("և") == normalize("եւ")
    # the abbreviation mark is part of the word
    assert normalize("ա՟ծ") != normalize("ած")


def test_layout_fits_width():
    lay = layout(JOHN, 20)
    assert lay.lines == 3
    assert all(len(r) <= 20 for r in lay.rows)


def test_layout_word_positions():
    lay = layout(JOHN, 20)
    for w in lay.words:
        row = lay.rows[w.row]
        assert row[w.col : w.col + len(w.text)] == w.text
    texts = [w.text for w in lay.words]
    assert texts == words_of(JOHN)


def test_layout_keeps_source_lines():
    lay = layout(JOHN, 20)
    first = [w for w in lay.words if w.text == "Նա"][0]
    assert first.line == 1


def test_word_count_same_at_any_width():
    n = len(layout(JOHN, 80).words)
    assert len(layout(JOHN, 12).words) == n


def test_references_ignore_case():
    lay = layout(JOHN, 80)
    words = lay.words
    i = [w.text for w in words].index("եւ")
    refs = references(words, i)
    assert [words[j].text for j in refs] == [
        "եւ",
        "եւ",
        "Եւ",
    ]


def test_references_count():
    words = layout(JOHN, 80).words
    i = [w.text for w in words].index("Բանն")
    assert len(references(words, i)) == 3


def test_find_wraps_around():
    words = layout(JOHN, 80).words
    last = len(words) - 1
    hit = find(words, "ԲԱՆՆ", last)
    assert words[hit].text == "Բանն"
    assert find(words, "զզզ", 0) is None


def test_vertical_nearest_column():
    lay = layout("ա բբբբ գ\nդդդդդդ ե\nզ", 80)
    words = lay.words
    i = [w.text for w in words].index("բբբբ")
    down = vertical(words, i, 1)
    assert words[down].text == "դդդդդդ"
    assert words[vertical(words, down, 1)].text == "զ"
    last = len(words) - 1
    assert vertical(words, last, 1) == last
    assert vertical(words, 0, -1) == 0
