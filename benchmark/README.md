# Benchmark: Grabar into modern Armenian

Six chunks of Grabar (183 lines, 27 KB) with the
translation they are compared to, to test how well
a model translates. The same prompt, the same
chunks for every model.

## The cases

| Case | Lines | Tests | Reference |
|---|--:|---|---|
| `amaran-07-scholastic` | 26 | sermon, a scholastic argument in short steps, a `(Գլուխ. X)` line | Claude, in review |
| `amaran-10-confession` | 23 | sermon, comparisons and a story, a leading `*` | Claude, in review |
| `gosh-laws-deut` | 53 | law: a verse of the Torah and the comment, `[..]` section lines, capital titles | Claude, unreviewed |
| `gosh-canon-qa` | 44 | law: questions and answers on canons | Claude, unreviewed |
| `gosh-inheritance` | 18 | law: long legal sentences about shares | Claude, unreviewed |
| `gosh-judges` | 19 | preface: judges, witnesses, oaths | Claude, unreviewed |

`cases.tsv` lists them. Each folder in `cases/` has

- `prompt.txt`: the whole prompt, to paste as it is;
- `source.txt`: the Grabar chunk alone;
- `reference.txt`: the translation to compare with.

The chunks are copies, frozen: the translations in
`books/` are still being corrected, the benchmark
must not move. `python3 benchmark/build.py --check`
shows what changed in `books/` since;
`build.py` without it takes the new text.

## How to run

For each model and each case:

1. Open a new conversation (or an API call with no
   tools, no web search, the same settings for every
   model). In a chat, paste `cases/<case>/prompt.txt`.
   Through the API, use `prompt.md` as the system
   prompt and `source.txt` as the one user message.
2. Save the reply exactly as it came (do not fix it,
   not even a code fence or a comment) as
   `runs/<model>/<case>.txt`. Name the folder after
   the model, for example `fable-5.2`, `opus-5.5`,
   `sonnet-5.5`, `haiku-5.5`. Other files in the
   folder (a `NOTES.md` with the settings, the date)
   are not read.
3. One try for each case. To measure luck, run the
   whole set again into `runs/<model>-2/`.

Then

    python3 benchmark/score.py            # numbers
    python3 benchmark/score.py --worst 5  # bad lines
    python3 benchmark/review.py make      # blind sheet
    # rate review/ratings.tsv (1-5), then
    python3 benchmark/review.py reveal    # by model

`score.py` writes `results/summary.md` and
`results/scores.json`. Only the standard library is
needed. A missing case shows as `-`.

## What the numbers mean

- **rules ok**: the output keeps the line count and
  the blank lines, copies `[..]` and `ԳԼՈՒԽ` lines
  exactly, has no `եւ`, no Latin letters and no added
  `«»` or `[ ]`. A run that breaks a rule cannot be
  used for the books, whatever its other scores.
- **chrF**: how close the text is to the reference
  (character 6-grams, 0–100). **line** is the same
  line by line, **word** is the F1 of the words.
- **copy**: the share of words left as in the Grabar.
  The references have about 17%: names, numbers, and
  words the same in both languages.
- **(copy source)**, the first row: the Grabar given
  back as the answer, about 40. This is the floor.

## What they do not mean

- The references are all made by Claude, so a model
  that writes like Claude scores higher, and a good
  different translation lower. There is no
  independent human reference. Use chrF to find bad
  runs. To rank good ones, use the blind review, by
  someone who reads the Grabar.
- Six chunks are few: differences of a point or two
  are noise. Run twice before drawing a conclusion.
- Reference errors: the Gosh references are not yet
  reviewed; if you find one, correct it in `books/`
  and in `cases/`, and note it here.
