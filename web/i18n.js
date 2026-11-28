// nx-gir web: the languages of the pages and their
// words. Every page is under its language:
// /hy/library, /en/read/<book>, /ru/blog. The
// language of the address is LANG; the one picked
// last is kept (LANG_KEY), and a first visit takes
// the browser's. The words of the pages are in UI,
// one table per language with the same keys (a
// test checks it); t(key) gives the word in LANG,
// else in English, else in Armenian. A value may
// be a function of numbers (t("books", 3)).
// The books themselves are not translated here.
"use strict";

// Armenian first (LANGS in nxgir_blog.py)
const LANGS = ["hy", "en", "ru"];
const LANG_KEY = "nxgir-ui-lang";
// the language button's names
const LANG_SHORT = { hy: "Հայ", en: "Eng",
  ru: "Рус" };
const LANG_FULL = { hy: "Հայերեն", en: "English",
  ru: "Русский" };

// the language at the start of a path, or ""
function langOf(path) {
  const m = /^\/([a-z]{2})(?=\/|$)/.exec(path);
  return m && LANGS.includes(m[1]) ? m[1] : "";
}

// the browser's language, if one of ours, else
// Armenian
function browserLang() {
  const all = navigator.languages
    || [navigator.language || ""];
  for (const l of all) {
    const k = String(l).slice(0, 2).toLowerCase();
    if (LANGS.includes(k)) return k;
  }
  return "hy";
}

function savedLang() {
  try {
    const l = localStorage.getItem(LANG_KEY);
    if (LANGS.includes(l)) return l;
  } catch (e) {}
  return "";
}

function saveLang(l) {
  try {
    localStorage.setItem(LANG_KEY, l);
  } catch (e) {}
}

let LANG = langOf(location.pathname) || savedLang()
  || browserLang();

// the word for key in LANG; args go to a function
function t(key, ...args) {
  for (const l of [LANG, "en", "hy"]) {
    const v = UI[l] && UI[l][key];
    if (v == null) continue;
    return typeof v === "function" ? v(...args) : v;
  }
  return key;
}

// Russian plural: one, few, many
function ruN(n, one, few, many) {
  const a = n % 10;
  const b = n % 100;
  if (a === 1 && b !== 11) return one;
  if (a >= 2 && a <= 4 && (b < 12 || b > 14)) {
    return few;
  }
  return many;
}

function enN(n, one, many) {
  return n === 1 ? one : many;
}

const UI = {
  hy: {
    // the menu, the tab bar and the footer
    "nav.home": "Գլխավոր",
    "nav.library": "Գրադարան",
    "nav.continue": "Շարունակել",
    "nav.search": "Որոնում",
    "nav.recent": "Ընթերցումներ",
    "nav.reference": "Տեղեկատու",
    "nav.blog": "Բլոգ",
    "nav.map": "Քարտեզ",
    "nav.map3d": "Եռաչափ քարտեզ",
    "m3.models": "Եռաչափ վերակազմություններ",
    "m3.models.sub": "Վանքեր ու ամրոցներ՝ վերակառուցված հին լուսանկարներից ու հատակագծերից",
    "m3.model": "Եռաչափ մոդել",
    "m3.names": "Անունները",
    "m3.hint3d": "Քաշեք՝ պտտելու համար, երկու մատով՝ մոտեցնելու ու շարժելու. անվան վրա սեղմելով՝ մոտենում եք",
    "m3.onmap": "Եռաչափ քարտեզի վրա",
    "m3.book": "Կարդալ գիրքը",
    "m3.sources": "Աղբյուրներ",
    "m3.sub": "Հայկական լեռնաշխարհը՝ լեռներով ու լճերով",
    "m3.hint": "Քաշեք՝ շարժելու համար, երկու մատով՝ պտտելու ու թեքելու",
    "m3.flat": "Հարթ քարտեզ",
    "m3.nogl": "Ձեր զննարկիչը եռաչափ պատկեր (WebGL) ցույց չի տալիս։",
    "m3.load": "Եռաչափ քարտեզը բեռնվում է…",
    "m3.left": "Պտտել ձախ",
    "m3.right": "Պտտել աջ",
    "m3.above": "Նայել վերևից",
    "m3.side": "Նայել կողքից",
    "m3.badge": "3D",
    "nav.comics": "Կոմիքսներ",
    "nav.features": "Հնարավորություններ",
    "nav.contribute": "Միանալ",
    "nav.news": "Հայտարարություններ",
    "nav.timeline": "Թարմացումներ",
    "nav.stats": "Վիճակագրություն",
    "nav.offline": "Անցանց",
    "nav.menu": "Ցանկ",
    "nav.more": "Ավելին",
    "nav.main": "Հիմնական էջեր",
    "nav.pages": "Էջեր",
    "lang.pick": "Լեզու",
    "foot.tr": "Թարգմանությունները՝ ",
    "foot.pd": " · Գրաբար բնագրերը հանրային"
      + " սեփականություն են",
    "foot.join": "Դառնալ մասնակից",
    "nav.about": "Կայքի մասին",
    "foot.by1": "Մշակել են ",
    "foot.name": "Սերգեյ Օհանյանը",
    "foot.by2": " և Claude-ը",
    "ab.title": "Նախագծի մասին",
    "ab.sub":
      "Նախագիրը (nxGir) գրաբար՝ հին հայերեն գրքերի "
      + "անվճար գրադարան և ընթերցարան է։ "
      + "Յուրաքանչյուր բառի իմաստը կարելի է տեսնել, "
      + "իսկ պատրաստ թարգմանությունները կարդացվում "
      + "են բնագրի կողքին։",
    "ab.what.h": "Հին գրքերի ընթերցարան",
    "ab.what.t":
      "Նախագիրը հավաքում է գրաբարով գրված գրքեր՝ "
      + "առաջին պատմիչներից մինչև ավելի ուշ "
      + "ժամանակագրություններ ու մեկնություններ։ "
      + "Դրանք կարելի է կարդալ դիտարկիչում, "
      + "հեռախոսով կամ տերմինալում. տեքստը պարզ "
      + "յունիկոդ է, ոչինչ տեղադրել պետք չէ։",
    "ab.name.h": "Անունը",
    "ab.name.t":
      "Նախագիր՝ «նախ» (առաջին) և «գիր» (տառ, "
      + "գրություն) բառերից։ Անգլերեն նախագիծը "
      + "կոչվում է nxGir։",
    "ab.do.h": "Ինչ կարելի է անել",
    "ab.do.t":
      "Բացեք գիրքը և սեղմեք բառի վրա՝ նրա իմաստն "
      + "ու ձևերը տեսնելու համար։ Կարդացեք գրաբարը "
      + "ժամանակակից հայերենի կողքին։ Որոնեք ամբողջ "
      + "գրադարանում։ Քարտեզի վրա հետևեք գրքերի "
      + "վայրերին։ Կարդացեք բլոգը և կոմիքսները։",
    "ab.open.h": "Ազատ և բաց",
    "ab.open.t":
      "Գրաբար բնագրերը հանրային սեփականություն են։ "
      + "Մեր թարգմանությունները տարածվում են CC "
      + "BY-SA 4.0 լիցենզիայով և սկսվում են որպես "
      + "մեքենայական սևագրեր. դրանք նշված են, մինչև "
      + "մարդը վերանայի։ Կոդը և տեքստերը GitHub-ում "
      + "են, և ցանկացողը կարող է օգնել։",
    "ab.author.h": "Հեղինակը",
    "ab.author.t":
      "Նախագիրը ստեղծում են Սերգեյ Օհանյանը և "
      + "Claude-ը՝ Anthropic-ի արհեստական "
      + "բանականության օգնականը, որն օգնում է գրել "
      + "կոդը և թարգմանությունների առաջին սևագրերը։ "
      + "Հարցերը, ուղղումներն ու գաղափարները "
      + "ողջունվում են։",
    "ab.jump": "Կապ ↓",
    "ct.email": "Էլ. փոստ",
    "ct.github": "GitHub",
    "ct.instagram": "Instagram",
    "home": "← Գլխավոր",
    "back.library": "Վերադառնալ գրադարան",
    "error": "Ինչ-որ բան այն չէ",
    "title.top": "Գրաբար գրքեր՝ բառ առ բառ",
    "theme.light": "Լուսավոր",
    "theme.dark": "Մուգ",
    "theme.black": "Սև",
    "video.play": "Դիտել տեսանյութը",
    "video.note": "Տեսանյութը բեռնվում է YouTube-ից միայն սեղմելուց հետո։",
    "video.youtube": "Դիտել YouTube-ում",
    "theme.pick": (now, paper) => "Ոճ՝ " + now
      + (paper ? " · " + paper : ""),
    "theme.system": "Ինչպես համակարգում",
    "theme.themes": "Ոճ",
    "theme.menu": "Ոճ և թուղթ",
    "phone": "Հեռախոսի տեսք",
    "phone.on": "Հեռախոսի տեսք՝ միացված (սեղմեք՝"
      + " լայն տեսքի համար)",
    // counts
    "n.book": (n) => n + " գիրք",
    "n.part": (n) => n + " մաս",
    "n.file": (n) => n + " ֆայլ",
    "n.folder": (n) => n + " թղթապանակ",
    "n.line": (n) => n + " տող",
    "n.word": (n) => n + " բառ",
    "n.day": (n) => n + " օր",
    // the top page's banners
    "dot": "։",
    "n.heading": (n) => n + " վերնագիր",
    "dev.title": "Կայքը շարունակաբար զարգանում է",
    "dev.text": "Ամեն ժամ ավելացնում ենք նոր"
      + " հնարավորություններ ու բարելավումներ։"
      + " Պարբերաբար այցելեք մեզ՝ տեսնելու, թե ինչ"
      + " նորություններ կան։",
    "dev.more": "Տեսեք վերջին թարմացումները →",
    "dev.mail": "Հարցեր կամ առաջարկնե՞ր ունեք։"
      + " Գրեք մեզ՝ ",
    "join.title": "Միացեք Նախագրին",
    "join.text": "Օգնեք թարգմանել և խմբագրել առկա"
      + " թարգմանությունները",
    "join.go": "Ինչպես միանալ →",
    "mapb.text": "Պատմական դեպքերի վայրերը քարտեզի վրա",
    "mapb.go": "Բացել քարտեզը →",
    "top.about": "Նախագծի մասին →",
    // readings
    "ago.now": "հենց նոր",
    "ago.min": (n) => n + " րոպե առաջ",
    "ago.hour": (n) => n + " ժամ առաջ",
    "ago.yesterday": "երեկ",
    "ago.days": (n) => n + " օր առաջ",
    "shelf.grabar": "Գրաբար",
    "shelf.ashkharhabar": "Աշխարհաբար",
    "cancel": "Չեղարկել",
    "remove": "Հեռացնել",
    "forget.title": "Հեռացնել ցանկից",
    "forget.q": "Հեռացնե՞լ ցանկից",
    "forget.note": "Գիրքը չի ջնջվի։ Որտեղ կանգ եք առել՝"
      + " կմնա, և նորից բացելիս այն կվերադառնա ցանկ։",
    "recent.go": "Շարունակել կարդալ",
    "recent.all": "Բոլոր ընթերցումները →",
    "recent.h1": "Իմ ընթերցումները",
    "recent.static": "Պահված է միայն այս դիտարկիչում",
    "recent.local": "Այս համակարգչում",
    "recent.none": "Դեռ ոչինչ չեք կարդացել։ ",
    // a book's page
    "pct.read": (n) => n + "% կարդացված",
    "part.n": (n) => "Մաս " + n,
    "vol.done": (done, total) => " · թարգմանված "
  + done + "/" + total,
    "vol.go": "Շարունակել → ",
    "vol.start": "Սկսել կարդալ →",
    "new.text": "+ Նոր տեքստ",
    "no.books": "Այստեղ գրքեր չկան։",
    // the welcome on the top page
    "intro.hi": "Ողջույն",
    "intro.q1": "Ինչի՞ համար է կայքը։",
    "intro.a1": "Այստեղ կարող եք կարդալ գրաբարով՝ դասական"
      + " հայերենով գրված գրքեր։",
    "intro.q2": "Ինչպե՞ս իմանալ բառի իմաստը։",
    "intro.a2": "Սեղմեք բառի վրա, և կտեսնեք դրա իմաստը,"
      + " բառարանային ձևը և այն մյուս տեղերը, որտեղ բառը"
      + " հանդիպում է գրքում։",
    "intro.q3": "Ի՞նչ փոփոխություններ կան կայքում։",
    "intro.all": "Բոլոր իրադարձությունները →"
      + " Թարմացումներ",
    "intro.q4": "Ո՞վ է թարգմանել։",
    "intro.a4": "Թարգմանությունը մեքենայական է և դեռ"
      + " ստուգված չէ մասնագետի կողմից։",
    "intro.q5": "Ինչպե՞ս կապվել։",
    "intro.a5": "Հարցերի, առաջարկների կամ սխալների մասին"
      + " գրեք նախագծի հեղինակին՝ ",
    "intro.contacts": "Բոլոր կոնտակտները →",
    "tip.label": "Հուշում",
    "tip.lib.a": "Գրադարանում սեղմեք",
    "tip.lib.b": "հեղինակի անվան կողքին՝ նրա մասին"
      + " կարդալու, կամ",
    "tip.lib.c": "գրքի կողքին՝ գրքի մասին կարդալու։",
    // the Library
    "lib.done": "թարգմանված",
    "lib.bookpage": "Գրքի էջը →",
    "lib.none": "Գրքեր դեռ չկան։",
    "lib.part": (p) => "մաս " + p + " · ",
    "lib.noread": "Դեռ ոչինչ չեք կարդում։ Բացեք գիրքը՝ այն"
      + " կհայտնվի այստեղ։",
    "lib.all": "Բոլոր գրքերը",
    "lib.starred": "★ Ընտրված",
    "lib.reading": "Ընթերցվող",
    "lib.marks": "Էջանիշեր",
    "lib.nomarks": "Էջանիշեր դեռ չկան։ Գրքում սեղմեք բառի վրա,"
      + " ապա՝ ☆ Էջանիշ։",
    "lib.nostars": "Ընտրված գրքեր դեռ չկան։ Գրքի կողքի"
      + " ☆-ով ավելացրեք այստեղ։",
    "star.off": "Հանել աստղը",
    "star.on": "Աստղանշել",
    "lib.sub": (n) => "Գրաբար գրքեր · " + n + " · ",
    "lib.find": "Գտնել հեղինակ կամ գիրք",
    "lib.tip": "Գրքերի ներսում տեքստ փնտրելու համար"
      + " օգտվեք ամբողջական որոնումից։",
    "lib.tipgo": "Բացել որոնումը",
    "prev": "Նախորդը",
    "next": "Հաջորդը",
    "clear": "Մաքրել",
    "none": "Չկա",
    // dates and the Timeline
    "months": ["հնվ", "փտվ", "մրտ", "ապր", "մյս",
  "հնս", "հլս", "օգս", "սեպ", "հոկ", "նոյ",
  "դեկ"],
    "kind.Start": "Սկիզբ",
    "kind.Books": "Գրքեր",
    "kind.Translation": "Թարգմանություն",
    "kind.Reader": "Ընթերցիչ",
    "kind.Dictionary": "Բառարան",
    "kind.Texts": "Տեքստեր",
    "kind.Site": "Կայք",
    "all": "Բոլորը",
    "show": "Ցույց տալ",
    "read.go": "Կարդալ →",
    "open.go": "Բացել →",
    "tl.day": (n) => " · օր " + n,
    "tl.sub": "Ինչպես է աճել nxGir-ը՝ առաջին տողից մինչև"
      + " այսօր",
    "tl.days": "օր",
    "tl.books": "գրաբար գիրք",
    "tl.parts": "թարգմանված մաս",
    "tl.next": "Հաջորդը",
    "tl.limits": "Որքան ենք մոտ սահմաններին →"
      + " Վիճակագրություն",
    "tl.en": "Իրադարձությունները դեռ միայն անգլերեն են։",
    // the Contribute page
    "co.title": "Դառնալ մասնակից",
    "co.alt": "Ընթերցող ծառի տակ՝ նոութբուքով, հետևում"
      + " վանք և լեռ",
    "co.mission": "Մեր առաքելությունը՝ հին հայերեն գրքերը"
      + " բացել յուրաքանչյուր ընթերցողի համար՝ բառ առ"
      + " բառ, այն լեզվով, որով այսօր խոսում ենք։",
    "co.aside": "Պատկերացրեք գրչատուն՝ նոր աշակերտով․"
      + " արհեստական բանականությունն արագ է արտագրում և"
      + " երբեք մոմ չի խնդրում, բայց վանականը դեռ պետք է"
      + " ստուգի յուրաքանչյուր տող։",
    "co.sub": "Նախագիրը բաց նախագիծ է՝ հին հայերեն գրքեր՝"
      + " բառ առ բառ, և դրանց թարգմանությունները"
      + " ժամանակակից հայերենով, ազատ՝ յուրաքանչյուրի"
      + " համար։ Այն աճում է օգնողների շնորհիվ։",
    "co.ways": "Ինչպես մասնակցել",
    "co.ways.where": "Ինչով",
    "co.ways.how": "Ինչպես",
    "co.w.mobile": "Հեռախոս՝ ChatGPT հավելվածով",
    "co.w.mobile.how": "Ավելացրեք GitHub հավելումը և"
      + " խնդրեք ChatGPT-ին բացել pull request։"
      + " Համակարգիչ և git պետք չեն։",
    "co.w.mobile.go": "Քայլերը՝ նկարներով",
    "co.w.pc": "Համակարգիչ",
    "co.w.pc.how": "ChatGPT-ն դիտարկչով՝ նույն GitHub"
      + " հավելումով, կամ git-ով. պատճենեք շտեմարանը,"
      + " ավելացրեք ձեր ֆայլը և բացեք pull request։",
    "co.w.pc.go": "Ձեռնարկ՝ CONTRIBUTING.md",
    "co.gh": "Նախագիծը GitHub-ում",
    "co.lic1": "Թարգմանությունները տարածվում են ",
    "co.lic2": " լիցենզիայով. թարգմանություն ուղարկելով՝"
      + " համաձայնում եք այն հրապարակել այս լիցենզիայով։",
    // the Features page
    "nothing": "Այստեղ դեռ ոչինչ չկա։",
    // the Statistics page
    "st.measured": "չափված ",
    "st.of": " / ",
    "lv.ok": "Նորմալ",
    "lv.watch": "Ուշադրություն",
    "lv.near": "Սահմանին մոտ",
    "st.cols": ["Ամսաթիվ", "Commit", "Տեքստ", "Կայք",
  "Git", "Կառուցում"],
    "st.none": "Վիճակագրություն այստեղ չկա՝ ",
    "st.sub": (d) => "Որքան է պարունակում գրադարանը, և"
  + " որքան է այն մոտ GitHub-ի ու հեռախոսի"
  + " սահմաններին։ Չափված է " + d
  + ", commit ",
    "st.files": "գրքի ֆայլ",
    "st.text": "տեքստ",
    "st.words": "տարբեր բառ",
    "st.tr": "թարգմանված",
    "st.closest": "Ամենամոտը՝ ",
    "st.at": (n) => "՝ սահմանի " + n + "%-ը։",
    "st.limits": "Սահմաններ",
    "st.history": "Պատմություն",
    "st.what": "Ինչ է նշանակում յուրաքանչյուր սահման՝ ",
    "st.folders": "Թղթապանակներ",
    // the Offline page
    "off.h1": "Կարդալ առանց ցանցի",
    "off.here": "Այս օրինակն արդեն աշխատում է այս"
      + " սարքում․ ցանց պետք չէ։",
    "off.about": "մոտ 80 ՄԲ",
    "off.save": "Պահել առանց ցանցի համար",
    "off.list": "Պահվում է․ ֆայլերի ցանկը բեռնվում է…",
    "off.saving": "Պահվում է…",
    "off.busy": (d, n, p) => "Պահվում է․ " + d + " / " + n
  + " ֆայլ (" + p + "%)։ Կարող եք շարունակել"
  + " կարդալ։",
    "off.done": (n) => "Պահված է․ բոլոր " + n + " ֆայլերը"
  + " այս սարքում են։ Այն ինքն իրեն թարմացնում"
  + " է, երբ ցանցում եք։",
    "off.remove": "Ջնջել պահված օրինակը",
    "off.part": 
      (d, n) => "Մասամբ պահված է․ " + d + " / " + n
        + " ֆայլ։ Սեղմեք՝ շարունակելու համար։",
    "off.go": "Շարունակել պահելը",
    "off.nothing": "Դեռ ոչինչ պահված չէ։",
    "off.offnow": "Գրքերի պահումն առայժմ անջատված է։",
    "off.install": "Տեղադրել հավելվածը",
    "off.how": "Chrome-ում՝ ⋮ ցանկը, ապա «Տեղադրել"
      + " հավելվածը» (կամ «Ավելացնել գլխավոր էկրանին»)։"
      + " iPhone-ում՝ Safari-ում «Կիսվել», ապա «Գլխավոր"
      + " էկրանին»։",
    "off.ways": (n) => n + " եղանակ՝ կարդալու առանց"
  + " ցանցի։",
    "off.h_app": "1. Տեղադրել հավելվածը",
    "off.app": "Կայքը ստանում է իր պատկերակը և բացվում է"
      + " իր պատուհանում, ինչպես հավելված։",
    "off.h_save": "2. Պահել գրքերն այս դիտարկիչում",
    "off.books": (mb) => "Բոլոր գրքերը, թարգմանությունները"
  + " և բառերի իմաստները՝ " + mb + "։ Դրանք"
  + " մնում են այս սարքի դիտարկիչում և"
  + " փոխարինվում են նորերով, երբ կայքը"
  + " փոխվում է։",
    "off.h_zip": "3. Ներբեռնել կայքը որպես ֆայլ",
    "off.zip1": (s) => "Մեկ zip ֆայլ (" + s + ")։ Բացեք այն"
  + " և գործարկեք ",
    "off.zip2": " (պետք է Python 3, այն Termux-ում էլ"
      + " կա)։ Այն ինքն իրեն չի թարմացվում։",
    "off.dl": "Ներբեռնել zip-ը",
    // search
    "s.box": "Որոնել գրքերում",
    "s.where": (part, line) => (part ? "մաս " + part
  + " · " : "") + "տող " + line,
    "s.alllines": (n) => "Բոլոր " + nf(n) + " տողերը →",
    "s.lines": (n) => nf(n) + " տող",
    "s.books": (n) => nf(n) + " գիրք",
    "s.authors": (n) => nf(n) + " հեղինակ",
    "s.allbooks": (n) => "Բոլոր " + n + " գրքերը →",
    "s.names": "Հեղինակներ և գրքեր",
    "s.hint": "Գրեք բառը գրաբար կամ աշխարհաբար"
      + " ուղղագրությամբ․ թագավոր-ը կգտնի նաև թագաւոր-ը։",
    "s.wait": "Որոնվում է…",
    "s.common": "․ շատ հաճախ է, որոնվում են մյուս բառերը։",
    "s.common1": "․ շատ հաճախ է․ ավելացրեք ևս մի բառ։",
    "s.all": "Բոլորը",
    "s.forms": "Որոնել բառաձևերը",
    "s.spelled": "Գրելաձևեր",
    "s.open": "Բացել բոլորը",
    "s.close": "Փակել բոլորը",
    "s.found": "Տողեր",
    "s.notin": "Այստեղ չկա․ նայեք մյուս ֆիլտրերը։",
    "s.none": "Չգտնվեց։",
    "s.library": "Որոնել ամբողջ գրադարանում",
    "s.sel": "Որոնել գրադարանում՝ ",
    "s.back": "Արդյունքներին",
    "s.q": "Որոնում՝ ",
    "s.nth": (r, n) => "արդյունք " + nf(r) + " / " + nf(n),
    // the reader
    "close": "Փակել",
    "r.meanin": "Իմաստները՝",
    "r.only": "Միայն այստեղ",
    "r.places": (at, n) => at + " / " + n + " տեղ",
    "r.inbook": "Այս գրքում",
    "r.prevplace": "Նախորդ տեղը",
    "r.nextplace": "Հաջորդ տեղը",
    "blog.copy": "Պատճենել",
    "r.copied": "✓ Պատճենված է",
    "r.linkto": "Հղում այս տողին",
    "r.link": "🔗 Հղում տողին",
    "r.fix": "Ճիշտ տեքստը",
    "r.comment": "Մեկնաբանություն",
    "r.gh": "Ուղարկել GitHub-ով",
    "r.mail": "Ուղարկել էլ. փոստով",
    "r.report": "Հաղորդել սխալի մասին",
    "r.should": "Ինչպես պետք է լինի",
    "r.note": "Մեկնաբանություն, աղբյուր (ըստ ցանկության)",
    "r.ghhow": "GitHub-ը բացում է նոր issue, որը կարող եք"
      + " կարդալ և ուղարկել (պետք է հաշիվ)։ Առանց հաշվի՝"
      + " ուղարկեք էլ. փոստով։",
    "r.marked": "★ Էջանշված է",
    "r.mark": "☆ Էջանիշ",
    "r.addnote": "✎ Նշում",
    "r.looking": "Որոնվում է…",
    "r.failed": "Չհաջողվեց գտնել՝ ",
    "r.abbr": "Հապավում",
    "r.meaning": "Իմաստը",
    "r.noword": "Բառարանում չկա։",
    "r.marks": "Էջանիշներ",
    "r.notes": "Նշումներ",
    "r.back": "Վերադառնալ թղթապանակ",
    "r.backto": (x) => "Վերադառնալ՝ " + x,
    "r.contents": "Բովանդակություն",
    "r.edit": "Խմբագրել տեքստը",
    "r.par": "Զուգահեռ",
    "r.two": "Ցույց տալ երկու տարբերակները",
    "r.beside": (x) => "Կողք կողքի՝ " + x,
    "r.under": "Յուրաքանչյուր տող իր զույգի տակ",
    "r.stacked": "Տողերը մեկը մյուսի տակ (սեղմեք՝ կողք"
      + " կողքի)",
    "r.side": "Կողք կողքի (սեղմեք՝ տողերը մեկը մյուսի տակ)",
    "r.settings": "Տեքստի կարգավորումներ",
    "r.text": "Տեքստ",
    "r.smaller": "Փոքր տառեր",
    "r.bigger": "Մեծ տառեր",
    "r.center": "Տեքստը կենտրոնում",
    "r.centered": "Տեքստը կենտրոնում է",
    "r.left": "Տեքստը ձախից",
    "r.spacing": (k, n) => "Տողերի միջակայք " + k + " / "
  + n,
    "r.widest": "Ամենալայն միջակայքը (սեղմեք՝ սովորական)",
    "r.more": "Տողերի միջակայք (սեղմեք՝ ավելի)",
    "r.sent": "Յուրաքանչյուր նախադասություն նոր տողից",
    "r.apart": "Նախադասությունները առանձին (սեղմեք՝"
      + " միացնել)",
    "r.written": "Տեքստը՝ ինչպես գրված է (սեղմեք՝"
      + " նախադասություններով)",
    "r.width": "Տեքստը ամբողջ լայնքով",
    "r.whole": "Ամբողջ լայնքով (սեղմեք՝ սյունակ)",
    "r.column": "Տեքստը սյունակում (սեղմեք՝ ամբողջ"
      + " լայնքով)",
    "r.paged": "Երկար մասը կարդալ էջերով",
    "r.font": "Տեքստի տառատեսակը",
    "r.tile.center": "Կենտրոն",
    "r.tile.spacing": "Միջտող",
    "r.tile.sent": "Տողատել",
    "r.tile.width": "Լայնք",
    "nav.settings": "Կարգավորումներ",
    "set.sub": "Ինչպես են երևում գրքերը այս սարքում",
    "set.size": "Տառերի չափը",
    "set.spacing": "Տողերի միջակայք",
    "set.reading": "Կարդալիս",
    "set.kept": "Կարգավորումները պահվում են այս զննարկչում։",
    "set.site": "Կայքը",
    "set.statsnote": "Որքան է պարունակում գրադարանը",
    "set.back": "Վերադառնալ գրքին",
    "set.undernote": "Թարգմանությունը կողքին՝ լայն էկրանին",
    "set.barsnote": "Ներքև ոլորելիս վերևի գործիքները և"
      + " ներքևի ներդիրները հեռանում են, վերև ոլորելիս՝"
      + " վերադառնում",
    "r.bars": "Թաքցնել վերևի և ներքևի վահանակները ոլորելիս",
    "r.tile.layout": "Իրար տակ",
    "r.saved": "Էջանիշներ և նշումներ",
    "r.paper": "Էջի թուղթը",
    "paper.plain": "Պարզ",
    "paper.papyrus": "Պապիրուս",
    "paper.parchment": "Հին գիրք",
    "paper.vellum": "Մագաղաթ",
    "paper.candle": "Մոմի լույսով",
    "r.fontsample": "Նախագիր",
    "r.fail": "Չհաջողվեց պահել՝ ",
    "r.line": (n) => "տող " + n,
    "r.prevpage": "Նախորդ էջը",
    "r.nextpage": "Հաջորդ էջը",
    "r.page": (k, n) => "Էջ " + k + " / " + n,
    "r.chapter": "Գլուխ",
    "r.local": "Պահվում է միայն այս զննարկչում։",
    "r.nosave": "Չհաջողվեց պահել։",
    "r.nomarks": "Էջանիշներ դեռ չկան։ Սեղմեք բառի վրա,"
      + " ապա՝ ☆ Էջանիշ։",
    "r.nonotes": "Նշումներ դեռ չկան։ Սեղմեք բառի վրա,"
      + " ապա՝ ✎ Նշում։",
    "edit": "Խմբագրել",
    "delete": "Ջնջել",
    "r.delnote": "Ջնջե՞լ այս նշումը։",
    "r.notebox": "Նշում",
    "save": "Պահել",
    "r.editnote": "Խմբագրել նշումը",
    "r.newnote": "Նոր նշում",
    "r.pages": "Էջեր",
    "r.prev": "‹ Նախորդը",
    "r.next": "Հաջորդը ›",
    "r.help": "Օգնել խմբագրել",
    "r.parts": "Մասեր",
    "r.partprev": (n, total) => "← Մաս " + n + " / " + total
,
    "r.partnext": (n, total) => "Մաս " + n + " / " + total
  + " →",
    "r.allparts": (n) => "Բոլոր " + n + " մասերը՝ ",
    "r.word": "Բառ",
    "r.read": "Կարդացված",
    "tr.machine": (m) => "Թարգմանությունը՝ Նախագիր ·"
  + " մեքենայական (" + m + "), դեռ չխմբագրված",
    "tr.review": (m, who) => "Թարգմանությունը՝ Նախագիր ·"
  + " մեքենայական (" + m + "), խմբագրում են՝ "
  + who,
    "tr.reviewed": (m, who) => "Թարգմանությունը՝ Նախագիր · "
  + m + ", խմբագրել են՝ " + who,
    // the editor (nxgir web only)
    "ed.leave": "Դուրս գա՞լ առանց փոփոխությունները"
      + " պահելու։",
    "ed.md": "Պահվում է ճիշտ այնպես, ինչպես գրված է։"
      + " Markdown՝ # վերնագիր, > մեջբերում, **թավ**,"
      + " *շեղ*։",
    "ed.edit": (x) => "Խմբագրել՝ " + x,
    "ed.reload": "Նորից բեռնել ֆայլը",
    "ed.saving": "Պահվում է…",
    "ed.saved": "Պահված է՝ ",
    "ed.changed": "Ֆայլը սկավառակի վրա փոխվել է այն"
      + " բացելուց հետո (git pull?), ուստի չպահվեց։ Ձեր"
      + " տեքստը դեռ այստեղ է․ պատճենեք այն, ապա նորից"
      + " բեռնեք ֆայլը։",
    "ed.not": "Չպահվեց՝ ",
    "ed.done": "Պատրաստ է",
    "ed.new": "Նոր տեքստ",
    "ed.title": "# Վերնագիր (Սաղ 118:33–37)\n\nՏեքստը…",
    "ed.one": "Մեկ տեքստ՝ մեկ ֆայլում, անվանված ըստ"
      + " հատվածի և կարճ վերնագրի՝ լատինատառ։ ",
    "ed.file": "Ֆայլի անունը",
    "ed.create": "Ստեղծել",
    // errors
    "err.static": "Չկա հրապարակված օրինակում",
    "err.theme": "Այդպիսի թեմա չկա",
    "err.post": "Այդպիսի գրառում չկա",
    "err.series": "Այդպիսի շարք չկա",
    "err.news": "Այդպիսի հայտարարություն չկա",
    // the reader
    "r.tap": " · սեղմեք բառի վրա՝ իմաստը տեսնելու համար",
  },
  en: {
    "nav.home": "Home",
    "nav.library": "Library",
    "nav.continue": "Continue",
    "nav.search": "Search",
    "nav.recent": "Readings",
    "nav.reference": "Reference",
    "nav.blog": "Blog",
    "nav.map": "Map",
    "nav.map3d": "3D map",
    "m3.models": "3D reconstructions",
    "m3.models.sub": "Monasteries and castles, rebuilt from old photographs and plans",
    "m3.model": "3D model",
    "m3.names": "Names",
    "m3.hint3d": "Drag to turn; two fingers (or the right button) zoom and move; tap a name to go closer",
    "m3.onmap": "On the 3D map",
    "m3.book": "Read the book",
    "m3.sources": "Sources",
    "m3.sub": "The Armenian Highland, its mountains and lakes",
    "m3.hint": "Drag to move; two fingers (or the right button) turn and tilt",
    "m3.flat": "Flat map",
    "m3.nogl": "Your browser cannot show 3D (WebGL).",
    "m3.load": "Loading the 3D map…",
    "m3.left": "Turn left",
    "m3.right": "Turn right",
    "m3.above": "Look from above",
    "m3.side": "Look from the side",
    "m3.badge": "3D",
    "nav.comics": "Comics",
    "nav.features": "Features",
    "nav.contribute": "Join",
    "nav.news": "Announcements",
    "nav.timeline": "Timeline",
    "nav.stats": "Statistics",
    "nav.offline": "Offline",
    "nav.menu": "Menu",
    "nav.more": "More",
    "nav.main": "Main pages",
    "nav.pages": "Pages",
    "lang.pick": "Language",
    "foot.tr": "Translations ",
    "foot.pd": " · Grabar texts in the public domain",
    "foot.join": "Become a contributor",
    "nav.about": "About",
    "foot.by1": "Developed by ",
    "foot.name": "Sergey Ohanyan",
    "foot.by2": " and Claude",
    "ab.title": "About the project",
    "ab.sub":
      "Նախագիր (nxGir) is a free library and "
      + "reader of books in Grabar, Classical "
      + "Armenian. Every word can be looked up, and "
      + "ready translations are read beside the "
      + "original.",
    "ab.what.h": "A reader for old Armenian books",
    "ab.what.t":
      "nxGir collects books written in Grabar, "
      + "from the first historians to later "
      + "chronicles and commentaries. You can read "
      + "them in a browser, on a phone or in the "
      + "terminal; the text is plain Unicode, and "
      + "there is nothing to install.",
    "ab.name.h": "The name",
    "ab.name.t":
      "Նախագիր is made of նախ, “first”, and գիր, "
      + "“letter, script”. In English the project is "
      + "called nxGir.",
    "ab.do.h": "What you can do",
    "ab.do.t":
      "Open a book and click a word to see its "
      + "meaning and forms. Read Grabar beside a "
      + "Modern Armenian translation. Search the "
      + "whole Library. Follow the places of the "
      + "books on the map. Read the blog and the "
      + "comics.",
    "ab.open.h": "Free and open",
    "ab.open.t":
      "The Grabar texts are in the public domain. "
      + "Our translations are under CC BY-SA 4.0 and "
      + "begin as machine drafts; they are marked as "
      + "such until a person reviews them. The code "
      + "and the texts are on GitHub, and anyone can "
      + "help.",
    "ab.author.h": "The author",
    "ab.author.t":
      "nxGir is made by Sergey Ohanyan together "
      + "with Claude, an AI assistant made by "
      + "Anthropic, which helps write the code and "
      + "the first drafts of the translations. "
      + "Questions, corrections and ideas are "
      + "welcome.",
    "ab.jump": "Contact ↓",
    "ct.email": "Email",
    "ct.github": "GitHub",
    "ct.instagram": "Instagram",
    "home": "← Home",
    "back.library": "Back to the library",
    "error": "Something went wrong",
    "title.top": "Grabar books, word by word",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "theme.black": "Black",
    "video.play": "Play the video",
    "video.note": "The video loads from YouTube only when you play it.",
    "video.youtube": "Watch on YouTube",
    "theme.pick": (now, paper) => "Theme: " + now
      + (paper ? " · " + paper : ""),
    "theme.system": "As the system",
    "theme.themes": "Theme",
    "theme.menu": "Theme and paper",
    "phone": "Phone view",
    "phone.on": "Phone view: on (click for the"
      + " wide view)",
    "n.book": (n) => n + enN(n, " book", " books"),
    "n.part": (n) => n + enN(n, " part", " parts"),
    "n.file": (n) => n + enN(n, " file", " files"),
    "n.folder": (n) => n
      + enN(n, " folder", " folders"),
    "n.line": (n) => n + enN(n, " line", " lines"),
    "n.word": (n) => n + enN(n, " word", " words"),
    "n.day": (n) => n + enN(n, " day", " days"),
    // the top page's banners
    "dot": ".",
    "n.heading": (n) => n
  + enN(n, " heading", " headings"),
    "dev.title": "Under active development",
    "dev.text": "New features are added every day. Come"
      + " back often to see what is new.",
    "dev.more": "See what is new on the timeline →",
    "dev.mail": "Questions or ideas? Write to ",
    "join.title": "Join nxGir",
    "join.text": "Help translate and edit the translations"
      + " we have",
    "join.go": "How to join →",
    "mapb.text": "The places of history on the map",
    "mapb.go": "Open the map →",
    "top.about": "About the project →",
    // readings
    "ago.now": "just now",
    "ago.min": (n) => n + " min ago",
    "ago.hour": (n) => n + enN(n, " hour", " hours")
  + " ago",
    "ago.yesterday": "yesterday",
    "ago.days": (n) => n + enN(n, " day", " days")
  + " ago",
    "shelf.grabar": "Grabar",
    "shelf.ashkharhabar": "Modern Armenian",
    "cancel": "Cancel",
    "remove": "Remove",
    "forget.title": "Remove from the list",
    "forget.q": "Remove from the list?",
    "forget.note": "The book is not deleted. Where you"
      + " stopped is kept, and opening it again brings it"
      + " back to the list.",
    "recent.go": "Continue reading",
    "recent.all": "All readings →",
    "recent.h1": "My readings",
    "recent.static": "Kept in this browser only",
    "recent.local": "On this computer",
    "recent.none": "Nothing read yet. ",
    // a book's page
    "pct.read": (n) => n + "% read",
    "part.n": (n) => "Part " + n,
    "vol.done": (done, total) => " · translated "
  + done + "/" + total,
    "vol.go": "Continue → ",
    "vol.start": "Start reading →",
    "new.text": "+ New text",
    "no.books": "No books here.",
    // the welcome on the top page
    "intro.hi": "Welcome",
    "intro.q1": "What is the site for?",
    "intro.a1": "Here you can read books written in"
      + " Grabar, Classical Armenian.",
    "intro.q2": "How do I find what a word means?",
    "intro.a2": "Tap a word to see its meaning, its"
      + " dictionary form and the other places in the book"
      + " where it is found.",
    "intro.q3": "What is new on the site?",
    "intro.all": "All events → Timeline",
    "intro.q4": "Who translated the books?",
    "intro.a4": "The translations are made by machine and"
      + " not yet checked by a specialist.",
    "intro.q5": "How can I get in touch?",
    "intro.a5": "Write to the author of the project with"
      + " questions, ideas or mistakes found: ",
    "intro.contacts": "All contacts →",
    "tip.label": "Tip",
    "tip.lib.a": "In the Library, tap",
    "tip.lib.b": "beside an author's name to read about"
      + " the author, and",
    "tip.lib.c": "beside a book to read about the book.",
    // the Library
    "lib.done": "translated",
    "lib.bookpage": "Book page →",
    "lib.none": "No books yet.",
    "lib.part": (p) => "part " + p + " · ",
    "lib.noread": "Nothing being read yet. Open a book and"
      + " it shows here.",
    "lib.all": "All books",
    "lib.starred": "★ Starred",
    "lib.reading": "Reading",
    "lib.marks": "Bookmarks",
    "lib.nomarks": "No bookmarks yet. In a book tap a word,"
      + " then ☆ Bookmark.",
    "lib.nostars": "No starred books yet. Add them here"
      + " with the ☆ beside a book.",
    "star.off": "Take the star off",
    "star.on": "Star",
    "lib.sub": (n) => "Grabar books · " + n + " · ",
    "lib.find": "Find an author or a book",
    "lib.tip": "To search for text inside the books,"
      + " use the full search.",
    "lib.tipgo": "Open search",
    "prev": "Previous",
    "next": "Next",
    "clear": "Clear",
    "none": "None",
    // dates and the Timeline
    "months": ["Jan", "Feb", "Mar", "Apr", "May",
  "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
  "Dec"],
    "kind.Start": "Start",
    "kind.Books": "Books",
    "kind.Translation": "Translation",
    "kind.Reader": "Reader",
    "kind.Dictionary": "Dictionary",
    "kind.Texts": "Texts",
    "kind.Site": "Site",
    "all": "All",
    "show": "Show",
    "read.go": "Read →",
    "open.go": "Open →",
    "tl.day": (n) => " · day " + n,
    "tl.sub": "How nxGir grew, from the first line"
      + " to today",
    "tl.days": "days",
    "tl.books": "Grabar books",
    "tl.parts": "parts translated",
    "tl.next": "Next",
    "tl.limits": "How close we are to the limits →"
      + " Statistics",
    "tl.en": "",
    // the Contribute page
    "co.title": "Become a contributor",
    "co.alt": "A reader under a tree with a laptop, a"
      + " monastery and a mountain behind",
    "co.mission": "Our mission: to open the old Armenian"
      + " books to every reader, word by word, in the"
      + " language we speak today.",
    "co.aside": "Think of it as a scriptorium with a new"
      + " apprentice: the AI copies fast and never asks"
      + " for candles, but a monk still has to check"
      + " every line.",
    "co.sub": "Նախագիր (nxGir) is an open project: old"
      + " Armenian books, word by word, and their"
      + " translations into modern Armenian, free for"
      + " anyone to read. It grows with the people who"
      + " help.",
    "co.ways": "Ways to contribute",
    "co.ways.where": "Where",
    "co.ways.how": "How",
    "co.w.mobile": "Phone: the ChatGPT app",
    "co.w.mobile.how": "Add the GitHub plugin and ask"
      + " ChatGPT to open the pull request. No computer or"
      + " git needed.",
    "co.w.mobile.go": "Steps with screenshots",
    "co.w.pc": "Computer",
    "co.w.pc.how": "ChatGPT in the browser with the same"
      + " GitHub plugin, or git: copy the repository, add"
      + " your file and open a pull request.",
    "co.w.pc.go": "Guide: CONTRIBUTING.md",
    "co.gh": "The project on GitHub",
    "co.lic1": "Translations are under ",
    "co.lic2": "; by sending one you agree to publish it"
      + " under this license.",
    // the Features page
    "nothing": "Nothing here yet.",
    // the Statistics page
    "st.measured": "measured ",
    "st.of": " of ",
    "lv.ok": "Fine",
    "lv.watch": "Watch",
    "lv.near": "Near the limit",
    "st.cols": ["Date", "Commit", "Text", "Site", "Git",
  "Build"],
    "st.none": "No statistics here: ",
    "st.sub": (d) => "How much the library holds, and how"
  + " close it is to the limits of GitHub and of"
  + " a phone. Measured " + d + " at commit ",
    "st.files": "book files",
    "st.text": "of text",
    "st.words": "different words",
    "st.tr": "translated",
    "st.closest": "Closest: ",
    "st.at": (n) => " at " + n + "% of its limit.",
    "st.limits": "Limits",
    "st.history": "History",
    "st.what": "What each limit means: ",
    "st.folders": "Folders",
    // the Offline page
    "off.h1": "Read offline",
    "off.here": "This copy already runs on this device:"
      + " no network is needed.",
    "off.about": "about 80 MB",
    "off.save": "Save for offline",
    "off.list": "Saving: getting the list of files…",
    "off.saving": "Saving…",
    "off.busy": (d, n, p) => "Saving: " + d + " of " + n
  + " files (" + p + "%). You can keep"
  + " reading.",
    "off.done": (n) => "Saved: all " + n + " files are on"
  + " this device. It updates itself when you"
  + " are online.",
    "off.remove": "Remove the saved copy",
    "off.part": (d, n) => "Partly saved: " + d + " of " + n
  + " files. Press to go on.",
    "off.go": "Continue saving",
    "off.nothing": "Nothing saved yet.",
    "off.offnow": "Saving the books is switched off for"
      + " now.",
    "off.install": "Install app",
    "off.how": "In Chrome: the ⋮ menu, then Install app"
      + " (or Add to Home screen). On an iPhone, in"
      + " Safari: Share, then Add to Home Screen.",
    "off.ways": (n) => (n === 3 ? "Three" : "Two")
  + " ways to read with no network.",
    "off.h_app": "1. Install the app",
    "off.app": "The site gets its own icon and opens in"
      + " its own window, like an app.",
    "off.h_save": "2. Save the books in this browser",
    "off.books": (mb) => "All the books, translations and"
  + " word meanings: " + mb + ". They stay in"
  + " the browser on this device, and are"
  + " replaced by the new ones when the site"
  + " changes.",
    "off.h_zip": "3. Download the site as a file",
    "off.zip1": (s) => "One zip file (" + s + "). Unpack it"
  + " and run ",
    "off.zip2": " (Python 3 is needed; it is in Termux"
      + " too). It does not update itself.",
    "off.dl": "Download the zip",
    // search
    "s.box": "Search the books",
    "s.where": (part, line) => (part ? "part " + part
  + " · " : "") + "line " + line,
    "s.alllines": (n) => "All " + nf(n) + " lines →",
    "s.lines": (n) => nf(n) + enN(n, " line", " lines"),
    "s.books": (n) => nf(n) + enN(n, " book", " books"),
    "s.authors": 
      (n) => nf(n) + enN(n, " author", " authors"),
    "s.allbooks": (n) => "All " + n + " books →",
    "s.names": "Authors and books",
    "s.hint": "Write the word in the classical or the"
      + " reformed spelling: թագավոր finds թագաւոր too.",
    "s.wait": "Searching…",
    "s.common": ": too common, the other words are"
      + " searched.",
    "s.common1": ": too common; add another word.",
    "s.all": "All",
    "s.forms": "Search word forms",
    "s.spelled": "Spellings",
    "s.open": "Open all",
    "s.close": "Close all",
    "s.found": "Lines",
    "s.notin": "Not here: look under the other filters.",
    "s.none": "Not found.",
    "s.library": "Search the whole library",
    "s.sel": "Search the library: ",
    "s.back": "To the results",
    "s.q": "Search: ",
    "s.nth": (r, n) => "result " + nf(r) + " of " + nf(n),
    // the reader
    "close": "Close",
    "r.meanin": "Meanings in",
    "r.only": "Only here",
    "r.places": (at, n) => at + " of " + n + " places",
    "r.inbook": "In this book",
    "r.prevplace": "Previous place",
    "r.nextplace": "Next place",
    "blog.copy": "Copy",
    "r.copied": "✓ Copied",
    "r.linkto": "Link to this line",
    "r.link": "🔗 Link to line",
    "r.fix": "The correct text",
    "r.comment": "Comment",
    "r.gh": "Send on GitHub",
    "r.mail": "Send by email",
    "r.report": "Report an error",
    "r.should": "What it should say",
    "r.note": "Comment, source (optional)",
    "r.ghhow": "GitHub opens a new issue for you to read"
      + " and send (an account is needed). With no"
      + " account, send it by email.",
    "r.marked": "★ Bookmarked",
    "r.mark": "☆ Bookmark",
    "r.addnote": "✎ Add note",
    "r.looking": "Looking up…",
    "r.failed": "Lookup failed: ",
    "r.abbr": "Abbreviation",
    "r.meaning": "Meaning",
    "r.noword": "Not in the vocabulary.",
    "r.marks": "Bookmarks",
    "r.notes": "Notes",
    "r.back": "Back to the folder",
    "r.backto": (x) => "Back to " + x,
    "r.contents": "Contents",
    "r.edit": "Edit text",
    "r.par": "Parallel",
    "r.two": "Show the two versions",
    "r.beside": (x) => "Side by side with " + x,
    "r.under": "Each line under its pair",
    "r.stacked": "Lines under each other (click for side"
      + " by side)",
    "r.side": "Side by side (click for lines under each"
      + " other)",
    "r.settings": "Text settings",
    "r.text": "Text",
    "r.smaller": "Smaller text",
    "r.bigger": "Bigger text",
    "r.center": "Center the text",
    "r.centered": "Text centered",
    "r.left": "Text on the left",
    "r.spacing": (k, n) => "Line spacing " + k + " of " + n,
    "r.widest": "Widest lines (click for normal)",
    "r.more": "Line spacing (click for more)",
    "r.sent": "Each sentence on its own line",
    "r.apart": "Sentences apart (click to join)",
    "r.written": "Text as written (click for sentences)",
    "r.width": "Text across the whole width",
    "r.whole": "Whole width (click for a column)",
    "r.column": "Text in a column (click for whole width)",
    "r.paged": "Read a long part in pages",
    "r.font": "Font of the text",
    "r.tile.center": "Center",
    "r.tile.spacing": "Spacing",
    "r.tile.sent": "Sentences",
    "r.tile.width": "Width",
    "nav.settings": "Settings",
    "set.sub": "How the books look on this device",
    "set.size": "Text size",
    "set.spacing": "Line spacing",
    "set.reading": "While reading",
    "set.kept": "The settings are kept in this browser.",
    "set.site": "The site",
    "set.statsnote": "How much the library holds",
    "set.back": "Back to the book",
    "set.undernote": "With the translation beside, on a"
      + " wide screen",
    "set.barsnote": "Scrolling down, the tools at the top"
      + " and the tabs at the bottom step aside; scrolling"
      + " up brings them back",
    "r.bars": "Hide the top and bottom bars while"
      + " scrolling",
    "r.tile.layout": "Stacked",
    "r.saved": "Bookmarks and notes",
    "r.paper": "Paper of the page",
    "paper.plain": "Plain",
    "paper.papyrus": "Papyrus",
    "paper.parchment": "Old book",
    "paper.vellum": "Vellum",
    "paper.candle": "By candlelight",
    "r.fontsample": "Նախագիր",
    "r.fail": "Could not save: ",
    "r.line": (n) => "line " + n,
    "r.prevpage": "Previous page",
    "r.nextpage": "Next page",
    "r.page": (k, n) => "Page " + k + " of " + n,
    "r.chapter": "Chapter",
    "r.local": "Kept in this browser only.",
    "r.nosave": "Could not save.",
    "r.nomarks": "No bookmarks yet. Tap a word, then ☆"
      + " Bookmark.",
    "r.nonotes": "No notes yet. Tap a word, then ✎ Add"
      + " note.",
    "edit": "Edit",
    "delete": "Delete",
    "r.delnote": "Delete this note?",
    "r.notebox": "Note",
    "save": "Save",
    "r.editnote": "Edit note",
    "r.newnote": "New note",
    "r.pages": "Pages",
    "r.prev": "‹ Previous",
    "r.next": "Next ›",
    "r.help": "Help edit",
    "r.parts": "Parts",
    "r.partprev": 
      (n, total) => "← Part " + n + " of " + total,
    "r.partnext": (n, total) => "Part " + n + " of " + total
  + " →",
    "r.allparts": (n) => "All " + n + " parts of ",
    "r.word": "Word",
    "r.read": "Read",
    "tr.machine": 
      (m) => "Translation: nxGir · machine (" + m
        + "), not yet reviewed",
    "tr.review": 
      (m, who) => "Translation: nxGir · machine ("
        + m + "), being reviewed by " + who,
    "tr.reviewed": (m, who) => "Translation: nxGir · " + m
  + ", reviewed by " + who,
    // the editor (nxgir web only)
    "ed.leave": "Leave without saving your changes?",
    "ed.md": "Saved exactly as typed. Markdown: # title,"
      + " > quote, **bold**, *italic*.",
    "ed.edit": (x) => "Edit " + x,
    "ed.reload": "Load the file again",
    "ed.saving": "Saving…",
    "ed.saved": "Saved at ",
    "ed.changed": "The file changed on disk since you"
      + " opened it (a git pull?), so it was not saved."
      + " Your text is still here: copy it, then load the"
      + " file again.",
    "ed.not": "Not saved: ",
    "ed.done": "Done",
    "ed.new": "New text",
    "ed.title": "# Title (Ps 118:33–37)\n\nThe text…",
    "ed.one": "One text per file, named by its passage"
      + " and a short title in Latin letters. ",
    "ed.file": "File name",
    "ed.create": "Create",
    // errors
    "err.static": "Not in the published copy",
    "err.theme": "No such theme",
    "err.post": "No such post",
    "err.series": "No such series",
    "err.news": "No such announcement",
    // the reader
    "r.tap": " · tap a word to look it up",
  },
  ru: {
    "nav.home": "Главная",
    "nav.library": "Библиотека",
    "nav.continue": "Продолжить",
    "nav.search": "Поиск",
    "nav.recent": "Чтение",
    "nav.reference": "Справочник",
    "nav.blog": "Блог",
    "nav.map": "Карта",
    "nav.map3d": "3D-карта",
    "m3.models": "3D-реконструкции",
    "m3.models.sub": "Монастыри и крепости, восстановленные по старым фотографиям и планам",
    "m3.model": "3D-модель",
    "m3.names": "Названия",
    "m3.hint3d": "Тяните, чтобы вращать; двумя пальцами (или правой кнопкой) — приближение и сдвиг; нажмите на название, чтобы подойти ближе",
    "m3.onmap": "На 3D-карте",
    "m3.book": "Читать книгу",
    "m3.sources": "Источники",
    "m3.sub": "Армянское нагорье, его горы и озёра",
    "m3.hint": "Тяните, чтобы двигать; двумя пальцами (или правой кнопкой) — поворот и наклон",
    "m3.flat": "Плоская карта",
    "m3.nogl": "Ваш браузер не показывает 3D (WebGL).",
    "m3.load": "Загружается 3D-карта…",
    "m3.left": "Повернуть влево",
    "m3.right": "Повернуть вправо",
    "m3.above": "Смотреть сверху",
    "m3.side": "Смотреть сбоку",
    "m3.badge": "3D",
    "nav.comics": "Комиксы",
    "nav.features": "Возможности",
    "nav.contribute": "Участвовать",
    "nav.news": "Объявления",
    "nav.timeline": "Хронология",
    "nav.stats": "Статистика",
    "nav.offline": "Офлайн",
    "nav.menu": "Меню",
    "nav.more": "Ещё",
    "nav.main": "Главные страницы",
    "nav.pages": "Страницы",
    "lang.pick": "Язык",
    "foot.tr": "Переводы ",
    "foot.pd": " · Тексты на грабаре в общественном"
      + " достоянии",
    "foot.join": "Стать участником",
    "nav.about": "О проекте",
    "foot.by1": "Разработали ",
    "foot.name": "Сергей Оганян",
    "foot.by2": " и Claude",
    "ab.title": "О проекте",
    "ab.sub":
      "Նախագիր (nxGir) — бесплатная библиотека и "
      + "читалка книг на грабаре, древнеармянском "
      + "языке. Можно узнать значение каждого слова, "
      + "а готовые переводы читаются рядом с "
      + "оригиналом.",
    "ab.what.h": "Читалка старых армянских книг",
    "ab.what.t":
      "nxGir собирает книги, написанные на "
      + "грабаре: от первых историков до поздних "
      + "хроник и толкований. Их можно читать в "
      + "браузере, на телефоне или в терминале; "
      + "текст — обычный Unicode, ничего "
      + "устанавливать не нужно.",
    "ab.name.h": "Название",
    "ab.name.t":
      "Նախագիր составлено из слов նախ — «первый» и "
      + "գիր — «буква, письмо». По-английски проект "
      + "называется nxGir.",
    "ab.do.h": "Что можно делать",
    "ab.do.t":
      "Откройте книгу и нажмите на слово, чтобы "
      + "увидеть его значение и формы. Читайте "
      + "грабар рядом с переводом на современный "
      + "армянский. Ищите по всей библиотеке. "
      + "Следите за местами из книг на карте. "
      + "Читайте блог и комиксы.",
    "ab.open.h": "Свободно и открыто",
    "ab.open.t":
      "Тексты на грабаре — общественное достояние. "
      + "Наши переводы распространяются по лицензии "
      + "CC BY-SA 4.0 и начинаются как машинные "
      + "черновики; они помечены, пока их не "
      + "проверит человек. Код и тексты лежат на "
      + "GitHub, помочь может каждый.",
    "ab.author.h": "Автор",
    "ab.author.t":
      "nxGir делают Сергей Оганян и Claude — "
      + "ИИ-помощник от Anthropic, который помогает "
      + "писать код и первые черновики переводов. "
      + "Вопросы, исправления и идеи приветствуются.",
    "ab.jump": "Контакты ↓",
    "ct.email": "Почта",
    "ct.github": "GitHub",
    "ct.instagram": "Instagram",
    "home": "← Главная",
    "back.library": "Вернуться в библиотеку",
    "error": "Что-то пошло не так",
    "title.top": "Книги на грабаре, слово за словом",
    "theme.light": "Светлая",
    "theme.dark": "Тёмная",
    "theme.black": "Чёрная",
    "video.play": "Смотреть видео",
    "video.note": "Видео загружается с YouTube только после нажатия.",
    "video.youtube": "Смотреть на YouTube",
    "theme.pick": (now, paper) => "Тема: " + now
      + (paper ? " · " + paper : ""),
    "theme.system": "Как в системе",
    "theme.themes": "Тема",
    "theme.menu": "Тема и бумага",
    "phone": "Вид телефона",
    "phone.on": "Вид телефона: включён (нажмите для"
      + " широкого вида)",
    "n.book": (n) => n + ruN(n, " книга", " книги",
      " книг"),
    "n.part": (n) => n + ruN(n, " часть", " части",
      " частей"),
    "n.file": (n) => n + ruN(n, " файл", " файла",
      " файлов"),
    "n.folder": (n) => n + ruN(n, " папка", " папки",
      " папок"),
    "n.line": (n) => n + ruN(n, " строка", " строки",
      " строк"),
    "n.word": (n) => n + ruN(n, " слово", " слова",
      " слов"),
    "n.day": (n) => n + ruN(n, " день", " дня",
      " дней"),
    // the top page's banners
    "dot": ".",
    "n.heading": (n) => n + ruN(n, " заголовок",
  " заголовка", " заголовков"),
    "dev.title": "Сайт активно развивается",
    "dev.text": "Новые возможности появляются каждый день."
      + " Заходите почаще, чтобы увидеть, что нового.",
    "dev.more": "Что нового — в хронологии →",
    "dev.mail": "Вопросы или идеи? Пишите на ",
    "join.title": "Присоединяйтесь к nxGir",
    "join.text": "Помогите переводить и править готовые"
      + " переводы",
    "join.go": "Как присоединиться →",
    "mapb.text": "Места исторических событий на карте",
    "mapb.go": "Открыть карту →",
    "top.about": "О проекте →",
    // readings
    "ago.now": "только что",
    "ago.min": (n) => n + " мин. назад",
    "ago.hour": (n) => n + ruN(n, " час", " часа",
  " часов") + " назад",
    "ago.yesterday": "вчера",
    "ago.days": (n) => n + ruN(n, " день", " дня",
  " дней") + " назад",
    "shelf.grabar": "Грабар",
    "shelf.ashkharhabar": "Ашхарабар",
    "cancel": "Отмена",
    "remove": "Убрать",
    "forget.title": "Убрать из списка",
    "forget.q": "Убрать из списка?",
    "forget.note": "Книга не удаляется. Место, где вы"
      + " остановились, сохранится, и книга вернётся в"
      + " список, когда вы откроете её снова.",
    "recent.go": "Продолжить чтение",
    "recent.all": "Всё чтение →",
    "recent.h1": "Моё чтение",
    "recent.static": "Хранится только в этом браузере",
    "recent.local": "На этом компьютере",
    "recent.none": "Вы ещё ничего не читали. ",
    // a book's page
    "pct.read": (n) => "прочитано " + n + "%",
    "part.n": (n) => "Часть " + n,
    "vol.done": (done, total) => " · переведено "
  + done + "/" + total,
    "vol.go": "Продолжить → ",
    "vol.start": "Начать чтение →",
    "new.text": "+ Новый текст",
    "no.books": "Здесь нет книг.",
    // the welcome on the top page
    "intro.hi": "Добро пожаловать",
    "intro.q1": "Для чего этот сайт?",
    "intro.a1": "Здесь можно читать книги, написанные на"
      + " грабаре — классическом армянском языке.",
    "intro.q2": "Как узнать значение слова?",
    "intro.a2": "Нажмите на слово, и вы увидите его"
      + " значение, словарную форму и другие места в"
      + " книге, где оно встречается.",
    "intro.q3": "Что нового на сайте?",
    "intro.all": "Все события → Хронология",
    "intro.q4": "Кто перевёл книги?",
    "intro.a4": "Переводы машинные и ещё не проверены"
      + " специалистом.",
    "intro.q5": "Как связаться?",
    "intro.a5": "С вопросами, предложениями или найденными"
      + " ошибками пишите автору проекта: ",
    "intro.contacts": "Все контакты →",
    "tip.label": "Совет",
    "tip.lib.a": "В Библиотеке нажмите",
    "tip.lib.b": "рядом с именем автора, чтобы прочитать"
      + " об авторе, или",
    "tip.lib.c": "рядом с книгой, чтобы прочитать о книге.",
    // the Library
    "lib.done": "переведено",
    "lib.bookpage": "Страница книги →",
    "lib.none": "Книг пока нет.",
    "lib.part": (p) => "часть " + p + " · ",
    "lib.noread": "Вы пока ничего не читаете. Откройте"
      + " книгу, и она появится здесь.",
    "lib.all": "Все книги",
    "lib.starred": "★ Избранное",
    "lib.reading": "Читаю",
    "lib.marks": "Закладки",
    "lib.nomarks": "Закладок пока нет. В книге нажмите на"
      + " слово, затем ☆ Закладка.",
    "lib.nostars": "Избранных книг пока нет. Добавьте их"
      + " сюда кнопкой ☆ рядом с книгой.",
    "star.off": "Убрать из избранного",
    "star.on": "В избранное",
    "lib.sub": (n) => "Книги на грабаре · " + n + " · ",
    "lib.find": "Найти автора или книгу",
    "lib.tip": "Чтобы искать текст внутри книг,"
      + " используйте полный поиск.",
    "lib.tipgo": "Открыть поиск",
    "prev": "Предыдущее",
    "next": "Следующее",
    "clear": "Очистить",
    "none": "Нет",
    // dates and the Timeline
    "months": ["янв", "фев", "мар", "апр", "мая",
  "июн", "июл", "авг", "сен", "окт", "ноя",
  "дек"],
    "kind.Start": "Начало",
    "kind.Books": "Книги",
    "kind.Translation": "Перевод",
    "kind.Reader": "Читалка",
    "kind.Dictionary": "Словарь",
    "kind.Texts": "Тексты",
    "kind.Site": "Сайт",
    "all": "Все",
    "show": "Показать",
    "read.go": "Читать →",
    "open.go": "Открыть →",
    "tl.day": (n) => " · день " + n,
    "tl.sub": "Как рос nxGir, от первой строки до"
      + " сегодняшнего дня",
    "tl.days": "дней",
    "tl.books": "книг на грабаре",
    "tl.parts": "переведённых частей",
    "tl.next": "Дальше",
    "tl.limits": "Насколько мы близки к пределам →"
      + " Статистика",
    "tl.en": "События пока только на английском.",
    // the Contribute page
    "co.title": "Стать участником",
    "co.alt": "Читатель под деревом с ноутбуком, позади"
      + " монастырь и гора",
    "co.mission": "Наша миссия — открыть старые армянские"
      + " книги каждому читателю, слово за словом, на"
      + " языке, на котором мы говорим сегодня.",
    "co.aside": "Представьте скрипторий с новым учеником:"
      + " ИИ переписывает быстро и никогда не просит"
      + " свечей, но монах всё равно должен проверить"
      + " каждую строку.",
    "co.sub": "Նախագիր (nxGir) — открытый проект: старые"
      + " армянские книги, слово за словом, и их переводы"
      + " на современный армянский, свободные для всех."
      + " Он растёт вместе с теми, кто помогает.",
    "co.ways": "Как участвовать",
    "co.ways.where": "Где",
    "co.ways.how": "Как",
    "co.w.mobile": "Телефон: приложение ChatGPT",
    "co.w.mobile.how": "Добавьте плагин GitHub и"
      + " попросите ChatGPT открыть pull request. Компьютер"
      + " и git не нужны.",
    "co.w.mobile.go": "Шаги со снимками",
    "co.w.pc": "Компьютер",
    "co.w.pc.how": "ChatGPT в браузере с тем же плагином"
      + " GitHub или git: сделайте копию репозитория,"
      + " добавьте файл и откройте pull request.",
    "co.w.pc.go": "Руководство: CONTRIBUTING.md",
    "co.gh": "Проект на GitHub",
    "co.lic1": "Переводы распространяются по лицензии ",
    "co.lic2": "; отправляя перевод, вы соглашаетесь"
      + " опубликовать его по этой лицензии.",
    // the Features page
    "nothing": "Здесь пока ничего нет.",
    // the Statistics page
    "st.measured": "измерено ",
    "st.of": " из ",
    "lv.ok": "В норме",
    "lv.watch": "Внимание",
    "lv.near": "Близко к пределу",
    "st.cols": ["Дата", "Коммит", "Текст", "Сайт", "Git",
  "Сборка"],
    "st.none": "Здесь нет статистики: ",
    "st.sub": 
      (d) => "Сколько вмещает библиотека и насколько"
        + " она близка к пределам GitHub и телефона."
        + " Измерено " + d + " на коммите ",
    "st.files": "файлов книг",
    "st.text": "текста",
    "st.words": "разных слов",
    "st.tr": "переведено",
    "st.closest": "Ближе всего: ",
    "st.at": (n) => ": " + n + "% предела.",
    "st.limits": "Пределы",
    "st.history": "История",
    "st.what": "Что значит каждый предел: ",
    "st.folders": "Папки",
    // the Offline page
    "off.h1": "Читать офлайн",
    "off.here": "Эта копия уже работает на этом"
      + " устройстве: сеть не нужна.",
    "off.about": "около 80 МБ",
    "off.save": "Сохранить для офлайна",
    "off.list": "Сохранение: загружается список файлов…",
    "off.saving": "Сохранение…",
    "off.busy": (d, n, p) => "Сохранение: " + d + " из " + n
  + " файлов (" + p + "%). Можно продолжать"
  + " читать.",
    "off.done": (n) => "Сохранено: все " + n + " файлов на"
  + " этом устройстве. Копия обновляется сама,"
  + " когда вы в сети.",
    "off.remove": "Удалить сохранённую копию",
    "off.part": 
      (d, n) => "Сохранено частично: " + d + " из "
        + n + " файлов. Нажмите, чтобы продолжить.",
    "off.go": "Продолжить сохранение",
    "off.nothing": "Пока ничего не сохранено.",
    "off.offnow": "Сохранение книг пока отключено.",
    "off.install": "Установить приложение",
    "off.how": "В Chrome: меню ⋮, затем «Установить"
      + " приложение» (или «Добавить на главный экран»)."
      + " На iPhone в Safari: «Поделиться», затем «На"
      + " экран Домой».",
    "off.ways": (n) => n + " способа читать без сети.",
    "off.h_app": "1. Установить приложение",
    "off.app": "Сайт получает свой значок и открывается в"
      + " своём окне, как приложение.",
    "off.h_save": "2. Сохранить книги в этом браузере",
    "off.books": (mb) => "Все книги, переводы и значения"
  + " слов: " + mb + ". Они хранятся в браузере"
  + " на этом устройстве и заменяются новыми,"
  + " когда сайт меняется.",
    "off.h_zip": "3. Скачать сайт одним файлом",
    "off.zip1": (s) => "Один zip-файл (" + s + ")."
  + " Распакуйте его и запустите ",
    "off.zip2": " (нужен Python 3, он есть и в Termux)."
      + " Сам он не обновляется.",
    "off.dl": "Скачать zip",
    // search
    "s.box": "Искать в книгах",
    "s.where": (part, line) => (part ? "часть " + part
  + " · " : "") + "строка " + line,
    "s.alllines": (n) => "Все " + nf(n) + " "
  + ruN(n, "строка", "строки", "строк") + " →",
    "s.lines": (n) => nf(n) + ruN(n, " строка", " строки",
  " строк"),
    "s.books": (n) => nf(n) + ruN(n, " книга", " книги",
  " книг"),
    "s.authors": (n) => nf(n) + ruN(n, " автор", " автора",
  " авторов"),
    "s.allbooks": (n) => "Все " + n + " "
  + ruN(n, "книга", "книги", "книг") + " →",
    "s.names": "Авторы и книги",
    "s.hint": "Пишите слово в классической или"
      + " реформированной орфографии: թագավոր найдёт и"
      + " թագաւոր.",
    "s.wait": "Поиск…",
    "s.common": ": слишком частое, ищутся другие слова.",
    "s.common1": ": слишком частое; добавьте ещё слово.",
    "s.all": "Все",
    "s.forms": "Искать словоформы",
    "s.spelled": "Написания",
    "s.open": "Раскрыть все",
    "s.close": "Свернуть все",
    "s.found": "Строки",
    "s.notin": "Здесь нет: посмотрите другие фильтры.",
    "s.none": "Не найдено.",
    "s.library": "Искать во всей библиотеке",
    "s.sel": "Искать в библиотеке: ",
    "s.back": "К результатам",
    "s.q": "Поиск: ",
    "s.nth": (r, n) => "результат " + nf(r) + " из "
  + nf(n),
    // the reader
    "close": "Закрыть",
    "r.meanin": "Значения на",
    "r.only": "Только здесь",
    "r.places": (at, n) => at + " из " + n + " мест",
    "r.inbook": "В этой книге",
    "r.prevplace": "Предыдущее место",
    "r.nextplace": "Следующее место",
    "blog.copy": "Копировать",
    "r.copied": "✓ Скопировано",
    "r.linkto": "Ссылка на эту строку",
    "r.link": "🔗 Ссылка на строку",
    "r.fix": "Правильный текст",
    "r.comment": "Комментарий",
    "r.gh": "Отправить через GitHub",
    "r.mail": "Отправить по почте",
    "r.report": "Сообщить об ошибке",
    "r.should": "Как должно быть",
    "r.note": "Комментарий, источник (необязательно)",
    "r.ghhow": "GitHub откроет новый issue, который вы"
      + " прочтёте и отправите (нужен аккаунт). Без"
      + " аккаунта отправьте по почте.",
    "r.marked": "★ В закладках",
    "r.mark": "☆ Закладка",
    "r.addnote": "✎ Заметка",
    "r.looking": "Поиск…",
    "r.failed": "Не удалось найти: ",
    "r.abbr": "Сокращение",
    "r.meaning": "Значение",
    "r.noword": "Нет в словаре.",
    "r.marks": "Закладки",
    "r.notes": "Заметки",
    "r.back": "Назад к папке",
    "r.backto": (x) => "Назад: " + x,
    "r.contents": "Содержание",
    "r.edit": "Править текст",
    "r.par": "Параллельно",
    "r.two": "Показать обе версии",
    "r.beside": (x) => "Рядом с: " + x,
    "r.under": "Каждая строка под своей парой",
    "r.stacked": "Строки друг под другом (нажмите: рядом)",
    "r.side": "Рядом (нажмите: строки друг под другом)",
    "r.settings": "Настройки текста",
    "r.text": "Текст",
    "r.smaller": "Мельче",
    "r.bigger": "Крупнее",
    "r.center": "Текст по центру",
    "r.centered": "Текст по центру",
    "r.left": "Текст слева",
    "r.spacing": (k, n) => "Межстрочный интервал " + k
  + " из " + n,
    "r.widest": "Самый широкий интервал (нажмите: обычный)",
    "r.more": "Межстрочный интервал (нажмите: больше)",
    "r.sent": "Каждое предложение с новой строки",
    "r.apart": "Предложения отдельно (нажмите: вместе)",
    "r.written": "Текст как написан (нажмите: по"
      + " предложениям)",
    "r.width": "Текст на всю ширину",
    "r.whole": "На всю ширину (нажмите: колонка)",
    "r.column": "Текст в колонке (нажмите: на всю ширину)",
    "r.paged": "Читать длинную часть по страницам",
    "r.font": "Шрифт текста",
    "r.tile.center": "Центр",
    "r.tile.spacing": "Интервал",
    "r.tile.sent": "Фразы",
    "r.tile.width": "Ширина",
    "nav.settings": "Настройки",
    "set.sub": "Как выглядят книги на этом устройстве",
    "set.size": "Размер текста",
    "set.spacing": "Межстрочный интервал",
    "set.reading": "При чтении",
    "set.kept": "Настройки хранятся в этом браузере.",
    "set.site": "Сайт",
    "set.statsnote": "Сколько всего в библиотеке",
    "set.back": "Вернуться к книге",
    "set.undernote": "С переводом рядом, на широком экране",
    "set.barsnote": "При прокрутке вниз инструменты сверху"
      + " и вкладки снизу убираются, при прокрутке вверх"
      + " возвращаются",
    "r.bars": "Скрывать верхнюю и нижнюю панели при"
      + " прокрутке",
    "r.tile.layout": "Стопкой",
    "r.saved": "Закладки и заметки",
    "r.paper": "Бумага страницы",
    "paper.plain": "Обычная",
    "paper.papyrus": "Папирус",
    "paper.parchment": "Старая книга",
    "paper.vellum": "Пергамент",
    "paper.candle": "При свече",
    "r.fontsample": "Նախագիր",
    "r.fail": "Не удалось сохранить: ",
    "r.line": (n) => "строка " + n,
    "r.prevpage": "Предыдущая страница",
    "r.nextpage": "Следующая страница",
    "r.page": (k, n) => "Страница " + k + " из " + n,
    "r.chapter": "Глава",
    "r.local": "Хранится только в этом браузере.",
    "r.nosave": "Не удалось сохранить.",
    "r.nomarks": "Закладок пока нет. Нажмите на слово,"
      + " затем ☆ Закладка.",
    "r.nonotes": "Заметок пока нет. Нажмите на слово,"
      + " затем ✎ Заметка.",
    "edit": "Править",
    "delete": "Удалить",
    "r.delnote": "Удалить эту заметку?",
    "r.notebox": "Заметка",
    "save": "Сохранить",
    "r.editnote": "Править заметку",
    "r.newnote": "Новая заметка",
    "r.pages": "Страницы",
    "r.prev": "‹ Назад",
    "r.next": "Дальше ›",
    "r.help": "Помочь править",
    "r.parts": "Части",
    "r.partprev": (n, total) => "← Часть " + n + " из "
  + total,
    "r.partnext": 
      (n, total) => "Часть " + n + " из " + total
        + " →",
    "r.allparts": (n) => "Все " + n + " "
  + ruN(n, "часть", "части", "частей") + ": ",
    "r.word": "Слово",
    "r.read": "Прочитано",
    "tr.machine": (m) => "Перевод: nxGir · машинный (" + m
  + "), ещё не проверен",
    "tr.review": (m, who) => "Перевод: nxGir · машинный ("
  + m + "), проверяет: " + who,
    "tr.reviewed": (m, who) => "Перевод: nxGir · " + m
  + ", проверил(и): " + who,
    // the editor (nxgir web only)
    "ed.leave": "Уйти, не сохранив изменения?",
    "ed.md": "Сохраняется точно как написано. Markdown: #"
      + " заголовок, > цитата, **жирный**, *курсив*.",
    "ed.edit": (x) => "Править: " + x,
    "ed.reload": "Загрузить файл снова",
    "ed.saving": "Сохранение…",
    "ed.saved": "Сохранено в ",
    "ed.changed": "Файл изменился на диске после открытия"
      + " (git pull?), поэтому не сохранён. Ваш текст всё"
      + " ещё здесь: скопируйте его и загрузите файл"
      + " снова.",
    "ed.not": "Не сохранено: ",
    "ed.done": "Готово",
    "ed.new": "Новый текст",
    "ed.title": "# Заголовок (Пс 118:33–37)\n\nТекст…",
    "ed.one": "Один текст в файле, названном по отрывку и"
      + " короткому заголовку латиницей. ",
    "ed.file": "Имя файла",
    "ed.create": "Создать",
    // errors
    "err.static": "Нет в опубликованной копии",
    "err.theme": "Нет такой темы",
    "err.post": "Нет такой записи",
    "err.series": "Нет такой серии",
    "err.news": "Нет такого объявления",
    // the reader
    "r.tap": " · нажмите на слово, чтобы узнать значение",
  },
};
