"""Run a configured solver and save an immutable experiment directory."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from math import isfinite
from pathlib import Path
import platform
import subprocess
import sys
from uuid import uuid4

from shikaku.config import load_config
from shikaku.solvers.skyline import solve
from tests.oracle import cell_oracle


ROOT = Path(__file__).resolve().parents[1]


def git_output(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "experiments/configs/baseline.json")
    parser.add_argument("--sizes", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6, 7, 8, 13])
    parser.add_argument("--time-limit", type=float, default=2.0)
    parser.add_argument("--output-root", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    if any(n < 1 for n in args.sizes) or not isfinite(args.time_limit) or args.time_limit < 0:
        parser.error("sizes must be positive; time limit finite and non-negative")
    try:
        config = load_config(args.config)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    now = datetime.now(timezone.utc)
    destination = args.output_root / (now.strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8])
    destination.mkdir(parents=True, exist_ok=False)
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
               for folder in ("shikaku", "experiments", "tests")
               for p in sorted((ROOT / folder).rglob("*.py"))}
    hashes = {name: hashlib.sha256(content.encode("utf-8")).hexdigest()
              for name, content in sources.items()}
    settings = {"solver": config, "sizes": args.sizes, "time_limit": args.time_limit,
                "oracle_up_to": 4}
    report = {"created_utc": now.isoformat(), "python": sys.version,
              "platform": platform.platform(), "git_head": git_output("rev-parse", "HEAD"),
              "git_status": git_output("status", "--short"), "source_sha256": hashes,
              "configuration": settings, "status": "RUNNING", "results": []}
    (destination / "config.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    # A snapshot makes runs reproducible even when the working tree is uncommitted.
    (destination / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")

    def save():
        (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    save()
    try:
        for n in args.sizes:
            result = solve(n, **config["options"], time_limit=args.time_limit)
            if n <= 4:
                expected, partitions = cell_oracle(n)
                result.update(oracle_k=expected, oracle_partitions=partitions)
                assert result["lower_bound"] <= expected <= result["upper_bound"]
                if result["k"] is not None:
                    assert result["k"] == expected
                if not config["options"]["prune"] and result["termination"] == "search_exhausted":
                    assert result["complete_partitions"] == partitions
            report["results"].append(result)
            save()
            print(f"n={n} {result['status']} bounds=[{result['lower_bound']},"
                  f"{result['upper_bound']}] nodes={result['nodes']}")
    except BaseException as exc:
        report["status"] = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "FAILED"
        report["error"] = str(exc)
        save()
        raise
    report["status"] = "COMPLETED"
    save()
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
