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

Chunks 1–10: lines 1–750 translated in ten 75-line
chunks. Source and translation line counts match for the
translated prefix, and blank-line positions match. The
draft is being added incrementally and is not yet complete
or reviewed.

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

## How to do the next part

Continue Part 1 at source line 751, in chunks of 75–150
lines. After Part 1 is complete, run the repository
structure check, add the translation record as `machine`,
update the source and timeline records, and run the
repository tests. Then continue with Parts 2 and 3.
