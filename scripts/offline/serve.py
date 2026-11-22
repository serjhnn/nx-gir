#!/usr/bin/env python3
"""Read nxGir offline: python3 serve.py [PORT]

Serves this folder at http://localhost:8000/ and opens
it in the browser. Stop with Ctrl+C. Nothing leaves
your computer: the server listens on localhost only.
"""

import functools
import http.server
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    """Files as they are; a page of the app (a path
    like /library, which is no file) gets index.html,
    and app.js reads the address."""

    def do_GET(self):
        want = self.headers.get("Accept", "")
        if (
            "text/html" in want
            and not Path(
                self.translate_path(self.path.split("?")[0])
            ).exists()
        ):
            self.path = "/index.html"
        super().do_GET()


def main(argv):
    port = int(argv[0]) if argv else 8000
    handler = functools.partial(
        Handler,
        directory=str(HERE),
    )
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", port), handler
    )
    url = f"http://localhost:{port}/"
    print(f"nxGir: {url}  (stop with Ctrl+C)")
    try:
        webbrowser.open(url)
    except Exception:
        pass  # no browser here: open the address
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
