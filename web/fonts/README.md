# Fonts of the web reader

Bundled so the pages load nothing from other sites.
`../fonts.css` names them; the font list in the
reader's text settings chooses between them, for the
text of the books only.

| Files | Font | License |
|---|---|---|
| `noto-*` | Noto Serif Armenian | SIL OFL 1.1, `OFL-noto-serif-armenian.txt` |
| `garamond-*` | EB Garamond | SIL OFL 1.1, `OFL-eb-garamond.txt` |
| `oldstandard-*` | Old Standard TT | SIL OFL 1.1, `OFL-old-standard.txt` |
| `arian-grqi-*` | Arian Grqi | Free license of Ruben Hakobyan (Tarumian), `Arian-AMU-license.txt` |
| `arian-serif-*` | Arian AMU Serif | the same |
| `faulmann-*` | Faulmann, by Dare-demo Iie (2020) | no license file; fonter.am: "free to download and free to use, personally or commercially" |
| `geghagrutyun-*` | Armeniapedia Geghagrutyun, by Raffi Kojian (2016) | no license file; fonter.am: "free to download and free to use, personally or commercially" |
| `tumanian-*` | Tumanian's Handwriting, by Ruben Tarumian (2005) | no license file; the author (tarumian.am/?p=2243): "Տառատեսակը կարող եք ազատորեն ներբեռնել եւ անվճար գործածել" (free to download and use) |
| `freeserif-*` | GNU FreeSerif, Armenian letters only | GPL 3+ with the font exception, `FreeFont-license.txt` |
| `bolorgir-*` | nxGir Bolorgir, our own, made from Noto Serif Armenian and Noto Serif | SIL OFL 1.1, `OFL-bolorgir.txt` |
| `dzeragir-*` | nxGir Dzeragir, our own: the letters of a scribe (Walters Ms. W.541, CC0 images) | SIL OFL 1.1, `OFL-dzeragir.txt` |

The Arian fonts are the .ttf files of
`arian-grqi.zip` and `arian-amu-serif.zip` from
fonter.am (fonts/arian-grqi, fonts/arian-amu-serif),
renamed but otherwise as they came: their license
(Armenian, from the zips) lets anyone copy and share
them with the license beside them, and asks that a
changed font not use the names Arian, AMU or
Tarumian; their name tables also cite the SIL OFL
1.1, with the Reserved Font Name Arian AMU.

Faulmann is FaulmannFont.ttf of `faulmann.zip` from
fonter.am (fonts/faulmann), renamed but otherwise as
it came. It has no license of its own beyond the
copyright line "(c) Dare-demo Iie, 2020"; it is here
on fonter.am's terms quoted above.

Geghagrutyun is ArmeniapediaGeghagrutyun.ttf of
`armeniapedia-geghagrutyun.zip` from fonter.am
(fonts/armeniapedia-geghagrutyun), renamed but
otherwise as it came, on the same terms: only the
copyright line "Copyright (c) 2016, Raffi Kojian".
It has the Armenian letters and digits, no
punctuation, Latin or Cyrillic.

Tumanian's Handwriting is
ArTar_TumanianDzeragir_U.ttf of
`tumanian-dzeragir.zip` from fonter.am
(fonts/tumanian-dzeragir), renamed but otherwise as it
came. It carries "Copyright (c) 2005 by Ruben
Tarumian. All rights reserved."; its terms are the
author's words quoted above.

The Noto, EB Garamond and Old Standard files are the
woff2 files of the Fontsource npm packages
(`@fontsource/noto-serif-armenian`,
`@fontsource/eb-garamond`,
`@fontsource/old-standard-tt`, version 5.3.0),
renamed. The FreeSerif files are cut from
FreeSerif.ttf, FreeSerifItalic.ttf and
FreeSerifBold.ttf of Debian's `fonts-freefont-ttf`
(20211204) with fontTools, keeping U+0530-058F and
U+FB13-FB17:

```sh
pyftsubset FreeSerif.ttf --flavor=woff2 \
  --unicodes=U+0530-058F,U+FB13-FB17 \
  --layout-features='*' \
  --output-file=freeserif-400-normal.woff2
```

nxGir Bolorgir is made by `scripts/render-font.py`
(run it again after changing it; it takes about a
minute and a half): each letter of Noto Serif
Armenian (and the Latin letters, digits and
punctuation of Noto Serif, from the files here) is
drawn big, made wider and lower, thinned to its
middle line and written again with a broad pen at
35°, as in a bolorgir manuscript; the picture is
traced back to curves with potrace. Being made
from Noto, it is under the OFL like Noto, with a
name of its own (Noto has no Reserved Font Name).
The script needs scipy, scikit-image, fonttools,
brotli and potracer (pip), and nothing else here
does.

nxGir Dzeragir is made by
`scripts/render-scan-font.py` from the letters in
`sources/w541/` (how they were taken from the
manuscript is in `sources/w541/README.md`): each is
traced with potrace, its width measured on its body
so that tails and hooks reach over the letters
beside it, as written. Every letter in it is the
scribe's: the capitals are his small letters drawn
bigger, ։ two of his dots, and his և (the word եւ
as one sign) stands for a typed ե ւ (liga). What he
never wrote (օ, ֆ, Latin letters, digits, most
punctuation) is not in the font; the reader shows
it in Noto, the next font in the stack.
