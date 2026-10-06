# AW-0110 — Posthoc distortion on candidate-generated cache

## Hypothesis and predeclared gates

The Turbo3/4 survivors from AW-0108 also survive the unchanged provisional.25
relative attention-output L2 limit on AW-0109 final decode after32 generated
tokens. Before measuring distortion, independent CPU attention must agree with
native FP16 output within1e-3 at each actual full-attention layer3/31/63.
This is a cheap component rejection criterion, not model-quality acceptance.

## Configuration and execution

Frozen external plan pins source, AW-0109 capture result, AW-0107 trusted oracle,
Atomic CPU codec and original Prism base dylib. The captured selective candidate,
model/runtime/host/sampling/storage/configuration pins inherit AW-0109. No new
model inference, tool permission, task/verifier or sampling changes in this CPU
screen. Quantize only48 populated keys/values per four KV heads, dimension256;
24 query heads, q8 keys and Turbo2/3/4 values, inverse WHT in two128 groups.
Masks and complete tensor strides retained; canaries checked each encoded row.
`python3 scripts/check_bonsai_accumulated_turbo_attention.py` exit0.

## Results

| Layer | Native/CPU FP16 | q8 K/Turbo2 V | q8 K/Turbo3 V | q8 K/Turbo4 V |
| --- | ---: | ---: | ---: | ---: |
| 3 | .00008969 | .202316 | .099138 | .078470 |
| 31 | .00050896 | .269936 | .136840 | .088919 |
| 63 | .00002343 | .235526 | .110739 | .092661 |

All baseline oracles pass; Turbo2 fails middle layer and remains rejected.
Turbo3/4 retained for further context/faithful execution falsifiers. Phase host
pressure1/swap898.06MiB unchanged, macOS27.0.1/26A434; no performance claim.

## Evidence, limitations and disposition

`evidence/AW-0110-accumulated-attention.json` records all external hashes.
Raw evidence `/Users/chad/Models/agentwing/evidence/AW-0110`.
Posthoc quantization of FP16-generated cache does not establish accumulation
under compressed execution. No long-context, vision, complete Google algorithm,
Metal dispatch or endpoint gate acceptance. Runtime remains FP16; P1 frozen.
Retained3/4; rejected2 under unchanged cheap criterion. Next: faithful compressed
execution and broader cache coverage before endpoint comparisons.
