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
- Text files in `data/`, `grabar/` and
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
  edited by hand)
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
- `scripts/build-site.py`: the read-only copy of the
  web reader for GitHub Pages (`site/`, published by
  `.github/workflows/pages.yml`): the answers of the
  API as files, read by `app.js` when `static.js`
  sets `NXGIR_STATIC`; tested in
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
