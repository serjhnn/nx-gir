// Set the theme and the book font before the page is
// drawn, so they do not flash: the theme picked with
// the button, or, until one is picked, the system's;
// the font from the text settings (app.js).
(function () {
  var t = null;
  try {
    t = localStorage.getItem("nxgir-theme");
  } catch (e) {}
  var ok = { light: 1, dark: 1, black: 1 };
  if (!ok[t]) {
    var dark = window.matchMedia &&
      matchMedia("(prefers-color-scheme: dark)").matches;
    t = dark ? "dark" : "light";
  }
  document.documentElement.dataset.theme = t;
  try {
    var v = JSON.parse(
      localStorage.getItem("nxgir-view") || "{}");
    if (v.font) {
      document.documentElement.dataset.font = v.font;
    }
  } catch (e) {}
})();
