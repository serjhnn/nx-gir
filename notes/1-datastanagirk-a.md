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

## How it was done

Both parts are done (part 2 on 2026-11-12), by
"How to do the next part" in
`notes/3-amaran-hator.md`, with these changes
(the same hold for redactions Բ and Գ, if they
are translated):

- the title line is «Դատաստանագիրք, Ա
  խմբագրություն · N/2»;
- the `[Ա]` lines and `ԳԼՈՒԽ Ա` stay exactly as in
  the Grabar (the Contents finds a section by its
  `[Ա]` line, `SECTION_RE` in `nxgir_reader.py`);
  the title under it is translated, in capitals,
  "… ԴԱՏԱՍՏԱՆՆԵՐԻ ՄԱՍԻՆ" for «ՅԱՂԱԳՍ ԴԱՏԱՍՏԱՆԱՑ
  …»;
- the Grabar has no «» or parentheses for
  quotations: add none; its few `[…]` editorial
  insertions are kept; words the translation adds
  to make a sentence whole are in ( );
- terms kept as they are: `դահեկան`, `դանգ`,
  `թասու`, `գարի` (money and its parts, law ՃԴ),
  `սիկղ`, `երկդրամյան`, `չեքչեք`; `որոշվել` for
  being cut off from the church, `լուծվել` for a
  cleric losing his rank.

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

## Part 2 · laws ՃԸ–ՄԾԱ

144 laws (108–251), 2067 lines. From ՃԼԲ on most
laws are canons (of the councils, of Basil, of the
Armenian fathers), quoted first, with Gosh's
comment after a blank line; ՃԿԵ–ՃՀԳ and ՃՂԳ–ՃՂԴ
are questions and answers (`Հարց.` /
`Պատասխան.`).

- ՃԸ–ՃԼԱ (lines 3–239): laws from Deuteronomy
  with Gosh's comments: witnesses and false
  witnesses, a body found in the fields, captive
  women, the firstborn, the stubborn son, the
  hanged, lost and fallen animals, men's and
  women's clothes, birds' nests, the parapet,
  runaway slaves, a neighbour's harvest and
  vineyard, the bill of divorce, the newly
  married and war, pledges (millstones, the
  widow's garment), the hired man's wage, fathers
  and sons, forty stripes, the woman in a fight.
- ՃԼԲ–ՃԿԴ (240–574): canons: grave robbers,
  killing a robber, founding a church, ordaining
  bishops and catholicoi, clergy who lend at
  interest, abducted betrothed girls, eating
  meat, church property, a broken vow of
  virginity, baptizing pregnant women, divorce
  for adultery and for hatred, the age of
  ordination (thirty), country priests,
  chorepiscopi, parents and children, Maundy
  Thursday, bishops under the metropolitan,
  appeals, ordaining in another's diocese,
  marrying outsiders.
- ՃԿԵ–ՃՀԳ (575–683): questions and answers:
  the suicide of a madman, a possessed wife,
  impotence, a crippled wife, a priest who kills
  robbers, killing by the possessed, barrenness,
  killing by accident; Gosh on intent, no intent
  and the two mixed.
- ՃՀԴ–ՃՀԹ (684–736): killing in war (three
  years without communion), sons who leave,
  eunuchs, fourfold and threefold repayment.
- ՃՁ–ՃՁԴ (737–826): inheritance of sons and
  daughters (a daughter at home as a son, two
  married ones as one), from when a child
  inherits (birth, against "the pupils of
  Mahmet"), disabled children, wills (three
  witnesses), funeral costs and what husband and
  wife inherit from each other.
- ՃՁԵ–ՃՂԸ (827–1004): fraud in sales, false
  witnesses, betrothal, who may marry (lepers,
  the lame, blind, deaf, mute), child marriages,
  milk kinship, boundaries (cross and Gospel as
  an oath), leaving a wife and mother (fines in
  dram, the leper-house), a barren wife, wives
  who leave, abduction.
- ՃՂԹ–ՄԺԱ (1005–1157): priests: the senior
  priest, shares of the income, service,
  memorial gifts, the excommunicated, closing a
  church, spouses of captives (seven years),
  heirs of church land, priests' houses free of
  the nobles, nobles in monasteries, infirmaries.
- ՄԺԲ–ՄԺԳ (1158–1250): kinship in marriage: a
  catholicos's letter of the eighteenth year of
  Khosrov son of Ormizd, then Gosh's reckoning of
  the degrees (the fourth for laymen, the fifth
  for priests).
- ՄԺԴ–ՄԻԴ (1251–1373): shipwrecks, impostors
  collecting alms, new villages, when a sale
  holds (the heirs' consent, a sealed deed),
  brides' shares, death from a tree or a church
  stone, hanging thieves, animals that kill,
  sending a man to work, teaching without pay,
  what drunkenness is.
- ՄԻԵ (1374–1665): a treatise, not a law: the
  nine orders of angels (Moses, the prophets,
  Jude, Dionysius), of the Levites and of the
  church (patriarchs down to psalm-singers, with
  deaconesses), the four sees of the evangelists
  and Justinian's change, then the nine orders
  of the Byzantine palace with their dress and
  the other court servants.
- ՄԻԶ–ՄԼԳ (1666–1821): sending others to work,
  hired men, a church built against another, who
  deposes clergy, kings, princes, nobles and
  soldiers; wounding animals in one's field,
  frightening a horse; a list of killings without
  intent, with intent and mixed.
- ՄԼԴ–ՄԾԱ (1822–2065): damage by water,
  physicians, forced work, vine-dressers,
  shepherds, gifts to a ruined church, markets
  (measures, false coin, customs, prices),
  craftsmen, tools, blood price and penance,
  millers, lent horses, "earth money" for graves
  and a dead priest's goods, boundaries and
  fences, possessed animals, a child bride,
  places of pilgrimage, sold spoils.
- Line 2067: the closing line of the book.

Notes on the text:

- Lines 386–387 (ՃԽԵ): the Grabar has the same
  sentence twice; the translation too.
- Line 949: the number is `[ՂՃԵ]` (for ՃՂԵ) in
  the Grabar; kept in both files.
- Line 1382 (ՄԻԵ): «յաղագս հիշատակաց» is read as
  հրեշտակաց ("of the angels"), as the passage
  needs.
- ՄԻԵ, the palace: the Greek titles stay in
  Armenian letters (եղենդիար, վեստիտոր,
  կանտիտոր, պռոքսետոր, ստրատոր, սքողար …), and
  so do unclear words of dress and place (գրատ,
  վաղար, կոպաղ, բեղար, դրսմոն); «ասին կրիտքն»
  (line 1632) is read as one title, ասինկրիտ.
  A reviewer who knows the Byzantine court
  should look at lines 1596–1650 first.
- Left untranslated as unclear: `կիսար` (line
  1786), `հակարաշ` (title of ՄԼԷ).
- Line 1872: the editorial `[ի]` is kept.
- Line 2055: «մարդ տառիւքն է անդրադարձութեամբ»:
  դրամ read backwards is մարդ; the translation
  says so.
- Words chosen: `մեռելոց` for the costs of
  burial and memorial (ՃՁԴ), `իրավատեր` for
  անկաւոր (ՄԷ), `աստիճան` for ազգ and `սերունդ`
  for զարմ in the degrees of kinship
  (ՄԺԲ–ՄԺԳ), `երկամուսին` for երկակ, `աքսորել`
  kept for deposing (ՄԻԹ–ՄԼ).
