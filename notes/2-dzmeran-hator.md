# Ձմեռան հատոր: notes on the parts

Working notes gathered while translating Grigor
Tatevatsi's winter volume (Գիրք քարոզութեան որ կոչի
Ձմեռան հատոր) into modern Eastern Armenian, the same
way as Ամառան հատոր (`notes/3-amaran-hator.md`). Not
on the shelf and not on the Pages site.

Files: `books/grabar/grigor-tatevatsi/2-dzmeran-hator/`
and the translation at the same path under
`books/ashkharhabar/`. Line numbers are the same in
both. The parts are Digilib's (18 of them, cut by
size between sections); there are no `ԳԼՈՒԽ` group
lines. A sermon's heading is one line: `Գլուխ X.`
(or `Գլուխ. X.`), the title and often the verse; one
sermon (part 1, Բ) is headed `Քարոզ. Բ.` instead.

The sermons follow the church year from the New
Year and the feasts of the Nativity; they are built
like the summer ones: an opening, numbered heads
(առաջին, երկրորդ, ...), questions (հարցումն) and
answers, and a closing doxology.

## How to do the next part

Part 1 is done. To do part N (2 next), follow
"How to do the next part" in
`notes/3-amaran-hator.md`, with these changes:

- the file is `2-dzmeran-hator/NN.txt`;
- the title line is «Քարոզգիրք, որ կոչվում է
  Ձմեռան հատոր · N/18»;
- headings: `Գլուխ X.` / `Գլուխ. X.` become
  `Գլուխ X.`, `Քարոզ. X.` becomes `Քարոզ X.`; keep
  the number right after `Գլուխ` or `Քարոզ`, so the
  Contents finds the sermon (`CHAPTER_RE` and
  `SERMON_RE` in `nxgir_reader.py`);
- quotations: the Grabar uses «» here; keep the
  same number of « and » on each line, closed or
  not;
- at the end, add a "Part N" section here.

## Part 1 · Գլուխ Ա-Զ (sermons 1–6)

- Lines 3–60: the preface of the 1740 Constantinople
  edition (Թվին ՌՃՁԹ), by Catholicos Ghazar, at the
  request of Mahtesi Shahnazar of Ghapan: gifts of
  knowledge, the teachers of the Church; Grigor's
  praise (his works: the Winter and Summer volumes,
  the Book of Questions; the "fourth illuminator"
  after Gregory, Mesrop and Odznetsi; his mother's
  dream of the Illuminator's lamp; pupil of
  Hovhannes Vorotnetsi; a long list of his titles
  and of his gifts of soul and body).
- Line 92: «Նախերգանք», preludes to the readings:
  set phrases that introduce Moses, David, Solomon,
  Job, Isaiah and Paul.
- Առաջին (line 130): the New Year, Ps 80:4 «Փող
  հարէք ի գլուխս ամսոց». The bell and the
  semantron (Noah's ark, Moses' trumpets, battle,
  the last trumpet; three strokes at night); ten
  meanings of the New Year; why it is in winter;
  the Armenian month names (Hayk's children) and
  their meanings; year, month, week (the seven
  planets), leap day, the epact, the 19-year cycle;
  Christ as the "year" (Luke 4:19), ten reasons.
- Բ (line 386): «Քարոզ. Բ.» headed as by Hovhannes
  Vorotnetsi; Luke 1:26 "in the sixth month". The
  date of the Annunciation against the "heretics";
  why an angel was sent; ten honours of the
  greeting; five kinds of greeting; Mary's four
  answers; four kinds of holiness; Mary above all
  virgins and angels.
- Գ (line 497): the Annunciation, Ps 71:6 «Իջցէ
  որպէս զանձրեւ ի վերայ գեղման». Gideon's fleece;
  Moses' "rain on the grass" (Deut 32:2); ten
  properties of rain; Mary as fleece, earth, grass;
  rain, dew and shower (preaching, grace,
  chastisement); thirty-, sixty- and hundredfold.
- Դ (line 698): the Nativity, Ps 106:20 «Առաքեաց
  զբան իւր եւ բժշկեաց զնոսա». Ten ways the Son is
  "Word"; why God became man; why the Son and not
  the Father or the Spirit; why at that time (the
  six ages; the sign of the cross); the six
  salvations (from sin, the curses, Satan, death,
  hell, idolatry).
- Ե (line 921): the Nativity, Ps 2:7. Why the
  Nativity heads all feasts; why the Annunciation
  is remembered on 5 January; why it starts at
  night; the nine days, the eve without liturgy,
  the names ճրագալոյց / ճրագալոյծ / ճրագալոյս;
  why 6 January; the shepherds, the cave (Eve's
  relics buried there by Shem); the twelve
  readings and Daniel's three youths.
- Զ (line 1132): the Nativity, John 1:14. Ten
  likenesses of the Word made flesh to a written
  word; ten reasons for the incarnation; four
  heresies (the Word changed, Apollinaris, a
  heavenly body, Marcellus and Photinus); why
  "flesh" and not "soul" (the forty-day body at
  once); without flesh, against the flesh, for the
  flesh; Bethlehem, the cave, the swaddling clothes
  and the manger; why at the end of the law, after
  the kings, in winter and at night.

## Notes on the text

- Part 1 line 81: the Illuminator's words in the
  dream have no quotation marks; kept so. Many
  lines open a quotation closed on a later line or
  not at all, or close one opened earlier (32, 36,
  50, 191, 196, 208, 229, 380, 525/526, 559, 670,
  736/737, 779, 870, 880/881, 1009, 1045, 1132,
  1309, 1314/1315, 1323); the marks are kept as in
  the Grabar.
- Part 1 line 109: the prelude to Job is headed
  «Նպատակն համբերութեան երանելին Յիսուս Քրիստոս»;
  kept.
- Part 1 line 251 reads «ի ձեռն» where «ի ձմեռն»
  (in winter) is meant; translated so.
- Part 1 line 313 (the 19-year cycle) is garbled
  («ՑՊ խ. ամացն»); translated as it stands.
- Part 1 line 380 reads «անօրէնութիւն» for
  «տնօրէնութիւն» (economy); translated so.
- Part 1 lines 461 and 462 both say "perfect
  obedience"; kept.
- Part 1 lines 586–589 repeat themselves in a
  garbled way; lines 617–619 give «Չորրորդ»
  twice; kept. Line 625 «խաղալից» is read as
  «խաղաղալից».
- Part 1 line 782 reads «ծնաւ եւ Աստուծոյ ի
  յԱդամայ»: Eve, born from Adam, is meant;
  translated so.
- Part 1 lines 949 and 1062 repeat «Երկրորդ» for
  the third; line 1089 has «երրորդ» for the
  second birth; line 1342 repeats «վարդապետք թէ»;
  kept.
- Part 1 line 1027 «ԳԳ ժամ» is unclear; kept.
  Line 1047 «մեծի աւետարանիչ» is translated "the
  forerunner of the great gospel".
- Part 1 lines 1088 and 1330 garble «զի
  աստուածածնաւն ողջասցի եւ Աստուծոյ»; translated
  by the sense (Eve healed through the God-bearer
  and through God).
