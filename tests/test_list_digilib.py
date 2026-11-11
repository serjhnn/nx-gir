import importlib.util
from pathlib import Path

path = (
    Path(__file__).parent.parent / "scripts/list-digilib.py"
)
spec = importlib.util.spec_from_file_location("ld", path)
ld = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ld)

PAGE = """
<h1>Պատմութիւն</h1>
<div class="btn-group rm7">Հեղինակ</div>
<div class="btn-group rm15"><span>
<a class="underline" href="/x">ՍԵԲԷՈՍ</a></span>
</div>
<div class="btn-group rm7">Բաժին</div>
<div class="btn-group rm15">
<span><a href="/a">Ա բաժին</a></span>
<span><a href="/b">Բ բաժին</a></span>
</div>
<div class="btn-group rm7">Թեմա</div>
<div class="btn-group">
<span><a href="/c">Պատմագրութիւն</a></span>
</div>
<a href="/book/321/">x</a>
<a href="/book/54/">y</a>
<a href="/book/321/1/2/">z</a>
"""

# Grabar and modern samples, long enough for a verdict
GRABAR = (
    "Եւ եղեւ յետ այնորիկ ասէ ցնոսա, զի ոչ գիտէին "
    "զնա, եւ նորա ընդ նոսա էր ի քաղաքին "
) * 5
MODERN = (
    "Նա իր տանը շատ էր աշխատում, իսկ մենք նրանց "
    "հետ գնում էինք դաշտերում ու այգիներում "
) * 5


def test_details():
    assert ld.details(PAGE) == {
        "title": "Պատմութիւն",
        "author": "ՍԵԲԷՈՍ",
        "section": "Ա բաժին; Բ բաժին",
        "theme": "Պատմագրութիւն",
    }


def test_ids_in_page_order_without_repeats():
    assert ld.ids(PAGE) == ["321", "54"]


def test_kind():
    assert ld.kind(GRABAR) == "grabar"
    assert ld.kind(MODERN) == "modern"
    assert ld.kind("Եւ ասէ") == "no text"


def test_verdict():
    assert ld.verdict(MODERN, GRABAR) == "mixed"
    assert ld.verdict("", GRABAR) == "grabar"
    assert ld.verdict(GRABAR, "") == "grabar"
    assert ld.verdict(MODERN, MODERN) == "modern"


def test_other_language():
    text = "The Life and Adventures of Joseph Emin " * 5
    assert ld.kind(text) == "other language"
    assert ld.kind("Жизнь и приключения " * 10) == (
        "other language"
    )


def test_few_markers_are_unclear():
    # Armenian words, but almost no marker words
    assert ld.kind("Գանձ սրբոյ լուսոյ " * 10) == "unclear"
    assert ld.judge(100, 5, 0) == "grabar"
    assert ld.judge(100, 2, 2) == "unclear"
    assert ld.judge(100, 0, 9) == "unclear"
    assert ld.judge(100, 0, 10) == "modern"
