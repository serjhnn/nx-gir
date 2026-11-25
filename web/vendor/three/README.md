# three.js

`three.min.js` is three.js r187 (npm `three@0.187.0`,
MIT, see `LICENSE`), the whole library in one ES
module, made with esbuild:

    npm install three@0.187.0 esbuild
    echo 'export * from "three";' > all.js
    npx esbuild all.js --bundle --minify \
      --format=esm --legal-comments=inline \
      --outfile=three.min.js

Only the 3D map loads it (`web/map3d.js`, opened
by `map3dPage()` in `app.js`), when that page is
opened. It is not in the files the first screen
needs (`SHELL` in `web/sw.js`).
