# The letters of W.541

The small letters of nxGir Dzeragir, taken from
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
   colon is drawn as his ։.

`letters.tsv` gives the copies and pages of each,
and `.` the scribe's dot. օ (the scribe writes աւ)
and ֆ are not in the manuscript, so not in the font.

The pictures are 120 pixels per x-height, the
baseline at row 288, black ink on white.
