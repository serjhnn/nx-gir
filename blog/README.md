# The nx-gir blog

Posts for the Blog page (`#/blog`, `/api/blog`),
read by `scripts/nxgir_blog.py`. Content, not code.

- One file per post and language:
  `YYYY-MM-DD-slug.LANG.md`, the date it is
  published, a short name in Latin letters and the
  language, `hy`, `en` or `ru`
  (`2026-11-07-welcome.hy.md`). The versions of a
  post share the date and the slug; the slug is its
  address, `#/blog/welcome`.
- Themes: a line `theme: site`, `theme: authors` or
  `theme: books` right after the title puts the
  post in a theme; the line is not shown. One
  version of a post is enough (the others must
  not differ). The Blog page has a sub page for
  each (`#/blog/theme/authors`) with tabs between
  them. `THEMES` in `scripts/nxgir_blog.py` must
  match `BLOG_THEMES` in `web/app.js` (a test
  checks it); a new theme is added to both.
- A line `![alt](name.jpg)` on its own is a
  picture: the file is in `web/img/` (jpg, png or
  webp, about 1000 px wide, under 300 KB).
- First line: `# Title`. Then paragraphs, split by
  empty lines; `## ` starts a subheading. No other
  Markdown for now: the text is shown as it is.
- Newest first on the page, in the language the
  reader picks (Armenian first); a post without
  that language shows in the first one it has.
- Drafts go in `blog/drafts/`, named the same way:
  they are not read, so not on the page or the
  site. Move a draft up into `blog/` to publish it.
