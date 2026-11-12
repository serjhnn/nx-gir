# Translation guide

How a part of a Grabar book is translated into modern
Eastern Armenian in nx-gir. It is the workflow used for
Mkhitar Gosh's Գիրք Դատաստանի, redaction Ա, following
`notes/3-amaran-hator.md`. For a work with other
conventions, its own notes come first.

## Files

- Grabar: `books/grabar/<author>/<work>/NN.txt`.
- Translation: the same path under
  `books/ashkharhabar/`.
- The web reader shows them side by side, so the
  translation has the same lines as the Grabar.

## 1. Before a part

Read:

1. `CLAUDE.md`.
2. The work's notes in `notes/`: "How to do the next
   part" and "Notes on the text".
3. The work's entry in `books/SOURCES.md`.
4. The first 40 lines of the last finished part, both
   versions: they show the local format.

Find the next part from the files and `git log`, not
from memory.

## 2. Split the Grabar

Cut the Grabar into sentences before translating, with
the script in step 1 of `notes/3-amaran-hator.md`: one
sentence on each line, cut after `։`; a run `։։` and a
closing `)` stay on the line; a blank line where a
paragraph ended. Only line breaks change. Count the
places where `։` had no space after it, for
`books/SOURCES.md`.

## 3. Translate

Line by line. For every Grabar line, one translation
line.

- The same number of lines. Blank lines in the same
  places. Never join two lines or split one.
- Modern Eastern Armenian, reformed spelling: `և` and
  `Եվ`, never `եւ`.
- The meaning of each sentence, nothing added, nothing
  left out, no explaining. Keep the author's tone, every
  comparison and example, repeated passages and odd
  numbering.
- Unclear word: the best reading. Never leave Grabar in
  the translation. A word that cannot be identified (a
  Greek title, a garbled word) stays in Armenian letters
  and goes in the notes.
- No added marks: no «», no square brackets, and no
  parentheses for your own words (the Grabar's
  parentheses are its quotation signs; keep them).
- Section lines such as `[Ա]` and group lines such as
  `ԳԼՈՒԽ Ա` are copied exactly: the Contents finds
  sections by them. A title in capitals under one is
  translated and stays in capitals. `(Գլուխ. X)` becomes
  `(Գլուխ X)`. A leading `*` stays.
- The first line is the part title, in the form of the
  existing files (for Gosh:
  `Դատաստանագիրք, Ա խմբագրություն · N/2`).
- Terms kept as they are, in Gosh: դահեկան, դանգ,
  թասու, գարի, սիկղ, երկդրամյան, չեքչեք. `որոշվել` is
  for being cut off from the church, `լուծվել` for a
  cleric losing rank.
- Never copy from a modern translation, the 1994
  Etchmiadzin Bible included: it is not free.

## 4. In chunks, checked

1. Draft chunks of 75–150 lines outside the repository
   (the scratch folder), one file per chunk, each ending
   at a line end.
2. Join the chunks so far and check them against the
   Grabar after every chunk, not at the end. Run from the
   repository root, with the two paths:

   ```sh
   python3 - GRABAR TRANSLATION <<'EOF'
   import sys
   sys.path[:0] = ["scripts", "benchmark"]
   import score
   from nxgir_reader import contents
   def load(p):
       return open(p).read().split("\n")[:-1]
   t = load(sys.argv[2])
   g = load(sys.argv[1])[:len(t)]
   for k, v in score.structure(g, t).items():
       print(f"{k:13}", v)
   a, b = contents(g), contents(t)
   print("contents", len(a), len(b), [
       (x["line"], x["n"]) for x in a] == [
       (x["line"], x["n"]) for x in b])
   EOF
   ```

   It compares with the first lines of the Grabar, so it
   works on a part that is not finished. `lines_ok` and
   `blank_ok` must be `True`; `locked_bad`,
   `old_spelling` and `latin` must be `0`; `contents`
   must end in `True`. `extra_marks` and `no_end` should
   be `0` for Gosh; in a work that has «» or lines
   ending in a comma, look at them and judge.
3. While translating, write down for the notes: what
   each range of lines covers, terms you decided, odd
   readings and slips in the Grabar (with line numbers),
   unclear words.
4. When the last chunk passes, write the whole file to
   `books/ashkharhabar/`.

## 5. Records

- `books/SOURCES.md`: the part and its lines, the count
  of `։` without a space, source oddities.
- `books/TRANSLATIONS.tsv`: the path, status `machine`,
  no reviewer, today's date (a test fails without it).
- The work's notes: a "Part N" section (what each range
  covers, terms, uncertainties, the lines to check
  first), and "How to do the next part".
- `timeline.tsv`: a line for a milestone, in English.
- After a new book or a few parts:
  `scripts/check-limits.py --site --record` and the state
  in `notes/limits.md`.
- Then `ruff format scripts/ tests/`,
  `ruff check scripts/ tests/`, `python3 -m pytest`, and
  say what they printed.

## 6. Commit

One commit for a part, naming the work and the part. Push
the session branch. Ask before pushing to `main`.

A translation stays `machine` until a person reads it.
Do not describe it as checked.
