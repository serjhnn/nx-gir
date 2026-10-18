#!/usr/bin/env python3
"""Render the nx-gir logo to an SVG image.

Uses the same logo and gold-to-red gradient as the
shell. Run again after changing the logo:

    scripts/render-logo.py [LOGO] [out.svg]

LOGO is a key of nxgir_logo.LOGOS (default: hy).
"""

import sys
from html import escape
from pathlib import Path

import nxgir_logo as logo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

FONT_SIZE = 16
CHAR_W = FONT_SIZE * 0.6  # monospace advance
LINE_H = FONT_SIZE * 1.25
PAD = 20
BG = "#1e1e24"
NBSP = "\u00a0"


def render(lines, title):
    cols = max(len(line) for line in lines)
    w = round(cols * CHAR_W + 2 * PAD)
    h = round(len(lines) * LINE_H + 2 * PAD)
    colors = [
        "#%02x%02x%02x" % rgb
        for rgb in logo.row_colors(len(lines))
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{w}" height="{h}"'
        f' viewBox="0 0 {w} {h}">',
        f"<title>{escape(title)}</title>",
        f'<rect width="{w}" height="{h}"'
        f' rx="8" fill="{BG}"/>',
        '<g font-family="DejaVu Sans Mono,Menlo,'
        'Consolas,monospace"'
        f' font-size="{FONT_SIZE}"'
        ' xml:space="preserve">',
    ]
    for row, (line, color) in enumerate(zip(lines, colors)):
        y = round(PAD + (row + 0.8) * LINE_H, 1)
        # browsers collapse runs of plain spaces
        text = escape(line).replace(" ", NBSP)
        out.append(
            f'<text x="{PAD}" y="{y}"'
            f' fill="{color}">{text}</text>'
        )
    out += ["</g>", "</svg>"]
    return "\n".join(out) + "\n"


def main(argv):
    name = argv[0] if argv else logo.DEFAULT_LOGO
    default = ROOT / "docs" / f"logo-{name}.svg"
    out = Path(argv[1]) if len(argv) > 1 else default
    title = "նղ֊գիր" if name.startswith("hy") else "nX-gir"
    svg = render(logo.LOGOS[name], title)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(
        out.relative_to(ROOT)
        if out.is_relative_to(ROOT)
        else out
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
