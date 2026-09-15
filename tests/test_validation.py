"""Reject malformed witness partitions."""

import unittest
from shikaku import Rect, validate_partition


class ValidationTests(unittest.TestCase):
    def test_validator_rejects_invalid_witnesses(self):
        for rects in [[Rect(0, 0, 1, 1)], [Rect(0, 0, 2, 2), Rect(0, 0, 1, 1)],
                      [Rect(0, 0, 3, 2)], [Rect(0, 0, 0, 2)]]:
            with self.assertRaises(ValueError):
                validate_partition(2, rects)

