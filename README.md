# Shikaku

Tools for generating, viewing, and solving [Shikaku](https://en.wikipedia.org/wiki/Shikaku) puzzles: partition a W x H
grid into rectangles so each rectangle contains exactly one numbered clue equal to its area.

Requires Python 3.9+ (standard library only — `tkinter` ships with the standard Windows/macOS installers).

## Files

- **`shikaku_common.py`** — shared data model (`Rect`, `Clue`, `Puzzle`) and the puzzle text format's
  reader/writer. Imported by the other three scripts.
- **`shikaku_gen.py`** — generates a puzzle by tiling: recursively splits the grid into rectangles
  (guillotine cuts) within a min/max area range, then drops one clue per rectangle. Solvable by
  construction, since the tiling itself is a witness solution.
- **`shikaku_display.py`** — renders a puzzle file as text art: the blank clue grid, and (if the file
  includes a witness tiling) the solved grid with rectangle boundaries drawn.
- **`shikaku_solver.py`** — interactive Tkinter app for solving a puzzle by hand: drag to draw a
  rectangle, right-click to remove one, live validity feedback, win detection.

## Usage

Generate a puzzle:

```sh
python shikaku_gen.py --width 12 --height 8 --min-area 2 --max-area 10 --seed 42 --solution --output puzzle.txt
```

| Flag | Meaning | Default |
|---|---|---|
| `--width`, `--height` | grid dimensions | 10, 10 |
| `--min-area`, `--max-area` | rectangle area bounds | 2, 10 |
| `--split-prob` | chance to split a rectangle further even under `--max-area`, for size variety | 0.3 |
| `--seed` | RNG seed, for reproducible puzzles | random |
| `--solution` | include the witness tiling in the output | off |
| `--output` | output file (default: stdout) | stdout |

View it as text art:

```sh
python shikaku_display.py puzzle.txt              # clue grid + solution
python shikaku_display.py --puzzle-only puzzle.txt
python shikaku_display.py --solution-only puzzle.txt
python shikaku_gen.py --seed 1 --solution | python shikaku_display.py   # pipe directly, no file
python shikaku_display.py --unicode puzzle.txt    # nicer box-drawing chars, needs a UTF-8 terminal
```

Solve it interactively:

```sh
python shikaku_solver.py puzzle.txt   # or launch with no argument and use Open.../New... in the toolbar
```

## Puzzle file format

```
W H
N
row col value      (N clue lines)
SOLUTION            (omitted if no witness tiling was generated)
top left height width   (N rectangle lines, only present after SOLUTION)
```

All coordinates are 0-indexed. `Puzzle.from_text` / `Puzzle.to_text` in `shikaku_common.py` are the
canonical reader/writer — read/write puzzle files through those rather than re-parsing the format
elsewhere.
