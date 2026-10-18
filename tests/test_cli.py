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
