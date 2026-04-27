"""Implement merge_intervals.

See PROMPT.md for the exact overlap rule and edge cases.
"""
from __future__ import annotations


def merge_intervals(intervals):
    """Return a list of merged half-open intervals, sorted by start."""
    # Drop empty intervals (start == end) and sort by start.
    filtered = sorted(
        ((a, b) for a, b in intervals if a < b),
        key=lambda iv: iv[0],
    )
    merged = []
    for start, end in filtered:
        if merged and start < merged[-1][1]:
            # Overlap: extend the last interval's end if needed.
            prev_start, prev_end = merged[-1]
            if end > prev_end:
                merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))
    return merged
