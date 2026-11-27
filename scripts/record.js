// Record a short tutorial video of the web reader.
// Run through scripts/record-web.py, which starts the
// server; by hand:
//
//   node scripts/record.js http://localhost:8088 out/
//   node scripts/record.js URL out/ fonts
//
// The third argument is the story: "tour" (the
// default, the whole site) or "fonts" (the fonts,
// themes and papers).
// Needs `npm install playwright`. Writes a .webm to
// the folder. A fake cursor and captions are drawn
// into the page, as the video has no mouse.
// Edit STEPS below (the captions are in English).
const { chromium } = require("playwright");
const [BASE, OUT, STORY = "tour"] =
  process.argv.slice(2);
const BOOK = "/en/read/grabar/smbat-sparapet/" +
  "2-taregirk/01.txt";

const INIT = `
(() => {
  const mk = () => {
    if (!document.documentElement ||
        document.getElementById("rec-cur")) return;
    const c = document.createElement("div");
    c.id = "rec-cur";
    Object.assign(c.style, {
      position: "fixed", zIndex: 2147483647,
      width: "22px", height: "22px",
      borderRadius: "50%", left: "-50px",
      top: "-50px", border: "2px solid #fff",
      background: "rgba(214,90,50,.55)",
      boxShadow: "0 0 6px rgba(0,0,0,.5)",
      pointerEvents: "none",
      transform: "translate(-50%,-50%)",
      transition: "width .12s,height .12s",
    });
    const k = document.createElement("div");
    k.id = "rec-cap";
    Object.assign(k.style, {
      position: "fixed", zIndex: 2147483646,
      left: "50%", bottom: "26px",
      transform: "translateX(-50%)",
      maxWidth: "80%", padding: "12px 22px",
      borderRadius: "12px", color: "#fff",
      background: "rgba(20,16,14,.85)",
      font: "600 24px Inter,system-ui,sans-serif",
      textAlign: "center", opacity: "0",
      transition: "opacity .3s",
      pointerEvents: "none",
    });
    document.documentElement.append(c, k);
    addEventListener("mousemove", (e) => {
      c.style.left = e.clientX + "px";
      c.style.top = e.clientY + "px";
    }, true);
    addEventListener("mousedown", () => {
      c.style.width = c.style.height = "34px";
    }, true);
    addEventListener("mouseup", () => {
      c.style.width = c.style.height = "22px";
    }, true);
  };
  document.addEventListener("DOMContentLoaded", mk);
  setInterval(mk, 300);
})();
`;

// the moves of a story: wait, captions, the mouse
function kit(p) {
  const wait = (ms) => p.waitForTimeout(ms);
  const cap = (txt) => p.evaluate((t) => {
    const k = document.getElementById("rec-cap");
    if (!k) return;
    if (t) k.textContent = t;
    k.style.opacity = t ? "1" : "0";
  }, txt);
  // a button in the sticky toolbar's card never
  // counts as stable: it is in view, go on
  const go = async (loc) => {
    await loc.scrollIntoViewIfNeeded(
      { timeout: 1500 }).catch(() => {});
    const r = await loc.boundingBox();
    await p.mouse.move(r.x + r.width / 2,
      r.y + r.height / 2, { steps: 25 });
    await wait(250);
  };
  const down = async () => {
    await p.mouse.down();
    await wait(90);
    await p.mouse.up();
  };
  const click = async (loc) => {
    await go(loc);
    await down();
  };
  const scroll = async (dy, n = 10) => {
    for (let i = 0; i < n; i++) {
      await p.mouse.wheel(0, dy / n);
      await wait(40);
    }
  };
  const home = async () => {
    await p.goto(BASE + "/en/");
    await p.waitForSelector(".nxgir");
  };
  return { wait, cap, go, down, click, scroll, home };
}

// the whole site, about 70 s
async function tour(p) {
  const { wait, cap, down, click, scroll, home } =
    kit(p);

  await home();
  await wait(800);
  await cap("nxGir: a free library of Grabar, " +
    "classical Armenian");
  await wait(3200);
  await cap("Language: Armenian, English, Russian");
  await click(p.locator('a[hreflang="ru"]').first());
  await wait(1800);
  await click(p.locator('a[hreflang="en"]').first());
  await wait(1400);

  await cap("Search all books at once");
  await click(p.getByPlaceholder(/Search/).first());
  await p.keyboard.type("թագավոր", { delay: 140 });
  await p.keyboard.press("Enter");
  await wait(2500);
  await cap("Modern spelling finds the old one " +
    "(թագավոր finds թագաւոր)");
  await scroll(500);
  await wait(2600);

  await cap("The Library: every book by author");
  await home();
  await wait(600);
  await click(p.getByRole("link", { name: /^Library/ })
    .first());
  await wait(1600);
  await scroll(600, 14);
  await wait(1500);

  await cap("Open a book: Smbat Sparapet, Chronicle");
  await p.goto(BASE + BOOK);
  await p.waitForSelector(".pl");
  await wait(2200);
  await cap("Grabar on the left, our modern " +
    "Armenian translation on the right");
  await wait(3600);

  // words are not elements: click a point in the text
  await cap("Tap any word to look it up");
  const bb = await p.locator('.pl[data-l="4"]')
    .boundingBox();
  await p.mouse.move(bb.x + 170, bb.y + 12,
    { steps: 25 });
  await wait(300);
  await down();
  await p.waitForSelector(".panel .entry",
    { timeout: 5000 }).catch(() => {});
  await wait(3800);
  await cap("Short forms, meanings, and how often " +
    "it is in the book");
  await wait(3500);

  await cap("Bookmark a word, or add a note");
  await click(p.locator(".panel")
    .getByRole("button", { name: /Bookmark/ }).first());
  await wait(2800);

  await cap("Contents: jump between chapters");
  await click(p.getByRole("button",
    { name: /Contents/ }).first());
  await wait(2800);

  await cap("Change the text size");
  await click(p.getByRole("button",
    { name: "Text settings" }).first());
  await wait(900);
  const big = p.getByRole("button",
    { name: "Bigger text" }).first();
  await click(big);
  await wait(400);
  await click(big);
  await wait(3000);

  await cap("Themes, and papers like an old book");
  // the theme menu: dark, black, a paper, and
  // back to light
  const th = p.locator("#theme");
  for (const pick of ["dark", "black",
    "paper:parchment", "paper:plain", "light"]) {
    await click(th);
    await wait(500);
    await click(p.locator(
      `.theme-list [data-pick="${pick}"]`));
    await wait(1400);
  }

  await cap("The map of the Armenian Highland");
  await p.goto(BASE + "/en/map");
  await p.waitForSelector(".pin");
  await wait(2800);
  await click(p.locator(".pin").nth(3));
  await wait(3200);

  await cap("Where you stopped is saved. " +
    "Happy reading!");
  await home();
  await wait(3800);
  await cap("");
  await wait(500);
}

// the fonts, the themes and the papers, about 60 s
async function fonts(p) {
  const { wait, cap, click, scroll, home } = kit(p);
  const more = p.getByRole("button",
    { name: "Text settings" }).first();
  // the settings card, open or shut: scrolling the
  // page shuts it too, so look before clicking
  const settings = async (on) => {
    const open = await p.locator(".tools.open")
      .count() > 0;
    if (open !== on) await click(more);
    if (on) {
      await p.locator(".view .font-pick")
        .waitFor({ state: "visible" });
    }
    await wait(400);
  };
  // the font list in the card, then one font by its
  // name; the card shut after it
  const font = async (name, text) => {
    await settings(true);
    await click(p.locator(".view .font-pick"));
    await wait(700);
    await cap(text);
    await click(p.locator(".view .font-opt")
      .filter({ hasText: name }).first());
    await wait(500);
    await settings(false);
    await wait(1900);
  };
  const pick = async (what) => {
    await click(p.locator("#theme"));
    await wait(600);
    await click(p.locator(
      `.theme-list [data-pick="${what}"]`));
    await wait(1200);
  };

  await p.goto(BASE + BOOK);
  await p.waitForSelector(".pl");
  // the contents open beside the text on a wide
  // screen: shut, and the text filling the screen
  await p.locator(".panel .close").click()
    .catch(() => {});
  await p.mouse.move(640, 420);
  await scroll(330, 6);
  await wait(500);
  await cap("New in nxGir: fonts and themes");
  await wait(2400);

  await cap("Text settings: the fonts of the books");
  await settings(true);
  await wait(500);
  await click(p.locator(".view .font-pick"));
  await wait(1200);
  await cap("Each font is shown in its own letters");
  await wait(2600);
  await click(p.locator(".view .font-pick"));
  await settings(false);

  await font("nxGir Bolorgir", "nxGir Bolorgir: " +
    "our own font, written with a broad pen");
  await font("nxGir Dzeragir", "nxGir Dzeragir: " +
    "the hand of a 17th-century scribe");
  await cap("Traced letter by letter from " +
    "a manuscript (Walters Ms. W.541)");
  await wait(2200);
  await font("nxGir Dzeragir Thin", "nxGir " +
    "Dzeragir Thin: the same hand, a finer pen");
  await font("Arian Grqi", "Or a printed book " +
    "face: Arian Grqi, Noto, Garamond...");

  await cap("Themes: light, dark and black");
  await settings(true);
  await pick("dark");
  await pick("black");
  await cap("Papers behind the page: papyrus, " +
    "old book, vellum, candlelight");
  for (const k of ["papyrus", "parchment",
    "vellum", "candle"]) {
    await pick("paper:" + k);
  }
  await settings(false);
  await wait(1800);

  await cap("The theme and the paper hold on " +
    "every page");
  await home();
  await wait(1200);
  await click(p.getByRole("link", { name: /^Library/ })
    .first());
  await wait(2400);
  await click(p.locator("#theme"));
  await wait(600);
  await click(p.locator(
    '.theme-list [data-pick="paper:plain"]'));
  await wait(900);
  await click(p.locator("#theme"));
  await wait(600);
  await click(p.locator(
    '.theme-list [data-pick="light"]'));
  await wait(1200);
  await cap("nxgir.am · Happy reading!");
  await wait(2600);
  await cap("");
  await wait(500);
}

const STORIES = { tour, fonts };

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: {
      dir: OUT, size: { width: 1280, height: 720 } },
    colorScheme: "light",
  });
  await ctx.addInitScript(INIT);
  if (!STORIES[STORY]) {
    throw new Error("no story " + STORY);
  }
  await STORIES[STORY](await ctx.newPage());
  await ctx.close();
  await b.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
