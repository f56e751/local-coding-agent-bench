"""T1 grader — pytest suite for search_rotated."""
import math
import sys
from pathlib import Path

# Make the starter importable whether pytest is run from project root or elsewhere.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "starter"))

from solution import search_rotated  # noqa: E402


# ---- Basic correctness (10) ----

def test_found_in_rotated():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4

def test_not_found_in_rotated():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1

def test_unrotated_found():
    assert search_rotated([1, 2, 3, 4, 5, 6], 4) == 3

def test_unrotated_not_found():
    assert search_rotated([1, 2, 3, 4, 5, 6], 7) == -1

def test_target_at_pivot():
    assert search_rotated([5, 6, 7, 1, 2, 3, 4], 1) == 3

def test_target_just_before_pivot():
    assert search_rotated([5, 6, 7, 1, 2, 3, 4], 7) == 2

def test_target_first_element():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 4) == 0

def test_target_last_element():
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 2) == 6

def test_negatives_mixed():
    assert search_rotated([3, 4, -2, -1, 0, 1, 2], -2) == 2

def test_all_negatives_rotated():
    assert search_rotated([-3, -2, -1, -7, -6, -5, -4], -7) == 3


# ---- Edge cases (7) ----

def test_empty_array():
    assert search_rotated([], 1) == -1

def test_single_element_found():
    assert search_rotated([5], 5) == 0

def test_single_element_not_found():
    assert search_rotated([5], 3) == -1

def test_two_elements_rotated_found_first():
    assert search_rotated([3, 1], 3) == 0

def test_two_elements_rotated_found_second():
    assert search_rotated([3, 1], 1) == 1

def test_two_elements_unrotated_found():
    assert search_rotated([1, 3], 3) == 1

def test_full_rotation_equivalent():
    # rotated by len(nums) is the same as unrotated
    assert search_rotated([1, 2, 3, 4, 5], 4) == 3


# ---- Structured (2) ----

def test_rotation_at_every_possible_pivot():
    base = [10, 20, 30, 40, 50, 60, 70, 80]
    for k in range(len(base)):
        rotated = base[k:] + base[:k]
        for v in base:
            idx = search_rotated(rotated, v)
            assert 0 <= idx < len(rotated) and rotated[idx] == v, (
                f"rotation k={k}, v={v}, got idx={idx}"
            )

def test_large_array_returns_correct_index():
    n = 10000
    pivot = 3721
    base = list(range(n))
    rotated = base[pivot:] + base[:pivot]
    for target in (0, 1, n - 1, n // 2, 9999, 3720, 3721):
        idx = search_rotated(rotated, target)
        assert rotated[idx] == target


# ---- Performance — O(log n) enforced ----

class CountingList(list):
    """Every __getitem__ increments an access counter.

    Allows the test to enforce O(log n) behavior without monkeypatching.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accesses = 0

    def __getitem__(self, idx):
        self.accesses += 1
        return super().__getitem__(idx)

    # len() is legal and O(1); we deliberately do NOT count it.


def test_access_count_is_logarithmic():
    n = 8192  # 2^13
    base = list(range(n))
    rotated_list = base[5000:] + base[:5000]
    counting = CountingList(rotated_list)
    idx = search_rotated(counting, 5000)
    assert counting[idx] == 5000
    # Allow a generous constant: 4 * ceil(log2(n)) + 4 = 4*13 + 4 = 56
    limit = 4 * math.ceil(math.log2(n)) + 4
    assert counting.accesses <= limit, (
        f"too many element accesses: {counting.accesses} > {limit} "
        f"(suggests a linear scan, not O(log n))"
    )
