#!/usr/bin/env python3
"""Render web/og-image.png: the picture a link to
nxgir.am shows on LinkedIn and other sites (the
og:image in web/index.html), 1200x630.

Takes it with Playwright for Node, with the
fonts of web/fonts/. Needs (for this script only)
Node.js and:

    npm install playwright

Run again after changing the logo or the colors:

    scripts/render-og.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
OUT = WEB / "og-image.png"

# the light theme of style.css. LinkedIn crops
# the sides (a Featured link shows about the
# middle 960px), so all of it is centered and
# kept in the middle 840px
CARD = """<!doctype html>
<html lang="hy">
<head>
<meta charset="utf-8">
<base href="{web}/">
<link rel="stylesheet" href="fonts.css">
<style>
* {{ margin: 0; box-sizing: border-box; }}
html, body {{ width: 1200px; height: 630px; }}
body {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 180px;
  text-align: center;
  background: #faf9f5;
  color: #141413;
  font-family: system-ui, sans-serif;
  border-bottom: 14px solid #d97757;
}}
.top {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
}}
svg {{
  width: 116px;
  height: 126px;
  fill: none;
  stroke: #d97757;
  stroke-linecap: round;
  stroke-linejoin: round;
}}
h1 {{
  font: 400 100px "nx Arian Grqi", serif;
  line-height: 1.1;
}}
h2 {{
  margin-top: 32px;
  font-size: 50px;
  font-weight: 600;
}}
p {{
  margin-top: 20px;
  font-size: 30px;
  color: #6b6a65;
  line-height: 1.35;
}}
.url {{
  margin-top: 40px;
  font-size: 30px;
  font-weight: 600;
  color: #b85c3e;
}}
</style>
</head>
<body>
<div class="top">
  <svg viewBox="4 3 24 26" aria-hidden="true">
    <path stroke-width="1.3"
      d="M5.5 8.5Q5.5 5 9 5V19Q9 23 12.5 23
      Q16 23 16 19V13Q16 9 19.5 9Q23 9 23 13V27
      Q26.5 27 26.5 23.5"/>
    <path stroke-width="3.6"
      d="M9 5V19M16 13V19M23 13V27"/>
  </svg>
  <h1>Նախագիր</h1>
</div>
<h2 lang="en">Old Armenian Book Reader</h2>
<p lang="en">Grabar books with Modern Armenian
translations side by side, and the meaning of
every word a tap away.</p>
<div class="url" lang="en">nxgir.am</div>
</body>
</html>
"""

# the browser part: argv is [page, out]
SHOOT = r"""
const { chromium } = require("playwright");
const [page, out] = process.argv.slice(1);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({
    viewport: { width: 1200, height: 630 },
  });
  await p.goto("file://" + page);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: out });
  await b.close();
})();
"""


def main():
    if not shutil.which("node"):
        print("needs node (Node.js)", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(
            CARD.format(web=WEB.as_uri()), "utf-8"
        )
        r = subprocess.run(
            ["node", "-e", SHOOT, str(page), str(OUT)]
        )
    if r.returncode:
        return r.returncode
    kb = OUT.stat().st_size // 1024
    print(f"{OUT.relative_to(ROOT)}: {kb} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
