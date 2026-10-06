# AW-0062 — Bonsai 2 local multimodal migration

## Status

Completed negative initial admission, 2026-10-05.

## Hypothesis

Bonsai 2 27B PTQ1_0 with Prism llama.cpp Metal and Q8 vision projector can complete text, image, and native tool-continuation checks on the 16 GB M1 without violating host gates.

## Configuration identities

Candidate: spec/bonsai-local.json. Historical Swiftlet configurations retained as controls; no speed comparison in this bring-up.

## Fixed conditions

Macmini9,1, M1 8-core, 16 GB; macOS 27.0.1 (26A434); internal SSD, initially 11 GiB available; user-authorized removal of two NoMachine session logs reclaimed 277.66 GiB, yielding 285 GiB free. No model or experiment artifacts were removed. Harness repository HEAD 0f3c16abd38c8c71a2642787e0da679f21f8d275 plus recorded working-tree changes. Pi 0.84.4 retained. Model Apache-2.0, exact revision/artifact hashes in candidate spec. Runtime prism-b10743-adfffbe, demo 74fab33d81d81a535525bd98c7a676b22d4dca46. One model process/slot; 4096 context, FP16 KV, 1024 vision token cap; sampling and medium reasoning in spec. Loopback only; acquisition needs network, inference fixtures use local inputs. Record ambient pressure, swap, thermal state, cache state, prompt and adapter hashes per run.

## Primary metric and acceptance rule

Three independently checked API functional gates plus an actual sandboxed Pi read/write/verify task (text correctness, local image correctness, native tool call plus associated result continuation), all passing with pressure below 4 and swap growth at most 1024 MiB. Replicate functional checks before operational promotion. This does not establish verified autonomous utility/hour superiority or full-context capability.

## Cheap falsifier

Verify runtime version and artifact integrity, then tiny text request under pressure monitoring. Stop before further tests on host violation or incoherent output.

## Commands / Results

All weight and runtime archive hashes matched. Direct API text, vision, native tool selection and tool-result continuation passed. Actual Pi task failed: it generated exactly one reasoning token, no calls, and no answer.txt. Inspection of pinned Pi 0.84.4 simple-options.js found a fixed 4096-token context safety reserve. Declaring 4096 total context clamps every response to max_tokens=1. This is a harness/runtime configuration mismatch, not evidence of weak model tool selection.

Run /Users/chad/Models/agentwing/evidence/AW-0062/20261006T020051Z-rep0: 96.80 seconds, pressure peak 2, swap growth peak 1010.25 MiB. Functional admission failed; second replicate was not attempted. Initial configuration preserved in evidence/AW-0062-initial-configuration.json. A concurrent setup integrity reread adds I/O/memory confounding; no performance claim is made. Runtime executable bytes remained pinned.

## Confounders and deviations

Ambient desktop apps consume unified memory. Compact context and image cap are explicit initial operating limits. Unrelated pre-existing repository edits preserved.

## Evidence

External evidence: /Users/chad/Models/agentwing/evidence/AW-0062. Hash summaries will be committed; weights stay outside Git.

## Conclusion / Disposition

Reject the exact 4096-context Pi admission arm. Test 8192 actual server and declared Pi context in AW-0063; preserve all other tasks and verifiers.
