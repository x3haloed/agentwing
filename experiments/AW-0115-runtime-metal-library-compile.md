# AW-0115 — Complete Turbo Metal library runtime compilation

## Status and hypothesis

Retained compilation path. Available runtime Metal compiler can compile the
complete pinned Atomic source unchanged and expose Bonsai256/256 asymmetric
q8-K/Turbo3-V and q8-K/Turbo4-V vector attention kernels plus inverse WHT.

## Frozen configuration and reproduction

External plan hashes AW-0114 source authority, embedded source, Swift runner,
compiled executable and exact Swift build command. Source remains Atomic
074bf826e1b06005a51737d29387e36657f41bf7 with unchanged arithmetic. Embed the
preserved ggml-common.h and ggml-metal-impl.h contents at their matching quoted
include directives in full ggml-metal.metal; leave conditional Metal includes
and other preprocessing intact. No shortened kernel extraction.

Compile `experiments/fixtures/turbo-metal-library.swift` with `swiftc -O`;
run executable against embedded.metal. Runner sets MTLCompileOptions language
version3.0, uses MTLCreateSystemDefaultDevice/makeLibrary, and asserts three
required function names. Primary acceptance: exit0 and all names present.
Internal SSD, Apple M1 Macmini9,1/16GB, macOS27.0.1/26A434. No model inference,
cache allocation, sampler, harness tools or task/verifier changes. No endpoint
or pressure/performance claim; host samples were not collected for compile-only.

## Results and evidence

Runtime compilation exit0, no stderr. Apple M1 library has976 function names;
both kernel_flash_attn_ext_vec_kq8_0_vturbo3_dk256_dv256 and
kernel_flash_attn_ext_vec_kq8_0_vturbo4_dk256_dv256 are present, as is
kernel_turbo_wht. `evidence/AW-0115-metal-library-compile.json` records all file
hashes/results; raw `/Users/chad/Models/agentwing/evidence/AW-0115`.

## Disposition and limits

Retain runtime compiler path; offline missing toolchain failure AW-0114 remains.
Kernel presence/compilation is not specialized-pipeline dispatch or correctness,
actual registered Prism cache types/allocations, compressed generation, vision,
quality or endpoint throughput. Next: exact function constants, strides, scratch
and threadgroup dispatch against independent CPU attention authority. P1 and
current FP16 runtime remain intact.
