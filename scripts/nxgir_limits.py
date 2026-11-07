"""How close nx-gir is to the limits of GitHub and of
a phone: the measures behind scripts/check-limits.py
and the Statistics page of the web reader
(/api/stats, data/stats.json on the Pages site).

The limits and what they mean are explained in
notes/limits.md; notes/limits.tsv keeps the
measures over time.
"""

import datetime
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOKS = ROOT / "books"
HISTORY = ROOT / "notes" / "limits.tsv"

KB = 1024
MB = KB * KB
GB = KB * MB

# key: (label, limit, what sets it); in this order on
# the page
LIMITS = {
    "site": ("Pages site", GB, "GitHub Pages limit"),
    "git": ("Git history", GB, "GitHub's advice"),
    "file": ("Largest file", 50 * MB, "GitHub warns"),
    "part": ("Largest book part", MB, "our own target"),
    "build": ("Site build", 600, "our own target"),
}
# shares from which a limit is to be watched, and
# near; below WATCH it is fine
WATCH = 50
NEAR = 80
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


def by_folder(root=BOOKS):
    """{top folder: bytes of text}, e.g. grabar and
    ashkharhabar."""
    out = {}
    for p in sorted(root.rglob("*.txt")):
        top = p.relative_to(root).parts[0]
        out[top] = out.get(top, 0) + p.stat().st_size
    return out


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


def folder_size(path):
    """Bytes of all files under path."""
    return sum(
        p.stat().st_size
        for p in Path(path).rglob("*")
        if p.is_file()
    )


def measure(root=ROOT):
    """The measures that take seconds, as a dict of
    FIELDS (site and build "") with the names of the
    largest files and the text by folder."""
    n, text, part = books(root / "books")
    file = largest_tracked(root)
    return {
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
        "folders": by_folder(root / "books"),
    }


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
    return 100 * value / LIMITS[key][1]


def level(pct):
    """ "ok", "watch" or "near" for a share."""
    if pct >= NEAR:
        return "near"
    if pct >= WATCH:
        return "watch"
    return "ok"


def line(label, value, key, note=""):
    """One row: label, value / limit, percent, note."""
    limit = LIMITS[key][1]
    fmt = seconds if key == "build" else human
    used = f"{fmt(value)} / {fmt(limit)}"
    row = f"{label:<9}{used:<20}{share(value, key):>4.0f}%"
    return f"{row}  {note}" if note else row


def closest(m):
    """(share, key) of the limit m is closest to."""
    return max(
        (share(m[k], k), k) for k in LIMITS if m[k] != ""
    )


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
    pct, key = closest(m)
    rows.append(
        f"closest: {key} at {pct:.0f}% ({LIMITS[key][2]})"
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


def history(path=HISTORY):
    """The recorded lines of path, oldest first, as
    dicts of FIELDS; numbers as int, "" kept."""
    if not Path(path).exists():
        return []
    out = []
    for row in Path(path).read_text("utf-8").splitlines():
        if not row.strip() or row.startswith("#"):
            continue
        vals = row.split("\t")
        if vals[0] == FIELDS[0]:
            continue  # the names of the fields
        d = dict(zip(FIELDS, vals))
        for k in FIELDS[2:]:
            d[k] = int(d[k]) if d.get(k) else ""
        out.append(d)
    return out


def stats(m, past=(), words=None):
    """The Statistics page for measures m, the
    recorded past (oldest first) and the number of
    different words (or None). Where m has no site,
    build or git size, the last recorded one is
    shown, with its date: close enough, and the
    Pages build has no git history to measure."""
    m = dict(m)
    since = {}
    for k in ("site", "build", "git"):
        if m[k] == "":
            for row in reversed(past):
                if row[k] != "":
                    m[k] = row[k]
                    since[k] = row["date"]
                    break
    where = {
        "file": m.get("file_name", ""),
        "part": m.get("part_name", ""),
    }
    limits = []
    for k, (label, limit, by) in LIMITS.items():
        if m[k] == "":
            continue
        pct = share(m[k], k)
        limits.append(
            {
                "key": k,
                "label": label,
                "value": m[k],
                "limit": limit,
                "unit": "s" if k == "build" else "B",
                "share": round(pct, 1),
                "level": level(pct),
                "by": by,
                "where": where.get(k, ""),
                "since": since.get(k, ""),
            }
        )
    near = max(limits, key=lambda x: x["share"])
    return {
        "date": m["date"],
        "commit": m["commit"],
        "books": m["books"],
        "text": m["text"],
        "folders": m.get("folders", {}),
        "words": words,
        "limits": limits,
        "closest": near["key"],
        "history": [
            {k: row[k] for k in FIELDS}
            for row in reversed(past)
        ],
    }
