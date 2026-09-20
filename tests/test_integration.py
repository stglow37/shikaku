"""Public entry points, optional solver selection, and published witness."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from shikaku.config import load_config
from shikaku.dispatch import solve_configured
from shikaku.known import carnahan_20
from shikaku.validation import validate_partition


class IntegrationTests(unittest.TestCase):
    def test_default_remains_baseline(self):
        result = solve_configured(4, load_config())
        self.assertEqual((result["k"], result["nodes"]), (5, 33))

    def test_published_20(self):
        witness = carnahan_20()
        self.assertEqual(validate_partition(20, witness), 27)
        self.assertEqual(sorted(r.area for r in witness),
                         list(range(1, 22)) + [24, 25, 27, 28, 30, 35])

    def test_configs_and_invalid_options(self):
        configs = [
            ({"solver": "cpsat", "options": {"num_workers": 1}}, True),
            ({"solver": "strips", "options": {"max_parts": 3}}, True),
            ({"solver": "cpsat", "options": {"prune": False}}, False),
            ({"solver": "strips", "options": {"workers": True}}, False),
            ({"solver": "strips", "options": {"max_height": 0}}, False),
            ({"solver": "skyline", "options": {}}, False),
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            for config, valid in configs:
                with self.subTest(config=config):
                    path.write_text(json.dumps(config))
                    if valid:
                        self.assertEqual(load_config(path), config)
                    else:
                        with self.assertRaises(ValueError):
                            load_config(path)

    def test_no_prune_rejected_for_other_solvers(self):
        result = subprocess.run(
            [sys.executable, "-m", "shikaku", "4", "--no-prune", "--config",
             "experiments/configs/strips.json"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("applies only to skyline", result.stderr)


if __name__ == "__main__":
    unittest.main()
