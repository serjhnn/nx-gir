#!/bin/sh
# Build a Blender model for the web page: the buildings
# as web/models/<name>/ (a .gltf, its .bin and its
# textures), then welded and squeezed (16-bit
# positions, 8-bit normals: KHR_mesh_quantization) by
# gltf-transform (npm @gltf-transform/cli, Node.js).
#
#     blender/web.sh glakavank
set -e
name=${1:-glakavank}
root=$(cd "$(dirname "$0")/.." && pwd)
out="$root/web/models/$name"
blender -b --factory-startup -P "$root/blender/$name.py" \
    -- --no-render --web
tmp=$(mktemp -d)
npx -y @gltf-transform/cli@4.1.0 weld \
    "$out/$name.gltf" "$tmp/a.gltf"
npx -y @gltf-transform/cli@4.1.0 quantize \
    "$tmp/a.gltf" "$tmp/$name.gltf" \
    --quantize-position 14 --quantize-normal 8 \
    --quantize-texcoord 12
rm -f "$tmp/a.gltf" "$tmp/a.bin" "$out"/*
cp "$tmp"/* "$out/"
rm -rf "$tmp"
du -sh "$out"
