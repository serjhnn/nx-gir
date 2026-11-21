# Search: a plan

Search across the whole library, in Grabar and in
the translations, on `nxgir web` and on the Pages
site (no server there). Step 1 is built
(2026-11-21, see Steps); the numbers
below were measured on 2026-11-21 (after the
merge of main at 4399b9a) with a prototype.

Search inside one part already exists: tap a word
and the ‹ › arrows go through its places in the
part ("Every place a word appears").

Decided (2026-11-21):
- The Bible is not searched, for now.
- A search box on every page, at the top of the
  page (on the home page under the menu buttons).
- Results open on Գրաբար; the filters show the
  translations too (Աշխարհաբար) or both
  (Բոլորը) when the reader wants.
- Results by author, folded, in the Library's
  order; a tap unfolds one.
- The search box stays in view on scrolling (it
  sticks to the top). Not in the reader (decided
  later the same day): there the word panel has
  "Որոնել ամբողջ գրադարանում · 915" (the Grabar
  lines), and selected text (up to 6 words) a
  button at the bottom of the screen that searches
  its words.
- A book in two editions (the Taregirk and the
  Taregirk (Digilib)) shows in both.
- Under Բոլորը a Grabar line and its translation
  (the same line of the same part) are one result:
  the Grabar line, its translation under it, counted
  once, whichever of the two has the word
  (`paired()` in `app.js`). թագավոր: 1,014 places,
  not 932 + 192 lines.

## What it finds

1. **A word, in either spelling.** A reader types
   modern spelling; the books are in the classical
   one. Both are folded to one key, so `թագավոր`
   finds `թագաւոր` and the other way round:
   - `normalize()` first (as `wordKey()` in
     `app.js`),
   - then `ւ` → `վ` (but not in `ու`), `իւ` → `յու`,
     `եա` → `յա`, `եօ` → `յո`, `է` → `ե`, `օ` → `ո`,
     and `յ` before a vowel at the start → `հ`.
   The results show each spelling found and how
   often (`թագաւոր 1071 · թագավոր 195`).
2. **All forms of a word** (a switch): the forms
   of the word in `grabar/forms.tsv`, the same
   table the word lookup uses. `թագավոր`: 1,074
   lines; with all forms (`թագաւորի`,
   `թագաւորաց`, `թագաւորք` ...) 2,382.
3. **A phrase** in quotes: the words next to each
   other, in that order (`"արքայ Հայոց"`: 48 lines
   in 11 books).
4. Later: scribal abbreviations
   (`վարդապետ` also finds `վրդ`, from
   `abbreviations.tsv`), a word's start
   (`թագաւ*`), and search inside one book (from
   its page).

A line is one hit, however many times the word is
in it. Matching is on whole words only.

## The pages

Screenshots: `search-1` to `search-9`, and
`search-2b` (mockups
drawn inside the real web reader, with real
results).

- **Where it starts**: a search box on every
  page, at the top of the page under the top bar:
  on the home page under the row of menu buttons
  (1), on the Library (8) and in the reader above
  the book's path (9). On a results page it is
  under the heading and holds the search (2). The word panel in the
  reader gets "Որոնել ամբողջ գրադարանում ·
  1074" under the ‹ › of the part (6).
- **Results** (`#/search?q=...`, 2): the count
  (`892 տող · 40 հեղինակ · 58 գիրք`), the filters
  Բոլորը / Գրաբար / Աշխարհաբար with their counts,
  Գրաբար chosen at first (`&in=` keeps another
  choice), the "Բոլոր ձևերը" switch and the
  spellings found. Then the authors, in Library
  order, each folded: a row with › , the name and
  `147 տող · 3 գիրք` (the books only when more
  than one). "Բացել բոլորը" unfolds them all.
- **An author unfolded** (2b): its books, each
  with its count and its first two lines, the word
  marked, "մաս 1 · տող 1656", and "Բոլոր 43
  տողերը →" for the rest. A tag says Գրաբար or
  Աշխարհաբար when both are shown. The unfolded
  authors stay in the link (`&open=`), so the
  back button from the reader finds them open.
  With one author only, it is unfolded at once.
- **All forms** (3): the forms found, each a chip
  with its count; tapping one turns it off.
- **A phrase** (4): a hint under the box says what
  the quotes do.
- **In the reader** (5): a result opens the part at
  its line (`#/read/<part>?line=N`, as now), with
  the word marked, and a strip under the reading
  tools: `Որոնում՝ թագավոր · արդյունք 37 / 1074`,
  ‹ › to the next result (into the next part or
  book), ← back to the results where they were.
- Dark and black themes take the colors as they
  are (7: the translations chosen). The labels are in Armenian, as on the
  home page.

## How it is built

One module, `scripts/nxgir_search.py` (tested in
`tests/test_search.py`): `loose()`, the index of a
set of parts, and the search over it. Its users:

- `nxgir web`: `/api/search?q=&in=&forms=`; the
  index is built in memory on the first search (a
  few seconds) and kept.
- `build-site.py`: writes the index as files, read
  by `staticApi("search")` in `app.js`.
- (Maybe) `nxgir search` in the terminal.

`loose()` in `app.js` must match the Python one,
as `wordKey()` does `normalize()` (a test checks
both).

### On the Pages site

- `data/search/<bucket>.json`: the loose key of
  each word → its spellings → the lines it is in,
  as `[part, line, line, ...]` with the lines
  delta-coded. 256 buckets, as the word lookups.
  A search fetches one bucket a word.
- `data/search/parts.json`: the number of each
  part → its name, book and author.
- `data/lines/<part>/<n>.json`: the text of the
  part, 100 lines a file, for the lines shown in
  the results and to check a phrase. Only the
  files of the shown lines are fetched (20 lines on
  the first screen: at most 20 small files).
- A phrase: the lines that have all its words
  (from the buckets), then the order checked in
  the line files. Over 300 such lines, the count
  says "about".
- Very common words (in more than 5,000 lines:
  `եւ`, `ի`, `է`, `զի`, `որ`, `ոչ` ...) are not
  in the buckets: alone they say "too common, add
  a word"; in a phrase they are checked in the line
  files only.

### Size (measured; the Bible is not searched)

| What | Now |
|---|---|
| Grabar | 220 parts, 40.9 MB, 2.6 M word-lines, 247 k words |
| Translations | 39 parts, 7.3 MB, 0.5 M word-lines, 48 k words |
| Index, plain JSON | about 32 MB, less delta-coded |
| Line files | about 50 MB |

The site would grow from about 193 MB to about
275 MB (27% of 1 GB) and the build by about 15 s.
Run `check-limits.py --site --record` after it.

## Steps

1. (Built 2026-11-21.) A word in either spelling, Grabar and
   translations: the module, `/api/search`, the
   site files, the results page (by author,
   folded), the search box
   on every page, the strip in the reader. Tests; a
   Features entry in hy, en, ru; a Timeline line; a
   limits record.
   Built as planned, with these differences: the
   index is served as data and the search runs in
   `app.js` (the same code for `nxgir web` and the
   site); a search of several words finds the lines
   with all of them, in any order (the phrase in
   quotes is step 2); the reader's strip is a row
   of its tools. `nxgir web` builds the index in a
   thread at start (about 10 s, some 300 MB at the
   peak, 40-70 MB kept). The site: 267 MB (search
   26 MB, lines 51 MB), the build about 70 s.
2. Phrases, all forms. (The button in the word
   panel was built with step 1, with one for
   selected text.)
3. Abbreviations, a word's start, inside one book.

## Open questions

None now.
