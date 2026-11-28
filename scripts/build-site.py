#!/usr/bin/env python3
"""Build the published, read-only copy of the web
reader: plain files for GitHub Pages, no server.

    scripts/build-site.py [--zip] [OUT]   (default: site/)

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
    data/authors.json               /api/authors
    data/author/<id>.json           /api/author
    data/book/<author>/<book>.json  /api/book-info
    data/book-cards/<lang>.json     /api/book-cards,
        the Reference page
    data/comics.json                /api/comics
    data/map.json                   /api/map
    data/titles.json                each book's title,
        for /api/recent (the rest is in the browser)
    data/library.json               /api/library
    data/volume/<folder>.json       /api/volume, for each
        folder two or more levels into grabar/ and
        ashkharhabar/
    data/stats.json                 /api/stats, with
        this site's size and build time
    data/search/parts.json          /api/search-parts
    data/search/<n>.json            /api/search, the
        words of the searched books (nxgir_search.py),
        spread over BUCKETS files by bucket() of their
        loose key
    data/lines/<book>/<k>.json      /api/lines: a book
        searched, 100 lines a file

and, for search engines (searchable()): the pages
of app.js are paths (/library, /read/<book>), and
each one that a search engine should list is also a
file, <path>/index.html: the page of the app with
its own title, description and canonical link, and
its words in place of the top page's, which app.js
draws over (route_page()). Other paths are given
404.html, the plain app, which reads the address:

    Every page of the app is under its language
    (web/i18n.js): /hy/library, /en/blog. The pages
    with Armenian text are under hy/ only:

    <lang>/   the top page in each language, named
        by each other (home_pages())
    hy/read/<book>/   each book, its text in the
        HTML; our translations with their credit and
        license (licensed())
    <lang>/blog/<slug>/   each blog post in each of
        its languages; <lang>/comics/<slug>/ the same
    <lang>/features/   the Features page
    <lang>/map/, <lang>/map/<place>/   the Map page,
        and each place that a post or comic names,
        with those stories (map_pages())
    hy/library/, hy/b/<folder>/, hy/reference/,
        <lang>/blog/, <lang>/comics/,
        <lang>/timeline/   the lists, with links
        (hub_pages())
    sitemap.xml, robots.txt   where they are

and, only with --zip (not built now, kept for later),
the whole site as one file to read with no network
(offline_zip()):

    nxgir-site.zip   the pages and data, a static.js
        with no visit counter, and scripts/offline/
        (README.txt, serve.py); linked on the Offline
        page
    download.json    its name and size, not in it

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
import re
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import nxgir_limits as lim  # noqa: E402
import nxgir_map as nm  # noqa: E402
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
    "i18n.js",
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


STATIC_JS = (
    "// the published copy: app.js reads data/\n"
    "window.NXGIR_STATIC = true;\n"
)
# the offline copy: a zip of the site (offline_zip())
ZIP = "nxgir-site.zip"
# the languages of the pages (LANGS in web/i18n.js),
# each a folder of pages for search engines
LANGS = web.blog_posts.LANGS
# left out of it: the pages for search engines
NOT_OFFLINE = tuple(f"{x}/" for x in LANGS) + (
    "404.html",
    "sitemap.xml",
    "robots.txt",
    "sw.js",
    "offline.json",
)
# not saved by "Save for offline" either (sw.js)
NOT_SAVED = NOT_OFFLINE + (
    "og-image.png",
    "download.json",
    ZIP,
    MARK,
    ".nojekyll",
)


def pages(out, counter=GOATCOUNTER, download=False):
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
        STATIC_JS
        + f'window.NXGIR_BUILD = "{build}";\n'
        + (
            f'window.NXGIR_DOWNLOAD = "{ZIP}";\n'
            if download
            else ""
        )
        + 'window.NXGIR_SW = "sw.js";\n'
        + count,
        encoding="utf-8",
    )
    # the service worker names the build, so a new
    # build is a new cache (web/sw.js)
    sw = (out / "sw.js").read_text(encoding="utf-8")
    mark = 'const BUILD = "dev";'
    if mark not in sw:
        raise SystemExit("sw.js: no BUILD line")
    (out / "sw.js").write_text(
        sw.replace(mark, f'const BUILD = "{build}";'),
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
    comics=web.comic_series.COMICS,
    places=web.place_map.PLACES,
    authors=web.author_info.AUTHORS,
    zip_site=False,
):
    """Write the site for files [(name, size, path)],
    the events of timeline (timeline.tsv), the
    posts in blog (blog/) and the Features page
    (features/) into out; with zip_site, also the
    site as one zip file (offline_zip()). Returns
    (books, folders, words)."""
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
    pages(out, download=zip_site)
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
            comics=comics,
            places=places,
            authors=authors,
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
        write_json(data / "comics.json", web.comics(app))
        ids = web.authors(app)
        write_json(data / "authors.json", ids)
        for aid in ids["authors"]:
            write_json(
                data / "author" / f"{aid}.json",
                web.author(app, aid),
            )
        for bid in ids["books"]:
            write_json(
                data / "book" / f"{bid}.json",
                web.book_info(app, bid),
            )
        for lang in web.author_info.LANGS:
            write_json(
                data / "book-cards" / f"{lang}.json",
                web.book_cards(app, lang),
            )
        write_json(data / "map.json", web.map_data(app))
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
            top, _, key = f.partition("/")
            if top in web.PARALLEL and key:
                write_json(
                    data / "volume" / f"{f}.json",
                    web.volume(app, f),
                )
        search_files(data, app)
        words = set()
        searchable(out, app, files, dirs)
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
    offline_list(out)
    if zip_site:
        offline_zip(out)
    return len(files), len(dirs), len(words)


def search_files(data, app):
    """The search index as files (nxgir_search.py):
    the parts searched, the words by bucket of their
    loose key, and the lines of each part."""
    index, parts = web.search_index(app)
    write_json(data / "search" / "parts.json", parts)
    write_json(
        data / "search" / "lemmas.json",
        web.search_lemmas(app),
    )
    found = [{} for _ in range(BUCKETS)]
    for key in index.keys():
        found[bucket(key)][key] = index.entry(key)
    for n, part in enumerate(found):
        write_json(data / "search" / f"{n}.json", part)
    for name in index.parts:
        text = web.book_text(app, name)
        n = len(text.splitlines())
        for k in range(0, max(n, 1), web.srch.CHUNK):
            k //= web.srch.CHUNK
            write_json(
                data / "lines" / name / f"{k}.json",
                {"lines": web.srch.chunk(text, k)},
            )


def offline_list(out):
    """offline.json: the build and every file the
    service worker keeps when asked to save the
    whole site, [path, bytes] (web/sw.js). The pages
    for search engines are not in it."""
    build = re.search(
        r'NXGIR_BUILD = "(\w+)"',
        (out / "static.js").read_text("utf-8"),
    ).group(1)
    files = []
    for p in sorted(out.rglob("*")):
        rel = p.relative_to(out).as_posix()
        if p.is_file() and not rel.startswith(NOT_SAVED):
            files.append([quote(rel), p.stat().st_size])
    write_json(
        out / "offline.json",
        {"build": build, "files": files},
    )


def offline_zip(out):
    """The site as one file, ZIP, to read with no
    network: the pages and data (not the pages for
    search engines), a static.js with no visit
    counter and no link to this file, and
    scripts/offline/ (README.txt, serve.py: file://
    cannot read the data files). The address and
    size of the file go to download.json, which is
    not in it."""
    base = "nxgir-site/"
    path = out / ZIP
    with zipfile.ZipFile(
        path, "w", zipfile.ZIP_DEFLATED, compresslevel=9
    ) as z:
        for p in sorted(out.rglob("*")):
            rel = p.relative_to(out).as_posix()
            if (
                not p.is_file()
                or p == path
                or rel == MARK
                or rel == "static.js"
                or rel.startswith(NOT_OFFLINE)
            ):
                continue
            z.write(p, base + rel)
        static = (out / "static.js").read_text("utf-8")
        z.writestr(
            base + "static.js",
            "".join(
                x
                for x in static.splitlines(keepends=True)
                if x.startswith(
                    ("//", "window.NXGIR_STATIC")
                )
                or "NXGIR_BUILD" in x
            ),
        )
        for p in sorted(
            (ROOT / "scripts/offline").iterdir()
        ):
            z.write(p, base + p.name)
    write_json(
        out / "download.json",
        {"file": ZIP, "bytes": path.stat().st_size},
    )


def page_path(name):
    """Where a book's page is: hy/read/<book>/, the
    name as it is, with its .txt."""
    return "hy/read/" + name


def route_url(path):
    """The full address of the page at path: with a
    slash at the end, as GitHub Pages gives a folder.
    Each part is %-escaped as in enc() of app.js."""
    return f"{SITE}/{quote(path)}/" if path else SITE + "/"


def url(path):
    """The full address of a file of the site."""
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


def named(html):
    """Escaped HTML with each nxGir in the accent
    color, as named() in app.js."""
    return html.replace(
        "nxGir", '<span class="nxgir">nxGir</span>'
    )


def sub(pattern, text, html):
    """html with the first match of pattern (across
    lines) replaced by text, as it is. The pattern
    must be there."""
    new, n = re.subn(
        pattern, lambda m: text, html, count=1, flags=re.S
    )
    if not n:
        raise SystemExit(f"index.html: no {pattern}")
    return new


# the titles and first words of the lists in each
# language (the Blog, Comics and Timeline pages of
# app.js)
LISTS = {
    "blog": {
        "hy": (
            "Բլոգ",
            "Նորություններ և նշումներ Նախագրից։",
        ),
        "en": ("Blog", "News and notes from nxGir."),
        "ru": ("Блог", "Новости и заметки nxGir."),
    },
    "comics": {
        "hy": (
            "Կոմիքսներ",
            "Գրադարանի գրքերի տեսարանները նկարներով։",
        ),
        "en": (
            "Comics",
            "Scenes from the books of the Library.",
        ),
        "ru": ("Комиксы", "Сцены из книг Библиотеки."),
    },
    "timeline": {
        "hy": (
            "Թարմացումներ",
            "Նախագրի հիմնական քայլերը՝ նորից հին։",
        ),
        "en": (
            "Timeline",
            "The main steps of nxGir, newest first.",
        ),
        "ru": (
            "Хронология",
            "Главные шаги nxGir, от новых к старым.",
        ),
    },
    "about": {
        "hy": (
            "Նախագծի մասին",
            "Նախագիրը (nxGir)՝ գրաբար գրքերի անվճար"
            " գրադարան և ընթերցարան։ Հեղինակ՝ Սերգեյ"
            " Օհանյան։",
        ),
        "en": (
            "About the project",
            "nxGir is a free library and reader of"
            " Grabar books. Made by Sergey Ohanyan"
            " with Claude.",
        ),
        "ru": (
            "О проекте",
            "nxGir — бесплатная библиотека и читалка"
            " книг на грабаре. Автор — Сергей Оганян"
            " вместе с Claude.",
        ),
    },
}

# the top page in each language: its title (as
# "title.top" in web/i18n.js) and what the site is
HOME = {
    "hy": (
        "Գրաբար գրքեր՝ բառ առ բառ",
        "Գրաբար գրքեր՝ ժամանակակից հայերեն"
        " թարգմանության հետ կողք կողքի, և ամեն բառի"
        " իմաստը՝ մեկ հպումով. Գրիգոր Տաթևացի, Ներսես"
        " Շնորհալի և շատ ուրիշներ։",
    ),
    "en": (
        "Grabar books, word by word",
        "Grabar (Classical Armenian) books with Modern"
        " Armenian translations side by side, and the"
        " meaning of every word a tap away: Grigor"
        " Tatevatsi, Nerses Shnorhali and many others.",
    ),
    "ru": (
        "Книги на грабаре, слово за словом",
        "Книги на грабаре (классическом армянском) с"
        " переводами на современный армянский бок о"
        " бок и значением каждого слова в одно"
        " касание: Григор Татеваци, Нерсес Шнорали и"
        " многие другие.",
    ),
}


def home_alt():
    """The top page in each language, for the head
    of each (hreflang); the root, which opens the
    browser's, as x-default."""
    esc = htm.escape
    return "".join(
        '<link rel="alternate" hreflang='
        f'"{lang}" href="{esc(route_url(lang))}">\n'
        for lang in LANGS
    ) + (
        '<link rel="alternate" hreflang="x-default"'
        f' href="{SITE}/">\n'
    )


def home_pages(out):
    """<lang>/: the top page in each language.
    Returns [(path, title)]."""
    links = []
    for lang in LANGS:
        title, desc = HOME[lang]
        route_page(
            out,
            lang,
            lang=lang,
            title=title,
            desc=desc,
            text=f"<p>{htm.escape(desc)}</p>",
            alt=home_alt(),
        )
        links.append((lang, title))
    return links


def route_page(out, path, text, alt="", lang="hy", **kw):
    """Write the page at path (a folder of out, with
    index.html): index.html of out, told its own
    title, desc, canonical link and og: lines, with
    text (HTML, under the heading) in place of the
    top page's own words, and alt (links in the head:
    its other languages, its license). app.js draws
    over the words, reading the address."""
    esc = htm.escape
    title, desc = esc(kw["title"]), esc(kw["desc"])
    canon = esc(route_url(path))
    html = (out / "index.html").read_text("utf-8")
    html = html.replace(
        '<html lang="en">', f'<html lang="{lang}">', 1
    )
    html = sub(
        r"<title>.*?</title>",
        f"<title>{title} · Նախագիր | nxGir</title>",
        html,
    )
    html = sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{desc}">',
        html,
    )
    for prop, val in (
        ("title", title),
        ("description", desc),
        ("url", canon),
        ("type", "article"),
    ):
        html = sub(
            rf'<meta property="og:{prop}"\s+'
            r'content="[^"]*">',
            f'<meta property="og:{prop}" content="{val}">',
            html,
        )
    html = html.replace(
        "</head>",
        f'<link rel="canonical" href="{canon}">\n'
        + alt
        + "</head>",
        1,
    )
    html = sub(
        r'<section class="about" id="about">.*?'
        r"</section>",
        '<section class="about" id="about"'
        f' lang="{lang}">\n'
        f"<h1>{named(title)}</h1>\n{text}\n</section>",
        html,
    )
    dest = out / path / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, "utf-8")


def post_page(slug, lang, kind="blog"):
    """Where a blog post's (or, with kind "comics",
    a comics series') page is."""
    return f"{lang}/{kind}/{slug}"


def blog_block(block, lang="hy"):
    """One block of a blog post as HTML."""
    kind, text, *alt = block
    if kind == "link":
        # "#/3d/id" is the page /<lang>/3d/id
        href = route_url(f"{lang}/{alt[0][2:]}")
        return (
            f'<p><a href="{htm.escape(href)}">'
            f"{named(htm.escape(text))}</a></p>"
        )
    if kind == "video":
        # the still, a link to the video on YouTube
        src = htm.escape(url(f"img/{alt[1]}"))
        watch = htm.escape(
            f"https://www.youtube.com/watch?v={text}"
        )
        return (
            f'<p><a href="{watch}"><img'
            ' style="max-width:100%;height:auto"'
            f' src="{src}" alt="{htm.escape(alt[0])}">'
            "</a></p>"
        )
    if kind == "img":
        src = htm.escape(url(f"img/{text}"))
        return (
            '<p><img style="max-width:100%;height:auto"'
            f' src="{src}" alt="{htm.escape(alt[0])}"></p>'
        )
    if kind == "list":
        items = "".join(
            f"<li>{named(htm.escape(x))}</li>" for x in text
        )
        return f"<ul>{items}</ul>"
    if kind == "prompt":
        return f"<pre>{htm.escape(text)}</pre>"
    if kind == "cap":
        return f"<p><em>{named(htm.escape(text))}</em></p>"
    tag = "h2" if kind == "h" else "p"
    return f"<{tag}>{named(htm.escape(text))}</{tag}>"


def post_pages(out, app, comics=False):
    """Each version of each blog post as a page,
    <lang>/blog/<slug>/, which names the others
    (hreflang); with comics, each version of each
    comics series, <lang>/comics/<slug>/.
    Returns [(path, title, date)]."""
    links = []
    kind = "comics" if comics else "blog"
    posts = (
        web.comics(app)["series"]
        if comics
        else web.blog(app)["posts"]
    )
    for p in posts:
        slug, vs = p["slug"], p["versions"]

        def page_of(v, slug=slug):
            return post_page(slug, v["lang"], kind)

        alt = "".join(
            '<link rel="alternate" hreflang='
            f'"{v["lang"]}" href="'
            f"{htm.escape(route_url(page_of(v)))}"
            '">\n'
            for v in vs
        )
        for v in vs:
            path = page_of(v)
            text = "\n".join(
                blog_block(b, v["lang"])
                for b in v["blocks"]
            )
            paras = [
                b[1] for b in v["blocks"] if b[0] == "p"
            ]
            route_page(
                out,
                path,
                lang=v["lang"],
                title=v["title"],
                desc=describe([""] + paras),
                text=text,
                alt=alt if len(vs) > 1 else "",
            )
            links.append((path, v["title"], p["date"]))
    return links


def feature_pages(out, app):
    """The Features page in each of its languages
    as a page, <lang>/features/, naming
    the others (hreflang). Returns [(path,
    title)]."""
    vs = web.features(app)["versions"]

    def page(lang):
        return f"{lang}/features"

    alt = "".join(
        '<link rel="alternate" hreflang='
        f'"{v["lang"]}" href="'
        f'{htm.escape(route_url(page(v["lang"])))}">\n'
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
        route_page(
            out,
            path,
            lang=v["lang"],
            title=v["title"],
            desc=describe([""] + paras),
            text=text,
            alt=alt if len(vs) > 1 else "",
        )
        links.append((path, v["title"]))
    return links


# the title and the first words of the Map page, in
# each language (MAP_UI in app.js)
MAP_PAGE = {
    "hy": (
        "Քարտեզ",
        "Հայկական լեռնաշխարհի վայրերը, որոնց մասին"
        " գրառումներ և կոմիքսներ կան։",
    ),
    "en": (
        "Map",
        "The places of the Armenian Highland that"
        " posts and comics are about.",
    ),
    "ru": (
        "Карта",
        "Места Армянского нагорья, о которых есть"
        " записи и комиксы.",
    ),
}


def map_pages(out, app):
    """The Map as pages for search engines: for
    each language <lang>/map/, the places with a
    link to their page, and for each place that a post
    or comic names, <lang>/map/<id>/ with those
    stories, linked to their own plain pages. All
    name each other (hreflang). Returns (links,
    dated): [(path, title)] and [(path, title, date)]
    with the date of the newest story."""
    places = web.map_data(app)["places"]
    if not places:
        return [], []
    named_ = [p for p in places if p["stories"]]
    esc = htm.escape

    def alt(paths):
        return "".join(
            '<link rel="alternate" hreflang='
            f'"{lang}" href="{esc(route_url(path))}">\n'
            for lang, path in paths
        )

    links, dated = [], []
    langs = list(MAP_PAGE)
    for lang in langs:
        title, intro = MAP_PAGE[lang]
        kinds = nm.KIND_NAMES[lang]
        items = []
        for p in places:
            name = esc(p["names"][lang])
            if p["stories"]:
                href = esc(f"/{lang}/map/{p['id']}/")
                name = f'<a href="{href}">{name}</a>'
            items.append(
                f"<li>{name} · {esc(kinds[p['kind']])}</li>"
            )
        path = f"{lang}/map"
        route_page(
            out,
            path,
            lang=lang,
            title=title,
            desc=intro,
            text=f"<p>{esc(intro)}</p>\n<ul>\n"
            + "\n".join(items)
            + "\n</ul>",
            alt=alt([(x, f"{x}/map") for x in langs]),
        )
        links.append((path, title))
    for p in named_:
        sibs = alt(
            [(x, f"{x}/map/{p['id']}") for x in langs]
        )
        newest = max(s["date"] for s in p["stories"])
        for lang in langs:
            body = [f"<p>{esc(kinds_of(p, lang))}</p>"]
            leads = []
            for s in p["stories"]:
                v = next(
                    (
                        x
                        for x in s["versions"]
                        if x["lang"] == lang
                    ),
                    s["versions"][0],
                )
                href = esc(
                    "/"
                    + post_page(
                        s["slug"], v["lang"], s["type"]
                    )
                    + "/"
                )
                body.append(
                    f'<h2><a href="{href}">'
                    f"{named(esc(v['title']))}</a></h2>"
                )
                if v["lead"]:
                    leads.append(v["lead"])
                    body.append(
                        f"<p>{named(esc(v['lead']))}</p>"
                    )
            path = f"{lang}/map/{p['id']}"
            route_page(
                out,
                path,
                lang=lang,
                title=p["names"][lang],
                desc=describe([""] + leads)
                or p["names"][lang],
                text="\n".join(body),
                alt=sibs,
            )
            dated.append((path, p["names"][lang], newest))
    return links, dated


def kinds_of(place, lang):
    """The kind of a place in lang, as a word."""
    return nm.KIND_NAMES[lang][place["kind"]]


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


def all_names(names, aid, hy=""):
    """An author's name in each language, joined: Armenian
    (hy, or the one in names), English, Russian."""
    got = names.get(aid, {})
    seen = []
    for n in [hy or got.get("hy", "")] + [
        got.get(x, "") for x in ("en", "ru")
    ]:
        if n and n not in seen:
            seen.append(n)
    return " · ".join(seen)


def part_href(part):
    """The link to a part of a volume's page."""
    return "/" + page_path(part["name"]) + "/"


def volume_pages(out, app, dirs, names):
    """hy/b/<folder>/ for the folder of each book of
    grabar/ and ashkharhabar/ (a book's page in the
    app): its parts, linked to their pages. Returns
    [(path, title)] and the set of folders."""
    esc = htm.escape
    links, folders_ = [], set()
    for f in dirs:
        top, _, key = f.partition("/")
        if top not in web.PARALLEL or key.count("/") < 1:
            continue
        v = web.volume(app, f)
        body = []
        by = ", ".join(
            all_names(names, a["id"], a["name"])
            for a in v["authors"]
        )
        if by:
            body.append(f"<p>{esc(by)}</p>")
        for g in v["groups"]:
            if g["label"]:
                body.append(f"<h2>{esc(g['label'])}</h2>")
            items = "".join(
                f'<li><a href="{esc(part_href(p))}">'
                f"{esc(p['title'] or str(p['n']))}"
                "</a></li>\n"
                for p in g["parts"]
            )
            body.append(f"<ol>\n{items}</ol>")
        path = f"hy/b/{f}"
        title = v["title"] or v["book"]
        route_page(
            out,
            path,
            title=title,
            desc=f"{title}: " + by,
            text="\n".join(body),
        )
        links.append((path, title))
        folders_.add(f)
    return links, folders_


def list_page(out, path, title, desc, items, lang="hy"):
    """A page that is a list of links: items is
    [(href, label)]; its path is the page's."""
    esc = htm.escape
    li = "".join(
        f'<li><a href="{esc(h)}">{named(esc(t))}</a></li>\n'
        for h, t in items
    )
    route_page(
        out,
        path,
        lang=lang,
        title=title,
        desc=desc,
        text=f"<p>{esc(desc)}</p>\n<ul>\n{li}</ul>",
    )
    return path, title


def cards_page(out, app):
    """hy/reference/: the Reference page, each book with
    its name, author, time of writing and first
    paragraph, in Armenian. Returns (path, title)."""
    esc = htm.escape
    body = []
    for c in web.book_cards(app, "hy")["books"]:
        to = "hy/" + c["to"].removeprefix("#/")
        who = " · ".join(p["name"] for p in c["authors"])
        body.append(
            f'<h2><a href="/{esc(to)}/">'
            f"{esc(c['name'])}</a></h2>\n"
            f"<p>{esc(who)} · {esc(c['written'])}"
            f" · {esc(c['kind'])}</p>\n"
            f"<p>{esc(c['lead'])}</p>"
        )
    title = "Տեղեկատու · Reference"
    route_page(
        out,
        "hy/reference",
        title=title,
        desc="Every Grabar book of nxGir on a card:"
        " what it is, who wrote it and when.",
        text="\n".join(body),
    )
    return "hy/reference", title


def author_page(out, app, author, books, ids, names):
    """hy/library/<id>/: an author with the card about
    them (authors/), in each language it has, and
    their books (HTML list items). Returns (path,
    title)."""
    esc = htm.escape
    aid = author["folder"].rpartition("/")[2]
    body = []
    title = all_names(names, aid, author["name"])
    if aid in ids:
        card = web.author(app, aid)["versions"]
        for v in card:
            head = " · ".join(
                esc(x) for x in (v["years"], v["role"]) if x
            )
            body.append(
                f'<div lang="{v["lang"]}">\n'
                f"<p><b>{esc(v['name'])}</b>"
                f"{' · ' + head if head else ''}</p>\n"
                + "\n".join(
                    f"<p>{esc(t)}</p>" for t in v["text"]
                )
                + "\n</div>"
            )
    body.append("<ul>\n" + "".join(books) + "</ul>")
    path = f"hy/library/{aid}"
    route_page(
        out,
        path,
        title=title,
        desc=f"{title}: "
        + describe(
            [""] + (card[0]["text"] if aid in ids else [])
        ),
        text="\n".join(body),
    )
    return path, title


def hub_pages(out, app, dirs):
    """The lists: hy/library/ (the authors and their
    books), hy/b/<folder>/ (volume_pages()), and in
    each language <lang>/blog/, <lang>/comics/,
    <lang>/timeline/ and <lang>/about/. Returns
    [(path, title)]."""
    esc = htm.escape
    info = web.authors(app)
    ids, names = info["authors"], info["names"]
    more, volumes = volume_pages(out, app, dirs, names)
    body = []
    for a in web.library(app)["authors"]:
        books = []
        for b in a["books"]:
            f = "grabar/" + b["id"]
            to = (
                f"hy/b/{f}"
                if f in volumes
                else page_path(b["first"])
            )
            books.append(
                f'<li><a href="/{esc(to)}/">'
                f"{esc(b['title'])}</a></li>\n"
            )
        body.append(
            "<h2>"
            + esc(
                all_names(
                    names,
                    a["folder"].rpartition("/")[2],
                    a["name"],
                )
            )
            + "</h2>\n<ul>\n"
            + "".join(books)
            + "</ul>"
        )
        more.append(
            author_page(out, app, a, books, ids, names)
        )
    route_page(
        out,
        "hy/library",
        title="Գրադարան · Library of Grabar books",
        desc="Grabar (Classical Armenian) books, by"
        " author, with Modern Armenian translations.",
        text="<p>Grabar (Classical Armenian) books,"
        " by author, with Modern Armenian"
        " translations.</p>\n" + "\n".join(body),
    )
    links = [("hy/library", "Library")] + more
    links.append(cards_page(out, app))
    for kind, posts in (
        ("blog", web.blog(app)["posts"]),
        ("comics", web.comics(app)["series"]),
    ):
        for lang in LANGS:
            title, desc = LISTS[kind][lang]
            items = []
            for p in posts:
                v = next(
                    (
                        x
                        for x in p["versions"]
                        if x["lang"] == lang
                    ),
                    p["versions"][0],
                )
                items.append(
                    (
                        "/"
                        + post_page(
                            p["slug"], v["lang"], kind
                        )
                        + "/",
                        v["title"],
                    )
                )
            if items:
                links.append(
                    list_page(
                        out,
                        f"{lang}/{kind}",
                        title,
                        desc,
                        items,
                        lang=lang,
                    )
                )
    events = web.timeline(app)["events"]
    li = "".join(
        f'<li><time datetime="{e["date"]}">'
        f"{e['date']}</time> "
        f"<b>{named(esc(e['title']))}</b>: "
        f"{named(esc(e['text']))}</li>\n"
        for e in events
    )
    # the events are in English (timeline.tsv)
    for lang in LANGS:
        title, desc = LISTS["timeline"][lang]
        route_page(
            out,
            f"{lang}/timeline",
            lang=lang,
            title=title,
            desc=desc,
            text=f'<ul lang="en">\n{li}</ul>',
        )
        links.append((f"{lang}/timeline", title))
    for lang in LANGS:
        title, desc = LISTS["about"][lang]
        route_page(
            out,
            f"{lang}/about",
            lang=lang,
            title=title,
            desc=desc,
            text=f"<p>{esc(desc)}</p>",
        )
        links.append((f"{lang}/about", title))
    return links


def searchable(out, app, files, dirs=()):
    """What search engines need to find the pages:
    the paths of app.js are all the one top page to
    them, so each page that should be listed is also
    a file of its own with its words (route_page()):
    the top page in each language (home_pages()),
    each book (hy/read/<book>/) with its text, the lists
    (hub_pages()), the blog posts (post_pages()),
    with their dates, the Features page
    (feature_pages()) and the Map (map_pages()). They
    are listed in sitemap.xml, which robots.txt names,
    and linked from index.html for browsers without
    JavaScript. 404.html is the plain app: GitHub
    Pages gives it for every other path, and app.js
    reads the address."""
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
        lic, text = licensed(web.credit(app, name), text)
        route_page(
            out,
            path,
            title=title,
            desc=describe(lines),
            text=text,
            alt=lic,
        )
        links.append((path, title))
    links += home_pages(out)
    links += hub_pages(out, app, dirs)
    posts = post_pages(out, app)
    posts += post_pages(out, app, comics=True)
    links += feature_pages(out, app)
    more, dated = map_pages(out, app)
    links += more
    posts += dated
    urls = [(SITE + "/", "")]
    urls += [(route_url(p), "") for p, _ in links]
    urls += [(route_url(p), d) for p, _, d in posts]
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
    (out / "404.html").write_text(html, "utf-8")
    # the list goes in main, after its own words
    tag = "</main>"
    if html.count(tag) != 1:
        raise SystemExit("index.html: no main")
    nav = "".join(
        f'<li><a href="/{esc(p)}/">{esc(t)}</a></li>\n'
        for p, t in links
    )
    html = html.replace(
        tag,
        "<noscript><ul>\n"
        + nav
        + "</ul></noscript>\n"
        + tag,
    )
    canon = (
        f'<link rel="canonical" href="{SITE}/">\n'
        + home_alt()
    )
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
    zip_site = "--zip" in argv
    argv = [a for a in argv if a != "--zip"]
    out = Path(argv[0]) if argv else ROOT / "site"
    books, dirs, words = build(
        out, shelf_files(), zip_site=zip_site
    )
    print(
        f"{out}: {books} books, {dirs} folders,"
        f" {words} words, {size(out)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
