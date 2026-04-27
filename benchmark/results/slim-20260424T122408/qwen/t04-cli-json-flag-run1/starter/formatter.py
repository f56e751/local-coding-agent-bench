"""Output formatting for wordcount.

Extend this module to support JSON output for the --output-format flag.
"""
from __future__ import annotations
import json


def format_text(stats: dict) -> str:
    """Render stats in the human-readable text form."""
    return (
        f"Lines: {stats['lines']}\n"
        f"Words: {stats['words']}\n"
        f"Chars: {stats['chars']}"
    )


def format_json(stats: dict) -> str:
    """Render stats as a JSON document."""
    return json.dumps(stats)
