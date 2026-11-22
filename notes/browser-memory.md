# Browser memory of the web reader

How much memory a browser needs to read a part in
the web reader (`nxgir web` and the Pages site,
the same `web/app.js`), why it takes that much, and
what could make it smaller if a phone ever has
trouble. The short form and the limit are in
`notes/limits.md`.

## How it was measured (2026-11-11, commit f015bc5)

`scripts/measure-memory.js`, with `nxgir web`
running (and `NXGIR_STATE` set to an empty folder,
so no saved positions get in the way). It drives
the Chromium that comes with Playwright, headless,
on Linux:

    node scripts/measure-memory.js parts
    PHONE=1 node scripts/measure-memory.js fresh 5
    PHONE=1 node scripts/measure-memory.js why \
      grabar/mkhitar-gosh/1-datastanagirk-a/01.txt

- `parts`: all 93 parts of `books/grabar/` and
  `books/ashkharhabar/`, largest first, opened one
  after another in one tab as a reader would: to
  the end of the text and three words looked up.
  Desktop (1400x900) and phone (390x844, touch).
- `fresh`: the same, each part in a new browser:
  what one part costs alone.
- `why`: one part five ways (below), each after a
  garbage collection: where the memory goes.

What is counted:

- **heap**: the JavaScript heap of the page
  (`JSHeapUsedSize`): `app.js`'s data.
- **elements**: the DOM nodes of the page
  (`Nodes`; elements and text nodes).
- **tab**: the memory (PSS) of the renderer
  process, the tab: DOM, layout, styles, images,
  heap, all of it. This is what a phone runs out
  of.
- **all**: every Chromium process (the browser
  and GPU processes too, about 110 MB of it
  without any page).

## What was found

One part in a fresh tab, phone screen, the
largest parts:

| Part | Words | Elements | Heap | Tab |
|---|---|---|---|---|
| Datastanagirk A 01, side by side | 24,922 | 127k | 12 MB | 297 MB |
| Amaran hator 05, side by side | 23,720 | 121k | 11 MB | 291 MB |
| Amaran hator 12, side by side | 23,957 | 121k | 11 MB | 288 MB |
| Matean 01 (Grabar alone) | 21,060 | 67k | 11 MB | 207 MB |
| Datastanagirk C 01 (Grabar alone) | 22,624 | 70k | 11 MB | 208 MB |

The home page alone is 65 MB of the tab. The whole
browser was at most about 410 MB. A desktop screen
takes a little more (325 MB for the first part):
more of the text is drawn at once.

All 93 parts one after another in one tab: the
heap never passed 46 MB; the tab grew to about
1 GB (desktop) and 870 MB (phone), but that was
garbage not yet collected: after a collection the
tab was 180 MB and 2,770 elements, the same as the
home page. **Nothing is kept from a part once
another is open**: no leak. (A heap snapshot
showed this; an early run seemed to leak because
Playwright's `waitForSelector` handle kept each
part alive, so the script now disposes it.)

### Where it goes

Datastanagirk A 01 (274 KB of Grabar) with its
translation (297 KB) side by side, phone screen,
after a garbage collection:

| Case | Elements | Heap | Tab |
|---|---|---|---|
| Home page | 323 | 1 MB | 64 MB |
| Side by side | 125,519 | 5 MB | 186 MB |
| The same, scrolled to the end | 125,519 | 5 MB | 190 MB |
| Translation hidden (one column) | 125,516 | 5 MB | 159 MB |
| Text not laid out (`display: none`) | 125,519 | 5 MB | 127 MB |

So of the about 120 MB the part adds:

- **about 60 MB is the DOM**: 125,000 nodes, about
  500 bytes each (the node, its text, its
  `class` and `data-i`);
- **about 60 MB is the layout** of the whole text
  (boxes and lines for every word), 30 MB of it
  for the translation column;
- **the JavaScript data is small**: 5 MB at rest.

Scrolling to the end adds almost nothing: the
picture is drawn only where the screen is. Opening
a part takes about 110 MB more for a moment (297
against 186 MB): the JSON of both versions as text
and parsed, the nodes being built, and memory the
tab keeps for later after it is freed.

As a rule of thumb: **about 0.5 MB of tab per KB
of text** opened (both versions counted), on top
of 65 MB for the page itself.

## Why it takes that much

- **Every word is an element.** `book()` in
  `app.js` puts each word in a `<span class="w"
  data-i="...">` so that a tap finds it, and
  bookmarks, notes, search and the reading
  position point at it (`R.spans`, `R.keys`,
  `R.wpos`). A Grabar word is three nodes: the
  span, its text and the space after it. That is
  about 70,000 nodes for 22,000 words.
- **The translation is built even when hidden.**
  Side by side adds a `<p class="par">` after
  every line with the other version as plain text
  (no spans), about 55,000 nodes more; hiding it
  (the one-column view) only stops its layout.
- **The whole part is in the page at once**, so
  the browser lays out all of it, not only the
  screen. This is what makes Ctrl-F, the Contents
  and the reading position simple and exact.
- **A part is about 270–300 KB** of text: parts
  are cut by `fetch-digilib.py` and kept under
  1 MB (`notes/limits.md`).

## How to make it smaller, if needed

Measure before and after with `why` and `fresh`.
From the cheapest change to the largest:

1. **Don't build the translation when it is
   hidden**, or build it on the first switch to
   side by side: saves its 55,000 nodes and 30 MB
   of layout for readers of one column.
2. **Lay out only what is near the screen**:
   `content-visibility: auto` with a
   `contain-intrinsic-size` on the paragraphs of
   `.text` (CSS only). Could save most of the
   60 MB of layout. Check that the reading
   position, `lastWord()`, the Contents and
   jumping to a bookmark still land on the right
   word: they measure with
   `getBoundingClientRect()`, and paragraphs not
   laid out have only their estimated height.
3. **No `data-i` on every span**: find the index
   with a `WeakMap` from span to index, or from
   the position of the span in `R.spans`. A few
   MB.
4. **Fewer nodes per word**: keep one text node
   per line and find the tapped word with
   `document.caretPositionFromPoint()`
   (`caretRangeFromPoint()` in older Chrome); show
   the chosen word, bookmarks and notes with the
   CSS Custom Highlight API instead of classes on
   spans. About two thirds of the nodes go, but
   every place that uses `R.spans` changes.
5. **Smaller parts**: cut at about 150 KB instead
   of 300 KB (`fetch-digilib.py`, and the
   translations with them). Halves everything,
   but means more parts to page through.
6. **Show only a window of the part** (a few
   hundred lines around the screen, built while
   scrolling). The smallest memory, but the
   largest change: Ctrl-F would find only what
   is built, and the scroll bar would lie.

The phone readers today (Chrome on Android with
3 GB or more) have room for the largest part; the
first sign of trouble would be Android reloading
the tab in the background (the position is saved,
so nothing is lost). Start with 1 and 2 then.

## After steps 1 and 2 (2026-11-16)

Both are done (plan: `notes/ram-plan.md`): the other
version is built only while Side by side is on
(`syncPar()` in `app.js`), and `.text > p` has
`content-visibility: auto` with a height guess from
the line's length (`--rows`, `style.css`).

Datastanagirk A 01, phone screen, after a garbage
collection (`why`):

| Case | Before | After |
|---|---|---|
| Side by side | 184 MB | 140 MB |
| Side by side, scrolled to the end | 190 MB | 160 MB |
| One column | 154 MB | 117 MB |
| One column, elements | 125,525 | 73,668 |

The page height stays within 0.1% of what it was, and
line links, the saved position and Side by side off
and on land where they did.

## In pages (2026-11-16)

A part is read a page at a time (the default; the ▤
button in the text settings turns it off): about 5,000
characters of Grabar are in the page, the rest is
only data (`showPage()` in `app.js`; plan:
`notes/ram-plan.md`). Same part, phone screen:

| Case | One long text | In pages |
|---|---|---|
| Side by side | 144 MB | 82 MB |
| One column | 118 MB | 78 MB |
| Elements, side by side | 125,533 | 7,313 |
| Peak when opening (5 largest, `fresh 5`) | 249 MB | 128 MB |

The home page is 70 MB, so a page adds about 12 MB
(against about 75 MB). All 15 pages one after
another: no growth (heap 5.3 MB, 7,300 to 8,400
elements). Ctrl-F finds the page only.

## The home page, what the 70 MB is (2026-11-16)

Phone screen, tab memory after a garbage collection,
three runs each (the 47 MB floor is `about:blank`):

| Case | Tab |
|---|---|
| Real home page | 70.7 MB |
| `app.js` parsed but not run | 54.4 MB |
| `app.js` empty | 54.4 MB |
| `app.js` minified (esbuild) | 70.3 MB |
| `app.js` and `style.css` minified | 69.6 MB |
| No `style.css` | 59.7 MB |
| Images resized to about 2x their size | 66.5 MB |
| No images | 63.5 MB |

- **The size of the script costs nothing**: parsing
  all of `app.js` is the same as an empty script, and
  minifying changes nothing. So minifying, or
  splitting rarely used pages out of `app.js`, would
  not lower the tab. (The first guess of 18 MB for
  "scripts" was wrong: blocking JS also removes the
  images, the shelf and the fonts it draws.)
- What costs is what the page draws when it runs: the
  two banners (1200x675 and 600x400, shown at about
  358x120 and 222x120, decoded at full size) cost
  about 7 MB, 4 MB of it saved by resizing them to
  720 and 444 px wide (140 and 59 KB to 68 and 39 KB);
  fonts about 2 MB; the rest is layout and painting of
  the styled page.
- Numbers are from headless Chromium on Linux; an
  Android WebView will differ, but the order should
  hold.


## Page size 5,000 (2026-11-22)

`PAGE_CHARS` went from 10,000 to 5,000 for slow
devices. Measured with the CPU throttled 8x (CDP),
Pixel 5 screen, Datastanagirk A 01, median of 3 runs,
a fresh state each:

| Page | Pages | Nodes | 5 turns | Per turn |
|---|---|---|---|---|
| 10,000 | 15 | 8,763 | 1,010 ms | ~200 ms |
| 5,000 | 29 | 4,618 | 701 ms | 140 ms |
| 3,000 | 48 | 3,129 | 534 ms | 106 ms |

Opening a part costs the same (fetch and parse, about
1.1 s at 8x). A turn is mostly layout and style, not
script: caching `fit()` and `setStick()` changed
nothing (their time was the first forced layout).
A prototype with no word spans (one text node per
line, option 4 above) reached 121 ms a turn at 10,000
and 105 ms at 5,000: not worth the change for now.

## Plain lines, words on demand (2026-11-22)

A line of the page is built as plain text (class `pl`,
`plainLine()` in `app.js`), with no `<span class="w">`
for each word. A word's element is made only when
something needs it: a tap (`expandLine()`, then
`elementFromPoint()` finds the word under the finger,
so no caret API is needed), a mark, a note, the
sentence highlight, a jump (`spanOf()`). Where a word
is on the screen (the reading position, keeping the
place when the text size changes) comes from a range
over its letters (`wordRect()`). Lines with bold or
italic parts are built with words as before.

Same setup as above (CPU 8x slower, Pixel 5 screen,
Datastanagirk A 01, median of 3 runs):

| Page | Build | Nodes | Per turn | Tap, rare word | Tap, common word |
|---|---|---|---|---|---|
| 10,000 | words | 8,764 | 173 ms | 208 ms | 70 ms |
| 10,000 | plain | 4,210 | 123 ms | 237 ms | 70 ms |
| 5,000 | words | 4,619 | 141 ms | 163-184 ms | 112-127 ms |
| 5,000 | plain | 2,375 | 113-130 ms | 213 ms | 129-159 ms |

- A turn is 15-30% quicker; script time halves (385 to
  199 ms for 5 turns at 10,000).
- The first tap in a line costs 30-50 ms more (the
  line is made into words). A common word marks
  itself in every line of the page, so that tap
  makes most of the page's words, once.
- Plain pages of 10,000 turn as fast as word pages of
  5,000, with half the pages.
- The reading position is the same with plain and
  with word lines (checked at three scroll places);
  taps found the right word 28 of 28 times.
- The measuring harness must wait for the home page
  to finish before opening a part: a hash change
  while the home page is still drawing can leave the
  home page on the screen.
