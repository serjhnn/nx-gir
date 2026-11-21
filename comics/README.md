# The nx-gir comics

Series for the Comics page (`#/comics`,
`#/comics/<slug>`, `/api/comics`), read by
`scripts/nxgir_comics.py`. Content, not code.

- The format is the blog's (`blog/README.md`): one
  file per series and language,
  `YYYY-MM-DD-slug.LANG.md` (`hy`, `en` or `ru`,
  Armenian first); the versions of a series share
  the date and the slug, which is its address.
- First line `# Title`, then the intro paragraph,
  which is also the card on the list. Then a
  `## ` heading and the pages of the comic: each a
  line `![alt](name.jpg)` on its own (the file is in
  `web/img/`, about 1000 px wide, under 300 KB),
  with a `> ` note under it (its place in the
  source, e.g. a quoted line of the book). After
  them, paragraphs with explanations: what the
  book says, what the comic changes, where to read
  it.
- The first picture is the cover on the list.
- The words in the pictures: a retelling, not a
  quotation; the source is named in every series.
  No sacred words in what we write (CLAUDE.md);
  the quoted lines of the books are as they are.
- Newest first. Drafts go in `comics/drafts/`:
  not read, so not on the page or the site.
