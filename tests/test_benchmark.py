"""Benchmark protocol validation and end-to-end smoke tests."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experiments.analyze_benchmarks import aggregate
from experiments.benchmark import _validate_benchmark


def tiny_config():
    return {
        "schema_version": 1,
        "repeats": 1,
        "wall_timeout_grace_seconds": 5,
        "suites": [{
            "name": "tiny-skyline", "role": "exact",
            "solver": {"solver": "skyline", "options": {"prune": True}},
            "sizes": [4], "time_limit_seconds": 1,
        }],
    }


class BenchmarkTests(unittest.TestCase):
    def test_protocol_validation(self):
        self.assertEqual(_validate_benchmark(tiny_config()), tiny_config())
        invalid = tiny_config()
        invalid["repeats"] = True
        with self.assertRaises(ValueError):
            _validate_benchmark(invalid)
        invalid = tiny_config()
        invalid["suites"][0]["solver"]["options"] = {"prune": "yes"}
        with self.assertRaises(ValueError):
            _validate_benchmark(invalid)

    def test_runner_and_analysis_smoke(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = root / "config.json"
            config.write_text(json.dumps(tiny_config()), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, "-m", "experiments.benchmark", "--config", str(config),
                 "--output-root", str(root)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            outputs = [path for path in root.glob("benchmark-*") if path.is_dir()]
            self.assertEqual(len(outputs), 1)
            report = json.loads(
                (outputs[0] / "benchmark.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "COMPLETED")
            self.assertEqual(report["trials"][0]["outcome"], "COMPLETED")
            rows = aggregate(report)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["exact_runs"], 1)


if __name__ == "__main__":
    unittest.main()
