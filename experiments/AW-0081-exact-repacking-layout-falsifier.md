# AW-0081 — Exact repacking tiny layout falsifier

## Status and hypothesis

Tiny source-derived layout check passed. PTQ1_0 decoded ternary codes can be
packed positionally into PQ2_0 without changing raw FP16 group scale bits.
This is a necessary layout property, not a complete representation acceptance.

## Identities and fixed conditions

Pinned Prism runtime source `adfffbe41b2cabcd51fff326ab045662265062bb`,
external source `/Users/chad/Models/agentwing/evidence/AW-0079/source-screen`.
All six source-file hashes verified before checking. No model weights read,
compiled kernel run, tensor artifact generated or active profile changed.
Script SHA-256 `9a53c88e4030b39c2e47903efe8c0fb6e45519a962e78281400bad95a418fe63`. Hardware timing irrelevant to this integer-layout check;
no speed or memory residency claim. Source-derived CPU staging and separate
Metal lookup/element mapping are compared without evaluating floating values.

## Primary metric and cheap falsifier

Require identical 128 integer codes and exact scale bits in every fixture.
6656 fixtures cover every byte value at each of 26 payload positions, plus 128
seeded heterogeneous fixtures. All 65536 raw scale patterns copied unchanged.
Heterogeneous fixtures distinguish reversed element order. Tiny fixtures do
not independently validate source algorithms or compiled dispatch.

## Commands and results

`python3 scripts/check_bonsai_repacking_layout.py` passed 6784 payload fixtures
and 65536 raw scale patterns. This source-level positive permits compiled
reference and actual tensor checks before any full streaming conversion.
Source receipt, script hash and result: `evidence/AW-0081-layout-falsifier.json`,
SHA-256 `bd71ca1c7c51073e0a748c780373573566d5a7bf5ca3e2aa8b7baa609b97a388`. No GGUF metadata, real matrix, activation, candidate behavior,
installation cost or endpoint improvement has yet been verified.

## Confounders and disposition

The Python check consumed approximately 2.1s while AW-0080 navigation was live;
that activity remains charged in AW-0080 wall and must not support a clean
comparative rate claim. No model owner, download or large build ran alongside.
Retained for next compiled/tensor fidelity gates; not promoted. Larger PQ2
storage and all decode/installation/unified-memory costs remain to measure.
