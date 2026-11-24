#!/usr/bin/env python3
"""Record a short video tutorial of the web reader.

Starts the server on a free port with a throwaway
state (so your own positions and notes do not show),
runs scripts/record.js with Playwright for Node, and
turns the .webm into an .mp4 with ffmpeg. Needs
Node.js, ffmpeg and:

    npm install playwright

Run:

    scripts/record-web.py [out.mp4]

The steps and captions are in scripts/record.js.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import nxgir_web as web  # noqa: E402
from nxgir_state import State  # noqa: E402


def files():
    """Every book on the shelf, as nxgir web has it."""
    import importlib.util

    path = ROOT / "scripts" / "nxgir-cli.py"
    spec = importlib.util.spec_from_file_location(
        "cli", path
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli.shelf_files()


def main():
    for tool in ("node", "ffmpeg"):
        if not shutil.which(tool):
            print(f"needs {tool}", file=sys.stderr)
            return 1
    out = Path(
        sys.argv[1] if len(sys.argv) > 1 else "tutorial.mp4"
    ).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        State(tmp / "state.json").save()
        app = web.App(files(), tmp / "state.json")
        srv = web.server(app, port=0)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever)
        t.start()
        try:
            r = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts" / "record.js"),
                    f"http://localhost:{port}",
                    str(tmp / "vid"),
                ],
                env=dict(os.environ),
            )
        finally:
            srv.shutdown()
            srv.server_close()
        if r.returncode:
            return r.returncode
        webm = next((tmp / "vid").glob("*.webm"))
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(webm),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "23",
                "-movflags",
                "+faststart",
                str(out),
            ],
            check=True,
        )
    print(f"{out}: {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
