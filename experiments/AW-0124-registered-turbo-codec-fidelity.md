# AW-0124 — Registered Prism traits and CPU codec fidelity

Retained. Hypothesis: integrated Prism base library preserves original format
identities and remapped Turbo traits, and its CPU codecs reproduce all actual
populated value-row encodings from the trusted standalone authority.

Frozen plan pins executed harness, built base dylib against AW-0123 result,
AW-0110 packed authority and AW-0109 capture. Loaded type identities verified:
q2_0=42/block64/18bytes; pq2_0=142/block128/34bytes; ptq1_0=143/block128/28bytes;
turbo2/3/4=144/145/146/block128/34,50,68bytes. CPU WHTgroup128.

Primary rule declared before execution: six identities match, nine real
192-row encodings byte-identical and row-boundary canaries intact.192 rows are
four heads×48 populated tokens at each layer3/31/63; padding excluded. Actual
F16 captures converted to F32, direct newly registered base codec entrypoints.
`python3 scripts/check_prism_registered_turbo.py` exit0; all identities and nine
cases pass. Includes Turbo2 ABI coverage without reversing its quality-screen
rejection. Phase pressure1/swap898.06MiB unchanged, no performance claim.

Configuration/model/runtime/host provenance inherits AW-0109/AW-0123, fixed
internal SSD M1/16GB/macOS27.0.1. No new model inference, task/tool/permission or
sampling change. Evidence `evidence/AW-0124-turbo-registration.json`, raw
`/Users/chad/Models/agentwing/evidence/AW-0124`.

This checks integrated base traits/direct codecs, not full CPU backend support,
Metal registration/cache allocation/graph, compressed model generation, vision
or endpoint qualification. Retain for next port stage; P1/default runtime intact.
