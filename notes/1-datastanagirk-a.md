# Դատաստանագիրք, Ա խմբ.: notes on the parts

Working notes gathered while translating Mkhitar
Gosh's law book (Գիրք Դատաստանի, redaction Ա) into
modern Eastern Armenian, the same way as Ամառան
հատոր (`notes/3-amaran-hator.md`). Not on the shelf
and not on the Pages site.

Files: `books/grabar/mkhitar-gosh/1-datastanagirk-a/`
and the translation at the same path under
`books/ashkharhabar/`. Line numbers are the same in
both. The book has two parts (Digilib's, cut by
size between sections). Each section starts with
Digilib's number on a line of its own (`[Ա]`),
then its title in capitals, then the text. The
numbers start again at `[Ա]` where the laws begin
(line 517 of part 1), after the preface.

How the laws are built: a law from the Torah is
often quoted first (Exodus, Leviticus, Numbers,
Deuteronomy), then Gosh's comment: how it is to be
kept "now", among Christians, often with a ransom
(փրկանք) or fine (տուգանք) in place of death, and
penance left to the canons. Others are his own,
from custom, from the canons of the apostles and
from the laws of other Christian peoples.

## How to do the next part

Part 1 is done. To do part 2, follow "How to do
the next part" in `notes/3-amaran-hator.md`, with
these changes:

- the file is `1-datastanagirk-a/02.txt`;
- the title line is «Դատաստանագիրք, Ա
  խմբագրություն · 2/2»;
- the `[Ա]` lines and `ԳԼՈՒԽ Ա` stay exactly as in
  the Grabar (the Contents finds a section by its
  `[Ա]` line, `SECTION_RE` in `nxgir_reader.py`);
  the title under it is translated, in capitals,
  "ԴԱՏԱՍՏԱՆՆԵՐԻ ՄԱՍԻՆ" for «ՅԱՂԱԳՍ ԴԱՏԱՍՏԱՆԱՑ»;
- the Grabar has no «» or parentheses for
  quotations: add none; its few `[…]` editorial
  insertions are kept;
- terms kept as they are: `դահեկան`, `դանգ`,
  `թասու`, `գարի` (money and its parts, law ՃԴ),
  `սիկղ`, `երկդրամյան`, `չեքչեք`; `որոշվել` for
  being cut off from the church, `լուծվել` for a
  cleric losing his rank;
- at the end, add a "Part 2" section here.

## Part 1 · preface and laws Ա–ՃԷ

The preface (Նախադրութիւն), eleven chapters:

- Ա (line 5): an answer to those who say the
  Armenians have no laws: why Christ and the
  apostles left no written law of judgement (six
  reasons).
- Բ (line 30): why Gosh writes now (twelve
  reasons: scorn from others, judges who take
  bribes, oaths, forgetfulness, ...); twelve as
  two sixes; how he came to write: brother Pavghos,
  and Catholicos Stepanos of Aghvank, who urged him.
- Գ (line 104): to Catholicos Stepanos: the law
  book beside the canons, as body beside soul.
- Դ (line 130): who judges: God, then men (kings,
  princes, elders, prophets, priests), and each
  man his own soul.
- Ե (line 152): what judgement is (the word
  դատաստան), whom it is for (the "middle" people,
  neither plainly good nor plainly bad), and to
  whom it is given: the bishops.
- Զ (line 179): how judges, the accused and the
  accusers must be: no bribes, hear both, two or
  three witnesses, two or three assessors (the
  Romans' 72, the Greeks' and Georgians' three),
  patience, a prison, no false words.
- Է (line 250): witnesses: their age (25), women
  (only through men), unbelievers (not against
  Christians), why two or three (long list of
  witnesses in Scripture).
- Ը (line 306): oaths: forbidden by Christ, so not
  commanded here, only ruled; the oath of
  confession (on cross, Gospel, church) and the
  oath of denial (blowing out a lamp, a dog's tail,
  treading a cross), never to be taken; who may
  not swear; penances (3 years, 7 years, for life).
- Թ (line 416): Christians must not go to
  unbelievers' courts; what the Muslims believe
  and do.
- Ժ (line 459): the sources: natural law, the
  Torah, the canons, Scripture, other Christian
  peoples; the book is to grow, like the canons.
- ԺԱ (line 497): colophon: begun in the Armenian
  year ՈԼԳ (1184), under Hasan and Vakhtang of
  Khachen, Prince Ruben of Cilicia, Catholicos
  Grigor and Catholicos Stepanos, in the hermitage
  of Dasno by the monastery of Horomashen, in
  the province of Gandzak.

The laws (line 515: «ՍԿԻԶԲՆ ԴԱՏԱՍՏԱՆԻ»):

- Ա–Ե (lines 517–815): judges' share (the
  estates of the heirless), kings (succession,
  daughters, war, plunder, taxes: the fifth, the
  tithe; crafts and their honour), monasteries and
  their abbots, teachers (վարդապետ), priests.
- Զ–ԺԹ (lines 816–1000): husband and wife: impotence,
  madness, leprosy, captivity, hatred, adultery,
  barrenness, a long absence (seven years), a
  violent husband, apostasy, murder.
- Ի–ԻԹ (lines 1001–1089): guilty princes' heirs;
  serfs are free to leave; children who kill or
  wound in play, wagers, drinking bouts; adultery,
  virgins.
- Լ–ԽԳ (lines 1090–1227): slandered brides;
  mines, forests, rivers and game; treasure
  troves; beards pulled; grain pits; serfs worked
  too hard; the apostolic canons on priests,
  judges, church property and bishops.
- ԽԴ–ԿԴ (lines 1228–1431): church thieves;
  bishops accused and their witnesses; nepotism;
  bishops in worldly business; slaves as clerics;
  insulting kings; child murder; robbers;
  abduction; Hebrew and foreign slaves; striking
  or cursing parents; kidnapping; fights;
  "an eye for an eye", paid in fines (26 dahekan
  and half a dang a limb).
- ԿԵ–ՀԲ (lines 1432–1516): the goring ox; pits
  and wells; animals that kill.
- ՀԳ–ՁԹ (lines 1517–1718): theft of cattle,
  breaking in, church theft, grazing, fire,
  deposits, things lent, a seduced betrothed girl,
  loans (no interest), pledges, arson, cutting
  trees, Lev 6 on lying about a deposit, holy
  food, the blasphemer (Lev 24), killing animals.
- Ղ–Ճ (lines 1719–1839): selling land and houses
  (redemption within seven years), priests'
  houses, mills; sales of animals (seven days or a
  year to return them), oxen, cows, bees, jars,
  crops in advance, renting a mill.
- ՃԱ–ՃԷ (lines 1840–2003): inheritance
  (Zelophehad's daughters; a son, a daughter at
  home, two married daughters as one son; the
  mother's and wife's dang), a woman's estate, the
  arithmetic of shares in dang, tasu and gari,
  contempt of priests and judges (Deut 17), the
  priests' portion (Deut 18), boundary stones
  (Deut 19:14).

Notes on the text:

- Line 519: `ԳԼՈՒԽ Ա` under `[Ա]` is the only
  group line; the Contents lists both.
- Line 1888: the Grabar opens a «» it does not
  close; the translation closes it.
