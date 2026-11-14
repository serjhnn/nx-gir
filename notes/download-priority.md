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
- Ղեւոնդ (44), Թովմա Մեծոփեցի (76), Կիրակոս
  Գանձակեցի (66), Թովմա Արծրունի (64)

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
