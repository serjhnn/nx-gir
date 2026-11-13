"""The blog of nx-gir: blog/, one Markdown file per
post and language, named YYYY-MM-DD-slug.LANG.md
(see blog/README.md); the versions of a post share
its date and slug.
Drafts are in blog/drafts/, which is not read.

A post is a "# Title" line, then paragraphs split
by empty lines; "## " starts a subheading; a line
![alt](name.jpg) alone is a picture, a file of
web/img/. read()
checks every file and stops on a bad one, so a
mistake shows when the site is built. Tested in
tests/test_blog.py.
"""

import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
# the languages of the posts, in the order the
# page offers them: Armenian first
LANGS = ("hy", "en", "ru")
NAME_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)"
    r"\.([a-z]{2})\.md"
)


IMG_RE = re.compile(
    r"!\[([^\]]*)\]\(([A-Za-z0-9_-]+\.(?:jpg|png|webp))\)"
)


class BlogError(ValueError):
    pass


def parse(text, name):
    """The title and blocks of a post: blocks are
    ["p", text], ["h", text] and ["img", file, alt],
    a paragraph's lines joined by spaces."""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines or not lines[0].startswith("# "):
        raise BlogError(f"{name}: no # title first")
    title = lines[0][2:].strip()
    blocks, para = [], []

    def end():
        if para:
            blocks.append(["p", " ".join(para)])
            para.clear()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            end()
        elif IMG_RE.fullmatch(line):
            end()
            alt, src = IMG_RE.fullmatch(line).groups()
            blocks.append(["img", src, alt])
        elif line.startswith("## "):
            end()
            blocks.append(["h", line[3:].strip()])
        else:
            para.append(line)
    end()
    if not title or not blocks:
        raise BlogError(f"{name}: no title or text")
    return title, blocks


def read(folder=BLOG):
    """The posts in folder, newest first, as {slug,
    date, versions}: versions [{lang, title,
    blocks}] in the order of LANGS. Files other
    than *.md (and README.md) are left alone."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    posts = {}
    for p in sorted(folder.glob("*.md")):
        if p.name == "README.md":
            continue
        m = NAME_RE.fullmatch(p.name)
        if not m:
            raise BlogError(
                f"{p.name}: not YYYY-MM-DD-slug.LANG.md"
            )
        date, slug, lang = m.groups()
        if lang not in LANGS:
            raise BlogError(
                f"{p.name}: language not in {LANGS}"
            )
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            raise BlogError(
                f"{p.name}: bad date {date!r}"
            ) from None
        post = posts.setdefault(
            slug, {"slug": slug, "date": date}
        )
        if post["date"] != date:
            raise BlogError(
                f"{p.name}: two dates for {slug!r}"
            )
        text = p.read_text(encoding="utf-8")
        title, blocks = parse(text, p.name)
        post.setdefault("versions", []).append(
            {"lang": lang, "title": title, "blocks": blocks}
        )
    out = sorted(
        posts.values(),
        key=lambda p: p["date"],
        reverse=True,
    )
    for post in out:
        post["versions"].sort(
            key=lambda v: LANGS.index(v["lang"])
        )
    return out
