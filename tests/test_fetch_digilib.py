import importlib.util
from pathlib import Path

path = (
    Path(__file__).parent.parent
    / "scripts/fetch-digilib.py"
)
spec = importlib.util.spec_from_file_location("fd", path)
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

PAGE = """
<a href="/book/7/1/11/x">Ա</a>
<div class="WebComponent Label WordLabel"><div>
 <span>&nbsp;&nbsp;<word>
   Եւ</word> <word>
   ասէ</word>, <word>
   նոցա</word>։</span><br>
 <span><b>
   <word>Զի</word></b> <word>բանն</word></span>
</div></div>
<div class="WordLabel">other box</div>
"""


def test_text_keeps_paragraphs_and_punctuation():
    text = fd.Text()
    text.feed(PAGE)
    assert text.paragraphs() == ["Եւ ասէ, նոցա։", "Զի բանն"]


def test_sections_in_order_without_repeats():
    toc = fd.Sections(7)
    toc.feed(
        '<a href="/book/7/1/11/a">﻿Գլուխ <b>Ա</b></a>'
        '<a href="/book/8/1/12/a">other book</a>'
        '<a href="/book/7/1/13/a">Գլուխ Բ</a>'
        '<a href="/book/7/1/11/a">Գլուխ Ա</a>'
    )
    assert toc.found == [
        ("/book/7/1/11/a", "Գլուխ Ա"),
        ("/book/7/1/13/a", "Գլուխ Բ"),
    ]


def test_text_paragraphs_from_p_and_headings():
    text = fd.Text()
    text.feed(
        '<div class="WordLabel"><div>'
        "<h2><span><word>ԺԱ</word>. <word>Քարոզ</word>"
        "</span></h2><span> </span>"
        "<p><span>&nbsp;</span></p>"
        "<p><span><word>Վարդապետք</word> <word>ասեն</word>"
        "</span></p><p><word>Նախ</word></p></div></div>"
    )
    assert text.paragraphs() == [
        "ԺԱ. Քարոզ",
        "Վարդապետք ասեն",
        "Նախ",
    ]


def test_split_keeps_sections_whole():
    secs = [
        ("Ա", ["x" * 60]),
        ("Բ", ["y" * 60]),
        ("Գ", ["z"]),
    ]
    parts = fd.split(secs, 100)
    assert [[h for h, _ in p] for p in parts] == [
        ["Ա"],
        ["Բ", "Գ"],
    ]
    # one section bigger than size still makes a part
    assert fd.split([("Ա", ["x" * 500])], 100) == [
        [("Ա", ["x" * 500])]
    ]
    assert fd.split([], 100) == []
