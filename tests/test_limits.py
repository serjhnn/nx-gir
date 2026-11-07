import subprocess

import nxgir_limits as cl


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


def test_level():
    assert cl.level(10) == "ok"
    assert cl.level(50) == "watch"
    assert cl.level(80) == "near"


def test_history(tmp_path):
    tsv = tmp_path / "limits.tsv"
    assert cl.history(tsv) == []
    cl.record(measures(), tsv)
    cl.record(measures(site=10, build=61.4), tsv)
    rows = cl.history(tsv)
    assert [r["site"] for r in rows] == ["", 10]
    assert rows[1]["build"] == 61
    assert rows[0]["books"] == 3


def test_stats_takes_the_last_site_measured():
    past = [
        measures(date="2026-11-01", site=5 * cl.MB),
        measures(date="2026-11-02", build=20),
        measures(date="2026-11-03"),
    ]
    past = [{k: r[k] for k in cl.FIELDS} for r in past]
    s = cl.stats(measures(folders={"grabar": 3}), past)
    got = {x["key"]: x for x in s["limits"]}
    assert got["site"]["value"] == 5 * cl.MB
    assert got["site"]["since"] == "2026-11-01"
    assert got["build"]["since"] == "2026-11-02"
    assert got["git"]["since"] == ""
    assert got["part"]["where"] == "grabar/a.txt"
    assert got["part"]["level"] == "watch"
    assert s["closest"] == "part"
    assert s["folders"] == {"grabar": 3}
    # newest first
    assert [r["date"] for r in s["history"]] == [
        "2026-11-03",
        "2026-11-02",
        "2026-11-01",
    ]
    # no git size measured: the last recorded one
    s = cl.stats(measures(git=""), past)
    got = {x["key"]: x for x in s["limits"]}
    assert got["git"]["since"] == "2026-11-03"


def test_stats_without_a_site():
    s = cl.stats(measures(), [])
    keys = [x["key"] for x in s["limits"]]
    assert keys == ["git", "file", "part"]
