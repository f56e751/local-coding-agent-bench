"""Implement merge_intervals.

See PROMPT.md for the exact overlap rule and edge cases.
"""
from __future__ import annotations


def merge_intervals(intervals):
    """Return a list of merged half-open intervals, sorted by start."""
    # Filter out empty intervals (where start == end)
    filtered_intervals = [(start, end) for start, end in intervals if start < end]
    
    # Handle empty input
    if not filtered_intervals:
        return []
    
    # Sort intervals by start time
    filtered_intervals.sort()
    
    # Merge overlapping intervals
    merged = [filtered_intervals[0]]
    
    for current_start, current_end in filtered_intervals[1:]:
        last_start, last_end = merged[-1]
        
        # Check if current interval overlaps with the last merged interval
        # Two intervals [a, b) and [c, d) overlap iff a < d and c < b
        if last_start < current_end and current_start < last_end:
            # Merge them by extending the end of the last interval
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add the current interval
            merged.append((current_start, current_end))
    
    return merged