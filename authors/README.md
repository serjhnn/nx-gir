# About the authors

The card the scroll button opens beside an author's
name (the Library, a book's page, the search page),
read by `scripts/nxgir_authors.py`. Content, not
code.

- One file per author and language: `<id>.LANG.md`,
  the id being the author's folder in
  `books/grabar/` (`mkhitar-gosh.hy.md`), the
  language `hy`, `en` or `ru`. The button shows only
  for an author with a file here.
- First line: `# Name`, as the language writes it
  (in Armenian, as in `books/LIBRARY.tsv`).
- Then `key: value` lines:
  - `years`: the years of life, as the language
    writes them (`մոտ 1130 – 1213`, `5th century`)
  - `role`: what the author was, a few words
  - `source`: where the facts come from
  - `place`: ids of `map/places.tsv`, by commas; the
    card links them to the map
  - `post`: the slug of a blog post about the author
  - `face`: a picture in `web/` (the author's face,
    a square, shown round)
  - `status`: `machine` (written by Claude, not yet
    read by a person; the card says so) or
    `reviewed`

  `years`, `role` and `source` belong to each
  language. `place`, `post`, `face` and `status` are
  shared: one version is enough, and the others
  must not differ (a test checks it).
- Then the text: two short paragraphs, split by an
  empty line, no other Markdown. What matters for a
  reader of the books: where and when the author
  lived, what they wrote, the books of ours.
- Sacred words may be used here: these are about
  the authors, not examples (`CLAUDE.md`).
- A test (`tests/test_authors.py`) checks that
  every id is an author of `LIBRARY.tsv`, that every
  place, post and face exists, and that every author
  has all three languages.

## About the books

The card the book icon opens on the Library (a
book with a card has its icon in the accent color).

- One file per book and language, in the author's
  folder here: `<author>/<book>.LANG.md`, the path
  being the book's in `books/grabar/` (a folder of
  parts, or a single file without `.txt`):
  `mkhitar-gosh/1-datastanagirk-a.hy.md`.
- First line: `# Name`, the book's name as the
  language writes it (in Armenian, as in
  `books/LIBRARY.tsv`).
- Then the same `key: value` lines as an author's,
  but `written` (when it was written) in place of
  `years`, `kind` (what the book is, a few words) in
  place of `role`, and no `face`.
- Then two short paragraphs: what the book is,
  when, where and why it was written, what is in
  it; and what this copy is (an edition, a part
  of the work), and what it meant later.
- A test (`tests/test_authors.py`) checks that
  every book is in `books/grabar/` under an author
  of `LIBRARY.tsv`, with all three languages.
