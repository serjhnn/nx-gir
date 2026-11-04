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

// -- a book, as plain text for now --

async function book(name) {
  const data = await api("book?name=" +
    encodeURIComponent(name));
  const title = name.split("/").pop();
  document.title = title + " · nx-gir";
  const text = h("div", { class: "text",
    lang: "hy" });
  for (const parts of data.lines) {
    text.append(h("p", {}, parts.join("")));
  }
  show(crumbs(name, false), h("h1", {}, title),
    h("p", { class: "sub" },
      plural(data.lines.length, "line")),
    text);
}

// -- pages --

async function route() {
  const hash = location.hash.replace(/^#\/?/, "");
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
