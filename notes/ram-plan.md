# Plan: the web reader on old phones (RAM and old browsers)

Start a new session from this file: read it, then do
the first step marked **to do**. Background numbers:
`notes/browser-memory.md`. Tools: `scripts/measure-memory.js`
(Playwright, `nxgir web` running).

## The problem

Old phones (1-2 GB RAM, an old Android WebView)
cannot load the page. Two causes, in this order of
likelihood:

1. **The script does not parse** (old browser): the
   page stays on the static text of `index.html`.
2. **The tab runs out of memory** when a big part is
   opened (about 290 MB of tab for the largest part
   side by side, on top of 65 MB for the home page);
   Android kills the tab.

## Status

| Step | What | State |
|---|---|---|
| A | Build the translation only while shown | **done** |
| B | `content-visibility: auto` on paragraphs | **done** |
| P | Read a part in pages (option 2) | **done** |
| P2 | Pages of 5,000 characters (was 10,000) | **done** (2026-11-22) |
| C | Lower the opening peak | done in part (see below) |
| D | Smaller parts (150 KB) | to do, optional |
| E | Old browsers: fallback page | to do, next |
| F | Old browsers: transpile / fallbacks | to do |
| G | Low-memory mode | done as P (pages are the default) |
| H | Fewer nodes per word | **done** as plain lines (2026-11-22) |
| I | A window of lines | later, biggest |

Measured on `grabar/mkhitar-gosh/1-datastanagirk-a/01.txt`
(the largest part), phone screen, after a garbage
collection (`PHONE=1 node scripts/measure-memory.js
why <part>`):

| Case | Before | After A+B |
|---|---|---|
| Home page | 71 MB | 69 MB |
| Side by side | 184 MB | 140 MB |
| Side by side, scrolled to the end | 190 MB | 160 MB |
| One column | 154 MB | 117 MB |
| One column, elements | 125,525 | 73,668 |

After P (pages), same part, phone screen:

| Case | After A+B | With pages |
|---|---|---|
| Side by side | 144 MB | 82 MB |
| One column | 118 MB | 78 MB |
| Elements, side by side | 125,533 | 7,313 |
| Peak when opening, 5 largest parts (`fresh 5`) | 249 MB | 128 MB |

The home page alone is 70 MB, so a page costs about
12 MB on top of it instead of about 75 MB. Going
through all 15 pages of a part: no leak (7,300 to
8,400 elements, heap 5.3 MB at both ends).

## Done: P (pages)

The idea (option 2 of the discussion): the part is
cut into pages of about 5,000 characters of Grabar
(`PAGE_CHARS` in `app.js`); only one page is in the
DOM, with ‹ Previous / Next › above and below.
Parallel stays: a page holds its lines and their
pairs. A part under 15,000 characters is one page.

How (`web/app.js`, `web/style.css`):
- `book()` makes every word as *data* (`R.keys`,
  `R.wpos`, `R.first`, `R.src`) and `showPage(k)`
  makes the elements of page k only. `R.spans` has
  a hole for each word not in the page (index =
  word of the part), `R.lo`/`R.hi` the page's
  words. `topWord()`/`lastWord()` search the page.
- `ensure(i)` shows the page of word i; `go()` and
  `choose()` call it first (Contents, bookmarks,
  `?line=`, the n/N keys across pages). Texts of
  words not on the page come from the data:
  `wordAt()`, `wordsOf()`, `snippet()`.
- `pagesOf()` decides the pages; `paged()` says if
  they are on: always, unless the reader turned them
  off with the ▤ button in the text settings (beside
  the font list). Kept in the `nxgir-view` setting
  as `paged` (null = on, the default).
- The reader's tools show ‹ n/N › for the pages
  (`pagesBtn()`), where the parts buttons were (the
  back button leads to the book's page); the cards to
  the other parts show on the last page only.
- The progress bar counts the whole part
  (`progress()`); a saved position is a word, so it
  opens on the right page.
- Not in pages: one page = the whole part, the same
  code, nothing changes.

Cost: Ctrl-F finds only the page; the scroll bar is
a page's. Translation credit is on the first page.

Checked with Playwright (phone): `?line=` links to
lines 3, 400, 1500, 1990; next/previous page; the
saved position after a reload; Contents jump to
a heading on another page; a word tapped and its
panel; Pages off and on keeping the place. The
measurements: `PHONE=1 node scripts/measure-memory.js
why <part>` (the new rows) and `VIEW='{"paged":true}'
PHONE=1 node scripts/measure-memory.js fresh 5`.
Added to the Features page in hy, en, ru.

Not checked: a real old phone; wide-screen use of
pages beyond a look at a screenshot; the published
site (`site/`, `NXGIR_STATIC`) is the same code but
was not opened; try `scripts/build-site.py`.

## Done: C (opening), in part (2026-11-16)

- The other version is fetched only when shown
  (`loadPar()`; `R.par` is `{ name }` until then; turning
  Side by side on fetches it, then builds it; if it
  cannot be read the part is read alone and the ⇆
  button goes). Saves 535 KB of JSON (about 83 KB
  compressed) to download and parse for a one-column
  reader; the tab memory did not change (117 against
  116 MB, `fresh 5`, one column).
- Page size: 10,000, 6,000, 4,000 and 2,500
  characters all gave 76-82 MB in the tab (the
  browser's floor is 70 MB), so the size stayed 10,000
  (fewest "Next" taps). Memory did not tell them
  apart, but speed does: on a slow CPU a turn is
  quicker with smaller pages (see P2 and "Done: H"
  below); `PAGE_CHARS` is 5,000 since 2026-11-22.
- Building a page in chunks: not done; the peak when
  opening is 128 MB (249 before pages), and a page is
  small. Look again only if a real phone still dies
  on opening.
- Left: the book files are about 500 KB of JSON for
  300 KB of text (a compact format would halve the
  download); not measured on the published site.

## Done: H, plain lines (2026-11-22)

Why: on a slow CPU (a Fire tablet) a page turn cost
about 200 ms at 10,000 characters (measured with the
CPU 8x slower), mostly building about 8,700 nodes and
the layout and style of them, not the script. Smaller
pages (P2) took it to 140 ms; plain lines to about
120 ms.

What changed in `web/app.js` (numbers:
`notes/browser-memory.md`, "Plain lines"):

- `showPage()` builds each line as plain text
  (`plainLine()`, class `pl`; sentence cuts are kept
  as empty `.cut` spans). Lines with bold or italic
  parts, and so `R.format[line].spans`, still get
  word spans (`fillLine()`).
- `expandLine(line)` turns a plain line into its words
  (`fillLine()`); `spanOf(i)` gives the element of
  word i, making it if needed; `wordRect(i)` gives the
  screen box of word i from a range over its letters,
  without making the element.
- A tap on a plain line (`text` click handler)
  expands that line and then asks
  `document.elementFromPoint()` which word is under
  the finger: no caret API, so no new browser
  requirement. A tap while text is selected does
  nothing, so selecting and the search button for the
  selection are as before.
- Everything that needed a word's element uses
  `spanOf()` (marks, the chosen word, the sentence,
  bookmarks, notes, `go()`, reveal); everything that
  only needed its place uses `wordRect()`
  (`topWord()`, `lastWord()`, keeping the place when
  the text size changes, the first word of the part).
  Removing a mark only touches `R.spans`: a line that
  is still plain has none.
- The cost moved to the first tap in a line (about
  30-50 ms more). A tap on a common word marks it in
  every line of the page, so it makes most of the
  page's words once.

Result (8x slower CPU): per page turn 173 to 123 ms at
10,000 characters, 141 to about 120 ms at 5,000;
nodes 8,764 to 4,210 and 4,619 to 2,375. Plain pages
of 10,000 turn as fast as word pages of 5,000.

### Still to do for this (small)

1. **Try it on the real Fire tablet** (the 8x CPU
   number is a model, not the device), at 5,000 and
   at 10,000 characters. If the tablet is fine at
   10,000, set `PAGE_CHARS` back to 10,000 (half the
   pages, the same speed).
2. **A test.** The checks were one-off Playwright
   scripts. Put a short one in `tests/` (skipped when
   Playwright is missing): open a part, expect no
   `.w` at first, tap a word and expect the panel and
   `R.sel`, `topWord()` equal with plain lines and
   with all lines expanded.
3. **Side by side toggled changes the top word** by
   a few words (5 in one check). Compare with the
   build before this change to see if it is new.
4. **The home page can replace the reader** when a
   part is opened while the home page is still
   loading (a hash change before it finished
   drawing). Found by the measuring script; it is
   older than this change. Find who draws last and
   make the route win.
5. Measure memory again (`why`, `fresh 5`): fewer
   nodes should lower the tab a little; it was not
   measured.

## Done: A and B

**A. Build the translation only while shown.**
Why: the other version (a `<p class="par">` after every
line) was built even when Side by side was off, and
only hidden by CSS: 55,000 nodes for nothing.
How (`web/app.js`): `book()` builds only the Grabar
lines and keeps each `<p>` in `R.lineEls`; `syncPar()`
(called by `applyView()` and once after the lines are
in the page) builds the `.par` lines, the two column
names and the translation credit when `R.par &&
view.parallel`, and removes them when it is turned
off. `R.parBuilt`, `R.ready` and `R.credited` keep the
state. The JSON of the other version is still fetched
(the ⇆ button needs its name); it is about 5 MB of
heap.

**B. `content-visibility: auto`.**
Why: the browser laid out all 125,000 nodes (about
60 MB), though only a screenful is seen.
How (`web/style.css`, before the Markdown section):
`.text > p` gets `content-visibility: auto` inside
`@supports`, and a `contain-intrinsic-height` guess of
`--rows * line-height`. `--rows` is set in `app.js` on
each line and each `.par` from its length (`rows()`,
36 characters a row): the whole page height came out
within 0.1% of the old one (340,399 against 340,739 px
side by side), so the scroll bar does not lie. The
`auto` form (Chrome 107+) makes the browser remember
the real height after a paragraph has been drawn; an
older browser gets the guess only; Chrome before 85
ignores it all.

What was checked (Playwright, phone screen): a link
`?line=3, 400, 1500, 1990` lands at the same place as
before and stays there; the saved reading position
comes back to the same line; Side by side off and on
works (a 40 px shift after switching on is the same as
before the change); no page errors. `pytest` passes.
**Not checked:** Safari and Firefox (c-v is Safari
18+, Firefox 125+), and an old Android WebView:
nothing should break (the property is ignored), but
try it.

## To do

### C. Lower the opening peak (about 110 MB for a moment)

Why: while a part opens, the JSON of both versions is
text and parsed data at once, and the nodes are being
built; a phone is killed at the peak, not at rest.
How, in order:
1. Fetch the translation only when it is shown (an
   `R.par = { name: other }` stub until `syncPar()`
   needs `lines`); then a one-column reader never
   downloads or parses it. Check every use of
   `R.par` (about 10 in `app.js`: `par`, `credit`,
   `first`, `starts`).
2. Build the Grabar lines in chunks (a few hundred
   lines per `requestAnimationFrame`) so garbage
   collection can run between them; keep the
   reading position working (`data.at`, `?line=`
   need all lines: build up to that line first).
3. Measure the peak: `node scripts/measure-memory.js
   fresh 5` (the `tab` column peak).

### D. Smaller parts (optional, no code)

Cut at about 150 KB instead of 300 KB in
`scripts/fetch-digilib.py` and re-cut the translations
to match (`PARALLEL`, lines one for one). Halves all
the numbers, at the price of twice the parts. Only if
C is not enough.

### E. Old browsers: a fallback page (do this first)

Why: `app.js` uses `?.` (Chrome 80+; lines 1994, 2313,
2316, 2626, 2690, 2920), `.flat()` and `.flatMap()`
(Chrome 69+; lines 36, 398, 1299) and `const`, arrows,
spread (Chrome 49+). On an older WebView the whole
script is a SyntaxError: a blank app.
How:
1. In `web/index.html`, before `app.js`, a tiny inline
   classic script: `try { new Function("a?.b");
   [].flat() } catch (e) { show a message }`. The
   message (Armenian, English) says the browser is
   too old and links to the plain pages
   `read/<book>.html` that `build-site.py` already
   writes, and to the list of browsers that work.
2. Do not load `app.js` when the test fails (put the
   `<script src="app.js">` in by `document.write` or
   `createElement` only when it passes).
3. Test with Playwright: block `?.` by serving a
   copy of the page with an old user agent is not
   enough; instead run the test function with a
   stub that throws, and check the message shows.
   Add a test in `tests/test_site.py` that
   `index.html` still has the check.

### F. Old browsers: make the code run

Pick one:
- **Build step for the site only**: `esbuild --target=chrome60`
  on `app.js` inside `scripts/build-site.py`
  (the rule "no build step" stays true for development
  and for `nxgir web`). Add small polyfills for
  `.flat()`, `.flatMap()`. Needs esbuild in the build
  (`pages.yml`).
- **By hand**: replace the 9 uses of `?.`, `.flat()`
  and `.flatMap()`; check with `acorn --ecma2015`
  (or `node --check` on an old Node).
- CSS fallbacks: a solid `color:` line before each
  `color-mix(...)` (`style.css`: lines about 493,
  542, 576), `top/right/bottom/left: 0` beside
  `inset: 0` (about 640), a `padding-top` hack or a
  fixed height beside `aspect-ratio` (about 592),
  `:is(...)` written out (about 102, 113).
- The service worker and "Save for offline" must fail
  silently without `serviceWorker` (already tested by
  `"serviceWorker" in navigator`: confirm).

### G. Low-memory mode

Why: on a 1-2 GB phone even 117 MB may be too much
next to the browser's own 110 MB and other apps.
How: when `navigator.deviceMemory` is 2 or less (or
unknown and the screen is small), default `view.parallel`
to false (only when the reader has not chosen: no
`nxgir-view` in `localStorage`) and show a short
note on the ⇆ button; offer a Settings switch
("Light mode"). With A done this costs nothing to
build. Measure with `why`, one column.

### J. Home page: not the script (measured)

Minifying or splitting `app.js` does not lower the tab
(see `notes/browser-memory.md`, "the home page"): its
size costs 0 MB. What is left to gain on the home page
is the two banner images (about 4 MB by resizing
`web/contribute.jpg` to 720 px and
`web/smbat-sparapet-face.jpg` to 444 px wide; also
the next announcement's `face`, `NEWS` in `app.js`),
and nothing else worth a change.

### H. Fewer nodes per word: done, see "Done: H"

What is left of the original idea (CSS Custom
Highlight API for the chosen word, bookmarks and
notes) is not needed: marks still use classes on
the word's span, made on demand. Look at it again
only if the first tap in a line proves too slow on a
real tablet.

### I. A window of lines (last resort)

Build only a few hundred lines around the screen while
scrolling. The least memory, but Ctrl-F finds only
what is built and the scroll bar lies. Only if H is
not enough.

## How to work

- One step at a time; measure before and after with
  `scripts/measure-memory.js` (`why`, `fresh 5`), write
  the numbers in `notes/browser-memory.md`.
- Check the reader still works: a line link, the saved
  position, Contents, a bookmark jump, Side by side
  off and on, a font-size change (the script used for
  A and B is described above; recreate it with
  Playwright: open `#/read/<part>?line=N`, read the
  `top` of that line's `<p>`, expect about 155 px).
- Before committing: `ruff format scripts/ tests/`,
  `ruff check scripts/ tests/`, `python3 -m pytest`.
  Max line width is 60 in `web/` too.
- Add a Timeline line and a limits record
  (`scripts/check-limits.py --site --record`) with a
  milestone, as `CLAUDE.md` says.
- Commit and push to the session's own branch; ask
  before pushing to `main`.
