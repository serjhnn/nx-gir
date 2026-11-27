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

# the light theme of style.css, on the paper of
# the reader: what the site does, shown once (a
# line of Yeghishe, its translation below, and a
# word's meaning). LinkedIn crops the sides (a
# Featured link shows about the middle 960px), so
# all of it is kept in the middle 840px
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
  background:
    radial-gradient(ellipse at center,
      #fbf6e9 40%, #efe3c6 100%);
  color: #141413;
  font-family: system-ui, sans-serif;
  border-bottom: 14px solid #d97757;
}}
.top {{
  display: flex;
  align-items: center;
  gap: 16px;
}}
svg {{
  width: 52px;
  height: 56px;
  fill: none;
  stroke: #d97757;
  stroke-linecap: round;
  stroke-linejoin: round;
}}
.name {{
  font: 400 50px "nx Arian Grqi", serif;
}}
.en {{
  font-size: 24px;
  font-weight: 600;
  color: #6b6a65;
  margin-left: 6px;
}}
.grabar {{
  margin-top: 78px;
  font: 400 50px "nx Arian Grqi", serif;
  line-height: 1.25;
  color: #3b2a1a;
}}
mark {{
  position: relative;
  background: #f3d3c4;
  color: inherit;
  border-radius: 6px;
  padding: 0 6px;
}}
.word {{
  position: absolute;
  left: 50%;
  bottom: 100%;
  transform: translate(-50%, -12px);
  white-space: nowrap;
  padding: 6px 16px;
  border-radius: 10px;
  background: #141413;
  color: #faf9f5;
  font: 500 22px system-ui, sans-serif;
}}
.word b {{ color: #e8a185; font-weight: 600; }}
.modern {{
  margin-top: 18px;
  font: 400 26px "nx Noto Serif Armenian", serif;
  color: #5a4a38;
}}
.who {{
  margin-top: 16px;
  font: 400 22px "nx Noto Serif Armenian", serif;
  color: #8a7a66;
}}
.foot {{
  margin-top: 34px;
  font-size: 26px;
  color: #6b6a65;
}}
.foot b {{ color: #b85c3e; }}
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
  <span class="name">Նախագիր</span>
  <span class="en" lang="en">nxGir</span>
</div>
<p class="grabar">Մահ ոչ <mark>իմացեալ<span
class="word" lang="en"><b>իմանամ</b> · to
understand, to know</span></mark>՝ մահ է,<br>
մահ իմացեալ՝ անմահութիւն է։</p>
<p class="modern">Մահը չգիտակցված՝ մահ է,
մահը գիտակցված՝ անմահություն է։</p>
<p class="who">Եղիշէ, Վասն Վարդանայ</p>
<p class="foot" lang="en">Old Armenian books,
word by word · <b>nxgir.am</b></p>
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
