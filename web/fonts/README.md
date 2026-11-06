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
| `freeserif-*` | GNU FreeSerif, Armenian letters only | GPL 3+ with the font exception, `FreeFont-license.txt` |

The Arian fonts are the .ttf files of
`arian-grqi.zip` and `arian-amu-serif.zip` from
fonter.am (fonts/arian-grqi, fonts/arian-amu-serif),
renamed but otherwise as they came: their license
(Armenian, from the zips) lets anyone copy and share
them with the license beside them, and asks that a
changed font not use the names Arian, AMU or
Tarumian; their name tables also cite the SIL OFL
1.1, with the Reserved Font Name Arian AMU.

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
