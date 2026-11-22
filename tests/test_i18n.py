"""The words of the web pages in each language
(web/i18n.js): the same keys in hy, en and ru,
every key app.js asks for is there, and the
languages are those of the blog."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import nxgir_blog as blog  # noqa: E402

I18N = ROOT / "web/i18n.js"
APP = ROOT / "web/app.js"

# i18n.js with what a browser gives it, then the
# keys and the kind of value of each language
LOAD = """
globalThis.navigator = { languages: ["en"] };
globalThis.location = { pathname: "/" };
globalThis.localStorage = { getItem: () => null };
const src = require("fs").readFileSync(
  process.argv[1], "utf8");
const out = new Function(src
  + "; return { LANGS, UI, t, LANG,"
  + " langOf };")();
const kinds = {};
for (const [l, words] of Object.entries(out.UI)) {
  kinds[l] = {};
  for (const [k, v] of Object.entries(words)) {
    kinds[l][k] = typeof v;
  }
}
console.log(JSON.stringify({ langs: out.LANGS,
  kinds, lang: out.LANG,
  paths: ["/hy/library", "/en", "/xx/a", "/ru/",
    "/library"].map(out.langOf) }));
"""


@pytest.fixture(scope="module")
def ui():
    if not shutil.which("node"):
        pytest.skip("needs Node.js")
    got = subprocess.run(
        ["node", "-e", LOAD, str(I18N)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(got)


def test_languages_are_the_blogs(ui):
    assert tuple(ui["langs"]) == blog.LANGS
    assert set(ui["kinds"]) == set(blog.LANGS)


def test_every_language_has_every_key(ui):
    hy = ui["kinds"]["hy"]
    for lang, words in ui["kinds"].items():
        assert set(words) == set(hy), lang
        # a function in one is a function in all
        assert words == hy, lang


def test_browser_language_and_paths(ui):
    assert ui["lang"] == "en"
    assert ui["paths"] == ["hy", "en", "", "ru", ""]


def used_keys():
    """The keys app.js asks t() for by name."""
    js = APP.read_text("utf-8")
    keys = set(re.findall(r'\bt\("([\w.]*\w)"', js))
    # MENU, TABS, MORE: labels that are keys
    keys |= set(re.findall(r'"(nav\.\w+)"', js))
    return keys


def test_app_asks_only_for_known_keys(ui):
    missing = used_keys() - set(ui["kinds"]["en"])
    assert not missing, sorted(missing)
