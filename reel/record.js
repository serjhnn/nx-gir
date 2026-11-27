// Records reel.html into an mp4, frame by frame.
//   node record.js DIR OUT.mp4    the video
//   node record.js DIR - 3,13.5   stills in DIR/shots/
// DIR is the folder of reel.html (run prep.py first).
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const [, , dir, out, only] = process.argv;
const FPS = 30;

function ffmpeg(out) {
  const a = [
    "-y", "-f", "image2pipe", "-r", "" + FPS,
    "-i", "-",
    // a silent track: Instagram wants audio
    "-f", "lavfi", "-i",
    "anullsrc=r=44100:cl=stereo", "-shortest",
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-movflags", "+faststart", out,
  ];
  return spawn("ffmpeg", a,
    { stdio: ["pipe", "ignore", "inherit"] });
}

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage(
    { viewport: { width: 1080, height: 1920 } });
  await p.goto("file://" + dir + "/reel.html");
  await p.evaluate(() => init());
  if (only) {
    fs.mkdirSync(dir + "/shots", { recursive: true });
    for (const t of only.split(",")) {
      await p.evaluate((t) => render(t), +t);
      const path = `${dir}/shots/shot-${t}.png`;
      await p.screenshot({ path });
    }
    await b.close();
    return;
  }
  const T = await p.evaluate(() => TOTAL);
  const ff = ffmpeg(out);
  for (let f = 0; f < T * FPS; f++) {
    await p.evaluate((t) => render(t), f / FPS);
    const buf = await p.screenshot(
      { type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf))
      await new Promise((r) => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await b.close();
})();
