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
| C | Lower the opening peak | to do |
| D | Smaller parts (150 KB) | to do, optional |
| E | Old browsers: fallback page | to do, first |
| F | Old browsers: transpile / fallbacks | to do |
| G | Low-memory mode (default one column) | to do |
| H | Fewer nodes per word | later, big |
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

### H. Fewer nodes per word (later, big)

One text node per line, the tapped word found with
`caretPositionFromPoint()` / `caretRangeFromPoint()`,
bookmarks and the chosen word with the CSS Custom
Highlight API (Chrome 105+; fall back to spans below
that). About two thirds of the nodes go. Every place
that uses `R.spans` changes. Only after C-G if phones
still fail.

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
