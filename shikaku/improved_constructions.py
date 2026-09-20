"""Proved strip improvements and published witnesses; no search is required.

See docs/theory_progress.md for the proof of k(16t) >= 22t-1.
The historical baseline construction remains in constructions.py.
"""

from .constructions import initial_partition
from .known import carnahan_20
from .model import Rect


def _check_n(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")


def _pad(n: int, m: int, rectangles: list[Rect]) -> list[Rect]:
    """Embed an m-square witness and cover its right and bottom borders."""
    if n == m:
        return rectangles
    return rectangles + [Rect(0, m, m, n-m), Rect(m, 0, n-m, n)]


def residual_partition(n: int) -> list[Rect]:
    """Improve the old construction by filling its last two rows together."""
    _check_n(n)
    rectangles = initial_partition(n)
    first_rows = n//2 + 1
    remaining = n - first_rows
    used_rows = first_rows + 3*(remaining//3)
    if n - used_rows == 2:
        rectangles = [rect for rect in rectangles if rect.row < used_rows]
        rectangles.append(Rect(used_rows, 0, 2, n))
    return rectangles


def partition_11_over_8(n: int) -> list[Rect]:
    """Return the 22t-1 witness for t=floor(n/16), padded to n-square.

    Requires n >= 16. For n=16t the score is exactly 22t-1.
    """
    _check_n(n)
    if n < 16:
        raise ValueError("the 11/8 construction requires n >= 16")
    t = n//16
    m = 16*t
    rectangles: list[Rect] = []
    row = 0
    for width in range(1, m//2, 2):
        rectangles += [Rect(row, 0, 1, width), Rect(row, width, 1, m-width)]
        row += 1
    pairs = [(width, m//2-width) for width in range(2, m//4+1, 2)]
    for p in range(0, len(pairs), 2):
        col = 0
        for width in pairs[p] + pairs[p+1]:
            rectangles.append(Rect(row, col, 1, width))
            col += width
        row += 1
    for width in range(m//4, m//2):
        rectangles += [Rect(row, 0, 2, width), Rect(row, width, 2, m-width)]
        row += 2
    for width in range(6*t+1, 8*t, 2):
        rectangles += [Rect(row, 0, 3, width), Rect(row, width, 3, m-width)]
        row += 3
    assert row == m
    return _pad(n, m, rectangles)


def best_partition(n: int) -> list[Rect]:
    """Choose the strongest available explicit witness, with no optimization."""
    _check_n(n)
    candidates = [residual_partition(n)]
    if n >= 16:
        candidates.append(partition_11_over_8(n))
    if n >= 20:
        candidates.append(_pad(n, 20, carnahan_20()))
    return max(candidates, key=lambda rects: len({rect.area for rect in rects}))
