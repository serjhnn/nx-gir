# Sources

Copies of the sources used for the Grabar helper data,
so every entry can be checked by hand.

## abrahamyan-1959/

Աշոտ Գ. Աբրահամյան, «Հայ գրի և գրչության պատմություն»,
Երևան, 1959, 416 pages. Scanned copy on the Internet
Archive: <https://archive.org/details/Abrahamyan>
(scan leaves 61-63, 300 ppi).

The pages of the chapter «Համառոտագրություն»
(abbreviations), cut from the scan:

| File | What is on the page | Kind in `abbreviations.tsv` |
|------|---------------------|-----------------------------|
| `page-111.jpg` | the 7 sacred names in երկաթագիր, nominative and genitive; պ = պէս; ք = քան | `sacred`, `part` |
| `page-112.jpg` | more ք = քան; ը = ընդ; կ = կամ; one-letter names (Գ°, Յ°, …) | `part`, `name` |
| `page-113.jpg` | two-letter words (թւ, վս, ամ, …); three and more letters (թգր, վրդ, եպկս, …); names (Եգս, Դւթ, …) | `word`, `name` |
| `page-114.jpg` | more names (Գրգր, Թրս, …); the -ութիւն endings and their case forms | `name`, `ending` |

Notes from reading the scans:

- The book spells Israel the old way, Իսրայէղ
  (abbreviated ԻԷՂ, genitive ԻՂԻ).
- Letters that were hard to read: վսյ (վասնորոյ),
  ճշտ (ճշմարիտ), Գգիկ (Գագիկ), զւր (զինուոր). Check
  them on `page-113.jpg` and `page-114.jpg`.
- The book has the mark (a line) over every short form;
  `abbreviations.tsv` leaves it out.
- The book says there are hundreds of abbreviations and
  gives only examples, so the list is not complete.

The pages are copied here only for checking the data.

## wiktionary/

`pativ-mark.wikitext`: the English Wiktionary entry for
the mark «՟» (<https://en.wiktionary.org/wiki/՟>), source
text as of 2026-10-21. It cites Tumanyan's grammar, p. 19.
Used for: յԱյ (յԱստուծոյ), Ավ (Աստուծով), -ութէ (-ութենէ),
and as a second source for ած, այ, ամ, սբ, պտ, -ութի and
-ութե. Its text is under CC BY-SA 4.0
(<https://creativecommons.org/licenses/by-sa/4.0/>).
Note: it gives Այ = Աստուածոյ, while Abrahamyan gives
աստուծոյ; the list uses Աստուծոյ.
