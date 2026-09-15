"""Independent witness validation."""

from .model import Rect


def validate_partition(n: int, rects: list[Rect]) -> int:
    """Independent cell-based witness check; returns the distinct-area count."""
    if n < 1:
        raise ValueError("n must be positive")
    occupied: set[tuple[int, int]] = set()
    for r in rects:
        if (r.row < 0 or r.col < 0 or r.height < 1 or r.width < 1
                or r.row + r.height > n or r.col + r.width > n):
            raise ValueError("rectangle outside grid or non-positive dimensions")
        for row in range(r.row, r.row + r.height):
            for col in range(r.col, r.col + r.width):
                cell = row, col
                if cell in occupied:
                    raise ValueError("overlapping rectangles")
                occupied.add(cell)
    if len(occupied) != n * n:
        raise ValueError("partition has uncovered cells")
    return len({r.area for r in rects})
