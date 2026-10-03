# Results Status

**No live model evaluation runs have been completed for this research release.**

`python pilot.py --provider fixture` runs a deterministic pipeline check that returns the written answer key. It exercises prompt construction, grading, and report output only. Those deliberately correct fixtures are simulated software checks and provide no evidence about language-model performance. Local reports under `results/runs/` are excluded from Git by default.

The local fixture check completed 36 simulated trials across 12 tasks and three conditions. The report correctly labels itself as a synthetic pipeline check and contains no model-performance metrics.

The included public task set is exploratory and unheld. It cannot support confirmatory or population-wide conclusions. Live reports from the OpenAI provider should retain their model name, usage records, individual trials, and uncertainty intervals.

Future result releases must include:

- Frozen protocol and task/skill/grader hashes.
- Exact model and harness settings.
- All assigned trials, including errors and timeouts.
- Raw trajectories with necessary privacy redaction documented.
- Independent outcome checks and unsupported-claim annotations.
- Analysis instructions, uncertainty intervals, and beneficial, harmful, or inconclusive effects.
- Total usage and cost accounting.

Never merge fixture rows with API-provider rows in one performance summary. Keep any later simulated fixtures in a separately labeled directory. Never silently fall back from an unavailable live provider to a mock and publish the output as an empirical run.
