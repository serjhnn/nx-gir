// Set the theme before the page is drawn, so it does
// not flash: the one picked with the button, or, until
// one is picked, the system's.
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
})();
