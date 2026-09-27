"""Auditable witness for k(16t) >= 22t-1, and padded witnesses.

Run from the repository root with python -m experiments.theory_strip.
This independent research script does not alter the baseline solver.
"""
from __future__ import annotations
import json
from pathlib import Path
from shikaku.improved_constructions import partition_11_over_8
from shikaku.validation import validate_partition


def representable_upper(n: int) -> int:
    remaining = n*n
    count = 0
    for area in sorted({a*b for a in range(1, n+1) for b in range(1, n+1)}):
        if area > remaining:
            break
        remaining -= area
        count += 1
    return count


def main() -> None:
    rows = []
    for n in range(16, 257):
        rectangles = partition_11_over_8(n)
        count = validate_partition(n, rectangles)
        guaranteed = 22*(n//16)-1
        assert count >= guaranteed
        if n % 16 == 0:
            assert count == guaranteed
        upper = representable_upper(n)
        assert count <= upper
        rows.append(dict(n=n, count=count, theorem_lower=guaranteed, upper=upper,
                         rectangles=len(rectangles), exact=count==upper))
    output = Path(__file__).with_name('theory_strip_results.json')
    output.write_text(json.dumps(rows, indent=2) + '\n', encoding="utf-8")
    print(json.dumps({'verified_n_range':[16,256], 'exact_cases':[r for r in rows if r['exact']],
                      'results':str(output)}, indent=2))

if __name__ == '__main__':
    main()
