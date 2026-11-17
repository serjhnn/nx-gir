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

| `lines.py` | cut a page into line images + typed text |
| `train.py` | `.lstmf` files, `lstmtraining`, held-out blocks |

Planned: `post.py` (correction with the `grabar/` word
lists and the confusion table) and an LLM pass over the
low-confidence words (see the triage below).

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
