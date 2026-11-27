#!/bin/sh
# Makes the fonts reel: reel/nxgir-fonts-reel.mp4.
# Run from the repository root. Needs Pillow, numpy,
# scipy, ffmpeg and Playwright for Node.
#   sh reel/make.sh            the video
#   sh reel/make.sh 3,13.5     stills in reel/build/
set -e
python3 reel/prep.py
: "${NODE_PATH:=/opt/node-tools/node_modules}"
export NODE_PATH
dir="$(pwd)/reel"
if [ -n "$1" ]; then
  node reel/record.js "$dir" - "$1"
else
  node reel/record.js "$dir" \
    "$dir/nxgir-fonts-reel.mp4"
fi
