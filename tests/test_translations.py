from pathlib import Path

import nxgir_translations as tr
import pytest

ROOT = Path(__file__).parent.parent
BOOKS = ROOT / "books"


def test_the_table():
    table = tr.read()
    assert table
    for key in table:
        assert (BOOKS / key).exists(), key
        assert not key.startswith(tr.NOT_OURS), key


def test_every_translation_listed():
    # each translation in books/ is ours (and under
    # the license) or named in NOT_OURS
    table = tr.read()
    top = BOOKS / "ashkharhabar"
    for p in sorted(top.rglob("*.txt")):
        name = str(p.relative_to(BOOKS))
        if name.startswith(tr.NOT_OURS):
            assert tr.find(table, name) is None
        else:
            assert tr.find(table, name), name


def write(tmp_path, *lines):
    p = tmp_path / "t.tsv"
    p.write_text(
        "# head\n\n" + "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    return p


def test_read_and_find(tmp_path):
    p = write(
        tmp_path,
        "a/book\tmachine\t\t2026-11-10",
        "a/book/02.txt\treview\tAni\t2026-11-11",
        "a/other.txt\treviewed\tAni, Vardan\t2026-11-12",
    )
    t = tr.read(p)
    assert list(t) == [
        "a/book",
        "a/book/02.txt",
        "a/other.txt",
    ]
    assert tr.find(t, "a/book/01.txt")["status"] == (
        "machine"
    )
    # the longest match wins
    two = tr.find(t, "a/book/02.txt")
    assert two["reviewers"] == ["Ani"]
    assert tr.find(t, "a/bookish.txt") is None
    assert tr.find(t, "a/other.txt")["reviewers"] == [
        "Ani",
        "Vardan",
    ]
    assert tr.read(None) == {}
    assert tr.read(tmp_path / "none.tsv") == {}


def test_credit(tmp_path):
    p = write(
        tmp_path,
        "m.txt\tmachine\t\t2026-11-10",
        "r.txt\treview\tAni\t2026-11-10",
        "d.txt\treviewed\tAni, Vardan\t2026-11-10",
    )
    t = tr.read(p)
    m = tr.credit(t, "m.txt")
    assert m["license"] == "CC BY-SA 4.0"
    assert m["url"] == tr.LICENSE_URL
    assert "չխմբագրված" in m["text"]
    r = tr.credit(t, "r.txt")["text"]
    assert r.endswith("խմբագրում է՝ Ani")
    d = tr.credit(t, "d.txt")["text"]
    assert d.endswith("խմբագրել են՝ Ani, Vardan")
    assert tr.credit(t, "x.txt") is None


@pytest.mark.parametrize(
    "line",
    [
        "a.txt\treview\tAni",
        "\treview\tAni\t2026-11-10",
        "a.txt\tdone\tAni\t2026-11-10",
        "a.txt\tmachine\tAni\t2026-11-10",
        "a.txt\treview\t\t2026-11-10",
        "a.txt\treview\tAni\t10.11.2026",
    ],
)
def test_bad_lines(tmp_path, line):
    with pytest.raises(tr.TranslationsError):
        tr.read(write(tmp_path, line))
