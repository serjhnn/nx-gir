"""The benchmark: the cases and the scoring."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "benchmark"))

import build  # noqa: E402
import score  # noqa: E402

CASES = ROOT / "benchmark" / "cases"


def lines(path):
    return path.read_text().rstrip("\n").split("\n")


def test_every_case_is_complete_and_aligned():
    rows = build.read_cases()
    assert len(rows) >= 5
    for row in rows:
        folder = CASES / row["id"]
        src = lines(folder / "source.txt")
        ref = lines(folder / "reference.txt")
        assert len(src) == row["last"] - row["first"] + 1
        assert len(src) == len(ref), row["id"]
        assert build.blanks(src) == build.blanks(ref)
        assert src[0] and src[-1]
        prompt = (folder / "prompt.txt").read_text()
        head = (build.HERE / "prompt.md").read_text()
        assert (
            prompt
            == head
            + build.DASHES
            + (folder / "source.txt").read_text()
        )


def test_every_case_folder_is_listed():
    ids = {r["id"] for r in build.read_cases()}
    assert ids == {p.name for p in CASES.iterdir()}


def test_normalize_reads_the_old_ligature():
    assert score.normalize("եւ Եւ ԵՒ") == "և Եվ ԵՎ"
    assert score.words("Եւ, ի։") == ["եվ", "ի"]


def test_chrf_is_100_for_the_same_text_and_less_for_other():
    a = "Մահացու մեղքը թողնում է ճանապարհը։"
    assert score.chrf(a, a) == 100
    assert 0 < score.chrf("Ճանապարհը թողնում է։", a) < 100
    assert score.chrf("xyz", a) == 0


def test_clean_drops_a_code_fence():
    out, fenced = score.clean("```\nաբ։\n\nգդ։\n```\n")
    assert out == ["աբ։", "", "գդ։"]
    assert fenced


def test_structure_finds_each_broken_rule():
    src = ["[Ա]", "", "Տեքստ։"]
    good = score.structure(src, ["[Ա]", "", "Տեքստ։"])
    assert score.passed(good)
    for out in (
        ["[Ա]", "Տեքստ։"],
        ["[Բ]", "", "Տեքստ։"],
        ["[Ա]", "Տեքստ", "Տեքստ։"],
        ["[Ա]", "", "Եւ տեքստ։"],
        ["[Ա]", "", "Text։"],
        ["[Ա]", "", "«Տեքստ»։"],
    ):
        assert not score.passed(
            score.structure(src, out)
        ), out


def test_reference_scores_full_and_the_source_less():
    case = CASES / "gosh-inheritance"
    ref = lines(case / "reference.txt")
    res = score.score_run(case, ref, False)
    assert res["structure_ok"]
    assert res["chrf"] == 100
    src = lines(case / "source.txt")
    floor = score.score_run(case, src, False)
    assert floor["chrf"] < 60
    assert floor["copy"] > 90
