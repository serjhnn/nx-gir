from nxgir_ui import PLAIN, THEME_NAMES, THEMES, fit


def test_themes_define_every_role():
    for name, spec in THEMES.items():
        assert name in THEME_NAMES
        if spec is not None:
            assert set(spec) == set(PLAIN), name


def test_sepia_colors_are_256_color_numbers():
    for fg, bg, _ in THEMES["sepia"].values():
        assert 16 <= fg <= 255 and 16 <= bg <= 255


def test_fit_picks_longest_that_fits():
    texts = ("a long help line", "short", "s")
    assert fit(texts, 40) == "a long help line"
    assert fit(texts, 8) == "short"
    assert fit(texts, 2) == "s"
    assert fit(texts, 1) == "s"
