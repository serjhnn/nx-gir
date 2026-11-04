#!/usr/bin/env python3
"""Render README screenshots of the web reader to
docs/web-*.png.

Starts the server on a free port with a throwaway
state (a bookmark and a note, so they show), then
takes the pictures with Playwright for Node. Needs
(for this script only) Node.js and:

    npm install playwright

Run again after changing the pages in web/:

    scripts/render-web.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "scripts"))

import nxgir_web as web  # noqa: E402
from nxgir_state import State  # noqa: E402

BOOK = "grabar/bible/new-testament/1-matthew.txt"
WORD = 260  # է: has an abbreviation and a meaning

# the browser part: argv is [port, book, word, docs]
SHOOT = r"""
const { chromium } = require("playwright");
const [port, book, word, docs] =
  process.argv.slice(1);
const url = "http://localhost:" + port +
  "/#/read/" + encodeURIComponent(book);

(async () => {
  const b = await chromium.launch();
  // phone, light: a word looked up
  let p = await b.newPage({
    viewport: { width: 390, height: 760 },
    deviceScaleFactor: 2,
    colorScheme: "light",
  });
  await p.goto(url);
  await p.waitForSelector(".w");
  await p.locator(".w").nth(Number(word)).click();
  await p.waitForSelector(".panel .entry");
  await p.screenshot({ path: docs + "/web-light.png" });
  // wide, dark: the notes beside the text
  p = await b.newPage({
    viewport: { width: 1200, height: 760 },
    deviceScaleFactor: 1.5,
    colorScheme: "dark",
  });
  await p.goto(url);
  await p.waitForSelector(".w");
  await p.getByRole("button", { name: /Notes/ })
    .click();
  await p.waitForSelector(".items");
  await p.screenshot({ path: docs + "/web-dark.png" });
  await b.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
"""


def files():
    """Every book on the shelf, as nxgir web has it."""
    import importlib.util

    path = ROOT / "scripts" / "nxgir-cli.py"
    spec = importlib.util.spec_from_file_location(
        "cli", path
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli.shelf_files()


def sample_state(path):
    """A state with Matthew opened, and a bookmark
    and a note on word WORD (its sentence)."""
    app = web.App(files(), path)
    lay = web.book_words(app, BOOK)
    words = lay.words
    st = State(path)
    st.set_position(BOOK, [0, 0], len(lay.lines))
    st.toggle_mark(BOOK, web.pos_of(words, WORD))
    st.save()
    web.note(
        app,
        {
            "name": BOOK,
            "pos": web.pos_of(words, WORD),
            "text": "1:20: the angel speaks to"
            " Joseph in a dream.",
        },
    )
    return app


def main():
    if not shutil.which("node"):
        print("needs node (Node.js)", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        app = sample_state(Path(tmp) / "state.json")
        srv = web.server(app, port=0)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever)
        t.start()
        try:
            r = subprocess.run(
                [
                    "node",
                    "-e",
                    SHOOT,
                    str(port),
                    BOOK,
                    str(WORD),
                    str(DOCS),
                ],
                env=dict(os.environ),
            )
        finally:
            srv.shutdown()
            srv.server_close()
    if r.returncode:
        return r.returncode
    for name in ("web-light.png", "web-dark.png"):
        size = (DOCS / name).stat().st_size
        print(f"docs/{name}: {size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
