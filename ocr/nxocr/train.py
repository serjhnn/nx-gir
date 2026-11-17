"""Fine-tune Tesseract's LSTM on line samples.

Steps: write_samples (line PNG, text, box file), then
make_lstmf (Tesseract's own training format), then
fine_tune (lstmtraining, continuing from the base model)
and finalize (a .traineddata to use with -l).
"""

import subprocess
from pathlib import Path

LIST = "lstmf.txt"


def fold(page, first=26, block=5, every=4):
    """True if the page is held out for testing.

    Whole blocks of pages are held out, not single
    pages, so a test page has no neighbour in training.
    """
    return ((page - first) // block) % every == every - 1


def half(page, first=26, block=5, every=4):
    """`dev` or `test` for a held-out page, else None.

    The held-out blocks are split in two: the first half
    is for choosing settings (post-correction), the second
    for the numbers reported, so the settings are never
    chosen on the pages they are scored on.
    """
    if not fold(page, first, block, every):
        return None
    n = (page - first) // block // every
    return "dev" if n < 3 else "test"


def write_sample(folder, name, img, text):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    img.save(folder / f"{name}.png")
    (folder / f"{name}.gt.txt").write_text(
        text + "\n", encoding="utf8"
    )
    w, h = img.size
    box = (
        f"WordStr 0 0 {w} {h} 0 #{text}\n\t 0 0 {w} {h} 0\n"
    )
    (folder / f"{name}.box").write_text(
        box, encoding="utf8"
    )


def make_lstmf(folder, tessdata, lang="hye"):
    """Make name.lstmf for every sample; write the list."""
    folder = Path(folder)
    done = []
    for png in sorted(folder.glob("*.png")):
        base = png.with_suffix("")
        out = Path(f"{base}.lstmf")
        if not out.exists():
            subprocess.run(
                [
                    "tesseract",
                    str(png),
                    str(base),
                    "--tessdata-dir",
                    str(tessdata),
                    "-l",
                    lang,
                    "--psm",
                    "13",
                    "lstm.train",
                ],
                check=True,
                capture_output=True,
            )
        if out.exists():
            done.append(str(out))
    (folder / LIST).write_text("\n".join(done) + "\n")
    return len(done)


def extract_lstm(traineddata, out):
    subprocess.run(
        [
            "combine_tessdata",
            "-e",
            str(traineddata),
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def fine_tune(
    base,
    lstm,
    train_dir,
    eval_dir,
    work,
    steps,
    rate=0.0002,
):
    """Run lstmtraining; returns the checkpoint prefix."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    prefix = work / "model"
    cmd = [
        "lstmtraining",
        "--model_output",
        str(prefix),
        "--continue_from",
        str(lstm),
        "--traineddata",
        str(base),
        "--train_listfile",
        str(Path(train_dir) / LIST),
        "--eval_listfile",
        str(Path(eval_dir) / LIST),
        "--max_iterations",
        str(steps),
        "--learning_rate",
        str(rate),
    ]
    log = work / "train.log"
    with open(log, "w") as fh:
        subprocess.run(
            cmd, check=True, stdout=fh, stderr=fh
        )
    return prefix


def finalize(prefix, base, out):
    """Best checkpoint -> a .traineddata file."""
    subprocess.run(
        [
            "lstmtraining",
            "--stop_training",
            "--continue_from",
            f"{prefix}_checkpoint",
            "--traineddata",
            str(base),
            "--model_output",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
