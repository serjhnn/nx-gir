# Fonts of the web reader

Bundled so the pages load nothing from other sites.
`../fonts.css` names them; the font button in the
reader chooses between them.

| Files | Font | License |
|---|---|---|
| `noto-*` | Noto Serif Armenian | SIL OFL 1.1, `OFL-noto-serif-armenian.txt` |
| `garamond-*` | EB Garamond | SIL OFL 1.1, `OFL-eb-garamond.txt` |
| `oldstandard-*` | Old Standard TT | SIL OFL 1.1, `OFL-old-standard.txt` |
| `freeserif-*` | GNU FreeSerif, Armenian letters only | GPL 3+ with the font exception, `FreeFont-license.txt` |

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
