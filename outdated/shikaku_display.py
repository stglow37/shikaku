#!/usr/bin/env python3
"""Render a Shikaku puzzle (produced by shikaku_gen.py) as text art.

Shows the clue grid (every cell boxed, numbers where clues sit) and,
if the file includes a witness tiling, the solved grid (only the
rectangle boundaries drawn).
"""

import argparse
import sys

from shikaku_common import Puzzle

# Box-drawing character for each combination of walls meeting at a
# grid corner, keyed by a (up, down, left, right) tuple of booleans.
# Unicode line-drawing glyphs mojibake on non-UTF-8 consoles (e.g. the
# default Windows cp949/cp1252 code pages), so ASCII is the default;
# --unicode opts into the prettier version.
_JUNCTION_ASCII = {
    (False, False, False, False): " ",
    (True, False, False, False): "|",
    (False, True, False, False): "|",
    (False, False, True, False): "-",
    (False, False, False, True): "-",
    (True, True, False, False): "|",
    (False, False, True, True): "-",
    (True, False, True, False): "+",
    (True, False, False, True): "+",
    (False, True, True, False): "+",
    (False, True, False, True): "+",
    (True, True, True, False): "+",
    (True, True, False, True): "+",
    (True, False, True, True): "+",
    (False, True, True, True): "+",
    (True, True, True, True): "+",
}

_JUNCTION_UNICODE = {
    (False, False, False, False): " ",
    (True, False, False, False): "╵",
    (False, True, False, False): "╷",
    (False, False, True, False): "╴",
    (False, False, False, True): "╶",
    (True, True, False, False): "│",
    (False, False, True, True): "─",
    (True, False, True, False): "┘",
    (True, False, False, True): "└",
    (False, True, True, False): "┐",
    (False, True, False, True): "┌",
    (True, True, True, False): "┤",
    (True, True, False, True): "├",
    (True, False, True, True): "┴",
    (False, True, True, True): "┬",
    (True, True, True, True): "┼",
}


def _build_walls(width, height, rects):
    """h_wall[r][c] = wall segment above cell (r, c), for r in 0..H, c in 0..W-1.
    v_wall[r][c] = wall segment left of cell (r, c), for r in 0..H-1, c in 0..W."""
    h_wall = [[False] * width for _ in range(height + 1)]
    v_wall = [[False] * (width + 1) for _ in range(height)]

    for c in range(width):
        h_wall[0][c] = True
        h_wall[height][c] = True
    for r in range(height):
        v_wall[r][0] = True
        v_wall[r][width] = True

    if rects is None:
        for r in range(height + 1):
            for c in range(width):
                h_wall[r][c] = True
        for r in range(height):
            for c in range(width + 1):
                v_wall[r][c] = True
    else:
        for rect in rects:
            for c in range(rect.x, rect.x + rect.w):
                h_wall[rect.y][c] = True
                h_wall[rect.y + rect.h][c] = True
            for r in range(rect.y, rect.y + rect.h):
                v_wall[r][rect.x] = True
                v_wall[r][rect.x + rect.w] = True

    return h_wall, v_wall


def render(puzzle: Puzzle, show_solution: bool, unicode: bool = False) -> str:
    width, height = puzzle.width, puzzle.height
    rects = puzzle.solution if show_solution else None
    h_wall, v_wall = _build_walls(width, height, rects)

    junctions = _JUNCTION_UNICODE if unicode else _JUNCTION_ASCII
    h_char = "─" if unicode else "-"
    v_char = "│" if unicode else "|"

    grid = [["" for _ in range(width)] for _ in range(height)]
    for clue in puzzle.clues:
        grid[clue.row][clue.col] = str(clue.value)

    cell_w = max((len(s) for row in grid for s in row), default=1)
    cell_w = max(cell_w, 2)

    def corner(r, c):
        up = v_wall[r - 1][c] if r > 0 else False
        down = v_wall[r][c] if r < height else False
        left = h_wall[r][c - 1] if c > 0 else False
        right = h_wall[r][c] if c < width else False
        return junctions[(up, down, left, right)]

    lines = []
    for r in range(height + 1):
        row_chars = []
        for c in range(width):
            row_chars.append(corner(r, c))
            row_chars.append((h_char if h_wall[r][c] else " ") * cell_w)
        row_chars.append(corner(r, width))
        lines.append("".join(row_chars))

        if r < height:
            content_chars = []
            for c in range(width):
                content_chars.append(v_char if v_wall[r][c] else " ")
                content_chars.append(grid[r][c].rjust(cell_w))
            content_chars.append(v_char if v_wall[r][width] else " ")
            lines.append("".join(content_chars))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Display a Shikaku puzzle as text art.")
    parser.add_argument("file", nargs="?", default=None, help="puzzle file (default: stdin)")
    parser.add_argument("--puzzle-only", action="store_true", help="only show the unsolved clue grid")
    parser.add_argument("--solution-only", action="store_true", help="only show the solved grid")
    parser.add_argument(
        "--unicode", action="store_true", help="use Unicode box-drawing characters (needs a UTF-8 terminal)"
    )
    args = parser.parse_args()

    if args.unicode:
        # Windows defaults stdout to the console code page (e.g. cp949),
        # which can't represent box-drawing glyphs and corrupts them even
        # when writing to a file. Force UTF-8 regardless of platform.
        sys.stdout.reconfigure(encoding="utf-8")

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    puzzle = Puzzle.from_text(text)

    want_puzzle = not args.solution_only
    want_solution = puzzle.solution is not None and not args.puzzle_only

    if args.solution_only and puzzle.solution is None:
        parser.error("puzzle file has no witness solution to show")

    if want_puzzle:
        print(f"Shikaku {puzzle.width}x{puzzle.height} ({len(puzzle.clues)} clues)")
        print(render(puzzle, show_solution=False, unicode=args.unicode))
    if want_solution:
        if want_puzzle:
            print()
        print("Solution:")
        print(render(puzzle, show_solution=True, unicode=args.unicode))


if __name__ == "__main__":
    main()
