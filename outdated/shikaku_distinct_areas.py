#!/usr/bin/env python3
"""For a w x h grid, find the maximum number of rectangles k such that
some dissection into k rectangles has pairwise-distinct areas, and show
one such dissection.

Two-stage approach (see module docstring sections below for why):

  1. candidate_ks() -- a fast NECESSARY condition. An area can only ever
     appear as some rectangle in the grid if it has a factor pair
     (p, q) with p <= w, q <= h (in either orientation); call this set
     of areas "representable". Since the pieces must tile the grid
     exactly, their areas must be k distinct representable areas
     summing to exactly w*h -- a bounded subset-sum problem, solved by
     DP. This upper-bounds which k are even worth trying.

  2. find_max_dissection() -- confirms candidates constructively, from
     the largest k down: always place a rectangle at the current
     topmost-leftmost empty cell (canonical order, so no dissection is
     explored twice), trying only not-yet-used representable areas,
     pruned by re-applying the same subset-sum bound to whatever's left
     at each step. The first k with a successful construction is the
     true maximum (empirically, on every grid checked against brute
     force up to 10x10, this candidate bound was already exact and the
     achievable k's formed a gap-free range 1..k_max -- but this isn't
     assumed here; each k is still verified by an actual construction).
"""

import argparse
import sys
from typing import List, Optional, Set

from shikaku_common import Clue, Puzzle, Rect
from shikaku_display import render


def _divisors(a: int) -> List[int]:
    ds = []
    p = 1
    while p * p <= a:
        if a % p == 0:
            ds.append(p)
            if p != a // p:
                ds.append(a // p)
        p += 1
    return ds


def representable_areas(w: int, h: int) -> Set[int]:
    """Areas that fit as *some* rectangle in a w x h grid, ignoring position."""
    total = w * h
    areas = set()
    for a in range(1, total + 1):
        for p in _divisors(a):
            q = a // p
            if (p <= w and q <= h) or (p <= h and q <= w):
                areas.add(a)
                break
    return areas


def candidate_ks(w: int, h: int) -> Set[int]:
    """k's for which some k-subset of representable areas sums to w*h."""
    total = w * h
    areas = sorted(representable_areas(w, h))

    k_max = 1
    while k_max * (k_max + 1) // 2 <= total:
        k_max += 1
    k_max -= 1

    dp: List[Set[int]] = [set() for _ in range(k_max + 1)]
    dp[0].add(0)
    for a in areas:
        for k in range(min(k_max, len(dp) - 1) - 1, -1, -1):
            for s in list(dp[k]):
                if s + a <= total:
                    dp[k + 1].add(s + a)

    return {k for k in range(1, k_max + 1) if total in dp[k]}


def _construct(w: int, h: int, target_k: int, areas: Set[int]) -> Optional[List[Rect]]:
    """Try to build a dissection into exactly target_k rectangles with
    distinct, representable areas. Returns the rectangles, or None."""
    total = w * h
    used: Set[int] = set()
    placed: List[Rect] = []

    def solve(skyline) -> bool:
        r = min(skyline)
        if r == h:
            return len(used) == target_k
        if len(used) >= target_k:
            return False

        c = skyline.index(r)
        max_w = 0
        while c + max_w < w and skyline[c + max_w] == r:
            max_w += 1

        k_left = target_k - len(used)
        remaining_area = total - sum(used)
        avail = sorted(a for a in areas if a not in used)
        if len(avail) < k_left or sum(avail[:k_left]) > remaining_area:
            return False  # even the cheapest remaining areas don't fit

        for wid in range(1, max_w + 1):
            for hei in range(1, h - r + 1):
                area = wid * hei
                if area in used or area not in areas or area > remaining_area:
                    continue
                used.add(area)
                placed.append(Rect(c, r, wid, hei))
                new_sky = list(skyline)
                for cc in range(c, c + wid):
                    new_sky[cc] = r + hei
                if solve(tuple(new_sky)):
                    return True
                used.discard(area)
                placed.pop()
        return False

    sys.setrecursionlimit(max(sys.getrecursionlimit(), w * h + 100))
    return list(placed) if solve((0,) * w) else None


def find_max_dissection(w: int, h: int):
    """Returns (k_max, rects) for the largest k with a valid distinct-area
    dissection of the w x h grid."""
    areas = representable_areas(w, h)
    for k in sorted(candidate_ks(w, h), reverse=True):
        rects = _construct(w, h, k, areas)
        if rects is not None:
            return k, rects
    return 0, []  # unreachable for w,h >= 1 (k=1, the whole grid, always works)


def _as_puzzle(w: int, h: int, rects: List[Rect]) -> Puzzle:
    clues = [Clue(row=r.y, col=r.x, value=r.area) for r in rects]
    return Puzzle(width=w, height=h, clues=clues, solution=rects)


def main():
    parser = argparse.ArgumentParser(
        description="Find the max number of rectangles in a distinct-area dissection of a w x h grid."
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

    k_max, rects = find_max_dissection(args.width, args.height)
    areas = sorted(r.area for r in rects)
    print(f"{args.width}x{args.height} grid: max {k_max} rectangles with distinct areas {areas}")
    print()
    puzzle = _as_puzzle(args.width, args.height, rects)
    print(render(puzzle, show_solution=True, unicode=args.unicode))

    if args.output:
        with open(args.output, "w") as f:
            f.write(puzzle.to_text())


if __name__ == "__main__":
    main()
