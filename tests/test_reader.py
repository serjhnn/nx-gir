import nxgir_grabar as grabar
from nxgir_reader import (
    MARGIN_NAMES,
    MARGINS,
    PANEL_HELPS,
    READ_HELP,
    SIDE_MIN,
    TEXT_MAX,
    WORD_RE,
    abbr_panel,
    find,
    layout,
    margin,
    normalize,
    references,
    row_x,
    snippet,
    split,
    text_width,
    vertical,
    visible_rows,
    wrap_lines,
)
from nxgir_ui import help_line

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
    assert len(lay.lines) == 3
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


def test_line_columns():
    lay = layout(JOHN, 12)
    for w in lay.words:
        line = lay.lines[w.line]
        assert line[w.lcol : w.lcol + len(w.text)] == w.text


def test_snippet_short_text_unchanged():
    assert snippet("ա բ գ", 2, 1, 20) == ("ա բ գ", 2)


def test_snippet_keeps_word_in_view():
    text = "ա" * 30 + " Բանն " + "բ" * 30
    col = text.index("Բանն")
    for width in (8, 12, 20, 40):
        piece, c = snippet(text, col, 4, width)
        assert len(piece) == width
        assert piece[c : c + 4] == "Բանն"
        assert piece[0] == "…" and piece[-1] == "…"


def test_snippet_at_ends():
    text = "Բանն " + "բ" * 40
    piece, c = snippet(text, 0, 4, 10)
    assert c == 0 and piece.startswith("Բանն")
    assert piece.endswith("…")
    text = "բ" * 40 + " Բանն"
    piece, c = snippet(text, 41, 4, 10)
    assert piece.endswith("Բանն") and piece[0] == "…"
    assert piece[c : c + 4] == "Բանն"


def test_split_no_panel():
    text, panel, side = split(20, 60, "auto", 0)
    assert panel is None and not side
    assert (text.h, text.w) == (17, 60)


def test_split_auto_narrow_below():
    text, panel, side = split(30, 50, "auto", 4)
    assert not side
    assert panel.h == 4 and panel.w == 50
    assert text.h + panel.h == 27
    assert panel.y == text.y + text.h


def test_split_below_is_capped():
    text, panel, side = split(30, 50, "auto", 100)
    assert panel.h == 27 // 2
    assert text.h == 27 - panel.h


def test_split_auto_wide_side():
    text, panel, side = split(30, SIDE_MIN, "auto", 4)
    assert side
    assert panel.h == text.h == 27
    assert text.w + 1 + panel.w == SIDE_MIN
    assert 30 <= panel.w <= 50
    assert panel.x == text.w + 1


def test_split_modes():
    assert not split(30, 120, "below", 4)[2]
    assert split(30, 70, "side", 4)[2]
    # too narrow for a side panel: falls back to below
    assert not split(30, 50, "side", 4)[2]


def test_row_x_narrow_screen():
    # phone: 10% margin (4 columns) at each side
    assert margin(40) == 4
    assert text_width(40) == 32
    assert row_x(40, 10, "left") == 4
    assert row_x(40, 10, "center") == 4 + (32 - 10) // 2
    assert row_x(40, 32, "center") == 4


def test_margins_on_both_sides():
    for w in (20, 34, 42, 60, 80, 100, 160):
        cw = text_width(w)
        left = row_x(w, cw, "left")
        right = w - left - cw
        assert left >= margin(w), w
        assert right >= margin(w), w
        assert margin(w) >= 1


def test_every_margin_keeps_both_sides():
    for size in MARGINS:
        assert size in MARGIN_NAMES
        for w in (20, 40, 60, 100, 160):
            cw = text_width(w, size)
            left = row_x(w, cw, "left", size)
            right = w - left - cw
            assert left >= margin(w, size) >= 1
            assert right >= margin(w, size)


def test_margins_change_width_on_phone():
    # 40 columns: 4, 6, 8, 2 and 1 empty at each side
    widths = [text_width(40, m) for m in MARGINS]
    assert widths == [32, 28, 24, 36, 38]


def test_margins_change_width_on_wide_screen():
    # the column cap follows the margins, so z also
    # shows where the cap, not the margin, decides
    widths = [text_width(200, m) for m in MARGINS]
    assert widths[0] == TEXT_MAX
    assert widths[1] < widths[0]
    assert widths[2] < widths[1]
    assert widths[3] > widths[0]
    assert widths[4] > widths[3]


def test_read_help_grows_with_width():
    phone = help_line(READ_HELP, 40)
    assert len(phone) < 40
    assert phone.endswith("q back")
    wide = help_line(READ_HELP, 200)
    for k, what, _ in READ_HELP:
        assert f"{k} {what}" in wide
    assert "z margins" in help_line(READ_HELP, 100)


def test_panel_helps_fit():
    for items in PANEL_HELPS.values():
        for w in range(10, 120):
            t = help_line(items, w)
            if t != help_line(items, 1):
                assert len(t) < w


def test_row_x_wide_screen_centers_column():
    left = row_x(100, 10, "left")
    assert left == (100 - TEXT_MAX) // 2
    full = row_x(100, TEXT_MAX, "center")
    assert full == left


def test_vertical_uses_screen_columns():
    # with centered rows, "գ" (short row) sits under
    # the middle of the long row above it
    lay = layout("աաա բբբ գգգ\nդ", 80)
    words = lay.words
    rows = lay.rows

    def centered(row):
        return row_x(40, len(rows[row]), "center")

    i = [w.text for w in words].index("բբբ")
    assert vertical(words, i, 1, centered) == 3
    j = vertical(words, 3, -1, centered)
    assert words[j].text == "բբբ"
    # left-aligned: "դ" is under the first word
    assert words[vertical(words, 3, -1)].text == "աաա"


def test_visible_rows():
    # single spacing: one text row per screen row
    assert visible_rows(10, 0) == 10
    # double: rows 0, 2, 4, 6, 8 (the last gap is cut)
    assert visible_rows(10, 1) == 5
    assert visible_rows(9, 1) == 5
    # triple: rows 0, 3, 6, 9
    assert visible_rows(10, 2) == 4
    assert visible_rows(1, 2) == 1
    assert visible_rows(0, 1) == 1


def test_abbr_panel():
    p = abbr_panel("ա՟ծ")
    assert p.kind == "abbr" and p.title == "ա՟ծ"
    assert p.entries[0].text == "ա՟ծ → Աստուած"
    assert all(e.target == -1 for e in p.entries)
    # no abbreviation: what the word means
    p = abbr_panel("լուսնի")
    assert p.entries[0].text == "լուսին · noun"
    assert abbr_panel("քքքք") is None


def test_abbr_panel_wraps():
    p = abbr_panel("սէր")
    p.wrap(20)
    texts = [e.text for e in p.entries]
    assert all(len(t) <= 20 for t in texts)
    assert len(texts) > len(p.text)
    p.sel = len(texts) - 1
    p.wrap(200)
    assert p.sel == len(p.entries) - 1


def test_abbr_panel_hy():
    p = abbr_panel("լուսնի", lang="hy")
    assert p.lang == "hy" and p.title == "լուսնի · hy"
    assert p.entries[0].text == "լուսին · գոյական"
    # an abbreviation is the same in both
    p = abbr_panel("ա՟ծ", lang="hy")
    assert p.entries[0].text == "ա՟ծ → Աստուած"
    assert abbr_panel("քքքք", lang="hy") is None


def test_abbr_panel_hy_falls_back_to_english():
    word = next(
        w
        for k, ws in grabar.vocabulary()[0].items()
        for w in ws
        if not grabar.define(w.word, lang="hy")
    ).word
    p = abbr_panel(word, lang="hy")
    texts = [e.text for e in p.entries]
    assert texts[0] == "no Armenian meaning; English:"
    assert texts[-1].startswith("Source: Wiktionary")


def test_wrap_lines():
    out = wrap_lines(["a b c", "  dd ee ff gg"], 8)
    assert out == ["a b c", "  dd ee", "    ff", "    gg"]
