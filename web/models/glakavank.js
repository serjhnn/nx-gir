// Glakavank, the monastery of Karapet above the plain
// of Mush (Taron), as it stood in 1893, before 1915.
// Read by web/model3d.js; listed in models.json.
//
// The buildings are a model made in Blender, by
// script: blender/glakavank.py (see blender/README.md),
// exported to models/glakavank/ (a .gltf, its .bin and
// its textures, Poly Haven, CC0). This file gives the
// ground round it, the bushes, the names of the parts
// and the first view; the ground is the same as the
// one the Blender script draws (height()).
//
// Built from:
// - the plan in R. Hewsen, Armenia: A Historical
//   Atlas (2001), p. 206, as redrawn on Wikimedia
//   Commons (Surb_Karapet_Monastery_plan.png, CC
//   BY-SA 4.0): the hall of 16 columns, the four
//   chapels on the east, the porch and belfry on the
//   west; measured at about 0.085 m a pixel;
// - H. F. B. Lynch, Armenia: Travels and Studies,
//   vol. 2 (1901), pp. 176-181, and his photographs;
// - the photographs before 1915 on the page "Մշո Ս.
//   Կարապետ" of Nune Movsisyan's blog (2013), with
//   its text from «Տարոնի պատմական հուշարձանները»;
// - a view of the 1890s: earth roofs on every
//   building, the round tower at the corner.
// Copies: sources/glakavank/ (see its README).
//
// Metres; x to the east, z to the south, y up (the
// Blender model's north is -z here).

export function build(k) {
  const group = k.group([]);
  // the low oak scrub on the slopes
  group.add(scrub(k));
  return {
    group,
    gltf: "models/glakavank/glakavank.gltf",
    terrain: { height, color, size: 2600, seg: 260 },
    sky: ["#8eabc9", "#e4ddcd"],
    fog: [400, 4200],
    shadow: 95,
    view: { target: [-8, 7, 2], dist: 105, tilt: 1.2,
      turn: -0.82 },
    limits: { dist: [10, 420], far: 200 },
    labels: [
      { id: "belfry", at: [-16.85, 33.5, 0] },
      { id: "gavit", at: [-22.3, 8.5, 0] },
      { id: "church", at: [-2, 10.8, 0] },
      { id: "stepanos", at: [23, 25.6, -6.4] },
      { id: "karapet", at: [23, 25.6, 7] },
      { id: "north", at: [21, 10.2, -20] },
      { id: "gevorg", at: [18, 10.2, 17] },
      { id: "gate", at: [-63, 10.5, 0] },
      { id: "mampre", at: [-55, 14.4, 22] },
      { id: "cells", at: [-10, 10.5, 39] },
      { id: "tower", at: [-22, 13.5, 45] },
      { id: "cemetery", at: [-73, 1.5, 59] },
      { id: "harutyun", at: [-40, 7, 22] },
      { id: "khachbak", at: [37, 3, -8] },
      { id: "westcells", at: [-56, 10, -22] },
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
