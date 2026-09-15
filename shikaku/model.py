"""Shared rectangle and serialized solver result types."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Rect:
    row: int
    col: int
    height: int
    width: int

    @property
    def area(self) -> int:
        return self.height * self.width
