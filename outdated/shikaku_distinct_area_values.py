#!/usr/bin/env python3
"""For a w x h grid, tiled completely (no gaps, no overlaps) but with
repeated areas now allowed, find the maximum number of DISTINCT area
values that can appear among the pieces -- and show one such tiling.

Equivalence this relies on: any leftover space in a tiling can always
be closed off with plain 1x1 filler squares (area 1 always fits a
single empty cell, and repeats are fine here now). So whatever set of
distinct-area rectangles can be packed into the grid without
overlapping each other -- even if they leave gaps -- can always be
finished into a full tiling without losing any of the distinct values
already placed. Maximizing "distinct area values in a full tiling with
repeats allowed" is therefore equivalent to maximizing "how many
pairwise non-overlapping, distinct-area rectangles fit in the grid,
coverage not required" -- a rectangle-PACKING problem, not an
exact-cover/tiling one like shikaku_distinct_areas.py solved.

That reframing changes both stages of the approach used there:

  1. Necessary-condition bound: since pieces no longer need to sum to
     exactly w*h (only at most), the cheapest way to reach a count k is
     always the k *smallest* representable areas -- a sorted prefix
     sum, no subset-sum DP needed.

  2. Constructive confirmation: packing (rather than covering) gets no
     help from the "always fill the topmost-leftmost empty cell"
     canonical order used before, since cells are now allowed to stay
     empty forever. This is closer to a rectangle/set-packing problem
     (NP-hard in general). Solved here with branch-and-bound: process
     candidate areas largest-first (most constraining), at each one
     either place it (try every valid non-overlapping position) or
     skip it, and prune whenever even taking every remaining candidate
     area couldn't beat the best packing found so far.
"""

import argparse
import sys
from typing import Dict, List, Tuple

from shikaku_common import Clue, Puzzle, Rect
from shikaku_display import render
from shikaku_distinct_areas import representable_areas


def max_k_bound(w: int, h: int) -> int:
    """Necessary-condition upper bound: the cheapest way to reach a
    count k is the k smallest representable areas, so find the largest
    k whose sum is still <= w*h."""
    areas = sorted(representable_areas(w, h))
    total = w * h
    running = 0
    k = 0
    for a in areas:
        if running + a > total:
            break
        running += a
        k += 1
    return k


def _placements_for_area(w: int, h: int, area: int) -> List[Tuple[Rect, int]]:
    """Every (Rect, bitmask) placement of a rectangle with this area,
    anywhere in the w x h grid (both orientations)."""
    placements = []
    dims = set()
    p = 1
    while p * p <= area:
        if area % p == 0:
            q = area // p
            dims.add((p, q))
            dims.add((q, p))
        p += 1

    for pw, ph in dims:
        if pw > w or ph > h:
            continue
        row_mask = (1 << pw) - 1
        for x in range(0, w - pw + 1):
            for y in range(0, h - ph + 1):
                mask = 0
                for r in range(y, y + ph):
                    mask |= row_mask << (r * w + x)
                placements.append((Rect(x, y, pw, ph), mask))
    return placements


def find_max_packing(w: int, h: int):
    """Returns (k_max, rects): the largest set of pairwise
    non-overlapping, distinct-area rectangles that fit in the grid."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), w * h + 1000))

    areas_desc = sorted(representable_areas(w, h), reverse=True)
    n = len(areas_desc)
    placements_by_area: Dict[int, List[Tuple[Rect, int]]] = {
        a: _placements_for_area(w, h, a) for a in areas_desc
    }
    total_cells = w * h

    # tail_sum[m] = sum of the m globally-smallest representable areas.
    # Since areas_desc is sorted descending, those are always its last m
    # entries -- and any suffix areas_desc[idx:] is itself a tail of a
    # descending list, so its own m smallest entries are exactly the
    # same last m elements (idx-independent). That makes this a much
    # tighter bound than just counting remaining areas: it also accounts
    # for whether they'd actually fit in the free space left.
    tail_sum = [0] * (n + 1)
    for i in range(1, n + 1):
        tail_sum[i] = tail_sum[i - 1] + areas_desc[n - i]

    best_count = 0
    best_rects: List[Rect] = []
    chosen: List[Rect] = []

    def search(idx: int, covered: int) -> None:
        nonlocal best_count, best_rects
        if len(chosen) > best_count:
            best_count = len(chosen)
            best_rects = list(chosen)
        if idx == n:
            return

        remaining_areas = n - idx
        free_cells = total_cells - bin(covered).count("1")
        needed = best_count - len(chosen) + 1
        if needed > remaining_areas or tail_sum[needed] > free_cells:
            return  # even the cheapest `needed` remaining areas can't fit

        area = areas_desc[idx]
        for rect, mask in placements_by_area[area]:
            if mask & covered == 0:
                chosen.append(rect)
                search(idx + 1, covered | mask)
                chosen.pop()
        search(idx + 1, covered)  # skip this area entirely

    search(0, 0)
    return best_count, best_rects


def _fill_with_unit_squares(w: int, h: int, rects: List[Rect]) -> List[Rect]:
    """Complete a packing into a full tiling by filling every remaining
    cell with a 1x1 filler (repeats of area 1 are fine -- only the
    distinct values already in the packing are what we're counting)."""
    covered = [[False] * w for _ in range(h)]
    for r in rects:
        for row in range(r.y, r.y + r.h):
            for col in range(r.x, r.x + r.w):
                covered[row][col] = True

    filled = list(rects)
    for row in range(h):
        for col in range(w):
            if not covered[row][col]:
                filled.append(Rect(col, row, 1, 1))
    return filled


def _as_puzzle(w: int, h: int, rects: List[Rect]) -> Puzzle:
    clues = [Clue(row=r.y, col=r.x, value=r.area) for r in rects]
    return Puzzle(width=w, height=h, clues=clues, solution=rects)


def main():
    parser = argparse.ArgumentParser(
        description="Max number of DISTINCT area values across a full tiling of a w x h grid (repeats allowed)."
    )
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("--unicode", action="store_true", help="use Unicode box-drawing characters")
    parser.add_argument("--output", type=str, default=None, help="also write the puzzle to this file")
    args = parser.parse_args()

    if args.width < 1 or args.height < 1:
        parser.error("width and height must be >= 1")

    if args.unicode:
        sys.stdout.reconfigure(encoding="utf-8")

    k, rects = find_max_packing(args.width, args.height)
    areas = sorted(r.area for r in rects)
    print(f"{args.width}x{args.height} grid: max {k} distinct area values {areas}")
    print()

    tiling = _fill_with_unit_squares(args.width, args.height, rects)
    puzzle = _as_puzzle(args.width, args.height, tiling)
    print(render(puzzle, show_solution=True, unicode=args.unicode))

    if args.output:
        with open(args.output, "w") as f:
            f.write(puzzle.to_text())


if __name__ == "__main__":
    main()
