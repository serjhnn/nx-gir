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
