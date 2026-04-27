# Task T1 — Search in Rotated Sorted Array

You are working in a Python project in your current working directory. Your goal:

1. Read `starter/solution.py` — it declares a function you must implement.
2. Implement `search_rotated(nums, target)` so that every test in `tests/test_solution.py` passes.
3. Your solution **must run in O(log n) time**. A linear scan will fail the performance test in the suite.
4. When you believe you are done, run `pytest tests/ -v` from the project root and confirm a clean green output.

## Problem

An integer array that was originally sorted in **ascending order** has been **rotated at some unknown pivot** (for example `[0,1,2,4,5,6,7]` rotated at index 3 becomes `[4,5,6,7,0,1,2]`). All values are distinct (no duplicates).

Given such a rotated array `nums` and an integer `target`, return the **index** of `target` in `nums`, or `-1` if it is not present.

## Constraints

- Time complexity: **O(log n)** — measured by a test that fails if you call `len(nums)` or iterate more than `4 * ceil(log2(n)) + 4` times.
- Handle edge cases: empty array, single element, array not actually rotated, array rotated so the original start is at the very end.
- No external dependencies. Pure Python only.

## What to modify

Only touch `starter/solution.py`. Do not modify the tests. Do not create new top-level files.
