from nxgir_browse import Shelf, folder_items, parent

NT = "grabar/bible/new-testament"
FILES = [
    (f"{NT}/1-matthew.txt", 100, None),
    (f"{NT}/2-mark.txt", 50, None),
    ("grabar/notes.txt", 10, None),
    ("test/grabar_john.txt", 30, None),
    ("test/sample_english.txt", 5, None),
    ("loose.txt", 1, None),
]


def labels(items):
    return [i.label for i in items]


def test_parent():
    assert parent("a/b/c") == "a/b"
    assert parent("a") == ""
    assert parent("") == ""


def test_top_folder():
    items = folder_items(FILES, "")
    assert labels(items) == [
        "grabar/",
        "test/",
        "loose.txt",
    ]
    grabar = items[0]
    assert grabar.folder and grabar.size == 3
    assert grabar.name == "grabar"


def test_sub_folder_has_up_row_first():
    items = folder_items(FILES, "grabar")
    assert labels(items) == ["..", "bible/", "notes.txt"]
    assert items[0].name == ""
    book = items[2]
    assert (
        not book.folder and book.name == "grabar/notes.txt"
    )


def test_deep_folder_books():
    items = folder_items(FILES, NT)
    assert labels(items) == [
        "..",
        "1-matthew.txt",
        "2-mark.txt",
    ]
    assert items[0].name == "grabar/bible"


def test_open_and_up_remember_the_cursor():
    shelf = Shelf(FILES)
    shelf.pane.pos = 1  # test/
    shelf.open("test")
    assert shelf.folder == "test"
    shelf.up()
    assert shelf.folder == ""
    assert shelf.items[shelf.pane.pos].name == "test"


def test_up_selects_the_folder_we_left():
    shelf = Shelf(FILES, NT)
    shelf.up()
    assert shelf.folder == "grabar/bible"
    assert (
        shelf.items[shelf.pane.pos].label
        == "new-testament/"
    )


def test_missing_saved_folder_opens_top():
    assert Shelf(FILES, "gone/away").folder == ""


def test_search_jumps_into_folder():
    shelf = Shelf(FILES)
    shelf.pane.query = "mark"
    shelf.search(None, "next")
    assert shelf.folder == NT
    assert shelf.items[shelf.pane.pos].label == "2-mark.txt"
    # next match wraps around to the same book
    shelf.search(None, "next")
    assert shelf.items[shelf.pane.pos].label == "2-mark.txt"


def test_search_next_and_previous():
    shelf = Shelf(FILES)
    shelf.pane.query = "john"
    shelf.search(None, "next")
    assert shelf.folder == "test"
    shelf.pane.query = ".txt"
    shelf.search(None, "next")
    item = shelf.items[shelf.pane.pos]
    assert item.name == "test/sample_english.txt"
    shelf.search(None, "prev")
    item = shelf.items[shelf.pane.pos]
    assert item.name == "test/grabar_john.txt"


def test_search_not_found():
    shelf = Shelf(FILES)
    shelf.pane.query = "zzz"
    shelf.search(None, "next")
    assert shelf.pane.msg == "not found: zzz"
    assert shelf.folder == ""


def test_new_folder_starts_below_up_row():
    shelf = Shelf(FILES)
    shelf.open("grabar")
    assert shelf.items[shelf.pane.pos].label == "bible/"
    shelf.open("grabar/bible")
    item = shelf.items[shelf.pane.pos]
    assert item.label == "new-testament/"
