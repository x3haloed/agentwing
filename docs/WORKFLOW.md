# Workflow

## Before an experiment

1. Read `TARGET.md`, `RED_LINES.md`, and `LEARNINGS.md`.
2. Copy `experiments/TEMPLATE.md` to the next `AW-NNNN` record.
3. State one falsifiable hypothesis and one primary metric.
4. Pin all model, runtime, harness, adapter, skill, task, and verifier revisions.
5. Declare storage, cache, context, sampling, permissions, and thermal state.
6. Run the cheapest integrity or pressure falsifier first.

## During an experiment

1. Capture commands and exit statuses.
2. Write large traces outside Git and hash them.
3. Sample host pressure and swap throughout the run.
4. Preserve failed and timed-out trials.
5. Stop on a red-line violation and record the stop as a result.

## After an experiment

1. Compute the predeclared primary metric.
2. Separate endpoint results from diagnostics.
3. State uncertainty, confounders, and protocol deviations.
4. Assign one disposition: promoted, retained, rejected, superseded, or
   unresolved.
5. Update `LEARNINGS.md` and machine-readable specs only when evidence warrants
   a belief change.

