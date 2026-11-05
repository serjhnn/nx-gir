// Set the theme before the page is drawn, so it does
// not flash: the one picked with the button, or, until
// one is picked, the system's.
(function () {
  var t = null;
  try {
    t = localStorage.getItem("nxgir-theme");
  } catch (e) {}
  if (t !== "light" && t !== "dark") {
    var dark = window.matchMedia &&
      matchMedia("(prefers-color-scheme: dark)").matches;
    t = dark ? "dark" : "light";
  }
  document.documentElement.dataset.theme = t;
})();
