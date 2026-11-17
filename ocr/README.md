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

Planned: `post.py` (correction with the `grabar/`
word lists and the confusion table), a fine-tuned
`hye_grabar` model, and an LLM pass over the
low-confidence lines (see the triage below).

## Numbers (Smbat 1859, PDF pages 26-156, 20 pages)

Stock `hye`, `--psm 6`, top 10% and bottom 7% cut:

| Variant | CER | WER |
|---------|----:|----:|
| as is | 24.0% | 58.5% |
| `--scale 1.5` | 23.7% | 57.7% |

Binarizing and deskew change almost nothing (the scan
is already straight); the stock model is the limit.

Triage (stock): re-reading every word the engine is
under 70% sure of is 67% of the text and catches 84% of
the wrong words (74% precision). At under 50%: 49% of
the text, 67% of the errors. So with the stock model an
LLM pass over low-confidence words is too big to be
cheap; the point of fine-tuning is to bring that share
down. Results: `results/*.json`.
