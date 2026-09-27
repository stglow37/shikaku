"""Render dependency-free SVG figures from benchmark analysis summary.json."""

import argparse
import html
import json
from pathlib import Path


COLORS = ["#2563eb", "#dc2626", "#059669", "#7c3aed"]


def _panel(rows, suites, *, x0, y0, width, height, value_key, title, y_label):
    selected = [row for row in rows if row["suite"] in suites
                and row.get(value_key) is not None]
    xs = sorted({row["n"] for row in selected})
    values = [row[value_key] for row in selected]
    if not xs or not values:
        return ""
    x_min, x_max = min(xs), max(xs)
    y_min = 0
    y_max = max(values) or 1
    plot_left, plot_top = x0 + 55, y0 + 35
    plot_width, plot_height = width - 75, height - 85

    def sx(value):
        return plot_left + (value - x_min) * plot_width / max(1, x_max - x_min)

    def sy(value):
        return plot_top + plot_height - (value - y_min) * plot_height / max(1, y_max - y_min)

    output = [
        f'<text x="{x0 + width/2}" y="{y0 + 20}" text-anchor="middle" '
        f'font-size="16" font-weight="bold">{html.escape(title)}</text>',
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" '
        f'y2="{plot_top + plot_height}" stroke="#475569"/>',
        f'<line x1="{plot_left}" y1="{plot_top + plot_height}" '
        f'x2="{plot_left + plot_width}" y2="{plot_top + plot_height}" stroke="#475569"/>',
        f'<text x="{x0 + 13}" y="{plot_top + plot_height/2}" '
        f'transform="rotate(-90 {x0 + 13} {plot_top + plot_height/2})" '
        f'text-anchor="middle" font-size="12">{html.escape(y_label)}</text>',
        f'<text x="{plot_left + plot_width/2}" y="{y0 + height - 8}" '
        f'text-anchor="middle" font-size="12">n</text>',
    ]
    for tick in range(5):
        value = y_max * tick / 4
        y = sy(value)
        output.extend([
            f'<line x1="{plot_left}" y1="{y:.2f}" x2="{plot_left + plot_width}" '
            f'y2="{y:.2f}" stroke="#e2e8f0"/>',
            f'<text x="{plot_left - 7}" y="{y + 4:.2f}" text-anchor="end" '
            f'font-size="10">{value:.1f}</text>',
        ])
    for value in xs:
        x = sx(value)
        output.append(
            f'<text x="{x:.2f}" y="{plot_top + plot_height + 17}" '
            f'text-anchor="middle" font-size="10">{value}</text>')
    for index, suite in enumerate(suites):
        color = COLORS[index % len(COLORS)]
        series = sorted((row for row in selected if row["suite"] == suite),
                        key=lambda row: row["n"])
        if not series:
            continue
        points = " ".join(f"{sx(row['n']):.2f},{sy(row[value_key]):.2f}"
                          for row in series)
        output.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="2.5"/>')
        for row in series:
            output.append(
                f'<circle cx="{sx(row["n"]):.2f}" cy="{sy(row[value_key]):.2f}" '
                f'r="3.5" fill="{color}"/>')
        legend_x = plot_left + 8 + index * (plot_width / max(1, len(suites)))
        output.extend([
            f'<line x1="{legend_x}" y1="{plot_top + 9}" x2="{legend_x + 20}" '
            f'y2="{plot_top + 9}" stroke="{color}" stroke-width="3"/>',
            f'<text x="{legend_x + 25}" y="{plot_top + 13}" font-size="10">'
            f'{html.escape(suite)}</text>',
        ])
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path, help="analysis/summary.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.summary.read_text(encoding="utf-8"))["rows"]
    output = args.output or args.summary.with_name("benchmark.svg")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" '
        'viewBox="0 0 1200 520">',
        '<rect width="1200" height="520" fill="white"/>',
        '<g font-family="Arial, sans-serif" fill="#0f172a">',
        _panel(rows, ["skyline-bounded", "cpsat-baseline-hints"],
               x0=10, y0=10, width=580, height=490, value_key="median_gap",
               title="Exact solvers under a 10 s solve budget", y_label="median gap"),
        _panel(rows, ["cpsat-best-known-hard", "strips-four-hard"],
               x0=610, y0=10, width=580, height=490, value_key="best_lower_bound",
               title="Hard instances under a 30 s solve budget", y_label="best lower bound"),
        '</g></svg>',
    ]
    output.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
