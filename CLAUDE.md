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

## The name

- **Նախագիր**: the Armenian name in all text
  people read (headings, titles, the blog, the
  welcome); inflected as usual (Նախագրի,
  Նախագրից, Նախագրում).
- **նխ՟գիր** (or նխ֊գիր): the short form, as a
  scribe writes it (`նխ` = `նախ` in
  `grabar/abbreviations.tsv`); only where the
  name is explained, beside Նախագիր, and not on
  the web pages (the README explains it); never
  inflected.
- **nxGir**: the English name in text people read
  on the site (pages, blog, timeline), beside
  Նախագիր in the header and footer; shown in the
  accent color (`named()` in `app.js` and
  `build-site.py`, class `nxgir`).
- **nx-gir** / **nxgir**: code, commands, file
  names, the repository, nxgir.am.
- The logo is art and stays as drawn (`նղ`);
  don't change it to match.

## Examples

- No sacred words in examples or screenshots
  (God, Jesus, Christ, Lord, holy, Israel,
  Jerusalem: the `sacred` kind in
  `grabar/abbreviations.tsv`, and their forms).
  This covers the README, the web pages, the
  Features page, the blog, help texts and the
  word looked up in `docs/` images. Take an
  everyday word: վրդ → վարդապետ, թգր → թագաւոր.
  The books themselves are quoted as they are,
  and the author cards (`authors/`) may use them.

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
- `ocr/`: OCR tooling for scanned books, apart from the
  reader. **Read `ocr/README.md` first**: the commands,
  the results, how to pick it up again. Pillow, numpy and
  `tesseract` (+ `hye`) needed only there. `ocr/run.py`
  (`page`, `eval`, `samples`, `train`, `proxy`, `tune`), the
  package `ocr/nxocr/`, `ocr/results/` (scores and the LLM
  answers, kept), `ocr/models/` (only `hye_grabar`; others
  are made again, not committed); tested in
  `tests/test_ocr.py`. Code in it follows the same limits
  (`ruff format ocr/`); `ocr/cache/` is not in git.
  Rules: score every step with `eval` on held-out pages
  against typed text before keeping it; the word list and
  the LLM pass only suggest (a review list), never rewrite
  unless `--apply`; look at a bad page by eye before
  trusting a number
- `scripts/nxgir_logo.py`: logos and gradient colors
- `scripts/fetch-bible.py`: downloads a book of the
  1895 Grabar Bible into `books/` (see
  `books/SOURCES.md`)
- `scripts/fetch-digilib.py`: downloads a book from
  digilib.am into `books/`, cut into parts. Digilib
  lists some books out of order: check the ☰ list and
  the first chapters, and fetch again with `--by-id`
  (the cache is kept); a section that only repeats the
  one before it is left empty
- `scripts/list-digilib.py`: lists every Digilib
  book in `notes/digilib.tsv`, with a link and a
  guess whether it is Grabar (tested in
  `tests/test_list_digilib.py`); a slow run (two
  requests a book), resumable from
  `.digilib-cache/list/`
- `books/`: the library; `data/`: test texts.
  A book under `grabar/` and its translation at the
  same path under `ashkharhabar/` are read side by
  side in the web reader (`PARALLEL` in
  `nxgir_web.py`); keep their lines one for one
- `books/LIBRARY.tsv`: the Library page
  (`/library`, `/api/library`): author names and
  short book names for `books/grabar/` (content; a
  test checks every path and author). Authors are
  shown in its order. **Always last, in this order:**
  Շնորհալի (`nerses-shnorhali`), Շիրակացի
  (`anania-shirakatsi`), Աստվածաշունչ (`bible`): put a
  new author above them (a test checks it)
  A book's line may end with its co-authors
  (`zenob-glak`), each with a name line and no
  folder: shown before the author everywhere
  (`coauthors()` in `nxgir_web.py`,
  `authorNames()` in `app.js`)
- A book's page (`/b/<folder>`, `/api/volume`,
  `volume()` in `nxgir_web.py`; on the site
  `data/volume/<folder>.json`): the parts of a book
  under `grabar/` or `ashkharhabar/` in order, with
  their first heading, a ⇆ mark and progress; a
  folder of single files (the Bible) is grouped by
  sub-folder, named in `LIBRARY.tsv`. The Library,
  the reader's back button and `folderHref()` in
  `app.js` lead there; `up`
  gives the links above it; the shelf's and the
  reader's breadcrumbs use the same names
  (`shelf_crumbs()`), and an old `/f/` link to a
  book's folder redirects there. Keep `PAGED` in
  `app.js` equal to `PARALLEL`
- `books/TRANSLATIONS.tsv`: our translations in
  `books/ashkharhabar/` (all but `bible/`, which is
  not ours): their status (`machine`, `review`,
  `reviewed`), reviewers and date, read by
  `scripts/nxgir_translations.py` (tested in
  `tests/test_translations.py`, which checks every
  translation is listed). The web reader and the
  site's book pages show it with the license, CC
  BY-SA 4.0 (`CONTRIBUTING.md`, README). Add a line
  with every new translated part, as `machine`
- `map/places.tsv`: the places of the map (the ancient
  Armenian names only, in the spelling of the books;
  en and ru are the same names transliterated, the
  modern name only in the note), read by
  `scripts/nxgir_map.py` (tested in
  `tests/test_map.py`). The map is the painted picture
  `web/img/map/base.webp` (Armenian Highland, 36.5-42.5
  N, 38-49.5 E, not to scale), so every place gives its
  own `x`, `y` (percent of the picture) on a painted
  tower or peak; lat and lon are the true place, and
  `project()` only gives a rough fallback. A post or a
  comic names its places on a `place:` line after the
  title (`blog/README.md`). The Map page (`/map`,
  `/map/<place>`, `mapPage()` in `app.js`; `/api/map`,
  `map_data()` in `nxgir_web.py`; on the site
  `data/map.json`): pins on the picture, zoom and
  drag, a small panel over the map (`map-pop`, beside
  its pin, docked at the bottom on a narrow map) with
  links to the stories, filters, and the list
  below it. A new place goes in `places.tsv` with its
  `x`, `y` (look at the picture); `MAP_UI` kinds in
  `app.js` must match `KINDS` (a test checks it). The
  pins' position is set with `el.style`, never a style
  attribute (the CSP forbids it). A post page links
  its places (`placeChips()`). For search engines
  `build-site.py` writes `map/<lang>/` and a page
  for each place that a post names,
  `map/<id>/<lang>/` (`map_pages()`; the kind
  names are `KIND_NAMES` in `nxgir_map.py`). The
  README picture `docs/web-map.jpg` is made by
  `scripts/render-web.py`. How it works, the pitfalls
  and the to-do list: `notes/map.md` (read it first)
- `blog/`: the Blog page (`/blog`, `/blog/<slug>`,
  `/api/blog`): one `YYYY-MM-DD-slug.LANG.md` per
  post and language (hy, en, ru; Armenian first),
  read by `scripts/nxgir_blog.py` (tested in
  `tests/test_blog.py`; the format is in
  `blog/README.md`); content, exempt from the line
  limit; on the site as `data/blog.json`
- `authors/`: the card about an author, opened by
  the scroll button (`ICONS.scroll`) beside the
  author's name on the Library, a book's page and
  the search page (`authorInfoBtn()`,
  `authorInfo()` in `app.js`; `/api/authors`,
  `/api/author?id=`; on the site
  `data/authors.json` and `data/author/<id>.json`):
  one `<id>.LANG.md` per author and language (hy,
  en, ru), the id the author's folder in
  `books/grabar/`, read by
  `scripts/nxgir_authors.py` (tested in
  `tests/test_authors.py`; the format is in
  `authors/README.md`); content, exempt from the
  line limit. Claude writes them from a source,
  `status: machine` until the user reviews one.
  The button shows only for an author with a file.
  A book has a card too, opened by its icon on the
  Library (`bookItem()`, `bookInfo()` in `app.js`;
  `/api/book-info?id=<author>/<book>`, ids in
  `/api/authors`; on the site
  `data/book/<author>/<book>.json`):
  `authors/<author>/<book>.LANG.md`, the book's
  path in `books/grabar/`, read by `read_books()`
  (`written` and `kind` in place of `years` and
  `role`)
- The Reference page, Տեղեկատու (`/reference`,
  `referencePage()`, `bookCard()` in `app.js`;
  `/api/book-cards?lang=`, `book_cards()` in
  `nxgir_web.py`; on the site
  `data/book-cards/<lang>.json` and `reference/`):
  every book card, in the Library's order, with
  chips for its kind and century. The kind is
  `group_of()` of the English `kind` (`GROUPS` in
  `nxgir_authors.py`: a new book whose kind fits
  none fails a test, add a word there), the
  century `century_of()` of the English `written`
- `features/`: the Features page (`/features`,
  `/api/features`): what the site can do, one
  `features.LANG.md` per language (drafts in
  `features/drafts/`), in the blog's format, read
  by `scripts/nxgir_features.py` (tested in
  `tests/test_features.py`; see
  `features/README.md`); on the site as
  `data/features.json` and
  `features/<lang>/`. Add a feature there
  with every new one on the site
- `notes/`: working notes, e.g. what each part of a
  book covers (`notes/3-amaran-hator.md`,
  `notes/2-dzmeran-hator.md` and
  `notes/1-datastanagirk-a.md`, added to with
  every translated part); not on the shelf and
  not on the Pages site
- `TRANSLATION_GUIDE.md`: how a part is translated, for
  contributors and for any AI tool (the prompt, an
  example, a check that can be run). It holds the text
  of `benchmark/prompt.md`; `tests/test_guide.py`
  checks that, and that its check runs. Change the two
  together
- `benchmark/`: a benchmark of models translating
  Grabar (chunks from translated parts, frozen in
  `cases/`, a prompt, `score.py`, a blind human
  review in `review.py`; see `benchmark/README.md`,
  tested in `tests/test_benchmark.py`). Code in it
  follows the same limits (ruff:
  `ruff format benchmark/`). The model outputs go in
  `benchmark/runs/<model>/`
- `scripts/nxgir_limits.py`: how close the
  repository is to the limits of GitHub and of a
  phone (tested in `tests/test_limits.py`), shown by
  `scripts/check-limits.py` and on the Statistics
  page (`/stats`: `/api/stats`, and
  `data/stats.json` written by `build-site.py`
  with the site's size and build time; the git
  size there is the last in `notes/limits.tsv`). The
  limits, a dated state and a to-do list are in
  `notes/limits.md`.
  After a new book or a few translated parts, run it
  with `--site --record` (adds a line to
  `notes/limits.tsv`) and update the notes.
  How much browser memory the web reader takes
  (and how to lower it) is in
  `notes/browser-memory.md`, measured with
  `scripts/measure-memory.js` (Playwright, with
  `nxgir web` running); measure it only when the
  user asks, not with every new book
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
- The reader's Contents (☰ in the web reader): the
  sermons and chapters of the open part, found by
  `contents()` in `nxgir_reader.py` from the text
  itself: `ԳԼՈՒԽ ...` group lines, Digilib's
  `[Ա]` section lines (the title is the next
  line), a sermon's `(Գլուխ. X)` number (its
  heading is the paragraph above, or the same line
  when only the verse is before it) and `Գլուխ X`
  lines. A title must mean something: a chapter
  line that only points at a list (`ի մեծ ցանկէն`,
  `POINTER_RE`) takes what follows it, or the next
  line, as its title; a title that only
  numbers the chapter (`label_only()`, Վեցերորդ Պրակ
  Հատորիս։) takes the next two lines too, until it
  says what it is about (three lines at most; the
  label words are the `LABEL_*` tables, to add to for
  a book that numbers its chapters otherwise).
  When the first heading is not at the start of the
  part, the list begins with an entry for the start
  (its first line, `"start": true`). A `(Պրակ X)`
  heading (Գիրք հարցմանց, a book of questions) is an
  entry of its own, `"kind": "Պրակ"`, with its topic
  (on the line or below it, not Հարց։), the letter
  in a capital; running text after a chapter line that
  only points at a list is not its title. A
  translation keeps the `(Պրակ X)` line in that form
  (the letter in a capital) and translates the topic
  (`TRANSLATION_GUIDE.md`). Nothing to add by
  hand: keep these lines as they are in every book
  and translation, and check the list after a new
  part (step 3 in `notes/3-amaran-hator.md`).
  A book of regions with none of these headings (the
  Աշխարհացոյց) takes its lines that start with an
  ordinal and ՝ (`Երկրորդ՝ Բրիտանացւոցն է`,
  `Երկրորդը՝ ...`; `ordinal_entries()`, at least 5)
  as entries, titled `Երկրորդ · Բրիտանացւոց`; a
  translation keeps the ՝ after each ordinal.
  Եղիշէ's `Առաջին յեղանակ՝ Ժամանակն` headings
  count too (three in a part are enough; the title
  is the whole line).
  A book with `Ա. Title` lines, each followed by
  the number alone (`titled_numbers()`, at least 5)
  is read too (Գրիգոր Լուսաւորիչ), and so is an
  `Ա. Title` line alone between blank lines with text
  after it (Եղիշէ, Խրատք).
  A critical edition (Եղիշէ, Մեկնութիւն Արարածոց)
  has `Ա (Ա II)` section lines, read like Digilib's
  `[Ա]`, and ԾԱՆՕԹԱԳՐՈՒԹԻՒՆՆԵՐ, ՅԱՒԵԼՈՒԱԾ as groups.
  A `[Ա]` line followed by `ԳԼՈՒԽ Ա` is one entry,
  titled by the line after the ԳԼՈՒԽ line (Ուխտանէս).
  A chronicle in `[1]`, `[2]` sections with no other
  headings has no list (`NO_CONTENTS`).
  A chronicle whose paragraphs start with their year
  (`Ի թուին 413`, `Իսկ ի թուականին Հայոց 410`; at
  least 10) takes those paragraphs as entries, "n"
  the year (`year_entries()`; Սմբատ Սպարապետ's
  Տարեգիրք); its translation starts them with the
  year too (`413 թվականին`, `Իսկ Հայոց 410
  թվականին`).
  A chronicle that names the year inside the line, in
  letters after a hyphen, the thousand left out
  (`ի -ՆԱ թուականին Հայոց`, 401; Մատթէոս
  Ուռհայեցի), has an entry for each such line, "n"
  the letters as printed (`dash_year_entries()`, at
  least 10).
  Homilies headed `ՃԱՌ ՀԻՆԳԵՐՈՐԴ` (three or
  more in a part; Սեբերիանոս Եմեսացի) are entries,
  titled with the subject line below
  (`homily_entries()`).
  A florilegium whose quotations are numbered afresh
  with each author (`1 * Երանելւոյն Երանոսի՝ ...`;
  Կոմիտաս Աղցեցի, Կնիք հաւատոյ) has an entry for
  each line that starts with `1`, titled by the
  line (`one_entries()`, at least 8).
  A long part (150 lines or more, no `[1]` sections)
  whose sections start with a title alone between blank
  lines, three or more, is read as that (`title_lines()`,
  the last rule; Ներսէս Լամբրոնացի).
  A book of songs or sermons numbered in letters
  with titles in capitals (`Ա. ՏԱՂ ՅԱՐՈՒԹԵԱՆ ...`,
  Narekatsi's Գանձեր եւ Տաղեր) takes those lines
  (`numbered_entries()`, at least 5; a heading
  written twice a few lines apart is one entry).
- **Every new book: fix its Contents.** After adding
  a book or a new work, check the ☰ list of its
  parts in the web reader, and run
  `python3 -m pytest tests/test_contents.py`: every
  part of 150 lines or more must have entries. If
  one has none, or the list is wrong (a heading
  missing, a line that is not a heading), teach
  `contents()` in `nxgir_reader.py` the form of its
  headings (a rule, as above, with a test in
  `tests/test_reader.py`); never edit the text to
  fit. Only a work with no headings at all goes in
  `NO_CONTENTS` in `tests/test_contents.py`, with the
  reason. Add the book's Library name
  (`books/LIBRARY.tsv`), a Timeline line and a
  limits record in the same change
- Routing: a page is a path under its language
  (`/hy/library`, `/en/read/<book>?line=3`), opened
  with `pushState` (`goTo()`, `hashNow()`,
  `setRoute()`, `inLang()` in `app.js`; the code
  still names a page `"#/library"`, without the
  language, and `h()` turns an `href` of that form
  into the path in `LANG` and marks it `data-r`,
  which one click handler opens; a path with its
  language, `inLang("ru", "#/map")`, is kept as it
  is). `index.html` has `<base href="/">`, so files
  are found from any path. An old link (`#/library`,
  `/library`, `/blog/<slug>/en`) is replaced by its
  path with the language first at start. `nxgir web`
  gives `index.html` for a path that is no file (a
  browser asking for a page). On the site,
  `build-site.py` writes `<lang>/<path>/index.html`
  for each page a search engine should list
  (`route_page()`; the pages of Armenian text, books,
  authors, the Library, under `hy/` only), and
  `404.html` for the rest; a new page of that kind
  goes in `searchable()`. Never write
  `location.hash`.
- **Languages** (`notes/i18n.md`, read it first):
  every page is in Armenian, English and Russian.
  `web/i18n.js` (loaded before `app.js`) has `LANGS`,
  `LANG` (from the address; a first visit takes the
  browser's; kept as `nxgir-ui-lang`) and `UI`, the
  words of the pages, one table per language with
  the same keys; `t("key", ...)` gives one in
  `LANG` (else English, else Armenian). **Never
  write words of the interface in `app.js`**: add a
  key to all three languages of `UI`
  (`tests/test_i18n.py` checks the keys, and that
  every `t("...")` is there). `<html lang>` is
  `LANG`; text of the books, authors' and books'
  names keep `lang: "hy"`. The language slider
  (`langButton()`: Հայ · Eng · Рус, the thumb slides
  under the current one; on a phone a row of its own
  with the full names) links the page in each
  language; the globe button beside it hides and
  shows it (kept as `nxgir-lang-bar`, shown at
  first);
  `route()` calls `followLang()`, which sends
  `langchange` for what is drawn once (menus, tab
  bar). The per-page pickers (blog, comics, map,
  Features, cards and Reference, announcements,
  word meanings) start from `LANG`; a pick holds
  until the language changes (`pagePick`). Word
  meanings: Armenian for hy, English for en and ru
  (no Russian yet). The Timeline's events and the
  limits on Statistics stay in English.
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
  page (`/timeline`) and, the newest three, in the
  welcome. Add a line with every milestone, in
  English for now. `KINDS` must match `app.js` (a
  test checks it)
- `scripts/nxgir_search.py`: search across the
  library (`/search`; the search box at the top of
  every page but the reader, kept in view on
  scrolling: `searchBox()`, `searchPage()` in
  `app.js`; in the reader the word panel's button,
  `searchWordButton()`, and a button for selected
  text, `selSearch`): an
  index of `grabar/` and `ashkharhabar/` (not the
  Bible, `LEFT_OUT`) by `loose()` key, which folds
  the classical spelling into the reformed one
  (թագավոր finds թագաւոր). `nxgir web` serves it
  (`/api/search`, `/api/search-parts`,
  `/api/lines`; built at start, in a thread) and
  `build-site.py` writes it as `data/search/` and
  `data/lines/`; the search itself is in `app.js`.
  `loose()` in `app.js` must match the Python one
  (a test checks it). Above the lines it lists the
  authors and books whose name the words start
  (`nameHits()`, `nameList()` in `app.js`), an
  author also by its English and Russian names from
  `authors/` (`/api/authors`); tested in
  `tests/test_search.py`. The plan, what is built
  and what is next: `notes/search.md`
- `scripts/build-site.py`: the read-only copy of the
  web reader for GitHub Pages (`site/`, published by
  `.github/workflows/pages.yml`): the answers of the
  API as files, read by `app.js` when `static.js`
  sets `NXGIR_STATIC`; for search engines, a page of
  its own for the top page in each language
  (`<lang>/`, `home_pages()`), each book
  (`hy/read/<book>/`), author (`hy/library/<id>/`,
  named in Armenian, English and Russian:
  `all_names()`), book (`hy/b/<folder>/`) and blog
  post (`<lang>/blog/<slug>/`), `sitemap.xml`
  and `robots.txt`; tested in
  `tests/test_site.py`. `bucket()` and `BUCKETS` must
  match `app.js` (a test checks it). It also writes
  `nxgir-site.zip` only with `--zip` (not built now,
  kept for later: `offline_zip()`, the site without
  the pages for search engines and the visit counter,
  with `scripts/offline/`: `serve.py` and `README.txt`;
  the Offline page shows it when `static.js` has
  `NXGIR_DOWNLOAD`). The Offline page (`/offline`,
  footer link `offlineLink()`, `offlinePage()` in
  `app.js`) offers the install and the saved copy. The
  site is also an installable app: `manifest.webmanifest`
  (icons from `scripts/render-icons.py`) and the
  service worker `web/sw.js`, started by
  `startWorker()` on the published site only; the build
  writes its build id into it and `offline.json`, the
  files "Save for offline" keeps (`offline_list()`)
- `scripts/render-logo.py`, `scripts/render-screens.py`,
  `scripts/render-web.py`: regenerate the README
  images in `docs/` after changing the logo, the
  screens or the web pages
- `scripts/render-og.py`: regenerates
  `web/og-image.png`, the link preview image
  (`og:image` in `web/index.html`, for LinkedIn
  and others) after changing the logo or colors
- Linux and Termux only, no Windows support for now.

## Git

- One developer, no pull requests. Commit and push
  to the session's own branch first, then ask before
  pushing the work to `main`.
