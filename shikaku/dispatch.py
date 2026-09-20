"""Lazy solver dispatch keeps the baseline free of optional dependencies."""


def solve_configured(n: int, config: dict, *, time_limit: float | None = None) -> dict:
    if config["solver"] == "skyline":
        from .solvers.skyline import solve
    elif config["solver"] == "cpsat":
        from .solvers.cpsat import solve
    elif config["solver"] == "strips":
        from .solvers.strips import solve
    else:
        raise ValueError(f"unknown solver: {config['solver']}")
    return solve(n, **config["options"], time_limit=time_limit)
