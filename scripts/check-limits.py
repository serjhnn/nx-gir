#!/usr/bin/env python3
"""How close nx-gir is to the limits of GitHub and of
a phone: a few numbers and the share of each limit.

    scripts/check-limits.py           quick (seconds)
    scripts/check-limits.py --site    also build the
        Pages site in a temporary folder and time it
    scripts/check-limits.py --site --record
        and add a line to notes/limits.tsv, to
        compare with later

The measures are in nxgir_limits.py; the limits and
what they mean are explained in notes/limits.md. The
same numbers are on the Statistics page of the web
reader.
"""

import importlib.util
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import nxgir_limits as lim  # noqa: E402


def site(out):
    """Build the Pages site into out: (bytes, seconds)."""
    path = HERE / "build-site.py"
    spec = importlib.util.spec_from_file_location(
        "build_site", path
    )
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    start = time.monotonic()
    bs.build(out, bs.shelf_files())
    took = time.monotonic() - start
    return lim.folder_size(out), took


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    m = lim.measure()
    if "--site" in argv:
        with tempfile.TemporaryDirectory() as tmp:
            m["site"], m["build"] = site(Path(tmp) / "site")
    print("\n".join(lim.report(m)))
    if "--record" in argv:
        lim.record(m)
        print(f"added to {lim.HISTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
