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


def main(argv):
    port = int(argv[0]) if argv else 8000
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
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
