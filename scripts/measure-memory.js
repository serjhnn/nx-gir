#!/usr/bin/env node
// How much browser memory the web reader takes:
// notes/browser-memory.md explains the numbers.
//
// Needs `nxgir web` running (another port: BASE=)
// and Playwright with Chromium (Linux: reads
// /proc for the memory of the processes).
//
//   node scripts/measure-memory.js parts [N]
//     the N largest parts of books/ (all if no N),
//     each read in one tab after the other: words,
//     page elements, JS heap and memory (MB)
//   node scripts/measure-memory.js fresh [N]
//     the same, each part in a fresh browser
//   node scripts/measure-memory.js why <book>
//     where the memory of one part goes
//
// PHONE=1: a phone screen (390x844, touch).

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const BASE = process.env.BASE ||
  "http://localhost:8765/";
const ROOT = path.join(__dirname, "..", "books");
const MB = (b) => (b / 1048576).toFixed(0);
const wait = (ms) =>
  new Promise((r) => setTimeout(r, ms));

// the parts of books/grabar and books/ashkharhabar,
// largest first
function parts() {
  const out = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir,
      { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith(".txt")) {
        out.push([fs.statSync(p).size,
          path.relative(ROOT, p)]);
      }
    }
  };
  walk(path.join(ROOT, "grabar"));
  walk(path.join(ROOT, "ashkharhabar"));
  return out.sort((a, b) => b[0] - a[0])
    .map((x) => x[1]);
}

// memory (PSS) of Chromium's processes:
// {renderer, total}
function pss() {
  const out = { renderer: 0, total: 0 };
  for (const pid of fs.readdirSync("/proc")) {
    if (!/^\d+$/.test(pid)) continue;
    try {
      const c = fs.readFileSync(
        `/proc/${pid}/cmdline`, "utf8");
      if (!/chrom/i.test(c.split("\0")[0])) {
        continue;
      }
      const s = fs.readFileSync(
        `/proc/${pid}/smaps_rollup`, "utf8");
      const k = +s.match(/^Pss:\s+(\d+)/m)[1];
      out.total += k * 1024;
      if (/--type=renderer/.test(c)) {
        out.renderer += k * 1024;
      }
    } catch (e) {} // gone meanwhile
  }
  return out;
}

async function open(view) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext(
    process.env.PHONE
      ? { viewport: { width: 390, height: 844 },
        isMobile: true, hasTouch: true }
      : { viewport: { width: 1400, height: 900 } });
  if (view) {
    await ctx.addInitScript((v) => {
      localStorage.setItem("nxgir-view", v);
    }, JSON.stringify(view));
  }
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Performance.enable");
  const metric = async (name) => {
    const { metrics } = await cdp.send(
      "Performance.getMetrics");
    return metrics.find((m) => m.name === name)
      .value;
  };
  return { browser, page, cdp, metric };
}

// open a part as a reader would: to its end,
// three words looked up
async function read(page, book) {
  await page.goto(BASE + "#/read/" +
    encodeURIComponent(book));
  // a handle left open keeps the page in memory
  await (await page.waitForSelector(".w",
    { timeout: 60000 })).dispose();
  await wait(500);
  await page.evaluate(async () => {
    const H = document.documentElement
      .scrollHeight;
    for (let y = 0; y <= H; y += H / 20) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 30));
    }
  });
  const n = await page.$$eval(".w",
    (a) => a.length);
  for (const i of [0, 50, 500]) {
    if (i >= n) continue;
    const w = page.locator(".w").nth(i);
    await w.scrollIntoViewIfNeeded();
    await w.click();
    await wait(250);
  }
  return n;
}

const HEAD = "part\twords\telements\theap\ttab\tall";

async function row(b, tab, book) {
  const n = book ? await read(tab.page, book) : 0;
  const p = pss();
  const heap = await tab.metric("JSHeapUsedSize");
  console.log([book || "(home)", n,
    await tab.metric("Nodes"), MB(heap),
    MB(p.renderer), MB(p.total)].join("\t"));
  b.heap = Math.max(b.heap, heap);
  b.tab = Math.max(b.tab, p.renderer);
  b.all = Math.max(b.all, p.total);
}

async function inOneTab(books) {
  const tab = await open();
  const peak = { heap: 0, tab: 0, all: 0 };
  console.log(HEAD);
  await tab.page.goto(BASE);
  await wait(1500);
  await row(peak, tab, null);
  for (const b of books) await row(peak, tab, b);
  await tab.cdp.send(
    "HeapProfiler.collectGarbage");
  await wait(1000);
  console.log(`peak: heap ${MB(peak.heap)}, tab`
    + ` ${MB(peak.tab)}, all ${MB(peak.all)} MB;`
    + " after GC: heap "
    + MB(await tab.metric("JSHeapUsedSize"))
    + ", tab " + MB(pss().renderer)
    + " MB, " + (await tab.metric("Nodes"))
    + " elements");
  await tab.browser.close();
}

async function fresh(books) {
  const peak = { heap: 0, tab: 0, all: 0 };
  console.log(HEAD);
  for (const b of books) {
    const tab = await open();
    await tab.page.goto(BASE);
    await wait(1000);
    await row(peak, tab, b);
    await tab.browser.close();
  }
  console.log(`peak: heap ${MB(peak.heap)}, tab`
    + ` ${MB(peak.tab)}, all ${MB(peak.all)} MB`);
}

// one part, once each way, after a GC
async function why(book) {
  const ways = [
    ["home page", null, "home"],
    ["side by side", { parallel: true }, ""],
    ["side by side, scrolled to the end",
      { parallel: true }, "scroll"],
    ["translation hidden (one column)",
      { parallel: false }, ""],
    ["text not laid out (display: none)",
      { parallel: true }, "hide"],
  ];
  console.log("case\telements\theap\ttab");
  for (const [label, view, how] of ways) {
    const { browser, page, cdp, metric } =
      await open(view);
    if (how === "home") {
      await page.goto(BASE);
    } else {
      await page.goto(BASE + "#/read/" +
        encodeURIComponent(book));
      await (await page.waitForSelector(".w"))
        .dispose();
    }
    if (how === "hide") {
      await page.evaluate(() => {
        document.querySelector(".text")
          .style.display = "none";
      });
    }
    if (how === "scroll") {
      await page.evaluate(async () => {
        const H = document.documentElement
          .scrollHeight;
        for (let y = 0; y <= H; y += H / 40) {
          window.scrollTo(0, y);
          await new Promise(
            (r) => setTimeout(r, 50));
        }
      });
    }
    await wait(1500);
    await cdp.send("HeapProfiler.collectGarbage");
    await wait(500);
    console.log([label, await metric("Nodes"),
      MB(await metric("JSHeapUsedSize")),
      MB(pss().renderer)].join("\t"));
    await browser.close();
  }
}

async function main() {
  const [cmd, arg] = process.argv.slice(2);
  const top = (n) => parts().slice(0,
    n ? Number(n) : undefined);
  if (cmd === "parts") await inOneTab(top(arg));
  else if (cmd === "fresh") await fresh(top(arg));
  else if (cmd === "why" && arg) await why(arg);
  else {
    console.error("usage: measure-memory.js"
      + " parts [N] | fresh [N] | why <book>");
    process.exitCode = 2;
  }
}

main();
