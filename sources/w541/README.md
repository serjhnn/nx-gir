# The letters of W.541

The letters of nxGir Dzeragir: the small letters
(steps 1-9) and the capitals (step 10). The small
letters were taken from
eleven pages of Walters Ms. W.541 (images 40, 80,
100, 120, 163, 180, 260, 280, 300, 320 and 420 of
the OPenn set; see `../README.md`).

How they were taken:

1. The red channel of each 600 dpi master shows the
   black ink and hides the paper and the red
   initials; the ink was cut into lines (by the row
   profile of each column) and into its connected
   pieces, about 6300 of them. Letters this scribe
   joins come out as one piece; those were left out.
2. The pieces were grouped by shape (k-means on the
   piece placed by its baseline and x-height). The
   clear groups were named by eye.
3. Every line was then read with those names and
   looked for in the Gospels of the 1895 Grabar
   Bible (`books/grabar/bible/new-testament/`),
   allowing a few wrong letters. 233 lines were
   found; each piece of a found line takes the
   letter of the text at its place. This corrected
   the names given by eye (the hooked form is մ, the
   one like a J is յ, the triangle is ձ) and named
   letters the groups had mixed (ո and ս, ա and տ).
4. For each letter, the copies that agree best in
   shape (up to 14) were laid over each other on
   the baseline, shifted to fit, and averaged; the
   ink most copies share was kept (`letters/`).

27 small letters came out whole this way, from
eleven pages: ա դ ե զ է ը ի լ խ կ հ ձ ղ մ յ ն շ ո
պ ս վ տ ր ց ւ փ ք.

5. The rest this scribe joins to the letters beside
   them. With sixteen more pages (images 50 to 350,
   every twentieth; 27 pages in all, 460 lines found
   in the Gospels), a piece whose text is known and
   holds the letter at its start or end next to
   letters already found was cut: the widths of the
   found letters say where, and the cut goes at the
   thinnest column near there (the joining stroke).
   The cuts were checked by eye and the good ones
   averaged: բ գ թ ժ ծ ճ չ ջ ռ (one to six copies
   each; ճ has only one).

6. ե and և. The six copies first taken for ե have a
   small upturned hook on the foot: they are the
   scribe's և, the word «եւ» written as one sign
   (compare «= եւ ի ժամանակի» on image 70). The
   plain ե (a tall stem, an arm in the middle, a
   foot on the baseline, as in «ձեր» and
   «ամենայն») was cut like the joined letters: 220
   cuts where the text has ե but not եւ; the 23
   that agree best in shape were averaged. The font
   draws a typed ե ւ as his և (an OpenType liga).

7. շ, made again: the first had four copies, one
   of them wrong. Now nine cuts where the text has
   շ, and seven more pieces of the same shape found
   among the pieces the alignment did not read
   (pieces of that shape were also չ and լ, left
   out): 16 copies from 11 pages.

8. ծ and թ: averages of their copies came out
   unclear, so each is one copy, chosen by eye by
   the user among the copies found (ծ from image
   120, թ from image 290), its edge only smoothed.

9. Punctuation. The manuscript gives only the dot
   (`.`, and ։ as two of them). The other marks of
   the font, ՝ ՛ ՞ ՜ , ; « » - ֊ ( ), are not the
   scribe's: Claude drew them with a round pen of
   his weight, so they are as heavy as his letters
   (`marks/`, listed in `marks.tsv`). The ASCII
   colon is drawn as his ։. The digits 0-9 are
   drawn the same way, leaning with his hand.

10. Capitals (`capitals/`, `capitals.tsv`). The
   text has no black capitals: its sentences open
   with a red initial, written large at the start
   of a line. 185 pages (images 20 to 480, every
   fifth and every fifth plus two) were read
   again for the red ink alone: red over green
   well above the paper's, smoothed, kept where it
   touches clearly red ink, so the pale hairlines
   stay. Its pieces of initial size (about 1040)
   were grouped by shape. Each page's run of
   initials was lined up with the capitals that
   open sentences in the 1895 Gospels, all pages at
   once and in order (a page only moves the text
   forward); a group took the letter the text gives
   most. Where the text could not say (rare
   letters, a print that starts its sentences
   otherwise), the word after the initial was read
   on the page: «Բայց ասեմ ձեզ», «Դուք էք աղ
   երկրի», «Որ ընդունի», «Վասն այդորիկ», «Մարդ
   բարի», «Գնացին աշակերտքն». This corrected two
   names: the shape like Կ is his Վ, the U with a
   flag his Մ. For each letter the copies whose
   shape and text agree were scaled to one height,
   fitted on the medoid (the copy most like the
   others) by size and place, and the 8 closest
   averaged, as in step 4; Ձ, with five copies, is
   the medoid alone. Then 265 pages (every other
   page from 14 to 480): the initials far from all
   named shapes were grouped, shown to the user
   with their line, and named by them: Կ («Կամ
   զիա՞րդ»), Ս (a plain U, «Սաղմովն ծնաւ»; his Մ
   has a flag), Ք, Փ, Թ and Տ (an S); an Ո with a
   hook is Ո՞, not Ռ. Then those the text points
   at, among the initials still unnamed: Լ
   («Լուարուք»), Ը (an L with a loop), Ծ
   («Ծնունդք իժից»), Չ («Չոգաւ», «Չոգան»: a plain
   2) and Ձ («Ձայն»: the 2 with a stroke across its
   foot; the first Ձ, a plain 2, was his Չ). Their
   copies were found by shape and averaged, or one
   copy taken where only one is clean (Թ, Ը, Ծ, Ձ,
   Ք, Փ, Տ). Last, for the rare ones, the pages
   where the Gospels have a sentence starting with
   them were worked out from the pages already
   lined up, and only those fetched (27 more):
   Խ («Խնդրեցէք եւ տացի ձեզ»), Ճ («Ճրագ
   մարմնոյ») and Է («Էր Անդրէաս», a Ե with a
   foot), then, with 31 pages more, Ժ («Ժողովեցին
   եւ լցին», John 6:13) and Շ («Շուրջ եղեն
   զնովաւ», John 10:24); one copy each. 30
   capitals: Ա Բ Գ Դ Ե Զ Է Ը Թ Ժ Ի Լ Խ Ծ Կ Հ Ձ Ճ
   Մ Յ Ն Շ Ո Չ Պ Ս Վ Տ Փ Ք. At every sentence of
   the Gospels that starts with Ղ Ջ Ռ Ր Ց, the
   place between the initials around it was looked
   at: W.541 writes no initial there. Ռ and Ց were
   then taken from another book of the same kind,
   W.542 (`../w542/README.md`). Ղ Ջ Ր are in
   neither (nor were they found in a hymnal, W.547),
   so, at the user's asking, Claude composed them
   from his own capitals: Ր is his Ո with the right
   leg ended short, Ղ his Լ with the hump of his Ի
   on its stem, Ջ his Չ with its top hook carried
   on down across the descent, closing a loop, as
   the printed Ջ (copies 0 in `capitals.tsv`). 35
   capitals in all; Ւ and Ֆ, which open no
   sentence, are not; Օ is drawn, as օ (below);
   the font keeps his small letters bigger for
   those. The pictures are as large as written
   (the ink alone); the initials are written finer
   than the text, so the font scales them alike
   and widens their strokes to his weight
   (`scripts/render-scan-font.py`).

`letters.tsv` gives the copies and pages of each,
and `.` the scribe's dot. օ (the scribe writes աւ)
and ֆ are not in the manuscript. օ and Օ are drawn
by Claude, with a broad nib moved along a leaning
oval, as heavy as his letters (`marks/0585.png`,
`0555.png`, in `marks.tsv`, at the user's asking);
ֆ is not in the font.

The pictures in `letters/` are 120 pixels per
x-height, the baseline at row 288, black ink on
white; those in `capitals/` are the red ink of the
initials, as large as written, in black.
