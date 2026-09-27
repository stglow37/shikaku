"""Render standalone figures from the validated research summary (matplotlib)."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from shikaku.improved_constructions import partition_11_over_8
from shikaku.model import Rect
from shikaku.validation import validate_partition


def plot_partition(ax, n, rects, title, groups=False):
    count = validate_partition(n, rects)
    cmap = plt.get_cmap("Pastel1")
    for rect in rects:
        group = (0 if rect.row < n / 4 else 1 if rect.row < 5 * n / 16
                 else 2 if rect.row < 13 * n / 16 else 3) if groups else rect.area % 9
        ax.add_patch(Rectangle((rect.col, rect.row), rect.width, rect.height,
                              facecolor=cmap(group), edgecolor="#25334a", linewidth=0.65))
        ax.text(rect.col + rect.width / 2, rect.row + rect.height / 2, str(rect.area),
                ha="center", va="center", fontsize=8 if n <= 20 else 6, color="#162033")
    ax.set(xlim=(0, n), ylim=(n, 0), aspect="equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{title}\n{n} x {n}: {count} distinct areas", fontsize=13, pad=12)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    destination = args.summary.parent
    by_n = {r["n"]: r for r in data["results"]}
    fig, axs = plt.subplots(1, 2, figsize=(13, 7), layout="constrained")
    plot_partition(axs[0], 16, partition_11_over_8(16), "Explicit 11/8 construction", True)
    plot_partition(axs[1], 20, [Rect(**r) for r in by_n[20]["rectangles"]],
                   "Certified optimal partition")
    fig.suptitle("Shikaku research | numbers show rectangle areas", fontsize=16)
    for ext in ("png", "svg"):
        fig.savefig(destination / f"partitions.{ext}", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 5.5), layout="constrained")
    rows = data["results"]
    ax.plot([r["n"] for r in rows], [r["upper_bound"] for r in rows], color="#26344b",
            linewidth=1.5, label="Certified area upper bound U(n)")
    ax.plot([r["n"] for r in rows], [r["classical_lower"] for r in rows], "--",
            color="#c17c34", label="Original construction")
    ax.scatter([r["n"] for r in rows], [r["lower_bound"] for r in rows],
               color="#087c84", s=24, zorder=3, label="Best verified witness")
    ax.set(xlabel="Square side length n", ylabel="Number of distinct areas",
           title="Computed bounds: a dot on the upper line certifies the exact value")
    ax.grid(alpha=0.18)
    ax.legend()
    for ext in ("png", "svg"):
        fig.savefig(destination / f"bounds.{ext}", dpi=180)
    plt.close(fig)
    print(destination)


if __name__ == "__main__":
    main()
