// nx-gir web: the bookshelf and the theme button.
// Pages are #/ (top), #/f/<folder> and
// #/read/<book>; the data comes from /api/.
"use strict";

const main = document.getElementById("main");

// -- small helpers --

// h("a", {href: "#/"}, "text", child): an element.
// Text is always set as text, never as HTML. Kids
// may be lists; null kids are left out.
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
  sun: [
    "M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8z",
    "M12 2v2M12 20v2M2 12h2M20 12h2" +
      "M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4" +
      "M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  ],
  moon: [
    "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z",
  ],
  left: ["M4 6h16M4 10h10M4 14h16M4 18h10"],
  // lines with an up-down arrow beside them
  spacing: ["M11 6h9M11 12h9M11 18h9",
    "M5 4v16M3 6l2-2l2 2M3 18l2 2l2-2"],
  center: ["M4 6h16M7 10h10M4 14h16M7 18h10"],
  back: ["M19 12H5M11 6l-6 6l6 6"],
  // two sliders: the text settings
  sliders: ["M4 7h9M17 7h3M4 17h3M11 17h9",
    "M15 5a2 2 0 1 0 0 4a2 2 0 1 0 0-4z",
    "M9 15a2 2 0 1 0 0 4a2 2 0 1 0 0-4z"],
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
// files the words are spread over, per language;
// as BUCKETS in build-site.py
const BUCKETS = 256;
const buckets = new Map();

async function json(url) {
  const r = await fetch(url);
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

function enc(name) {
  return name.split("/").map(encodeURIComponent)
    .join("/");
}

function show(...kids) {
  // (replaceChildren would write null as "null")
  main.replaceChildren(
    ...kids.filter((k) => k != null));
  window.scrollTo(0, 0);
}

function showError(msg) {
  show(
    h("p", { class: "error" }, msg + ". ",
      h("a", { href: "#/" }, "Back to the library"))
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

function theme() {
  const t = document.documentElement.dataset.theme;
  return t === "dark" ? "dark" : "light";
}

function drawTheme() {
  const t = theme();
  const names = { light: "Light", dark: "Dark" };
  const which = { light: "sun", dark: "moon" };
  const other = t === "dark" ? "light" : "dark";
  button.replaceChildren(icon(ICONS[which[t]]));
  button.title = "Theme: " + names[t] +
    " (click for " + names[other].toLowerCase() + ")";
  button.setAttribute("aria-label", button.title);
}

button.addEventListener("click", () => {
  const t = theme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = t;
  try {
    localStorage.setItem("nxgir-theme", t);
  } catch (e) {}
  drawTheme();
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
    plural(item.size, "book")));
}

async function shelf(folder) {
  const q = encodeURIComponent(folder);
  const data = await api("shelf?folder=" + q);
  const books = data.items.reduce(
    (n, i) => n + (i.folder ? i.size : 1), 0);
  const title = folder
    ? folder.split("/").pop() : "Library";
  document.title = folder
    ? title + " · nx-gir" : "nx-gir";
  const list = h("ul", { class: "shelf" });
  for (const item of data.items) {
    list.append(h("li", {}, item.folder
      ? folderRow(item) : bookRow(item)));
  }
  const lang = folder.split("/")[1];
  show(
    folder ? crumbs(folder, false) : null,
    h("h1", {}, title),
    h("p", { class: "sub" }, plural(books, "book")),
    data.editable ? h("div", { class: "actions" },
      h("a", { class: "icon-btn",
        href: "#/new/" + (lang || "ru") },
      "+ New text")) : null,
    data.items.length ? list
      : h("p", { class: "empty" }, "No books here.")
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
  saved: "", // the position last saved
  timer: 0,
  par: null, // the other version: book() data
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
  const close = btn("×", closePanel,
    { class: "icon-btn close", "aria-label": "Close" });
  R.panel.replaceChildren(
    h("div", { class: "panel-head" },
      h("h2", { lang: titleLang }, title), close),
    h("div", { class: "panel-body" }, ...body));
  R.panel.hidden = false;
  document.body.classList.add("panel-open");
}

function closePanel() {
  mark(false);
  sentence(false);
  R.sel = -1;
  R.refs = [];
  if (R.panel) R.panel.hidden = true;
  document.body.classList.remove("panel-open");
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
    h("a", { class: "icon-btn back",
      href: dir ? "#/f/" + enc(dir) : "#/",
      "aria-label": "Back to the folder",
      title: "Back to " + (dir || "the library") },
    icon(ICONS.back)),
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
const view = { size: SIZE, center: false, line: 0,
  parallel: true };
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
  view.parallel = v.parallel !== false;
} catch (e) {}

function applyView() {
  // on the page too: the word panel follows the size
  document.documentElement.style.setProperty(
    "--text-size", SIZES[view.size] + "rem");
  if (!R.text) return;
  R.text.style.setProperty("--text-size",
    SIZES[view.size] + "rem");
  R.text.style.setProperty("--text-line",
    LINES[view.line]);
  R.text.classList.toggle("centered", view.center);
  const par = Boolean(R.par && view.parallel);
  R.text.classList.toggle("parallel", par);
  document.body.classList.toggle("parallel", par);
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
        parallel: view.parallel }));
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
  // the theme button joins the row while reading
  button);
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
    // as State.progress() counts it
    const pct = Math.min(100,
      Math.round(100 * (pos[0] + 1) / R.lines));
    try {
      localStorage.setItem("nxgir-read:" + R.name,
        JSON.stringify({ at: top, pct }));
    } catch (e) {}
    return;
  }
  send("position", { name: R.name, pos,
    lines: R.lines }, keepalive).catch(() => {
    R.saved = "";
  });
}

window.addEventListener("scroll", () => {
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
  return h("p", { class: "par" }, parts.join(""));
}

async function book(name) {
  const data = await api("book?name=" +
    encodeURIComponent(name));
  const title = name.split("/").pop();
  document.title = title + " · nx-gir";
  Object.assign(R, {
    name: "", lines: data.lines.length,
    spans: [], keys: [], wpos: [],
    starts: data.starts, marks: data.marks,
    notes: data.notes, sel: -1, refs: [],
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
    } catch (e) {} // read it alone
  }
  const text = h("div", { class: "text",
    lang: "hy" });
  R.text = text;
  applyView();
  const frag = document.createDocumentFragment();
  const format = data.format || {};
  if (R.par) {
    frag.append(...parHead(name, R.par.name));
  }
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
  document.body.classList.add("reading");
  show(crumbs(name, false), h("h1", {}, title),
    h("p", { class: "sub" },
      plural(data.lines.length, "line") +
      " · tap a word to look it up"),
    R.tools,
    h("div", { class: "reader" }, text, R.panel));
  decorate();
  // the first word: stay at the top, title shown
  if (data.at > 0 && R.spans[data.at]) {
    const top = R.spans[data.at]
      .getBoundingClientRect().top + window.scrollY;
    window.scrollTo(0, top - bar() - 16);
  }
  // from now on scrolling is saved
  R.name = name;
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
  document.title = "Edit " + title + " · nx-gir";
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
  document.title = "New text · nx-gir";
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
    "parallel");
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
    } else if (hash.startsWith("f/")) {
      await shelf(decodeURIComponent(hash.slice(2)));
    } else {
      await shelf("");
    }
  } catch (e) {
    showError(e.message || "Something went wrong");
  }
}

window.addEventListener("hashchange", route);
drawTheme();
route();
