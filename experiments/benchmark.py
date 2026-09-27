"""Run an isolated, resumable benchmark matrix with independent validation."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from math import isfinite
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

from shikaku.config import validate_config
from shikaku.model import Rect
from shikaku.validation import validate_partition


ROOT = Path(__file__).resolve().parents[1]


def _git_output(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _dependency_versions() -> dict[str, str]:
    found = {}
    for name in ("ortools", "protobuf", "numpy"):
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            pass
    return found


def _validate_benchmark(config: object) -> dict:
    if not isinstance(config, dict) or set(config) != {
            "schema_version", "repeats", "wall_timeout_grace_seconds", "suites"}:
        raise ValueError("benchmark config has unexpected fields")
    if config["schema_version"] != 1:
        raise ValueError("unsupported benchmark schema_version")
    if type(config["repeats"]) is not int or config["repeats"] < 1:
        raise ValueError("repeats must be a positive integer")
    grace = config["wall_timeout_grace_seconds"]
    if (isinstance(grace, bool) or not isinstance(grace, (int, float))
            or not isfinite(grace) or grace < 0):
        raise ValueError("wall_timeout_grace_seconds must be finite and non-negative")
    suites = config["suites"]
    if not isinstance(suites, list) or not suites:
        raise ValueError("suites must be a non-empty list")
    names = set()
    for suite in suites:
        if not isinstance(suite, dict) or set(suite) != {
                "name", "role", "solver", "sizes", "time_limit_seconds"}:
            raise ValueError("benchmark suite has unexpected fields")
        if (not isinstance(suite["name"], str) or not suite["name"]
                or suite["name"] in names):
            raise ValueError("suite names must be unique non-empty strings")
        names.add(suite["name"])
        if suite["role"] not in {"exact", "construction", "ablation"}:
            raise ValueError("suite role must be exact, construction, or ablation")
        validate_config(suite["solver"])
        sizes = suite["sizes"]
        if (not isinstance(sizes, list) or not sizes
                or any(type(n) is not int or n < 1 for n in sizes)
                or len(set(sizes)) != len(sizes)):
            raise ValueError("suite sizes must be unique positive integers")
        limit = suite["time_limit_seconds"]
        if (isinstance(limit, bool) or not isinstance(limit, (int, float))
                or not isfinite(limit) or limit < 0):
            raise ValueError("suite time_limit_seconds must be finite and non-negative")
        if (suite["solver"]["solver"] == "cpsat"
                and suite["solver"]["options"].get("seed_strategy") == "eleven_eighths"
                and min(sizes) < 16):
            raise ValueError("eleven_eighths benchmark sizes must be at least 16")
    return config


def _trial_specs(config: dict):
    """Interleave suites at each size to reduce temporal ordering bias."""
    suites = config["suites"]
    max_sizes = max(len(suite["sizes"]) for suite in suites)
    for repetition in range(config["repeats"]):
        for index in range(max_sizes):
            for suite in suites:
                if index < len(suite["sizes"]):
                    n = suite["sizes"][index]
                    yield {
                        "trial_id": f"{suite['name']}__n{n}__r{repetition + 1}",
                        "suite": suite["name"], "role": suite["role"],
                        "repetition": repetition + 1, "n": n,
                    }, suite


def _validate_result(n: int, result: dict) -> int:
    if result.get("n") != n:
        raise ValueError("solver returned the wrong dimension")
    witness = [Rect(**rect) for rect in result["rectangles"]]
    score = validate_partition(n, witness)
    if score != result["lower_bound"]:
        raise ValueError("validated witness disagrees with lower_bound")
    if not score <= result["upper_bound"]:
        raise ValueError("lower_bound exceeds upper_bound")
    if result.get("k") is not None and not result["k"] == score == result["upper_bound"]:
        raise ValueError("claimed exact value is not certified by matching bounds")
    return score


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _tail(value: str | bytes | None, length: int) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return value[-length:]


def _new_report(config: dict, config_path: Path) -> dict:
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
               for folder in ("shikaku", "experiments", "tests")
               for p in sorted((ROOT / folder).rglob("*.py"))}
    hashes = {name: hashlib.sha256(content.encode("utf-8")).hexdigest()
              for name, content in sources.items()}
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RUNNING",
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "dependencies": _dependency_versions(),
        "git_head": _git_output("rev-parse", "HEAD"),
        "git_status": _git_output("status", "--short"),
        "configuration_source": str(config_path.resolve()),
        "configuration": config,
        "source_sha256": hashes,
        "trials": [],
        "sources": sources,
    }


def _run_trial(destination: Path, spec: dict, suite: dict, grace: float) -> dict:
    solver_config = destination / "solver-configs" / f"{suite['name']}.json"
    command = [
        sys.executable, "-m", "shikaku", str(spec["n"]),
        "--config", str(solver_config), "--time-limit", str(suite["time_limit_seconds"]),
    ]
    started = perf_counter()
    try:
        process = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            timeout=suite["time_limit_seconds"] + grace, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return spec | {
            "outcome": "PROCESS_TIMEOUT",
            "process_elapsed_seconds": perf_counter() - started,
            "wall_timeout_seconds": suite["time_limit_seconds"] + grace,
            "stdout_tail": _tail(exc.stdout, 2000),
            "stderr_tail": _tail(exc.stderr, 2000),
        }
    elapsed = perf_counter() - started
    if process.returncode != 0:
        return spec | {
            "outcome": "PROCESS_ERROR", "returncode": process.returncode,
            "process_elapsed_seconds": elapsed,
            "stdout_tail": process.stdout[-2000:], "stderr_tail": process.stderr[-4000:],
        }
    try:
        result = json.loads(process.stdout)
        verified_score = _validate_result(spec["n"], result)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return spec | {
            "outcome": "INVALID_RESULT", "process_elapsed_seconds": elapsed,
            "validation_error": str(exc), "stdout_tail": process.stdout[-4000:],
            "stderr_tail": process.stderr[-2000:],
        }
    return spec | {
        "outcome": "COMPLETED", "process_elapsed_seconds": elapsed,
        "verified_score": verified_score, "result": result,
        "stderr_tail": process.stderr[-2000:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT / "results")
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    if (args.config is None) == (args.resume is None):
        parser.error("provide exactly one of --config or --resume")

    if args.resume is not None:
        destination = args.resume.resolve()
        report_path = destination / "benchmark.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        config = _validate_benchmark(report["configuration"])
        config_path = Path(report["configuration_source"])
        if report["status"] == "COMPLETED":
            parser.error("benchmark is already complete")
        report["status"] = "RUNNING"
        report.pop("error", None)
    else:
        config_path = args.config.resolve()
        config = _validate_benchmark(json.loads(config_path.read_text(encoding="utf-8")))
        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        destination = (args.output_root.resolve()
                       / f"benchmark-{now}-{uuid4().hex[:8]}")
        destination.mkdir(parents=True, exist_ok=False)
        (destination / "solver-configs").mkdir()
        report = _new_report(config, config_path)
        _write_json(destination / "config.json", config)
        _write_json(destination / "sources.json", report.pop("sources"))
        for suite in config["suites"]:
            _write_json(destination / "solver-configs" / f"{suite['name']}.json",
                        suite["solver"])

    report_path = destination / "benchmark.json"
    completed = {trial["trial_id"] for trial in report["trials"]
                 if trial["outcome"] == "COMPLETED"}

    def save() -> None:
        _write_json(report_path, report)

    save()
    try:
        for spec, suite in _trial_specs(config):
            if spec["trial_id"] in completed:
                continue
            trial = _run_trial(
                destination, spec, suite, config["wall_timeout_grace_seconds"])
            # A resumed benchmark replaces a failed attempt for the same trial.
            report["trials"] = [old for old in report["trials"]
                                if old["trial_id"] != spec["trial_id"]]
            report["trials"].append(trial)
            completed.add(spec["trial_id"])
            save()
            bounds = ""
            if trial["outcome"] == "COMPLETED":
                result = trial["result"]
                bounds = f" bounds=[{result['lower_bound']},{result['upper_bound']}]"
            print(f"{trial['trial_id']} {trial['outcome']}{bounds}", flush=True)
    except BaseException as exc:
        report["status"] = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "FAILED"
        report["error"] = str(exc)
        save()
        raise
    failures = [trial for trial in report["trials"] if trial["outcome"] != "COMPLETED"]
    report["status"] = "COMPLETED_WITH_ERRORS" if failures else "COMPLETED"
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    save()
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
