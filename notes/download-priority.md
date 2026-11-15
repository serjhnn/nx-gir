# Grabar books to download, by priority

From `notes/digilib.tsv` (2026-11-11): books in the
section "Հայ դասական մատենագրութիւն" with typed text,
not yet in `books/`. The `kind` column is a guess:
check a book before fetching it
(`scripts/fetch-digilib.py`). Numbers: Digilib id,
sections (parts).

Already ours: Tatevatsi, Gosh, Shnorhali, Anania
(partly), Narekatsi (ids 178, 3052; the list is older
than the import).

## 1. The 5th-century core (plain Grabar, the model
   of the language)

| id  | author, book | parts | kind |
|-----|--------------|-------|------|
| 162 | Եզնիկ Կողբացի, Եղծ աղանդոց | 93 | mixed |
| 54  | Ագաթանգեղոս, Պատմութիւն Հայոց | 138 | mixed |
| 310 | Փաւստոս Բուզանդ, Պատմութիւն Հայոց | 148 | mixed |
| 252 | Կորիւն, Վարք Մաշտոցի | 91 | mixed |
| 286 | Մովսէս Խորենացի, Պատմութիւն Հայոց | 194 | grabar |
| 1591 | Ղազար Փարպեցի, Պատմութիւն Հայոց | 104 | grabar |
| 150 | Եղիշէ, Վասն Վարդանայ | 8 | mixed |
| 1394 | Եղիշէ, Մեկնութիւն Արարածոց | 108 | grabar |

Status (2026-11-14): Eznik (162) is in `books/`.
Agathangelos (54) is in `books/` too (2026-11-15,
138 sections in four parts; its chapters are lines
`Ա.` on their own, read by `lone_numbers()` in
`nxgir_reader.py`). Five sections are empty on
Digilib: group headings with no text of their own.
Pavstos Buzand (310) is in `books/` too (2026-11-15,
148 sections in three parts; five are empty group
headings). Koriun (252) is in `books/` too (2026-11-15, 91
sections in two parts: Digilib holds four editions of
the text, kept as they are; chapters `[Գլուխ Ա]`,
`[Բ]`). Movses Khorenatsi (286) is in `books/` too
(2026-11-15, 194 sections in three parts). Digilib
lists its sections sorted by title, so the three
books come mixed: fetched with `--by-id`; chapter
numbers restart at Ա for Books II and III (no book
headings on Digilib). Ghazar Parpetsi (1591) is in `books/` too
(2026-11-15, 104 sections in three parts; three are
empty; chapters are lines `Ա.`, with footnote
numbers at some line starts, left as on Digilib).
Yeghishe, Vasn Vardanay (150) is in `books/` too
(2026-11-15, 8 sections in two parts; its seven
`Առաջին յեղանակ՝` headings are read by
`ordinal_entries()`). Yeghishe, Meknutiun Arardatsots (1394) is in
`books/` too (2026-11-15, 108 sections in three
parts; a critical edition with manuscript marks, fetched
with `--by-id`: Digilib lists the first 22 sections
out of order; its headings `Ա (Ա II)`, and the notes
and appendix, are read by `contents()`).
Group 1 is done, with Yeghishe's Khratk (1395, 32
sections in three parts: counsels, a treatise on
souls, a commentary on Joshua and Judges; its Contents
lists only the lettered chapters, `Բ. Վասն ...`) and
Ghazar's Tught (1592, one short part).

Group 2 (2026-11-15): Grigor Lusavorich, Yachakhapatum
charq (1596) is in `books/` (25 sections in three
parts; chapters `Ա. Title` with the number alone on
the next line, `titled_numbers()`; three headings
have broken characters from Digilib, left as they
are; the edition note at the start is kept). The two
Kanonk (370, 371) are in `books/` too (one part each,
under 150 lines). Shirakatsi was already complete (19 works, see
`books/SOURCES.md`). Hetum Patmich: 203 and 204 are in
`books/` (one part each; the chronicle, 204, has four
sections marked [1]-[4] and no headings: in
`NO_CONTENTS`). Not taken: 1588, a modern edition
with a long modern foreword, a table of three
editions and a variants apparatus; 202 (Hetum II's
annals, unclear). Ghevond (168) is in `books/` (2026-11-15, 44
sections in two parts, one empty). Next, with the Digilib ids (the
numbers in group 2 below are not ids: 64, 66, 76 are
Shirakatsi's): Kirakos Gandzaketsi (250),
Tovma Artsruni (346), Kirakos Rshtuntsi (251).
Tovma Metsopetsi (347) is in `books/` (76 sections in one
part; the five appendix headings at the end have no
text on Digilib, which shows the last chapter again
for them: `blank_repeats()` in `fetch-digilib.py`).

Also Եղիշէ Խրատք 1395, Ղազար Փարպեցի Թուղթ 1592.
These are the most read and the best sources for
Grabar vocabulary; "mixed" means a modern foreword:
the fetch script must cut it.

## 2. Short and cheap (1 to 40 parts, grabar)

- Գրիգոր Լուսաւորիչ: Յաճախապատում ճառք (1596, 25),
  Կանոնք (370, 371, 1 part each)
- Անանիա Շիրակացի: the rest, 12 of 19 books are
  grabar (e.g. 64, 67, 68, 70)
- Հեթում Պատմիչ (3 books, 10 parts)
- Եղիշէ, Խրատք (32)
- Ղեւոնդ (168), Թովմա Մեծոփեցի (347), Կիրակոս
  Գանձակեցի (250), Թովմա Արծրունի (346)

## 3. Medieval histories (grabar, 40 to 200 parts)

Ուխտանէս (148), Մովսէս Կաղանկատուացի / Դասխուրանցի
(111), Յովհաննէս Դրասխանակերտցի (69), Զաքարիա
Քանաքեռցի (135), Գրիգոր Դարանաղցի (177), Առաքել
Դաւրիժեցի (60), Արիստակէս Լաստիվերցի (26)

## 4. Law, theology and poetry (close to the
   existing library)

- Սմբատ Սպարապետ, Դատաստանագիրք (211, 169 parts):
  joins Gosh's law book
- Վարդան Այգեկցի, Ժողովածոյ առակաց (389)
- Ներսէս Լամբրոնացի, Խորհրդածութիւնք (133)
- Յակոբ Շահամիրեան, Որոգայթ փառաց (521, long)
- Սուքիաս, Տաղեր (27); Սիմէօն Լեհացի; Առաքել
  Բաղիշեցի; Ամիրաս Երզնկացի (medieval songs,
  unclear: check)

## 5. Late and long (grabar, later)

Երեմիա Չէլէպի Քէօմիւրճեան (152 parts, 9 books),
Սիմէօն Կաթողիկոս Երեւանցի (457), Չամչեանց,
Պատմութիւն Հայոց (443), Ժողովածուներ (1045)

## Skip for now

"no text" (696 books, PDF scans only), "modern" and
"other language"; "unclear" books need a look first.

## Per book, as in CLAUDE.md

Library name (`books/LIBRARY.tsv`), Contents check
(`tests/test_contents.py`), a Timeline line and a
limits record (`check-limits.py --site --record`).
