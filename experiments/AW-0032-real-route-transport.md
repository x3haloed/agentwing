# AW-0032 — Read concurrency on real expert misses

Hypothesis: limiting concurrent reads to four within each already-known batch
reduces transport-plus-consumption wall time relative to dispatching every miss
concurrently. Primary metric: total replay wall seconds, interleaved all/4/all/4/all.
No future routing is used to overlap batches. Same 1,000 batches and 9,249 misses
from AW-0031, all 40 packed layers, unchanged bytes. GPU scan consumes every byte;
per-batch scan outputs must match across arms. This is transport evidence, not
model numerics, inference latency or autonomous utility evidence.

Standalone Objective-C/Metal probe; original P1 untouched. Buffers reused across
batches, sized to largest recorded miss batch. No model loaded, no cache flush,
no forced file-cache policy, no additional expert cache. Disk counters sampled
at exact arm boundaries via proc_pid_rusage, host pressure <4 and swap growth
<=1 GiB; 300 second supervised deadline. Preserve failed trials. Existing OS
cache state uncontrolled; bracket controls and report disk bytes per arm.

Input: AW-0031/20260905T183732Z/T1/experts.jsonl, hash checked against its receipt.
Model: Qwen3.6-35B-A3B 8-bit qpack, revision
720a56073578a3b42b5c40410baf90281bab9c0f. Runtime routing base 459b201,
instrumentation 406f992. Same 29-token prompt and 24 greedy decode steps as
AW-0031; no Pi harness or agent benchmark executed. Native compiler, OS,
hardware, storage and source/binary/input hashes recorded with raw results.

## Results and disposition

Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0032/20260905T184847Z`.
Receipt SHA256: `220c53e42f8ac9dcf26b799ad0e7d53a2dcec9f4949033bcfaed131fc553e015`.
Compact results: `evidence/AW-0032-transport-results.json`. All archived hashes
verified; native build succeeded without diagnostics; five arms exited cleanly.

| Arm | Concurrent reads | Wall seconds | Read seconds | GPU wait seconds | Process disk GiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 | Full batch | 7.247 | 5.654 | 1.527 | 16.509 |
| A1 | 4 | 7.324 | 5.748 | 1.528 | 16.283 |
| C2 | Full batch | 7.171 | 5.595 | 1.527 | 16.321 |
| A2 | 4 | 7.350 | 5.756 | 1.547 | 16.284 |
| C3 | Full batch | 7.157 | 5.578 | 1.532 | 16.280 |

Both candidate arms lose to their bracketing control means: 1.60% and 2.59%
longer wall time. This small sample does not establish a universal slowdown,
but provides no reason to replace full-batch dispatch with a four-read cap.
Read time increases while GPU consumption time remains similar. Every arm reads
28.790 GiB logically. Every GPU scan fingerprint matches the first arm for every
batch. Scan consumes all words, but fingerprints are not proof of byte identity
or a model numerical test. No inference/agent speedup is claimed.

Host pressure remained 1 with zero sampled swap growth. Staging buffers total
441,188,352 bytes, at most 132 experts. Peak process footprint was approximately
551 MiB. No model runs concurrently. P1 preflight passes after cleanup.

Limits: this replay retains staging buffers, not the actual LFU cache contents;
it excludes model weights, KV and real matrix multiplication. First arm creates
reference scan output storage (about 118 MB), later arms compare against it.
That allocation and OS file-cache warming can bias the first control. Later
controls still beat both candidates. The lower process disk demand than AW-0031
(~16 versus ~21–22 GiB) is evidence that memory residency/compute differences
matter; do not substitute replay timings for actual inference timings. Process
disk counters include OS attribution rather than direct device measurement.
No cross-batch overlap was attempted because future routes depend on compute.

Disposition: **rejected** four-read cap on this trace; retain full-batch control.
The real-route replay remains a diagnostic tool for further transport/layout
experiments. Reducing necessary bytes or identifying actual dependency-safe
read/compute overlap remains unresolved. P1 and agent capability policy unchanged.

Reproduce: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_real_route_transport.py`.
This verifies its input trace hash, builds the standalone probe, supervises the
five-arm run and archives source, binary, environment, logs and raw hashes.
