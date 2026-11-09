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

Parts 1–13 are done. To do part N (14 next):

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

## Part 8 · ԳԼՈՒԽ ԿԱ-ԿԵ and ԿԶ-Հ (sermons 61–70)

- ԿԱ (line 5): pride and humility, Prov 3:34
  «Տէր ամբարտաւանաց հակառակ կայ». Satan's fall
  and Adam's; Korah burnt, Dathan swallowed
  (priesthood heavenly, rule earthly); ten reasons
  God forgives all sinners but the proud; four
  words: ամբարհաւաճ, հպարտ, ամբարտաւան, սնափառ;
  natural, contemplative and practical humility;
  ten goods of humility (the valley gathers the
  rain, the bough with fruit hangs low, the bush
  of Moses).
- ԿԲ (line 113): envy, Ps 36:1 «Մի նախանձիր ընդ
  չարս». Seven deadly sins, pride and envy the
  devil's own; good and evil envy; five marks of
  envy (it eats the envier first; it is toward
  equals and betters; all toil is for envy; root
  of all crimes; "eats his own arm": Cain,
  Absalom); the envier like a silent dog, fire
  under straw, a dying man; ten ways envy is worse
  than anger (the man who asked to lose one eye so
  his enemy lost two); չարակնութիւն, նախանձ,
  մախանք (Saul and David); "better one handful
  with quiet".
- ԿԳ (line 261): greed, Prov 27:20 «Դժոխք եւ
  կորուստ ոչ յագի». Five senses, four elements;
  eye and ear never full; greed of heart and of
  belly compared; three degrees (want, greed,
  plunder); the greedy poor and the greedy rich
  (dropsy, a holed jar, fire, a hungry wolf); two
  causes (lost dominion of Adam; natural need,
  which is good: six reasons); measure, time and
  command make an act sin or justice (Hosea,
  Elijah, Phinehas; Saul's and Uzziah's
  offerings). Breaks off mid-sentence.
- ԿԴ (line 371): love of money, Eccl 5:9. Plato's
  three parts of the soul; silver neither food nor
  clothing; greed as idolatry in ten ways; the
  miser cannot sleep (Judith and Holofernes);
  riches lost or losing their owner
  (Sennacherib, Belshazzar); left to strangers;
  the miser, the twice robbed, the hoarder (Nabal,
  Ahab and Jezebel, Judas without a grave); the
  miser and the stillborn child (six likenesses);
  the rich man and Lazarus.
- ԿԵ (line 492, "from another"): gluttony, Phil
  3:19 and Luke 21:34. Against nature, the
  brother and God (the belly as god, the kitchen
  for a temple); six harms like six diseases, with
  the physicians' remedies read spiritually
  (bleeding and wormwood: Christ's blood and gall;
  the elephants shown mulberry juice in
  Maccabees; "dog's stomach"); poverty and
  sickness; eating and drinking.
- ԿԶ (line 562; group ԳԼՈՒԽ ԿԶ-Հ starts):
  drunkenness, Eph 5:18. Four drunkennesses (of
  wisdom, of God's mercy, of the joy of the
  kingdom, of wine); Noah and Lot; worst in
  clergy, bishops and kings; Evagrius: no wine for
  monks, measure for lay people; wine changes and
  stirs; four may drink (the poor, mourners, the
  sick, the old). Then (line 624) on prodigality,
  opposed to liberality in four ways; worse in
  priests (Chrysostom: feed the poor rather than
  gild stones).
- ԿԷ (line 650): Satan's snares and fornication,
  Prov 30:15 "the leech has three daughters".
  Why Moses was silent about Satan; Satan named
  lion, dog, bull, adder, leech (ten likenesses);
  the three daughters: grave, love of women,
  Tartarus; why "daughters"; Adam ate for love of
  Eve; the flood, Dinah, Baal-peor, Gibeah,
  Samson, David, Solomon, John the Baptist; earth
  never full of water, fire never says enough:
  good and evil knowledge, good and evil love.
- ԿԸ (line 782): the harms of harlots (Proverbs):
  ten harms, from the look to the fire; God sees
  through distance, house, dark and body. Then
  (line 838) on fornication: ten reasons God told
  Hosea to take a harlot; harlotry and adultery
  compared; why the holy is not defiled by the
  unclean.
- ԿԹ (line 879): the yoke of the law, Hos 10:11
  "Ephraim is a trained heifer" (ten marks); "give
  them a miscarrying womb" (Hos 9:14). Then short
  pieces: why the prophets threatened (line 913);
  Amos 3:12, two legs and a piece of an ear (line
  928); Habakkuk 2:14 and 1:5, the knowledge and
  glory of God and "behold, you scoffers" (line
  950).
- Հ (line 1010): idolatry, Hos 13:4. Ten reasons
  not to worship creatures; how priests urged
  human sacrifice; why idolatry is the worst sin;
  its beginnings (a father's image of a dead son),
  causes (demons, sorcerers like Aramazd, Kronos,
  Aphrodite; kings; the possessed) and supports;
  the meaning of կուռք; six materials and ten
  degrees; holy images are not idols, and God
  asks no soul of the painter (the cherubim, the
  image on the cloth).

## Part 9 · ԳԼՈՒԽ ՀԱ-ՀԵ (sermons 71–75)

Only one chapter group; the file is 669 lines.

- ՀԱ (line 5): untimely death, Wis 1:13 «Աստուած
  զմահ ոչ արար». The commandment between life and
  death; we sin by turning our face from God;
  heaven and earth as witnesses (Moses); why the
  righteous die with the wicked (Abraham's ten
  righteous; the threshing sledge cleans the wheat
  and breaks the straw); three kinds of untimely
  death: weeding, fruit-picking, harvest; against
  those who think the plague is caught (why flee,
  and "flee and hide" read as fleeing sin; Lot,
  Noah, the blood on the doors).
- ՀԲ (line 116): the evil day, Prov 11:4 «Ոչ
  օգնեսցեն ինչք յաւուր բարկութեան». Three evil
  days: this life, death, judgement; the mind
  chooses good from evil (sin dressed as good: tin
  over copper, the hook, the harlot's honey);
  evils of trial, of snares (David and Absalom,
  Bathsheba) and of punishment (sword and bow, Ps
  7); God warns from afar, then near, then on the
  body; the day of death (the thief at four
  watches; why we do not know it; the pitiless
  caller); the day of judgement (no advocate,
  the saints and angels turned accusers).
- ՀԳ (line 267): affliction, Ps 119:1. Ten
  afflictions of our nature (needs, excess,
  illness, beasts, people, demons, the elements,
  service of God, death, the torments); why God
  allows them (Job, Paul, Hezekiah, Lazarus, the
  man born blind, the martyrs); whether the Old
  Law punished only here; why Israel suffered in
  Egypt and the apostles were killed; five gains
  (Chrysostom: the sledge, the file, the fire) and
  five harms of affliction (among the Armenians).
- ՀԴ (line 352): chastisement, Joel 2:15 «Փող
  հարէք ի Սիօն». Rebuke for friends, vengeance
  for enemies; Joel's six counsels: sound the
  trumpet openly, gather every age, fast (the
  daily and the set fasts), pray, weep (tears as
  hot water, alms as soap; the child who cries
  for the breast), "spare your people"; four
  examples: Nineveh, David's census and the
  plague (Ornan's threshing floor, the third to
  the sixth hour), Hezekiah and Rabshakeh (and
  Judith, Gog and Magog under Zerubbabel), God
  merciful, compassionate and long-suffering (the
  sinful woman and the two debtors). Ends with a
  line announcing the next sermon (line 575).
- ՀԵ (line 577): repentance, Matt 3:2. Can a man
  be healed by repentance (Gregory of Nyssa: two
  gifts, repentance and resurrection); not one sin
  while keeping the others; hating, confessing,
  doing the opposite; ten kinds of repentance, one
  accepted; ten chains of Satan that keep us from
  confession; ten reasons to repent at once (fire
  in the house, the open prison, dung for gold,
  the wise virgins); five ways: confession,
  prayer, humility, alms, forgiving debts.

## Part 10 · ԳԼՈՒԽ ՀԶ-Ձ (sermons 76–80)

One chapter group, 823 lines. The Digilib text has
two stray pieces from elsewhere inside sermon ՀԸ
(see "Notes on the text").

- ՀԶ (line 5): repentance again, Matt 3:2. God
  willed it in word and deed (Enoch, Manasseh,
  David, the publican, the harlot, the thief,
  Peter); images of repentance: the waning and
  waxing moon, the new tablets, Moses' rod and
  hand, Aaron's rod, the eagle renewed, the bear
  that drinks before sleep, the snake's skin,
  trees and the earth in spring; animals and
  evergreens as images of steady virtue;
  repentance as a second font; "if the spirit of
  the ruler rises against you" (Eccl 10:4):
  against despair, keep both your sins and
  Christ's grace in mind.
- ՀԷ (line 151): remorse, Ps 118:163 «Զմեղս
  ատեցի եւ անարգեցի». Willing and unwilling sin;
  remorse, conscience and the "complaining" part;
  "where sin abounded"; the sinful woman in
  Simon's house (three ways Christ comes to a
  house; the two debtors; six lessons); six
  causes of remorse; where sins are forgiven: in
  remorse (God), in confession (the soul, the
  priest's loosing), in penance (the punishment);
  the unjust steward; David and Nathan.
- ՀԸ (line 269): confession, Jas 5:16. Why to a
  priest (ten reasons: he binds and looses,
  "priest" means atoner, the angel of the Lord,
  judge of clean and unclean); ten mysteries of
  confession (the thief who flees when you cry
  out, the beast's mouth, the wound shown to the
  physician, the pit); ten gains; its power in
  the Law (the thief's fifth, the hand on the
  victim, the leper); the sinful woman's three
  parts of repentance. After the doxology (line
  378) two stray pieces follow: lines 380–420 on
  greed (Adam, Cain, the flood, Achan, Saul,
  Ahab, Gehazi, Ananias, Judas), and lines
  422–510 on the creation of woman from Adam's
  rib and on marriage (why the rib, the left
  side, the rite at the church door, "one
  flesh").
- ՀԹ (line 512): confession again, Jas 5:16.
  Gold refined in the furnace; confession and
  penance as a second cleansing (the mirror,
  oil and emery); ten likenesses of sin and
  rust; the dog and its vomit; baptism and
  confession compared in ten ways; good and evil
  shame (Joseph and Susanna, Achan and Gehazi);
  why penance after confession (six reasons);
  against money for confession.
- Ձ (line 645, "from another"): confession, 1 John
  1:9. The world's court and God's (Achan);
  twelve things a full confession needs (the
  bloodletter and the lancet, the hundred holes
  in a ship, the widow who hid her sin and the
  two dragons, the beggar who shows his wound,
  the seal of confession); why not to delay
  (fire, the open prison, the money-changer, the
  bow of God; not till sickness: myrrh that flows
  of itself; not till the last week of Lent);
  Ezekiel 5 read as confession. Ends with a line
  announcing sermons on prayer, fasting and alms.

## Part 11 · ԳԼՈՒԽ ՁԱ-ՁԵ, ՁԶ-Ղ and ՂԱ-ՂԵ (sermons 81–95)

Three chapter groups, 1308 lines: a run of sermons
on prayer, then one on fasting.

- ՁԱ (line 5): prayer, 1 Tim 2:1. Why the good
  works are three (fasting, prayer, alms: six
  reasons); twelve reasons prayer is above the
  others (աղ "salt" in աղօթք); prayer, petition,
  supplication, thanksgiving told apart four
  ways; fruitful and fruitless prayer (the
  hypocrite, the impatient, the bold, the
  mocking); praying for others; seven marks of
  pleasing prayer, seven hindrances, ten gains.
- ՁԲ (line 153): "do not heap up empty phrases",
  Matt 6:7. How to pray at all hours; ten kinds
  of the heathen's "much speaking" (gods that are
  absent demons, cursing one's enemy: the
  prophets cursed Satan and sin, not men); why God
  gives bodily things (eight reasons) and why he
  often does not; ten marks of pleasing prayer
  and the gifts that go with it; ten gains; prayer
  as the highest of the acquired virtues.
- ՁԳ (line 320): "my prayer was pure", Job 16:17.
  Purity of heart, tongue and hands; prayer to
  God as king, lord, judge and friend; four sides
  of pleasing prayer (who prays, who receives,
  what is asked, the helpers); ten spurs and ten
  hindrances; prayer as a messenger (Rabshakeh's
  foolish envoy); gains of silent prayer.
- ՁԴ (line 410): the order of the hours, Ps
  50:17. Seven hours in the Old Law, nine in the
  New (twelve with the three private ones); why
  at night and why midnight begins the day; a
  long reading of the night, morning, noon and
  evening offices, hymn by hymn, with the events
  of each hour (third, sixth, ninth). Lines
  414–417 are a garbled repeat of the opening.
- ՁԵ (line 602): Song 6:7 "seven concubines and
  nine brides": seven hours of the Law, nine of
  the Church (nine reasons); three hours for lay
  people; common and private prayer.
- ՁԶ (line 720, group ԳԼՈՒԽ ՁԶ-Ղ starts): the
  morning, Ps 62:7: ten reasons to pray at dawn
  (Adam made at that hour, Christ before
  Pilate, the morning of the resurrection).
- ՁԷ (line 759): the morning, Isa 26:9. Day and
  night as good and evil works, this life and the
  next, death and resurrection; ten examples of
  morning prayer (the angels' morning and evening
  knowledge, Adam, the Exodus, the manna, the
  cock).
- ՁԸ (line 846): the noon hour, Ps 54:18: ten
  reasons (the noonday demon, the sun at its
  height, Adam's fall and Christ's gall at the
  sixth hour).
- ՁԹ (line 888): grace at table, Ps 144:15. Why
  we bless food before and after; spiritual food
  and drink; breaking bread crosswise; blessing
  the wine cup (Evagrius); the cupbearer stands.
- Ղ (line 951): the evening, Ps 54:18: ten
  reasons; six ways of prayer; why prayers seem
  unheard (twelve reasons) and what a request
  needs.
- ՂԱ (line 1015, group ԳԼՈՒԽ ՂԱ-ՂԵ starts):
  prayer aloud, Ps 141:2: fifteen reasons (the
  living harp, demons fleeing loud praise).
- ՂԲ (line 1043): prayer aloud again: fourteen
  reasons (the drink offerings of Num 15, the
  walls of Jericho); four turns: the bodiless
  into the body, the high into the low, the far
  into the near, the hard into the easy.
- ՂԳ (line 1086): "justice is better than the
  blood of sacrifice", Prov 21:3. Prayer as the
  true, speaking sacrifice; five reasons the
  offerings of the wicked are refused; will and
  time turn good into evil and evil into good.
- ՂԴ (line 1144): joy and sorrow, Phil 4:4. Four
  sorrows, two only apparent; shame and sorrow
  told apart; the Lord's joy and the world's;
  Christ's sorrow over sinners and joy at good
  works; angels rejoice, demons grieve. Line 1211
  closes the sermons on prayer.
- ՂԵ (line 1214): fasting, Zech 8:19 "the fast of
  the fourth, fifth, seventh and tenth". Five
  causes of sickness and health in body and soul;
  four fasts not accepted (forced, for health,
  for money, for show); the four, five, seven and
  ten read as the heart's evils, the senses, the
  seven deadly sins and the Ten Commandments;
  three gains (healing, victory over the flesh,
  a lifted mind). Short, "for much was said in
  the first volume"; ends announcing alms.

## Part 12 · ԳԼՈՒԽ ՂԶ-Ճ and ՃԱ-ՃԵ (sermons 96–105)

Two chapter groups, 1247 lines: five sermons on
the poor and on alms, then five on the church
(the building, its consecration and door, its
people).

- ՂԶ (line 5): the poor, Ps 40:1 "blessed is he
  who considers the poor". Seven ranks of the
  poor like the seven ranks of priests (the poor
  and the fallen rich, orphan and widow, the sick,
  prisoners and captives, strangers, the hungry,
  the dead); why the poor are priests "in power";
  the gleanings left in field and vineyard; four
  reasons to care for animals; alms to all,
  Christian or not; ransoming captives and burying
  the dead above all.
- ՂԷ (line 101): Eccl 11:2 "give a portion to
  seven, and also to eight". God asks a share of
  all he gave (three reasons); what we give him
  is for our own good (the fire and the light);
  four praises of the number seven (rest, the
  "virgin" number, body and soul, Israel's
  feasts); seven and eight as this life and the
  next; sow morning and evening: four kinds of
  men in youth and old age. Breaks off in the
  middle of a sentence (line 183).
- ՂԸ (line 185): Prov 15:27 "by alms and faith
  sins are cleansed". Nature, goodness, gratitude
  and law move us to alms; ten gains of alms and
  ten harms of mercilessness, all from Proverbs
  (the lender to God, mocking the poor: Ham,
  Michal, the boys and Elisha; ransoming the
  condemned as the new law of love).
- ՂԹ (line 360): Luke 6:36 "be merciful". God's
  common and special care: six gifts to the good,
  six "busynesses" to the wicked; why the poor
  exist (the rich are saved through them); alms
  from ill-gotten wealth; to whom first (the just,
  Christians, priests, captives, the dead); alms
  as the second gate of the kingdom and above the
  other virtues (ten reasons; the lamps of the
  virgins; the Last Judgement).
- Ճ (line 478): Prov 27:23 "know the state of
  your flocks". The ranks of the poor as flocks
  (ten likenesses: rams and oxen as priests and
  teachers, clean and unclean beasts); excuses
  answered (the lord who does not work, the poor
  man: spiritual alms); the six works of mercy of
  Matt 25; the seven parts of the blessing on the
  just and six of the sentence on the wicked.
- ՃԱ (line 626, group ԳԼՈՒԽ ՃԱ-ՃԵ starts at
  624): on
  laying the foundations and consecrating a
  church: the stones, the psalms and responses of
  the rite read as the Old Testament, the
  Incarnation and the heavenly city. No verse.
- ՃԲ (line 687): the church, Ps 45:4 "the Most
  High made holy his dwelling". God's dwellings
  for each creature; the tabernacle of Moses (why
  built: ten reasons; ten curtains; four colours
  as elements and virtues; three parts); why God
  is worshipped with bodily things too; why a
  church is blessed (against the Manichaeans and
  those who reject blessings), no water in the
  chalice, re-consecration of a defiled church;
  the hewn stone with six faces.
- ՃԳ (line 858): the new door of a church, Ps
  117:20 "this is the gate of the Lord". Ten
  "doors" (justice, baptism, holy orders, faith
  hope love, penance, fear of God, humility,
  wisdom, Christ, the church door); the senses as
  doors (six likenesses); why a door is blessed
  and anointed in five places (the Passover
  blood).
- ՃԴ (line 949): the people of the church, Song
  1:5 "I am black and beautiful". The church as
  bride (six reasons); the verse read of Adam and
  Eve (the sun that "looked askance" as Satan:
  ten reasons; "my mother's sons" as the demons;
  the vineyard not kept as Eden), of Israel, of
  Christians and of the soul (the face's four
  colours; the senses as vineyards).
- ՃԵ (line 1095): Rev 12:1 "a woman clothed with
  the sun". The woman as the Virgin, the church
  (building, people, the saints in heaven) and
  the earth; the moon as faith and baptism; five
  wonders of birth from the font; three kinds of
  "parents" in the church; the dragon, the souls
  of the dead fought over (Michael and Moses'
  body), the Antichrist's three and a half years;
  the male child as the risen Christ.

## Part 13 · ԳԼՈՒԽ ՃԶ-ՃԺ and ՃԺԱ-ՃԺԵ (sermons 106–115)

Two chapter groups, 1139 lines: five sermons on
the woman of Revelation 17, on virgins and on
Saint Gregory the Illuminator, then five on
rulers, on the rich and the poor, and on the
demons.

- ՃԶ (line 5): Rev 17:3 "a woman sitting on a
  scarlet beast". The beast as Satan, its seven
  heads the seven deadly sins, its ten horns the
  broken commandments; the woman read as the
  harlot (against adorned women in church; the
  three unclean spirits like frogs, five
  likenesses), as the city, as the heretics (six
  kinds of fornication and of virginity; eight
  causes of heresy), as this bodily life and as
  "new Rome"; the ten kings in three lists; the
  Antichrist.
- ՃԷ (line 156): Prov 31:29 "many daughters have
  done worthily". The six kinds of virginity
  again (the tongue: measure, wisdom and order in
  speech); ten reasons why the soul is the bride
  of Christ; the Armenian virgin saints
  (Hripsime, Gayane, Sandukht); true and false
  beauty; the godly wife; husband and wife on one
  road (four kinds of couples); the faithful
  servant.
- ՃԸ (line 309): John 3:6 "that which is born of
  the flesh is flesh". Bodily and spiritual
  offspring compared (ten points); ten miseries
  of marriage (widowhood, death in childbirth);
  the greatness of virginity (incorruption, the
  Father, the Virgin, the angels).
- ՃԹ (line 387, no verse): five gains of
  virginity: it leads back to the first life of
  paradise (ten steps of the fall, climbed back in
  reverse), is like the resurrection, is the art
  of the divine life (the lost coin), purity of
  heart (Elijah and John the Baptist), freedom
  from cares; three kinds of virginity; short
  rules for virgins, widows and the ears.
- ՃԺ (line 526): Gregory the Illuminator, Ps 87:7
  "they laid me in the lowest pit". Gregory as a
  new Adam (eight contrasts, all on the serpent);
  four questions: why the pit (ten reasons), why
  serpents (eight), why Trdat became a boar (ten),
  why the name Grigor (ten: the bird that called
  "gurgur", the six letters, "watchful"); a
  closing prayer to Gregory for the Armenians in
  servitude.
- ՃԺԱ (line 641, group ԳԼՈՒԽ ՃԺԱ-ՃԺԵ starts at
  639): rulers, Prov 11:14 "where there is no
  guidance, they fall like leaves". The ruler as
  the reason, head, eye, tongue and heart of the
  land, spiritual and bodily rule; the Armenians
  without princes; counsel (the Roman senate,
  Saul and David) and just judgement (why the
  Ishmaelites' rule grows); four kinds of wisdom
  in war.
- ՃԺԲ (line 753): Luke 16:19, the rich man.
  God's greatness and man's (seven differences);
  ten reasons why wealth is good; what spoils it
  (unjust gain, greed, waste) and what spoils
  poverty; four gifts like a sword (wisdom,
  beauty, power, wealth); four reasons God gives
  wealth and four he gives poverty.
- ՃԺԳ (line 843): 1 Sam 2:7 "the Lord makes poor
  and makes rich". Good wealth (three ways);
  four reasons God gives it; ten gains of wealth
  and ten miseries of poverty, all from Proverbs
  and Ecclesiastes; ten spiritual gains of
  poverty.
- ՃԺԴ (line 926): Prov 30:7–8 "remove far from me
  vanity and lies". God's grace and the demons'
  deceit; a thousand at the left and ten
  thousand at the right (Ps 90:7): the demons'
  war from both sides; war in three places (this
  life, the stations after death, the judgement:
  Egypt, the desert and Canaan); what "vain" and
  "false" mean; right and left glory.
- ՃԺԵ (line 1028): Prov 30:8 "give me neither
  poverty nor riches". Good, evil and middle
  wealth and poverty; the rich man's grave; good
  and bad bodily wealth and poverty; food and
  clothing as the measure; God keeps the
  Armenians neither rich nor very poor.

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
- Part 8 line 263 reads «2Օ» (an Armenian Օ for
  the zero); written as 20.
- Part 8 line 369: sermon ԿԳ breaks off in the
  middle of a sentence («զի ախտիւ»); the next line
  is the heading of ԿԴ. Kept as it stands.
- Part 8 lines 518 and 552 open a quotation that
  is never closed; the parentheses are kept as in
  the Grabar.
- Part 8 line 711 reads «եհար» ("struck") where
  «եհան» ("brought out") is meant; translated so.
- Part 8 line 905 starts «Երրորդ՝ կերակրէ.
  հերծուածօղքն»; the stray verb is left out.
- Part 8 line 1126 ends in the abbreviation «յաւ»
  (for յաւիտեանս); written out in full.
- Part 9 line 186 ends in a `)` with no opening
  one; kept.
- Part 9 line 338 reads «հարբեցօղ» ("drunkard")
  among the virtues affliction brings: «համբերող»
  is meant and translated.
- Part 9 line 526 reads "a hundred and eighty-five
  troops" without «հազար» (line 532 has it); kept
  as it stands.
- Part 9 line 583 reads «ըստ գտանք»: one word,
  «ըստգտանք» ("reproach", as «ըստգտանիցեն» in
  part 11 line 1081); translated «հանդիմանություն»
  (first rendered «զղջում», corrected with part 11).
- Part 9 line 608 reads «թողութիւն եւ թողութիւն»
  (kept) and «զի ունին միաբանութիւն», translated
  as the question of 2 Cor 6:14 («ի՞նչ
  միաբանություն ունեն»).
- Part 9 line 668 opens a quotation that is never
  closed; kept.
- Part 10 line 6 has the verse and `(Գլուխ. ՀԶ)`
  on one line (no `։` after the verse); kept.
- Part 10 line 75 again reads «ըստ գտանք»
  (as part 9 line 583); translated the same way.
- Part 10 lines 380–420 (on greed, starting in
  the middle of a sentence) and 422–510 (on the
  creation of woman and on marriage, starting
  with a stray «ւ») stand after the doxology of
  ՀԸ; they belong elsewhere but are kept and
  translated where they stand. Line 389 is a
  broken repeat of line 390; kept.
- Part 10 line 391 reads "for Ս reasons"; two
  follow, so «Բ» is meant: translated «երկու».
- Part 10 line 620 repeats «Երկրորդ» for the
  third; kept.
- Part 10 lines 190 and 548 and 555 open
  quotations closed on a later line or not at
  all (lines 191, 556; 548 never); kept.
- Part 10 line 725 reads «Մետանասերորդ» for
  «Մետասաներորդ»: translated «Տասնմեկերորդ».
- Part 10 line 818 reads «պատարագս» where
  «պարագայս» (circumstances) is meant;
  translated so.
- Part 11 line 414 opens with a `)` that has no
  opening; lines 414–417 repeat the verse in a
  garbled way. Kept as they stand.
- Part 11 lines 566 and 587 start with a small
  letter: a sentence cut by a paragraph break;
  kept.
- Part 11 lines 616, 622 and 624 give a number
  that the list after them does not match (seven
  for nine, four for three); kept as numbered.
- Part 11 lines 89, 136, 213 and 1084 open a
  quotation that is never closed, and 768/770,
  1098/1099, 1134/1135, 1268/1271 close it on a
  later line; parentheses kept as in the Grabar.
- Part 12 line 102 reads «Տուր բաժին եւ Բանց»
  for «եօթանց» ("to seven", as in lines 117,
  129, 158) and gives Eccl 11:2 as "the psalm";
  translated «յոթին», "the psalm" kept.
- Part 12 line 98 reads «հանդերձն Ադանիս»;
  translated as Adam's garment of light.
- Part 12 lines 154 and 333 open a quotation
  that is never closed; 440/441, 473–475,
  799/800 and 1241/1243 close theirs on a later
  line;
  parentheses kept as in the Grabar.
- Part 12 line 183 (sermon ՂԷ) breaks off at
  «եւ»; line 185 has the heading of ՂԸ, its verse
  and reference on one line. Kept.
- Part 12 line 295 says the boys who mocked
  Elisha died "in Bethlehem" (Bethel in 2 Kings
  2); kept.
- Part 12 line 567: «աղքատ եւ օդեաց դասքն» is
  translated "the ranks of the poor and of
  orphans", and «երկրաւոր» (earthly) garment as
  «երկնավոր», which the sense needs.
- Part 12 repeats words or phrases at lines 383,
  568, 629, 758, 813, 883, 975, 1030, 1035 and
  1042; kept and translated as they stand.
- Part 12 line 789 reads «երեք ազգ փրկութիւն»
  where the list (foundation, blessing, vessels)
  needs «սրբութիւն»; translated so. Lines 719
  and 789 carry two sentences without a `։`.
- Part 12 line 887 garbles Ps 111:1; translated
  by the sense (blessed is the man who delights
  in his commandments). Line 900 garbles Col 4:6;
  translated as it stands.
- Part 12 lines 1064–1065 go from «Մին» to
  «Երրորդ» with no second; kept.
- Part 12 line 1097 gives the reference as
  «Յայտ. 123. 1» (for 12:1); kept.
- Part 13 line 85 calls the seven-headed beast
  "eight-headed" to match eight causes of heresy;
  line 54 has «մայր կռապաշտութեան» where line 10
  has «պոռնկութեան»; both kept.
- Part 13 lines 98 and 122 end in a `)` with no
  opening one (98 a stray bit of the verse);
  kept. Lines 250, 261 and 294 start with a small
  letter (a sentence cut by a `։`); kept.
- Part 13 line 116 reads «Որպէս մերկն է
  հրեշտակն» for «մեկնէ» ("as the angel
  explains"); translated so. Line 150 reads «ի
  տասն պատճառի» where "divided into ten" is
  meant; translated so.
- Part 13 line 166 repeats a phrase; line 934 is
  a broken repeat of line 933; line 1130 repeats
  «առաքեալն չափ եւ սահման դնէ մեզ». Kept and
  translated as they stand.
- Part 13 line 237 garbles Ps 44:14 («ի վերջ
  աւորս յոսկէ հուռս»); translated by the sense
  (inside, in gold fringes). Line 374 «առաքիաննայ»
  is translated as "is present with" (Gregory of
  Nyssa on virginity).
- Part 13 line 506 quotes 1 Tim 5:6 as «Գիրք
  այրին»; translated «Փափկասուն այրին», as the
  verse reads.
- Part 13 line 532 («զսուրէն ատեաց եւ խոտեաց
  զԱնդրանիկն») is unclear; translated as it
  stands, the two words taken as names.
- Part 13 line 615: Gregory is taken «ի կեսարի
  Աստուծոյ»; translated "God's Caesarea". The
  bird's names «գուրգուր» and «դռուն» are kept.
- Part 13 line 700 has "fifty men" (Ծ) in the
  Roman senate where 1 Macc 8:15 has 320; kept.
- Part 13 line 724 «Նա հաղ» and «ասախ» and
  «շարղ դատաստանի» (the Ishmaelites' laws) are
  translated by the sense (no wrong, order, just
  judgement). Line 730 repeats a clause; kept.
- Part 13 line 1030 gives the reference as
  «Առակ. 3ծ. 8» (Ծ for the zero); written as 30.
- Part 13 line 1016 announces three glories and
  lists two (the second has two kinds); kept.
