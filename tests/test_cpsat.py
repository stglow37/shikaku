"""Independent formulation checks and adversarial solver-status handling."""

import importlib.util
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from shikaku.model import Rect
from shikaku.solvers.cpsat import seed_partition, solve
from shikaku.validation import validate_partition
from tests.oracle import cell_oracle


HAS_ORTOOLS = importlib.util.find_spec("ortools") is not None


class CpSatInputTests(unittest.TestCase):
    def test_invalid_inputs_before_optional_import(self):
        for n in (0, -1, 1.5, True, "2"):
            with self.subTest(n=n), self.assertRaises(ValueError):
                solve(n)
        options = [
            {"time_limit": value} for value in (-1, float("nan"), float("inf"), True, "1")
        ] + [{"num_workers": value} for value in (0, -1, True, 1.5)] + [
            {"random_seed": value} for value in (-1, True, 2**31, 1.5)
        ] + [{"log_search_progress": 1}, {"use_hints": 1},
             {"seed_strategy": "unknown"}, {"seed_strategy": 1}]
        for option in options:
            with self.subTest(option=option), self.assertRaises(ValueError):
                solve(2, **option)

    def test_seed_strategies_are_explicit_and_validated(self):
        baseline = seed_partition(16, "baseline")
        eleven_eighths = seed_partition(16, "eleven_eighths")
        best_known = seed_partition(20, "best_known")
        self.assertEqual(validate_partition(16, baseline), 20)
        self.assertEqual(validate_partition(16, eleven_eighths), 21)
        self.assertEqual(validate_partition(20, best_known), 27)
        with self.assertRaises(ValueError):
            seed_partition(15, "eleven_eighths")
        with self.assertRaises(ValueError):
            seed_partition(16, "unknown")

    def test_missing_optional_dependency_has_install_instruction(self):
        real_import = __import__

        def import_without_ortools(name, *args, **kwargs):
            if name == "ortools" or name.startswith("ortools."):
                raise ModuleNotFoundError("No module named 'ortools'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_without_ortools):
            with self.assertRaisesRegex(ImportError, "requirements-cpsat.txt"):
                solve(5)


@unittest.skipUnless(HAS_ORTOOLS, "optional OR-Tools dependency not installed")
class CpSatTests(unittest.TestCase):
    def test_small_grids_against_independent_cell_oracle(self):
        for n in range(1, 5):
            with self.subTest(n=n):
                expected, _ = cell_oracle(n)
                result = solve(n)
                expected_status = "NOT_RUN" if n < 4 else "OPTIMAL"
                self.assertEqual(result["solver_status"], expected_status)
                self.assertEqual(result["k"], expected)
                self.assertEqual(result["lower_bound"], expected)
                self.assertEqual(result["upper_bound"], expected)
                expected_source = "initial_construction" if n < 4 else "cp_sat"
                self.assertEqual(result["witness_source"], expected_source)
                expected_variables = 0 if n < 4 else (n * (n + 1) // 2)**2
                self.assertEqual(result["rectangle_variables"], expected_variables)
                self.assertEqual(validate_partition(n, [Rect(**r) for r in
                                                       result["rectangles"]]), expected)

    def test_zero_solver_time_keeps_verified_seed(self):
        result = solve(5, time_limit=0)
        self.assertEqual(result["solver_status"], "UNKNOWN")
        self.assertEqual(result["status"], "TIME_LIMIT")
        self.assertIsNone(result["k"])
        self.assertIsNone(result["solver_upper_bound"])
        self.assertIsNone(result["solver_objective"])
        self.assertEqual(result["witness_source"], "initial_construction")
        self.assertLess(result["lower_bound"], result["upper_bound"])
        self.assertEqual(validate_partition(5, [Rect(**r) for r in result["rectangles"]]),
                         result["lower_bound"])
        self.assertGreaterEqual(result["model_build_seconds"], 0)
        self.assertGreaterEqual(result["elapsed_seconds"], result["model_build_seconds"])

    def test_zero_time_can_use_improved_seed_without_hints(self):
        result = solve(16, time_limit=0, seed_strategy="eleven_eighths",
                       use_hints=False)
        self.assertEqual(result["k"], 21)
        self.assertEqual(result["solver_status"], "NOT_RUN")
        self.assertEqual(result["seed_strategy"], "eleven_eighths")
        self.assertFalse(result["use_hints"])

    def test_exact_by_independent_bounds_skips_solver(self):
        result = solve(7, time_limit=0)
        self.assertEqual(result["solver_status"], "NOT_RUN")
        self.assertEqual(result["status"], "OPTIMAL")
        self.assertEqual(result["termination"], "certified_initial_bounds")
        self.assertEqual(result["k"], 9)
        self.assertEqual(result["rectangle_variables"], 0)

    def test_feasible_is_not_automatically_optimal(self):
        from ortools.sat.python import cp_model

        class FeasibleSeedSolver:
            """Emulate a stopped solver that returned the model's seed only."""

            parameters = SimpleNamespace()
            objective_value = 5.0
            best_objective_bound = 6.0
            num_branches = 0
            num_conflicts = 0
            wall_time = 0.0

            def solve(self, model):
                hint = model.proto.solution_hint
                self.values = dict(zip(hint.vars, hint.values))
                return cp_model.FEASIBLE

            def status_name(self, status):
                return "FEASIBLE"

            def value(self, variable):
                return self.values[variable.index]

        with patch.object(cp_model, "CpSolver", FeasibleSeedSolver):
            result = solve(5, time_limit=1)
        self.assertEqual(result["solver_status"], "FEASIBLE")
        self.assertEqual(result["status"], "TIME_LIMIT")
        self.assertIsNone(result["k"])
        self.assertEqual((result["lower_bound"], result["upper_bound"]), (5, 6))
        self.assertEqual(validate_partition(5, [Rect(**r) for r in result["rectangles"]]), 5)


if __name__ == "__main__":
    unittest.main()
