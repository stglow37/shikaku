"""Validate strip witnesses and prevent restricted certificates becoming global."""

import importlib.util
import unittest

from shikaku import Rect, validate_partition
from shikaku.solvers.strips import solve, width_partitions


HAS_ORTOOLS = importlib.util.find_spec("ortools") is not None


def strip_oracle(n):
    """Independent exhaustive DP from every ordered composition of each strip."""
    configs = []
    for height in range(1, n + 1):
        for cuts in range(1 << (n - 1)):
            widths = []
            last = 0
            for col in range(1, n):
                if cuts & (1 << (col - 1)):
                    widths.append(col - last)
                    last = col
            widths.append(n - last)
            configs.append((height, frozenset(height * w for w in widths)))
    states = [{frozenset()}] + [set() for _ in range(n)]
    for row in range(n):
        for areas in states[row]:
            for height, added in configs:
                if row + height <= n:
                    states[row + height].add(areas | added)
    return max(map(len, states[n]))


class StripTests(unittest.TestCase):
    def test_partitions(self):
        expected = {(5,), (1, 4), (2, 3), (1, 1, 3), (1, 2, 2)}
        self.assertEqual(set(width_partitions(5, 3)), expected)

    def test_zero_time_preserves_witness(self):
        result = solve(5, time_limit=0)
        self.assertEqual(result["status"], "TIME_LIMIT")
        self.assertIsNone(result["k"])
        self.assertEqual(result["restricted_status"], "NOT_RUN")
        self.assertEqual(validate_partition(5, [Rect(**r) for r in result["rectangles"]]),
                         result["lower_bound"])

    @unittest.skipUnless(HAS_ORTOOLS, "optional OR-Tools dependency not installed")
    def test_independent_small_strip_enumeration(self):
        for n in range(1, 7):
            result = solve(n, max_parts=n, time_limit=10)
            self.assertEqual(result["lower_bound"], strip_oracle(n))
            self.assertEqual(validate_partition(n, [Rect(**r) for r in result["rectangles"]]),
                             result["lower_bound"])

    @unittest.skipUnless(HAS_ORTOOLS, "optional OR-Tools dependency not installed")
    def test_restricted_optimum_is_not_global(self):
        result = solve(5, max_parts=1, time_limit=10)
        self.assertEqual(result["restricted_status"], "OPTIMAL")
        self.assertEqual(result["status"], "LOWER_BOUND")
        self.assertIsNone(result["k"])
        self.assertLess(result["lower_bound"], result["upper_bound"])
        self.assertEqual(result["lower_bound"], result["initial_lower_bound"])

    @unittest.skipUnless(HAS_ORTOOLS, "optional OR-Tools dependency not installed")
    def test_better_witness_certifies_exactness(self):
        result = solve(5, time_limit=10)
        self.assertEqual(result["k"], 6)
        self.assertGreater(result["lower_bound"], result["initial_lower_bound"])

    def test_invalid_options(self):
        for n in [0, -1, 2.5, True]:
            with self.assertRaises(ValueError):
                solve(n)
        for kwargs in [{"max_parts": 0}, {"max_height": -1}, {"workers": 0},
                       {"seed": -1}, {"seed": 2**31}, {"time_limit": float("nan")},
                       {"time_limit": -1}]:
            with self.assertRaises(ValueError):
                solve(5, **kwargs)


if __name__ == "__main__":
    unittest.main()
