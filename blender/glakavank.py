"""Glakavank, the monastery of Karapet above the plain
of Mush (Taron), as it stood in 1893: a model built
in Blender, by script.

    blender -b --factory-startup -P blender/glakavank.py \\
        -- [--quick] [--no-render] [--glb]

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
    pts = L.arch(w, h, pointed)
    holes.add(pts, deep * 2, L.face(x, y, z, rz))
    b = Vector((x, y, z)) - n * (deep - 0.02)
    L.box("win-back", w, 0.02, h, "hole", b.x, b.y, z, -rz)
    if frame:
        f = Vector((x, y, z - 0.12)) + n * 0.06
        fr = L.prism(
            "frame",
            L.arch(w + 0.38, h + 0.3, pointed),
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


def spire(name, x, y, z, r, h, n, cross=True):
    """A cone of n sides of stone slabs, a rib on each
    edge, a ball and a cross."""
    L.lathe(
        name,
        [(r + 0.15, -0.2), (r + 0.15, 0), (r, 0), (0, h)],
        n,
        "slate",
        x,
        y,
        z,
    )
    for i in range(n):
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
        for j in range(9):
            t = PI * j / 8
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


def church():
    hw, hd, hh = 23.4, 28.5, 10.0
    hx, hy = -0.2, -0.25
    hall = L.box("hall", hw, hd, hh, "ashlar", hx, hy)
    holes = Holes("hall")
    frames = []
    south = hy - hd / 2
    north = hy + hd / 2
    west = hx - hw / 2
    for x in (-8.5, -3, 2.5, 8):
        frames.append(
            window(holes, x, south, 3.2, PI, 0.55, 0.95)
        )
        frames.append(
            window(
                holes, x + 1.4, south, 7.1, PI, 0.55, 0.95
            )
        )
        frames.append(
            window(holes, x, north, 7.1, 0, 0.55, 0.95)
        )
    for y in (-10, -7, 7, 10):
        frames.append(
            window(holes, west, y, 7.1, -PI / 2, 0.55, 0.95)
        )
    holes.cut(hall, *frames)
    out = L.rect(hx, hy, hw, hd)
    checker(out, 0.0)
    # a string course, the cornice, the parapet and
    # the earth roof
    L.mould(
        "hall-course",
        out,
        [(0.0, 5.55), (0.1, 5.6), (0.1, 5.75), (0.0, 5.8)],
        "porch",
    )
    L.mould(
        "hall-cornice",
        out,
        [
            (0.0, 9.3),
            (0.08, 9.35),
            (0.12, 9.5),
            (0.3, 9.65),
            (0.4, 9.85),
            (0.4, 10.0),
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
    for x, y, w, d in (
        (hx, south - 0.1, hw + 0.6, 0.45),
        (hx, north + 0.1, hw + 0.6, 0.45),
        (west - 0.1, hy, 0.45, hd),
    ):
        L.box("parapet", w, d, 0.6, "ashlar", x, y, hh)
    L.bevel(hall, 0.03)


def chapels():
    specs = [
        # north (Astvatsatsin on the plan), a small
        # house with a gable on its roof
        dict(y0=14.5, y1=25.5, x1=31, h=9, house=True),
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
        # Gevorg
        dict(y0=-21.7, y1=-11.9, x1=25.2, h=9),
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
        fr = window(
            holes,
            c["x1"],
            cy,
            h - 4,
            PI / 2,
            0.4,
            1.3,
            True,
        )
        holes.cut(body, fr)
        out = L.rect(cx, cy, w, d)
        checker(out, 0.0)
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
            if c.get("house"):
                hb = L.box(
                    "house",
                    7,
                    5,
                    3,
                    "ashlar",
                    cx - 4,
                    cy,
                    h,
                )
                L.gable(
                    "house-roof",
                    7.6,
                    5.8,
                    1.7,
                    "slate",
                    cx - 4,
                    cy,
                    h + 3,
                    PI / 2,
                )
                L.bevel(hb, 0.03)
            continue
        dx, dy = c["drum"]
        L.box("ch-roof", w, d, 0.3, "earth", cx, cy, h)
        L.gable(
            "ch-gable",
            10,
            9.8,
            2.5,
            "slate",
            dx,
            dy,
            h,
            PI / 2,
        )
        L.gable(
            "ch-gable", 10, 9.8, 2.5, "slate", dx, dy, h, 0
        )
        drum(dx, dy, h + 1, c.get("band", False))


def drum(dx, dy, b, band):
    """A drum of sixteen sides in courses of light and
    dark stone, a blind arcade round it, narrow
    windows, a moulded cornice and a ribbed cone."""
    r, n, hgt = 2.7, 16, 6.4
    L.lathe(
        "drum-plinth",
        [(2.98, -0.55), (2.98, -0.1), (2.75, 0.0)],
        n,
        "porch",
        dx,
        dy,
        b,
    )
    bm = bmesh.new()
    rows = 14
    ch = hgt / rows
    for row in range(rows):
        lo = []
        hi = []
        for i in range(n):
            a = 2 * PI * i / n
            p = (dx + r * math.sin(a), dy + r * math.cos(a))
            lo.append(bm.verts.new((*p, b + row * ch)))
            hi.append(
                bm.verts.new((*p, b + (row + 1) * ch))
            )
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            f.material_index = (i + row) % 2
    o = L.obj("drum", bm, "porch", "round")
    o.data.materials.append(L.MATS["basalt"])
    holes = Holes("drum")
    rin = r * math.cos(PI / n)
    for i in range(4):
        f = i * PI / 2 + PI / n
        x = dx + rin * math.sin(f)
        y = dy + rin * math.cos(f)
        window(
            holes,
            x,
            y,
            b + 1.2,
            f,
            0.3,
            1.25,
            True,
            0.4,
            None,
        )
    holes.cut(o)
    # the blind arcade
    z0 = b + (2.6 if band else 3.4)
    hc = 2.6 if band else 2.0
    half = r * math.sin(PI / n)
    bm = bmesh.new()
    for i in range(n):
        a = 2 * PI * i / n
        f = a + PI / n
        cxy = Vector(
            (
                dx + (rin + 0.07) * math.sin(f),
                dy + (rin + 0.07) * math.cos(f),
                z0 + hc,
            )
        )
        u = Vector((math.cos(f), -math.sin(f), 0))
        v = Vector((0, 0, 1))
        w = u.cross(v)
        R = half - 0.05
        segs, sides, t = 10, 5, 0.075
        rings = []
        for k in range(segs + 1):
            th = PI * k / segs
            nrm = u * math.cos(th) + v * math.sin(th)
            p = cxy + nrm * R
            ring = []
            for s in range(sides):
                ph = 2 * PI * s / sides
                ring.append(
                    bm.verts.new(
                        p
                        + (
                            nrm * math.cos(ph)
                            + w * math.sin(ph)
                        )
                        * t
                    )
                )
            rings.append(ring)
        for lo, hi in zip(rings, rings[1:]):
            for s in range(sides):
                q = (s + 1) % sides
                bm.faces.new((lo[s], lo[q], hi[q], hi[s]))
    L.obj("arcade-arches", bm, "porch")
    for i in range(n):
        a = 2 * PI * i / n
        L.cyl(
            "arcade-col",
            0.09,
            hc,
            8,
            "porch",
            dx + (r + 0.05) * math.sin(a),
            dy + (r + 0.05) * math.cos(a),
            z0,
        )
    if band:
        L.lathe(
            "drum-band",
            [(2.79, 0), (2.79, 0.18)],
            n,
            "porch",
            dx,
            dy,
            z0 - 0.18,
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
    spire("drum-cone", dx, dy, top + 0.7, 3.15, 5.2, n)


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


def belfry(gx):
    """First stage: a square of stone opened by a
    pointed arch on each side, clustered columns, a
    gable with a rosette over each arch, a spire on
    each corner. Second: eight columns under pointed
    arches round a bell, a ribbed roof, a cross."""
    by, s, sh = 10.9, 7.6, 7.6
    L.box(
        "bel-plinth",
        s + 0.7,
        s + 0.7,
        0.5,
        "porch",
        gx,
        0,
        by - 0.5,
    )
    block = L.box("belfry", s, s, sh, "porch", gx, 0, by)
    holes = Holes("belfry")
    for rz in (0, PI / 2):
        holes.add(
            L.arch(4.2, 6.6, True),
            s + 2,
            L.face(gx, 0, by, rz),
        )
    holes.cut(block)
    L.bevel(block, 0.03)
    for rz in (0, PI / 2, PI, -PI / 2):
        n = n_of(rz)
        t = Vector((n.y, -n.x, 0))
        c = Vector((gx, 0, 0)) + n * (s / 2)
        for sg in (-1, 1):
            for off in (2.35, 2.72):
                p = c + t * sg * off + n * 0.14
                column("bel-col", p.x, p.y, by, 5.8, 0.12)
        # the gable and its rosette
        g = c - n * 0.25
        L.prism(
            "bel-gable",
            [(-s / 2 + 0.2, 0), (s / 2 - 0.2, 0), (0, 2.8)],
            0.5,
            "porch",
            L.face(g.x, g.y, by + sh + 0.45, rz),
        )
        rp = c + n * 0.02
        rosette(rp.x, rp.y, by + sh + 1.3, rz, 0.5)
        # its raking cornice
        for sg in (-1, 1):
            a = c + t * sg * (s / 2 + 0.1) + n * 0.05
            rod(
                "bel-rake",
                (a.x, a.y, by + sh + 0.45),
                (
                    c.x + n.x * 0.05,
                    c.y + n.y * 0.05,
                    by + sh + 3.35,
                ),
                0.12,
                "porch",
            )
    L.mould(
        "bel-cornice",
        L.rect(gx, 0, s, s),
        [
            (0.0, sh - 0.1),
            (0.15, sh + 0.05),
            (0.35, sh + 0.25),
            (0.35, sh + 0.45),
        ],
        "porch",
        by,
    )
    for cx, cy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x = gx + cx * (s / 2 - 0.15)
        y = cy * (s / 2 - 0.15)
        L.box(
            "pinnacle",
            0.8,
            0.8,
            1.7,
            "porch",
            x,
            y,
            by + sh + 0.45,
        )
        spire(
            "pin-spire",
            x,
            y,
            by + sh + 2.15,
            0.55,
            2.0,
            4,
            False,
        )
    # the great bell
    L.lathe(
        "bell",
        [
            (0.0, 0),
            (1.05, 0),
            (1.0, 0.2),
            (0.75, 0.6),
            (0.55, 1.2),
            (0.45, 1.5),
            (0.0, 1.55),
        ],
        24,
        "bronze",
        gx,
        0,
        by + 2.6,
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
    ch = 3.6
    for i in range(8):
        a = i * PI / 4
        column(
            "ring-col",
            gx + ur * math.sin(a),
            ur * math.cos(a),
            top,
            ch,
            0.18,
        )
    ring = L.lathe(
        "ring-arch",
        [(2.85, 0), (2.85, 1.6)],
        8,
        "porch",
        gx,
        0,
        top + ch - 0.9,
    )
    inner = L.lathe(
        "ring-in",
        [(2.2, -1), (2.2, 3)],
        8,
        "porch",
        gx,
        0,
        top + ch - 0.9,
    )
    holes = Holes("ring")
    for i in range(8):
        f = i * PI / 4 + PI / 8
        holes.add(
            L.arch(1.6, 1.4, True),
            2.0,
            L.face(
                gx + 2.6 * math.sin(f),
                2.6 * math.cos(f),
                top + ch - 0.92,
                f,
            ),
        )
    holes.cut(ring)
    L.cut(ring, [inner])
    L.lathe(
        "bell2",
        [
            (0.0, 0),
            (0.6, 0),
            (0.55, 0.12),
            (0.4, 0.4),
            (0.3, 0.8),
            (0.0, 0.85),
        ],
        16,
        "bronze",
        gx,
        0,
        top + 1.4,
    )
    ry = top + ch + 0.7
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
    spire("bel-roof", gx, 0, ry + 0.65, 3.25, 5.6, 8)


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
        for name, (eye, look, lens) in VIEWS.items():
            cam = L.camera(name, eye, look, lens)
            L.render(
                cam, OUT / f"{name}.jpg", size, samples
            )
    if "--glb" in ARGS:
        L.export_glb(OUT / "glakavank.glb")


main()
