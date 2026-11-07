// Set the theme, the book font and the phone view
// before the page is drawn, so they do not flash:
// the theme picked with the button, or, until one
// is picked, the system's; the font from the text
// settings; the phone view from its button
// (app.js).
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
  // the phone view on a wide screen (the view
  // button in app.js): .phone, else .wide
  var phone = false;
  try {
    phone = localStorage.getItem("nxgir-phone") === "1";
  } catch (e) {}
  document.documentElement.classList.add(
    phone ? "phone" : "wide");
  try {
    var v = JSON.parse(
      localStorage.getItem("nxgir-view") || "{}");
    if (v.font) {
      document.documentElement.dataset.font = v.font;
    }
  } catch (e) {}
})();
