"""The church of 1301 at Yeghvard (Kotayk): a model built
in Blender, by script.

    blender -b --factory-startup -P blender/yeghvard.py \\
        -- [--quick] [--no-render] [--views=a,b]

Writes blender/out/yeghvard.blend and renders of the
views of the user's photographs (VIEWS).

Built from the user's photographs of 2026-06-28
(sources/yeghvard/) and what Wikipedia says (twelve
columns in the drum). No size of it is known: every
size here is ESTIMATED from the photographs, all from
one guess, the width of the lower storey (W, 5.6 m,
from the stone courses and the doors); the rest is in
proportion to it, measured on the photographs.

The church: a square lower storey (a burial chapel),
dark basalt below, orange tuff above; a band of chain
between the storeys; above it a cross in plan, four
arms under gables, each face with its own carvings; a
drum of twelve columns, arches and a cone.

The carved figures (the eagle, the lions, the two
figures of the west gable) are the user's photographs
laid on a relief raised from their light and shade:
from afar they read, close they are flat.

Here x is east, y north, z up; metres. An angle rz
says where a face looks: 0 north, pi/2 east. On a
face, s runs to the right of one who looks at it.
"""

import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib as L  # noqa: E402

OUT = L.ROOT / "out"
SRC = L.ROOT.parent / "sources" / "yeghvard"
PI = math.pi
ARGS = (
    sys.argv[sys.argv.index("--") + 1 :]
    if "--" in sys.argv
    else []
)
QUICK = "--quick" in ARGS

# -- the sizes (all estimated, see above) --
W = 5.6  # the lower storey, square
LOW = 5.0  # its height, to the band
BAND = 0.35  # the band of chain
DARK = 2.1  # the basalt at the foot
A = 4.2  # the width of each arm above
UP = LOW + BAND  # the foot of the upper storey
EAVE = 9.2  # the eaves of the arms
RISE = 2.4  # the gables
SLOPE = RISE / (A / 2)
APEX = EAVE + RISE
DRUM_R = 2.0  # the ring under the columns
DRUM_TOP = APEX + 0.5
COL_H = 2.0
COL_RING = 1.72
ARC_H = 0.9  # the arcade over the columns
CONE_H = 3.4

NORTH, EAST, SOUTH, WEST = 0.0, PI / 2, PI, -PI / 2
FACES = (NORTH, EAST, SOUTH, WEST)


def materials():
    res = "1k" if QUICK else "2k"
    L.material(
        "tuff",
        "large_sandstone_blocks",
        3.0,
        (1.45, 1.0, 0.8),
        res,
    )
    L.material(
        "carved",
        "large_sandstone_blocks",
        3.0,
        (1.55, 1.12, 0.92),
        res,
        normal=0.5,
    )
    L.material(
        "basalt",
        "large_sandstone_blocks",
        3.0,
        (0.52, 0.47, 0.45),
        res,
    )
    L.material(
        "roofstone",
        "large_sandstone_blocks",
        1.6,
        (1.05, 0.78, 0.62),
        res,
    )
    L.material(
        "paving",
        "cobblestone_floor_04",
        3.0,
        (0.62, 0.6, 0.6),
        res,
    )
    L.material(
        "grass",
        "withered_grass",
        5.0,
        (0.5, 0.75, 0.3),
        res,
    )
    L.plain("hole", (0.015, 0.013, 0.012), 1.0)
    L.plain("iron", (0.05, 0.05, 0.05), 0.5, 0.6)


# -- places on the faces --


def n_of(rz):
    return Vector((math.sin(rz), math.cos(rz), 0))


def t_of(rz):
    """The face's own x (its u): to the left of one
    who looks at it."""
    return Vector((math.cos(rz), -math.sin(rz), 0))


def wp(rz, s, z, out=0.0, d=W / 2):
    """The point s to the right on the face rz, at
    height z, out from it (the face d from the
    middle)."""
    p = n_of(rz) * (d + out) - t_of(rz) * s
    return Vector((p.x, p.y, z))


def place(rz, s, z, out=0.0, d=W / 2):
    p = wp(rz, s, z, out, d)
    return L.face(p.x, p.y, p.z, rz)


class Holes:
    """Openings to cut: gathered, then cut at once."""

    def __init__(self, name):
        self.name = name
        self.items = []

    def add(self, pts, depth, where):
        self.items.append((pts, depth, where))

    def cut(self, targets):
        if not self.items:
            return
        c = L.prisms(self.name + "-cut", self.items)
        for t in targets:
            L.cut(t, [c])


HOLES = Holes("holes")
CUT = []  # what the holes go through


def rect(w, h):
    return [
        (-w / 2, 0),
        (w / 2, 0),
        (w / 2, h),
        (-w / 2, h),
    ]


def opening(rz, s, z, w, h, shape="rect", deep=0.5):
    """A hole in the face, its sill at z, a dark back
    deep in the wall."""
    pts = (
        rect(w, h)
        if shape == "rect"
        else L.arch(w, h, shape == "pointed")
    )
    HOLES.add(
        pts, deep * 2 + 0.6, place(rz, s, z, -0.3 + 0.3)
    )
    L.prism(
        "back",
        pts,
        0.02,
        "hole",
        place(rz, s, z, -deep),
    )


def raised(name, pts, rz, s, z, out, depth, mat="carved"):
    """A flat shape standing out of the face."""
    return L.prism(
        name, pts, depth, mat, place(rz, s, z, out)
    )


def frame(rz, s, z0, w, h, bw, out, depth, mat="carved"):
    """A flat frame w by h, its bars bw wide, standing
    out of the face round s, from z0."""
    for ds, z, fw, fh in (
        (0.0, z0, w, bw),
        (0.0, z0 + h - bw, w, bw),
        (-(w - bw) / 2, z0 + bw, bw, h - 2 * bw),
        ((w - bw) / 2, z0 + bw, bw, h - 2 * bw),
    ):
        raised(
            "frame",
            rect(fw, fh),
            rz,
            s + ds,
            z,
            out,
            depth,
            mat,
        )


# -- carved work --


def roll(rz, pts, out, r=0.05, closed=False, sides=6):
    """A round moulding along the points [(s, z)] of a
    face."""
    return L.tube(
        "roll",
        [wp(rz, s, z, out) for s, z in pts],
        r,
        "carved",
        sides,
        closed,
    )


def chain(rz, a, b, out=0.08, link=0.42, hgt=0.2):
    """A chain of six-sided links, as carved round the
    frames and in the band, from a to b [(s, z)]."""
    a, b = Vector(a), Vector(b)
    d = b - a
    n = max(1, round(d.length / (link * 0.78)))
    t = d.normalized()
    e = Vector((-t.y, t.x))
    q = link * 0.22
    for i in range(n):
        c = a + d * ((i + 0.5) / n)
        pts = [
            c - t * (link / 2),
            c - t * (link / 2 - q) + e * (hgt / 2),
            c + t * (link / 2 - q) + e * (hgt / 2),
            c + t * (link / 2),
            c + t * (link / 2 - q) - e * (hgt / 2),
            c - t * (link / 2 - q) - e * (hgt / 2),
        ]
        roll(
            rz,
            [(p.x, p.y) for p in pts],
            out,
            0.045,
            True,
            4,
        )


def chain_path(rz, pts, out=0.08, closed=True):
    k = len(pts)
    for i in range(k if closed else k - 1):
        chain(rz, pts[i], pts[(i + 1) % k], out)


def rosette(rz, s, z, r=0.2, out=0.03):
    """A carved rosette: a disc, twelve petals, a
    boss."""
    pl = place(rz, s, z, out)
    disc = [
        (
            r * math.cos(2 * PI * i / 20),
            r * math.sin(2 * PI * i / 20),
        )
        for i in range(20)
    ]
    L.prism("ros", disc, 0.06, "carved", pl)
    items = []
    for i in range(12):
        a = 2 * PI * i / 12
        lens = []
        for j in range(5):
            u = PI * j / 4
            lens.append(
                (
                    0.12 * r + 0.32 * r * (1 - math.cos(u)),
                    0.12 * r * math.sin(u),
                )
            )
        lens += [(u, -v) for u, v in reversed(lens[1:-1])]
        items.append(
            (
                lens,
                0.04,
                pl
                @ Matrix.Translation((0, 0.05, 0))
                @ Matrix.Rotation(a, 4, "Y"),
            )
        )
    L.prisms("ros-petals", items, "carved")


def star(r, k=8, inner=0.62):
    return [
        (
            (r if i % 2 == 0 else r * inner)
            * math.cos(PI * i / k + PI / 2),
            (r if i % 2 == 0 else r * inner)
            * math.sin(PI * i / k + PI / 2),
        )
        for i in range(2 * k)
    ]


def blind_arch(rz, s, z0, h, w=0.8):
    """A blind arch: twin shafts, capitals, a pointed
    arch of interlace, a rosette under it."""
    top = z0 + h
    for side in (-1, 1):
        for k in (-0.065, 0.065):
            p = wp(rz, s + side * w / 2 + k, z0, 0.07)
            L.cyl(
                "shaft", 0.055, h, 8, "carved", p.x, p.y, z0
            )
        c = wp(rz, s + side * w / 2, top, 0.08)
        L.box(
            "capital",
            0.3,
            0.22,
            0.16,
            "carved",
            c.x,
            c.y,
            top,
            -rz,
        )
    arc = L.arch(w, w * 0.62, True)[2:]
    sy = arc[0][1]
    pts = [(s - u, top + 0.16 + v - sy) for u, v in arc]
    roll(rz, pts, 0.1, 0.08, False, 5)
    rosette(rz, s, top + 0.38, 0.13)


def knot(rz, s, z, r=0.22, out=0.08):
    """An interlaced knot: two squares turned."""
    for a in (0.0, PI / 4):
        pts = [
            (
                s + r * math.cos(a + PI / 2 * i),
                z + r * math.sin(a + PI / 2 * i),
            )
            for i in range(4)
        ]
        roll(rz, pts, out, 0.05, True, 4)


# -- carvings from the photographs --


def crop(name, box):
    """A part of a photograph in sources/yeghvard/ as a
    picture of its own (box in pixels, from the top
    left): (picture, its light as an array)."""
    import numpy as np

    src = bpy.data.images.load(str(SRC / name))
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32)
    px = px.reshape(h, w, 4)[::-1]  # rows from the top
    x0, y0, x1, y1 = box
    part = px[y0:y1, x0:x1].copy()
    bpy.data.images.remove(src)
    ph, pw = part.shape[:2]
    img = bpy.data.images.new(
        "relief-" + name[:2] + f"-{x0}", pw, ph
    )
    img.pixels[:] = part[::-1].ravel()
    out = L.CACHE / "yeghvard" / f"{img.name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(out)
    img.file_format = "PNG"
    img.save()
    lum = part[..., :3] @ np.array([0.3, 0.59, 0.11])
    return img, lum


def relief(name, box, rz, s, z, w, depth=0.12, out=0.03):
    """The carving in the photograph name (box) on the
    face rz, its foot at z, w wide: a grid raised by
    its light (the lit stone stands out), the picture
    laid on it, the edge sunk into the wall."""
    import numpy as np

    img, lum = crop(name, box)
    ph, pw = lum.shape
    h = w * ph / pw
    nx = 70
    ny = max(2, round(nx * ph / pw))
    # smooth the light, so the relief is not noise
    k = 5
    pad = np.pad(lum, k, mode="edge")
    cs = pad.cumsum(0).cumsum(1)
    sm = (
        cs[2 * k :, 2 * k :]
        - cs[: -2 * k, 2 * k :]
        - cs[2 * k :, : -2 * k]
        + cs[: -2 * k, : -2 * k]
    ) / (2 * k) ** 2
    sm = (sm - sm.min()) / max(1e-6, np.ptp(sm))
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    vs = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            fu, fv = i / nx, j / ny
            py = min(
                sm.shape[0] - 1, int((1 - fv) * sm.shape[0])
            )
            px = min(sm.shape[1] - 1, int(fu * sm.shape[1]))
            edge = min(fu, 1 - fu, fv, 1 - fv) * 12
            lift = sm[py, px] * min(1.0, edge) * depth
            row.append(
                bm.verts.new(
                    (-(fu - 0.5) * w, lift, fv * h)
                )
            )
        vs.append(row)
    for j in range(ny):
        for i in range(nx):
            f = bm.faces.new(
                (
                    vs[j][i],
                    vs[j][i + 1],
                    vs[j + 1][i + 1],
                    vs[j + 1][i],
                )
            )
            for lp, (di, dj) in zip(
                f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))
            ):
                lp[uvl].uv = ((i + di) / nx, (j + dj) / ny)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.transform(
        bm, matrix=place(rz, s, z, out), verts=bm.verts
    )
    m = bpy.data.materials.new("relief-" + img.name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    # the photograph is lit already: darker
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    mul.inputs[7].default_value = (0.62, 0.55, 0.5, 1)
    nt.links.new(t.outputs[0], mul.inputs[6])
    nt.links.new(mul.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    L.MATS[m.name] = m
    o = L.obj("relief", bm, m.name, "keep")
    # a slab behind it, so no light shows round it
    L.prism(
        "relief-slab",
        rect(w, h),
        0.06,
        "carved",
        place(rz, s, z, out - 0.035),
    )
    return o


# -- the building --


def masses():
    """The walls as solids: the lower square, the
    cross of the arms, their gables."""
    low = L.box("walls-low", W, W, DARK, "basalt", 0, 0, 0)
    mid = L.box(
        "walls-mid", W, W, LOW - DARK, "tuff", 0, 0, DARK
    )
    ew = L.box("arm-ew", W, A, EAVE - UP, "tuff", 0, 0, UP)
    ns = L.box("arm-ns", A, W, EAVE - UP, "tuff", 0, 0, UP)
    g1 = L.gable(
        "gable-ew", W, A, RISE, "tuff", 0, 0, EAVE, PI / 2
    )
    g2 = L.gable(
        "gable-ns", W, A, RISE, "tuff", 0, 0, EAVE, 0
    )
    CUT.extend([low, mid, ew, ns, g1, g2])
    # the band between the storeys, a ledge in the
    # corners of the cross
    L.box(
        "band",
        W + 0.16,
        W + 0.16,
        BAND,
        "carved",
        0,
        0,
        LOW,
    )
    for rz in FACES:
        chain(
            rz,
            (-W / 2 - 0.02, LOW + BAND / 2),
            (W / 2 + 0.02, LOW + BAND / 2),
            0.1,
            0.5,
            0.24,
        )


def roofs():
    """Stone slabs on the gables, a cornice of stars
    under their edges."""
    t, over = 0.2, 0.28
    S = A / 2 + over
    for rz in (0.0, PI / 2):
        for side in (-1, 1):
            pts = [
                (side * S, RISE - S * SLOPE),
                (0.0, RISE),
                (0.0, RISE + t),
                (side * S, RISE + t - S * SLOPE),
            ]
            if side > 0:
                pts = pts[::-1]
            L.prism(
                "roof",
                pts,
                W + 0.3,
                "roofstone",
                L.face(0, 0, EAVE, rz),
            )
    for rz in FACES:
        for side in (-1, 1):
            a = (side * (A / 2 + 0.12), EAVE - 0.06)
            b = (0.0, APEX + 0.06)
            roll(rz, [a, b], 0.16, 0.11, False, 4)
            # the stars along the edge
            ln = (Vector(b) - Vector(a)).length
            k = int(ln / 0.3)
            items = []
            for i in range(1, k):
                c = Vector(a).lerp(Vector(b), i / k)
                items.append(
                    (
                        star(0.1),
                        0.05,
                        place(rz, c.x, c.y - 0.24, 0.03),
                    )
                )
            L.prisms("stars", items, "carved")


def drum():
    """The ring, twelve columns, their arches, the
    cornice, the cone, the cross."""
    base = APEX - 1.4
    L.lathe(
        "drum-ring",
        [
            (DRUM_R, 0),
            (DRUM_R, DRUM_TOP - base - 0.2),
            (DRUM_R + 0.1, DRUM_TOP - base - 0.15),
            (DRUM_R + 0.1, DRUM_TOP - base),
            (0.0, DRUM_TOP - base),
        ],
        36,
        "tuff",
        0,
        0,
        base,
    )
    # a roll of interlace round the ring
    pts = [
        (
            (DRUM_R + 0.04) * math.sin(2 * PI * i / 48),
            (DRUM_R + 0.04) * math.cos(2 * PI * i / 48),
            DRUM_TOP - 0.55,
        )
        for i in range(48)
    ]
    L.tube("drum-roll", pts, 0.06, "carved", 6, True)
    z = DRUM_TOP
    for i in range(12):
        a = 2 * PI * (i + 0.5) / 12
        x, y = (
            COL_RING * math.sin(a),
            COL_RING * math.cos(a),
        )
        r = 0.15
        L.lathe(
            "column",
            [
                (r * 1.5, 0),
                (r * 1.5, 0.14),
                (r, 0.24),
                (r, COL_H - 0.38),
                (r * 1.25, COL_H - 0.3),
                (r * 1.6, COL_H - 0.12),
                (r * 1.6, COL_H),
            ],
            10,
            "carved",
            x,
            y,
            z,
        )
    # the arcade: a ring of stone over the columns,
    # an arch cut between each two
    z1 = z + COL_H
    shell = L.lathe(
        "arcade",
        [
            (DRUM_R - 0.05, 0),
            (DRUM_R - 0.05, ARC_H),
            (0.0, ARC_H),
        ],
        48,
        "tuff",
        0,
        0,
        z1,
    )
    inner = L.lathe(
        "arcade-in",
        [
            (DRUM_R - 0.4, -0.1),
            (DRUM_R - 0.4, ARC_H - 0.25),
            (0.0, ARC_H - 0.05),
        ],
        48,
        None,
        0,
        0,
        z1,
    )
    items = []
    for i in range(12):
        a = 2 * PI * i / 12
        w = 2 * PI * COL_RING / 12 - 0.3
        pts = [(-w / 2, -0.2)] + [
            (u, v) for u, v in L.arch(w, 0.62, False)[1:]
        ]
        pts[1] = (w / 2, -0.2)
        rot = Matrix.Rotation(-a, 4, "Z")
        items.append(
            (
                pts,
                1.2,
                rot
                @ Matrix.Translation((0, DRUM_R - 0.2, z1)),
            )
        )
    cutter = L.prisms("arcade-cut", items)
    L.cut(shell, [cutter, inner])
    # the arches carved round the openings
    for i in range(12):
        a = 2 * PI * i / 12
        w = 2 * PI * COL_RING / 12
        arc = L.arch(w - 0.3, 0.62, False)[2:]
        pts = []
        for u, v in arc:
            q = a - u / (DRUM_R + 0.02)
            pts.append(
                (
                    (DRUM_R + 0.0) * math.sin(q),
                    (DRUM_R + 0.0) * math.cos(q),
                    z1 + v,
                )
            )
        L.tube("arch-roll", pts, 0.05, "carved", 5)
    # the inside, dark, seen between the columns
    L.cyl(
        "drum-in",
        COL_RING - 0.45,
        COL_H + 0.1,
        16,
        "hole",
        0,
        0,
        z,
    )
    z2 = z1 + ARC_H
    L.lathe(
        "cornice",
        [
            (DRUM_R - 0.05, 0),
            (DRUM_R + 0.12, 0.12),
            (DRUM_R + 0.2, 0.3),
            (0.0, 0.3),
        ],
        48,
        "carved",
        0,
        0,
        z2,
    )
    # the cone of stone slabs, a little curved
    z3 = z2 + 0.3
    prof = [(DRUM_R + 0.28, -0.08)]
    for i in range(9):
        f = i / 8
        prof.append(
            (
                (DRUM_R + 0.25) * (1 - f) ** 1.1,
                CONE_H * f,
            )
        )
    prof[-1] = (0.0, CONE_H)
    L.lathe("cone", prof, 24, "roofstone", 0, 0, z3)
    top = z3 + CONE_H
    L.lathe(
        "ball",
        [
            (0.0, -0.1),
            (0.16, 0.0),
            (0.22, 0.18),
            (0.16, 0.36),
            (0.0, 0.42),
        ],
        12,
        "carved",
        0,
        0,
        top - 0.1,
    )
    L.box("cross", 0.06, 0.06, 1.0, "iron", 0, 0, top + 0.3)
    L.box("cross", 0.6, 0.06, 0.06, "iron", 0, 0, top + 1.0)
    # the rays of the cross, as in the photograph
    for k in range(8):
        a = PI * k / 4
        p = Vector((0.22 * math.cos(a), 0, top + 1.03))
        p.z += 0.22 * math.sin(a)
        L.box(
            "ray",
            0.03,
            0.03,
            0.03,
            "iron",
            p.x,
            p.y,
            p.z,
        )


# -- the faces --


def upper_frame(rz, z0, z1, w, tab, z2):
    """The frame of chain round the middle of an
    upper face: a rectangle, a narrower step on top
    (the outline of a cross)."""
    pts = [
        (-w / 2, z0),
        (w / 2, z0),
        (w / 2, z1),
        (tab / 2, z1),
        (tab / 2, z2),
        (-tab / 2, z2),
        (-tab / 2, z1),
        (-w / 2, z1),
    ]
    chain_path(rz, pts)


def arm_common(rz):
    """What every arm has: two blind arches."""
    for s in (-1.55, 1.55):
        blind_arch(rz, s, UP + 0.15, EAVE - UP - 0.75)


def big_arch(rz):
    """The large round arch of interlace (north,
    east), from the inner shafts of the blind
    arches up into the gable."""
    w = 2 * (1.55 - 0.4)
    spring = EAVE - 0.6 + 0.16
    arc = L.arch(w, w / 2, False)[2:]
    pts = [(-u, spring + v) for u, v in arc]
    roll(rz, pts, 0.1, 0.09, False, 5)


def north():
    rz = NORTH
    arm_common(rz)
    big_arch(rz)
    upper_frame(
        rz, UP + 0.6, EAVE - 0.7, 1.7, 0.9, EAVE + 0.1
    )
    relief(
        "26-north-relief.jpg",
        (180, 400, 560, 700),
        rz,
        0.0,
        UP + 2.05,
        1.15,
    )
    rosette(rz, 0.0, EAVE - 0.3, 0.2)
    opening(rz, 0.0, UP + 0.85, 0.2, 0.85, "round", 0.6)
    roll(
        rz,
        [
            (u, UP + 0.75 + v)
            for u, v in L.arch(0.7, 1.25)[2:]
        ],
        0.08,
        0.06,
    )
    knot(rz, 0.0, UP + 0.3)
    lower_cross(rz)


def south():
    rz = SOUTH
    arm_common(rz)
    # a round arch of chain over the eagle
    chain_path(
        rz,
        [(-0.95, UP + 0.45), (-0.95, EAVE - 0.4)],
        closed=False,
    )
    chain_path(
        rz,
        [(0.95, UP + 0.45), (0.95, EAVE - 0.4)],
        closed=False,
    )
    arc = L.arch(1.9, 0.95, False)[2:]
    pts = [(-u, EAVE - 0.4 + v) for u, v in arc]
    for p, q in zip(pts[::2], pts[2::2]):
        chain(rz, p, q)
    relief(
        "30-south-eagle.jpg",
        (250, 370, 600, 890),
        rz,
        0.0,
        UP + 2.15,
        1.2,
    )
    # the window split by a column
    zw = UP + 0.5
    opening(rz, 0.0, zw, 0.78, 1.3, "rect", 0.6)
    p = wp(rz, 0.0, zw, -0.15)
    L.cyl(
        "win-column", 0.08, 1.1, 10, "carved", p.x, p.y, zw
    )
    L.box(
        "win-capital",
        0.3,
        0.3,
        0.2,
        "carved",
        p.x,
        p.y,
        zw + 1.1,
        -rz,
    )
    frame(rz, 0.0, zw - 0.15, 1.15, 1.6, 0.17, 0.04, 0.08)
    knot(rz, 0.0, UP + 0.18, 0.15)
    lower_cross(rz)


def east():
    rz = EAST
    arm_common(rz)
    big_arch(rz)
    upper_frame(
        rz, UP + 0.6, EAVE - 0.7, 1.7, 0.9, EAVE + 0.1
    )
    relief(
        "34-east-relief.jpg",
        (250, 360, 520, 610),
        rz,
        0.0,
        UP + 2.05,
        1.0,
    )
    rosette(rz, 0.0, EAVE - 0.3, 0.2)
    # the slit window in its four-lobed frame
    opening(rz, 0.0, UP + 0.9, 0.2, 0.8, "round", 0.6)
    lobes = []
    for i in range(48):
        a = 2 * PI * i / 48
        r = 0.62 + 0.14 * math.cos(4 * a)
        lobes.append(
            (
                r * math.sin(a) * 0.85,
                UP + 1.3 + r * math.cos(a),
            )
        )
    roll(rz, lobes, 0.08, 0.07, True, 6)
    knot(rz, 0.0, UP + 0.3, 0.16)
    # below: a rib down the wall, a double rosette, a
    # small window in stepped frames, two slits
    roll(rz, [(0, LOW - 0.05), (0, 3.65)], 0.04, 0.06)
    for s in (-0.22, 0.22):
        rosette(rz, s, 3.4, 0.17)
        roll(
            rz,
            [
                (
                    s + 0.21 * math.cos(2 * PI * i / 20),
                    3.4 + 0.21 * math.sin(2 * PI * i / 20),
                )
                for i in range(20)
            ],
            0.04,
            0.04,
            True,
        )
    roll(rz, [(0, 3.15), (0, 2.45)], 0.04, 0.06)
    for k, size in enumerate((0.95, 0.75, 0.55)):
        frame(
            rz,
            0.0,
            1.45 + (0.95 - size) / 2,
            size,
            size,
            0.09,
            0.06 - 0.02 * k,
            0.08,
        )
    opening(rz, 0.0, 1.6, 0.14, 0.55, "rect", 0.5)
    for s in (-1.75, 1.75):
        opening(rz, s, 1.7, 0.12, 0.5, "round", 0.5)


def west():
    rz = WEST
    arm_common(rz)
    # the high door: a square opening, a niche over it
    # with a stalactite head, frames of stars and of
    # chain, a corbel under it (the stairs were wood)
    dw, dh = 1.05, 1.4
    opening(rz, 0.0, UP, dw, dh, "rect", 0.9)
    HOLES.add(
        L.arch(dw, 0.85, True),
        0.5,
        place(rz, 0.0, UP + dh, 0.0),
    )
    L.prism(
        "niche-back",
        L.arch(dw, 0.85, True),
        0.02,
        "carved",
        place(rz, 0.0, UP + dh, -0.24),
    )
    for k in range(3):
        p = wp(rz, 0.0, UP + dh + 0.05 + 0.2 * k, -0.12)
        L.lathe(
            "stalactite",
            [
                (0.0, 0.0),
                (0.42 - 0.12 * k, 0.12),
                (0.0, 0.32),
            ],
            6,
            "carved",
            p.x,
            p.y,
            p.z,
        )
    frame(rz, 0.0, UP - 0.1, 1.75, 2.6, 0.35, 0.03, 0.08)
    items = []
    for k in range(7):
        for s in (-0.69, 0.69):
            items.append(
                (
                    star(0.15),
                    0.05,
                    place(rz, s, UP + 0.2 + k * 0.33, 0.08),
                )
            )
    for k in range(5):
        items.append(
            (
                star(0.15),
                0.05,
                place(
                    rz, -0.66 + k * 0.33, UP + 2.32, 0.08
                ),
            )
        )
    L.prisms("stars", items, "carved")
    for k, (w, h) in enumerate(((2.1, 2.75), (2.5, 2.95))):
        pts = [
            (-w / 2, UP),
            (-w / 2, UP + h),
            (w / 2, UP + h),
            (w / 2, UP),
        ]
        if k == 0:
            roll(rz, pts, 0.1, 0.06)
        else:
            chain_path(rz, pts, 0.1, closed=False)
    p = wp(rz, 0.0, UP - 0.55, 0.3)
    L.box(
        "corbel",
        1.3,
        0.6,
        0.55,
        "basalt",
        p.x,
        p.y,
        p.z,
        -rz,
    )
    for s, z in (
        (-0.55, LOW - 1.0),
        (0.55, LOW - 1.0),
        (0.0, LOW - 1.45),
    ):
        p = wp(rz, s, z, 0.05)
        L.box(
            "stair-stone",
            0.55,
            0.1,
            0.42,
            "tuff",
            p.x,
            p.y,
            z,
            -rz,
        )
    # the two lions on bulls over the door
    relief(
        "20-west-upper-door-lions.jpg",
        (145, 100, 315, 195),
        rz,
        -0.72,
        UP + 3.0,
        0.95,
        0.08,
    )
    relief(
        "20-west-upper-door-lions.jpg",
        (420, 95, 590, 195),
        rz,
        0.72,
        UP + 3.0,
        0.95,
        0.08,
    )
    # the cross of chain in the gable, the two figures
    chain(rz, (0.0, UP + 2.95), (0.0, APEX - 0.35))
    chain(rz, (-1.4, EAVE + 0.25), (1.4, EAVE + 0.25))
    for s, z in (
        (0.0, APEX - 0.45),
        (-1.45, EAVE + 0.25),
        (1.45, EAVE + 0.25),
    ):
        knot(rz, s, z, 0.17)
    relief(
        "15-west-gable-figures.jpg",
        (70, 320, 280, 640),
        rz,
        -0.62,
        EAVE + 0.42,
        0.42,
        0.08,
    )
    relief(
        "15-west-gable-figures.jpg",
        (500, 360, 690, 670),
        rz,
        0.62,
        EAVE + 0.42,
        0.38,
        0.08,
    )
    # small cross-stones and the inscription beside
    # the door
    for s in (-1.75, -1.42):
        for z in (UP + 0.6, UP + 1.25):
            raised(
                "khachkar",
                rect(0.28, 0.5),
                rz,
                s,
                z,
                0.02,
                0.05,
            )
            raised(
                "kh-cross",
                [
                    (-0.03, 0.06),
                    (0.03, 0.06),
                    (0.03, 0.27),
                    (0.09, 0.27),
                    (0.09, 0.33),
                    (0.03, 0.33),
                    (0.03, 0.44),
                    (-0.03, 0.44),
                    (-0.03, 0.33),
                    (-0.09, 0.33),
                    (-0.09, 0.27),
                    (-0.03, 0.27),
                ],
                rz,
                s,
                z,
                0.05,
                0.03,
            )
    raised(
        "inscription",
        rect(0.7, 0.9),
        rz,
        -1.58,
        UP + 1.85,
        0.015,
        0.03,
    )
    # the door of the lower storey, round-headed in a
    # dark frame
    opening(rz, 0.0, 0.0, 1.0, 2.25, "round", 0.6)
    for w, h, out in ((1.2, 2.45, 0.06), (1.45, 2.6, 0.09)):
        pts = [(-u, v) for u, v in L.arch(w, h)[2:]]
        pts = [(-w / 2, 0.0)] + pts + [(w / 2, 0.0)]
        roll(rz, pts, out, 0.07, False, 6)


def lower_cross(rz):
    """The cross-shaped frame round the slit window of
    the lower storey (north, south), carved with a
    lattice."""
    a, b = 0.55, 1.0
    pts = [
        (-a / 2, -b),
        (a / 2, -b),
        (a / 2, -a / 2),
        (b, -a / 2),
        (b, a / 2),
        (a / 2, a / 2),
        (a / 2, b),
        (-a / 2, b),
        (-a / 2, a / 2),
        (-b, a / 2),
        (-b, -a / 2),
        (-a / 2, -a / 2),
    ]
    zc = 3.4
    fr = L.prism(
        "cross-frame",
        [(u, zc + v) for u, v in pts],
        0.14,
        "carved",
        place(rz, 0.0, 0.0, 0.0),
    )
    CUT.append(fr)
    outline = [(u * 1.12, zc + v * 1.12) for u, v in pts]
    roll(rz, outline, 0.08, 0.05, True, 5)
    opening(rz, 0.0, zc - 0.45, 0.16, 0.7, "round", 0.6)


def mottle(rz, seed):
    """Light stones in the dark foot of a wall, dark
    ones in the light, as on the walls."""
    r = random.Random(seed)
    for _ in range(10):
        s = r.uniform(-W / 2 + 0.4, W / 2 - 0.4)
        if abs(s) < 1.25:
            continue
        z = 0.45 * r.randrange(1, int((DARK + 0.9) / 0.45))
        mat = "tuff" if z < DARK else "basalt"
        p = wp(rz, s, z, 0.01)
        L.box(
            "stone",
            r.choice((0.4, 0.5, 0.65)),
            0.04,
            0.43,
            mat,
            p.x,
            p.y,
            z,
            -rz,
        )


def ground():
    L.box("paving", 16, 16, 0.1, "paving", 0, 0, -0.1)
    L.box("path", 30, 3.2, 0.1, "paving", 23, 0, -0.11)
    L.box("grass", 300, 300, 0.1, "grass", 0, 0, -0.14)
    # a step round the foot of the walls
    L.box(
        "plinth", W + 0.3, W + 0.3, 0.12, "basalt", 0, 0, 0
    )


# the views of the photographs: eye, look, lens
VIEWS = {
    # 02: from the path, the east side
    "east": ((19, -1.5, 1.5), (0, 0, 9.5), 22),
    # 23: the north side and the west door
    "north": ((-5, 13, 1.5), (0, 0, 7.5), 20),
    # 31: the south side
    "south": ((3, -13, 1.5), (0, 0, 7.5), 20),
    # 13, 14: the west front
    "west": ((-12, -0.5, 2.0), (0, 0, 8.5), 22),
    "overview": ((20, -24, 15), (0, 0, 8.5), 32),
    "drum": ((7, -9, 13), (0, 0, 13.5), 32),
    # close views, to check the details
    "north-low": ((-1, 9, 2.5), (0, 0, 3.2), 35),
    "south-up": ((1, -10, 6), (0, 0, 8), 35),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L.reset()
    materials()
    masses()
    roofs()
    drum()
    north()
    south()
    east()
    west()
    for i, rz in enumerate(FACES):
        mottle(rz, i)
    HOLES.cut(CUT)
    ground()
    L.finish(join=True)
    L.sky("kloofendal_48d_partly_cloudy_puresky", 1.0, 0.6)
    # a June morning, about ten
    L.sun(105, 55, 4.5)
    bpy.ops.wm.save_as_mainfile(
        filepath=str(OUT / "yeghvard.blend")
    )
    if "--no-render" in ARGS:
        return
    size = (600, 800) if QUICK else (1200, 1600)
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
            cam, OUT / f"yeghvard-{name}.jpg", size, samples
        )


main()
