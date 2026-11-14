#!/usr/bin/env python3
"""Render the app icons of web/ from web/icon.svg:
icon-192.png, icon-512.png and icon-maskable-512.png
(the manifest, web/manifest.webmanifest, names them).
The maskable one has the mark in the middle 60% of a
full square, as Android crops it to a circle.

Needs Node.js and (for this script only):

    npm install playwright

Run again after changing the logo:

    scripts/render-icons.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
SVG = (WEB / "icon.svg").read_text("utf-8")
ACCENT = "#D97757"
# [file, size, padding in %, rounded]
ICONS = [
    ("icon-192.png", 192, 0, True),
    ("icon-512.png", 512, 0, True),
    ("icon-maskable-512.png", 512, 20, False),
]

PAGE = """<!doctype html>
<style>
* {{ margin: 0; }}
html, body {{ width: {n}px; height: {n}px;
  background: {bg}; overflow: hidden; }}
svg {{ display: block; margin: {pad}px;
  width: {inner}px; height: {inner}px; }}
</style>
{svg}
"""

SHOOT = r"""
const { chromium } = require("playwright");
const [page, out, size] = process.argv.slice(1);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({
    viewport: { width: +size, height: +size },
  });
  await p.goto("file://" + page);
  await p.screenshot({ path: out, omitBackground: true });
  await b.close();
})();
"""


def main():
    if not shutil.which("node"):
        print("needs node (Node.js)", file=sys.stderr)
        return 1
    for name, n, pct, rounded in ICONS:
        pad = n * pct // 100
        art = SVG
        if not rounded:
            # a full square: the mark without its tile
            art = art.replace(' rx="7"', "")
        html = PAGE.format(
            n=n,
            bg="transparent" if rounded else ACCENT,
            pad=pad,
            inner=n - 2 * pad,
            svg=art,
        )
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "icon.html"
            page.write_text(html, "utf-8")
            out = WEB / name
            r = subprocess.run(
                [
                    "node",
                    "-e",
                    SHOOT,
                    str(page),
                    str(out),
                    str(n),
                ]
            )
        if r.returncode:
            return r.returncode
        size = out.stat().st_size
        print(f"{out.relative_to(ROOT)}: {size} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
