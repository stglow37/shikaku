#!/usr/bin/env python3
"""Shikaku puzzle solver via exact-cover search (bitmask Algorithm X).

Each clue's candidate rectangles (every area-factor pair x every position
that contains the clue's own cell and no other clue's cell) are
precomputed as bitmasks over grid cells. Because a candidate is thrown
out the moment it would swallow a different clue's cell, "each clue
picks exactly one rectangle" comes for free once we require "each cell
is covered exactly once" -- the whole puzzle reduces to a pure
exact-cover problem over cells, in the same family as Sudoku or
pentomino tiling.

Solved by backtracking with a minimum-remaining-candidates (MRV)
heuristic: at each step, branch on whichever unplaced clue currently has
the fewest valid candidates. This is the core of Knuth's Algorithm X --
it forces "naked singles" (a clue down to one option gets placed with no
real branching) and detects dead ends the instant some clue hits zero
options, without needing separate propagation code. Candidate/cell
overlap tests are single Python-int bitwise ops (`&`), which is what
keeps this fast without a dependency on a full Dancing Links structure.
"""

import argparse
import sys
from typing import Dict, FrozenSet, List, Optional, Tuple

from shikaku_common import Clue, Puzzle, Rect

Candidate = Tuple[int, Rect]  # (bitmask of covered cells, the rectangle)


def candidate_rectangles(puzzle: Puzzle) -> List[List[Candidate]]:
    """For each clue (by index, matching puzzle.clues order): every
    (bitmask, Rect) with area == clue.value, in bounds, containing the
    clue's own cell, and containing no other clue's cell."""
    width, height = puzzle.width, puzzle.height
    clue_at: Dict[Tuple[int, int], int] = {(c.row, c.col): i for i, c in enumerate(puzzle.clues)}

    all_candidates: List[List[Candidate]] = []
    for idx, clue in enumerate(puzzle.clues):
        value = clue.value
        options: List[Candidate] = []
        for w in range(1, min(value, width) + 1):
            if value % w:
                continue
            h = value // w
            if h > height:
                continue
            x_min, x_max = max(0, clue.col - w + 1), min(clue.col, width - w)
            y_min, y_max = max(0, clue.row - h + 1), min(clue.row, height - h)
            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    mask = 0
                    valid = True
                    for r in range(y, y + h):
                        base = r * width
                        for c in range(x, x + w):
                            other = clue_at.get((r, c))
                            if other is not None and other != idx:
                                valid = False
                                break
                            mask |= 1 << (base + c)
                        if not valid:
                            break
                    if valid:
                        options.append((mask, Rect(x, y, w, h)))
        all_candidates.append(options)
    return all_candidates


def solve(puzzle: Puzzle, limit: int = 1) -> List[List[Rect]]:
    """Return up to `limit` solutions, each a list of Rects in the same
    order as puzzle.clues. Pass limit=2 to test uniqueness cheaply
    (stops as soon as a second solution is found)."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(puzzle.clues) + 100))

    width, height = puzzle.width, puzzle.height
    full_mask = (1 << (width * height)) - 1
    candidates = candidate_rectangles(puzzle)
    n = len(candidates)

    solutions: List[List[Rect]] = []
    placement: List[Optional[Rect]] = [None] * n

    def backtrack(remaining: FrozenSet[int], covered: int) -> bool:
        if not remaining:
            if covered == full_mask:
                solutions.append(list(placement))
            return len(solutions) >= limit

        # For every still-uncovered cell, collect which (clue, candidate)
        # pairs could still cover it. This is Algorithm X's real
        # heuristic: branch on the most-constrained *cell*, not the
        # most-constrained clue -- a cell can become a bottleneck because
        # neighboring clues' candidates shrank, even if no single clue
        # looks constrained on its own.
        cell_candidates: Dict[int, List[Tuple[int, Candidate]]] = {}
        union_mask = 0
        for idx in remaining:
            valid = [(m, r) for (m, r) in candidates[idx] if m & covered == 0]
            if not valid:
                return False  # dead end: this clue has no room left
            for m, r in valid:
                union_mask |= m
                bits = m
                while bits:
                    low = bits & (-bits)
                    cell_candidates.setdefault(low, []).append((idx, (m, r)))
                    bits ^= low

        if union_mask != (full_mask & ~covered):
            return False  # dead end: some uncovered cell has no candidate left

        best_options = min(cell_candidates.values(), key=len)

        for idx, (mask, rect) in best_options:
            placement[idx] = rect
            if backtrack(remaining - {idx}, covered | mask):
                return True
            placement[idx] = None
        return False

    backtrack(frozenset(range(n)), 0)
    return solutions


def main():
    parser = argparse.ArgumentParser(description="Solve a Shikaku puzzle via exact-cover search.")
    parser.add_argument("puzzle", nargs="?", help="puzzle file (default: stdin)")
    parser.add_argument(
        "--check-unique",
        action="store_true",
        help="report whether the puzzle has exactly one solution, instead of printing it",
    )
    parser.add_argument("--output", type=str, default=None, help="output file (default: stdout)")
    args = parser.parse_args()

    text = open(args.puzzle, encoding="utf-8").read() if args.puzzle else sys.stdin.read()
    puzzle = Puzzle.from_text(text)

    if args.check_unique:
        solutions = solve(puzzle, limit=2)
        if not solutions:
            print("No solution.")
            sys.exit(1)
        print("Unique solution." if len(solutions) == 1 else "Multiple solutions (not unique).")
        return

    solutions = solve(puzzle, limit=1)
    if not solutions:
        print("No solution found.", file=sys.stderr)
        sys.exit(1)

    puzzle.solution = solutions[0]
    output = puzzle.to_text()
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
