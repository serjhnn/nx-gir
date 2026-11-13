# Sources of the books in books/

## grabar/bible/new-testament/

The four Gospels in Grabar, from the Armenian Bible,
Venice 1895, edited by Arsen Bagratuni (public domain),
as published at <https://bible.armeniancathedral.org/>.

| File | Book | Chapters | Verses |
|------|------|---------:|-------:|
| `1-matthew.txt` | Աւետարան ըստ Մատթէոսի | 28 | 1068 |
| `2-mark.txt` | Աւետարան ըստ Մարկոսի | 16 | 675 |
| `3-luke.txt` | Աւետարան ըստ Ղուկասու | 24 | 1153 |
| `4-john.txt` | Աւետարան ըստ Յովհաննու | 21 | 877 |

Downloaded with `scripts/fetch-bible.py`, which also
documents the cleanup:

```sh
D=books/grabar/bible/new-testament
scripts/fetch-bible.py Mt 28 "Աւետարան ըստ Մատթէոսի" $D/1-matthew.txt
scripts/fetch-bible.py Mk 16 "Աւետարան ըստ Մարկոսի" $D/2-mark.txt
scripts/fetch-bible.py Lk 24 "Աւետարան ըստ Ղուկասու" $D/3-luke.txt
scripts/fetch-bible.py Jn 21 "Աւետարան ըստ Յովհաննու" $D/4-john.txt
```

Changes made when copying:

- The site writes `:` and `` ` `` in place of the Armenian
  full stop and comma; they were replaced with `։` and `՝`.
- Footnote markers like `[12]` and the ``` `` ``` that
  close a footnoted passage were removed (107 in Matthew,
  110 in Mark, 151 in Luke, 91 in John). The footnotes
  themselves are not included.
- Where a full stop stood on both sides of a footnote
  marker, one was kept (Matthew 1×, Mark 2×, John 1×).
- One verse per line, without verse numbers; each
  chapter starts with a heading `Գլուխ Ա`, `Գլուխ Բ`, ….

How this edition differs from the usual verse list:

- Matthew 16:3 has a number but no text, and Matthew
  23:14 is not in the edition. Both passages are also
  missing from several old manuscripts.
- Mark 9 numbers its verses 42, 44, 46 where other
  editions use 43–47; the text (hand, foot, eye) is all
  there.
- Luke has 1153 verses against the usual 1151 because
  of different verse division.
- John 14:14 is not in the edition.

## grabar/bible/old-testament/

Psalm 118 from the same Venice 1895 Bible and site.
The edition numbers the Psalms as the Greek and
Armenian Bibles do, so this is the long psalm
"Երանեալ են ամբիծք" (Psalm 119 in Hebrew numbering).

| File | Book | Verses |
|------|------|-------:|
| `psalm-118.txt` | Սաղմոս ՃԺԸ | 176 |

Downloaded on 2026-11-05 with the same cleanup as the
Gospels (47 footnote markers removed):

```sh
D=books/grabar/bible/old-testament
scripts/fetch-bible.py Ps 118-118 "Սաղմոս ՃԺԸ" $D/psalm-118.txt
```

The first line after the title is the heading
`Ալէլուիա։` (verse 0 on the site); then one verse per
line, without verse numbers or chapter heading.

## ashkharhabar/anania-shirakatsi/

Eight works of `grabar/anania-shirakatsi/`
translated into modern Eastern Armenian, one part
each, line for line with the Grabar (`01.txt`): `4-`,
`7-`, `8-`, `13-`, `14-`, `15-` (the Աշխարհացոյց, 471
lines), `16-` and `18-`. Made by Claude (Sonnet
5.5) on 2026-11-13 at the user's request, from the
Grabar only. Machine translation, not human-reviewed.

The Grabar files of these eight were cut into
sentences first (a line after each `։`; a blank line
where a Digilib paragraph ended); only line breaks
changed. No `։` had a missing space after it.
Choices and doubts: `notes/anania-shirakatsi.md`.

## ashkharhabar/bible/old-testament/

Psalm 118 in the Eastern Armenian translation of
the Mother See of Holy Etchmiadzin (Աստուածաշունչ
մատեան, Էջմիածին, 1994), as published on the same
site (its "Eastern Armenian 1994" text), in the
classical spelling the site uses. This translation
is not in the public domain; only this psalm is
included, for reading beside the Grabar.

| File | Book | Verses |
|------|------|-------:|
| `psalm-118.txt` | Սաղմոս ՃԺԸ | 176 |

Downloaded on 2026-11-05:

```sh
D=books/ashkharhabar/bible/old-testament
scripts/fetch-bible.py --1994 Ps 118-118 "Սաղմոս ՃԺԸ" $D/psalm-118.txt
```

The site's `:` was replaced with `։`; nothing else was
changed. The lines match
`grabar/bible/old-testament/psalm-118.txt` one for one
(title, `Ալէլուիա`, verses 1–176), so the web reader
can show the two side by side.

## grabar/grigor-tatevatsi/

Three works of Grigor Tatevatsi (Գրիգոր Տաթեւացի,
1346–1409) in Grabar, from Digilib, the digital library
of Armenian literature of the American University of
Armenia (<https://www.digilib.am>). Digilib typed the
texts from old printed editions; the texts themselves
are centuries old and in the public domain. Digilib
does not state a license for its typed copies.

| Folder | Work | Digilib | Sections | Parts |
|--------|------|---------|---------:|------:|
| `1-girk-harcmanc/` | Գիրք հարցմանց (Book of Questions) | [1477](https://www.digilib.am/book/1477/) | 511 | 12 |
| `2-dzmeran-hator/` | Գիրք քարոզութեան որ կոչի Ձմեռան հատոր (winter sermons) | [1476](https://www.digilib.am/book/1476/) | 164 | 18 |
| `3-amaran-hator/` | Գիրք քարոզութեան որ կոչի Ամառան հատոր (summer sermons) | [3409](https://www.digilib.am/book/3409/) | 38 | 24 |

Downloaded on 2026-10-21 with `scripts/fetch-digilib.py`:

```sh
D=books/grabar/grigor-tatevatsi
scripts/fetch-digilib.py 1477 "Գիրք հարցմանց" $D/1-girk-harcmanc
scripts/fetch-digilib.py 1476 "Գիրք քարոզութեան որ կոչի Ձմեռան հատոր" $D/2-dzmeran-hator
scripts/fetch-digilib.py 3409 "Գիրք քարոզութեան որ կոչի Ամառան հատոր" $D/3-amaran-hator
```

How the files are made:

- Each Digilib section becomes a heading line followed
  by its paragraphs, one per line. Runs of spaces
  become one space, and a heading repeated as the
  first paragraph is kept once; otherwise spelling,
  punctuation and the stress marks (՛) are as on
  Digilib.
- Each work is cut into parts of about 150,000
  characters (`01.txt`, `02.txt`, …) between sections,
  so the reader stays quick on a phone. The first line
  of a part is the title and `n/total`.
- In Գիրք հարցմանց, 42 sections are only group headings
  (e.g. `Գլուխ Ա ի մեծ ցանկէն`, `Երկրորդ Հատոր`) and
  have no text of their own.
- Some paragraphs are very long (a whole sermon in the
  summer volume can be one paragraph), as on Digilib.
- `3-amaran-hator/01.txt` to `15.txt` are cut
  further: one sentence per line (a sentence ends
  at `։`, as the reader counts them), with a blank
  line where a Digilib paragraph ended, to be read
  beside its translation in `ashkharhabar/`. The
  words are as on Digilib; where a `։` had no space
  after it (6 times in part 1, 5 in part 2, 7 in
  part 3, 6 in part 4, 9 in part 5, 4 in part
  6, 11 in part 7, none in parts 8 and 9, 1 in
  part 10, none in part 11, 2 in part 12, none
  in part 13, 3 in part 14, none in part 15),
  the line break now stands there.
- `2-dzmeran-hator/01.txt` is cut the same way
  (no `։` without a space after it).
- `1-girk-harcmanc/01.txt` and `02.txt` are cut the
  same way (no `։` without a space after it in
  either).

## ashkharhabar/grigor-tatevatsi/3-amaran-hator/

`01.txt` to `15.txt`: a translation into modern
Eastern Armenian of the same files in
`grabar/grigor-tatevatsi/3-amaran-hator/` (parts 1
to 15 of 24 of Ամառան հատոր: the sermons on Psalm
118:35 and on the Ten Commandments, Գլուխ Ա–Ե; on
visions and dreams, on Deuteronomy 15:9, on the Holy
Trinity and on the Lord's Prayer, Գլուխ Զ–ԺԱ; on
faith, hope, love, virtue, prudence and wisdom,
Գլուխ ԺԲ–Ի; on courage and work, sloth, sleep,
marriage and justice, Գլուխ ԻԱ–Լ; on wrongs, on
the sacraments of baptism, communion and
ordination, and on monks, Գլուխ ԼԱ–Խ; on
priests and confessors, on marriage and on sin,
Գլուխ ԽԱ–Ծ; on mortal and venial sin, sinful
thoughts, the tongue, slander, anger, patience
and laughter, Գլուխ ԾԱ–Կ; on pride and humility,
envy, greed, love of money, gluttony,
drunkenness, fornication, the yoke of the law
and idolatry, Գլուխ ԿԱ–Հ; on untimely death,
the evil day, affliction, chastisement and
repentance, Գլուխ ՀԱ–ՀԵ; on repentance, remorse
and confession, Գլուխ ՀԶ–Ձ; on prayer, the hours
of prayer, grace at table, the voice in prayer,
joy and sorrow, and fasting, Գլուխ ՁԱ–ՂԵ; on the
poor and on almsgiving, Գլուխ ՂԶ–Ճ; on the
consecration of a church, its door and its
people, and on the woman of Revelation 12,
Գլուխ ՃԱ–ՃԵ; on the woman on the scarlet beast,
on virgins and virginity, and on Saint Gregory
the Illuminator, Գլուխ ՃԶ–ՃԺ; on rulers, on the
rich and the poor, and on the deceit of
demons, Գլուխ ՃԺԱ–ՃԺԵ; on patriarchs and
leaders, on teachers and their counsel, and on
the young and the discipline of children,
Գլուխ ՃԺԶ–ՃԻ; on judges, on the twelve
apostles and the seventy-two disciples, on
Saint Bartholomew, and on the ark of the
covenant, Գլուխ ՃԻԱ–ՃԻԵ), made by Claude
(Anthropic's AI model) on 2026-11-06,
2026-11-07 and 2026-11-09 at the user's
request. It is a machine translation, not a
published or reviewed one: read it as a help to
the Grabar, not in its place.

## ashkharhabar/grigor-tatevatsi/2-dzmeran-hator/

`01.txt`: a translation into modern Eastern
Armenian of `grabar/grigor-tatevatsi/2-dzmeran-hator/01.txt`
(part 1 of 18 of Ձմեռան հատոր: the preface of the
1740 edition and praise of Grigor, the preludes to
the readings, and the sermons on the New Year, on
the Annunciation and on the Nativity, Գլուխ Ա–Զ),
made by Claude (Anthropic's AI model) on
2026-11-10 at the user's request, the same way as
the translation of Ամառան հատոր above. It is a
machine translation, not a published or reviewed
one: read it as a help to the Grabar, not in its
place.

## ashkharhabar/mkhitar-gosh/1-datastanagirk-a/

`01.txt`: a translation into modern Eastern
Armenian of `grabar/mkhitar-gosh/1-datastanagirk-a/01.txt`
(part 1 of 2 of Գիրք Դատաստանի, Ա խմբագրութիւն:
the preface in eleven chapters, with the colophon
of 1184, and laws Ա–ՃԷ: on judges, kings, monks,
teachers and priests, marriage and divorce,
children, serfs, finds, church property and
bishops, slaves, wounds, animals, theft, fire,
deposits, pledges, loans, sales and inheritance),
made by Claude (Anthropic's AI model) on
2026-11-11 at the user's request, the same way as
the translation of Ամառան հատոր above. It is a
machine translation, not a published or reviewed
one: read it as a help to the Grabar, not in its
place.

`02.txt`: the same for
`grabar/mkhitar-gosh/1-datastanagirk-a/02.txt`
(part 2 of 2, laws ՃԸ–ՄԾԱ: more laws from
Deuteronomy, on witnesses, lost things, pledges
and wages; the canons of the councils and of the
fathers on bishops, priests, marriage and
divorce, questions and answers; inheritance and
wills; kinship in marriage; the nine orders of
angels, of the church and of the Byzantine
palace; killing with and without intent,
physicians, craftsmen, herdsmen, millers, trade
and prices, boundaries and places of pilgrimage,
to the closing line of the book), made by Claude
on 2026-11-12 at the user's request, the same
way. With it the whole of redaction Ա is
translated. It is a machine translation too.

## ashkharhabar/mkhitar-gosh/2-datastanagirk-b/

`01.txt`: a translation into modern Eastern Armenian of
`grabar/mkhitar-gosh/2-datastanagirk-b/01.txt`
(part 1 of 2 of Գիրք Դատաստանի, Բ խմբագրութիւն:
the preface and the first part of the laws and canons,
through item 108 at the end), made by ChatGPT (GPT-6)
on 2026-11-12 at the user's request, following the
method recorded for Mkhitar Gosh's redaction Ա.
It is a machine translation, not a published or
human-reviewed text: read it as a help to the Grabar,
not in its place.

`02.txt`: a translation into modern Eastern Armenian of
`grabar/mkhitar-gosh/2-datastanagirk-b/02.txt`
(part 2 of 2, continuing with item 109 and ending at
item 130 and the colophon: the remaining canons,
the nine orders of angels, church and palace,
and secular laws on kingship, inheritance, property,
trade, labor, injury and homicide), made by ChatGPT
(GPT-6) on 2026-11-12 at the user's request, following
the same method. The source was split into 1,369
reader lines; there were no instances of `։` without
a following space. The translation is a machine
translation, not a published or human-reviewed text.

## ashkharhabar/grigor-tatevatsi/1-girk-harcmanc/

`01.txt`: a translation into modern Eastern Armenian of
`grabar/grigor-tatevatsi/1-girk-harcmanc/01.txt`
(part 1 of 12 of Գիրք հարցմանց, 2,865 lines), made
by ChatGPT (GPT-6) on 2026-11-12 at the user's
request. Passages that are uncertain or damaged in
the source are marked `*` (78 lines) for review.
It is a machine translation, not a published or
human-reviewed text: read it as a help to the Grabar,
not in its place.

`02.txt`: the same for part 2 of 12 (3,439 lines, the
Questions against the two-natures teachers, the
proofs from Scripture, and the third volume, on the
theology of Dionysius, as far as the angels),
made by Claude (Sonnet 5.5) on 2026-11-13 at the
user's request. Passages that are uncertain or
damaged in the source (the Digilib text has broken
words) are marked with a trailing `*` (63 lines).
Machine translation, not human-reviewed.

## All translations

- License: CC BY-SA 4.0 (see `CONTRIBUTING.md`).
  Who reviews each part, and how far, is in
  `TRANSLATIONS.tsv`; a part marked `review` or
  `reviewed` there is no longer only the machine
  translation described above.
- Reformed (Soviet) spelling, as written in Armenia
  today.
- The lines match the Grabar one for one: one
  Grabar sentence per line and its translation on the
  same line of the translated file, so the web reader shows the
  two side by side. Where the translation joins what
  the Grabar says in two sentences (mostly the words
  before a quotation, which the Grabar ends with
  `։`), it is cut at the same place, so some lines
  end in a comma or a `.`.
- Quotations keep the parentheses (Ամառան հատոր)
  or the «» (Ձմեռան հատոր) of the Grabar; the
  Datastanagirk has neither, and none are added.
  Slips and repeated passages in the Digilib text are
  translated as they stand, not corrected.

## grabar/nerses-shnorhali/

Seven works of Nerses Shnorhali (Ներսէս Շնորհալի,
1102–1173, Catholicos of the Armenians), from
Digilib, like the Tatevatsi works above (same
remarks on the source and license).

| Folder | Work | Digilib | Sections |
|--------|------|---------|---------:|
| `1-tught-yndhanrakan/` | Թուղթ ընդհանրական (General Epistle), prose | [299](https://www.digilib.am/book/299/) | 10 |
| `2-voghb-edesioy/` | Ողբ Եդեսիոյ (Lament on Edessa), verse | [301](https://www.digilib.am/book/301/) | 14 |
| `3-vipasanutyun/` | Վիպասանութիւն (a history in verse) | [300](https://www.digilib.am/book/300/) | 2 |
| `4-gandzer/` | Գանձեր, տաղեր, փոխեր (hymns) | [296](https://www.digilib.am/book/296/) | 14 |
| `5-tagher/` | Տաղեր (songs) | [298](https://www.digilib.am/book/298/) | 102 |
| `6-yaghags-yerkni/` | Յաղագս երկնի եւ զարդուց նորա (On the heavens), verse | [295](https://www.digilib.am/book/295/) | 1 |
| `7-hanelukner/` | Հանելուկներ (riddles), verse | [297](https://www.digilib.am/book/297/) | 1 |

Downloaded on 2026-11-07 with
`scripts/fetch-digilib.py`, made the same way as
the Tatevatsi works:

```sh
D=books/grabar/nerses-shnorhali
scripts/fetch-digilib.py 299 "Թուղթ ընդհանրական" $D/1-tught-yndhanrakan
scripts/fetch-digilib.py 301 "Ողբ Եդեսիոյ" $D/2-voghb-edesioy
scripts/fetch-digilib.py 300 "Վիպասանութիւն" $D/3-vipasanutyun
scripts/fetch-digilib.py 296 "Գանձեր, տաղեր, փոխեր" $D/4-gandzer
scripts/fetch-digilib.py 298 "Տաղեր" $D/5-tagher
scripts/fetch-digilib.py 295 "Յաղագս երկնի եւ զարդուց նորա" $D/6-yaghags-yerkni
scripts/fetch-digilib.py 297 "Հանելուկներ" $D/7-hanelukner
```

Notes:

- Each work is small enough for one part (`01.txt`).
- The headings are Digilib's section numbers
  (`[Ա]`, `[1]`, …). In `4-gandzer/` they start at
  `[ՃԳ]`, as on Digilib, and one section is only a
  group heading (`- ՀԱՎԵԼՎԱԾՆԵՐ ՏԱՂԵՐ ՓՈԽԵՐ`) with
  no text of its own.
- The poems have one verse per line; the General
  Epistle has long paragraphs, like Tatevatsi.
- Digilib writes `:` for the Armenian full stop `։`
  and `'` for the stress mark `՛` here; they are kept
  as on Digilib (the reader counts `:` as a sentence
  end too).
- The riddles (`7-hanelukner/`) are not Grabar but
  Middle Armenian, the language of the 12th–13th
  centuries (`զետ` "like", `ու` "and", `կու`,
  `հանց`, verbs such as `դառնա`, `կարդա`). They are
  kept here with the other works under his name.

## grabar/mkhitar-gosh/

The law book of Mkhitar Gosh (Մխիթար Գոշ, about
1130–1213), Գիրք Դատաստանի (Datastanagirk), from
Digilib, like the Tatevatsi works above (same
remarks on the source and license). Digilib has it
in three redactions (խմբագրութիւն), each a book of
its own; they are the same work, worded and
numbered differently. These are Gosh's only books
on Digilib (his fables are not there).

| Folder | Work | Digilib | Sections | Parts |
|--------|------|---------|---------:|------:|
| `1-datastanagirk-a/` | Գիրք Դատաստանի, Ա խմբ. | [277](https://www.digilib.am/book/277/) | 264 | 2 |
| `2-datastanagirk-b/` | Գիրք Դատաստանի, Բ խմբ. | [278](https://www.digilib.am/book/278/) | 268 | 2 |
| `3-datastanagirk-c/` | Գիրք Դատաստանի, Գ խմբ. | [279](https://www.digilib.am/book/279/) | 263 | 2 |

Downloaded on 2026-11-11 with
`scripts/fetch-digilib.py`, made the same way as
the Tatevatsi works:

```sh
D=books/grabar/mkhitar-gosh
scripts/fetch-digilib.py 277 "Գիրք Դատաստանի, Ա խմբագրութիւն" $D/1-datastanagirk-a
scripts/fetch-digilib.py 278 "Գիրք Դատաստանի, Բ խմբագրութիւն" $D/2-datastanagirk-b
scripts/fetch-digilib.py 279 "Գիրք Դատաստանի, Գ խմբագրութիւն" $D/3-datastanagirk-c
```

Notes:

- The headings are Digilib's section numbers
  (`[Ա]`, `[Բ]`, …); the title of each law
  (`ՅԱՂԱԳՍ ԴԱՏԱՍՏԱՆԱՑ …`, in Գ `ԳԼՈՒԽ … ՎԱՍՆ …`)
  is the first line under it. The numbers start
  again where the laws begin, after the preface.
- 2 sections in Ա, 3 in Բ and 2 in Գ are only
  headings (the title or `Նախադրութիւն`, and the
  start of the laws) with no text of their own.
- Բ numbers the laws in the text as well
  (`1. «…`), and puts them in «».
- `1-datastanagirk-a/01.txt` and `02.txt`, and
  `2-datastanagirk-b/01.txt` and `02.txt`, are cut
  into reader lines, like the Tatevatsi parts above,
  to be read beside their translations in
  `ashkharhabar/` (no `։` without a following space
  in any of these files).

## grabar/grigor-narekatsi/

The Book of Lamentations of Grigor Narekatsi
(Գրիգոր Նարեկացի, about 951–1003), Մատեան
ողբերգութեան, from Digilib, like the Tatevatsi
works above (same remarks on the source and
license).

| Folder | Work | Digilib | Sections | Parts |
|--------|------|---------|---------:|------:|
| `1-matean-voghbergutyan/` | Մատեան ողբերգութեան (Book of Lamentations), verse | [178](https://www.digilib.am/book/178/) | 96 | 3 |

Downloaded on 2026-11-11 with
`scripts/fetch-digilib.py`, made the same way as
the Tatevatsi works:

```sh
D=books/grabar/grigor-narekatsi
scripts/fetch-digilib.py 178 "Մատեան ողբերգութեան" $D/1-matean-voghbergutyan
```

Notes:

- The 95 chapters (Բան) have Digilib's numbers as
  headings, `[Ա]` to `[ՂԵ]`, after one group
  heading (`- ԲԱՆ`) with no text of its own. Each
  chapter starts with its title (`Ի ԽՈՐՈՑ ՍՐՏԻՑ
  ԽԱՒՍՔ ԸՆԴ ԱՍՏՈՒԾՈՅ`) and the numbers of its
  parts (`Ա`, `Բ`, …) stand on lines of their own.
- One verse per line.
- Digilib writes `~` for the exclamation mark `՜`,
  mostly inside a word (`Ձա~յն`), where the reader
  would cut the word in two; all 121 were replaced
  with `՜`. Otherwise the text is as on Digilib:
  `:` for `։`, `` ` `` for `՝` and `'` for the
  stress mark `՛`, as in the Shnorhali works.

## grabar/anania-shirakatsi/

Nineteen works of Anania Shirakatsi (Անանիա Շիրակացի,
c. 610–685) in Grabar, from Digilib
(<https://www.digilib.am>): the texts are centuries
old and in the public domain; Digilib states no
license for its typed copies.

| Folder | Work | Digilib |
|--------|------|---------|
| `1-zatki-char/` | Զատկի ճառ | [81](https://www.digilib.am/book/81/) |
| `2-ampoc-nshanac/` | Յաղագս ամպոց եւ նշանաց | [60](https://www.digilib.am/book/60/) |
| `3-i-yaytnutyun/` | Ի յայտնութիւն Տեառն եւ Փրկչին մերոյ | [64](https://www.digilib.am/book/64/) |
| `4-yishatakaran/` | Յիշատակարան | [66](https://www.digilib.am/book/66/) |
| `5-harcman-lucman/` | Յաղագս հարցման եւ լուծման | [67](https://www.digilib.am/book/67/) |
| `6-kenac-iuroc/` | Վասն որպիսութեան կենաց իւրոց | [68](https://www.digilib.am/book/68/) |
| `7-khrakhchanakank/` | Խրախճանականք | [70](https://www.digilib.am/book/70/) |
| `8-mghonachapk/` | Մղոնաչափք եւ Օդաչափք | [74](https://www.digilib.am/book/74/) |
| `9-patmutyun/` | Պատմութիւն | [75](https://www.digilib.am/book/75/) |
| `10-bacayaytutyan-tvoc/` | Սակս բացայայտութեան թուոց | [76](https://www.digilib.am/book/76/) |
| `11-shrjagayutyan-erknic/` | Յաղագս շրջագայութեան երկնից | [79](https://www.digilib.am/book/79/) |
| `12-tomarakan-patarik/` | Տոմարական պատառիկ | [80](https://www.digilib.am/book/80/) |
| `13-akanc-patuakanac/` | Յաղագս ականց պատուականաց | [59](https://www.digilib.am/book/59/) |
| `14-shaghkaputyan/` | Յաղագս շաղկապութեան արեգական եւ լուսնի | [61](https://www.digilib.am/book/61/) |
| `15-ashkharhacuyc/` | Աշխարհացոյց | [62](https://www.digilib.am/book/62/) |
| `16-yapoc-chapuc/` | Յաղագս յափոց, չափուց եւ պատարաց | [63](https://www.digilib.am/book/63/) |
| `17-kendanatesakac/` | Յաղագս կենդանատեսակաց | [69](https://www.digilib.am/book/69/) |
| `18-kshroy-kshroc/` | Յաղագս կշռոյ, կշռոց եւ կշռորդաց | [72](https://www.digilib.am/book/72/) |
| `19-orchaputyun-sheki/` | Որչափութիւն շեկի | [77](https://www.digilib.am/book/77/) |

Downloaded on 2026-11-13 with
`scripts/fetch-digilib.py` (`ID TITLE OUT`), each
work as one part; made as for Grigor Tatevatsi above.
`1`–`12` are the books Digilib's list marks `grabar`;
`13`–`19` are marked `unclear` or `modern` there, and
were taken after the user read a sentence of each
and judged them Grabar (many are lists of numbers
and measures). Not taken: 58 and 65 (tables of
letter-numerals), 73 and 78 (no typed text).
