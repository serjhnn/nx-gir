"""About the authors of the Library: authors/, one
Markdown file per author and language, named
<id>.LANG.md, the id being the author's folder in
books/grabar/ (see authors/README.md). The web
reader shows it in a panel, opened by the scroll
button beside an author's name.

A file is a "# Name" line, then "key: value" lines
(META), then paragraphs split by empty lines:

    years   the years of life, as the language
            writes them
    role    what the author was, a few words
    source  where the facts come from
    place   ids of map/places.tsv, by commas
    post    the slug of a blog post about the author
    face    a picture in web/, the author's face
    status  "machine" (written by Claude, not yet
            read by a person) or "reviewed"

name, years, role and source belong to each
language; place, post, face and status are shared:
one version is enough, and the others must not
differ. read() checks every file and stops on a bad
one. Tested in tests/test_authors.py.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTHORS = ROOT / "authors"
# the languages, in the order the panel offers them
LANGS = ("hy", "en", "ru")
# the fields of each language, and the shared ones
OWN = ("years", "role", "source")
SHARED = ("place", "post", "face", "status")
STATUSES = ("machine", "reviewed")
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAME_RE = re.compile(
    r"([a-z0-9]+(?:-[a-z0-9]+)*)\.([a-z]{2})\.md"
)
META_RE = re.compile(r"([a-z]+): *(.*)")
FACE_RE = re.compile(r"[A-Za-z0-9_-]+\.(?:jpg|png|webp)")


class AuthorError(ValueError):
    pass


def parse(text, name):
    """The name, fields and paragraphs of one file:
    (name, {key: value}, [paragraph])."""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines or not lines[0].startswith("# "):
        raise AuthorError(f"{name}: no # name first")
    title = lines[0][2:].strip()
    meta, paras, para = {}, [], []
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        m = META_RE.fullmatch(line)
        if line and not m:
            break
        if m:
            key, value = m.groups()
            if key not in OWN + SHARED:
                raise AuthorError(
                    f"{name}: unknown field {key!r}"
                )
            if key in meta:
                raise AuthorError(
                    f"{name}: {key!r} given twice"
                )
            meta[key] = value.strip()
        i += 1
    for line in lines[i:]:
        line = line.strip()
        if line:
            para.append(line)
        elif para:
            paras.append(" ".join(para))
            para = []
    if para:
        paras.append(" ".join(para))
    if not title or not paras:
        raise AuthorError(f"{name}: no name or text")
    return title, meta, paras


def shared(meta, name):
    """The shared fields of a file, checked: places
    a list of ids."""
    out = {}
    if "place" in meta:
        ids = [p for p in re.split(r" *, *", meta["place"])]
        for pid in ids:
            if not ID_RE.fullmatch(pid):
                raise AuthorError(
                    f"{name}: bad place {pid!r}"
                )
        out["places"] = ids
    if "post" in meta:
        if not ID_RE.fullmatch(meta["post"]):
            raise AuthorError(f"{name}: bad post slug")
        out["post"] = meta["post"]
    if "face" in meta:
        if not FACE_RE.fullmatch(meta["face"]):
            raise AuthorError(f"{name}: bad face file")
        out["face"] = meta["face"]
    if "status" in meta:
        if meta["status"] not in STATUSES:
            raise AuthorError(
                f"{name}: status not in {STATUSES}"
            )
        out["status"] = meta["status"]
    return out


def read(folder=AUTHORS):
    """The authors written about, by id: {id, places,
    post, face, status, versions}, versions [{lang,
    name, years, role, source, text}] in the order
    of LANGS. README.md is left alone."""
    folder = Path(folder)
    if not folder.is_dir():
        return {}
    out = {}
    for p in sorted(folder.glob("*.md")):
        if p.name == "README.md":
            continue
        m = NAME_RE.fullmatch(p.name)
        if not m:
            raise AuthorError(f"{p.name}: not <id>.LANG.md")
        aid, lang = m.groups()
        if lang not in LANGS:
            raise AuthorError(
                f"{p.name}: language not in {LANGS}"
            )
        text = p.read_text(encoding="utf-8")
        name, meta, paras = parse(text, p.name)
        a = out.setdefault(aid, {"id": aid})
        for key, value in shared(meta, p.name).items():
            if a.setdefault(key, value) != value:
                raise AuthorError(
                    f"{p.name}: {key!r} differs from"
                    " another language"
                )
        a.setdefault("versions", []).append(
            {
                "lang": lang,
                "name": name,
                **{k: meta.get(k, "") for k in OWN},
                "text": paras,
            }
        )
    for a in out.values():
        a.setdefault("places", [])
        a.setdefault("post", None)
        a.setdefault("face", None)
        a.setdefault("status", "machine")
        a["versions"].sort(
            key=lambda v: LANGS.index(v["lang"])
        )
    return out
