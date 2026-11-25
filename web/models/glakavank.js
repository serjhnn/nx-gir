// Glakavank, the monastery of Karapet above the plain
// of Mush (Taron), as it stood in 1893, before 1915.
// Read by web/model3d.js; listed in models.json.
//
// Built from:
// - the plan in R. Hewsen, Armenia: A Historical
//   Atlas (2001), p. 206, as redrawn on Wikimedia
//   Commons (Surb_Karapet_Monastery_plan.png, CC
//   BY-SA 4.0): the hall of 16 columns, the four
//   chapels on the east, the porch and belfry on the
//   west; measured at about 0.085 m a pixel;
// - H. F. B. Lynch, Armenia: Travels and Studies,
//   vol. 2 (1901), pp. 176-181, and his photographs:
//   the monastery from the south (the walls, the
//   round tower, the slope), the church from the
//   south-west (the belfry, the porch, the graves)
//   and the two chapels (banded drums, cones);
// - the photographs before 1915 on the page "Մշո Ս.
//   Կարապետ" of Nune Movsisyan's blog (2013), with
//   its text from «Տարոնի պատմական հուշարձանները»:
//   the church from the south-west and from the
//   west (the belfry's two stages, the checkered
//   base, the earth roof, the slender drums), the
//   cells on the north and west, the cross-yard
//   behind the church, the Harutyun chapel.
// Sizes the sources do not give (heights, the
// enclosure) are estimated from the photographs.
// Copies: sources/glakavank/ (see its README).
//
// Metres; x to the east, z to the south, y up.

const PI = Math.PI;

export function build(k) {
  const { box, cyl, cone, gable, arcade, hole } = k;
  const parts = [];
  const add = (...m) => parts.push(...m);

  // -- the church --

  // the hall: 16 columns inside, a flat roof
  add(box(23.4, 10, 28.5, "stone", -0.2, 0, 0.25));
  // its roof of earth, and the band of light and
  // dark stone at the foot of its walls
  add(box(23.2, 0.25, 28.3, "earth", -0.2, 10, 0.25),
    box(23.6, 1.6, 28.7, "band", -0.2, 0, 0.25));
  // its parapet
  add(box(23.8, 0.7, 0.5, "stone", -0.2, 10, -14.2),
    box(23.8, 0.7, 0.5, "stone", -0.2, 10, 14.7),
    box(0.5, 0.7, 28.5, "stone", -12.1, 10, 0.25));
  // windows on the south and north
  // (small: two rows, as in the photographs)
  for (const x of [-8, -2.5, 3, 8.5]) {
    for (const y of [3.2, 6.8]) {
      add(hole(0.6, 1, x + (y > 5 ? 1.2 : 0), y,
        14.53),
      hole(0.6, 1, x, y, -14.03));
    }
  }
  // and on the west, beside the porch
  for (const z of [-10, -7, 7, 10]) {
    add(hole(0.6, 1, -11.93, 6.8, z, PI / 2));
  }

  // the chapels on the east, north to south
  const chapels = [
    // north (Astvatsatsin on the plan)
    { z0: -25.5, z1: -14.5, x1: 31, h: 9,
      house: true },
    // Stepanos, with a drum
    { z0: -14.5, z1: 2.1, x1: 32.3, h: 10,
      drum: [23, -6.4] },
    // Karapet, with a drum
    { z0: 2.1, z1: 11.9, x1: 32.3, h: 10,
      drum: [23, 7.0], band: true },
    // Gevorg
    { z0: 11.9, z1: 21.7, x1: 25.2, h: 9 },
  ];
  for (const c of chapels) {
    const x0 = 11.3;
    const w = c.x1 - x0;
    const d = c.z1 - c.z0;
    const cx = (x0 + c.x1) / 2;
    const cz = (c.z0 + c.z1) / 2;
    add(box(w, c.h, d, "stone", cx, 0, cz));
    // small windows high up on the east
    add(hole(0.7, 1.6, c.x1 + 0.03, c.h - 3.5, cz,
      PI / 2));
    if (!c.drum) {
      // a low roof of two slopes
      add(gable(w, 1.6, d, "roof", cx, c.h, cz));
      if (c.house) {
        // the small house with a gable on the roof
        add(box(7, 3, 5, "stone", cx - 4, c.h, cz),
          gable(7.4, 1.6, 5.4, "roof", cx - 4,
            c.h + 3, cz));
      }
      continue;
    }
    const [dx, dz] = c.drum;
    // roofs of two slopes crossing under the drum
    add(gable(9.6, 2.4, 9.4, "roof", dx, c.h, dz),
      gable(9.4, 2.4, 9.6, "roof", dx, c.h, dz,
        PI / 2));
    // the drum: twelve sides, light and dark stone
    add(cyl(2.7, 6.4, 16, "band", dx, c.h + 1, dz),
      cyl(2.95, 0.4, 16, "ashlar", dx, c.h + 1, dz),
      cyl(2.95, 0.45, 16, "ashlar", dx, c.h + 7.2,
        dz));
    if (c.band) {
      // the band of blind arches round the drum
      add(cyl(2.8, 2.2, 16, "ashlar", dx, c.h + 4.6,
        dz));
    }
    for (let i = 0; i < 4; i++) {
      const a = i * PI / 2 + PI / 12;
      add(hole(0.5, 1.3, dx + 2.82 * Math.cos(a),
        c.h + 3.3, dz + 2.82 * Math.sin(a),
        PI / 2 - a));
    }
    // the cone of stone slabs, and its cross
    add(cone(3.1, 5.2, 16, "roof", dx, c.h + 7.65,
      dz));
    add(box(0.14, 1.1, 0.14, "bronze", dx,
      c.h + 12.8, dz),
    box(0.6, 0.12, 0.12, "bronze", dx, c.h + 13.5,
      dz));
  }

  // -- the porch (gavit) and the belfry, on the west --

  const gx = -16.85;
  add(box(9.9, 10.4, 9.4, "ashlar", gx, 0, 0),
    box(10.2, 1.6, 9.7, "band", gx, 0, 0));
  // the west front: the door, white marble slabs
  // with reliefs, four windows above
  const fx = gx - 4.95;
  add(box(0.3, 6.2, 3.4, "ashlar", fx - 0.12, 0, 0),
    gable(0.3, 1.4, 3.4, "ashlar", fx - 0.12, 6.2, 0),
    hole(2.2, 3.4, fx - 0.3, 0, 0, PI / 2));
  for (const [z, y, w, h] of [[-3.2, 1.2, 1.4, 2.4],
    [3.2, 1.2, 1.4, 2.4], [0, 4.7, 3.4, 1.2],
    [-3.3, 4.4, 1.1, 1.1], [3.3, 4.4, 1.1, 1.1]]) {
    add(box(0.1, h, w, "marble", fx - 0.05, y, z));
  }
  for (const z of [-3.3, -1.1, 1.1, 3.3]) {
    add(hole(0.6, 1.1, fx - 0.03, 7.6, z, PI / 2));
  }
  // the cornice of the porch
  add(box(10.5, 0.5, 10, "ashlar", gx, 10.4, 0));

  // the belfry, first stage: open arches on four
  // sides, a small gable over each
  const by = 10.9;
  const s = 7.6;
  const t = 0.8;
  const sh = 8;
  const arch = (x, z, ry) => arcade(s, sh, t, 1, 4.6,
    6.8, "ashlar", x, by, z, ry);
  add(arch(gx - s / 2 + t / 2, 0, PI / 2),
    arch(gx + s / 2 - t / 2, 0, PI / 2),
    arch(gx, -s / 2 + t / 2, 0),
    arch(gx, s / 2 - t / 2, 0));
  add(box(s + 0.8, 0.6, s + 0.8, "ashlar", gx,
    by + sh, 0));
  const gy = by + sh + 0.6;
  const g = s / 2;
  add(gable(0.8, 1.6, s, "ashlar", gx - g, gy, 0),
    gable(0.8, 1.6, s, "ashlar", gx + g, gy, 0),
    gable(0.8, 1.6, s, "ashlar", gx, gy, -g, PI / 2),
    gable(0.8, 1.6, s, "ashlar", gx, gy, g, PI / 2));
  // clustered columns at the corners, and a small
  // spire on each
  for (const [cx2, cz2] of [[-1, -1], [1, -1],
    [1, 1], [-1, 1]]) {
    const x = gx + cx2 * (s / 2 - 0.1);
    const z = cz2 * (s / 2 - 0.1);
    add(cyl(0.32, sh, 8, "marble", x, by, z),
      cone(0.38, 1.6, 8, "ashlar", x, by + sh + 0.6,
        z));
  }
  // the great bell
  add(cyl(1.05, 1.5, 16, "bronze", gx, by + 2.6, 0,
    0.45));

  // second stage: eight columns round a bell, a
  // roof of eight sides, a cross
  const uy = gy;
  add(cyl(2.9, 0.7, 8, "ashlar", gx, uy, 0));
  for (let i = 0; i < 8; i++) {
    const a = i * PI / 4 + PI / 8;
    add(cyl(0.24, 4.6, 8, "marble",
      gx + 2.45 * Math.cos(a), uy + 0.7,
      2.45 * Math.sin(a)));
  }
  add(cyl(0.6, 0.9, 12, "bronze", gx, uy + 2.2, 0,
    0.28));
  add(cyl(3, 0.7, 8, "ashlar", gx, uy + 5.3, 0));
  add(cone(3.2, 5.4, 8, "roof", gx, uy + 6, 0));
  add(box(0.16, 1.4, 0.16, "bronze", gx, uy + 11.4, 0),
    box(0.8, 0.14, 0.14, "bronze", gx, uy + 12.2, 0));

  // the graves before the porch: stelae in two rows
  const r = k.rnd(41);
  for (let i = 0; i < 6; i++) {
    for (const x of [-27, -24.5]) {
      add(box(0.55, 1.3 + r() * 0.6, 0.28, "marble",
        x + r() * 0.4, 0, -6.5 + i * 2.6));
    }
  }

  // -- the enclosure: like a fortress --

  const W = -62;
  const E = 42;
  const N = -40;
  const S = 44;
  const wh = 8;
  const wt = 1.8;
  // the court, paved
  add(box(E - W, 0.08, S - N, "court", (W + E) / 2, 0,
    (N + S) / 2));
  // the walls; the gate is on the west
  add(box(E - W, wh, wt, "rubble", (W + E) / 2, 0, N),
    box(E - W, wh, wt, "rubble", (W + E) / 2, 0, S),
    box(wt, wh, S - N, "rubble", E, 0, (N + S) / 2),
    box(wt, wh, -6 - N, "rubble", W, 0, (N - 6) / 2),
    box(wt, wh, S - 6, "rubble", W, 0, (S + 6) / 2));
  // the gatehouse, its door half open
  add(arcade(12, 10, 6, 1, 4, 6.2, "rubble", W, 0, 0,
    PI / 2));
  add(box(0.25, 5.8, 2, "wood", W + 3.2, 0, -1.6,
    -0.6),
  box(0.25, 5.8, 2, "wood", W + 3.2, 0, 1.6, 0.6));
  // round towers at the corners, and the great
  // round tower on the south
  for (const [x, z, rr, h] of [[W, N, 4.2, 11],
    [E, N, 4.2, 11], [E, S, 4.2, 11], [W, S, 4.6, 12],
    [-22, S + 1, 5.6, 12.5]]) {
    add(cyl(rr, h, 18, "rubble", x, 0, z),
      cyl(rr + 0.3, 0.9, 18, "rubble", x, h, z),
      cyl(rr - 0.2, 0.3, 18, "earth", x, h + 0.7, z));
  }

  // -- the buildings round the court --

  // the long line of buildings on the south: cells
  // and the refectory, a gallery of two floors on
  // the court
  const sx0 = W + 1;
  const sx1 = E - 1;
  const sw = sx1 - sx0;
  const scx = (sx0 + sx1) / 2;
  add(box(sw, 10, 9.5, "rubble", scx, 0, S - 5.6),
    box(sw, 0.3, 9.3, "earth", scx, 10, S - 5.6));
  add(box(sw, 0.5, 3, "ashlar", scx, 5, 32.4),
    box(sw, 0.6, 3.4, "ashlar", scx, 10, 32.4));
  add(arcade(sw, 5, 0.6, 24, 2.6, 3.8, "ashlar",
    scx, 0, 31.1),
  arcade(sw, 5, 0.6, 24, 2.4, 3.4, "ashlar",
    scx, 5, 31.1, 0, 0.8));
  for (let i = 0; i < 18; i++) {
    add(hole(0.6, 1.1, sx0 + 4 + i * 5.4, 6.5,
      S + 0.95));
  }
  // the buildings on the north, a gallery too
  add(box(sw, 8, 7, "rubble", scx, 0, N + 4.4),
    box(sw, 0.3, 6.8, "earth", scx, 8, N + 4.4));
  add(box(sw, 0.6, 3, "ashlar", scx, 8, -32.2));
  add(arcade(sw, 4, 0.6, 24, 2.6, 3.2, "ashlar",
    scx, 0, -31),
  arcade(sw, 4, 0.6, 24, 2.4, 2.8, "ashlar",
    scx, 4, -31, 0, 0.6));
  // the cells on the west, two floors, a gallery
  // on the court (the gate between them)
  add(box(7, 9, 30, "rubble", W + 4.4, 0, -22),
    box(6.8, 0.3, 30, "earth", W + 4.4, 9, -22),
    box(3, 0.5, 30, "ashlar", W + 9.4, 4.5, -22),
    box(3.4, 0.6, 30, "ashlar", W + 9.4, 9, -22));
  add(arcade(30, 4.5, 0.6, 9, 2.4, 3.4, "ashlar",
    W + 10.6, 0, -22, PI / 2),
  arcade(30, 4.5, 0.6, 9, 2.2, 3, "ashlar",
    W + 10.6, 4.5, -22, PI / 2, 0.6));
  // the Harutyun chapel in the south-west court,
  // in a yard of its own walled with stone
  const hx = -40;
  const hz = 22;
  add(box(5, 4.5, 6.5, "stone", hx, 0, hz),
    gable(5.4, 1.8, 7, "roof", hx, 4.5, hz, PI / 2),
    box(12, 1.6, 0.6, "rubble", hx, 0, hz - 6),
    box(12, 1.6, 0.6, "rubble", hx, 0, hz + 6),
    box(0.6, 1.6, 12, "rubble", hx + 6, 0, hz),
    box(0.6, 1.6, 4, "rubble", hx - 6, 0, hz - 4),
    box(0.6, 1.6, 4, "rubble", hx - 6, 0, hz + 4));
  // the cross-yard (Khachbak) behind the church:
  // the graves of the abbots, cross-stones
  const kq = k.rnd(53);
  for (let i = 0; i < 16; i++) {
    const z = -30 + i * 3.4 + kq();
    const x = 34.5 + (i % 3) * 2;
    if (i % 4 === 0) {
      add(box(0.3, 2.2, 1.2, "ashlar", x, 0, z),
        box(0.4, 0.3, 1.4, "ashlar", x, 2.2, z));
    } else {
      add(box(1, 0.35, 2, "marble", x, 0, z));
    }
  }
  // the new buildings on the west, by Bishop
  // Mampre: for a printing press and a library
  add(box(12, 12, 20, "ashlar", W + 7, 0, 22));
  add(gable(12.4, 2.2, 20.4, "roof", W + 7, 12, 22,
    PI / 2));
  for (let f = 0; f < 3; f++) {
    for (let i = 0; i < 5; i++) {
      add(hole(1, 1.8, W + 13.03, 1.5 + f * 3.6,
        14 + i * 4, PI / 2));
    }
  }

  // -- outside: the terrace and its little
  // cemetery, south-west, below the walls --
  const q = k.rnd(9);
  for (let i = 0; i < 22; i++) {
    const x = -82 + q() * 18;
    const z = 54 + q() * 10;
    add(box(0.5, 0.8 + q() * 0.8, 0.25, "ashlar",
      x, height(x, z) - 0.2, z, q() * 0.4));
  }

  const group = k.group(parts);

  // the low oak scrub on the slopes
  group.add(scrub(k));

  return {
    group,
    terrain: { height, color, size: 900 },
    sky: ["#8eabc9", "#e4ddcd"],
    shadow: 95,
    view: { target: [-8, 7, 2], dist: 105, tilt: 1.2,
      turn: -0.82 },
    limits: { dist: [12, 340], far: 170 },
    labels: [
      { id: "belfry", at: [gx, 33.2, 0] },
      { id: "gavit", at: [fx - 0.5, 8.5, 0] },
      { id: "church", at: [-2, 10.8, 0] },
      { id: "stepanos", at: [23, 24.4, -6.4] },
      { id: "karapet", at: [23, 24.4, 7] },
      { id: "north", at: [21, 10.2, -20] },
      { id: "gevorg", at: [18, 10.2, 17] },
      { id: "gate", at: [W - 1, 10.5, 0] },
      { id: "mampre", at: [W + 7, 14.4, 22] },
      { id: "cells", at: [-10, 10.5, 39] },
      { id: "tower", at: [-22, 13.5, S + 1] },
      { id: "cemetery", at: [-73, 1.5, 59] },
      { id: "harutyun", at: [-40, 7, 22] },
      { id: "khachbak", at: [37, 3, -8] },
      { id: "westcells", at: [W + 6, 10, -22] },
    ],
  };
}

// -- the ground: the monastery on a terrace high on
// the mountain wall north of the plain; the slope
// falls to the south in fields, rises to the north --

function smooth(a, b, x) {
  const t = Math.max(0, Math.min(1, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
}

function wave(x, z) {
  return Math.sin(x * 0.021 + 1.3) * Math.cos(z * 0.017)
    + 0.5 * Math.sin(x * 0.057 - z * 0.043)
    + 0.25 * Math.sin(x * 0.13 + z * 0.11);
}

function height(x, z) {
  // the terrace of the monastery, flat
  const inX = smooth(-95, -70, x) * (1 - smooth(50,
    75, x));
  const inZ = smooth(-62, -45, z) * (1 - smooth(68,
    80, z));
  const flat = inX * inZ;
  // north: up to the ridges
  const n = Math.max(0, -z - 45);
  let y = n * 0.42 + n * n * 0.0011;
  // south: down in terraced fields
  const s = Math.max(0, z - 52);
  const step = 8;
  const qq = s / step;
  const f = qq - Math.floor(qq);
  const riser = f < 0.75 ? 0 : (f - 0.75) / 0.25;
  y -= (Math.floor(qq) + riser) * step * 0.3;
  // and a little down to the west, where the road
  // comes up
  y -= Math.max(0, -x - 90) * 0.12;
  y += wave(x, z) * (3 + n * 0.08 + s * 0.02);
  return y * (1 - flat) - 0.02 * flat;
}

// dry grass and grey rock, as in the photographs
// (the slopes are bare, the grass yellow by summer)
function color(x, z, y) {
  const w = wave(x * 1.7, z * 1.7);
  if (y > 95 + w * 12) return "#8a8379";
  if (y > 60 + w * 10) return w > 0 ? "#86806a"
    : "#8f8674";
  const near = Math.abs(x + 6) < 85
    && z > -52 && z < 62;
  if (near) return w > 0.3 ? "#8b7d64" : "#94866b";
  // fields below, stubble and fallow
  if (z > 60) {
    const band = Math.floor((z - 52) / 8) % 2;
    return band ? "#a8996a" : "#958c5f";
  }
  return w > 0 ? "#8f8a5c" : "#9d9266";
}

// low oak bushes on the slopes round the walls
function scrub(k) {
  const T = k.THREE;
  const geo = new T.IcosahedronGeometry(1, 0);
  const n = 900;
  const m = new T.InstancedMesh(geo, k.mats.leaf, n);
  m.castShadow = true;
  const r = k.rnd(77);
  const o = new T.Object3D();
  const c = new T.Color();
  let i = 0;
  while (i < n) {
    const x = (r() - 0.5) * 520;
    const z = (r() - 0.5) * 520;
    // not on the terrace nor the fields below it
    if (x > -100 && x < 60 && z > -55 && z < 70) {
      continue;
    }
    if (z > 70 && r() < 0.75) continue;
    const s = 0.6 + r() * 1.2;
    o.position.set(x, height(x, z) + s * 0.5, z);
    o.scale.set(s * (1 + r() * 0.6), s * 0.8,
      s * (1 + r() * 0.6));
    o.rotation.y = r() * Math.PI;
    o.updateMatrix();
    m.setMatrixAt(i, o.matrix);
    c.setHSL(0.13 + r() * 0.06, 0.25,
      0.22 + r() * 0.1);
    m.setColorAt(i, c);
    i++;
  }
  return m;
}
