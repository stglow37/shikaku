"""Constructive lower bounds from horizontal strips using optional OR-Tools.

The restricted model cannot certify infeasibility for arbitrary rectangle tilings.
A returned k is exact only when a witness reaches the general area upper bound.
"""

from collections import defaultdict
from dataclasses import asdict
from math import ceil, isfinite
from time import perf_counter
from typing import Iterator

from ..bounds import additional_bound
from ..constructions import initial_partition
from ..model import Rect
from ..validation import validate_partition


def width_partitions(total: int, max_parts: int, minimum: int = 1) -> Iterator[tuple[int, ...]]:
    """Yield integer partitions with at most max_parts parts, in ascending order."""
    if max_parts < 1 or total < minimum:
        return
    yield (total,)
    if max_parts > 1:
        for first in range(minimum, total // 2 + 1):
            for rest in width_partitions(total - first, max_parts - 1, first):
                yield (first,) + rest


def solve(n: int, *, time_limit: float | None = None, max_parts: int = 3,
          max_height: int | None = None, workers: int = 1,
          seed: int = 0) -> dict:
    """Find a lower bound using strips with at most max_parts rectangles each.

    Unused rows can always be filled by unit squares. The time limit includes
    preprocessing; its remaining portion is passed to CP-SAT. A completed strip
    optimization still returns k=None unless the general upper bound is reached.
    OR-Tools is imported lazily, and isn't needed for time_limit=0 or an initial
    witness that is already globally optimal.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    for value, name in ((max_parts, "max_parts"), (workers, "workers")):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if max_height is not None and (not isinstance(max_height, int)
                                  or isinstance(max_height, bool) or max_height < 1):
        raise ValueError("max_height must be a positive integer")
    if (not isinstance(seed, int) or isinstance(seed, bool)
            or not 0 <= seed <= 2**31 - 1):
        raise ValueError("seed must be an integer between 0 and 2**31 - 1")
    if time_limit is not None and (
        isinstance(time_limit, bool) or not isinstance(time_limit, (int, float))
        or not isfinite(time_limit) or time_limit < 0
    ):
        raise ValueError("time_limit must be finite and non-negative")
    started = perf_counter()
    possible_areas = sorted({h * w for h in range(1, n + 1) for w in range(1, n + 1)})
    upper = additional_bound(possible_areas, frozenset(), n * n)
    best_rects = initial_partition(n)
    initial = best = validate_partition(n, best_rects)
    reason = "upper_bound_reached" if best == upper else "time_limit"
    strip_status = "NOT_RUN"
    strip_upper = None
    strip_lower = None
    config_count = branches = conflicts = 0
    model_build_seconds = solve_call_seconds = solver_wall_seconds = 0.0
    if best < upper and time_limit != 0:
        try:
            from ortools.sat.python import cp_model
        except ImportError as exc:
            raise ImportError("The strip solver requires OR-Tools: install requirements-cpsat.txt") from exc
        build_started = perf_counter()
        model = cp_model.CpModel()
        configs = []
        area_sources = defaultdict(list)
        def out_of_time():
            return time_limit is not None and perf_counter() - started >= time_limit

        parts = []
        for widths in width_partitions(n, min(n, max_parts)):
            if out_of_time():
                break
            parts.append(widths)
        for height in range(1, min(n, max_height or n) + 1):
            if out_of_time():
                break
            seen = set()
            for widths in parts:
                if out_of_time():
                    break
                areas = frozenset(height * w for w in widths)
                if areas in seen:
                    continue
                seen.add(areas)
                choice = model.new_bool_var(f"strip_{height}_{len(configs)}")
                configs.append((height, widths, choice))
                for area in areas:
                    area_sources[area].append(choice)
        config_count = len(configs)
        filler = model.new_int_var(0, n, "unit_filler_rows")
        has_filler = model.new_bool_var("has_unit_filler")
        model.add(filler >= 1).only_enforce_if(has_filler)
        model.add(filler == 0).only_enforce_if(has_filler.Not())
        area_sources[1].append(has_filler)
        model.add(sum(h * x for h, _, x in configs) + filler == n)
        used = {}
        for area, sources in area_sources.items():
            present = model.new_bool_var(f"area_{area}")
            model.add_max_equality(present, sources)
            used[area] = present
        model.add(sum(used.values()) <= upper)
        model.add(sum(area * present for area, present in used.items()) <= n * n)
        model.maximize(sum(used.values()))
        # Seed with the baseline construction where the configured family allows it.
        groups = defaultdict(list)
        for rect in best_rects:
            groups[(rect.row, rect.height)].append(rect.width)
        hint_keys = {(h, tuple(sorted(widths))) for (_, h), widths in groups.items()
                     if len(widths) <= max_parts and h <= (max_height or n)}
        hinted_height = 0
        hinted_areas = set()
        for height, widths, choice in configs:
            chosen = (height, widths) in hint_keys
            model.add_hint(choice, int(chosen))
            if chosen:
                hinted_height += height
                hinted_areas.update(height * w for w in widths)
        if hinted_height <= n:
            model.add_hint(filler, n - hinted_height)
            model.add_hint(has_filler, int(hinted_height < n))
            if hinted_height < n:
                hinted_areas.add(1)
            for area, present in used.items():
                model.add_hint(present, int(area in hinted_areas))
        model_build_seconds = perf_counter() - build_started
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed
        remaining = None if time_limit is None else time_limit - (perf_counter() - started)
        if remaining is None or remaining > 0:
            if remaining is not None:
                solver.parameters.max_time_in_seconds = remaining
            solve_started = perf_counter()
            status = solver.solve(model)
            solve_call_seconds = perf_counter() - solve_started
            solver_wall_seconds = solver.wall_time
            strip_status = solver.status_name(status)
            branches = solver.num_branches
            conflicts = solver.num_conflicts
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                rects = []
                row = 0
                for height, widths, choice in configs:
                    if solver.boolean_value(choice):
                        col = 0
                        for width in widths:
                            rects.append(Rect(row, col, height, width))
                            col += width
                        row += height
                rects.extend(Rect(y, x, 1, 1) for y in range(row, n) for x in range(n))
                score = validate_partition(n, rects)
                strip_lower = score
                assert abs(solver.objective_value - score) < 1e-6
                if score > best:
                    best, best_rects = score, rects
                strip_upper = min(upper, ceil(solver.best_objective_bound))
            if best == upper:
                reason = "upper_bound_reached"
            elif status == cp_model.OPTIMAL:
                reason = "restricted_optimum"
            elif status == cp_model.INFEASIBLE:
                raise RuntimeError("Strip model unexpectedly infeasible despite unit-square filler")
            elif status == cp_model.MODEL_INVALID:
                raise RuntimeError("Invalid strip model: " + solver.response_stats())
    assert validate_partition(n, best_rects) == best
    exact = best == upper
    return {
        "n": n, "solver": "strips", "status": "OPTIMAL" if exact else
        ("LOWER_BOUND" if reason == "restricted_optimum" else "TIME_LIMIT"),
        "k": best if exact else None, "lower_bound": best, "upper_bound": upper,
        "initial_lower_bound": initial, "area_upper_bound": upper,
        "termination": reason, "restricted_status": strip_status,
        "restricted_lower_bound": strip_lower,
        "restricted_upper_bound": strip_upper, "max_parts": max_parts,
        "max_height": min(n, max_height or n), "workers": workers, "seed": seed,
        "strip_configurations": config_count, "nodes": branches,
        "conflicts": conflicts, "elapsed_seconds": perf_counter() - started,
        "model_build_seconds": model_build_seconds,
        "solve_call_seconds": solve_call_seconds, "solver_wall_seconds": solver_wall_seconds,
        "time_limit": time_limit,
        "distinct_areas": sorted({r.area for r in best_rects}),
        "rectangles": [asdict(r) for r in best_rects],
    }
