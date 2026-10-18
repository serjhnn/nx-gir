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
- [ ] Remember the last position, bookmarks
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
