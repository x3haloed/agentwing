# AW-0031 — Actual inference routing and disk-read trace

Contract: preserve model bytes, router selections, sampler and P1 behavior.
Instrument only an isolated Swiftlet checkout derived from 459b201; P1 runtime
and profile remain unchanged. No narrowing of tasks/tools or claimed agent
speedup. Observe actual per-token routing plus cache batch hits/misses,
selection/read durations and independent process-attributed disk reads.

Use opt-in bounded JSONL tracing (maximum 10000 events) and macOS
proc_pid_rusage sampling. Separate logical bytes requested by pread from disk
read counters; page-cache hits can make these very different. OS-attributed
process disk reads include other files and may not equal raw SSD media traffic.
CLI component scope, same short coding prompt/greedy 24 tokens as AW-0029,
trace-off/on/off on the same isolated executable to bracket tracing overhead.
Require matching output and identical aggregate hit/miss counts; do not infer
broader capability from a truncated diagnostic. Host pressure < 4, swap growth
<= 1 GiB, one model owner, 180-second deadline per run. Preserve build and all raw data.

## Build and provenance

Isolated checkout:
`/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0031`.
Instrumentation commit 406f992, based on 459b201. Patch archived beside this
record, not added to P1's runtime patch series. Opt-in trace is absent by default.
The first relocated-cache build failed due to absolute compiler module paths;
its log is preserved. Copied build outputs were moved aside, not removed from
the original reproduction. Fresh release CLI build succeeded in 75.27 seconds.
No model ran during the build. Command:
`swift build --package-path /Users/chad/Models/agentwing/reproductions/Swiftlet-AW0031 -c release --jobs 2 --disable-automatic-resolution --product swiftlet`.
Native observer build:
`xcrun clang -O2 -fobjc-arc -framework Foundation probes/process_io_trace.m -o /Users/chad/Models/agentwing/evidence/AW-0031/process_io_trace`.

## Measurements

Raw run: `/Users/chad/Models/agentwing/evidence/AW-0031/20260905T183732Z`.
`evidence/AW-0031-routing-results.json` verifies raw hashes, sequence continuity,
per-layer routing counts, per-token decode batches and prefill expert unions.
3120 events are below the 10000-event cap. Exactly 2120 token-layer routes
(29 prompt + 24 generated steps, 40 layers, 8 experts each), 1000 cache batches,
10697 batched requests, 1448 hits and 9249 misses reconcile with CLI totals.
All three generated outputs are byte-identical. This is a diagnostic output,
not proof of general agent capability or task completion.

| Arm | Prefill sec | Decode sec | OS-attributed disk reads GiB | Peak process footprint GiB |
| --- | ---: | ---: | ---: | ---: |
| C1 trace off |7.672|10.939|22.035|2.611|
| T1 trace on |7.636|11.414|21.792|2.624|
| C2 trace off |7.574|11.193|20.975|2.628|

Traced model-step total 19.050 seconds is 1.5–2.4% above the bracketed controls.
That is an observed overhead range for this short trial, not a confidence
interval. The independent 20 ms sampler runs in all arms, so its common overhead
is not estimated here. Startup-inclusive elapsed 24.90/23.08/22.01 seconds also reflects
warming/setup and should not be used to claim the trace improves performance.
Pressure 1 and zero sampled swap growth in every arm; source/P1 preflight passes
again after all owned processes stop. Process footprint is not total system
memory residency; file-cache and other shared/file-backed memory matter.

Trace sums: 28.790 GiB of logical expert preads, 58.1 ms cache selection and 6.978 seconds
inside read batches. Those read batches include dispatch, reads/copying and
waiting; they are not a pure device-latency counter. OS-attributed disk-read
samples include non-expert files and can miss final I/O between last sample
and exit; they are not exact physical-media or per-expert attribution. Nonetheless
roughly 21–22 GiB/process contradicts treating real inference like AW-0030's
zero-disk-read warmed microbenchmark.

## Actual locality and replay

Each decode step requests 320 distinct (layer, expert) pairs, 0.996 GiB of logical
expert bytes. Adjacent steps overlap 49–146 pairs, mean 95.6/320 (29.9%). Thus even
retaining one full previous step would not serve most next-step expert requests.
This is one short prompt, not a workload-independent routing law.

A fixed-route replay of the real LFU policy, batch protection and slot tie-break
reproduces all 1448 observed hits at 160 slots. Results:

| Capacity slots | Approx cache GiB | Hits | Misses | Logical miss GiB |
| --- | ---: | ---: | ---: | ---: |
|160|0.498|1448|9249|28.790|
|240|0.747|1831|8866|27.598|
|320|0.996|2295|8402|26.154|
|480|1.494|2860|7837|24.395|

These are logical read-volume counterfactuals, not speed predictions. Larger
caches consume memory and can evict useful OS file-cache pages or induce swap.
The 240-slot replay also matches AW-0029's measured larger-cache counts, although
that trial did not improve speed. Doubling slots removes only about 9.2% of total
logical expert reads on this trace. Do not promote a larger cache from replay.

## Disposition and next evidence

Tracing work complete; retain the diagnostic tools and actual routing stream.
P1 remains unchanged. No agent behavior, task policy, weight precision, routing
selection or numeric kernel was changed. The instrumentation build is not a
replacement production runtime and has not been promoted.

Highest-value follow-up is to replay this real multi-layer sequence for transport
experiments, with both logical and OS-attributed I/O measured, instead of a small
hot synthetic set. Cache-policy housekeeping has little latency budget here.
Reducing bytes per selected expert or overlapping unavoidable reads with compute
has a stronger physical basis, but precision changes require independent numeric
and broader agentic-capability validation. Actual overlap opportunities depend
on router dependencies; they are not established by this trace alone.

Reproduce with `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_real_routing.py`
after the isolated build and observer compilation. Analyze with
`PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/analyze_real_routing.py RUN`.
No public API or P1 default is changed by either command.
