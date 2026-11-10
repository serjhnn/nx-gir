# The nx-gir features

What the site can do, for the Features page
(`#/features`, `/api/features`), read by
`scripts/nxgir_features.py`. Content, not code.

- One file per language: `features.LANG.md`,
  `hy`, `en` or `ru` (Armenian first on the page).
- First line: `# Title`. Then a short paragraph
  about the page, then one `## Feature` heading per
  feature with its paragraphs. No other Markdown:
  the text is shown as it is (the same format as a
  blog post, `blog/README.md`).
- Add a feature with every new one on the site,
  in each language the page has; keep the same
  order in each.
- Drafts go in `features/drafts/`: not read, so
  not on the page or the site. Move a draft up to
  publish it.
