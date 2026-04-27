"""Implement search_rotated below.

Grader runs: pytest tests/ -v
Time constraint: O(log n).
"""
from __future__ import annotations


def search_rotated(nums: list[int], target: int) -> int:
    """Return the index of `target` in the rotated sorted array `nums`,
    or -1 if `target` is not present.

    The input `nums` is a distinct-value array originally sorted ascending,
    then rotated by some unknown amount. Must run in O(log n) time.
    """
    n = len(nums)
    if n == 0:
        return -1

    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = nums[mid]
        if mid_val == target:
            return mid

        lo_val = nums[lo]
        # Determine which half is sorted by comparing lo_val and mid_val.
        if lo_val <= mid_val:
            # Left half [lo..mid] is sorted in ascending order.
            if lo_val <= target < mid_val:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            # Right half [mid..hi] is sorted in ascending order.
            hi_val = nums[hi]
            if mid_val < target <= hi_val:
                lo = mid + 1
            else:
                hi = mid - 1

    return -1
