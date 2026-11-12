# Դատաստանագիրք, Բ խմբ.: notes on the parts

Working notes for translating Mkhitar Gosh's law book
(Գիրք Դատաստանի, Բ խմբագրութիւն) into modern Eastern
Armenian. This follows the workflow recorded in
`notes/1-datastanagirk-a.md`; the general translation
principles are in `TRANSLATION_GUIDE.md`.

Files:
- Grabar: `books/grabar/mkhitar-gosh/2-datastanagirk-b/`
- Modern Armenian: `books/ashkharhabar/mkhitar-gosh/2-datastanagirk-b/`

The files are aligned line for line. The translated
part's title is
`Դատաստանագիրք, Բ խմբագրություն · 1/2`.
Section markers such as `[Ա]` and the Armenian-letter
numbering are retained. Section headings are translated
in capitals, generally ending in
`ԴԱՏԱՍՏԱՆՆԵՐԻ ՄԱՍԻՆ`.

## Part 1

Part 1 has been translated in full (2026-11-12).
It contains the preface and the first part of the laws
and canons, ending with item 108, on marriage between
relatives. The text includes rules concerning clergy,
church property, monasteries, marriage and divorce,
captivity, inheritance, and ecclesiastical discipline.

The Grabar source and translation have matching line
counts and blank-line positions. The translation is an
AI draft, not a human-reviewed or specialist edition.
The status is recorded as `machine` in
`books/TRANSLATIONS.tsv`.

## Part 2

Part 2 has been translated in full (2026-11-12).
It continues with item 109, finishes the ecclesiastical
canons, and then gives the secular laws through item 130
and the colophon. Topics include the nine orders of
angels, church and palace, royal authority, inheritance,
property, trade, labor, animals, injury and homicide.

The source was split into 1,369 reader lines. The
translation has the same line count and blank-line
positions, and all 146 section markers are in the same
positions. The source's repeated `[ՃԻԱ]` section marker
and the spacing of law `16 .` are preserved. No old `եւ` spelling, Latin text or added
quotation marks remain. The status is `machine`; no
human or specialist review has been done.

## Points for human review

- The source's numbering is irregular in places. For
  example, item 109 appears before item 104 near the
  end of the part. The source order and numbering have
  been preserved rather than silently corrected.
- The medical and bodily-condition terms in the section
  on marriage (especially `ուրուկ` and `արուագէտ`)
  need a Grabar specialist's review. The translation
  keeps `ուրուկ` literal rather than assigning it a
  modern diagnosis.
- The term `գոդեաց` in the penalties for unlawful
  marriage (lines 1701 and 1715) is rendered as
  `անառակների տուն`; this interpretation should be
  checked against the source and historical usage.
- The section on degrees of kinship at the end of part 1
  is dense. Its explanation of the degrees and
  step-relations should receive specialist review.
- Part 2 uses many historical church, palace and
  administrative titles. Several palace ranks and garment
  names are transliterated from the source and need a
  specialist's review.
- The terms `մահր`, `պռոյգք`, `տուայր`, and the related
  rules for a wife's property need historical and legal
  review. The same applies to the detailed inheritance
  shares, coin values, blood-price calculations and
  kinship rules.
- Some passages on animals, medical practice and the
  duties of hired workers are difficult to read in the
  Grabar and should be checked against a specialist
  edition or manuscript.

## Next work

Redaction Բ is now translated in both parts. Before
starting redaction Գ, read this file,
`notes/1-datastanagirk-a.md`, and
`TRANSLATION_GUIDE.md`, then inspect the corresponding
Grabar source and translation state. Continue on a
separate branch, preserve line-for-line alignment,
update `books/SOURCES.md` and `books/TRANSLATIONS.tsv`,
and keep the status `machine` until a person has
actually reviewed the translation.
