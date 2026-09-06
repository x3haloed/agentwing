# AW-0033 — P2 contract and first representation feasibility screen

Hypothesis: inexpensive lossless coding of P1's existing expert bytes can provide
at least 50% size reduction, warranting a physical decoder test. Primary metric:
page-aligned compressed/source byte ratio on a deterministic small routed sample.
Reject this particular route to a half-size artifact if every sampled ratio is
above 0.5; this does not reject other lossless representations. No endpoint claim.

Before measurement: choose layers 0, 20, 39; at each layer take two least frequent
and two most frequent expert identities in AW-0031 actual route events, with ID
tie-breaks. Frequency is only within this short trace, not production rarity.
Test zlib level 1 on original bytes and reversible even/odd byte shuffle.
Verify exact decompression and inverse transformation. No whole bank conversion.
Charge 16 KiB page rounding. Retain per-expert hashes externally, compact ratios
in Git. Host gates inherited from P1; one sequential reader, no model execution.

P2 contract is in spec/p2-acceptance.json. The expanded corpus is NOT frozen or
implemented yet. Existing P1 acceptance and benchmark files remain unchanged.
Prismwing c87d0c1 and Firewing 0610a1a motivate complete memory accounting and
multi-layer routed/accumulated fidelity before large integration work.

## Results

Raw evidence: `/Users/chad/Models/agentwing/evidence/AW-0033/20260906T054119Z`.
Compact receipt and summaries: `evidence/AW-0033-feasibility-results.json`.
All raw hashes verified and all 24 codec round trips matched exact source bytes.
Raw zlib-1 page-aligned sizes range from 60.29% to 95.59% of original expert
bytes; even/odd shuffle ranges from 60.78% to 95.59%. No sampled form meets 50%.
Reject these forms as the proposed half-size representation, not lossless coding
in general. No physical decode or throughput measurement was necessary at this
rung. Sampling is small and biased deliberately toward observed frequency tails;
do not extrapolate its average to bank size or production demand.

P1's 3,342,336-byte expert is 3,145,728 bytes of packed weights plus 196,608 bytes
of BF16 scales/biases, with zero padding. Holding that metadata constant, a
hypothetical four-bit form is 52.94% of current bytes, not exactly half.

AW-0031 T1 read batches occupy 36.63% of its 19.050-second model-step wall.
Under unchanged non-read work, proportional read time and free codec execution,
halving read time gives 1.224x; achieving 1.25x requires read time below 45.40%
of control. These are conditional arithmetic diagnostics, NOT an endpoint bound:
agent prompt lengths differ, OS cache and representation change residency, and
compressed execution can change compute as well as storage traffic. Candidate
screening must account for those effects rather than promising a 25% gain from
half-size files alone. Direct low-bit execution remains a distinct possibility;
source inspection finds existing specialized four- and eight-bit affine GEMV
paths, but no candidate fidelity or performance has been established.

Disposition: retain the P2 contract and conditional accounting; reject the two
sampled codec forms for the half-size hypothesis. Expanded benchmark construction,
its independent verifier audit and corpus freeze are the next required work.
P1 remains unchanged. This experiment does not complete the active goal.
