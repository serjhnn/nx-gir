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
  },
};
