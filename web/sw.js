// The service worker of the published site: keeps
// the pages and files you open, so they open with no
// network, and, when asked (#/offline), every file of
// the site. build-site.py puts the build in BUILD and
// writes offline.json, the list of files.
//
// One cache for each build: a new build makes a new
// cache, fills it again if you saved everything, and
// drops the old one. Files of one build go together,
// so the app and its data never mix.

const BUILD = "dev";
const NAME = "nxgir-" + BUILD;
const META = "nxgir-meta";
// not kept: these must always come from the network
const FRESH = ["sw.js", "offline.json", "download.json",
  "nxgir-site.zip"];
// opened at once: what the first screen needs
const SHELL = ["./", "index.html", "style.css",
  "app.js", "theme.js", "fonts.css", "static.js",
  "icon.svg", "manifest.webmanifest"];

let busy = false;
let done = 0;
let total = 0;

function fresh(path) {
  return new Request(path, { cache: "reload" });
}

async function tell(msg) {
  for (const c of await self.clients.matchAll()) {
    c.postMessage(msg);
  }
}

// what the user asked: {want, total, build,
// complete}; complete is for that build
async function meta(set) {
  const cache = await caches.open(META);
  if (set) {
    await cache.put("meta", new Response(
      JSON.stringify(set)));
    return set;
  }
  const r = await cache.match("meta");
  return r ? r.json() : { want: false, total: 0 };
}

async function state() {
  const m = await meta();
  const ok = m.want && m.complete && m.build === BUILD;
  const n = (await (await caches.open(NAME)).keys())
    .length;
  return { type: "state", want: m.want, busy,
    done: busy ? done : ok ? m.total
      : Math.min(n, m.total),
    total: busy ? total : m.total,
    complete: ok && !busy };
}

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(NAME);
    await cache.addAll(SHELL.map(fresh));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) {
      if (k !== NAME && k !== META) {
        await caches.delete(k);
      }
    }
    await self.clients.claim();
    // saved everything before: fill the new build too
    if ((await meta()).want) await saveAll();
  })());
});

// every file of offline.json that is not kept yet,
// six at a time; stops quietly when a newer build is
// out (offline.json names another one)
async function saveAll() {
  if (busy) return;
  busy = true;
  try {
    const info = await (await fetch(
      fresh("offline.json"))).json();
    if (info.build !== BUILD) return;
    const cache = await caches.open(NAME);
    const todo = [];
    for (const [path] of info.files) {
      if (!await cache.match(path,
        { ignoreSearch: true })) todo.push(path);
    }
    total = info.files.length;
    done = total - todo.length;
    await meta({ want: true, total, build: BUILD,
      complete: false });
    let bad = 0;
    let last = 0;
    const work = async () => {
      while (todo.length) {
        const path = todo.pop();
        try {
          const r = await fetch(fresh(path));
          if (!r.ok) throw new Error(r.status);
          await cache.put(path, r);
          done++;
        } catch (err) {
          bad++;
        }
        if (Date.now() - last > 200) {
          last = Date.now();
          await tell(await state());
        }
      }
    };
    await Promise.all(Array.from({ length: 6 }, work));
    if (bad) done = total - bad;
    await meta({ want: true, total, build: BUILD,
      complete: bad === 0 });
  } catch (err) {
    // offline now: the next try continues
  } finally {
    busy = false;
    await tell(await state());
  }
}

self.addEventListener("message", (e) => {
  const type = e.data && e.data.type;
  if (type === "status") {
    e.waitUntil(state().then(tell));
  } else if (type === "save" || type === "resume") {
    if (type === "save") {
      e.waitUntil(meta().then((m) => meta({
        ...m, want: true })).then(saveAll));
    } else {
      e.waitUntil(meta().then((m) =>
        m.want ? saveAll() : null));
    }
  } else if (type === "clear") {
    e.waitUntil((async () => {
      await caches.delete(NAME);
      await caches.delete(META);
      await (await caches.open(NAME)).addAll(
        SHELL.map(fresh));
      await tell(await state());
    })());
  }
});

async function answer(req) {
  const cache = await caches.open(NAME);
  const hit = await cache.match(req,
    { ignoreSearch: true });
  if (hit) return hit;
  try {
    const res = await fetch(req);
    if (res.ok) {
      cache.put(req, res.clone()).catch(() => {});
    }
    return res;
  } catch (err) {
    if (req.mode === "navigate") {
      const home = await cache.match("./");
      if (home) return home;
    }
    throw err;
  }
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  const file = url.pathname.split("/").pop();
  if (FRESH.includes(file)) return;
  e.respondWith(answer(req));
});
