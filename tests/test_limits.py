import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
path = ROOT / "scripts/check-limits.py"
spec = importlib.util.spec_from_file_location("cl", path)
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)


def test_books(tmp_path):
    (tmp_path / "grabar").mkdir()
    (tmp_path / "grabar" / "a.txt").write_text("ab")
    (tmp_path / "b.txt").write_text("abcd")
    (tmp_path / "c.md").write_text("not a book")
    n, total, big = cl.books(tmp_path)
    assert (n, total) == (2, 6)
    assert big == (4, "b.txt")


def test_books_empty(tmp_path):
    assert cl.books(tmp_path)[:2] == (0, 0)


def test_human():
    assert cl.human(12) == "12 B"
    assert cl.human(1536) == "1.5 KB"
    assert cl.human(3 * cl.MB) == "3.0 MB"
    assert cl.human(cl.GB) == "1.0 GB"


def test_line():
    row = cl.line("site", 100 * cl.MB, "site")
    assert row.startswith("site     100.0 MB / 1.0 GB")
    assert row.endswith("10%")
    row = cl.line("build", 60, "build", "x")
    assert "60 s / 10.0 min" in row
    assert row.endswith("10%  x")


def measures(**kw):
    m = {
        "date": "2026-11-07",
        "commit": "abc1234",
        "books": 3,
        "text": 3000,
        "part": cl.MB // 2,
        "part_name": "grabar/a.txt",
        "file": 1000,
        "file_name": "x.tsv",
        "git": 5000,
        "site": "",
        "build": "",
    }
    m.update(kw)
    return m


def test_report():
    rows = cl.report(measures())
    assert rows[0] == "2026-11-07  commit abc1234"
    assert "not built" in rows[2]
    assert rows[-1].startswith("closest: part at 50%")
    rows = cl.report(measures(site=cl.GB, build=30))
    assert rows[-1].startswith("closest: site at 100%")
    assert any(r.startswith("build") for r in rows)


def test_record(tmp_path):
    tsv = tmp_path / "limits.tsv"
    cl.record(measures(), tsv)
    cl.record(measures(site=10, build=61.4), tsv)
    lines = tsv.read_text().splitlines()
    head = [x for x in lines if x.startswith("date")]
    assert head == ["\t".join(cl.FIELDS)]
    rows = [x.split("\t") for x in lines[-2:]]
    assert rows[0][-2:] == ["", ""]
    assert rows[1][-2:] == ["10", "61"]


def test_history_matches_head():
    text = cl.HISTORY.read_text(encoding="utf-8")
    assert text.startswith(cl.HEAD)
    for row in text.splitlines()[
        len(cl.HEAD.splitlines()) :
    ]:
        assert len(row.split("\t")) == len(cl.FIELDS)


def test_git_measures(tmp_path):
    def run(*a):
        subprocess.run(
            ["git", *a],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

    run("init", "-q")
    (tmp_path / "big.txt").write_text("x" * 100)
    (tmp_path / "small.txt").write_text("y")
    run("add", ".")
    run(
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-qm",
        "t",
    )
    assert cl.largest_tracked(tmp_path) == (
        100,
        "big.txt",
    )
    assert cl.history_size(tmp_path) > 0
