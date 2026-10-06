# AW-0128 — Runtime attention shader macro failure

Rejected. Frozen native Prism ggml_flash_attn_ext probe uses actual Q/q8K/TurboV
buffers from AW-0116,64 cache positions/48 active, full24-head output and CPU
rotated attention authority AW-0113. Primary rule six graphs supported/exit0,
finite6144-value outputs and relative L2<=.005. Source/harness/binary/runtime and
input/CPU authorities pinned before runtime;90s/case,.25s host checks.

First case exits3 before graph compute: Metal library initialization fails
because added vector specializations occur after `FA_TYPES` is undefined.
C++ build cannot detect this runtime shader problem. No output, no accuracy
result; remaining cases unattempted. Pressure1/swap growth0. Fixed internal SSD
M1/16GB/macOS27.0.1; no model inference/task/tool/sampling/permission changes.

Metadata `evidence/AW-0128-prism-attention.json`; raw native/compiler logs and
frozen plan `/Users/chad/Models/agentwing/evidence/AW-0128`. Preserve failure,
correct placement under separate AW-0129/AW-0130 revision. No qualification.
