"""Saved reading state: positions, bookmarks, settings.

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
