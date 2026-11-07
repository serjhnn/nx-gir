#!/usr/bin/env python3
"""Build the published, read-only copy of the web
reader: plain files for GitHub Pages, no server.

    scripts/build-site.py [OUT]      (default: site/)

It holds the pages of web/ and, under data/, the
answers `nxgir web` would give, worked out once with
the same functions (nxgir_web.py):

    data/shelf/<folder>/index.json  /api/shelf
    data/book/<name>.json           /api/book
    data/word/<lang>/<n>.json       /api/word, the
        words of the books that the Grabar helpers
        know, spread over BUCKETS files by bucket()
    data/timeline.json              /api/timeline
    data/stats.json                 /api/stats, with
        this site's size and build time

The test texts of data/ and the user's own texts in
interpretations/ are left out.

static.js tells app.js to read these files. The copy
only reads: no bookmarks, notes or editing, and where
you stopped is kept in the browser. Nothing of the
saved state on this computer goes into it.

.github/workflows/pages.yml runs this on every push
to main and publishes OUT.
"""

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import nxgir_limits as lim  # noqa: E402
import nxgir_web as web  # noqa: E402

# files the words are spread over, per language;
# as BUCKETS in web/app.js
BUCKETS = 256
# marks a folder this script made, so it may be
# emptied and made again
MARK = ".nxgir-site"
# the files index.html loads, given a ?v= of their
# content (versioned())
VERSIONED = (
    "theme.js",
    "fonts.css",
    "style.css",
    "static.js",
    "app.js",
)
# GoatCounter (goatcounter.com): the site's code,
# CODE.goatcounter.com, where the published copy
# counts its visits; "" counts nothing
GOATCOUNTER = "nxgir"


def bucket(w):
    """Which file a word is in: FNV-1a over its code
    points; as bucket() in web/app.js."""
    x = 0x811C9DC5
    for ch in w:
        x = ((x ^ ord(ch)) * 0x01000193) & 0xFFFFFFFF
    return x % BUCKETS


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        obj, ensure_ascii=False, separators=(",", ":")
    )
    path.write_text(text, encoding="utf-8")


def folders(files):
    """Every folder on the shelf, "" (the top) too."""
    out = {""}
    for name, _, _ in files:
        parts = name.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            out.add("/".join(parts[:i]))
    return sorted(out)


def pages(out, counter=GOATCOUNTER):
    """The pages of web/, told to read the files, and
    where to count visits (counter: a GoatCounter
    code, or "")."""
    for p in web.WEB_DIR.iterdir():
        if p.is_file():
            shutil.copy2(p, out / p.name)
        elif p.is_dir():  # fonts/
            shutil.copytree(
                p, out / p.name, dirs_exist_ok=True
            )
    count = ""
    if counter:
        url = f"https://{counter}.goatcounter.com/count"
        count = f'window.NXGIR_COUNT = "{url}";\n'
    (out / "static.js").write_text(
        "// the published copy: app.js reads data/\n"
        "window.NXGIR_STATIC = true;\n" + count,
        encoding="utf-8",
    )
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    tag = '<script src="app.js"></script>'
    if tag not in html:
        raise SystemExit("index.html: no app.js script")
    html = html.replace(
        tag, '<script src="static.js"></script>\n' + tag
    )
    index.write_text(versioned(html, out), "utf-8")
    # GitHub Pages: serve the files as they are
    (out / ".nojekyll").write_text("")


def versioned(html, out):
    """html with ?v=<hash of the file> after each of
    VERSIONED: GitHub Pages lets browsers keep a
    file for 10 minutes, and a new page with an old
    app.js or theme.js would be broken. With a new
    name for each change the page and its files go
    together."""
    for name in VERSIONED:
        data = (out / name).read_bytes()
        v = hashlib.sha256(data).hexdigest()[:10]
        for attr in ("src", "href"):
            old = f'{attr}="{name}"'
            if old not in html:
                continue
            new = f'{attr}="{name}?v={v}"'
            html = html.replace(old, new)
    return html


def build(out, files, timeline=web.tl.TIMELINE):
    """Write the site for files [(name, size, path)]
    and the events of timeline (timeline.tsv) into
    out. Returns (books, folders, words)."""
    start = time.monotonic()
    out = Path(out)
    if out.exists():
        if not (out / MARK).exists():
            raise SystemExit(
                f"{out} exists and was not made by"
                " build-site.py; not touching it"
            )
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARK).write_text("")
    pages(out)
    data = out / "data"
    with tempfile.TemporaryDirectory() as tmp:
        # an empty state: positions stay at home
        state = Path(tmp) / "state.json"
        app = web.App(
            files, state_path=state, timeline=timeline
        )
        dirs = folders(files)
        write_json(
            data / "timeline.json", web.timeline(app)
        )
        for f in dirs:
            path = data / "shelf" / f / "index.json"
            write_json(path, web.shelf(app, f))
        words = set()
        for name, _, _ in files:
            b = web.book(app, name)
            write_json(data / "book" / f"{name}.json", b)
            for line in b["lines"]:
                words.update(w.strip() for w in line[1::2])
    words.discard("")
    for lang in web.LANGS:
        found = [{} for _ in range(BUCKETS)]
        for w in sorted(words):
            d = web.word(w, lang)
            if d["abbr"] or d["meaning"]:
                found[bucket(w)][w] = [
                    d["abbr"],
                    d["meaning"],
                ]
        for n, part in enumerate(found):
            write_json(
                data / "word" / lang / f"{n}.json", part
            )
    write_json(
        data / "stats.json",
        stats(out, words, time.monotonic() - start),
    )
    return len(files), len(dirs), len(words)


def stats(out, words, took, root=ROOT):
    """The Statistics page with the size of the site
    in out and the time it took to build. The size
    of the git history is the last recorded in
    notes/limits.tsv: GitHub Actions checks out the
    last commit only. Without git at all the page
    says so."""
    try:
        m = lim.measure(root)
    except (OSError, lim.subprocess.CalledProcessError):
        return {"error": "measured without git"}
    m["site"] = lim.folder_size(out)
    m["build"] = round(took)
    m["git"] = ""  # the recorded one, see above
    return lim.stats(m, lim.history(), len(words))


def shelf_files():
    """The books, as the CLI finds them, without the
    test texts of data/ and interpretations/."""
    path = HERE / "nxgir-cli.py"
    spec = importlib.util.spec_from_file_location(
        "nxgir_cli", path
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return [
        f
        for f in cli.shelf_files()
        if not unpublished(
            f[2], cli.DATA_DIR, cli.NOTES_DIR
        )
    ]


def unpublished(path, *dirs):
    """True for a file in one of dirs: data/ (test
    texts) and interpretations/ (the user's own)."""
    p = Path(path).resolve()
    return any(
        p.is_relative_to(Path(d).resolve()) for d in dirs
    )


def size(path):
    n = sum(
        p.stat().st_size
        for p in path.rglob("*")
        if p.is_file()
    )
    return f"{n / 1e6:.1f} MB"


def main(argv):
    out = Path(argv[0]) if argv else ROOT / "site"
    books, dirs, words = build(out, shelf_files())
    print(
        f"{out}: {books} books, {dirs} folders,"
        f" {words} words, {size(out)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
