# Benchmark summary

Times are medians over completed repetitions. Node counts are meaningful only
within one solver family. A timeout is not evidence of infeasibility.

## exact

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-hints | 4 | 3/3 | 3 | 5–5 | 0 | 0.602 | 0.002 | 0.011 | 181 |
| cpsat-baseline-hints | 5 | 3/3 | 3 | 6–6 | 0 | 0.856 | 0.005 | 0.015 | 421 |
| cpsat-baseline-hints | 6 | 3/3 | 3 | 7–7 | 0 | 0.641 | 0.008 | 0.040 | 6000 |
| cpsat-baseline-hints | 9 | 3/3 | 3 | 12–12 | 0 | 1.064 | 0.044 | 0.389 | 35211 |
| cpsat-baseline-hints | 10 | 3/3 | 3 | 13–13 | 0 | 1.672 | 0.071 | 0.941 | 84504 |
| cpsat-baseline-hints | 11 | 3/3 | 3 | 14–14 | 0 | 2.342 | 0.094 | 1.454 | 107227 |
| cpsat-baseline-hints | 12 | 3/3 | 3 | 16–16 | 0 | 4.087 | 0.142 | 3.197 | 290431 |
| cpsat-baseline-hints | 14 | 3/3 | 3 | 19–19 | 0 | 6.712 | 0.239 | 5.817 | 389633 |
| cpsat-baseline-hints | 15 | 3/3 | 3 | 20–20 | 0 | 7.888 | 0.318 | 7.019 | 519688 |
| cpsat-baseline-hints | 16 | 3/3 | 1 | 21–21 | 1 | 10.562 | 0.424 | 9.497 | 8750 |
| cpsat-baseline-hints | 17 | 3/3 | 0 | 21–23 | 2 | 11.836 | 0.660 | 10.655 | 2196 |
| cpsat-baseline-hints | 18 | 3/3 | 0 | 22–24 | 2 | 12.023 | 0.769 | 10.097 | 0 |
| cpsat-baseline-hints | 19 | 3/3 | 0 | 25–26 | 1 | 11.329 | 1.124 | 9.412 | 0 |
| cpsat-baseline-hints | 20 | 3/3 | 0 | 26–27 | 1 | 12.053 | 1.246 | 10.150 | 0 |
| skyline-bounded | 4 | 3/3 | 3 | 5–5 | 0 | 0.132 | — | — | 33 |
| skyline-bounded | 5 | 3/3 | 3 | 6–6 | 0 | 0.171 | — | — | 113 |
| skyline-bounded | 6 | 3/3 | 3 | 7–7 | 0 | 0.150 | — | — | 273 |
| skyline-bounded | 9 | 3/3 | 3 | 12–12 | 0 | 0.245 | — | — | 52430 |
| skyline-bounded | 10 | 3/3 | 3 | 13–13 | 0 | 1.208 | — | — | 547825 |
| skyline-bounded | 11 | 3/3 | 3 | 14–14 | 0 | 2.551 | — | — | 1048527 |
| skyline-bounded | 12 | 3/3 | 0 | 15–16 | 1 | 10.137 | — | — | 4555908 |
| skyline-bounded | 14 | 3/3 | 0 | 18–19 | 1 | 10.149 | — | — | 4370866 |
| skyline-bounded | 15 | 3/3 | 0 | 19–20 | 1 | 10.154 | — | — | 4353481 |
| skyline-bounded | 16 | 3/3 | 0 | 20–21 | 1 | 10.164 | — | — | 4229975 |
| skyline-bounded | 17 | 3/3 | 0 | 21–23 | 2 | 10.133 | — | — | 3670653 |
| skyline-bounded | 18 | 3/3 | 0 | 22–24 | 2 | 10.131 | — | — | 3948077 |
| skyline-bounded | 19 | 3/3 | 0 | 25–26 | 1 | 10.176 | — | — | 3524659 |
| skyline-bounded | 20 | 3/3 | 0 | 26–27 | 1 | 10.131 | — | — | 3780052 |

## construction

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-best-known-hard | 24 | 3/3 | 0 | 32–33 | 2 | 33.868 | 3.517 | 30.068 | 1374 |
| cpsat-best-known-hard | 27 | 3/3 | 0 | 35–37 | 2 | 37.960 | 6.290 | 31.024 | 0 |
| cpsat-best-known-hard | 30 | 3/3 | 0 | 39–41 | 2 | 44.457 | 10.998 | 32.085 | 0 |
| cpsat-best-known-hard | 33 | 3/3 | 3 | 45–45 | 0 | 0.136 | 0.000 | 0.000 | 0 |
| strips-four-hard | 24 | 3/3 | 0 | 31–33 | 2 | 30.339 | 0.020 | 29.561 | 997330 |
| strips-four-hard | 27 | 3/3 | 0 | 35–37 | 2 | 30.210 | 0.032 | 29.492 | 1151404 |
| strips-four-hard | 30 | 3/3 | 0 | 39–41 | 2 | 30.201 | 0.041 | 29.512 | 1401362 |
| strips-four-hard | 33 | 3/3 | 0 | 44–45 | 1 | 30.182 | 0.049 | 29.565 | 1308638 |
| strips-four-hard | 36 | 3/3 | 0 | 47–49 | 2 | 30.221 | 0.065 | 29.484 | 1219871 |
| strips-four-hard | 40 | 3/3 | 0 | 53–55 | 2 | 30.792 | 0.088 | 29.461 | 1293088 |

## ablation

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-no-hints | 16 | 3/3 | 3 | 21–21 | 0 | 10.014 | 0.297 | 9.098 | 753548 |
| cpsat-baseline-no-hints | 17 | 3/3 | 0 | 21–23 | 2 | 11.186 | 0.427 | 9.912 | 2196 |
| cpsat-baseline-no-hints | 18 | 3/3 | 0 | 22–24 | 2 | 11.975 | 0.538 | 10.888 | 0 |
| cpsat-baseline-no-hints | 19 | 3/3 | 0 | 25–26 | 1 | 11.709 | 0.761 | 10.147 | 1968 |
| cpsat-eleven-eighths-hints | 16 | 3/3 | 3 | 21–21 | 0 | 0.134 | 0.000 | 0.000 | 0 |
| cpsat-eleven-eighths-hints | 17 | 3/3 | 3 | 23–23 | 0 | 0.142 | 0.000 | 0.000 | 0 |
| cpsat-eleven-eighths-hints | 18 | 3/3 | 0 | 23–24 | 1 | 11.462 | 0.732 | 9.996 | 0 |
| cpsat-eleven-eighths-hints | 19 | 3/3 | 0 | 23–26 | 3 | 11.478 | 1.018 | 9.647 | 0 |
| cpsat-eleven-eighths-no-hints | 16 | 3/3 | 3 | 21–21 | 0 | 0.137 | 0.000 | 0.000 | 0 |
| cpsat-eleven-eighths-no-hints | 17 | 3/3 | 3 | 23–23 | 0 | 0.142 | 0.000 | 0.000 | 0 |
| cpsat-eleven-eighths-no-hints | 18 | 3/3 | 0 | 23–24 | 1 | 11.398 | 0.519 | 10.087 | 0 |
| cpsat-eleven-eighths-no-hints | 19 | 3/3 | 0 | 23–26 | 3 | 11.701 | 0.757 | 10.076 | 1968 |
| skyline-unbounded | 4 | 3/3 | 3 | 5–5 | 0 | 0.441 | — | — | 161863 |
| skyline-unbounded | 5 | 3/3 | 3 | 6–6 | 0 | 10.176 | — | — | 4672638 |
| skyline-unbounded | 6 | 3/3 | 0 | 6–7 | 1 | 10.157 | — | — | 4181802 |

