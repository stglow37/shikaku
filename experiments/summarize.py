"""Combine independently validated witnesses; certify exactness via area bounds.

Uses only the standard library. Pass experiment directories with --runs.
"""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from math import isqrt
import json
from pathlib import Path

from shikaku.bounds import area_upper_bound
from shikaku.constructions import initial_partition
from shikaku.improved_constructions import best_partition
from shikaku.extensions import extend_partition
from shikaku.model import Rect
from shikaku.validation import validate_partition


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, nargs="*", default=[])
    parser.add_argument("--max-n", type=int, default=40)
    parser.add_argument("--extension-gap", type=int, default=8)
    parser.add_argument("--output", type=Path, default=ROOT / "results/research-20260920")
    args = parser.parse_args()
    if args.max_n < 1 or args.extension_gap < 0:
        parser.error("--max-n must be positive and --extension-gap non-negative")
    if args.output.exists():
        parser.error("output directory already exists; choose a new one")
    rows = {}
    for n in range(1, args.max_n + 1):
        witness = best_partition(n)
        lower = validate_partition(n, witness)
        rows[n] = dict(
            n=n, classical_lower=validate_partition(n, initial_partition(n)),
            explicit_lower=lower, lower_bound=lower, upper_bound=area_upper_bound(n),
            triangle_upper=(isqrt(8 * n * n + 1) - 1) // 2,
            witness_source="best_explicit_construction",
            rectangles=[asdict(r) for r in witness],
            distinct_areas=sorted({r.area for r in witness}),
        )
    run_paths = []
    comparisons = []
    for directory in args.runs:
        report_path = directory / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        try:
            relative = str(report_path.resolve().relative_to(ROOT))
        except ValueError:
            relative = str(report_path.resolve())
        run_paths.append(relative)
        for result in report["results"]:
            n = result["n"]
            witness = [Rect(**r) for r in result["rectangles"]]
            score = validate_partition(n, witness)
            if score != result["lower_bound"]:
                raise ValueError(f"invalid witness score in {relative}")
            if score > area_upper_bound(n):
                raise ValueError(f"witness exceeds certified bound in {relative}")
            comparisons.append({key: result.get(key) for key in (
                "n", "solver", "status", "lower_bound", "upper_bound", "elapsed_seconds",
                "model_build_seconds", "solve_call_seconds", "nodes",
                "restricted_status", "restricted_lower_bound", "restricted_upper_bound",
            )} | {"source": relative, "configuration": report["configuration"]})
            if n in rows and score > rows[n]["lower_bound"]:
                rows[n].update(lower_bound=score, rectangles=result["rectangles"],
                               witness_source=relative,
                               distinct_areas=sorted({r.area for r in witness}))
    for n, row in rows.items():
        row["direct_lower"] = row["lower_bound"]
        for m in range(max(1, n - args.extension_gap), n):
            base = [Rect(**r) for r in rows[m]["rectangles"]]
            witness = extend_partition(m, n, base)
            score = validate_partition(n, witness)
            if score > row["upper_bound"]:
                raise ValueError("extended witness exceeds certified upper bound")
            if score > row["lower_bound"]:
                row.update(lower_bound=score, rectangles=[asdict(r) for r in witness],
                           witness_source=f"border_extension_from_{m}", extension_from=m,
                           distinct_areas=sorted({r.area for r in witness}))
        row["k"] = row["lower_bound"] if row["lower_bound"] == row["upper_bound"] else None
    summary = dict(
        created_utc=datetime.now(timezone.utc).isoformat(),
        certification="Every exact k is a checked witness meeting the independent area upper U(n).",
        runs=run_paths, extension_gap=args.extension_gap,
        results=list(rows.values()), comparisons=comparisons,
    )
    args.output.mkdir(parents=True)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
               for folder in ("shikaku", "experiments", "tests")
               for p in sorted((ROOT / folder).rglob("*.py"))}
    (args.output / "sources.json").write_text(
        json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    table = ["| n | 기존 구성 | 개선한 명시적 구성 | 최선 하한 | 상한 U(n) | 정확값 |",
             "|---:|---:|---:|---:|---:|---:|"]
    for row in rows.values():
        table.append("| {n} | {classical_lower} | {explicit_lower} | {lower_bound} | {upper_bound} | {exact} |".format(
            **row, exact=row["k"] if row["k"] is not None else "미확정"))
    (args.output / "table.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    print("\n".join(table))
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
