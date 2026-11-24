# Գրիգոր Նարեկացի: notes on the parts

Working notes for translating Գրիգոր Նարեկացի's
Մատեան ողբերգութեան into modern Eastern Armenian.
The general rules are in `TRANSLATION_GUIDE.md`.

Files:
- Grabar: `books/grabar/grigor-narekatsi/1-matean-voghbergutyan/`
- Translation: `books/ashkharhabar/grigor-narekatsi/1-matean-voghbergutyan/`

The Grabar files were split at sentence boundaries,
one sentence per line, with paragraph breaks retained.
The wording was not changed. Part 1 (`01.txt`) has
964 aligned lines and covers the first 36 numbered
sections, ending at `[ԼԶ]`.

## Part 1

Translated in full on 2026-11-15 by GPT-6. The translation has
the same 964 lines and blank-line positions as the
Grabar. All section markers are preserved. The text
uses modern Eastern Armenian reformed spelling
(`և`, never `եւ`). It is recorded as `machine` in
`books/TRANSLATIONS.tsv`; it has not been reviewed by
a human or a Grabar specialist.

The part contains a sequence of prayers and meditations
on repentance, divine mercy, confession, the Trinity,
Christ's incarnation, crucifixion and resurrection, and
the work of the Holy Spirit. It includes long poetic
catalogues, biblical allusions, and repeated parallel
phrases; these have been translated without shortening
the source.

## Points for human review

- Check the long parallel catalogues and unusual
  metaphors against the Grabar, especially where a
  literal rendering may sound unusual in modern Armenian.
- Review theological terms and the wording of passages
  on the Trinity, the incarnation, and the Holy Spirit.
- Check biblical allusions and personal names, including
  the references to Abraham, Anna, Sarah, Moses, David,
  Elijah, Ezekiel, and the Canaanite woman.
- Some expressions are difficult to interpret without
  a specialist edition or manuscript comparison. The
  translation is a first reading, not a critical edition.

## Part 2

Translated in full on 2026-11-24 by Claude. The
translation has the same 3,933 lines and blank-line
positions as the Grabar; all 38 chapter markers
(`[ԼԷ]` to `[ՀԴ]`, chapters 37 to 74) are copied and
the Contents match the Grabar's. Spelling is the
reformed one (`և`). It is `machine` in
`books/TRANSLATIONS.tsv`; no human or Grabar
specialist has read it.

The Grabar lines here are verse lines, many of them
half a sentence, so the translation is one fragment
for each line and the sentence runs across several
lines. Where the Grabar ends a stanza with `:` the
translation ends with `։`. The title of the part is
`Մատյան ողբերգության · 2/3`, as in part 1.

Every chapter has the same two title lines (the
"added again, a second lament" title and `Ի ԽՈՐՈՑ
ՍՐՏԻՑ ԽԱՒՍՔ ԸՆԴ ԱՍՏՈՒԾՈՅ`), translated the same way
each time. In `[ԽԱ]` and `[ԽԲ]` the two titles stand
on one line in the Grabar; they do so in the
translation.

What the chapters are about, roughly: more confessions
and prayers for mercy; long chains of parallel lines
(what is hard for the writer is easy for Christ;
the writer's faults listed one by one; the good that
Christ does to every kind of sinner); and many
sayings from the Psalms, the Prophets and the Epistles
worked into the prayers (`[Կ]`, `[ԿԱ]`, `[ԿԲ]`).

Terms: Աստված, Քրիստոս, Հիսուս, Հոգի Սուրբ, Բելիար
(kept as the name in the Grabar). `Քեզ`, `Քո` for God
are capitalised as in part 1.

### Slips and odd things in the Grabar (line numbers of
the Grabar `02.txt`)

- `[ԾԷ]` stands twice, at lines 1744 and 1866; `[ԾԵ]`
  does not stand at all (`[ԾԴ]` at 1567 is followed by
  `[ԾԶ]` at 1659). All copied as they are.
- `[ԿԸ ]` (line 3124) has a space before `]`; copied
  exactly.
- Chapter `[ԿԶ]`: the parts go `Ա Բ Դ Ե Զ Է` (no `Գ`,
  line 2914 is `Դ`); chapter `[ՀԲ]` has `Գ` twice (lines
  3649 and 3674). Copied as they are.
- Line 3808 (`[ՀԴ]`, second title) ends with a stray
  space and a backtick; the translation does not copy
  it.
- Line 2963: two words run together (`պատեցեալԼրմանն`);
  `Լրմանն` is unclear, read as "by everyone's
  reproach".
- Line 2202: `Թարահատայ թարմատարի` is unclear; the name
  is kept in Armenian letters as `Թարահատի թարմատարի`.
- Line 2721 `Ատտիկեցիս` ("Attic"): kept as `Ատտիկեցի`.

## Points for human review

- The chains of parallel lines (`[ԽԵ]`, `[ԾԶ]`,
  `[ՀԱ]`): the Grabar has long runs of one-word
  nouns and participles; the translation turns them
  into short noun phrases and may lose a shade.
- The long theological passages on the Eucharist and
  the two natures of Christ (`[ԾԱ]` to `[ԾԴ]`, `[ԿԳ]`).
- The Psalm quotations in `[Կ]` and `[ԿԱ]`: they are
  translated as the Grabar reads, not taken from a
  modern Bible; a reviewer should compare them with
  the Psalter.
- Biblical names in the long lists (`[ԿԳ]`, `[ԿԴ]`,
  `[ՀԱ]`).
- The unclear places listed above.

## How to do the next part

Part 3 (`03.txt`, 1,795 lines) is next. Follow
`TRANSLATION_GUIDE.md`: check the part boundaries,
translate in chunks of 75 to 150 lines, one chapter
at a time works well (the chapters are 50 to 250
lines), and run the check after every chunk. Take
care that a fragment line is not joined with the line
after it: most slips in part 2 were two Grabar lines
written as one. Keep the status `machine` until a
person has reviewed it.
