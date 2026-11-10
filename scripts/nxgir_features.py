"""The Features page of nx-gir: what the site can
do, in features/, one Markdown file per language,
features.LANG.md (see features/README.md). The
format is a blog post's (nxgir_blog.parse()): a
"# Title" line, then paragraphs; "## " starts a
feature. Drafts are in features/drafts/, which is
not read. Tested in tests/test_features.py.
"""

import re
from pathlib import Path

import nxgir_blog as blog

ROOT = Path(__file__).resolve().parent.parent
FEATURES = ROOT / "features"
NAME_RE = re.compile(r"features\.([a-z]{2})\.md")


def read(folder=FEATURES):
    """The page in each language, in the order of
    blog.LANGS: [{lang, title, blocks}]. A bad file
    stops it (blog.BlogError), so a mistake shows
    when the site is built."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    out = []
    for p in sorted(folder.glob("*.md")):
        if p.name == "README.md":
            continue
        m = NAME_RE.fullmatch(p.name)
        if not m:
            raise blog.BlogError(
                f"{p.name}: not features.LANG.md"
            )
        lang = m.group(1)
        if lang not in blog.LANGS:
            raise blog.BlogError(
                f"{p.name}: language not in {blog.LANGS}"
            )
        text = p.read_text(encoding="utf-8")
        title, blocks = blog.parse(text, p.name)
        out.append(
            {"lang": lang, "title": title, "blocks": blocks}
        )
    out.sort(key=lambda v: blog.LANGS.index(v["lang"]))
    return out
