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


## Runtime source reconstruction

Run `python3 scripts/verify_runtime_patch_series.py` to verify every archived
patch hash and apply the series from the pinned upstream revision in a
temporary Git index. The resulting tree must equal both the recorded runtime
commit tree and `swiftlet.source_tree` in `spec/dependencies.json`. The check
leaves the checkout, real index, and branch unchanged; Git may add reconstructed
objects to its object store. This verifies source identity only. Reproduction
also requires the pinned dependencies, model, build, protocol tests, and
endpoint measurements. The recorded successful check is in
`evidence/runtime-patch-reconstruction.json`.
