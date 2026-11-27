#!/usr/bin/env node
// How costly each paper is to paint on scrolling:
// notes/paper-texture.md explains the numbers.
//
// Needs `nxgir web` running (another port: BASE=)
// and Playwright with Chromium.
//
//   node scripts/measure-paper.js [book] [paper...]
//
// For each paper (default: all, and plain), a phone
// screen opens the book, jumps 8 times to a part of
// the text not yet painted, and sums the time of the
// raster tasks in a trace (ms): the work of
// painting the new tiles. SVG=1 takes the baked
// tile away (bakePaper() in app.js), to see the SVG
// layers as style.css draws them.
//
// Not a screenshot's time: a noisy picture takes
// longer to save as PNG, which is not the browser's
// work on scrolling.

const { chromium, devices } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");

const BASE = process.env.BASE ||
  "http://localhost:8765/";
const BOOK = process.argv[2] ||
  "grabar/hovhan-mamikonean/" +
  "1-patmutiun-taronoy/01.txt";
const PAPERS = process.argv.length > 3
  ? process.argv.slice(3)
  : ["plain", "papyrus", "parchment", "vellum",
    "candle"];
const JUMP = 1100;

async function measure(browser, paper) {
  const ctx = await browser.newContext({
    ...devices["Pixel 7"] });
  await ctx.addInitScript((p) => {
    localStorage.setItem("nxgir-view",
      JSON.stringify({ paper: p }));
  }, paper);
  const page = await ctx.newPage();
  await page.goto(BASE + "hy/read/" + BOOK);
  await page.waitForTimeout(3000);
  if (process.env.SVG) {
    await page.evaluate(() => {
      const s = document.documentElement.style;
      s.removeProperty("--paper-img");
      s.removeProperty("--paper-size");
    });
  }
  await page.screenshot();
  const file = path.join(os.tmpdir(),
    "nxgir-paper-trace.json");
  await browser.startTracing(page, { path: file,
    categories: ["cc",
      "disabled-by-default-devtools.timeline"] });
  for (let i = 1; i <= 8; i++) {
    await page.evaluate((y) => scrollTo(0, y),
      i * JUMP);
    // a screenshot makes the browser paint now
    await page.screenshot();
  }
  await browser.stopTracing();
  const events = JSON.parse(
    fs.readFileSync(file, "utf8")).traceEvents;
  let ms = 0;
  for (const e of events) {
    if (e.ph === "X" && e.name === "RasterTask") {
      ms += e.dur / 1000;
    }
  }
  const baked = await page.evaluate(() =>
    document.documentElement.style
      .getPropertyValue("--paper-img").length > 0);
  await ctx.close();
  return { ms, baked };
}

(async () => {
  const browser = await chromium.launch();
  for (const paper of PAPERS) {
    const r = await measure(browser, paper);
    console.log(paper.padEnd(10),
      String(Math.round(r.ms)).padStart(5), "ms",
      r.baked ? "(baked tile)" : "");
  }
  await browser.close();
})();
