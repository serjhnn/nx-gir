// nx-gir web: the bookshelf and the theme button.
// Pages are #/ (top), #/f/<folder>, #/b/<book>
// (a book's parts), #/read/<book>,
// #/library, #/reference (the book cards),
// #/timeline, #/blog, #/comics,
// #/features,
// #/contribute, #/news and #/stats; the
// data
// comes from
// /api/.
"use strict";

const main = document.getElementById("main");
// the words index.html has before the app draws
// the page: shown again under an error
const ABOUT = document.getElementById("about");

// -- small helpers --

// h("a", {href: "#/"}, "text", child): an element.
// Text is always set as text, never as HTML. Kids
// may be lists; null kids are left out.
// text with each nxGir in the accent color (the
// name, as in the header): strings and spans for h()
function named(text) {
  return String(text).split(/(nxGir)/).map((t) =>
    t === "nxGir"
      ? h("span", { class: "nxgir" }, t) : t);
}

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null) continue;
    if (k === "class") el.className = v;
    else if (k === "href" && (String(v).startsWith("#/")
      || langOf(String(v)))) {
      setRoute(el, v);
    } else el.setAttribute(k, v);
  }
  el.append(...kids.flat().filter((k) => k != null));
  return el;
}

// -- addresses --
// A page is a path under its language (i18n.js):
// /hy/library, /en/read/<book>?line=3. The code
// names a page without the language, as it did when
// the pages were after a #: "#/library"; setRoute()
// turns that into the path for a link, in LANG,
// hashNow() gives the page shown in that form,
// goTo() opens one without reloading. A path with
// its language (inLang()) is opened as it is.

// the path of page "#/library" in language l
function inLang(l, hash) {
  const rest = hash.replace(/^#?\/?/, "");
  return "/" + l + "/" + rest;
}

// the link of an <a> to a page: a path, opened by the
// click handler below, not by the browser
function setRoute(a, hash) {
  a.setAttribute("href", hash.startsWith("#")
    ? inLang(LANG, hash) : hash);
  a.setAttribute("data-r", "");
}

// the page shown, as "#/library" (the root: "#/")
function hashNow() {
  const path = location.pathname
    .replace(/^\/[a-z]{2}(?=\/|$)/, "")
    .replace(/\/+$/, "");
  return "#" + (path || "/") + location.search;
}

// a page as a path with its language: "#/library"
// in LANG, "/library" too, "/ru/map" as it is
function pathOf(to) {
  if (to.startsWith("#")) return inLang(LANG, to);
  return langOf(to) ? to : inLang(LANG, to);
}

// open a page: "#/library" (or a path); replace: the
// entry of history is replaced, not added to
function goTo(to, replace) {
  const url = pathOf(to);
  const now = location.pathname + location.search;
  if (url === now) return;
  if (replace) history.replaceState(null, "", url);
  else history.pushState(null, "", url);
  window.dispatchEvent(new Event("navigate"));
}

// back and forward
window.addEventListener("popstate", () => {
  window.dispatchEvent(new Event("navigate"));
});

// a link to a page: no reload
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-r]");
  if (!a || e.defaultPrevented || e.button
    || e.metaKey || e.ctrlKey || e.shiftKey
    || e.altKey || a.target) return;
  e.preventDefault();
  goTo(a.getAttribute("href"));
});

// An old link: nxgir.am/#/library, /library, and
// the language at the end, /blog/<slug>/en,
// /map/<place>/ru, /features/hy: the same page with
// the language first
{
  let path = location.pathname;
  let search = location.search;
  if (location.hash.startsWith("#/")) {
    const [p, q] = location.hash.slice(1).split("?");
    path = p;
    search = q ? "?" + q : "";
  }
  if (!langOf(path)) {
    let l = LANG;
    const m = new RegExp("^/(blog|comics|features"
      + "|map)(/.*?)?/([a-z]{2})/?$").exec(path);
    if (m && LANGS.includes(m[3])) {
      l = m[3];
      path = "/" + m[1] + (m[2] || "");
    }
    history.replaceState(null, "",
      inLang(l, path) + search);
  }
  LANG = langOf(location.pathname);
  saveLang(LANG);
  document.documentElement.lang = LANG;
}

const SVG = "http://www.w3.org/2000/svg";

// An icon from SVG path data, 24x24, stroked.
function icon(paths, cls) {
  const s = document.createElementNS(SVG, "svg");
  s.setAttribute("viewBox", "0 0 24 24");
  s.setAttribute("fill", "none");
  s.setAttribute("stroke", "currentColor");
  s.setAttribute("stroke-width", "1.6");
  s.setAttribute("stroke-linecap", "round");
  s.setAttribute("stroke-linejoin", "round");
  s.setAttribute("aria-hidden", "true");
  if (cls) s.setAttribute("class", cls);
  for (const d of paths) {
    const p = document.createElementNS(SVG, "path");
    p.setAttribute("d", d);
    s.append(p);
  }
  return s;
}

const ICONS = {
  // a bin: take off the list
  bin: [
    "M4 7h16M10 11v6M14 11v6",
    "M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12",
    "M9 7V4h6v3",
  ],
  folder: [
    "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8" +
      "a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  ],
  book: [
    "M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z",
    "M5 18a2 2 0 0 1 2-2h11",
  ],
  // three lines: the menu
  menu: ["M4 7h16", "M4 12h16", "M4 17h16"],
  // an open book: continue reading
  resume: [
    "M12 6c-2-1.5-5-2-8-2v14c3 0 6 .5 8 2"
      + "c2-1.5 5-2 8-2V4c-3 0-6 .5-8 2z",
    "M12 6v14",
  ],
  // a clock: the readings
  clock: [
    "M12 21a9 9 0 1 0 0-18a9 9 0 0 0 0 18z",
    "M12 7v5l3 2",
  ],
  // a pen: the blog
  pen: [
    "M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z",
    "M13.5 6.5l4 4",
  ],
  // a person: an author
  person: [
    "M12 11a3.5 3.5 0 1 0 0-7a3.5 3.5 0 0 0 0 7z",
    "M5 20c0-4 3-6.5 7-6.5s7 2.5 7 6.5",
  ],
  // a rolled sheet with lines: about an author
  scroll: [
    "M7 4h11a2 2 0 0 1 0 4H7",
    "M7 4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10"
      + "a2 2 0 0 0 2-2V8",
    "M9 12h7M9 15h5",
  ],
  // a pin: a place on the map
  pin: [
    "M12 21s-6-5.5-6-11a6 6 0 0 1 12 0"
      + "c0 5.5-6 11-6 11z",
    "M12 12a2 2 0 1 0 0-4a2 2 0 0 0 0 4z",
  ],
  // a person and a plus: become a contributor
  join: [
    "M9 11a3.5 3.5 0 1 0 0-7a3.5 3.5 0 0 0 0 7z",
    "M3 20a6 6 0 0 1 12 0",
    "M19 8v6M16 11h6",
  ],
  // two panels: the comics
  panels: [
    "M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4" +
      "a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z",
    "M3 12h18M12 4v8",
  ],
  // a card over another: the book cards
  cards: [
    "M8 7h11a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H8" +
      "a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z",
    "M4 16V5a1 1 0 0 1 1-1h11",
    "M10 11h7M10 14h7M10 17h4",
  ],
  // a folded map: the map
  map: [
    "M9 4L3 6v14l6-2l6 2l6-2V4l-6 2z",
    "M9 4v14M15 6v14",
  ],
  // a horn: the announcements
  horn: [
    "M4 10v4h3l7 4V6L7 10z",
    "M17.5 9a4 4 0 0 1 0 6",
  ],
  // a ticked box: the features
  tick: [
    "M5 4h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5" +
      "a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z",
    "M8 12l3 3l5-6",
  ],
  // a globe: the language slider shows or hides
  globe: [
    "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18z",
    "M3 12h18",
    "M12 3c3 2.5 3 15.5 0 18",
    "M12 3c-3 2.5-3 15.5 0 18",
  ],
  sun: [
    "M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8z",
    "M12 2v2M12 20v2M2 12h2M20 12h2" +
      "M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4" +
      "M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  ],
  moon: [
    "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z",
  ],
  // the moon and a star: the black theme
  night: [
    "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z",
    "M17 3v4M15 5h4",
  ],
  left: ["M4 6h16M4 10h10M4 14h16M4 18h10"],
  // lines with an up-down arrow beside them
  spacing: ["M11 6h9M11 12h9M11 18h9",
    "M5 4v16M3 6l2-2l2 2M3 18l2 2l2-2"],
  center: ["M4 6h16M7 10h10M4 14h16M7 18h10"],
  back: ["M19 12H5M11 6l-6 6l6 6"],
  // a phone: the phone view
  phone: ["M8 3h8a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1"
    + "H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z",
    "M11 18h2"],
  // two sliders: the text settings
  sliders: ["M4 7h9M17 7h3M4 17h3M11 17h9",
    "M15 5a2 2 0 1 0 0 4a2 2 0 1 0 0-4z",
    "M9 15a2 2 0 1 0 0 4a2 2 0 1 0 0-4z"],
  // two columns: the versions side by side
  columns: ["M4 5h7v14H4zM13 5h7v14h-7z"],
  // two rows: each line under its pair
  rows: ["M4 4h16v7H4zM4 13h16v7H4z"],
  // arrows out to both sides: full width
  width: ["M3 12h18M7 8l-4 4l4 4M17 8l4 4l-4 4"],
  // a magnifying glass: search
  search: ["M11 4.5a6.5 6.5 0 1 0 0 13a6.5 6.5 0 1 0"
    + " 0-13z", "M16 16l4.5 4.5"],
  // an arrow head: a folded list
  fold: ["M9 6l6 6l-6 6"],
  // up and down: the found one before, after
  up: ["M6 15l6-6l6 6"],
  down: ["M6 9l6 6l6-6"],
};

// 512 B, 3.4 KB: like human_size() in Python.
function size(n) {
  if (n < 1024) return n + " B";
  n /= 1024;
  if (n < 1024) return n.toFixed(1) + " KB";
  return (n / 1024).toFixed(1) + " MB";
}

// "3 books" in LANG: a count of a word that has a
// key "n.<word>" in i18n.js, else in English
function plural(n, word) {
  if (UI.en["n." + word]) return t("n." + word, n);
  return n + " " + word + (n === 1 ? "" : "s");
}

async function api(path) {
  if (STATIC) return staticApi(path);
  const r = await fetch("/api/" + path);
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || r.status);
  return data;
}

// -- the published copy (GitHub Pages) --
// No server there: scripts/build-site.py wrote the
// answers into files under data/, and sets
// NXGIR_STATIC (static.js). It only reads: no
// bookmarks, notes or editing; where you stopped is
// kept in this browser.

const STATIC = window.NXGIR_STATIC === true;
// this build of the published copy: after each
// file's address, so that a browser never mixes
// this app.js with data of another build
const BUILD = window.NXGIR_BUILD || "";

// Visits to the published copy are counted by
// GoatCounter (NXGIR_COUNT, set by static.js when
// build-site.py has a code): the page (its path
// starts with the language, /en/library) and its
// title, where the visitor came from and the screen
// width;
// no cookies, nothing about the visitor. Sent as an
// image, as GoatCounter allows, so no script of
// theirs is loaded. Not when a program drives the
// browser, and never on the local server.
let counted = "";
function visit(path) {
  if (path === counted) return;
  const first = counted === "";
  counted = path;
  const q = { p: path, t: document.title };
  // where they came from, on the first page only
  if (first && document.referrer) {
    q.r = document.referrer;
  }
  beacon(q);
}

function beacon(q) {
  const url = window.NXGIR_COUNT;
  if (!STATIC || !url || navigator.webdriver) return;
  const all = new URLSearchParams({ ...q,
    s: String(screen.width),
    rnd: Math.random().toString(36).slice(2) });
  new Image().src = url + "?" + all;
}

// How far into a book readers get: the first time
// this browser sees the end of a quarter of it, an
// event "/read/<book>/50%" is counted (titled
// "<title> · 50%"). The part seen is the line of
// the last word on the screen. Kept per browser,
// so a reader who comes back is not counted again.
const DEPTHS = [25, 50, 75, 100];
function depth(title) {
  if (!STATIC || !window.NXGIR_COUNT) return;
  const key = "nxgir-depth:" + R.name;
  let got = 0;
  try {
    got = Number(localStorage.getItem(key)) || 0;
  } catch (e) {}
  const line = R.wpos[lastWord()][0] + 1;
  const pct = 100 * line / R.lines;
  const now = DEPTHS.filter((d) => d <= pct + 0.5)
    .pop() || 0;
  if (now <= got) return;
  try {
    localStorage.setItem(key, String(now));
  } catch (e) {}
  for (const d of DEPTHS) {
    if (d <= got || d > now) continue;
    beacon({ p: "/read/" + R.name + "/" + d + "%",
      t: (title || R.name) + " · " + d + "%",
      e: "true" });
  }
}

// files the words are spread over, per language;
// as BUCKETS in build-site.py
const BUCKETS = 256;
const buckets = new Map();

// a file of the published copy; tried twice, as a
// network may drop a request
async function json(url) {
  if (BUILD) url += "?b=" + BUILD;
  let r;
  try {
    r = await fetch(url);
  } catch (e) {
    await new Promise((ok) => setTimeout(ok, 1000));
    r = await fetch(url);
  }
  if (!r.ok) {
    throw new Error(r.status === 404
      ? "Not in the published copy" : r.status);
  }
  return r.json();
}

// FNV-1a over the code points of a word: which file
// it is in; as bucket() in build-site.py
function bucket(w) {
  let x = 0x811c9dc5;
  for (const ch of w) {
    x = Math.imul(x ^ ch.codePointAt(0), 0x01000193);
  }
  return (x >>> 0) % BUCKETS;
}

function readAt(name) {
  try {
    return JSON.parse(localStorage.getItem(
      "nxgir-read:" + name) || "null");
  } catch (e) {
    return null;
  }
}

// the books read in this browser, newest first, as
// /api/recent gives them: n of them, or all for 0;
// titles from data/titles.json
async function recentHere(n) {
  let titles = {};
  try {
    titles = await json("data/titles.json");
  } catch (e) {}
  const loaded = Object.keys(titles).length > 0;
  const pre = "nxgir-read:";
  const items = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k.startsWith(pre)) continue;
      const r = readAt(k.slice(pre.length));
      if (!r || r.hidden) continue;
      const name = k.slice(pre.length);
      // a book no longer on the site
      if (loaded && !(name in titles)) continue;
      items.push({ name,
        title: titles[name] || r.title
          || name.split("/").pop(),
        progress: r.pct, seen: r.t || 0 });
    }
  } catch (e) {}
  items.sort((a, b) => b.seen - a.seen);
  return n > 0 ? items.slice(0, n) : items;
}

async function staticApi(path) {
  const [route, query] = path.split("?");
  const q = new URLSearchParams(query);
  if (route === "shelf") {
    const f = q.get("folder") || "";
    const data = await json("data/shelf/" +
      (f ? enc(f) + "/" : "") + "index.json");
    for (const item of data.items) {
      const r = item.folder ? null : readAt(item.name);
      if (r) item.progress = r.pct;
    }
    return data;
  }
  if (route === "timeline") {
    return json("data/timeline.json");
  }
  if (route === "blog") {
    return json("data/blog.json");
  }
  if (route === "features") {
    return json("data/features.json");
  }
  if (route === "authors") {
    return json("data/authors.json");
  }
  if (route === "author") {
    return json("data/author/" + enc(q.get("id"))
      + ".json");
  }
  if (route === "book-cards") {
    return json("data/book-cards/"
      + (q.get("lang") || "hy") + ".json");
  }
  if (route === "book-info") {
    return json("data/book/" + q.get("id")
      .split("/").map(enc).join("/") + ".json");
  }
  if (route === "comics") {
    return json("data/comics.json");
  }
  if (route === "map") {
    return json("data/map.json");
  }
  if (route === "recent") {
    return { items: await recentHere(
      Number(q.get("n")) || 0) };
  }
  if (route === "stats") {
    return json("data/stats.json");
  }
  if (route === "library") {
    return { ...(await json("data/library.json")),
      stars: starsHere() };
  }
  if (route === "volume") {
    const data = await json("data/volume/" +
      enc(q.get("folder")) + ".json");
    for (const g of data.groups) {
      for (const p of g.parts) {
        const r = readAt(p.name);
        if (r) {
          p.progress = r.pct;
          p.seen = r.t || 0;
        }
      }
    }
    return data;
  }
  if (route === "book") {
    const name = q.get("name");
    const data = await json("data/book/" + enc(name)
      + ".json");
    const r = readAt(name);
    if (r) data.at = r.at;
    return data;
  }
  if (route === "word") {
    const w = q.get("w").trim();
    const k = q.get("lang") + "/" + bucket(w);
    if (!buckets.has(k)) {
      buckets.set(k, json("data/word/" + k + ".json")
        .catch((e) => {
          buckets.delete(k);
          throw e;
        }));
    }
    const e = (await buckets.get(k))[w];
    return { word: w, abbr: e ? e[0] : [],
      meaning: e ? e[1] : [] };
  }
  // search: the files of build-site.py
  if (route === "search") {
    const key = loose(q.get("w").trim());
    const k = "search/" + bucket(key);
    if (!buckets.has(k)) {
      buckets.set(k, json("data/" + k + ".json")
        .catch((e) => {
          buckets.delete(k);
          throw e;
        }));
    }
    const e = (await buckets.get(k))[key];
    return { key, entry: e || null };
  }
  if (route === "search-parts") {
    return json("data/search/parts.json");
  }
  if (route === "lines") {
    return json("data/lines/" + enc(q.get("name"))
      + "/" + Number(q.get("k")) + ".json");
  }
  throw new Error(t("err.static"));
}

// the end of every tab title
const NAME = "Նախագիր | nxGir";

// the top page's title, as in index.html: what
// search results show
function topTitle() {
  return NAME + " · " + t("title.top");
}

function enc(name) {
  return name.split("/").map(encodeURIComponent)
    .join("/");
}

function show(...kids) {
  // (replaceChildren would write null as "null")
  main.replaceChildren(
    ...withSearch(kids), siteFooter());
  window.scrollTo(0, 0);
}

// a page without the footer (the Library: its
// lists go on to the bottom of the screen)
function showBare(...kids) {
  main.replaceChildren(...withSearch(kids));
  window.scrollTo(0, 0);
}

// the bottom of every page: the main pages, the
// license, how to help and who made it
const REPO = "https://github.com/serjhnn/nx-gir";
const BY_SA = "https://creativecommons.org/"
  + "licenses/by-sa/4.0/";

function siteFooter() {
  const pages = ["library", "reference", "blog",
    "comics", "map", "features", "timeline",
    "stats", "recent"];
  return h("footer", { class: "site-foot" },
    h("p", { class: "foot-name" },
      h("span", { lang: "hy" }, "Նախագիր"),
      h("span", { class: "foot-sep",
        "aria-hidden": "true" }),
      named("nxGir")),
    h("nav", { "aria-label": t("nav.pages") },
      pages.flatMap((p, i) => [
        i ? " · " : null,
        h("a", { href: "#/" + p }, t("nav." + p))])),
    h("p", {}, t("foot.tr"),
      h("a", { href: BY_SA, rel: "license" },
        "CC BY-SA 4.0"),
      t("foot.pd")),
    h("p", {},
      h("a", { href: "#/contribute" },
        t("foot.join")),
      " · ",
      h("a", { href: "#/news" }, t("nav.news")),
      " · ",
      h("a", { href: REPO }, "GitHub"),
      offlineLink()),
    h("p", {}, t("foot.by")));
}

// the published site only: a link to #/offline
function offlineLink() {
  if (!hasWorker()) return null;
  return [" · ", h("a", { href: "#/offline" },
    t("nav.offline"))];
}

// an error, and under it what the site is: a
// search engine that hits an error quotes that,
// not the error (data-nosnippet)
function showError(msg) {
  show(
    h("p", { class: "error", "data-nosnippet": "" },
      msg + ". ",
      h("a", { href: "#/" }, t("back.library"))),
    ABOUT
  );
}

// Library / grabar / bible: links up the folders;
// above: [{label, folder}] from the API, with the
// names of LIBRARY.tsv, else the folder names.
function crumbs(path, last, above) {
  const nav = h("nav", { class: "crumbs",
    "aria-label": "Folders" });
  const parts = path ? path.split("/") : [];
  if (!last) parts.pop();
  nav.append(h("a", { href: "#/" },
    t("nav.library")));
  parts.forEach((p, i) => {
    const to = parts.slice(0, i + 1).join("/");
    const a = above && above[i];
    nav.append(h("span", { class: "sep" }, "/"),
      h("a", { href: a ? a.to : folderHref(to),
        lang: a ? "hy"
        : null }, a ? a.label : p));
  });
  return nav;
}

// -- theme --

const button = document.getElementById("theme");
const topBar = button.parentNode;

// light, dark, black, and around again
const THEMES = ["light", "dark", "black"];
const THEME_ICONS = {
  light: "sun", dark: "moon", black: "night" };

function theme() {
  const t = document.documentElement.dataset.theme;
  return THEMES.includes(t) ? t : "light";
}

function nextTheme(t) {
  return THEMES[(THEMES.indexOf(t) + 1) %
    THEMES.length];
}

function drawTheme() {
  const now = theme();
  const other = nextTheme(now);
  button.replaceChildren(
    icon(ICONS[THEME_ICONS[now]]));
  button.title = t("theme.title",
    t("theme." + now), t("theme." + other));
  button.setAttribute("aria-label", button.title);
}

button.addEventListener("click", () => {
  const t = nextTheme(theme());
  document.documentElement.dataset.theme = t;
  try {
    localStorage.setItem("nxgir-theme", t);
  } catch (e) {}
  drawTheme();
});

// -- the phone view --
// On a wide screen, the pages as on a phone: in a
// column a phone wide, with the phone's layout
// (.phone on <html>, set early by theme.js; the
// CSS rules for wide screens need .wide). Kept per
// browser. The button is hidden on a phone.

const viewBtn = document.getElementById("view");

// .wide or .phone, if theme.js did not set one (an
// old copy of it, kept by the browser)
{
  const html = document.documentElement;
  if (!html.classList.contains("phone")) {
    html.classList.add("wide");
  }
}

function drawView() {
  const on = document.documentElement.classList
    .contains("phone");
  viewBtn.replaceChildren(icon(ICONS.phone));
  viewBtn.title = on ? t("phone.on") : t("phone");
  viewBtn.setAttribute("aria-label", t("phone"));
  viewBtn.setAttribute("aria-pressed", String(on));
}

viewBtn.addEventListener("click", () => {
  const html = document.documentElement;
  const on = !html.classList.contains("phone");
  html.classList.toggle("phone", on);
  html.classList.toggle("wide", !on);
  try {
    localStorage.setItem("nxgir-phone",
      on ? "1" : "0");
  } catch (e) {}
  drawView();
});

// -- the language --
// A slider in the top bar (Հայ, Eng, Рус): the three
// languages always in view, each a link to the page
// shown in it, the thumb under the current one. The
// names are short; the full name is the title and the
// aria-label. route() sees the new language in the
// address and sends "langchange": the thumb slides,
// the menus, the tab bar and the buttons draw their
// words again, then the page itself is drawn.

function langButton() {
  const nav = h("nav", { class: "lang-slider",
    id: "lang-slider", role: "group" });
  // the globe hides the slider and brings it back; the
  // choice is kept (shown at first)
  const globe = h("button", {
    class: "icon-btn lang-globe", type: "button",
    "aria-controls": "lang-slider" }, icon(ICONS.globe));
  const show = (on, keep) => {
    nav.hidden = !on;
    globe.setAttribute("aria-expanded", String(on));
    if (!keep) return;
    try {
      localStorage.setItem("nxgir-lang-bar",
        on ? "1" : "0");
    } catch (e) {}
  };
  let shown = true;
  try {
    shown = localStorage.getItem("nxgir-lang-bar") !== "0";
  } catch (e) {}
  globe.addEventListener("click",
    () => show(nav.hidden, true));
  // short in the bar, the full name on a phone, where
  // the slider has a row of its own (style.css)
  const links = LANGS.map((l) => h("a",
    { lang: l, hreflang: l },
    h("span", { class: "ls" }, LANG_SHORT[l]),
    h("span", { class: "lf" }, LANG_FULL[l])));
  nav.append(...links);
  const draw = () => {
    nav.setAttribute("aria-label", t("lang.pick"));
    nav.title = t("lang.pick");
    globe.title = t("lang.pick");
    globe.setAttribute("aria-label", t("lang.pick"));
    nav.style.setProperty("--i", LANGS.indexOf(LANG));
    links.forEach((a, i) => {
      const l = LANGS[i];
      setRoute(a, inLang(l, hashNow()));
      a.title = LANG_FULL[l];
      a.setAttribute("aria-label", LANG_FULL[l]);
      if (l === LANG) {
        a.setAttribute("aria-current", "true");
      } else a.removeAttribute("aria-current");
    });
  };
  window.addEventListener("navigate", draw);
  // the language changes after "navigate": the links
  // in each language and the thumb, drawn again
  window.addEventListener("langchange", draw);
  draw();
  show(shown, false);
  topBar.prepend(nav);
  topBar.append(globe);
}
langButton();

// the language of the address, if it changed: kept,
// and every part drawn once (not the page) told
function followLang() {
  const l = langOf(location.pathname) || LANG;
  if (l === LANG) return;
  LANG = l;
  saveLang(l);
  document.documentElement.lang = l;
  drawTheme();
  drawView();
  window.dispatchEvent(new Event("langchange"));
}

// -- bookshelf --

function bookRow(item) {
  const dot = item.label.lastIndexOf(".");
  const base = dot > 0 ? item.label.slice(0, dot)
    : item.label;
  const ext = dot > 0 ? item.label.slice(dot + 1)
    : "";
  const meta = h("span", { class: "meta" });
  const pct = item.progress;
  meta.append(pct == null ? size(item.size)
    : pct + "% · " + size(item.size));
  if (pct != null) {
    const fill = h("span");
    fill.style.width = pct + "%";
    meta.append(h("span", { class: "progress",
      role: "img",
      "aria-label": t("pct.read", pct) },
    fill));
  }
  return h("a", { class: "row",
    href: "#/read/" + enc(item.name) },
  icon(ICONS.book, "ico"),
  h("span", { class: "name" }, base,
    ext ? h("span", { class: "ext" }, ext) : null),
  meta);
}

function folderRow(item) {
  return h("a", { class: "row",
    href: folderHref(item.name) },
  icon(ICONS.folder, "ico"),
  h("span", { class: "name" },
    item.label.replace(/\/$/, "")),
  h("span", { class: "meta" },
    plural(item.size, item.unit || "book")));
}

// where visitors can write: kept in parts and put
// together only in the page, so that programs
// gathering addresses from the files do not find it
const CONTACT = ["nxgir.lib", "gmail.com"];

// the menu items: the row on the top page and the
// list the ☰ button of the top bar opens
// (labels: keys of UI in i18n.js)
const MENU = [
  ["#/library", "book", "nav.library"],
  ["#/reference", "cards", "nav.reference"],
  ["#/blog", "pen", "nav.blog"],
  ["#/comics", "panels", "nav.comics"],
  ["#/map", "map", "nav.map"],
  ["#/features", "tick", "nav.features"],
  ["#/contribute", "join", "nav.contribute"],
  ["#/news", "horn", "nav.news"],
];

function menuLink([href, ic, label]) {
  return h("a", { class: "icon-btn", href },
    icon(ICONS[ic]), t(label));
}

// the welcome above the library: questions a
// first-time visitor may ask
function intro(news) {
  const qa = (q, ...a) => [h("h3", {}, t(q)),
    h("p", {}, ...a)];
  return h("section", { class: "intro" },
    h("h2", {}, t("intro.hi")),
    qa("intro.q1", t("intro.a1")),
    qa("intro.q2", t("intro.a2")),
    news && news.length ? [
      h("h3", {}, t("intro.q3")),
      newsList(news),
      h("p", { class: "more" },
        h("a", { href: "#/timeline" },
          t("intro.all")))] : null,
    qa("intro.q4", t("intro.a4")),
    qa("intro.q5", t("intro.a5"), mail(), t("dot")));
}

// a tip: a framed note with its label in a pill on
// the top line (.tip); kids are its words and icons
function tip(...kids) {
  return h("aside", { class: "tip" },
    h("span", { class: "tip-tag" },
      h("i", { class: "tip-dot" }), t("tip.label"),
      h("i", { class: "tip-dot" })),
    h("p", {}, ...kids),
    h("i", { class: "tip-dot tip-end" }));
}

// an icon inside a tip's sentence
function tipIcon(name) {
  return h("span", { class: "tip-ic" },
    icon(ICONS[name]));
}

// the tip under the menu of the top page: what the
// scroll and the book icon of the Library open
function libraryTip() {
  return tip(t("tip.lib.a") + " ", tipIcon("scroll"),
    " " + t("tip.lib.b") + " ", tipIcon("book"),
    " " + t("tip.lib.c"));
}

// the newest steps of the timeline, in English
// for now (timeline.tsv)
function newsList(news) {
  const list = h("ul", { class: "news" });
  for (const e of news) {
    const to = eventHref(e);
    list.append(h("li", {},
      h("time", { datetime: e.date },
        day(e.date)),
      h("div", { lang: "en" },
        to ? h("a", { href: to }, named(e.title))
          : h("b", {}, named(e.title)),
        e.text ? h("span", {}, named(e.text))
          : null)));
  }
  return list;
}

// the contact address as a link, made in the page
function mail() {
  const at = CONTACT.join(String.fromCharCode(64));
  const a = h("a", { href: "#" }, at);
  // the mailto only when it is used
  const set = () => { a.href = "mailto:" + at; };
  a.addEventListener("pointerdown", set);
  a.addEventListener("focus", set);
  a.addEventListener("click", set);
  return a;
}

// the folders or books of a shelf as a list
function shelfList(data) {
  const list = h("ul", { class: "shelf" });
  for (const item of data.items) {
    list.append(h("li", {}, item.folder
      ? folderRow(item) : bookRow(item)));
  }
  return data.items.length ? list
    : h("p", { class: "empty" }, t("no.books"));
}

async function shelf(folder) {
  // an old link to a book's folder: its page
  const page = folderHref(folder);
  if (page.startsWith("#/b/")) {
    goTo(page, true);
    return;
  }
  const q = encodeURIComponent(folder);
  const [data, last] = await Promise.all([
    api("shelf?folder=" + q),
    folder ? null : api("recent?n=" + RECENT)
      .catch(() => null)]);
  // the top page: its top bar is pinned (CSS)
  document.body.classList.toggle("home", !folder);
  const title = folder
    ? data.title || folder.split("/").pop()
    : t("nav.library");
  document.title = folder
    ? title + " · " + NAME : topTitle();
  const lang = folder.split("/")[1];
  show(
    folder ? crumbs(folder, false, data.crumbs)
      : null,
    // the top page's heading, as in index.html, for
    // screen readers and search engines; not seen
    folder ? null : h("h1", { class: "sr-only" },
      "nxGir · ", h("span", { lang: "hy" },
        "Նախագիր")),
    // at the top: the picture, the Library and the
    // other pages, what was read last, then the
    // welcome
    folder ? null : devBanner(),
    folder ? null : topBanner(),
    folder ? null : menuBar(...MENU.map(menuLink)),
    folder ? null : libraryTip(),
    ...(folder ? [] : NEWS.slice(0, 2).map(
      (a) => newsBanner(a))),
    folder ? null : joinBanner(),
    folder ? null : mapBanner(),
    last && last.items.length
      ? recentCard(last.items) : null,
    folder ? null : intro(data.news),
    // the top page has no list of folders: it is
    // at the bottom of #/stats
    folder ? h("h1", { lang: data.title
      && data.title !== folder.split("/").pop()
      ? "hy" : null }, title) : null,
    folder ? h("p", { class: "sub" }, plural(
      data.count, data.unit)) : null,
    folder && data.editable ? h("div",
      { class: "actions" },
      h("a", { class: "icon-btn",
        href: "#/new/" + (lang || "ru") },
      t("new.text"))) : null,
    folder ? shelfList(data) : null
  );
}

// the menu buttons of the top page. On a phone
// they are one line to swipe, with a dot per button
// under it (the one in view is filled); the dots
// are hidden when all the buttons fit
function menuBar(...links) {
  const row = h("p", { class: "lib-btn", lang: "hy" },
    ...links);
  const dots = h("div", { class: "menu-dots",
    "aria-hidden": "true" },
  ...links.map(() => h("span", {})));
  const update = () => {
    const max = row.scrollWidth - row.clientWidth;
    dots.hidden = max <= 1;
    const k = max > 0 ? Math.round(
      row.scrollLeft / max * (links.length - 1)) : 0;
    [...dots.children].forEach((d, i) =>
      d.classList.toggle("on", i === k));
  };
  row.addEventListener("scroll", update,
    { passive: true });
  if (window.ResizeObserver) {
    new ResizeObserver(update).observe(row);
  } else {
    window.addEventListener("resize", update);
  }
  return h("div", { class: "menu-bar" }, row, dots);
}

// the ☰ button in the top bar: it opens all the
// menu items in a list under the bar
function headerMenu() {
  const bar = topBar.parentNode;
  const panel = h("nav", { class: "menu-panel",
    id: "menu-panel", hidden: "" });
  const more = h("button", { class: "icon-btn menu-more",
    type: "button", "aria-expanded": "false",
    "aria-controls": "menu-panel" },
  icon(ICONS.menu));
  // its words, again when the language changes
  const draw = () => {
    panel.lang = LANG;
    panel.setAttribute("aria-label", t("nav.menu"));
    panel.replaceChildren(...MENU.map(menuLink));
    more.title = t("nav.menu");
    more.setAttribute("aria-label", t("nav.menu"));
  };
  draw();
  window.addEventListener("langchange", draw);
  const open = (on) => {
    panel.hidden = !on;
    more.setAttribute("aria-expanded", String(on));
  };
  more.addEventListener("click", () => open(panel.hidden));
  panel.addEventListener("click", (e) => {
    if (e.target.closest("a")) open(false);
  });
  document.addEventListener("pointerdown", (e) => {
    if (!bar.contains(e.target)) open(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) {
      open(false);
      more.focus();
    }
  });
  window.addEventListener("navigate",
    () => open(false));
  topBar.append(more);
  bar.append(panel);
}
headerMenu();

// the tab bar at the bottom of a phone (shown by
// style.css under 40rem; hidden in the reader):
// the main pages, and a sheet with all the others
// (labels: keys of UI in i18n.js)
const TABS = [
  ["#/", "logo", "nav.home", "home"],
  ["#/library", "book", "nav.library", "library"],
  ["#/recent", "resume", "nav.continue", "continue"],
  ["#/reference", "cards", "nav.reference", "reference"],
];
// the pages the More tab opens
const MORE = [
  ["#/recent", "clock", "nav.recent"],
  ["#/search", "search", "nav.search"],
  ["#/blog", "pen", "nav.blog"],
  ["#/map", "map", "nav.map"],
  ["#/comics", "panels", "nav.comics"],
  ["#/features", "tick", "nav.features"],
  ["#/contribute", "join", "nav.contribute"],
  ["#/news", "horn", "nav.news"],
  ["#/timeline", "scroll", "nav.timeline"],
  ["#/stats", "sliders", "nav.stats"],
];

// which tab a page belongs to: a TABS key, "more",
// or "" (the reader and the editor have no bar)
function tabFor(hash) {
  const top = hash.split(/[/?]/)[0];
  if (top === "read") return "continue";
  if (["edit", "new"].includes(top)) return "";
  if (top === "") return "home";
  if (["library", "b", "f"].includes(top)) {
    return "library";
  }
  if (top === "reference") return "reference";
  return "more";
}

// Each tab remembers its page and how far it was
// scrolled (in the tab, one page deep as it goes:
// Library, a book's page, Readings, Library again
// returns to the book's page). The Continue tab
// opens the book read last; the reader keeps its own
// place. Tapping the tab shown scrolls to the top,
// and from the top goes to the tab's first page.
const REMEMBER = ["home", "library", "reference"];
let tabPlace = {};
try {
  tabPlace = JSON.parse(
    sessionStorage.getItem("nxgir-tabs") || "{}");
} catch (e) {
  tabPlace = {};
}
let shownHash = null;
let restoreY = 0;

function rememberTab(hash, y) {
  const key = tabFor(hash);
  if (!REMEMBER.includes(key)) return;
  tabPlace[key] = { hash, y };
  try {
    sessionStorage.setItem("nxgir-tabs",
      JSON.stringify(tabPlace));
  } catch (e) {
    // no storage: the tabs forget on reload
  }
}

async function tabClick(e) {
  const a = e.target.closest("a[data-tab]");
  if (!a || e.defaultPrevented) return;
  const key = a.dataset.tab;
  const now = tabFor(
    hashNow().replace(/^#\/?/, ""));
  if (key === "continue") {
    e.preventDefault();
    if (now === "continue") return; // already reading
    let to = "#/recent";
    try {
      const data = await api("recent");
      const last = data.items[0];
      if (last) to = "#/read/" + enc(last.name);
    } catch (err) {
      // the list of readings instead
    }
    goTo(to);
  } else if (key === now) {
    if (window.scrollY > 4) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  } else if (tabPlace[key]) {
    e.preventDefault();
    restoreY = tabPlace[key].y;
    goTo("#/" + tabPlace[key].hash);
  }
}

// the logo of the header, as drawn, for the home tab
function logoMark() {
  const mark = document.querySelector(".brand-mark");
  return mark.cloneNode(true);
}

function tabBar() {
  const link = ([href, ic, label, key]) => h("a",
    { href, "data-tab": key },
    ic === "logo" ? logoMark() : icon(ICONS[ic]),
    t(label));
  const sheet = h("nav", { class: "more-sheet",
    id: "more-sheet", hidden: "" });
  const more = h("button", { type: "button",
    "data-tab": "more", "aria-expanded": "false",
    "aria-controls": "more-sheet" });
  const bar = h("nav", { class: "tabbar" });
  // its words and links, again when the language
  // changes
  const draw = () => {
    sheet.lang = LANG;
    sheet.setAttribute("aria-label", t("nav.more"));
    sheet.replaceChildren(...MORE.map(menuLink));
    more.replaceChildren(icon(ICONS.menu),
      t("nav.more"));
    bar.lang = LANG;
    bar.setAttribute("aria-label", t("nav.main"));
    bar.replaceChildren(...TABS.map(link), more);
    if (bar.isConnected) {
      markTab(hashNow().replace(/^#\/?/, ""));
    }
  };
  draw();
  window.addEventListener("langchange", draw);
  bar.addEventListener("click", tabClick);
  const open = (on) => {
    sheet.hidden = !on;
    more.setAttribute("aria-expanded", String(on));
  };
  more.addEventListener("click",
    () => open(sheet.hidden));
  // a link to the page already open does not navigate,
  // so the sheet is shut by the click itself
  sheet.addEventListener("click", (e) => {
    if (e.target.closest("a")) open(false);
  });
  document.addEventListener("pointerdown", (e) => {
    if (!bar.contains(e.target)
      && !sheet.contains(e.target)) open(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !sheet.hidden) {
      open(false);
      more.focus();
    }
  });
  window.addEventListener("navigate",
    () => open(false));
  document.body.append(sheet, bar);
  return bar;
}
const tabs = tabBar();

// in the reader the bar shows on scrolling up, and
// goes again on scrolling down (.peek, style.css)
let lastY = 0;
window.addEventListener("scroll", () => {
  const y = window.scrollY;
  const body = document.body;
  if (!body.classList.contains("reading")) {
    body.classList.remove("peek");
  } else if (y < lastY - 8) {
    body.classList.add("peek");
  } else if (y > lastY + 8 || y < 50) {
    body.classList.remove("peek");
  } else {
    return;
  }
  lastY = y;
}, { passive: true });

// mark the tab of the page shown
function markTab(hash) {
  const now = tabFor(hash);
  for (const el of tabs.children) {
    if (el.dataset.tab === now) {
      el.setAttribute("aria-current", "page");
    } else {
      el.removeAttribute("aria-current");
    }
  }
}

// on scrolling, the top bar of the top page stays
// at the top, with a line under it (.scrolled)
window.addEventListener("scroll", () => {
  document.documentElement.classList.toggle(
    "scrolled", window.scrollY > 40);
}, { passive: true });

// the picture at the very top of the top page,
// with a short line in its corner
function topBanner() {
  return h("div", { class: "top-banner" },
    h("img", { src: "banner.jpg", alt: "",
      width: "1600", height: "550",
      fetchpriority: "high" }),
    h("p", { class: "top-text", lang: "hy" },
      "… ժամանակ ժողովելոյ քարինս"));
}

// a note at the top of the top page: the site is
// being built, with something new every day; it
// opens the timeline; and the contact address
function devBanner() {
  return h("div", { class: "dev-banner",
    role: "note", lang: LANG },
  h("span", { class: "dev-dot", "aria-hidden": "true" }),
  h("span", { class: "dev-text" },
    h("a", { class: "dev-go", href: "#/timeline" },
      h("b", {}, t("dev.title")),
      h("span", {}, t("dev.text")),
      h("span", { class: "dev-more" },
        t("dev.more"))),
    h("span", { class: "dev-mail" },
      t("dev.mail"), mail(), t("dot"))));
}

// a narrow banner on the top page, with the
// picture of #/contribute, leading there
function joinBanner() {
  return h("a", { class: "join-banner",
    href: "#/contribute", lang: LANG },
  h("img", { src: "contribute.jpg", alt: "",
    width: "1200", height: "675" }),
  h("span", { class: "join-text" },
    h("b", {}, t("join.title")),
    h("span", {}, t("join.text")),
    h("span", { class: "join-go" }, t("join.go"))));
}

// a narrow banner on the top page, with the
// painted map, leading to #/map
function mapBanner() {
  return h("a", { class: "join-banner map-banner",
    href: "#/map", lang: LANG },
  h("img", { src: "img/map/base.webp", alt: "",
    width: "1536", height: "1024",
    loading: "lazy" }),
  h("span", { class: "join-text" },
    h("b", {}, t("nav.map")),
    h("span", {}, t("mapb.text")),
    h("span", { class: "join-go" }, t("mapb.go"))));
}

// a narrow banner on the top page, with the
// picture of the newest announcement. A click on it
// leads to #/news; its two links, under the words,
// to the announcement and to the book itself (its
// own words in bookText, else "Read the book")
function newsBanner(a = NEWS[0],
  lang = newsLang()) {
  const en = lang !== "hy" && a["banner_" + lang];
  const ui = NEWS_UI[lang];
  const to = "#/news/" + a.id;
  return h("div", { class: "join-banner news-banner",
    lang },
  h("img", { src: a.face, alt: "",
    width: "600", height: "400" }),
  // the whole banner, for a mouse or a finger; the
  // links below are for a keyboard
  h("a", { class: "banner-all", href: to,
    tabindex: "-1", "aria-hidden": "true" }),
  h("span", { class: "join-text" },
    h("b", {}, (en || a.banner)[0]),
    h("span", {}, (en || a.banner)[1]),
    h("span", { class: "join-go" },
      h("a", { href: to }, ui.read),
      a.book ? h("a", { href: a.book },
        a.bookText ? a.bookText[lang] : ui.book)
        : null)));
}

// -- readings --

// how many of the books read last the top page
// shows; #/recent shows them all
const RECENT = 3;

// "seen" (seconds) as "how long ago", in LANG
function ago(seen) {
  if (!seen) return "";
  const s = Date.now() / 1000 - seen;
  const n = (k) => Math.max(1, Math.floor(s / k));
  if (s < 60) return t("ago.now");
  if (s < 3600) return t("ago.min", n(60));
  if (s < 86400) return t("ago.hour", n(3600));
  if (s < 2 * 86400) return t("ago.yesterday");
  if (s < 30 * 86400) return t("ago.days", n(86400));
  const d = new Date(seen * 1000);
  return day(d.toISOString().slice(0, 10), true);
}

// the language of a book, from its top folder
const SHELF_LANGS = ["grabar", "ashkharhabar"];

// a styled question before a reading is taken off
// the list: true when answered yes
function askForget(title) {
  return new Promise((done) => {
    const box = h("dialog", { class: "ask" });
    const end = (yes) => {
      box.close();
      box.remove();
      done(yes);
    };
    const no = h("button", { type: "button",
      class: "icon-btn" }, t("cancel"));
    const yes = h("button", { type: "button",
      class: "icon-btn danger" },
    icon(ICONS.bin), t("remove"));
    no.addEventListener("click", () => end(false));
    yes.addEventListener("click", () => end(true));
    box.append(h("div", { class: "ask-card",
      lang: LANG },
    h("h2", {}, t("forget.q")),
    h("p", { class: "ask-book", lang: "hy" }, title),
    h("p", { class: "ask-note" }, t("forget.note")),
    h("div", { class: "ask-btns" }, no, yes)));
    box.addEventListener("click", (e) => {
      if (e.target === box) end(false);
    });
    box.addEventListener("cancel", (e) => {
      e.preventDefault();
      end(false);
    });
    document.body.append(box);
    box.showModal();
    no.focus();
  });
}

// take a book off the list of readings: where it
// was left stays, and reading it again brings it
// back
async function forget(name) {
  if (!STATIC) {
    await send("forget", { name });
    return;
  }
  const r = readAt(name);
  if (!r) return;
  r.hidden = true;
  try {
    localStorage.setItem("nxgir-read:" + name,
      JSON.stringify(r));
  } catch (e) {}
}

// books read, newest first (/api/recent)
function readingList(items) {
  const list = h("ul", { class: "readings" });
  for (const r of items) {
    const pct = r.progress || 0;
    const fill = h("span");
    fill.style.width = pct + "%";
    const top = r.name.split("/")[0];
    const lang = SHELF_LANGS.includes(top)
      ? t("shelf." + top) : "";
    const when = ago(r.seen);
    const x = h("button", { type: "button",
      class: "forget",
      "aria-label": t("forget.title"),
      title: t("forget.title") },
    icon(ICONS.bin));
    x.addEventListener("click", async () => {
      if (!await askForget(r.title)) return;
      x.disabled = true;
      try {
        await forget(r.name);
      } catch (e) {
        x.disabled = false;
        return;
      }
      route(); // the next one moves up
    });
    list.append(h("li", {},
      x,
      h("a", { href: "#/read/" + enc(r.name),
        lang: "hy" }, r.title),
      h("div", { class: "meta" },
        lang ? h("span", { class: "tag" }, lang)
          : null,
        h("span", {}, pct + "%"),
        when ? h("span", {}, "· " + when) : null),
      h("span", { class: "progress", role: "img",
        "aria-label": pct + "%" }, fill)));
  }
  return list;
}

// the top of the home page: the books read last
function recentCard(items) {
  return h("section", { class: "recent",
    lang: LANG },
    h("h2", {}, t("recent.go")),
    readingList(items),
    h("p", { class: "more" },
      h("a", { href: "#/recent" }, t("recent.all"))));
}

async function recentPage() {
  const data = await api("recent");
  document.title = t("nav.recent") + " · " + NAME;
  show(
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("h1", {}, t("recent.h1")),
    h("p", { class: "sub" },
      STATIC ? t("recent.static") : t("recent.local")),
    data.items.length
      ? h("section", { class: "recent all" },
        readingList(data.items))
      : h("p", { class: "empty" }, t("recent.none"),
        h("a", { href: "#/" }, t("nav.library"))));
}

// -- a book's page --

// the folders of the Library, whose books have a
// page (volume() in nxgir_web.py); an author's own
// folder, two levels down, stays on the shelf
const PAGED = ["grabar", "ashkharhabar"];

function dirOf(name) {
  return name.split("/").slice(0, -1).join("/");
}

// where a folder opens: the page of a book (three
// levels down in grabar/), or the plain shelf
function folderHref(dir) {
  const [top, ...rest] = dir.split("/");
  if (rest.length > 1 && PAGED.includes(top)) {
    return "#/b/" + enc(dir);
  }
  return dir ? "#/f/" + enc(dir) : "#/";
}

// the name of a link up: the Library in LANG, the
// authors and books in Armenian
function upLabel(u) {
  return u.to === "#/library" ? t("nav.library")
    : u.label;
}

// links up: [{label, to}] as volume() gives them
function upLinks(up) {
  const nav = h("nav", { class: "crumbs",
    "aria-label": t("nav.library") });
  up.forEach((u, i) => {
    if (i) nav.append(h("span", { class: "sep" }, "/"));
    nav.append(h("a", { href: u.to,
      lang: u.to === "#/library" ? null : "hy" },
    upLabel(u)));
  });
  return nav;
}

// one part of a book: its number, first heading,
// whether it is translated, and how far it is read
function partRow(p, here) {
  const meta = h("span", { class: "meta" });
  if (p.translated) {
    meta.append(h("span", { class: "done" }, "⇆"));
  }
  if (p.progress != null) {
    const fill = h("span");
    fill.style.width = p.progress + "%";
    meta.append(p.progress + "%",
      h("span", { class: "progress", role: "img",
        "aria-label": t("pct.read", p.progress) },
      fill));
  }
  const a = h("a", { class: "row part",
    href: "#/read/" + enc(p.name) },
  h("span", { class: "num" }, String(p.n)),
  p.title ? h("span", { class: "name", lang: "hy" },
    p.title)
    : h("span", { class: "name" }, t("part.n", p.n)),
  meta);
  if (here) a.setAttribute("aria-current", "true");
  return a;
}

// #/b/<folder>: a book, its parts in order; the
// button goes on from where it was left
async function bookPage(folder) {
  const data = await api("volume?folder=" +
    encodeURIComponent(folder));
  document.title = data.book + " · " + NAME;
  let last = null;
  for (const g of data.groups) {
    for (const p of g.parts) {
      if (p.progress != null && (!last
        || p.seen > last.seen)) last = p;
    }
  }
  const first = data.groups[0].parts[0];
  const go = last || first;
  const groups = data.groups.map((g) => {
    const list = h("ul", { class: "shelf" });
    for (const p of g.parts) {
      list.append(h("li", {}, partRow(p)));
    }
    return h("section", { class: "volume-group" },
      g.label ? h("h2", {}, g.label) : null, list);
  });
  // back up one level, as the Library's ← Home
  const up = data.up[data.up.length - 1];
  // the author under the title, when written
  // about; co-authors (LIBRARY.tsv) before it
  const people = data.authors || [];
  const by = h("p", { class: "by", hidden: "" });
  const own = folder.split("/").length === 2;
  if (!own && people.length > 1) {
    by.classList.add("co-names");
    by.append(...authorNames(people, by));
    watchNames(by);
  } else if (!own) {
    by.append(up.label, authorInfoBtn(
      folder.split("/")[1], up.label, by));
  }
  show(
    h("p", { class: "crumbs" },
      h("a", { href: up.to, lang: up.to
        === "#/library" ? null : "hy" },
      "← " + upLabel(up))),
    h("div", { class: "volume" },
      h("h1", { lang: "hy" }, data.book,
        own ? authorInfoBtn(folder.split("/")[1],
          data.book) : null),
      own ? null : by,
      data.title !== data.book
        ? h("p", { class: "sub", lang: "hy" },
          data.title) : null,
      h("p", { class: "sub" }, plural(data.total,
        "part") + (data.done ? t("vol.done",
        data.done, data.total) : "")),
      h("p", { class: "intro-btn" },
        h("a", { class: "icon-btn primary",
          href: "#/read/" + enc(go.name) },
        last ? [t("vol.go"), go.title
          ? h("span", { lang: "hy" }, go.title)
          : t("part.n", go.n)] : t("vol.start"))),
      groups));
}

// -- library --

// starred books of the Library, newest first:
// in the saved state on the local server, in this
// browser on the published copy
const STARS = "nxgir-stars";

function starsHere() {
  try {
    const s = JSON.parse(
      localStorage.getItem(STARS) || "[]");
    return Array.isArray(s) ? s : [];
  } catch (e) {
    return [];
  }
}

// the tab of the Library last shown in this
// browser: "all", "starred" or "reading"
const LIB_TAB = "nxgir-library-tab";
const LIB_TABS = ["all", "starred", "reading"];

function libraryTab() {
  try {
    const t = localStorage.getItem(LIB_TAB);
    return LIB_TABS.includes(t) ? t : "all";
  } catch (e) {
    return "all";
  }
}

// the books of the Library being read, last read
// first: [{b, by, at: the part read last, its
// progress, part ("3/12" for a book in parts) and
// seen}]. A translation read counts for its book.
function readingBooks(data, items) {
  const of = new Map();
  for (const a of data.authors) {
    for (const b of a.books) {
      const key = b.parts > 1 ? dirOf(b.first)
        : b.first;
      of.set(key, { b, by: a.name });
    }
  }
  const out = new Map();
  for (const r of items) {
    const name = r.name.replace(
      /^ashkharhabar\//, "grabar/");
    const x = of.get(name) || of.get(dirOf(name));
    if (!x || out.has(x.b.first)) continue;
    const m = /· (\d+\/\d+)$/.exec(r.title || "");
    out.set(x.b.first, { ...x, at: r.name,
      names: [],
      progress: r.progress || 0,
      part: x.b.parts > 1 && m ? m[1] : "",
      seen: r.seen });
  }
  // every part read of a book, to take it off
  for (const r of items) {
    const name = r.name.replace(
      /^ashkharhabar\//, "grabar/");
    const x = of.get(name) || of.get(dirOf(name));
    if (x && out.has(x.b.first)) {
      out.get(x.b.first).names.push(r.name);
    }
  }
  return [...out.values()];
}

// star a book (named by its first file), or take
// the star off; the stars after it
async function toggleStar(name) {
  if (!STATIC) {
    return (await send("star", { name })).stars;
  }
  const s = starsHere();
  const i = s.indexOf(name);
  if (i >= 0) s.splice(i, 1);
  else s.unshift(name);
  try {
    localStorage.setItem(STARS, JSON.stringify(s));
  } catch (e) {}
  return s;
}

// one book of #/library: its short name, how many
// parts and how much is translated; by: its
// author, in the starred list
// a book's authors in one line: its co-authors
// first (LIBRARY.tsv), then its author
function byLine(co, name) {
  return (co || []).map((c) => c.name)
    .concat([name]).join(" · ");
}

// the names of authors [{id, name}] as elements,
// each with its scroll button; show is shown with
// the first known. When they do not fit on one
// line, the last goes on its own, smaller
// (fitNames()).
function authorNames(people, show) {
  const out = [];
  people.forEach((p, i) => {
    if (i) {
      out.push(h("span", { class: "co-sep" },
        " · "));
    }
    const last = i > 0 && i === people.length - 1;
    out.push(h("span", { class: last
      ? "co-name co-last" : "co-name" }, p.name,
    authorInfoBtn(p.id, p.name, show)));
  });
  return out;
}

// el holds authorNames(): "wrapped" when its
// names do not fit on one line
const namesFit = typeof ResizeObserver === "undefined"
  ? null : new ResizeObserver((all) => {
    for (const e of all) fitNames(e.target);
  });
function fitNames(el) {
  if (!el.isConnected) {
    if (namesFit) namesFit.unobserve(el);
    return;
  }
  const names = el.querySelectorAll(".co-name");
  if (names.length < 2) return;
  el.classList.remove("wrapped");
  const first = names[0].getBoundingClientRect();
  const last = names[names.length - 1]
    .getBoundingClientRect();
  if (last.top >= first.bottom - 1) {
    el.classList.add("wrapped");
  }
}
function watchNames(el) {
  if (namesFit) namesFit.observe(el);
  else requestAnimationFrame(() => fitNames(el));
  return el;
}

function libraryRow(b, by) {
  const meta = h("span", { class: "meta",
    lang: LANG });
  if (b.parts > 1) meta.append(plural(b.parts, "part"));
  if (b.done) {
    meta.append(h("span", { class: "done" },
      b.done === b.parts ? t("lib.done")
        : t("lib.done") + " " + b.done + "/"
          + b.parts));
  }
  // a long book opens on its page, a short one in
  // the reader
  const a = h("a", { class: "row",
    href: b.parts > 1 ? folderHref(dirOf(b.first))
      : "#/read/" + enc(b.first) },
  icon(ICONS.book, "ico"),
  h("span", { class: "name" }, b.name,
    by ? h("span", { class: "by" }, by) : null),
  meta);
  // the full title, when the name is short
  if (b.title !== b.name) a.title = b.title;
  return a;
}

// a tab's list slides in from the side of its tab
// (dir > 0: from the right). Only the rows on the
// screen move: a whole long list at once is too
// much for a phone, which then shows no slide.
function slideIn(pane, dir) {
  if (matchMedia("(prefers-reduced-motion: reduce)")
    .matches) return;
  const rows = pane.querySelectorAll(
    "h2, li, p.empty");
  for (const r of rows) {
    const box = r.getBoundingClientRect();
    if (box.bottom < 0) continue;
    if (box.top > innerHeight) break;
    r.animate([
      { transform: `translateX(${dir * 48}px)`,
        opacity: 0 },
      { transform: "none", opacity: 1 },
    ], { duration: 250, easing: "ease-out" });
  }
}

// #/library: the Grabar books, by author, or the
// starred ones, or those being read (tabs);
// #/library/<author> scrolls to that author
// a long book's parts open under its row, on the
// same page (the row's click; "the book's page" is
// a link in the list). The parts come from the
// book's page data once, at the first opening.
function openParts(li, b) {
  const row = li.querySelector(".row");
  const meta = row.querySelector(".meta");
  const chev = icon(ICONS.fold, "chev");
  meta.prepend(chev);
  row.setAttribute("aria-expanded", "false");
  let panel = null;
  row.addEventListener("click", async (e) => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey
      || e.shiftKey || e.button) return;
    e.preventDefault();
    const on = row.getAttribute("aria-expanded")
      !== "true";
    row.setAttribute("aria-expanded", String(on));
    li.classList.toggle("open", on);
    if (panel) {
      panel.hidden = !on;
      return;
    }
    panel = h("li", { class: "parts", lang: LANG });
    li.after(panel);
    try {
      const dir = dirOf(b.first);
      const data = await api("volume?folder="
        + encodeURIComponent(dir));
      const list = h("ul", { class: "shelf" });
      for (const g of data.groups) {
        if (g.label) {
          list.append(h("li", { class: "group" },
            g.label));
        }
        for (const p of g.parts) {
          list.append(h("li", {}, partRow(p)));
        }
      }
      panel.replaceChildren(list,
        h("a", { class: "parts-page",
          href: folderHref(dir) }, t("lib.bookpage")));
    } catch (err) {
      panel.remove();
      panel = null;
      row.setAttribute("aria-expanded", "false");
      li.classList.remove("open");
    }
  });
}

async function libraryPage(who) {
  const [data, recent] = await Promise.all([
    api("library"),
    api("recent?n=0").catch(() => ({ items: [] })),
  ]);
  document.title = t("nav.library") + " · " + NAME;
  let stars = data.stars || [];
  // first file -> the book and its author
  const books = new Map();
  for (const a of data.authors) {
    for (const b of a.books) {
      books.set(b.first,
        { b, by: byLine(b.with, a.name) });
    }
  }
  let buttons = [];
  // ☆ beside a book
  const starBtn = (b) => {
    const btn = h("button", { type: "button",
      class: "star" });
    btn.dataset.name = b.first;
    btn.addEventListener("click", async () => {
      try {
        stars = await toggleStar(b.first);
      } catch (e) {
        return;
      }
      drawStars();
    });
    buttons.push(btn);
    return btn;
  };
  const empty = (msg) => h("p", { class: "empty",
    lang: LANG }, msg);
  // what the find box finds: authors and books, in
  // the order shown (libraryFind())
  const finds = [];
  // the panes, one per tab
  const groups = data.authors.map((a) => {
    const id = a.folder.split("/").pop();
    const list = h("ul", { class: "shelf" });
    // co-authors of all its books go in the
    // heading, others under a book's name
    const page = a.page;
    const co = a.with || [];
    const shared = new Set(co.map((c) => c.id));
    const rows = a.books.map((b) => {
      const own = (b.with || []).filter(
        (c) => !shared.has(c.id));
      const li = bookItem(b, libraryRow(b,
        own.length ? byLine(own, a.name) : null),
      starBtn(b));
      if (b.parts > 1 && !page) openParts(li, b);
      list.append(li);
      return { el: li, names: [b.name, b.title,
        ...own.map((c) => c.name)],
      ids: own.map((c) => c.id), book: b.id };
    });
    // an author whose books are grouped (the Bible)
    // has a page of its own (flat_author())
    const head = co.length
      ? watchNames(h("h2", { class: "co-names" },
        ...authorNames(co.concat([{ id,
          name: a.name }]))))
      : h("h2", {}, page
        ? h("a", { href: "#/b/" + enc(a.folder) },
          a.name)
        : a.name, authorInfoBtn(id, a.name));
    finds.push({ el: head, names: [a.name,
      ...co.map((c) => c.name)],
    ids: [id, ...co.map((c) => c.id)] }, ...rows);
    return h("section", { class: "author",
      id: "author-" + id }, head, list);
  });
  const panes = {
    all: h("div", {}, groups.length ? groups
      : empty(t("lib.none"))),
    starred: h("div"),
    reading: h("div"),
  };
  // being read: each opens where it was left
  const reading = readingBooks(data, recent.items);
  const readList = h("ul", { class: "shelf" });
  for (const r of reading) {
    const row = libraryRow(r.b, r.by);
    setRoute(row, "#/read/" + enc(r.at));
    const meta = row.querySelector(".meta");
    const fill = h("span");
    fill.style.width = r.progress + "%";
    meta.lang = LANG;
    meta.replaceChildren(
      (r.part ? t("lib.part", r.part) : "")
        + r.progress + "%",
      h("span", { class: "progress", role: "img",
        "aria-label": r.progress + "%" }, fill));
    const x = h("button", { type: "button",
      class: "forget",
      "aria-label": t("forget.title"),
      title: t("forget.title") },
    icon(ICONS.bin));
    x.addEventListener("click", async () => {
      if (!await askForget(r.b.name)) return;
      x.disabled = true;
      try {
        for (const n of r.names) await forget(n);
      } catch (e) {
        x.disabled = false;
        return;
      }
      route();
    });
    readList.append(
      bookItem(r.b, row, starBtn(r.b), x));
  }
  panes.reading.append(reading.length ? readList
    : empty(t("lib.noread")));
  // the tabs
  const n = data.authors.reduce(
    (k, a) => k + a.books.length, 0);
  const count = (k) => h("span", { class: "count" },
    String(k));
  const starCount = count(0);
  const labels = {
    all: [t("lib.all"), count(n)],
    starred: [t("lib.starred"), starCount],
    reading: [t("lib.reading"), reading.length
      ? count(reading.length) : null],
  };
  const tabs = h("div", { class: "lib-tabs",
    role: "tablist", "aria-label": t("nav.library") },
  h("span", { class: "thumb",
    "aria-hidden": "true" }));
  const tabBtn = {};
  for (const t of LIB_TABS) {
    const b = h("button", { type: "button",
      role: "tab", id: "tab-" + t,
      "aria-controls": "lib-" + t },
    h("span", { class: "label" }, labels[t][0]),
    labels[t][1]);
    b.addEventListener("click",
      () => pick(t, true, true));
    tabBtn[t] = b;
    tabs.append(b);
    Object.assign(panes[t], { id: "lib-" + t });
    panes[t].setAttribute("role", "tabpanel");
    panes[t].setAttribute("aria-labelledby",
      "tab-" + t);
  }
  const drawStars = () => {
    const list = h("ul", { class: "shelf" });
    for (const k of stars) {
      const x = books.get(k);
      if (!x) continue;
      list.append(bookItem(x.b,
        libraryRow(x.b, x.by), starBtn(x.b)));
    }
    const k = list.children.length;
    panes.starred.replaceChildren(k ? list
      : empty(t("lib.nostars")));
    starCount.textContent = String(k);
    starCount.hidden = !k;
    buttons = buttons.filter((x) => x.isConnected);
    for (const x of buttons) {
      const on = stars.includes(x.dataset.name);
      x.textContent = on ? "★" : "☆";
      x.setAttribute("aria-pressed", String(on));
      x.title = on ? t("star.off") : t("star.on");
    }
  };
  const pick = (tab, keep, slide) => {
    const from = LIB_TABS.indexOf(tabs.dataset.tab);
    tabs.dataset.tab = tab;
    for (const t of LIB_TABS) {
      const on = t === tab;
      tabBtn[t].setAttribute("aria-selected",
        String(on));
      tabBtn[t].tabIndex = on ? 0 : -1;
      panes[t].hidden = !on;
    }
    if (slide) {
      // scrolled down the list before: the new
      // one from its start, just below the tabs
      const top = panes[tab].getBoundingClientRect()
        .top - tabs.offsetHeight;
      if (top < 0) scrollBy(0, top);
      const to = LIB_TABS.indexOf(tab);
      if (to !== from) slideIn(panes[tab], to - from);
    }
    if (!keep) return;
    try {
      localStorage.setItem(LIB_TAB, tab);
    } catch (e) {}
  };
  // ← and → move between the tabs
  tabs.addEventListener("keydown", (e) => {
    const step = { ArrowLeft: -1, ArrowRight: 1 }[e.key];
    if (!step) return;
    const i = LIB_TABS.indexOf(tabs.dataset.tab);
    const t = LIB_TABS[(i + step + 3) % 3];
    pick(t, true, true);
    tabBtn[t].focus();
  });
  // a swipe left or right on the page moves to the
  // next tab or the one before (not past the ends);
  // the new list slides in from that side
  // the names of authors and books: Armenian
  const body = h("div", { class: "lib-panes",
    lang: "hy" },
    panes.all, panes.starred, panes.reading);
  let touch = null;
  // the whole page, so a short list is no smaller
  // a place to swipe
  const page = main;
  const onStart = (e) => {
    const p = e.touches[0];
    // one finger, away from the screen's edges
    // (the phone's own back gesture)
    touch = e.touches.length === 1
      && p.clientX > 24
      && p.clientX < innerWidth - 24
      ? { x: p.clientX, y: p.clientY,
        t: Date.now() } : null;
  };
  const onEnd = (e) => {
    // gone to another page
    if (!body.isConnected) {
      page.removeEventListener("touchstart",
        onStart);
      page.removeEventListener("touchend", onEnd);
      return;
    }
    if (!touch) return;
    const p = e.changedTouches[0];
    const dx = p.clientX - touch.x;
    const dy = p.clientY - touch.y;
    const quick = Date.now() - touch.t < 700;
    touch = null;
    if (!quick || Math.abs(dx) < 60
      || Math.abs(dx) < 2 * Math.abs(dy)) return;
    const i = LIB_TABS.indexOf(tabs.dataset.tab);
    const t = LIB_TABS[i + (dx < 0 ? 1 : -1)];
    if (!t) return;
    pick(t, true, true);
  };
  page.addEventListener("touchstart", onStart,
    { passive: true });
  page.addEventListener("touchend", onEnd,
    { passive: true });
  // a found one or an author just below the stuck
  // find box and tabs; a book with its author's
  // name above it, when both fit
  const toView = (el) => {
    const stuck = parseFloat(
      getComputedStyle(tabs).top) || 0;
    const room = innerHeight - stuck
      - tabs.offsetHeight;
    const head = el.closest(".author")
      ?.querySelector("h2");
    const box = el.getBoundingClientRect();
    if (head && box.bottom - head
      .getBoundingClientRect().top < room * 0.6) {
      el = head;
    }
    scrollTo(0, el.getBoundingClientRect().top
      + scrollY - stuck - tabs.offsetHeight - 12);
  };
  // the Library's own find box, in place of the
  // search of the books (withSearch())
  const find = libraryFind(finds, toView, () => {
    if (tabs.dataset.tab !== "all") {
      pick("all", false);
    }
  });
  showBare(find,
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("div", { class: "library" },
      h("h1", {}, t("nav.library")),
      h("p", { class: "sub" }, t("lib.sub", n),
        h("a", { href: "#/reference" },
          t("nav.reference") + " →")),
      tabs, body));
  drawStars();
  // the lists at least a screen high: a short one
  // still lets the tabs stay where they are, at the
  // top of the screen, when switched to
  body.style.minHeight =
    `calc(100vh - ${tabs.offsetHeight}px)`;
  // an author's link opens all the books
  pick(who ? "all" : libraryTab(), false);
  const at = who
    && document.getElementById("author-" + who);
  // after setStick() has measured the find box
  // (withSearch(), the frame before)
  if (at) requestAnimationFrame(() => toView(at));
}

// The Library's find box: authors and books whose
// name has the words (nameFits()), an author also
// by its English or Russian name; each found one in
// turn (Enter, ▼; Shift+Enter, ▲), scrolled into
// view by show. items: { el, names, ids, book? }
// in the order shown, ids the authors and
// co-authors whose other names count, book the
// id whose card's titles count (/api/authors
// "titles"); all() opens the tab of all books.
function libraryFind(items, show, all) {
  const input = h("input", { type: "search",
    name: "find",
    placeholder: t("lib.find") + "…",
    "aria-label": t("lib.find"),
    enterkeyhint: "search", autocomplete: "off",
    autocapitalize: "off", spellcheck: "false" });
  const count = h("span", { class: "lf-count",
    "aria-live": "polite" });
  const step = (ico, label, d) => {
    const b = btn(icon(ico), () => go(d), {
      class: "lf-step", "aria-label": label,
      title: label });
    b.hidden = true;
    return b;
  };
  const prev = step(ICONS.up, t("prev"), -1);
  const next = step(ICONS.down, t("next"), 1);
  // the count and the steps in one chip
  const chip = h("span", { class: "lf-chip" },
    count, prev, next);
  const clear = h("button", { type: "button",
    class: "sbox-x", "aria-label": t("clear"),
    title: t("clear") }, "✕");
  clear.hidden = true;
  chip.hidden = true;
  let names = {};
  let titles = {};
  authorsAbout().then((d) => {
    names = d.names || {};
    titles = d.titles || {};
    if (input.value.trim()) run();
  });
  let found = [];
  let at = 0;
  const mark = () => {
    found.forEach((x, i) => x.el.classList
      .toggle("lf-now", i === at));
    count.textContent = !found.length ? t("none")
      : found.length === 1 ? "1"
        : at + 1 + " / " + found.length;
    if (found.length) show(found[at].el);
  };
  const run = () => {
    for (const x of found) {
      x.el.classList.remove("lf-hit", "lf-now");
    }
    const q = input.value.trim();
    clear.hidden = !input.value;
    found = [];
    at = 0;
    if (q) {
      const fits = nameFits(q);
      const other = (id) => Object.entries(
        names[id] || {}).some(([l, n]) => l !== "hy"
        && fits(n));
      found = items.filter((x) => x.names.some(fits)
        || x.ids.some(other)
        || Object.values(titles[x.book] || {})
          .some(fits));
      all();
    }
    for (const x of found) x.el.classList.add("lf-hit");
    chip.hidden = !q;
    chip.classList.toggle("lf-none", !found.length);
    chip.classList.toggle("lf-one",
      found.length === 1);
    prev.hidden = next.hidden = found.length < 2;
    if (q) mark();
  };
  const go = (d) => {
    if (!found.length) return;
    at = (at + d + found.length) % found.length;
    mark();
  };
  input.addEventListener("input", run);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.shiftKey) {
      e.preventDefault();
      go(-1);
    } else if (e.key === "Escape" && input.value) {
      input.value = "";
      run();
    }
  });
  clear.addEventListener("click", () => {
    input.value = "";
    run();
    input.focus();
  });
  const form = h("form", { class: "sbox lib-find",
    role: "search" },
  icon(ICONS.search), input, chip, clear);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    go(1);
  });
  const wrap = h("div", { class: "search-wrap" }, form);
  stickBelow(wrap);
  return withHome(wrap);
}

// The site's mark on the left of a stuck search box
// (wrap, .search-wrap): home, as in the reader's
// tools, once the top bar with its own mark is
// scrolled away (.away); the Library and the search
// page
function withHome(wrap) {
  const home = h("a", { class: "box-home",
    href: "#/", "aria-label": t("nav.home"),
    title: t("nav.home") },
  document.querySelector(".brand-mark")
    .cloneNode(true));
  wrap.classList.add("home-wrap");
  wrap.prepend(home);
  const seen = new IntersectionObserver(([e]) => {
    if (!wrap.isConnected && wrap.dataset.shown) {
      seen.disconnect();
      return;
    }
    wrap.dataset.shown = "1";
    wrap.classList.toggle("away", !e.isIntersecting);
  });
  seen.observe(topBar.parentNode);
  return wrap;
}

// -- timeline --

// the kinds of events: KINDS in nxgir_timeline.py
const KINDS = ["Start", "Books", "Translation",
  "Reader", "Dictionary", "Texts", "Site"];


// "2026-11-07" as a date at noon UTC, so the day
// is the same in every time zone
function isoDate(iso) {
  return new Date(iso + "T12:00:00Z");
}

// "2026-11-07": "7 Nov", or "7 Nov 2026" (the
// month in LANG)
function day(iso, year) {
  const d = isoDate(iso);
  return d.getUTCDate() + " " +
    t("months")[d.getUTCMonth()] +
    (year ? " " + d.getUTCFullYear() : "");
}

// days from start to iso (or today), the first 1
function dayNo(start, iso) {
  const end = iso ? isoDate(iso)
    : isoDate(new Date().toISOString().slice(0, 10));
  return Math.round((end - isoDate(start)) /
    86400000) + 1;
}

// where an event's link goes (link_to() in
// nxgir_web.py), or ""
function eventHref(e) {
  if (e.to === "read") return "#/read/" + enc(e.link);
  if (e.to === "folder") return folderHref(e.link);
  if (e.to === "url") return e.link;
  return "";
}

function eventLink(e) {
  const to = eventHref(e);
  if (!to) return null;
  const label = e.to === "url"
    ? e.link.replace(/^https:\/\//, "")
      .replace(/\/$/, "")
    : e.to === "read" ? t("read.go") : t("open.go");
  return h("p", { class: "links" },
    h("a", { href: to }, label));
}

function eventItem(e) {
  return h("li", { class: "ev" +
      (e.big ? " big" : ""), "data-kind": e.kind },
    h("h3", {},
      h("span", { class: "chip" },
        t("kind." + e.kind)),
      h("span", { lang: "en" }, named(e.title))),
    e.text ? h("p", { lang: "en" }, named(e.text))
      : null,
    eventLink(e));
}

// the events, newest first, under their days;
// only those of kind, if one is given
function eventList(data, kind) {
  const list = h("ol", { class: "tl" });
  let last = "";
  for (const e of data.events) {
    if (kind && e.kind !== kind) continue;
    if (e.date !== last) {
      last = e.date;
      list.append(h("li", { class: "day" },
        h("b", {}, day(e.date, true)),
        t("tl.day", dayNo(data.start, e.date))));
    }
    list.append(eventItem(e));
  }
  return list;
}

async function timelinePage() {
  const data = await api("timeline");
  document.title = t("nav.timeline") + " · " + NAME;
  const stat = (n, label) => h("div", {},
    h("b", {}, String(n)), h("span", {}, label));
  // a filter for each kind with more than one
  // event, in the order of KINDS
  const kinds = KINDS.filter((k) => data.events
    .filter((e) => e.kind === k).length > 1);
  let list = eventList(data, "");
  const filters = h("div", { class: "filters",
    role: "group", "aria-label": t("show") });
  for (const k of ["", ...kinds]) {
    const b = h("button", { type: "button",
      "aria-pressed": String(!k) },
    k ? t("kind." + k) : t("all"));
    b.addEventListener("click", () => {
      for (const o of filters.children) {
        o.setAttribute("aria-pressed",
          String(o === b));
      }
      const next = eventList(data, k);
      list.replaceWith(next);
      list = next;
    });
    filters.append(b);
  }
  show(
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("h1", {}, t("nav.timeline")),
    h("p", { class: "sub" }, named(t("tl.sub"))),
    t("tl.en") ? h("p", { class: "sub" }, t("tl.en"))
      : null,
    data.start ? h("div", { class: "stats" },
      stat(dayNo(data.start), t("tl.days")),
      stat(data.books, t("tl.books")),
      stat(data.parts, t("tl.parts")))
      : null,
    kinds.length > 1 ? filters : null,
    list,
    data.next.length ? h("section", {},
      h("h2", { class: "tl-next" }, t("tl.next")),
      h("ol", { class: "tl next" },
        data.next.map(eventItem))) : null,
    h("p", { class: "more-link" },
      h("a", { href: "#/stats" }, t("tl.limits")))
  );
}

// -- blog --

// the languages of the posts: LANGS in
// nxgir_blog.py, with the page's own words
const BLOG = {
  hy: { name: "Հայերեն", title: "Բլոգ",
    sub: "Նորություններ և նշումներ Նախագրից",
    home: "← Գլխավոր", none: "Գրառումներ դեռ չկան։",
    read: "Կարդալ →" },
  en: { name: "English", title: "Blog",
    sub: "News and notes from nxGir",
    home: "← Home", none: "No posts yet.",
    read: "Read →" },
  ru: { name: "Русский", title: "Блог",
    sub: "Новости и заметки nxGir",
    home: "← Главная", none: "Записей пока нет.",
    read: "Читать →" },
};
// the themes of the posts: THEMES in nxgir_blog.py;
// each has a sub page, #/blog/theme/<name>
const BLOG_THEMES = {
  site: { hy: "Կայքի մասին", en: "About the site",
    ru: "О сайте" },
  authors: { hy: "Հեղինակների մասին",
    en: "About authors", ru: "Об авторах" },
  books: { hy: "Գրքերի մասին", en: "About books",
    ru: "О книгах" },
};

const MONTHS_HY = ["հունվարի", "փետրվարի",
  "մարտի", "ապրիլի", "մայիսի", "հունիսի",
  "հուլիսի", "օգոստոսի", "սեպտեմբերի",
  "հոկտեմբերի", "նոյեմբերի", "դեկտեմբերի"];
const MONTHS_RU = ["января", "февраля", "марта",
  "апреля", "мая", "июня", "июля", "августа",
  "сентября", "октября", "ноября", "декабря"];

// "2026-11-07" in lang, with the year
function longDay(iso, lang) {
  const d = isoDate(iso);
  const n = d.getUTCDate();
  const m = d.getUTCMonth();
  const y = d.getUTCFullYear();
  if (lang === "hy") {
    return y + " թ. " + MONTHS_HY[m] + " " + n;
  }
  if (lang === "ru") {
    return n + " " + MONTHS_RU[m] + " " + y;
  }
  return day(iso, true);
}

// The pages with a language picker of their own
// (the blog, comics, map and Features; the author
// cards and Reference; the announcements; the
// meanings of words) show the language of the
// address; one picked there is kept for that kind
// of page until the language of the site changes.
const pagePick = {};
window.addEventListener("langchange", () => {
  for (const k of Object.keys(pagePick)) {
    delete pagePick[k];
  }
});
// the pickers' own languages once kept in the
// browser: the address says it now
try {
  for (const k of ["nxgir-blog-lang",
    "nxgir-author-lang", "nxgir-lang"]) {
    localStorage.removeItem(k);
  }
} catch (e) {}

// the language of the blog's pages: the one picked
// there, else the site's
function blogLang() {
  return pagePick.blog || LANG;
}

function setBlogLang(lang) {
  pagePick.blog = lang;
}

// a post's version in lang, or its first one
function version(p, lang) {
  return p.versions.find((v) => v.lang === lang)
    || p.versions[0];
}

// the places a post or series names, as links to the
// map: the names (by id) come from the map's data;
// null when it names none or the data is missing
async function placeNames(item) {
  if (!item || !item.places || !item.places.length) {
    return null;
  }
  try {
    const m = await api("map");
    return new Map(m.places.map((x) => [x.id, x.names]));
  } catch (e) {
    return null;
  }
}

function placeChips(item, names, lang) {
  const ids = names
    ? item.places.filter((id) => names.has(id)) : [];
  if (!ids.length) return null;
  return h("p", { class: "post-places", lang },
    icon(ICONS.map),
    h("span", {}, ids.flatMap((id, i) => [i ? ", " : "",
      h("a", { href: "#/map/" + id },
        names.get(id)[lang])])));
}

// one post: its date, title and text (parse()
// in nxgir_blog.py: ["p", text], ["h", text] or
// ["img", file, alt])
function postItem(p, lang) {
  const v = version(p, lang);
  return h("article", { class: "post p-" + p.slug,
    id: "post-" + p.slug, lang: v.lang },
  h("time", { datetime: p.date },
    longDay(p.date, v.lang)),
  h("h2", {},
    h("a", { href: "#/blog/" + p.slug },
      named(v.title))),
  v.blocks.map(([kind, text, alt]) =>
    kind === "img"
      ? h("img", { src: "img/" + text, alt,
        loading: "lazy" })
      : h(kind === "h" ? "h3" : "p",
        kind === "cap" ? { class: "cap" } : {},
        named(text))));
}

// a post in the list: a card with its date,
// title and first paragraph, the whole card a
// link to the post's own page
function postCard(p, lang) {
  const v = version(p, lang);
  const lead = v.blocks.find(([k]) => k === "p");
  return h("a", { class: "post-card",
    href: "#/blog/" + p.slug, lang: v.lang },
  h("span", { class: "pc-top" },
    h("time", { datetime: p.date },
      longDay(p.date, v.lang)),
    h("span", { class: "pc-more" },
      BLOG[v.lang].read)),
  h("span", { class: "pc-title" }, named(v.title)),
  lead ? h("span", { class: "pc-lead" },
    named(lead[1]))
    : null);
}

// #/blog: the posts about the site, newest first,
// always: no theme is remembered; #/blog/<slug>
// that one post; #/blog/<slug>/<lang> in lang;
// #/blog/theme/<name> the posts of one theme
async function blogPage(path) {
  let [slug, want] = path.split("/");
  let theme = null;
  if (slug === "theme") {
    theme = want;
    if (!(theme in BLOG_THEMES)) {
      throw new Error(t("err.theme"));
    }
    slug = want = "";
  }
  const home = !slug && !theme;
  if (home) theme = "site";
  const data = await api("blog");
  const one = slug
    ? data.posts.find((p) => p.slug === slug) : null;
  if (slug && !one) throw new Error(t("err.post"));
  const names = await placeNames(one);
  const posts = theme
    ? data.posts.filter((p) => p.theme === theme)
    : data.posts;
  const draw = () => {
    // the languages the posts on this page have;
    // the one picked, if they have it
    const have = new Set((one ? [one] : posts)
      .flatMap((p) => p.versions.map((v) => v.lang)));
    const langs = Object.keys(BLOG)
      .filter((l) => have.has(l));
    const lang = have.has(blogLang()) || !langs.length
      ? blogLang() : langs[0];
    const t = BLOG[lang];
    const pick = h("div", { class: "filters outline",
      role: "group", "aria-label": "Language" },
    langs.map((l) => {
      const b = h("button", { type: "button",
        lang: l, "aria-pressed": String(l === lang) },
      BLOG[l].name);
      b.addEventListener("click", () => {
        setBlogLang(l);
        draw();
      });
      return b;
    }));
    // one tab for each theme
    const tabs = h("nav", { class: "filters outline themes",
      "aria-label": "Themes", lang },
    Object.entries(BLOG_THEMES).map(([k, v]) =>
      h("a", { href: k === "site" ? "#/blog"
        : "#/blog/theme/" + k,
      "aria-current": k === theme ? "page" : null },
      v[lang])));
    const name = theme && !home
      ? BLOG_THEMES[theme][lang] : "";
    document.title = (one ? version(one, lang).title
      + " · " : "") + (name ? name + " · " : "")
      + t.title + " · " + NAME;
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, t.home),
        one || !home ? [" · ", h("a", { href: "#/blog" },
          t.title)] : null,
        one && one.theme ? [" · ", h("a", {
          href: "#/blog/theme/" + one.theme },
        BLOG_THEMES[one.theme][lang])] : null),
      one ? null : h("h1", { lang }, name || t.title),
      one ? null : h("p", { class: "sub", lang },
        named(t.sub)),
      one ? null : tabs,
      langs.length > 1 ? pick : null,
      one ? placeChips(one, names, lang) : null,
      h("div", {
        class: "blog" + (one ? " one p-" + one.slug : "") },
        one ? postItem(one, lang)
          : posts.length
            ? posts.map((p) => postCard(p, lang))
            : h("p", { class: "empty", lang },
              t.none)));
  };
  draw();
}

// -- comics --

// the words of the Comics page, by language
const COMICS_UI = {
  hy: { title: "Կոմիքսներ",
    sub: "Գրադարանի գրքերի տեսարանները նկարներով",
    none: "Շարքեր դեռ չկան։" },
  en: { title: "Comics",
    sub: "Scenes from the books of the Library",
    none: "No series yet." },
  ru: { title: "Комиксы",
    sub: "Сцены из книг Библиотеки",
    none: "Серий пока нет." },
};

// a series in the list: its first picture as the
// cover, its date, title and intro, the whole card
// a link to the series' own page
function comicCard(s, lang) {
  const v = version(s, lang);
  const lead = v.blocks.find(([k]) => k === "p");
  const cover = v.blocks.find(([k]) => k === "img");
  return h("a", { class: "post-card comic-card",
    href: "#/comics/" + s.slug, lang: v.lang },
  cover ? h("img", { src: "img/" + cover[1],
    alt: cover[2], loading: "lazy" }) : null,
  h("span", { class: "pc-top" },
    h("time", { datetime: s.date },
      longDay(s.date, v.lang)),
    h("span", { class: "pc-more" },
      BLOG[v.lang].read)),
  h("span", { class: "pc-title" }, named(v.title)),
  lead ? h("span", { class: "pc-lead" },
    named(lead[1])) : null);
}

// one series, whole: the pages (pictures with their
// notes) one under the other, full width
function comicItem(s, lang) {
  const v = version(s, lang);
  return h("article", { class: "post comic p-" + s.slug,
    lang: v.lang },
  h("time", { datetime: s.date },
    longDay(s.date, v.lang)),
  h("h2", {}, named(v.title)),
  v.blocks.map(([kind, text, alt]) =>
    kind === "img"
      ? h("img", { src: "img/" + text, alt,
        loading: "lazy" })
      : h(kind === "h" ? "h3" : "p",
        kind === "cap" ? { class: "cap" } : {},
        named(text))));
}

// #/comics: the series, newest first; #/comics/<slug>
// one series; #/comics/<slug>/<lang> in lang (the
// language is the blog's choice)
async function comicsPage(path) {
  const [slug] = path.split("/");
  const data = await api("comics");
  const one = slug
    ? data.series.find((s) => s.slug === slug) : null;
  if (slug && !one) throw new Error(t("err.series"));
  const names = await placeNames(one);
  const draw = () => {
    const have = new Set((one ? [one] : data.series)
      .flatMap((s) => s.versions.map((v) => v.lang)));
    const langs = Object.keys(BLOG)
      .filter((l) => have.has(l));
    const lang = have.has(blogLang()) || !langs.length
      ? blogLang() : langs[0];
    const t = COMICS_UI[lang];
    const pick = h("div", { class: "filters outline",
      role: "group", "aria-label": "Language" },
    langs.map((l) => {
      const b = h("button", { type: "button",
        lang: l, "aria-pressed": String(l === lang) },
      BLOG[l].name);
      b.addEventListener("click", () => {
        setBlogLang(l);
        draw();
      });
      return b;
    }));
    document.title = (one ? version(one, lang).title
      + " · " : "") + t.title + " · " + NAME;
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, BLOG[lang].home),
        one ? [" · ", h("a", { href: "#/comics" },
          t.title)] : null),
      one ? null : h("h1", { lang }, t.title),
      one ? null : h("p", { class: "sub", lang },
        t.sub),
      langs.length > 1 ? pick : null,
      one ? placeChips(one, names, lang) : null,
      one ? h("div", { class: "blog one comics" },
        comicItem(one, lang))
        : h("div", { class: "blog comics-list" },
          data.series.length
            ? data.series.map((s) => comicCard(s, lang))
            : h("p", { class: "empty", lang }, t.none)));
  };
  draw();
}

// -- map --

// #/map: the painted map of the Armenian Highland
// (map/places.tsv, nxgir_map.py): a pin on each
// place, a card with the posts and comics that name
// it; #/map/<place> opens that place
const MAP_UI = {
  hy: { title: "Քարտեզ",
    sub: "Գրառումներն ու կոմիքսները՝ իրենց վայրերում",
    all: "Բոլորը", blog: "Բլոգ", comics: "Կոմիքս",
    places: "Վայրեր",
    none: "Այս վայրի մասին գրառումներ դեռ չկան։",
    zin: "Մոտեցնել", zout: "Հեռացնել",
    reset: "Ամբողջ քարտեզը", close: "Փակել",
    list: "Բոլոր վայրերը",
    map: "Հայկական լեռնաշխարհի քարտեզ",
    kinds: { city: "Քաղաք", fortress: "Բերդ",
      monastery: "Վանք", region: "Գավառ",
      lake: "Լիճ", mountain: "Լեռ" } },
  en: { title: "Map",
    sub: "Posts and comics, each at its place",
    all: "All", blog: "Blog", comics: "Comics",
    places: "Places",
    none: "No posts about this place yet.",
    zin: "Zoom in", zout: "Zoom out",
    reset: "Whole map", close: "Close",
    list: "All places",
    map: "Map of the Armenian Highland",
    kinds: { city: "City", fortress: "Fortress",
      monastery: "Monastery", region: "Region",
      lake: "Lake", mountain: "Mountain" } },
  ru: { title: "Карта",
    sub: "Записи и комиксы на своих местах",
    all: "Все", blog: "Блог", comics: "Комиксы",
    places: "Места",
    none: "О этом месте записей пока нет.",
    zin: "Приблизить", zout: "Отдалить",
    reset: "Вся карта", close: "Закрыть",
    list: "Все места",
    map: "Карта Армянского нагорья",
    kinds: { city: "Город", fortress: "Крепость",
      monastery: "Монастырь", region: "Область",
      lake: "Озеро", mountain: "Гора" } },
};
const MAP_MAX = 3;
const MAP_FRESH = 14 * 24 * 3600 * 1000;

// where a story is read
function storyHref(s) {
  return "#/" + (s.type === "comics" ? "comics/" : "blog/")
    + s.slug;
}

// a place's pin: its stories decide the look
function pinKind(p) {
  if (p.stories.some((s) => s.type === "blog")) {
    return "blog";
  }
  return p.stories.length ? "comics" : "place";
}

// a story in the popup: a link, with its cover small,
// its type and date, and its title
function mapLink(s, lang) {
  const v = version(s, lang);
  const t = MAP_UI[lang];
  return h("a", { class: "map-link",
    href: storyHref(s), lang: v.lang },
  v.cover ? h("img", { src: "img/" + v.cover,
    alt: "", loading: "lazy" }) : null,
  h("span", { class: "ml-text" },
    h("span", { class: "ml-meta" },
      icon(ICONS[s.type === "comics" ? "panels"
        : "book"]),
      h("span", {}, t[s.type] + " · ",
        h("time", { datetime: s.date },
          longDay(s.date, v.lang)))),
    h("span", { class: "ml-title" }, named(v.title))));
}

async function mapPage(path) {
  // map/<place>
  let [want] = path.split("/");
  if (want in BLOG) want = "";
  const data = await api("map");
  const places = data.places;
  const by = new Map(places.map((p) => [p.id, p]));
  const st = { lang: blogLang(), filter: "all",
    sel: by.has(want) ? want : "",
    s: 1, x: 0, y: 0 };
  const shown = (p) => st.filter === "all"
    || (st.filter === "places" ? !p.stories.length
      : p.stories.some((s) => s.type === st.filter));
  const draw = () => {
    const lang = st.lang;
    const t = MAP_UI[lang];
    const nm = (p) => p.names[lang];
    const view = h("div", { class: "map-view",
      tabindex: "0", role: "application",
      "aria-label": t.map });
    const stage = h("div", { class: "map-stage" },
      h("img", { src: data.image, alt: "",
        draggable: "false" }));
    view.append(stage);
    const pins = new Map();
    for (const p of places) {
      const kind = pinKind(p);
      const fresh = p.stories.some((s) =>
        Date.now() - isoDate(s.date) < MAP_FRESH);
      const b = h("button", { type: "button",
        class: "pin pin-" + kind + (fresh ? " fresh" : "")
          + (p.x > 88 ? " pin-r" : ""),
        "aria-label": nm(p) },
      h("span", { class: "pin-dot" },
        kind === "place" ? null
          : icon(ICONS[kind === "blog" ? "book"
            : "panels"])),
      h("span", { class: "pin-label", lang },
        nm(p)));
      // not a style attribute: the CSP forbids it
      b.style.left = p.x + "%";
      b.style.top = p.y + "%";
      b.addEventListener("click", () => {
        if (!moved) pick(p.id, false, false);
      });
      pins.set(p.id, b);
      stage.append(b);
    }
    // the small panel of the place opened, over the map
    const pop = h("section", { class: "map-pop",
      role: "dialog", hidden: "" });
    // not under the finger that drags the map
    pop.addEventListener("pointerdown", (e) =>
      e.stopPropagation());
    view.append(pop);
    // beside its pin (it follows the pin as the map
    // moves); on a narrow map, docked at the bottom
    const placePop = () => {
      const p = by.get(st.sel);
      if (!p || pop.hidden) return;
      const w = view.clientWidth;
      const hh = view.clientHeight;
      const dock = w < 520;
      pop.classList.toggle("dock", dock);
      view.classList.toggle("popped", dock);
      if (dock) {
        pop.style.left = "";
        pop.style.top = "";
        return;
      }
      const px = st.x + p.x / 100 * w * st.s;
      const py = st.y + p.y / 100 * hh * st.s;
      const pw = pop.offsetWidth;
      const ph = pop.offsetHeight;
      let x = px + 22;
      if (x + pw > w - 8) x = px - 22 - pw;
      x = Math.max(8, Math.min(w - pw - 8, x));
      const y = Math.max(8,
        Math.min(hh - ph - 8, py - ph / 2));
      pop.style.left = x + "px";
      pop.style.top = y + "px";
    };
    // the view: zoom and pan, clamped to the picture
    const apply = () => {
      const w = view.clientWidth;
      const hh = view.clientHeight;
      st.s = Math.min(MAP_MAX, Math.max(1, st.s));
      st.x = Math.min(0, Math.max(w - w * st.s, st.x));
      st.y = Math.min(0, Math.max(hh - hh * st.s, st.y));
      stage.style.transform = "translate(" + st.x
        + "px," + st.y + "px) scale(" + st.s + ")";
      stage.style.setProperty("--inv", 1 / st.s);
      stage.classList.toggle("zoomed", st.s >= 2.4);
      view.classList.toggle("in", st.s > 1);
      if (st.sel) placePop();
    };
    const zoomAt = (cx, cy, s2) => {
      s2 = Math.min(MAP_MAX, Math.max(1, s2));
      st.x = cx - (cx - st.x) * s2 / st.s;
      st.y = cy - (cy - st.y) * s2 / st.s;
      st.s = s2;
      apply();
    };
    const center = (zoomIn) => {
      const p = by.get(st.sel);
      if (!p) return;
      const w = view.clientWidth;
      const hh = view.clientHeight;
      if (zoomIn) st.s = Math.max(st.s, 2);
      st.x = w / 2 - p.x / 100 * w * st.s;
      st.y = hh / 2 - p.y / 100 * hh * st.s;
      apply();
    };
    const drawPop = () => {
      const p = by.get(st.sel);
      for (const [id, b] of pins) {
        b.classList.toggle("on", id === st.sel);
        b.setAttribute("aria-pressed",
          String(id === st.sel));
      }
      if (!p) {
        pop.hidden = true;
        pop.replaceChildren();
        view.classList.remove("popped");
        return;
      }
      const close = h("button", { type: "button",
        class: "map-close", "aria-label": t.close },
      "×");
      close.addEventListener("click", closePop);
      pop.lang = lang;
      pop.setAttribute("aria-label", nm(p));
      pop.replaceChildren(close,
        h("p", { class: "map-kind" }, t.kinds[p.kind]),
        h("h2", {}, nm(p)),
        p.stories.length
          ? h("div", { class: "map-links" },
            p.stories.map((s) => mapLink(s, lang)))
          : h("p", { class: "empty" }, t.none));
      pop.hidden = false;
      placePop();
    };
    function closePop() {
      st.sel = "";
      history.replaceState(history.state, "",
        pathOf("#/map"));
      drawPop();
    }
    // move: bring the place to the middle of the view
    function pick(id, zoomIn, move) {
      st.sel = id;
      history.replaceState(history.state, "",
        pathOf("#/map/" + id));
      drawPop();
      if (move) center(zoomIn);
    }
    // drag, pinch; a drag is not a click on a pin
    let moved = false;
    const ptrs = new Map();
    let start = null;
    let pinch = 0;
    const gap = () => {
      const [a, b] = [...ptrs.values()];
      return Math.hypot(a.clientX - b.clientX,
        a.clientY - b.clientY);
    };
    view.addEventListener("pointerdown", (e) => {
      ptrs.set(e.pointerId, e);
      moved = false;
      start = { x: e.clientX, y: e.clientY };
      pinch = ptrs.size === 2 ? gap() : 0;
    });
    view.addEventListener("pointermove", (e) => {
      const prev = ptrs.get(e.pointerId);
      if (!prev) return;
      ptrs.set(e.pointerId, e);
      if (ptrs.size === 2) {
        const [a, b] = [...ptrs.values()];
        const r = view.getBoundingClientRect();
        const d = gap();
        if (pinch) {
          zoomAt((a.clientX + b.clientX) / 2 - r.left,
            (a.clientY + b.clientY) / 2 - r.top,
            st.s * d / pinch);
        }
        pinch = d;
        moved = true;
        return;
      }
      if (!moved && Math.hypot(e.clientX - start.x,
        e.clientY - start.y) < 6) return;
      if (!moved) view.setPointerCapture(e.pointerId);
      moved = true;
      st.x += e.clientX - prev.clientX;
      st.y += e.clientY - prev.clientY;
      apply();
    });
    const lift = (e) => {
      ptrs.delete(e.pointerId);
      pinch = 0;
    };
    view.addEventListener("pointerup", lift);
    view.addEventListener("pointercancel", lift);
    // a tap on the map itself closes the panel
    view.addEventListener("click", (e) => {
      if (moved || !st.sel) return;
      if (e.target.closest(".pin, .map-pop, .map-ctl")) {
        return;
      }
      closePop();
    });
    // ctrl + wheel (a trackpad pinch) zooms; the plain
    // wheel still scrolls the page
    view.addEventListener("wheel", (e) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const r = view.getBoundingClientRect();
      zoomAt(e.clientX - r.left, e.clientY - r.top,
        st.s * Math.exp(-e.deltaY / 200));
    }, { passive: false });
    view.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && st.sel) {
        e.preventDefault();
        closePop();
        return;
      }
      const w = view.clientWidth;
      const hh = view.clientHeight;
      const step = { ArrowLeft: [40, 0],
        ArrowRight: [-40, 0], ArrowUp: [0, 40],
        ArrowDown: [0, -40] }[e.key];
      if (e.key === "+" || e.key === "=") {
        zoomAt(w / 2, hh / 2, st.s * 1.4);
      } else if (e.key === "-") {
        zoomAt(w / 2, hh / 2, st.s / 1.4);
      } else if (step && st.s > 1) {
        st.x += step[0];
        st.y += step[1];
        apply();
      } else {
        return;
      }
      e.preventDefault();
    });
    const ctl = (label, text, fn) => {
      const b = h("button", { type: "button",
        "aria-label": label, title: label }, text);
      b.addEventListener("click", fn);
      return b;
    };
    const mid = (k) => zoomAt(view.clientWidth / 2,
      view.clientHeight / 2, st.s * k);
    view.append(h("div", { class: "map-ctl" },
      ctl(t.zin, "+", () => mid(1.5)),
      ctl(t.zout, "−", () => mid(1 / 1.5)),
      ctl(t.reset, "⌂", () => {
        st.s = 1;
        st.x = 0;
        st.y = 0;
        apply();
      })));
    const hasLang = (l) => places.some((p) =>
      p.stories.some((s) =>
        s.versions.some((v) => v.lang === l)));
    const langs = Object.keys(BLOG).filter(hasLang);
    const group = (items, now, set) => h("div", {
      class: "filters outline", role: "group" },
    items.map(([k, label, lg]) => {
      const b = h("button", { type: "button", lang: lg,
        "aria-pressed": String(k === now) }, label);
      b.addEventListener("click", () => set(k));
      return b;
    }));
    const pickLang = group(
      langs.map((l) => [l, BLOG[l].name, l]), lang,
      (l) => {
        st.lang = l;
        setBlogLang(l);
        draw();
      });
    const pickShow = group(
      ["all", "blog", "comics", "places"].map((k) =>
        [k, t[k], lang]), st.filter,
      (k) => {
        st.filter = k;
        draw();
      });
    for (const p of places) {
      pins.get(p.id).hidden = !shown(p);
    }
    // the same places as a list: for a keyboard, a
    // screen reader, and a map that has not loaded
    const list = h("ul", { class: "map-list", lang },
      [...places].sort((a, b) =>
        b.stories.length - a.stories.length)
        .filter(shown).map((p) => {
          const b = h("button", { type: "button" },
            nm(p));
          b.addEventListener("click", () => {
            pick(p.id, true, true);
            view.scrollIntoView({ block: "nearest" });
          });
          return h("li", {}, b,
            h("span", {}, " · " + t.kinds[p.kind]
              + (p.stories.length
                ? " · " + p.stories.length : "")));
        }));
    document.title = t.title + " · " + NAME;
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, BLOG[lang].home)),
      h("h1", { lang }, t.title),
      h("p", { class: "sub", lang }, t.sub),
      langs.length > 1 ? pickLang : null,
      pickShow,
      h("div", { class: "map-wrap" }, view),
      h("h2", { class: "map-list-h", lang }, t.list),
      list);
    apply();
    drawPop();
    if (st.sel) center(true);
  };
  draw();
}

// -- features --

// the page's blocks as an intro (the paragraphs
// before the first feature) and one card per
// "## " feature with its paragraphs
function featureCards(blocks) {
  const intro = [];
  const list = h("ul", { class: "features" });
  let card = null;
  for (const [kind, text] of blocks) {
    if (kind === "h") {
      card = h("li", {}, h("h2", {}, text));
      list.append(card);
    } else if (card) {
      card.append(h("p", {}, text));
    } else {
      intro.push(h("p", { class: "sub" }, text));
    }
  }
  return [intro, list];
}

// #/features: what the site can do, in the
// language picked for the blog; #/features/<lang>
// in lang
async function featuresPage(want) {
  const data = await api("features");
  const draw = () => {
    const langs = data.versions.map((v) => v.lang);
    const lang = langs.includes(blogLang())
      || !langs.length ? blogLang() : langs[0];
    const v = data.versions.find((x) =>
      x.lang === lang);
    const pick = h("div", { class: "filters outline",
      role: "group", "aria-label": "Language" },
    langs.map((l) => {
      const b = h("button", { type: "button",
        lang: l, "aria-pressed": String(l === lang) },
      BLOG[l].name);
      b.addEventListener("click", () => {
        setBlogLang(l);
        draw();
      });
      return b;
    }));
    document.title = (v ? v.title : "Features")
      + " · " + NAME;
    const [intro, list] = v ? featureCards(v.blocks)
      : [[], null];
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, BLOG[lang].home)),
      h("h1", { lang }, v ? v.title : "Features"),
      h("div", { lang }, intro),
      langs.length > 1 ? pick : null,
      v ? h("div", { lang }, list)
        : h("p", { class: "empty" }, t("nothing")));
  };
  draw();
}

// -- contribute --

// #/contribute: how to help. The translations
// need two kinds of work: first drafts made with
// AI for the parts not yet translated, and people
// who read the drafts beside the Grabar
const HOWTO = REPO + "/blob/main/CONTRIBUTING.md";

// in each language
const WAYS = {
  en: [
    ["Read and review",
      "Every translation starts as a machine draft."
      + " It becomes a book only when someone who"
      + " knows Grabar reads it beside the original,"
      + " line by line, and corrects it.",
      "Open a part, press ⇆ Parallel, and read."
      + " Your name is shown above every part you"
      + " review."],
    ["Translate with AI",
      "Many parts have no translation yet. Make a"
      + " first draft into modern Armenian with an"
      + " AI model, one line for each Grabar line,"
      + " keeping the chapter lines as they are.",
      "A draft goes in as machine, and waits for"
      + " its first reader."],
    ["Bring texts and words",
      "Grabar books that are not here yet, words"
      + " missing from the glossary, abbreviations"
      + " from a printed source, and scans of old"
      + " prints to test with."],
  ],
  hy: [
    ["Կարդալ և ստուգել",
      "Յուրաքանչյուր թարգմանություն սկսվում է"
      + " մեքենայական սևագրից։ Այն գիրք է դառնում միայն"
      + " այն ժամանակ, երբ գրաբար իմացող մեկը կարդում է"
      + " այն բնագրի կողքին՝ տող առ տող, և ուղղում։",
      "Բացեք մի մաս, սեղմեք ⇆ Զուգահեռ և կարդացեք։ Ձեր"
      + " անունը կերևա ձեր ստուգած յուրաքանչյուր մասի"
      + " վերևում։"],
    ["Թարգմանել արհեստական բանականությամբ",
      "Շատ մասեր դեռ թարգմանություն չունեն։ Արհեստական"
      + " բանականության օգնությամբ պատրաստեք աշխարհաբար"
      + " առաջին սևագիրը՝ գրաբարի յուրաքանչյուր տողի"
      + " դիմաց մեկ տող, գլուխների տողերը թողնելով"
      + " անփոփոխ։",
      "Սևագիրը մտնում է որպես մեքենայական և սպասում է"
      + " իր առաջին ընթերցողին։"],
    ["Բերել տեքստեր և բառեր",
      "Գրաբար գրքեր, որոնք դեռ այստեղ չկան, բառարանում"
      + " պակասող բառեր, տպագիր աղբյուրից հապավումներ և"
      + " հին տպագրությունների պատկերներ՝ փորձարկելու"
      + " համար։"],
  ],
  ru: [
    ["Читать и проверять",
      "Каждый перевод начинается с машинного"
      + " черновика. Книгой он становится, только когда"
      + " человек, знающий грабар, прочтёт его рядом с"
      + " оригиналом, строка за строкой, и исправит.",
      "Откройте часть, нажмите ⇆ Параллельно и"
      + " читайте. Ваше имя будет указано над каждой"
      + " частью, которую вы проверите."],
    ["Переводить с ИИ",
      "У многих частей ещё нет перевода. Сделайте с"
      + " помощью модели ИИ первый черновик на"
      + " современный армянский — по строке на каждую"
      + " строку грабара, оставляя строки глав как есть.",
      "Черновик добавляется как машинный и ждёт своего"
      + " первого читателя."],
    ["Приносить тексты и слова",
      "Книги на грабаре, которых здесь ещё нет, слова,"
      + " которых не хватает в словаре, сокращения из"
      + " печатного источника и сканы старых изданий для"
      + " проверки."],
  ],
};

function contributePage() {
  document.title = t("co.title") + " · " + NAME;
  const list = h("ul", { class: "features" },
    (WAYS[LANG] || WAYS.en).map(([title, ...text]) =>
      h("li", {}, h("h2", {}, title),
        text.map((x) => h("p", {}, x)))));
  show(
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("figure", { class: "hero" },
      h("img", { src: "contribute.jpg",
        width: "1200", height: "675",
        alt: t("co.alt") }),
      h("figcaption", { class: "mission" },
        h("p", {}, t("co.mission")),
        h("p", { class: "aside" }, t("co.aside")))),
    h("h1", {}, t("co.title")),
    h("p", { class: "sub" }, named(t("co.sub"))),
    list,
    h("p", { class: "cta" },
      h("a", { class: "cta-main", href: HOWTO },
        t("co.start")),
      h("a", { href: REPO }, t("co.gh"))),
    h("p", { class: "sub" }, t("co.lic1"),
      h("a", { href: BY_SA, rel: "license" },
        "CC BY-SA 4.0"), t("co.lic2")));
}

// -- announcements --

// #/news: what is new on the shelf, newest first.
// Each: a date, a picture, a title, a lead,
// sections [heading, paragraphs...], links
// [label, href] (the first the main one), and the
// two lines of the banner on the top page, over
// face, a crop of the picture
const SMBAT = "#/b/grabar/smbat-sparapet/";

const ZENOB = "#/b/grabar/hovhan-mamikonean/";

// the words of the page itself, by language
const NEWS_UI = {
  hy: { home: "Գլխավոր", title: "Հայտարարություններ",
    read: "Կարդալ →", book: "Կարդալ գիրքը →" },
  en: { home: "Home", title: "Announcements",
    read: "Read →", book: "Read the book →" },
  ru: { home: "Главная", title: "Объявления",
    read: "Читать →", book: "Читать книгу →" },
};

const NEWS = [{
  id: "zenob-glak",
  book: "#/read/grabar/hovhan-mamikonean/"
    + "1-patmutiun-taronoy/01.txt",
  date: "2026-11-22",
  img: "zenob-glak.jpg",
  face: "zenob-glak-face.jpg",
  alt: "Zenob Glak, History of Taron, 4th century:"
    + " a painted map of Taron among mountains,"
    + " a castle on it, and a rider on a cliff",
  title: "The History of Taron on the shelf",
  lead: "The History of Taron (Պատմութիւն"
    + " Տարաւնոյ) tells how a land in the heart of"
    + " the Armenian Highland took a new faith and"
    + " fought for it. Its first part is"
    + " attributed to Zenob Glak (Զենոբ Գլակ), the"
    + " second is by Hovhan Mamikonean. The whole"
    + " book is now in the nxGir Library, in Grabar"
    + " and in modern Armenian, side by side.",
  banner: ["Զենոբ Գլակ",
    "Տարոնի պատմությունը՝ IV դարից. գիրքը"
    + " գրադարանում է"],
  banner_en: ["Zenob Glak",
    "The History of Taron, from the 4th century:"
    + " the book is in the Library"],
  banner_ru: ["Зеноб Глак",
    "История Тарона, с IV века: книга в библиотеке"],
  sections: [
    ["Who he was",
      "By tradition Zenob was a disciple of"
      + " Gregory the Illuminator, who came with him"
      + " from Caesarea; some sources call him a"
      + " Syrian. He was the first abbot of the"
      + " monastery of Surb Karapet in Taron, which"
      + " was called Glakavank after him."],
    ["The first part",
      "Sections Ա–Դ, 654 lines: at Gregory's"
      + " command Zenob writes to the Syrian bishops"
      + " how the new faith took hold in Taron. It"
      + " holds the letters of Gregory and the"
      + " bishops, and the two battles at Ardzan."],
    ["Hovhan Mamikonean's part",
      "Hovhan, a later abbot of Glak, carried the"
      + " book on (sections Ե–ԺԱ): the abbots of"
      + " Glak, and the wars of the Mamikonians of"
      + " Taron against the Persians. Scholars doubt"
      + " that Zenob wrote the first part himself,"
      + " and date the whole book to the 7th to"
      + " 10th centuries."],
    ["Read it",
      "The book, 1704 lines, is in the Library with"
      + " every Grabar line beside its modern"
      + " Armenian translation and every word open"
      + " to look up. The translations are first"
      + " drafts, made with AI: they wait for"
      + " readers who know Grabar to check them."],
  ],
  links: [
    ["Read the History of Taron", ZENOB
      + "1-patmutiun-taronoy"],
    ["Taron on the map", "#/map"],
    ["Help review the translations",
      "#/contribute"],
  ],
  ask: "Which other lands of the Highland have"
    + " a story that is still unread?",
  hy: {
    alt: "Զենոբ Գլակ, Տարոնի պատմություն, IV դար․ "
      + "Տարոնի նկարված քարտեզը լեռների մեջ, "
      + "նրա վրա ամրոց, իսկ ժայռի վրա՝ ձիավոր",
    title: "Տարոնի պատմությունը՝ գրադարանում",
    lead: "«Տարոնի պատմությունը» (Պատմութիւն "
      + "Տարաւնոյ) պատմում է, թե Հայկական "
      + "բարձրավանդակի սրտում գտնվող երկիրն ինչպես "
      + "ընդունեց նոր հավատը և պայքարեց դրա "
      + "համար։ Առաջին մասը վերագրվում է Զենոբ "
      + "Գլակին, երկրորդը Հովհան Մամիկոնյանինն է։ "
      + "Ամբողջ գիրքն այժմ nxGir գրադարանում է՝ "
      + "գրաբարով և աշխարհաբարով, կողք կողքի։",
    sections: [
      ["Ո՞վ էր նա",
        "Ավանդաբար Զենոբը Գրիգոր Լուսավորչի "
        + "աշակերտն էր և նրա հետ եկել էր Կեսարիայից․ "
        + "որոշ աղբյուրներ նրան ասորի են համարում։ "
        + "Նա Տարոնի Սուրբ Կարապետ վանքի առաջին "
        + "առաջնորդն էր, և վանքը նրա անունով կոչվեց "
        + "Գլակավանք։"],
      ["Առաջին մասը",
        "Ա–Դ հատվածները՝ 654 տող։ Գրիգորի "
        + "հրամանով Զենոբը ասորի եպիսկոպոսներին "
        + "գրում է, թե ինչպես նոր հավատը հաստատվեց "
        + "Տարոնում։ Այստեղ են Գրիգորի և "
        + "եպիսկոպոսների նամակները, ինչպես նաև "
        + "Արծանի երկու ճակատամարտերը։"],
      ["Հովհան Մամիկոնյանի մասը",
        "Գլակի հետագա առաջնորդ Հովհանը շարունակեց "
        + "գիրքը (Ե–ԺԱ հատվածներ)․ Գլակի "
        + "առաջնորդները և Տարոնի Մամիկոնյանների "
        + "պատերազմները պարսիկների դեմ։ Գիտնականները "
        + "կասկածում են, թե առաջին մասը Զենոբն է "
        + "գրել, և ամբողջ գիրքը թվագրում են "
        + "VII–X դարերով։"],
      ["Կարդացե՛ք",
        "Գիրքը՝ 1704 տող, գրադարանում է․ "
        + "գրաբարի յուրաքանչյուր տողի կողքին՝ "
        + "աշխարհաբար թարգմանությունը, և "
        + "յուրաքանչյուր բառ կարելի է որոնել։ "
        + "Թարգմանությունները նախնական "
        + "տարբերակներ են՝ պատրաստված արհեստական "
        + "բանականությամբ, և սպասում են գրաբար "
        + "իմացող ընթերցողների ստուգմանը։"],
    ],
    links: ["Կարդալ Տարոնի պատմությունը",
      "Տարոնը քարտեզի վրա",
      "Օգնել թարգմանությունների ստուգմանը"],
    ask: "Բարձրավանդակի էլ ո՞ր երկրների "
      + "պատմությունն է դեռ սպասում ընթերցողին։",
  },
  ru: {
    alt:
      "Зеноб Глак, История Тарона, IV век:"
      + " нарисованная карта Тарона среди гор, на ней"
      + " крепость, а на скале всадник",
    title:
      "История Тарона в библиотеке",
    lead:
      "«История Тарона» (Պատմութիւն Տարաւնոյ)"
      + " рассказывает, как страна в самом сердце"
      + " Армянского нагорья приняла новую веру и"
      + " боролась за неё. Первая часть приписывается"
      + " Зенобу Глаку (Զենոբ Գլակ), вторая принадлежит"
      + " Ованесу Мамиконяну. Вся книга теперь в"
      + " библиотеке nxGir, на грабаре и на современном"
      + " армянском, бок о бок.",
    sections: [
      ["Кем он был",
        "По преданию, Зеноб был учеником Григория"
        + " Просветителя и пришёл с ним из Кесарии;"
        + " некоторые источники называют его сирийцем."
        + " Он стал первым настоятелем монастыря Сурб"
        + " Карапет в Тароне, который по его имени"
        + " назвали Глакаванком."],
      ["Первая часть",
        "Разделы Ա–Դ, 654 строки: по велению Григория"
        + " Зеноб пишет сирийским епископам о том, как"
        + " новая вера утвердилась в Тароне. Здесь"
        + " письма Григория и епископов и две битвы при"
        + " Арцане."],
      ["Часть Ованеса Мамиконяна",
        "Ованес, позднейший настоятель Глака,"
        + " продолжил книгу (разделы Ե–ԺԱ): настоятели"
        + " Глака и войны Мамиконянов Тарона с персами."
        + " Учёные сомневаются, что первую часть написал"
        + " сам Зеноб, и датируют всю книгу VII–X веками."],
      ["Читайте",
        "Книга, 1704 строки, есть в библиотеке: рядом"
        + " с каждой строкой на грабаре её перевод на"
        + " современный армянский, и каждое слово можно"
        + " посмотреть в словаре. Переводы — первые"
        + " черновики, сделанные с помощью ИИ: они ждут"
        + " читателей, знающих грабар, чтобы те их"
        + " проверили."],
    ],
    links: ["Читать Историю Тарона",
      "Тарон на карте",
      "Помочь проверить переводы"],
    ask:
      "Какие ещё земли нагорья хранят историю, которую"
      + " пока никто не прочёл?",
  },
}, {
  id: "smbat-sparapet",
  book: "#/read/grabar/smbat-sparapet/"
    + "2-taregirk/01.txt",
  bookText: {
    hy: "Կարդալ Տարեգիրքը →",
    en: "Read the Taregirk →",
    ru: "Читать Летопись →",
  },
  date: "2026-11-16",
  img: "smbat-sparapet.jpg",
  face: "smbat-sparapet-face.jpg",
  alt: "Smbat Sparapet in a red cloak, a quill"
    + " and a book in his hands; behind him a"
    + " fortress under a snowy mountain, and a"
    + " Mongol khan receiving an envoy",
  title: "Smbat Sparapet on the shelf",
  lead: "Smbat Sparapet (Սմբատ Սպարապետ,"
    + " 1208–1276) was not just a warrior: he was"
    + " a diplomat, a lawgiver and a historian."
    + " Both of his books are now in the nxGir"
    + " Library, in Grabar and in modern"
    + " Armenian, side by side.",
  banner: ["Սմբատ Սպարապետ",
    "Զորավար, դիվանագետ և պատմիչ. նրա"
    + " գրքերը գրադարանում են"],
  banner_en: ["Smbat Sparapet",
    "Commander, diplomat and historian: his"
    + " books are in the Library"],
  banner_ru: ["Смбат Спарапет",
    "Полководец, дипломат и историк: его книги в"
    + " библиотеке"],
  sections: [
    ["Who he was",
      "Smbat was born in 1208 in the Armenian"
      + " kingdom of Cilicia, on the Mediterranean"
      + " coast, the son of Constantine of"
      + " Baberon, the regent of the kingdom. When"
      + " his younger brother Hetum I was crowned"
      + " king in 1226, Smbat became his sparapet:"
      + " the constable, commander of the army.",
      "He held that office for half a century. He"
      + " led the army against the Seljuk sultans"
      + " of Rum and the Mamluks of Egypt, and fell"
      + " in battle in 1276, at Sarvandikar, an old"
      + " man still in the saddle."],
    ["A journey to the Great Khan",
      "In 1247, when the Mongols had become the"
      + " greatest power of Asia, Hetum sent Smbat"
      + " to their court at Karakorum. He crossed"
      + " Persia and Central Asia, met Güyük Khan,"
      + " and came home in 1250 with an agreement"
      + " that kept Cilicia safe for years, as an"
      + " ally rather than a conquered land.",
      "On the way he wrote from Samarkand to his"
      + " brother-in-law, the king of Cyprus,"
      + " about the lands and peoples he saw. The"
      + " letter was copied in Latin and read in"
      + " Europe: one of the first eyewitness"
      + " accounts of the Mongol empire to reach"
      + " it."],
    ["A translator of laws",
      "Cilicia lived beside the crusader states,"
      + " and Smbat knew their French. He"
      + " translated the Assizes of Antioch, the"
      + " laws of the Frankish principality, into"
      + " Armenian. The French original is lost:"
      + " the laws survive only in his"
      + " translation."],
    ["The Datastanagirk, his book of laws",
      "In 1265 he made a law book for the kingdom,"
      + " reworking the Datastanagirk of Mkhitar"
      + " Gosh, a century older. He says he moved"
      + " the laws out of old, hard books into the"
      + " everyday words people spoke; so it is"
      + " written in the Middle Armenian of"
      + " Cilicia, with French, Greek and Arabic"
      + " words in it.",
      "Its 211 sections cover the whole life of a"
      + " kingdom: the rights of the king, coin and"
      + " castles; war and spoils; the church and"
      + " its offices; marriage and divorce;"
      + " inheritance; trade, mills and gardens;"
      + " slaves and hired labour; loans and"
      + " usury; damage done by fire, floods and"
      + " animals; killing and wounding, willing"
      + " and unwilling."],
    ["The Taregirk, his chronicle",
      "His chronicle tells the story of Armenia"
      + " year by year, from 951 to his own time:"
      + " the Bagratid kings of Ani and the"
      + " emperors of Byzantium; the fall of Ani"
      + " to Alp Arslan in 1064; the death of the"
      + " last king, Gagik II; the Rubenid princes"
      + " of Cilicia and the crowning of Levon,"
      + " its first king, in 1198.",
      "Then it comes to the events he lived"
      + " through, and to the sieges of Tarsus"
      + " he told himself. Others carried it on to"
      + " 1331, and added lists of the princes and"
      + " kings of Cilicia, its constables and the"
      + " emperors of Rome and Byzantium. Each"
      + " part opens with a contents list by"
      + " year."],
    ["Read them",
      "Both books are in the Library, with every"
      + " Grabar line beside its modern Armenian"
      + " translation and every word open to look"
      + " up. The translations are first drafts,"
      + " made with AI: they wait for readers who"
      + " know Grabar to check them line by"
      + " line."],
  ],
  links: [
    ["Read the Taregirk", SMBAT + "2-taregirk"],
    ["Read the Datastanagirk",
      SMBAT + "1-datastanagirk"],
    ["Help review the translations",
      "#/contribute"],
  ],
  ask: "How many remarkable stories from"
    + " Armenian history are still waiting to be"
    + " rediscovered?",
  hy: {
    alt:
      "Սմբատ Սպարապետը կարմիր թիկնոցով, ձեռքին գրիչ և "
      + "գիրք. նրա հետևում ամրոց է ձյունածածկ լեռան տակ, "
      + "իսկ մոնղոլ խանն ընդունում է դեսպանին",
    title: "Սմբատ Սպարապետը՝ գրադարանում",
    lead:
      "Սմբատ Սպարապետը (Սմբատ Սպարապետ, 1208–1276) "
      + "պարզապես զորական չէր․ նա դիվանագետ էր, օրենսդիր "
      + "և պատմիչ։ Նրա երկու գրքերն էլ այժմ հասանելի են "
      + "nxGir գրադարանում՝ կողք կողքի, գրաբարով և "
      + "աշխարհաբարով։",
    sections: [
      ["Ո՞վ էր նա",
        "Սմբատը ծնվել է 1208 թվականին Կիլիկիայի "
        + "հայկական թագավորությունում՝ Միջերկրական ծովի "
        + "ափին։ Նա թագավորության խնամակալ Կոստանդին "
        + "Պապեռոնի որդին էր։ Երբ 1226 թվականին նրա "
        + "կրտսեր եղբայր Հեթում Ա-ն թագադրվեց, Սմբատը "
        + "դարձավ սպարապետ՝ զորքի գլխավոր հրամանատարը։",
        "Նա այդ պաշտոնը զբաղեցրեց շուրջ կես դար։ Սմբատը "
        + "գլխավորել է հայկական զորքերը Ռումի սելջուկ "
        + "սուլթանների և Եգիպտոսի մամլուքների դեմ մղված "
        + "պատերազմներում։ 1276 թվականին նա զոհվեց "
        + "Սարվանդիքարի ճակատամարտում՝ արդեն տարեց "
        + "հասակում, բայց դեռևս մարտական նժույգի վրա։"],
      ["Ճանապարհորդություն դեպի Մեծ խանի արքունիք",
        "1247 թվականին, երբ մոնղոլները դարձել էին "
        + "Ասիայի ամենահզոր ուժը, Հեթումը Սմբատին "
        + "ուղարկեց նրանց արքունիք՝ Կարակորում։ Նա անցավ "
        + "Պարսկաստանով և Կենտրոնական Ասիայով, հանդիպեց "
        + "Գույուկ խանին և 1250 թվականին վերադարձավ մի "
        + "համաձայնությամբ, որը տարիներ շարունակ ապահովեց "
        + "Կիլիկիայի անվտանգությունը՝ որպես դաշնակցի, այլ "
        + "ոչ թե նվաճված երկրի։",
        "Ճանապարհին՝ Սամարղանդից, նա նամակ գրեց իր "
        + "փեսային՝ Կիպրոսի թագավորին՝ պատմելով իր տեսած "
        + "երկրների ու ժողովուրդների մասին։ Նամակը "
        + "թարգմանվեց լատիներեն և տարածվեց Եվրոպայում՝ "
        + "դառնալով մոնղոլական կայսրության մասին այնտեղ "
        + "հասած առաջին ականատեսի վկայություններից մեկը։"],
      ["Օրենքների թարգմանիչը",
        "Կիլիկիան հարևան էր խաչակիրների "
        + "պետություններին, և Սմբատը տիրապետում էր նրանց "
        + "լեզվին՝ ֆրանսերենին։ Նա հայերեն թարգմանեց "
        + "Անտիոքի ասիզները՝ ֆրանկյան իշխանապետության "
        + "օրենքները։ Ֆրանսերեն բնագիրը կորել է․ այդ "
        + "օրենքները մեզ են հասել միայն Սմբատի "
        + "թարգմանությամբ։"],
      ["«Դատաստանագիրք»-ը՝ նրա օրենսգիրքը",
        "1265 թվականին նա թագավորության համար կազմեց "
        + "օրենսգիրք՝ վերամշակելով շուրջ մեկ դար առաջ "
        + "Մխիթար Գոշի ստեղծած «Դատաստանագիրքը»։ Ինքը՝ "
        + "Սմբատը, նշում է, որ օրենքները հին ու "
        + "դժվարամատչելի գրքերից տեղափոխել է մարդկանց "
        + "առօրյա խոսքին ավելի մոտ լեզվի։ Այդ պատճառով "
        + "աշխատությունը գրված է Կիլիկիայի միջին "
        + "հայերենով՝ ֆրանսերեն, հունարեն և արաբերեն "
        + "բառերի գործածությամբ։",
        "Գրքի 211 հոդվածներն ընդգրկում են թագավորության "
        + "կյանքի գրեթե բոլոր ոլորտները՝ թագավորի "
        + "իրավունքները, դրամը և ամրոցները, պատերազմն ու "
        + "ավարը, եկեղեցին և նրա պաշտոնները, "
        + "ամուսնությունն ու ամուսնալուծությունը, "
        + "ժառանգությունը, առևտուրը, ջրաղացներն ու "
        + "այգիները, ստրկությունն ու վարձու աշխատանքը, "
        + "փոխառություններն ու վաշխառությունը, հրդեհների, "
        + "ջրհեղեղների և կենդանիների պատճառած վնասները, "
        + "սպանությունն ու մարմնական վնասվածքները՝ "
        + "դիտավորյալ և ոչ դիտավորյալ։"],
      ["«Տարեգիրք»-ը՝ նրա ժամանակագրությունը",
        "Սմբատի ժամանակագրությունը պատմում է Հայաստանի "
        + "պատմությունը տարեցտարի՝ 951 թվականից մինչև իր "
        + "ապրած ժամանակները։ Այնտեղ հիշատակվում են Անիի "
        + "Բագրատունի թագավորներն ու Բյուզանդիայի "
        + "կայսրերը, 1064 թվականին Ալփ Արսլանի կողմից "
        + "Անիի գրավումը, վերջին թագավոր Գագիկ Բ-ի մահը, "
        + "Կիլիկիայի Ռուբինյան իշխանները և 1198 թվականին "
        + "Լևոնի՝ Կիլիկիայի առաջին թագավորի "
        + "թագադրությունը։",
        "Այնուհետև պատմությունը հասնում է այն "
        + "իրադարձություններին, որոնց ականատեսն էր ինքը՝ "
        + "Սմբատը, այդ թվում՝ Տարսոնի պաշարումներին, "
        + "որոնց մասին նա պատմում է անձամբ։ Հետագա "
        + "հեղինակները շարունակել են ժամանակագրությունը "
        + "մինչև 1331 թվականը՝ ավելացնելով Կիլիկիայի "
        + "իշխանների ու թագավորների, սպարապետների, ինչպես "
        + "նաև Հռոմի և Բյուզանդիայի կայսրերի ցանկերը։ "
        + "Յուրաքանչյուր հատված սկսվում է ըստ տարիների "
        + "կազմված բովանդակության ցանկով։"],
      ["Կարդացե՛ք դրանք",
        "Երկու գրքերն էլ հասանելի են nxGir գրադարանում․ "
        + "գրաբարի յուրաքանչյուր տողի կողքին տեղադրված է "
        + "դրա աշխարհաբար թարգմանությունը, և "
        + "յուրաքանչյուր բառ կարելի է առանձին որոնել ու "
        + "ուսումնասիրել։",
        "Թարգմանությունները դեռ նախնական տարբերակներ "
        + "են՝ պատրաստված արհեստական բանականության "
        + "օգնությամբ։ Դրանք սպասում են գրաբարին "
        + "տիրապետող ընթերցողներին, որոնք կկարողանան "
        + "ստուգել և ճշգրտել դրանք՝ տող առ տող։"],
    ],
    links: ["Կարդալ Տարեգիրքը",
      "Կարդալ Դատաստանագիրքը",
      "Օգնել թարգմանությունների ստուգմանը"],
    ask:
      "Հայոց պատմության դեռ քանի՞ ուշագրավ պատմություն "
      + "է սպասում իր վերահայտնագործողներին։",
  },
  ru: {
    alt:
      "Смбат Спарапет в красном плаще, с пером и"
      + " книгой в руках; позади крепость под снежной"
      + " горой и монгольский хан, принимающий посла",
    title:
      "Смбат Спарапет в библиотеке",
    lead:
      "Смбат Спарапет (Սմբատ Սպարապետ, 1208–1276) был"
      + " не только воином: он был дипломатом,"
      + " законодателем и историком. Обе его книги"
      + " теперь в библиотеке nxGir, на грабаре и на"
      + " современном армянском, бок о бок.",
    sections: [
      ["Кем он был",
        "Смбат родился в 1208 году в Армянском царстве"
        + " Киликии, на берегу Средиземного моря, в"
        + " семье Константина Баберонского, регента"
        + " царства. Когда в 1226 году его младший брат"
        + " Хетум I был коронован, Смбат стал его"
        + " спарапетом — главнокомандующим войска.",
        "Он занимал эту должность полвека. Он водил"
        + " войско против сельджукских султанов Рума и"
        + " египетских мамлюков и пал в бою в 1276 году"
        + " при Сарвандикаре — уже старым, но всё ещё в"
        + " седле."],
      ["Путешествие к великому хану",
        "В 1247 году, когда монголы стали величайшей"
        + " силой Азии, Хетум отправил Смбата к их двору"
        + " в Каракорум. Он пересёк Персию и Среднюю"
        + " Азию, встретился с Гуюк-ханом и в 1250 году"
        + " вернулся с соглашением, которое на годы"
        + " обезопасило Киликию — как союзника, а не"
        + " покорённую страну.",
        "В пути, из Самарканда, он написал своему"
        + " зятю, королю Кипра, о землях и народах,"
        + " которые видел. Письмо переписали по-латыни и"
        + " читали в Европе: это одно из первых"
        + " свидетельств очевидца о Монгольской империи,"
        + " дошедших туда."],
      ["Переводчик законов",
        "Киликия соседствовала с государствами"
        + " крестоносцев, и Смбат знал их французский."
        + " Он перевёл на армянский Антиохийские ассизы"
        + " — законы франкского княжества. Французский"
        + " оригинал утрачен: законы сохранились только"
        + " в его переводе."],
      ["«Судебник», его книга законов",
        "В 1265 году он составил для царства судебник,"
        + " переработав «Судебник» Мхитара Гоша,"
        + " написанный веком раньше. По его словам, он"
        + " перенёс законы из старых трудных книг в"
        + " повседневную речь; поэтому книга написана на"
        + " среднеармянском языке Киликии, с"
        + " французскими, греческими и арабскими словами.",
        "Её 211 статей охватывают всю жизнь царства:"
        + " права царя, монету и крепости; войну и"
        + " добычу; церковь и её чины; брак и развод;"
        + " наследство; торговлю, мельницы и сады; рабов"
        + " и наёмный труд; займы и ростовщичество;"
        + " ущерб от пожаров, наводнений и животных;"
        + " убийства и ранения, умышленные и"
        + " неумышленные."],
      ["«Летопись», его хроника",
        "Его хроника рассказывает историю Армении год"
        + " за годом, с 951 года до его собственного"
        + " времени: цари Багратиды в Ани и императоры"
        + " Византии; взятие Ани Алп-Арсланом в 1064"
        + " году; смерть последнего царя Гагика II;"
        + " князья Рубениды в Киликии и коронация"
        + " Левона, её первого царя, в 1198 году.",
        "Затем она доходит до событий, которые он"
        + " пережил сам, и до осад Тарса, о которых он"
        + " рассказывает лично. Другие продолжили её до"
        + " 1331 года и добавили списки князей и царей"
        + " Киликии, её спарапетов и императоров Рима и"
        + " Византии. Каждая часть начинается с"
        + " оглавления по годам."],
      ["Читайте",
        "Обе книги есть в библиотеке: рядом с каждой"
        + " строкой на грабаре её перевод на современный"
        + " армянский, и каждое слово можно посмотреть в"
        + " словаре. Переводы — первые черновики,"
        + " сделанные с помощью ИИ: они ждут читателей,"
        + " знающих грабар, чтобы те проверили их строка"
        + " за строкой."],
    ],
    links: ["Читать Летопись",
      "Читать Судебник",
      "Помочь проверить переводы"],
    ask:
      "Сколько ещё удивительных историй армянской"
      + " истории ждут, чтобы их открыли заново?",
  },
}];

// the picture, a button: it opens the whole
// picture over the page (a dialog; a click, Esc or
// the close button shuts it)
function zoomable(a) {
  const img = h("img", { src: a.img, width: "1200",
    height: "800", alt: a.alt });
  const open = h("button", { type: "button",
    class: "zoom", "aria-label": "Enlarge the picture" },
  img);
  open.addEventListener("click", () => {
    const big = h("img", { src: a.img, alt: a.alt });
    const shut = h("button", { type: "button",
      class: "shut", "aria-label": "Close" }, "×");
    const box = h("dialog", { class: "lightbox" },
      shut, big);
    const close = () => {
      box.close();
      box.remove();
    };
    box.addEventListener("click", close);
    box.addEventListener("cancel", () => box.remove());
    document.body.append(box);
    box.showModal();
  });
  return h("figure", { class: "hero wide" }, open);
}

// -- about an author: the scroll button beside an
// author's name opens a card (authors/, read by
// nxgir_authors.py; /api/authors, /api/author) --

// the words of the card, by language
const AUTHOR_UI = {
  hy: { about: "Հեղինակի մասին", close: "Փակել",
    book: "Գրքի մասին",
    source: "Աղբյուր՝ ",
    machine: "Գրել է Claude-ը, դեռ չի ստուգվել" },
  en: { about: "About the author", close: "Close",
    book: "About the book",
    source: "Source: ",
    machine: "Written by Claude, not yet reviewed" },
  ru: { about: "Об авторе", close: "Закрыть",
    book: "О книге",
    source: "Источник: ",
    machine: "Написано Claude, ещё не проверено" },
};
const LANG_LABEL = { hy: "Հայ", en: "Eng", ru: "Рус" };

// the authors written about, asked once: their ids
// and their names in each language
let authorData = null;
function authorsAbout() {
  if (!authorData) {
    authorData = api("authors")
      .catch(() => ({ authors: [], names: {},
        books: [], titles: {} }));
  }
  return authorData;
}
function knownAuthors() {
  return authorsAbout().then((d) =>
    new Set(d.authors));
}
function knownBooks() {
  return authorsAbout().then((d) =>
    new Set(d.books || []));
}

// the scroll button for an author's id (its folder
// in grabar/); hidden until the author is known to
// have a card. show, if given, is shown with it.
function authorInfoBtn(id, name, show) {
  const b = h("button", { type: "button",
    class: "info-btn", hidden: "",
    title: AUTHOR_UI.hy.about,
    "aria-label": AUTHOR_UI.hy.about + "՝ " + name },
  icon(ICONS.scroll));
  b.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    authorInfo(id);
  });
  knownAuthors().then((ids) => {
    if (!ids.has(id)) return;
    b.hidden = false;
    if (show) show.hidden = false;
  });
  return b;
}

// a book's row of the Library in its li: its icon
// opens the card about the book (authors/<author>/
// <book>.LANG.md), once it is known to have one; a
// file of a grouped book (the Bible's Gospels) has
// the card of its group (bible/new-testament)
function bookItem(b, row, ...more) {
  const li = h("li", {}, row, ...more);
  knownBooks().then((ids) => {
    const group = b.id.split("/").slice(0, 2)
      .join("/");
    const id = ids.has(b.id) ? b.id
      : ids.has(group) ? group : "";
    if (!id) return;
    const ui = AUTHOR_UI.hy;
    const k = h("button", { type: "button",
      class: "book-info", title: ui.book,
      "aria-label": ui.book + "՝ " + b.name },
    icon(ICONS.book));
    k.addEventListener("click", (e) => {
      e.preventDefault();
      bookInfo(id);
    });
    li.classList.add("has-card");
    li.prepend(k);
  });
  return li;
}

// the language of an author's or book's card: the
// one picked on a card, else the site's, else
// English, else the first it has
function authorLang(a) {
  const has = a.versions.map((v) => v.lang);
  return [pagePick.author || LANG, "en"]
    .find((l) => has.includes(l)) || has[0];
}

// the card about an author (a dialog: ×, Esc, a
// click outside it or on a link shuts it)
async function authorInfo(id) {
  let a;
  try {
    a = await api("author?id=" + encodeURIComponent(id));
  } catch (e) {
    return;
  }
  infoCard(a);
}

// the card about a book: as an author's, the time
// of writing and what it is in place of the years
// and the role
async function bookInfo(id) {
  let a;
  try {
    a = await api("book-info?id="
      + encodeURIComponent(id));
  } catch (e) {
    return;
  }
  infoCard({ ...a, versions: a.versions.map((v) =>
    ({ ...v, years: v.written, role: v.kind })) });
}

// the dialog of an author's or a book's card
function infoCard(a) {
  const card = h("div", { class: "ai-card" });
  const box = h("dialog", { class: "author-info" },
    card);
  const close = () => {
    box.close();
    box.remove();
  };
  const draw = (lang) => {
    const v = a.versions.find((x) => x.lang === lang);
    const ui = AUTHOR_UI[lang] || AUTHOR_UI.en;
    const shut = h("button", { type: "button",
      class: "shut", "aria-label": ui.close }, "×");
    shut.addEventListener("click", close);
    const langs = a.versions.length > 1 ? h("div",
      { class: "ai-langs" }, ...a.versions.map((x) => {
        const b = h("button", { type: "button",
          lang: x.lang,
          "aria-pressed": String(x.lang === lang) },
        LANG_LABEL[x.lang] || x.lang);
        b.addEventListener("click", () => {
          try {
            pagePick.author = x.lang;
          } catch (e) {}
          draw(x.lang);
        });
        return b;
      })) : null;
    const links = [
      ...a.places.map((p) => h("a", {
        href: "#/map/" + enc(p.id) },
      icon(ICONS.pin), p[lang] || p.hy)),
    ];
    if (a.post) {
      links.push(h("a", { href: "#/blog/"
        + enc(a.post.slug) }, icon(ICONS.pen),
      a.post.titles[lang] || a.post.titles.hy
        || Object.values(a.post.titles)[0]));
    }
    const note = [v.source ? ui.source + v.source
      : null, a.status === "machine" ? ui.machine
      : null].filter(Boolean).join(" · ");
    card.setAttribute("lang", lang);
    // replaceChildren() would show a null as "null"
    card.replaceChildren(...[shut,
      h("div", { class: "ai-head" },
        a.face ? h("img", { src: a.face, alt: "",
          class: "ai-face" }) : null,
        h("div", {},
          h("h2", {}, v.name),
          v.years ? h("p", { class: "ai-years" },
            v.years) : null,
          v.role ? h("p", { class: "ai-role" },
            v.role) : null)),
      langs,
      ...v.text.map((t) => h("p", {}, t)),
      links.length ? h("div", { class: "ai-links" },
        ...links) : null,
      note ? h("p", { class: "ai-src" }, note)
        : null].filter(Boolean));
    for (const l of card.querySelectorAll("a")) {
      l.addEventListener("click", close);
    }
  };
  draw(authorLang(a));
  box.addEventListener("click", (e) => {
    if (e.target === box) close();
  });
  box.addEventListener("cancel", () => box.remove());
  document.body.append(box);
  box.showModal();
}

// -- the Reference: the book cards --

// the words of #/reference, in the language of the
// cards; age(n): a century, in Roman numerals
const CARDS_UI = {
  hy: { title: "Տեղեկատու", home: "← Գլխավոր",
    count: (b, a) => b + " գիրք · " + a + " հեղինակ",
    find: "Գտնել գիրք, հեղինակ կամ տեսակ…",
    read: "Կարդալ", more: "Ավելին",
    parts: (n) => n + " մաս", done: "թարգմանված",
    none: "Ոչինչ չգտնվեց։",
    library: "Ցանկով՝ Գրադարան →",
    all: "Բոլորը", kind: "Տեսակ", ages: "Դար",
    age: (r) => r + " դ." },
  en: { title: "Reference", home: "← Home",
    count: (b, a) => b + " books · " + a + " authors",
    find: "Find a book, an author or a kind…",
    read: "Read", more: "More",
    parts: (n) => plural(n, "part"),
    done: "translated", none: "Nothing found.",
    library: "As a list: Library →",
    all: "All", kind: "Kind", ages: "Century",
    age: (r) => r + " c." },
  ru: { title: "Справочник", home: "← Главная",
    count: (b, a) => "Книг: " + b + " · авторов: " + a,
    find: "Найти книгу, автора или жанр…",
    read: "Читать", more: "Подробнее",
    parts: (n) => n + " ч.", done: "переведено",
    none: "Ничего не найдено.",
    library: "Списком: Библиотека →",
    all: "Все", kind: "Жанр", ages: "Век",
    age: (r) => r + " в." },
};

// 5 -> V
function roman(n) {
  const R = [[10, "X"], [9, "IX"], [5, "V"],
    [4, "IV"], [1, "I"]];
  let out = "";
  for (const [k, s] of R) {
    while (n >= k) {
      out += s;
      n -= k;
    }
  }
  return out;
}

// a hue for each author, the same on every visit:
// the colored edge of its books' cards
function authorHue(id) {
  let k = 0;
  for (const c of id) k = (k * 31 + c.charCodeAt(0)) % 360;
  return k;
}

// one card of #/reference: what the book is and
// when it was written, its name (opens it), its
// authors, the first paragraph about it, its parts
// and how much is translated; More opens the whole
// card. On a phone it is a low banner (style.css).
function bookCard(c, ui) {
  const who = c.authors[c.authors.length - 1];
  const meta = h("span", { class: "bc-meta" });
  if (c.parts > 1) {
    meta.append(h("span", {}, ui.parts(c.parts)));
  }
  if (c.done) {
    meta.append(h("span", { class: "done" },
      c.done === c.parts ? ui.done
        : ui.done + " " + c.done + "/" + c.parts));
  }
  const more = btn(ui.more, () => bookInfo(c.id),
    { class: "icon-btn bc-more" });
  const el = h("li", { class: "bcard",
    lang: c.lang },
  h("p", { class: "bc-top" },
    h("span", { class: "bc-kind" }, c.kind),
    c.written ? h("span", { class: "bc-when" },
      c.written) : null),
  h("h2", {}, h("a", { href: c.to }, c.name)),
  c.lang !== "hy" ? h("p", { class: "bc-hy",
    lang: "hy" }, c.short) : null,
  h("p", { class: "bc-by", lang: c.lang },
    ...authorNames(c.authors)),
  h("p", { class: "bc-lead" }, c.lead),
  h("div", { class: "bc-foot" }, meta, more,
    h("a", { class: "bc-read", href: c.to },
      ui.read)));
  el.style.setProperty("--hue",
    String(authorHue(who.id)));
  return el;
}

// a row of filter chips: [[value, label, count]],
// the one picked pressed, one with a count of 0
// off (null: no count); pick(value) on a click
function chipRow(name, items, now, pick) {
  return h("div", { class: "filters outline bc-chips",
    role: "group", "aria-label": name },
  items.map(([v, label, n]) => {
    const b = h("button", { type: "button",
      "aria-pressed": String(v === now),
      disabled: n === 0 && v !== now ? "" : null },
    label, n != null ? h("span", { class: "count" },
      String(n)) : null);
    b.addEventListener("click", () => pick(v));
    return b;
  }));
}

// #/reference: every book written about (authors/),
// a card each, in the Library's order; the language
// of the cards is the one of the author cards
// (pagePick.author). The chips keep the books of one
// kind (GROUPS in nxgir_authors.py) or century, and
// the find box those whose name, authors, kind or
// time have its words.
async function referencePage() {
  let lang = pagePick.author || LANG;
  if (!(lang in CARDS_UI)) lang = "hy";
  let data = await api("book-cards?lang=" + lang);
  let q = "";
  let kind = "";
  let age = 0;
  const grid = h("ul", { class: "bcards" });
  const none = h("p", { class: "empty", hidden: "" });
  const input = h("input", { type: "search",
    name: "find", enterkeyhint: "search",
    autocomplete: "off", autocapitalize: "off",
    spellcheck: "false" });
  const head = h("div", { class: "bc-head" });
  const chips = h("div", { class: "bc-filters" });
  const filter = () => {
    const fits = q ? nameFits(q) : null;
    let n = 0;
    data.books.forEach((c, i) => {
      const words = [c.name, c.short, c.kind,
        c.written, ...c.authors.map((p) => p.name)];
      const on = (!kind || c.group === kind)
        && (!age || c.century === age)
        && (!fits || words.some(fits));
      grid.children[i].hidden = !on;
      if (on) n += 1;
    });
    none.hidden = n > 0;
  };
  // the chips: the kinds and centuries the books
  // have, each with how many there are of it in the
  // century picked (or of the kind picked)
  const drawChips = () => {
    const ui = CARDS_UI[lang];
    const count = (f) => data.books.filter(f).length;
    const inAge = (c) => !age || c.century === age;
    const ofKind = (c) => !kind || c.group === kind;
    const kinds = data.groups
      .filter((g) => count((c) => c.group === g.id))
      .map((g) => [g.id, g.name,
        count((c) => c.group === g.id && inAge(c))]);
    const ages = [...new Set(data.books
      .map((c) => c.century).filter(Boolean))]
      .sort((a, b) => a - b)
      .map((k) => [k, ui.age(roman(k)),
        count((c) => c.century === k && ofKind(c))]);
    chips.replaceChildren(
      chipRow(ui.kind, [["", ui.all, null], ...kinds],
        kind, (v) => {
          kind = v;
          drawChips();
          filter();
        }),
      chipRow(ui.ages, [[0, ui.all, null], ...ages],
        age, (v) => {
          age = v;
          drawChips();
          filter();
        }));
  };
  const draw = () => {
    const ui = CARDS_UI[lang];
    document.title = ui.title + " · " + NAME;
    const n = new Set(data.books.map((c) =>
      c.authors[c.authors.length - 1].id)).size;
    input.placeholder = ui.find;
    input.setAttribute("aria-label", ui.find);
    none.textContent = ui.none;
    const pick = h("div", { class: "filters outline",
      role: "group", "aria-label": "Language" },
    data.langs.map((l) => {
      const b = h("button", { type: "button",
        lang: l, "aria-pressed": String(l === lang) },
      LANG_LABEL[l] || l);
      b.addEventListener("click", async () => {
        if (l === lang) return;
        try {
          data = await api("book-cards?lang=" + l);
        } catch (e) {
          return;
        }
        lang = l;
        pagePick.author = l;
        draw();
      });
      return b;
    }));
    head.setAttribute("lang", lang);
    chips.setAttribute("lang", lang);
    head.replaceChildren(
      h("p", { class: "crumbs" },
        h("a", { href: "#/" }, ui.home)),
      h("h1", {}, ui.title),
      h("p", { class: "sub" },
        ui.count(data.books.length, n), " · ",
        h("a", { href: "#/library" }, ui.library)),
      pick);
    drawChips();
    grid.replaceChildren(
      ...data.books.map((c) => bookCard(c, ui)));
    for (const el of grid.querySelectorAll(
      ".bc-by")) watchNames(el);
    filter();
  };
  input.addEventListener("input", () => {
    q = input.value.trim();
    filter();
  });
  // the page's own find box, in place of the search
  // of the books (withSearch()), as the Library's
  const form = h("form", { class: "sbox",
    role: "search" }, icon(ICONS.search), input);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    input.blur();
  });
  draw();
  show(h("div", { class: "search-wrap" }, form),
    head, chips, grid, none);
}

// the languages an announcement has: English, and
// Armenian in its hy, Russian in its ru (the same
// fields; links are the labels only)
function newsText(a, lang) {
  const x = lang !== "en" && a[lang];
  if (!x) return a;
  return { ...a, ...x,
    links: a.links.map(([, to], i) =>
      [x.links[i], to]) };
}

// one announcement, whole: #/news/<id>
function newsItem(a0, lang) {
  const a = newsText(a0, lang);
  const [main, ...more] = a.links;
  return h("article", { class: "news", lang },
    zoomable(a),
    h("p", { class: "sub" },
      h("time", { datetime: a.date },
        longDay(a.date, lang))),
    h("h2", { class: "news-title" }, a.title),
    h("p", { class: "lead" }, named(a.lead)),
    h("ul", { class: "features" },
      a.sections.map(([title, ...text]) =>
        h("li", {}, h("h2", {}, title),
          text.map((t) => h("p", {}, named(t)))))),
    h("figure", { class: "mission" },
      h("p", {}, a.ask)),
    h("p", { class: "cta" },
      h("a", { class: "cta-main", href: main[1] },
        main[0]),
      more.map(([label, to]) =>
        h("a", { href: to }, label))));
}

// #/news: narrow banners, newest first; #/news/<id>
// one announcement
// the language of the announcements: the one
// picked here, else the site's
function newsLang() {
  return pagePick.news || LANG;
}

function newsPage(id) {
  const one = id ? NEWS.find((a) => a.id === id)
    : null;
  if (id && !one) {
    throw new Error(t("err.news"));
  }
  const draw = () => {
    const lang = newsLang();
    const t = NEWS_UI[lang];
    const pick = h("div", { class: "filters outline news-lang",
      role: "group", "aria-label": "Language" },
    LANGS.map((l) => {
      const b = h("button", { type: "button",
        lang: l, "aria-pressed": String(l === lang) },
      BLOG[l].name);
      b.addEventListener("click", () => {
        pagePick.news = l;
        draw();
      });
      return b;
    }));
    document.title = (one ? newsText(one, lang).title
      + " · " : "") + t.title + " · " + NAME;
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, t.home),
        one ? [" · ", h("a", { href: "#/news" },
          t.title)] : null),
      one ? null : h("h1", { lang }, t.title),
      one ? null : pick,
      one ? newsItem(one, lang)
        : h("div", { class: "news-list" },
          NEWS.map((a) => newsBanner(a, lang))));
  };
  draw();
}

// -- statistics --

// 16490140 bytes: "15.7 MB"; as human() in
// nxgir_limits.py
function size(n) {
  for (const [unit, k] of [["GB", 2 ** 30],
    ["MB", 2 ** 20], ["KB", 2 ** 10]]) {
    if (n >= k) return (n / k).toFixed(1) + " " + unit;
  }
  return n + " B";
}

function secs(n) {
  return n < 120 ? Math.round(n) + " s"
    : (n / 60).toFixed(1) + " min";
}

// the limits explained (notes/limits.md)
const NOTES = "https://github.com/serjhnn/nx-gir/"
  + "blob/main/notes/limits.md";

// the levels of LIMITS in nxgir_limits.py, shown
// with a word, never by color alone

function amount(x, n) {
  return x.unit === "s" ? secs(n) : size(n);
}

function limitRow(x, closest) {
  const pct = Math.min(x.share, 100);
  const shown = x.share < 1 ? "<1%"
    : Math.round(x.share) + "%";
  const bar = h("span", { class: "meter",
      role: "meter", "aria-valuemin": "0",
      "aria-valuemax": "100",
      "aria-valuenow": String(Math.round(pct)),
      "aria-label": x.label },
    h("span", { style: "width:" +
      Math.max(pct, 0.8) + "%" }));
  const notes = [x.by];
  if (x.where) notes.push(x.where);
  if (x.since) notes.push(t("st.measured") + day(x.since));
  return h("li", { class: "limit" +
      (x.key === closest ? " closest" : ""),
      "data-level": x.level },
    h("div", { class: "limit-head" },
      h("b", { lang: "en" }, x.label),
      h("span", { class: "pct" }, shown)),
    bar,
    h("div", { class: "limit-foot" },
      h("span", {}, amount(x, x.value) + t("st.of") +
        amount(x, x.limit)),
      h("span", { class: "level" },
        t("lv." + x.level))),
    h("p", { class: "limit-by", lang: "en" },
      notes.join(" · ")));
}

// the recorded measures, newest first, as a table
function historyTable(rows) {
  const cell = (v, f) => h("td", {},
    v === "" ? "–" : f(v));
  return h("div", { class: "table-wrap" },
    h("table", { class: "history" },
      h("thead", {}, h("tr", {},
        t("st.cols").map((x) => h("th", {}, x)))),
      h("tbody", {}, rows.map((r) => h("tr", {},
        h("td", {}, day(r.date, true)),
        h("td", {}, h("code", {}, r.commit)),
        cell(r.text, size), cell(r.site, size),
        cell(r.git, size), cell(r.build, secs))))));
}

async function statsPage() {
  const data = await api("stats");
  document.title = t("nav.stats") + " · " + NAME;
  const head = [
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("h1", {}, t("nav.stats")),
  ];
  if (data.error) {
    show(...head, h("p", { class: "empty" },
      t("st.none") + data.error + t("dot")));
    return;
  }
  const stat = (n, label) => h("div", {},
    h("b", {}, String(n)), h("span", {}, label));
  const f = data.folders || {};
  const near = data.limits.find((x) =>
    x.key === data.closest);
  // the folders of the library, as the top page
  // once listed them
  const top = await api("shelf?folder=")
    .catch(() => null);
  show(
    ...head,
    h("p", { class: "sub" },
      t("st.sub", day(data.date, true)),
      h("code", {}, data.commit), t("dot")),
    h("div", { class: "stats" },
      stat(data.books, t("st.files")),
      stat(size(data.text), t("st.text")),
      data.words ? stat(data.words.toLocaleString(
        "en"), t("st.words"))
        : stat(size(f.ashkharhabar || 0),
          t("st.tr"))),
    near ? h("p", { class: "verdict",
        "data-level": near.level },
      t("st.closest"), h("b", { lang: "en" },
        near.label),
      t("st.at", Math.round(near.share))) : null,
    h("h2", { class: "tl-next" }, t("st.limits")),
    h("ul", { class: "limits" },
      data.limits.map((x) =>
        limitRow(x, data.closest))),
    data.history.length ? h("section", {},
      h("h2", { class: "tl-next" }, t("st.history")),
      historyTable(data.history)) : null,
    h("p", { class: "more-link" },
      t("st.what"),
      h("a", { href: NOTES }, "notes/limits.md")),
    top ? h("section", {},
      h("h2", { class: "tl-next" }, t("st.folders")),
      h("p", { class: "sub" }, plural(top.count,
        top.unit)),
      shelfList(top)) : null
  );
}

// -- offline --

// "Install app": the browser's own prompt, kept
// until the Offline page asks for it
let installPrompt = null;
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  installPrompt = e;
});
window.addEventListener("appinstalled", () => {
  installPrompt = null;
});

// does this copy have a service worker (sw.js)? only
// the published site does
function hasWorker() {
  return STATIC && !!window.NXGIR_SW
    && "serviceWorker" in navigator;
}

// a message to the service worker, once it is there
function tellWorker(type) {
  if (!hasWorker()) return;
  navigator.serviceWorker.ready.then((reg) => {
    if (reg.active) reg.active.postMessage({ type });
  }).catch(() => {});
}

// who shows the state of the saved copy: a function
// of the Offline page while it is open
let offlineShow = null;
if (hasWorker()) {
  navigator.serviceWorker.addEventListener("message",
    (e) => {
      const m = e.data;
      if (offlineShow && m && m.type === "state") {
        offlineShow(m);
      }
    });
}

// the published site keeps what you open, and a new
// build replaces the old one: the page reloads once
// when the new worker takes over
function startWorker() {
  if (!hasWorker()) return;
  const had = !!navigator.serviceWorker.controller;
  let reloading = false;
  navigator.serviceWorker.addEventListener(
    "controllerchange", () => {
      if (!had || reloading) return;
      reloading = true;
      location.reload();
    });
  navigator.serviceWorker.register(window.NXGIR_SW, {
    scope: "./", updateViaCache: "none" })
    .then((reg) => {
      reg.update().catch(() => {});
    }).catch(() => {});
}

// saving every book is switched off for now (the
// button stays); SAVE in sw.js must match
const OFFLINE_SAVE = false;

// #/offline: install the app, save every book in
// this browser, or download the site as a file
async function offlinePage() {
  document.title = t("nav.offline") + " · " + NAME;
  const head = [
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("h1", {}, t("off.h1")),
  ];
  if (!hasWorker()) {
    show(...head, h("p", { class: "sub" },
      t("off.here")));
    return;
  }
  const info = await json("offline.json")
    .catch(() => null);
  const mb = info ? size(info.files.reduce(
    (n, f) => n + f[1], 0)) : t("off.about");
  // the zip is not built now (build-site.py --zip)
  const zip = window.NXGIR_DOWNLOAD
    ? await json("download.json").catch(() => null)
    : null;
  const status = h("p", { class: "sub", role: "status" });
  const btn = h("button", { type: "button",
    class: "icon-btn primary" }, t("off.save"));
  let now = { want: false };
  let poll = 0;
  btn.addEventListener("click", () => {
    if (now.complete) {
      tellWorker("clear");
    } else {
      if (navigator.storage && navigator.storage.persist) {
        navigator.storage.persist().catch(() => {});
      }
      tellWorker("save");
    }
  });
  offlineShow = (st) => {
    if (!document.body.contains(status)) return;
    if (!OFFLINE_SAVE) return;
    now = st;
    const pct = st.total
      ? Math.round(100 * st.done / st.total) : 0;
    btn.disabled = st.busy || !OFFLINE_SAVE;
    // the worker can be stopped by the browser, or its
    // last message lost: ask again until it is done
    clearTimeout(poll);
    if (st.busy) {
      poll = setTimeout(() => tellWorker("status"), 2000);
    }
    if (st.busy && !st.total) {
      status.textContent = t("off.list");
      btn.textContent = t("off.saving");
    } else if (st.busy) {
      status.textContent = t("off.busy", st.done,
        st.total, pct);
      btn.textContent = t("off.saving");
    } else if (st.complete) {
      status.textContent = t("off.done", st.total);
      btn.textContent = t("off.remove");
    } else if (st.want) {
      status.textContent = t("off.part", st.done,
        st.total);
      btn.textContent = t("off.go");
    } else {
      status.textContent = t("off.nothing");
      btn.textContent = t("off.save");
    }
  };
  if (!OFFLINE_SAVE) {
    status.textContent = t("off.offnow");
    btn.disabled = true;
  } else {
    tellWorker("status");
  }
  const how = installPrompt
    ? h("button", { type: "button",
      class: "icon-btn primary" }, t("off.install"))
    : h("p", {}, t("off.how"));
  if (installPrompt) {
    how.addEventListener("click", async () => {
      installPrompt.prompt();
      await installPrompt.userChoice;
      installPrompt = null;
      how.remove();
    });
  }
  show(
    ...head,
    h("p", { class: "sub" }, t("off.ways", zip ? 3 : 2)),
    h("h2", { class: "tl-next" }, t("off.h_app")),
    h("p", {}, t("off.app")),
    how,
    h("h2", { class: "tl-next" }, t("off.h_save")),
    h("p", {}, t("off.books", mb)),
    status,
    h("p", {}, btn),
    zip ? [
      h("h2", { class: "tl-next" }, t("off.h_zip")),
      h("p", {}, t("off.zip1", size(zip.bytes)),
        h("code", {}, "python3 serve.py"),
        t("off.zip2")),
      h("p", {}, h("a", { class: "icon-btn",
        href: window.NXGIR_DOWNLOAD, download: "" },
      t("off.dl")))] : null
  );
}

// -- reader --

// Key for comparing words: normalize() in
// nxgir_reader.py. Ignores case and the marks
// ՛ ՜ ՞, and ' ’ written for ՛; և is the same as
// եւ (tests/test_web.py checks this matches on
// the whole library).
function wordKey(w) {
  return w.toLowerCase().replace(/[՛՜՞'’]/g, "")
    .replace(/և/g, "եւ");
}

// Key of a word for search: the classical spelling
// folded into the reformed one, so թագավոր finds
// թագաւոր; as loose() in nxgir_search.py
function loose(w) {
  return wordKey(w).replace(/իւ/g, "յու")
    .replace(/եա/g, "յա").replace(/եօ/g, "յո")
    .replace(/(?<!ո)ւ/g, "վ").replace(/է/g, "ե")
    .replace(/օ/g, "ո")
    .replace(/^յ(?=[աեէըիոօ])/, "հ");
}

const LANG_NAMES = { en: "English", hy: "Հայերեն" };
const cache = new Map();

// the language of the meanings of words: English
// or Armenian (no Russian yet: English); the one
// picked in the word panel, else the site's
function meaningLang() {
  return pagePick.meaning
    || (LANG === "hy" ? "hy" : "en");
}

// state of the open book
const R = {
  name: "",
  lines: 0, // lines in the file
  spans: [], // every word, in reading order
  keys: [], // wordKey of each
  wpos: [], // [line, n] of each, as saved
  starts: [], // first word of every sentence
  marks: [], // [{pos, at}]: at = word index
  notes: [], // [{pos, quote, text, date, at}]
  sel: -1, // the chosen word
  refs: [], // indexes of words with its key
  panel: null,
  tools: null,
  prog: null, // the bar of how far in the reader is
  title: "", // of the book open
  head: "", // its first line
  saved: "", // the position last saved
  timer: 0,
  par: null, // the other version: book() data
  lineEls: [], // the <p> of each line (not .par)
  ready: false, // the lines are in the page
  parBuilt: false, // the other version is in the page
  end: null, // the cards to the next part (partEnd)
  src: [], // the lines of the part: [text, word, ...]
  first: [], // the first word of each line (+ the end)
  pages: [], // [first line, last line + 1] of each page
  page: 0, // the page in the page now
  lo: 0, // words of that page: [lo, hi)
  hi: 0,
  credited: false, // the part has its own credit
  contents: [], // its chapters: [{line, n, title,
  // level}]
};

async function send(path, body, keepalive) {
  const r = await fetch("/api/" + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    keepalive: !!keepalive,
  });
  const data = await r.json();
  if (!r.ok) {
    const e = new Error(data.error || r.status);
    e.status = r.status;
    throw e;
  }
  return data;
}

async function lookup(w) {
  const lang = meaningLang();
  const k = lang + "\n" + w;
  if (!cache.has(k)) {
    cache.set(k, api("word?w=" + encodeURIComponent(w)
      + "&lang=" + lang));
  }
  try {
    return await cache.get(k);
  } catch (e) {
    cache.delete(k);
    throw e;
  }
}

// Lines from the Grabar helpers as a list: a line
// at the left is a heading, an indented one is an
// item, "Source: ..." is a small note.
function helperLines(lines) {
  const box = h("div", { class: "entry",
    lang: "hy" });
  let list = null;
  for (const line of lines) {
    if (line.startsWith("Source:")) {
      box.append(h("p", { class: "source",
        lang: "en" }, line));
    } else if (line.startsWith(" ")) {
      if (!list) {
        list = h("ul");
        box.append(list);
      }
      list.append(h("li", {}, line.trim()));
    } else {
      list = null;
      box.append(h("p", { class: "head" }, line));
    }
  }
  return box;
}

function section(title, ...kids) {
  return h("section", { class: "part" },
    h("h3", {}, title), ...kids);
}

function btn(label, onClick, attrs) {
  const b = h("button", Object.assign(
    { type: "button", class: "icon-btn" }, attrs),
  label);
  b.addEventListener("click", onClick);
  return b;
}

// -- the panel: a word, the bookmarks, the notes,
// or a note being written --

function sheet() {
  return R.panel && !R.panel.hidden &&
    getComputedStyle(R.panel).position === "fixed";
}

// kind: what the panel shows, for the buttons that
// open it (the title is in LANG)
function openPanel(title, titleLang, ...body) {
  const close = btn("×", closePanel,
    { class: "icon-btn close",
      "aria-label": t("close") });
  R.panel.replaceChildren(
    h("div", { class: "panel-head" },
      h("h2", { lang: titleLang }, title), close),
    h("div", { class: "panel-body" }, ...body));
  R.panel.hidden = false;
  R.panel.dataset.kind = title === t("r.contents")
    ? "Contents" : title;
  document.body.classList.add("panel-open");
  tocOpen(R.panel.dataset.kind === "Contents");
}

function closePanel() {
  mark(false);
  sentence(false);
  R.sel = -1;
  R.refs = [];
  if (R.panel) R.panel.hidden = true;
  document.body.classList.remove("panel-open");
  tocOpen(false);
}

// A phone's keyboard covers the bottom of the page,
// and the panel with it. The visual viewport is the
// part left; lift the panel to its bottom, and keep
// the panel short enough to fit above the keyboard.
function lift() {
  const v = window.visualViewport;
  if (!v || !R.panel || R.panel.hidden) return;
  // measure where the panel really is: the sizes of
  // the window differ from the area a fixed box
  // sits in (the address bar), so they can't be
  // trusted. Only the panel moves: never scroll the
  // page here, it would raise another event, and
  // the text would creep upward.
  R.panel.style.bottom = "";
  R.panel.style.maxHeight = "";
  const shown = v.offsetTop + v.height;
  const kb = Math.round(Math.max(0,
    R.panel.getBoundingClientRect().bottom - shown));
  if (!kb) return;
  R.panel.style.bottom = kb + "px";
  R.panel.style.maxHeight =
    Math.max(120, v.height * 0.7) + "px";
}

if (window.visualViewport) {
  visualViewport.addEventListener("resize", lift);
  visualViewport.addEventListener("scroll", lift);
}

// the Contents button shows whether its list is open
function tocOpen(open) {
  R.tools?.querySelector(".toc-btn")
    ?.setAttribute("aria-expanded", String(open));
}

function langSwitch() {
  const box = h("div", { class: "seg",
    role: "group", "aria-label": t("r.meanin") });
  for (const l of ["en", "hy"]) {
    box.append(btn(LANG_NAMES[l], () => {
      if (l === meaningLang()) return;
      pagePick.meaning = l;
      drawWord();
    }, { class: null, lang: l,
      "aria-pressed": String(l === meaningLang()) }));
  }
  return box;
}

function placesNav() {
  const n = R.refs.length;
  const at = R.refs.indexOf(R.sel);
  const off = n < 2 ? "" : null;
  const label = n === 1 ? t("r.only")
    : t("r.places", at + 1, n);
  return section(t("r.inbook"),
    h("div", { class: "places" },
      h("span", {}, label),
      btn("‹", () => step(-1), { disabled: off,
        "aria-label": t("r.prevplace") }),
      btn("›", () => step(1), { disabled: off,
        "aria-label": t("r.nextplace") })));
}

function markAt(i) {
  return R.marks.find((m) => m.at === i);
}

// the address of the line of word i, to share
function lineLink(i) {
  return location.origin +
    pathOf("#/read/" + enc(R.name)) +
    "?line=" + (R.wpos[i][0] + 1);
}

async function copyLink(b) {
  const link = lineLink(R.sel);
  try {
    await navigator.clipboard.writeText(link);
    b.textContent = t("r.copied");
  } catch (e) {
    // no clipboard: show it to copy by hand
    prompt(t("r.linkto"), link);
  }
}

function linkButton() {
  const b = btn(t("r.link"), () => copyLink(b));
  return b;
}

// -- reporting an error --
// No server to send it to: the report opens as a
// new issue on GitHub, filled in, for the reader
// to look over and send

const ISSUES = "https://github.com/serjhnn/nx-gir"
  + "/issues/new";

// the address of the issue; info: {name, par, line,
// quote, fix, comment, link}
// REPORT-START
function reportText(info) {
  const tr = info.name.startsWith("ashkharhabar/");
  const quote = info.quote.length > 600
    ? info.quote.slice(0, 599) + "…" : info.quote;
  const body = [
    "**" + (tr ? "Translation" : "Grabar text")
      + ":** `books/" + info.name + "`, line "
      + info.line,
    info.par ? "**Other version:** `books/"
      + info.par + "`" : "",
    "**Place:** " + info.link,
    "> " + quote.replace(/\n+/g, " "),
    "**Correction:**\n" + (info.fix || "…"),
    info.comment ? "**Comment:**\n" + info.comment
      : "",
    tr ? "_By sending this I agree that my"
      + " correction is published under CC BY-SA"
      + " 4.0._" : "",
  ].filter(Boolean).join("\n\n");
  return {
    tr,
    title: "Error in " + info.name + ", line "
      + info.line,
    body: body.slice(0, 5000),
  };
}

function reportUrl(info) {
  const r = reportText(info);
  const q = new URLSearchParams({
    title: r.title, body: r.body,
    labels: r.tr ? "translation" : "grabar-text",
  });
  return ISSUES + "?" + q;
}

// the same report as an email, for those with no
// GitHub account
function reportMail(info) {
  const r = reportText(info);
  const at = CONTACT.join(String.fromCharCode(64));
  return "mailto:" + at + "?subject="
    + encodeURIComponent(r.title) + "&body="
    + encodeURIComponent(r.body.slice(0, 1500));
}
// REPORT-END

// the panel for an error in the chosen sentence
function reportError() {
  const at = R.sel;
  mark(false);
  sentence(true, at);
  const [lo, hi] = lit;
  const quote = wordsOf(lo, hi);
  const fix = h("textarea", { rows: "4",
    "aria-label": t("r.fix") });
  const note = h("textarea", { rows: "3",
    "aria-label": t("r.comment") });
  const send = h("a", { class: "icon-btn primary",
    target: "_blank", rel: "noopener" },
  t("r.gh"));
  const mail = h("a", { class: "icon-btn",
    rel: "noopener" }, t("r.mail"));
  const refresh = () => {
    const info = {
      name: R.name, par: R.par ? R.par.name : "",
      line: R.wpos[at][0] + 1, quote,
      fix: fix.value.trim(),
      comment: note.value.trim(),
      link: lineLink(at) };
    send.href = reportUrl(info);
    mail.href = reportMail(info);
  };
  fix.addEventListener("input", refresh);
  note.addEventListener("input", refresh);
  refresh();
  const cancel = btn(t("cancel"), () => {
    sentence(false);
    choose(at);
  });
  openPanel(t("r.report"), LANG,
    h("p", { class: "item-quote", lang: "hy" },
      "«" + (quote.length > 120
        ? quote.slice(0, 119) + "…" : quote) + "»"),
    h("label", { class: "rep-label" },
      t("r.should"), fix),
    h("label", { class: "rep-label" },
      t("r.note"), note),
    h("p", { class: "none" }, t("r.ghhow")),
    h("div", { class: "actions" }, send, mail,
      cancel));
  reveal(spanOf(at));
  fix.focus({ preventScroll: true });
}

function reportButton() {
  return btn("⚑ " + t("r.report"), reportError);
}

function wordActions() {
  const on = !!markAt(R.sel);
  return h("div", { class: "actions" },
    btn(on ? t("r.marked") : t("r.mark"),
      toggleMark, { "aria-pressed": String(on) }),
    btn(t("r.addnote"), () => editNote(-1)),
    linkButton(), reportButton());
}

// draw the panel for the chosen word
async function drawWord() {
  const at = R.sel;
  if (!R.panel || at < 0) return;
  const w = wordAt(at);
  openPanel(w, "hy",
    h("p", { class: "loading" }, t("r.looking")));
  let data;
  try {
    data = await lookup(w);
  } catch (e) {
    data = { error: e.message };
  }
  // a later word may have been chosen meanwhile
  if (R.sel !== at) return;
  const parts = [STATIC
    ? h("div", { class: "actions" }, linkButton(),
      reportButton())
    : wordActions(),
    placesNav(), searchWordButton(w)];
  if (data.error) {
    parts.push(h("p", { class: "error" },
      t("r.failed") + data.error));
  } else {
    if (data.abbr.length) {
      parts.push(section(t("r.abbr"),
        helperLines(data.abbr)));
    }
    parts.push(section(t("r.meaning"), langSwitch(),
      data.meaning.length ? helperLines(data.meaning)
        : h("p", { class: "none" }, t("r.noword"))));
  }
  R.panel.querySelector(".panel-body")
    .replaceChildren(...parts.filter(Boolean));
}

function mark(on) {
  // only the words of the page in the page
  for (const i of R.refs) {
    (on ? spanOf(i) : R.spans[i])
      ?.classList.toggle("ref", on);
  }
  if (R.sel >= 0) {
    (on ? spanOf(R.sel) : R.spans[R.sel])
      ?.classList.toggle("sel", on);
  }
}

// [first, last + 1): the sentence with word i
function sentenceOf(i) {
  let k = 0;
  while (k + 1 < R.starts.length &&
    R.starts[k + 1] <= i) k++;
  const hi = k + 1 < R.starts.length
    ? R.starts[k + 1] : R.spans.length;
  return [R.starts[k] || 0, hi];
}

let lit = null; // the sentence shown for a note
function sentence(on, i) {
  if (lit) {
    for (let j = lit[0]; j < lit[1]; j++) {
      R.spans[j]?.classList.remove("sent");
    }
    lit = null;
  }
  if (!on) return;
  lit = sentenceOf(i);
  for (let j = lit[0]; j < lit[1]; j++) {
    spanOf(j)?.classList.add("sent");
  }
}

// where the toolbar sticks: below the search box
function stickTop() {
  return R.tools ? parseFloat(
    getComputedStyle(R.tools).top) || 0 : 0;
}

// the bottom of the toolbar stuck to the top
function bar() {
  return R.tools ? R.tools.offsetHeight + stickTop()
    : 0;
}

// keep a word in view between the toolbar and the
// bottom sheet
function reveal(span) {
  if (!span) return;
  const r = span.getBoundingClientRect();
  const cover = sheet()
    ? R.panel.getBoundingClientRect().height : 0;
  const top = bar() + 16;
  const bottom = window.innerHeight - cover - 16;
  if (r.top < top || r.bottom > bottom) {
    const mid = (r.top + r.bottom) / 2;
    window.scrollBy({ top: mid - (top + bottom) / 2 });
  }
}

function choose(i) {
  mark(false);
  sentence(false);
  const key = R.keys[i];
  if (R.sel < 0 || R.keys[R.sel] !== key) {
    R.refs = [];
    R.keys.forEach((k, j) => {
      if (k === key) R.refs.push(j);
    });
  }
  ensure(i);
  R.sel = i;
  mark(true);
  drawWord().then(() => reveal(spanOf(i)));
}

function step(d) {
  const n = R.refs.length;
  if (n < 2) return;
  const at = R.refs.indexOf(R.sel);
  choose(R.refs[(at + d + n) % n]);
}

// scroll to word i and make it blink once
function go(i) {
  ensure(i);
  const s = spanOf(i);
  if (!s) return;
  if (sheet()) closePanel();
  const top = s.getBoundingClientRect().top;
  window.scrollBy({ top: top - bar() - 48 });
  s.classList.remove("flash");
  void s.offsetWidth; // restart the animation
  s.classList.add("flash");
}

// -- bookmarks and notes --

// the marks on the words, and the counts above
function decorate() {
  for (const s of main.querySelectorAll(
    ".w.bm, .w.noted")) {
    s.classList.remove("bm", "noted");
  }
  for (const m of R.marks) {
    spanOf(m.at)?.classList.add("bm");
  }
  for (const n of R.notes) {
    spanOf(n.at)?.classList.add("noted");
  }
  // on a phone the names hide, the counts stay
  const count = (sign, name, n) => [sign + " ",
    h("span", { class: "long" }, name + " · "),
    String(n)];
  const marks = t("r.marks") + " · " + R.marks.length;
  const notes = t("r.notes") + " · " + R.notes.length;
  // back to the folder the book is in
  const dir = dirOf(R.name || R.opening);
  R.tools.replaceChildren(...[
    R.who,
    R.prog,
    // the site's mark, once the top bar has
    // scrolled away (see stick())
    h("a", { class: "icon-btn home", href: "#/",
      "aria-label": t("nav.home"),
      title: t("nav.home") },
    document.querySelector(".brand-mark")
      .cloneNode(true)),
    h("a", { class: "icon-btn back",
      href: folderHref(dir),
      "aria-label": t("r.back"),
      title: t("r.backto", dir || t("nav.library")) },
    icon(ICONS.back)),
    pagesBtn(),
    // a second click hides the list again
    R.contents.length ? btn(["☰ ", h("span",
      { class: "long" }, t("r.contents"))],
    toggleContents, { class: "icon-btn toc-btn",
      "aria-label": t("r.contents"),
      "aria-expanded": String(!!R.panel &&
        !R.panel.hidden &&
        R.panel.dataset.kind === "Contents"),
      title: t("r.contents") + ": "
        + plural(R.contents.length, "heading") })
      : null,
    STATIC ? null : btn(count("★", t("r.marks"),
      R.marks.length), showMarks,
    { "aria-label": marks, title: marks }),
    STATIC ? null : btn(count("✎", t("r.notes"),
      R.notes.length), showNotes,
    { "aria-label": notes, title: notes }),
    R.editable ? h("a", { class: "icon-btn",
      href: "#/edit/" + enc(R.name || R.opening) },
    t("r.edit")) : null,
    R.par ? btn(["⇆ ", h("span", { class: "long" },
      t("r.par"))],
    () => setView({ parallel: !view.parallel }), {
      "aria-pressed": String(view.parallel),
      "aria-label": t("r.two"),
      title: t("r.beside", parLabel(R.par.name)) })
      : null,
    // on a wide screen: each line under its pair,
    // as on a phone, or beside it
    R.par && view.parallel ? btn(icon(ICONS[
      view.stacked ? "rows" : "columns"]),
    () => setView({ stacked: !view.stacked }), {
      class: "icon-btn par-layout",
      "aria-label": t("r.under"),
      "aria-pressed": String(view.stacked),
      title: view.stacked ? t("r.stacked")
        : t("r.side") }) : null,
    // on a phone the text tools hide behind this
    btn(icon(ICONS.sliders), () => {
      const open = R.tools.classList.toggle("open");
      more.setAttribute("aria-expanded",
        String(open));
    }, {
      class: "icon-btn more",
      "aria-expanded": String(
        R.tools.classList.contains("open")),
      "aria-label": t("r.settings"),
      title: t("r.settings") }),
    viewTools(),
    R.found ? foundStrip() : null,
  ].filter(Boolean));
  const more = R.tools.querySelector(".more");
  fit();
}

// Do all the buttons fit in one row? If not, the text
// settings hide behind the settings button (class
// collapsed); if they still do not, the names of the
// buttons go and only their icons stay (compact; both
// in style.css). Measured with everything shown, so it
// follows the width of the window, the names and the
// counts, not a fixed breakpoint.
function fit() {
  const t = R.tools;
  if (!t || !t.isConnected) return;
  const one = () => {
    const kids = [...t.children].filter((e) =>
      e.offsetParent
      && !e.classList.contains("readbar")
      && !e.classList.contains("found"));
    const edge = t.getBoundingClientRect().right;
    return !kids.some((e) =>
      e.offsetTop !== kids[0].offsetTop
      || e.getBoundingClientRect().right > edge + 1);
  };
  // the widest case: the home button shown too
  const stuck = t.classList.contains("stuck");
  t.classList.add("stuck");
  t.classList.remove("collapsed", "compact");
  if (!one()) {
    t.classList.add("collapsed");
    if (!one()) t.classList.add("compact");
  }
  t.classList.toggle("stuck", stuck);
}

let fitting = 0;
window.addEventListener("resize", () => {
  cancelAnimationFrame(fitting);
  fitting = requestAnimationFrame(fit);
}, { passive: true });

// -- how the text looks: size and alignment, kept
// in this browser (a phone and a computer may want
// different sizes) --

// text sizes in rem; SIZE is the default
const SIZES = [0.7, 0.8, 0.9, 1, 1.15, 1.3, 1.5, 1.75,
  2];
const SIZE = 4;
// space between lines, as line-height; the first is
// the default
const LINES = [1.75, 2.1, 2.5];
// the book fonts (fonts.css); the first is the
// default
const FONTS = ["grqi", "arianserif", "noto",
  "faulmann", "geghagrutyun", "tumanian",
  "garamond", "oldstandard"];
const FONT_NAMES = { grqi: "Arian Grqi",
  noto: "Noto Serif",
  arianserif: "Arian AMU Serif",
  faulmann: "Faulmann",
  geghagrutyun: "Geghagrutyun",
  tumanian: "Tumanian's Hand",
  garamond: "EB Garamond",
  oldstandard: "Old Standard" };
const view = { size: SIZE, center: false, line: 0,
  font: 0, parallel: true, sentences: false,
  full: false, stacked: false,
  // read in pages: null = yes (the default)
  paged: null };
try {
  const v = JSON.parse(
    localStorage.getItem("nxgir-view") || "{}");
  const i = SIZES.indexOf(v.rem);
  if (i >= 0) view.size = i;
  // saved before 0.7 and 0.8 came: the place in
  // the list, from 0.9
  else if (SIZES[v.size + 2]) view.size = v.size + 2;
  view.center = v.center === true;
  view.line = Math.max(0, LINES.indexOf(v.line));
  view.font = Math.max(0, FONTS.indexOf(v.font));
  view.parallel = v.parallel !== false;
  view.sentences = v.sentences === true;
  view.full = v.full === true;
  view.stacked = v.stacked === true;
  view.paged = typeof v.paged === "boolean"
    ? v.paged : null;
} catch (e) {}

function applyView() {
  // on the page too: the word panel follows the size
  document.documentElement.style.setProperty(
    "--text-size", SIZES[view.size] + "rem");
  // on the page, as the font list is drawn before
  // the text; style.css gives it to the text only
  const root = document.documentElement;
  if (view.font) root.dataset.font = FONTS[view.font];
  else delete root.dataset.font;
  if (!R.text) return;
  R.text.style.setProperty("--text-size",
    SIZES[view.size] + "rem");
  R.text.style.setProperty("--text-line",
    LINES[view.line]);
  R.text.classList.toggle("centered", view.center);
  R.text.classList.toggle("sentences",
    view.sentences);
  // the whole width of the screen, not a column
  R.text.classList.toggle("full", view.full);
  document.body.classList.toggle("full", view.full);
  syncPar();
  const par = Boolean(R.par && view.parallel);
  R.text.classList.toggle("parallel", par);
  R.text.classList.toggle("stacked",
    par && view.stacked);
  // the page widens for two columns only
  document.body.classList.toggle("parallel",
    par && !view.stacked);
}

function setView(change) {
  // Side by side turned on: its lines first
  if (change.parallel && R.par && !R.par.lines) {
    loadPar().then(() => setView(change));
    return;
  }
  // keep the word at the top of the screen there
  const i = R.ready && R.hi > R.lo ? topWord() : -1;
  const before = i >= 0 ? wordRect(i).top : 0;
  Object.assign(view, change);
  try {
    localStorage.setItem("nxgir-view",
      JSON.stringify({ rem: SIZES[view.size],
        center: view.center,
        line: LINES[view.line],
        font: FONTS[view.font],
        parallel: view.parallel,
        sentences: view.sentences,
        full: view.full,
        stacked: view.stacked,
        paged: view.paged }));
  } catch (e) {}
  applyView();
  if ("paged" in change) {
    R.pages = pagesOf();
    showPage(pageOfWord(Math.max(i, 0)), false);
  }
  if (i >= 0) {
    const r = wordRect(i);
    if (r) window.scrollBy(0, r.top - before);
  }
  decorate();
}

function viewTools() {
  const n = view.size;
  return h("div", { class: "view",
    role: "group", "aria-label": t("r.text") },
  btn("A−", () => setView({ size: n - 1 }), {
    "aria-label": t("r.smaller"),
    title: t("r.smaller"),
    disabled: n === 0 ? "" : null }),
  btn("A+", () => setView({ size: n + 1 }), {
    "aria-label": t("r.bigger"),
    title: t("r.bigger"),
    disabled: n === SIZES.length - 1 ? "" : null }),
  btn(icon(ICONS[view.center ? "center" : "left"]),
    () => setView({ center: !view.center }), {
      "aria-label": t("r.center"),
      "aria-pressed": String(view.center),
      title: view.center ? t("r.centered")
        : t("r.left") }),
  btn(icon(ICONS.spacing),
    () => setView({
      line: (view.line + 1) % LINES.length }), {
      "aria-label": t("r.spacing", view.line + 1,
        LINES.length),
      title: view.line === LINES.length - 1
        ? t("r.widest") : t("r.more") }),
  btn("¶", () => setView({
    sentences: !view.sentences }), {
    "aria-label": t("r.sent"),
    "aria-pressed": String(view.sentences),
    title: view.sentences ? t("r.apart")
      : t("r.written") }),
  btn(icon(ICONS.width),
    () => setView({ full: !view.full }), {
      "aria-label": t("r.width"),
      "aria-pressed": String(view.full),
      title: view.full ? t("r.whole")
        : t("r.column") }),
  // a long part in pages: a page at a time is in
  // the browser, a few MB instead of hundreds
  btn("▤", () => setView({ paged: !paged() }), {
    "aria-label": t("r.paged"),
    "aria-pressed": String(paged()),
    title: paged() ? t("r.inpages") : t("r.long") }),
  fontPick(),
  // the theme button joins the row while reading
  button);
}

// the book fonts by name
function fontPick() {
  const pick = h("select", { class: "font-pick",
    "aria-label": t("r.font"),
    title: t("r.font") },
  FONTS.map((f, i) => h("option", { value: String(i),
    selected: i === view.font ? "" : null },
  FONT_NAMES[f])));
  pick.addEventListener("change", () =>
    setView({ font: Number(pick.value) }));
  return pick;
}

function fail(e) {
  alert(t("r.fail") + e.message);
}

async function toggleMark() {
  try {
    const r = await send("mark",
      { name: R.name, pos: R.wpos[R.sel] });
    R.marks = r.marks;
  } catch (e) {
    return fail(e);
  }
  decorate();
  if (R.sel >= 0) drawWord();
}

// the text of a line from word i on, cut to n
function snippet(i, n = 70) {
  const [line, k] = R.wpos[i];
  const t = R.src[line].slice(2 * k + 1).join("")
    .trim();
  return t.length > n
    ? t.slice(0, n - 1).trimEnd() + "…" : t;
}

function lineOf(i) {
  return t("r.line", R.wpos[i][0] + 1);
}

// -- pages of a part --

// ‹ n/N › in the tools: the page before and the page
// after, and the number of this one. Only when the
// part is in pages. (The other parts of the book are
// one step back: the back button.)
function pagesBtn() {
  const n = R.pages.length;
  if (n < 2) return null;
  const k = R.page;
  const arrow = (to, sign, label, off) => btn(sign,
    () => turnPage(to), {
      class: "icon-btn part-step" + (off ? " off" : ""),
      "aria-label": label, title: label });
  return h("span", { class: "part-tools" },
    arrow(k - 1, "‹", t("r.prevpage"), k === 0),
    h("span", { class: "icon-btn",
      "aria-label": t("r.page", k + 1, n),
      title: t("r.page", k + 1, n) },
    (k + 1) + "/" + n),
    arrow(k + 1, "›", t("r.nextpage"), k === n - 1));
}

// -- the contents: the chapters and sermons --

// the first word on the line or after it
function wordOfLine(line) {
  let lo = 0;
  let hi = R.wpos.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (R.wpos[mid][0] < line) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function toggleContents() {
  if (R.panel && !R.panel.hidden &&
      R.panel.dataset.kind === "Contents") {
    closePanel();
  } else {
    showContents();
  }
}

function showContents() {
  closePanel();
  // the heading the top of the page is under
  const top = R.spans.length
    ? R.wpos[topWord()][0] : 0;
  let here = -1;
  R.contents.forEach((c, k) => {
    if (c.line <= top) here = k;
  });
  const list = h("ul", { class: "items toc" });
  R.contents.forEach((c, k) => {
    const meta = c.level === 1 || !c.n ? ""
      : (c.kind || t("r.chapter")) + " " + c.n + " · ";
    const link = h("button", { type: "button",
      class: "item-main" },
    h("span", { class: "item-meta" },
      meta + t("r.line", c.line + 1)),
    h("span", { class: "item-quote", lang: "hy" },
      c.title || (c.kind || "Գլուխ") + " " + c.n));
    link.addEventListener("click", () =>
      go(wordOfLine(c.line)));
    const li = h("li", { class: c.level === 1
      ? "group" : null }, link);
    if (k === here) {
      li.classList.add("here");
      link.setAttribute("aria-current", "true");
    }
    list.append(li);
  });
  openPanel(t("r.contents"), LANG, list);
  // the book's title under the heading, which
  // stays at the top while the list scrolls
  const head = R.panel.querySelector(".panel-head h2");
  const box = h("div", { class: "toc-head" });
  head.before(box);
  box.append(head, h("p", { class: "toc-book",
    lang: "hy" }, R.head || R.title));
  list.querySelector(".here")
    ?.scrollIntoView({ block: "center" });
}

function showMarks() {
  closePanel();
  if (!R.marks.length) {
    openPanel(t("r.marks"), LANG, h("p",
      { class: "none" }, t("r.nomarks")));
    return;
  }
  const list = h("ul", { class: "items" });
  for (const m of R.marks) {
    const link = h("button", { type: "button",
      class: "item-main" },
    h("span", { class: "item-meta" }, lineOf(m.at)),
    h("span", { class: "item-quote", lang: "hy" },
      snippet(m.at)));
    link.addEventListener("click", () => go(m.at));
    const del = btn(t("remove"), async () => {
      try {
        R.marks = (await send("mark",
          { name: R.name, pos: m.pos })).marks;
      } catch (e) {
        return fail(e);
      }
      decorate();
      showMarks();
    }, { class: "link-btn" });
    list.append(h("li", {}, link, del));
  }
  openPanel(t("r.marks"), LANG, list);
}

function showNotes() {
  closePanel();
  if (!R.notes.length) {
    openPanel(t("r.notes"), LANG, h("p",
      { class: "none" }, t("r.nonotes")));
    return;
  }
  const list = h("ul", { class: "items" });
  R.notes.forEach((n, i) => {
    const link = h("button", { type: "button",
      class: "item-main" },
    h("span", { class: "item-meta" },
      lineOf(n.at) + (n.date ? " · " + n.date : "")),
    h("span", { class: "item-quote", lang: "hy" },
      "«" + n.quote + "»"),
    h("span", { class: "item-text" }, n.text));
    link.addEventListener("click", () => go(n.at));
    const edit = btn(t("edit"), () => {
      R.sel = -1;
      editNote(i);
    }, { class: "link-btn" });
    const del = btn(t("delete"), async () => {
      if (!confirm(t("r.delnote"))) return;
      try {
        R.notes = (await send("note", { name: R.name,
          i: i, delete: true })).notes;
      } catch (e) {
        return fail(e);
      }
      decorate();
      showNotes();
    }, { class: "link-btn" });
    list.append(h("li", {}, link,
      h("div", { class: "item-btns" }, edit, del)));
  });
  openPanel(t("r.notes"), LANG, list);
}

// write a new note on the chosen word's sentence
// (i = -1), or change note i
function editNote(i) {
  const old = i >= 0 ? R.notes[i] : null;
  const at = old ? old.at : R.sel;
  mark(false);
  sentence(true, at);
  const [lo, hi] = lit;
  const words = wordsOf(lo, hi);
  const box = h("textarea", { rows: "5",
    "aria-label": t("r.notebox") });
  box.value = old ? old.text : "";
  const save = btn(t("save"), async () => {
    const text = box.value.trim();
    if (!text) return box.focus();
    const body = old ? { name: R.name, i: i, text }
      : { name: R.name, pos: R.wpos[at], text };
    try {
      R.notes = (await send("note", body)).notes;
    } catch (e) {
      return fail(e);
    }
    decorate();
    showNotes();
  }, { class: "icon-btn primary" });
  const cancel = btn(t("cancel"), () => {
    if (old) showNotes();
    else closePanel();
  });
  openPanel(old ? t("r.editnote") : t("r.newnote"),
    LANG,
    h("p", { class: "item-quote", lang: "hy" },
      "«" + (words.length > 120
        ? words.slice(0, 119) + "…" : words) + "»"),
    box, h("div", { class: "actions" }, save, cancel));
  reveal(spanOf(at));
  box.focus({ preventScroll: true });
}

// -- where the book was left --

// the first word at the top of the screen, not
// hidden under the toolbar
function topWord() {
  const edge = R.tools.getBoundingClientRect().bottom;
  let lo = Math.min(R.lo, R.spans.length - 1);
  let hi = Math.max(lo, R.hi - 1);
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    const r = wordRect(mid);
    if (r.bottom > edge) hi = mid;
    else lo = mid + 1;
  }
  return lo;
}

// How long readers stay with a book: the time a
// book is open, the page in front and the reader
// active (a scroll, tap or key in the last two
// minutes) is added up per browser and book; when
// it passes 1, 5, 15, 30 or 60 minutes, an event
// "/read/<book>/5min" is counted (titled
// "<title> · 5 min"), once each.
const MINUTES = [1, 5, 15, 30, 60];
const TICK = 10; // seconds
const IDLE = 120; // seconds without a sign of life
let alive = 0; // when the reader last did something
function stir() {
  alive = Date.now();
}
for (const ev of ["scroll", "pointerdown",
  "keydown"]) {
  window.addEventListener(ev, stir,
    { passive: true });
}
function tick() {
  if (!R.name || document.hidden) return;
  if (Date.now() - alive > IDLE * 1000) return;
  const key = "nxgir-time:" + R.name;
  let was = 0;
  try {
    was = Number(localStorage.getItem(key)) || 0;
  } catch (e) {
    return; // nowhere to keep it
  }
  const now = was + TICK;
  try {
    localStorage.setItem(key, String(now));
  } catch (e) {
    return;
  }
  for (const m of MINUTES) {
    if (was < m * 60 && now >= m * 60) {
      const t = R.title || R.name;
      beacon({ p: `/read/${R.name}/${m}min`,
        t: `${t} · ${m} min`, e: "true" });
    }
  }
}
if (STATIC && window.NXGIR_COUNT) {
  setInterval(tick, TICK * 1000);
}

// the last word on the screen
function lastWord() {
  const edge = window.innerHeight;
  let lo = Math.min(R.lo, R.spans.length - 1);
  let hi = Math.max(lo, R.hi - 1);
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    const r = wordRect(mid);
    if (r.top < edge) lo = mid;
    else hi = mid - 1;
  }
  return lo;
}

function savePos(keepalive) {
  clearTimeout(R.timer);
  R.timer = 0;
  if (!R.name || !R.spans.length) return;
  const top = topWord();
  const pos = R.wpos[top];
  const k = pos.join(",");
  if (k === R.saved) return;
  R.saved = k;
  if (STATIC) {
    depth(R.title);
    // as State.progress() counts it
    const pct = Math.min(100,
      Math.round(100 * (pos[0] + 1) / R.lines));
    try {
      localStorage.setItem("nxgir-read:" + R.name,
        JSON.stringify({ at: top, pct,
          t: Math.floor(Date.now() / 1000),
          title: R.head }));
    } catch (e) {}
    return;
  }
  send("position", { name: R.name, pos,
    lines: R.lines }, keepalive).catch(() => {
    R.saved = "";
  });
}

// the toolbar at the top of the screen: it shows
// the home button
function stick() {
  if (!R.tools) return;
  R.tools.classList.toggle("stuck",
    R.tools.getBoundingClientRect().top
      < stickTop() + 1);
}

// how much of the text has been scrolled past,
// in the bar above the reader's buttons: 100%
// once its end is on the screen
function progress() {
  if (!R.prog || !R.text?.isConnected) return;
  const r = R.text.getBoundingClientRect();
  const seen = window.innerHeight - r.top;
  const f = r.height > 0
    ? Math.min(1, Math.max(0, seen / r.height)) : 1;
  // of the page, then of the whole part
  const [a, b] = R.pages[R.page] || [0, R.lines];
  const all = R.lines > 0
    ? (a + f * (b - a)) / R.lines : f;
  const pct = Math.round(all * 100);
  R.prog.firstChild.firstChild.style.width =
    pct + "%";
  R.prog.setAttribute("aria-valuenow", pct);
}

window.addEventListener("resize", progress,
  { passive: true });

window.addEventListener("scroll", () => {
  stick();
  progress();
  if (!R.name) return;
  clearTimeout(R.timer);
  // the published copy only writes to this
  // browser: save at once; the server gets one
  // request once the scrolling stops
  R.timer = setTimeout(savePos, STATIC ? 0 : 200);
}, { passive: true });

document.addEventListener("visibilitychange", () => {
  if (document.hidden && R.timer) savePos(true);
});
window.addEventListener("pagehide", () => {
  if (R.timer) savePos(true);
});

document.addEventListener("keydown", (e) => {
  if (e.target.closest("textarea")) return;
  if (e.key === "Escape") closePanel();
  if (R.sel < 0) return;
  if (e.key === "n") step(1);
  else if (e.key === "N") step(-1);
});

// Text that starts `at` characters into its line,
// with the bold and italic parts of the line
// ([start, end, "b" or "i"], counted in characters
// as Python does, not in JS string units) wrapped in
// <strong> and <em>.
function styled(t, at, spans) {
  if (!spans.length) return [t];
  const chars = Array.from(t);
  const end = at + chars.length;
  const cuts = new Set([at, end]);
  for (const [a, b] of spans) {
    if (a > at && a < end) cuts.add(a);
    if (b > at && b < end) cuts.add(b);
  }
  const points = [...cuts].sort((x, y) => x - y);
  const out = [];
  for (let k = 0; k + 1 < points.length; k++) {
    const [a, b] = [points[k], points[k + 1]];
    const piece = chars.slice(a - at, b - at).join("");
    const sp = spans.find((x) => x[0] <= a && b <= x[1]);
    out.push(sp ? h(sp[2] === "b" ? "strong" : "em",
      {}, piece) : piece);
  }
  return out;
}

// -- two versions side by side: the other one
// (data.parallel, e.g. ashkharhabar/ beside
// grabar/) goes in a .par line after each line;
// the CSS puts it under its line on a phone and
// beside it on a wide screen --

// the name of a version (grabar, ashkharhabar) in
// LANG
function parLabel(name) {
  const top = name.split("/")[0];
  return SHELF_LANGS.includes(top) ? t("shelf." + top)
    : top;
}

// the names above the two columns; the other one
// opens that version
function parHead(name, other) {
  return [
    h("p", { class: "par par-head" },
      parLabel(name)),
    h("p", { class: "par par-head" },
      h("a", { href: "#/read/" + enc(other) },
        parLabel(other))),
  ];
}

// -- pages: a long part is read a page at a time --
//
// Only the lines of one page are in the page (the
// DOM), so a phone with little memory holds a few
// MB for a part instead of hundreds. Everything else
// (R.keys, R.wpos, R.src) is data, for all the words
// of the part: R.spans has the word elements of the
// page only, at the index of the word in the part.

// the characters of a page
const PAGE_CHARS = 5000;

// Read in pages? Yes, unless the reader turned it
// off in the text settings (the ▤ button).
function paged() {
  return view.paged !== false;
}

// [first line, last line + 1] of each page; the whole
// part is one page when it is short or not in pages
function pagesOf() {
  const n = R.src.length;
  const size = R.src.map((parts) =>
    parts.join("").length);
  const total = size.reduce((x, y) => x + y, 0);
  if (!paged() || total < PAGE_CHARS * 1.5) {
    return [[0, n]];
  }
  const out = [];
  let from = 0;
  let sum = 0;
  size.forEach((c, line) => {
    sum += c;
    if (sum >= PAGE_CHARS && line + 1 < n) {
      out.push([from, line + 1]);
      from = line + 1;
      sum = 0;
    }
  });
  // not a last page of a few lines
  if (sum < PAGE_CHARS / 3 && out.length) {
    out[out.length - 1][1] = n;
  } else {
    out.push([from, n]);
  }
  return out;
}

// the page with word i
function pageOfWord(i) {
  let k = 0;
  while (k + 1 < R.pages.length
    && R.first[R.pages[k][1]] <= i) k++;
  return k;
}

// show the page with word i (before using its
// element)
function ensure(i) {
  if (i < R.lo || i >= R.hi) {
    showPage(pageOfWord(i), false);
  }
}

// the text of word i, from the data (its element may
// not be in the page)
function wordAt(i) {
  const [line, n] = R.wpos[i];
  return R.src[line][2 * n + 1];
}

function wordsOf(lo, hi) {
  const out = [];
  for (let j = lo; j < hi; j++) out.push(wordAt(j));
  return out.join(" ");
}

// ‹ 2 / 11 › above and under the text
function pager(where) {
  const n = R.pages.length;
  if (n < 2) return null;
  const k = R.page;
  const to = (d) => () => turnPage(k + d);
  return h("div", { class: "pager " + where,
    role: "navigation", "aria-label": t("r.pages") },
  btn(t("r.prev"), to(-1), {
    disabled: k === 0 ? "" : null }),
  h("span", {}, (k + 1) + " / " + n),
  btn(t("r.next"), to(1), {
    disabled: k === n - 1 ? "" : null }));
}

// to the top of another page
function turnPage(k) {
  showPage(k, false);
  const top = R.text.getBoundingClientRect().top
    + window.scrollY;
  window.scrollTo(0, top - bar() - 16);
  stick();
  progress();
}

// Build page k in .text. fresh: the book is being
// opened, its toolbar is not there yet.
function showPage(k, fresh) {
  mark(false);
  sentence(false);
  R.spans.fill(undefined, R.lo, R.hi);
  const [a, b] = R.pages[k];
  Object.assign(R, { page: k, lo: R.first[a],
    hi: R.first[b], lineEls: [], parBuilt: false });
  const frag = document.createDocumentFragment();
  if (k === 0 && R.credit) {
    frag.append(trCredit(R.credit, false));
  }
  frag.append(pager("top") || "");
  for (let line = a; line < b; line++) {
    const parts = R.src[line];
    const p = document.createElement("p");
    const f = R.format[line];
    if (f && f.h) p.className = "md-h md-h" + f.h;
    if (f && f.q) p.classList.add("md-q");
    p.dataset.l = line;
    p.style.setProperty("--rows",
      rows(parts.join("").length));
    // plain text, unless the line has bold or italic
    if (f && f.spans.length) fillLine(p, line);
    else plainLine(p, line);
    frag.append(p);
    R.lineEls[line] = p;
  }
  frag.append(pager("end") || "");
  R.text.replaceChildren(frag);
  // the cards to the parts before and after: at the
  // end of the last page only
  if (R.end) {
    R.end.style.display = k < R.pages.length - 1
      ? "none" : "";
  }
  R.ready = true;
  syncPar();
  if (fresh) return;
  decorate();
  mark(true);
}

// A line as plain text, with no element for each
// word: about half the nodes of a page, so a page
// turn is quicker on a slow device. The words are
// made when one is needed (expandLine): a tap, a
// mark, a note, a jump to a word.
function plainLine(p, line) {
  let at = R.first[line];
  let text = "";
  R.src[line].forEach((t, j) => {
    if (j % 2) {
      if (j > 1 && R.startSet.has(at)) {
        if (text) p.append(text);
        p.append(cut());
        text = "";
      }
      at++;
    }
    text += t;
  });
  if (text) p.append(text);
  p.classList.add("pl");
}

// The line with an element for each word: R.spans
function fillLine(p, line) {
  const f = R.format[line];
  const spans = f ? f.spans : [];
  let at = R.first[line];
  let chars = 0; // characters before this part
  R.src[line].forEach((t, j) => {
    const nodes = styled(t, chars, spans);
    chars += Array.from(t).length;
    if (j % 2 === 0) {
      if (t) p.append(...nodes);
      return;
    }
    if (j > 1 && R.startSet.has(at)) {
      p.append(cut());
    }
    const s = document.createElement("span");
    s.className = "w";
    s.dataset.i = at;
    s.append(...nodes);
    R.spans[at++] = s;
    p.append(s);
  });
}

// a plain line of the page becomes its words; the
// text and its place stay the same
function expandLine(line) {
  const p = R.lineEls[line];
  if (!p || !p.classList.contains("pl")) return;
  p.classList.remove("pl");
  p.replaceChildren();
  fillLine(p, line);
}

// the element of word i (of the page), made if the
// line is still plain
function spanOf(i) {
  if (!R.spans[i] && i >= R.lo && i < R.hi) {
    expandLine(R.wpos[i][0]);
  }
  return R.spans[i];
}

// where word i is on the screen, without making
// its element: the range of its letters in a plain
// line; null when it is not on the page
function wordRect(i) {
  const s = R.spans[i];
  if (s) return s.getBoundingClientRect();
  if (i < R.lo || i >= R.hi) return null;
  const [line, k] = R.wpos[i];
  const p = R.lineEls[line];
  const parts = R.src[line];
  let from = 0;
  for (let j = 0; j < 2 * k + 1; j++) {
    from += parts[j].length;
  }
  const to = from + parts[2 * k + 1].length;
  let base = 0;
  for (const n of p.childNodes) {
    if (n.nodeType !== 3) continue;
    if (from < base + n.length) {
      const r = document.createRange();
      r.setStart(n, from - base);
      r.setEnd(n, Math.min(to, base + n.length) - base);
      return r.getBoundingClientRect();
    }
    base += n.length;
  }
  return p.getBoundingClientRect();
}

// Rows a paragraph of n characters takes, for the
// height the browser guesses before it is drawn
// (--rows, see content-visibility in style.css)
const ROW = 36;

function rows(n) {
  return String(Math.max(1, Math.ceil(n / ROW)));
}

function parLine(line) {
  const parts = R.par.lines[line] || [""];
  const p = h("p", { class: "par" });
  p.style.setProperty("--rows",
    rows(parts.join("").length));
  let i = R.par.first[line] || 0;
  parts.forEach((t, k) => {
    if (k % 2 && k > 1 && R.par.starts.has(i)) {
      p.append(cut());
    }
    if (k % 2) i++;
    if (t) p.append(t);
  });
  return p;
}

// who made and reviewed a translation and its
// license (data.credit, books/TRANSLATIONS.tsv);
// of the other version (of), it hides with it
const HELP = "https://github.com/serjhnn/nx-gir/"
  + "blob/main/CONTRIBUTING.md";

// Fetch the other version (R.par is only its name
// until then): a reader of one column never needs
// it. If it cannot be read, the part is read alone.
async function loadPar() {
  const par = R.par;
  if (!par || par.lines) return;
  try {
    const d = await api("book?name=" +
      encodeURIComponent(par.name));
    // the first word of each of its lines
    let n = 0;
    d.first = d.lines.map((parts) => {
      const at = n;
      n += (parts.length - 1) / 2;
      return at;
    });
    d.starts = new Set(d.starts || []);
    if (R.par === par) R.par = d;
  } catch (e) {
    if (R.par === par) R.par = null;
  }
}

// The other version is built only while it is
// shown (Side by side on): about 55,000 nodes and
// 30 MB of layout for a long part. Turning it off
// removes it again. Called by applyView() and once
// the lines are in the page.
function syncPar() {
  const want = Boolean(R.par && R.par.lines
    && view.parallel && R.ready);
  if (want === R.parBuilt) return;
  R.parBuilt = want;
  if (!want) {
    for (const e of R.text.querySelectorAll(
      ".par, .of-par")) e.remove();
    return;
  }
  // (R.lineEls has the lines of this page only)
  R.lineEls.forEach((p, line) => {
    p.after(parLine(line));
  });
  // lines the other version has more of: at the end
  // of the last page
  if (R.page === R.pages.length - 1) {
    const end = R.text.querySelector(".pager.end");
    for (let line = R.lines;
      line < R.par.lines.length; line++) {
      const more = [h("p", { class: "par" }),
        parLine(line)];
      if (end) end.before(...more);
      else R.text.append(...more);
    }
  }
  const of = R.page === 0 && !R.credited
    && R.par.credit;
  R.text.prepend(...parHead(R.opening, R.par.name),
    ...(of ? [trCredit(R.par.credit, true)] : []));
}

// the credit line of a translation in LANG: in
// Armenian as the server words it (TEXTS in
// nxgir_translations.py)
function creditText(c) {
  if (LANG === "hy" || !c.status) return c.text;
  const who = (c.reviewers || []).join(", ");
  return t("tr." + c.status, c.model || "Claude",
    who);
}

function trCredit(c, of) {
  return h("p", { class: "tr-credit"
    + (of ? " of-par" : "") },
    named(creditText(c)), " · ",
    h("a", { href: c.url, rel: "license" },
      c.license),
    " · ",
    h("a", { href: HELP }, t("r.help")));
}

// the end of a part of a long book (data.parts):
// the parts before and after it, and its folder
function partEnd(p) {
  if (!p || !(p.prev || p.next)) return null;
  const card = (q, cls, label) => q
    ? h("a", { class: cls,
      href: "#/read/" + enc(q.name) },
    h("small", {}, label),
    q.title ? h("span", { lang: "hy" }, q.title)
      : null)
    : h("span");
  return h("div", { class: "part-end" },
    h("nav", { class: "part-nav",
      "aria-label": t("r.parts") },
    card(p.prev, "prev",
      t("r.partprev", p.n - 1, p.total)),
    card(p.next, "next",
      t("r.partnext", p.n + 1, p.total))),
    h("p", { class: "part-all" },
      h("a", { href: folderHref(p.folder) },
        t("r.allparts", p.total),
        h("span", { lang: "hy" }, p.book))));
}

// where a sentence starts inside a line: shown as
// a break when Sentences (¶) is on
function cut() {
  return h("span", { class: "cut" });
}

async function book(name, line, found) {
  const data = await api("book?name=" +
    encodeURIComponent(name));
  const title = name.split("/").pop();
  document.title = title + " · " + NAME;
  Object.assign(R, {
    name: "", lines: data.lines.length,
    spans: [], keys: [], wpos: [], lo: 0, hi: 0,
    starts: data.starts, marks: data.marks,
    notes: data.notes, sel: -1, refs: [],
    contents: data.contents || [],
    saved: "", editable: data.editable,
    opening: name, par: null, parts: data.parts,
    lineEls: [], ready: false, parBuilt: false,
    end: null,
    credited: Boolean(data.credit),
    credit: data.credit, src: data.lines,
    format: data.format || {},
    startSet: new Set(data.starts || []),
    found: found || null,
  });
  // every word as data; the elements are made a
  // page at a time (showPage)
  R.first = [];
  data.lines.forEach((parts, line) => {
    R.first.push(R.keys.length);
    for (let j = 1; j < parts.length; j += 2) {
      R.keys.push(wordKey(parts[j]));
      R.wpos.push([line, (j - 1) / 2]);
    }
  });
  R.first.push(R.keys.length);
  R.spans = new Array(R.keys.length);
  R.pages = pagesOf();
  // the other version, read beside it on a wide
  // screen
  const other = (data.parallel || [])[0];
  if (other) {
    // its lines are fetched only when shown
    R.par = { name: other };
    if (view.parallel) await loadPar();
  }
  const text = h("div", { class: "text",
    lang: "hy" });
  R.text = text;
  applyView();
  // the page with the line asked for, the saved
  // place, or the start
  const want = line >= 1 && R.keys.length
    ? Math.min(line, data.lines.length) - 1 : -1;
  const first = want >= 0 ? wordOfLine(want)
    : Math.max(0, data.at || 0);
  showPage(pageOfWord(first), true);
  text.addEventListener("click", (e) => {
    let s = e.target.closest(".w");
    const p = !s && e.target.closest("p.pl");
    if (p && text.contains(p) && e.detail > 0) {
      // a plain line: make its words, then see which
      // one is under the finger
      const sel = document.getSelection();
      if (sel && !sel.isCollapsed) return;
      expandLine(Number(p.dataset.l));
      s = document.elementFromPoint(e.clientX,
        e.clientY)?.closest(".w");
    }
    if (!s) return;
    const i = Number(s.dataset.i);
    if (i === R.sel) closePanel();
    else choose(i);
  });
  R.panel = h("aside", { class: "panel",
    "aria-label": t("r.word"), "aria-live": "polite" });
  R.panel.hidden = true;
  R.tools = h("div", { class: "tools" });
  // its height, for the panel beside the text
  // (--tools in style.css): it wraps and grows
  new ResizeObserver(() => {
    document.documentElement.style.setProperty(
      "--tools", R.tools.offsetHeight + "px");
  }).observe(R.tools);
  R.prog = h("div", { class: "readbar",
    role: "progressbar", "aria-label": t("r.read"),
    "aria-valuemin": "0", "aria-valuemax": "100" },
  h("span", { class: "track" }, h("span")));
  document.body.classList.add("reading");
  const pt = data.parts;
  // author and book, in small type above the bar
  const trail = pt
    ? pt.up.slice(1).map((u) => u.label).concat(pt.book)
    : (data.crumbs || []).slice(1).map((c) => c.label)
      .concat(data.label || title);
  R.who = h("div", { class: "readwho", lang: "hy" },
    trail.join(" · "));
  R.end = partEnd(pt);
  if (R.end && R.page < R.pages.length - 1) {
    R.end.style.display = "none";
  }
  show(pt ? upLinks(pt.up.concat([{ label: pt.book,
    to: folderHref(pt.folder) }]))
    : crumbs(name, false, data.crumbs),
  h("h1", { lang: data.label !== title ? "hy"
    : null }, pt
    ? pt.book + " · " + pt.n + "/" + pt.total
    : data.label || title),
    h("p", { class: "sub" },
      plural(data.lines.length, "line") + t("r.tap")),
    R.tools,
    h("div", { class: "reader" }, text, R.panel,
      R.end));
  decorate();
  // a link to a line: open exactly there; a search's
  // result: its words marked
  if (want >= 0 && R.found) {
    const i = foundWord(want);
    go(i);
    R.sel = i;
    mark(true);
  } else if (want >= 0) {
    go(wordOfLine(want));
  } else if (data.at > 0 && wordRect(data.at)) {
    // the first word: stay at the top, title shown
    const top = wordRect(data.at).top + window.scrollY;
    window.scrollTo(0, top - bar() - 16);
  }
  stick();
  progress();
  // from now on scrolling is saved
  R.name = name;
  R.title = title;
  // the first line, for the list of readings
  R.head = (data.lines[0] || []).join("").trim();
  // wide screen: the Contents open beside the text
  if (R.contents.length
    && matchMedia("(min-width: 64rem)").matches
    && document.documentElement.classList
      .contains("wide")) {
    const y = window.scrollY;
    showContents();
    window.scrollTo(0, y);
  }
  stir();
  savePos();
}

// -- editing interpretations --

// the text being edited
const E = {
  dirty: false, // changed since the last save
  hash: "", // the editor's page, to go back to
  back: false, // going back after "stay"
  save: null, // what Ctrl+S does
};

function leaveOk() {
  return !E.dirty ||
    confirm(t("ed.leave"));
}

window.addEventListener("beforeunload", (e) => {
  if (E.dirty) e.preventDefault();
});

document.addEventListener("keydown", (e) => {
  if (!E.save) return;
  if ((e.ctrlKey || e.metaKey) && e.key === "s") {
    e.preventDefault();
    E.save();
  }
});

function textBox(value, placeholder) {
  const box = h("textarea", { class: "editor",
    spellcheck: "true", placeholder,
    "aria-label": t("r.text") });
  box.value = value;
  // the size chosen with A− / A+ in the reader
  box.style.setProperty("--text-size",
    SIZES[view.size] + "rem");
  box.style.setProperty("--text-line",
    LINES[view.line]);
  box.addEventListener("input", () => {
    E.dirty = true;
  });
  return box;
}

function status() {
  return h("span", { class: "status",
    role: "status" });
}


async function edit(name) {
  const src = await api("source?name=" +
    encodeURIComponent(name));
  let ver = src.version;
  const title = name.split("/").pop();
  document.title = t("ed.edit", title) + " · " + NAME;
  const box = textBox(src.text);
  const msg = status();
  const reload = btn(t("ed.reload"), () => {
    if (!leaveOk()) return;
    E.dirty = false;
    route();
  });
  reload.hidden = true;
  async function save() {
    msg.className = "status";
    msg.textContent = t("ed.saving");
    try {
      const r = await send("save", { name,
        text: box.value, version: ver });
      ver = r.version;
      E.dirty = false;
      msg.textContent = t("ed.saved") +
        new Date().toLocaleTimeString([],
          { hour: "2-digit", minute: "2-digit" });
    } catch (e) {
      msg.className = "status error";
      msg.textContent = e.status === 409
        ? t("ed.changed") : t("ed.not") + e.message;
      reload.hidden = e.status !== 409;
    }
  }
  E.save = save;
  show(crumbs(name, false),
    h("h1", {}, t("ed.edit", title)),
    h("p", { class: "sub" }, t("ed.md")),
    box,
    h("div", { class: "actions" },
      btn(t("save"), save,
        { class: "icon-btn primary" }),
      h("a", { class: "icon-btn",
        href: "#/read/" + enc(name) }, t("ed.done")),
      reload, msg));
  box.focus({ preventScroll: true });
}

const TEXT_LANGS = {
  ru: "Русский",
  en: "English",
  hy: "Հայերեն",
};

async function newText(lang) {
  if (!TEXT_LANGS[lang]) lang = "ru";
  document.title = t("ed.new") + " · " + NAME;
  const file = h("input", { type: "text",
    class: "field", id: "file", autocomplete: "off",
    autocapitalize: "none", spellcheck: "false",
    placeholder: "ps-118-33-37-pustota-i-put" });
  const where = h("span", { class: "item-meta" });
  const langs = h("div", { class: "seg",
    role: "group", "aria-label": t("lang.pick") });
  const msg = status();
  function draw() {
    const f = file.value.trim() || "…";
    where.textContent = "interpretations/" + lang +
      "/" + f.replace(/\.md$/, "") + ".md";
    langs.replaceChildren(...Object.entries(TEXT_LANGS)
      .map(([l, label]) => btn(label, () => {
        lang = l;
        draw();
      }, { class: null, lang: l,
        "aria-pressed": String(l === lang) })));
  }
  file.addEventListener("input", () => {
    E.dirty = true;
    msg.textContent = "";
    draw();
  });
  draw();
  const box = textBox("", t("ed.title"));
  async function create() {
    msg.className = "status";
    msg.textContent = t("ed.saving");
    try {
      const r = await send("new", { lang,
        file: file.value.trim(), text: box.value });
      E.dirty = false;
      goTo("#/read/" + enc(r.name));
    } catch (e) {
      msg.className = "status error";
      msg.textContent = t("ed.not") + e.message;
    }
  }
  E.save = create;
  // the language folder may have no texts yet
  show(crumbs("interpretations/new", false),
    h("h1", {}, t("ed.new")),
    h("p", { class: "sub" }, t("ed.one") + t("ed.md")),
    h("div", { class: "form" },
      langs,
      h("label", { for: "file" }, t("ed.file")),
      file, where),
    box,
    h("div", { class: "actions" },
      btn(t("ed.create"), create,
        { class: "icon-btn primary" }),
      h("a", { class: "icon-btn",
        href: "#/f/interpretations" }, t("cancel")),
      msg));
  file.focus();
}

// -- pages --

function clearReading() {
  document.body.classList.remove("reading",
    "parallel", "full");
}

// -- search across the library (notes/search.md) --

// The index is nxgir_search.py's: /api/search gives
// a word's entry, {spelling: [[part, line, +line,
// ...]]}, or {"*": lines} for a word too common to
// search alone; /api/search-parts the parts, books
// and authors (in the Library's order); /api/lines
// 100 lines of a part, for the lines shown.

// the words of a search, as WORD_RE in the reader
const SEARCH_WORD = /\p{L}+(?:[՛՜՞՟'’]\p{L}*)*/gu;
// the texts a search shows: Grabar first
const SEARCH_IN = ["all", "grabar", "ashkharhabar"];
// their names, in LANG
function searchInName(w) {
  return w === "all" ? t("s.all") : t("shelf." + w);
}
// lines a book shows before "all its lines"
const SEARCH_FIRST = 2;
// lines a part's file holds (CHUNK in Python)
const SEARCH_CHUNK = 100;
// the last results, for ‹ › in the reader (this tab)
const FOUND = "nxgir-found";
const searchCache = new Map();
const lineFiles = new Map();
let searchParts = null;

function searchHref(q, where, open) {
  const p = new URLSearchParams({ q });
  if (where && where !== "grabar") p.set("in", where);
  if (open && open.size) {
    p.set("open", [...open].join(","));
  }
  return "#/search?" + p;
}

// 1 074: thousands apart, as in the mockups
function nf(n) {
  return String(n).replace(/\B(?=(\d{3})+$)/g, " ");
}

// the search box at the top of every page; it stays
// in view on scrolling (style.css)
function searchBox(value) {
  const input = h("input", { type: "search", name: "q",
    placeholder: t("s.box") + "…",
    "aria-label": t("s.box"),
    enterkeyhint: "search", autocomplete: "off",
    autocapitalize: "off", spellcheck: "false" });
  input.value = value || "";
  const clear = h("button", { type: "button",
    class: "sbox-x", "aria-label": t("clear"),
    title: t("clear") }, "✕");
  const showClear = () => {
    clear.hidden = !input.value;
  };
  showClear();
  input.addEventListener("input", showClear);
  clear.addEventListener("click", () => {
    input.value = "";
    showClear();
    input.focus();
  });
  const form = h("form", { class: "sbox",
    role: "search" },
  icon(ICONS.search), input, clear);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    input.blur();
    goTo(searchHref(q));
  });
  const wrap = h("div", { class: "search-wrap" }, form);
  stickBelow(wrap);
  return wrap;
}

// The height of what is stuck at the top: the top
// bar on the top page and the search box, as --stick;
// the Library's tabs and the reader's tools stick
// below it (style.css)
const stuckTop = new ResizeObserver(() => setStick());
let stuckBox = null;
function stickBelow(wrap) {
  if (stuckBox) stuckTop.unobserve(stuckBox);
  stuckBox = wrap;
  stuckTop.observe(wrap);
}
stuckTop.observe(topBar.parentNode);
function setStick() {
  const head = topBar.parentNode.offsetHeight;
  const root = document.documentElement.style;
  const home = document.body.classList.contains("home");
  root.setProperty("--head", head + "px");
  const box = stuckBox && stuckBox.isConnected
    ? stuckBox.offsetHeight : 0;
  root.setProperty("--stick",
    (home ? head : 0) + box + "px");
}

// a page's parts with the search box: under the menu
// buttons on the top page, else first; the results
// page has its own
function withSearch(kids) {
  kids = kids.filter((k) => k != null);
  requestAnimationFrame(setStick);
  // not in the reader: its tools are at the top, and
  // a word or a selection is searched from there
  // (searchWordButton(), selection button)
  if (document.body.classList.contains("reading")) {
    return kids;
  }
  if (kids.some((k) => k.classList
    && k.classList.contains("search-wrap"))) {
    return kids;
  }
  const box = searchBox("");
  const at = kids.findIndex((k) => k.classList
    && k.classList.contains("menu-bar"));
  kids.splice(at + 1, 0, box);
  return kids;
}

async function searchEntry(w) {
  const k = loose(w);
  if (!searchCache.has(k)) {
    searchCache.set(k, api("search?w="
      + encodeURIComponent(w)).catch((e) => {
      searchCache.delete(k);
      throw e;
    }));
  }
  return searchCache.get(k);
}

async function partsOf() {
  if (!searchParts) {
    searchParts = api("search-parts").catch((e) => {
      searchParts = null;
      throw e;
    });
  }
  return searchParts;
}

// line n (1-based) of a part, from its file of 100
async function lineText(name, n) {
  const k = Math.floor((n - 1) / SEARCH_CHUNK);
  const id = name + "|" + k;
  if (!lineFiles.has(id)) {
    lineFiles.set(id, api("lines?name="
      + encodeURIComponent(name) + "&k=" + k)
      .catch((e) => {
        lineFiles.delete(id);
        throw e;
      }));
  }
  const data = await lineFiles.get(id);
  return data.lines[(n - 1) % SEARCH_CHUNK] || "";
}

// {"part:line": [spelling, ...]} of an entry
function linesOf(entry) {
  const out = new Map();
  for (const [s, rows] of Object.entries(entry)) {
    for (const [p, ...ns] of rows) {
      let n = 0;
      ns.forEach((d, i) => {
        n = i ? n + d : d;
        const id = p + ":" + n;
        if (!out.has(id)) out.set(id, []);
        out.get(id).push(s);
      });
    }
  }
  return out;
}

// The lines of a search: those with all its words
// (each in either spelling). A word too common to
// search alone is left out when there are others.
async function findLines(q) {
  const words = [...new Set(q.match(SEARCH_WORD)
    || [])];
  const found = await Promise.all(
    words.map(searchEntry));
  const common = [];
  const used = [];
  found.forEach((f, i) => {
    if (f.entry && f.entry["*"]) {
      common.push([words[i], f.entry["*"]]);
    } else {
      used.push([words[i], f]);
    }
  });
  let lines = null;
  const spelled = [];
  for (const [w, f] of used) {
    const got = f.entry ? linesOf(f.entry) : new Map();
    spelled.push([w, f.key, got]);
    if (lines === null) {
      lines = new Set(got.keys());
    } else {
      lines = new Set([...lines].filter((id) =>
        got.has(id)));
    }
  }
  return { words, common, spelled,
    keys: new Set(spelled.map((x) => x[1])),
    lines: lines ? [...lines] : [] };
}

// the lines of a search, by author and book, in the
// Library's order; in a book the Grabar lines first
function grouped(parts, ids, where) {
  let hits = [];
  for (const id of ids) {
    const [p, line] = id.split(":").map(Number);
    const [name, b, n] = parts.parts[p];
    const top = name.split("/")[0];
    if (where !== "all" && top !== where) continue;
    hits.push({ id, ids: [id], name, top, b, n, line,
      a: parts.books[b][2] });
  }
  if (where === "all") hits = paired(hits, parts);
  const tops = { grabar: 0, ashkharhabar: 1 };
  hits.sort((x, y) => x.a - y.a || x.b - y.b
    || tops[x.top] - tops[y.top] || x.n - y.n
    || x.line - y.line);
  const authors = [];
  for (const x of hits) {
    let a = authors[authors.length - 1];
    if (!a || a.a !== x.a) {
      a = { a: x.a, books: [], lines: 0 };
      authors.push(a);
    }
    let bk = a.books[a.books.length - 1];
    if (!bk || bk.b !== x.b) {
      bk = { b: x.b, hits: [] };
      a.books.push(bk);
    }
    bk.hits.push(x);
    a.lines++;
  }
  return { hits, authors };
}

// A Grabar line and its translation (the same line
// of the same part in ashkharhabar/) as one result:
// the Grabar line, and under it its translation,
// whichever of the two has the word
function paired(hits, parts) {
  if (!parts.names) {
    parts.names = new Set(parts.parts.map((x) => x[0]));
  }
  const by = new Map();
  for (const x of hits) {
    const rest = x.name.slice(x.name.indexOf("/") + 1);
    const k = rest + ":" + x.line;
    const g = "grabar/" + rest;
    const t = "ashkharhabar/" + rest;
    const y = by.get(k);
    if (y) {
      y.ids.push(x.id);
      continue;
    }
    const main = parts.names.has(g) ? g : x.name;
    by.set(k, { ...x, id: k, name: main,
      top: main.split("/")[0],
      pair: main !== t && parts.names.has(t) ? t
        : null });
  }
  return [...by.values()];
}

// the line, the words searched marked, cut around
// the first of them (a line without them: its start)
function hitSnippet(text, keys) {
  const marks = [];
  for (const m of text.matchAll(SEARCH_WORD)) {
    if (keys.has(loose(m[0]))) {
      marks.push([m.index, m.index + m[0].length]);
    }
  }
  let a = 0;
  let b = text.length;
  if (marks.length) {
    a = Math.max(0, marks[0][0] - 40);
    b = Math.min(text.length, marks[0][1] + 100);
    if (a > 0) a = text.indexOf(" ", a) + 1 || a;
    if (b < text.length) {
      b = text.lastIndexOf(" ", b);
      if (b <= marks[0][1]) b = marks[0][1];
    }
  } else if (b > 140) {
    b = text.lastIndexOf(" ", 140);
    if (b < 1) b = 140;
  }
  const out = [a > 0 ? "… " : ""];
  let at = a;
  for (const [x, y] of marks) {
    if (x < a || y > b) continue;
    out.push(text.slice(at, x),
      h("mark", {}, text.slice(x, y)));
    at = y;
  }
  out.push(text.slice(at, b), b < text.length
    ? " …" : "");
  return out;
}

// fill the lines of the results as they come into
// view
const snippetsSeen = new IntersectionObserver(
  (entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      snippetsSeen.unobserve(e.target);
      const el = e.target;
      lineText(el.dataset.name, Number(el.dataset.line))
        .then((t) => el.replaceChildren(
          ...hitSnippet(t, el.keys)))
        .catch(() => el.replaceChildren("…"));
    }
  }, { rootMargin: "200px" });

function hitHref(q, name, line, r) {
  return "#/read/" + enc(name) + "?" + new
  URLSearchParams({ line, q, r });
}

// one line found: where it is and its text
function hitItem(x, i, ctx) {
  const parts = ctx.parts.books[x.b][3] > 1;
  const where = t("s.where", parts ? x.n : 0,
    x.line);
  const line = (name, cls) => {
    const snip = h("span", { class: cls,
      lang: "hy" }, "…");
    snip.dataset.name = name;
    snip.dataset.line = x.line;
    snip.keys = ctx.keys;
    snippetsSeen.observe(snip);
    return snip;
  };
  // under Բոլորը a Grabar line with its translation
  // is one result; a line alone says which it is
  const tag = ctx.where === "all" && !x.pair
    && x.top !== "grabar";
  return h("li", {}, h("a", {
    href: hitHref(ctx.q, x.name, x.line, i) },
  h("span", { class: "where" },
    tag ? h("span", { class: "chip" },
      searchInName(x.top)) : null, where),
  line(x.name, "snip"),
  x.pair ? line(x.pair, "snip tr") : null));
}

function bookHref(key) {
  return /\.(txt|md)$/.test(key)
    ? "#/read/grabar/" + enc(key)
    : "#/b/grabar/" + enc(key);
}

// an author's books and their lines
function authorBooks(a, ctx) {
  const box = h("div", { class: "s-in" });
  for (const bk of a.books) {
    const [key, title] = ctx.parts.books[bk.b];
    const list = h("ul", { class: "s-hits" });
    const shown = (n) => {
      list.replaceChildren(...bk.hits.slice(0, n)
        .map((x) => hitItem(x, ctx.index.get(x.id),
          ctx)));
    };
    shown(SEARCH_FIRST);
    const all = bk.hits.length > SEARCH_FIRST
      ? btn(t("s.alllines", bk.hits.length), () => {
        shown(bk.hits.length);
        all.remove();
      }, { class: "s-all" }) : null;
    box.append(h("a", { class: "s-book",
      href: bookHref(key) },
    h("span", { lang: "hy" }, title),
    h("span", { class: "meta" },
      t("s.lines", bk.hits.length))), list);
    // append() would show a null as "null"
    if (all) box.append(all);
  }
  return box;
}

// a test of a name: has it every word of q, as the
// start of one of its words, in either spelling
function nameFits(q) {
  const want = q.split(/\s+/).map(loose)
    .filter(Boolean);
  return (name) => {
    const ws = String(name || "")
      .split(/[\s,.()-]+/).map(loose);
    return want.every((w) =>
      ws.some((x) => x.startsWith(w)));
  };
}

// authors and books whose name has every word of
// q (as the start of one of its words), in either
// spelling; an author also by its English and
// Russian names (names: /api/authors), shown as
// "also"; a book also by the titles of its card
// (titles: /api/authors), shown the same way
function nameHits(q, parts, names, titles = {}) {
  const fits = nameFits(q);
  const authors = [];
  parts.authors.forEach(([id, name], i) => {
    if (fits(name)) {
      authors.push({ id, name, i });
      return;
    }
    const other = Object.entries(names[id] || {})
      .find(([l, n]) => l !== "hy" && fits(n));
    if (other) {
      authors.push({ id, name, i, also: other[1] });
    }
  });
  // a book also by its co-authors' names
  const coFits = ([id, name]) => fits(name)
    || Object.values(names[id] || {}).some(fits);
  const co = parts.with || {};
  // a co-author has no folder: a row of its own, to
  // its first book (bi), with the books it is in
  const seen = new Set(authors.map((a) => a.id));
  for (const [bi, list] of Object.entries(co)) {
    for (const c of list) {
      if (seen.has(c[0]) || !coFits(c)) continue;
      seen.add(c[0]);
      const also = Object.entries(names[c[0]] || {})
        .find(([l, n]) => l !== "hy" && fits(n));
      authors.push({ id: c[0], name: c[1],
        bi: Number(bi), co: true,
        also: also && !fits(c[1]) ? also[1] : "",
        n: Object.values(co).filter((l) =>
          l.some((x) => x[0] === c[0])).length });
    }
  }
  const books = parts.books
    .map(([key, name, ai], i) => ({ key, name, ai,
      co: co[i] || [] }))
    .filter((b) => {
      if (fits(b.name) || b.co.some(coFits)) {
        return true;
      }
      const t = Object.entries(titles[b.key] || {})
        .find(([l, n]) => l !== "hy" && fits(n));
      if (t) b.also = t[1];
      return !!t;
    });
  return { authors, books };
}

// the names found, above the lines
function nameList(q, parts, names, titles) {
  const { authors, books } = nameHits(q, parts,
    names, titles);
  if (!authors.length && !books.length) return null;
  const n = (ai) => parts.books
    .filter((b) => b[2] === ai).length;
  const list = h("ul", { class: "shelf s-names" });
  for (const a of authors) {
    const to = a.co ? bookHref(parts.books[a.bi][0])
      : "#/library/" + enc(a.id);
    list.append(h("li", {}, h("a", { class: "row",
      href: to },
    icon(ICONS.person, "ico"),
    h("span", { class: "name", lang: "hy" }, a.name,
      a.also ? h("span", { class: "by" }, a.also)
        : null),
    h("span", { class: "meta" },
      t("s.books", a.co ? a.n : n(a.i)))),
    authorInfoBtn(a.id, a.name)));
  }
  const rows = books.map((b) => h("li", {},
    h("a", { class: "row", href: bookHref(b.key) },
      icon(ICONS.book, "ico"),
      h("span", { class: "name", lang: "hy" }, b.name,
        h("span", { class: "by" },
          (b.also ? [b.also] : []).concat(
            b.co.map((c) => c[1]),
            [parts.authors[b.ai][1]]).join(" · "))))));
  // a common title (Պատմութիւն Հայոց): the first
  // few, and a button for the rest
  const FEW = 5;
  list.append(...rows.slice(0, FEW));
  const more = rows.length > FEW ? btn(
    t("s.allbooks", rows.length), () => {
    list.append(...rows.slice(FEW));
    more.remove();
  }, { class: "link-btn s-names-more" }) : null;
  return h("section", {},
    h("h2", { class: "s-head2" }, t("s.names")),
    list, more);
}

async function searchPage(query) {
  const p = new URLSearchParams(query);
  const q = (p.get("q") || "").trim();
  const where = SEARCH_IN.includes(p.get("in"))
    ? p.get("in") : "grabar";
  const open = new Set((p.get("open") || "")
    .split(",").filter(Boolean));
  document.title = (q ? q + " · " : "")
    + t("nav.search") + " · " + NAME;
  const head = [
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, t("home"))),
    h("h1", {}, t("nav.search")),
    withHome(searchBox(q)),
  ];
  const say = (...x) => show(...head,
    h("p", { class: "sub" }, ...x));
  if (!q.match(SEARCH_WORD)) {
    say(t("s.hint"));
    return;
  }
  // the first search of `nxgir web` waits for its
  // index
  say(t("s.wait"));
  const at = hashNow();
  const [parts, f, about] = await Promise.all([
    partsOf(), findLines(q), authorsAbout()]);
  // gone to another page meanwhile
  if (hashNow() !== at) return;
  // how many parts each book has, for "մաս n"
  for (const b of parts.books) b[3] = 0;
  const seen = new Set();
  for (const [name, b] of parts.parts) {
    const k = b + ":" + name.split("/").pop();
    if (!seen.has(k)) parts.books[b][3]++;
    seen.add(k);
  }
  const counts = {};
  for (const w of SEARCH_IN) {
    counts[w] = grouped(parts, f.lines, w).hits.length;
  }
  const g = grouped(parts, f.lines, where);
  // the list in the order shown, for the reader
  const index = new Map(g.hits.map((x, i) =>
    [x.id, i]));
  const remember = () => {
    try {
      sessionStorage.setItem(FOUND, JSON.stringify({
        q, back: searchHref(q, where, open),
        list: g.hits.map((x) => [x.name, x.line]) }));
    } catch (e) {}
  };
  const ctx = { q, where, parts, index,
    keys: f.keys };
  const names = nameList(q, parts, about.names,
    about.titles);
  const common = f.common.length ? h("p",
    { class: "hint" },
    f.common.map(([w, n]) => w + " ("
      + t("s.lines", n) + ")").join(", "),
    f.spelled.length ? t("s.common")
      : t("s.common1")) : null;
  // a name found and no line: the names alone
  const none = SEARCH_IN.every((w) => !counts[w]);
  if (!f.spelled.length || (names && none)) {
    show(...head, names, common);
    return;
  }
  const filters = h("div", { class: "filters" },
    ...SEARCH_IN.map((w) =>
      h("a", { href: searchHref(q, w),
        "aria-current": w === where ? "page" : null },
      searchInName(w) + " · " + nf(counts[w]))));
  // each spelling found, and in how many lines; for
  // the words found in more than one
  const spells = new Map();
  for (const [, , got] of f.spelled) {
    const one = new Map();
    for (const x of g.hits) {
      const here = new Set(x.ids.flatMap((id) =>
        got.get(id) || []));
      for (const s of here) {
        one.set(s, (one.get(s) || 0) + 1);
      }
    }
    if (one.size > 1) {
      for (const [s, n] of one) spells.set(s, n);
    }
  }
  const spelling = spells.size ? h("p",
    { class: "s-opts" },
    h("span", {}, t("s.spelled")),
    ...[...spells].sort((x, y) => y[1] - x[1])
      .map(([s, n]) => h("span", { class: "chip" },
        h("b", {}, s), " " + nf(n)))) : null;
  const nb = g.authors.reduce((n, a) =>
    n + a.books.length, 0);
  const all = g.authors.length > 1 && btn(
    t("s.open"), () => {
      const on = open.size < g.authors.length;
      for (const a of g.authors) {
        const id = parts.authors[a.a][0];
        if (on) open.add(id);
        else open.delete(id);
      }
      draw();
    }, { class: "link-btn s-open" });
  const list = h("ul", { class: "s-authors" });
  // an author folded or not, in the address too, so
  // that back from the reader finds it the same
  const draw = () => {
    history.replaceState(history.state, "",
      pathOf(searchHref(q, where, open)));
    remember();
    if (all) {
      all.textContent = open.size >= g.authors.length
        ? t("s.close") : t("s.open");
    }
    list.replaceChildren(...g.authors.map((a) => {
      const [id, name] = parts.authors[a.a];
      const on = open.has(id) || g.authors.length === 1;
      const row = h("button", { type: "button",
        class: "s-auth", "aria-expanded": String(on) },
      icon(ICONS.fold, "chev"),
      h("span", { class: "s-name", lang: "hy" },
        name),
      h("span", { class: "meta" }, t("s.lines", a.lines)
        + (a.books.length > 1 ? " · "
          + t("s.books", a.books.length) : "")));
      row.addEventListener("click", () => {
        if (open.has(id)) open.delete(id);
        else open.add(id);
        draw();
      });
      return h("li", { class: on ? "on" : null },
        h("div", { class: "s-head" }, row,
          authorInfoBtn(id, name)),
        on ? authorBooks(a, ctx) : null);
    }));
  };
  draw();
  show(...head, names,
    names ? h("h2", { class: "s-head2" },
      t("s.found")) : null,
    h("p", { class: "s-sum" },
      h("span", {}, t("s.lines", g.hits.length)
        + " · " + t("s.authors", g.authors.length)
        + " · " + t("s.books", nb)), all || null),
    filters, spelling, common,
    g.hits.length ? list : h("p", { class: "sub" },
      f.lines.length ? t("s.notin") : t("s.none")));
}

// -- searching the library from the reader --

// in the word panel: the word in the whole library,
// with how many Grabar lines have it
function searchWordButton(w) {
  const n = h("span", { class: "n" });
  const a = h("a", { class: "s-btn",
    href: searchHref(w) }, icon(ICONS.search),
  t("s.library"), n);
  Promise.all([partsOf(), searchEntry(w)])
    .then(([parts, f]) => {
      if (!f.entry || f.entry["*"]) return;
      let k = 0;
      for (const id of linesOf(f.entry).keys()) {
        const p = Number(id.split(":")[0]);
        if (parts.parts[p][0].startsWith("grabar/")) k++;
      }
      if (k) n.textContent = " · " + nf(k);
    }).catch(() => {});
  return a;
}

// text selected in the reader (a long press, or a
// drag over the words): a button at the bottom of
// the screen searches its words in the library
const selSearch = h("a", { class: "sel-search",
  hidden: "" });
document.body.append(selSearch);
// at most this many words: a few words, not a page
const SEL_WORDS = 6;
let selTimer = 0;
document.addEventListener("selectionchange", () => {
  clearTimeout(selTimer);
  selTimer = setTimeout(() => {
    const sel = document.getSelection();
    const text = sel && !sel.isCollapsed
      ? sel.toString() : "";
    const words = text.match(SEARCH_WORD) || [];
    const inText = R.text && R.text.isConnected
      && sel.rangeCount
      && R.text.contains(sel.getRangeAt(0)
        .commonAncestorContainer);
    if (!inText || !words.length
      || words.length > SEL_WORDS) {
      selSearch.hidden = true;
      return;
    }
    const q = words.join(" ");
    setRoute(selSearch, searchHref(q));
    selSearch.replaceChildren(icon(ICONS.search),
      h("span", {}, t("s.sel"),
        h("b", { lang: "hy" }, q)));
    selSearch.hidden = false;
  }, 250);
});
selSearch.addEventListener("click", () => {
  selSearch.hidden = true;
});
window.addEventListener("navigate", () => {
  selSearch.hidden = true;
});

// -- a result in the reader: the words marked, and
// ‹ › to the results before and after it --

// R.found from #/read/...?q=&r=: the search, this
// result's number and the list, if this tab has it
function foundOf(q, r, name, line) {
  if (!q) return null;
  const f = { q, r: -1, list: null,
    back: searchHref(q),
    keys: new Set((q.match(SEARCH_WORD) || [])
      .map(loose)) };
  try {
    const s = JSON.parse(sessionStorage.getItem(FOUND)
      || "null");
    const x = s && s.q === q && s.list[r];
    if (x && x[0] === name && x[1] === line) {
      Object.assign(f, { r, list: s.list,
        back: s.back });
    }
  } catch (e) {}
  return f;
}

// the word searched on a line, or its first word
function foundWord(line) {
  R.refs = [];
  R.keys.forEach((k, j) => {
    if (R.found.keys.has(loose(k))) R.refs.push(j);
  });
  const i = R.refs.find((j) => R.wpos[j][0] === line);
  return i === undefined ? wordOfLine(line) : i;
}

// in the reader's tools: back to the results, and
// the result before and after
function foundStrip() {
  const f = R.found;
  const n = f.list ? f.list.length : 0;
  const to = (k, sign, label) => {
    const x = n && f.list[k];
    return x ? h("a", { class: "icon-btn",
      href: hitHref(f.q, x[0], x[1], k),
      "aria-label": label, title: label }, sign)
      : h("span", { class: "icon-btn off",
        "aria-hidden": "true" }, sign);
  };
  return h("div", { class: "found" },
    h("a", { class: "icon-btn", href: f.back,
      "aria-label": t("s.back"),
      title: t("s.back") }, icon(ICONS.back)),
    h("span", { class: "t" }, t("s.q"),
      h("b", { lang: "hy" }, f.q), n ? h("br") : null,
      n ? t("s.nth", f.r + 1, n) : null),
    n ? to(f.r - 1, "‹", t("prev")) : null,
    n ? to(f.r + 1, "›", t("next")) : null);
}

async function route() {
  clearTimeout(placeTimer);
  // unsaved text: ask before leaving the editor
  if (E.back) {
    E.back = false;
    return;
  }
  if (E.hash && hashNow() !== E.hash) {
    if (!leaveOk()) {
      E.back = true;
      goTo(E.hash);
      return;
    }
  }
  E.dirty = false;
  E.save = null;
  E.hash = "";
  followLang();
  const hash = hashNow().replace(/^#\/?/, "");
  markTab(hash);
  if (shownHash !== null) {
    rememberTab(shownHash, window.scrollY);
  }
  shownHash = hash;
  document.body.classList.remove("peek");
  if (R.timer) savePos(true);
  R.name = "";
  closePanel();
  R.panel = null;
  R.par = null;
  // going to another part keeps the reading layout,
  // or the page would narrow and widen while it loads
  if (!hash.startsWith("read/")) clearReading();
  document.body.classList.remove("home");
  // back to the top bar from the reading tools
  // (in its place: before the language globe)
  if (button.parentNode !== topBar) {
    topBar.insertBefore(button,
      topBar.querySelector(".lang-globe"));
  }
  try {
    if (hash.startsWith("read/")) {
      // #/read/<book>?line=N opens at line N; with
      // q=, a search's result (r= its number)
      const [path, query] = hash.split("?");
      const p = new URLSearchParams(query);
      const line = Number(p.get("line"));
      const name = decodeURIComponent(path.slice(5));
      await book(name, line, foundOf(p.get("q"),
        Number(p.get("r")), name, line));
    } else if (hash.startsWith("edit/")) {
      E.hash = hashNow();
      await edit(decodeURIComponent(hash.slice(5)));
    } else if (hash.startsWith("new/")) {
      E.hash = hashNow();
      await newText(hash.slice(4));
    } else if (hash === "search"
      || hash.startsWith("search?")) {
      await searchPage(hash.slice(7));
    } else if (hash === "timeline") {
      await timelinePage();
    } else if (hash === "blog"
      || hash.startsWith("blog/")) {
      await blogPage(decodeURIComponent(
        hash.slice(5)));
    } else if (hash === "comics"
      || hash.startsWith("comics/")) {
      await comicsPage(decodeURIComponent(
        hash.slice(7)));
    } else if (hash === "map"
      || hash.startsWith("map/")) {
      await mapPage(decodeURIComponent(hash.slice(4)));
    } else if (hash === "features"
      || hash.startsWith("features/")) {
      await featuresPage(hash.slice(9));
    } else if (hash === "reference") {
      await referencePage();
    } else if (hash === "contribute") {
      contributePage();
    } else if (hash === "news"
      || hash.startsWith("news/")) {
      newsPage(decodeURIComponent(hash.slice(5)));
    } else if (hash === "stats") {
      await statsPage();
    } else if (hash === "offline") {
      await offlinePage();
    } else if (hash === "recent") {
      await recentPage();
    } else if (hash === "library"
      || hash.startsWith("library/")) {
      await libraryPage(decodeURIComponent(
        hash.slice(8)));
    } else if (hash.startsWith("b/")) {
      await bookPage(decodeURIComponent(hash.slice(2)));
    } else if (hash.startsWith("f/")) {
      await shelf(decodeURIComponent(hash.slice(2)));
    } else {
      await shelf("");
    }
    backToPlace(hash);
    visit("/" + LANG + "/" + decodeURIComponent(hash));
  } catch (e) {
    clearReading();
    showError(e.message || t("error"));
  }
}

// Back (the phone's back button too) returns to the
// place on the page left: each history entry keeps its
// scroll, written as the page scrolls; a new page has
// none and starts at the top. The reader keeps its own
// place (savePos), so not for read/.
if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}

function reading(hash) {
  return hash.startsWith("read/");
}

let placeTimer = 0;
window.addEventListener("scroll", () => {
  clearTimeout(placeTimer);
  placeTimer = setTimeout(() => {
    const hash = hashNow().replace(/^#\/?/, "");
    if (reading(hash)) return;
    history.replaceState(
      { ...(history.state || {}), y: window.scrollY },
      "");
    rememberTab(hash, window.scrollY);
  }, 150);
}, { passive: true });

function backToPlace(hash) {
  const y = restoreY
    || (history.state && history.state.y);
  restoreY = 0;
  if (!reading(hash) && y) window.scrollTo(0, y);
}

window.addEventListener("navigate", route);
drawTheme();
drawView();
route();
startWorker();
