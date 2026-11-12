# Translation guide

How to translate Grabar (Classical Armenian) texts into
modern Eastern Armenian for nx-gir. It follows the
workflow used for Grigor Tatevatsi's Ամառան հատոր and
Mkhitar Gosh's Գիրք Դատաստանի, and is written for future
human and AI-assisted sessions.

`CLAUDE.md`, the work notes in `notes/` and
`books/SOURCES.md` are authoritative. When a rule here
conflicts with them, stop and resolve it; do not guess.

## 1. What is translated, and where

The Grabar text is under `books/grabar/<author>/<work>/`,
one file per part (`NN.txt`). Its translation is at the
same relative path under `books/ashkharhabar/`. The web
reader shows the two side by side, so **alignment is as
important as the language**: every translated line must
match the Grabar line beside it.

| Work | Notes | State (check the files) |
|---|---|---|
| Tatevatsi, Ամառան հատոր, 24 parts | `notes/3-amaran-hator.md` | parts 1–15 done, in review |
| Tatevatsi, Ձմեռան հատոր, 18 parts | `notes/2-dzmeran-hator.md` | part 1 done, in review |
| Tatevatsi, Գիրք հարցմանց, 12 parts | `notes/1-girk-harcmanc.md` if present | not started |
| Gosh, Գիրք Դատաստանի, redaction Ա, 2 parts | `notes/1-datastanagirk-a.md` | done, `machine` |

The order planned for Tatevatsi is Ամառան հատոր, then
Ձմեռան հատոր, then Գիրք հարցմանց. Redactions Բ and Գ of
Gosh are on the shelf, not translated. Treat this table
as a plan, not as proof: the real state is in
`books/TRANSLATIONS.tsv`, the notes and the Git history.

Before translating a work that is not in the table (verse,
numbered laws, a different Digilib layout), read its entry
in `books/SOURCES.md` and write its conventions down in a
new notes file before the first part. Do not apply another
work's rules blindly.

## 2. Start of a session

Read, in this order:

1. `CLAUDE.md` — repository rules.
2. This guide.
3. `PLANS.md`, the plan for the work.
4. The work's notes: "How to do the next part" and
   "Notes on the text" in particular.
5. The work's section in `books/SOURCES.md`.
6. `books/TRANSLATIONS.tsv`: status and reviewers.
7. The last finished part, both versions, at least its
   first 40 lines: it shows the local format and terms.

Do not trust remembered progress. Find the next
unfinished part from the files and `git log`.

## 3. Rules of the translation

### Language

- **Modern Eastern Armenian**, reformed spelling as
  written in Armenia today: `և` and `Եվ`, never `եւ`;
  `ու`, `ություն` and so on.
- Clear, natural modern Armenian, close to the source:
  modern words and word order, not the Grabar's.

### Fidelity

- Translate the meaning of each sentence. Do not
  paraphrase a paragraph, summarize, modernize the
  argument or explain.
- Keep the author's voice and reasoning: contrasts,
  repetitions, rhetorical questions, every comparison
  and example, the order of the presentation.
- Translate everything, including headings, short
  fragments and repeated text. Keep repeated passages,
  odd numbering and apparent slips: translate what is
  there, and list the oddity in the notes.
- Do not add words to the text. If grammar needs one,
  add it without a mark: parentheses are the Grabar's
  quotation signs, so never use them for your own words.
  (Gosh, redaction Ա, still has about 175 such pairs, 99
  in part 1 and 77 in part 2, from before this rule: take
  them out when the parts are reviewed.)
- No footnotes, no square-bracket explanations and no
  commentary inside a translation.
- Never leave Grabar in the translation. Give the best
  reading of an unclear word. Only a word that cannot be
  identified at all (a Greek title, a garbled word) stays
  in Armenian letters, and it is listed in the notes for
  a reviewer.
- Do not hide a real ambiguity behind an invented
  certainty, and do not replace a historical concept with
  a modern one that only looks similar.
- Names, references, numbers and examples stay faithful.
  Numbers written in Armenian letters stay in Armenian
  letters (do not turn `ՃՁԳ հազար` into digits). Do not
  correct a probable numerical slip: record it in
  `books/SOURCES.md` or the notes so it can be checked
  against another edition.

### Quotations and Scripture

- Keep the Grabar's own quotation signs (parentheses in
  Ամառան հատոր) and add no second set. Which signs a
  work uses is in section 4; follow the previous part.
- Translate Biblical quotations from the Grabar as it
  stands: Tatevatsi may quote from memory.
- Never copy from a modern translation. This includes
  the 1994 Etchmiadzin Bible: it is not free, and
  `books/ashkharhabar/bible/old-testament/psalm-118.txt`
  is there only to be read beside the Grabar. A quotation
  that happens to resemble it is still translated from
  the Grabar.

### Terms

- One Grabar term, one modern equivalent, throughout a
  work, as long as the sense is the same. When a word
  clearly has two senses, keep two equivalents and record
  the difference.
- Prefer the established Armenian term to an improvised
  synonym. Compare other occurrences before choosing.
- Tatevatsi: the shared glossary is
  `books/ashkharhabar/grigor-tatevatsi/TERMS.md`. Check
  if it exists; create it when decisions start to
  accumulate (Grabar form, chosen equivalent, sense,
  alternatives). Examples from the plan: շնութիւն →
  շնություն, ցանկութիւն → ցանկություն, ցասումն →
  ցասում, բանն (reason) → բանականություն. The commandments
  keep familiar forms: «Մի՛ սպանիր», «Մի՛ շնացիր».
- Gosh: terms kept as they are, or fixed, are listed in
  the notes (coins; `որոշվել` and `լուծվել`).
- When you change a term, search the earlier parts too.

## 4. Layout: one line for one line

Split the Grabar into sentences **before** translating
(translating long paragraphs first merges sentences and
breaks the alignment).

- One Grabar sentence on each line, cut after `։`. A run
  `։։` and a closing `)` stay on the line (`։)`). A blank
  line stays where a Digilib paragraph ended.
- The `.` in the Grabar is not a sentence end here.
- Only line breaks and whitespace change. Compare the
  split file with the original, ignoring those.
- The script is step 1 of "How to do the next part" in
  `notes/3-amaran-hator.md`; it cuts only after `։`, while
  the reader also counts `:` (`SENTENCE_END` in
  `scripts/nxgir_reader.py`). Check that the source has no
  `:` at sentence ends, and count the places where `։` had
  no space after it, for `books/SOURCES.md`.

The translation then has:

- the same number of lines as the Grabar;
- blank lines at exactly the same positions;
- on each nonblank line, the translation of that Grabar
  line only: never join two lines, never split one.

If modern Armenian reads better with another clause order,
change the order inside the line. A line may end with a
comma or a full stop where a quotation follows; not every
line must look like a whole sentence.

### Conventions by work

| | Tatevatsi | Gosh, Գիրք Դատաստանի |
|---|---|---|
| Title line (first line) | `Քարոզգիրք, որ կոչվում է Ամառան հատոր · N/24` | `Դատաստանագիրք, Ա խմբագրություն · N/2` |
| Headings | `(Գլուխ. X)` becomes `(Գլուխ X)`; group lines such as `ԳԼՈՒԽ ԼԱ-ԼԵ` are copied | `[Ա]` lines and `ԳԼՈՒԽ Ա` copied exactly; the capitals title under `[Ա]` is translated, in capitals |
| Quotations | the Grabar's parentheses; reviewed parts may have «» added: follow the part before | the Grabar has none: add none; parentheses stay |
| Square brackets | add none | add none; the Grabar's own `[...]` stay |
| Leading `*` | kept | — |

The title line is the part title in the form of the
existing files: copy it from the previous part and change
the number.

### The Contents

The reader's Contents (☰) is made from the text by
`contents()` in `scripts/nxgir_reader.py`, not by hand: it
finds `ԳԼՈՒԽ ...` group lines, Digilib's `[Ա]` section lines
(`SECTION_RE`, the title is the next line), `(Գլուխ X)`
lines and `Գլուխ X` lines. Keep those lines as they are, in
the Grabar and the translation. If a sermon or section is
missing or shows its verse instead of its heading, fix
`contents()` and its test, never the text.

## 5. Workflow for a part

### A. Source

1. Confirm the Grabar file and the part number.
2. Read the notes and the end of the previous part.
3. If the file is not split into sentences, split it
   (section 4). Do not assume a helper script exists in the
   repository; the one in the notes is the verified one.

### B. Translate

1. Work in chunks of 75–150 lines, drafted outside the
   repository (the session's scratch folder), one file per
   chunk. Read the Grabar chunk, then write the translation
   line against line.
2. **Check every chunk when it is written**: the total
   number of lines so far, blank lines in the same places,
   `[..]` lines unchanged, no `եւ`, no Latin letters. A
   mistake found in the next chunk is cheap; found in the
   whole part it is not.
3. While translating, write down for the notes: what each
   range of lines covers, terms you had to decide, odd
   readings and slips, unclear words (with line numbers).
4. When all chunks pass, join them and write the file to
   `books/ashkharhabar/`.

### C. Check the part

Run from the repository root; `PART` is the path under
`books/grabar/`:

```sh
python3 - PART <<'EOF'
import sys
sys.path[:0] = ["scripts", "benchmark"]
import score
from nxgir_reader import contents
rel = sys.argv[1]
def load(side):
    p = f"books/{side}/{rel}"
    return open(p).read().split("\n")[:-1]
g, t = load("grabar"), load("ashkharhabar")
for k, v in score.structure(g, t).items():
    print(f"{k:13}", v)
a, b = contents(g), contents(t)
same = [(x["line"], x["n"]) for x in a] == [
    (x["line"], x["n"]) for x in b]
print("contents", len(a), len(b), same)
EOF
```

Read it like this:

- `lines_ok` and `blank_ok` must be `True`; `locked_bad`,
  `old_spelling` and `latin` must be `0`.
- `extra_marks` and `no_end` are hints. For Gosh both are
  `0`. A Tatevatsi part may have more: «» added in review,
  lines that end with a comma or a full stop before a
  quotation. Look at them; do not force them to zero.
- The Contents lists must be equal, and every sermon or
  section must show its heading. Print the lists (see
  `contents()`) and look at them once.

Then:

- [ ] Every Grabar sentence has its translation: no
      omissions, no duplicated lines.
- [ ] Spot-read a few places in `nxgir web` beside the
      Grabar.
- [ ] No `։` inside a line unless the Grabar has it there.
- [ ] Oddities and slips are kept as they are and listed
      in the notes.
- [ ] `ruff format scripts/ tests/`, `ruff check scripts/
      tests/`, `python3 -m pytest`: run, and say what they
      printed. Never claim a check passed unless it ran.

### D. Records

For every finished part:

1. `books/SOURCES.md`: the part and its range, the count of
   `։` without a space, source oddities.
2. `books/TRANSLATIONS.tsv`: add the path with status
   `machine`, no reviewer, today's date. Statuses are in
   section 6; tests fail if a translation is not listed.
3. The work's notes: a "Part N" section: what each range of
   lines covers, headings, terms, uncertainties, lines to
   check first. Update "How to do the next part".
4. `PLANS.md`: the checklist, when the work is in it.
5. `timeline.tsv`: a line for a milestone (a first part, a
   finished work), in English.
6. After a new book or a few parts: `scripts/check-limits.py
   --site --record`, and the state in `notes/limits.md`.
7. `TERMS.md`, if a term was decided.

### E. Commit

One commit per part, with a message that names the work
and the part. Push the session branch. **Ask before
pushing or merging to `main`.**

## 6. Review and status

A machine translation is not a scholarly edition and must
not be shown as a verified one.

- `machine`: made by Claude, not yet read by a person.
- `review`: a person is reading it; name them and the date.
- `reviewed`: read through and corrected completely; use it
  only when that is true.
- Ask someone who reads Grabar to check the hard places
  (the notes list them), the terms and a sample. Record
  what was checked and by whom.
- The project's own translations are under CC BY-SA 4.0
  (`CONTRIBUTING.md`, `README.md`). Do not copy modern
  translations or dictionaries. The source licenses are in
  `books/SOURCES.md`.

## 7. Git and handoff

- Work on the session branch. Commit, push the branch, and
  ask before `main`.
- Do not overwrite unrelated changes or discard work on the
  branch.
- End a session in a state another session can read.

A handoff note says: the branch and last commit; the last
finished part; the next part; whether its source is already
split; which checks ran and what they printed; terms decided
and questions left; which records were updated; and the
status of the translation.

## 8. Models

`benchmark/` holds chunks of translated parts, a fixed
prompt and scripts to compare models (see its README). Its
`prompt.md` restates the rules above: keep the two in step.
Before moving a work to another model, run the benchmark on
it and read the bad lines.

## 9. References

- `CLAUDE.md` — repository rules.
- `PLANS.md` — plans, Tatevatsi in particular.
- `books/SOURCES.md` — sources, ranges, peculiarities.
- `books/TRANSLATIONS.tsv` — status, reviewers, dates.
- `notes/` — the work notes (section 1).
- `scripts/nxgir_reader.py` — sentences and the Contents.
- `CONTRIBUTING.md` — contributions and the license.
- `benchmark/README.md` — comparing models.

**Session rule:** look at the real state first, follow the
source and the work's notes, keep one line for one line,
check each chunk as you write it, record every decision, and
leave a clear handoff.
