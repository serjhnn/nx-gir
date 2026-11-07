# nx-gir notes for Claude

## Code style

- Max line width is 60 characters in all code
  (Python, shell, config). The code is read on a phone.
- Configured in `pyproject.toml` (ruff) and
  `.editorconfig`.
- Before committing, run:

  ```sh
  ruff format scripts/ tests/
  ruff check scripts/ tests/
  python3 -m pytest
  ```

- `ruff format` cannot split long strings, comments or
  docstrings; shorten or wrap those by hand.
- Text files in `data/`, `grabar/`, `blog/` and
  `interpretations/` are content, not code, and are
  exempt.

## Layout

- `scripts/nxgir-cli.py`: commands and the `nxgir>` shell
- `scripts/nxgir_browse.py`: `bookshelf`, a folder
  view of `books/`, `data/` and `interpretations/`
  (the shelves are `SHELVES` in `nxgir-cli.py`;
  curses); folder logic
  is tested in `tests/test_browse.py`
- `scripts/nxgir_reader.py`: the reader; text model at
  the top (tested in `tests/`), curses screen below
- `scripts/nxgir_state.py`: saved positions,
  bookmarks, notes and settings (JSON in
  `~/.local/state/nxgir/`; tests use `NXGIR_STATE`)
- `scripts/nxgir_ui.py`: shared curses helpers; read
  keys with `key()`, it handles terminal resizes
- `scripts/nxgir_grabar.py`: Grabar helpers
  (`nxgir grabar abbr`, `nxgir grabar word`); the
  data is in `grabar/` (`abbreviations.tsv` names its
  sources in the header; add only entries from a
  source, or, when the user asks, readings of our own
  marked `N`; `vocabulary.tsv` and `forms.tsv` are
  built from Wiktionary by
  `scripts/fetch-vocabulary.py`, and
  `vocabulary-hy.tsv` (Armenian meanings) from the
  Armenian Wiktionary by
  `scripts/fetch-vocabulary-hy.py`; none of them is
  edited by hand). `vocabulary-claude.tsv` is
  different: meanings Claude wrote (English and
  Armenian, one line per word form) for words the
  Wiktionary lists lack, most frequent first; shown
  only when Wiktionary has nothing, always marked
  `SOURCE_AI`. Add to it by hand, in batches; a test
  checks the format and that it never repeats a
  Wiktionary word
- `sources/`: copies of the sources (page scans, entry
  texts) behind the `grabar/` data; add the copy and a
  note in `sources/README.md` with every new source
- `scripts/nxgir_logo.py`: logos and gradient colors
- `scripts/fetch-bible.py`: downloads a book of the
  1895 Grabar Bible into `books/` (see
  `books/SOURCES.md`)
- `scripts/fetch-digilib.py`: downloads a book from
  digilib.am into `books/`, cut into parts
- `books/`: the library; `data/`: test texts.
  A book under `grabar/` and its translation at the
  same path under `ashkharhabar/` are read side by
  side in the web reader (`PARALLEL` in
  `nxgir_web.py`); keep their lines one for one
- `books/LIBRARY.tsv`: the Library page
  (`#/library`, `/api/library`): author names and
  short book names for `books/grabar/` (content; a
  test checks every path and author)
- `blog/`: the Blog page (`#/blog`, `#/blog/<slug>`,
  `/api/blog`): one `YYYY-MM-DD-slug.md` per post,
  read by `scripts/nxgir_blog.py` (tested in
  `tests/test_blog.py`; the format is in
  `blog/README.md`); content, exempt from the line
  limit; on the site as `data/blog.json`
- `notes/`: working notes, e.g. what each part of a
  book covers (`notes/3-amaran-hator.md`, added to
  with every translated part); not on the shelf and
  not on the Pages site
- `scripts/nxgir_limits.py`: how close the
  repository is to the limits of GitHub and of a
  phone (tested in `tests/test_limits.py`), shown by
  `scripts/check-limits.py` and on the Statistics
  page (`#/stats`: `/api/stats`, and
  `data/stats.json` written by `build-site.py`
  with the site's size and build time; the git
  size there is the last in `notes/limits.tsv`). The
  limits, a dated state and a to-do list are in
  `notes/limits.md`.
  After a new book or a few translated parts, run it
  with `--site --record` (adds a line to
  `notes/limits.tsv`) and update the notes
- `interpretations/`: the user's own texts on the
  books, in Russian (`ru/`), English (`en/`) and
  Armenian (`hy/`);
  content, not code: save them exactly as given
- `scripts/nxgir_web.py`: `nxgir web`, the local web
  reader: a standard-library HTTP server and a JSON
  API (tested in `tests/test_web.py`); it reuses the
  reader's text model and state, so both readers
  share positions, bookmarks and notes. The only
  files it writes are `.md` texts in
  `interpretations/` (edited or new, saved exactly as
  given, never over a file changed on disk)
- `web/`: the web pages (plain HTML, CSS, JS, no
  build step, nothing loaded from other sites); the
  60-character limit applies here too. `wordKey()`
  in `app.js` must match `normalize()` in the reader
  (a test checks it)
- `timeline.tsv`: the main steps of the project
  (content, exempt from the line limit; its head
  explains the fields), read by
  `scripts/nxgir_timeline.py` (tested in
  `tests/test_timeline.py`); shown on the Timeline
  page (`#/timeline`) and, the newest three, in the
  welcome. Add a line with every milestone, in
  English for now. `KINDS` must match `app.js` (a
  test checks it)
- `scripts/build-site.py`: the read-only copy of the
  web reader for GitHub Pages (`site/`, published by
  `.github/workflows/pages.yml`): the answers of the
  API as files, read by `app.js` when `static.js`
  sets `NXGIR_STATIC`; for search engines, each
  book also as plain HTML (`read/<book>.html`)
  and each blog post (`blog/<slug>.html`),
  `sitemap.xml` and `robots.txt`; tested in
  `tests/test_site.py`. `bucket()` and `BUCKETS` must
  match `app.js` (a test checks it)
- `scripts/render-logo.py`, `scripts/render-screens.py`,
  `scripts/render-web.py`: regenerate the README
  images in `docs/` after changing the logo, the
  screens or the web pages
- Linux and Termux only, no Windows support for now.

## Git

- One developer, no pull requests. Commit and push
  to the session's own branch first, then ask before
  pushing the work to `main`.
