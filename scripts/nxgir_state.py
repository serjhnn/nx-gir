"""Saved reading state: positions, bookmarks, notes
and settings.

Stored as JSON in $NXGIR_STATE, else
$XDG_STATE_HOME/nxgir/state.json, else
~/.local/state/nxgir/state.json. A position is
[line, n]: the n-th word (from 0) of a line of the file
(from 0), so it does not depend on the screen size.
"""

import json
import os
import tempfile
import time
from pathlib import Path

VERSION = 1
SETTINGS = {
    "theme": "sepia",
    "dim": 0,
    "align": "center",
    "mode": "auto",
    "spacing": 1,
    "margin": 0.10,
}


def default_path():
    if os.environ.get("NXGIR_STATE"):
        return Path(os.environ["NXGIR_STATE"])
    base = os.environ.get("XDG_STATE_HOME")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".local" / "state"
    return root / "nxgir" / "state.json"


def is_note(n):
    """True for a well-formed note (see add_note)."""
    return (
        isinstance(n, dict)
        and isinstance(n.get("pos"), list)
        and len(n["pos"]) == 2
        and isinstance(n.get("text"), str)
        and isinstance(n.get("quote", ""), str)
    )


class State:
    def __init__(self, path=None):
        self.path = Path(path or default_path())
        self.settings = dict(SETTINGS)
        self.books = {}

    @classmethod
    def load(cls, path=None):
        """Read the state file. A missing or damaged file
        gives a fresh state (a damaged one is kept as
        state.json.bad)."""
        st = cls(path)
        try:
            data = json.loads(
                st.path.read_text(encoding="utf-8")
            )
            st.settings.update(data.get("settings", {}))
            st.books = dict(data.get("books", {}))
            for b in st.books.values():
                if "notes" in b:
                    b["notes"] = [
                        n for n in b["notes"] if is_note(n)
                    ]
        except FileNotFoundError:
            pass
        except (OSError, ValueError, AttributeError):
            try:
                st.path.replace(st.path.with_suffix(".bad"))
            except OSError:
                pass
            st.settings = dict(SETTINGS)
            st.books = {}
        return st

    def save(self):
        """Write the file atomically; never raises."""
        data = {
            "version": VERSION,
            "settings": self.settings,
            "books": self.books,
        }
        text = json.dumps(
            data, ensure_ascii=False, indent=1
        )
        try:
            self.path.parent.mkdir(
                parents=True, exist_ok=True
            )
            fd, tmp = tempfile.mkstemp(
                dir=self.path.parent, prefix=".state-"
            )
        except OSError:
            return False
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, self.path)
            return True
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            return False

    # -- books --

    def book(self, key):
        """The saved entry for a book (created if new)."""
        return self.books.setdefault(key, {})

    def position(self, key):
        """[line, n] where the book was left, or None."""
        pos = self.books.get(key, {}).get("pos")
        return list(pos) if pos else None

    def set_position(self, key, pos, lines):
        b = self.book(key)
        b["pos"] = list(pos)
        b["lines"] = lines
        b["seen"] = int(time.time())

    def progress(self, key):
        """Percent read (0-100), or None if never opened."""
        b = self.books.get(key)
        if not b or "pos" not in b or not b.get("lines"):
            return None
        line = b["pos"][0] + 1
        return min(100, round(100 * line / b["lines"]))

    def marks(self, key):
        """Bookmarks of a book: sorted [[line, n], ...]."""
        return [
            list(m)
            for m in self.books.get(key, {}).get(
                "marks", []
            )
        ]

    def toggle_mark(self, key, pos):
        """Add a bookmark at pos, or remove it if there.
        True if added."""
        marks = self.marks(key)
        pos = list(pos)
        added = pos not in marks
        if added:
            marks.append(pos)
        else:
            marks.remove(pos)
        self.book(key)["marks"] = sorted(marks)
        return added

    def notes(self, key):
        """Notes of a book, sorted by place: [{"pos":
        [line, n] of the sentence's first word,
        "quote": its first words, "text", "date"}]."""
        return self.books.get(key, {}).get("notes", [])

    def add_note(self, key, pos, quote, text):
        """Add a note to the sentence at pos; its index
        in notes()."""
        note = {
            "pos": list(pos),
            "quote": quote,
            "text": text,
            "date": time.strftime("%Y-%m-%d"),
        }
        notes = self.book(key).setdefault("notes", [])
        notes.append(note)
        # stable: notes of one sentence stay in the
        # order they were written
        notes.sort(key=lambda n: n["pos"])
        return notes.index(note)

    def edit_note(self, key, i, text):
        self.book(key)["notes"][i]["text"] = text

    def delete_note(self, key, i):
        del self.book(key)["notes"][i]
