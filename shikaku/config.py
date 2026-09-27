"""Explicit, validated solver settings shared by CLI and experiments."""

import json
from pathlib import Path


def load_config(path: Path | None = None) -> dict:
    config = ({"solver": "skyline", "options": {"prune": True}}
              if path is None else json.loads(path.read_text(encoding="utf-8")))
    return validate_config(config)


def validate_config(config: dict) -> dict:
    """Validate and return an in-memory solver configuration."""
    if (not isinstance(config, dict) or set(config) != {"solver", "options"}
            or not isinstance(config["options"], dict)):
        raise ValueError('expected solver and options fields')
    solver, options = config["solver"], config["options"]
    if solver == "skyline":
        if set(options) != {"prune"} or type(options["prune"]) is not bool:
            raise ValueError('skyline expects options={"prune": boolean}')
    elif solver == "cpsat":
        if set(options) - {"num_workers", "random_seed", "log_search_progress",
                           "seed_strategy", "use_hints"}:
            raise ValueError("unknown cpsat option")
        _integer_option(options, "num_workers", 1)
        _integer_option(options, "random_seed", 0)
        if type(options.get("log_search_progress", False)) is not bool:
            raise ValueError("log_search_progress must be boolean")
        if options.get("seed_strategy", "baseline") not in {
                "baseline", "eleven_eighths", "best_known"}:
            raise ValueError("unknown cpsat seed_strategy")
        if type(options.get("use_hints", True)) is not bool:
            raise ValueError("use_hints must be boolean")
    elif solver == "strips":
        if set(options) - {"max_parts", "max_height", "workers", "seed"}:
            raise ValueError("unknown strips option")
        for key in ("max_parts", "workers"):
            _integer_option(options, key, 1)
        _integer_option(options, "seed", 0)
        if options.get("max_height") is not None:
            _integer_option(options, "max_height", 1)
    else:
        raise ValueError(f"unknown solver: {solver}")
    return config


def _integer_option(options: dict, key: str, minimum: int) -> None:
    if key in options and (type(options[key]) is not int or options[key] < minimum):
        raise ValueError(f"{key} must be an integer >= {minimum}")
