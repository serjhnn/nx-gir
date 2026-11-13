# Girk harcmanc: notes on the parts

Grigor Tatevatsi's Book of Questions (Գիրք հարցմանց),
12 parts. Files: `books/grabar/grigor-tatevatsi/
1-girk-harcmanc/` and the same path under
`books/ashkharhabar/`, aligned line for line. The
method is in `TRANSLATION_GUIDE.md`.

## How to do the next part

Parts 1 and 2 are done. To do part 3 (of 12):

1. The Grabar of part 3 is still in Digilib
   paragraphs (1,344 lines). Cut it into sentences
   with the script in step 1 of
   `notes/3-amaran-hator.md`, commit the split on its
   own, and count the `։` without a space after it
   (none in parts 1 and 2).
2. Translate in chunks of 150–200 lines into
   `books/ashkharhabar/.../03.txt`; the title line is
   `Հարցումների գիրք · 3/12`. Check each chunk with
   the check of `TRANSLATION_GUIDE.md`.
3. Doubtful lines get a trailing ` *`, as in parts 1
   and 2; every other line of a sentence ends with
   `։`. A line that is a heading with a full stop
   in the Grabar (`Հարցումն առաջին.`) may end with
   `։`.
4. Records: this file, `books/SOURCES.md`,
   `books/TRANSLATIONS.tsv`, `timeline.tsv`.

## Part 1

Translated 2026-11-12 by GPT-6 (a contributor's
work), status `machine`. 2,865 lines on both sides,
blank lines in the same places. Uncertain or damaged
passages are marked `*` in the translation (78
lines): search for them when reviewing. Needs a
reader of Grabar for the philosophical and
theological terms and for readings damaged in the
OCR.

## Part 2

Translated 2026-11-13 by Claude (Sonnet 5.5), status
`machine`. 3,439 lines on both sides (the Grabar was
cut into sentences first, like part 1), blank lines
in the same places, `Contents` identical (the two
chapter lines `Գլուխ Ը` and `Գլուխ Թ`). The title
line is `Հարցումների գիրք · 2/12`, as in part 1.

What it covers (line numbers in both files):

- 3–105 (Պրակ Բ): fourteen questions against the
  two-natures teachers (երկաբնակք).
- 107–285 (Պրակ Գ, Դ): proofs from Scripture that
  Christ is true God (twenty), and that He is one,
  God born of the Virgin in the body (twenty).
- 287–360 (Պրակ Ե–Զ): why only the Word is incarnate
  when the nature is common; Christ is man by the
  divine nature and God by the human one, in the
  sense of the union.
- 362–1550 (Պրակ Է–Ի): the Chalcedonians and the
  Nestorians against the union by nature; the four
  ways of the union; the sayings of Gregory and
  Cyril (Պրակ Ժ, ԺԱ); how to flee from Nestorius
  and from Eutyches (ԺԳ); one nature, two natures
  (ԺԴ); the dialogues (ԺԵ, ԺԶ); the parts of
  Christ's body are God (ԺԸ); the questions of
  Gevorg (ԺԹ); whether Christ's human mind knew
  God (Ի, thirty proofs). The second volume ends
  at line 1550.
- 1552–1675: the third volume begins: the table of
  contents of the theology of Dionysius, of the
  angels and of the demons.
- 1677–3271 (`Գլուխ Ը`, Պրակ Ա–ԻԵ): the theology of
  Dionysius as questions and answers: the
  ineffable and the sayable, the rest of the mind
  (1732), union and distinction (1770), the
  Trinity (1899–2063), one and many (2064), the
  exemplar `յարացոյց` (2214), eternity and time
  (2330–2487), life (2488), the vision of God, of
  angels and of men (2555–2764), the word and truth
  and faith (2765–2824), the four kinds of theology
  (2826), the sun as a likeness of God (2945), wonder
  and jealousy (3115), love and the good (3165),
  breadth, length, depth, height (3202), alpha and
  omega (3229), why the body is called Christ's foot
  (3257).
- 3273–3439 (`Գլուխ Թ`, Պրակ Ա–Զ): on the angels:
  the intelligible and the intelligent, why gifts
  are unequal, the word and the voice, why the
  visions are so humble, the nine orders (ends
  mid-chapter; part 3 goes on).

Notes on the text and choices:

- `Պրակ` is kept as it is (part 1 put `տետրակ` where
  the Grabar said `Պրակ Հատորիս`, in the prose, not
  in these headings).
- The names follow the Grabar: Եվտիքես, Նեստոր,
  Ապողինար, Կյուրեղ, Իրենեոս; `Ռեթեոս` (an author of
  Dionysian passages, line 739) is kept as the
  text has it. `Ալպերա` (1507) is Albert, left as is.
- `երկաբնակ` is kept (a holder of two natures), and
  `բաժանող` is used for the one who divides
  Christ (a Nestorian). Pronouns for God and
  Christ are capitalised in some lines (as in part
  1) and not in others; to be made even by the
  reviewer.
- 63 lines end with ` *` (the doubtful ones, as in
  part 1): a damaged word, a garbled sentence or a
  term not found. Find them with `grep -n ' \*$'`.
  The check in the guide counts these as `no_end`;
  without them it is 0.
- Terms the Wiktionary lists do not have, and so
  left as in the Grabar: `յարացոյց` / `յարացույց`
  (exemplar, from 2147), `տուտ` (1671), `ախեղծ`
  (1238), `վանգ` (1884), `զտրամորոշություն` (757).
- Slips and repeats in the Grabar, translated as
  they stand: at 3033 the third head is named
  `Երկրորդ` (the second is at 3030); 3393–3403 the two
  opinions on the ten orders are written twice; the
  punctuation of quotes is broken in places (738,
  746, 1264, 1469); the third volume's headings at
  1556–1675 repeat the table of contents of the
  chapters that follow.
- Words broken by the OCR (`Երկ րորդ`, `ո ՛ր`) were
  read as the words they should be.

