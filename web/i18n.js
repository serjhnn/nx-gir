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
    "nav.comics": "Կոմիքսներ",
    "nav.features": "Հնարավորություններ",
    "nav.contribute": "Միանալ",
    "nav.news": "Հայտարարություններ",
    "nav.timeline": "Ժամանակագրություն",
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
    "foot.by": "Մշակել են Ս.Օ.-ն և Claude-ը",
    "home": "← Գլխավոր",
    "back.library": "Վերադառնալ գրադարան",
    "error": "Ինչ-որ բան այն չէ",
    "title.top": "Գրաբար գրքեր՝ բառ առ բառ",
    "theme.light": "Լուսավոր",
    "theme.dark": "Մուգ",
    "theme.black": "Սև",
    "theme.title": (now, next) => "Ոճ՝ " + now
      + " (սեղմեք՝ " + next + ")",
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
    "dev.title": "Կայքը ակտիվ մշակման փուլում է",
    "dev.text": "Ամեն օր նոր հնարավորություններ են"
      + " ավելանում։ Հաճախ վերադարձեք՝ տեսնելու, թե ինչ է"
      + " նոր։",
    "dev.more": "Տեսնել նորությունները"
      + " ժամանակագրությունում →",
    "dev.mail": "Հարցեր կամ գաղափարնե՞ր։ Գրեք՝ ",
    "join.title": "Միացեք Նախագրին",
    "join.text": "Օգնեք թարգմանել և խմբագրել առկա"
      + " թարգմանությունները",
    "join.go": "Ինչպես միանալ →",
    "mapb.text": "Պատմական դեպքերի վայրերը քարտեզի վրա",
    "mapb.go": "Բացել քարտեզը →",
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
      + " Ժամանակագրություն",
    "intro.q4": "Ո՞վ է թարգմանել։",
    "intro.a4": "Թարգմանությունը մեքենայական է և դեռ"
      + " ստուգված չէ մասնագետի կողմից։",
    "intro.q5": "Ինչպե՞ս կապվել։",
    "intro.a5": "Հարցերի, առաջարկների կամ սխալների մասին"
      + " գրեք նախագծի հեղինակին՝ ",
    // the Library
    "lib.done": "թարգմանված",
    "lib.none": "Գրքեր դեռ չկան։",
    "lib.part": (p) => "մաս " + p + " · ",
    "lib.noread": "Դեռ ոչինչ չեք կարդում։ Բացեք գիրքը՝ այն"
      + " կհայտնվի այստեղ։",
    "lib.all": "Բոլոր գրքերը",
    "lib.starred": "★ Ընտրված",
    "lib.reading": "Ընթերցվող",
    "lib.nostars": "Ընտրված գրքեր դեռ չկան։ Գրքի կողքի"
      + " ☆-ով ավելացրեք այստեղ։",
    "star.off": "Հանել աստղը",
    "star.on": "Աստղանշել",
    "lib.sub": (n) => "Գրաբար գրքեր · " + n + " · ",
    "lib.find": "Գտնել հեղինակ կամ գիրք",
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
    "co.start": "Ինչպես սկսել",
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
    "s.spelled": "Գրված է՝",
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
    "foot.by": "Developed by S.O. and Claude",
    "home": "← Home",
    "back.library": "Back to the library",
    "error": "Something went wrong",
    "title.top": "Grabar books, word by word",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "theme.black": "Black",
    "theme.title": (now, next) => "Theme: " + now
      + " (click for " + next.toLowerCase() + ")",
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
    // the Library
    "lib.done": "translated",
    "lib.none": "No books yet.",
    "lib.part": (p) => "part " + p + " · ",
    "lib.noread": "Nothing being read yet. Open a book and"
      + " it shows here.",
    "lib.all": "All books",
    "lib.starred": "★ Starred",
    "lib.reading": "Reading",
    "lib.nostars": "No starred books yet. Add them here"
      + " with the ☆ beside a book.",
    "star.off": "Take the star off",
    "star.on": "Star",
    "lib.sub": (n) => "Grabar books · " + n + " · ",
    "lib.find": "Find an author or a book",
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
    "co.start": "How to start",
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
    "s.spelled": "Spelled:",
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
    "foot.by": "Разработали С.О. и Claude",
    "home": "← Главная",
    "back.library": "Вернуться в библиотеку",
    "error": "Что-то пошло не так",
    "title.top": "Книги на грабаре, слово за словом",
    "theme.light": "Светлая",
    "theme.dark": "Тёмная",
    "theme.black": "Чёрная",
    "theme.title": (now, next) => "Тема: " + now
      + " (нажмите: " + next.toLowerCase() + ")",
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
    // the Library
    "lib.done": "переведено",
    "lib.none": "Книг пока нет.",
    "lib.part": (p) => "часть " + p + " · ",
    "lib.noread": "Вы пока ничего не читаете. Откройте"
      + " книгу, и она появится здесь.",
    "lib.all": "Все книги",
    "lib.starred": "★ Избранное",
    "lib.reading": "Читаю",
    "lib.nostars": "Избранных книг пока нет. Добавьте их"
      + " сюда кнопкой ☆ рядом с книгой.",
    "star.off": "Убрать из избранного",
    "star.on": "В избранное",
    "lib.sub": (n) => "Книги на грабаре · " + n + " · ",
    "lib.find": "Найти автора или книгу",
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
    "co.start": "Как начать",
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
    "s.spelled": "Написано:",
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
  },
};
