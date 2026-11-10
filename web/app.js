// nx-gir web: the bookshelf and the theme button.
// Pages are #/ (top), #/f/<folder>, #/read/<book>,
// #/library, #/timeline, #/blog, #/features and
// #/stats; the
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
    else el.setAttribute(k, v);
  }
  el.append(...kids.flat().filter((k) => k != null));
  return el;
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
  folder: [
    "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8" +
      "a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  ],
  book: [
    "M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z",
    "M5 18a2 2 0 0 1 2-2h11",
  ],
  // a pen: the blog
  pen: [
    "M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z",
    "M13.5 6.5l4 4",
  ],
  // a ticked box: the features
  tick: [
    "M5 4h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5" +
      "a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z",
    "M8 12l3 3l5-6",
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
};

// 512 B, 3.4 KB: like human_size() in Python.
function size(n) {
  if (n < 1024) return n + " B";
  n /= 1024;
  if (n < 1024) return n.toFixed(1) + " KB";
  return (n / 1024).toFixed(1) + " MB";
}

function plural(n, word) {
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
// build-site.py has a code): the page and its title,
// where the visitor came from and the screen width;
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
  if (route === "recent") {
    return { items: await recentHere(
      Number(q.get("n")) || 0) };
  }
  if (route === "stats") {
    return json("data/stats.json");
  }
  if (route === "library") {
    return json("data/library.json");
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
  throw new Error("Not in the published copy");
}

// the top page's title, as in index.html: what
// search results show
const TOP_TITLE =
  "Նախագիր · Գրաբար · Grabar books, word by word";

function enc(name) {
  return name.split("/").map(encodeURIComponent)
    .join("/");
}

function show(...kids) {
  // (replaceChildren would write null as "null")
  main.replaceChildren(
    ...kids.filter((k) => k != null), siteFooter());
  window.scrollTo(0, 0);
}

// the bottom of every page: the main pages, the
// license, how to help and who made it
const REPO = "https://github.com/serjhnn/nx-gir";
const BY_SA = "https://creativecommons.org/"
  + "licenses/by-sa/4.0/";

function siteFooter() {
  const pages = [["#/library", "Library"],
    ["#/blog", "Blog"], ["#/features", "Features"],
    ["#/timeline", "Timeline"],
    ["#/stats", "Statistics"],
    ["#/recent", "Readings"]];
  return h("footer", { class: "site-foot" },
    h("p", { class: "foot-name" },
      h("span", { lang: "hy" }, "Նախագիր"),
      " (", named("nxGir"), ")"),
    h("nav", { "aria-label": "Pages" },
      pages.flatMap(([to, label], i) => [
        i ? " · " : null,
        h("a", { href: to }, label)])),
    h("p", {}, "Translations ",
      h("a", { href: BY_SA, rel: "license" },
        "CC BY-SA 4.0"),
      " · Grabar texts in the public domain"),
    h("p", {},
      h("a", { href: REPO + "/blob/main/"
        + "CONTRIBUTING.md" },
      "Help review the translations"),
      " · ",
      h("a", { href: REPO }, "GitHub")),
    h("p", {}, "Developed by S.O. and Claude"));
}

// an error, and under it what the site is: a
// search engine that hits an error quotes that,
// not the error (data-nosnippet)
function showError(msg) {
  show(
    h("p", { class: "error", "data-nosnippet": "" },
      msg + ". ",
      h("a", { href: "#/" }, "Back to the library")),
    ABOUT
  );
}

// Library / grabar / bible: links up the folders.
function crumbs(path, last) {
  const nav = h("nav", { class: "crumbs",
    "aria-label": "Folders" });
  const parts = path ? path.split("/") : [];
  if (!last) parts.pop();
  nav.append(h("a", { href: "#/" }, "Library"));
  parts.forEach((p, i) => {
    const to = parts.slice(0, i + 1).join("/");
    nav.append(h("span", { class: "sep" }, "/"),
      h("a", { href: "#/f/" + enc(to) }, p));
  });
  return nav;
}

// -- theme --

const button = document.getElementById("theme");
const topBar = button.parentNode;

// light, dark, black, and around again
const THEMES = ["light", "dark", "black"];
const THEME_NAMES = {
  light: "Light", dark: "Dark", black: "Black" };
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
  const t = theme();
  const other = nextTheme(t);
  button.replaceChildren(
    icon(ICONS[THEME_ICONS[t]]));
  button.title = "Theme: " + THEME_NAMES[t] +
    " (click for " +
    THEME_NAMES[other].toLowerCase() + ")";
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
  viewBtn.title = on ? "Phone view: on (click for"
    + " the wide view)" : "Phone view";
  viewBtn.setAttribute("aria-label", "Phone view");
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
      role: "img", "aria-label": pct + "% read" },
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
    href: "#/f/" + enc(item.name) },
  icon(ICONS.folder, "ico"),
  h("span", { class: "name" },
    item.label.replace(/\/$/, "")),
  h("span", { class: "meta" },
    plural(item.size, item.unit || "book")));
}

// where a first-time visitor starts: Grabar and
// its modern Armenian translation side by side
const START = "grabar/grigor-tatevatsi/" +
  "3-amaran-hator/01.txt";
// the books whose translation the welcome shows;
// the others wait for a page of their own
const FRONT = "grabar/grigor-tatevatsi/";

// where visitors can write: kept in parts and put
// together only in the page, so that programs
// gathering addresses from the files do not find it
const CONTACT = ["serj.hnn13", "gmail.com"];

// the welcome above the library, in Armenian:
// questions a first-time visitor may ask
function intro(status, news) {
  status = (status || []).filter(
    (b) => b.folder.startsWith(FRONT));
  const qa = (q, ...a) => [h("h3", {}, q),
    h("p", {}, ...a)];
  return h("section", { class: "intro", lang: "hy" },
    h("h2", {}, "Ողջույն"),
    qa("Ինչի՞ համար է կայքը։",
      "Այստեղ կարող եք կարդալ գրաբարով՝ դասական "
      + "հայերենով գրված գրքեր։"),
    qa("Ինչպե՞ս իմանալ բառի իմաստը։",
      "Սեղմեք բառի վրա, և կտեսնեք դրա իմաստը, "
      + "բառարանային ձևը և այն մյուս տեղերը, "
      + "որտեղ բառը հանդիպում է գրքում։"),
    qa("Որտեղի՞ց սկսել։",
      "Բացեք Գրիգոր Տաթևացու «Ամառան հատորի» "
      + "առաջին մասը. գրաբար բնագիրն այնտեղ "
      + "ժամանակակից հայերեն թարգմանության հետ "
      + "կողք կողքի է, ամեն նախադասությունը՝ "
      + "առանձին տողում։"),
    h("p", { class: "intro-btn" },
      h("a", { class: "icon-btn primary",
        href: "#/read/" + enc(START) },
      "Կարդալ «Ամառան հատոր», մաս 1 →")),
    status.length ? [
      h("h3", {}, "Ի՞նչ է արդեն թարգմանված։"),
      statusList(status)] : null,
    news && news.length ? [
      h("h3", {},
        "Ի՞նչ փոփոխություններ կան կայքում։"),
      newsList(news),
      h("p", { class: "more" },
        h("a", { href: "#/timeline" },
          "All events → Timeline"))] : null,
    qa("Ո՞վ է թարգմանել։",
      "Թարգմանությունը մեքենայական է և դեռ "
      + "ստուգված չէ մասնագետի կողմից։"),
    qa("Ինչպե՞ս կապվել։",
      "Հարցերի, առաջարկների կամ սխալների մասին "
      + "գրեք նախագծի հեղինակին՝ ", mail(), "։"));
}

// the long books and how many of their parts
// have a translation (status() in nxgir_web.py)
function statusList(status) {
  const list = h("ul", { class: "status" });
  for (const b of status) {
    const pct = Math.round(100 * b.done / b.parts);
    const fill = h("span");
    fill.style.width = pct + "%";
    const to = b.first ? "#/read/" + enc(b.first)
      : "#/f/" + enc(b.folder);
    list.append(h("li", {},
      h("a", { href: to }, b.title),
      h("span", { class: "meta" },
        b.done + " / " + b.parts + " մաս"),
      h("span", { class: "progress", role: "img",
        "aria-label": pct + "%" }, fill)));
  }
  return list;
}

// the newest steps of the timeline, in English
// for now (timeline.tsv)
function newsList(news) {
  const list = h("ul", { class: "news",
    lang: "en" });
  for (const e of news) {
    const to = eventHref(e);
    list.append(h("li", {},
      h("time", { datetime: e.date },
        day(e.date)),
      h("div", {},
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

async function shelf(folder) {
  const q = encodeURIComponent(folder);
  const [data, last] = await Promise.all([
    api("shelf?folder=" + q),
    folder ? null : api("recent?n=" + RECENT)
      .catch(() => null)]);
  const title = folder
    ? folder.split("/").pop() : "Library";
  document.title = folder
    ? title + " · Նախագիր" : TOP_TITLE;
  const list = h("ul", { class: "shelf" });
  for (const item of data.items) {
    list.append(h("li", {}, item.folder
      ? folderRow(item) : bookRow(item)));
  }
  const lang = folder.split("/")[1];
  show(
    folder ? crumbs(folder, false) : null,
    // at the top: the Library button, what was
    // read last, then the welcome
    folder ? null : h("p", { class: "lib-btn",
      lang: "hy" },
    h("a", { class: "icon-btn",
      href: "#/library" },
    icon(ICONS.book), "Գրադարան"),
    h("a", { class: "icon-btn",
      href: "#/blog" },
    icon(ICONS.pen), "Բլոգ"),
    h("a", { class: "icon-btn",
      href: "#/features" },
    icon(ICONS.tick), "Հնարավորություններ")),
    last && last.items.length
      ? recentCard(last.items) : null,
    folder ? null : intro(data.status, data.news),
    h("h1", {}, title),
    h("p", { class: "sub" }, plural(data.count,
      data.unit)),
    data.editable ? h("div", { class: "actions" },
      h("a", { class: "icon-btn",
        href: "#/new/" + (lang || "ru") },
      "+ New text")) : null,
    data.items.length ? list
      : h("p", { class: "empty" }, "No books here.")
  );
}

// -- readings --

// how many of the books read last the top page
// shows; #/recent shows them all
const RECENT = 3;

// "seen" (seconds) as Armenian "how long ago"
function ago(seen) {
  if (!seen) return "";
  const s = Date.now() / 1000 - seen;
  const n = (k) => Math.max(1, Math.floor(s / k));
  if (s < 60) return "հենց նոր";
  if (s < 3600) return n(60) + " րոպե առաջ";
  if (s < 86400) return n(3600) + " ժամ առաջ";
  if (s < 2 * 86400) return "երեկ";
  if (s < 30 * 86400) return n(86400) + " օր առաջ";
  const d = new Date(seen * 1000);
  return day(d.toISOString().slice(0, 10), true);
}

// the language of a book, from its top folder
const SHELF_LANGS = { grabar: "Գրաբար",
  ashkharhabar: "Աշխարհաբար" };

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
    const lang = SHELF_LANGS[r.name.split("/")[0]];
    const when = ago(r.seen);
    const x = h("button", { type: "button",
      class: "forget",
      "aria-label": "Հեռացնել ցանկից",
      title: "Հեռացնել ցանկից" }, "×");
    x.addEventListener("click", async () => {
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
      h("a", { href: "#/read/" + enc(r.name) },
        r.title),
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
    lang: "hy" },
    h("h2", {}, "Շարունակել կարդալ"),
    readingList(items),
    h("p", { class: "more" },
      h("a", { href: "#/recent" },
        "Բոլոր ընթերցումները →")));
}

async function recentPage() {
  const data = await api("recent");
  document.title = "Readings · Նախագիր";
  show(
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, "← Home")),
    h("h1", { lang: "hy" }, "Իմ ընթերցումները"),
    h("p", { class: "sub", lang: "hy" },
      STATIC ? "Պահված է միայն այս դիտարկիչում"
        : "Այս համակարգչում"),
    data.items.length
      ? h("section", { class: "recent all",
        lang: "hy" }, readingList(data.items))
      : h("p", { class: "empty", lang: "hy" },
        "Դեռ ոչինչ չեք կարդացել։ ",
        h("a", { href: "#/" }, "Գրադարան")));
}

// -- library --

// one book of #/library: its short name, how many
// parts and how much is translated
function libraryRow(b) {
  const meta = h("span", { class: "meta" });
  if (b.parts > 1) meta.append(b.parts + " մաս");
  if (b.done) {
    meta.append(h("span", { class: "done" },
      b.done === b.parts ? "թարգմանված"
        : "թարգմանված " + b.done + "/" + b.parts));
  }
  const a = h("a", { class: "row",
    href: "#/read/" + enc(b.first) },
  icon(ICONS.book, "ico"),
  h("span", { class: "name" }, b.name),
  meta);
  // the full title, when the name is short
  if (b.title !== b.name) a.title = b.title;
  return a;
}

// #/library: the Grabar books, by author
async function libraryPage() {
  const data = await api("library");
  document.title = "Գրադարան · Նախագիր";
  const groups = data.authors.map((a) => {
    const list = h("ul", { class: "shelf" });
    for (const b of a.books) {
      list.append(h("li", {}, libraryRow(b)));
    }
    return h("section", { class: "author" },
      h("h2", {}, a.name), list);
  });
  const n = data.authors.reduce(
    (k, a) => k + a.books.length, 0);
  show(
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, "← Home")),
    h("div", { class: "library", lang: "hy" },
      h("h1", {}, "Գրադարան"),
      h("p", { class: "sub" },
        "Գրաբար գրքեր · " + n),
      groups.length ? groups
        : h("p", { class: "empty" },
          "Գրքեր դեռ չկան։")));
}

// -- timeline --

// the kinds of events: KINDS in nxgir_timeline.py
const KINDS = ["Start", "Books", "Translation",
  "Reader", "Dictionary", "Texts", "Site"];

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May",
  "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// "2026-11-07" as a date at noon UTC, so the day
// is the same in every time zone
function isoDate(iso) {
  return new Date(iso + "T12:00:00Z");
}

// "2026-11-07": "7 Nov", or "7 Nov 2026"
function day(iso, year) {
  const d = isoDate(iso);
  return d.getUTCDate() + " " +
    MONTHS[d.getUTCMonth()] +
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
  if (e.to === "folder") return "#/f/" + enc(e.link);
  if (e.to === "url") return e.link;
  return "";
}

function eventLink(e) {
  const to = eventHref(e);
  if (!to) return null;
  const label = e.to === "url"
    ? e.link.replace(/^https:\/\//, "")
      .replace(/\/$/, "")
    : e.to === "read" ? "Read →" : "Open →";
  return h("p", { class: "links" },
    h("a", { href: to }, label));
}

function eventItem(e) {
  return h("li", { class: "ev" +
      (e.big ? " big" : ""), "data-kind": e.kind },
    h("h3", {},
      h("span", { class: "chip" }, e.kind),
      named(e.title)),
    e.text ? h("p", {}, named(e.text)) : null,
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
        " · day " + dayNo(data.start, e.date)));
    }
    list.append(eventItem(e));
  }
  return list;
}

async function timelinePage() {
  const data = await api("timeline");
  document.title = "Timeline · Նախագիր";
  const stat = (n, label) => h("div", {},
    h("b", {}, String(n)), h("span", {}, label));
  // a filter for each kind with more than one
  // event, in the order of KINDS
  const kinds = KINDS.filter((k) => data.events
    .filter((e) => e.kind === k).length > 1);
  let list = eventList(data, "");
  const filters = h("div", { class: "filters",
    role: "group", "aria-label": "Show" });
  for (const k of ["", ...kinds]) {
    const b = h("button", { type: "button",
      "aria-pressed": String(!k) }, k || "All");
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
      h("a", { href: "#/" }, "← Home")),
    h("h1", {}, "Timeline"),
    h("p", { class: "sub" },
      named("How nxGir grew, from the first"
        + " line to today")),
    data.start ? h("div", { class: "stats" },
      stat(dayNo(data.start), "days"),
      stat(data.books, "Grabar books"),
      stat(data.parts, "parts translated"))
      : null,
    kinds.length > 1 ? filters : null,
    list,
    data.next.length ? h("section", {},
      h("h2", { class: "tl-next" }, "Next"),
      h("ol", { class: "tl next" },
        data.next.map(eventItem))) : null,
    h("p", { class: "more-link" },
      h("a", { href: "#/stats" },
        "How close we are to the limits → Statistics"))
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
const BLOG_LANG = "nxgir-blog-lang";

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

// the language the reader picked, or Armenian
function blogLang() {
  try {
    const l = localStorage.getItem(BLOG_LANG);
    if (l in BLOG) return l;
  } catch (e) {}
  return "hy";
}

function setBlogLang(lang) {
  try {
    localStorage.setItem(BLOG_LANG, lang);
  } catch (e) {}
}

// a post's version in lang, or its first one
function version(p, lang) {
  return p.versions.find((v) => v.lang === lang)
    || p.versions[0];
}

// one post: its date, title and text (parse()
// in nxgir_blog.py: ["p", text] or ["h", text])
function postItem(p, lang) {
  const v = version(p, lang);
  return h("article", { class: "post",
    id: "post-" + p.slug, lang: v.lang },
  h("time", { datetime: p.date },
    longDay(p.date, v.lang)),
  h("h2", {},
    h("a", { href: "#/blog/" + p.slug },
      named(v.title))),
  v.blocks.map(([kind, text]) =>
    h(kind === "h" ? "h3" : "p", {}, named(text))));
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

// #/blog: every post, newest first; #/blog/<slug>
// that one post; #/blog/<slug>/<lang> in lang
async function blogPage(path) {
  const [slug, want] = path.split("/");
  if (want in BLOG) setBlogLang(want);
  const data = await api("blog");
  const one = slug
    ? data.posts.find((p) => p.slug === slug) : null;
  if (slug && !one) throw new Error("No such post");
  const draw = () => {
    // the languages the posts on this page have;
    // the one picked, if they have it
    const have = new Set((one ? [one] : data.posts)
      .flatMap((p) => p.versions.map((v) => v.lang)));
    const langs = Object.keys(BLOG)
      .filter((l) => have.has(l));
    const lang = have.has(blogLang()) || !langs.length
      ? blogLang() : langs[0];
    const t = BLOG[lang];
    const pick = h("div", { class: "filters",
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
      + " · " : "") + t.title + " · Նախագիր";
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, t.home),
        one ? [" · ", h("a", { href: "#/blog" },
          t.title)] : null),
      one ? null : h("h1", { lang }, t.title),
      one ? null : h("p", { class: "sub", lang },
        named(t.sub)),
      langs.length > 1 ? pick : null,
      h("div", { class: "blog" + (one ? " one" : "") },
        one ? postItem(one, lang)
          : data.posts.length
            ? data.posts.map((p) => postCard(p, lang))
            : h("p", { class: "empty", lang },
              t.none)));
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
  if (want in BLOG) setBlogLang(want);
  const data = await api("features");
  const draw = () => {
    const langs = data.versions.map((v) => v.lang);
    const lang = langs.includes(blogLang())
      || !langs.length ? blogLang() : langs[0];
    const v = data.versions.find((x) =>
      x.lang === lang);
    const pick = h("div", { class: "filters",
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
      + " · Նախագիր";
    const [intro, list] = v ? featureCards(v.blocks)
      : [[], null];
    show(
      h("p", { class: "crumbs", lang },
        h("a", { href: "#/" }, BLOG[lang].home)),
      h("h1", { lang }, v ? v.title : "Features"),
      h("div", { lang }, intro),
      langs.length > 1 ? pick : null,
      v ? h("div", { lang }, list)
        : h("p", { class: "empty" },
          "Nothing here yet."));
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
const LEVELS = { ok: "Fine", watch: "Watch",
  near: "Near the limit" };

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
  if (x.since) notes.push("measured " + day(x.since));
  return h("li", { class: "limit" +
      (x.key === closest ? " closest" : ""),
      "data-level": x.level },
    h("div", { class: "limit-head" },
      h("b", {}, x.label),
      h("span", { class: "pct" }, shown)),
    bar,
    h("div", { class: "limit-foot" },
      h("span", {}, amount(x, x.value) + " of " +
        amount(x, x.limit)),
      h("span", { class: "level" },
        LEVELS[x.level])),
    h("p", { class: "limit-by" }, notes.join(" · ")));
}

// the recorded measures, newest first, as a table
function historyTable(rows) {
  const cell = (v, f) => h("td", {},
    v === "" ? "–" : f(v));
  return h("div", { class: "table-wrap" },
    h("table", { class: "history" },
      h("thead", {}, h("tr", {},
        ["Date", "Commit", "Text", "Site", "Git",
          "Build"].map((t) => h("th", {}, t)))),
      h("tbody", {}, rows.map((r) => h("tr", {},
        h("td", {}, day(r.date, true)),
        h("td", {}, h("code", {}, r.commit)),
        cell(r.text, size), cell(r.site, size),
        cell(r.git, size), cell(r.build, secs))))));
}

async function statsPage() {
  const data = await api("stats");
  document.title = "Statistics · Նախագիր";
  const head = [
    h("p", { class: "crumbs" },
      h("a", { href: "#/" }, "← Home")),
    h("h1", {}, "Statistics"),
  ];
  if (data.error) {
    show(...head, h("p", { class: "empty" },
      "No statistics here: " + data.error + "."));
    return;
  }
  const stat = (n, label) => h("div", {},
    h("b", {}, String(n)), h("span", {}, label));
  const f = data.folders || {};
  const near = data.limits.find((x) =>
    x.key === data.closest);
  show(
    ...head,
    h("p", { class: "sub" },
      "How much the library holds, and how close it"
      + " is to the limits of GitHub and of a phone."
      + " Measured " + day(data.date, true)
      + " at commit ", h("code", {}, data.commit),
      "."),
    h("div", { class: "stats" },
      stat(data.books, "book files"),
      stat(size(data.text), "of text"),
      data.words ? stat(data.words.toLocaleString(
        "en"), "different words")
        : stat(size(f.ashkharhabar || 0),
          "translated")),
    near ? h("p", { class: "verdict",
        "data-level": near.level },
      "Closest: ", h("b", {}, near.label),
      " at " + Math.round(near.share) + "% of its"
      + " limit.") : null,
    h("h2", { class: "tl-next" }, "Limits"),
    h("ul", { class: "limits" },
      data.limits.map((x) =>
        limitRow(x, data.closest))),
    data.history.length ? h("section", {},
      h("h2", { class: "tl-next" }, "History"),
      historyTable(data.history)) : null,
    h("p", { class: "more-link" },
      "What each limit means: ",
      h("a", { href: NOTES }, "notes/limits.md"))
  );
}

// -- reader --

// Key for comparing words: normalize() in
// nxgir_reader.py. Ignores case and the marks
// ՛ ՜ ՞; և is the same as եւ (tests/test_web.py
// checks this matches on the whole library).
function wordKey(w) {
  return w.toLowerCase().replace(/[՛՜՞]/g, "")
    .replace(/և/g, "եւ");
}

const LANG_NAMES = { en: "English", hy: "Հայերեն" };
const cache = new Map();
let lang = "en";
try {
  if (localStorage.getItem("nxgir-lang") === "hy") {
    lang = "hy";
  }
} catch (e) {}

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

function openPanel(title, titleLang, ...body) {
  // the Contents button closes its own list
  const close = title === "Contents" ? null
    : btn("×", closePanel, { class: "icon-btn close",
      "aria-label": "Close" });
  R.panel.replaceChildren(
    h("div", { class: "panel-head" },
      h("h2", { lang: titleLang }, title), close),
    h("div", { class: "panel-body" }, ...body));
  R.panel.hidden = false;
  R.panel.dataset.kind = title;
  document.body.classList.add("panel-open");
  tocOpen(title === "Contents");
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

// the Contents button shows whether its list is open
function tocOpen(open) {
  R.tools?.querySelector(".toc-btn")
    ?.setAttribute("aria-expanded", String(open));
}

function langSwitch() {
  const box = h("div", { class: "seg",
    role: "group", "aria-label": "Meanings in" });
  for (const l of ["en", "hy"]) {
    box.append(btn(LANG_NAMES[l], () => {
      if (l === lang) return;
      lang = l;
      try {
        localStorage.setItem("nxgir-lang", l);
      } catch (e) {}
      drawWord();
    }, { class: null, lang: l,
      "aria-pressed": String(l === lang) }));
  }
  return box;
}

function placesNav() {
  const n = R.refs.length;
  const at = R.refs.indexOf(R.sel);
  const off = n < 2 ? "" : null;
  const label = n === 1 ? "Only here"
    : (at + 1) + " of " + n + " places";
  return section("In this book",
    h("div", { class: "places" },
      h("span", {}, label),
      btn("‹", () => step(-1), { disabled: off,
        "aria-label": "Previous place" }),
      btn("›", () => step(1), { disabled: off,
        "aria-label": "Next place" })));
}

function markAt(i) {
  return R.marks.find((m) => m.at === i);
}

function wordActions() {
  const on = !!markAt(R.sel);
  return h("div", { class: "actions" },
    btn(on ? "★ Bookmarked" : "☆ Bookmark",
      toggleMark, { "aria-pressed": String(on) }),
    btn("✎ Add note", () => editNote(-1)));
}

// draw the panel for the chosen word
async function drawWord() {
  const span = R.spans[R.sel];
  if (!R.panel || !span) return;
  const w = span.textContent;
  openPanel(w, "hy",
    h("p", { class: "loading" }, "Looking up…"));
  let data;
  try {
    data = await lookup(w);
  } catch (e) {
    data = { error: e.message };
  }
  // a later word may have been chosen meanwhile
  if (R.spans[R.sel] !== span) return;
  const parts = [STATIC ? null : wordActions(),
    placesNav()];
  if (data.error) {
    parts.push(h("p", { class: "error" },
      "Lookup failed: " + data.error));
  } else {
    if (data.abbr.length) {
      parts.push(section("Abbreviation",
        helperLines(data.abbr)));
    }
    parts.push(section("Meaning", langSwitch(),
      data.meaning.length ? helperLines(data.meaning)
        : h("p", { class: "none" },
          "Not in the vocabulary.")));
  }
  R.panel.querySelector(".panel-body")
    .replaceChildren(...parts.filter(Boolean));
}

function mark(on) {
  for (const i of R.refs) {
    R.spans[i].classList.toggle("ref", on);
  }
  if (R.sel >= 0) {
    R.spans[R.sel].classList.toggle("sel", on);
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
      R.spans[j].classList.remove("sent");
    }
    lit = null;
  }
  if (!on) return;
  lit = sentenceOf(i);
  for (let j = lit[0]; j < lit[1]; j++) {
    R.spans[j].classList.add("sent");
  }
}

// height of the toolbar stuck to the top
function bar() {
  return R.tools ? R.tools.offsetHeight : 0;
}

// keep a word in view between the toolbar and the
// bottom sheet
function reveal(span) {
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
  R.sel = i;
  mark(true);
  drawWord().then(() => reveal(R.spans[i]));
}

function step(d) {
  const n = R.refs.length;
  if (n < 2) return;
  const at = R.refs.indexOf(R.sel);
  choose(R.refs[(at + d + n) % n]);
}

// scroll to word i and make it blink once
function go(i) {
  const s = R.spans[i];
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
    R.spans[m.at]?.classList.add("bm");
  }
  for (const n of R.notes) {
    R.spans[n.at]?.classList.add("noted");
  }
  // on a phone the names hide, the counts stay
  const count = (sign, name, n) => [sign + " ",
    h("span", { class: "long" }, name + " · "),
    String(n)];
  const marks = "Bookmarks · " + R.marks.length;
  const notes = "Notes · " + R.notes.length;
  // back to the folder the book is in
  const dir = (R.name || R.opening).split("/")
    .slice(0, -1).join("/");
  R.tools.replaceChildren(...[
    R.prog,
    // the site's mark, once the top bar has
    // scrolled away (see stick())
    h("a", { class: "icon-btn home", href: "#/",
      "aria-label": "Library", title: "Library" },
    document.querySelector(".brand-mark")
      .cloneNode(true)),
    h("a", { class: "icon-btn back",
      href: dir ? "#/f/" + enc(dir) : "#/",
      "aria-label": "Back to the folder",
      title: "Back to " + (dir || "the library") },
    icon(ICONS.back)),
    // a second click hides the list again
    R.contents.length ? btn(["☰ ", h("span",
      { class: "long" }, "Contents")],
    toggleContents, { class: "icon-btn toc-btn",
      "aria-label": "Contents",
      "aria-expanded": String(!!R.panel &&
        !R.panel.hidden &&
        R.panel.dataset.kind === "Contents"),
      title: "Contents: "
        + plural(R.contents.length, "heading") })
      : null,
    STATIC ? null : btn(count("★", "Bookmarks",
      R.marks.length), showMarks,
    { "aria-label": marks, title: marks }),
    STATIC ? null : btn(count("✎", "Notes",
      R.notes.length), showNotes,
    { "aria-label": notes, title: notes }),
    R.editable ? h("a", { class: "icon-btn",
      href: "#/edit/" + enc(R.name || R.opening) },
    "Edit text") : null,
    R.par ? btn(["⇆ ", h("span", { class: "long" },
      "Parallel")],
    () => setView({ parallel: !view.parallel }), {
      "aria-pressed": String(view.parallel),
      "aria-label": "Show the two versions",
      title: "Side by side with "
        + parLabel(R.par.name) }) : null,
    // on a wide screen: each line under its pair,
    // as on a phone, or beside it
    R.par && view.parallel ? btn(icon(ICONS[
      view.stacked ? "rows" : "columns"]),
    () => setView({ stacked: !view.stacked }), {
      class: "icon-btn par-layout",
      "aria-label": "Each line under its pair",
      "aria-pressed": String(view.stacked),
      title: view.stacked
        ? "Lines under each other (click for"
          + " side by side)"
        : "Side by side (click for lines under"
          + " each other)" }) : null,
    // on a phone the text tools hide behind this
    btn(icon(ICONS.sliders), () => {
      const open = R.tools.classList.toggle("open");
      more.setAttribute("aria-expanded",
        String(open));
    }, {
      class: "icon-btn more",
      "aria-expanded": String(
        R.tools.classList.contains("open")),
      "aria-label": "Text settings",
      title: "Text settings" }),
    viewTools(),
  ].filter(Boolean));
  const more = R.tools.querySelector(".more");
}

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
  full: false, stacked: false };
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
  const par = Boolean(R.par && view.parallel);
  R.text.classList.toggle("parallel", par);
  R.text.classList.toggle("stacked",
    par && view.stacked);
  // the page widens for two columns only
  document.body.classList.toggle("parallel",
    par && !view.stacked);
}

function setView(change) {
  // keep the word at the top of the screen there
  const i = R.spans.length ? topWord() : -1;
  const before = i >= 0
    ? R.spans[i].getBoundingClientRect().top : 0;
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
        stacked: view.stacked }));
  } catch (e) {}
  applyView();
  if (i >= 0) {
    const after = R.spans[i].getBoundingClientRect().top;
    window.scrollBy(0, after - before);
  }
  decorate();
}

function viewTools() {
  const n = view.size;
  return h("div", { class: "view",
    role: "group", "aria-label": "Text" },
  btn("A−", () => setView({ size: n - 1 }), {
    "aria-label": "Smaller text",
    title: "Smaller text",
    disabled: n === 0 ? "" : null }),
  btn("A+", () => setView({ size: n + 1 }), {
    "aria-label": "Bigger text",
    title: "Bigger text",
    disabled: n === SIZES.length - 1 ? "" : null }),
  btn(icon(ICONS[view.center ? "center" : "left"]),
    () => setView({ center: !view.center }), {
      "aria-label": "Center the text",
      "aria-pressed": String(view.center),
      title: view.center ? "Text centered"
        : "Text on the left" }),
  btn(icon(ICONS.spacing),
    () => setView({
      line: (view.line + 1) % LINES.length }), {
      "aria-label": "Line spacing " + (view.line + 1)
        + " of " + LINES.length,
      title: view.line === LINES.length - 1
        ? "Widest lines (click for normal)"
        : "Line spacing (click for more)" }),
  btn("¶", () => setView({
    sentences: !view.sentences }), {
    "aria-label": "Each sentence on its own line",
    "aria-pressed": String(view.sentences),
    title: view.sentences
      ? "Sentences apart (click to join)"
      : "Text as written (click for sentences)" }),
  btn(icon(ICONS.width),
    () => setView({ full: !view.full }), {
      "aria-label": "Text across the whole width",
      "aria-pressed": String(view.full),
      title: view.full
        ? "Whole width (click for a column)"
        : "Text in a column (click for whole"
          + " width)" }),
  fontPick(),
  // the theme button joins the row while reading
  button);
}

// the book fonts by name
function fontPick() {
  const pick = h("select", { class: "font-pick",
    "aria-label": "Font of the text",
    title: "Font of the text" },
  FONTS.map((f, i) => h("option", { value: String(i),
    selected: i === view.font ? "" : null },
  FONT_NAMES[f])));
  pick.addEventListener("change", () =>
    setView({ font: Number(pick.value) }));
  return pick;
}

function fail(e) {
  alert("Could not save: " + e.message);
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
  const s = R.spans[i];
  const nodes = [...s.parentElement.childNodes];
  const t = nodes.slice(nodes.indexOf(s))
    .map((x) => x.textContent).join("").trim();
  return t.length > n
    ? t.slice(0, n - 1).trimEnd() + "…" : t;
}

function lineOf(i) {
  return "line " + (R.wpos[i][0] + 1);
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
    const meta = c.level === 1 ? ""
      : (c.n ? "Գլուխ " + c.n + " · " : "");
    const link = h("button", { type: "button",
      class: "item-main" },
    h("span", { class: "item-meta" },
      meta + "line " + (c.line + 1)),
    h("span", { class: "item-quote", lang: "hy" },
      c.title || "Գլուխ " + c.n));
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
  openPanel("Contents", "en", list);
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
    openPanel("Bookmarks", "en", h("p",
      { class: "none" }, "No bookmarks yet. Tap a"
      + " word, then ☆ Bookmark."));
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
    const del = btn("Remove", async () => {
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
  openPanel("Bookmarks", "en", list);
}

function showNotes() {
  closePanel();
  if (!R.notes.length) {
    openPanel("Notes", "en", h("p",
      { class: "none" }, "No notes yet. Tap a word,"
      + " then ✎ Add note."));
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
    const edit = btn("Edit", () => {
      R.sel = -1;
      editNote(i);
    }, { class: "link-btn" });
    const del = btn("Delete", async () => {
      if (!confirm("Delete this note?")) return;
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
  openPanel("Notes", "en", list);
}

// write a new note on the chosen word's sentence
// (i = -1), or change note i
function editNote(i) {
  const old = i >= 0 ? R.notes[i] : null;
  const at = old ? old.at : R.sel;
  mark(false);
  sentence(true, at);
  const [lo, hi] = lit;
  const words = R.spans.slice(lo, hi)
    .map((s) => s.textContent).join(" ");
  const box = h("textarea", { rows: "5",
    "aria-label": "Note" });
  box.value = old ? old.text : "";
  const save = btn("Save", async () => {
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
  const cancel = btn("Cancel", () => {
    if (old) showNotes();
    else closePanel();
  });
  openPanel(old ? "Edit note" : "New note", "en",
    h("p", { class: "item-quote", lang: "hy" },
      "«" + (words.length > 120
        ? words.slice(0, 119) + "…" : words) + "»"),
    box, h("div", { class: "actions" }, save, cancel));
  reveal(R.spans[at]);
  box.focus({ preventScroll: true });
}

// -- where the book was left --

// the first word at the top of the screen, not
// hidden under the toolbar
function topWord() {
  const edge = R.tools.getBoundingClientRect().bottom;
  let lo = 0;
  let hi = R.spans.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    const r = R.spans[mid].getBoundingClientRect();
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
  let lo = 0;
  let hi = R.spans.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    const r = R.spans[mid].getBoundingClientRect();
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
    R.tools.getBoundingClientRect().top < 1);
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
  const pct = Math.round(f * 100);
  R.prog.firstChild.firstChild.style.width =
    pct + "%";
  R.prog.lastChild.textContent = pct + "%";
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

const PAR_NAMES = { grabar: "Գրաբար",
  ashkharhabar: "Աշխարհաբար" };

function parLabel(name) {
  const top = name.split("/")[0];
  return PAR_NAMES[top] || top;
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

function parLine(line) {
  const parts = R.par.lines[line] || [""];
  const p = h("p", { class: "par" });
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

function trCredit(c, of) {
  return h("p", { class: "tr-credit"
    + (of ? " of-par" : "") },
    c.text + " · ",
    h("a", { href: c.url, rel: "license" },
      c.license),
    " · ",
    h("a", { href: HELP }, "Օգնել խմբագրել"));
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
      "aria-label": "Parts" },
    card(p.prev, "prev", "← Part "
      + (p.n - 1) + " of " + p.total),
    card(p.next, "next", "Part " + (p.n + 1)
      + " of " + p.total + " →")),
    h("p", { class: "part-all" },
      h("a", { href: "#/f/" + enc(p.folder) },
        "All " + p.total + " parts of ",
        h("span", { lang: "hy" }, p.book))));
}

// where a sentence starts inside a line: shown as
// a break when Sentences (¶) is on
function cut() {
  return h("span", { class: "cut" });
}

async function book(name) {
  const data = await api("book?name=" +
    encodeURIComponent(name));
  const title = name.split("/").pop();
  document.title = title + " · Նախագիր";
  Object.assign(R, {
    name: "", lines: data.lines.length,
    spans: [], keys: [], wpos: [],
    starts: data.starts, marks: data.marks,
    notes: data.notes, sel: -1, refs: [],
    contents: data.contents || [],
    saved: "", editable: data.editable,
    opening: name, par: null,
  });
  // the other version, read beside it on a wide
  // screen
  const other = (data.parallel || [])[0];
  if (other) {
    try {
      R.par = await api("book?name=" +
        encodeURIComponent(other));
      // the first word of each of its lines
      let n = 0;
      R.par.first = R.par.lines.map((parts) => {
        const at = n;
        n += (parts.length - 1) / 2;
        return at;
      });
      R.par.starts = new Set(R.par.starts || []);
    } catch (e) {} // read it alone
  }
  const text = h("div", { class: "text",
    lang: "hy" });
  R.text = text;
  applyView();
  const frag = document.createDocumentFragment();
  const format = data.format || {};
  const starts = new Set(data.starts || []);
  if (R.par) {
    frag.append(...parHead(name, R.par.name));
  }
  const of = !data.credit && R.par && R.par.credit;
  const credit = data.credit || of;
  if (credit) frag.append(trCredit(credit, of));
  data.lines.forEach((parts, line) => {
    const p = document.createElement("p");
    const f = format[line];
    if (f && f.h) p.className = "md-h md-h" + f.h;
    if (f && f.q) p.classList.add("md-q");
    const spans = f ? f.spans : [];
    let at = 0; // characters before this part
    parts.forEach((t, k) => {
      const nodes = styled(t, at, spans);
      at += Array.from(t).length;
      if (k % 2 === 0) {
        if (t) p.append(...nodes);
        return;
      }
      if (k > 1 && starts.has(R.spans.length)) {
        p.append(cut());
      }
      const s = document.createElement("span");
      s.className = "w";
      s.dataset.i = R.spans.length;
      s.append(...nodes);
      R.spans.push(s);
      R.keys.push(wordKey(t));
      R.wpos.push([line, (k - 1) / 2]);
      p.append(s);
    });
    frag.append(p);
    if (R.par) frag.append(parLine(line));
  });
  // lines the other version has more of
  for (let line = data.lines.length;
    R.par && line < R.par.lines.length; line++) {
    frag.append(h("p", { class: "par" }),
      parLine(line));
  }
  text.append(frag);
  text.addEventListener("click", (e) => {
    const s = e.target.closest(".w");
    if (!s) return;
    const i = Number(s.dataset.i);
    if (i === R.sel) closePanel();
    else choose(i);
  });
  R.panel = h("aside", { class: "panel",
    "aria-label": "Word", "aria-live": "polite" });
  R.panel.hidden = true;
  R.tools = h("div", { class: "tools" });
  // its height, for the panel beside the text
  // (--tools in style.css): it wraps and grows
  new ResizeObserver(() => {
    document.documentElement.style.setProperty(
      "--tools", R.tools.offsetHeight + "px");
  }).observe(R.tools);
  R.prog = h("div", { class: "readbar",
    role: "progressbar", "aria-label": "Read",
    "aria-valuemin": "0", "aria-valuemax": "100" },
  h("span", { class: "track" }, h("span")),
  h("span", { class: "pct" }, "0%"));
  document.body.classList.add("reading");
  show(crumbs(name, false), h("h1", {}, title),
    h("p", { class: "sub" },
      plural(data.lines.length, "line") +
      " · tap a word to look it up"),
    R.tools,
    h("div", { class: "reader" }, text, R.panel,
      partEnd(data.parts)));
  decorate();
  // the first word: stay at the top, title shown
  if (data.at > 0 && R.spans[data.at]) {
    const top = R.spans[data.at]
      .getBoundingClientRect().top + window.scrollY;
    window.scrollTo(0, top - bar() - 16);
  }
  stick();
  progress();
  // from now on scrolling is saved
  R.name = name;
  R.title = title;
  // the first line, for the list of readings
  R.head = (data.lines[0] || []).join("").trim();
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
    confirm("Leave without saving your changes?");
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
    "aria-label": "Text" });
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

const MD_HELP = "Saved exactly as typed. Markdown:"
  + " # title, > quote, **bold**, *italic*.";

async function edit(name) {
  const src = await api("source?name=" +
    encodeURIComponent(name));
  let ver = src.version;
  const title = name.split("/").pop();
  document.title = "Edit " + title + " · Նախագիր";
  const box = textBox(src.text);
  const msg = status();
  const reload = btn("Load the file again", () => {
    if (!leaveOk()) return;
    E.dirty = false;
    route();
  });
  reload.hidden = true;
  async function save() {
    msg.className = "status";
    msg.textContent = "Saving…";
    try {
      const r = await send("save", { name,
        text: box.value, version: ver });
      ver = r.version;
      E.dirty = false;
      msg.textContent = "Saved at " +
        new Date().toLocaleTimeString([],
          { hour: "2-digit", minute: "2-digit" });
    } catch (e) {
      msg.className = "status error";
      msg.textContent = e.status === 409
        ? "The file changed on disk since you opened"
          + " it (a git pull?), so it was not saved."
          + " Your text is still here: copy it, then"
          + " load the file again."
        : "Not saved: " + e.message;
      reload.hidden = e.status !== 409;
    }
  }
  E.save = save;
  show(crumbs(name, false),
    h("h1", {}, "Edit " + title),
    h("p", { class: "sub" }, MD_HELP),
    box,
    h("div", { class: "actions" },
      btn("Save", save, { class: "icon-btn primary" }),
      h("a", { class: "icon-btn",
        href: "#/read/" + enc(name) }, "Done"),
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
  document.title = "New text · Նախագիր";
  const file = h("input", { type: "text",
    class: "field", id: "file", autocomplete: "off",
    autocapitalize: "none", spellcheck: "false",
    placeholder: "ps-118-33-37-pustota-i-put" });
  const where = h("span", { class: "item-meta" });
  const langs = h("div", { class: "seg",
    role: "group", "aria-label": "Language" });
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
  const box = textBox("",
    "# Title (Ps 118:33–37)\n\nThe text…");
  async function create() {
    msg.className = "status";
    msg.textContent = "Saving…";
    try {
      const r = await send("new", { lang,
        file: file.value.trim(), text: box.value });
      E.dirty = false;
      location.hash = "#/read/" + enc(r.name);
    } catch (e) {
      msg.className = "status error";
      msg.textContent = "Not saved: " + e.message;
    }
  }
  E.save = create;
  // the language folder may have no texts yet
  show(crumbs("interpretations/new", false),
    h("h1", {}, "New text"),
    h("p", { class: "sub" }, "One text per file,"
      + " named by its passage and a short title in"
      + " Latin letters. " + MD_HELP),
    h("div", { class: "form" },
      langs,
      h("label", { for: "file" }, "File name"),
      file, where),
    box,
    h("div", { class: "actions" },
      btn("Create", create,
        { class: "icon-btn primary" }),
      h("a", { class: "icon-btn",
        href: "#/f/interpretations" }, "Cancel"),
      msg));
  file.focus();
}

// -- pages --

async function route() {
  // unsaved text: ask before leaving the editor
  if (E.back) {
    E.back = false;
    return;
  }
  if (E.hash && location.hash !== E.hash) {
    if (!leaveOk()) {
      E.back = true;
      location.hash = E.hash;
      return;
    }
  }
  E.dirty = false;
  E.save = null;
  E.hash = "";
  const hash = location.hash.replace(/^#\/?/, "");
  if (R.timer) savePos(true);
  R.name = "";
  closePanel();
  R.panel = null;
  R.par = null;
  document.body.classList.remove("reading",
    "parallel", "full");
  // back to the top bar from the reading tools
  if (button.parentNode !== topBar) topBar.append(button);
  try {
    if (hash.startsWith("read/")) {
      await book(decodeURIComponent(hash.slice(5)));
    } else if (hash.startsWith("edit/")) {
      E.hash = location.hash;
      await edit(decodeURIComponent(hash.slice(5)));
    } else if (hash.startsWith("new/")) {
      E.hash = location.hash;
      await newText(hash.slice(4));
    } else if (hash === "timeline") {
      await timelinePage();
    } else if (hash === "blog"
      || hash.startsWith("blog/")) {
      await blogPage(decodeURIComponent(
        hash.slice(5)));
    } else if (hash === "features"
      || hash.startsWith("features/")) {
      await featuresPage(hash.slice(9));
    } else if (hash === "stats") {
      await statsPage();
    } else if (hash === "recent") {
      await recentPage();
    } else if (hash === "library") {
      await libraryPage();
    } else if (hash.startsWith("f/")) {
      await shelf(decodeURIComponent(hash.slice(2)));
    } else {
      await shelf("");
    }
    visit("/" + decodeURIComponent(hash));
  } catch (e) {
    showError(e.message || "Something went wrong");
  }
}

window.addEventListener("hashchange", route);
drawTheme();
drawView();
route();
