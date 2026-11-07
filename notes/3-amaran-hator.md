# Ամառան հատոր: notes on the parts

Working notes gathered while translating Grigor
Tatevatsi's summer volume (Գիրք քարոզութեան որ կոչի
Ամառան հատոր) into modern Eastern Armenian. Not on
the shelf and not on the Pages site: for later use
(a table of contents, the welcome page, indexes).

Files: `books/grabar/grigor-tatevatsi/3-amaran-hator/`
and the translation at the same path under
`books/ashkharhabar/`. Line numbers are the same in
both. Each part is cut at the Digilib chapter
groups (ԳԼՈՒԽ Ա-Ե, Զ-Ժ, ...); a sermon's heading
gives its text, then the verse, then `(Գլուխ ...)`.

How the sermons are built: a short opening, then
the text cut into numbered "heads" (նախ, երկրորդ,
... տասներորդ), often with questions (հարց) and
answers (պատասխանի), many comparisons from nature
(ants, bees, the body, seeds, the sea), and a
closing prayer with the doxology.

## How to do the next part

Parts 1–7 are done. To do part N (08 next):

1. Split the Grabar into sentences in place (the
   file from Digilib has long paragraphs):

   ```python
   import re, sys
   p = sys.argv[1]
   lines = open(p).read().split("\n")
   cut = re.compile(
       r"(։+)(\s*\))?\s*(?=[^\s)])")
   def sub(m):
       close = ")" if m.group(2) else ""
       return m.group(1) + close + "\n"
   out = []
   for i, ln in enumerate(lines):
       if i == 0:
           out.append(ln)
           continue
       if not ln.strip():
           continue
       if out[-1] != "":
           out.append("")
       part = cut.sub(sub, ln.strip())
       out += [x.strip()
               for x in part.split("\n")]
   open(p, "w").write("\n".join(out) + "\n")
   ```

   One sentence per line, cut after `։` (a run
   `։։` and a closing `)` stay on the line); a
   blank line where a Digilib paragraph ended.
   Count the places where `։` had no space after
   it, for `books/SOURCES.md`.
2. Translate line for line into
   `books/ashkharhabar/.../NN.txt`, in chunks of
   about 75 lines:
   - title line: «Քարոզգիրք, որ կոչվում է Ամառան
     հատոր · N/24»; `(Գլուխ. X)` becomes
     `(Գլուխ X)`; chapter group lines
     (`ԳԼՈՒԽ ԼԱ-ԼԵ`) stay as they are;
   - reformed spelling, `և`/`Եվ`, never `եւ`;
   - quotations keep the Grabar's parentheses;
     no square brackets; a leading `*` is kept;
   - repeated passages and odd numbering are kept
     (see "Notes on the text" below).
3. Check: same line count as the Grabar, blank
   lines at the same places, no `։` inside a line
   (except where the Grabar has it), no Latin
   letters, no `եւ`.
4. Update `books/SOURCES.md` (file range, the `։`
   count, the part's sermons in the translation
   note) and add a "Part N" section here.
5. Run ruff and pytest, commit, push to the
   session branch, then ask before `main`.

## Part 1 · ԳԼՈՒԽ Ա-Ե (sermons 1–5)

Opens with a prayer to the Holy Spirit and the title
of the book: "second volume" of Grigor's sermons
(the winter volume is the first), by Grigor
"Եռամեծ", pupil of Hovhannes Vorotnetsi.

- Ա: Ps 118:35 «Առաջնորդեա ինձ ի շաւիղս
  պատուիրանաց քոց». Two ways of life, good and
  evil; the good is natural to man, evil came
  later (from Satan and from free will); God's law
  turns us back; how the law is kept.
- Բ: the beginning of the Ten Commandments, Ex
  20:2–3 («Ես եմ Տէր Աստուած քո...»); body and soul,
  idolatry.
- Գ: «Մի սպանաներ, մի շնար, մի գողանար...», Ex
  20:13; the commandments of the second table.
- Դ: the Ten Commandments in general.
- Ե: the ten plagues of Egypt, Wis 11:16 «Որով ոք
  մեղանչէ, նովին եւ տանջի».

## Part 2 · ԳԼՈՒԽ Զ-Ժ (sermons 6–10)

- Զ (line 5): visions and dreams, Hos 12:10. Five
  ways God warns (reason, visions and dreams, body
  signs, animals, signs in the sky); four kinds of
  dreams (natural, from the humours, demonic,
  divine vision); why the unworthy see visions
  (Pharaoh, Nebuchadnezzar, Balaam, Caiaphas);
  Joseph's interpretation; seven as a holy number;
  the kinds of famine (of bread, of the word, of
  works, of faith, the "famine" after death);
  storing up treasure in heaven, almsgiving.
- Է (line 122): «Հայեաց ի քեզ, գուցէ լինիցի բան
  ծածուկ ի սրտի քում», Deut 15:9. Ten meanings of
  "look to yourself": the soul's eyes; soul, body,
  possessions; the virtues (3 divine, 4 human);
  the seven deadly sins (and Evagrius' eight
  thoughts); the seven sacraments; each rank of
  clergy (catholicos to dpir; nine ranks like the
  nine choirs of angels); rulers and judges; the
  six things praised in the world; men, women, old,
  young, rich, poor, masters, servants; clergy and
  lay people.
- Ը (line 335): the Holy Trinity, John 4:24 «Հոգի
  է Աստուած». Witnesses from Scripture (long list
  of OT verses), from the philosophers (ten
  arguments: goodness shares itself, intellect and
  will, three dimensions, Aristotle on order), and
  from the teachers' images (sun, light and heat;
  mind, word and breath; Adam, Eve and Seth; root,
  tree and fruit; sea, river and spring; the apple's
  taste, smell and colour). Why "one God" does not
  exclude the Son and the Spirit (four senses of
  "one").
- Թ (line 504): the Lord's Prayer I, Luke 11:2.
  Why this prayer is above all others; six ways God
  is called Father (by nature, creation, rebirth,
  teaching, care, inheritance) and six ways he is
  our Father; ten good things in "Father"; the
  unworthy who say "Father" (six blasphemies);
  four ways one becomes a son of Satan (will,
  works, likeness, image) and Satan's "features";
  why "our" and not "my"; ten reasons for "in
  heaven"; six ways to rise to heaven; the
  prodigal son read as Adam and the sinner (the
  kiss, robe, ring, shoes, fatted calf).
- Ժ (line 677): the Lord's Prayer II. Priesthood of
  the law and of grace; ten works that make us
  worthy to say "Father"; «Սուրբ եղիցի անուն քո»;
  «Եկեսցէ արքայութիւն քո» (four reasons; the
  variant «եկեսցէ հոգի քո սուրբ»); each petition
  addressed to a person of the Trinity.

## Part 3 · ԳԼՈՒԽ ԺԱ-Ի (sermons 11–20)

- ԺԱ (line 5): the Lord's Prayer III, from «Եղիցին
  կամք քո» to «Ամէն». Five causes of sickness and
  health of body and soul; God's will as health;
  "on earth as in heaven" (angels, wine and its
  lees); daily bread (four meanings; "today",
  against care for tomorrow but not against work);
  forgiving debts (six meanings; God learns from
  us; harm of not forgiving; the unforgiving
  servant); temptation and evil (Satan's names; the
  bait and the hook); the doxology and Amen.
- ԺԲ (line 177): faith I, Heb 11:6. Isaiah's three
  ways to know God; what faith is (Paul, Dionysius);
  faith sees more than mind or eye (four proofs);
  where faith comes from (light of nature, of
  grace, of glory); faith is in the intellect, ruled
  by the will; three kinds (demons', dead,
  living); the fourteen steps of faith on Jacob's
  ladder (7 of the Godhead, 7 of Christ's
  economy) and a creed built from them.
- ԺԳ (line 355): faith II, Jas 2:20 «Հաւատք առանց
  գործոց մեռեալ են». Faith given at baptism; how
  Christ "does not know" a man (four reasons); two
  kinds of faith (confession, trust in Scripture);
  ten differences between dead and living faith;
  why works are needed though the kingdom is free
  (ten reasons; images: two oxen, two wings, root
  and fruit, foundation and building: gold, silver,
  stones against wood, hay, reed); ten goods of
  faith; the many kinds of unbeliever.
- ԺԴ (line 600): faith, hope and love, Gal 5:6.
  Three lights (reason, the written law, the
  gospel); differences of the three virtues and
  their order; why love is the greatest (four
  ways); how faculties gone astray are set right.
- ԺԵ (line 685): hope, Rom 5:5 «Յոյս ոչ երբէք
  ամաչեցուցանէ». What hope is; hope and faith
  compared; why hope does not shame (hoping in
  Christ, not in men); the goods of hope; despair.
- ԺԶ (line 757; group ԳԼՈՒԽ ԺԶ-Ի starts): love I,
  John 15:12, from "another" (Յայլմէ) preacher. Love
  unites (the body, the elements, the heavens, the
  ranks of angels); four unions of the Church's
  members; ten ways members of a body love each
  other; six ways Christ loved us; animals love
  their kind (pigs and dogs).
- ԺԷ (line 874): love II, also "from another".
  Four properties of holy love; why we must love
  (one father Adam; nature teaches unity; the
  neighbour is precious: blood, angels, image;
  members of one body); "love your neighbour as
  yourself" (three meanings); seven degrees of
  love; love as a compass; discord.
- ԺԸ (line 1018): virtue, Aristotle «Գովելի են
  գեղեցիկքն...». The three parts of the soul; what
  virtue is (teachers, Aristotle's mean); divine and
  human virtues and their opposites; moral,
  economic and political virtue; works of each
  virtue and vice (prudence, courage, temperance,
  justice, liberality, magnanimity); a fallen
  priest may not celebrate; ten praises of virtue.
- ԺԹ (line 1184): prudence, Eccl 1:18 «Որ յաւելու
  ի գիտութիւն, յաւելու ի ցաւս». The soul's four
  gifts kept after the fall; why the wise grieve
  (ten reasons; the shipwreck seen from shore);
  heretics' words as wild honey, holy words as
  true honey; the fool cannot be beaten out of his
  folly (ten reasons).
- Ի (line 1324): wisdom, Prov 3:13 «Երանեալ է այր
  որ եգիտ զիմաստութիւն». Practical wisdom (moral,
  acquired, divine) and theoretical wisdom (God,
  Christ, the Spirit, faith and hope, meditation on
  good works, Greek natural philosophy, which saved
  some pagans in Christ's descent to hell); ten
  praises of wisdom (the hidden treasure, the tree
  of life, the way, creation by wisdom).

## Part 4 · ԳԼՈՒԽ ԻԱ-ԻԵ and ԻԶ-Լ (sermons 21–30)

- ԻԱ (line 5): courage and work, Rom 12:11 and Prov
  6:6 «Ով վատ, երթ առ մրջիւնն». Four proofs that man
  is made for work; what the ant teaches (zeal and
  three kinds of wisdom); the bee as theoretical
  virtue (ten reasons).
- ԻԲ (line 112): work, Gen 2:15 «գործել եւ պահել».
  Ten meanings of tilling and keeping Eden; bodily
  work and its reasons; farming the best of crafts
  (six reasons).
- ԻԳ (line 171): farmers, Prov 24:30. The parable
  of the sower read three ways; four crafts (good,
  evil, two mixed); man as field and vineyard (ten
  reasons); why a sermon ends with a blessing
  (text, prologue, sermon, exhortation, blessing as
  seed, ploughing, sowing, harrowing, watering).
- ԻԴ (line 315): the idle, Ps 48:10 «Վաստակեա
  յաւիտեան». Bread of soul and body; four kinds
  (work and eat, etc.); Solomon's ten sayings on the
  sluggard (the door on its hinge, "a lion in the
  way", poverty like a runner); summer and winter.
- ԻԵ (line 499): sleep, Luke 22:46. Four kinds of
  sleep and of wakefulness; what dreams are
  (Gregory of Nyssa: the vegetative soul); ten ways
  sin is like sleep; why we must wake (the cock
  that crows three times, church bells rung three
  times); old age.
- ԻԶ (line 622; group ԳԼՈՒԽ ԻԶ-Լ starts): lawful
  marriage, Heb 13:4. Ten honours of marriage
  against fornication; three ways marriage is
  defiled (excess, forbidden days: Sun, Wed, Fri,
  fasts; manner); why adultery is forbidden;
  Solomon's twelve warnings; the sea of desire.
- ԻԷ (line 759): justice I, Hos 10:12 «Սերմանեցէք
  զարդարութիւն». Four witnesses (nature, will,
  mind, Scripture); how justice is sown and its
  fruit; ten reasons for the image of the seed;
  what justice is and its kinds (soul and body,
  this life and the next, toward God and men, in
  trade, of the tongue, of judges, in marriage).
- ԻԸ (line 895): justice II, Ps 10:8. Justice with
  mercy and without; four useless justices (the old
  law, Jephthah's and Herod's oaths, outward purity,
  the Novatians' ban on marriage and meat); "a just
  man perishing in his justice" (the Pharisee and
  the publican; the Jews and the law); wisdom
  helping more than ten rulers.
- ԻԹ (line 1026): justice III, Ps 118:121. Man made
  just (six proofs); six causes of sin; six helpers
  of the just man around him.
- Լ (line 1097): just weights and trade, Prov 11:1.
  Weight, measure and cubit; ten goods of fair
  measure; just profit; ten sins of the cheating
  merchant (կուղբակ "thief's yard"); man as a pair
  of scales (soul and body); scales of love, of
  loan, of repayment.

## Part 5 · ԳԼՈՒԽ ԼԱ-ԼԵ and ԼԶ-Խ (sermons 31–40)

- ԼԱ (line 5): wrongs and false accusation, Eccl
  4:1. Ten ways of wronging; "better the dead and
  the unborn".
- ԼԲ (line 103): the seven sacraments and baptism,
  John 3:5. Why the rite was handed down by word
  and uses bodily signs; why seven sacraments; the
  godfather; ten reasons why women do not enter at
  baptism; renouncing to the west, confessing to
  the east; triple immersion as death and burial;
  anointing, and why the Armenians anoint in a
  hidden way; priests may confirm; no rebaptism.
- ԼԳ (line 333): baptism, Zech 3:9. Birth from the
  font and bodily birth (six likenesses, six
  differences); three births (body, grace, glory);
  faith, baptism and anointing and the Trinity;
  warm water, myron, light, cross; confirmation on
  the forehead; old and new Adam; circumcision of
  the heart.
- ԼԴ (line 505): communion, John 6:52. Names of the
  sacrament; the liturgy explained (incense,
  psalms, readings, alleluia, creed); three
  unworthy classes sent out; confession.
- ԼԵ (line 620): communion, continued. Three worthy
  classes; washing of hands; kiss of peace; words
  of God, angels and men, three languages; the two
  blessings (institution, epiclesis); twelve
  reasons for bread and wine; one loaf, against
  the Franks; accidents and substance; against the
  dyophysites; the saints remembered; elevation;
  ten qualities of the host.
- ԼԶ (line 776; group ԳԼՈՒԽ ԼԶ-Խ starts, "from
  another"): the Liturgy, Matt 26:26. Union through
  the five senses; why hidden under bread and
  wine; four essentials (true priest, matter,
  words, intention); five objections answered
  with natural images (star and serpent-stone,
  mercury and sulphur, petrifying waters; the sun
  in a mirror; the widow of Zarephath; many places
  at once; Isaac and Jacob for the accidents).
- ԼԷ (line 905): ordination, Ps 131:16. Dionysius'
  definition of hierarchy; order everywhere
  (angels, heavens, elements, cities); likeness to
  God: purify, illumine, perfect (deacon, priest,
  bishop); the priest as angel, mediator,
  watchman, salt, elder; the lazy and the active
  priest.
- ԼԸ (line 1052): the priesthood, Ps 109:4. The
  angelic hierarchy; demons have no priesthood or
  prophecy; old and new priesthood (tabernacle as
  type); the nine ranks (doorkeeper, reader,
  exorcist, candle-bearer, dpir, deacon, priest,
  bishop, catholicos); the rite: tonsure, key,
  kneeling, laying on of hands, Gospel on the
  bishop's head, the kiss; only priests give the
  right hand; a closing charge to priests.
- ԼԹ (line 1274): monks, Luke 14:27. Dionysius'
  three graces and the classes of the church (five
  orders to be purified, the people, the monks as
  «կամարար»); six meanings of «միայնակեաց»;
  monozon and skemavor; what a monk may not do;
  the rite: renouncing (loved ones, goods,
  pleasures; will, evil thoughts, pride), tonsure
  in five places, the habit (five garments, four
  more for the skemavor, the Egyptian fathers);
  priests and deacons who become monks only change
  dress; communion at the end.
- Խ (line 1360, "from another"): the orders, Lev
  21:6. Order in the Trinity, angels, heavens (the
  seven planets with Armenian and Arabic names),
  elements, plants, animals, men; seven church
  orders like seven planets. Part one: what Christ
  wants of ministers: good birth, full age (25),
  no blemish: the twelve bodily blemishes of Lev
  21 read as twelve blemishes of the soul; which
  bodily defects bar a priest; eunuchs (three
  kinds, the Nicene canon). Part two: six
  essentials of ordination (a bishop, the matter
  handed over, the words for each of the seven
  orders, a man, baptised, true intention); nine
  seals; essentials vs accidents of a rite.

## Part 6 · ԳԼՈՒԽ ԽԱ-ԽԵ and ԽԶ-Ծ (sermons 41–50)

- ԽԱ (line 5, "from another"): the priesthood, Ps
  131:9 «Քահանայք Քո զգեցցին զարդարութիւն». Three
  spiritual degrees (nature, grace, glory) and
  order in each; why many orders (three reasons;
  Moses' seventy elders; the queen of Sheba);
  Solomon's throne with six steps; three honours of
  priests: the six vestments (խոյր, շապիկ, գօտի:
  Elijah's leather belt and Christ's golden one,
  ձեռնուրար and բազպան, ուրար, նափորտ, each read
  as the Passion and as a virtue), the tonsure as
  a round crown (four reasons), the seat at
  Christ's table above the angels; four reasons
  for purity (the ark, the cupbearer, one dish,
  God's works).
- ԽԲ (line 124): priests, Mal 2:7 «Շրթունք
  քահանային զգուշասցին գիտութեան». The lips that
  keep knowledge (eight ways; no pork, no clipped
  psalms: Satan takes the remainder); "the law
  from his mouth"; sixteen likenesses of the priest
  to an angel. Questions: why monks wear wool and
  not linen (ten reasons each for wool and for the
  linen of the old law); the loose robe of the
  clergy; why they are called «ժառանգաւորք»; why
  Christ went to the wedding and turned water into
  wine (ten reasons; the six jars; water and wine
  as advice to the married).
- ԽԳ (line 249, "from another"): confessors, Mal
  2:7 again. Four reasons the confessor needs
  knowledge; seventeen rules: the right remedy for
  each sin, penance by time, age, sex and rank,
  none for the dying, no money for confession, the
  seal (a locked chest that breaks before it
  opens), purges and binders for the soul, gentle
  words before the lancet; one who led others
  into sin must bring them back (spiritual theft;
  the robber must clothe whom he stripped).
- ԽԴ (line 298): marriage I, Gen 1:27. "Not good
  to be alone"; why woman is good though she
  caused the fall (God's goods are not stopped by
  one sin; why God spares sinners: six reasons);
  without the fall no incarnation (felix culpa);
  against a corruptible paradise with sexual
  generation (seven proofs; Gregory of Nyssa; the
  Muslims' bodily paradise); how men would have
  multiplied (like angels, like lamps lit from
  one); betrothal, consent, blessing, union; three
  goods of marriage (faith, offspring, sacrament);
  impediments; the two bonds and two deaths.
- ԽԵ (line 421): marriage II, Gen 2:21. Only the
  heading: no text follows on Digilib.
- ԽԶ (line 426; group ԳԼՈՒԽ ԽԶ-Ծ starts): marriage
  III, Eph 5:32 «Խորհուրդս այս մեծ է». The seven
  sacraments; betrothal and the ring (ten
  meanings: faith); the wedding as the incarnation
  (ten properties of Adam's rib and the Virgin's
  blood) and as Christ's union with the Church
  (ten more); the bride at the left, then the
  right; seven garments and seven gifts (four of
  the body, three of the soul); dowry, gifts, veil,
  crown, red and white thread; no crown at a second
  marriage; three days of feast (Adam and Eve's
  three happy hours) and the crown taken off on
  the eighth day.
- ԽԷ (line 609): sins I, 1 John 5:16 «եւ են՝ որք
  մահու չափի են». Natural discernment; sins of
  ignorance, of weakness and of will; twelve
  differences between unwilling and wilful sin
  (stumbling and falling in a pit, sick and dead,
  warm water and a furnace); why God does not drag
  us to good by force; God is not the cause of sin
  (all he gave is good and measured); what sin
  harms in body and in soul; why man sins (Satan
  paints evil as good; the fish and the hook); no
  repentance after death; prayers for the dead
  help only the penitent.
- ԽԸ (line 761): sins II, Ex 34:7 "visiting the
  sins of the fathers to the third and fourth
  generation" (six readings: seven ages, four
  births, four centuries before Canaan, four
  ways of sinning, four ages of man); why God
  punishes; good works of unbelievers and mortal
  sinners (dead, yet useful: eight reasons); four
  signs of being in God's love; quantity and
  quality of sin; the priest owes seven times more
  good, the bishop eight, the catholicos nine, the
  vardapet five honours more.
- ԽԹ (line 861): sins III, Jas 1:15 «Ցանկութիւն
  յղացեալ՝ զմեղս ծնանի». Desire as the serpent
  (fourteen likenesses); desire and pleasure,
  passion and defilement, sin and lawlessness;
  sin, death and "unto death"; sins of the four
  humours (Gregory of Nyssa); good shared is good,
  evil shared is evil; "you number my steps and
  seal my sins in a bag" (Job 14:16–17).
- Ծ (line 947, "from another, and right"):
  original sin, Ps 50:7. Original, mortal and
  venial sin and how they differ (one, common,
  equal, unwilled, of nature not person; the
  Virgin cleansed at her ensoulment; only Christ
  free of it); the four wounds it leaves (desire:
  the hydrus and the crocodile; ignorance; anger;
  malice). Goes on in part 7.

## Part 7 · ԳԼՈՒԽ ԾԱ-ԾԵ and ԾԶ-Կ (sermons 51–60)

- ԾԱ (line 5): mortal sin. Objections (the soul is
  immortal; sinners still act well); four marks:
  it destroys life (love of God as the heart's
  warmth), takes away the power to rise (one can
  throw oneself into a fire, not climb out),
  leaves the way (Alpha and Omega; the narrow and
  the broad way) and binds to Gehenna; why a short
  pleasure earns endless pain (the offended
  person's rank: a soldier, a king, God); good
  works done in mortal sin are not remembered.
- ԾԲ (line 54): venial sin, known by event, cause
  and nature; wood, hay and reed; man cannot live
  without it (1 John 1:8), and it is cleansed by
  general confession, beating the breast, the
  sign of the cross, the Trisagion, the Lord's
  Prayer. Four harms of all sin: death and the
  strife of the elements, a low place (the eye set
  high, the rich man buried in hell), endless
  pain, darkened sight.
- ԾԳ (line 116): sinful thoughts, Wis 1:9. Ten
  reasons to guard the mind (the root before the
  shoot; the charioteer; eight thoughts as arrows;
  the mind as lamp, mirror, judge, spring), then
  ten from Scripture (adultery in the heart; Job's
  daily sacrifices; the tray offered to a king;
  the Spirit as watchman over word, anger and
  desire; whitewashed tombs); the double trial of
  thoughts, by God's word and in confession.
- ԾԴ (line 208): the tongue, Prov 18:21 «Մահ եւ
  կեանք ի ձեռն լեզուի». Why the tongue slips (quick,
  shameless, walled in the mouth); the fear of God
  as bridle and reins; ten goods of the tongue
  (peace, prayer, praise, teaching, intercession)
  and ten evils: lying, false witness (six rules
  for a witness), heresy and apostasy (the
  apostate is better: four reasons), false oaths,
  idle talk and betrayal, slander and gossip,
  buffoonery, anger, sorcery, cursing (no
  communion and no blessed earth for those who
  curse).
- ԾԵ (line 354, "from another"): the tongue, Ps
  33:14. Ten reasons to keep it (the gift of
  speech; the mouth receives Christ's body; the
  uncovered vessel and the flies; bridle and
  rudder, Jas 3; fire of Pentecost against the fire
  of the tongue; speech shows one's country);
  Anthony's disciples "with no door"; Secundus the
  philosopher and his mother; six rules for the
  preacher (fit the hearers, plain words, the
  right time, measured anger, tears, do first
  what you preach).
- ԾԶ (line 444; group ԳԼՈՒԽ ԾԶ-Կ starts): the evil
  tongue, Ps 33:14 again. Hatred, blasphemy (worse
  than the Jews' and the idolaters'; the son who
  would not shoot at his father's body), anger and
  slander announced; blasphemy of the heart and of
  the tongue.
- ԾԷ (line 512, "from another"): slander, Jas
  4:11. Spiritual theft worse than bodily; the
  slanderer like eight animals (dog, pig, snake,
  bear, an evil brood, the dung beetle, Satan's
  "priests" with the backgammon board and the dice
  numbered against the Faith, Hanun who shaved
  David's men); slandering a leader (Miriam, Ham,
  Uzzah, David and Saul's robe); the listener sins
  too (six reasons); six ways of slander.
- ԾԸ (line 656): anger, Jas 3:6. Man as a city
  (senses as gates and windows, the mouth a double
  door); ten harms of anger; anger and wrath
  compared; ten goods of a gentle tongue (the
  peacemaker; a soft answer; Korah and Moses;
  Zedekiah, Nabal and Abigail).
- ԾԹ (line 796): patience, Prov 20:22. Four kinds
  of revenge and four harms of taking it; why
  patience is above the other virtues; ten fruits
  of patience; patience and continence compared.
- Կ (line 844): laughter, Luke 6:25. Laughter as
  an accident, not the essence (David the
  Invincible, eight proofs; Trophonius' cave);
  from the breath, muscles and sinews; do animals
  laugh; ten causes of laughter, ten harms, ten
  punishments; Christ never laughed but wept; the
  seven evils contained in "woe".

## Notes on the text

- The Digilib text has many misprints; repeated
  passages and whole repeated sentences are kept
  and translated as they stand; a plainly misspelt
  single word is translated as the word meant (for
  example part 3 line 399 «ուրախանամք» for
  «ուրանամք»).
- Sermons ԺԶ and ԺԷ are headed «Յայլմէ քարոզ»,
  "a sermon from another": perhaps not by Grigor.
- Some numbered lists skip or repeat a number
  (e.g. two "second"s); kept as in the text.
- Part 5 line 1238 is a stray «Իսկ վերատեսակ։»
  (a false start of the next line); kept as a line
  of its own.
- Part 5 line 1447 reads «կարեն գալ» ("can come")
  where the sense needs «ոչ կարեն»; translated as
  «չեն կարող գալ».
- Part 6 line 421: sermon ԽԵ is only a heading;
  the next line starts group ԳԼՈՒԽ ԽԶ-Ծ.
- Part 6 line 607 is a stray fragment «պատւով ե»
  between two sermons; kept as «պատվով ե».
- Part 6 line 585 reads «եւ զայս ունին հրեշտակք»
  ("and this the angels have") where the sense
  needs «ոչ ունին»; translated as «չունեն».
- Part 6 line 590 reads «զի ժամ» where line 595
  shows "three hours" is meant; translated as
  «երեք ժամ».
- Part 6 line 699 reads «կամ սիրով» ("or by
  love") among punishments: «սրով» (by the sword)
  is meant and translated.
- Part 7 line 271 reads «սատանայն շահնա» ("Satan's
  gain") where the liar is meant («ստախօսին
  շահն»); translated so.
- Part 7 line 561 ends in a stray `?` before a
  paragraph break; kept.
- Part 7 lines 863 and 882 (a definition of
  laughter, «ստերիւրեցելոյ ... հագագի», and a
  saying «մի ծաղր յանգուքն») are garbled;
  translated by the sense.
