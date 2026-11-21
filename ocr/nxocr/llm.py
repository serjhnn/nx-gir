"""The LLM pass: a model re-reads the uncertain words.

The engine's confidence picks the lines to check: a line
with a word under the threshold is sent to the model with
its image, the OCR text (uncertain words in ⟦ ⟧) and the
word-list suggestion for each, if there is one. Most of a
book is not sent. The model may change only the marked
words: a reply that changes the number of words is thrown
away, and a change to a word that was not marked is
ignored. What is left are Corrections (step "llm"), to be
reviewed like the word list's; nothing is rewritten unless
asked.

The backend is a small class (complete()), so a test can
use a fake one. `Anthropic` talks to the Messages API with
the standard library; answers are kept in a cache folder,
so the same line is paid for once.
"""

import base64
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .post import Correction, correct

OPEN, CLOSE = "⟦", "⟧"

SYSTEM = (
    Path(__file__)
    .with_name("llm_prompt.txt")
    .read_text(encoding="utf8")
    .strip()
)


@dataclass
class Item:
    """A line to check."""

    line: int
    words: list  # the OCR words, as text
    flags: list  # indices of the uncertain ones
    hints: dict = field(
        default_factory=dict
    )  # index -> word
    confs: list = field(default_factory=list)
    image: bytes = b""  # PNG of the line

    def text(self):
        out = []
        for i, w in enumerate(self.words):
            out.append(
                f"{OPEN}{w}{CLOSE}"
                if i in self.flags
                else w
            )
        return " ".join(out)


def select(page, conf=80.0, hints=None, images=None):
    """Items for the lines with a word under `conf`.

    hints maps (line, word) to a suggested word; images maps
    a line number to its PNG bytes.
    """
    hints = hints or {}
    images = images or {}
    items = []
    for n, ln in enumerate(page.lines):
        flags = [
            m
            for m, w in enumerate(ln.words)
            if w.conf < conf
        ]
        if not flags:
            continue
        found = {
            m: hints[n, m] for m in flags if (n, m) in hints
        }
        items.append(
            Item(
                n,
                [w.text for w in ln.words],
                flags,
                found,
                [w.conf for w in ln.words],
                images.get(n, b""),
            )
        )
    return items


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def content(items):
    """The user message: each line, image and text."""
    blocks = []
    for k, it in enumerate(items, 1):
        if it.image:
            blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(
                            it.image
                        ).decode(),
                    },
                }
            )
        text = f"Line {k}: {it.text()}"
        for i in sorted(it.hints):
            text += (
                f"\n  suggestion for {OPEN}{it.words[i]}"
                f"{CLOSE}: {it.hints[i]}"
            )
        blocks.append({"type": "text", "text": text})
    return blocks


def parse(reply, count):
    """The list of lines in a reply, or None."""
    m = re.search(r"\{.*\}", reply, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except ValueError:
        return None
    got = (
        data.get("lines")
        if isinstance(data, dict)
        else None
    )
    if not isinstance(got, list) or len(got) != count:
        return None
    if not all(isinstance(s, str) for s in got):
        return None
    return got


def accept(item, reply):
    """{index: new word} for the marked words that changed.

    None if the reply changes the number of words. A change
    to a word that was not marked is ignored.
    """
    new = reply.replace(OPEN, "").replace(CLOSE, "").split()
    if len(new) != len(item.words):
        return None
    return {
        i: new[i]
        for i in item.flags
        if new[i] != item.words[i]
    }


class Pending(Exception):
    """A request waits for an answer (see Files)."""


class Files:
    """A backend for when no API key can be used.

    Each request is written to a folder of its own (the
    prompt and the line images); the answer is read from
    `reply.txt` in it. Whoever answers (a person, an agent)
    only needs that folder. A request with no answer yet
    raises Pending, and `pending` lists the folders.
    """

    def __init__(self, folder):
        self.folder = Path(folder)
        self.pending = []
        self.usage = {
            "input": 0,
            "output": 0,
            "calls": 0,
            "cached": 0,
        }

    def complete(self, system, blocks):
        raw = json.dumps(
            blocks, ensure_ascii=False
        ).encode()
        name = hashlib.sha256(
            system.encode() + raw
        ).hexdigest()[:16]
        folder = self.folder / name
        reply = folder / "reply.txt"
        if reply.exists():
            self.usage["cached"] += 1
            return reply.read_text(encoding="utf8")
        if not folder.exists():
            folder.mkdir(parents=True)
            self.write(folder, system, blocks)
        self.pending.append(folder)
        raise Pending(str(folder))

    @staticmethod
    def write(folder, system, blocks):
        text, k = [system, "", "---", ""], 0
        for b in blocks:
            if b["type"] == "image":
                k += 1
                data = base64.b64decode(b["source"]["data"])
                (folder / f"line-{k}.png").write_bytes(data)
                text.append(f"[image: line-{k}.png]")
            else:
                text.append(b["text"])
        text += [
            "",
            "---",
            "Write your JSON answer to reply.txt.",
        ]
        (folder / "request.md").write_text(
            "\n".join(text) + "\n", encoding="utf8"
        )


class Anthropic:
    """The Messages API, with the standard library.

    The key is ANTHROPIC_API_KEY (any text when the network
    adds the key itself). Answers are cached in `cache`.
    """

    def __init__(self, model, cache=None, max_tokens=2048):
        self.model = model
        self.cache = Path(cache) if cache else None
        self.max_tokens = max_tokens
        base = os.environ.get(
            "ANTHROPIC_BASE_URL",
            "https://api.anthropic.com",
        )
        self.url = base.rstrip("/") + "/v1/messages"
        self.usage = {
            "input": 0,
            "output": 0,
            "calls": 0,
            "cached": 0,
        }

    def complete(self, system, blocks):
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [
                {"role": "user", "content": blocks}
            ],
        }
        raw = json.dumps(body, ensure_ascii=False).encode()
        path = None
        if self.cache:
            name = hashlib.sha256(raw).hexdigest()[:32]
            path = self.cache / f"{name}.json"
            if path.exists():
                self.usage["cached"] += 1
                return json.loads(path.read_text())["text"]
        data = self.post(raw)
        text = "".join(
            b.get("text", "")
            for b in data.get("content", [])
        )
        use = data.get("usage", {})
        self.usage["input"] += use.get("input_tokens", 0)
        self.usage["output"] += use.get("output_tokens", 0)
        self.usage["calls"] += 1
        if path:
            self.cache.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"text": text, "usage": use})
            )
        return text

    def post(self, raw, tries=5):
        key = os.environ.get("ANTHROPIC_API_KEY", "unset")
        head = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        }
        for k in range(tries):
            req = urllib.request.Request(
                self.url, raw, head
            )
            try:
                with urllib.request.urlopen(
                    req, timeout=120
                ) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if (
                    e.code in (429, 500, 502, 503, 529)
                    and k < tries - 1
                ):
                    time.sleep(2**k)
                    continue
                raise RuntimeError(
                    f"API {e.code}: {e.read()[:300]!r}"
                ) from None
        raise RuntimeError("no answer")


def review(items, backend, batch=8):
    """{line: {word index: new word}} from the model."""
    out = {}
    for i in range(0, len(items), batch):
        part = items[i : i + batch]
        try:
            reply = backend.complete(SYSTEM, content(part))
        except Pending:
            continue
        lines = parse(reply, len(part))
        if lines is None:
            continue
        for it, text in zip(part, lines):
            got = accept(it, text)
            if got:
                out[it.line] = got
    return out


def suggest(
    page,
    backend,
    conf=80.0,
    lex=None,
    costs=None,
    images=None,
    batch=8,
    params=None,
):
    """Corrections (step llm) for a Page; no change."""
    hints = {}
    if lex is not None:
        for c in correct(page, lex, costs, params):
            hints[c.line, c.word] = c.new
    items = select(page, conf, hints, images)
    found = review(items, backend, batch)
    out = []
    for it in items:
        for i, new in sorted(
            found.get(it.line, {}).items()
        ):
            out.append(
                Correction(
                    it.line,
                    i,
                    it.words[i],
                    new,
                    0.0,
                    it.confs[i],
                    0.0,
                    "llm",
                )
            )
    return out, len(items)
