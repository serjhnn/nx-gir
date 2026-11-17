# ocr/: OCR tooling for scanned books

All the OCR code lives here, apart from the reader
(`scripts/`). It turns page scans (a PDF, e.g. the
1859 Smbat Տարեգիրք in `sources/`) into text for
`books/`. Needs Pillow, numpy, and the `tesseract`
(with `hye`) and `pdftoppm` programs; the reader
itself does not need any of these.

    python3 ocr/run.py page PDF N
    python3 ocr/run.py eval PDF --ref DIR --pages 26-156

`eval` OCRs pages already typed in `DIR` and scores
them, so each step is measured before it is kept.

## Pipeline (`nxocr/`)

| Module | Step |
|--------|------|
| `pages.py` | render PDF pages (cached in `cache/`) |
| `prep.py` | crop, deskew, binarize (Sauvola), scale |
| `engine.py` | Tesseract with word confidences; one `Page` shape so engines can be swapped |
| `textnorm.py` | the comparison key (no marks, case, spacing) |
| `metrics.py` | edit distance and alignment (numpy) |
| `locate.py` | place a page in the typed text, by voting |
| `evaluate.py` | CER, WER, confusions, triage |

| `post.py` | correction with word lists, every change logged |
| `lines.py` | cut a page into line images + typed text |
| `train.py` | `.lstmf` files, `lstmtraining`, held-out blocks |

Planned: a context step for real-word errors (see
Post-correction) and an LLM pass over the low-confidence
words (see the triage below).

## Fine-tuning (`models/hye_grabar.traineddata`)

    python3 ocr/run.py base        # tessdata_best hye
    python3 ocr/run.py samples PDF --ref DIR \
        --pages 26-156 --out ocr/cache/smbat \
        --tessdata ocr/cache/base
    python3 ocr/run.py train --out ocr/cache/smbat \
        --steps 4000
    python3 ocr/run.py eval PDF --ref DIR \
        --pages 26-156 --heldout --lang hye_grabar

`samples` OCRs the typed pages, aligns every line to
the typed text, keeps lines under 50% error with only
known characters, and writes line image, text and
`.lstmf`. Whole 5-page blocks (`train.fold()`, a quarter
of the pages) are held out for `eval`; a page scanned
twice is kept out of training if its twin is held out.
The base is the float `tessdata_best` model (the apt
`hye` is integer and cannot be tuned). Training takes
about 5 minutes on 4 CPUs. `models/` is kept in git
(6 MB).

## Post-correction (`post.py`): suggestions only

The word list suggests; it does not rewrite. The tests
below show why: even the best settings made 4-6 words
wrong, silently, in a book. So by default the text stays
as the engine read it and the suggestions go to a list
for a person (or the LLM pass) to check:

    python3 ocr/run.py page PDF N --lang hye_grabar \
        --suggest --review page-N.tsv

`--review FILE` writes one row per suggestion (page, line,
word, confidence, old, new, edit cost, context gain, step;
without it they go to stderr). `--apply` changes the text
too. In code, `post.correct()` and `post.context()` return
the Corrections and change nothing unless `apply=True`.
`eval --post` scores what the suggestions would be worth if
every one were applied (on a copy); that is a ceiling, not
what the tool does.

Evaluation:

    python3 ocr/run.py eval PDF --ref DIR --pages 26-156 \
        --half test --lang hye_grabar --post \
        --costs ocr/results/smbat-dev-tuned.json \
        --skip-book smbat-sparapet/2-taregirk

An unknown word that is close to exactly one known word
is replaced by it. Known words: Wiktionary (`grabar/`)
and the typed books in `books/grabar/`, with the book
being tested left out (`--skip-book`): 246 000 words,
9 s and 700 MB to build (the distance-2 index covers only
long words seen 3 times or more). Close is a weighted edit
distance: a swap the engine is known to make costs less
(`--costs`, the confusions of a `eval --json`). Left alone:
words the engine is 80% sure of or more, capitalized words
(names), words with no or two equal candidates, and the
halves of a word split at a line end. Every change is a
`Correction` (old, new, cost, confidence); `--show N`
prints them, so each can be reviewed.

Settings were chosen on the dev half of the held-out
pages (`train.half()`: the first 3 held-out blocks, 15
pages) and scored on the test half (the other 15), which
was not looked at before.

### Adapting to the book, and context (`--adapt`, `--context`)

    ... --post --context --adapt DIR --adapt-weight 6 \
        --weight 6 --gain 5 --ctx-conf 90

`--adapt DIR` adds the typed book itself to the word
lists and the word-pair counts, `--adapt-weight` times,
so names and the author's own forms are known. The
held-out pages (dev and test) are cut out of it first
(`Reference.without()`), so no page is scored against its
own text. `--context` (`post.context()`) weighs every
uncertain word and the words close to it by how well each
fits its neighbours (word-pair counts from the corpus and
the adapted book), less the cost of the change.

Test half, `hye_grabar`, same pages as above:

| | CER | WER | words changed | fixed | made wrong |
|--|--:|--:|--:|--:|--:|
| OCR | 3.3% | 7.7% | | | |
| word list | 3.3% | 7.4% | 23 | 12 | 4 |
| + adapted to the book | 3.3% | 7.4% | 21 | 12 | 4 |
| word list + context, adapted | 3.2% | 7.2% | 33 | 20 | 6 |

Dev half, the same steps: 10.55% WER, 9.72% (word list),
9.5% (adapted: 28 fixed, 1 made wrong), 9.5% (with
context: 33 fixed, 4 made wrong).

What did not work, so it is not tried again: context alone
(every setting made more words wrong than it fixed, the
best one about even); context only where the pair counts
have seen the candidate beside its neighbours and never the
original (126-206 changes, more made wrong than fixed).
The pair counts come from other authors and other centuries,
and a frequent word beats the right rare one. The gain of
this whole step is small: about half a point of WER, with a
log of every change to review. The real-word errors
(`քրիստոս` for `քրիստոսի`) are mostly still there; they are
a job for the LLM pass, or for a model of the book trained
on more of its own text.

## Numbers (Smbat 1859, PDF pages 26-156)

Held-out pages only (30 pages, never used in training),
`--psm 6`, top 10% and bottom 7% cut:

| Model | CER | WER |
|-------|----:|----:|
| stock `hye` | 25.9% | 58.7% |
| `hye_grabar` (4000 steps) | 3.5% | 9.1% |

Per page: median 2.8%, 3.1% without page 45 (a scan
smear hides half the text), 2.7% without page 124 too
(stray marks in the margin and signature). The rest are
1-5%. The `eval` report lists the worst pages.

Preparation matters little: with the stock model scale
1.5 gave 23.7% against 24.0% on 20 pages; binarize and
deskew changed nothing (the scan is straight).

Triage: re-read the words the engine is under N% sure of
(share of all words, share of the wrong words caught):

| N | stock | `hye_grabar` |
|--:|-------|--------------|
| 70 | 67% / 84% | 11% / 56% |
| 80 | 77% / 91% | 15% / 65% |
| 90 | 89% / 97% | 30% / 83% |

With the tuned model an LLM pass over the words under
80% is 15% of the text and reaches two thirds of the
errors; under 90% is 30% and reaches 83%. Results:
`results/*.json`.

Caveats: the typed text was itself typed from this scan
(its own errors count against the OCR), and test and
training pages share one typeface, so these numbers are
for this book. Other books must be measured the same way
before the model is trusted on them.

## Another book: Aristakes Lastivertsi, Yerevan 1963

A book the model never saw: a Soviet critical edition
(Karen Yuzbashyan), a different italic typeface, a skewed
scan with dark edges, margin line numbers, and an apparatus
of manuscript variants in small print under the text. Scan:
<https://archive.org/details/LastiverttsiGrabar1963>
(`Lastiverttsi_grabar_1963.pdf`, 157 pages; kept in
`cache/other/`, not in git). Reference: our typed text
`books/grabar/aristakes-lastivertsi/1-patmutiun/` (the same
critical edition, from Digilib). 8 pages spread over PDF
pages 22-140, top 8% and bottom 2% cut:

| Model and settings | CER | WER |
|--------------------|----:|----:|
| stock `hye`, binarize, layout | 38.6% | 67.5% |
| `hye_grabar` as is | 43.2% | 57.6% |
| `hye_grabar` + `--layout 0.85` | 25.8% | 41.0% |
| `hye_grabar` + `--layout 0.85 --binarize` | 23.5% | 39.1% |

- The Smbat model carries over only partly: on this
  typeface it makes about 23% character errors, against
  3.5% on the book it was tuned on (stock: 39%).
- The big step is the layout filter (`layout.py`,
  `--layout`): lines set smaller than 85% of the main text
  are the apparatus, and it is not in the typed text.
  Without it the apparatus counts as 17 points of error.
  Deskew changed nothing here either.
- So a new book needs its own tuning, as the Smbat model
  needed one: the `samples` and `train` commands work on
  any scan with typed pages; expect a few typed pages (tens,
  not hundreds) to bring it down a long way, to be measured
  on held-out pages as for Smbat.

Results: `results/aristakes-*.json`. Not done: tuning on this
book, the word-list step here, and the other pages (the
sample is 8 of about 120).
