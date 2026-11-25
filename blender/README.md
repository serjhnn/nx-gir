# Blender models

Monasteries and castles built in Blender, by script,
for a more detailed model than the ones written in
code for the web (`web/models/`). Nothing here is on
the site yet: the page `/3d/glakavank` still shows the
model of `web/models/glakavank.js`.

- `lib.py`: helpers: textures and skies from
  [Poly Haven](https://polyhaven.com) (CC0, fetched
  into `cache/`, not in git), materials, texture
  coordinates in metres, shapes (boxes, shapes turned
  on a lathe, outlines made solid, pointed and round
  arches, mouldings round an outline), holes cut with
  exact booleans, worn edges (bevels), renders, and
  the export to glTF (`.glb`) for the web.
- `glakavank.py`: Glakavank, the monastery of Karapet
  above Mush, as it stood in 1893. The same sources
  and sizes as `web/models/glakavank.js` (copies in
  `sources/glakavank/`).
- `renders/`: renders kept to compare with the old
  photographs.

## Running

Blender 4.2 LTS (`blender` on the path), headless:

    blender -b --factory-startup -P blender/glakavank.py \
        -- [--quick] [--no-render] [--glb]

It writes `blender/out/`: `glakavank.blend` (open it
in Blender to look round), a render of each view of
the photographs (`VIEWS` in `glakavank.py`) and, with
`--glb`, `glakavank.glb` (1K textures, Draco). With
`--quick`: 1K textures, small renders, a few
samples: about 1.5 minutes on 4 cores; the full one
takes about 20 minutes.

Blender 4.2 LTS can be fetched from
<https://download.blender.org/release/Blender4.2/>
(`blender-4.2.*-linux-x64.tar.xz`).

## Stone and sky (Poly Haven, CC0)

`large_sandstone_blocks` (the church, tinted grey; the
dark courses of the checkered band),
`castle_wall_varriation` (the enclosure),
`roof_slates_02` (cones and roofs), `marble_01`
(columns, slabs), `cobblestone_floor_04` (the court),
`withered_grass` (the slopes), `aerial_grass_rock`
(the earth roofs); the sky
`kloofendal_48d_partly_cloudy_puresky`.

## Pitfalls

- Holes are cut with the exact boolean, many at once
  (one cutter object of many prisms, `Holes`); the
  cutters may overlap (`use_self`). A cut that leaves
  nothing is reported ("empty after cutting") and the
  object dropped: make its cutters smaller.
- Shapes are made in world coordinates, so the
  textures can be laid in metres (`uv_set()`); keep
  objects at the origin.
- In the end the objects of each material are joined
  into one (`finish()`), so the `.glb` has few parts
  to draw.
