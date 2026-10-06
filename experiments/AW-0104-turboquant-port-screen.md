# AW-0104 — TurboQuant port IDs and effective cache-cost falsifier

## Status and hypothesis

Complete static screen. Hypothesis: preserved Atomic Turbo code can be copied
into pinned Prism unchanged and retain symmetric advertised byte savings.
Cheapest falsifier: compare enums, locked sources, actual Bonsai head metadata
and upstream effective-type resolution before build. No model invocation.

## Results

All ten Atomic AW-0071 locked files match074bf826e1b06005a51737d29387e36657f41bf7.
Atomic Turbo2 enum42 collides with Prism Q2_0 enum42. Prism already reserves
PQ2_0=142/PTQ1_0=143 and COUNT144. A port must preserve all Prism identities;
proposed new internal IDs144/145/146, COUNT147, are not implemented.

Actual base GGUF declares24 query heads,4 KV heads, K/V256. Atomic constructor
uses layer0 head values and upgrades symmetric Turbo K to q8_0 when ratio>=6
unless explicitly disabled. If the port preserves declared head resolution,
Bonsai meets that threshold. Actual loaded hparams/effective types still need
build-time/runtime verification; this is a conditional source prediction.

At16K, existing FP16 logical KV1024MiB. Symmetric Turbo2/3/4 arithmetic
136/200/272MiB is not the expected default effective cost under that policy:
q8 K + Turbo V gives340/372/408MiB, respectively. Head-padding/rotation/transient
installation costs remain excluded, along with149.62MiB recurrent state and
saved checkpoints, language/vision weights and full agent wall. Do not silently
remove the upstream quality precaution to claim smaller allocations. Published
foreign-model examples/comments are not Bonsai quality authority.

## Configuration and evidence

Prism target adfffbe41b2cabcd51fff326ab045662265062bb; preserved Atomic MIT
source outside Git. Base HF revision b072e1d3b35a0a630cece372c2127528e0994386.
Static header/source/model-directory read only; no sampling/context/scoring/
permissions or existing runtime change, no hardware performance claim.
Small evidence/AW-0104-turboquant-port-screen.json pins both headers, existing
lock verification and cost arithmetic. Sources remain at the AW-0071 external
location and hash lock. Inline Python source/hash/metadata/equation checks exit0.

## Disposition

Reject verbatim port and symmetric default cost assumptions. Retain explicitly
remapped asymmetric port for bounded compiled codec and real KV/attention tests
before integration. This practical WHT/Lloyd-Max codec is not established as the
complete Google PolarQuant+QJL algorithm, nor is any lossy cache quality or
25% endpoint improvement claimed. P1 and current runtime remain unchanged.
