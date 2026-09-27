"""Optional independent all-rectangle exact-cover model for OR-Tools CP-SAT."""

from dataclasses import asdict
from math import ceil, isfinite
from time import perf_counter

from ..bounds import area_upper_bound
from ..constructions import initial_partition
from ..improved_constructions import best_partition, partition_11_over_8
from ..model import Rect
from ..validation import validate_partition


def _load_ortools():
    # Baseline solvers and importing this module do not require OR-Tools.
    try:
        import ortools
        from ortools.sat.python import cp_model
    except ImportError as exc:
        raise ImportError(
            "CP-SAT requires optional dependencies; run "
            "python -m pip install -r requirements-cpsat.txt"
        ) from exc
    return ortools.__version__, cp_model


def seed_partition(n: int, strategy: str) -> list[Rect]:
    """Return the independently verified construction used to seed CP-SAT."""
    if strategy == "baseline":
        return initial_partition(n)
    if strategy == "eleven_eighths":
        if n < 16:
            raise ValueError("the eleven_eighths seed requires n >= 16")
        return partition_11_over_8(n)
    if strategy == "best_known":
        return best_partition(n)
    raise ValueError(
        "seed_strategy must be baseline, eleven_eighths, or best_known")


def solve(n: int, *, time_limit: float | None = None, num_workers: int = 1,
          random_seed: int = 0, log_search_progress: bool = False,
          seed_strategy: str = "baseline", use_hints: bool = True) -> dict:
    """Return a validated partition and certified interval containing k(n).

    time_limit applies to the CP-SAT solve call only. Model construction,
    dependency import, extraction and validation are outside that limit.
    An UNKNOWN response never supplies a witness or an objective bound here;
    the independently checked initial partition and area bound remain valid.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    if time_limit is not None and (
        isinstance(time_limit, bool) or not isinstance(time_limit, (int, float))
        or not isfinite(time_limit) or time_limit < 0
    ):
        raise ValueError("time_limit must be finite and non-negative")
    if type(num_workers) is not int or num_workers < 1:
        raise ValueError("num_workers must be a positive integer")
    if type(random_seed) is not int or not 0 <= random_seed <= 2**31 - 1:
        raise ValueError("random_seed must be an integer between 0 and 2**31-1")
    if type(log_search_progress) is not bool:
        raise ValueError("log_search_progress must be boolean")
    if type(use_hints) is not bool:
        raise ValueError("use_hints must be boolean")
    started = perf_counter()
    # Establish independent bounds before importing or constructing CP-SAT.
    best_rects = seed_partition(n, seed_strategy)
    initial_lower = best = validate_partition(n, best_rects)
    area_upper = area_upper_bound(n)
    witness_source = ("initial_construction" if seed_strategy == "baseline"
                      else f"{seed_strategy}_construction")
    if best == area_upper:
        elapsed = perf_counter() - started
        return {
            "n": n, "solver": "cpsat", "status": "OPTIMAL",
            "solver_status": "NOT_RUN", "k": best,
            "lower_bound": best, "upper_bound": best,
            "initial_lower_bound": initial_lower, "area_upper_bound": area_upper,
            "solver_objective": None, "solver_upper_bound": None,
            "termination": "certified_initial_bounds",
            "witness_source": witness_source,
            "nodes": 0, "branches": 0, "conflicts": 0,
            "rectangle_variables": 0, "area_variables": 0,
            "cell_rectangle_incidences": 0,
            "dependency_import_seconds": 0.0, "model_build_seconds": 0.0,
            "solve_call_seconds": 0.0, "solver_wall_seconds": 0.0,
            "elapsed_seconds": elapsed, "time_limit_seconds": time_limit,
            "ortools_version": None, "num_workers": num_workers,
            "random_seed": random_seed, "seed_strategy": seed_strategy,
            "use_hints": use_hints,
            "distinct_areas": sorted({rect.area for rect in best_rects}),
            "rectangles": [asdict(rect) for rect in best_rects],
        }

    version, cp_model = _load_ortools()
    imported = perf_counter()
    areas = sorted({height * width for height in range(1, n + 1)
                    for width in range(1, n + 1)})
    seed_rects = set(best_rects)
    seed_areas = {rect.area for rect in best_rects}

    model = cp_model.CpModel()
    rects = []
    selected = []
    by_cell = [[] for _ in range(n * n)]
    by_area = {area: [] for area in areas}
    incidences = 0
    for top in range(n):
        for bottom in range(top + 1, n + 1):
            for left in range(n):
                for right in range(left + 1, n + 1):
                    rect = Rect(top, left, bottom - top, right - left)
                    variable = model.new_bool_var(f"r_{top}_{left}_{bottom}_{right}")
                    rects.append(rect)
                    selected.append(variable)
                    by_area[rect.area].append(variable)
                    for row in range(top, bottom):
                        for col in range(left, right):
                            by_cell[row * n + col].append(variable)
                    incidences += rect.area
                    if use_hints:
                        model.add_hint(variable, int(rect in seed_rects))

    for covering in by_cell:
        model.add_exactly_one(covering)
    present = {}
    for area in areas:
        present[area] = model.new_bool_var(f"a_{area}")
        # Equivalence, not only y <= sum(x): a feasible incumbent's objective
        # already equals its actual distinct-area count, even before optimality.
        model.add_max_equality(present[area], by_area[area])
        if use_hints:
            model.add_hint(present[area], int(area in seed_areas))
    objective = sum(present.values())
    model.add(objective >= initial_lower)
    model.add(objective <= area_upper)
    model.add(sum(area * present[area] for area in areas) <= n * n)
    model.maximize(objective)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = num_workers
    solver.parameters.random_seed = random_seed
    solver.parameters.log_search_progress = log_search_progress
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = time_limit
    built = perf_counter()
    status = solver.solve(model)
    solved = perf_counter()
    solver_status = solver.status_name(status)
    if status == cp_model.MODEL_INVALID:
        raise RuntimeError(f"CP-SAT model invalid: {model.validate()}")
    if status == cp_model.INFEASIBLE:
        # The checked construction is a feasible model assignment. A contrary
        # response is a modelling/solver failure, never a mathematical result.
        raise RuntimeError("CP-SAT reported INFEASIBLE despite a verified seed")

    upper = area_upper
    solver_upper = solver_objective = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        candidate = [rect for rect, variable in zip(rects, selected)
                     if solver.value(variable)]
        score = validate_partition(n, candidate)
        solver_objective = solver.objective_value
        if abs(solver_objective - score) > 1e-6 or score < initial_lower:
            raise RuntimeError("CP-SAT objective disagrees with validated witness")
        best, best_rects = score, candidate
        witness_source = "cp_sat"
        raw_upper = solver.best_objective_bound
        if not isfinite(raw_upper) or raw_upper < best - 1e-6:
            raise RuntimeError("CP-SAT objective bound contradicts its witness")
        # Ceil is conservative for a floating-point upper bound. Do not round
        # down using a tolerance that could turn a bound into an overclaim.
        solver_upper = ceil(raw_upper)
        upper = min(area_upper, solver_upper)
        if status == cp_model.OPTIMAL:
            upper = best
    elif status != cp_model.UNKNOWN:
        raise RuntimeError(f"Unexpected CP-SAT status: {solver_status}")

    exact = best == upper
    if status == cp_model.OPTIMAL:
        termination = "cp_sat_optimal"
    elif exact:
        termination = "certified_bounds_meet"
    else:
        termination = "time_limit" if time_limit is not None else "solver_stopped"
    if validate_partition(n, best_rects) != best:
        raise RuntimeError("Returned partition failed validation")
    return {
        "n": n, "solver": "cpsat", "status": "OPTIMAL" if exact else "TIME_LIMIT"
        if time_limit is not None else solver_status,
        "solver_status": solver_status, "k": best if exact else None,
        "lower_bound": best, "upper_bound": upper,
        "initial_lower_bound": initial_lower, "area_upper_bound": area_upper,
        "solver_objective": solver_objective, "solver_upper_bound": solver_upper,
        "termination": termination, "witness_source": witness_source,
        "nodes": solver.num_branches, "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "rectangle_variables": len(rects), "area_variables": len(areas),
        "cell_rectangle_incidences": incidences,
        "dependency_import_seconds": imported - started,
        "model_build_seconds": built - imported,
        "solve_call_seconds": solved - built,
        "solver_wall_seconds": solver.wall_time,
        "elapsed_seconds": perf_counter() - started,
        "time_limit_seconds": time_limit, "ortools_version": version,
        "num_workers": num_workers, "random_seed": random_seed,
        "seed_strategy": seed_strategy, "use_hints": use_hints,
        "distinct_areas": sorted({rect.area for rect in best_rects}),
        "rectangles": [asdict(rect) for rect in best_rects],
    }
