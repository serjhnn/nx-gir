# Translation guide

A working guide for translating Grabar (Classical Armenian)
texts into modern Armenian for nx-gir. It is written for
future human and AI-assisted sessions. The repository's
source files and work-specific notes remain authoritative:
when a rule here conflicts with a source-specific note,
stop and resolve the conflict rather than guessing.

## 1. Purpose and scope

The main current translation project is Grigor Tatevatsi's
three works:

- `1-girk-harcmanc/` — Գիրք հարցմանց
- `2-dzmeran-hator/` — Ձմեռան հատոր
- `3-amaran-hator/` — Ամառան հատոր

The Grabar originals are under
`books/grabar/grigor-tatevatsi/`. Their modern Armenian
translations belong at the same relative paths under
`books/ashkharhabar/grigor-tatevatsi/`.

The web reader presents the two versions in parallel.
This makes structural fidelity just as important as
linguistic quality: every translated line must correspond
to the Grabar line beside it.

This guide is primarily based on the Tatevatsi workflow.
Other authors and genres may have different structures
(verse, numbered sections, legal articles, etc.). Before
translating another work, read its entry in
`books/SOURCES.md` and its work-specific notes. Do not
apply Tatevatsi's sermon-heading or sentence-splitting
rules blindly to another text.

Other works translated so far follow their own notes:
Mkhitar Gosh's law book (Գիրք Դատաստանի, redaction Ա)
is described in section 5A below and in
`notes/1-datastanagirk-a.md`.

## 2. Read before starting a session

At the beginning of every new session, inspect the current
branch and read the relevant files from the repository:

1. `CLAUDE.md` — repository-wide working rules.
2. This file — translation workflow and quality rules.
3. `PLANS.md`, especially
   **Plan: Grigor Tatevatsi in modern Armenian**.
4. The relevant work notes:
   - `notes/3-amaran-hator.md`
   - `notes/2-dzmeran-hator.md`
   - `notes/1-girk-harcmanc.md`, if present.
5. The relevant sections of `books/SOURCES.md`.
6. `books/TRANSLATIONS.tsv` — current status and
   reviewers for each translated file.
7. The Grabar source part, its translation if one exists,
   and adjacent completed parts. Use them to understand
   the local formatting and terminology.

Do not rely on remembered progress from an earlier session.
Check the actual files and Git history. Find the next
unfinished part from the work notes and the repository,
rather than assuming that the old plan is still current.

## 3. Translation principles

### Language and spelling

- Write in **modern Eastern Armenian**, using the
  **reformed (Soviet) spelling** used in Armenia today.
- Use `և` and `Եվ`, not `եւ`.
- Use clear, natural modern Armenian, but remain close
  to the source.
- Translate the meaning of the Grabar sentence; do not
  paraphrase a whole paragraph, summarize, modernize the
  author's argument, or add explanations to the text.
- Preserve the author's voice, reasoning, contrasts,
  repetitions, rhetorical questions, examples and order
  of presentation.
- Keep technical, theological, philosophical and
  ecclesiastical terms consistent throughout a work.
- Do not replace an unfamiliar historical concept with
  a modern concept that only seems similar.
- Do not silently repair a source error or resolve a
  genuine ambiguity by inventing certainty. Preserve
  what the source says; record an important uncertainty
  for later review.

### Fidelity

- Translate everything that belongs to the source,
  including headings, short fragments and repeated text.
- Preserve repeated passages, unusual wording, odd
  numbering and apparent typographical slips. Translate
  what is actually present.
- Do not omit difficult sentences or leave untranslated
  Grabar in the modern Armenian file. If a passage cannot
  be understood confidently, mark it for review in the
  working notes rather than making up a translation.
- Keep names, references, numbers and examples faithful
  to the source.
- Do not add footnotes, square-bracket explanations or
  editorial commentary to the translation unless the
  work's established format explicitly requires them.

### Quotations and Scripture

- Preserve the quotation style and delimiters used by
  the particular Grabar work. Tatevatsi's works do not
  all use the same quotation marks: follow the source
  and the established part format.
- For Tatevatsi, translate Biblical quotations from the
  Grabar text as it stands. Tatevatsi may quote from
  memory or use wording that differs from a standard
  Bible edition.
- Do not copy the 1994 Eastern Armenian Etchmiadzin
  Bible translation into these translations; it is not
  free for reuse. A quotation that happens to resemble
  it must still be translated independently from the
  Grabar source.
- Preserve the source's parentheses or guillemets.
  Do not add a second set of quotation marks.
- Preserve a leading `*` where it occurs in the
  established source/translation format.

## 4. Structure: one source line, one translation line

For Tatevatsi, the source must be split into sentences
**before** translating. Translating long paragraphs first
and splitting afterwards can combine two Grabar sentences
into one modern sentence and make alignment difficult.

- Put one Grabar sentence on each line.
- Keep a blank line wherever the original Digilib
  paragraph ended.
- Do not change the Grabar wording while splitting it.
  Only line breaks and whitespace needed for the layout
  may change.
- In the Tatevatsi reader, sentence endings include
  Armenian full stop `։` and colon `:`. A closing
  parenthesis belongs with the sentence (for example,
  `։)`). A run such as `։։` must remain intact.
- The Grabar middle stop `.` is not normally a sentence
  boundary in this workflow.
- The splitting script in `notes/3-amaran-hator.md` cuts
  only after `։`, while the reader also counts `:`
  (`SENTENCE_END` in `scripts/nxgir_reader.py`). Check
  whether a source has `:` at the end of its sentences
  before relying on either.
- Check the reader's actual sentence model and the
  work-specific notes before applying these rules. Some
  Digilib sources use different punctuation conventions.

Then translate line for line:

- The translation has the same number of lines as the
  Grabar file.
- Every nonblank translation line translates the
  corresponding Grabar line only.
- Blank lines occur at exactly the same positions.
- Never join two source lines into one translation line,
  or split one source line into several translation lines.
- If a modern Armenian sentence would read more naturally
  with a different clause order, change the wording inside
  that line; do not change the alignment.
- A line may naturally end with a comma or another
  continuation mark if the source sentence was split
  for alignment before a quotation. Do not force every
  translated line to look like a complete standalone
  sentence.

For Tatevatsi parts, the first line of the translation
is the part title in the established form, for example:

`Քարոզգիրք, որ կոչվում է Ամառան հատոր · N/24`

Use the correct work title, part number and total. Follow
the existing files for the exact title format.

## 5. Tatevatsi formatting details

The practical notes for Ամառան հատոր record these rules;
check the winter volume and question book notes for any
differences:

- `(Գլուխ. X)` becomes `(Գլուխ X)` in the modern
  Armenian translation.
- Chapter-group lines such as `ԳԼՈՒԽ ԼԱ-ԼԵ` remain
  as they are in the established format.
- Keep quotation delimiters as in the Grabar source.
  In Ամառան հատոր, quotations retain parentheses.
- Do not introduce square brackets. (This is a rule for
  the Tatevatsi parts. Works with bracketed section
  lines keep them: see section 5A.)
- Keep a leading `*` where present.
- Preserve repeated passages and unusual numbering.
- Keep headings and structural lines needed by the
  reader's Contents list. Do not rewrite them for style.

The reader's Contents are generated from the text by
`contents()` in `scripts/nxgir_reader.py`. They are
not maintained as a separate hand-written contents
list. After a part is added, inspect the Contents in both
the Grabar and translation. Every sermon/section should
appear with its heading, not merely its Biblical verse.
If the Contents parser misses a heading, investigate the
parser and its tests; do not distort the source text to
work around a parser bug.

## 5A. Datastanagirk (Mkhitar Gosh)

Գիրք Դատաստանի, redaction Ա, is translated (both parts,
status `machine`) at
`books/grabar/mkhitar-gosh/1-datastanagirk-a/`, and at
the same path under `books/ashkharhabar/`. Redactions
Բ and Գ are on the shelf but not translated. The
workflow is section 8, with these differences:

- The title line is `Դատաստանագիրք, Ա խմբագրություն · N/2`.
- Digilib's section lines (`[Ա]`, `[ՃԸ]`, ...) and
  `ԳԼՈՒԽ Ա` are copied exactly as in the Grabar: the
  Contents finds the sections by them (`SECTION_RE` in
  `scripts/nxgir_reader.py`). The title in capitals under
  a section line is translated and stays in capitals:
  «ՅԱՂԱԳՍ ԴԱՏԱՍՏԱՆԱՑ ...» becomes
  «... ԴԱՏԱՍՏԱՆՆԵՐԻ ՄԱՍԻՆ». So square brackets stay in
  these files, and so do the Grabar's own `[...]`
  insertions. Add none.
- The Grabar has no «» here: add none. Its parentheses
  stay.
- Names of coins stay as they are: դահեկան, դանգ, թասու,
  գարի, սիկղ, երկդրամյան, չեքչեք. `որոշվել` is for being
  cut off from the church, `լուծվել` for a cleric losing
  rank.
- Source peculiarities are kept: a sentence the Grabar
  repeats (part 2, lines 386–387), a law numbered
  `[ՂՃԵ]` for ՃՂԵ. They are listed in the notes.
- Words that could not be identified, such as the
  Byzantine court titles in law ՄԻԵ (part 2, lines
  1596–1650), stay in Armenian letters and are listed in
  the notes for a reviewer to check first.

Open point: in part 2, words added to make a sentence
whole stand in parentheses, the same sign as the
Grabar's own quotation parentheses. This is not a rule
of this guide. Decide whether to keep it before
continuing it in other parts or works.

## 6. Terminology

Consistency matters especially in theological and
philosophical writing.

- Use the same modern Armenian equivalent for the same
  Grabar term when it has the same meaning.
- Do not force one equivalent when a Grabar word clearly
  has different senses. Record the distinction in the
  glossary.
- When choosing a term, consider its meaning in context,
  its historical/theological sense and how it is used
  elsewhere in the work.
- Prefer established Armenian terminology over an
  improvised modern synonym.
- If uncertain, compare other occurrences and consult
  reliable dictionaries or a person who reads Grabar.
  Record unresolved choices for review.
- When a term is changed, search for earlier occurrences
  and consider whether they should be updated too.

The project plan names this shared glossary:

`books/ashkharhabar/grigor-tatevatsi/TERMS.md`

Check whether it already exists. If it does not, create
it when terminology decisions begin to accumulate; do
not assume it exists merely because it is mentioned in
the plan. Record the Grabar form, chosen modern Armenian
equivalent, sense/context and any important alternatives.

Examples already mentioned in the plan:

| Grabar | Modern Armenian |
|---|---|
| վարդապետ | վարդապետ |
| շնութիւն | շնություն |
| ցասումն | ցասում |
| ցանկութիւն | ցանկություն |
| բանն (in the sense of reason) | բանականություն |

The Ten Commandments use familiar modern forms such as
«Մի՛ սպանիր» and «Մի՛ շնացիր». keep such choices
consistent.

## 7. Numbers, names and source peculiarities

- Numbers written with Armenian letters in the Grabar
  remain written with Armenian letters in the translation
  when that is the established format. For example, do
  not silently convert a source form such as `ՃՁԳ հազար`
  into Arabic digits.
- Do not correct a possible numerical slip in the source.
  Record it in `books/SOURCES.md` or the relevant work
  notes so it can be checked against another edition.
- Preserve names and historical forms as the source gives
  them, using consistent modern Armenian spelling where
  appropriate.
- Preserve source peculiarities that affect meaning or
  interpretation and flag uncertain readings.

## 8. Practical workflow for a part

Use this sequence for each new Tatevatsi part.

### A. Establish the source

1. Confirm the exact Grabar source path and part number.
2. Read the corresponding work notes and the previous
   translated part.
3. Check the source file's current state and whether it
   has already been split into sentences.
4. If it is not split, split it using the established
   workflow or a verified project script. Do not assume
   a planned helper script exists; check the repository.
5. Preserve the original words and paragraph boundaries.
   Compare the split file with the pre-split source,
   ignoring only whitespace/line breaks.

### B. Translate

1. Work in manageable chunks. The Ամառան հատոր notes
   recommend chunks of about 75 lines.
2. Translate each line against its matching Grabar line.
3. Keep line breaks and blank lines exactly aligned.
4. Follow the work's title, heading and quotation style.
5. Apply the glossary consistently.
6. Keep a list of ambiguous passages, terminology
   decisions and source anomalies for the notes/reviewer.

### C. Check the part

Check all of the following before committing:

- [ ] Same line count in Grabar and translation.
- [ ] Blank lines at identical positions.
- [ ] Every source sentence has a corresponding
      translation; no omissions or duplicated lines.
- [ ] The translation follows the source line by line.
- [ ] Reformed Eastern Armenian spelling is used.
- [ ] No accidental `եւ`; use `և`.
- [ ] No accidental Latin letters in Armenian text.
- [ ] Punctuation and quotation delimiters follow the
      source and work-specific rules.
- [ ] Numbers, names, repetitions and apparent slips
      have not been silently changed.
- [ ] Headings and chapter-group lines are preserved.
- [ ] The web reader's Contents list is correct in both
      versions.
- [ ] A sample of the parallel text has been read in
      `nxgir web` or the published/local web reader.

For Ամառան հատոր, the practical notes also advise
checking that no Armenian full stop `։` remains inside
a line, except where the Grabar itself has it. Apply
this check with awareness of the source's punctuation
and the sentence-splitting rules.

Use existing tests and scripts where available. The plan
mentions future tests for unchanged Grabar text and
matching line/blank-line positions; verify whether those
tests have since been implemented before writing new
ones. Do not claim a test passed unless it was actually
run.

### D. Update project records

For every completed part:

1. Add or update its source details in
   `books/SOURCES.md`, including the source part/range
   and any important punctuation or numerical issues.
2. Add the translation path to
   `books/TRANSLATIONS.tsv`.
3. Use the correct status:
   - `machine`: machine-generated and not yet reviewed
     by a person.
   - `review`: currently being reviewed or partly
     reviewed; name the reviewer and date.
   - `reviewed`: read through and corrected by the
     named reviewer(s); use only when that review is
     actually complete.
4. Add a section for the part to the relevant
   `notes/` file, recording its contents, headings,
   special terms, uncertainties and source peculiarities.
5. Update the progress checklist in `PLANS.md` when
   appropriate.
6. If a glossary decision was made, update
   `TERMS.md`.

The TSV format and status meanings are documented in
`books/TRANSLATIONS.tsv`. Follow its current format
exactly; tests check that translations are listed.

## 9. Review and attribution

A machine translation is not a scholarly edition and
must not be presented as fully verified Grabar
translation.

- Mark machine-generated work as `machine` until a
  person begins reviewing it.
- Record the reviewer's name and date when review starts.
- Mark a part `reviewed` only after the reviewer has
  read through and corrected the whole part.
- Ask a person who reads Grabar to check difficult
  passages, terminology and a sample of the translation.
  Record which parts were checked and by whom.
- Keep the public-facing status accurate. Do not imply
  that an AI-generated translation has been checked by
  a Grabar specialist unless that has happened.

The project's own modern Armenian translations are
licensed under **CC BY-SA 4.0**. Check
`CONTRIBUTING.md`, `README.md` and
`books/TRANSLATIONS.tsv` for the current attribution
and license wording. Do not copy text from copyrighted
modern translations or dictionaries. The Grabar source
license and provenance are documented separately in
`books/SOURCES.md`.

## 10. Git and session handoff

- Work on the session branch, not directly on `main`.
- Commit per part where practical. This keeps a large
  work resumable and makes review easier.
- Use a clear commit message naming the work and part.
- Push the branch after the commit.
- **Ask before pushing or merging anything to `main`.**
- Do not overwrite unrelated changes or discard work
  already present on the branch.
- Before ending a session, leave the repository in a
  state another session can understand.

A useful handoff note should say:

- the branch and latest commit;
- the exact part/file last completed;
- the next part to work on;
- whether the source is already sentence-split;
- which checks were actually run and their results;
- terminology decisions and unresolved questions;
- which project records were updated;
- whether the translation is machine, in review or
  reviewed.

## 11. Work order and current progress

The original Tatevatsi plan sets this order:

1. Finish Ամառան հատոր.
2. Continue with Ձմեռան հատոր.
3. Then translate Գիրք հարցմանց.

The part counts in the plan are 24, 18 and 12,
respectively. Treat these counts and progress marks as
a plan, not as proof of the current state. Recheck the
actual files, notes and `books/TRANSLATIONS.tsv`
at the start of each session.

## 12. Useful repository references

- `CLAUDE.md` — repository conventions and architecture.
- `PLANS.md` — long-term plans and Tatevatsi translation
  plan.
- `books/SOURCES.md` — source provenance, part ranges
  and notes about the source texts.
- `books/TRANSLATIONS.tsv` — translation status,
  reviewers and dates.
- `notes/3-amaran-hator.md` — detailed practical notes
  for Ամառան հատոր.
- `notes/2-dzmeran-hator.md` — winter-volume notes.
- `notes/1-datastanagirk-a.md` — notes on Gosh's law
  book, redaction Ա.
- `benchmark/` — chunks of translated parts with a fixed
  prompt and scripts, to compare models (see its
  README). Its `prompt.md` restates the rules above;
  keep the two in step.
- `notes/1-girk-harcmanc.md` — question-book notes,
  if present.
- `scripts/nxgir_reader.py` — reader sentence and
  Contents logic.
- `CONTRIBUTING.md` — contribution and license terms.

**Session rule:** inspect the current repository state
first, follow the source and work-specific notes, preserve
one-to-one alignment, record every decision, and leave
a clear handoff for the next session.
