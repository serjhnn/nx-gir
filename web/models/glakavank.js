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
//   west (the belfry's two stages, its pointed
//   arches, gables and spires, the ring of columns;
//   the checkered base, the earth roof, the slender
//   drums with their blind arcades), the cells on
//   the north and west, the cross-yard behind the
//   church, the Harutyun chapel;
// - a view of the 1890s: earth roofs on every
//   building, the round tower at the corner.
// Sizes the sources do not give (heights, the
// enclosure) are estimated from the photographs.
// Copies: sources/glakavank/ (see its README).
//
// Metres; x to the east, z to the south, y up. An
// angle a round a tower points to (sin a, cos a):
// the kit's way (ry) of turning a face.

const PI = Math.PI;

export function build(k) {
  const T = k.THREE;
  const { box, cyl, cone, gable, arcade, win } = k;
  const parts = [];
  const add = (...m) => parts.push(...m);

  // a thin rod from point a to point b (the ribs of
  // the cones)
  const rod = (a, b, r, mat) => {
    const A = new T.Vector3(...a);
    const B = new T.Vector3(...b);
    const d = B.clone().sub(A);
    const m = k.mesh(new T.CylinderGeometry(r, r,
      d.length(), 5), mat);
    m.position.copy(A).add(B).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(
      new T.Vector3(0, 1, 0), d.normalize());
    return m;
  };
  // a cone of n sides with a rib on each edge, a
  // ball and a cross on top
  const spire = (r, h, n, x, y, z, cross = true) => {
    const out = [cone(r, h, n, "roof", x, y, z)];
    for (let i = 0; i < n; i++) {
      const a = i * 2 * PI / n;
      out.push(rod([x + r * Math.sin(a), y,
        z + r * Math.cos(a)], [x, y + h, z], 0.07,
      "roof"));
    }
    out.push(cyl(r + 0.12, 0.2, n, "ashlar", x, y - 0.1,
      z));
    if (cross) {
      const b = k.mesh(new T.SphereGeometry(0.22, 10, 8),
        "bronze");
      b.position.set(x, y + h + 0.1, z);
      out.push(b,
        box(0.12, 1.2, 0.12, "bronze", x, y + h + 0.2, z),
        box(0.6, 0.11, 0.11, "bronze", x, y + h + 0.95,
          z));
    }
    return out;
  };
  // a ring of arches on the face of a round drum:
  // n half-columns, an arch between each two
  const blindArcade = (x, y, z, r, n, h) => {
    const out = [];
    const half = r * Math.sin(PI / n);
    const rin = r * Math.cos(PI / n);
    for (let i = 0; i < n; i++) {
      const a = i * 2 * PI / n;
      out.push(cyl(0.09, h, 6, "ashlar",
        x + (r + 0.04) * Math.sin(a), y,
        z + (r + 0.04) * Math.cos(a)));
      const f = a + PI / n;
      const ring = k.mesh(new T.TorusGeometry(
        half - 0.04, 0.075, 5, 10, PI), "ashlar");
      ring.position.set(x + (rin + 0.06) * Math.sin(f),
        y + h, z + (rin + 0.06) * Math.cos(f));
      ring.rotation.y = f;
      out.push(ring);
    }
    return out;
  };

  // -- the church: the hall --

  const hw = 23.4;
  const hd = 28.5;
  const hx = -0.2;
  const hz = 0.25;
  const hh = 10;
  add(box(hw, hh, hd, "stone", hx, 0, hz),
    // the band of light and dark stone at its foot
    box(hw + 0.3, 1.6, hd + 0.3, "band", hx, 0, hz),
    // a string course half way up
    box(hw + 0.16, 0.18, hd + 0.16, "ashlar", hx, 5.6,
      hz),
    k.cornice(hw, hd, hx, hh - 0.5, hz),
    // the roof of earth, its low parapet
    box(hw + 0.2, 0.3, hd + 0.2, "earth", hx, hh, hz),
    box(hw + 0.6, 0.6, 0.45, "stone", hx, hh,
      hz - hd / 2 - 0.1),
    box(hw + 0.6, 0.6, 0.45, "stone", hx, hh,
      hz + hd / 2 + 0.1),
    box(0.45, 0.6, hd, "stone", hx - hw / 2 - 0.1, hh,
      hz));
  // small windows in two rows, framed
  const south = hz + hd / 2;
  const north = hz - hd / 2;
  for (const x of [-8.5, -3, 2.5, 8]) {
    add(win(0.55, 0.95, x, 3.2, south, 0),
      win(0.55, 0.95, x + 1.4, 7.1, south, 0),
      win(0.55, 0.95, x, 7.1, north, PI));
  }
  for (const z of [-10, -7, 7, 10]) {
    add(win(0.55, 0.95, hx - hw / 2, 7.1, z, -PI / 2));
  }

  // -- the chapels on the east, north to south --

  const chapels = [
    // north (Astvatsatsin on the plan); a small
    // house with a gable on its roof
    { z0: -25.5, z1: -14.5, x1: 31, h: 9,
      house: true },
    // Stepanos, with a drum
    { z0: -14.5, z1: 2.1, x1: 32.3, h: 10,
      drum: [23, -6.4] },
    // Karapet, with a drum and a band of arches
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
    add(box(w, c.h, d, "stone", cx, 0, cz),
      box(w + 0.3, 1.6, d + 0.3, "band", cx, 0, cz),
      k.cornice(w, d, cx, c.h - 0.5, cz));
    // a window on the east
    add(win(0.4, 1.3, c.x1, c.h - 4, cz, PI / 2,
      true));
    if (!c.drum) {
      // a low roof of two slopes, eaves standing out
      add(gable(w + 0.6, 1.6, d + 0.8, "roof", cx, c.h,
        cz));
      if (c.house) {
        add(box(7, 3, 5, "stone", cx - 4, c.h, cz),
          gable(7.6, 1.7, 5.8, "roof", cx - 4,
            c.h + 3, cz),
          win(0.4, 0.8, cx - 7.5, c.h + 1, cz, -PI / 2));
      }
      continue;
    }
    const [dx, dz] = c.drum;
    const b = c.h + 1;
    // roofs of two slopes crossing under the drum,
    // their gables to the four sides
    add(box(w, 0.3, d, "earth", cx, c.h, cz),
      gable(10, 2.5, 9.8, "roof", dx, c.h, dz),
      gable(9.8, 2.5, 10, "roof", dx, c.h, dz, PI / 2));
    // the drum: sixteen sides, light and dark stone
    add(cyl(2.95, 0.5, 16, "ashlar", dx, b - 0.5, dz),
      cyl(2.7, 6.4, 16, "band", dx, b, dz));
    // the blind arcade round it, higher on Karapet's
    add(...blindArcade(dx, b + (c.band ? 2.6 : 3.4),
      dz, 2.7, 16, c.band ? 2.6 : 2.0));
    if (c.band) {
      add(cyl(2.78, 0.18, 16, "ashlar", dx, b + 2.5,
        dz));
    }
    // four narrow windows
    for (let i = 0; i < 4; i++) {
      const f = i * PI / 2 + PI / 16;
      const rin = 2.7 * Math.cos(PI / 16);
      add(win(0.3, 1.2, dx + rin * Math.sin(f), b + 1.2,
        dz + rin * Math.cos(f), f, true));
    }
    // the cornice, then the ribbed cone
    add(cyl(2.92, 0.25, 16, "ashlar", dx, b + 6.4, dz),
      cyl(3.12, 0.3, 16, "ashlar", dx, b + 6.65, dz));
    add(...spire(3.15, 5.2, 16, dx, b + 6.95, dz));
  }

  // -- the porch (gavit) and the belfry, on the west --

  const gx = -16.85;
  const fx = gx - 4.95;
  add(box(9.9, 10.4, 9.4, "ashlar", gx, 0, 0),
    box(10.2, 1.6, 9.7, "band", gx, 0, 0),
    box(10.06, 0.18, 9.56, "ashlar", gx, 5.6, 0),
    k.cornice(9.9, 9.4, gx, 10.1, 0));
  // the portal: three pointed frames stepping in, a
  // carved slab under its point, the door
  for (const [i, ow, oh, aw, ah] of [
    [0, 5.2, 7.6, 3.8, 6.8], [1, 4.3, 6.9, 3, 6.1],
    [2, 3.5, 6.2, 2.3, 5.4]]) {
    add(arcade(ow, oh, 0.22, 1, aw, ah, "ashlar",
      fx - 0.55 + i * 0.2, 0, 0, -PI / 2, 0, true));
  }
  add(k.slab(1.6, 1.3, "rosette", fx - 0.06, 3.5, 0,
    -PI / 2),
  box(0.12, 3.3, 2, "wood", fx - 0.06, 0, 0));
  // the white marble slabs with reliefs on its front
  for (const [z, y, w, h] of [[-3.6, 1.8, 1.1, 1.6],
    [3.6, 1.8, 1.1, 1.6], [-3.6, 4.2, 1.1, 1.1],
    [3.6, 4.2, 1.1, 1.1]]) {
    add(k.slab(w, h, "rosette", fx - 0.06, y, z,
      -PI / 2));
  }
  for (const z of [-3.4, 3.4]) {
    add(win(0.5, 0.9, fx, 7.6, z, -PI / 2));
  }
  for (const s of [-1, 1]) {
    add(win(0.5, 0.9, gx, 7.6, s * 4.7, s > 0 ? 0 : PI),
      win(0.5, 0.9, gx, 3.2, s * 4.7, s > 0 ? 0 : PI));
  }

  // the belfry, first stage: a pointed arch on each
  // side between clustered columns, a steep gable
  // over it with a carved rosette, a spire on each
  // corner
  const by = 10.9;
  const s = 7.6;
  const t = 0.8;
  const sh = 7.6;
  add(box(s + 0.6, 0.5, s + 0.6, "ashlar", gx, by - 0.5,
    0));
  // each side: centre on the face, the way it looks
  const sides = [[gx - s / 2, 0, -PI / 2],
    [gx + s / 2, 0, PI / 2], [gx, -s / 2, PI],
    [gx, s / 2, 0]];
  for (const [x, z, ry] of sides) {
    const nx = Math.sin(ry);
    const nz = Math.cos(ry);
    // along the face
    const ax = Math.cos(ry);
    const az = -Math.sin(ry);
    add(arcade(s, sh, t, 1, 4.2, 6.6, "ashlar",
      x - nx * t / 2, by, z - nz * t / 2, ry, 0, true));
    for (const sgn of [-1, 1]) {
      for (const off of [2.35, 2.7]) {
        const px = x + ax * sgn * off + nx * 0.12;
        const pz = z + az * sgn * off + nz * 0.12;
        add(cyl(0.13, 5.6, 8, "marble", px, by, pz),
          box(0.34, 0.3, 0.34, "ashlar", px, by + 5.6,
            pz));
      }
    }
    // the gable and its rosette
    add(gable(0.5, 2.8, s - 0.4, "ashlar",
      x - nx * 0.25, by + sh + 0.45, z - nz * 0.25,
      ry + PI / 2));
    add(k.slab(1.1, 1.1, "rosette", x + nx * 0.02,
      by + sh + 0.75, z + nz * 0.02, ry));
  }
  add(k.cornice(s, s, gx, by + sh - 0.05, 0));
  for (const [cx2, cz2] of [[-1, -1], [1, -1],
    [1, 1], [-1, 1]]) {
    const x = gx + cx2 * (s / 2 - 0.15);
    const z = cz2 * (s / 2 - 0.15);
    add(box(0.8, 1.7, 0.8, "ashlar", x, by + sh + 0.45,
      z));
    add(...spire(0.55, 2, 4, x, by + sh + 2.15, z,
      false));
  }
  // the great bell
  add(cyl(1.05, 1.5, 16, "bronze", gx, by + 2.8, 0,
    0.45));

  // second stage: a ring of eight columns under
  // pointed arches, a bell, a ribbed roof of eight
  // sides and a cross
  const uy = by + sh + 0.5;
  const ur = 2.5;
  add(cyl(3, 0.6, 8, "ashlar", gx, uy, 0),
    cyl(3.2, 0.25, 8, "ashlar", gx, uy + 0.6, 0));
  const top = uy + 0.85;
  const colH = 3.6;
  for (let i = 0; i < 8; i++) {
    const a = i * PI / 4;
    add(cyl(0.2, colH, 8, "marble",
      gx + ur * Math.sin(a), top, ur * Math.cos(a)),
    box(0.45, 0.3, 0.45, "ashlar",
      gx + ur * Math.sin(a), top + colH,
      ur * Math.cos(a)));
    const f = a + PI / 8;
    const chord = 2 * ur * Math.sin(PI / 8);
    const rin = ur * Math.cos(PI / 8);
    add(arcade(chord + 0.3, 1.6, 0.3, 1, chord - 0.25,
      1.4, "ashlar", gx + rin * Math.sin(f),
      top + colH - 0.9, rin * Math.cos(f), f, 0, true));
  }
  add(cyl(0.6, 0.9, 12, "bronze", gx, top + 1.4, 0,
    0.28));
  const ry2 = top + colH + 0.7;
  add(cyl(2.95, 0.3, 8, "ashlar", gx, ry2, 0),
    cyl(3.2, 0.35, 8, "ashlar", gx, ry2 + 0.3, 0));
  add(...spire(3.25, 5.6, 8, gx, ry2 + 0.65, 0));

  // the graves before the porch: stelae in two rows
  const r = k.rnd(41);
  for (let i = 0; i < 6; i++) {
    for (const x of [-27, -24.5]) {
      add(box(0.55, 1.3 + r() * 0.6, 0.28, "marble",
        x + r() * 0.4, 0, -6.5 + i * 2.6));
    }
  }
  // a low iron fence round them: posts and two rails
  const rail = (x0, z0, x1, z1) => {
    const out = [];
    const len = Math.hypot(x1 - x0, z1 - z0);
    const n = Math.round(len / 1.2);
    for (let i = 0; i <= n; i++) {
      out.push(box(0.05, 1, 0.05, "iron",
        x0 + (x1 - x0) * i / n, 0,
        z0 + (z1 - z0) * i / n));
    }
    const ang = Math.atan2(z1 - z0, x1 - x0);
    for (const y of [0.35, 0.92]) {
      out.push(box(len, 0.04, 0.04, "iron",
        (x0 + x1) / 2, y, (z0 + z1) / 2, -ang));
    }
    return out;
  };
  add(...rail(-28.2, -8, -28.2, 8),
    ...rail(-28.2, -8, -23.6, -8),
    ...rail(-28.2, 8, -23.6, 8));

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
  // the walls, an earth top; the gate on the west
  const walls = [[E - W, wt, (W + E) / 2, N],
    [E - W, wt, (W + E) / 2, S],
    [wt, S - N, E, (N + S) / 2],
    [wt, -6 - N, W, (N - 6) / 2],
    [wt, S - 6, W, (S + 6) / 2]];
  for (const [w, d, x, z] of walls) {
    add(box(w, wh, d, "rubble", x, 0, z),
      box(w + 0.2, 0.5, d + 0.2, "stone", x, wh - 0.5,
        z),
      box(w, 0.25, d, "earth", x, wh, z));
  }
  // small windows high on the outer walls
  for (let i = 0; i < 16; i++) {
    add(k.hole(0.35, 0.7, W + 6 + i * 6.2, 6.2,
      S + 0.92));
  }
  // the gatehouse, its door half open
  add(arcade(12, 10, 6, 1, 4, 6.2, "rubble", W, 0, 0,
    PI / 2),
  box(6.2, 0.6, 12.2, "stone", W, 9.4, 0),
  box(6, 0.25, 12, "earth", W, 10, 0));
  add(box(0.25, 5.8, 2, "wood", W + 3.2, 0, -1.6,
    -0.6),
  box(0.25, 5.8, 2, "wood", W + 3.2, 0, 1.6, 0.6));
  // round towers at the corners, and the great
  // round tower on the south; narrow loopholes
  for (const [x, z, rr, h] of [[W, N, 4.2, 11],
    [E, N, 4.2, 11], [E, S, 4.2, 11], [W, S, 4.6, 12],
    [-22, S + 1, 5.6, 12.5]]) {
    add(cyl(rr, h, 24, "rubble", x, 0, z),
      cyl(rr + 0.25, 0.5, 24, "stone", x, h - 0.5, z),
      cyl(rr + 0.3, 0.9, 24, "rubble", x, h, z),
      cyl(rr - 0.2, 0.3, 24, "earth", x, h + 0.7, z));
    for (let i = 0; i < 5; i++) {
      const a = i * 2 * PI / 5 + 0.3;
      add(k.hole(0.25, 1, x + rr * Math.sin(a), 5,
        z + rr * Math.cos(a), a));
    }
  }

  // -- the buildings round the court --

  // the long line of buildings on the south: cells
  // and the refectory, a gallery of two floors on
  // the court, an earth roof
  const sx0 = W + 1;
  const sx1 = E - 1;
  const sw = sx1 - sx0;
  const scx = (sx0 + sx1) / 2;
  add(box(sw, 10, 9.5, "rubble", scx, 0, S - 5.6),
    box(sw, 0.3, 9.3, "earth", scx, 10, S - 5.6));
  add(box(sw, 0.5, 3, "ashlar", scx, 5, 32.4),
    box(sw, 0.6, 3.4, "ashlar", scx, 10, 32.4),
    box(sw, 0.25, 3.4, "earth", scx, 10.6, 32.4));
  add(arcade(sw, 5, 0.6, 24, 2.6, 3.8, "ashlar",
    scx, 0, 31.1),
  arcade(sw, 5, 0.6, 24, 2.4, 3.4, "ashlar",
    scx, 5, 31.1, 0, 0.8));
  // doors and windows inside the gallery
  for (let i = 0; i < 24; i++) {
    const x = sx0 + (i + 0.5) * sw / 24;
    add(k.hole(1, 2.1, x, 0, 33.75),
      k.hole(0.6, 1, x, 6.6, 33.75));
  }
  // the buildings on the north, a gallery too
  add(box(sw, 8, 7, "rubble", scx, 0, N + 4.4),
    box(sw, 0.3, 6.8, "earth", scx, 8, N + 4.4));
  add(box(sw, 0.6, 3, "ashlar", scx, 8, -32.2),
    box(sw, 0.25, 3, "earth", scx, 8.6, -32.2));
  add(arcade(sw, 4, 0.6, 24, 2.6, 3.2, "ashlar",
    scx, 0, -31),
  arcade(sw, 4, 0.6, 24, 2.4, 2.8, "ashlar",
    scx, 4, -31, 0, 0.6));
  for (let i = 0; i < 24; i++) {
    const x = sx0 + (i + 0.5) * sw / 24;
    add(k.hole(0.9, 2, x, 0, -32.85),
      k.hole(0.55, 0.9, x, 5.3, -32.85));
  }
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
  const hcx = -40;
  const hcz = 22;
  add(box(5, 4.5, 6.5, "stone", hcx, 0, hcz),
    box(5.3, 1, 6.8, "band", hcx, 0, hcz),
    gable(5.6, 1.8, 7.2, "roof", hcx, 4.5, hcz, PI / 2),
    win(0.3, 0.9, hcx + 2.5, 2.4, hcz, PI / 2, true),
    k.hole(1, 2, hcx - 2.53, 0, hcz, -PI / 2),
    box(12, 1.6, 0.6, "rubble", hcx, 0, hcz - 6),
    box(12, 1.6, 0.6, "rubble", hcx, 0, hcz + 6),
    box(0.6, 1.6, 12, "rubble", hcx + 6, 0, hcz),
    box(0.6, 1.6, 4, "rubble", hcx - 6, 0, hcz - 4),
    box(0.6, 1.6, 4, "rubble", hcx - 6, 0, hcz + 4));
  // the cross-yard (Khachbak) behind the church:
  // cross-stones and the slabs over the abbots'
  // graves
  const kq = k.rnd(53);
  for (let i = 0; i < 16; i++) {
    const z = -30 + i * 3.4 + kq();
    const x = 34.5 + (i % 3) * 2;
    if (i % 3 === 0) {
      add(box(1.5, 0.5, 0.6, "ashlar", x, 0, z),
        k.slab(1.1, 2, "cross", x, 0.5, z + 0.1, 0),
        box(1.3, 0.3, 0.35, "ashlar", x, 2.5, z));
    } else {
      add(box(1, 0.35, 2, "marble", x, 0, z));
    }
  }
  // the new buildings on the west, by Bishop
  // Mampre: for a printing press and a library
  add(box(12, 12, 20, "ashlar", W + 7, 0, 22),
    k.cornice(12, 20, W + 7, 11.5, 22),
    gable(12.8, 2.2, 21, "roof", W + 7, 12, 22,
      PI / 2));
  for (let f = 0; f < 3; f++) {
    for (let i = 0; i < 5; i++) {
      add(win(0.9, 1.6, W + 13, 1.5 + f * 3.6,
        14 + i * 4, PI / 2));
    }
  }

  // -- trees: a poplar and walnuts in the court, as
  // in the photographs; more below the walls --
  for (const [kind, x, z, h, sd] of [
    ["poplar", 6, -25, 17, 1], ["walnut", -32, -22, 9, 2],
    ["poplar", -52, 2, 15, 3], ["walnut", 30, 26, 8, 4],
    ["walnut", -78, 30, 10, 5], ["poplar", -84, 46, 16,
      6], ["walnut", 60, 52, 9, 7],
    ["walnut", -30, 66, 11, 8], ["poplar", 12, 64, 18,
      9], ["walnut", 70, -10, 10, 10]]) {
    add(k.tree(kind, x, height(x, z), z, h, sd));
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
    terrain: { height, color, size: 2600, seg: 260 },
    sky: ["#8eabc9", "#e4ddcd"],
    fog: [400, 4200],
    shadow: 95,
    view: { target: [-8, 7, 2], dist: 105, tilt: 1.2,
      turn: -0.82 },
    limits: { dist: [10, 420], far: 200 },
    labels: [
      { id: "belfry", at: [gx, 33.5, 0] },
      { id: "gavit", at: [fx - 0.5, 8.5, 0] },
      { id: "church", at: [-2, 10.8, 0] },
      { id: "stepanos", at: [23, 24.6, -6.4] },
      { id: "karapet", at: [23, 24.6, 7] },
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
// the mountain wall north of the plain of Mush; the
// slope falls to the south in fields, then steeply
// to the plain, about 670 m below (Lynch); mountains
// beyond it, and the ridges rise to the north --

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
  y += wave(x * 0.2, z * 0.2) * n * 0.12;
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
  y = y * (1 - flat) - 0.02 * flat;
  // further south, the steep fall to the plain,
  // the plain, and the mountains beyond it
  const fall = smooth(230, 650, z);
  const plain = -560 + wave(x * 0.2, z * 0.2) * 8;
  y = y * (1 - fall) + plain * fall;
  const far = smooth(1050, 1300, z);
  y += far * (420 + wave(x * 0.08, z * 0.08) * 160);
  return y;
}

// dry grass and grey rock, as in the photographs
// (the slopes are bare, the grass yellow by summer)
function color(x, z, y) {
  const w = wave(x * 1.7, z * 1.7);
  if (z > 1000) return w > 0 ? "#8a8a86" : "#7f8183";
  if (z > 600) {
    // the plain: fields of many colors
    const fx = Math.floor(x / 60 + w * 0.3);
    const fz = Math.floor(z / 45);
    const k = (fx * 7 + fz * 13) % 4;
    return ["#a8996a", "#8f9258", "#b2a477",
      "#7f8a50"][(k + 4) % 4];
  }
  if (y > 95 + w * 12) return "#8a8379";
  if (y > 60 + w * 10) return w > 0 ? "#86806a"
    : "#8f8674";
  const near = Math.abs(x + 6) < 85
    && z > -52 && z < 62;
  if (near) return w > 0.3 ? "#8b7d64" : "#94866b";
  // fields below, stubble and fallow
  if (z > 60 && z < 240) {
    const band = Math.floor((z - 52) / 8) % 2;
    return band ? "#a8996a" : "#958c5f";
  }
  return w > 0 ? "#8f8a5c" : "#9d9266";
}

// low oak bushes on the slopes round the walls
function scrub(k) {
  const T = k.THREE;
  const geo = new T.IcosahedronGeometry(1, 1);
  const pos = geo.attributes.position;
  const jr = k.rnd(78);
  for (let i = 0; i < pos.count; i++) {
    const j = 0.75 + jr() * 0.5;
    pos.setXYZ(i, pos.getX(i) * j, pos.getY(i) * j,
      pos.getZ(i) * j);
  }
  geo.computeVertexNormals();
  const n = 1200;
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
    o.position.set(x, height(x, z) + s * 0.4, z);
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
