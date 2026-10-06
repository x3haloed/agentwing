# AW-0200 — Isolated Metal 6-bit value-cache correctness screen

## Status and hypothesis

Completed. Standalone M1 Metal encode/decode preserves AW199 indices, norm
scale and inverse output on all actual layers3/31/63. Predeclared correctness
acceptance: exact indices/reserved, scale error<=.2%, decoded relativeL2<=.005,
finite results, sampled pressure<4/swapgrowth<=1024MiB/freeSSD>=8GiB.
Primary metric is numerical correctness; cost is diagnostic, not acceptance.

## Fixed configuration

AW199 saved fixtures/theory books,128-value signed WHT,F16norm,4/6bit packed
layouts68/100bytes. Fresh standaloneMetal processes in4/6/6/4 order at each
layer,5windows×64 encode+decode+packedCPUreadback operations per process:
12processes/3840 complete operations. Binary-search centroid selection in
both prototypes, explicit fastMathdisabled. Sources/binary/parent/task-free
scope/hardwareOS/thermal/storage pinned in immutable external plan/receipt.
No model server, task, tool call, sampling or reasoning. Fixed16GBM1/internalSSD.

Build command in receipt; run:

```
python3 scripts/screen_bonsai_value_precision_metal.py
python3 scripts/audit_bonsai_value_precision_metal.py
```

External output must be fresh to reproduce; preserve prior evidence.

## Results

All12 packed/decoded outputs byteexact CPU reference (4608 groups). Independent
file/hash replay passes. Sampled pressure1/swaprange0MiB/minfree138,097,053,696B.
Half-second monitoring can miss short peaks; not full-model host admission.

Median6bit/4bit combined prototype operation costs:1.155/1.316/1.183 for
layers3/31/63. Each uses all10 windows/precision/layer. These are standalone
binary-search encode/full inverse/packed readback costs, not native llama
SET_ROWS, native flash-attention cost or endpoint speed. Compile/setup costs
recorded separately in logs; process duration includes monitor polling.
Decoded bytes inspected independently after each process, packed bytes
CPU-touched after every operation. GPU decoder is separate from CPU native
inverse, strengthening AW199's shared-inverse limitation for these fixtures.

## Evidence, limitations and disposition

`evidence/AW-0200-value-precision-metal-screen.json` pins raw hashes and audit
under `/Users/chad/Models/agentwing/evidence/AW-0200`. Host build warns that
fastMathEnabled is deprecated; option remains explicit and successful.

Retain numerical Metal survivor, with cost concern. Native cache-type wiring,
writer scheduling/row indices, vector/matrix flash-attention, installation,
full-model own accumulated trajectories, vision/tools and endpoint validation
remain required. Prototype16–32%extra component cost is not a reason to claim
speed or whole-system rejection. No runtime/profile/default/P1 modification.
Not full Google PolarQuant/QJL. Goal remains unproven.
