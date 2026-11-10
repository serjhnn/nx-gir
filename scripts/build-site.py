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
    data/blog.json                  /api/blog
    data/features.json              /api/features
    data/titles.json                each book's title,
        for /api/recent (the rest is in the browser)
    data/library.json               /api/library
    data/stats.json                 /api/stats, with
        this site's size and build time

and, for search engines (searchable()), which do
not see the #/ pages of app.js:

    read/<book>.html   each book as a plain page,
        its text in the HTML, linked to the reader;
        our translations with their credit and
        license (licensed())
    blog/<slug>.<lang>.html   each blog post in
        each of its languages, the same way
    features.<lang>.html   the Features page, the
        same way
    sitemap.xml, robots.txt   where they are

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
import html as htm
import importlib.util
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

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
# the published address (the custom domain set in
# Settings, Pages), for sitemap.xml and canonical
# links
SITE = "https://nxgir.am"
# what search results show under a book's title:
# the start of its text, this long at most
DESCRIBE = 155


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
    code, or "").

    static.js also names this build, which app.js
    puts after the address of each file of data/
    (?b=): a browser may keep a file for 10
    minutes, and a new app.js must not read an old
    blog.json (or the other way round). static.js
    is versioned, so a new build is a new page."""
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
    build = f"{time.time_ns():x}"
    (out / "static.js").write_text(
        "// the published copy: app.js reads data/\n"
        "window.NXGIR_STATIC = true;\n"
        f'window.NXGIR_BUILD = "{build}";\n' + count,
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


def build(
    out,
    files,
    timeline=web.tl.TIMELINE,
    blog=web.blog_posts.BLOG,
    features=web.feature_list.FEATURES,
):
    """Write the site for files [(name, size, path)],
    the events of timeline (timeline.tsv), the
    posts in blog (blog/) and the Features page
    (features/) into out. Returns (books, folders,
    words)."""
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
            files,
            state_path=state,
            timeline=timeline,
            blog=blog,
            features=features,
        )
        dirs = folders(files)
        write_json(
            data / "timeline.json", web.timeline(app)
        )
        write_json(data / "library.json", web.library(app))
        write_json(data / "blog.json", web.blog(app))
        write_json(
            data / "features.json", web.features(app)
        )
        # for the list of readings, which only has
        # the names (recentHere() in app.js)
        write_json(
            data / "titles.json",
            {
                n: web.book_title(app, n)
                for n, _, _ in files
            },
        )
        for f in dirs:
            path = data / "shelf" / f / "index.json"
            write_json(path, web.shelf(app, f))
        words = set()
        searchable(out, app, files)
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


def page_path(name):
    """Where a book's plain page is: read/<book>.html,
    without the .txt or .md."""
    return "read/" + name.rpartition(".")[0] + ".html"


def url(path):
    """The full address of a path of the site, each
    part %-escaped as in enc() of app.js."""
    return f"{SITE}/{quote(path)}"


def describe(lines, n=DESCRIBE):
    """The start of a text, after its title, cut at a
    word: for <meta name="description">."""
    text = " ".join(
        x.strip() for x in lines[1:] if x.strip()
    )
    if len(text) <= n:
        return text
    return text[:n].rpartition(" ")[0] + "…"


PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport"
  content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<base href="/">
<title>{title} · Նախագիր</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
{alt}<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<link rel="icon" href="icon.svg">
<script src="theme.js"></script>
<link rel="stylesheet" href="fonts.css">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="bar">
  <a class="brand" href="./" lang="hy">Նախագիր</a>
</header>
<main class="plain">
<p><a href="{reader}">{open}</a></p>
<h1>{title}</h1>
{text}
</main>
</body>
</html>
"""


# the link at the top of a plain page
OPEN_BOOK = "Read in the reader,\nwith word lookup"
OPEN_POST = {
    "hy": "Բացել Նախագրում",
    "en": "Open in nx-gir",
    "ru": "Открыть в nx-gir",
}


def plain_page(out, path, text, alt="", **kw):
    """Write a plain page (PAGE) at path of out:
    text and alt (links in the head: its other
    languages, its license) are HTML, the rest
    (title, desc, reader, and lang and open if not
    the book's) plain."""
    kw = {"lang": "hy", "open": OPEN_BOOK, **kw}
    kw = {k: htm.escape(v) for k, v in kw.items()}
    page = PAGE.format(
        canon=htm.escape(url(path)),
        text=text,
        alt=alt,
        **kw,
    )
    dest = out / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(versioned(page, out), "utf-8")


def post_page(slug, lang):
    """Where a blog post's plain page is."""
    return f"blog/{slug}.{lang}.html"


def post_pages(out, app):
    """Each version of each blog post as a plain
    page, blog/<slug>.<lang>.html, which names the
    others (hreflang). Returns [(path, title,
    date)]."""
    links = []
    for p in web.blog(app)["posts"]:
        slug, vs = p["slug"], p["versions"]
        alt = "".join(
            '<link rel="alternate" hreflang='
            f'"{v["lang"]}" href="'
            f"{htm.escape(url(post_page(slug, v['lang'])))}"
            '">\n'
            for v in vs
        )
        for v in vs:
            path = post_page(slug, v["lang"])
            text = "\n".join(
                f"<{t}>{htm.escape(x)}</{t}>"
                for k, x in v["blocks"]
                for t in ["h2" if k == "h" else "p"]
            )
            paras = [x for k, x in v["blocks"] if k == "p"]
            plain_page(
                out,
                path,
                lang=v["lang"],
                open=OPEN_POST[v["lang"]],
                title=v["title"],
                desc=describe([""] + paras),
                reader=f"./#/blog/{slug}/{v['lang']}",
                text=text,
                alt=alt if len(vs) > 1 else "",
            )
            links.append((path, v["title"], p["date"]))
    return links


def feature_pages(out, app):
    """The Features page in each of its languages
    as a plain page, features.<lang>.html, naming
    the others (hreflang). Returns [(path,
    title)]."""
    vs = web.features(app)["versions"]

    def page(lang):
        return f"features.{lang}.html"

    alt = "".join(
        '<link rel="alternate" hreflang='
        f'"{v["lang"]}" href="'
        f'{htm.escape(url(page(v["lang"])))}">\n'
        for v in vs
    )
    links = []
    for v in vs:
        path = page(v["lang"])
        text = "\n".join(
            f"<{t}>{htm.escape(x)}</{t}>"
            for k, x in v["blocks"]
            for t in ["h2" if k == "h" else "p"]
        )
        paras = [x for k, x in v["blocks"] if k == "p"]
        plain_page(
            out,
            path,
            lang=v["lang"],
            open=OPEN_POST[v["lang"]],
            title=v["title"],
            desc=describe([""] + paras),
            reader=f"./#/features/{v['lang']}",
            text=text,
            alt=alt if len(vs) > 1 else "",
        )
        links.append((path, v["title"]))
    return links


def licensed(credit, text):
    """For one of our translations (credit, from
    nxgir_web.credit()): the license link for the
    head, and text with the credit line on top.
    Else ("", text)."""
    if not credit:
        return "", text
    esc = htm.escape
    href = esc(credit["url"])
    line = (
        f'<p class="tr-credit">{esc(credit["text"])} · '
        f'<a rel="license" href="{href}">'
        f"{esc(credit['license'])}</a></p>\n"
    )
    return (
        f'<link rel="license" href="{href}">\n',
        line + text,
    )


def searchable(out, app, files):
    """What search engines need to find the books:
    app.js shows everything at #/ addresses, and to
    a search engine those are all the one top page.
    So each book is also a plain page with its text
    (read/<book>.html), listed in sitemap.xml, which
    robots.txt names, and linked from index.html for
    browsers without JavaScript. The blog posts
    too (post_pages()), with their dates, and the
    Features page (feature_pages())."""
    esc = htm.escape
    links = []
    for name, _, _ in files:
        lines = web.book_text(app, name).splitlines()
        if not lines:
            continue
        path = page_path(name)
        title = lines[0].strip() or name
        text = "\n".join(
            f"<p>{esc(x.strip())}</p>"
            for x in lines[1:]
            if x.strip()
        )
        reader = "./#/read/" + "/".join(
            quote(x, safe="") for x in name.split("/")
        )
        lic, text = licensed(web.credit(app, name), text)
        plain_page(
            out,
            path,
            title=title,
            desc=describe(lines),
            reader=reader,
            text=text,
            alt=lic,
        )
        links.append((path, title))
    posts = post_pages(out, app)
    links += feature_pages(out, app)
    urls = [(SITE + "/", "")]
    urls += [(url(p), "") for p, _ in links]
    urls += [(url(p), d) for p, _, d in posts]
    links += [(p, t) for p, t, _ in posts]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/'
        'schemas/sitemap/0.9">\n'
        + "".join(
            f"<url><loc>{esc(u)}</loc>"
            + (f"<lastmod>{d}</lastmod>" if d else "")
            + "</url>\n"
            for u, d in urls
        )
        + "</urlset>\n",
        "utf-8",
    )
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
        "utf-8",
    )
    index = out / "index.html"
    html = index.read_text("utf-8")
    # the list goes in main, after its own words
    tag = "</main>"
    if html.count(tag) != 1:
        raise SystemExit("index.html: no main")
    nav = "".join(
        f'<li><a href="{esc(p)}">{esc(t)}</a></li>\n'
        for p, t in links
    )
    html = html.replace(
        tag,
        "<noscript><ul>\n"
        + nav
        + "</ul></noscript>\n"
        + tag,
    )
    canon = f'<link rel="canonical" href="{SITE}/">\n'
    html = html.replace("</head>", canon + "</head>")
    index.write_text(html, "utf-8")


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
