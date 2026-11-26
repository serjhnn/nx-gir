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

## lastivertsi-1963/

`lastivertsi-grabar-1963.pdf`: Պատմութիւն Արիստակիսի
Լաստիվերցւոյ, Yerevan 1963, the critical edition by
Karen Yuzbashyan, 157 PDF pages (12.5 MB, 300 ppi, black
and white), on the Internet Archive (put there by Robert
Bedrosian): <https://archive.org/details/LastiverttsiGrabar1963>
(file `Lastiverttsi_grabar_1963.pdf`, copied unchanged on
2026-11-17).

Used to test and tune the OCR (`ocr/`): a second book with
a different typeface from the Smbat scan, with the
manuscript variants (the apparatus) in small print under
the text. The text in `books/grabar/aristakes-lastivertsi/`
(from Digilib) is the same critical edition, and is the
reference the OCR is scored against. Pages are not typed
from this scan.

## glakavank/

What the 3D model of Glakavank (the monastery of
Karapet above Mush, `web/models/glakavank.js`) is built
from, copied on 2026-11-25:

| File | What it is |
|------|------------|
| `lynch-1901-fig155-south.jpg` | H. F. B. Lynch, *Armenia: Travels and Studies*, vol. 2 (1901), Fig. 155, "Monastery of Surb Karapet from the South" (PDF page 242): the walls, the round tower, the two cones, the slope |
| `lynch-1901-church-south-west.jpg` | the same book, "Church of Surb Karapet from South-West" (PDF page 243): the belfry over the porch, the hall, the graves |
| `lynch-1901-fig158-two-chapels.jpg` | the same book, Fig. 158, "The Two Chapels at Surb Karapet" (PDF page 251): the banded drums, the cones, the cross roofs |
| `before-1915-church-south-west.jpg` | a photograph before 1915 (photographer not named), the church from high in the south-west: the two stages of the belfry, the checkered base, the earth roof, the slender drums; from Nune Movsisyan's blog (below) |
| `before-1915-church-three-views.jpg` | three photographs before 1915 put together on the same blog page: the church from the south-west and twice from the west (the belfry and the cones) |
| `plan-hewsen-2001-commons.png` | the plan, drawn by Yerevantsi after R. Hewsen, *Armenia: A Historical Atlas* (2001), p. 206; Wikimedia Commons, `File:Surb_Karapet_Monastery_plan.png`, CC BY-SA 4.0 |

Lynch's book (public domain) is the scan on the
Internet Archive:
<https://archive.org/details/armeniatravelsst02lync>
(`armeniatravelsst02lync.pdf`); the photographs are cut
from it, in grey. His text on the monastery is on
pp. 176-181: the gate on the west, the long line of
buildings on the south, the belfry and porch faced with
white marble, the two chapels on the east "with their
polygonal towers and conical roofs", the flat roof of
the church, the terrace and cemetery outside the walls,
the height (about 6400 feet).

The two photographs above come from the page «Մշո Ս.
Կարապետ» (2013) of Nune Movsisyan's blog,
<https://movsisyannune.com/2013/08/13/%D5%B4%D5%B7%D5%B8-%D5%BD-%D5%AF%D5%A1%D6%80%D5%A1%D5%BA%D5%A5%D5%BF-%D5%BE%D5%A1%D5%B6%D6%84%D5%A8/>
(copied on 2026-11-25; its text is not copied). Its
text, from the book «Տարոնի պատմական հուշարձանները»,
adds: the belfry domed on eight columns, with four
bells; the martyrium 10 by 6 m and 15 m high; the
cells of two floors on the north and the west; the
cross-yard (Խաչբակ) behind the church, the graves of
the abbots; the Harutyun chapel in the south-west
court, walled with stone.

Measured from the plan at about 0.085 m a pixel: the
hall 23 by 28 m (16 columns), the chapels 20 m deep.
Not in any source, estimated from the photographs: the
heights, the size of the enclosure (about 104 by 84 m),
the round towers at the corners, where in the court
the Harutyun chapel stood.

## yeghvard/

Photographs taken by the user on 2026-06-28 (09:53 to
10:02), for a 3D model of the two-storey church of
1301 in Yeghvard (Kotayk; still to be confirmed by
the user): a burial chapel below, a church above
entered by a high door (once by stairs), a drum of
columns on top. Shrunk to 1000 pixels and without
their metadata; the names follow the walk round the
building. The sides are named by what is carved on
them; which side faces where is not yet known (the
lion-and-arch side is in shade and has the front on
its right, so it may be the north).

| File | What it shows |
|------|---------------|
| `01-front-gable-figures.jpg` | the front's gable: two figures in relief beside a cross of interlaced bands (a woman with a child, and a man) |
| `02-front-gable-cornice.jpg` | the eaves of a gable: the star rosettes of the cornice, a carved triangle, the foot of the drum's columns |
| `03-front-blind-arch-inscription.jpg` | a blind arch beside the upper door: pointed arch of interlace, a rosette, twin shafts, the inscription below |
| `04-front-inscription-khachkars.jpg` | the inscription and four small khachkars set in the wall |
| `05-upper-door-vault.jpg` | through the upper door: the stalactite (muqarnas) vault inside |
| `06-upper-door-lions.jpg` | the upper door: frames of stars and chains, a stalactite head, two lions attacking bulls above it, the corbel below (where the stairs were) |
| `07-front-corner-from-side.jpg` | the corner of the front, from below: the setback of the roofs, the drum's columns, the inscriptions |
| `08-lion-arch-gable.jpg` | the lion-and-arch side, its upper storey: a large arch of interlace over a cross-shaped frame, a lion on a bull, a slit window, two blind arches |
| `09-lion-arch-whole-far.jpg` | the whole church from this side, with the front on the right (the lower door) |
| `10-lion-arch-whole.jpg` | the same, nearer: the two storeys, the cross-shaped window below, the drum |
| `11-lion-arch-gable-oblique.jpg` | the upper storey of this side, from the left |
| `12-lion-arch-relief.jpg` | the lion on the bull, close |
| `13-eagle-gable-oblique.jpg` | the eagle side, its upper storey: a frame of chains, an eagle holding a lamb, a window split by a column, two blind arches, a knot below |
| `14-eagle-window-column.jpg` | that window and its column, close |
| `15-eagle-relief-left.jpg`, `16-eagle-relief.jpg`, `19-eagle-relief-close.jpg` | the eagle and the lamb, close |
| `17-eagle-whole.jpg` | the whole church from the eagle side: the cross-shaped window below, the drum of columns |
| `18-eagle-gable.jpg` | the eagle side's gable, near the front |
| `20-lion-quatrefoil-relief.jpg` | a third side: a lion on a bull over a quatrefoil frame with a slit window, a rosette above |

Not yet seen, to look for: the plan and the sizes
(a published survey), the side of the quatrefoil as
a whole, the roof and the drum's top from afar, the
lower door and the inside of the lower storey.
