# Sources

Copies of the sources used for the Grabar helper data,
so every entry can be checked by hand, and the scan
behind a book typed from print.

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

## Vocabulary: Wiktionary via kaikki.org

`grabar/vocabulary.tsv` and `grabar/forms.tsv` are
built by `scripts/fetch-vocabulary.py` from the Old
Armenian entries of the English Wiktionary, as
extracted by kaikki.org (wiktextract):
<https://kaikki.org/dictionary/Old%20Armenian/>.
The extract is 48 MB, so no copy of it is kept here:
the TSV files keep the headword, part of speech and
glosses of every entry, and each one can be checked at
`https://en.wiktionary.org/wiki/<word>#Old_Armenian`.
The download date is at the top of both files. Their
text is under CC BY-SA 4.0
(<https://creativecommons.org/licenses/by-sa/4.0/>).

To update, run `scripts/fetch-vocabulary.py`; do not
edit the files by hand.

## Armenian meanings: the Armenian Wiktionary

`grabar/vocabulary-hy.tsv` is built by
`scripts/fetch-vocabulary-hy.py` from the dump of the
Armenian Wiktionary
(<https://dumps.wikimedia.org/hywiktionary/latest/>,
`pages-articles.xml.bz2`, 40 MB, so no copy is kept
here). The download date is at the top of the file.
Its text is under CC BY-SA 4.0
(<https://creativecommons.org/licenses/by-sa/4.0/>);
each row can be checked at
`https://hy.wiktionary.org/wiki/<entry>`.

The entries are modern Armenian, in the reformed
spelling. `wiktionary/hy-astvats.wikitext` is one of
them, as of the dump of 2026-10-01: the page աստված,
with its classical spelling in `{{why|աստուած}}`, the
part of speech `{{-hy-գո-}}` and the meanings on the
`#` lines. The script matches our Grabar headwords to
the entries by that spelling, by the title, or by
simple spelling rules (`reform()` in the script).

To update, run `scripts/fetch-vocabulary-hy.py`; do
not edit the file by hand.

## N: no source yet

Entries marked `N` in `abbreviations.tsv` were read from
the letters and the grammar in nx-gir (e.g. ամցն =
ամենեցուն) and are not from a published source, so there
is no copy here. When a source turns up, add its copy
here and change the mark.

## shahnazareants-1859/

`taregirk-1859.pdf`: Տարեգիրք Սմբատայ Սպարապետի,
Paris 1859, edited by K. Shahnazareants (public
domain), 267 PDF pages (5.4 MB), the scan made by
Google and put on the Internet Archive by Robert
Bedrosian: <https://archive.org/details/SmbatGrabarTaregirk1859>
(file `Smbat_grabar_taregirk_1859.pdf`, copied
unchanged on 2026-11-15).

The text of `books/grabar/smbat-sparapet/2-taregirk/`
was typed from it: printed pages 21-141 are PDF pages
26-156 (pages 51-60 scan 41-50 a second time, so a
printed page p is PDF page p + 5 up to page 45 and
p + 15 after it). The 50 words that were hard to read
are in `notes/smbat-sparapet-taregirk.md`, by printed
page; check them here. The rest of the book (the
editor's preface and notes, and Vahram Rabuni's
history of the Rubenians) is not in the library.
