// The 3D map (#/map3d, map3dPage() in app.js): the
// painted picture of the Map page laid on a relief
// (img/map/height.png, scripts/render-heightmap.py)
// with three.js (vendor/three/), loaded only when
// this page is opened. The pins are buttons over the
// canvas, as on the Map page, moved as the view
// turns. It draws only when something moves.
//
// start(view, data, opts) fills the element view and
// gives { pick(id), reset(), turn(deg), tilt(deg),
// zoom(k), stop() }; opts: pins (a button for each
// place, by id) and onPick(id) for a tap on a pin.

import * as THREE from "./vendor/three/three.min.js";

// the size of the map in the scene: the picture is
// 1536x1024, so 15 x 10; how high the relief rises
const W = 15;
const D = 10;
const RISE = 1.5;
// the segments of the relief (the height map is
// 384x256: one every second pixel)
const SEG_X = 192;
const SEG_Z = 128;
// the view: distance, tilt from straight down,
// both in their limits
const DIST = [3, 22];
const TILT = [0.15, 1.25];
const HOME = { dist: 9.6, tilt: 0.78, turn: 0 };

// a picture's pixels: { w, h, px } (grey, 0-255)
async function heights(src) {
  const img = new Image();
  img.src = src;
  await img.decode();
  const c = document.createElement("canvas");
  c.width = img.width;
  c.height = img.height;
  const g = c.getContext("2d");
  g.drawImage(img, 0, 0);
  const rgba = g.getImageData(0, 0, c.width,
    c.height).data;
  const px = new Uint8Array(c.width * c.height);
  for (let i = 0; i < px.length; i++) {
    px[i] = rgba[i * 4];
  }
  return { w: c.width, h: c.height, px };
}

// the height at u, v (0-1 across and down the
// picture), smooth between pixels
function heightAt(hm, u, v) {
  const x = Math.min(hm.w - 1.001,
    Math.max(0, u * (hm.w - 1)));
  const y = Math.min(hm.h - 1.001,
    Math.max(0, v * (hm.h - 1)));
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const fx = x - x0;
  const fy = y - y0;
  const at = (i, j) => hm.px[(y0 + j) * hm.w + x0 + i];
  const top = at(0, 0) * (1 - fx) + at(1, 0) * fx;
  const low = at(0, 1) * (1 - fx) + at(1, 1) * fx;
  return (top * (1 - fy) + low * fy) / 255 * RISE;
}

// a place's x, y (percent of the picture) in the
// scene, on the ground
function spot(hm, x, y) {
  const u = x / 100;
  const v = y / 100;
  return new THREE.Vector3((u - 0.5) * W,
    heightAt(hm, u, v), (v - 0.5) * D);
}

// the color of the page behind the map
function pageColor() {
  const c = getComputedStyle(document.body)
    .backgroundColor;
  return new THREE.Color(c && c !== "rgba(0, 0, 0, 0)"
    ? c : "#faf9f5");
}

export function supported() {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2")
      || c.getContext("webgl"));
  } catch {
    return false;
  }
}

export async function start(view, data, opts) {
  const [hm, tex] = await Promise.all([
    heights(data.height),
    new THREE.TextureLoader().loadAsync(data.image),
  ]);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;

  const renderer = new THREE.WebGLRenderer({
    antialias: true, powerPreference: "low-power" });
  renderer.setPixelRatio(
    Math.min(2, window.devicePixelRatio || 1));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  const canvas = renderer.domElement;
  canvas.className = "m3-canvas";
  view.prepend(canvas);

  const scene = new THREE.Scene();
  const bg = pageColor();
  scene.background = bg;
  scene.fog = new THREE.Fog(bg, 16, 34);

  // the relief: the plane, its points raised
  const geo = new THREE.PlaneGeometry(W, D,
    SEG_X, SEG_Z);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const uv = geo.attributes.uv;
  for (let i = 0; i < pos.count; i++) {
    pos.setY(i, heightAt(hm, uv.getX(i),
      1 - uv.getY(i)));
  }
  geo.computeVertexNormals();
  const ground = new THREE.Mesh(geo,
    new THREE.MeshStandardMaterial({ map: tex,
      roughness: 0.95, metalness: 0 }));
  scene.add(ground);
  // the edge: a dark rim under the map, as a table
  const rim = new THREE.Mesh(
    new THREE.BoxGeometry(W + 0.2, 0.4, D + 0.2),
    new THREE.MeshStandardMaterial({
      color: 0x6b4a2a, roughness: 1 }));
  rim.position.y = -0.21;
  scene.add(rim);

  // light: the sky, and a low sun from the north-west
  // (the painting is lit from there) for the shadows
  // of the slopes
  scene.add(new THREE.HemisphereLight(0xfff4dc,
    0x5a4630, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff,
    1.6);
  sun.position.set(-6, 7, -5);
  scene.add(sun);

  const cam = new THREE.PerspectiveCamera(40, 1,
    0.1, 100);
  const st = { ...HOME,
    target: new THREE.Vector3(0, 0, 0.6) };
  let anim = null;
  let frame = 0;
  let alive = true;

  const place = () => {
    const s = Math.sin(st.tilt);
    cam.position.set(
      st.target.x + st.dist * s * Math.sin(st.turn),
      st.target.y + st.dist * Math.cos(st.tilt),
      st.target.z + st.dist * s * Math.cos(st.turn));
    cam.lookAt(st.target);
  };

  // the pins: over the canvas, where their place is
  const spots = new Map();
  for (const p of data.places) {
    const v = spot(hm, p.x, p.y);
    v.y += 0.02;
    spots.set(p.id, v);
  }
  const tmp = new THREE.Vector3();
  const drawPins = () => {
    const w = view.clientWidth;
    const hh = view.clientHeight;
    for (const [id, b] of opts.pins) {
      const v = spots.get(id);
      tmp.copy(v).project(cam);
      const out = tmp.z > 1 || Math.abs(tmp.x) > 1.1
        || Math.abs(tmp.y) > 1.1;
      b.classList.toggle("m3-off", out);
      b.style.left = ((tmp.x + 1) / 2 * w) + "px";
      b.style.top = ((1 - tmp.y) / 2 * hh) + "px";
      // the nearer, the bigger; the far ones behind
      const d = cam.position.distanceTo(v);
      b.style.setProperty("--inv",
        Math.max(0.6, Math.min(1.2, 9 / d)).toFixed(2));
      b.style.zIndex = String(Math.round(100 - d));
    }
    if (opts.onDraw) opts.onDraw();
  };

  const size = () => {
    const w = view.clientWidth;
    const hh = view.clientHeight;
    renderer.setSize(w, hh, false);
    cam.aspect = w / hh;
    cam.updateProjectionMatrix();
  };

  const render = () => {
    frame = 0;
    if (!alive) return;
    if (!view.isConnected) {
      stop();
      return;
    }
    if (anim) {
      const k = Math.min(1,
        (performance.now() - anim.t0) / anim.ms);
      const e = k < 0.5 ? 2 * k * k
        : 1 - (-2 * k + 2) ** 2 / 2;
      for (const key of ["dist", "tilt", "turn"]) {
        st[key] = anim.from[key]
          + (anim.to[key] - anim.from[key]) * e;
      }
      st.target.lerpVectors(anim.from.target,
        anim.to.target, e);
      if (k >= 1) anim = null;
    }
    place();
    renderer.render(scene, cam);
    drawPins();
    if (anim) ask();
  };
  const ask = () => {
    if (!frame) frame = requestAnimationFrame(render);
  };

  const keep = () => {
    st.dist = Math.min(DIST[1],
      Math.max(DIST[0], st.dist));
    st.tilt = Math.min(TILT[1],
      Math.max(TILT[0], st.tilt));
    st.target.x = Math.min(W / 2,
      Math.max(-W / 2, st.target.x));
    st.target.z = Math.min(D / 2,
      Math.max(-D / 2, st.target.z));
    st.target.y = heightAt(hm,
      st.target.x / W + 0.5, st.target.z / D + 0.5);
  };
  const go = (to, ms = 700) => {
    const from = { dist: st.dist, tilt: st.tilt,
      turn: st.turn, target: st.target.clone() };
    const end = { dist: to.dist ?? st.dist,
      tilt: to.tilt ?? st.tilt,
      turn: to.turn ?? st.turn,
      target: (to.target || st.target).clone() };
    // the short way round
    while (end.turn - from.turn > Math.PI) {
      end.turn -= 2 * Math.PI;
    }
    while (from.turn - end.turn > Math.PI) {
      end.turn += 2 * Math.PI;
    }
    anim = { from, to: end, ms,
      t0: performance.now() };
    ask();
  };

  // drag: one finger or the mouse moves the map;
  // two fingers zoom (pinch), turn (twist) and tilt
  // (both up or down); the right button or shift
  // turns and tilts
  const ac = new AbortController();
  const on = (el, ev, fn, o = {}) =>
    el.addEventListener(ev, fn,
      { ...o, signal: ac.signal });
  const ptrs = new Map();
  let two = null;
  let moved = false;
  let down = null;
  const pan = (dx, dy) => {
    const k = st.dist / view.clientHeight * 0.75;
    const c = Math.cos(st.turn);
    const s = Math.sin(st.turn);
    st.target.x -= (dx * c + dy * s) * k;
    st.target.z -= (-dx * s + dy * c) * k;
  };
  const twoOf = () => {
    const [a, b] = [...ptrs.values()];
    return { d: Math.hypot(a.x - b.x, a.y - b.y),
      a: Math.atan2(b.y - a.y, b.x - a.x),
      y: (a.y + b.y) / 2 };
  };
  on(canvas, "contextmenu", (e) => e.preventDefault());
  on(canvas, "pointerdown", (e) => {
    anim = null;
    canvas.setPointerCapture(e.pointerId);
    ptrs.set(e.pointerId, { x: e.clientX,
      y: e.clientY, turn: e.button === 2
        || e.shiftKey });
    moved = false;
    down = { x: e.clientX, y: e.clientY };
    two = ptrs.size === 2 ? twoOf() : null;
  });
  on(canvas, "pointermove", (e) => {
    const p = ptrs.get(e.pointerId);
    if (!p) return;
    const dx = e.clientX - p.x;
    const dy = e.clientY - p.y;
    p.x = e.clientX;
    p.y = e.clientY;
    if (Math.hypot(e.clientX - down.x,
      e.clientY - down.y) > 5) moved = true;
    if (ptrs.size === 2 && two) {
      const now = twoOf();
      st.dist *= two.d / now.d;
      st.turn -= now.a - two.a;
      st.tilt -= (now.y - two.y) * 0.004;
      two = now;
    } else if (ptrs.size === 1) {
      if (p.turn) {
        st.turn -= dx * 0.006;
        st.tilt -= dy * 0.004;
      } else {
        pan(dx, dy);
      }
    }
    keep();
    ask();
  });
  const lift = (e) => {
    ptrs.delete(e.pointerId);
    two = null;
  };
  on(canvas, "pointerup", lift);
  on(canvas, "pointercancel", lift);
  // a tap on the map (not a drag): no place
  on(canvas, "click", () => {
    if (!moved && opts.onPick) opts.onPick("");
  });
  on(canvas, "wheel", (e) => {
    e.preventDefault();
    anim = null;
    st.dist *= Math.exp(e.deltaY / 400);
    keep();
    ask();
  }, { passive: false });
  const ro = new ResizeObserver(() => {
    size();
    ask();
  });
  ro.observe(view);
  // the theme changed: the page's color behind
  const mo = new MutationObserver(() => {
    const c = pageColor();
    scene.background = c;
    scene.fog.color = c;
    ask();
  });
  mo.observe(document.documentElement,
    { attributes: true });

  function stop() {
    if (!alive) return;
    alive = false;
    cancelAnimationFrame(frame);
    ac.abort();
    ro.disconnect();
    mo.disconnect();
    geo.dispose();
    tex.dispose();
    ground.material.dispose();
    rim.geometry.dispose();
    rim.material.dispose();
    renderer.dispose();
    renderer.forceContextLoss();
    canvas.remove();
  }

  size();
  // the first view: from high above, coming down
  st.dist = 20;
  st.tilt = 0.3;
  keep();
  go({ dist: HOME.dist, tilt: HOME.tilt }, 1600);

  return {
    // fly to a place, a little closer
    pick(id) {
      const v = spots.get(id);
      if (!v) return;
      go({ target: v, dist: Math.min(st.dist, 7),
        tilt: Math.max(st.tilt, 0.8) });
    },
    reset() {
      go({ ...HOME,
        target: new THREE.Vector3(0, 0, 0.6) });
    },
    turn(deg) {
      go({ turn: st.turn + deg * Math.PI / 180 }, 400);
    },
    tilt(k) {
      go({ tilt: Math.min(TILT[1], Math.max(TILT[0],
        st.tilt + k)) }, 400);
    },
    zoom(k) {
      go({ dist: Math.min(DIST[1], Math.max(DIST[0],
        st.dist * k)) }, 300);
    },
    redraw: ask,
    stop,
  };
}
