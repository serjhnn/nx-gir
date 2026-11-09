# Limits: how far nx-gir can grow

How much more the library can hold before storage or
speed becomes a problem, measured so it can be
compared later. Run

    scripts/check-limits.py --site --record

after a big addition (a new book, a few translated
parts): it prints each number against its limit and
adds a line to `notes/limits.tsv`, the history. The
quick form without `--site` takes seconds; `--site`
builds the Pages site in a temporary folder (about a
quarter of a minute today).

The same numbers are on the **Statistics** page of
the web reader (`#/stats`, linked under the shelf
and from the Timeline). On the Pages site they are
measured at every publish, with the site's real size
and build time; the git history is the last size in
`limits.tsv` (GitHub Actions copies only the last
commit, and an estimate is enough). In `nxgir web`
the git size is measured, and the site's size and
build time are the last ones in `limits.tsv`. So
record after big additions to keep them fresh.

## State on 2026-11-09 (commit d4db7fb)

Amaran hator parts 1–13 of 24 translated; 80 book
files on the shelf; the reader has a Contents list
(the sermons of each part, in the book JSON).

| What | Now | Limit | Used |
|---|---|---|---|
| Book text (`books/`) | 16.0 MB, 80 files | — | — |
| Grabar / translation | 13.1 MB / 2.9 MB | — | — |
| Pages site | 76.9 MB | 1 GB | 8% |
| Git history | 18.2 MB | 1 GB | 2% |
| Largest file | 6.0 MB (`grabar/vocabulary-hy.tsv`) | 50 MB | 12% |
| Largest book part | 278 KB (Amaran hator 05, translation) | 1 MB | 27% |
| Site build | 20 s | 10 min | 3% |

Since 2026-11-07 (52c1df8): one translated part
added 0.9 MB to the site and 1.6 MB to git; the
build took 20 s instead of 15 (one measure, on
another machine: watch it, not a trend yet).

The site is 25 MB of books (about 1.6 times their
text) and 33 MB of word lookups (512 files, at most
140 KB each). The word lookups grow with the number
of different words, so more slowly than the text:
new books mostly repeat words already there.
Since 52c1df8 another 16 MB are the books as plain
HTML pages for search engines (`read/`, about the
size of their text), with `sitemap.xml`.

## The limits

- **Pages site, 1 GB** (GitHub's limit for a
  published site). The first hard limit. At today's
  ratios it is reached at roughly 400–600 MB of book
  text: 25–35 times the library now.
- **Repository, under 1 GB** (GitHub's advice;
  5 GB is the strong limit). Text compresses well in
  git, so this comes after the site.
- **One file, 50 MB** (GitHub warns; 100 MB is
  refused). Only the dictionaries in `grabar/` are
  big; book parts are far below.
- **One book part, 1 MB** (our own limit). Both
  readers load one whole file; on a phone in Termux a
  part should stay small. The number of books does not
  matter for the readers, only the size of each part.
  Keep cutting big books into parts, as
  `fetch-digilib.py` does.
- **Site build, 10 minutes** (our own limit).
  GitHub Actions allows hours, but a slow build slows
  every publish. On 2026-11-07 more than half of
  the build was `nxgir_grabar.load()` reading
  `grabar/abbreviations.tsv` again for every
  different word (about 207,000 times); now it is
  read once and indexed (65 s down to about 15 s,
  the same site). The rest grows with the books.

The translations take far longer than the space runs
out: a translated part adds about 250 KB.

## To do

- [x] Read `abbreviations.tsv` once per run
  (cache `nxgir_grabar.load()`, index the table):
  done 2026-11-07, the site build from 65 s to
  about 15 s.
- [ ] Run `check-limits.py --site --record` after
  each new book or every few translated parts, and
  compare with the line above.
- [ ] When the site passes 50% (500 MB): look at
  the word lookups first (only the words of the
  books, fewer or smaller buckets), then at the book
  JSON (it repeats every word and space).
- [ ] When a book part passes 1 MB: cut it in two.
- [ ] When the repository passes 500 MB: think about
  keeping the large source copies (`sources/`, page
  scans) out of git.
