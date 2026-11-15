# Եղիշե. notes on Մեկնութիւն Արարածոց

Working notes for the modern Eastern Armenian translation.

Source: Digilib book 1394,
https://www.digilib.am/book/1394/. The critical edition
collects fragments attributed to Yeghishe; it is not a
complete surviving copy of the original work. The source
is in three parts under
`books/grabar/yeghishe/2-meknutiun-ararodzots/`.

## Part 1 progress

The original Part 1 file had 847 lines. It has been split
at Armenian full stops into 1,483 reader lines, keeping
paragraph breaks. No full stop lacked a following space.
Only line breaks and paragraph spacing were changed; the
Grabar wording was not edited.

Part 1: all 1,483 source lines translated in twenty chunks (nineteen 75-line chunks and a final 58-line chunk). Source and translation line counts match, and all blank-line positions match. The machine draft is complete but has not yet undergone human review.

## Translation decisions

- Modern Eastern Armenian, reformed spelling.
- One translation line per Grabar line; preserve blank
  lines and the edition's section and folio markers.
- Manuscript sigla A and H, lowercase note marker a,
  and Roman-numeral heading labels are represented in
  the translation by Armenian equivalents Ա, Հ, ա and
  Armenian numerals. The Grabar source remains unchanged.
- Preserve the Greek and Hebrew terms in Armenian
  transcription where the passage discusses their forms.
- Translate faithfully without adding explanations.
- Record uncertain readings here rather than silently
  correcting the source.

## Chunk 1 · lines 1–75

Opening discussion of disorder in the elements and divine
providence; God's incorporeal nature and creation of the
four elements; the relation of the world to its Creator;
the firmament and the Greek and Hebrew terms for wind and
spirit; the creation of light; and the beginning of the
commentary on the second day.

## Review (2026-11-15, after the draft)

Fixed in the repository after the draft:

- The `machine` record is in `books/TRANSLATIONS.tsv`
  (its model is not stated in the draft: to fill in).
- The 224 lines with added « » lost them, as the guide
  says (the check showed 480 extra marks); five lines
  that lost their closing `։` have it again.
- The headings `Բ (Ա II)` are `Բ (Ա Բ)` in the
  translation (no Latin letters); `contents()` reads
  both, so the two lists have the same 91 entries.

To check in the human review:

- The Grabar has editorial `[ ]` for letters or words
  restored by the editors (18 of them); the draft drops
  all but one. Compare them line by line.
- The parentheses differ in 34 lines.
- Without « » some quoted speech reads less clearly;
  the sentence before it ends with `.`.

## How to do the next part

Part 1 translation is complete. Next step: human review
against the Grabar source, with particular attention to
damaged or uncertain OCR passages and theological
terminology. Then continue with Parts 2 and 3.
