"""Independently check coverage and the proved counts of new witnesses."""

import unittest

from shikaku.constructions import initial_partition
from shikaku.improved_constructions import (
    best_partition, partition_11_over_8, residual_partition,
)
from shikaku.validation import validate_partition


class ImprovedConstructionTests(unittest.TestCase):
    def test_all_cells_and_theorem_count(self):
        for t in range(1, 17):
            n = 16*t
            self.assertEqual(validate_partition(n, partition_11_over_8(n)), 22*t-1)

    def test_every_padding_remainder(self):
        for n in range(16, 64):
            self.assertGreaterEqual(validate_partition(n, partition_11_over_8(n)),
                                    22*(n//16)-1)

    def test_residual_two_rows(self):
        for n in range(1, 65):
            old = validate_partition(n, initial_partition(n))
            new = validate_partition(n, residual_partition(n))
            self.assertEqual(new, old + (n % 6 in (0, 5)))

    def test_best_and_known_exact_cases(self):
        for n in range(1, 81):
            score = validate_partition(n, best_partition(n))
            self.assertGreaterEqual(score, validate_partition(n, initial_partition(n)))
        for n, expected in [(5, 6), (6, 7), (16, 21), (17, 23), (20, 27), (33, 45)]:
            self.assertEqual(validate_partition(n, best_partition(n)), expected)

    def test_invalid_dimensions(self):
        for function in (best_partition, residual_partition, partition_11_over_8):
            for n in (0, -1, 1.5, True):
                with self.assertRaises(ValueError):
                    function(n)
        with self.assertRaises(ValueError):
            partition_11_over_8(15)


if __name__ == '__main__':
    unittest.main()
