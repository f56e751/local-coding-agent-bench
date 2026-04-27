# Task T2 — Merge Intervals

## Problem

Implement `merge_intervals(intervals)` in `starter/solution.py`.

Given a list of half-open integer intervals `[start, end)` (end exclusive), merge every pair of **overlapping** intervals into a single interval and return the result sorted by start ascending.

- Overlap rule: two intervals `[a, b)` and `[c, d)` overlap iff `a < d and c < b` (strict — sharing only an endpoint does NOT count as overlap because the intervals are half-open).
- Input may be empty, unsorted, contain duplicates, contain nested intervals, or contain single-point intervals where `start == end` (these represent empty intervals and should be dropped from the output).
- Output must contain no overlapping intervals and be sorted by start.

## Examples

```python
merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)])
# → [(1, 6), (8, 10), (15, 18)]

merge_intervals([(1, 4), (4, 5)])
# → [(1, 4), (4, 5)]   # they touch at 4 but don't overlap (half-open)

merge_intervals([(5, 5), (1, 3)])
# → [(1, 3)]           # (5, 5) is an empty interval, dropped
```

## What to modify

Only `starter/solution.py`. Do not touch the tests. Run `pytest tests/ -v` before finishing.

## Constraints

- Python stdlib only.
- Input intervals are tuples of two ints; output must be a list of 2-tuples of ints.
- Expect N up to about 10_000 — `O(n log n)` is fine.
