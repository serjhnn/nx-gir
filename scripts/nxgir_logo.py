"""nx-gir logos and their gradient colors.

Used by the shell (nxgir-cli.py) and by render-logo.py
for the README image.
"""

LOGO_HY = r"""
 ____                           __
/_/ / __  ____         ____ _  / /_    ____
 / / / / / __ \  ____ / __ `/ / __ \  / __ \
/ /_/ / / / / / /___// /_/ / / / / / / / / /
\__,_/ /_/ / /__     \__, _ / / /_/ / / /_/
          /____/       /_/ /_/     /_/
""".strip("\n").splitlines()

LOGO_HY_UPRIGHT = r"""
 ____                              _
|__  |  _   _ __           __ _   | |__    _ __
   | | | | | '_ \   ___   / _` |  | '_ \  | '_ \
   | |_| | | | | | |___| | (_| |  | | | | | | | |
    \__,_| |_| | |__      \__, |_ | | |_| | | |_|
               |____|        |_|  |_|     |_|
""".strip("\n").splitlines()

LOGO_HY_BLOCK = r"""
  ▄▄▄                              ▄▄
 ▀███                              ██
   ██   ▄▄  ▄▄ ▄▄▄        ▄▄▄ ▄▄   ██ ▄▄▄  ▄▄ ▄▄▄
   ██   ██  ███▀██▄      ▄██▀███   ███▀███ ███████
   ██   ██  ██▀  ██ ▄▄▄▄ ██   ██   ██▀  ██ ███  ██
   ██  ▄██  ██   ██ ▀██▀ ██   ██   ██   ██ ███  ██
   ███▄███  ██   ██      ▀██▄███▄▄ ██   ██ ███  ██
    ▀▀▀▀▀▀  ▀▀   ██       ▀▀▀▀██▀▀ ██   ▀▀ ███  ▀▀
                 ███▄         ██   ██      ███
                 ▀▀▀          ▀▀   ▀▀      ▀▀
""".strip("\n").splitlines()

LOGO_EN = r"""
         _  __            _
   ____ | |/ /     ____ _(_)____
  / __ \|   /_____/ __ `/ / ___/
 / / / /   /_____/ /_/ / / /
/_/ /_/_/|_|     \__, /_/_/
                /____/
""".strip("\n").splitlines()

LOGOS = {
    "hy": LOGO_HY,
    "hy-upright": LOGO_HY_UPRIGHT,
    "hy-block": LOGO_HY_BLOCK,
    "en": LOGO_EN,
}
DESCRIPTIONS = {
    "hy": "Armenian, slanted (default)",
    "hy-upright": "Armenian, upright",
    "hy-block": "Armenian, blocks",
    "en": "Latin",
}
DEFAULT_LOGO = "hy"

# Gradient colors (RGB).
RED = (200, 16, 46)
GOLD = (255, 196, 0)
TOP, BOTTOM = GOLD, RED


def row_colors(n, start=TOP, end=BOTTOM):
    """RGB color for each of n rows, start to end."""
    span = max(n - 1, 1)
    return [
        tuple(
            round(a + (b - a) * row / span)
            for a, b in zip(start, end)
        )
        for row in range(n)
    ]
