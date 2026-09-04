# AW-0003 — K2 Horizon 36B-A4B feasibility

## Status

Planned. No artifact download authorized or started.

## Hypothesis

At least one official or provenance-preserving quantization of K2 Horizon MoVA
36B-A4B can be served on the base 16 GB M1 with valid reasoning and tool-call
parsing, acceptable memory pressure, and sufficient end-to-end work rate to
enter the B0/C0 screening comparison.

## Pinned upstream identities

- Source model: `IFM/K2-Horizon-MoVA-36B-A4B`
- Source revision: `05cab0a4d7150c1c460a000b37ff40cc1af2feaa`
- Official GGUF repository: `IFM/K2-Horizon-MoVA-36B-A4B-GGUF`
- GGUF revision: `d1df6130209e274b23f7ad2ae0454d19e120d189`
- License reported by publisher: Apache-2.0

## Published configuration to preserve

- Reasoning effort: high
- Temperature: 1.0
- Top-p: 0.95
- Reasoning parser: `k2_horizon`
- Tool-call parser: `k2_horizon`
- Default tool format: XML; JSON and typed XML are also supported

## Cheap falsifiers

1. Inventory the official GGUF shards and quantizations without downloading.
2. Confirm local-runtime support for the `k2_horizon` architecture, MoVA, chat
   template, reasoning parser, and tool-call parser.
3. Estimate resident memory, KV state, and storage traffic at 8K and 16K.
4. Reject a normal resident path that cannot stay below the host-pressure gate;
   retain a streaming path only if MoVA and routed experts can be represented
   without semantic loss.

## Required first endpoint

The same deterministic read/search/edit/test/recovery fixture used for B0 and
C0, with every parser or adapter transformation recorded.

## Results

Pending.

## Disposition

Unresolved.

