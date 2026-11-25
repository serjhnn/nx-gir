"""Helpers for the Blender models of nx-gir (blender/).

Run inside Blender (bpy), headless: see README.md.
Textures and skies come from Poly Haven (CC0) and are
kept in blender/cache/ (not in git). Blender works in
metres with z up; here x is east and y north.

The shapes are made with bmesh in world coordinates
(objects stay at the origin), so the texture
coordinates can be set in metres from the faces
(uv_box(), uv_round()) and a stone is the same size
on every wall.
"""

import json
import math
import os
import urllib.request
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
API = "https://api.polyhaven.com/files/"
UA = {"User-Agent": "nx-gir-blender/1.0"}


# -- the cache of textures and skies --


def get(url, path):
    """The file at url, kept at path."""
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req) as r:
            data = r.read()
        path.write_bytes(data)
    return path


def info(pid):
    path = CACHE / "info" / f"{pid}.json"
    get(API + pid, path)
    return json.loads(path.read_text())


def texture(pid, res="2k"):
    """The colour, normal and roughness maps of a
    Poly Haven texture: {"diff", "nor", "rough"}."""
    d = info(pid)
    out = {}
    for key, name in (
        ("Diffuse", "diff"),
        ("nor_gl", "nor"),
        ("Rough", "rough"),
    ):
        url = d[key][res]["jpg"]["url"]
        out[name] = get(
            url, CACHE / "tex" / pid / f"{name}_{res}.jpg"
        )
    return out


def hdri(pid, res="2k"):
    url = info(pid)["hdri"][res]["hdr"]["url"]
    return get(url, CACHE / "hdri" / f"{pid}_{res}.hdr")


# -- the scene --


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    return sc


def sky(pid, strength=1.0, rot=0.0):
    """The world lit by a sky photograph (HDRI)."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(hdri(pid)))
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, rot)
    nt.links.new(tc.outputs["Generated"], mp.inputs[0])
    nt.links.new(mp.outputs[0], env.inputs[0])
    nt.links.new(env.outputs[0], bg.inputs[0])
    bg.inputs["Strength"].default_value = strength
    return w


def sun(azimuth, elevation, strength=4.0, angle=0.6):
    """A sun from azimuth (degrees from north, to the
    east) and elevation (degrees)."""
    d = bpy.data.lights.new("sun", "SUN")
    d.energy = strength
    d.angle = math.radians(angle)
    o = bpy.data.objects.new("sun", d)
    bpy.context.scene.collection.objects.link(o)
    az = math.radians(azimuth)
    el = math.radians(elevation)
    # the light points away from where the sun is
    to = Vector(
        (
            -math.sin(az) * math.cos(el),
            -math.cos(az) * math.cos(el),
            -math.sin(el),
        )
    )
    o.rotation_euler = to.to_track_quat(
        "-Z", "Y"
    ).to_euler()
    return o


def camera(name, eye, look, lens=35):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    c.clip_end = 6000
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    o.location = eye
    d = Vector(look) - Vector(eye)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o


def render(cam, path, size=(1200, 900), samples=64):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# -- materials --

MATS = {}


def tinted(path, rgb):
    """A copy of the colour map at path, its colours
    multiplied by rgb (0 to 1 each)."""
    import numpy as np

    key = "_".join(f"{c:.2f}" for c in rgb)
    out = path.with_name(f"{path.stem}_t{key}.jpg")
    if out.exists():
        return out
    img = bpy.data.images.load(str(path))
    px = np.array(img.pixels[:], dtype=np.float32)
    px = px.reshape(-1, 4)
    px[:, :3] *= np.array(rgb, dtype=np.float32)
    img.pixels[:] = px.ravel().clip(0, 1)
    img.filepath_raw = str(out)
    img.file_format = "JPEG"
    img.save()
    bpy.data.images.remove(img)
    return out


def material(
    name,
    pid,
    size,
    tint=None,
    res="2k",
    rough=None,
    normal=1.0,
):
    """A stone (or other) material from a Poly Haven
    texture; one picture covers size metres."""
    tex = texture(pid, res)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (
        1 / size,
        1 / size,
        1,
    )
    nt.links.new(tc.outputs["UV"], mp.inputs[0])

    def img(path, color, kind):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(str(path))
        # to find the smaller picture for the web
        n.image["src"] = [
            pid,
            kind,
            list(tint or []) if kind == "diff" else [],
        ]
        if not color:
            n.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs[0], n.inputs[0])
        return n

    diff = tex["diff"]
    if tint:
        diff = tinted(diff, tint)
    d = img(diff, True, "diff")
    nt.links.new(d.outputs[0], bsdf.inputs["Base Color"])
    r = img(tex["rough"], False, "rough")
    nt.links.new(r.outputs[0], bsdf.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = normal
    nn = img(tex["nor"], False, "nor")
    nt.links.new(nn.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], bsdf.inputs["Normal"])
    MATS[name] = m
    return m


def plain(name, rgb, rough=0.8, metal=0.0):
    """A material of one colour."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    MATS[name] = m
    return m


# -- shapes: meshes in world coordinates --


def obj(name, bm, mat, uv="box"):
    """A new object of the bmesh bm, with mat; uv is
    how its texture is laid: "box" or "round"."""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if mat:
        o.data.materials.append(MATS[mat])
    o["uv"] = uv
    return o


def box(name, w, d, h, mat, x, y, z=0.0, rz=0.0):
    """A box w (x) by d (y) by h, standing on z."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    m = (
        Matrix.Translation((x, y, z + h / 2))
        @ Matrix.Rotation(rz, 4, "Z")
        @ Matrix.Diagonal((w, d, h, 1))
    )
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return obj(name, bm, mat)


def lathe(name, prof, n, mat, x, y, z=0.0, rz=0.0):
    """A round (or n-sided) shape turned from prof:
    [(radius, height), ...] from the bottom up; ends
    closed where the radius is 0, capped otherwise."""
    bm = bmesh.new()
    rings = []
    for r, h in prof:
        ring = []
        for i in range(n):
            a = rz + 2 * math.pi * i / n
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
    for lo, hi in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(name, bm, mat, "round")


def cyl(name, r, h, n, mat, x, y, z=0.0, r2=None):
    r2 = r if r2 is None else r2
    return lathe(name, [(r, 0), (r2, h)], n, mat, x, y, z)


def cone(name, r, h, n, mat, x, y, z=0.0):
    return lathe(name, [(r, 0), (0.0, h)], n, mat, x, y, z)


def arch(w, h, pointed=False, n=12):
    """The outline of an opening w wide and h high
    (to the top of its arch), from its sill: points
    round it, counter-clockwise, as (u, v)."""
    r = w / 2
    if not pointed:
        sy = h - r
        pts = [(-r, 0.0), (r, 0.0)]
        for i in range(n + 1):
            a = math.pi * i / n
            pts.append(
                (r * math.cos(a), sy + r * math.sin(a))
            )
        return pts
    big = w * 0.75
    th = math.acos((r - big) / big)
    sy = h - big * math.sin(th)
    pts = [(-r, 0.0), (r, 0.0)]
    # the right arc, centre (r - big, sy), from 0 up
    for i in range(n + 1):
        a = (math.pi - th) * i / n
        pts.append(
            (
                r - big + big * math.cos(a),
                sy + big * math.sin(a),
            )
        )
    # the left arc, centre (big - r, sy), to pi
    for i in range(1, n + 1):
        a = th + (math.pi - th) * i / n
        pts.append(
            (
                big - r + big * math.cos(a),
                sy + big * math.sin(a),
            )
        )
    return pts


def foil(w, h, lobes=5, n=8):
    """The outline of a cusped (many-lobed) arch w
    wide and h high, from its sill: a round arch
    whose head is cut into lobes, points between."""
    r = w / 2
    sy = h - r
    pts = [(-r, 0.0), (r, 0.0)]
    k = lobes * n
    for i in range(k + 1):
        a = math.pi * i / k
        f = math.sin(math.pi * (i % n) / n)
        rr = r * (0.78 + 0.22 * f)
        if i in (0, k):
            rr = r
        pts.append(
            (rr * math.cos(a), sy + rr * math.sin(a))
        )
    return pts


def tube(name, pts, r, mat, sides=6, closed=False):
    """A round moulding (a roll) swept along the
    points pts [(x, y, z), ...]."""
    bm = bmesh.new()
    pts = [Vector(p) for p in pts]
    k = len(pts)
    rings = []
    for i, p in enumerate(pts):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % k]
        else:
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, k - 1)]
        t = (b - a).normalized()
        up = Vector((0, 0, 1))
        if abs(t.dot(up)) > 0.9:
            up = Vector((1, 0, 0))
        u = t.cross(up).normalized()
        v = u.cross(t).normalized()
        rings.append(
            [
                bm.verts.new(
                    p
                    + (
                        u
                        * math.cos(2 * math.pi * s / sides)
                        + v
                        * math.sin(2 * math.pi * s / sides)
                    )
                    * r
                )
                for s in range(sides)
            ]
        )
    pairs = list(zip(rings, rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for lo, hi in pairs:
        for s in range(sides):
            q = (s + 1) % sides
            bm.faces.new((lo[s], lo[q], hi[q], hi[s]))
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(name, bm, mat)


def on_face(pts, place, out=0.0):
    """The points [(u, v)] of an outline on a face
    (as in prism) in the world, out from the face."""
    return [place @ Vector((u, out, v)) for u, v in pts]


def prism(name, pts, depth, mat, place, uv="box"):
    """The outline pts [(u, v), ...] made solid, depth
    thick (from -depth/2 to depth/2), then put in the
    world by the matrix place: u along its x, v up its
    z, depth along its y."""
    bm = bmesh.new()
    front = [
        bm.verts.new((u, -depth / 2, v)) for u, v in pts
    ]
    back = [bm.verts.new((u, depth / 2, v)) for u, v in pts]
    k = len(pts)
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((front[j], front[i], back[i], back[j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=place, verts=bm.verts)
    return obj(name, bm, mat, uv)


def prisms(name, items, mat=None):
    """Many prisms in one object (to cut many holes
    at once): items [(pts, depth, place), ...]."""
    bm = bmesh.new()
    for pts, depth, place in items:
        vs = []
        front = [
            bm.verts.new((u, -depth / 2, v)) for u, v in pts
        ]
        back = [
            bm.verts.new((u, depth / 2, v)) for u, v in pts
        ]
        vs = front + back
        k = len(pts)
        bm.faces.new(front)
        bm.faces.new(list(reversed(back)))
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new(
                (front[j], front[i], back[i], back[j])
            )
        bmesh.ops.transform(bm, matrix=place, verts=vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(name, bm, mat)


def face(x, y, z, rz):
    """The matrix that stands a prism on a wall face
    at x, y, z: its depth along the face's normal,
    which looks to rz (radians from north (+y),
    turning east)."""
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(
        -rz, 4, "Z"
    )


def mould(name, outline, prof, mat, z=0.0):
    """A moulding round a convex outline [(x, y)]
    (counter-clockwise): prof [(out, up), ...] from
    the bottom, out how far it stands from the
    outline, up its height."""
    bm = bmesh.new()
    k = len(outline)
    cx = sum(p[0] for p in outline) / k
    cy = sum(p[1] for p in outline) / k

    def grow(p, d):
        # move each corner out along its bisector,
        # so the sides move out by d
        out = []
        for i in range(k):
            a = Vector(outline[i - 1])
            b = Vector(outline[i])
            c = Vector(outline[(i + 1) % k])
            n1 = Vector((b - a).yx) * Vector((1, -1))
            n2 = Vector((c - b).yx) * Vector((1, -1))
            n1.normalize()
            n2.normalize()
            m = (n1 + n2).normalized()
            out.append(b + m * (d / max(0.2, m.dot(n1))))
        return out

    rings = []
    for o, u in prof:
        pts = grow(outline, o)
        rings.append(
            [bm.verts.new((p.x, p.y, z + u)) for p in pts]
        )
    for lo, hi in zip(rings, rings[1:]):
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    del cx, cy
    return obj(name, bm, mat)


def rect(x, y, w, d):
    """A rectangle w by d round x, y, counter-clockwise."""
    return [
        (x - w / 2, y - d / 2),
        (x + w / 2, y - d / 2),
        (x + w / 2, y + d / 2),
        (x - w / 2, y + d / 2),
    ]


def ngon(x, y, r, n, rz=0.0):
    return [
        (
            x + r * math.sin(rz + 2 * math.pi * i / n),
            y + r * math.cos(rz + 2 * math.pi * i / n),
        )
        for i in reversed(range(n))
    ]


def gable(name, length, span, rise, mat, x, y, z, rz=0.0):
    """A roof of two slopes: its ridge length long,
    along rz (0: north-south), span wide, rise high."""
    pts = [(-span / 2, 0.0), (span / 2, 0.0), (0.0, rise)]
    place = face(x, y, z, rz)
    return prism(name, pts, length, mat, place)


# -- cutting and finishing --


def cut(target, cutters):
    """Holes in target where cutters are (exact
    boolean); the cutters are removed in finish()."""
    for c in cutters:
        m = target.modifiers.new("cut", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.solver = "EXACT"
        m.use_self = True
        m.object = c
        c["cutter"] = True
        c.hide_render = True
        c.display_type = "WIRE"
    return target


def bevel(o, width=0.03, segs=1):
    m = o.modifiers.new("bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(35)
    m.harden_normals = False
    return o


def apply_all(o):
    with bpy.context.temp_override(
        object=o, active_object=o, selected_objects=[o]
    ):
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)


def uv_set(o):
    """Texture coordinates in metres: box (each face
    from the axis it faces most) or round (around a
    vertical axis through the object's middle)."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.loops.layers.uv.verify()
    mode = o.get("uv", "box")
    if mode == "round":
        xs = [v.co.x for v in bm.verts]
        ys = [v.co.y for v in bm.verts]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        r = max(0.1, (max(xs) - min(xs)) / 2)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            c = lp.vert.co
            if mode == "round" and ax != 2:
                a = math.atan2(c.x - cx, c.y - cy)
                lp[lay].uv = (a * r, c.z)
            elif ax == 2:
                lp[lay].uv = (c.x, c.y)
            elif ax == 0:
                lp[lay].uv = (c.y, c.z)
            else:
                lp[lay].uv = (c.x, c.z)
    # one face that crosses the seam of a round
    # object: keep its u together
    if mode == "round":
        for f in bm.faces:
            us = [lp[lay].uv.x for lp in f.loops]
            if max(us) - min(us) > math.pi * r:
                for lp in f.loops:
                    if lp[lay].uv.x < 0:
                        lp[lay].uv.x += 2 * math.pi * r
    bm.to_mesh(me)
    bm.free()


def smooth(o, angle=40):
    """Smooth shading on o, sharp edges kept."""
    with bpy.context.temp_override(
        object=o, active_object=o, selected_objects=[o]
    ):
        bpy.ops.object.shade_smooth_by_angle(
            angle=math.radians(angle)
        )


def finish(join=True):
    """Apply the cuts and bevels, lay the textures,
    remove the cutters; then join the objects of each
    material into one (fewer pieces to draw)."""
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in objs:
        if not o.get("cutter"):
            apply_all(o)
    for o in objs:
        if o.get("cutter"):
            bpy.data.objects.remove(o)
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in list(objs):
        # a cut that took everything (a bad boolean)
        if not o.data.vertices:
            print("empty after cutting:", o.name)
            bpy.data.objects.remove(o)
            objs.remove(o)
    for o in objs:
        uv_set(o)
        if o.get("uv") == "round":
            smooth(o)
    if os.environ.get("NXGIR_COUNT"):
        top = sorted(
            objs, key=lambda o: -len(o.data.vertices)
        )
        by = {}
        for o in objs:
            k = o.name.split(".")[0]
            by[k] = by.get(k, 0) + len(o.data.vertices)
        for k, n in sorted(by.items(), key=lambda x: -x[1])[
            :25
        ]:
            print("COUNT", k, n)
        del top
    if not join:
        return objs
    by = {}
    for o in objs:
        key = (
            o.data.materials[0].name
            if o.data.materials
            else ""
        )
        by.setdefault(key, []).append(o)
    out = []
    for key, group in by.items():
        first = group[0]
        with bpy.context.temp_override(
            active_object=first,
            object=first,
            selected_objects=group,
            selected_editable_objects=group,
        ):
            bpy.ops.object.join()
        first.name = key or "mesh"
        out.append(first)
    return out


def export_glb(path, res="1k"):
    """The scene as one .glb file for the web: its
    textures swapped for the smaller ones (res), the
    meshes squeezed (Draco)."""
    for im in bpy.data.images:
        if "src" not in im:
            continue
        pid, kind, tint = im["src"]
        small = texture(pid, res)[kind]
        if tint:
            small = tinted(small, list(tint))
        im.filepath = str(small)
        im.reload()
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_image_format="JPEG",
        export_cameras=False,
        export_lights=False,
    )


def export_web(folder, skip=(), size=512, rough=0.9):
    """The scene for the web page: a .gltf with its
    .bin and its textures as separate files in folder
    (the page's rules forbid the blob: addresses a
    single .glb would need), no Draco (its decoder
    runs in a blob: worker); textures size pixels
    square, colour and relief only (a roughness of
    rough instead of a map); the objects named in
    skip left out (the page draws its own ground)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for f in folder.iterdir():
        f.unlink()
    for name in skip:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o)
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        nt = m.node_tree
        b = nt.nodes.get("Principled BSDF")
        if not b:
            continue
        r = b.inputs["Roughness"]
        for lk in list(r.links):
            nt.links.remove(lk)
        r.default_value = rough
    done = {}
    for im in list(bpy.data.images):
        if "src" not in im:
            continue
        pid, kind, tint = im["src"]
        if kind == "rough":
            continue
        key = (pid, kind, tuple(tint))
        if key not in done:
            src = texture(pid, "1k")[kind]
            if tint:
                src = tinted(src, list(tint))
            small = bpy.data.images.load(str(src))
            small.scale(size, size)
            name = f"{pid}-{kind}"
            if tint:
                name += "-" + "-".join(
                    f"{round(c * 100)}" for c in tint
                )
            out = CACHE / "web" / f"{name}.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            small.filepath_raw = str(out)
            small.file_format = "JPEG"
            small.save()
            bpy.data.images.remove(small)
            done[key] = (out, name)
        out, name = done[key]
        im.filepath = str(out)
        im.name = name
        im.reload()
    bpy.ops.export_scene.gltf(
        filepath=str(folder / (folder.name + ".gltf")),
        export_format="GLTF_SEPARATE",
        export_texture_dir="",
        export_apply=True,
        export_image_format="JPEG",
        export_jpeg_quality=82,
        export_cameras=False,
        export_lights=False,
        export_extras=False,
    )
