"""Compare OCR and typed text fairly.

The typed books and the OCR differ in things that are
not recognition errors: spacing, line breaks, the
punctuation marks, case. `key()` removes them.
"""

import re
import unicodedata

# Armenian punctuation, and the stress marks
MARKS = "՛՜՝՞՚՟։՝՛՜՞՚.,;:!?()[]«»\"'`’‘-–—…·"
DROP = re.compile("[\\s" + re.escape(MARKS) + "՚-՟։֊]")
NUMBERS = re.compile(r"[0-9]+")


def key(text):
    """Letters only, lower case, `և` as `եւ`."""
    text = unicodedata.normalize("NFC", text)
    text = text.casefold().replace("և", "եւ")
    text = NUMBERS.sub("", text)
    return DROP.sub("", text)


def join_hyphens(text):
    """Join words broken at a line end (`լըլա-`)."""
    return re.sub(r"[-֊]\s*\n\s*", "", text)


def words(text):
    """Words, without marks, as a list."""
    text = join_hyphens(text).casefold().replace("և", "եւ")
    out = []
    for w in text.split():
        w = DROP.sub("", NUMBERS.sub("", w))
        if w:
            out.append(w)
    return out
