"""Cross-check skyline search against independent full enumeration."""

import unittest
from shikaku import Rect, solve, validate_partition
from shikaku.constructions import initial_partition
from tests.oracle import cell_oracle


class BaselineTests(unittest.TestCase):
    def test_cross_check_all_partitions(self):
        for n in range(1, 5):
            with self.subTest(n=n):
                expected, leaves = cell_oracle(n)
                for prune in (False, True):
                    result = solve(n, prune=prune)
                    self.assertEqual(result["status"], "OPTIMAL")
                    self.assertEqual(result["k"], expected)
                    self.assertEqual(validate_partition(n, [Rect(**r) for r in
                                                           result["rectangles"]]), expected)
                    if not prune:
                        self.assertEqual(result["complete_partitions"], leaves)

    def test_note_exact_values(self):
        for n, expected in [(7, 9), (8, 10), (13, 17)]:
            result = solve(n)
            self.assertEqual(result["k"], expected)

    def test_construction(self):
        for n in range(1, 41):
            score = validate_partition(n, initial_partition(n))
            self.assertGreaterEqual(score, n + 2 * (((n + 1) // 2 - 1) // 3))

    def test_timeout_is_not_infeasibility(self):
        result = solve(5, time_limit=0)
        self.assertEqual(result["status"], "TIME_LIMIT")
        self.assertIsNone(result["k"])
        self.assertLess(result["lower_bound"], result["upper_bound"])
        validate_partition(5, [Rect(**r) for r in result["rectangles"]])

    def test_invalid_input(self):
        for n in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                solve(n)
        for limit in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                solve(2, time_limit=limit)


if __name__ == "__main__":
    unittest.main()
