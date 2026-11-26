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

Photographs taken by the user on 2026-06-28 (09:48 to
10:02) of the two-storey church of 1301 in Yeghvard
(Kotayk), for a 3D model: a burial chapel below, a
church above entered by a high door on the west (once
by wooden stairs), a drum of columns and a cone on
top. Shrunk to 1000 pixels, without their metadata,
numbered in the order they were taken (the walk round
the building).

The sides: the high door is on the west, the front
(Wikipedia below: the bird on the right side, the goat
on the left, the cat on the goat at the back). The
user's shadow in `01` and `02`, at about ten in the
morning, points at the back, so it faces east; the
left side (north) is in shade.

| File | What it shows |
|------|---------------|
| `01-approach-from-gate.jpg`, `02-approach-path.jpg` | the church at the end of the path from the gate: the east side, the drum and the cone |
| `03-east-whole.jpg` | the east side, whole, from the south-east corner: the dark lower courses, a small stepped window and two slits below, a double rosette, the upper frame |
| `04-east-gable.jpg` | the east upper storey: a large arch of interlace, a frame of chains, a lion on a goat over a quatrefoil with a slit window, two blind arches |
| `05`-`08` | the eaves of the east gable: star rosettes, carved triangles, the corner capitals; the gable's top at the foot of the drum, with a ball |
| `09-eaves-drum-column.jpg`, `10-eaves-drum-column-2.jpg` | the drum's columns, their bases and capitals, over the eaves |
| `11-blind-arch-rosette.jpg` | a blind arch: pointed, of interlace, a rosette, twin shafts |
| `12-lower-cross-window.jpg` | a cross-shaped window of the lower storey, carved with a lattice (north or south) |
| `13-west-upper-storey.jpg` | the west upper storey, whole: the high door with its stalactite head, two lions on bulls, the inscriptions and khachkars, the corbel |
| `14-west-gable-drum.jpg` | the west gable and the drum: the cross of interlaced bands, the two figures, the twelve columns, the cone |
| `15-west-gable-figures.jpg` | the two figures in the west gable (a woman with a child, a man) |
| `16-west-gable-cornice.jpg` | the eaves of the west gable and the foot of the drum |
| `17-west-blind-arch-inscription.jpg`, `18-west-inscription-khachkars.jpg` | the blind arch left of the door, the inscription and the small khachkars |
| `19-west-upper-door-vault.jpg` | through the high door: the stalactite vault inside |
| `20-west-upper-door-lions.jpg` | the high door and the corbel under it |
| `21-west-corner-from-north.jpg` | the north-west corner from below: the setback of the roofs, the drum, the inscriptions |
| `22-north-gable.jpg`, `25-north-gable-oblique.jpg` | the north upper storey: a large arch, a cross-shaped frame, the relief, a slit window, two blind arches |
| `23-north-whole-far.jpg`, `24-north-whole.jpg` | the whole church from the north, the west on the right (its lower door) |
| `26-north-relief.jpg` | the north relief, close |
| `27-south-gable-oblique.jpg`, `32-south-gable.jpg` | the south upper storey: a frame of chains, the eagle with a lamb, a window split by a column, a knot below |
| `28-south-window-column.jpg` | that window and its column |
| `29`, `30`, `33` | the eagle, close |
| `31-south-whole.jpg` | the whole church from the south |
| `34-east-relief.jpg` | the east relief (a lion on a goat), close |

No sizes: none were measured, and none are in the
sources read so far. Wikipedia, «Holy Mother of God
Church, Yeghvard»
(<https://en.wikipedia.org/wiki/Holy_Mother_of_God_Church,_Yeghvard>,
read 2026-11-26, CC BY-SA 4.0) gives: finished 1301,
architect Shahik Vardapet; cruciform inside, almost
square outside; a drum of twelve columns with arches
and a cone; one small window on the north and east of
the upper storey, a larger one with a column on the
south; the lower storey's portal on the west, a small
window on each other side. The study with the plan,
P. Donabédian, Y. Porter, «Eghvard (Arménie, début
XIVe siècle), La chapelle de l'alliance», *Hortus
Artium Medievalium* 23 (2), 2017, pp. 837-855
(HAL `halshs-01592491`), could not be fetched from
here.
