# KV memory on the installed B0 runtime

The earlier thread estimated 12 full-attention layers with FP16 KV. Inspection
of the installed pinned checkpoint and Swiftlet source on 2026-09-04 supersedes
both assumptions: **10 full-attention layers, FP32 GPU K/V, plus FP32 CPU
mirrors**. The other 30 layers use recurrent state rather than growing K/V.

`QwenMetalModel.ensureKVCapacity` allocates four bytes per scalar for each GPU
K/V buffer and doubles capacity with a 256-position minimum.
`appendKVMirror` appends the same rows to CPU Float arrays. This gives:

```text
10 layers × 2 KV heads × 256 dimensions × 2 (K,V) × 4 bytes
= 40 KiB per position per copy
```

The audited Stage A run's largest reported prompt + reused + generated total
was 2,038 tokens. Two logical copies at that length occupy about 159.219 MiB.
GPU capacity rounding, CPU array spare capacity, transient reallocations,
recurrent state, and other model buffers are additional; this is source-derived
payload accounting, not an observed allocation peak. Run pressure remained 1
with zero swap growth.

| Context positions | Logical GPU + CPU KV payload |
| --- | ---: |
| 8,192 | 640 MiB |
| 32,768 | 2,560 MiB |
| 131,072 | 10,240 MiB |

TurboQuant/PolarQuant remains a relevant long-context experiment. At the current
short-task frontier, malformed generation and repeated prefill have direct
failure evidence while KV capacity does not. Do not spend the next experiment
on a quantized-cache integration or claim an end-to-end speedup from these
memory estimates. Profile actual live allocations when longer retained
histories or memory pressure become material, including whether the CPU mirror
can be eliminated before adding lossy compression.

Model revision, source/config hashes, and arithmetic are retained in
`evidence/KV-source-accounting.json`. No KV implementation was changed.
