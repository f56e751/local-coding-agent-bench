"""Implement search_rotated below.

Grader runs: pytest tests/ -v
Time constraint: O(log n).
"""


def search_rotated(nums, target):
    """Return the index of `target` in the rotated sorted array `nums`,
    or -1 if `target` is not present.

    The input `nums` is a distinct-value array originally sorted ascending,
    then rotated by some unknown amount. Must run in O(log n) time.
    """
    if not nums:
        return -1
    
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        # Determine which side is properly sorted
        if nums[left] <= nums[mid]:
            # Left side is sorted
            if nums[left] <= target < nums[mid]:
                # Target is in the left side
                right = mid - 1
            else:
                # Target is in the right side
                left = mid + 1
        else:
            # Right side is sorted
            if nums[mid] < target <= nums[right]:
                # Target is in the right side
                left = mid + 1
            else:
                # Target is in the left side
                right = mid - 1
    
    return -1
