from nxgir_ui import (
    PALETTES,
    PLAIN,
    THEME_NAMES,
    THEMES,
    fit,
)


def test_themes_define_every_role():
    for name, spec in THEMES.items():
        assert name in THEME_NAMES
        if spec is not None:
            assert set(spec) == set(PLAIN), name


def test_colors_are_256_color_numbers():
    for pal in PALETTES.values():
        for color in pal.values():
            assert 16 <= color <= 255


def rgb(n):
    """RGB of a 256-color number (16-255)."""
    if n >= 232:
        v = 8 + (n - 232) * 10
        return v, v, v
    n -= 16
    steps = (0, 95, 135, 175, 215, 255)
    return steps[n // 36], steps[n // 6 % 6], steps[n % 6]


def contrast(a, b):
    """WCAG contrast ratio of two 256-color numbers."""

    def lum(n):
        c = [x / 255 for x in rgb(n)]
        c = [
            x / 12.92
            if x <= 0.03928
            else ((x + 0.055) / 1.055) ** 2.4
            for x in c
        ]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_themes_are_readable():
    # 4.5:1 is the WCAG guideline for body text
    for name, pal in PALETTES.items():
        for role in ("text", "title", "help", "mark"):
            ratio = contrast(pal[role], pal["bg"])
            assert ratio >= 4.5, (name, role, ratio)


def test_fit_picks_longest_that_fits():
    texts = ("a long help line", "short", "s")
    assert fit(texts, 40) == "a long help line"
    assert fit(texts, 8) == "short"
    assert fit(texts, 2) == "s"
    assert fit(texts, 1) == "s"
