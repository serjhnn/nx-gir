import importlib.util
from pathlib import Path

ROOT = Path(__file__).parent.parent
path = ROOT / "scripts/render-birds.py"
spec = importlib.util.spec_from_file_location("rb", path)
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)


def test_svgs_match_the_script():
    # edit scripts/render-birds.py and run it, not the
    # SVGs in web/
    for name, text in rb.drawings().items():
        saved = (ROOT / "web" / name).read_text("utf-8")
        assert saved == text, name


def test_svgs_fit_60_columns():
    for text in rb.drawings().values():
        for line in text.splitlines():
            assert len(line) <= 60, line
