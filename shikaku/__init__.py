"""Distinct-area rectangle partition research tools."""

from .model import Rect
from .solvers.skyline import solve
from .validation import validate_partition

__all__ = ["Rect", "solve", "validate_partition"]
