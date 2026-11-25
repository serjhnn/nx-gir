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
  photographs; `renders/fixes/` the photographs and
  the model side by side, one picture per part
  fixed.

## Running

Blender 4.2 LTS (`blender` on the path), headless:

    blender -b --factory-startup -P blender/glakavank.py \
        -- [--quick] [--no-render] [--glb] [--views=a,b]

It writes `blender/out/`: `glakavank.blend` (open it
in Blender to look round), a render of each view of
the photographs (`VIEWS` in `glakavank.py`) and, with
`--glb`, `glakavank.glb` (1K textures, Draco). With
`--quick`: 1K textures, small renders, a few
samples: about 1.5 minutes on 4 cores; the full one
takes about 20 minutes. `--views=belfry,drums`
renders only those views; besides the views of the
photographs there are close views to check the
details: `belfry`, `drums`, `hall`.

Blender 4.2 LTS can be fetched from
<https://download.blender.org/release/Blender4.2/>
(`blender-4.2.*-linux-x64.tar.xz`).

## On the web page

`blender/web.sh glakavank` builds the buildings for the
page `/3d/glakavank`: `web/models/glakavank/` holds a
`.gltf`, its `.bin` and its textures (512 pixels,
colour and relief maps), read by `web/model3d.js` with
the loader `web/vendor/three/gltf.min.js`; the page
draws its own ground and bushes (`height()` is the
same in both). Not one `.glb`, and no Draco: the
page's rules (CSP) forbid the `blob:` addresses and
workers they need. The script then welds the vertices
and stores them in fewer bits (gltf-transform,
`KHR_mesh_quantization`): about 4.8 MB in all, loaded
only on that page.

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

## State (2026-11-25)

The full build takes about 15 minutes on 4 cores
(each render 3-4 minutes). `glakavank.glb`: 10.6 MB,
of which 8.5 MB are the 27 texture pictures (9
materials, 3 maps each, 1K) and about 2 MB the
meshes: too big for a phone yet. To do before the
web: smaller pictures (512 for the far materials, no
roughness map where it adds little), a lighter ground
(it is 300x300 squares), better trees and slopes
(grass and rock mixed, not one texture).

## Compared with the photographs, part by part (2026-11-25)

Fixed, each with a picture in `renders/fixes/`:

1. The belfry: cusped (five-lobed) arches, a high
   frieze and a plain roof above. The lower stage
   is an octagon in plan, four wide faces and four
   narrow corners cut off; roll mouldings stepping
   in round its arches, ringed shafts, steep gables
   with crockets and a finial (no rosettes); in each
   corner a tall gabled niche carved in, a small
   shrine at its foot; small pinnacles; low gables
   whose tops are level with the foot of the second
   stage (measured again from the photographs: the
   first stage about 7.7 m to there); no bell
   (none is seen), a ladder.
2. The drums, each its own: Stepanos in a patchwork
   of light and dark stone with a ring, a band of
   squares and a framed window; Karapet with eight
   tall pointed blind arches, light panels in them,
   a cone curved like a bell. Both flare at the foot;
   an iron cross, no gilt ball.
3. The hall: few windows, set as in the photographs
   (rectangles with bars, framed panels with a carved
   slab over them, one tall arched); three thin dark
   courses; dark stones scattered; lozenges at the
   foot of the west front; a thin slab cornice, no
   parapet; the clay jars along the south wall.
4. The roofs: low gabled arms round the drums with
   stone gables and windows; Gevorg's flat earth
   roof and barred windows; a flat-roofed hut on the
   hall's roof, right behind the belfry.

5. The porch front: one tall pointed portal in a
   frame, three small arched openings over it
   between two light slabs, tall blind niches with
   carved crowns; on the south and north faces two
   framed windows high, a blind niche, a pilaster;
   shafts at the corners; no rosette slabs.
6. The south front (Lynch Fig. 155, `SOUTH`):
   blocks of different heights, the top sloping
   down to the east, a small square tower at the
   east end, chimneys, the great round tower where
   the photograph has it; no round towers at the
   south corners; the south range ends where the
   wall falls away.
7. The court: a wooden railing on the galleries'
   upper floor, their upper arches larger than the
   lower; trees behind the belfry, the cypress
   behind the hut.

Still to do:

- The north corner towers are not seen in any
  photograph; kept for now.
- The ground is flat round the walls; Fig. 155 has
  the slope steeper on the south.
- The web page (`web.sh`) still has the model
  before these fixes.
