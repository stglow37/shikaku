"""Compare the sieve bound with direct enumeration of all rectangle areas."""

import unittest

from shikaku.bounds import area_upper_bound


class AreaUpperTests(unittest.TestCase):
    def test_sieve_matches_all_products_through_200(self):
        for n in range(1, 201):
            with self.subTest(n=n):
                areas = sorted({height * width for height in range(1, n + 1)
                                for width in range(1, n + 1)})
                total = 0
                expected = 0
                for area in areas:
                    if total + area > n * n:
                        break
                    total += area
                    expected += 1
                self.assertEqual(area_upper_bound(n), expected)

    def test_representability_improves_triangle_bound(self):
        # 22 distinct positive integers can fit area 256, but the cheapest
        # 22 areas representable in a 16 by 16 square sum to 266.
        self.assertEqual(area_upper_bound(16), 21)
        self.assertEqual(area_upper_bound(17), 23)
        self.assertEqual(area_upper_bound(20), 27)
        self.assertEqual(area_upper_bound(1), 1)

    def test_invalid_input(self):
        for n in (0, -1, 1.5, True, "2", None):
            with self.subTest(n=n), self.assertRaises(ValueError):
                area_upper_bound(n)


if __name__ == "__main__":
    unittest.main()
