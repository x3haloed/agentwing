# AW-0079 — Alternative Bonsai packing cost screen

## Status and hypothesis

Metadata screen complete; candidate retained, unqualified. PQ2_0 may trade
larger executable data for less unpacking work on Apple Silicon. No measured
speed or capability claim is made.

## Configuration identities and fixed conditions

Same pinned model revision `b072e1d3b35a0a630cece372c2127528e0994386` as PTQ1_0.
Candidate PQ2_0 SHA-256
`3907dc1658db1f78a9826bf8d5bcb8dc65db0d466388937af57f2294fae62ec1`.
Control PTQ1_0 SHA-256
`53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3`.
Prospective runtime is Prism `adfffbe41b2cabcd51fff326ab045662265062bb`.
No inference, activation comparison or benchmark was run. Harness, task,
thermal, sampling and cache conditions are therefore not experimental results.
Target remains the 16 GB M1 Mac mini and internal SSD, including Q8 vision.

## Primary metric and cheap falsifier

First screen published complete artifact sizes before downloading. A later
isolated admission must enforce existing pressure/swap gates and verify actual
weights, representation fidelity and full runtime costs before endpoint testing.
A larger file alone neither proves faster execution nor rejects the candidate.

## Commands and results

Read the pinned Hugging Face revision API with `blobs=true` using urllib,
limited to 512 KiB. No weights downloaded or read during AW-0078 inference.
PTQ1_0 is 5,946,648,928 bytes; PQ2_0 is 7,206,168,928 bytes: an additional
1,259,520,000 bytes (1.173 GiB), or 21.18%.
Q8 vision remains 629,246,976 bytes; KV, recurrent state, checkpoints,
compute buffers and installation duplication must be counted separately.
This is disk metadata, not measured physical residency.

## Evidence and limitations

`evidence/AW-0079-packing-metadata-screen.json`, SHA-256 `30e630c7d4327e9e57e9dadc3ed5e442c63a0955f18345677919586793873119`,
retains parsed pinned metadata and the API response hash. The original API
response body was not retained; artifact claims require hash verification on
acquisition. Primary publisher guide: https://docs.prismml.com/bonsai-2-27b#choosing-a-packing.
Vendor packing guidance motivates a test but supplies no Agentwing endpoint
result. Same revision does not independently prove decoded tensor equivalence.
No hardware or performance claim is inferred from this metadata screen.

## Disposition

Retained for isolated cost/fidelity admission after the active model owner
stops. No active profile, frozen task, verifier, timeout or P1 control changed.
