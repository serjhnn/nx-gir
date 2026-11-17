"""The OCR tooling in ocr/: metrics, locating, scoring."""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ocr"))

from nxocr import (  # noqa: E402
    engine,
    evaluate,
    locate,
    metrics,
    pages,
    prep,
    textnorm,
    train,
)

TEXT = (
    "Ի թուին չորեքհարիւր եւ վաթսուն դարձեալ հանդերձ "
    "զօրօք եկն ի վերայ քաղաքին եւ առեալ զնա ի գերութիւն "
    "եւ զկին եւ զորդիս նորա տարաւ ի կոստանդնուպօլիս "
    "իսկ ի թուին չորեքհարիւր վաթսուն եւ հինգ եղեւ"
)


def test_key_drops_marks_case_and_ligature():
    assert textnorm.key("Եւ, ա՛յն։ 12") == "եւայն"
    assert textnorm.key("և") == "եւ"


def test_words_join_hyphens():
    assert textnorm.words("լըլա-\nնալ ա։") == [
        "լըլանալ",
        "ա",
    ]


def test_distance():
    assert metrics.distance("abc", "abc") == 0
    assert metrics.distance("abc", "abd") == 1
    assert metrics.distance("abc", "ac") == 1
    assert metrics.distance("", "ab") == 2
    assert metrics.distance("kitten", "sitting") == 3


def test_word_distance():
    assert (
        metrics.word_distance(["a", "b"], ["a", "c"]) == 1
    )
    assert metrics.word_distance([], ["a"]) == 1


def test_ops_free_ends_finds_the_stretch():
    items, start, end = metrics.ops(
        "wor1d", "hello world!", True
    )
    assert (start, end) == (6, 11)
    assert metrics.errors(items) == 1
    assert ("~", "1", "l") in items


def test_ops_counts_insertions_and_deletions():
    items, _, _ = metrics.ops("abxc", "abc")
    assert [o for o, _, _ in items] == ["=", "=", "-", "="]
    items, _, _ = metrics.ops("ac", "abc")
    assert ("+", "", "b") in items


def test_locate_places_a_garbled_page():
    ref = locate.Reference(
        [TEXT * 1, "x" * 50 + TEXT[::-1]]
    )
    page = textnorm.key(TEXT[60:200])
    garbled = page[:30] + "ձ" + page[31:80] + page[85:]
    start, end = ref.locate(garbled)
    # the stretch holds the page, with some slack
    assert start <= ref.text.index(page[:12])
    assert end >= ref.text.index(page[:12]) + len(page) - 10


def test_locate_none_for_foreign_text():
    ref = locate.Reference([TEXT])
    assert ref.locate("ձ" * 80) is None


def words_of(text, conf=90):
    return [engine.Word(w, conf) for w in text.split()]


def test_score_page_perfect_and_flawed():
    ref = locate.Reference([TEXT])
    good = evaluate.score_page(
        1, words_of(TEXT[60:200]), ref
    )
    assert good.placed and good.errors == 0
    bad = TEXT[60:200].replace(
        "քաղաքին", "քաղաքին".replace("ղ", "դ")
    )
    res = evaluate.score_page(2, words_of(bad), ref)
    assert res.errors == 1 and res.word_errors == 1
    assert 0 < res.cer < 0.05
    assert res.confusions[("դ", "ղ")] == 1


def test_triage_catches_errors_by_confidence():
    r = evaluate.PageResult(1)
    r.flags = [
        (30, False),
        (40, True),
        (95, True),
        (95, True),
    ]
    rows = evaluate.triage([r], (50,))
    assert rows[0]["reread"] == 0.5
    assert rows[0]["caught"] == 1.0
    assert rows[0]["precision"] == 0.5


TSV = (
    "level\tpage_num\tblock_num\tpar_num\tline_num\t"
    "word_num\tleft\ttop\twidth\theight\tconf\ttext\n"
    "4\t1\t1\t1\t1\t0\t0\t0\t9\t9\t-1\t\n"
    "5\t1\t1\t1\t1\t1\t1\t2\t3\t4\t88.5\tԻ\n"
    "5\t1\t1\t1\t1\t2\t5\t2\t3\t4\t40\tթուին\n"
    "5\t1\t1\t1\t2\t1\t1\t9\t3\t4\t70\tեւ\n"
)


def test_parse_tsv_lines_and_confidence():
    page = engine.parse_tsv(TSV)
    assert [ln.text for ln in page.lines] == [
        "Ի թուին",
        "եւ",
    ]
    assert page.lines[0].conf == (88.5 + 40) / 2
    assert page.words()[1].box == (5, 2, 3, 4)


def test_parse_range_and_spread():
    assert pages.parse_range("3-5,9") == [3, 4, 5, 9]
    assert pages.parse_range("1-9", 4) == [1, 2, 3, 4]
    assert pages.spread(list(range(100)), 4) == [
        12,
        37,
        62,
        87,
    ]
    assert pages.spread([1, 2], 5) == [1, 2]


def test_crop_and_binarize():
    img = Image.new("L", (100, 200), 255)
    out = prep.prepare(img, prep.Prep(top=0.1, bottom=0.2))
    assert out.size == (100, 140)
    arr = np.full((60, 60), 200, np.uint8)
    arr[10:50, 29:32] = 30
    bw = prep.sauvola(arr, 15)
    assert bw[30, 30] == 0 and bw[2, 2] == 255


def test_skew_angle_finds_a_tilt():
    img = Image.new("L", (300, 300), 255)
    arr = np.asarray(img).copy()
    for y in range(40, 260, 20):
        arr[y : y + 6, 20:280] = 0
    tilted = Image.fromarray(arr).rotate(
        1.5, fillcolor=255, resample=Image.BILINEAR
    )
    assert abs(prep.skew_angle(tilted) + 1.5) < 0.5


def test_fold_holds_out_whole_blocks():
    held = [p for p in range(26, 66) if train.fold(p)]
    assert held == [41, 42, 43, 44, 45, 61, 62, 63, 64, 65]


def test_reference_original_keeps_marks():
    ref = locate.Reference(["Եւ զկին, նորա։ Ի թուին"])
    a = ref.text.index("զկին")
    b = ref.text.index("նորա")
    assert ref.original(a, b) == "զկին,"
    assert ref.original(b, len(ref.text)).startswith(
        "նորա։"
    )


def test_split_lines_labels_lines_from_typed_text():
    from nxocr import lines

    ref = locate.Reference([TEXT])
    ws = TEXT[60:200].split()
    rows = [ws[:6], ws[6:12], ws[12:]]
    page = engine.Page()
    for n, row in enumerate(rows):
        ln = engine.Line()
        for m, w in enumerate(row):
            box = (m * 90, n * 60, 80, 40)
            ln.words.append(engine.Word(w, 90, box))
        page.lines.append(ln)
    start, got = lines.split_lines(page, ref)
    assert start is not None and len(got) == 3
    assert got[0].text.startswith(ws[0])
    assert got[0].cer == 0
    assert got[0].box[0] < 0 + 1
    # characters the model does not know drop the line
    none = lines.split_lines(page, ref, chars={"ա"})[1]
    assert none == []


def small_lexicon():
    from nxocr import post

    counts = {
        "թագաւոր": 9,
        "թագաւորն": 6,
        "քաղաք": 8,
        "քաջ": 7,
        "քաղ": 3,
        "զօրք": 5,
        "զօրաց": 4,
        "ժամանակ": 5,
        "աշխարհ": 6,
    }
    return post.Lexicon(counts, long=7)


def one_line(*words):
    ln = engine.Line([engine.Word(w, c) for w, c in words])
    return engine.Page([ln])


def test_costs_make_known_swaps_cheaper():
    from nxocr import post

    plain = post.Costs()
    known = post.Costs([("ղ", "զ", 10), ("", "ե", 10)])
    assert plain.distance("ղօրք", "զօրք") == 1
    assert known.distance("ղօրք", "զօրք") == 0.4
    assert known.distance("թագաւոր", "թագաւեոր") == 0.4
    assert known.distance("աբ", "աբ") == 0


def test_correct_fixes_a_close_unknown_word():
    from nxocr import post

    page = one_line(("ղօրք,", 40), ("եկն", 95))
    costs = post.Costs([("ղ", "զ", 10)])
    got = post.correct(page, small_lexicon(), costs)
    # a suggestion only: the text is the engine's own
    assert page.lines[0].words[0].text == "ղօրք,"
    post.correct(page, small_lexicon(), costs, apply=True)
    assert page.lines[0].words[0].text == "զօրք,"
    assert [(c.old, c.new) for c in got] == [
        ("ղօրք,", "զօրք,")
    ]


def test_correct_leaves_alone():
    from nxocr import post

    lex, costs = small_lexicon(), post.Costs()
    # sure, a known word, a name, a word with no candidate
    page = one_line(
        ("ղօրք", 95),
        ("զօրք", 40),
        ("Ղօրք", 40),
        ("ձձձձձ", 40),
    )
    assert post.correct(page, lex, costs) == []
    # two equally close words: no guess
    lex.index.clear()
    two = post.Lexicon({"աբգդ": 5, "աբդդ": 5}, long=9)
    page = one_line(("աբեդ", 40))
    assert post.correct(page, two, costs) == []


def test_correct_keeps_the_halves_of_a_split_word():
    from nxocr import post

    lex = small_lexicon()
    page = engine.Page(
        [
            engine.Line([engine.Word("ժամ", 40)]),
            engine.Line([engine.Word("անակ", 40)]),
        ]
    )
    assert post.fragments(page, lex) == {(0, 0), (1, 0)}
    assert post.correct(page, lex, post.Costs()) == []


def test_half_splits_the_held_out_blocks():
    held = [p for p in range(26, 157) if train.fold(p)]
    halves = [train.half(p) for p in held]
    assert halves.count("dev") == halves.count("test")
    assert train.half(30) is None
    assert train.half(45) == "dev"
    assert train.half(145) == "test"


def test_reference_without_cuts_spans():
    ref = locate.Reference(["աբգդեզ ւթժ ինլխծկ"])
    a = ref.text.index("ւթժ")
    parts = ref.without([(a, a + 3)])
    assert "ւթժ" not in "".join(parts)
    assert "աբգդեզ" in "".join(parts)
    assert "ինլխծկ" in "".join(parts)


def test_lexicon_extra_counts_words_and_pairs():
    from nxocr import post

    counts = {"աբգ": 1}
    lex = post.Lexicon(counts, long=9)
    assert lex.pairs == {}
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "books" / "grabar").mkdir(parents=True)
        (root / "grabar").mkdir()
        for name in ("vocabulary", "forms"):
            (root / "grabar" / f"{name}.tsv").write_text(
                "#\n"
            )
        lex = post.Lexicon.from_repo(
            root, extra=[("աբգ դեզ աբգ", 3)]
        )
    assert lex.counts["աբգ"] == 6
    assert lex.pairs[("աբգ", "դեզ")] == 3


def test_context_picks_the_word_that_fits():
    from nxocr import post

    lex = post.Lexicon(
        {"եկն": 50, "մեզ": 40, "մեղ": 40, "աբգ": 10},
        pairs=post.Counter({("եկն", "մեզ"): 40}),
        long=9,
    )
    costs = post.Costs([("ղ", "զ", 10)])
    page = one_line(("եկն", 95), ("մեղ", 70))
    easy = post.ContextParams(weight=2.0)
    got = post.context(page, lex, costs, easy)
    assert [(c.old, c.new) for c in got] == [("մեղ", "մեզ")]
    assert got[0].gain > 1
    # the default asks for more: this change is not made
    page = one_line(("եկն", 95), ("մեղ", 70))
    assert post.context(page, lex, costs) == []
    # a word the engine is sure of is left alone
    page = one_line(("եկն", 95), ("մեղ", 95))
    p = post.ContextParams(max_conf=90, weight=2.0)
    assert post.context(page, lex, costs, p) == []
    # a sentence end breaks the context
    page = one_line(("եկն։", 95), ("մեղ", 70))
    assert post.context(page, lex, costs, easy) == []


def test_review_rows_and_no_rewrite_by_default():
    from nxocr import post

    lex = post.Lexicon(
        {"եկն": 50, "մեզ": 40, "մեղ": 40},
        pairs=post.Counter({("եկն", "մեզ"): 40}),
        long=9,
    )
    costs = post.Costs([("ղ", "զ", 10)])
    easy = post.ContextParams(weight=2.0)
    page = one_line(("եկն", 95), ("մեղ", 70))
    got = post.context(page, lex, costs, easy)
    assert page.lines[0].words[1].text == "մեղ"
    assert got[0].step == "context"
    rows = post.review(got, 7, head=True).split("\n")
    assert rows[0].split("\t") == [
        "page",
        "line",
        "word",
        "conf",
        "old",
        "new",
        "cost",
        "gain",
        "step",
    ]
    cols = rows[1].split("\t")
    assert cols[:6] == ["7", "1", "2", "70", "մեղ", "մեզ"]
    assert cols[-1] == "context"
    post.context(page, lex, costs, easy, apply=True)
    assert page.lines[0].words[1].text == "մեզ"
