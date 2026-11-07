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
- First line: `# Title`. Then paragraphs, split by
  empty lines; `## ` starts a subheading. No other
  Markdown for now: the text is shown as it is.
- Newest first on the page, in the language the
  reader picks (Armenian first); a post without
  that language shows in the first one it has.
