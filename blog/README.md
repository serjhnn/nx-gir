# The nx-gir blog

Posts for the Blog page (`/blog`, `/api/blog`),
read by `scripts/nxgir_blog.py`. Content, not code.

- One file per post and language:
  `YYYY-MM-DD-slug.LANG.md`, the date it is
  published, a short name in Latin letters and the
  language, `hy`, `en` or `ru`
  (`2026-11-07-welcome.hy.md`). The versions of a
  post share the date and the slug; the slug is its
  address, `/blog/welcome`.
- Themes: a line `theme: site`, `theme: authors`,
  `theme: books` or `theme: tech` (how things are
  made) right after the title puts the post in a
  theme; the line is not shown. One version of a
  post is enough (the others must not differ). The
  Blog page has a sub page for each
  (`/blog/theme/authors`), with tabs between them.
  `/blog` itself shows all the posts (the tab
  "All"), every time; nothing is remembered. A post
  without a theme is only on `/blog`. `THEMES` in
  `scripts/nxgir_blog.py` must match `BLOG_THEMES`
  in `web/app.js` (a test checks it); a new theme is
  added to both.
- Places: a line `place: ani, duin` right after the
  title (and the theme) names the places the post is
  about, ids of `map/places.tsv`; the map page shows
  the post on them. The line is not shown. One
  version is enough (the others must not differ). A
  test checks every id exists. Comics (`comics/`)
  take the same line.
- A line `![alt](name.jpg)` on its own is a
  picture: the file is in `web/img/` (jpg, png or
  webp, about 1000 px wide, under 300 KB).
- A line `![alt](youtube:ID still.jpg)` on its own
  is a YouTube video (ID the 11 letters after
  `v=` or `youtu.be/`): the page shows the still, a
  file in `web/img/` like a picture, with a play
  button, and loads the player from
  youtube-nocookie.com only when it is clicked (the
  one exception to "nothing from other sites"; the
  CSP's `frame-src`). The site's page for search
  engines shows the still as a link to the video.
- A line `[text](#/3d/glakavank)` on its own is a
  link to a page of the site (a path as `h()` takes
  it, starting `#/`).
- First line: `# Title`. Then paragraphs, split by
  empty lines; `## ` starts a subheading. No other
  Markdown for now: the text is shown as it is.
- Newest first on the page, in the language the
  reader picks (Armenian first); a post without
  that language shows in the first one it has.
- Drafts go in `blog/drafts/`, named the same way:
  they are not read, so not on the page or the
  site. Move a draft up into `blog/` to publish it.
