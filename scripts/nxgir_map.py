"""The map of nx-gir: map/places.tsv, the places (see
the head of that file), and where each stands on the
painted map, web/img/map/base.webp.

The picture is painted at an angle and its lakes and
mountains are not to scale, so latitude and longitude
only give a rough place: project() fits a plane to
landmarks of the picture, CONTROL. A place gives its
own x and y to stand on the painted tower or peak it
means; every place on the map should.

read() checks every line and stops on a bad one, so a
mistake shows when the site is built. Tested in
tests/test_map.py.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACES = ROOT / "map" / "places.tsv"
IMAGE = ROOT / "web" / "img" / "map" / "base.webp"

KINDS = (
    "city",
    "fortress",
    "monastery",
    "region",
    "lake",
    "mountain",
)
FIELDS = (
    "id",
    "kind",
    "lat",
    "lon",
    "x",
    "y",
    "hy",
    "en",
    "ru",
    "note",
)
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# the area the picture shows: south, north, west, east
BOUNDS = (36.5, 42.5, 38.0, 49.5)
# landmarks of the picture: lat, lon, and where each
# stands in it, x and y in percent
CONTROL = (
    (39.70, 44.30, 52.4, 37.5),  # Mount Masis
    (40.30, 45.30, 60.2, 30.3),  # Lake Sevan
    (37.70, 45.50, 61.8, 86.0),  # Lake Urmia
    (38.50, 43.38, 54.7, 70.3),  # Van
    (39.90, 41.27, 10.1, 59.6),  # Karin
    (38.40, 42.11, 25.1, 71.8),  # Baghesh
    (38.34, 43.03, 44.9, 69.8),  # Aghtamar
)
# how far a place projected from lat and lon may be
# from the painted one: the picture is art, not a
# projection, so a place that matters gets its own x, y
TOLERANCE = 13.0


class MapError(ValueError):
    pass


def solve(a, b):
    """x in a x = b, a square matrix (lists)."""
    n = len(a)
    a = [row[:] + [b[i]] for i, row in enumerate(a)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[p][i]) < 1e-12:
            raise MapError("the landmarks are in a line")
        a[i], a[p] = a[p], a[i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            for c in range(i, n + 1):
                a[r][c] -= f * a[i][c]
    x = [0.0] * n
    for i in reversed(range(n)):
        s = sum(a[i][c] * x[c] for c in range(i + 1, n))
        x[i] = (a[i][n] - s) / a[i][i]
    return x


def fit(points):
    """The two rows (a, b, c) of the affine map, least
    squares: x = a*lon + b*lat + c, and y the same."""
    rows = [(lon, lat, 1.0) for lat, lon, _, _ in points]
    gram = [
        [sum(r[i] * r[j] for r in rows) for j in range(3)]
        for i in range(3)
    ]
    out = []
    for k in (2, 3):
        rhs = [
            sum(r[i] * p[k] for r, p in zip(rows, points))
            for i in range(3)
        ]
        out.append(solve(gram, rhs))
    return out


MATRIX = fit(CONTROL)


def project(lat, lon, matrix=MATRIX):
    """The rough x and y, in percent of the picture,
    of a place at lat and lon."""
    (a, b, c), (d, e, f) = matrix
    return (
        round(a * lon + b * lat + c, 1),
        round(d * lon + e * lat + f, 1),
    )


def parse(line, n):
    """One line of places.tsv as a place."""
    parts = line.split("\t")
    if len(parts) != len(FIELDS):
        raise MapError(
            f"line {n}: {len(parts)} fields,"
            f" not {len(FIELDS)}"
        )
    p = dict(zip(FIELDS, (s.strip() for s in parts)))
    if not ID_RE.fullmatch(p["id"]):
        raise MapError(f"line {n}: bad id {p['id']!r}")
    if p["kind"] not in KINDS:
        raise MapError(
            f"line {n}: unknown kind {p['kind']!r}"
        )
    for f in ("lat", "lon", "x", "y"):
        if p[f] == "" and f in ("x", "y"):
            p[f] = None
            continue
        try:
            p[f] = float(p[f])
        except ValueError:
            raise MapError(
                f"line {n}: {f} is not a number"
            ) from None
    if (p["x"] is None) != (p["y"] is None):
        raise MapError(f"line {n}: x and y go together")
    for f in ("hy", "en", "ru"):
        if not p[f]:
            raise MapError(f"line {n}: no {f} name")
    return p


def read(path=PLACES):
    """The places of path, in the order of the file,
    each with "x" and "y" filled in: its own, or
    projected from lat and lon. Raises MapError on a
    bad line, a repeated id or a place outside the
    picture."""
    places, seen = [], set()
    text = Path(path).read_text(encoding="utf-8")
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        p = parse(line, n)
        if p["id"] in seen:
            raise MapError(f"line {n}: {p['id']} twice")
        seen.add(p["id"])
        south, north, west, east = BOUNDS
        if not (
            south <= p["lat"] <= north
            and west <= p["lon"] <= east
        ):
            raise MapError(
                f"line {n}: {p['id']} is off the map"
            )
        p["pinned"] = p["x"] is not None
        if not p["pinned"]:
            p["x"], p["y"] = project(p["lat"], p["lon"])
        if not (0 <= p["x"] <= 100 and 0 <= p["y"] <= 100):
            raise MapError(
                f"line {n}: {p['id']} is off the picture"
            )
        places.append(p)
    return places


# the longest lead on a card, in characters
LEAD = 220


def lead(blocks):
    """The first paragraph of a post, cut at a word
    when it is longer than LEAD."""
    for kind, text, *_ in blocks:
        if kind != "p":
            continue
        if len(text) <= LEAD:
            return text
        cut = text[:LEAD].rsplit(" ", 1)[0]
        return cut.rstrip(",;:։՝ ") + "…"
    return ""


def story(item, kind):
    """A post or a comics series as the map shows it:
    {type, slug, date, versions: [{lang, title, lead,
    cover, alt}]}; cover is the file of its first
    picture, in web/img/, or empty."""
    versions = []
    for v in item["versions"]:
        pic = next(
            (b for b in v["blocks"] if b[0] == "img"), None
        )
        versions.append(
            {
                "lang": v["lang"],
                "title": v["title"],
                "lead": lead(v["blocks"]),
                "cover": pic[1] if pic else "",
                "alt": pic[2] if pic else "",
            }
        )
    return {
        "type": kind,
        "slug": item["slug"],
        "date": item["date"],
        "versions": versions,
    }


def build(places, blog=(), comics=()):
    """The answer of /api/map: the picture, and each
    place with its names and the stories (posts and
    comics series, newest first) that name it. A post
    naming a place not in places raises MapError."""
    known = {p["id"] for p in places}
    found = {p["id"]: [] for p in places}
    for kind, items in (("blog", blog), ("comics", comics)):
        for item in items:
            for pid in item.get("places", []):
                if pid not in known:
                    raise MapError(
                        f"{item['slug']}: no place {pid!r}"
                    )
                found[pid].append(story(item, kind))
    out = []
    for p in places:
        found[p["id"]].sort(
            key=lambda s: s["date"], reverse=True
        )
        out.append(
            {
                "id": p["id"],
                "kind": p["kind"],
                "x": p["x"],
                "y": p["y"],
                "lat": p["lat"],
                "lon": p["lon"],
                "names": {
                    k: p[k] for k in ("hy", "en", "ru")
                },
                "stories": found[p["id"]],
            }
        )
    return {
        "image": "img/map/" + IMAGE.name,
        "kinds": list(KINDS),
        "places": out,
    }
