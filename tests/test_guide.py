"""TRANSLATION_GUIDE.md: its prompt and its check work."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = (ROOT / "TRANSLATION_GUIDE.md").read_text()
PART = "mkhitar-gosh/1-datastanagirk-a/02.txt"


def test_guide_has_the_benchmark_prompt():
    prompt = (ROOT / "benchmark" / "prompt.md").read_text()
    assert prompt.strip() in GUIDE


def snippet():
    m = re.search(
        r"<<'EOF'\n(.*?)\nEOF\n```", GUIDE, re.DOTALL
    )
    return m.group(1)


def run(grabar, modern):
    return subprocess.run(
        [sys.executable, "-", str(grabar), str(modern)],
        input=snippet(),
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_the_check_runs_on_a_translated_part():
    g = ROOT / "books" / "grabar" / PART
    t = ROOT / "books" / "ashkharhabar" / PART
    res = run(g, t)
    assert res.returncode == 0, res.stderr
    assert "lines_ok      True" in res.stdout
    assert "blank_ok      True" in res.stdout
    assert "first blank mismatch at line []" in res.stdout


def test_the_check_names_the_first_blank_mismatch(tmp_path):
    g = ROOT / "books" / "grabar" / PART
    lines = (
        (ROOT / "books" / "ashkharhabar" / PART)
        .read_text()
        .split("\n")
    )
    del lines[3]
    t = tmp_path / "t.txt"
    t.write_text("\n".join(lines[:300]) + "\n")
    res = run(g, t)
    assert "blank_ok      False" in res.stdout
    assert "first blank mismatch at line [4]" in res.stdout
