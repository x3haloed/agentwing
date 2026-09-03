# AW-0001 — Qwen3.6 8-bit Swiftlet/Pi baseline bring-up

## Status

Planned; blocked only on storage availability and implementation scheduling.

## Hypothesis

Swiftlet can serve Qwen3.6-35B-A3B 8-bit to Pi through a lossless observable
tool protocol on the base 16 GB M1 without critical memory pressure or more
than 1 GiB sustained swap growth.

## Configuration identity

- Model: `Leonickson/Qwen3.6-35B-A3B-8bit-qpack`, exact revision to pin
- Runtime: Swiftlet, exact commit to pin
- Harness: Pi, exact release/commit to pin
- Adapter: absent or exact implementation commit to pin
- Expert cache: 2 GB initially
- Concurrency: one
- Storage: internal SSD preferred; external SSD is a separately named arm

## Cheap falsifier

Before downloading weights, verify from source or a tiny protocol fixture that
the chosen adapter can round-trip Pi's tool declarations and results through
Swiftlet's Chat Completions interface without silently repairing calls.

## Stage A — protocol fixture

The agent must:

1. read a file;
2. search for a symbol;
3. apply a bounded edit;
4. run a test that initially fails;
5. interpret the failure and repair the edit;
6. stop after the verifier passes.

Reject malformed tool IDs, arguments, result association, or turn history.

## Stage B — pressure fixture

Run repeated tool turns for 30 minutes while recording memory pressure, process
memory, swap, storage reads, prefill, decode, and tool timing. Reject crashes,
critical pressure, protocol corruption, or sustained swap growth above 1 GiB.

## Results

Pending.

## Disposition

Unresolved.

