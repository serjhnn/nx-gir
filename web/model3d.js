// The 3D reconstructions (#/3d/<id>, model3dPage()
// in app.js): a monastery or a castle built in code
// from old photographs and plans, one module each in
// web/models/ (listed in web/models/models.json),
// drawn with three.js (vendor/three/), loaded only
// when the page is opened.
//
// A model's module exports build(kit), which gives
// { group, labels, view }: the buildings (metres, y
// up, x to the east, z to the south), the names
// shown over them ([{ id, at: [x, y, z], names }]),
// and the first view ({ target, dist, tilt, turn }).
// kit has three.js and helpers for stone and roofs
// (below), so a model is only its shapes.
//
// start(view, mod, opts) fills the element view and
// gives { reset(), turn(deg), zoom(k), focus(id),
// stop() }; opts: tags (a button for each label, by
// id). It draws only when something moves.

import * as THREE from "./vendor/three/three.min.js";

// -- textures, painted on a canvas: no files --

// a random generator with a seed: the same stones
// every time
function rnd(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function canvas(w, h) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return [c, c.getContext("2d")];
}

// noise that tiles: the same at x and x + N, values
// 0 to 1, made of `oct` layers
function noiser(seed, N) {
  const r = rnd(seed);
  const G = 64;
  const grid = new Float32Array(G * G).map(() => r());
  const at = (i, j) =>
    grid[((j % G) + G) % G * G + ((i % G) + G) % G];
  const one = (x, y, cells) => {
    const fx = x / N * cells;
    const fy = y / N * cells;
    const i = Math.floor(fx);
    const j = Math.floor(fy);
    let u = fx - i;
    let v = fy - j;
    u = u * u * (3 - 2 * u);
    v = v * v * (3 - 2 * v);
    const w = (a) => a % cells;
    const a = at(w(i), w(j));
    const b = at(w(i + 1), w(j));
    const c = at(w(i), w(j + 1));
    const d = at(w(i + 1), w(j + 1));
    return (a + (b - a) * u) * (1 - v)
      + (c + (d - c) * u) * v;
  };
  return (x, y, base = 4, oct = 4) => {
    let s = 0;
    let amp = 0.5;
    let cells = base;
    let tot = 0;
    for (let o = 0; o < oct; o++) {
      s += one(x, y, cells) * amp;
      tot += amp;
      amp *= 0.5;
      cells *= 2;
    }
    return s / tot;
  };
}

function hexRGB(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [n >> 16, (n >> 8) & 255, n & 255];
}

// a texture of stones, and its relief (a normal
// map): the joints are low, the stones' edges worn,
// with grain, stains and streaks of weather. One
// picture is o.size metres square. o.rows: courses;
// o.check: light and dark stones in turn (the
// drums); o.rough: rubble, stones of any size
function stoneTex(o) {
  const N = 512;
  const r = rnd(o.seed || 7);
  const nz = noiser((o.seed || 7) + 101, N);
  const col = new Float32Array(N * N * 3);
  const hgt = new Float32Array(N * N);
  const mort = hexRGB(o.mortar);
  // the joints first
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const k = y * N + x;
      const n = 0.8 + 0.4 * nz(x, y, 32, 3);
      col.set(mort.map((c) => c * n), k * 3);
      hgt[k] = 0.05 * n;
    }
  }
  const rows = o.rows;
  const joint = o.rough ? 5 : 2.5;
  // the courses: equal, or of uneven height
  const ys = [0];
  for (let i = 1; i < rows; i++) {
    const even = N / rows * i;
    ys.push(o.rough ? even + (r() - 0.5) * N / rows
      * 0.5 : even);
  }
  ys.push(N);
  for (let row = 0; row < rows; row++) {
    const y0 = ys[row];
    const y1 = ys[row + 1];
    const rh = y1 - y0;
    let x = o.check ? (row % 2) * rh * 0.8 : r() * 60;
    const end = x + N;
    let j = 0;
    while (x < end - rh * 0.6) {
      let w = o.check ? rh * 1.6
        : rh * (o.rough ? 0.8 + r() * 1.6
          : 1.3 + r() * 1.5);
      if (x + w > end - rh * 0.6) w = end - x;
      const dark = o.check && (j++ + row) % 2;
      const base = hexRGB(dark ? o.dark : o.light);
      const v = 1 + (r() - 0.5) * o.vary;
      // a block stained by the weather, from its top
      const stain = r() < 0.2 ? 0.06 + r() * 0.12 : 0;
      // the corners of rubble are round
      const rad = o.rough ? rh * (0.2 + r() * 0.25)
        : 2;
      const sx = r() * 400;
      for (let yy = Math.ceil(y0 + joint / 2);
        yy < y1 - joint / 2; yy++) {
        for (let xx = Math.ceil(x + joint / 2);
          xx < x + w - joint / 2; xx++) {
          // the distance to the stone's edge
          const dx = Math.min(xx - x, x + w - xx)
            - joint / 2;
          const dy = Math.min(yy - y0, y1 - yy)
            - joint / 2;
          let d = Math.min(dx, dy);
          if (dx < rad && dy < rad) {
            d = rad - Math.hypot(rad - dx, rad - dy);
          }
          if (d <= 0) continue;
          const px = ((xx % N) + N) % N;
          const k = yy * N + px;
          const g = nz(px + sx, yy, 16, 4);
          const fine = nz(px, yy, 128, 2);
          const edge = Math.min(1, d / 6);
          const big = nz(px, yy, 2, 2);
          let lum = v * (0.8 + 0.28 * g + 0.1 * fine)
            * (0.9 + 0.1 * edge) * (0.88 + 0.24 * big);
          if (stain) {
            const t = (yy - y0) / rh;
            const streak = nz(px * 4, yy * 0.2, 8, 2);
            lum *= 1 - stain * (1 - t) * (0.6 + streak);
          }
          col[k * 3] = base[0] * lum;
          col[k * 3 + 1] = base[1] * lum;
          col[k * 3 + 2] = base[2] * lum;
          // high in the middle, worn at the edges
          hgt[k] = 0.35 + 0.55 * Math.sqrt(edge)
            + 0.1 * g;
        }
      }
      x += w;
    }
  }
  // lichen and dirt, a few spots
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const k = y * N + x;
      const sp = nz(x + 900, y + 300, 24, 3);
      if (sp > 0.68) {
        const a = Math.min(1, (sp - 0.68) * 6)
          * (o.moss || 0.25);
        col[k * 3] = col[k * 3] * (1 - a) + 110 * a;
        col[k * 3 + 1] = col[k * 3 + 1] * (1 - a)
          + 104 * a;
        col[k * 3 + 2] = col[k * 3 + 2] * (1 - a)
          + 70 * a;
      }
    }
  }
  const [c, g] = canvas(N, N);
  const img = g.createImageData(N, N);
  const [c2, g2] = canvas(N, N);
  const nimg = g2.createImageData(N, N);
  const H = (x, y) => hgt[((y + N) % N) * N
    + (x + N) % N];
  const str = o.relief || 3;
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const k = y * N + x;
      for (let i = 0; i < 3; i++) {
        img.data[k * 4 + i] = Math.max(0,
          Math.min(255, col[k * 3 + i]));
      }
      img.data[k * 4 + 3] = 255;
      // the slope of the relief, as a normal
      const ddx = (H(x - 1, y) - H(x + 1, y)) * str;
      const ddy = (H(x, y + 1) - H(x, y - 1)) * str;
      const l = Math.hypot(ddx, ddy, 1);
      nimg.data[k * 4] = (ddx / l * 0.5 + 0.5) * 255;
      nimg.data[k * 4 + 1] = (ddy / l * 0.5 + 0.5) * 255;
      nimg.data[k * 4 + 2] = (1 / l * 0.5 + 0.5) * 255;
      nimg.data[k * 4 + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  g2.putImageData(nimg, 0, 0);
  const tex = (cv, srgb) => {
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    t.repeat.set(1 / o.size, 1 / o.size);
    return t;
  };
  return { map: tex(c, true), normalMap: tex(c2, false) };
}

// the ground's grain: grass, earth and stones, grey
// round 1, to multiply the colors of the slopes
function groundTex() {
  const N = 512;
  const nz = noiser(61, N);
  const r = rnd(62);
  const [c, g] = canvas(N, N);
  const img = g.createImageData(N, N);
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      const k = (y * N + x) * 4;
      const big = nz(x, y, 4, 3);
      const fine = nz(x, y, 96, 2);
      const blade = r() * 0.16;
      let l = 0.78 + 0.25 * big + 0.2 * fine + blade;
      let warm = 1 + (big - 0.5) * 0.25;
      // bare earth and stones in patches
      if (nz(x + 500, y, 12, 3) > 0.62) {
        l *= 0.92;
        warm *= 1.08;
      }
      img.data[k] = Math.min(255, 200 * l * warm);
      img.data[k + 1] = Math.min(255, 200 * l);
      img.data[k + 2] = Math.min(255,
        200 * l / warm * 0.94);
      img.data[k + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

// a color #rrggbb lighter (v > 0) or darker
function shade(hex, v) {
  const n = parseInt(hex.slice(1), 16);
  const f = (x) => Math.max(0, Math.min(255,
    Math.round(x * (1 + v))));
  return "rgb(" + f(n >> 16) + "," + f((n >> 8) & 255)
    + "," + f(n & 255) + ")";
}

// the materials a model takes by name
function materials() {
  const m = (t, o = {}) => new THREE.MeshStandardMaterial(
    { map: t.map, normalMap: t.normalMap,
      normalScale: new THREE.Vector2(1, 1),
      roughness: 0.95, metalness: 0, ...o });
  return {
    // dressed grey stone, the walls of the churches
    stone: m(stoneTex({ rows: 6, size: 3,
      light: "#857d71", dark: "#655e55", vary: 0.16,
      mortar: "#625b52", seed: 3 })),
    // lighter ashlar: the porch and the belfry
    ashlar: m(stoneTex({ rows: 5, size: 3,
      light: "#a0988a", dark: "#7d7569", vary: 0.12,
      mortar: "#7a7266", seed: 11 })),
    // light and dark stones in turn: the drums
    band: m(stoneTex({ rows: 6, size: 3, check: true,
      light: "#b5ab98", dark: "#4f4840", vary: 0.15,
      mortar: "#a49a8a", seed: 5 })),
    // rough rubble: the walls of the enclosure
    rubble: m(stoneTex({ rows: 9, size: 4,
      rough: true, moss: 0.35, relief: 4,
      light: "#8e8270", dark: "#6c6152", vary: 0.35,
      mortar: "#a39784", seed: 17 })),
    // stone slabs of the cones and roofs
    roof: m(stoneTex({ rows: 10, size: 2.5,
      light: "#5b5650", dark: "#3e3a36", vary: 0.25,
      mortar: "#2d2a27", seed: 23 })),
    // white marble slabs on the porch
    marble: new THREE.MeshStandardMaterial({
      color: 0xeae4d6, roughness: 0.5 }),
    // openings and windows: dark
    hole: new THREE.MeshStandardMaterial({
      color: 0x17130f, roughness: 1 }),
    wood: new THREE.MeshStandardMaterial({
      color: 0x5a3e26, roughness: 0.9 }),
    bronze: new THREE.MeshStandardMaterial({
      color: 0x9a7a3c, roughness: 0.45,
      metalness: 0.6 }),
    // the paving of the court
    court: m(stoneTex({ rows: 10, size: 4,
      rough: true, moss: 0.2,
      light: "#a39682", dark: "#8f846f", vary: 0.2,
      mortar: "#7d735f", seed: 31 })),
    // a flat roof of earth with grass on it
    earth: m(stoneTex({ rows: 16, size: 5,
      rough: true, moss: 0.6, relief: 1.2,
      light: "#86794f", dark: "#6a6844", vary: 0.3,
      mortar: "#77704c", seed: 37 })),
    leaf: new THREE.MeshStandardMaterial({
      color: 0x5d6b34, roughness: 1,
      flatShading: true }),
  };
}

// -- shapes, all measured in metres --

// the texture coordinates of a box in metres, so a
// stone is the same size on every face
function boxUV(geo, w, h, d) {
  const uv = geo.attributes.uv;
  // faces: +x, -x, +y, -y, +z, -z; 4 points each
  const size = [[d, h], [d, h], [w, d], [w, d],
    [w, h], [w, h]];
  for (let f = 0; f < 6; f++) {
    for (let i = 0; i < 4; i++) {
      const k = f * 4 + i;
      uv.setXY(k, uv.getX(k) * size[f][0],
        uv.getY(k) * size[f][1]);
    }
  }
  return geo;
}

// the same for a cylinder or a cone: around, up
function roundUV(geo, r, h) {
  const uv = geo.attributes.uv;
  const around = 2 * Math.PI * r;
  for (let k = 0; k < uv.count; k++) {
    uv.setXY(k, uv.getX(k) * around, uv.getY(k) * h);
  }
  return geo;
}

function makeKit(mats) {
  const mesh = (geo, mat) => {
    const m = new THREE.Mesh(geo,
      typeof mat === "string" ? mats[mat] : mat);
    m.castShadow = true;
    m.receiveShadow = true;
    return m;
  };
  const at = (m, x, y, z, ry = 0) => {
    m.position.set(x, y, z);
    m.rotation.y = ry;
    return m;
  };
  const kit = {
    THREE,
    mats,
    mesh,
    // a box w (x) by h by d (z), standing on y
    box(w, h, d, mat, x, y, z, ry = 0) {
      const g = boxUV(new THREE.BoxGeometry(w, h, d),
        w, h, d);
      g.translate(0, h / 2, 0);
      return at(mesh(g, mat), x, y, z, ry);
    },
    // a round or many-sided tower, standing on y
    cyl(r, h, sides, mat, x, y, z, r2 = r) {
      const g = roundUV(new THREE.CylinderGeometry(
        r2, r, h, sides), r, h);
      g.translate(0, h / 2, 0);
      return at(mesh(g, mat), x, y, z);
    },
    // a cone roof, standing on y
    cone(r, h, sides, mat, x, y, z) {
      const g = roundUV(new THREE.ConeGeometry(
        r, h, sides), r, Math.hypot(r, h));
      g.translate(0, h / 2, 0);
      return at(mesh(g, mat), x, y, z);
    },
    // a roof of two slopes: w long (x), d across,
    // h high, standing on y
    gable(w, h, d, mat, x, y, z, ry = 0) {
      const s = new THREE.Shape();
      s.moveTo(-d / 2, 0);
      s.lineTo(d / 2, 0);
      s.lineTo(0, h);
      s.closePath();
      const g = new THREE.ExtrudeGeometry(s,
        { depth: w, bevelEnabled: false });
      g.translate(0, 0, -w / 2);
      g.rotateY(Math.PI / 2);
      return at(mesh(g, mat), x, y, z, ry);
    },
    // a wall w long (x), h high, t thick, with n
    // arched openings aw wide and ah high (to the
    // top of the arch), from sill up; standing on y
    arcade(w, h, t, n, aw, ah, mat, x, y, z,
      ry = 0, sill = 0) {
      const s = new THREE.Shape();
      s.moveTo(-w / 2, 0);
      s.lineTo(w / 2, 0);
      s.lineTo(w / 2, h);
      s.lineTo(-w / 2, h);
      s.closePath();
      const step = w / n;
      for (let i = 0; i < n; i++) {
        const cx = -w / 2 + step * (i + 0.5);
        const p = new THREE.Path();
        const r = aw / 2;
        p.moveTo(cx - r, sill);
        p.lineTo(cx + r, sill);
        p.lineTo(cx + r, sill + ah - r);
        p.absarc(cx, sill + ah - r, r, 0, Math.PI,
          false);
        p.lineTo(cx - r, sill);
        s.holes.push(p);
      }
      const g = new THREE.ExtrudeGeometry(s,
        { depth: t, bevelEnabled: false,
          curveSegments: 10 });
      g.translate(0, 0, -t / 2);
      return at(mesh(g, mat), x, y, z, ry);
    },
    // a dark window or door, set on a wall's face
    hole(w, h, x, y, z, ry = 0) {
      return kit.box(w, h, 0.12, "hole", x, y, z, ry);
    },
    group(...kids) {
      const g = new THREE.Group();
      for (const k of kids.flat()) if (k) g.add(k);
      return g;
    },
    rnd,
  };
  return kit;
}

// -- the ground around: a slope, scrub, mountains --

// the sky: a gradient behind everything
function skyTex(top, low) {
  const [c, g] = canvas(4, 256);
  const gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, top);
  gr.addColorStop(1, low);
  g.fillStyle = gr;
  g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// the ground: height(x, z) and color(x, z, y) are
// the model's (its terrain); a large square around
function ground(kit, terrain) {
  const size = terrain.size || 900;
  const seg = 180;
  const geo = new THREE.PlaneGeometry(size, size,
    seg, seg);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const col = new Float32Array(pos.count * 3);
  const c = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const z = pos.getZ(i);
    const y = terrain.height(x, z);
    pos.setY(i, y);
    c.set(terrain.color(x, z, y));
    col.set([c.r, c.g, c.b], i * 3);
  }
  geo.setAttribute("color",
    new THREE.BufferAttribute(col, 3));
  geo.computeVertexNormals();
  const grain = groundTex();
  grain.repeat.set(size / 12, size / 12);
  const m = new THREE.Mesh(geo,
    new THREE.MeshStandardMaterial({ map: grain,
      vertexColors: true, roughness: 1 }));
  m.receiveShadow = true;
  return m;
}

// -- the viewer --

const TILT = [0.2, 1.42];

export function supported() {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2")
      || c.getContext("webgl"));
  } catch {
    return false;
  }
}

export async function start(view, mod, opts) {
  const renderer = new THREE.WebGLRenderer({
    antialias: true, powerPreference: "low-power" });
  renderer.setPixelRatio(
    Math.min(2, window.devicePixelRatio || 1));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  const cv = renderer.domElement;
  cv.className = "m3-canvas";
  view.prepend(cv);

  const kit = makeKit(materials());
  const model = mod.build(kit);
  const scene = new THREE.Scene();
  const sky = model.sky || ["#8fb3d9", "#e9e3d3"];
  scene.background = skyTex(sky[0], sky[1]);
  scene.fog = new THREE.Fog(sky[1], 180, 700);
  scene.add(model.group);
  if (model.terrain) scene.add(ground(kit, model.terrain));

  scene.add(new THREE.HemisphereLight(0xe8eef7,
    0x6a5a44, 1.5));
  const sun = new THREE.DirectionalLight(0xfff1d6, 2.6);
  // the afternoon sun, from the south-west
  sun.position.set(-75, 62, 55);
  sun.castShadow = true;
  const sh = model.shadow || 80;
  Object.assign(sun.shadow.camera, { left: -sh,
    right: sh, top: sh, bottom: -sh, near: 1,
    far: 400 });
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.0005;
  sun.shadow.normalBias = 0.05;
  scene.add(sun);

  const cam = new THREE.PerspectiveCamera(40, 1, 0.5,
    2000);
  // a tall view (a phone) stands further back
  const tall = view.clientWidth < view.clientHeight;
  const home = { ...model.view,
    dist: model.view.dist * (tall ? 1.55 : 1) };
  const st = { dist: home.dist, tilt: home.tilt,
    turn: home.turn,
    target: new THREE.Vector3(...home.target) };
  const lim = model.limits || { dist: [8, 260] };
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

  // the names: buttons over the canvas
  const spots = new Map(model.labels.map((l) =>
    [l.id, new THREE.Vector3(...l.at)]));
  const tmp = new THREE.Vector3();
  const drawTags = () => {
    const w = view.clientWidth;
    const hh = view.clientHeight;
    for (const [id, b] of opts.tags) {
      const v = spots.get(id);
      if (!v) continue;
      tmp.copy(v).project(cam);
      const out = tmp.z > 1 || Math.abs(tmp.x) > 1.05
        || Math.abs(tmp.y) > 1.05;
      b.classList.toggle("m3-off", out);
      b.style.left = ((tmp.x + 1) / 2 * w) + "px";
      b.style.top = ((1 - tmp.y) / 2 * hh) + "px";
      const d = cam.position.distanceTo(v);
      b.style.zIndex = String(Math.round(1000 - d));
    }
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
    drawTags();
    if (anim) ask();
  };
  const ask = () => {
    if (!frame) frame = requestAnimationFrame(render);
  };
  const keep = () => {
    st.dist = Math.min(lim.dist[1],
      Math.max(lim.dist[0], st.dist));
    st.tilt = Math.min(TILT[1],
      Math.max(TILT[0], st.tilt));
    st.target.y = Math.max(0, st.target.y);
    const far = lim.far || 150;
    st.target.x = Math.max(-far, Math.min(far,
      st.target.x));
    st.target.z = Math.max(-far, Math.min(far,
      st.target.z));
  };
  const go = (to, ms = 700) => {
    const from = { dist: st.dist, tilt: st.tilt,
      turn: st.turn, target: st.target.clone() };
    const end = { dist: to.dist ?? st.dist,
      tilt: to.tilt ?? st.tilt,
      turn: to.turn ?? st.turn,
      target: (to.target || st.target).clone() };
    while (end.turn - from.turn > Math.PI) {
      end.turn -= 2 * Math.PI;
    }
    while (from.turn - end.turn > Math.PI) {
      end.turn += 2 * Math.PI;
    }
    anim = { from, to: end, ms, t0: performance.now() };
    ask();
  };

  // drag: one finger or the mouse turns round the
  // buildings; two fingers zoom (pinch) and move;
  // the right button or shift moves
  const ac = new AbortController();
  const on = (el, ev, fn, o = {}) =>
    el.addEventListener(ev, fn,
      { ...o, signal: ac.signal });
  const ptrs = new Map();
  let two = null;
  const pan = (dx, dy) => {
    const k = st.dist / view.clientHeight * 1.1;
    const c = Math.cos(st.turn);
    const s = Math.sin(st.turn);
    st.target.x -= (dx * c + dy * s) * k;
    st.target.z -= (-dx * s + dy * c) * k;
  };
  const twoOf = () => {
    const [a, b] = [...ptrs.values()];
    return { d: Math.hypot(a.x - b.x, a.y - b.y),
      x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  };
  on(cv, "contextmenu", (e) => e.preventDefault());
  on(cv, "pointerdown", (e) => {
    anim = null;
    cv.setPointerCapture(e.pointerId);
    ptrs.set(e.pointerId, { x: e.clientX,
      y: e.clientY, move: e.button === 2
        || e.shiftKey });
    two = ptrs.size === 2 ? twoOf() : null;
  });
  on(cv, "pointermove", (e) => {
    const p = ptrs.get(e.pointerId);
    if (!p) return;
    const dx = e.clientX - p.x;
    const dy = e.clientY - p.y;
    p.x = e.clientX;
    p.y = e.clientY;
    if (ptrs.size === 2 && two) {
      const now = twoOf();
      st.dist *= two.d / now.d;
      pan(now.x - two.x, now.y - two.y);
      two = now;
    } else if (ptrs.size === 1) {
      if (p.move) {
        pan(dx, dy);
      } else {
        st.turn -= dx * 0.008;
        st.tilt -= dy * 0.006;
      }
    }
    keep();
    ask();
  });
  const lift = (e) => {
    ptrs.delete(e.pointerId);
    two = null;
  };
  on(cv, "pointerup", lift);
  on(cv, "pointercancel", lift);
  on(cv, "wheel", (e) => {
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

  function stop() {
    if (!alive) return;
    alive = false;
    cancelAnimationFrame(frame);
    ac.abort();
    ro.disconnect();
    scene.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
    });
    scene.traverse((o) => {
      if (o.material && o.material.map) {
        o.material.map.dispose();
      }
    });
    for (const m of Object.values(kit.mats)) {
      if (m.map) m.map.dispose();
      if (m.normalMap) m.normalMap.dispose();
      m.dispose();
    }
    if (scene.background) scene.background.dispose();
    renderer.dispose();
    renderer.forceContextLoss();
    cv.remove();
  }

  size();
  // the first view: coming round from further away
  st.dist = home.dist * 1.8;
  st.turn = home.turn - 0.6;
  st.tilt = Math.min(TILT[1], home.tilt + 0.1);
  go({ dist: home.dist, turn: home.turn,
    tilt: home.tilt }, 1800);

  return {
    reset() {
      go({ dist: home.dist, tilt: home.tilt,
        turn: home.turn,
        target: new THREE.Vector3(...home.target) });
    },
    turn(deg) {
      go({ turn: st.turn + deg * Math.PI / 180 }, 450);
    },
    tilt(k) {
      go({ tilt: Math.min(TILT[1], Math.max(TILT[0],
        st.tilt + k)) }, 400);
    },
    zoom(k) {
      go({ dist: Math.min(lim.dist[1],
        Math.max(lim.dist[0], st.dist * k)) }, 300);
    },
    // fly to a label
    focus(id) {
      const v = spots.get(id);
      if (!v) return;
      go({ target: v.clone().setY(v.y * 0.6),
        dist: Math.min(st.dist, 45) });
    },
    redraw: ask,
    stop,
  };
}
