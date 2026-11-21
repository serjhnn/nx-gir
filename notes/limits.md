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

## State on 2026-11-15 (commit 2119dba)

As on 2026-11-14, plus Eznik Koghbatsi (Eghts
aghandots, two parts), Agathangelos (Patmutiun
Hayots, four parts, 0.8 MB) and the first part of
Narekatsi's Matean in translation; 133 book files.

| What | Now | Limit | Used |
|---|---|---|---|
| Book text (`books/`) | 22.6 MB, 133 files | — | — |
| Grabar / translation | 17.1 MB / 5.5 MB | — | — |
| Pages site | 103.7 MB | 1 GB | 10% |
| Git history | 26.9 MB | 1 GB | 3% |
| Largest file | 6.0 MB (`grabar/vocabulary-hy.tsv`) | 50 MB | 12% |
| Largest book part | 310 KB (Girk harcmanc 01, translation) | 1 MB | 30% |
| Site build | 29 s | 10 min | 5% |
| Browser tab, largest part | 297 MB (phone, measured 2026-11-11) | about 1 GB | 30% |

Later on 2026-11-15 (commit b92dc68, after the Digilib
batch and the translations of Narekatsi, Agathangelos,
Yeghishe and Smbat Sparapet): 209 book files, 37.9 MB
of text; the Pages site 156.3 MB (15%); git 33.0 MB
(3%); the build 43 s (7%). The largest file and the
largest part are the same as above (30% at most).

Later still (after Smbat Sparapet's Taregirk, 224 KB
in two parts, typed from a scan): 211 book files,
38.2 MB of text; the site 157.0 MB (15%); git 16.1 MB
(2%, a fresh clone packs smaller); the build 37 s
(6%). The largest file and part are unchanged.

On 2026-11-16 (after the translation of the
Taregirk, two parts, 0.2 MB): 213 book files, 38.4 MB
of text; the site 157.6 MB (15%); git 22.2 MB (2%);
the build 42 s (7%). The largest file and part are
unchanged (30% at most).

On 2026-11-20 (after the translation of the Digilib
Taregirk of Smbat Sparapet, two parts, 0.5 MB): 251 book
files, 44.9 MB of text; the site 180.6 MB (18%); git
54.0 MB (5%); the build 46 s (8%). The closest limit is
the largest book part, 359 KB (35%, Komitas Aghtsetsi,
Knik havatoy 02); the new parts are far from it.

On 2026-11-21 (after search across the library,
notes/search.md, the books of Davit Anyaght, Giwt and
Mambre, and the eight early works of the second
Digilib batch): 267 book files, 47.1 MB of text; the
site 260.1 MB (25%), of which the search index
(`data/search/`) is about 26 MB and the lines it
shows (`data/lines/`) about 51 MB; git 42.9 MB (4%);
the build 68 s (11%), about 15 s of it for search. The closest
limit is still the largest part (35%).

Since 29dc9cf (2026-11-14): the site fell from 116 MB
to 104 MB because the zip of the site is no longer
built (it was 18 MB; `build-site.py --zip` makes it),
and the build from 44 s to 29 s. The text grew by 1.5 MB
(Eznik, Agathangelos, the Narekatsi translation),
the site by about 4 MB, git by 1.1 MB. `limits.tsv` has
one line for each date: a second record on the same day
replaces the first (what it did not measure stays), so
the Statistics page shows one row a day.

Before that, since 3859010: the measured site grew by about 15 MB
because the zip of the site (`nxgir-site.zip`, 18 MB)
was published with it, and making it is most of the
build's rise from 23 s to 44 s. `offline.json` lists the
75 MB that "Save for offline" kept in a browser (on
the device, not on Pages; saving is switched off now).
The git history grew by 1.4 MB: the Narekatsi part,
the app icons and the new code.

Before that, since 6591ae2: the 19 Anania Shirakatsi works (0.5 MB
Grabar, with seven short ones cut into sentence
lines) and their seven translations added about 3.4 MB
to the site and 1.2 MB to git; the build took 23 s
(steady). The largest part is still Girk harcmanc.
Sizes are in MB of 2^20 bytes, as
`check-limits.py` shows them.

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
- **Browser memory, about 1 GB a tab** (our own
  limit, for a phone of 3 GB). The web reader
  builds a whole part at once, every word an
  element, so a tab takes about 0.5 MB per KB of
  text it shows (both versions side by side
  counted), on top of 65 MB for the page. On
  2026-11-11 the largest part took 297 MB on a
  phone screen (Datastanagirk A 01 beside its
  translation, 570 KB together), Grabar alone
  about 210 MB, and the JavaScript heap at most
  46 MB; reading all 93 parts in one tab leaks
  nothing. A 1 MB part beside a 1 MB translation
  would be near 1 GB: that is why parts stay
  under 1 MB. How it was measured, why it takes
  that much and how to make it smaller are in
  `notes/browser-memory.md`. Measured only when
  asked, not with every new book: then with
  `scripts/measure-memory.js`, and update both
  notes.
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
