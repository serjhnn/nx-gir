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
