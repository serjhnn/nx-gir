# Recording the video tutorial

How to make the short video of the web reader
(`scripts/record-web.py`, `scripts/record.js`). For
Claude, to pick it up again.

## Run

    NODE_PATH=/opt/node-tools/node_modules \
      python3 scripts/record-web.py out.mp4

- Needs `node`, `ffmpeg` and Playwright for Node. In
  the cloud container Playwright is in
  `/opt/node-tools/node_modules` and Chromium is
  installed; do not run `playwright install`. Elsewhere:
  `npm install playwright`.
- The wrapper starts the server on a free port with an
  empty state (your real bookmarks never show), runs
  `record.js BASE OUTDIR`, then converts the `.webm`
  to `.mp4` (h264, yuv420p, faststart). About 70 s,
  1280x720, 2.7 MB.
- A `BrokenPipeError` in the output is the server
  noticing the browser closed; the video is fine.
- Write the video outside the repo (the scratchpad);
  it is not kept in git (size limits, `notes/limits.md`).
  Send it to the user with SendUserFile.

## How record.js works

- Playwright `recordVideo` has no mouse pointer, so
  `INIT` (an init script) draws a round cursor that
  follows `mousemove`, and a caption box
  (`#rec-cap`). Both are made with `el.style.x = ...`
  (never a style attribute: the CSP forbids it) and
  are made again by a timer after each page load.
- `steps(p)` is the story: `cap("text")` sets the
  caption (`cap("")` hides it), `click(locator)`
  moves the mouse in 25 steps, then presses, `wait()`
  holds the shot, `scroll()` turns the wheel slowly.
- The captions are English only. The page language
  is `/en/`.

## Pitfalls (all met once)

- In the parallel view the words are NOT elements
  (no `.w`): click a point in the line,
  `.pl[data-l="4"]`, and wait for `.panel .entry`.
  Other books (single column) may differ; look.
- `a[hreflang="ru"]` is the language link; the
  text `Рус` matches two elements (strict mode).
- The theme button is `#theme` (an aria-label
  "Themes" is the blog's tabs). In the reader it is
  inside the text settings ("Text settings" button),
  so open them first.
- `Bookmark` also matches the toolbar's `★ 0`: scope
  it with `.panel`.
- The text settings open as a wide list over the page;
  keep that shot short. The font list changes the
  layout badly (Faulmann): left out.
- The init script runs before `documentElement`
  exists: guard it.
- Use a book without sacred words (CLAUDE.md,
  Examples): Smbat Sparapet's Chronicle is used.

## After the pages change

Run it and look at frames, not only the exit code:

    ffmpeg -ss 30 -i out.mp4 -frames:v 1 f.png

then Read the picture. Every selector above can
break with the UI; fix `record.js`, not the pages.

## To do

- Armenian and Russian versions: an argument for the
  language (`/hy/`, `/ru/`) and the captions in a
  table per language (the site's rule: no interface
  words in one language only).
- A phone-sized version (390x760, the phone view).
- Not shown yet: the font list, Features, Timeline,
  Blog, Comics, interpretations (Edit text).
