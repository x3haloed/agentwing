# AW-0030 — Bounded expert mapping falsifier

Contract: explore removing expert-copy/dispatch work while preserving identical
weights and GPU-visible values. Standalone native Metal probe; P1/runtime/model
unchanged. No narrower agent behavior or capability claim. Single process,
internal SSD, no model inference concurrently. Stop critical pressure; external
supervisor applies180sec deadline and1024MiB swap-growth limit.

Probe:64 experts from layer00, eight at a time,3,342,336 bytes/expert. Validate
all mapped bytes with memcmp against pread and compute independent CPU scan
outputs. Each GPU dispatch reads every32-bit input word and must match those
CPU outputs. Then serial/concurrent/mapped/concurrent/mapped/serial,16 batches
per arm. Mapping lifetimes end after GPU completion; bounded live expert batch
is25.5MiB. Existing preallocated copy buffers also remain resident in mapped
arms, deliberately exposing that fixed memory overhead in footprint readings.

This is explicitly a warmed-data microbenchmark: validation precedes timing.
Record proc_pid_rusage disk-read bytes, pageins, CPU times, footprint, fetch,
GPU wait and total wall. Separate mmap/Metal-buffer creation from deferred GPU
page access; do not mistake a fast mmap return for completed reads. All arms
run the same scan kernel, not the model's quantized matrix multiplication.
Performance results cannot establish agent work/hour or safe full-model mapping.

First probe completed at20260905T160229Z. Serial full-arm wall74.7/77.7ms,
concurrent44.3/52.2ms, short-lived mapped88.2/99.7ms. Mapping fetch setup was
faster but GPU wait70.6/81.9ms versus concurrent16.1/20.4ms dominated. All timed
arms report zero process-attributed disk-read bytes. Every GPU result matches.
This falsifies a naive per-batch zero-copy win on warmed data. It does not
attribute the additional GPU wait to a specific driver mechanism.

Declared follow-up before running: add retained-mapped arm, at most64 expert
mappings (204MiB logical), reused across16 batches and released at arm end.
Compare concurrent/mapped/retained/concurrent/retained/mapped/concurrent. This
tests mapping lifetime rather than changing bytes or GPU arithmetic. Existing
copy buffers remain allocated identically. Keep footprint distinct from mapped
file bytes: file-backed residency is not fully described by process footprint.
Raw rusage user/system counter fields are now labeled without assumed units;
first probe's *_ns labels should be treated as raw counters, not timing claims.
Original source is archived beside first probe evidence before this amendment.

Retained-map probe20260905T160524Z passed. Concurrent wall45.3/43.6/43.8ms;
retained maps38.2/38.6ms; transient maps80.7/65.1ms. All GPU values match,
zero reported disk reads and sampled footprint roughly32MiB (not total resident
file pages). Retention appears helpful for this64-expert reused working set.

Before promotion/integration, falsify locality bias: add a128-expert pattern
with no repeated expert in the timed16 batches and a FIFO cap of64 retained
mappings (204MiB). Validation warms and checks all128 inputs first. No cold-SSD
claim. Preserve the v2 executable separately before compiling this amendment.

## Final results and disposition

Churn probe20260905T160743Z reversed the reuse-specific win: retained maps
63.8/121.6ms versus concurrent42.9–45.6ms. A source review found eviction occurred
after creating the replacement mapping, transiently allowing one extra3.19MiB
mapping above the retained-cache count. Moved eviction before creation and
repeated the churn probe as20260905T160857Z. Retained maps66.2/70.5ms versus
concurrent44.0–45.1ms; GPU results still match. All versions and failures of the
performance hypotheses are retained. Final source is the strict-cap variant.

All four probes completed under pressure1; recorded swap samples did not grow.
Every GPU output matches the independently computed CPU reference. All timed
arms report zero process-attributed disk reads. No model process was loaded and
no P1 executable/profile/weight was modified. Compact evidence and raw hashes:
`evidence/AW-0030-mapping-results.json`.

Do not integrate this mapping transport into P1. The small locality-case gain
is not robust under churn. Lower fetch setup cost moved to much larger command
completion waits, while reported GPU execution remained near10–12ms/arm.
This localizes the penalty outside the measured GPU kernel interval, but does
not identify a specific driver/VM mechanism. It is not evidence that copying
is always superior or that all zero-copy representations are exhausted.

Next useful measurement: capture actual routed-expert access and process disk
read counters during inference, then replay its locality/churn and separate
cache selection, dispatch and read costs. This standalone probe deliberately
does not claim that its synthetic trace or warm residency equals model serving.
Any further representation/kernel candidate must preserve byte/numeric behavior
where intended and pass broader agentic tasks before replacing P1.

## Reproduce

Compile on this Mac:
`xcrun clang -O2 -fobjc-arc -framework Foundation -framework Metal probes/expert_mapping.m -o /Users/chad/Models/agentwing/evidence/AW-0030/expert_mapping_v2`

Run `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/probe_expert_mapping.py`
for reuse, or append `churn` for128 unique experts under the64-mapping cap.
Outputs are new timestamped external directories. The binary name is historical;
each run archives its source and records the actual source/binary hashes.
