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
- The section on degrees of kinship at the end is dense.
  Its explanation of the degrees and step-relations
  should receive specialist review before being treated
  as authoritative.

## Continuing work

Before translating part 2, read this file,
`notes/1-datastanagirk-a.md`, and
`TRANSLATION_GUIDE.md`. Inspect the corresponding
Grabar source and existing translation state first.
Continue on a separate branch, preserve line-for-line
alignment, update `books/SOURCES.md` and
`books/TRANSLATIONS.tsv`, and keep the status
`machine` until a person has actually reviewed it.
