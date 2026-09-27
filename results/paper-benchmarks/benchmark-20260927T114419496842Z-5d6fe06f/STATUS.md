# Superseded diagnostic benchmark

This 159-trial run completed successfully and all witnesses were independently
validated. During analysis it exposed an implementation inefficiency: CP-SAT still
built and solved the full model when the selected construction already met the
independent area upper bound. Commit `f9ca7f4` fixes that issue.

Keep this run as the evidence that motivated the correction, but do not use its
timings for initially certified cases in the final comparison. A post-fix benchmark
using the same protocol is the paper-facing result.
