# Սմբատ Սպարապետ, Տարեգիրք: notes

Working notes on the text of the chronicle; not on
the shelf and not on the Pages site. The source and
how the text was made are in `books/SOURCES.md`.

## Hard readings

Words whose letters were hard to make out in the
scan (over-inked or faint print, a dark gutter);
the reading in the text is the best guess. Page is
the printed page of the 1859 edition, place is
part:line in `books/grabar/smbat-sparapet/2-taregirk/`.
Check them against another copy of the edition or
against Digilib's (Venice 1956) text when it is
back.

Digilib's text is now in
`books/grabar/smbat-sparapet/3-taregirk-digilib/`
(2026-11-19). It is a different, longer recension, so
only 4 of the readings below appear in it as words;
a few near misses may be reading errors of the scan
(`զբահն` for `զրահն`, `եղարկ` for `եզարկ`,
`ըմբռովն` for `ըռմբովն`, `սրաիւ` for `սրտիւ`). They
are hints for a review of the page image, not
corrections.

| Page | Place | Reading |
|-----:|------|---------|
| 30 | 1:78 | `ըմբռովն` |
| 30 | 1:78 | `եղարկ` |
| 31 | 1:85 | `զբահն` |
| 37 | 1:132 | `սարատեղատու-` |
| 43 | 1:187 | `առայօք` |
| 46 | 1:213 | `այլոյէս` |
| 46 | 1:214 | `զպարիսպսն` |
| 47 | 1:232 | `յՄնտնոր` |
| 47 | 1:232 | `հօրէն` |
| 50 | 1:258 | `զգետիքս` |
| 74 | 1:479 | `ակար` |
| 84 | 2:16 | `արեգայի` |
| 90 | 2:84 | `լըլա-` |
| 97 | 2:149 | `քէնել` |
| 102 | 2:204 | `անգամդաղ` |
| 103 | 2:212 | `նեքքին` |
| 103 | 2:213 | `կռուով` |
| 103 | 2:213 | `սղարեաց` |
| 107 | 2:265 | `զընտան` |
| 107 | 2:268 | `աղէկնդեալք` |
| 113 | 2:375 | `սխրալս` |
| 114 | 2:381 | `հաղաւ` |
| 114 | 2:381 | `միակեցնակ` |
| 114 | 2:386 | `սրաիւ` |
| 115 | 2:388 | `զօթխնոտի` |
| 115 | 2:388 | `զկլաս` |
| 115 | 2:388 | `զօտւոյ` |
| 116 | 2:397 | `զընտան` |
| 117 | 2:412 | `ծախեց` |
| 118 | 2:416 | `Իզլոր` |
| 118 | 2:418 | `անեցի` |
| 118 | 2:418 | `զԱտըլ` |
| 118 | 2:418 | `զՕքսեն` |
| 118 | 2:422 | `զԽառակիսայ` |
| 118 | 2:422 | `զերծ` |
| 118 | 2:424 | `հայրապետական` |
| 119 | 2:427 | `չհանդերձ` |
| 119 | 2:430 | `զանկը` |
| 119 | 2:430 | `չեղնէր` |
| 119 | 2:434 | `մէկեց` |
| 119 | 2:434 | `զուլտանայքն` |
| 119 | 2:434 | `Մսրայ` |
| 119 | 2:434 | `Անթափաց` |
| 120 | 2:437 | `Տարպայեանի` |
| 121 | 2:443 | `թաղտիրմե-` |
| 126 | 2:508 | `զպարկուտաղունք` |
| 129 | 2:552 | `զայն` |
| 134 | 2:621 | `ափխոսկ` |
| 141 | 2:818 | `չիչ` |
| 141 | 2:818 | `դեղղիր` |
| 23 | 1:26 | `զօրու ծանու` (a line end with a hyphen before `յարուցեալ`) |

## Other notes

- The year entries are the Contents (☰) of each
  part: `year_entries()` in `nxgir_reader.py`.
- The edition's own misprints are kept: `Ի թուին
  841` (for 741, part 2), `Եւ ի թուին 620` (for
  720), the entry for 769 written twice.
- Pages 142–181 of the edition (the editor's notes
  and the readings of the Moscow 1856 edition) are
  not copied; the note numbers are left out of the
  text.

## The translation

Both parts were translated into modern Eastern
Armenian on 2026-11-16, by `TRANSLATION_GUIDE.md`,
in chunks of 20–60 lines, each checked against the
Grabar (section 6 of the guide), and the whole
checked at the end: 562 and 820 lines, all blank
lines the same, 34 and 82 Contents entries the
same as the Grabar's. Files:
`books/ashkharhabar/smbat-sparapet/2-taregirk/`,
line numbers the same as the Grabar's. Status
`machine` in `books/TRANSLATIONS.tsv`.

### What each part covers

- Part 1, lines 1–100: Gagik I and his sons
  Hovhannes and Ashot; Nikephoros Phokas, his murder
  by John Tzimiskes; Vasak Pahlavuni at Bjni;
  Tzimiskes' war in Syria.
- 101–250: Tzimiskes' letter to Ashot (109–123);
  Basil II, Abulgharib and King Gurgen, David
  curopalates, Senekerim gives Vaspurakan to Basil
  (210–217), the Easter dispute and vardapet Samuel.
- 251–420: Basil's death; Romanos III, Michael IV,
  Maniakes at Edessa; the end of Gagik II's kingdom
  (362–383); Arts'n taken (400–407); Catholicos
  Petros in Constantinople; the fire at Antioch.
- 421–562: the siege of Manzikert and the Frank who
  burns the catapult (431–448); Doukas; Alp Arslan
  takes Ani (492–501); Gagik II, Catholicos Khachik,
  the dispute with Doukas (523–537); Mark of
  Caesarea and his dog (543–556); the sign at Pizu.
- Part 2, lines 1–135: Romanos Diogenes; Gagik II
  killed at Kyzistra (32–45), Toros avenges him
  (65–86); the Rubenids: Constantine, Toros, Levon I.
- 136–300: Toros II, Mleh, Ruben III, Levon II
  crowned king (291); Smbat names himself (298, 403).
- 301–366: the bishops and lords at the coronation.
- 367–480: Levon's reign, Lambron, Catholicos
  Hovhannes, Kayqawus, the regency of Constantine,
  Philip, Hetum I, the sieges of Tarsus (Smbat's own
  account, 463–476).
- 481–583: the continuators: Levon III, Hetum II,
  Oshin, Levon IV, Egypt's raids, up to 780.
- 585–811: the lists: the sees of Antioch and the
  four patriarchates (585–636); the princes and kings
  of Cilicia (638–660), constables and marshals; the
  Roman and Byzantine emperors (683–779); the
  patriarchs of Constantinople; the eras.
- 813–820: two last entries (772, 775: a blind man
  healed).

### Decisions

- The title line stays «Սմբատ Սպարապետ, Տարեգիրք
  · N/2»; the heading line is in capitals.
- Each year entry starts with its year, in the
  forms `413 թվականին`, `Իսկ 413 թվականին`, `Եվ
  Հայոց 491 թվականին`, `Դարձյալ՝ 470 թվականին`, so
  that `year_entries()` (`YEAR_RE`, which now reads
  these too) gives the same Contents. An entry the
  Grabar does not start with its year (`Ի սորա
  աւուրս, ի թուին 484`, `Ի սոյն թիւ 555`) does not
  start with it in the translation either.
- The «» of the Grabar are kept, the one `»` with
  no `«` too (1:438); none are added. The editor's
  additions in brackets, `(Աշոտոյ)`, are translated
  and kept in brackets.
- Names: Հույներ, Հոռոմներ (where the text says
  Հոռոմ), Տաճիկներ, Թուրք, Թաթար, Մուղալ, Ֆրանկներ
  as in the text; `կուրտ` and `կրտեր` are
  ներքինի (eunuchs; 1:25 too); `Տուկիծ` is Դուկիծ
  (Doukas); titles kept: պարոն, պայլ, գունդստապլ,
  մարաջախտ, սեբաստոս, ծավիզ, կատապան, դուքս,
  պրինց (`բրինձ`), լեգատ (`Լեկաթ`), կոմս (`Գունդ`).
- The misprints are kept: `841` (2:508), `620`
  (2:494); the year 769 twice (2:544, 546); `յետ
  ութ ամաց` (2:573) is eight years, as written.

### Unclear words (part:line)

Guessed from the sense, or kept in Armenian letters
when nothing could be found; the reviewer is to check
these first. Many are also hard readings of the scan
(the table above).

- 1:37 `ընդագոյն`: the sword tied so it could not
  be drawn (guess).
- 1:49 `երկրորդ Աբուսահլին`: «Աբուսահլի երկրորդը»,
  literal; perhaps his second in rank.
- 1:57 `եկից զամենեսին ի դեսն`: «բոլորին դաշտում
  թողեց», a guess.
- 1:105 `շաղաշարեալ էր մեղօք`: «մեղքերով
  շաղկապված էր (նրա հետ)», a guess.
- 1:192 `պատճենիցն`: «պատճենների», literal; the
  sense of the sentence is not clear.
- 1:198 `խոյլիկ`: a disease, kept.
- 1:232 `Մնտնոր`, `Պաղածհակ`: kept as names.
- 1:258 `զգետիքս`: «գետնի տակ», a guess.
- 1:290 `սպարիւ`: «վահանով», a guess.
- 1:293 `բազումքն`: read as Բազմաստղ (the
  Pleiades).
- 1:448 `զերբորդն`: kept («երբորդին»), not found.
- 1:474 `խայտակոտոր`: «ջարդված բեկորներ», a guess.
- 1:480 `զէտ զընտանեաց`: «ասես ընտանիներ», the
  sense unclear.
- 1:528 `պայխուն (պատասխանի)`: «պատասխաններ».
- 2:16 `արեգայի`: kept («արեգայի հանդերձ»).
- 2:84 `լըլա-խառն`: read as «լացախառն».
- 2:146 `պռոյգ`: «օժիտ» (a dowry).
- 2:149 `ի բեանք ... քէնել`: «իրենք ... վրեժ
  լուծել», a guess.
- 2:164 `ի կումզէ`: kept («կումզե»).
- 2:174 `քշփեց`: «հանդիմանեց», a guess.
- 2:189 `ջամբռ`: «գանձարան».
- 2:204 `անգամդաղ`: «անհապաղ», a guess.
- 2:212 `նեքքին`: read as ներքինի.
- 2:213 `սղարեաց`: «պաշարեց».
- 2:374 `արջիկս`: kept («արջիկների»).
- 2:375 `սխրալս`: kept («սխրալի»).
- 2:381 `հաղաւ ... միակեցնակ`: «միայնակ մնաց».
- 2:388 `զօթխնոտի զկլաս`: kept.
- 2:412 `սղարեն ... ծախեց`: «սղարը ... ետ վաճառել
  էր», a guess.
- 2:415 `գարմնին`: kept; the whole sentence is
  unclear.
- 2:418 `անեցի`: kept («նրա անեցին»).
- 2:422: the whole sentence is garbled; read as
  Levon ransoming his lords for Lulva, Kharakis and
  Lozav.
- 2:424 `հայրապետական`: «հայրապետական (պահապան)»,
  the sense unclear.
- 2:427 `չհանդերձ`: «չմնաց», a guess.
- 2:430 `զանկը ... ժամնի`: the sentence is a guess.
- 2:434 `մէկեց`: «միացրեց»; `Անթափաց`: Այնթապ.
- 2:437 `Տարպայեանի`: kept; `ըծեց`: «վերցրեց».
- 2:443 `թաղտիրմեցան`: «խորհրդակցեցին» (Persian
  tadbir), as `թաղտուիցէք` (442) and `թաղտիրմով`
  (446).
- 2:508 `պարկուտաղունք`: kept.
- 2:545 `շինր`: kept.
- 2:569 `ըզպամլին խայտնին չէն`: «պամլին ու խայտնին՝
  անվնաս», a guess.
- 2:615 `կնքեռն`: kept.
- 2:621 `ափխոսկ`: kept.
- 2:818 `չիչ`, `դեղղիր`: kept.

## The translation of the Digilib text

Both parts of `3-taregirk-digilib/` were translated into
modern Eastern Armenian on 2026-11-20, by
`TRANSLATION_GUIDE.md`, in chunks of 80–110 lines, each
checked against the Grabar (section 6 of the guide), and
the whole checked at the end: 1,041 and 1,056 lines, all
blank lines the same, no locked line changed, 83 and 173
Contents entries the same as the Grabar's. Files:
`books/ashkharhabar/smbat-sparapet/3-taregirk-digilib/`,
line numbers the same as the Grabar's. Status `machine`
in `books/TRANSLATIONS.tsv`.

The Grabar was first cut one sentence to a line with the
script of `notes/3-amaran-hator.md` (only line breaks
changed; one place in part 1 had `։` with no space after
it, none in part 2). Digilib's paragraphs became 1,041 and
1,056 lines.

### What each part covers

- Part 1, lines 1–141: Gagik I (400–420), the coronation
  at Ani, Nikephoros Phokas and his murder by Tzimiskes
  (39–46), the quarrel of Hovhannes and Ashot (52–75),
  Vasak Pahlavuni at Bjni (77–89), Tzimiskes' campaign
  and his letter to Ashot (101–141).
- 143–260: Abulgharib and the fall of King Gurgen's army
  (145–155), Catholicos Stepanos, David curopalates
  (166–173), Basil II and the Bulgarians, the Easter
  dispute and vardapet Samuel (207–218), Senekerim gives
  Vaspurakan to Basil (231–243), Basil at Trebizond and
  the miracle of the water (251–259).
- 261–412: Romanos III and Maniakes at Edessa
  (301–306), Catholicos Petros and Dioskoros (326–335),
  Abusuar's defeat at Gandzak (346–354), the death of
  King Hovhannes (363), Gagik II crowned (369), his
  summons to Constantinople and the end of the Bagratid
  kingdom (395–412).
- 414–520: the earthquake of 494, Arts'n taken (428–434),
  Petros at Constantinople, Liparit, Tughril at Manzikert
  and the Frank who burns the catapult (479–496).
- 521–640: famine and the Seljuk raids, Ani sacked by
  Alp Arslan (555–564), Gagik and Mark's dog Armen
  (606–618), the colophon-like entry on Catholicos
  Grigor Vkayasēr (579–582).
- 641–760: Romanos Diogenes and Manzikert (642–697),
  Philaretos and Tornik of Sasun (707–725), Grigor
  Vkayasēr in Egypt (729–731), the murder of Gagik II
  (759–764), Vasak killed at Antioch (739–740).
- 761–945: Suleiman and Antioch (782–788), Malik-Shah
  (806–817), the First Crusade and the Holy Lance
  (867–914), Jerusalem taken (916–921), Edessa and the
  Counts.
- 946–1041: Baldwin and Joscelin at Edessa, the Holy
  Fire that did not light (950–952), Sanjil and Alexios'
  betrayal (956–962), Bohemond's captivity and ransom
  (979), Gogh Vasil of Kesun (981–982, 1010), the Armenian
  bishops and Catholicoi.
- Part 2, lines 1–200: Joscelin and Baldwin, the siege of
  Edessa by Mawdud, Toros takes the fortress of the
  Mantaleh brothers and avenges Gagik II (22–34), Roger
  of Antioch, Baldwin II's captivities (133–142).
- 201–400: Levon I the Rubenid, Toros II and Mleh, the
  Armenian princes and the Crusaders; Nerses Shnorhali's
  lament for Edessa (252), the Armenian kings and
  Catholicoi.
- 401–700: Ruben III and Levon II, Saladin and Hattin
  (468–495), the coronation of Levon (569–572), the lists
  of archbishops, bishops and lords (574–692).
- 701–1056: the coup against Philip, Hetum I, the sieges
  of Tarsus (Smbat's own account, 836–863 in the plain
  language of his day), the Mongols, Hetum's journey to
  Mangu, Baybars at Antioch (1016), the death of Hetum
  (1032), Levon III; the colophons of Simeon of Aparan
  (829–834) and Catholicos Grigor, 1558 (1054–1056).

### Decisions

- The year headings (a bare number, `ՈԿԸ [668=1219]` at
  the start of an entry) are kept as they are; the
  Contents are the same as the Grabar's.
- Digilib's page marks inside the text (`/12ա/`: 354 of
  them) are not part of the sentences and are left out
  of the translation. The editor's brackets are kept
  where the Grabar has them, the words translated
  (`[Աշոտոյ]` → `[Աշոտը]`; `[30. 000]` → `[30 000]`).
- The `«` of the Grabar (9, all in part 1) have no
  closing mark in the source (`»` was read as `ե`: `քոե։`);
  most speech has none at all. The translation adds no
  marks: a speech follows a colon and runs to the end of
  the sentence. Where the Grabar has a `«`, the translation
  has it too.
- Names are in the reformed forms of the text, not
  corrected: Չմշկիկ (Tzimiskes), Դուկիծ (Doukas),
  Տիոժեն → Դիոգենես (Romanos Diogenes), Սալահատին, Ֆռանգ →
  ֆրանկ, Տաճիկ and Թուրք as in the text, Հոռոմ kept in
  `Հոռոմկլա`; titles: պարոն, պայլ, գունդստաբլ, սեբաստոս,
  կուրապաղատ, մարաջախտ, մայստոր, ֆրեր, ջամբռլայն, բրինձ
  (prince), կոմս, դուքս, ամիրա, սուլթան, խան; `բաբան` (a
  siege engine) and `խանդակ` (a ditch) as in the first
  text. `դահեկան` is kept.
- `ՅԻՇԱՏԱԿԱՐԱՆ` (the colophon headings, 1:447, 2:829,
  2:1054) is `ՀԻՇԱՏԱԿԱՐԱՆ`, in capitals as in the Grabar.
- The lists of the bishops and lords (2:574–692) were
  `Իշխ. Լամբրունին Հեթում։`; in the translation each is
  `Լամբրոնի իշխան՝ Հեթումը։`, the abbreviations
  `եպ.`, `Իշխ.`, `պր.` written in full.

### Unclear words (part:line)

Guessed from the sense, or kept in Armenian letters when
nothing could be found; the reviewer is to check these first.

- 1:236 `թիմաբերդս`: «ամրոց», a guess.
- 1:720 `հանապ ետ շինել` (Philaretos and the head of
  Tornik): read as a cup, «գավաթ շինել տվեց».
- 1:786 `Պելետիկք`: kept as a name of the Antiochenes.
- 2:314 `.....`: the lacuna of the Grabar, kept.
- 2:781 `Իտ[ ]եմ[ ]ն`: kept with its gaps.
- 2:780 `սրսլայիւ`: kept («սրսլայով»).
- 2:855 `ջրմտին դեհն ու ի ջրելին աղէկ նետընկէց մի`:
  a guess.
- 2:857 `քովս քովս`: «կողքս-կողքս», a guess.
- 2:869 `ֆսուս`: kept; the sense of the game is unclear.
- 2:1056 `տառայպանք`, `բարիշան`, `Հոտքար`, `Դայմազ`,
  `Ոստան`: kept as in the colophon.
