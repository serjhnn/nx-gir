# The fonts reel

A 47-second Instagram Reel (1080x1920, 30 fps) about
how nxGir Dzeragir and nxGir Bolorgir were made:
`nxgir-fonts-reel.mp4`. Its silent audio track is
there because Instagram wants one; add music in the
app.

## Make it again

    sh reel/make.sh            # the video, ~1.5 min
    sh reel/make.sh 3,13.5     # stills, to look at

Run from the repository root. Needs Pillow, numpy,
scipy, ffmpeg and Playwright for Node (in the cloud
container it is in `/opt/node-tools/node_modules`,
which `make.sh` uses unless `NODE_PATH` is set).

- `prep.py` writes `build/` (not in git): the
  letters (`sources/w541/letters/`) and red capitals
  (`sources/w541/capitals/`) as ink on transparent
  ground, page 163 of W.541 with the boxes of its
  pieces of ink, and the two fonts from `web/fonts/`.
- `reel.html` + `reel.js`: the scenes, drawn on a
  canvas by `render(t)`. `SCENES` holds each scene's
  start; a scene is a function in `S` that draws
  itself and returns its opacity (fades go through
  black).
- `record.js` calls `render()` for every frame and
  pipes the screenshots into ffmpeg.

## Rules for the picture

- Captions sit in the top band (`cap()`, y 330; the
  step pill above it at 250). Instagram covers the
  bottom ~30% (the caption, the account name) and a
  column of buttons on the right, so the content is
  centred at x 500 (`CX`), not 540, and ends above
  y ~1450.
- No sacred words in the words shown
  (CLAUDE.md, Examples).
- The averaging scene (step 3) is an illustration:
  the average itself shifted 14 times, not the
  copies.
- The numbers in the captions come from
  `sources/w541/README.md`; change them together.
