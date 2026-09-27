"""Validate and aggregate a benchmark report into paper-ready tables."""

import argparse
import csv
import io
import json
from pathlib import Path
from statistics import median

from shikaku.model import Rect
from shikaku.validation import validate_partition


def _number(values, key):
    found = [value[key] for value in values if value.get(key) is not None]
    return median(found) if found else None


def _fmt(value, digits=3):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _validate_trial(trial: dict) -> None:
    if trial["outcome"] != "COMPLETED":
        return
    result = trial["result"]
    witness = [Rect(**rect) for rect in result["rectangles"]]
    score = validate_partition(trial["n"], witness)
    if score != trial["verified_score"] or score != result["lower_bound"]:
        raise ValueError(f"invalid witness in {trial['trial_id']}")
    if score > result["upper_bound"]:
        raise ValueError(f"contradictory bounds in {trial['trial_id']}")


def aggregate(report: dict) -> list[dict]:
    suite_meta = {suite["name"]: suite for suite in report["configuration"]["suites"]}
    grouped = {}
    for trial in report["trials"]:
        _validate_trial(trial)
        grouped.setdefault((trial["suite"], trial["n"]), []).append(trial)
    rows = []
    for (suite_name, n), trials in grouped.items():
        completed = [trial for trial in trials if trial["outcome"] == "COMPLETED"]
        results = [trial["result"] for trial in completed]
        gaps = [result["upper_bound"] - result["lower_bound"] for result in results]
        exact = [result.get("k") is not None for result in results]
        initial_certified = [
            result.get("termination") == "certified_initial_bounds" for result in results]
        rows.append({
            "role": suite_meta[suite_name]["role"], "suite": suite_name, "n": n,
            "requested_runs": report["configuration"]["repeats"],
            "completed_runs": len(completed),
            "process_timeouts": sum(t["outcome"] == "PROCESS_TIMEOUT" for t in trials),
            "errors": sum(t["outcome"] not in {"COMPLETED", "PROCESS_TIMEOUT"}
                          for t in trials),
            "exact_runs": sum(exact),
            "initial_certified_runs": sum(initial_certified),
            "median_lower_bound": _number(results, "lower_bound"),
            "median_upper_bound": _number(results, "upper_bound"),
            "best_lower_bound": max((r["lower_bound"] for r in results), default=None),
            "best_upper_bound": min((r["upper_bound"] for r in results), default=None),
            "median_gap": median(gaps) if gaps else None,
            "median_process_seconds": _number(completed, "process_elapsed_seconds"),
            "median_elapsed_seconds": _number(results, "elapsed_seconds"),
            "median_model_build_seconds": _number(results, "model_build_seconds"),
            "median_solve_seconds": _number(results, "solve_call_seconds"),
            "median_nodes": _number(results, "nodes"),
        })
    return sorted(rows, key=lambda row: (row["role"], row["suite"], row["n"]))


def _markdown(rows: list[dict]) -> str:
    lines = [
        "# Benchmark summary",
        "",
        "Times are medians over completed repetitions. Node counts are meaningful only",
        "within one solver family. A timeout is not evidence of infeasibility.",
        "",
    ]
    for role in ("exact", "construction", "ablation"):
        selected = [row for row in rows if row["role"] == role]
        if not selected:
            continue
        lines.extend([
            f"## {role}", "",
            "| suite | n | completed | exact | initial | combined bounds | median gap | process s | build s | solve s | nodes |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in selected:
            bounds = f"{_fmt(row['best_lower_bound'])}–{_fmt(row['best_upper_bound'])}"
            lines.append(
                f"| {row['suite']} | {row['n']} | {row['completed_runs']}/"
                f"{row['requested_runs']} | {row['exact_runs']} | "
                f"{row['initial_certified_runs']} | {bounds} | "
                f"{_fmt(row['median_gap'])} | {_fmt(row['median_process_seconds'])} | "
                f"{_fmt(row['median_model_build_seconds'])} | "
                f"{_fmt(row['median_solve_seconds'])} | {_fmt(row['median_nodes'], 0)} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path,
                        help="benchmark directory or benchmark.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report_path = (args.benchmark / "benchmark.json" if args.benchmark.is_dir()
                   else args.benchmark)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = aggregate(report)
    destination = args.output or report_path.parent / "analysis"
    if destination.exists():
        parser.error("output directory already exists")
    destination.mkdir(parents=True)
    (destination / "summary.json").write_text(
        json.dumps({"benchmark": str(report_path.resolve()), "rows": rows}, indent=2) + "\n",
        encoding="utf-8")
    (destination / "summary.md").write_text(_markdown(rows), encoding="utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]) if rows else ["suite"])
    writer.writeheader()
    writer.writerows(rows)
    (destination / "summary.csv").write_text(buffer.getvalue(), encoding="utf-8")
    print(f"Validated {len(report['trials'])} trials; saved: {destination}")


if __name__ == "__main__":
    main()
