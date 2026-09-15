"""Constructive initial lower bounds."""

from .model import Rect


def initial_partition(n: int) -> list[Rect]:
    """The research note's height-1 / height-3 construction, plus unit fillers."""
    rects = []
    row = 0
    for width in range(1, n // 2 + 1):
        rects.extend([Rect(row, 0, 1, width), Rect(row, width, 1, n - width)])
        row += 1
    rects.append(Rect(row, 0, 1, n))
    row += 1
    strips = (n - row) // 3
    widths = range(n // 3 + 1, (n - 1) // 2 + 1)
    assert len(widths) >= strips
    for width in list(widths)[:strips]:
        rects.extend([Rect(row, 0, 3, width), Rect(row, width, 3, n - width)])
        row += 3
    rects.extend(Rect(y, x, 1, 1) for y in range(row, n) for x in range(n))
    return rects
