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

Planned: nothing open; the LLM pass is in `llm.py` (see the
section below).

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
(Karen Yuzbashyan), a different italic typeface, scanned
in spreads (the facing page shows at one edge, behind a
black binding line), margin line numbers, and an apparatus
of manuscript variants in small print under the text.
Scan: `sources/lastivertsi-1963/` (from
<https://archive.org/details/LastiverttsiGrabar1963>).
Reference: `books/grabar/aristakes-lastivertsi/1-patmutiun/`
(the same edition, from Digilib).

Tuned like Smbat: `samples` (PDF pages 20-150, 2034 train
and 615 held-out lines), `train` 3000 steps, scored on the
30 held-out pages (`--heldout`, blocks of 5):

    python3 ocr/run.py eval PDF --ref DIR --pages 20-150 \
        --heldout --lang aristakes_smbat --binarize --trim \
        --top 0.02 --bottom 0 --layout 0.85 --tail 0.96

| Model | CER | WER |
|-------|----:|----:|
| stock `hye` | 29.9% | 64.3% |
| `hye_grabar` (tuned on Smbat only) | 14.6% | 33.9% |
| `aristakes_stock` (tuned from stock) | 13.5% | 30.6% |
| `aristakes_smbat` (from `hye_grabar`) | 12.2% | 28.6% |

- The Smbat model alone already halves the stock error on a
  typeface it never saw; tuning on this book's own lines
  (2000 lines, a few minutes) adds only 2 points on top.
  Starting from the Smbat model is better than from stock.
- A typed-text reference is not enough: how a page is
  prepared and compared decides the number more than the
  model did. The numbers of an earlier run (21-23%, then 43%)
  were mostly the scan and the reference, found one by one:
  1. The apparatus (not in the typed text) was read as text:
     `--layout` drops lines set smaller than a share of the
     main text, and `--tail` cuts everything under two small
     lines in a row in the lower part of the page, since the
     notes are too close in size to tell by height alone.
  2. The facing page's edge was read as text: `--trim`
     (`prep.trim_edges`) cuts at the black binding line.
     Page 59 went from 29% to 12%.
  3. The reference held editors' notes, like `<Սաղմ. ՁԹ 5-6>`
     (Bible references), that the page does not print:
     `Reference` leaves out short `<...>` notes (a note
     without its `>` must not swallow the text after it:
     one in this book swallowed 700 characters and the
     pages around it scored over 100%).
  4. The comparison window was sized to the OCR text; it is
     now 15% longer.
- What is left: 12.2% = 6.4 points of missing text, 3.6 of
  extra, 2.2 of wrong letters. The missing text is mostly
  whole lines that Tesseract's layout analysis skips (page
  139: a gap of two line spacings), and on some pages the
  binding line is not found and the facing page's strip is
  still read. Not tried: finding the text lines ourselves
  (projection profile) and reading each with `--psm 7`;
  cutting at the text column instead of the binding line.
- Triage with `aristakes_smbat`: re-reading the words under
  80% confidence is 50% of the words and reaches 83% of the
  wrong ones, much more than on Smbat (15% / 65%); a book
  this poorly read needs the LLM pass on half its words.

The two Aristakes models are not kept in git (6 MB each, and
the text of this book is already typed): `samples` and
`train --start hye_grabar --name aristakes_smbat` make
them again in about 20 minutes. The first commit that had
them is in the history. Results:
`results/aristakes-heldout-*.json`. Not done on
this book: the word-list step, a count of how many typed
pages are enough (try 500, 1000 and 2000 lines), a larger
sample than 30 pages.

## Other scans of Smbat Sparapet

Searched on the Internet Archive for scans to test the Smbat
model on. None has a typed text that matches it, so none can
be scored with a true error rate:

| Scan | What it is | Why not scored |
|------|------------|----------------|
| `SmbataySparapetiTaregirk1956` | Venice 1956, S. Akelean, 286 pages: the chronicle | another recension from the 1859 one: different wording and narrative (page 47 is at the year 500; the 1859 text there has other events), so 1859 as reference gives 100% |
| `assisesdantioch00/01smbagoog` | Venice 1876, the law code, with a French translation | mostly French; the pages do not match our typed law code |
| `Karst1905ArmenischesRechtsbuch` | Strassburg 1905, the law code with a German translation | Digilib's text is another version; no page matches |

Digilib's copy of the 1956 text would be the reference for
the first, but the site is not reachable from here (the notes
say the same). Not added to `sources/`; the 1956 scan is
kept in `cache/other/` for now.

### A stand-in for accuracy: the known-word rate

    python3 ocr/run.py proxy PDF --pages 25-270 --sample 20 \
        --lang hye_grabar --skip-book smbat-sparapet/2-taregirk

`proxy` OCRs pages and reports the share of the words (3
letters or more, not capitalized) found in the word lists
and typed books, with the book itself left out, and the
engine's confidence. A misread word is rarely a real word.
Checked where the true error is known (held-out pages):

| Pages, model | True CER | Known words | Words under 80% |
|--------------|---------:|------------:|----------------:|
| 1859, stock `hye` | 25.9% | 48.2% | 76.6% |
| 1859, `hye_grabar` | 3.5% | 87.9% | 16.0% |
| Aristakes, stock `hye` | 29.9% | 46.9% | 66.2% |
| Aristakes, `hye_grabar` | 14.6% | 75.7% | 49.7% |

The 1956 scan (20 pages spread over 25-270; top 9%, bottom 2%,
`--trim --layout 0.85 --tail 0.96`):

| Model | Known words | Mean confidence | Under 80% |
|-------|------------:|----------------:|----------:|
| stock `hye` | 40.9% | 42.0 | 84.0% |
| `hye_grabar` | 81.0% | 68.1 | 48.6% |

So on a new Venice print of the same text the Smbat model
reads about twice as many real words as the stock one. By
the table the error is about 10% (known words, between the
1859 and the Aristakes rows) to about 14% (confidence, equal
to the Aristakes row): an estimate, not a measurement. To
measure it, type 3-5 pages of the 1956 text (or get Digilib's
copy), and `eval` against them. The stock model is as bad
as on the other books (about 30%).

## The LLM pass (`llm.py`)

    ... eval ... --llm-files DIR --llm-hints     # no API key
    ... eval ... --llm claude-sonnet-5-5         # API key
    ... page PDF N --llm MODEL --review N.tsv    # suggestions

Lines with a word the engine is under 80% sure of are sent to
a model: the line image, the OCR text with the uncertain words
marked ⟦ ⟧, and the word list's suggestion for each (`--llm-hints`).
The prompt is `nxocr/llm_prompt.txt`. The model may change
only the marked words (`accept()`): a reply with a different
number of words is thrown away, a change to an unmarked word is
ignored. Like the word list it only suggests (step `llm` in
the review list); `--apply` rewrites. Answers are cached, so a
line is paid for once, and tokens are counted.

Two backends: `Anthropic` (the Messages API, standard library,
key in `ANTHROPIC_API_KEY`) and `Files` (each request is a
folder with the prompt and the line images, the answer is read
from `reply.txt` in it). In this cloud session a script cannot
use the session's own login for the API, so the runs below used
`Files`, answered by Claude agents (Sonnet) that were told to
open every image and to read nothing but their folder; their
transcripts show no file outside the request folders was read,
and one agent that had skipped images was redone.

Smbat 1859, `hye_grabar`, word list hints on, threshold 80.
Settings and prompt were fixed on 4 dev pages; the test is 8
pages of the test half, not looked at before:

| Pages | Lines sent | CER | WER | Words changed | Fixed | Made wrong |
|-------|-----------:|----:|----:|--------------:|------:|-----------:|
| 4 dev | 68 of 101 | 2.91 -> 2.31% | 8.86 -> 6.81% | 25 | 17 | 2 |
| 8 test, Sonnet | 124 of 198 | 4.14 -> 3.72% | 7.54 -> 6.02% | 48 | 18 | 1 |
| 8 test, Haiku | 124 of 198 | 4.14 -> 3.90% | 7.54 -> 6.75% | 27 | 9 | 1 |

(Scored as if every change were made.) Only 13.8% of the words
are under 80, but they sit in 63% of the lines, and a line is
the unit sent: 19 requests of up to 8 lines for the 8 pages.

- The gain is the best of the post steps: 1.5 points of WER
  with one word made wrong, against 0.3 for the word list and
  four made wrong. It fixes what the word list cannot: real
  words in a wrong form and letters the list has no word for.
- A cheaper model (Haiku, the same 19 requests, same prompt
  and instructions; its transcripts also show no file outside
  the request folders) does about half the work: 9 words fixed
  against 18, one made wrong in both. It is more cautious
  (27 changes against 48) rather than worse: it keeps the OCR
  reading when the image is unclear, and misses what Sonnet
  gets. So Haiku is a safe but weak first pass; for a book
  where each point of WER matters, Sonnet. The agents' token
  counts are not API prices (Haiku's four agents used about
  380 000 tokens, Sonnet's about 340 000, most of it the
  agent overhead), so the real cost of each has to be
  measured with the API (`--llm MODEL` prints the tokens).
- Not all the changes are letters: of the 48, about 30 are
  numerals (`74 -> 740`, `543 -> 549`), punctuation and
  capitals, which the score ignores. Years in a chronicle
  matter, and the score cannot say if these are right: review
  the numerals by hand.
- What is left (WER 6%) is mostly words the engine was sure of
  (over 80%) and got wrong: about a third of the wrong words.
  The pass does not look at them.
- Cost, for the 8 test pages: 19 requests, 124 line images. The
  agents used about 340 000 tokens in all, most of it the agent
  overhead and the images; a direct API call would be much less.
  Measure it with the real API (`--llm MODEL` prints the tokens)
  before a whole book.
- Not done: a threshold other than 80, Sonnet only on the lines
  where Haiku is unsure, the 1963 Aristakes book (where half the
  words are under 80), and a check of the numerals against the
  page.
