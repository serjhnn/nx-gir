#!/usr/bin/env python3
"""How close nx-gir is to the limits of GitHub and of
a phone: a few numbers and the share of each limit.

    scripts/check-limits.py           quick (seconds)
    scripts/check-limits.py --site    also build the
        Pages site in a temporary folder and time it
        (about a minute)
    scripts/check-limits.py --site --record
        and add a line to notes/limits.tsv, to
        compare with later

The limits and what they mean are explained in
notes/limits.md.
"""

import datetime
import importlib.util
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOKS = ROOT / "books"
HISTORY = ROOT / "notes" / "limits.tsv"

KB = 1024
MB = KB * KB
GB = KB * MB

# (name, limit, what sets it)
LIMITS = {
    "site": (GB, "GitHub Pages: a site of 1 GB"),
    "git": (GB, "GitHub: a repository under 1 GB"),
    "file": (50 * MB, "GitHub: warns at 50 MB"),
    "part": (MB, "ours: a book part under 1 MB"),
    "build": (600, "ours: the site built in 10 min"),
}
FIELDS = (
    "date",
    "commit",
    "books",
    "text",
    "part",
    "file",
    "git",
    "site",
    "build",
)
HEAD = (
    "# Measured by scripts/check-limits.py --record:\n"
    "# sizes in bytes, build in seconds, empty when\n"
    "# not measured. See notes/limits.md.\n"
    + "\t".join(FIELDS)
    + "\n"
)


def books(root=BOOKS):
    """(number of book files, bytes of text, (bytes,
    name) of the largest file) under root."""
    files = sorted(root.rglob("*.txt"))
    sizes = [(p.stat().st_size, p) for p in files]
    total = sum(s for s, _ in sizes)
    big = max(sizes, default=(0, root))
    name = big[1].relative_to(root).as_posix()
    return len(files), total, (big[0], name)


def git(*args, root=ROOT):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def history_size(root=ROOT):
    """Bytes the whole git history takes on disk."""
    out = git(
        "rev-list",
        "--disk-usage",
        "--objects",
        "--all",
        root=root,
    )
    return int(out.strip())


def largest_tracked(root=ROOT):
    """(bytes, path) of the largest file in HEAD."""
    big = (0, "")
    for line in git(
        "ls-tree", "-r", "-l", "HEAD", root=root
    ).splitlines():
        meta, path = line.split("\t", 1)
        size = meta.split()[3]
        if size != "-":
            big = max(big, (int(size), path))
    return big


def site(out):
    """Build the Pages site into out: (bytes, seconds)."""
    path = HERE / "build-site.py"
    spec = importlib.util.spec_from_file_location(
        "build_site", path
    )
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    start = time.monotonic()
    bs.build(out, bs.shelf_files())
    took = time.monotonic() - start
    size = sum(
        p.stat().st_size
        for p in Path(out).rglob("*")
        if p.is_file()
    )
    return size, took


def human(n):
    """A size in bytes as B, KB, MB or GB."""
    for unit, size in (
        ("GB", GB),
        ("MB", MB),
        ("KB", KB),
    ):
        if n >= size:
            return f"{n / size:.1f} {unit}"
    return f"{n} B"


def seconds(n):
    if n < 120:
        return f"{n:.0f} s"
    return f"{n / 60:.1f} min"


def share(value, key):
    """Percent of the limit key that value uses."""
    return 100 * value / LIMITS[key][0]


def line(label, value, key, note=""):
    """One row: label, value / limit, percent, note."""
    limit = LIMITS[key][0]
    fmt = seconds if key == "build" else human
    used = f"{fmt(value)} / {fmt(limit)}"
    row = f"{label:<9}{used:<20}{share(value, key):>4.0f}%"
    return f"{row}  {note}" if note else row


def report(m):
    """The rows for measures m (a dict of FIELDS)."""
    rows = [
        f"{m['date']}  commit {m['commit']}",
        f"books    {m['books']} files,"
        f" {human(m['text'])} of text",
        line("site", m["site"], "site")
        if m["site"] != ""
        else "site     (not built; add --site)",
        line("git", m["git"], "git"),
        line("file", m["file"], "file", m["file_name"]),
        line("part", m["part"], "part", m["part_name"]),
    ]
    if m["build"] != "":
        rows.append(line("build", m["build"], "build"))
    worst = max(
        (share(m[k], k), k) for k in LIMITS if m[k] != ""
    )
    rows.append(
        f"closest: {worst[1]} at {worst[0]:.0f}%"
        f" ({LIMITS[worst[1]][1]})"
    )
    return rows


def record(m, path=HISTORY):
    """Add m as a line to path (made with its head)."""
    if not path.exists():
        path.write_text(HEAD, encoding="utf-8")
    vals = []
    for f in FIELDS:
        v = m[f]
        if f == "build" and v != "":
            v = f"{v:.0f}"
        vals.append(str(v))
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\t".join(vals) + "\n")


def measure(build=False, root=ROOT):
    n, text, part = books(root / "books")
    file = largest_tracked(root)
    m = {
        "date": datetime.date.today().isoformat(),
        "commit": git(
            "rev-parse", "--short", "HEAD", root=root
        ).strip(),
        "books": n,
        "text": text,
        "part": part[0],
        "part_name": part[1],
        "file": file[0],
        "file_name": file[1],
        "git": history_size(root),
        "site": "",
        "build": "",
    }
    if build:
        with tempfile.TemporaryDirectory() as tmp:
            m["site"], m["build"] = site(Path(tmp) / "site")
    return m


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    m = measure(build="--site" in argv)
    print("\n".join(report(m)))
    if "--record" in argv:
        record(m)
        print(f"added to {HISTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
