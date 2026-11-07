"""The timeline of nx-gir: timeline.tsv, the main
steps of the project (see the head of that file).

read() checks every line and stops on a bad one, so
a mistake shows when the site is built, not later
in the page. Tested in tests/test_timeline.py.
"""

import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMELINE = ROOT / "timeline.tsv"

KINDS = (
    "Start",
    "Books",
    "Translation",
    "Reader",
    "Dictionary",
    "Texts",
    "Site",
)
FIELDS = ("date", "kind", "big", "title", "text", "link")
# the date of a plan
NEXT = "next"
# events on the home page
NEWS = 3


class TimelineError(ValueError):
    pass


def parse(line, n):
    """One line of timeline.tsv as an event."""
    parts = line.split("\t")
    if len(parts) != len(FIELDS):
        raise TimelineError(
            f"line {n}: {len(parts)} fields,"
            f" not {len(FIELDS)}"
        )
    e = dict(zip(FIELDS, (p.strip() for p in parts)))
    if e["date"] != NEXT:
        try:
            datetime.date.fromisoformat(e["date"])
        except ValueError:
            raise TimelineError(
                f"line {n}: bad date {e['date']!r}"
            ) from None
    if e["kind"] not in KINDS:
        raise TimelineError(
            f"line {n}: unknown kind {e['kind']!r}"
        )
    if e["big"] not in ("", "*"):
        raise TimelineError(f"line {n}: big is * or empty")
    e["big"] = e["big"] == "*"
    if not e["title"]:
        raise TimelineError(f"line {n}: no title")
    return e


def read(path=TIMELINE):
    """The events of path, oldest first, the plans
    last. Raises TimelineError on a bad line or
    when the dates go back in time."""
    events = []
    text = Path(path).read_text(encoding="utf-8")
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        e = parse(line, n)
        last = events[-1]["date"] if events else ""
        if last == NEXT and e["date"] != NEXT:
            raise TimelineError(
                f"line {n}: a date after a plan"
            )
        if e["date"] != NEXT and e["date"] < last:
            raise TimelineError(
                f"line {n}: {e['date']} is before {last}"
            )
        events.append(e)
    return events


def done(events):
    """The events that happened, not the plans."""
    return [e for e in events if e["date"] != NEXT]


def news(events, n=NEWS):
    """The newest n events, newest first."""
    return done(events)[::-1][:n]
