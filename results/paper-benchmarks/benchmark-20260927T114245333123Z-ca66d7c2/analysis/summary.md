# Benchmark summary

Times are medians over completed repetitions. Node counts are meaningful only
within one solver family. A timeout is not evidence of infeasibility.

## exact

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-hints-pilot | 4 | 1/1 | 1 | 5–5 | 0 | 0.575 | 0.002 | 0.008 | 181 |
| skyline-bounded-pilot | 4 | 1/1 | 1 | 5–5 | 0 | 0.121 | — | — | 33 |
| skyline-bounded-pilot | 5 | 1/1 | 1 | 6–6 | 0 | 0.141 | — | — | 113 |

## construction

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| strips-pilot | 5 | 1/1 | 1 | 6–6 | 0 | 0.636 | 0.001 | 0.006 | 84 |

## ablation

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-no-hints-pilot | 4 | 1/1 | 1 | 5–5 | 0 | 0.642 | 0.001 | 0.008 | 184 |
| skyline-unbounded-pilot | 4 | 1/1 | 1 | 5–5 | 0 | 0.371 | — | — | 161863 |
| skyline-unbounded-pilot | 5 | 1/1 | 0 | 5–6 | 1 | 1.150 | — | — | 575287 |

