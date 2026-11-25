"""Glakavank, the monastery of Karapet above the plain
of Mush (Taron), as it stood in 1893: a model built
in Blender, by script.

    blender -b --factory-startup -P blender/glakavank.py \\
        -- [--quick] [--no-render] [--glb] [--web]

Writes blender/out/glakavank.blend, renders of the
views of the old photographs (blender/out/*.jpg) and,
with --glb, blender/out/glakavank.glb for the web.

The same sources and sizes as web/models/glakavank.js
(the plan after Hewsen, Lynch's photographs of 1893,
the photographs before 1915 and the text on Nune
Movsisyan's page; copies in sources/glakavank/), but
built as a modeller would: openings cut into solid
walls, worn edges, carvings in relief, stone from
photographs (Poly Haven, CC0).

Here x is east, y north, z up; metres. An angle rz
says where a face looks: 0 north, pi/2 east.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib as L  # noqa: E402

OUT = L.ROOT / "out"
PI = math.pi
ARGS = (
    sys.argv[sys.argv.index("--") + 1 :]
    if "--" in sys.argv
    else []
)
QUICK = "--quick" in ARGS


def materials():
    res = "1k" if QUICK else "2k"
    # dressed grey stone in long courses, as on the
    # hall and the porch in the photographs
    L.material(
        "ashlar",
        "large_sandstone_blocks",
        5.0,
        (1.0, 0.97, 0.92),
        res,
    )
    L.material(
        "porch",
        "large_sandstone_blocks",
        5.0,
        (1.18, 1.13, 1.05),
        res,
    )
    L.material(
        "basalt",
        "large_sandstone_blocks",
        5.0,
        (0.42, 0.4, 0.38),
        res,
    )
    L.material("marble", "marble_01", 1.6, None, res)
    L.material(
        "rubble", "castle_wall_varriation", 4.0, None, res
    )
    L.material(
        "slate",
        "roof_slates_02",
        2.6,
        (0.8, 0.8, 0.8),
        res,
    )
    L.material(
        "court", "cobblestone_floor_04", 3.5, None, res
    )
    L.material(
        "ground",
        "withered_grass",
        6.0,
        (0.62, 0.56, 0.42),
        res,
    )
    L.material("earth", "aerial_grass_rock", 9.0, None, res)
    L.plain("hole", (0.015, 0.013, 0.012), 1.0)
    L.plain("wood", (0.22, 0.13, 0.07), 0.7)
    L.plain("clay", (0.34, 0.2, 0.12), 0.85)
    L.plain("iron", (0.05, 0.05, 0.05), 0.5, 0.6)
    L.plain("bronze", (0.45, 0.32, 0.13), 0.35, 1.0)
    L.plain("leaf", (0.1, 0.12, 0.04), 0.9)
    L.plain("bark", (0.16, 0.12, 0.09), 0.9)


class Holes:
    """Openings to cut: gathered, then cut at once."""

    def __init__(self, name):
        self.name = name
        self.items = []

    def add(self, pts, depth, place):
        self.items.append((pts, depth, place))

    def cut(self, *targets):
        if not self.items:
            return
        c = L.prisms(self.name + "-cut", self.items)
        for t in targets:
            L.cut(t, [c])


def n_of(rz):
    return Vector((math.sin(rz), math.cos(rz), 0))


def outline(w, h, shape):
    """An opening: shape "rect", True (pointed) or
    False (round)."""
    if shape == "rect":
        return [
            (-w / 2, 0),
            (w / 2, 0),
            (w / 2, h),
            (-w / 2, h),
        ]
    return L.arch(w, h, shape)


def grille(x, y, z, rz, w, h, deep=0.2):
    """Iron bars across a window, set in from the
    face."""
    n = n_of(rz)
    t = Vector((n.y, -n.x, 0))
    c = Vector((x, y, z)) - n * deep
    k = max(2, round(w / 0.14))
    for i in range(1, k):
        p = c + t * (-w / 2 + w * i / k)
        rod("bar", p, p + Vector((0, 0, h)), 0.015, "iron")
    for j in (0.33, 0.66):
        a = c - t * w / 2 + Vector((0, 0, h * j))
        rod("bar", a, a + t * w, 0.015, "iron")


def plaque(x, y, z, rz, w=0.6, h=0.8):
    """A carved slab set in a wall, a cross in
    relief on it, as over the hall's windows."""
    n = n_of(rz)
    p = Vector((x, y, z)) + n * 0.04
    L.box("plaque", w, 0.08, h, "porch", p.x, p.y, z, -rz)
    f = Vector((x, y, z)) + n * 0.09
    a, b = 0.05, 0.22 * min(w, h) / 0.6
    pts = [
        (-a, 0.1),
        (a, 0.1),
        (a, h / 2 - a),
        (b, h / 2 - a),
        (b, h / 2 + a),
        (a, h / 2 + a),
        (a, h - 0.12),
        (-a, h - 0.12),
        (-a, h / 2 + a),
        (-b, h / 2 + a),
        (-b, h / 2 - a),
        (-a, h / 2 - a),
    ]
    L.prism(
        "plaque-cross",
        pts,
        0.04,
        "porch",
        L.face(f.x, f.y, z, rz),
    )


def window(
    holes,
    x,
    y,
    z,
    rz,
    w,
    h,
    pointed=False,
    deep=0.45,
    frame="porch",
):
    """A window w by h, its sill at z, in the face at
    x, y that looks to rz: cut deep into the wall, a
    dark back, a frame of dressed stone, a sill."""
    n = n_of(rz)
    pts = outline(w, h, pointed)
    holes.add(pts, deep * 2, L.face(x, y, z, rz))
    b = Vector((x, y, z)) - n * (deep - 0.02)
    L.box("win-back", w, 0.02, h, "hole", b.x, b.y, z, -rz)
    if frame:
        f = Vector((x, y, z - 0.12)) + n * 0.06
        fr = L.prism(
            "frame",
            outline(w + 0.38, h + 0.3, pointed),
            0.12,
            frame,
            L.face(f.x, f.y, f.z, rz),
        )
        s = Vector((x, y, z - 0.18)) + n * 0.12
        L.box(
            "sill",
            w + 0.6,
            0.26,
            0.16,
            frame,
            s.x,
            s.y,
            s.z,
            -rz,
        )
        return fr
    return None


def checker(outline, z, rows=2, size=0.8, out=0.03):
    """A band of light and dark stones in turn round
    a convex outline (the foot of the walls)."""
    k = len(outline)
    for i in range(k):
        a = Vector(outline[i])
        b = Vector(outline[(i + 1) % k])
        d = b - a
        ln = d.length
        nb = max(1, round(ln / size))
        step = ln / nb
        t = d / ln
        n = Vector((t.y, -t.x))
        rz = math.atan2(n.x, n.y)
        for r in range(rows):
            for j in range(nb):
                c = a + t * (step * (j + 0.5)) + n * out
                mat = "basalt" if (j + r) % 2 else "porch"
                L.box(
                    "chk",
                    step - 0.02,
                    0.12,
                    size - 0.02,
                    mat,
                    c.x,
                    c.y,
                    z + r * size,
                    -rz,
                )


def rod(name, a, b, r, mat, sides=4):
    a = Vector(a)
    b = Vector(b)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=sides,
        radius1=r,
        radius2=r,
        depth=d.length,
    )
    q = d.to_track_quat("Z", "Y")
    m = (
        Matrix.Translation((a + b) / 2)
        @ q.to_matrix().to_4x4()
    )
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return L.obj(name, bm, mat)


def spire(name, x, y, z, r, h, n, cross=True, ribs=True):
    """A cone of n sides of stone slabs, a rib on each
    edge (unless not ribs), a ball and a cross."""
    L.lathe(
        name,
        [(r + 0.15, -0.2), (r + 0.15, 0), (r, 0), (0, h)],
        n,
        "slate",
        x,
        y,
        z,
    )
    for i in range(n if ribs else 0):
        a = 2 * PI * i / n
        rod(
            name + "-rib",
            (x + r * math.sin(a), y + r * math.cos(a), z),
            (x, y, z + h),
            0.07,
            "slate",
        )
    if cross:
        L.lathe(
            name + "-ball",
            [
                (0.0, 0),
                (0.18, 0.08),
                (0.24, 0.25),
                (0.18, 0.42),
                (0.0, 0.5),
            ],
            12,
            "bronze",
            x,
            y,
            z + h - 0.1,
        )
        L.box(
            "cross",
            0.1,
            0.1,
            1.3,
            "bronze",
            x,
            y,
            z + h + 0.3,
        )
        L.box(
            "cross",
            0.65,
            0.1,
            0.1,
            "bronze",
            x,
            y,
            z + h + 1.15,
        )


def column(name, x, y, z, h, r, mat="marble"):
    """A column with a base and a capital."""
    L.lathe(
        name,
        [
            (r * 1.6, 0),
            (r * 1.6, 0.12),
            (r * 1.25, 0.22),
            (r, 0.3),
            (r, h - 0.35),
            (r * 1.2, h - 0.28),
            (r * 1.7, h - 0.1),
            (r * 1.7, h),
        ],
        12,
        mat,
        x,
        y,
        z,
    )


def rosette(x, y, z, rz, r=0.5, mat="marble"):
    """A carved rosette on a face: a ring, twelve
    petals, a boss."""
    place = L.face(x, y, z, rz)
    n = n_of(rz)
    items = []
    ring = [
        (
            r * math.cos(2 * PI * i / 24),
            r * math.sin(2 * PI * i / 24),
        )
        for i in range(24)
    ]
    L.prism(
        "ros-disc",
        ring,
        0.05,
        mat,
        L.face(*(Vector((x, y, z)) + n * 0.025), rz),
    )
    for i in range(12):
        a = 2 * PI * i / 12
        lens = []
        for j in range(5):
            t = PI * j / 4
            lens.append(
                (
                    0.1 + 0.32 * r * (1 - math.cos(t)),
                    0.09 * r * math.sin(t),
                )
            )
        lens += [(u, -v) for u, v in reversed(lens[1:-1])]
        rot = Matrix.Rotation(a, 4, "Y")
        items.append(
            (
                lens,
                0.05,
                place
                @ Matrix.Translation((0, 0.06, 0))
                @ rot,
            )
        )
    items.append(
        (
            [
                (
                    0.12 * r * math.cos(2 * PI * i / 12),
                    0.12 * r * math.sin(2 * PI * i / 12),
                )
                for i in range(12)
            ],
            0.08,
            place @ Matrix.Translation((0, 0.07, 0)),
        )
    )
    L.prisms("ros-petals", items, mat)


def cross_stone(x, y, rz):
    """A cross-stone (khachkar): a slab on a plinth, a
    cross with split ends and a rosette in relief, a
    frame, a little roof."""
    n = n_of(rz)
    L.box(
        "kh-plinth", 1.5, 0.7, 0.5, "ashlar", x, y, 0, -rz
    )
    L.box(
        "kh-slab", 1.1, 0.22, 2.0, "ashlar", x, y, 0.5, -rz
    )
    L.box(
        "kh-roof", 1.3, 0.38, 0.22, "ashlar", x, y, 2.5, -rz
    )
    f = Vector((x, y, 0)) + n * 0.11
    place = L.face(f.x, f.y, 0.5, rz)
    s = 0.07
    cross = [
        (-s, 0.5),
        (s, 0.5),
        (s, 1.05),
        (0.3, 1.05),
        (0.36, 1.17),
        (0.3, 1.25),
        (s, 1.25),
        (s, 1.6),
        (0.1, 1.72),
        (0, 1.8),
        (-0.1, 1.72),
        (-s, 1.6),
        (-s, 1.25),
        (-0.3, 1.25),
        (-0.36, 1.17),
        (-0.3, 1.05),
        (-s, 1.05),
    ]
    items = [(cross, 0.06, place)]
    fr = [
        (-0.5, 0.05),
        (0.5, 0.05),
        (0.5, 1.95),
        (-0.5, 1.95),
    ]
    inner = [
        (-0.42, 0.13),
        (0.42, 0.13),
        (0.42, 1.87),
        (-0.42, 1.87),
    ]
    for i in range(4):
        a, b = fr[i], fr[(i + 1) % 4]
        c, d = inner[(i + 1) % 4], inner[i]
        items.append(([a, b, c, d], 0.05, place))
    L.prisms("kh-relief", items, "ashlar")
    rosette(f.x, f.y, 0.5 + 0.28, rz, 0.16, "ashlar")


def tree(kind, x, y, z, h, seed):
    import random

    r = random.Random(seed)
    L.lathe(
        "trunk",
        [(h * 0.03, 0), (h * 0.02, h * 0.5)],
        7,
        "bark",
        x,
        y,
        z,
    )
    bm = bmesh.new()

    def clump(cx, cy, cz, sx, sz):
        ret = bmesh.ops.create_icosphere(
            bm, subdivisions=2, radius=1
        )
        vs = ret["verts"]
        for v in vs:
            k = 0.8 + r.random() * 0.35
            v.co = Vector(
                (
                    v.co.x * sx * k + cx,
                    v.co.y * sx * k + cy,
                    v.co.z * sz * k + cz,
                )
            )

    if kind == "poplar":
        for i in range(7):
            t = i / 6
            w = h * (0.12 - t * 0.06)
            clump(
                x + (r.random() - 0.5) * w * 0.4,
                y + (r.random() - 0.5) * w * 0.4,
                z + h * (0.28 + t * 0.64),
                w,
                h * 0.12,
            )
    else:
        clump(x, y, z + h * 0.68, h * 0.3, h * 0.24)
        for i in range(7):
            a = i * 2 * PI / 7 + r.random()
            d = h * (0.22 + r.random() * 0.08)
            clump(
                x + math.sin(a) * d,
                y + math.cos(a) * d,
                z + h * (0.5 + r.random() * 0.2),
                h * 0.2,
                h * 0.17,
            )
    o = L.obj("crown", bm, "leaf", "round")
    return o


# -- the ground --


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def wave(x, s):
    # s: to the south, as in web/models/glakavank.js
    return (
        math.sin(x * 0.021 + 1.3) * math.cos(s * 0.017)
        + 0.5 * math.sin(x * 0.057 - s * 0.043)
        + 0.25 * math.sin(x * 0.13 + s * 0.11)
    )


def height(x, y):
    """The same ground as the web page's (z there is
    south, so -y here)."""
    z = -y
    flat = (
        smoothstep(-95, -70, x)
        * (1 - smoothstep(50, 75, x))
        * smoothstep(-62, -45, z)
        * (1 - smoothstep(68, 80, z))
    )
    n = max(0.0, -z - 45)
    h = n * 0.42 + n * n * 0.0011
    h += wave(x * 0.2, z * 0.2) * n * 0.12
    s = max(0.0, z - 52)
    q = s / 8
    f = q - math.floor(q)
    riser = 0 if f < 0.75 else (f - 0.75) / 0.25
    h -= (math.floor(q) + riser) * 8 * 0.3
    h -= max(0.0, -x - 90) * 0.12
    h += wave(x, z) * (3 + n * 0.08 + s * 0.02)
    h = h * (1 - flat) - 0.02 * flat
    fall = smoothstep(230, 650, z)
    plain = -560 + wave(x * 0.2, z * 0.2) * 8
    h = h * (1 - fall) + plain * fall
    far = smoothstep(1050, 1300, z)
    h += far * (420 + wave(x * 0.08, z * 0.08) * 160)
    return h


def ground():
    bm = bmesh.new()
    size = 2400 if not QUICK else 1200
    seg = 300 if not QUICK else 150
    bmesh.ops.create_grid(
        bm, x_segments=seg, y_segments=seg, size=size / 2
    )
    for v in bm.verts:
        v.co.z = height(v.co.x, v.co.y)
    o = L.obj("ground", bm, "ground")
    L.smooth(o, 60)
    import random

    r = random.Random(77)
    bm = bmesh.new()
    k = 0
    while k < (700 if not QUICK else 250):
        x = (r.random() - 0.5) * 520
        y = (r.random() - 0.5) * 520
        if -100 < x < 60 and -70 < y < 55:
            continue
        if y < -70 and r.random() < 0.75:
            continue
        s = 0.6 + r.random() * 1.2
        ret = bmesh.ops.create_icosphere(
            bm, subdivisions=1, radius=1
        )
        for v in ret["verts"]:
            j = 0.75 + r.random() * 0.5
            v.co = Vector(
                (
                    x + v.co.x * s * j * 1.3,
                    y + v.co.y * s * j * 1.3,
                    height(x, y)
                    + s * 0.35
                    + v.co.z * s * 0.8 * j,
                )
            )
        k += 1
    L.obj("scrub", bm, "leaf", "round")


# -- the church --


def band(a, b, z, h, mat, out=0.04, gaps=()):
    """A course of stone h high at z along a wall from
    a to b (x, y), standing out by out; gaps
    [(t0, t1), ...] (0 to 1 along it) left out."""
    a, b = Vector(a), Vector(b)
    d = b - a
    t = d.normalized()
    n = Vector((-t.y, t.x))
    rz = math.atan2(n.x, n.y)
    spans, t0 = [], 0.0
    for g0, g1 in sorted(gaps):
        spans.append((t0, g0))
        t0 = g1
    spans.append((t0, 1.0))
    for u0, u1 in spans:
        if u1 - u0 < 0.01:
            continue
        c = a + d * ((u0 + u1) / 2) + n * (out / 2)
        L.box(
            "course",
            d.length * (u1 - u0),
            0.1 + out,
            h,
            mat,
            c.x,
            c.y,
            z,
            -rz,
        )


def diamonds(a, b, z, h):
    """The band of light lozenges on dark stone at the
    foot of the hall's west front."""
    a, b = Vector(a), Vector(b)
    d = b - a
    t = d.normalized()
    n = Vector((-t.y, t.x))
    rz = math.atan2(n.x, n.y)
    band(a, b, z, h, "basalt", 0.08)
    k = max(1, round(d.length / (h * 0.9)))
    step = d.length / k
    q = h * 0.42
    items = []
    for i in range(k):
        c = a + t * (step * (i + 0.5)) + n * 0.15
        items.append(
            (
                [(0, -q), (q, 0), (0, q), (-q, 0)],
                0.06,
                L.face(c.x, c.y, z + h / 2, rz),
            )
        )
    L.prisms("lozenges", items, "porch")


def mottle(a, b, z0, z1, k, seed):
    """Dark stones scattered in a wall from a to b,
    between z0 and z1, as on the hall."""
    import random

    r = random.Random(seed)
    a, b = Vector(a), Vector(b)
    d = b - a
    t = d.normalized()
    n = Vector((-t.y, t.x))
    rz = math.atan2(n.x, n.y)
    for _ in range(k):
        c = a + d * r.uniform(0.03, 0.97) + n * 0.015
        L.box(
            "dark-stone",
            r.choice((0.8, 1.1, 1.4, 1.7)),
            0.04,
            0.45,
            "basalt",
            c.x,
            c.y,
            z0 + 0.5 * r.randrange(int((z1 - z0) / 0.5)),
            -rz,
        )


def church():
    """The hall, after the photographs from the
    south-west: few windows, set as they came (small
    rectangles with iron bars, two in framed panels
    with a carved slab over them, a tall narrow
    arched one to the east), three thin courses of
    dark stone (one broken), dark stones scattered,
    lozenges at the foot of the west front, a plain
    step at the foot of the others, a thin slab for a
    cornice, the earth roof with no parapet."""
    hw, hd, hh = 23.4, 28.5, 10.0
    hx, hy = -0.2, -0.25
    hall = L.box("hall", hw, hd, hh, "ashlar", hx, hy)
    holes = Holes("hall")
    frames = []
    south = hy - hd / 2
    north = hy + hd / 2
    west = hx - hw / 2
    east = hx + hw / 2
    grilles = []
    # south: (x, sill, w, h, shape, framed panel)
    for x, z, w, h, shape, panel in (
        (-9.0, 7.0, 0.45, 0.6, "rect", False),
        (-5.5, 3.4, 0.55, 0.85, "rect", True),
        (1.5, 4.0, 0.55, 0.85, "rect", True),
        (6.0, 6.4, 0.45, 0.6, "rect", False),
        (9.6, 6.2, 0.32, 1.5, False, False),
    ):
        frames.append(
            window(
                holes,
                x,
                south,
                z,
                PI,
                w,
                h,
                shape,
                0.45,
                "porch" if panel else None,
            )
        )
        grilles.append((x, south, z, PI, w, h))
        if panel:
            plaque(x, south, z + h + 0.5, PI)
    # west, either side of the porch: (y, sill, ...)
    for y, z, w, h, shape, panel in (
        (-6.8, 6.6, 0.45, 0.6, "rect", False),
        (-10.6, 6.0, 0.45, 0.6, "rect", False),
        (-9.6, 2.6, 0.6, 0.95, "rect", True),
        (-13.2, 2.2, 0.45, 1.0, False, False),
        (6.8, 6.6, 0.45, 0.6, "rect", False),
        (10.6, 3.0, 0.6, 0.95, "rect", True),
    ):
        frames.append(
            window(
                holes,
                west,
                y,
                z,
                -PI / 2,
                w,
                h,
                shape,
                0.45,
                "porch" if panel else None,
            )
        )
        grilles.append((west, y, z, -PI / 2, w, h))
    # north
    for x, z in ((-7.5, 6.8), (-1.0, 4.2), (6.5, 6.8)):
        window(
            holes,
            x,
            north,
            z,
            0,
            0.45,
            0.6,
            "rect",
            0.45,
            None,
        )
        grilles.append((x, north, z, 0, 0.45, 0.6))
    holes.cut(hall, *[f for f in frames if f])
    for g in grilles:
        grille(*g)
    # the foot: lozenges on the west, a step elsewhere
    sw, se = (west, south), (east, south)
    nw, ne = (west, north), (east, north)
    diamonds(sw, (west, -4.7), 0.0, 1.5)
    diamonds((west, 4.7), nw, 0.0, 1.5)
    band(se, sw, 0.0, 1.0, "ashlar", 0.14)
    band(nw, ne, 0.0, 1.0, "ashlar", 0.14)
    L.mould(
        "hall-step",
        [
            (east - 0.2, south),
            (east, south),
            (east, north),
            (east - 0.2, north),
        ],
        [(0.0, 0.0), (0.14, 0.0), (0.14, 1.0), (0.0, 1.0)],
        "ashlar",
    )
    # three thin courses of dark stone, one broken
    for z, gs, gw in (
        (2.6, (), ()),
        (5.1, ((0.55, 0.72),), ((0.1, 0.25),)),
        (7.9, (), ()),
    ):
        band(se, sw, z, 0.2, "basalt", 0.03, gs)
        band(sw, (west, -4.7), z, 0.2, "basalt", 0.03, gw)
        band((west, 4.7), nw, z, 0.2, "basalt", 0.03)
        band(nw, ne, z, 0.2, "basalt", 0.03)
    mottle(se, sw, 1.4, 8.8, 40, 5)
    mottle(sw, (west, -4.7), 1.6, 8.8, 14, 6)
    mottle((west, 4.7), nw, 1.6, 8.8, 14, 7)
    mottle(nw, ne, 1.4, 8.8, 35, 8)
    # the cornice: a thin slab standing out
    out = L.rect(hx, hy, hw, hd)
    L.mould(
        "hall-cornice",
        out,
        [
            (0.0, 9.55),
            (0.3, 9.62),
            (0.32, 9.72),
            (0.32, 9.9),
            (0.22, 10.0),
        ],
        "porch",
    )
    L.box(
        "hall-roof",
        hw + 0.4,
        hd + 0.4,
        0.3,
        "earth",
        hx,
        hy,
        hh,
    )
    L.bevel(hall, 0.03)
    # the big clay jars lying along the south wall
    for i in range(10):
        x = -1.5 + i * 1.2
        jar(x, south - 1.0, 0.0)


def jar(x, y, z):
    """A big clay jar (karas) lying on its side, its
    mouth to the south."""
    o = L.lathe(
        "jar",
        [
            (0.12, 0),
            (0.3, 0.1),
            (0.42, 0.45),
            (0.44, 0.8),
            (0.34, 1.25),
            (0.22, 1.42),
            (0.24, 1.5),
            (0.0, 1.5),
        ],
        14,
        "clay",
        0,
        0,
        0,
    )
    m = Matrix.Translation(
        (x, y + 0.75, z + 0.42)
    ) @ Matrix.Rotation(PI / 2, 4, "X")
    o.data.transform(m)


def arm(x, y, z, length, span, rise, rz, wall=1.6):
    """An arm of the cross round a drum: low walls
    standing on the flat roof, a gable wall of stone
    at the end with a small window, a roof of slabs
    overhanging it."""
    place = L.face(x, y, z, rz)
    # the walls and the gable, one solid of stone
    w = span / 2
    L.prism(
        "arm",
        [
            (-w, 0),
            (w, 0),
            (w, wall),
            (0, wall + rise),
            (-w, wall),
        ],
        length,
        "porch",
        place,
    )
    # the roof slabs, overhanging
    o, t = w + 0.35, 0.22
    k = rise / w
    L.prism(
        "arm-roof",
        [
            (-o, wall - 0.35 * k),
            (0, wall + rise),
            (o, wall - 0.35 * k),
            (o, wall - 0.35 * k + t),
            (0, wall + rise + t),
            (-o, wall - 0.35 * k + t),
        ],
        length + 0.5,
        "slate",
        place,
    )
    # a small window in each end
    n = n_of(rz)
    for sg in (-1, 1):
        c = Vector((x, y, 0)) + n * sg * (length / 2 + 0.02)
        L.box(
            "arm-win",
            0.06 if rz % PI else 0.5,
            0.5 if rz % PI else 0.06,
            0.75,
            "hole",
            c.x,
            c.y,
            z + wall - 0.05,
        )
        f = Vector((x, y, 0)) + n * sg * (length / 2 + 0.01)
        L.box(
            "arm-frame",
            0.05 if rz % PI else 0.8,
            0.8 if rz % PI else 0.05,
            1.05,
            "marble",
            f.x,
            f.y,
            z + wall - 0.2,
        )


def chapels():
    """The four chapels on the east. Stepanos and
    Karapet carry the drums, each on a cross of low
    gabled arms (stone gables with a small window,
    Lynch Fig. 158 and the photograph from the
    west); Gevorg, standing out to the south, has a
    flat earth roof at the height of the hall and
    tall round-arched windows with bars (Fig. 158).
    The north chapel's roof is not in a photograph:
    a gable, as before. On the hall's roof, by the
    belfry, a small flat-roofed hut with a door."""
    specs = [
        # north (Astvatsatsin on the plan)
        dict(y0=14.5, y1=25.5, x1=31, h=9),
        # Stepanos, with a drum
        dict(
            y0=-2.1, y1=14.5, x1=32.3, h=10, drum=(23, 6.4)
        ),
        # Karapet, with a drum and a band of arches
        dict(
            y0=-11.9,
            y1=-2.1,
            x1=32.3,
            h=10,
            drum=(23, -7.0),
            band=True,
        ),
        # Gevorg, a flat roof
        dict(y0=-21.7, y1=-11.9, x1=25.2, h=10, flat=True),
    ]
    for c in specs:
        x0 = 11.3
        w = c["x1"] - x0
        d = c["y1"] - c["y0"]
        cx = (x0 + c["x1"]) / 2
        cy = (c["y0"] + c["y1"]) / 2
        h = c["h"]
        body = L.box("chapel", w, d, h, "ashlar", cx, cy)
        holes = Holes("chapel")
        frames = [
            window(
                holes,
                c["x1"],
                cy,
                h - 4,
                PI / 2,
                0.4,
                1.3,
                True,
            )
        ]
        if c.get("flat"):
            for x, z in ((14.0, 6.6), (21.0, 3.8)):
                frames.append(
                    window(
                        holes,
                        x,
                        c["y0"],
                        z,
                        PI,
                        0.5,
                        1.2,
                        False,
                    )
                )
                grille(x, c["y0"], z, PI, 0.5, 0.95, 0.25)
            frames.append(
                window(
                    holes,
                    x0,
                    -18.5,
                    5.0,
                    -PI / 2,
                    0.4,
                    1.1,
                    False,
                )
            )
            grille(x0, -18.5, 5.0, -PI / 2, 0.4, 0.85, 0.25)
        holes.cut(body, *frames)
        out = L.rect(cx, cy, w, d)
        L.mould(
            "ch-step",
            out,
            [
                (0.0, 0.0),
                (0.14, 0.0),
                (0.14, 1.0),
                (0.0, 1.0),
            ],
            "ashlar",
        )
        mottle(
            (x0, c["y0"]),
            (c["x1"], c["y0"]),
            1.4,
            h - 1.2,
            int(w * 1.5),
            int(cy * 10),
        )
        if c.get("flat"):
            L.mould(
                "ch-cornice",
                out,
                [
                    (0.0, h - 0.45),
                    (0.3, h - 0.38),
                    (0.32, h - 0.28),
                    (0.32, h - 0.1),
                    (0.22, h),
                ],
                "porch",
            )
        else:
            L.mould(
                "ch-cornice",
                out,
                [
                    (0.0, h - 0.6),
                    (0.12, h - 0.45),
                    (0.35, h - 0.2),
                    (0.35, h),
                ],
                "porch",
            )
        L.bevel(body, 0.03)
        if c.get("flat"):
            L.box(
                "ch-roof",
                w + 0.4,
                d + 0.4,
                0.3,
                "earth",
                cx,
                cy,
                h,
            )
            continue
        if "drum" not in c:
            L.gable(
                "ch-roof",
                w + 0.6,
                d + 0.8,
                1.6,
                "slate",
                cx,
                cy,
                h,
                PI / 2,
            )
            continue
        dx, dy = c["drum"]
        L.box("ch-roof", w, d, 0.3, "earth", cx, cy, h)
        arm(dx, dy, h, 10.0, 6.6, 1.9, PI / 2, 1.0)
        arm(dx, dy, h, 9.6, 6.6, 1.9, 0, 1.0)
        drum(dx, dy, h + 1, c.get("band", False))
    # right behind the belfry
    hut(-8.0, -2.6, 10.3)


def hut(x, y, z):
    """The small flat-roofed hut on the hall's roof,
    right behind the belfry:
    a door and a window to the west, one to the
    south, an earth roof on a thin slab."""
    w, d, h = 5.0, 3.6, 2.6
    L.box("hut", w, d, h, "porch", x, y, z)
    L.box(
        "hut-slab",
        w + 0.4,
        d + 0.4,
        0.2,
        "porch",
        x,
        y,
        z + h,
    )
    L.box(
        "hut-earth",
        w + 0.2,
        d + 0.2,
        0.2,
        "earth",
        x,
        y,
        z + h + 0.2,
    )
    fx = x - w / 2 - 0.03
    L.box(
        "hut-door", 0.06, 0.9, 1.8, "wood", fx, y - 0.6, z
    )
    L.box(
        "hut-win",
        0.06,
        0.6,
        0.6,
        "hole",
        fx,
        y + 0.9,
        z + 1.0,
    )
    L.box(
        "hut-win",
        0.6,
        0.06,
        0.6,
        "hole",
        x + 0.8,
        y - d / 2 - 0.03,
        z + 1.0,
    )


def patch_lathe(
    name,
    prof,
    n,
    mats,
    dark,
    seed,
    x,
    y,
    z,
    rows=None,
    light=None,
):
    """A shape turned from prof (as L.lathe) in
    stones of mats[0] and, by chance dark, mats[1]:
    the irregular light and dark patchwork of the
    drums. rows: rows of stones in each step of prof;
    light(i, k) may name a cell to give mats[2]."""
    import random

    rnd = random.Random(seed)
    bm = bmesh.new()
    pts = []
    for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
        k = rows or max(1, round(abs(h1 - h0) / 0.34))
        for j in range(k):
            t = j / k
            pts.append(
                (r0 + (r1 - r0) * t, h0 + (h1 - h0) * t)
            )
    pts.append(prof[-1])
    rings = []
    for r, h in pts:
        ring = []
        for i in range(n):
            a = 2 * PI * i / n
            ring.append(
                bm.verts.new(
                    (
                        x + r * math.sin(a),
                        y + r * math.cos(a),
                        z + h,
                    )
                )
            )
        rings.append(ring)
    for k, (lo, hi) in enumerate(zip(rings, rings[1:])):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            m = 1 if rnd.random() < dark else 0
            if light and light(i, k, pts[k][1]):
                m = 2
            f.material_index = m
    bm.faces.new(list(reversed(rings[0])))
    if pts[-1][0] > 0:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = L.obj(name, bm, mats[0], "round")
    for m in mats[1:]:
        o.data.materials.append(L.MATS[m])
    return o


def iron_cross(x, y, z):
    """A small knob and an iron cross on a cone."""
    L.lathe(
        "knob",
        [(0.0, 0), (0.16, 0.1), (0.12, 0.3), (0.0, 0.4)],
        8,
        "slate",
        x,
        y,
        z - 0.15,
    )
    L.box("cross", 0.06, 0.06, 0.9, "iron", x, y, z + 0.2)
    L.box("cross", 0.4, 0.06, 0.06, "iron", x, y, z + 0.8)


def drum(dx, dy, b, band):
    """A drum as in Lynch's Fig. 158 and the photograph
    before 1915 from the west. Stepanos (not band):
    an irregular patchwork of light and dark stone, a
    light ring, a dark band of small light squares, a
    framed window, a straight cone in patchwork too.
    Karapet (band): a blind arcade of eight tall
    pointed arches low on the drum, light plastered
    panels in them, a plain band and a frieze of
    small dark squares above, a cone curved like a
    bell. Both flare out at the foot."""
    r, n, hgt = 2.7, 32, 6.4
    seed = 7 if band else 3
    # the foot, flaring out to the roofs
    patch_lathe(
        "drum-foot",
        [(3.7, -1.3), (3.05, -0.2), (r, 0.3)],
        n,
        ["porch", "basalt"],
        0.3,
        seed + 1,
        dx,
        dy,
        b,
        rows=3,
    )
    z0a, ha, na = 0.55, 3.7, 8

    def panel(i, k, h):
        # inside an arch of the arcade?
        if not band:
            return False
        if not (z0a + 0.1 < h < z0a + ha - 0.25):
            return False
        a = (i + 0.5) / n * na
        u = (a - math.floor(a) - 0.5) * 2 * PI * r / na
        w = PI * r / na - 0.35
        if h - z0a > ha - w - 0.25:
            # in the pointed head
            t = (h - z0a - (ha - w - 0.25)) / (w + 0.25)
            return abs(u) < w * (1 - t) ** 0.6
        return abs(u) < w

    o = patch_lathe(
        "drum",
        [(r, 0.3), (r, hgt)],
        n,
        ["porch", "basalt", "marble"],
        0.22 if band else 0.45,
        seed,
        dx,
        dy,
        b,
        light=panel,
    )
    holes = Holes("drum")
    frames = []
    if band:
        for i in (1, 3, 5, 7):
            f = (i + 0.5) * 2 * PI / na
            window(
                holes,
                dx + r * math.sin(f),
                dy + r * math.cos(f),
                b + 1.5,
                f,
                0.22,
                1.2,
                True,
                0.4,
                None,
            )
    else:
        # a framed window to the west, slits round it
        f = -PI / 2 + PI / n
        frames.append(
            window(
                holes,
                dx + r * math.sin(f),
                dy + r * math.cos(f),
                b + 2.4,
                f,
                0.55,
                0.8,
                "rect",
                0.4,
                "marble",
            )
        )
        for f in (PI / n, PI / 2 + PI / n, PI + PI / n):
            window(
                holes,
                dx + r * math.sin(f),
                dy + r * math.cos(f),
                b + 2.0,
                f,
                0.18,
                1.0,
                False,
                0.4,
                None,
            )
    holes.cut(o, *[fr for fr in frames if fr])
    if band:
        # the rolls of the arcade, following the drum
        rr = r + 0.06
        for j in range(na):
            ac = (j + 0.5) * 2 * PI / na
            w = PI * r / na - 0.2
            pts = L.arch(2 * w, ha, True, 10)
            path = [pts[1], *pts[2:], pts[0]]
            L.tube(
                "arcade-roll",
                [
                    (
                        dx + rr * math.sin(ac + u / rr),
                        dy + rr * math.cos(ac + u / rr),
                        b + z0a + v,
                    )
                    for u, v in path
                ],
                0.08,
                "porch",
                8,
            )
        for j in range(na):
            a = j * 2 * PI / na
            L.cyl(
                "arcade-col",
                0.1,
                ha - 0.9,
                8,
                "porch",
                dx + (r + 0.08) * math.sin(a),
                dy + (r + 0.08) * math.cos(a),
                b + z0a,
            )
        # a plain band over the arcade
        L.lathe(
            "drum-band",
            [(r + 0.06, 0), (r + 0.06, 0.25)],
            n,
            "porch",
            dx,
            dy,
            b + z0a + ha + 0.25,
        )
    else:
        # the light ring
        L.lathe(
            "drum-ring",
            [
                (r + 0.05, 0),
                (r + 0.12, 0.1),
                (r + 0.05, 0.3),
            ],
            n,
            "porch",
            dx,
            dy,
            b + 4.3,
        )
    # the frieze of small squares under the cornice
    fz = b + hgt - 1.0
    L.lathe(
        "frieze",
        [(r + 0.02, 0), (r + 0.02, 0.8)],
        n,
        "porch" if band else "basalt",
        dx,
        dy,
        fz,
    )
    for i in range(n):
        a = (i + 0.5) * 2 * PI / n
        L.box(
            "frieze-sq",
            0.26,
            0.08,
            0.26,
            "basalt" if band else "porch",
            dx + (r + 0.03) * math.sin(a),
            dy + (r + 0.03) * math.cos(a),
            fz + 0.27,
            -a,
        )
    top = b + hgt
    L.lathe(
        "drum-cornice",
        [
            (2.72, 0),
            (2.85, 0.1),
            (2.95, 0.25),
            (3.1, 0.35),
            (3.2, 0.55),
            (3.2, 0.7),
        ],
        n,
        "porch",
        dx,
        dy,
        top,
    )
    # the cone: straight on Stepanos, curved like a
    # bell on Karapet; its slabs light and dark
    cr, chh = 3.2, 5.6
    prof = [(cr + 0.1, -0.15), (cr + 0.1, 0.0)]
    for k in range(9):
        t = k / 8
        rad = cr * (1 - t**1.3) if band else cr * (1 - t)
        prof.append((max(rad, 0.0), chh * t))
    patch_lathe(
        "drum-cone",
        prof,
        n,
        ["slate", "basalt"]
        if band
        else ["basalt", "porch"],
        0.3 if band else 0.2,
        seed + 2,
        dx,
        dy,
        top + 0.7,
        rows=2,
    )
    iron_cross(dx, dy, top + 0.7 + chh)


# -- the porch and the belfry --


def porch():
    gx, gw, gd, gh = -16.85, 9.9, 9.4, 10.4
    fx = gx - gw / 2
    body = L.box("porch", gw, gd, gh, "porch", gx, 0)
    holes = Holes("porch")
    frames = []
    # the portal: three pointed recesses stepping in,
    # the door at the back
    for aw, ah, dp in (
        (3.8, 6.8, 0.25),
        (3.0, 6.1, 0.5),
        (2.3, 5.4, 0.8),
    ):
        holes.add(
            L.arch(aw, ah, True),
            dp * 2,
            L.face(fx, 0, 0, -PI / 2),
        )
    L.box("door", 0.08, 2.0, 3.3, "wood", fx + 0.78, 0, 0)
    L.box(
        "door-back", 0.04, 2.3, 5.5, "hole", fx + 0.82, 0, 0
    )
    rosette(fx + 0.78, 0, 4.25, -PI / 2, 0.55)
    for y in (-3.4, 3.4):
        frames.append(
            window(holes, fx, y, 7.6, -PI / 2, 0.5, 0.9)
        )
    for s in (-1, 1):
        frames.append(
            window(
                holes,
                gx,
                s * gd / 2,
                7.6,
                0 if s > 0 else PI,
                0.5,
                0.9,
            )
        )
        frames.append(
            window(
                holes,
                gx,
                s * gd / 2,
                3.2,
                0 if s > 0 else PI,
                0.5,
                0.9,
            )
        )
    holes.cut(body, *frames)
    # the marble slabs with rosettes on its front
    for y, z, w, h in (
        (-3.6, 1.8, 1.1, 1.6),
        (3.6, 1.8, 1.1, 1.6),
        (-3.6, 4.2, 1.1, 1.1),
        (3.6, 4.2, 1.1, 1.1),
    ):
        L.box("slab", 0.1, w, h, "marble", fx - 0.05, y, z)
        rosette(
            fx - 0.1,
            y,
            z + h / 2,
            -PI / 2,
            min(w, h) * 0.38,
        )
    out = L.rect(gx, 0, gw, gd)
    checker(out, 0.0)
    L.mould(
        "porch-course",
        out,
        [(0.0, 5.55), (0.1, 5.6), (0.1, 5.75), (0.0, 5.8)],
        "porch",
    )
    L.mould(
        "porch-cornice",
        out,
        [
            (0.0, 9.7),
            (0.1, 9.8),
            (0.3, 10.05),
            (0.45, 10.25),
            (0.45, 10.4),
        ],
        "porch",
    )
    L.bevel(body, 0.03)
    belfry(gx)
    # the graves before the porch, an iron fence
    import random

    r = random.Random(41)
    for i in range(6):
        for x in (-27, -24.5):
            L.box(
                "stele",
                0.55,
                0.28,
                1.3 + r.random() * 0.6,
                "marble",
                x + r.random() * 0.4,
                6.5 - i * 2.6,
            )
    for a, b in (
        ((-28.2, 8), (-28.2, -8)),
        ((-28.2, 8), (-23.6, 8)),
        ((-28.2, -8), (-23.6, -8)),
    ):
        a, b = Vector(a), Vector(b)
        nb = round((b - a).length / 1.2)
        for i in range(nb + 1):
            p = a + (b - a) * i / nb
            L.box("post", 0.05, 0.05, 1.0, "iron", p.x, p.y)
        for z in (0.35, 0.92):
            rod(
                "rail",
                (a.x, a.y, z),
                (b.x, b.y, z),
                0.025,
                "iron",
            )


def shaft(name, x, y, z, h, r, mat="porch"):
    """A slender shaft with a base, two rings round
    it and a capital, as on the belfry's piers."""
    prof = [
        (r * 1.6, 0),
        (r * 1.6, 0.12),
        (r, 0.25),
    ]
    for f in (0.36, 0.68):
        z0 = h * f
        prof += [
            (r, z0 - 0.06),
            (r * 1.45, z0),
            (r * 1.45, z0 + 0.06),
            (r, z0 + 0.12),
        ]
    prof += [
        (r, h - 0.32),
        (r * 1.3, h - 0.22),
        (r * 1.8, h - 0.08),
        (r * 1.8, h),
    ]
    L.lathe(name, prof, 10, mat, x, y, z)


def arch_rolls(c, rz, z, orders, pointed=True):
    """Roll mouldings round an arched opening at c
    on a face that looks to rz: orders [(w, h,
    out), ...], each an arch w by h standing out
    from the face by out."""
    place = L.face(c.x, c.y, z, rz)
    for w, h, out in orders:
        pts = L.arch(w, h, pointed, 16)
        # the arch from one foot to the other, the
        # sill left out
        path = [pts[1], *pts[2:], pts[0]]
        L.tube(
            "roll",
            L.on_face(path, place, out),
            0.09,
            "porch",
            8,
        )


def octagon(x, y, s, c):
    """A square s wide round x, y with its corners cut
    off c along each side: four wide faces and four
    narrow ones, counter-clockwise."""
    h = s / 2
    return [
        (x - h + c, y - h),
        (x + h - c, y - h),
        (x + h, y - h + c),
        (x + h, y + h - c),
        (x + h - c, y + h),
        (x - h + c, y + h),
        (x - h, y + h - c),
        (x - h, y - h + c),
    ]


def shrine(x, y, z, rz):
    """The little gabled shrine standing at the foot
    of each corner niche: a base, a body with a
    small arched opening, a steep gable."""
    n = n_of(rz)
    L.box("tab-base", 0.9, 0.4, 0.3, "porch", x, y, z, -rz)
    L.box(
        "tab-body",
        0.75,
        0.35,
        1.2,
        "porch",
        x,
        y,
        z + 0.3,
        -rz,
    )
    f = Vector((x, y, z)) + n * 0.18
    L.prism(
        "tab-niche",
        L.arch(0.3, 0.75, True),
        0.03,
        "hole",
        L.face(f.x, f.y, z + 0.55, rz),
    )
    L.prism(
        "tab-gable",
        [(-0.48, 0), (0.48, 0), (0, 0.85)],
        0.42,
        "porch",
        L.face(x, y, z + 1.5, rz),
    )


def belfry(gx):
    """First stage, after the photographs before 1915:
    an octagon in plan, four wide faces each opened
    by a pointed arch with roll mouldings stepping
    in, and four narrow corners cut off, each with a
    tall gabled niche carved into it, a small shrine
    at its foot and a shaft either side; a steep gable
    over each arch with crockets and a finial, small
    pinnacles over the corners. Second: eight columns
    under cusped (five-lobed) arches, a high plain
    frieze, a roof of plain slabs."""
    by, s, sh = 10.9, 7.6, 7.6
    c8 = 1.25
    oct8 = octagon(gx, 0, s, c8)
    L.mould(
        "bel-plinth",
        oct8,
        [(0.35, -0.5), (0.35, 0.0)],
        "porch",
        by,
    )
    block = L.mould(
        "belfry", oct8, [(0.0, 0.0), (0.0, sh)], "porch", by
    )
    holes = Holes("belfry")
    aw, ah = 3.5, 6.75
    for rz in (0, PI / 2):
        holes.add(
            L.arch(aw, ah, True),
            s + 2,
            L.face(gx, 0, by, rz),
        )
    orders = ((4.1, 7.25, 0.22), (3.8, 7.0, 0.4))
    for rz in (0, PI / 2, PI, -PI / 2):
        n = n_of(rz)
        c = Vector((gx, 0, 0)) + n * (s / 2)
        for w, h, dp in orders:
            holes.add(
                L.arch(w, h, True),
                dp * 2,
                L.face(c.x, c.y, by, rz),
            )
    # the tall gabled niches in the cut-off corners
    hd = (s / 2 - c8 / 2) * math.sqrt(2)
    corners = []
    for cx, cy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        rz = math.atan2(cx, cy)
        n = n_of(rz)
        cc = Vector((gx, 0, 0)) + n * hd
        corners.append((cc, rz, n))
        holes.add(
            [
                (-0.5, 0),
                (0.5, 0),
                (0.5, 5.3),
                (0, 6.2),
                (-0.5, 5.3),
            ],
            0.9,
            L.face(cc.x, cc.y, by + 0.35, rz),
        )
    holes.cut(block)
    L.bevel(block, 0.03)
    for cc, rz, n in corners:
        p = cc - n * 0.25
        shrine(p.x, p.y, by + 0.35, rz)
        t = Vector((n.y, -n.x, 0))
        for sg in (-1, 1):
            q = cc + t * sg * 0.7 + n * 0.06
            shaft("bel-shaft", q.x, q.y, by, 6.4, 0.09)
        # its gable mould, a roll round the niche
        L.tube(
            "roll",
            L.on_face(
                [(-0.62, 5.25), (0, 6.35), (0.62, 5.25)],
                L.face(cc.x, cc.y, by + 0.35, rz),
                0.05,
            ),
            0.08,
            "porch",
            8,
        )
    for rz in (0, PI / 2, PI, -PI / 2):
        n = n_of(rz)
        t = Vector((n.y, -n.x, 0))
        c = Vector((gx, 0, 0)) + n * (s / 2)
        arch_rolls(
            c,
            rz,
            by,
            [
                (
                    orders[0][0] + 0.1,
                    orders[0][1] + 0.05,
                    -0.2,
                ),
                (
                    orders[1][0] + 0.1,
                    orders[1][1] + 0.05,
                    -0.38,
                ),
                (aw + 0.1, ah + 0.05, -0.55),
            ],
        )
        # the hood over the arch
        arch_rolls(c, rz, by, [(4.5, 7.5, 0.06)])
        # the clustered shafts beside the arch
        for sg in (-1, 1):
            for off in (2.28, 2.46):
                p = c + t * sg * off + n * 0.1
                shaft("bel-shaft", p.x, p.y, by, 5.0, 0.08)
        # the gable, its crockets and its finial
        g = c - n * 0.25
        top = by + sh + 0.25
        gw = s / 2 - c8 + 0.25
        L.prism(
            "bel-gable",
            [(-gw, 0), (gw, 0), (0, 3.4)],
            0.5,
            "porch",
            L.face(g.x, g.y, top, rz),
        )
        apex = c + n * 0.05
        for sg in (-1, 1):
            a = c + t * sg * gw + n * 0.05
            a = Vector((a.x, a.y, top))
            b = Vector((apex.x, apex.y, top + 3.45))
            rod("bel-rake", a, b, 0.11, "porch")
            for k in range(1, 6):
                q = a + (b - a) * (k / 6.0)
                L.box(
                    "crocket",
                    0.22,
                    0.22,
                    0.22,
                    "porch",
                    q.x,
                    q.y,
                    q.z + 0.08,
                    -rz,
                )
        spire(
            "bel-fin",
            apex.x,
            apex.y,
            top + 3.4,
            0.16,
            0.75,
            4,
            False,
            False,
        )
    L.mould(
        "bel-cornice",
        oct8,
        [
            (0.0, sh - 0.05),
            (0.12, sh + 0.05),
            (0.2, sh + 0.15),
            (0.2, sh + 0.25),
        ],
        "porch",
        by,
    )
    for cc, rz, n in corners:
        # a small pinnacle over each corner
        p = cc - n * 0.35
        z = by + sh + 0.25
        L.box(
            "pinnacle",
            0.45,
            0.45,
            0.7,
            "porch",
            p.x,
            p.y,
            z,
            -rz,
        )
        spire(
            "pin-spire",
            p.x,
            p.y,
            z + 0.7,
            0.28,
            1.0,
            4,
            False,
            False,
        )
    # the second stage
    uy = by + sh + 0.5
    ur = 2.5
    L.lathe(
        "ring-base",
        [
            (3.05, 0),
            (3.05, 0.6),
            (3.25, 0.65),
            (3.25, 0.85),
        ],
        8,
        "porch",
        gx,
        0,
        uy,
    )
    top = uy + 0.85
    ch = 3.3
    for i in range(8):
        a = i * PI / 4
        column(
            "ring-col",
            gx + ur * math.sin(a),
            ur * math.cos(a),
            top,
            ch,
            0.18,
            "porch",
        )
    band = 2.3
    z0 = top + ch - 0.9
    ring = L.lathe(
        "ring-arch",
        [(2.85, 0), (2.85, band)],
        8,
        "porch",
        gx,
        0,
        z0,
    )
    inner = L.lathe(
        "ring-in",
        [(2.2, -1), (2.2, band + 1)],
        8,
        "porch",
        gx,
        0,
        z0,
    )
    holes = Holes("ring")
    for i in range(8):
        f = i * PI / 4 + PI / 8
        holes.add(
            L.foil(1.7, 1.75),
            2.0,
            L.face(
                gx + 2.6 * math.sin(f),
                2.6 * math.cos(f),
                z0 - 0.02,
                f,
            ),
        )
    holes.cut(ring)
    L.cut(ring, [inner])
    # a ladder up to the bells
    for sg in (-1, 1):
        rod(
            "ladder",
            (gx - 1.2, sg * 0.25, top),
            (gx + 0.4, sg * 0.25, top + ch + 0.6),
            0.04,
            "wood",
        )
    for k in range(1, 9):
        f = k / 9
        x = gx - 1.2 + 1.6 * f
        z = top + (ch + 0.6) * f
        rod(
            "rung",
            (x, -0.25, z),
            (x, 0.25, z),
            0.025,
            "wood",
        )
    ry = z0 + band
    L.lathe(
        "ring-cornice",
        [
            (2.85, 0),
            (3.0, 0.1),
            (3.15, 0.3),
            (3.3, 0.5),
            (3.3, 0.65),
        ],
        8,
        "porch",
        gx,
        0,
        ry,
    )
    spire(
        "bel-roof",
        gx,
        0,
        ry + 0.65,
        3.25,
        5.6,
        8,
        True,
        False,
    )


# -- the enclosure and the buildings round the court --

W, E, N, S = -62.0, 42.0, 40.0, -44.0


def enclosure():
    wh, wt = 8.0, 1.8
    L.box(
        "court",
        E - W,
        N - S,
        0.08,
        "court",
        (W + E) / 2,
        (N + S) / 2,
    )
    walls = [
        (E - W, wt, (W + E) / 2, N),
        (E - W, wt, (W + E) / 2, S),
        (wt, N - S, E, (N + S) / 2),
        (wt, N - 6, W, (N + 6) / 2),
        (wt, -6 - S, W, (S - 6) / 2),
    ]
    outer = []
    for w, d, x, y in walls:
        o = L.box("wall", w, d, wh, "rubble", x, y)
        outer.append(o)
        L.box(
            "wall-top",
            w + 0.2,
            d + 0.2,
            0.5,
            "ashlar",
            x,
            y,
            wh - 0.5,
        )
        L.box("wall-earth", w, d, 0.25, "earth", x, y, wh)
        L.bevel(o, 0.05)
    holes = Holes("south")
    for i in range(16):
        x = W + 6 + i * 6.2
        holes.add(
            L.arch(0.35, 0.8), 3, L.face(x, S, 6.0, PI)
        )
    # the gatehouse on the west
    gate = L.box("gatehouse", 6, 12, 10, "rubble", W, 0)
    gh = Holes("gate")
    gh.add(L.arch(4, 6.2), 8, L.face(W, 0, 0, PI / 2))
    gh.cut(gate)
    L.box("gate-top", 6.2, 12.2, 0.6, "ashlar", W, 0, 9.4)
    L.box("gate-earth", 6, 12, 0.25, "earth", W, 0, 10)
    for sg in (-1, 1):
        L.box(
            "gate-door",
            0.25,
            2,
            5.8,
            "wood",
            W + 3.2,
            sg * 1.6,
            0,
            sg * 0.6,
        )
    # the round towers, the great one on the south
    towers = []
    for x, y, rr, h in (
        (W, N, 4.2, 11),
        (E, N, 4.2, 11),
        (E, S, 4.2, 11),
        (W, S, 4.6, 12),
        (-22, S - 1, 5.6, 12.5),
    ):
        t = L.cyl("tower", rr, h, 28, "rubble", x, y)
        towers.append(t)
        L.lathe(
            "tower-top",
            [
                (rr + 0.25, h - 0.5),
                (rr + 0.25, h),
                (rr + 0.3, h),
                (rr + 0.3, h + 0.9),
                (rr - 0.2, h + 0.9),
                (rr - 0.2, h + 0.7),
            ],
            28,
            "rubble",
            x,
            y,
        )
        L.cyl(
            "tower-earth",
            rr - 0.2,
            0.3,
            28,
            "earth",
            x,
            y,
            h + 0.6,
        )
        for i in range(5):
            a = i * 2 * PI / 5 + 0.3
            holes.add(
                L.arch(0.25, 1.1),
                2,
                L.face(
                    x + rr * math.sin(a),
                    y + rr * math.cos(a),
                    4.8,
                    a,
                ),
            )
    holes.cut(*outer, *towers)


def ranges():
    sx0, sx1 = W + 1, E - 1
    sw = sx1 - sx0
    scx = (sx0 + sx1) / 2
    # south: cells and the refectory, a gallery of two
    # floors on the court
    L.box("s-range", sw, 9.5, 10, "rubble", scx, S + 5.6)
    L.box(
        "s-earth", sw, 9.3, 0.3, "earth", scx, S + 5.6, 10
    )
    gal = L.box(
        "s-gallery", sw, 0.6, 10, "porch", scx, -31.1
    )
    holes = Holes("s-gal")
    for i in range(24):
        x = sx0 + (i + 0.5) * sw / 24
        holes.add(
            L.arch(2.6, 3.8), 1.5, L.face(x, -31.1, 0, 0)
        )
        holes.add(
            L.arch(2.4, 3.4), 1.5, L.face(x, -31.1, 5.8, 0)
        )
        L.box("door", 1.0, 0.05, 2.1, "hole", x, -33.6)
        L.box("door", 0.6, 0.05, 1.0, "hole", x, -33.6, 6.6)
    holes.cut(gal)
    L.box("s-floor", sw, 3, 0.4, "porch", scx, -32.4, 5.2)
    L.box("s-roof", sw, 3.4, 0.5, "porch", scx, -32.4, 10)
    L.box(
        "s-roof-earth",
        sw,
        3.4,
        0.25,
        "earth",
        scx,
        -32.4,
        10.5,
    )
    # north: cells, a gallery too
    L.box("n-range", sw, 7, 8, "rubble", scx, N - 4.4)
    L.box("n-earth", sw, 6.8, 0.3, "earth", scx, N - 4.4, 8)
    gal = L.box("n-gallery", sw, 0.6, 8, "porch", scx, 31)
    holes = Holes("n-gal")
    for i in range(24):
        x = sx0 + (i + 0.5) * sw / 24
        holes.add(
            L.arch(2.6, 3.2), 1.5, L.face(x, 31, 0, PI)
        )
        holes.add(
            L.arch(2.4, 2.8), 1.5, L.face(x, 31, 4.6, PI)
        )
        L.box("door", 0.9, 0.05, 2.0, "hole", x, 32.08)
    holes.cut(gal)
    L.box("n-floor", sw, 3, 0.4, "porch", scx, 32.2, 4)
    L.box("n-roof", sw, 3, 0.5, "porch", scx, 32.2, 8)
    L.box(
        "n-roof-earth", sw, 3, 0.25, "earth", scx, 32.2, 8.5
    )
    # west: cells on two floors, a gallery
    L.box("w-range", 7, 30, 9, "rubble", W + 4.4, 22)
    L.box("w-earth", 6.8, 30, 0.3, "earth", W + 4.4, 22, 9)
    gal = L.box(
        "w-gallery", 0.6, 30, 9, "porch", W + 10.6, 22
    )
    holes = Holes("w-gal")
    for i in range(9):
        y = 22 - 15 + (i + 0.5) * 30 / 9
        holes.add(
            L.arch(2.4, 3.4),
            1.5,
            L.face(W + 10.6, y, 0, PI / 2),
        )
        holes.add(
            L.arch(2.2, 3.0),
            1.5,
            L.face(W + 10.6, y, 5.1, PI / 2),
        )
    holes.cut(gal)
    L.box("w-roof", 3.4, 30, 0.5, "porch", W + 9.4, 22, 9)
    # Bishop Mampre's new building on the west
    mb = L.box("mampre", 12, 20, 12, "porch", W + 7, -22)
    holes = Holes("mampre")
    frames = []
    for f in range(3):
        for i in range(5):
            frames.append(
                window(
                    holes,
                    W + 13,
                    -14 - i * 4,
                    1.5 + f * 3.6,
                    PI / 2,
                    0.9,
                    1.6,
                )
            )
    holes.cut(mb, *frames)
    L.mould(
        "mb-cornice",
        L.rect(W + 7, -22, 12, 20),
        [
            (0, 11.4),
            (0.15, 11.55),
            (0.35, 11.8),
            (0.35, 12),
        ],
        "porch",
    )
    L.gable(
        "mb-roof", 21, 12.8, 2.2, "slate", W + 7, -22, 12, 0
    )
    L.bevel(mb, 0.03)
    # the Harutyun chapel in its walled yard
    hx, hy = -40.0, -22.0
    hc = L.box("harutyun", 5, 6.5, 4.5, "ashlar", hx, hy)
    hh = Holes("harutyun")
    fr = window(
        hh, hx + 2.5, hy, 2.4, PI / 2, 0.3, 0.9, True
    )
    hh.add(
        L.arch(1.0, 2.0),
        1.2,
        L.face(hx - 2.5, hy, 0, -PI / 2),
    )
    hh.cut(hc, fr)
    L.box("har-door", 0.05, 1.0, 2.0, "hole", hx - 2.2, hy)
    L.gable(
        "har-roof", 7.2, 5.6, 1.8, "slate", hx, hy, 4.5, 0
    )
    for x, y, w, d in (
        (hx, hy - 6, 12, 0.6),
        (hx, hy + 6, 12, 0.6),
        (hx + 6, hy, 0.6, 12),
        (hx - 6, hy - 4, 0.6, 4),
        (hx - 6, hy + 4, 0.6, 4),
    ):
        L.box("har-wall", w, d, 1.6, "rubble", x, y)
    # the cross-yard behind the church
    import random

    r = random.Random(53)
    for i in range(16):
        y = 30 - i * 3.4 - r.random()
        x = 34.5 + (i % 3) * 2
        if i % 3 == 0:
            cross_stone(x, y, -PI / 2)
        else:
            L.box("grave", 1, 2, 0.35, "marble", x, y)
    # the cemetery on the terrace outside, south-west
    for i in range(22):
        x = -82 + r.random() * 18
        y = -54 - r.random() * 10
        L.box(
            "stele",
            0.5,
            0.25,
            0.8 + r.random() * 0.8,
            "ashlar",
            x,
            y,
            height(x, y) - 0.2,
            r.random() * 0.4,
        )


def trees():
    for kind, x, y, h, sd in (
        ("poplar", 6, 25, 17, 1),
        ("walnut", -32, 22, 9, 2),
        ("poplar", -52, -2, 15, 3),
        ("walnut", 30, -26, 8, 4),
        ("walnut", -78, -30, 10, 5),
        ("poplar", -84, -46, 16, 6),
        ("walnut", 60, -52, 9, 7),
        ("walnut", -30, -66, 11, 8),
        ("poplar", 12, -64, 18, 9),
        ("walnut", 70, 10, 10, 10),
    ):
        tree(kind, x, y, height(x, y), h, sd)


# -- the views of the photographs --

VIEWS = {
    # the church from high in the south-west, as the
    # photograph before 1915
    "south-west": ((-46, -34, 19), (2, 2, 7), 32),
    # the porch and belfry from the west
    "west": ((-47, 1.5, 7.5), (-14, 0, 12), 35),
    # the whole monastery, as the web page opens
    "overview": ((-95, -125, 75), (-6, 0, 4), 32),
    # the chapels from the east
    "east": ((60, -22, 22), (20, 0, 12), 35),
    # close views, to check the details
    "belfry": ((-46, -24, 13), (-16.85, 0, 17.5), 38),
    "drums": ((-6, -3, 18), (23, -0.3, 16), 34),
    "hall": ((-31, -29, 8), (-3, -10, 5), 30),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L.reset()
    materials()
    church()
    chapels()
    porch()
    enclosure()
    ranges()
    trees()
    ground()
    L.finish(join=True)
    L.sky("kloofendal_48d_partly_cloudy_puresky", 1.0, 0.6)
    L.sun(215, 38, 4.5)
    bpy.ops.wm.save_as_mainfile(
        filepath=str(OUT / "glakavank.blend")
    )
    if "--no-render" not in ARGS:
        size = (800, 600) if QUICK else (1600, 1200)
        samples = 24 if QUICK else 96
        only = [
            a.split("=", 1)[1].split(",")
            for a in ARGS
            if a.startswith("--views=")
        ]
        for name, (eye, look, lens) in VIEWS.items():
            if only and name not in only[0]:
                continue
            cam = L.camera(name, eye, look, lens)
            L.render(
                cam, OUT / f"{name}.jpg", size, samples
            )
    if "--glb" in ARGS:
        L.export_glb(OUT / "glakavank.glb")
    if "--web" in ARGS:
        # the buildings for web/models/glakavank.js;
        # the page draws its own ground and bushes
        web = L.ROOT.parent / "web" / "models" / "glakavank"
        L.export_web(web, skip=("ground", "scrub"))


main()
