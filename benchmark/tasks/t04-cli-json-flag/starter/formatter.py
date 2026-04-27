"""Output formatting for wordcount.

Extend this module to support JSON output for the --output-format flag.
"""
from __future__ import annotations


def format_text(stats: dict) -> str:
    """Render stats in the human-readable text form."""
    return (
        f"Lines: {stats['lines']}\n"
        f"Words: {stats['words']}\n"
        f"Chars: {stats['chars']}"
    )


# TODO(task): add format_json(stats) and wire it from wordcount.py.
