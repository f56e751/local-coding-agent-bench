"""T2 grader — merge_intervals."""
import sys
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "starter"))

from solution import merge_intervals  # noqa: E402


def _listify(result):
    """Normalize result to list[tuple[int,int]] for comparison."""
    return [tuple(iv) for iv in result]


def test_empty():
    assert _listify(merge_intervals([])) == []

def test_single():
    assert _listify(merge_intervals([(1, 3)])) == [(1, 3)]

def test_already_sorted_no_overlap():
    assert _listify(merge_intervals([(1, 2), (3, 4), (5, 6)])) == [(1, 2), (3, 4), (5, 6)]

def test_simple_overlap():
    assert _listify(merge_intervals([(1, 3), (2, 6)])) == [(1, 6)]

def test_classic_leetcode_example():
    assert _listify(merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)])) == [(1, 6), (8, 10), (15, 18)]

def test_unsorted_input():
    assert _listify(merge_intervals([(8, 10), (1, 3), (2, 6), (15, 18)])) == [(1, 6), (8, 10), (15, 18)]

def test_fully_nested():
    assert _listify(merge_intervals([(1, 10), (2, 5), (3, 7)])) == [(1, 10)]

def test_chain_of_overlaps():
    assert _listify(merge_intervals([(1, 4), (3, 6), (5, 8), (7, 10)])) == [(1, 10)]

def test_touching_not_overlapping_half_open():
    # Half-open: [1,4) and [4,5) share only the point 4 (excluded from first).
    # Per PROMPT they do NOT overlap.
    assert _listify(merge_intervals([(1, 4), (4, 5)])) == [(1, 4), (4, 5)]

def test_duplicates():
    assert _listify(merge_intervals([(1, 4), (1, 4), (1, 4)])) == [(1, 4)]

def test_empty_interval_dropped():
    assert _listify(merge_intervals([(5, 5), (1, 3)])) == [(1, 3)]

def test_all_empty_intervals():
    assert _listify(merge_intervals([(2, 2), (5, 5)])) == []

def test_empty_interval_inside_larger_is_dropped():
    # (3,3) is empty; (1,5) still stands.
    assert _listify(merge_intervals([(1, 5), (3, 3)])) == [(1, 5)]

def test_negative_values():
    assert _listify(merge_intervals([(-5, -1), (-3, 2), (4, 7)])) == [(-5, 2), (4, 7)]

def test_single_point_at_boundary():
    # (4,4) empty dropped; (1,4) and (4,6) touch but don't overlap.
    assert _listify(merge_intervals([(1, 4), (4, 4), (4, 6)])) == [(1, 4), (4, 6)]

def test_large_chain_merges_to_one():
    n = 1000
    ivs = [(i, i + 2) for i in range(n)]
    # Each overlaps the next (i+1 < i+2), so all merge into [0, n+1).
    assert _listify(merge_intervals(ivs)) == [(0, n + 1)]

def test_random_stress_equivalent_to_naive():
    """Compare against a naive O(n * range) point-set implementation."""
    random.seed(42)
    for _ in range(50):
        n = random.randint(0, 30)
        ivs = []
        for _ in range(n):
            a = random.randint(-20, 20)
            b = random.randint(a, a + 15)  # could be empty (a == b)
            ivs.append((a, b))
        out = _listify(merge_intervals(list(ivs)))
        # naive reference: union of [a,b) via integer point set
        points = set()
        for a, b in ivs:
            for x in range(a, b):
                points.add(x)
        # reconstruct merged intervals from points
        expected = []
        sp = sorted(points)
        if sp:
            cur_start = sp[0]
            prev = sp[0]
            for x in sp[1:]:
                if x == prev + 1:
                    prev = x
                else:
                    expected.append((cur_start, prev + 1))
                    cur_start = x
                    prev = x
            expected.append((cur_start, prev + 1))
        assert out == expected, (
            f"mismatch for input {ivs}\n  got:      {out}\n  expected: {expected}"
        )

def test_returned_type_is_list_of_tuples_or_list_of_lists():
    r = merge_intervals([(1, 3), (2, 6)])
    assert isinstance(r, list)
    assert len(r) == 1
    assert len(r[0]) == 2
    # Each element tuple or list of ints:
    assert isinstance(r[0][0], int) and isinstance(r[0][1], int)

def test_output_sorted_by_start():
    result = _listify(merge_intervals([(10, 12), (1, 3), (5, 7)]))
    starts = [iv[0] for iv in result]
    assert starts == sorted(starts)

def test_does_not_mutate_input():
    inp = [(3, 5), (1, 2)]
    _ = merge_intervals(inp)
    assert inp == [(3, 5), (1, 2)], "input list was mutated"
