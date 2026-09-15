"""Explicit, validated solver settings shared by CLI and experiments."""

import json
from pathlib import Path


def load_config(path: Path | None = None) -> dict:
    config = ({"solver": "skyline", "options": {"prune": True}}
              if path is None else json.loads(path.read_text(encoding="utf-8")))
    if (not isinstance(config, dict) or set(config) != {"solver", "options"}
            or config["solver"] != "skyline"
            or not isinstance(config["options"], dict)
            or set(config["options"]) != {"prune"}
            or type(config["options"]["prune"]) is not bool):
        raise ValueError('expected solver="skyline" and options={"prune": boolean}')
    return config
