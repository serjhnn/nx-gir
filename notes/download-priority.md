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

## 0. Still to do, oldest first (2026-11-21)

Checked `notes/digilib.tsv` against `books/grabar/`:
the 5th to 7th century core (groups 1 to 3) is in
`books/`; these are what Digilib still has, oldest
and most important first. Dates from memory, the
`kind` is a guess: look before fetching.

| #  | work | id | parts | date |
|----|------|----|-------|------|
| 1  | Դաւիթ Անյաղթ, 4 works (philosophy, Aristotle, Porphyry) | 2600-2603 | 113 | 5th-6th c. |
| 2  | Գիւտ Արահեզացի, Թուղթ առ Վաչէ | 1519 | 1 | 5th c. |
| 3  | Մամբրէ Վերծանող, Ճառք | 1520 | 5 | 5th c. |
| 4  | Վրթանէս Քերթող, Յաղագս պատկերամարտից, Թղթեր | 1153, 1154 | 1+7 | 6th-7th c. |
| 5  | Գրիգորիս Արշարունի, Մեկնութիւն ընթերցուածոց | 2051 | 36 | about 7th c. |
| 6  | Անանուն, 684 թուականի պատմութիւն | 1597 | 35 | 7th-8th c. |
| 7  | Յովհան Մամիկոնեան, Պատմութիւն Տարաւնոյ | 1533 | 11 | tradition: 7th c. |
| 8  | Սահակ Վարդապետ (Մռուտ), Բացայայտութիւն (long) and 2 replies | 2202-2204 | 1 each | early medieval |
| 9  | Գրիգոր Մագիստրոս, Թղթեր (unclear: look first) | 177 | 88 | 11th c. |
| 10 | Վարդան Արեւելցի, Պատմութիւն; then 354, 355 | 356 | 101 | 13th c. |
| 11 | Մխիթար Անեցի, Աշխարհավէպ; Մխիթար Հերացի, Ջերմանց մխիթարութիւն | 276, 280 | 22, 49 | 12th c. |

Looked at on 2026-11-21 (first and middle section of
each; all plain Grabar, none needs a cut): 1153 is
one section of 15,000 letters; 1154 is seven letters;
2051 (36; the first, the title, is empty; headings
`Ա. Title`); 1597 (35; the first, Առաջաբան, is empty;
headings in `[ ]`; it tells of Jevanshir, so it is
7th century, up to 684 AD, not the Armenian era);
1533 (11; opens with the letters of Gregory and Zenob,
chapters `[Ա]`; the Zenob Glak tradition); 2202 is
one long section (136,000 letters), so it will be
cut into parts; 177 (88 letters, `[Ա]`, hard
Hellenizing Grabar); 356 (101; a 20,000-letter
preface first, in the style of the 1862 edition: look
at it, maybe keep). 2203 and 2204 not yet looked at.
Digilib's page numbers and `[ ]` stay as they are.

Next batch: 4 to 8 (1153, 1154, 2051, 1597, 1533,
2202 to 2204): about 100 sections, 4 to 5 minutes at
3 seconds a request. Then 9 and 10.

Added 2026-11-21: Grigor Aknertsi, Պատմութիւն
թաթարաց (1534, 17 sections) and Sargis Pitsak,
Ժամանակագրութիւն (317). Not taken: 202 (Hetum II,
mixed with a modern foreword), 336 (Orbelian, modern
text). Not on Digilib as typed text: Asoghik,
Mkhitar Ayrivanetsi, Hovhannes Erznkatsi, Vahram
Rabuni. Those with 0 sections (scans: Philon
Tirakatsi 1152, Vachagan 1156, Smbat Bagratuni 1157,
Sahak Ughkatsi 1158, Petros Syunetsi 1161-1163,
Nerses Bagrevandatsi 1166-1168, Hovhannes Gabeghenatsi
1170-1171, Hovhan Mayragometsi 1172-1174, Mathusagha
1189) cannot be fetched.

After these: the 1500s to 1800s chronicles and about
300 one-section songs (Տաղեր), minor.

Not possible: Փիլոն Տիրակացի (1152), Սահակ
Ձորոփորեցի (1159, 1160), Կորիւն's Life of Mesrop
(1561) and Յովհան Մամիկոնեան (1175, 1565): no typed
text on Digilib (scans only), or not Grabar.

Status (2026-11-21): 1 to 3 are in `books/`
(`davit-anyaght/`, `giwt-arahezatsi/`,
`mambre-vertsanogh/`)); 4 to 8 too (`vrtanes-kertogh/`,
`grigoris-arsharuni/`, `anonymous-684/`,
`hovhan-mamikonean/`, `sahak-vardapet-mrut/`).
9 (177, `grigor-magistros/`) and 10 (356, 354, 355,
`vardan-areveltsi/`) are in too. 11 (276, 280, `mkhitar-anetsi/`,
`mkhitar-heratsi/`) is in too: the ranked list is done.
What is left is later (15th to 19th century) or minor.

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
Shirakatsi's): Kirakos Gandzaketsi (250, 66 sections), Tovma
Artsruni (346, 64 sections in three books, chapters
restart at Ա) and Kirakos Rshtuntsi (251, 47 lines) are
in `books/` too. Group 2 is done.
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

Status (2026-11-15): in `books/`: Ukhtanes (350), Movses
Daskhurantsi (283), Grigor Daranaghtsi (172), Hovhannes
Drasxanakertsi (214), Aristakes (126), Arakel
Davrizhetsi (121). Digilib lists 350, 283 and 121 out
of order: fetched with `--by-id`. Daranaghtsi and
Drasxanakertsi are in sections marked [1], [2], ...
and have no Contents (`NUMBERED_ONLY` in
`tests/test_contents.py`). Ukhtanes has two `<font>`
fragments of Digilib's own markup in its text. Zakaria
Kanakertsi (367, 135 sections in three parts) too: group 3
is done.

## 4. Law, theology and poetry (close to the
   existing library)

Status (2026-11-15): Smbat Sparapet's Datastanagirk
(Digilib 332, 211 sections in one part) and Nerses
Lambronatsi's Khorhrdatsutiunk (1483, 133 sections in
seven parts, fetched with `--by-id`) are in `books/`.
The ids in the list below are not Digilib ids: Vardan
Aygektsi is 352 (Zhoghovatsoy arakats; Armat havatoy
353 is the other), Shahamirian 195 (194 is his
second Orogayt), Sukias 342. 352, 195 and 342 failed
when Digilib went down (404 on every page): to do.

Status (2026-11-19): Vardan Aygektsi, Zhoghovatsoy
arakats (352, 389 sections in three parts) and Sebeos,
Patmutiun (321, 52 sections in two parts; not on
the lists above, `mixed` but Grabar throughout) are in
`books/`. Shahamirian (194, 195) is not Grabar (1773):
skip. Sukias (342) is to check first.
Later the same day: Seberianos (3450), Mandakuni
(207), Yeghishe's Kanonk (1396), Abraham Aghbatanetsi
(1594, 1595), Anastas (1151), Anania Targmanich (1393),
Khosrovik (2200), Ozhnetsi (222), Tgha (180), Samuel
Anetsi (315), Nerses Paliants (293, 294), Yakob
Hrimetsi (188) and Komitas Aghtsetsi (1586). Not
kept: 83, the Paris and Vienna romance, a rhymed
poem in Middle Armenian. Nerses Shnorhali 295, 296
and 298 were ours already.

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
