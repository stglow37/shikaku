"""Shared data model and text I/O for Shikaku puzzles.

Raw (x, y, w, h) / (row, col, value) tuples are easy to mix up (which
index is which?) and give a puzzle file no self-describing structure a
second tool can parse without duplicating the writer's assumptions.
Rect/Clue/Puzzle fix both problems: fields are named, and Puzzle owns
its own text format so the generator and the display tool share one
source of truth instead of two independent parsers.

Text format:
    W H
    N
    row col value      (N lines)
    SOLUTION            (only if a witness tiling is included)
    top left height width   (N lines)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h

    def contains(self, row: int, col: int) -> bool:
        return self.y <= row < self.y + self.h and self.x <= col < self.x + self.w


@dataclass(frozen=True)
class Clue:
    row: int
    col: int
    value: int


@dataclass
class Puzzle:
    width: int
    height: int
    clues: List[Clue]
    solution: Optional[List[Rect]] = None

    def to_text(self) -> str:
        lines = [f"{self.width} {self.height}", str(len(self.clues))]
        for clue in self.clues:
            lines.append(f"{clue.row} {clue.col} {clue.value}")
        if self.solution is not None:
            lines.append("SOLUTION")
            for r in self.solution:
                lines.append(f"{r.y} {r.x} {r.h} {r.w}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def from_text(text: str) -> "Puzzle":
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        width, height = map(int, lines[0].split())
        n = int(lines[1])

        clues = []
        idx = 2
        for _ in range(n):
            r, c, v = map(int, lines[idx].split())
            clues.append(Clue(r, c, v))
            idx += 1

        solution = None
        if idx < len(lines) and lines[idx] == "SOLUTION":
            idx += 1
            solution = []
            for _ in range(n):
                y, x, h, w = map(int, lines[idx].split())
                solution.append(Rect(x, y, w, h))
                idx += 1

        return Puzzle(width, height, clues, solution)
