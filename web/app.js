// nx-gir web: the bookshelf and the theme button.
// Pages are #/ (top), #/f/<folder> and
// #/read/<book>; the data comes from /api/.
"use strict";

const main = document.getElementById("main");

// -- small helpers --

// h("a", {href: "#/"}, "text", child): an element.
// Text is always set as text, never as HTML.
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null) continue;
    if (k === "class") el.className = v;
    else el.setAttribute(k, v);
  }
  for (const k of kids) {
    if (k == null) continue;
    el.append(k);
  }
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
  auto: [
    "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18z",
    "M12 3v18a9 9 0 0 0 0-18z",
  ],
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
  const r = await fetch("/api/" + path);
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || r.status);
  return data;
}

function enc(name) {
  return name.split("/").map(encodeURIComponent)
    .join("/");
}

function show(...kids) {
  main.replaceChildren(...kids);
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

const THEMES = ["auto", "light", "dark"];
const button = document.getElementById("theme");

function theme() {
  const t = document.documentElement.dataset.theme;
  return THEMES.includes(t) ? t : "auto";
}

function drawTheme() {
  const t = theme();
  const names = { auto: "Auto", light: "Light",
    dark: "Dark" };
  const which = { auto: "auto", light: "sun",
    dark: "moon" };
  button.replaceChildren(icon(ICONS[which[t]]),
    h("span", {}, names[t]));
  button.title = "Theme: " + names[t] +
    " (click to change)";
}

button.addEventListener("click", () => {
  const t = THEMES[(THEMES.indexOf(theme()) + 1) % 3];
  const root = document.documentElement;
  if (t === "auto") delete root.dataset.theme;
  else root.dataset.theme = t;
  try {
    if (t === "auto") {
      localStorage.removeItem("nxgir-theme");
    } else {
      localStorage.setItem("nxgir-theme", t);
    }
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
  show(
    folder ? crumbs(folder, false) : null,
    h("h1", {}, title),
    h("p", { class: "sub" }, plural(books, "book")),
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
  spans: [], // every word, in reading order
  keys: [], // wordKey of each
  sel: -1, // the chosen word
  refs: [], // indexes of words with its key
  panel: null,
};

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

function langSwitch() {
  const box = h("div", { class: "seg",
    role: "group", "aria-label": "Meanings in" });
  for (const l of ["en", "hy"]) {
    const b = h("button", { type: "button",
      "aria-pressed": String(l === lang),
      lang: l }, LANG_NAMES[l]);
    b.addEventListener("click", () => {
      if (l === lang) return;
      lang = l;
      try {
        localStorage.setItem("nxgir-lang", l);
      } catch (e) {}
      drawPanel();
    });
    box.append(b);
  }
  return box;
}

function placesNav() {
  const n = R.refs.length;
  const at = R.refs.indexOf(R.sel);
  const prev = h("button", { type: "button",
    class: "icon-btn", "aria-label": "Previous place",
    disabled: n < 2 ? "" : null }, "‹");
  const next = h("button", { type: "button",
    class: "icon-btn", "aria-label": "Next place",
    disabled: n < 2 ? "" : null }, "›");
  prev.addEventListener("click", () => step(-1));
  next.addEventListener("click", () => step(1));
  const label = n === 1 ? "Only here"
    : (at + 1) + " of " + n + " places";
  return section("In this book",
    h("div", { class: "places" },
      h("span", {}, label), prev, next));
}

// draw the panel for the chosen word
async function drawPanel() {
  const panel = R.panel;
  const span = R.spans[R.sel];
  if (!panel || !span) return;
  const w = span.textContent;
  const close = h("button", { type: "button",
    class: "icon-btn close", "aria-label": "Close" },
  "×");
  close.addEventListener("click", closePanel);
  const body = h("div", { class: "panel-body" },
    h("p", { class: "loading" }, "Looking up…"));
  panel.replaceChildren(
    h("div", { class: "panel-head" },
      h("h2", { lang: "hy" }, w), close),
    body);
  panel.hidden = false;
  document.body.classList.add("panel-open");
  let data;
  try {
    data = await lookup(w);
  } catch (e) {
    body.replaceChildren(h("p", { class: "error" },
      "Lookup failed: " + e.message));
    return;
  }
  // a later word may have been chosen meanwhile
  if (R.spans[R.sel] !== span) return;
  const parts = [placesNav()];
  if (data.abbr.length) {
    parts.push(section("Abbreviation",
      helperLines(data.abbr)));
  }
  parts.push(section("Meaning", langSwitch(),
    data.meaning.length ? helperLines(data.meaning)
      : h("p", { class: "none" },
        "Not in the vocabulary.")));
  body.replaceChildren(...parts);
}

function mark(on) {
  for (const i of R.refs) {
    R.spans[i].classList.toggle("ref", on);
  }
  if (R.sel >= 0) {
    R.spans[R.sel].classList.toggle("sel", on);
  }
}

// keep a word in view above the bottom sheet
function reveal(span) {
  const r = span.getBoundingClientRect();
  const sheet = R.panel && !R.panel.hidden &&
    getComputedStyle(R.panel).position === "fixed"
    ? R.panel.getBoundingClientRect().height : 0;
  const bottom = window.innerHeight - sheet - 16;
  if (r.top < 72 || r.bottom > bottom) {
    const mid = (r.top + r.bottom) / 2;
    window.scrollBy({ top: mid - (72 + bottom) / 2 });
  }
}

function choose(i) {
  mark(false);
  const key = R.keys[i];
  if (R.sel < 0 || R.keys[R.sel] !== key) {
    R.refs = [];
    R.keys.forEach((k, j) => {
      if (k === key) R.refs.push(j);
    });
  }
  R.sel = i;
  mark(true);
  drawPanel().then(() => reveal(R.spans[i]));
}

function step(d) {
  const n = R.refs.length;
  if (n < 2) return;
  const at = R.refs.indexOf(R.sel);
  choose(R.refs[(at + d + n) % n]);
}

function closePanel() {
  mark(false);
  R.sel = -1;
  R.refs = [];
  if (R.panel) R.panel.hidden = true;
  document.body.classList.remove("panel-open");
}

document.addEventListener("keydown", (e) => {
  if (R.sel < 0) return;
  if (e.key === "Escape") closePanel();
  else if (e.key === "n") step(1);
  else if (e.key === "N") step(-1);
});

async function book(name) {
  const data = await api("book?name=" +
    encodeURIComponent(name));
  const title = name.split("/").pop();
  document.title = title + " · nx-gir";
  R.name = name;
  R.spans = [];
  R.keys = [];
  R.sel = -1;
  R.refs = [];
  const text = h("div", { class: "text",
    lang: "hy" });
  const frag = document.createDocumentFragment();
  for (const parts of data.lines) {
    const p = document.createElement("p");
    parts.forEach((t, k) => {
      if (k % 2 === 0) {
        if (t) p.append(t);
        return;
      }
      const s = document.createElement("span");
      s.className = "w";
      s.dataset.i = R.spans.length;
      s.textContent = t;
      R.spans.push(s);
      R.keys.push(wordKey(t));
      p.append(s);
    });
    frag.append(p);
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
  document.body.classList.add("reading");
  show(crumbs(name, false), h("h1", {}, title),
    h("p", { class: "sub" },
      plural(data.lines.length, "line") +
      " · tap a word to look it up"),
    h("div", { class: "reader" }, text, R.panel));
}

// -- pages --

async function route() {
  const hash = location.hash.replace(/^#\/?/, "");
  closePanel();
  R.panel = null;
  document.body.classList.remove("reading");
  try {
    if (hash.startsWith("read/")) {
      await book(decodeURIComponent(hash.slice(5)));
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
