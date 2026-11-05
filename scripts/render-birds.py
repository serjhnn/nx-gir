#!/usr/bin/env python3
"""Draw the bird-letter marks of the web reader.

ն and ղ, and n and x, drawn as birds in the old
bird-letter (թռչնագիր) style of Armenian manuscripts:
vermilion, lapis and gold on parchment, ink outlines,
bodies covered in feather scales. Writes

    web/mark-hy.svg   ն and ղ (header, before նղ֊գիր)
    web/mark-en.svg   n and x (header, before nx-gir)
    web/icon.svg      ն and ղ on a tile (browser tab)

Run again after changing a bird:

    scripts/render-birds.py

The output is wrapped to 60 columns like the rest of
web/. Coordinates are in a 100 by 100 box.
"""

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"

LAPIS = "#24479a"
RED = "#c43a22"
GOLD = "#d4a22a"
GOLD_L = "#f1cd5a"
GREEN = "#2f7a4b"
PARCH = "#f3e4c2"
INK = "#3a2414"
WHITE = "#fffaf0"

# the view of the marks; the descender of ղ and the
# crests reach out of the 100 box
VIEW = "2 6 96 98"

# ---- drawing helpers


def stroke(d, c, w):
    return (
        f'<path d="{d}" fill="none"'
        ' stroke-linecap="round" stroke-linejoin="round"'
        f' stroke="{c}" stroke-width="{w}"/>'
    )


def quill(d, c, w, mid=GOLD_L):
    """A long tail feather: ink edge, color, a gold
    shaft."""
    return (
        stroke(d, INK, w + 1.6)
        + stroke(d, c, w)
        + stroke(d, mid, 0.8)
    )


def neck(d, c):
    return stroke(d, INK, 7.4) + stroke(d, c, 5.6)


def shape(d, c, w=1):
    return (
        f'<path d="{d}" fill="{c}" stroke="{INK}"'
        f' stroke-width="{w}" stroke-linejoin="round"/>'
    )


def dot(x, y, r, c, out=INK, w=0.8):
    o = ""
    if out:
        o = f' stroke="{out}" stroke-width="{w}"'
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"'
        f' fill="{c}"{o}/>'
    )


def beads(pts):
    """Gold beads along a neck."""
    return "".join(
        dot(x, y, 0.9, GOLD_L, INK, 0.5) for x, y in pts
    )


def leaf(x0, y0, x1, y1, wd, c):
    """A leaf or feather from (x0, y0) to (x1, y1),
    wd wide on each side."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    nx, ny = -dy / n * wd, dx / n * wd
    return shape(
        f"M{x0} {y0}"
        f"Q{mx + nx:.1f} {my + ny:.1f} {x1} {y1}"
        f"Q{mx - nx:.1f} {my - ny:.1f} {x0} {y0}Z",
        c,
        0.8,
    )


def scales(d, base, uid, plain=False):
    """A body filled with rows of feather scallops;
    plain: no scallops (they blur when small)."""
    if plain:
        return shape(d, base, 1.1)
    return (
        f'<defs><pattern id="sc{uid}" width="5"'
        ' height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="5" height="4" fill="{base}"/>'
        '<path d="M0 4Q2.5 .2 5 4M-2.5 2Q0 -1.8 2.5 2'
        'M2.5 2Q5 -1.8 7.5 2" fill="none"'
        f' stroke="{GOLD_L}" stroke-width=".7"/>'
        "</pattern></defs>"
        + shape(d, f"url(#sc{uid})", 1.1)
    )


def wing(x, y, ln, ang, rows):
    """A wing hanging from (x, y) at ang degrees, ln
    long: rows of (color, length) feathers, the long
    flight feathers first."""
    s = ""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    for i, (c, k) in enumerate(rows):
        L = ln * k
        w = 4.2 - i * 0.5
        hx, hy = x + ux * L * 0.5, y + uy * L * 0.5
        d = (
            f"M{x - px * w:.1f} {y - py * w:.1f}"
            f"Q{hx - px * w * 1.2:.1f}"
            f" {hy - py * w * 1.2:.1f}"
            f" {x + ux * L:.1f} {y + uy * L:.1f}"
            f"Q{hx + px * w * 1.2:.1f}"
            f" {hy + py * w * 1.2:.1f}"
            f" {x + px * w:.1f} {y + py * w:.1f}Z"
        )
        s += shape(d, c, 0.9)
        if i:
            continue
        # marks across the flight feathers
        for t in (0.55, 0.7, 0.85):
            cx, cy = x + ux * L * t, y + uy * L * t
            e = w * 0.8
            s += stroke(
                f"M{cx - px * e:.1f} {cy - py * e:.1f}"
                f"L{cx + ux * 2:.1f} {cy + uy * 2:.1f}"
                f"L{cx + px * e:.1f} {cy + py * e:.1f}",
                INK,
                0.6,
            )
    # a gold covert with a red dot at the shoulder
    s += dot(x + ux * 2, y + uy * 2, 3, GOLD)
    s += dot(x + ux * 2, y + uy * 2, 1, RED, None)
    return s


def head(x, y, r, c, beak, crest):
    """A head at (x, y). beak: (tip x, tip y, hooked);
    crest: [(dx, dy, color)] plumes."""
    s = ""
    for dx, dy, cc in crest:
        s += leaf(x, y - r * 0.4, x + dx, y + dy, 1.4, cc)
    s += dot(x, y, r, c, INK, 1)
    tx, ty, hook = beak
    a = math.atan2(ty - y, tx - x)
    ca, sa = math.cos(a), math.sin(a)
    bx, by = x + ca * r * 0.8, y + sa * r * 0.8
    px, py = -sa * 1.9, ca * 1.9
    if hook:
        d = (
            f"M{bx - px:.1f} {by - py:.1f}"
            f"Q{tx - px * 1.4:.1f} {ty - py * 1.4:.1f}"
            f" {tx + px * 0.6:.1f} {ty + py * 0.6:.1f}"
            f"L{bx + px:.1f} {by + py:.1f}Z"
        )
    else:
        d = (
            f"M{bx - px:.1f} {by - py:.1f}"
            f"L{tx:.1f} {ty:.1f}"
            f"L{bx + px:.1f} {by + py:.1f}Z"
        )
    s += shape(d, GOLD, 0.8)
    # the eye looks along the beak
    ex = x + ca * r * 0.3
    ey = y + sa * r * 0.3 - r * 0.25
    s += dot(ex, ey, r * 0.42, WHITE)
    s += dot(
        ex + ca * r * 0.14,
        ey + sa * r * 0.14,
        r * 0.2,
        INK,
        None,
    )
    # a red cheek
    s += dot(
        x - ca * r * 0.35,
        y + r * 0.35,
        r * 0.3,
        RED,
        None,
    )
    return s


def fan(ox, oy, ends, cols):
    """A peacock tail: feathers from (ox, oy) to each
    end, with gold eyes."""
    s = ""
    for (x, y), c in zip(ends, cols):
        s += leaf(ox, oy, x, y, 2.6, c)
        ex = ox + (x - ox) * 0.75
        ey = oy + (y - oy) * 0.75
        s += dot(ex, ey, 1.7, GOLD)
        s += dot(ex, ey, 0.7, LAPIS, None)
    return s + dot(ox, oy, 1.8, GOLD)


def feet(x, y, c=GOLD):
    leg = f"M{x} {y}Q{x - 0.5} {y + 4} {x} {y + 7}"
    toes = (
        f"M{x - 3} {y + 8.6}"
        f"Q{x - 1} {y + 6.6} {x} {y + 7}"
        f"Q{x + 1} {y + 6.6} {x + 3.4} {y + 8.4}"
        f"M{x} {y + 7}L{x + 0.4} {y + 9.4}"
    )
    return (
        stroke(leg, INK, 2.6)
        + stroke(leg, c, 1.4)
        + stroke(toes, c, 1.2)
    )


def body_path(h, w):
    """A body 2h long, pointing up, around (0, 0)."""
    return (
        f"M0 {-h}"
        f"C{w} {-h * 0.8} {w * 1.05} {h * 0.4}"
        f" {w * 0.25} {h}"
        f"C{-w * 0.3} {h * 1.05} {-w * 1.05} {h * 0.45}"
        f" {-w * 0.95} {-h * 0.1}"
        f"C{-w * 0.9} {-h * 0.7} {-w * 0.45} {-h}"
        f" 0 {-h}Z"
    )


def bird_body(cx, cy, ang, h, w, base, uid, wings):
    """A scaled body with its wing, at (cx, cy) turned
    by ang degrees."""
    return (
        f'<g transform="translate({cx} {cy})'
        f' rotate({ang})">'
        + scales(body_path(h, w), base, uid)
        + wing(0.8, -h + 5, h * 1.75, 92, wings)
        + "</g>"
    )


# ---- the letters


def nu(uid, plain=False):
    """ն: a bird standing tall. Its neck bends back to
    the left into the hook, its body is the stem, its
    long tail sweeps round the bowl and up the right
    stem."""
    s = quill(
        "M20 62C21 76 33 79 37 70C40 62 37 46 40 34",
        RED,
        3.6,
    )
    s += fan(
        40,
        34,
        [(34, 21), (40, 18), (46, 22)],
        [GREEN, LAPIS, GREEN],
    )
    s += feet(15, 61)
    s += neck("M18 32C16 25 21 20 18 15", LAPIS)
    s += scales(
        "M18 27C25 30 27 44 24 56C22.5 63 19 67 17 66"
        "C12 64 10 54 11 44C12 34 13 28 18 27Z",
        LAPIS,
        uid,
        plain,
    )
    s += wing(
        20,
        33,
        30,
        82,
        [(RED, 1), (GREEN, 0.78), (LAPIS, 0.5)],
    )
    s += head(
        17,
        13,
        4.6,
        LAPIS,
        (6, 19, True),
        [(5, -6, RED), (8, -2.5, GOLD), (2, -7.5, GREEN)],
    )
    return s


def ghat(uid, plain=False):
    """ղ: a bird bowing. Its body is the right stem,
    its neck arches over to the left and down, the head
    and beak make the left stem; the tail falls below
    the line."""
    s = quill("M82 72C83 80 80 86 83 92", LAPIS, 3.4)
    s += fan(
        83,
        92,
        [(77, 99), (83, 101), (89, 98)],
        [RED, GREEN, RED],
    )
    s += neck(
        "M80 38C80 26 74 21 67 22C59 23 56 30 57 40"
        "C57.5 47 56 52 57 57",
        RED,
    )
    s += beads([(62, 23.6), (71, 21.8), (58, 32)])
    s += scales(
        "M80 34C88 36 90 50 88 60C87 67 84 73 81 74"
        "C76 73 73 64 74 54C75 44 74 35 80 34Z",
        RED,
        uid + "g",
        plain,
    )
    s += wing(
        81,
        40,
        30,
        96,
        [(LAPIS, 1), (GREEN, 0.78), (GOLD, 0.5)],
    )
    s += head(
        57,
        60,
        4.6,
        RED,
        (55.5, 72, False),
        [(9, -2, LAPIS), (8, 3, GREEN)],
    )
    return s


def n_bird(uid):
    """n: a bird bowing to the ground; its body stands
    on the right on its feet, its neck arches over and
    down to the head on the left; the tail is raised
    behind."""
    s = feet(34.5, 70) + feet(39.5, 70)
    s += quill("M39 66C45 66 47 60 46 52", LAPIS, 3.2)
    s += fan(
        46,
        52,
        [(41, 41), (47, 39), (52, 43)],
        [GREEN, RED, GREEN],
    )
    s += neck(
        "M36 40C36 26 29 21 23 22C15 23 12 31 13 43"
        "C13.5 53 12 60 13 64",
        RED,
    )
    s += beads([(18, 24.5), (27, 21.8), (13.4, 33)])
    s += bird_body(
        37,
        55,
        0,
        17,
        7,
        RED,
        uid,
        [(LAPIS, 1), (GREEN, 0.78), (GOLD, 0.5)],
    )
    s += head(
        13,
        67,
        4.4,
        RED,
        (12, 79, False),
        [(9, -2, LAPIS), (8, 3, GREEN)],
    )
    return s


def x_birds(uid):
    """x: two birds with crossed necks; their bodies
    are the lower arms, their necks the upper arms."""
    s = fan(
        58,
        79,
        [(50, 84), (53, 90), (59, 90)],
        [RED, GREEN, RED],
    )
    s += fan(
        90,
        79,
        [(98, 84), (95, 90), (89, 90)],
        [RED, LAPIS, RED],
    )
    s += bird_body(
        84,
        68,
        -28,
        12,
        6,
        GREEN,
        uid + "r",
        [(RED, 1), (LAPIS, 0.78), (GOLD, 0.5)],
    )
    s += bird_body(
        64,
        68,
        28,
        12,
        6,
        LAPIS,
        uid + "l",
        [(RED, 1), (GREEN, 0.78), (GOLD, 0.5)],
    )
    # the right bird's neck goes under, the left over
    s += neck("M78.5 59C75 48 66 40 62.5 31", GREEN)
    s += neck("M69.5 59C73 48 82 40 85.5 31", LAPIS)
    s += beads([(80.3, 40.4), (76.4, 46), (67.6, 40.4)])
    s += head(
        86.5,
        27,
        4.2,
        LAPIS,
        (96, 22.5, True),
        [(-6, -6, RED), (-2, -8, GOLD)],
    )
    s += head(
        61.5,
        27,
        4.2,
        GREEN,
        (52, 22.5, True),
        [(6, -6, RED), (2, -8, GOLD)],
    )
    return s


def tile(m):
    """m on parchment in a lapis frame."""
    return (
        '<rect width="100" height="100" rx="18"'
        f' fill="{PARCH}"/>'
        '<rect x="3.5" y="3.5" width="93" height="93"'
        f' rx="15" fill="none" stroke="{LAPIS}"'
        ' stroke-width="2.4"/>'
        '<g transform="translate(9.68 2.12)'
        f' scale(.84)">{m}</g>'
    )


# ---- writing the files, wrapped to 60 columns


def short(m):
    """1.2345 -> 1.23"""
    s = f"{float(m.group()):.2f}"
    return s.rstrip("0").rstrip(".")


def wrap_value(v, indent):
    """Break a long value before path commands or
    spaces."""
    lines, cur = [], ""
    for p in re.split(r"(?=[MLQCZ ])", v):
        if len(indent + cur + p) > 50 and cur:
            lines.append(cur)
            cur = ""
        cur += p
    lines.append(cur)
    return ("\n" + indent).join(lines)


def fmt(markup):
    """One tag a line; a long tag one attribute a
    line."""
    markup = re.sub(r"-?\d+\.\d{3,}", short, markup)
    out = []
    for t in re.findall(r"<[^>]+>", markup):
        if len(t) <= 60:
            out.append(t)
            continue
        m = re.match(r"<(/?\w+)(.*?)(/?)>$", t, re.S)
        name, attrs, close = m.groups()
        lines = ["<" + name]
        for a, v in re.findall(
            r'([\w:-]+)="([^"]*)"', attrs
        ):
            s = f'  {a}="{v}"'
            if len(s) > 57:
                v = wrap_value(v, "    ")
                s = f'  {a}="{v}"'
            lines.append(s)
        lines[-1] += "/>" if close else ">"
        out.append("\n".join(lines))
    return "\n".join(out) + "\n"


def document(body, view, comment):
    return (
        fmt(
            '<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="{view}">'
        )
        + f"<!-- {comment} -->\n"
        + fmt(body)
        + "</svg>\n"
    )


def drawings():
    """{file name in web/: SVG text}"""
    return {
        "mark-hy.svg": document(
            nu("n") + ghat("n"),
            VIEW,
            "ն and ղ as birds, in the old\n"
            "  bird-letter (թռչնագիր) style",
        ),
        "mark-en.svg": document(
            n_bird("x") + x_birds("x"),
            VIEW,
            "n and x as birds: a bowing bird and\n"
            "  two birds with crossed necks",
        ),
        # the tab icon: no scales, which blur at 16px
        "icon.svg": document(
            tile(nu("i", True) + ghat("i", True)),
            "0 0 100 100",
            "ն and ղ as birds; see mark-hy.svg",
        ),
    }


def main():
    for name, text in drawings().items():
        path = WEB / name
        path.write_text(text, encoding="utf-8")
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
