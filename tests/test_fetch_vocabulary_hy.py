import importlib.util
import io
from pathlib import Path

path = (
    Path(__file__).parent.parent
    / "scripts/fetch-vocabulary-hy.py"
)
spec = importlib.util.spec_from_file_location("fv", path)
fv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fv)

PAGE = """{{-hy-}}
{{why|փութամ}}
==Ստուգաբանություն==
# not a meaning: under a heading
{{-hy-բայ-}}
# շտապել, [[աճապարել]] {{օրն|Ես {{ընդգծել|փութացի}}։|ՀՊ}}
# {{հնց}} փույթ ունենալ ({{Հեղինակ|ՀՊ}})
#: an example
#
==== Հոմանիշներ ====
# շտապել, արտորալ
{{-en-}}
{{-en-verb-}}
# to hurry
"""

DUMP = """<mediawiki xmlns="x">
<page><title>Կաղապար:-hy-բայ-</title>
<text>&lt;h2&gt;Բայ&lt;/h2&gt;</text></page>
<page><title>Կաղապար:-hy-գոյ-</title>
<text>#ՎԵՐԱՀՂՈՒՄ [[:Կաղապար:-hy-գո-]]</text></page>
<page><title>Կաղապար:-hy-գո-</title>
<text>&lt;h2&gt; Գոյական &lt;/h2&gt;</text></page>
<page><title>փութալ</title><text>{page}</text></page>
<page><title>Մասնակից:x</title><text>{page}</text></page>
</mediawiki>
"""


def test_reform():
    assert fv.reform("ճաշեմ") == "ճաշել"
    assert fv.reform("նաւաստի") == "նավաստի"
    assert fv.reform("զմիւռնիա") == "զմյուռնիա"
    assert fv.reform("յոյս") == "հոյս"
    assert fv.reform("գէջ") == "գեջ"
    assert fv.reform("արեւ") == "արև"
    assert fv.reform("ուր") == "ուր"


def test_clean():
    line = "{{փխբ}} [[բառ|բառը]] ''մեծ'' {{օրն|x|y}}"
    assert fv.clean(line) == "փխբ. բառը մեծ"
    assert fv.clean("{{հնց|es}} հին") == "հնց. հին"
    assert fv.clean("{{օրինակ|միայն}}") == ""


def test_senses():
    got, why = fv.senses(PAGE)
    assert why == ["փութամ"]
    assert got == [
        ("բայ", ["շտապել, աճապարել", "հնց. փույթ ունենալ"])
    ]


def test_read_and_match():
    text = DUMP.replace("{page}", PAGE.replace("<", "&lt;"))
    pages, tpls = fv.read(io.BytesIO(text.encode()))
    assert list(pages) == ["փութալ"]
    names = {
        c: fv.pos_name(t, tpls) for c, t in tpls.items()
    }
    assert names == {
        "բայ": "բայ",
        "գոյ": "գոյական",
        "գո": "գոյական",
    }
    # by the classical spelling, by the spelling
    # rules, and a classical spelling of its own
    rows = fv.match(pages, ["փութամ", "փութալ", "ճաշեմ"])
    assert rows == [
        ("փութամ", "փութալ"),
        ("փութալ", "փութալ"),
    ]
    rows = fv.match(pages, ["ճաշեմ"])
    assert rows == [("փութամ", "փութալ")]
