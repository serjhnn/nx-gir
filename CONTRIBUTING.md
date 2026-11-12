# Contributing to nx-gir

Help is welcome, most of all with the translations
into modern Armenian, and with Grabar texts,
glossaries, abbreviations and test scans of old
prints.

## Reviewing a translation

The translations in `books/ashkharhabar/` (except
`bible/`) were first made by machine, by AI models
(Claude and GPT-6). They need people who know
Grabar to read them beside the original and correct
them.

1. Pick a part in `books/TRANSLATIONS.tsv` that is
   `machine`, or `review` if you work with its
   reviewer. Set it to `review` with your name.
2. Read it beside the Grabar: in the web reader,
   open the part and press ⇆ Parallel.
3. Correct the translation file. Keep one line per
   Grabar line, so the two stay side by side, and
   keep the `ԳԼՈՒԽ` and `(Գլուխ. X)` lines (see
   "Both translations" in `books/SOURCES.md`).
4. When the part is read through, set it to
   `reviewed`, with the date.

Your name is shown above the part in the reader
and on the site. Use the name you want to be
credited with.

## License of contributions

- **Translations** (`books/ashkharhabar/`, except
  `bible/`): [CC BY-SA 4.0][by-sa]. By sending a
  change to a translation you agree that it is
  published under this license, and that you have
  the right to do so (it is your own work, or free
  to use).
- **Grabar texts** (`books/grabar/`): old texts in
  the public domain; we add no license to them.
- **Code**: not decided yet.

## Crediting a translation

Name the work, Նախագիր and the license, and the
reviewers when it is reviewed, e.g.

> Գրիգոր Տաթեւացի, *Ամառան հատոր*, թարգմ.՝
> Նախագիր (nxgir.am), CC BY-SA 4.0

and say if you changed it. Your own version must be
under the same license.

[by-sa]: https://creativecommons.org/licenses/by-sa/4.0/
