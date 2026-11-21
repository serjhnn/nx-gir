# Search: a plan

Search across the whole library, in Grabar and in
the translations, on `nxgir web` and on the Pages
site (no server there). Not built yet; the numbers
below were measured on 2026-11-21 with a prototype.

Search inside one part already exists: tap a word
and the ‹ › arrows go through its places in the
part ("Every place a word appears").

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
   often (`թագաւոր 770 · թագավոր 128`).
2. **All forms of a word** (a switch): the forms
   of the word in `grabar/forms.tsv`, the same
   table the word lookup uses. `թագավոր`: 762
   lines; with all forms (`թագաւորի`,
   `թագաւորաց`, `թագաւորք` ...) 1,754.
3. **A phrase** in quotes: the words next to each
   other, in that order (`"արքայ Հայոց"`: 41 lines
   in 9 books).
4. Later: scribal abbreviations
   (`վարդապետ` also finds `վրդ`, from
   `abbreviations.tsv`), a word's start
   (`թագաւ*`), and search inside one book (from
   its page).

A line is one hit, however many times the word is
in it. Matching is on whole words only.

## The pages

Screenshots: `search-1` to `search-7` (mockups
drawn inside the real web reader, with real
results).

- **Where it starts**: a search box on the home
  page, under the buttons (1); the word panel in
  the reader gets "Որոնել ամբողջ գրադարանում ·
  762" under the ‹ › of the part (6).
- **Results** (`#/search?q=...`, 2): the box, the
  count (`762 տող · 42 գիրք`), the filters
  Բոլորը / Գրաբար / Աշխարհաբար with their counts,
  the "Բոլոր ձևերը" switch and the spellings
  found. Then the books in Library order, under
  their authors as on the Library page: each book
  with its count and its first two lines, the word
  marked, "մաս 1 · տող 1656", and "Բոլոր 48
  տողերը →" for the rest. A tag says Գրաբար or
  Աշխարհաբար when both are shown.
- **All forms** (3): the forms found, each a chip
  with its count; tapping one turns it off.
- **A phrase** (4): a hint under the box says what
  the quotes do.
- **In the reader** (5): a result opens the part at
  its line (`#/read/<part>?line=N`, as now), with
  the word marked, and a strip under the reading
  tools: `Որոնում՝ թագավոր · արդյունք 37 / 762`,
  ‹ › to the next result (into the next part or
  book), ← back to the results where they were.
- Dark and black themes take the colors as they
  are (7). The labels are in Armenian, as on the
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

### Size (measured, without the Bible)

| What | Now |
|---|---|
| Grabar | 177 parts, 33.5 MB, 2.1 M word-lines, 212 k words |
| Translations | 37 parts, 6.8 MB, 0.5 M word-lines, 46 k words |
| Index, plain JSON | about 27 MB, less delta-coded |
| Line files | about 40 MB |

The site would grow from about 158 MB to about
220 MB (22% of 1 GB) and the build by about 15 s.
Run `check-limits.py --site --record` after it.
With the Bible in, add its share; whether it is
searched is a question below.

## Steps

1. A word in either spelling, Grabar and
   translations: the module, `/api/search`, the
   site files, the results page, the box on the
   home page, the strip in the reader. Tests; a
   Features entry in hy, en, ru; a Timeline line; a
   limits record.
2. Phrases, all forms, the button in the word
   panel.
3. Abbreviations, a word's start, inside one book.

## Open questions

- Is the Bible searched too? (It is quoted as it
  is; it adds results to every common word.)
- The box on the home page only, or a 🔍 in the top
  bar of every page?
- Should a Grabar line and its translation show as
  one result (the pair), or as two?
