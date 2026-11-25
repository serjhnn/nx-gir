# The map: how it works, and what to improve

Notes for the next session. The Map page was built on
2026-11-18 in four commits (6d829c1, 470f58e, 5f18e05,
0daf747), all on `main`. Read this first, then
`CLAUDE.md` (the `map/places.tsv` entry) and
`blog/README.md` (the `place:` line).

## What it is

A painted map of the Armenian Highland with a pin on
each place that a blog post or a comic is about. A tap
on a pin opens a small panel with links to those
stories. Names are the ancient Armenian ones only.

- Page: `#/map` and `#/map/<place>` (`mapPage()` in
  `web/app.js`).
- API: `/api/map` (`map_data()` in
  `scripts/nxgir_web.py`); on the site
  `data/map.json` (`build-site.py`).
- Data: `map/places.tsv` and the picture
  `web/img/map/base.webp`.
- Reader and builder: `scripts/nxgir_map.py`.
- Posts and comics name places on a `place:` line
  (`scripts/nxgir_blog.py`, `split_meta()`).
- Search engines: `map.<lang>.html` and
  `map/<id>.<lang>.html` (`map_pages()` in
  `build-site.py`), in the sitemap.
- A post page links its places (`placeNames()` and
  `placeChips()` in `app.js`).
- Tests: `tests/test_map.py`, and the map parts of
  `tests/test_site.py` and `tests/test_blog.py`.
- README picture: `docs/web-map.jpg` (made by
  `scripts/render-web.py`).

## The data

### `map/places.tsv`

Tab-separated, `#` lines are comments; the head of the
file explains the fields:

`id  kind  lat  lon  x  y  hy  en  ru  note`

- `id`: Latin letters and dashes (`bjni`, `nor-getik`).
- `kind`: `city`, `fortress`, `monastery`, `region`,
  `lake`, `mountain` (`KINDS`; the names in the three
  languages are `KIND_NAMES`, and `MAP_UI` in `app.js`
  must have the same; a test checks it).
- `lat`, `lon`: the true place, to about 0.1 degree.
- `x`, `y`: where the pin stands on the PICTURE, in
  percent of its width and height. **Every place has
  them** (a test checks it). See "The picture".
- `hy`: the ancient name, in the books' spelling
  (`եւ`, `աւ`, `է`). `en`, `ru`: the same name
  transliterated, never the modern name.
- `note`: the modern name and any doubt; not shown.

The 20 places now: bjni, gandzak, nor-getik, ani,
erebuni, duin, vagharshapat, artashat, armavir,
avarayr, tatew, narek, shamiramakert, baghesh, karin,
geghama-tsov (Lake Sevan), bznunyats-tsov (Lake Van),
aghtamar, masis (Ararat), aragats.

Only three have stories now: bjni (the Vasak comic),
gandzak and nor-getik (the Mkhitar Gosh post).

Low confidence for the true coordinates: `narek`,
`avarayr` (0.3 degree), `gandzak`, `nor-getik`.

### `place:` lines

After the title (and the theme), one line:

    place: gandzak, nor-getik

It is not shown. One version of a post is enough; the
others must not differ (like `theme:`). Comics take it
too (`comics/` uses the blog reader). A test checks
that every id exists in `places.tsv`.

### What `/api/map` returns

`nxgir_map.build()`:

    {"image": "img/map/base.webp",
     "kinds": [...],
     "places": [{"id", "kind", "x", "y", "lat", "lon",
                 "names": {"hy", "en", "ru"},
                 "stories": [{"type": "blog"|"comics",
                              "slug", "date",
                              "versions": [{"lang",
                                "title", "lead",
                                "cover", "alt"}]}]}]}

Stories are newest first. `lead` is the first paragraph
cut at 220 characters; `cover` is the first picture
file in `web/img/`.

## The picture

`web/img/map/base.webp`, 1536x1024, 459 KB, made with
ChatGPT's image generator (the prompt is below). It is
art, not a projection: drawn at an angle, lakes and
mountains are not to scale. Aragats is about 10% of the
width too far west, the Caspian too high.

So a formula from lat/lon cannot place pins. A
four-point perspective fit (homography) blew up (Karin
at x=398%); a least-squares affine fit over the seven
`CONTROL` landmarks in `nxgir_map.py` is off by up to
12%. Therefore:

- every place has its own `x`, `y`, set by eye on the
  painted castle, peak or lake it stands for;
- `project(lat, lon)` is only a rough default for a new
  place (`TOLERANCE` 13 is how far the control points
  may be from it);
- `BOUNDS` = 36.5-42.5 N, 38.0-49.5 E (south, north,
  west, east): a place outside is an error.

To set `x`, `y` for a new place: draw a 10% grid over
the picture with Pillow, look, read the percent. Then
draw all pins over the picture to check them (that is
how the 20 were checked).

### The prompt that made the picture

Kept so it can be redone at a higher resolution: a hand
painted antique parchment map of the Armenian Highland,
fantasy cartographic style, warm sepia and ochre, relief
mountains, small castles, dotted trade routes. No text,
frame, border, compass, legend, pins or UI; fill the
whole canvas edge to edge; 3:2; north up. Area: north
42.5, south 36.5, west 38.0, east 49.5. Black Sea only
in the top-left corner, a thin Caspian strip on the
right edge. Lake Van (38.65 N, 42.95 E) with an island
church, Lake Sevan (40.3, 45.3), Lake Urmia (37.7,
45.5), the Euphrates, Tigris, Araxes and Kura. Ararat
(39.70, 44.30) the most prominent mountain, Aragats
(40.53, 44.20) with a crater lake, Sipan (38.9, 42.85),
Taurus in the south, Caucasus in the north. About
eight small walled towns at the control points (Ani,
Yerevan, Van, Dvin, Bitlis, Malatya, Karin, an Artsakh
monastery), the rest of the land open. No sacred
symbols. Ask the generator to report the pixel centre
of Ararat, Sevan, Van, Ani and Yerevan.

If the picture is replaced, every `x`, `y` must be set
again, and the `CONTROL` list too.

## The page, `mapPage()` in `web/app.js`

Everything is in one function, drawn again by `draw()`
when the language or the filter changes (`st` keeps
the view: language, filter, selected place, zoom and
position).

- `.map-view` (aspect 3/2, `overflow: hidden`) holds
  `.map-stage` (the picture and the pins; moved and
  scaled by a CSS transform, origin 0 0), the zoom
  buttons `.map-ctl`, and the panel `.map-pop`.
- Pins are `<button class="pin pin-blog|pin-comics|
  pin-place">`; `left` and `top` in percent. They keep
  their size at any zoom (`--inv` = 1 / scale, set in
  `apply()`). A story newer than 14 days (`MAP_FRESH`)
  makes a pin glow (`fresh`). A pin with `x` > 88 has
  its label on the left (`pin-r`).
- Labels: shown for pins with stories and the selected
  one; for all pins at scale 2.4 or more (`zoomed`);
  on hover and focus.
- Zoom 1-3 (`MAP_MAX`); `apply()` clamps the position
  so the picture always covers the view. Controls: the
  + / − / ⌂ buttons, drag, pinch (pointer events, two
  pointers), Ctrl+wheel (a trackpad pinch), keys + - and
  arrows. The plain wheel scrolls the page. At scale 1
  the view has `touch-action: pan-y`, above 1 `none`.
- A drag is not a click: `moved` is set once the pointer
  went 6 px, and the pointer is captured then.
- The panel `.map-pop` (role dialog) is inside the view,
  not transformed. On a view 520 px wide or more it
  stands beside the pin and follows it as the map moves
  (`placePop()`, called by `apply()`); narrower, it
  docks at the bottom (`.dock`, max 70% of the height)
  and the zoom buttons go to the top (`.popped`). Closes
  by ×, Esc, or a tap on the map itself.
- A pin click does not move the map; the list under the
  map and `#/map/<id>` do (`center()`, zoom 2).
- The address is kept with `history.replaceState`
  (`#/map/<id>`, `#/map`), so no `hashchange` and no
  redraw.
- Filters: All, Blog, Comics, Places (the places with
  no stories). Language buttons use the blog's choice
  (`blogLang()`, `setBlogLang()`).
- Under the map a list of all places (a keyboard and
  screen reader way in, and a fallback).
- The panel's links go to `#/blog/<slug>` or
  `#/comics/<slug>` (`storyHref()`).

## Pitfalls met while building it

- **CSP.** `default-src 'self'` forbids a `style="..."`
  attribute, so pins were all stacked in a corner.
  Set `el.style.left = ...` from script instead (never
  `h("x", {style: ...})`). The Statistics page's meter
  bar has the same problem and was not touched.
- **`h()` flattens one level.** `h("p", {}, ids.map(
  id => [", ", link]))` prints the links as text. Use
  `flatMap`, or wrap the list in an element.
- **Wide-screen CSS.** `tests/test_web.py` requires every
  selector in a `@media (min-width: ...)` block to start
  with `.wide `.
- **`scripts/build-site.py --help` is not help.** It
  built a 160 MB site into a folder named `--help`.
  Give it a real output folder, or call `bs.build()`
  from a test. Delete a stray folder.
- **Screenshots.** `scripts/render-web.py` rewrites all
  its `docs/` pictures; `git checkout` the ones that did
  not need to change. The map picture is a JPEG (a PNG
  was 964 KB). No sacred words in them (`CLAUDE.md`).
- **Line width** is 60 characters in `app.js`,
  `style.css` and Python too.
- Running the page for tests: `NXGIR_STATE=<scratch
  file> python3 scripts/nxgir-cli.py web --port 8088`,
  then Playwright (`require('playwright')` works
  anywhere); a phone is 390x760 with `hasTouch` and
  `isMobile`. There are no JS unit tests; drag, zoom,
  the filters, Esc and the panel were checked this way
  and are not in the test suite.

## To do, in the order I would do it

1. **A better picture.** 1536 px is soft above 2x on a
   large screen. Ask the generator for a larger one
   (prompt above); keep each place on the same painted
   feature if possible, else set every `x`, `y` again.
   Keep the file near 500 KB (webp), or serve two sizes
   and swap at zoom 2. Fix Aragats while at it.
2. **More places and stories.** Only three places have
   stories. The Library authors (Khorenatsi, Yeghishe,
   Agathangelos, Smbat, Tatevatsi, Narekatsi) can have
   posts with `place:` lines, and the Timeline's
   entries could too. Add a place to `places.tsv` with
   its `x`, `y`; the 17 that exist without stories
   are ready.
3. **Pins from books.** A part of a book (Yeghishe's
   Vasn Vardanay: Avarayr) could name its places, shown
   in the reader and the book page. Needs a new file
   (e.g. `map/books.tsv`: book path, place ids) and a
   field in `/api/volume`; not designed yet.
4. **Close pins.** Pins that touch (Armavir,
   Vagharshapat, Erebuni, Duin, Artashat) overlap at
   scale 1. Cluster into a count badge when zoomed out,
   or nudge the `x`, `y` apart.
5. **The Announcements filter.** The mockup had it;
   announcements are in `app.js` (`newsPage()`), not in
   data, so a pin cannot name them yet. They would need
   to move to files first.
6. **Cilicia and the diaspora.** Out of bounds (west
   edge 38 E). Hetum Patmich's Sis (37.4 N, 35.8 E) is
   not on the map. A second picture and a second page,
   or a wider first one; both change `BOUNDS`.
7. **Phone.** The map is only about 240 px tall at
   390 px width, and the docked panel covers most of
   it. Try a taller view on narrow screens (a 4:3 crop
   of the picture), a smaller panel, or a bottom sheet
   that can be dragged.
8. **Check the coordinates** of `narek`, `avarayr`,
   `gandzak`, `nor-getik` against a source and note it
   in the `note` column.
9. **Limits.** The picture and the 12 new pages are in
   the site size; run `scripts/check-limits.py --site
   --record` after the next batch of content.
10. **Place pages for search engines** have only a title
    and the story leads; thin. Add the note (the modern
    name) or a sentence about each place when there is
    content for it.
11. **Tests in a browser.** The panel, drag and zoom
    have none; a Playwright check in a script under
    `scripts/` (like `measure-memory.js`) would keep
    them from breaking.

## Decisions the user made

- Old Armenian names only, everywhere, no modern names
  on the map ("it is an ancient map"); the modern name
  lives in `note`.
- English and Russian show the old names transliterated
  (Masis, Duin, Baghesh).
- Ararat is Masis, Yerevan is Erebuni, Van is
  Shamiramakert, Lake Sevan is Geghama Tsov, Lake Van is
  Bznunyats Tsov, Goshavank is Nor Getik, Bitlis is
  Baghesh.
- A small panel at the pin, not a card below the map.
- One developer, no pull requests: commit to the
  session branch, push, ask before pushing to `main`.

## The 3D map (2026-11-25)

`#/map3d` (`web/map3d.js`): the same picture on a
relief, `web/img/map/height.png` (384x256), made by
`scripts/render-heightmap.py`. The relief is not from
real heights (the picture is not a projection): the
painted ranges and peaks are `RIDGES` there, set by eye
like the pins, and the strokes of the painting roughen
them; the water stays flat. Change `RIDGES` and run the
script again to raise or move a range.

To do: try it on a real phone (speed, touch); maybe a
lower `SEG_X`/`SEG_Z` there. Under it, the list of 3D
reconstructions (`web/models/`, see CLAUDE.md); a
place with a model has a "3D model" link in its panel
on the 3D map (Glakavank now).
