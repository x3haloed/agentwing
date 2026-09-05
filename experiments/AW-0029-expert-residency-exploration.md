# AW-0029 — Expert residency exploration

Status: declared diagnostic, not a promotion candidate.

Compression contract: preserve general coding/agentic capability, available
behavior and P1's existing validated configuration. Explore cache residency,
data movement and native execution; no narrower task policy, prompt restriction,
model replacement or weight precision change in this experiment. Project scope
is a bounded local exploration, not a new long-horizon goal. Existing native
Swiftlet instrumentation is sufficient; no runtime build or edits are needed.

Hypothesis: a modest expert-cache increase removes enough fetch work to warrant
an agent-level trial. Primary diagnostic metric: model step wall seconds and
expert-fetch share; report startup-inclusive elapsed separately. Capability is
not established by this component test. Preserve P1 and require broader task
validation for any future promotion.

Plan: sequential C1(0.5GB), A1(0.75GB), C2(0.5GB), same raw coding prompt,
24 greedy generated tokens, existing layer-major prefill default32, same CLI
binary/source/model/internal SSD. Do not purge OS caches; bracket to expose
warming. Record CPU-gap/fetch/hit/miss, GPU waits, output, host samples and
hashes. Stop at pressure>=4, swap growth>1024MiB or180sec per run; stop all later
arms on any failed run. This CLI bypasses Pi and uses greedy argmax, so it is
not interchangeable with P1 endpoint scoring or sampler behavior.

Cheap falsifier: if expert fetch is only a small fraction of runtime, or the
larger cache provides no consistent reduction against both controls, do not
advance a cache-size optimization based on hit rate alone. Inspect other
measured resources instead. Identical generated text is a smoke invariant,
not proof of general model/agentic capability preservation.

## Results

All three arms completed with pressure1, zero swap growth and byte-identical
24-token generated-output files. Raw hashes verified. No runtime, model,
P1 profile or frozen execution file changed. Evidence:
`/Users/chad/Models/agentwing/evidence/AW-0029/20260905T152834Z`;
compact receipt `evidence/AW-0029-residency-results.json`.

| Arm | Cache GB | Prefill seconds | Decode seconds | Decode fetch seconds | Decode hits/misses |
| --- | ---: | ---: | ---: | ---: | --- |
| C1 |0.5|7.580|11.001|3.896|1448/6232|
| A1 |0.75|7.601|11.094|3.917|1831/5849|
| C2 |0.5|7.499|10.832|3.793|1448/6232|

Startup-inclusive elapsed24.43/22.44/23.46sec does not demonstrate an inference
speedup: the candidate's measured model steps are slower than both controls.
Larger cache improves aggregate hit rate14%→17% but does not reduce fetch cost.
Do not advance this cache-size arm from this result. This is a failed cheap
falsifier, not proof that every cache policy or workload cannot benefit.

Expert fetch consumes35.0–35.4% of decode wall time and about39% of prefill here.
It includes victim selection, concurrent dispatch and pread; it is not a direct
physical SSD-stall measurement. Decode performs984 command-buffer waits across
24 steps (41 per step). Most remaining wall time is in those waits; encoding,
router selection and KV mirroring are small in this probe. Counters measure
buffer GPU execution separately, so wait wall time must not all be called
GPU arithmetic. Instrumentation and this short prompt limit generalization.

## Reachable structural follow-up

The qpack path fills GPU-shared cache slots with one pread per missing expert;
batched concurrent reads already exist. Do not propose adding batching as if
it were absent. Next separate cache bookkeeping/dispatch, memory copies and
physical I/O on a representative routed-expert trace. Test persistent bounded
read workers or fewer larger transfers only if that split identifies overhead.

A deeper alternative would map page-aligned qpack expert regions directly into
GPU-visible buffers with bounded lifetimes, removing the explicit slot-fill
copy. Swiftlet already uses bytesNoCopy mmap for other weight shards, but not
this bounded expert-cache path. This is an unimplemented hypothesis: mappings
may pin too much memory or simply move cost into page faults. First falsifier
should be a bounded byte-identical expert-read/kernel probe with residency,
faults and pressure measurement. Do not map the full model and assume free RAM.
Lower-precision weights remain a separate capability-sensitive branch.

Disposition: exploration complete; P1 unchanged. The measured bottleneck is
worth deeper investigation, but no work/hour or capability gain is claimed.
