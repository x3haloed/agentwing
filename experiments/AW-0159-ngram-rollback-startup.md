# AW-0159 — bounded ngram rollback allocation admission

Hypothesis: isolated AW158 server allocates three recurrent rollback slots with
full vision and compressed KV under existing pressure/swap gates. Primary
metric: allocation, health, clean exit and host gates; no performance claim.

Frozen prelaunch plan includes whole parent runtime/build/model profile, native
thinking/medium sampler,16K context, vision1024, source/patch/library/server and
harness hashes, M1/16GB/macOS27.0.1/internalSSD/thermal evidence. Verify parent
weights and frozen P1 inputs plus candidate artifacts before launch. One model
owner, loopback, startup60s watchdog, pressure<4 and growth<=1024MiB. Fresh server,
uncontrolled OS page cache. Command: python3 scripts/run_bonsai_rollback_startup.py.

Actual lookup2/proposal3 ngram-simple allocates n_rs_seq3; RS598.50MiB
(R22.50+S576). Both logged contexts have3slots. KV408MiB/16384cells with
Kq8_0272 and VTurbo4136. Vision model loaded; health/propsHTTP200. Server clean
exit0, pressure peak1, swap baseline1172.12MiB and growth0. No generation requests
or tools. Source reports bounded removal based on slot allocation; this is NOT a
forced-rejection fidelity test. Independent replay verifies all raw hashes,
harness pin, KV allocator line and captured pressure samples.

Retain startup/admission survivor. Forced-rejection restored logits, sampler
state, actual batched PTQ work, memory during generation and complete endpoint
cost remain unproven. No defaults/P1/task/scoring change or promotion.
External frozen plan/logs/host samples: /Users/chad/Models/agentwing/evidence/AW-0159.
Receipt: evidence/AW-0159-ngram-rollback-startup.json.
