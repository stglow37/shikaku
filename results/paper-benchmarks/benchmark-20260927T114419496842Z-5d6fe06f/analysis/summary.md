# Benchmark summary

Times are medians over completed repetitions. Node counts are meaningful only
within one solver family. A timeout is not evidence of infeasibility.

## exact

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-hints | 4 | 3/3 | 3 | 5–5 | 0 | 0.569 | 0.002 | 0.009 | 181 |
| cpsat-baseline-hints | 5 | 3/3 | 3 | 6–6 | 0 | 0.594 | 0.004 | 0.015 | 421 |
| cpsat-baseline-hints | 6 | 3/3 | 3 | 7–7 | 0 | 0.635 | 0.008 | 0.039 | 6000 |
| cpsat-baseline-hints | 9 | 3/3 | 3 | 12–12 | 0 | 0.989 | 0.043 | 0.368 | 35211 |
| cpsat-baseline-hints | 10 | 3/3 | 3 | 13–13 | 0 | 1.611 | 0.072 | 0.918 | 84504 |
| cpsat-baseline-hints | 11 | 3/3 | 3 | 14–14 | 0 | 2.194 | 0.101 | 1.417 | 107227 |
| cpsat-baseline-hints | 12 | 3/3 | 3 | 16–16 | 0 | 3.664 | 0.124 | 2.943 | 290431 |
| cpsat-baseline-hints | 14 | 3/3 | 3 | 19–19 | 0 | 6.319 | 0.235 | 5.520 | 389633 |
| cpsat-baseline-hints | 15 | 3/3 | 3 | 20–20 | 0 | 7.741 | 0.307 | 6.860 | 519688 |
| cpsat-baseline-hints | 16 | 3/3 | 3 | 21–21 | 0 | 10.069 | 0.417 | 9.074 | 740389 |
| cpsat-baseline-hints | 17 | 3/3 | 0 | 21–23 | 2 | 10.994 | 0.545 | 9.839 | 2196 |
| cpsat-baseline-hints | 18 | 3/3 | 0 | 22–24 | 2 | 11.011 | 0.722 | 9.715 | 0 |
| cpsat-baseline-hints | 19 | 3/3 | 0 | 25–26 | 1 | 12.566 | 0.965 | 10.971 | 1968 |
| cpsat-baseline-hints | 20 | 3/3 | 0 | 26–27 | 1 | 11.961 | 1.231 | 10.128 | 0 |
| skyline-bounded | 4 | 3/3 | 3 | 5–5 | 0 | 0.139 | — | — | 33 |
| skyline-bounded | 5 | 3/3 | 3 | 6–6 | 0 | 0.141 | — | — | 113 |
| skyline-bounded | 6 | 3/3 | 3 | 7–7 | 0 | 0.134 | — | — | 273 |
| skyline-bounded | 9 | 3/3 | 3 | 12–12 | 0 | 0.242 | — | — | 52430 |
| skyline-bounded | 10 | 3/3 | 3 | 13–13 | 0 | 1.206 | — | — | 547825 |
| skyline-bounded | 11 | 3/3 | 3 | 14–14 | 0 | 2.361 | — | — | 1048527 |
| skyline-bounded | 12 | 3/3 | 0 | 15–16 | 1 | 10.134 | — | — | 4794406 |
| skyline-bounded | 14 | 3/3 | 0 | 18–19 | 1 | 10.131 | — | — | 4612328 |
| skyline-bounded | 15 | 3/3 | 0 | 19–20 | 1 | 10.128 | — | — | 4514702 |
| skyline-bounded | 16 | 3/3 | 0 | 20–21 | 1 | 10.130 | — | — | 4480387 |
| skyline-bounded | 17 | 3/3 | 0 | 21–23 | 2 | 10.129 | — | — | 4295892 |
| skyline-bounded | 18 | 3/3 | 0 | 22–24 | 2 | 10.134 | — | — | 4161992 |
| skyline-bounded | 19 | 3/3 | 0 | 25–26 | 1 | 10.134 | — | — | 4066023 |
| skyline-bounded | 20 | 3/3 | 0 | 26–27 | 1 | 10.136 | — | — | 4030592 |

## construction

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-best-known-hard | 24 | 3/3 | 0 | 32–33 | 1 | 34.249 | 3.346 | 30.065 | 903457 |
| cpsat-best-known-hard | 27 | 3/3 | 0 | 35–37 | 2 | 36.971 | 6.060 | 29.836 | 0 |
| cpsat-best-known-hard | 30 | 3/3 | 0 | 39–41 | 2 | 42.621 | 10.808 | 30.999 | 0 |
| cpsat-best-known-hard | 33 | 3/3 | 3 | 45–45 | 0 | 52.756 | 18.219 | 33.521 | 0 |
| strips-four-hard | 24 | 3/3 | 0 | 31–33 | 2 | 30.201 | 0.022 | 29.492 | 1036019 |
| strips-four-hard | 27 | 3/3 | 0 | 35–37 | 2 | 30.193 | 0.035 | 29.574 | 1269177 |
| strips-four-hard | 30 | 3/3 | 0 | 40–41 | 1 | 30.178 | 0.040 | 29.576 | 1519601 |
| strips-four-hard | 33 | 3/3 | 0 | 44–45 | 1 | 30.187 | 0.048 | 29.564 | 1310696 |
| strips-four-hard | 36 | 3/3 | 0 | 47–49 | 2 | 30.205 | 0.061 | 29.526 | 1228326 |
| strips-four-hard | 40 | 3/3 | 0 | 53–55 | 2 | 30.196 | 0.083 | 29.471 | 1267265 |

## ablation

| suite | n | completed | exact | best bounds | gap | process s | build s | solve s | nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpsat-baseline-no-hints | 16 | 3/3 | 3 | 21–21 | 0 | 9.652 | 0.314 | 8.712 | 753548 |
| cpsat-baseline-no-hints | 17 | 3/3 | 0 | 21–23 | 2 | 10.297 | 0.391 | 9.311 | 2196 |
| cpsat-baseline-no-hints | 18 | 3/3 | 0 | 22–24 | 2 | 12.090 | 0.511 | 11.011 | 2084 |
| cpsat-baseline-no-hints | 19 | 3/3 | 0 | 25–26 | 1 | 11.522 | 0.789 | 10.059 | 1968 |
| cpsat-eleven-eighths-hints | 16 | 3/3 | 3 | 21–21 | 0 | 8.205 | 0.411 | 7.199 | 2388 |
| cpsat-eleven-eighths-hints | 17 | 3/3 | 3 | 23–23 | 0 | 10.925 | 0.551 | 9.764 | 2196 |
| cpsat-eleven-eighths-hints | 18 | 3/3 | 0 | 23–24 | 1 | 11.107 | 0.735 | 9.779 | 0 |
| cpsat-eleven-eighths-hints | 19 | 3/3 | 0 | 23–26 | 3 | 12.660 | 0.976 | 11.025 | 1968 |
| cpsat-eleven-eighths-no-hints | 16 | 3/3 | 3 | 21–21 | 0 | 9.410 | 0.295 | 8.513 | 748967 |
| cpsat-eleven-eighths-no-hints | 17 | 3/3 | 3 | 23–23 | 0 | 10.193 | 0.390 | 9.255 | 2196 |
| cpsat-eleven-eighths-no-hints | 18 | 3/3 | 0 | 23–24 | 1 | 11.871 | 0.524 | 10.814 | 2084 |
| cpsat-eleven-eighths-no-hints | 19 | 3/3 | 0 | 23–26 | 3 | 11.227 | 0.684 | 9.939 | 1968 |
| skyline-unbounded | 4 | 3/3 | 3 | 5–5 | 0 | 0.423 | — | — | 161863 |
| skyline-unbounded | 5 | 3/3 | 3 | 6–6 | 0 | 10.137 | — | — | 5258586 |
| skyline-unbounded | 6 | 3/3 | 0 | 6–7 | 1 | 10.138 | — | — | 5142685 |
