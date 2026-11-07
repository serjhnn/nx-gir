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
minute today).

## State on 2026-11-07 (commit 8dfe23d)

Amaran hator parts 1–12 of 24 translated; 79 book
files on the shelf.

| What | Now | Limit | Used |
|---|---|---|---|
| Book text (`books/`) | 15.7 MB, 79 files | — | — |
| Grabar / translation | 14 MB / 2.7 MB | — | — |
| Pages site | 59.8 MB | 1 GB | 6% |
| Git history | 16.5 MB | 1 GB | 2% |
| Largest file | 6.0 MB (`grabar/vocabulary-hy.tsv`) | 50 MB | 12% |
| Largest book part | 278 KB (Amaran hator 05, translation) | 1 MB | 27% |
| Site build | 65 s | 10 min | 11% |

The site is 25 MB of books (about 1.6 times their
text) and 33 MB of word lookups (512 files, at most
140 KB each). The word lookups grow with the number
of different words, so more slowly than the text:
new books mostly repeat words already there.

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
  every publish. Today more than half of the build
  is `nxgir_grabar.load()` reading
  `grabar/abbreviations.tsv` again for every
  different word (about 207,000 times).

The translations take far longer than the space runs
out: a translated part adds about 250 KB.

## To do

- [ ] Read `abbreviations.tsv` once per run
  (cache `nxgir_grabar.load()`): the site build
  from about a minute to seconds.
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
