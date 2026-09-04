# AW-0020 — Installed alternative feasibility

## Status

Local availability screen complete; no alternative endpoint trial.

## Hypothesis

Another installed model/runtime combination can enter a bounded protocol and
pressure trial without downloading a new checkpoint or modifying another project.

## Primary metric and cheap falsifier

Availability of usable model payloads and an agent-serving runtime. Inspect the
known project checkpoint directories, common local model stores, Hugging Face
snapshot entries and command availability. Read filesystem metadata only while
AW-0019 is running; do not launch another model owner or hash large payloads.

## Results

At the recorded observation time on 2026-09-04:

- Agentwing contains its pinned Qwen3.6 qpack.
- Firewing and MiMo Prismwing checkpoint directories contain only `.DS_Store`.
  Their repository descriptions of installed checkpoints are stale relative
  to this filesystem observation; their historical runtime results remain
  separate evidence and are not imported into Agentwing scores.
- The two Hugging Face entries (Qwen3.8-Flash-Next and GLM-5.3-Flash) each contain
  only 40 bytes in one regular file, with no snapshot payload entries.
- Standard Ollama and LM Studio model locations are absent.
- `ollama`, `llama-server`, and `mlx_lm.server` are absent from the observed PATH.
  OpenCode is installed, but a harness alone does not supply model weights or
  an alternative inference runtime.
- Internal SSD free space was 304 GiB. No files were deleted.

## Evidence

`evidence/local-model-inventory.json` records paths, entry names, timestamp,
metadata sizes, and executable discovery. Commands used Python pathlib, stat,
shutil.which, and `df -h`; no network access or model execution.

## Confounders and deviations

This is a bounded inventory of known locations, not an exhaustive search of the
user's disk. No claim is made about undiscovered custom installations. Missing
commands on PATH do not establish global absence. Availability says nothing
about capability or performance of a model that could be acquired later.

## Conclusion and disposition

No already-installed alternative model/runtime pair was found that can enter
an immediate endpoint screen. Retain Qwen/Swiftlet for current measurements;
leave newly acquired alternatives unresolved rather than marking that family
exhausted. Do not import older projects' completion gates into this goal.
