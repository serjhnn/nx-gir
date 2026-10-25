# nx-gir: long-term plans

A place for ideas and plans. This project will keep
growing for years, so this file is a living document:
add, change, and cross out as the ideas develop.

## The vision

Bring old Armenian manuscripts together on one online
platform, and make them open to anyone who is
interested, including people who don't know Armenian or
Grabar.

The Matenadaran alone holds tens of thousands of
manuscripts, and many of them have not been opened for
centuries. Their texts, pictures, and ornaments should
not stay hidden on shelves. They should be readable,
searchable, and seen.

## Three collections

### 1. Manuscripts library

- Collect the manuscripts in one place, starting with
  the Matenadaran and later other collections around the
  Armenian world
- For every manuscript: page scans, the text (via OCR
  and Grabar tools), and a description (title, author or
  scribe, date, place, size, condition)
- Make them readable for everyone:
  - original Grabar text
  - modern Armenian spelling
  - transliteration into Latin letters
  - translations or summaries in other languages
  - glossary help for old words and abbreviations
- Search by title, author, scribe, place, century,
  subject, and full text

### 2. Picture library

- Collect the pictures these books contain: miniatures,
  illuminated headpieces, decorated initials, marginal
  drawings
- Each picture is linked back to its manuscript and page
- Browse and search by subject, color, style, painter,
  school, period, and place

### 3. Knots

- Collect ancient Armenian knots and interlace
  ornaments from all around the Armenian world: from
  manuscripts, khachkars, churches, carpets, and other
  sources
- For every knot: a picture, where and when it was
  found, the source, and a clean drawing of the pattern
- Over time, compare and group them: how a pattern
  travels and changes between regions and centuries

## How nx-gir fits in

The terminal reader is the first building block. The
tools made for it are the same tools the platform needs:

- OCR for scanned pages → turning manuscript scans into
  text
- Grabar helpers (abbreviations, modern spelling,
  transliteration, numerals, glossary) → making the text
  readable for people who don't know Grabar

## Rough stages

1. **Interactive reader.** A terminal app for reading a
   book and understanding unknown words (details below).
   OCR and other Grabar helpers grow around it.
2. **First collection.** A small set of manuscripts
   (scans, text, descriptions) in one simple data format.
3. **Online platform.** A website to browse, read, and
   search the collection.
4. **Picture library.** Add miniatures and ornaments,
   linked to their pages.
5. **Knots.** Start the knot collection.
6. **Growing.** More manuscripts, more collections,
   translations, and help from volunteers and experts.

## Stage 1: interactive reader

A terminal reader that helps with words you don't know.

How it works:

1. Open a book and read it page by page.
2. Move the cursor to a word you want to know more about.
3. Press a key to get information about that word:

| Key | Shows |
|-----|-------|
| `t` | **Translation**: the word's meaning in modern Armenian (later other languages too) |
| `e` | **Explanation**: dictionary form, grammar (case, number, tense), and notes on old words and abbreviations |
| `s` | **References**: other places in the book where the word appears, so you can jump to them |

The information shows in a panel next to or below the
text, and the reader keeps your place in the book.

Progress:

- [x] Reader screen that fits the window, paging
- [x] Word cursor (`w`/`b`, `j`/`k`, `0`/`$`, `g`/`G`)
- [x] `s`: references panel (same word form for now)
- [x] Panel beside the text on wide screens (`p` to
      choose: auto, below, beside)
- [x] Remember the last position, bookmarks (`m`,
      `M`), settings and reading progress
- [x] Notes on sentences (`O` adds, `o` lists, `•`
      marks a sentence with notes; `nxgir notes`
      prints them)
- [ ] `t` and `e` with a starter glossary
- [ ] `s` across different forms of the same word

What it needs:

- A reader screen: paging, moving between words,
  bookmarks, remembering the last position
- A Grabar dictionary to look words up in (starter
  glossary first, larger dictionaries later)
- Finding the dictionary form of a word: Grabar words
  change their endings (`-ոյ`, `-աց`, `-ոց`, `-աւ`,
  `-ս`, `-դ`, `-ն`, …), so the reader needs to strip them
  to find the word
- An index of every word in the book for `s`, matching
  different forms of the same word

## Plan: pictures of places with their locations

Collect many pictures of places (churches, khachkars,
monasteries, inscriptions, carved knots) together with
where they are, for the picture library and the knots.
Google Maps is the starting point for finding places.

The rule from Google: the Maps terms do not allow
scraping, bulk downloading, or keeping Google's photos
and map data in our own collection. Photos from the
Places API may only be shown live, with their author
credits, not saved. So Google Maps is used to *find*
places; the pictures we keep come from sources that
allow it.

Where the pictures come from:

- Our own photos, and photos people send us with
  permission; the GPS location is read from the photo
  (EXIF)
- Our own Google Maps photos and saved places, through
  Google Takeout (they are ours to keep)
- Wikimedia Commons: many geotagged photos of Armenian
  churches and khachkars, under free licenses
- Wikidata: places with coordinates and a picture
  (for example "instance of: khachkar" or "church
  building" in Armenia and Artsakh)
- Mapillary: street-level photos under CC BY-SA
- Flickr: only photos with a free license and a
  location
- Monument lists (the Armenian state list of
  monuments, Wiki Loves Monuments Armenia) for the
  names and ids of places

For every picture we keep:

- the file, and a small preview
- place name (Armenian and Latin), latitude and
  longitude, and how exact the location is
- what it shows (church, khachkar, knot, inscription)
- the source, link, author, license and date
- the place id in the monument list or Wikidata, if
  there is one

TODO:

- [ ] Choose the data format: a `places.tsv` and a
      `pictures.tsv`, the pictures in a folder by
      place
- [ ] Find the places: a list made by hand in Google
      Maps (saved list → Takeout), plus the monument
      lists and Wikidata
- [ ] A script to read our own photos: GPS and date
      from EXIF, matched to the nearest known place
- [ ] A script to fetch Wikimedia Commons pictures by
      category or by area, with their licenses
- [ ] A script to fetch Wikidata places with
      coordinates and pictures (SPARQL)
- [ ] Mapillary and Flickr, after the first two work
- [ ] Find and drop duplicates (same picture from two
      sources)
- [ ] Check every license; keep only free ones, and
      keep the credits with the picture
- [ ] A map view to see what is collected and where
      the gaps are
- [ ] Decide where the pictures are stored (they will
      not fit in git; see the hosting question below)

## Plan: Armenian meanings of words (`A`)

`a` in the reader shows what a word means in English
(the Old Armenian entries of the English Wiktionary).
`A` shows the meaning in Armenian (done: built by
`scripts/fetch-vocabulary-hy.py` into
`grabar/vocabulary-hy.tsv`).

Chosen source: the Armenian Wiktionary
(hy.wiktionary.org), from its dump on
dumps.wikimedia.org (CC BY-SA 4.0, like the English
data). kaikki.org has no extract of it, so we read the
dump ourselves. What we found (dump of 2026-10-01):

- There is no Grabar section: the entries are modern
  Armenian, in the reformed spelling. Many give the
  classical spelling in `{{why|աստուած}}`, and old
  senses are marked `{{հնց}}` (about 7,500) or
  `{{գրբ}}`.
- 3,982 of our 7,679 Grabar headwords match an entry
  by title or by `{{why}}`; with simple spelling rules
  (իւ → յու, եա → յա, է → ե, -եմ → -ել, -ամ → -ալ, …)
  it was about 4,800 (62%) in the first count; in
  the built file it is 4,565 of 7,702 (59%).
- In the books in `books/`, 81% of the words get an
  English meaning; 75% get an Armenian one (71% from
  our headwords, the rest from the classical spellings
  of entries that have no English Grabar entry).
- The meanings are modern Armenian senses, not always
  the Grabar one; the `{{հնց}}` senses come closest.

Other sources, not used now; for later:

- [ ] *Նոր բառգիրք հայկազեան լեզուի* (Venice,
      1836–37): the great Grabar dictionary, public
      domain. Its explanations are in Grabar (and
      Latin), and it exists only as scans, so it needs
      OCR of two-column old print
- [ ] Հ. Աճառյան, *Հայերեն արմատական բառարան*
      (1926–35): public domain since 2024 (the author
      died in 1953). Roots and their history, with
      Armenian explanations; scans only, needs OCR
- [ ] Ստ. Մալխասյանց, *Հայերէն բացատրական բառարան*
      (1944–45): Grabar and modern words explained in
      Armenian, the best fit. Under copyright until the
      end of 2027 (the author died in 1957); free from
      2028
- [ ] Online copies of these dictionaries (e.g.
      nayiri.com): check their terms before using any
      text from them; copy only from scans we can cite
- [ ] Follow «տե՛ս [[...]]» (see …) links in the
      Wiktionary entries one step, to the entry that
      has the meaning
- [ ] Better old → new spelling rules, tested on the
      words that are still not found
- [ ] Show which senses are old (`{{հնց}}`, `{{գրբ}}`)
      first, or only those

## Open questions

- Permissions: which scans and texts can be published,
  and how to work together with the Matenadaran and other
  libraries and museums
- Licenses for the texts, pictures, and code
- Where to host the scans (they take a lot of space)
- How volunteers and scholars can help: checking OCR,
  translating, describing pictures, adding knots
- Funding for hosting and scanning over the years

## Notes

(free space for ideas)
