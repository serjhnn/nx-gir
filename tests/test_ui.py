from nxgir_ui import (
    DIMS,
    PALETTES,
    PLAIN,
    THEME_NAMES,
    THEMES,
    fade,
    fit,
    help_line,
    shorten,
    tail,
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


ITEMS = (
    ("w/b", "word", 0),
    ("/", "find", 1),
    ("z", "margins", 2),
    ("L", "spacing", 2),
    ("q", "back", 0),
)


def test_help_line_adds_items_by_priority():
    assert help_line(ITEMS, 200) == (
        "w/b word · / find · z margins · L spacing · q back"
    )
    # "/ find" comes before z, but stays in its place
    find = "w/b word · / find · q back"
    assert help_line(ITEMS, 27) == find
    assert help_line(ITEMS, 26) == "w/b word · q back"
    assert help_line(ITEMS, 20) == "w/b word · q back"


def test_help_line_falls_back_to_keys():
    assert help_line(ITEMS, 12) == "w/b / z L q"
    assert help_line(ITEMS, 8) == "w/b / q"
    # too narrow even for the keys: they are kept
    assert help_line(ITEMS, 3) == "w/b q"


def test_help_line_fits():
    for w in range(6, 80):
        assert len(help_line(ITEMS, w)) < w


def test_fade_none_keeps_color():
    assert fade(94, 230, 0) == 94


def test_dim_levels_differ_and_stay_visible():
    for name, pal in PALETTES.items():
        fg, bg = pal["text"], pal["bg"]
        levels = [fade(fg, bg, d) for d in DIMS]
        assert len(set(levels)) == len(DIMS), name
        assert bg not in levels, name
        # each level is closer to the page than the last
        ratios = [contrast(c, bg) for c in levels]
        assert ratios == sorted(ratios, reverse=True), name
        assert ratios[-1] > 1.3, (name, ratios)


def test_shorten_keeps_file_name():
    p = "grabar/bible/new-testament/2-mark.txt"
    assert shorten(p, 60) == p
    assert shorten(p, 30) == "…/new-testament/2-mark.txt"
    assert shorten(p, 20) == "…/2-mark.txt"
    assert len(shorten(p, 8)) <= 8
    assert shorten(p, 8).endswith("txt")
    for w in range(1, 45):
        assert len(shorten(p, w)) <= w


def test_tail_shows_end():
    assert tail("note: abc", 20) == "note: abc"
    assert tail("note: abcdef", 6) == "…bcdef"
    assert len(tail("x" * 50, 10)) == 10
