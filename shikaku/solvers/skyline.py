"""Skyline DFS baseline; no additional search optimizations."""

from dataclasses import asdict
from math import isfinite
from time import perf_counter
from typing import Iterator

from ..bounds import additional_bound
from ..constructions import initial_partition
from ..model import Rect
from ..validation import validate_partition


# A state contains skyline, used areas, witness prefix, and remaining cell count.
State = tuple[tuple[int, ...], frozenset[int], tuple[Rect, ...], int]


def children(n: int, state: State) -> Iterator[State]:
    heights, used, rects, remaining = state
    row = min(heights)
    col = heights.index(row)
    max_width = 0
    while col + max_width < n and heights[col + max_width] == row:
        max_width += 1
    # Fixed order, no new-area preference, symmetry, memoization or duplicate removal.
    for width in range(1, max_width + 1):
        for height in range(1, n - row + 1):
            rect = Rect(row, col, height, width)
            updated = list(heights)
            updated[col:col + width] = [row + height] * width
            yield (tuple(updated), used | {rect.area}, rects + (rect,),
                   remaining - rect.area)


def solve(n: int, *, prune: bool = True, time_limit: float | None = None) -> dict:
    """Return a verified witness and certified bounds; timeout never claims exactness.

    time_limit is checked during DFS (preprocessing/validation are not interrupted).
    prune=False also disables global-bound early exit, for full enumeration checks.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    if time_limit is not None and (not isfinite(time_limit) or time_limit < 0):
        raise ValueError("time_limit must be finite and non-negative")
    started = perf_counter()
    areas = sorted({a * b for a in range(1, n + 1) for b in range(1, n + 1)})
    global_upper = additional_bound(areas, frozenset(), n * n)
    best_rects = initial_partition(n)
    best = validate_partition(n, best_rects)
    initial_lower = best
    visited = pruned = leaves = 0
    reason = "search_exhausted"
    stack = [iter([((0,) * n, frozenset(), (), n * n)])]
    # Iterator frames avoid Python recursion limits without eagerly storing siblings.
    while stack:
        if prune and best == global_upper:
            reason = "upper_bound_reached"
            break
        if time_limit is not None and perf_counter() - started >= time_limit:
            reason = "time_limit"
            break
        try:
            state = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        visited += 1
        heights, used, rects, remaining = state
        if remaining == 0:
            leaves += 1
            if len(used) > best:
                best, best_rects = len(used), list(rects)
            continue
        if prune and len(used) + additional_bound(areas, used, remaining) <= best:
            pruned += 1
            continue
        stack.append(children(n, state))
    exact = reason != "time_limit" or best == global_upper
    assert validate_partition(n, best_rects) == best
    return {
        "n": n, "status": "OPTIMAL" if exact else "TIME_LIMIT",
        "k": best if exact else None, "lower_bound": best,
        "upper_bound": best if exact else global_upper,
        "initial_lower_bound": initial_lower, "area_upper_bound": global_upper,
        "termination": reason, "pruning": prune,
        "nodes": visited, "pruned_nodes": pruned, "complete_partitions": leaves,
        "elapsed_seconds": perf_counter() - started,
        "distinct_areas": sorted({r.area for r in best_rects}),
        "rectangles": [asdict(r) for r in best_rects],
    }
