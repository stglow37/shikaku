"""Run a solver with a shared command-line interface."""

import argparse
import json
from pathlib import Path

from .config import load_config
from .solvers.skyline import solve


def main():
    parser = argparse.ArgumentParser(description="Compute k(n) with verified bounds and witness.")
    parser.add_argument("n", type=int)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--no-prune", action="store_true", help="override config: full enumeration")
    parser.add_argument("--time-limit", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.no_prune:
            config["options"]["prune"] = False
        result = solve(args.n, **config["options"], time_limit=args.time_limit)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    result["configuration"] = config
    output = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
