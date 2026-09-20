"""Check border extensions as geometric witnesses and useful certificates."""

import unittest
from shikaku.extensions import extend_partition
from shikaku.improved_constructions import best_partition
from shikaku.model import Rect
from shikaku.validation import validate_partition


class ExtensionTests(unittest.TestCase):
    def test_coverage_preservation_and_determinism(self):
        for m in range(1, 13):
            original = best_partition(m)
            old = validate_partition(m, original)
            for n in range(m+1, m+5):
                result = extend_partition(m, n, original)
                self.assertEqual(result[:len(original)], original)
                self.assertGreaterEqual(validate_partition(n, result), old)
                self.assertEqual(result, extend_partition(m, n, original))

    def test_extension_of_computed_24_witness(self):
        # Independently recorded strip witness from the saved n=24 experiment.
        bands = [(1, [1, 23]), (1, [4, 6, 14]), (1, [5, 19]),
                 (1, [7, 17]), (1, [11, 13]), (2, [1, 4, 5, 14]),
                 (2, [8, 16]), (2, [9, 15]), (2, [11, 13]),
                 (3, [1, 3, 9, 11]), (3, [4, 5, 7, 8]), (5, [4, 5, 7, 8])]
        original = []
        row = 0
        for height, widths in bands:
            col = 0
            for width in widths:
                original.append(Rect(row, col, height, width))
                col += width
            row += height
        self.assertEqual(validate_partition(24, original), 33)
        self.assertEqual(validate_partition(26, extend_partition(24, 26, original)), 35)
        self.assertEqual(validate_partition(27, extend_partition(24, 27, original)), 36)

    def test_invalid_dimensions_and_witnesses(self):
        for m, n in [(0, 2), (2, 2), (3, 2), (True, 2), (1, 2.5)]:
            with self.assertRaises(ValueError):
                extend_partition(m, n, [Rect(0, 0, 1, 1)])
        for original in [[], [Rect(0, 0, 2, 2)], [Rect(0, 0, 1.0, 1)],
                         [Rect(0, 0, 1, 1), Rect(0, 0, 1, 1)]]:
            with self.assertRaises(ValueError):
                extend_partition(1, 2, original)


if __name__ == '__main__':
    unittest.main()
