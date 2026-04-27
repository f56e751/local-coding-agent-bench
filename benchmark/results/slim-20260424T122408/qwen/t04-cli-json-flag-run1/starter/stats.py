"""Line / word / character counting."""
from __future__ import annotations


def count(text: str) -> dict:
    """Return {'lines', 'words', 'chars'} for the given text.

    Lines are counted by newline characters; a trailing newline does not
    add an extra (empty) line.  `text.split()` is used for words, matching
    POSIX wc semantics (any whitespace as separator).
    """
    if not text:
        return {"lines": 0, "words": 0, "chars": 0}
    lines = text.count("\n")
    if not text.endswith("\n"):
        lines += 1  # last line has no trailing newline
    return {
        "lines": lines,
        "words": len(text.split()),
        "chars": len(text),
    }
