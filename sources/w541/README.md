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

27 small letters were found well enough:
ա դ ե զ է ը ի լ խ կ հ ձ ղ մ յ ն շ ո պ ս վ տ ր ց ւ փ ք
(`letters.tsv` gives the copies and pages of each).
The others (բ գ թ ժ ծ ճ չ ջ ռ օ ֆ), which this
scribe mostly joins to the letters beside them,
and the capitals, which the text hardly has, are
written with the pen of `scripts/render-font.py`
for now. More pages, or cutting joined pieces by
hand, would give them too.

The pictures are 120 pixels per x-height, the
baseline at row 288, black ink on white.
