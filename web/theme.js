// Set the theme before the page is drawn, so it does
// not flash. "auto" (nothing set) follows the system.
(function () {
  var t = null;
  try {
    t = localStorage.getItem("nxgir-theme");
  } catch (e) {}
  if (t === "light" || t === "dark") {
    document.documentElement.dataset.theme = t;
  }
})();
