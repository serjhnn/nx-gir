"""The Comics page of nx-gir: comics/, one Markdown
file per series and language, named
YYYY-MM-DD-slug.LANG.md (see comics/README.md). The
format is a blog post's (nxgir_blog.py): the title,
the intro, the pages as pictures with a note under
each, then the explanations. Drafts are in
comics/drafts/, which is not read. Tested in
tests/test_comics.py.
"""

from pathlib import Path

import nxgir_blog as blog

ROOT = Path(__file__).resolve().parent.parent
COMICS = ROOT / "comics"


def read(folder=COMICS):
    """The series in folder, newest first, as
    nxgir_blog.read() gives posts: {slug, date,
    theme, versions}. A bad file stops it
    (blog.BlogError), so a mistake shows when the
    site is built. A series needs a picture in each
    version."""
    series = blog.read(folder)
    for s in series:
        for v in s["versions"]:
            if not any(b[0] == "img" for b in v["blocks"]):
                raise blog.BlogError(
                    f"{s['slug']}.{v['lang']}: no pages"
                )
    return series
