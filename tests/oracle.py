"""Independent cell-mask exhaustive oracle for small grids."""

def cell_oracle(n: int) -> tuple[int, int]:
    """Enumerate all partitions: no skyline, area bound, seed, or memoization.

    Branch on the LAST free cell, and try all rectangles containing that cell.
    """
    candidates = [[] for _ in range(n * n)]
    for top in range(n):
        for bottom in range(top + 1, n + 1):
            for left in range(n):
                for right in range(left + 1, n + 1):
                    cells = [r * n + c for r in range(top, bottom)
                             for c in range(left, right)]
                    mask = sum(1 << c for c in cells)
                    for c in cells:
                        candidates[c].append((mask, len(cells)))
    full = (1 << (n * n)) - 1
    best = leaves = 0

    def visit(occupied: int, used: frozenset[int]) -> None:
        nonlocal best, leaves
        if occupied == full:
            best = max(best, len(used))
            leaves += 1
            return
        cell = (full ^ occupied).bit_length() - 1
        for mask, area in candidates[cell]:
            if not mask & occupied:
                visit(occupied | mask, used | {area})

    visit(0, frozenset())
    return best, leaves


