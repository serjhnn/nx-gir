# Translation guide

How a Grabar (Classical Armenian) text is translated into
modern Eastern Armenian in nx-gir. It is written for
**two readers**: contributors, and AI tools (an agent
with the repository, or a chat window with no access to
it). Everything an AI tool needs is on this page.

## In one minute

1. One Grabar line, one translation line. Same number of
   lines; blank lines in the same places.
2. Modern Eastern Armenian, reformed spelling: `և`, never
   `եւ`.
3. Translate the meaning of each sentence: add nothing,
   leave nothing out, explain nothing.
4. Copy lines like `[Ա]` and `ԳԼՈՒԽ Ա` exactly.
5. Add no «» and no `[ ]`. A word you must add to make a
   sentence whole may stand in `( )`.
6. Never leave Grabar words in the translation.
7. Run the check (section 6) after every chunk.
8. The result is `machine` until a person reads it.
   Never push to `main` without asking.

## Words used here

- **Grabar**: Classical Armenian, the language of the old
  texts. **Modern Armenian**: Eastern Armenian as written
  in Armenia today.
- **Part**: one file, `NN.txt`, of a book.
- **Chunk**: a piece of a part, 75–150 lines, translated
  at one time.
- **Locked line**: a line that is copied, not translated:
  a section line in square brackets (`[Ա]`, `[ՃԸ]`) or a
  group line (`ԳԼՈՒԽ Ա`). The reader builds its Contents
  from them.
- **Status** of a translation (`books/TRANSLATIONS.tsv`):
  `machine` (made by an AI tool, no person has read it),
  `review` (a person is reading it), `reviewed` (read
  through and corrected).

## Files

- Grabar: `books/grabar/<author>/<work>/NN.txt`.
- Translation: the same path under `books/ashkharhabar/`.
- The web reader shows the two side by side, line against
  line. That is why the lines must match.
- The notes of each work are in `notes/`; they list what
  each part covers and the choices made.

## 1. How to take part

- **Translate a part** (this guide). Needs Python 3 and the
  repository for the check; the translating can be done
  in any AI tool.
- **Review a part**: read it beside the Grabar and
  correct it. See `CONTRIBUTING.md`.
- A translation is published under CC BY-SA 4.0
  (`CONTRIBUTING.md`). Translate from the Grabar; do not
  copy from a modern translation, the 1994 Etchmiadzin
  Bible included (it is not free).

## 2. Two ways to work

**A. An agent with the repository** (a coding assistant):
follow sections 4–7 in order.

**B. A chat window** (no access to the files):

1. Open a **new** conversation for each chunk.
2. Paste the prompt of section 3, a line with three
   dashes, and the chunk of Grabar.
3. Save the reply exactly as it came, as a chunk file.
   If it stops early, ask for the rest, giving the last
   three lines it wrote; do not let it start over.
4. Join the chunks into one file and run the check
   (section 6) on it.

## 3. The prompt

Give this to the AI tool before the chunk. It is the same
text as `benchmark/prompt.md`, used to compare models.

```
You translate Classical Armenian (Grabar) into
modern Eastern Armenian.

The text you get is one chunk of a book, cut into
lines. Translate it line by line.

Rules:

1. Answer with the translation only: no comments,
   no notes, no quotation marks around it, no code
   block.
2. One output line for each input line. Do not
   merge or split lines. A blank line stays a blank
   line, at the same place. The output has exactly
   as many lines as the input.
3. Use the reformed spelling of modern Armenian:
   `և` (never `եւ`), `Եվ` at the start of a
   sentence, `ու`, `յ` only where modern Armenian
   has it. Use modern Eastern Armenian words and
   word order, not the Grabar's.
4. Be faithful, not word for word: the meaning of
   each sentence, nothing added, nothing left out,
   no explaining. Keep the author's tone, and every
   comparison and example.
5. A line in square brackets, such as `[ՃԸ]`, and
   a line that starts with `ԳԼՈՒԽ`, are copied
   exactly. A title in capital letters is
   translated and stays in capital letters.
   `(Գլուխ. ԾԱ)` becomes `(Գլուխ ԾԱ)`. A leading `*`
   stays.
6. Quoted words stand in parentheses in the Grabar:
   keep the parentheses. A word you must add to make
   a sentence whole may also stand in parentheses.
   Add no «», no square brackets and no other marks.
7. Keep the names of coins as they are: դահեկան,
   դանգ, թասու, գարի.
8. Every sentence ends with `։`, as in the Grabar.
9. If a word is unclear, give your best reading in
   modern Armenian. Never leave Grabar words in the
   translation.

The chunk follows after the line with three dashes.
```

## 4. What a good line looks like

Grabar, then the translation (Gosh, part 2, lines 77–84):

```
[ՃԺԵ]

ՅԱՂԱԳՍ ԴԱՏԱՍՏԱՆԱՑ ՅԱՐՈՒՑՈՂԱՑ ԶԱՆԿԵԱԼ ՉՈՐՔՈՏԱՆԻՍ

Գուցէ տեսանիցես զէշ եղբաւր քոյ կամ զեզն նորա անկեալ ի ճանապարհի եւ զանց առնիցես զնոքաւք, այլ յարուցանելով յարուսցես ընդ նմա։

Անվարձ եւ զայս եւս հրամայէ։
Եւ թէպէտ աւրինադրութիւն, սակայն եւ դատաւորաց է գիտել զայսոսիկ եւ խրատել, որ յաղագս սորին երթան յատեան։
```

```
[ՃԺԵ]

ԸՆԿԱԾ ՉՈՐՔՈՏԱՆԻՆԵՐԻՆ ՈՏՔԻ ՀԱՆՈՂՆԵՐԻ ԴԱՏԱՍՏԱՆՆԵՐԻ ՄԱՍԻՆ

Չլինի թե քո եղբոր էշը կամ նրա եզը ճանապարհին ընկած տեսնես և անցնես նրանց կողքով, այլ անպայման նրա հետ ոտքի հանիր։

Սա էլ է հրամայում առանց վարձի։
Եվ թեև օրենսդրություն է, սակայն դատավորներն էլ պետք է իմանան դա և խրատեն նրանց, ովքեր սրա համար ատյան են գնում։
```

What happened:

- `[ՃԺԵ]` is copied. The title in capitals is translated
  and stays in capitals.
- One sentence on each line; the blank lines are where
  they were. The two files have the same shape.
- No `եւ`, no added « » or `[ ]`, no Grabar words left.
- `թէպէտ աւրինադրութիւն` became `թեև օրենսդրություն է`:
  modern words and word order, the same meaning.

## 5. The rules, in detail

**Language**

- Modern Eastern Armenian, reformed spelling: `և` and
  `Եվ`, `ու`, `ություն`.
- Modern words and word order, not the Grabar's.

**Fidelity**

- The meaning of each sentence. Keep the author's tone,
  every comparison and example, repeated passages and odd
  numbering. Do not summarize or paraphrase a paragraph.
- Translate everything, titles and short fragments too.
- An unclear word: give the best reading. A word that
  cannot be identified at all (a Greek title, a garbled
  word) stays in Armenian letters and goes in the notes.
- Do not correct slips in the Grabar (a repeated
  sentence, a wrong number): translate what is there and
  write it in the notes.

**Marks and lines**

- The Grabar has parentheses for quoted words: keep them.
  Add no «» and no square brackets.
- If the modern sentence needs a word the Grabar does not
  have, put it in parentheses, as the Gosh translation
  does: `(եկող)`. Use it only when the sentence would
  not be whole without the word; the parentheses show
  that it is yours. Do not use them for explanations.
- Locked lines are copied exactly. `(Գլուխ. X)` becomes
  `(Գլուխ X)`. A leading `*` stays.
- The first line of a part is its title, in the form of
  the part before it (for Gosh:
  `Դատաստանագիրք, Ա խմբագրություն · N/2`).
- Every sentence ends with `։`, as in the Grabar.

**Terms**, in Gosh: դահեկան, դանգ, թասու, գարի, սիկղ,
երկդրամյան, չեքչեք stay as they are. `որոշվել` is for
being cut off from the church, `լուծվել` for a cleric
losing rank. Other works: see their notes.

**Help with Grabar words**

- `./nxgir grabar word <word>`: what a word means
  (Wiktionary; inflected forms work). A word that is not
  there says so.
- `./nxgir grabar abbr <word>`: expands a manuscript
  abbreviation.
- Frequent small words, as a hint only; read the
  sentence before choosing:

| Grabar | Usually |
|---|---|
| `զ` before a noun (`զմարդ`) | marks the object: dropped in modern Armenian |
| `ի`, `յ` | in, at, from, of |
| `թէ`, `եթէ` | թե, եթե |
| `որպէս` | ինչպես |
| `զի` | որովհետև, որ, որպեսզի |
| `վասն`, `յաղագս` | համար, մասին |
| `յորժամ` | երբ |
| `այլ`, `ապա` | բայց; ապա, հետո |
| `մի՛` + verb | a ban: մի՛ ... |
| ending `-իցէ`, `-իցեն` | often a wish or condition: թող ..., եթե ... |
| `-ութիւն`, `աւրէնք` | `-ություն`, `օրենք` (reformed spelling) |

## 6. The check

Run from the repository root, with the two paths: the
Grabar file and the translation (a part, or the chunks
joined so far; it compares with the first lines of the
Grabar, so a part not yet finished works):

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
bad = [i + 1 for i, (x, y) in enumerate(zip(g, t))
       if bool(x) != bool(y)]
print("first blank mismatch at line", bad[:1])
lock = [i + 1 for i, (x, y) in enumerate(zip(g, t))
        if score.locked(x) and x != y]
print("first locked mismatch at line", lock[:1])
a, b = contents(g), contents(t)
print("contents", len(a), len(b), [
    (x["line"], x["n"]) for x in a] == [
    (x["line"], x["n"]) for x in b])
EOF
```

How to read it:

| Line of the output | Good | If not |
|---|---|---|
| `lines_ok` | `True` | the line count differs: find where, with the two mismatch lines below |
| `blank_ok` | `True` | a blank line is missing or extra: see `first blank mismatch` |
| `locked_bad` | `0` | a `[..]` or `ԳԼՈՒԽ` line was changed: see `first locked mismatch` |
| `old_spelling` | `0` | there is a `եւ`: change it to `և` |
| `latin` | `0` | Latin letters in the text: remove |
| `extra_marks` | `0` | a « » or `[ ]` was added: remove |
| `no_end` | `0` | a line lost its `։` |
| `contents` | `... True` | the section lines differ from the Grabar |

When the line count is wrong, the lines after the first
mismatch are all shifted: fix that place first, then run
again. If you cannot run Python, check by hand: count the
lines, and look at the blank lines and the locked lines.

Common mistakes:

- two Grabar lines joined into one, or one split in two;
- a blank line dropped or added;
- `եւ` instead of `և`;
- a locked line translated or changed;
- « » or `[ ]` added;
- explanations or extra words put in the text, with or
  without parentheses;
- a sentence left out, or Grabar left in;
- a summary where a translation was asked for;
- a code block, a note or "Here is the translation" in
  the reply.

## 7. The workflow of a part (agent with the repository)

1. **Read** `CLAUDE.md` (or the rules of the repository),
   the work's notes in `notes/` ("How to do the next
   part", "Notes on the text"), the work's entry in
   `books/SOURCES.md`, and the first 40 lines of the last
   finished part, both versions. Find the next part from
   the files and `git log`, not from memory.
2. **Split the Grabar** into sentences with the script in
   step 1 of `notes/3-amaran-hator.md`: one sentence on
   each line, cut after `։`; a run `։։` and a closing `)`
   stay on the line; a blank line where a paragraph
   ended. Only line breaks change. Count the places where
   `։` had no space after it, for `books/SOURCES.md`.
3. **Translate in chunks** of 75–150 lines, drafted
   outside the repository, one file per chunk, each
   ending at a line end. Check after every chunk, not at
   the end: a mistake in one chunk is cheap, in a whole
   part it is not.
4. **Write down** while you translate, for the notes: what
   each range of lines covers, terms you decided, odd
   readings and slips in the Grabar (with line numbers),
   unclear words.
5. **Write the file** to `books/ashkharhabar/` when the
   last chunk passes, then run the check on the whole.
6. **Records**:
   - `books/SOURCES.md`: the part and its lines, the count
     of `։` without a space, source oddities.
   - `books/TRANSLATIONS.tsv`: the path, status
     `machine`, no reviewer, today's date (a test fails
     without it).
   - The work's notes: a "Part N" section, and "How to do
     the next part".
   - `timeline.tsv`: a line for a milestone, in English.
   - After a new book or a few parts:
     `scripts/check-limits.py --site --record`, and the
     state in `notes/limits.md`.
7. **Test**: `ruff format scripts/ tests/`,
   `ruff check scripts/ tests/`, `python3 -m pytest`. Say
   what they printed.
8. **Commit** one part at a time, naming the work and the
   part, and push the session branch.

## 8. What an AI tool must not do

- Push or merge to `main` without being asked.
- Change the Grabar text, except the sentence split.
- Overwrite a part that is `review` or `reviewed`, or
  change its status, without the reviewer.
- Present a `machine` translation as checked.
- Copy from a modern translation or a dictionary.
- Hide a doubt: put it in the notes.
- Claim that a check passed if it was not run.

## 9. Done when

- [ ] The check shows no problem (section 6).
- [ ] Every Grabar sentence has its translation.
- [ ] The notes, `books/SOURCES.md`, `books/TRANSLATIONS.tsv`
      and `timeline.tsv` are updated.
- [ ] `ruff` and `pytest` ran, and their result is said.
- [ ] The branch is pushed. Whoever owns the project
      decides about `main`.
