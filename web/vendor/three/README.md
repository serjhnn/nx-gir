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

`fx.min.js` is the post-processing of three.js r187
(EffectComposer, RenderPass, GTAOPass for the soft
shadows of corners, OutputPass, SMAAPass), bundled
the same way with its own import of three turned
into `./three.min.js`:

    cat > fx.js <<'END'
    export { EffectComposer } from "./node_modules/three/examples/jsm/postprocessing/EffectComposer.js";
    export { RenderPass } from "./node_modules/three/examples/jsm/postprocessing/RenderPass.js";
    export { GTAOPass } from "./node_modules/three/examples/jsm/postprocessing/GTAOPass.js";
    export { OutputPass } from "./node_modules/three/examples/jsm/postprocessing/OutputPass.js";
    export { SMAAPass } from "./node_modules/three/examples/jsm/postprocessing/SMAAPass.js";
    END
    npx esbuild fx.js --bundle --minify --format=esm \
      --external:three --legal-comments=inline \
      --outfile=fx.min.js
    sed -i 's#from"three"#from"./three.min.js"#g' fx.min.js

Only the 3D models load it (`web/model3d.js`).

`gltf.min.js` is three.js r187's GLTFLoader, bundled
the same way, for the models made in Blender
(`blender/`, `web/models/<id>/`):

    echo 'export { GLTFLoader } from "./node_modules/three/examples/jsm/loaders/GLTFLoader.js";' > gl.js
    npx esbuild gl.js --bundle --minify --format=esm \
      --external:three --legal-comments=inline \
      --outfile=gltf.min.js
    sed -i 's#from"three"#from"./three.min.js"#g' gltf.min.js
