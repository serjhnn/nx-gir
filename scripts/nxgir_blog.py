"""The blog of nx-gir: blog/, one Markdown file per
post, named YYYY-MM-DD-slug.md (see
blog/README.md).

A post is a "# Title" line, then paragraphs split
by empty lines; "## " starts a subheading. read()
checks every file and stops on a bad one, so a
mistake shows when the site is built. Tested in
tests/test_blog.py.
"""

import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
NAME_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)"
    r"\.md"
)


class BlogError(ValueError):
    pass


def parse(text, name):
    """The title and blocks of a post: blocks are
    ["p", text] and ["h", text], a paragraph's
    lines joined by spaces."""
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
    """The posts in folder, newest first, as
    {slug, date, title, blocks}. Files other than
    *.md (and README.md) are left alone."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    posts = []
    for p in sorted(folder.glob("*.md")):
        if p.name == "README.md":
            continue
        m = NAME_RE.fullmatch(p.name)
        if not m:
            raise BlogError(
                f"{p.name}: not YYYY-MM-DD-slug.md"
            )
        date, slug = m.groups()
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            raise BlogError(
                f"{p.name}: bad date {date!r}"
            ) from None
        text = p.read_text(encoding="utf-8")
        title, blocks = parse(text, p.name)
        posts.append(
            {
                "slug": slug,
                "date": date,
                "title": title,
                "blocks": blocks,
            }
        )
    slugs = [p["slug"] for p in posts]
    for s in slugs:
        if slugs.count(s) > 1:
            raise BlogError(f"two posts named {s!r}")
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts
