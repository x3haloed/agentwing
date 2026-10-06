# AW-0063 — Bonsai local admission with Pi context headroom

## Status

Completed, 2026-10-05. Successor to failed AW-0062; no comparative speed claim.

## Hypothesis

An actual 8192-token server and matching Pi context declaration prevent Pi's fixed 4096-token reserve from reducing output to one token, allowing the identical local text, reversed-image, native-tool and sandboxed Pi fixtures to complete twice within host gates.

## Configuration identities / Fixed conditions

spec/bonsai-local.json and config/pi-bonsai-models.json pin model, runtime, harness, sampling and context. Same PTQ1_0 + Q8 projector, Prism Metal release and Pi 0.84.4 as AW-0062. M1 Macmini9,1, 16 GB, macOS 27.0.1 (26A434), internal SSD, one slot, FP16 KV, 1024 image cap, medium reasoning. Same fixture tasks and verifiers, 1800 s per replicate (Pi subprocess 900 s). Loopback and existing sandbox boundary. No concurrent integrity reads or other model processes. Record ambient pressure, allocated swap, cache and thermal state; no fixed clean-state claim.

## Primary metric and acceptance rule

All four API checks and actual Pi read/write/verification pass in two sequential cold-server trials; critical pressure <4, peak swap growth <=1024 MiB each. This is functional admission only, not autonomous work-rate superiority.

## Cheap falsifier

Identical direct API smoke before the actual Pi loop. Reject corruption or host violation.

## Commands

PYTHONDONTWRITEBYTECODE=1 python3 scripts/probe_bonsai_local.py

## Additional managed-launcher check

After the two unchanged admission replicates, run the managed launcher with a
local image attachment and an empty workspace. Ask it to write the two image
colors in left/right order to colors.txt. Independently compare against the
fixture pixels. This separately checks launcher ownership and Pi image transport;
it is not an extra favorable task in a benchmark score.

## Results / Evidence / Conclusion

Both unchanged admission replicates passed all four API checks and the actual Pi task. Replicate 0: 188.659 seconds, pressure peak 2, swap growth 0 MiB, four valid Pi calls (two productive, two redundant). Replicate 1: 173.253 seconds, pressure peak 2, swap growth 0 MiB, three valid Pi calls (two productive, one redundant). Native API selection contributed one additional productive call per replicate. Zero malformed, denied or failed calls. Independent hash, image pixel, tool-ID association, transcript and byte-exact output audit passes in evidence/AW-0063-admission-audit.json.

Managed launcher with actual local image attachment passed: colors.txt contained blue,red, matching the reversed PNG fixture. One productive valid bash call; zero redundant, malformed, denied or failed calls. Pressure peak 1, zero swap growth. Summary and raw-evidence hash in evidence/AW-0063-managed-vision.json. Inherited process cleanup, timeout and host-stop tests: 6 passed. Runtime device discovery reports MTL0 Apple M1 and Accelerate; archive SHA-256 matches GitHub's published digest, and both weights match pinned HF LFS hashes.

Raw evidence remains under /Users/chad/Models/agentwing/evidence/AW-0062 with run-specific identities and hashes; corrected manifest records AW-0063. No trace deletion.

## Disposition

Promoted as the user-directed local operational default for text, vision and Pi tool loops at 8192 context and 1024 image tokens. Historical P1 retained as a control. No autonomous work-rate superiority, large-context admission or uncapped-image quality claim; those remain unresolved.
