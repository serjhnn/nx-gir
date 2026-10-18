#!/usr/bin/env python3
"""Render README screenshots of nxgir to docs/*.png.

Runs ./nxgir in a pseudo-terminal, presses keys, reads
the screen with pyte and draws it with Pillow. Needs
(for this script only):

    pip install pyte pillow

Run again after changing the screens:

    scripts/render-screens.py
"""

import fcntl
import os
import pty
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import time
from pathlib import Path

import pyte
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SIZE = 20  # font size in pixels
LINE = 26  # line height in pixels
DARK = (30, 30, 30)
LIGHT = (220, 220, 220)
NAMED = {
    "black": "000000",
    "red": "cd0000",
    "green": "00cd00",
    "brown": "cdcd00",
    "blue": "0000ee",
    "magenta": "cd00cd",
    "cyan": "00cdcd",
    "white": "e5e5e5",
}


def font(bold=False):
    """DejaVu Sans Mono (has Armenian), via fc-match."""
    name = "DejaVu Sans Mono"
    if bold:
        name += ":bold"
    path = None
    if shutil.which("fc-match"):
        out = subprocess.run(
            ["fc-match", "-f", "%{file}", name],
            capture_output=True,
            text=True,
        )
        path = out.stdout.strip() or None
    if not path:
        sys.exit("font not found: install DejaVu fonts")
    return ImageFont.truetype(path, SIZE)


def run(keys, cols, rows, env=None):
    """Start nxgir ls, press keys, return the screen."""
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)
    pid, fd = pty.fork()
    if pid == 0:
        os.environ.update(
            TERM="screen-256color",
            LANG="C.UTF-8",
            LC_ALL="C.UTF-8",
            **(env or {}),
        )
        size = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(0, termios.TIOCSWINSZ, size)
        os.chdir(ROOT)
        os.execv("./nxgir", ["./nxgir", "ls"])

    def pump(wait):
        end = time.time() + wait
        while time.time() < end:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                try:
                    stream.feed(os.read(fd, 65536))
                except OSError:
                    return

    pump(1.0)
    for k in keys:
        os.write(fd, k.encode())
        pump(0.4)
    # pyte can miss parts of curses' partial updates;
    # a resize signal makes nxgir repaint everything
    os.kill(pid, signal.SIGWINCH)
    pump(0.6)
    os.kill(pid, signal.SIGTERM)
    os.waitpid(pid, 0)
    os.close(fd)
    return screen


def color(name, default):
    name = NAMED.get(name, name)
    if name == "default":
        return default
    return tuple(
        int(name[i : i + 2], 16) for i in (0, 2, 4)
    )


def draw(screen):
    """The screen as an image."""
    regular, bold = font(), font(bold=True)
    cw = int(regular.getlength("M"))
    w, h = screen.columns * cw, screen.lines * LINE
    img = Image.new("RGB", (w, h), DARK)
    d = ImageDraw.Draw(img)
    for y in range(screen.lines):
        for x in range(screen.columns):
            ch = screen.buffer[y][x]
            fg = color(ch.fg, LIGHT)
            bg = color(ch.bg, DARK)
            if ch.reverse:
                fg, bg = bg, fg
            x0, y0 = x * cw, y * LINE
            d.rectangle(
                [x0, y0, x0 + cw, y0 + LINE], fill=bg
            )
            if ch.data.strip():
                f = bold if ch.bold else regular
                d.text(
                    (x0, y0 + 2), ch.data, font=f, fill=fg
                )
            if ch.underscore:
                yy = y0 + LINE - 3
                d.line([x0, yy, x0 + cw, yy], fill=fg)
    return img


def grid(images, per_row, pad=16, scale=2 / 3):
    """Images side by side in rows, on white."""
    w, h = images[0].size
    rows = -(-len(images) // per_row)
    sheet = Image.new(
        "RGB",
        (per_row * (w + pad) + pad, rows * (h + pad) + pad),
        (255, 255, 255),
    )
    for k, im in enumerate(images):
        x = pad + (k % per_row) * (w + pad)
        y = pad + (k // per_row) * (h + pad)
        sheet.paste(im, (x, y))
    size = (
        int(sheet.width * scale),
        int(sheet.height * scale),
    )
    return sheet.resize(size, Image.LANCZOS)


def save(img, path):
    """Save as a small palette PNG."""
    img = img.quantize(colors=64, method=Image.MEDIANCUT)
    img.save(path, optimize=True)


# keys to open test/grabar_john.txt from the list
OPEN_JOHN = ["jj", "\r"]
THEMES = ["sepia", "night", "gold", "paper", "tuff", "ink"]


def main():
    DOCS.mkdir(exist_ok=True)
    shots = {
        "screen-list.png": run([], 46, 12),
        "screen-reader.png": run(
            OPEN_JOHN + ["jjjjjjjww", "s"], 42, 22
        ),
        "screen-wide.png": run(
            OPEN_JOHN + ["jjjjjjjww", "s"], 100, 18
        ),
    }
    for name, screen in shots.items():
        save(draw(screen), DOCS / name)
        print(f"docs/{name}")
    images = [
        draw(
            run(
                OPEN_JOHN + ["jjjjjjj", "T"],
                42,
                18,
                {"NXGIR_THEME": theme},
            )
        )
        for theme in THEMES
    ]
    save(grid(images, 3), DOCS / "screen-themes.png")
    print("docs/screen-themes.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
