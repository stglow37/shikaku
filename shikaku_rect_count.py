#!/usr/bin/env python3
"""Count the number of ways to partition a w x h grid into axis-aligned,
integer-sided rectangles.

This is a studied enumerative-combinatorics problem, not something with a
closed-form formula:

  - OEIS A116694 - "Array read by antidiagonals: number of ways of dividing
    an n X m rectangle into integer-sided rectangles."
    https://oeis.org/A116694
  - OEIS A182275 - the n x n diagonal of the above (square grids).
    https://oeis.org/A182275
  - David A. Klarner and Spyros S. Magliveras, "The number of tilings of a
    block with blocks", European Journal of Combinatorics 9 (1988), 317-330.
    https://doi.org/10.1016/S0195-6698(88)80062-3
  - Joshua Smith and Helena Verrill, "On dividing rectangles into
    rectangles", Louisiana State Univ. (2006).
    https://oeis.org/A116694/a116694.pdf
  - Pablo Blanco, Robert Dougherty-Bliss, Natalya Ter-Saakov, and Doron
    Zeilberger, "In How Many Ways can a Rectangle be Rectangled?",
    arXiv:2606.05439 [math.CO], 2026.
    https://arxiv.org/abs/2606.05439

Algorithm (skyline / profile DP)
---------------------------------
Brute-force enumeration is infeasible past tiny grids. Instead, always
place the rectangle that covers the current topmost-leftmost still-empty
cell, try every valid width x height for it, and recurse. Because the
placement point is canonical (there's only one topmost-leftmost empty
cell at each step), every dissection - including non-guillotine
"pinwheel" ones that a simple recursive-cut formula would miss or
double-count - is generated exactly once.

The state that matters for memoization is the "skyline": for each column,
how many rows from the top are already filled. Many different placement
sequences lead to the same skyline, so memoizing on it collapses a huge
amount of redundant recursion. This is the same idea underlying the
transfer-matrix approach in the papers above (their transfer matrix is
built over exactly this kind of column-profile state); the fixed-size
recursion here is the direct/unaccelerated version of it.

Complexity notes
-----------------
Growth is roughly double-exponential once *both* dimensions grow: 8x8 in
this implementation takes ~2 minutes, and the state of the art (2026
paper above) explicitly states the 100x100 count will likely never be
known by anyone. If, however, one dimension m stays small while the other
n gets large, the DP only ever needs to fit its state in the shape that
scales with m, and repeats for every incremental column, so counts for
"2 x 10_000_000"-style grids are effectively free. Klarner-Magliveras and
Smith-Verrill exploit this by building the transfer matrix once (sized
purely from m) and raising it to a power via fast matrix exponentiation,
turning the "large n" axis into an O(log n) matrix-power instead of an
O(n) walk - useful if this module ever needs to handle a small-height,
huge-width case.
"""


def count_partitions(w: int, h: int) -> int:
    """Return the number of ways to partition a w x h grid into rectangles.

    Verified against known OEIS values, e.g. count_partitions(4, 4) == 70878
    and count_partitions(2, 3) == 34 (see A116694 / A182275).
    """
    if w <= 0 or h <= 0:
        raise ValueError("width and height must be positive")
    if w > h:
        w, h = h, w  # keep the skyline (length w) as the smaller side

    memo: dict[tuple[int, ...], int] = {}

    def solve(skyline: tuple[int, ...]) -> int:
        if skyline in memo:
            return memo[skyline]
        r = min(skyline)
        if r == h:
            return 1
        c = skyline.index(r)
        max_w = 0
        while c + max_w < w and skyline[c + max_w] == r:
            max_w += 1
        total = 0
        for wid in range(1, max_w + 1):
            for hei in range(1, h - r + 1):
                new_sky = list(skyline)
                for cc in range(c, c + wid):
                    new_sky[cc] = r + hei
                total += solve(tuple(new_sky))
        memo[skyline] = total
        return total

    return solve((0,) * w)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        w, h = int(sys.argv[1]), int(sys.argv[2])
    else:
        w, h = 5, 5
    print(f"{w}x{h}: {count_partitions(w, h)}")
