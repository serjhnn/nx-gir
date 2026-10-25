import importlib.util
from pathlib import Path

path = Path(__file__).parent.parent / "scripts/nxgir-cli.py"
spec = importlib.util.spec_from_file_location("cli", path)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def test_complete_command_names():
    assert cli.completions("", "bo") == ["bookshelf"]
    assert cli.completions("", "b") == [
        "banner",
        "bookshelf",
    ]
    assert "exit" in cli.completions("", "")
    assert cli.completions("", "zz") == []


def test_complete_arguments():
    assert cli.completions("bookshelf ", "") == ["--plain"]
    assert cli.completions("banner ", "hy-") == [
        "hy-upright",
        "hy-block",
    ]
    # one argument only
    assert cli.completions("banner hy ", "") == []
    assert cli.completions("nosuch ", "") == []


def test_bookshelf_replaces_ls(capsys):
    assert cli.run(["bookshelf", "--plain"]) == 0
    out = capsys.readouterr().out
    assert "test/grabar_john.txt" in out
    assert cli.run(["ls"]) != 0


def test_bookshelf_lists_books_not_notes(capsys):
    cli.run(["bookshelf", "--plain"])
    out = capsys.readouterr().out
    assert "new-testament/1-matthew.txt" in out
    assert "SOURCES.md" not in out


def test_grabar_word(capsys):
    assert cli.run(["grabar", "word", "լուսնի"]) == 0
    assert "moon" in capsys.readouterr().out
    assert cli.run(["grabar", "word", "zzz"]) == 1


def test_grabar_word_hy(capsys):
    args = ["grabar", "word", "--hy", "լուսնի"]
    assert cli.run(args) == 0
    assert "լուսին · գոյական" in capsys.readouterr().out


def test_grabar_abbr(capsys):
    assert cli.run(["grabar", "abbr", "ա՟ծ"]) == 0
    assert "Աստուած" in capsys.readouterr().out
    assert cli.run(["grabar", "abbr"]) == 0
    out = capsys.readouterr().out
    assert "Sources:" in out
    assert cli.run(["grabar", "abbr", "յամ"]) == 0
    out = capsys.readouterr().out
    assert "յամ → յամենայն" in out
    assert "+ ամ = ամենայն" in out
    assert cli.run(["grabar", "abbr", "իվր"]) == 0
    assert "իվր → ի վերայ" in capsys.readouterr().out
    assert cli.run(["grabar", "abbr", "zzz"]) == 1
    assert cli.completions("", "gr") == ["grabar"]
    assert cli.completions("grabar ", "") == [
        "abbr",
        "word",
    ]


def test_notes(capsys, tmp_path, monkeypatch):
    from nxgir_state import State

    path = tmp_path / "state.json"
    monkeypatch.setenv("NXGIR_STATE", str(path))
    assert cli.run(["notes"]) == 0
    assert "no notes yet" in capsys.readouterr().out
    st = State(path)
    st.add_note(
        "grabar/john.txt", [2, 0], "Ի սկզբանէ…", "Բանն"
    )
    st.save()
    assert cli.run(["notes"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("grabar/john.txt\n  line 3")
    assert "  «Ի սկզբանէ…»\n    Բանն\n" in out
    assert cli.run(["notes", "john"]) == 0
    assert cli.run(["notes", "matthew"]) == 1
