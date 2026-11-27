// The fonts reel: scenes drawn on a canvas, one frame
// at a time by render(t) (t in seconds); record.js
// calls it for every frame. Captions stay in the top
// band: Instagram covers the bottom and right edges.
const W = 1080, H = 1920;
const x = document.getElementById("c").getContext("2d");
const DARK = "#1f1e1d", PAPER = "#f3e7cf";
const ACC = "#d97757", INK = "#2a1d14";
const RED = "#b22820";
const SANS = "'Helvetica Neue',Arial,sans-serif";
const NAME = "Նախագիր";
const CX = 500; // centre of the content, left of
// the buttons on the right
let D, IM = {};

const ease = (t) => t < 0 ? 0 : t > 1 ? 1
  : t * t * (3 - 2 * t);
function back(t) {
  t = Math.min(1, Math.max(0, t));
  const s = 1.7;
  return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2;
}
const fadeIO = (t, d, f = 0.4) =>
  Math.min(ease(t / f), ease((d - t) / f));

function load(src) {
  return new Promise((r) => {
    const i = new Image();
    i.onload = () => r(i);
    i.src = src;
  });
}

async function init() {
  D = window.DATA;
  IM.page = await load("build/page.jpg");
  for (const h of D.L)
    IM["l" + h] = await load(`build/l${h}.png`);
  for (const [h] of D.C)
    IM["c" + h] = await load(`build/c${h}.png`);
  for (const f of ["Dz", "Bo"])
    await document.fonts.load(`80px ${f}`, "աբգ");
  return true;
}

// [scene, start in seconds]; the last is the end
const SCENES = [
  ["title", 0], ["page", 4.5], ["cut", 10],
  ["grid", 15.5], ["avg", 21], ["caps", 26.5],
  ["font", 32], ["bolor", 38], ["outro", 42.5],
  ["end", 47],
];
const TOTAL = 47;

function rr(a, b, w, h, r) {
  x.beginPath();
  x.roundRect(a, b, w, h, r);
}

function wrap(t, w, f) {
  x.font = f;
  const o = [];
  let l = "";
  for (const s of t.split(" ")) {
    const k = l ? l + " " + s : s;
    if (x.measureText(k).width > w && l) {
      o.push(l);
      l = s;
    } else l = k;
  }
  o.push(l);
  return o;
}

function fit(t, f, px, mw) {
  x.font = px + "px " + f;
  const w = x.measureText(t).width;
  if (w > mw) x.font = Math.floor((px * mw) / w)
    + "px " + f;
}

// the caption box, under the step pill
function cap(txt, sub, a, y = 330) {
  if (a <= 0) return;
  const F1 = "600 50px " + SANS, F2 = "36px " + SANS;
  x.save();
  x.globalAlpha = a;
  const ls = wrap(txt, 900, F1);
  const ss = sub ? wrap(sub, 900, F2) : [];
  const h = ls.length * 62
    + (ss.length ? ss.length * 48 + 18 : 0) + 60;
  x.fillStyle = "rgba(20,16,14,.82)";
  rr(60, y, 960, h, 28);
  x.fill();
  x.textAlign = "center";
  x.textBaseline = "top";
  x.fillStyle = "#fff";
  x.font = F1;
  ls.forEach((l, i) =>
    x.fillText(l, 540, y + 30 + i * 62));
  x.fillStyle = "#e9c9b4";
  x.font = F2;
  const y2 = y + 30 + ls.length * 62 + 18;
  ss.forEach((l, i) => x.fillText(l, 540, y2 + i * 48));
  x.restore();
}

function step(n, a) {
  if (a <= 0) return;
  x.save();
  x.globalAlpha = a;
  x.fillStyle = ACC;
  rr(60, 250, 260, 64, 32);
  x.fill();
  x.fillStyle = "#fff";
  x.textAlign = "center";
  x.textBaseline = "middle";
  x.font = "700 34px " + SANS;
  x.fillText("STEP " + n + " / 5", 190, 283);
  x.restore();
}

function paper() {
  x.fillStyle = PAPER;
  x.fillRect(0, 0, W, H);
  const g = x.createRadialGradient(
    540, 960, 300, 540, 960, 1200);
  g.addColorStop(0, "rgba(0,0,0,0)");
  g.addColorStop(1, "rgba(90,55,20,.28)");
  x.fillStyle = g;
  x.fillRect(0, 0, W, H);
}

function dark() {
  x.fillStyle = DARK;
  x.fillRect(0, 0, W, H);
}

// the page, zoomed z times around its point fx, fy
function page(z, fx, fy) {
  const s = (W / D.pw) * z;
  x.save();
  x.translate(540 - fx * s, 960 - fy * s);
  x.scale(s, s);
  x.drawImage(IM.page, 0, 0);
  x.restore();
  return s;
}

const S = {
  title(t, d) {
    dark();
    const p = ease((t - 0.3) / 2.2);
    x.save();
    x.textAlign = "center";
    fit(NAME, "Dz", 250, 900);
    const w = x.measureText(NAME).width;
    const x0 = 540 - w / 2 - 30, len = (w + 80) * p;
    x.beginPath();
    x.rect(x0, 600, len, 500);
    x.clip();
    x.fillStyle = PAPER;
    x.fillText(NAME, 540, 960);
    x.restore();
    if (p > 0 && p < 1) { // the pen
      x.fillStyle = ACC;
      x.beginPath();
      x.arc(x0 + len, 900, 10, 0, 7);
      x.fill();
    }
    cap("We turned a 400-year-old scribe's hand"
      + " into a font",
      "Two fonts, made for reading classical Armenian",
      ease((t - 1) / 0.5));
    return Math.min(1, ease((d - t) / 0.35));
  },

  page(t, d) {
    dark();
    const e = ease(t / d);
    page(1 + 0.9 * e, D.pw / 2 - 110 * e,
      D.ph / 2 - 150 * e);
    cap("A book of Gospels on paper, early 17th century",
      "Walters Art Museum, Ms. W.541"
      + " · the images are free (CC0)",
      fadeIO(t - 0.4, d - 0.4, 0.4));
    return fadeIO(t, d, 0.35);
  },

  cut(t, d) {
    dark();
    const s = page(1.9, 240, 360);
    const n = Math.floor(
      D.boxes.length * ease((t - 0.3) / 3.5));
    x.save();
    x.translate(540 - 240 * s, 960 - 360 * s);
    x.scale(s, s);
    x.lineWidth = 4 / s;
    for (let i = 0; i < n; i++) {
      const [a, b, w, h] = D.boxes[i];
      const blue = i % 3 === 0;
      x.strokeStyle = blue ? "#3b8fd9" : ACC;
      x.fillStyle = blue ? "rgba(59,143,217,.18)"
        : "rgba(217,119,87,.18)";
      x.fillRect(a - 1, b - 1, w + 2, h + 2);
      x.strokeRect(a - 1, b - 1, w + 2, h + 2);
    }
    x.restore();
    step(1, fadeIO(t, d, 0.3));
    cap("Cut the black ink into pieces",
      `this page: ${n} · about 6,300 from 11 pages`,
      fadeIO(t - 0.2, d - 0.2, 0.3));
    return fadeIO(t, d, 0.35);
  },

  grid(t, d) {
    paper();
    const cols = 7, cw = 115, ch = 135;
    const x0 = CX - (cols * cw) / 2;
    D.L.forEach((h, i) => {
      const a = (t - 0.3 - i * 0.09) / 0.45;
      if (a <= 0) return;
      const im = IM["l" + h], sc = 0.31 * back(a);
      x.save();
      x.globalAlpha = ease(a);
      x.translate(x0 + cw * (i % cols) + cw / 2,
        790 + ch * Math.floor(i / cols));
      x.scale(sc, sc);
      x.drawImage(im, -im.width / 2, -288);
      x.restore();
    });
    step(2, fadeIO(t, d, 0.3));
    cap("Group them by shape, then match every line"
      + " to the printed text",
      "460 lines found on 27 pages:"
      + " each piece learns its letter",
      fadeIO(t - 0.4, d - 0.4, 0.3));
    return fadeIO(t, d, 0.35);
  },

  // an illustration: the average, shifted 14 times
  avg(t, d) {
    paper();
    const im = IM.l0561, p = ease((t - 0.4) / 3);
    const R = [
      [-40, 25, -0.12], [35, -30, 0.1], [-20, -45, 0.06],
      [50, 20, -0.08], [-55, -10, 0.15], [15, 40, -0.05],
      [30, 10, 0.13], [-35, 35, 0.04], [45, -50, -0.1],
      [-10, -25, 0.09], [60, 45, 0.02], [-60, 50, -0.14],
      [20, -60, 0.07], [0, 30, -0.03],
    ];
    const sc = 1.6, q = (1 - p) * 2.2;
    x.save();
    x.translate(CX, 1080);
    for (const [dx, dy, r] of R) {
      x.save();
      x.globalAlpha = 0.18 + 0.06 * p;
      x.translate(dx * q, dy * q);
      x.rotate(r * (1 - p));
      x.scale(sc, sc);
      x.drawImage(im, -im.width / 2, -288);
      x.restore();
    }
    if (p > 0.9) {
      x.globalAlpha = (p - 0.9) * 10;
      x.scale(sc, sc);
      x.drawImage(im, -im.width / 2, -288);
    }
    x.restore();
    x.save();
    x.textAlign = "center";
    x.fillStyle = INK;
    x.font = "600 44px " + SANS;
    x.globalAlpha = fadeIO(t, d, 0.3);
    const k = Math.min(14, 1 + Math.floor(t * 5));
    x.fillText(p < 0.98 ? `copies of ա: ${k}`
      : "ա · his average", CX, 720);
    x.restore();
    step(3, fadeIO(t, d, 0.3));
    cap("Lay up to 14 copies of each letter"
      + " over each other",
      "and keep the ink most of them share",
      fadeIO(t - 0.4, d - 0.4, 0.3));
    return fadeIO(t, d, 0.35);
  },

  caps(t, d) {
    paper();
    const cols = 6, cw = 130, ch = 135;
    const x0 = CX - (cols * cw) / 2;
    D.C.forEach(([h, w, hh], i) => {
      const a = (t - 0.3 - i * 0.08) / 0.45;
      if (a <= 0) return;
      const s = Math.min(110 / w, 115 / hh) * back(a);
      x.save();
      x.globalAlpha = ease(a);
      x.translate(x0 + cw * (i % cols) + cw / 2,
        740 + ch * Math.floor(i / cols));
      x.scale(s, s);
      x.drawImage(IM["c" + h], -w / 2, -hh / 2);
      x.restore();
    });
    step(4, fadeIO(t, d, 0.3));
    cap("His red initials became the capitals",
      "185 pages read again for the red ink alone",
      fadeIO(t - 0.4, d - 0.4, 0.3));
    return fadeIO(t, d, 0.35);
  },

  font(t, d) {
    paper();
    const L = [NAME, "Բարի եկաք", "թագաւոր",
      "վարդապետ", "գիրք եւ գրիչ"];
    const all = L.join("").length;
    let k = Math.floor(all * ease((t - 0.3) / 3.6));
    x.save();
    x.textAlign = "center";
    L.forEach((l, i) => {
      const s = l.slice(0, Math.max(0, k));
      k -= l.length;
      if (i) x.font = "108px Dz";
      else fit(l, "Dz", 170, 900);
      x.fillStyle = i ? INK : RED;
      x.fillText(s, CX, i ? 900 + i * 130 : 850);
    });
    x.restore();
    step(5, fadeIO(t, d, 0.3));
    cap("Trace every letter to curves: nxGir Dzeragir",
      "every letter is the scribe's own,"
      + " in a font you can type",
      fadeIO(t - 0.4, d - 0.4, 0.3));
    return fadeIO(t, d, 0.35);
  },

  bolor(t, d) {
    paper();
    x.save();
    x.textAlign = "center";
    x.globalAlpha = ease((t - 0.2) / 1);
    fit(NAME, "Bo", 170, 900);
    x.fillStyle = RED;
    x.fillText(NAME, CX, 780);
    x.fillStyle = INK;
    x.font = "108px Bo";
    ["Բարի եկաք", "թագաւոր", "վարդապետ"].forEach(
      (l, i) => x.fillText(l, CX, 960 + i * 140));
    x.restore();
    const a = fadeIO(t, d, 0.3);
    x.save(); // the nib at 35°
    x.globalAlpha = a;
    x.translate(860, 620);
    x.rotate((-35 * Math.PI) / 180);
    x.fillStyle = ACC;
    x.fillRect(-45, -7, 90, 14);
    x.restore();
    x.save();
    x.globalAlpha = a;
    x.fillStyle = ACC;
    x.font = "600 32px " + SANS;
    x.textAlign = "center";
    x.fillText("35°", 860, 690);
    x.restore();
    cap("And a second one: nxGir Bolorgir",
      "printed letters written again"
      + " with a broad pen at 35°",
      fadeIO(t - 0.3, d - 0.3, 0.3));
    return fadeIO(t, d, 0.35);
  },

  outro(t, d) {
    dark();
    x.save();
    x.textAlign = "center";
    x.globalAlpha = ease(t / 0.6);
    x.fillStyle = ACC;
    fit(NAME, "Dz", 210, 900);
    x.fillText(NAME, 540, 660);
    x.font = "600 64px " + SANS;
    x.fillText("nxGir", 540, 770);
    x.globalAlpha = ease((t - 0.6) / 0.6);
    x.fillStyle = PAPER;
    x.font = "44px " + SANS;
    x.fillText("Read classical Armenian books",
      540, 930);
    x.fillText("in both fonts, free and open", 540, 990);
    x.globalAlpha = ease((t - 1.2) / 0.6);
    x.fillStyle = "#fff";
    x.font = "700 76px " + SANS;
    x.fillText("nxgir.am", 540, 1160);
    x.restore();
    return Math.min(1, ease((d - t) / 0.5));
  },

  end() {
    dark();
    return 1;
  },
};

function render(T) {
  x.globalAlpha = 1;
  x.clearRect(0, 0, W, H);
  let i = SCENES.length - 2;
  for (let j = 0; j < SCENES.length - 1; j++)
    if (T < SCENES[j + 1][1]) {
      i = j;
      break;
    }
  const [n, s] = SCENES[i];
  const d = SCENES[i + 1][1] - s;
  x.save();
  const o = S[n](T - s, d);
  x.restore();
  if (o < 1) { // fade through black
    x.fillStyle = `rgba(0,0,0,${1 - o})`;
    x.fillRect(0, 0, W, H);
  }
}
window.TOTAL = TOTAL;
