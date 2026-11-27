# The paper texture: what went wrong, what helped

The papers (papyrus, parchment, vellum, candle;
`PAPERS` in `app.js`, the colors and textures in
`web/style.css`) draw a texture behind the text:
noise from SVG filters (`feTurbulence`, data: URLs,
no image files) in two or three layers, and a darker
edge (a `radial-gradient`). Three problems came up
on a phone in November 2026, one after the other.
How each was found, what was tried, what was kept,
and the numbers.

    node scripts/measure-paper.js
    SVG=1 node scripts/measure-paper.js

(with `nxgir web` running; see "Measuring" below)

## 1. A bare strip at the bottom (20e6a67)

The texture was a fixed layer (`body::before`,
`position: fixed; inset: 0`), as tall as the
screen. On scrolling, the phone's browser hides its
address bar and the screen grows; the layer kept
the old height, and the page's plain color showed
below it, a light strip as tall as the bar, over
the text.

Fixed by making the layer as tall as the screen
with the bar hidden: `height: 100lvh` (the large
viewport; `100vh` before it for old browsers).

## 2. Scrolling lagged (d6c8fdd, a guess)

After that, scrolling felt slow. A guess, not
measured: the fixed layer, now taller than the
screen, was painted again while scrolling. Tried
`will-change: transform; contain: strict` to give it
a layer of its own, painted once. Replaced by 3
before it could be judged.

## 3. The texture moves with the text (712ef50)

Asked for: the texture should scroll with the text,
like a real page, not stay still behind it. The
fixed layer went; the texture is now the page's own
background (`:root[data-paper] body`), which also
ends problem 1 for good: a page background covers
the page however tall the screen grows.

The edge gradient now spans the whole page, not the
screen: on a long part only the left and right edges
are darker. Accepted.

## 4. Still slower than no paper (35a644f)

Scrolling with a paper was still clearly worse than
with none. This time measured.

### Measuring

A phone screen (Playwright's Pixel 7, 412x915, 2.6
pixels a point), Chromium headless, the part
`grabar/hovhan-mamikonean/1-patmutiun-taronoy/01.txt`
(long, in two languages). The page jumps 8 times to
text not painted yet; the browser must paint the
new tiles each time. What is counted: the time of
the `RasterTask` events in a trace, the work of
turning the page into pixels, which is where a
texture costs (it runs off the main thread).

Two first tries measured the wrong thing:

- frames on the main thread (`requestAnimationFrame`
  intervals): the same 16.7 ms with and without a
  paper, as raster is not on the main thread;
- the time of a screenshot: 120 ms without a paper,
  950 ms with one, but much of that was saving a
  noisy picture as PNG, which compresses slowly. The
  raster trace is the true cost.

### Where the time goes (raster, 8 new screens)

| background | ms |
|---|---|
| no paper | 8 |
| parchment: noise + edge gradient | 2797 |
| noise only | 2503 |
| edge gradient only | 83 |
| no texture, only the paper's colors | 11 |

The noise is the cost: two or three semi-transparent
layers, each an SVG filter, drawn again for every
new tile while scrolling. The gradient over the
whole page costs little.

### What was tried

| try | ms | kept |
|---|---|---|
| as it was (SVG layers) | 2797 | |
| each layer a bitmap, still layered | 3004 | no |
| all in one opaque tile, with color | 442 | yes |

Turning each layer into a bitmap does not help: the
cost is in blending several semi-transparent layers
over the whole page, not only in the filter.
Flattening them into one opaque picture does.

### The fix: `bakePaper()` in `app.js`

When a paper is set (`applyView()`), `app.js` reads
the paper's `--paper-img` and `--paper-size`, draws
the SVG layers once into a canvas, on the paper's
`--bg`, bottom layer first, and sets the result (a
WebP data: URL) as `--paper-img` on `<html>`, with
the edge gradient after it. Kept for each paper
while the page is open (`baked`). If anything fails
(a browser that will not draw an SVG into a canvas),
the SVG layers stay, as before.

The tile is as wide as the biggest layer (700 px),
so every layer's size must divide it: papyrus's
layers went from 320 px to 350, the fine grain of
the other papers from 180 px to 175 (the noise is
seamless at any size, `stitchTiles`). A new paper
must keep to this (a comment in `style.css` says
so), else `bakeTile()` gives up and the SVG stays.

The tile is drawn at 2 pixels a point at most
(1400x1400, about 7.8 MB of memory once decoded);
more did not change how it looks.

### Result (`scripts/measure-paper.js`)

| paper | before (SVG) | after (tile) |
|---|---|---|
| no paper | 107 | 107 |
| papyrus | 3696 | 478 |
| parchment | 2808 | 363 |
| vellum | 2617 | 508 |
| candle | 2700 | 447 |

(ms of raster for 8 new screens; the no-paper line
here includes the page's own text and buttons.)
About 6 to 8 times less work than before, still 3 to
5 times the no-paper page. This is software raster
on a desktop CPU; a phone paints a repeated bitmap
on its GPU, where it is cheaper still, while the SVG
filters stay costly there too.

On the user's phone (Android, the published
site, 2026-11-27): scrolling with a paper is smooth
now, as with none.

### How it looks

Each layer drawn by CSS and drawn into the canvas
gives the same color to the pixel's mean. The whole
page with the tile against the SVG layers, same
place: papyrus, vellum and candle differ by 1-4 of
255 on average; parchment by 6-9, a little lighter
(its big blotches are a bit softer), not visible
side by side. Accepted.

## Pitfalls

- `getComputedStyle(...).getPropertyValue()` of a
  custom property gives the text as written, with
  the `\` line breaks of `style.css`: take them out
  before using the URL (`svgLayers()`), and write
  `#` as `%23`.
- A `)` inside the SVG (`filter='url(%23n)'`) ends a
  naive `url(...)` match: match up to the closing
  `"` instead.
- `theme.js` sets the paper before `app.js` runs, so
  the first moments of a page use the SVG layers;
  the tile takes over as soon as it is drawn.

## Next, if needed

- Measure on a real phone in numbers (Chrome's
  DevTools over USB, Performance panel), if it ever
  feels slow again.
- If drawing the tile at start is slow on a phone,
  make the tiles ahead of time (a `render-*.py`
  script, WebP files in `web/img/`), at the cost of
  about 0.1-0.7 MB a paper.
- The edge gradient over the whole page could go
  back to a fixed layer of its own (`100lvh`), if
  its 80 ms or the look along a long page matters.
