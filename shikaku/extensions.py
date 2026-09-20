"""Extend a square witness by choosing cuts in its two new border strips."""

from .model import Rect
from .validation import validate_partition


def extend_partition(m: int, n: int, rects: list[Rect]) -> list[Rect]:
    """Preserve an m-square witness and maximize new areas in two borders.

    Requires 1 <= m < n. Each border is either whole or cut once along its
    long direction. All O(m*n) pairs are considered; ties keep the first
    option (whole borders first, then increasing cut positions).
    This optimizes only these border cuts, not every possible extension.
    """
    if type(m) is not int or type(n) is not int or not 1 <= m < n:
        raise ValueError("dimensions must be integers with 1 <= m < n")
    original = list(rects)
    for rect in original:
        if not isinstance(rect, Rect) or any(type(value) is not int for value in
                (rect.row, rect.col, rect.height, rect.width)):
            raise ValueError("witness must contain rectangles with integer coordinates")
    validate_partition(m, original)
    used = {rect.area for rect in original}
    d = n-m
    right = [[Rect(0, m, m, d)]] + [
        [Rect(0, m, cut, d), Rect(cut, m, m-cut, d)]
        for cut in range(1, m)]
    bottom = [[Rect(m, 0, d, n)]] + [
        [Rect(m, 0, d, cut), Rect(m, cut, d, n-cut)]
        for cut in range(1, n)]
    right_areas = [{rect.area for rect in option} - used for option in right]
    bottom_areas = [{rect.area for rect in option} - used for option in bottom]
    best_score = -1
    best_right = best_bottom = 0
    for i, added_right in enumerate(right_areas):
        for j, added_bottom in enumerate(bottom_areas):
            score = len(added_right | added_bottom)
            if score > best_score:
                best_score, best_right, best_bottom = score, i, j
    result = original + right[best_right] + bottom[best_bottom]
    score = validate_partition(n, result)
    if score != len(used) + best_score:
        raise RuntimeError("extended witness disagrees with its area count")
    return result
