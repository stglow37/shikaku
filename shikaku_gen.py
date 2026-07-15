#!/usr/bin/env python3
"""Shikaku puzzle generator via construction-by-tiling.

Recursively splits the W x H grid into rectangles (guillotine cuts),
places one clue per rectangle equal to its area, and emits the puzzle
plus (optionally) the witness tiling that proves it is solvable.
"""

import argparse
import random
import sys

from shikaku_common import Clue, Puzzle, Rect


def try_split(rect, min_area, rng):
    """Attempt one guillotine cut of rect into two sub-rectangles, each
    with area >= min_area. Returns a list of two Rects, or None if no
    valid cut exists."""
    axes = []
    if rect.w >= 2:
        axes.append("v")
    if rect.h >= 2:
        axes.append("h")
    rng.shuffle(axes)

    for axis in axes:
        if axis == "v":
            cuts = [c for c in range(1, rect.w) if c * rect.h >= min_area and (rect.w - c) * rect.h >= min_area]
            if cuts:
                c = rng.choice(cuts)
                return [Rect(rect.x, rect.y, c, rect.h), Rect(rect.x + c, rect.y, rect.w - c, rect.h)]
        else:
            cuts = [c for c in range(1, rect.h) if rect.w * c >= min_area and rect.w * (rect.h - c) >= min_area]
            if cuts:
                c = rng.choice(cuts)
                return [Rect(rect.x, rect.y, rect.w, c), Rect(rect.x, rect.y + c, rect.w, rect.h - c)]

    return None


def generate_tiling(width, height, min_area, max_area, split_prob, rng):
    """Returns a list of Rects that exactly partition the width x height grid."""
    pending = [Rect(0, 0, width, height)]
    result = []

    while pending:
        rect = pending.pop()
        area = rect.area

        must_split = area > max_area
        may_split = (not must_split) and area >= 2 * min_area and rng.random() < split_prob

        if must_split or may_split:
            parts = try_split(rect, min_area, rng)
            if parts is not None:
                pending.extend(parts)
                continue
            # Can't satisfy min_area with any cut; keep as a single
            # oversized rectangle rather than violate the constraint.

        result.append(rect)

    return result


def place_clues(rects, rng):
    """Returns a list of Clues, one per rectangle."""
    clues = []
    for rect in rects:
        r = rect.y + rng.randrange(rect.h)
        c = rect.x + rng.randrange(rect.w)
        clues.append(Clue(r, c, rect.area))
    return clues


def generate_puzzle(width, height, min_area, max_area, split_prob, rng):
    rects = generate_tiling(width, height, min_area, max_area, split_prob, rng)
    clues = place_clues(rects, rng)
    return Puzzle(width, height, clues, solution=rects)


def main():
    parser = argparse.ArgumentParser(description="Generate a Shikaku puzzle by tiling.")
    parser.add_argument("--width", type=int, default=10, help="grid width (columns)")
    parser.add_argument("--height", type=int, default=10, help="grid height (rows)")
    parser.add_argument("--min-area", type=int, default=2, help="minimum rectangle area")
    parser.add_argument("--max-area", type=int, default=10, help="maximum rectangle area")
    parser.add_argument(
        "--split-prob",
        type=float,
        default=0.3,
        help="probability of splitting a rectangle further even when under max-area",
    )
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    parser.add_argument(
        "--solution",
        action="store_true",
        help="also include the witness tiling in the output",
    )
    parser.add_argument("--output", type=str, default=None, help="output file (default: stdout)")
    args = parser.parse_args()

    if args.width < 1 or args.height < 1:
        parser.error("width and height must be >= 1")
    if args.min_area < 1:
        parser.error("min-area must be >= 1")
    if args.max_area < args.min_area:
        parser.error("max-area must be >= min-area")

    rng = random.Random(args.seed)

    puzzle = generate_puzzle(args.width, args.height, args.min_area, args.max_area, args.split_prob, rng)
    if not args.solution:
        puzzle.solution = None

    output = puzzle.to_text()

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
