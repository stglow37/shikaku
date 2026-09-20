"""Published constructions, translated into independently checkable coordinates."""

from .model import Rect
from .validation import validate_partition


def carnahan_20() -> list[Rect]:
    """S. Carnahan's 2010 MathOverflow answer, 27 distinct areas in 20x20.

    Source: https://mathoverflow.net/questions/38151/
    The source describes the cuts; these coordinates reconstruct those cuts.
    """
    rects = []
    for width in range(1, 10):
        rects.extend([Rect(width - 1, 0, 1, width),
                      Rect(width - 1, width, 1, 19 - width)])
    rects.extend([
        Rect(9, 0, 1, 19), Rect(0, 19, 20, 1),
        Rect(10, 0, 3, 9), Rect(10, 9, 3, 10),
        Rect(13, 0, 7, 3), Rect(13, 3, 7, 4),
        Rect(13, 7, 2, 12), Rect(15, 7, 5, 5), Rect(15, 12, 5, 7),
    ])
    if validate_partition(20, rects) != 27:
        raise RuntimeError("published construction reconstruction failed")
    return rects
