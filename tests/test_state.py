import json

from nxgir_reader import layout, pos_of, word_at
from nxgir_state import SETTINGS, State

TEXT = "ա բ գ\nդ ե\n\nզ է ը թ\nժ"


def test_missing_file_gives_defaults(tmp_path):
    st = State.load(tmp_path / "none.json")
    assert st.settings == SETTINGS
    assert st.books == {}


def test_save_and_load(tmp_path):
    path = tmp_path / "sub" / "state.json"
    st = State(path)
    st.settings["theme"] = "night"
    st.set_position("book.txt", [3, 2], 5)
    st.toggle_mark("book.txt", [1, 0])
    assert st.save()
    again = State.load(path)
    assert again.settings["theme"] == "night"
    assert again.position("book.txt") == [3, 2]
    assert again.marks("book.txt") == [[1, 0]]
    # no temporary files left behind
    assert [p.name for p in path.parent.iterdir()] == [
        "state.json"
    ]


def test_damaged_file_starts_fresh(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")
    st = State.load(path)
    assert st.books == {} and st.settings == SETTINGS
    assert (tmp_path / "state.bad").exists()


def test_armenian_text_kept_readable(tmp_path):
    path = tmp_path / "state.json"
    st = State(path)
    st.set_position("գիրք.txt", [0, 0], 1)
    st.save()
    assert "գիրք.txt" in path.read_text(encoding="utf-8")
    assert json.loads(path.read_text())["version"] == 1


def test_toggle_mark_adds_then_removes():
    st = State("unused.json")
    assert st.toggle_mark("b", [4, 1]) is True
    assert st.toggle_mark("b", [0, 0]) is True
    assert st.marks("b") == [[0, 0], [4, 1]]
    assert st.toggle_mark("b", [4, 1]) is False
    assert st.marks("b") == [[0, 0]]


def test_progress():
    st = State("unused.json")
    assert st.progress("b") is None
    st.set_position("b", [0, 0], 4)
    assert st.progress("b") == 25
    st.set_position("b", [3, 0], 4)
    assert st.progress("b") == 100


def test_position_same_at_any_width():
    wide = layout(TEXT, 80).words
    narrow = layout(TEXT, 10).words
    for i in range(len(wide)):
        pos = pos_of(wide, i)
        assert word_at(narrow, pos) == i
        assert pos_of(narrow, i) == pos


def test_position_values():
    words = layout(TEXT, 80).words
    texts = [w.text for w in words]
    assert pos_of(words, texts.index("գ")) == [0, 2]
    assert pos_of(words, texts.index("զ")) == [3, 0]
    assert pos_of(words, texts.index("թ")) == [3, 3]


def test_position_after_file_changed():
    words = layout(TEXT, 80).words
    texts = [w.text for w in words]
    # word number past the end of its line: last word
    assert texts[word_at(words, [1, 9])] == "ե"
    # empty line: the next word
    assert texts[word_at(words, [2, 0])] == "զ"
    # line past the end of the file: last word
    assert word_at(words, [99, 0]) == len(words) - 1
    assert word_at([], [0, 0]) == 0
