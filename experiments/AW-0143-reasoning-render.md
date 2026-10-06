# AW-0143 — live reasoning-effort rendering check

## Hypothesis and result

After AW-0142, test actual full experimental server /apply-template route rather
than infer prompt behavior from source. Same pinned server16K/q8-K/Turbo4-V/full
vision, default CLI medium. Controlled identical user message with omitted effort,
explicit medium and explicit xhigh; no inference. Default equals medium byte for
byte. Xhigh differs and inserts its specific reasoning instruction. Medium keeps
the thinking prefix and omits that xhigh instruction, as the pinned template
defines. All HTTP200, clean exit0, pressure1 and zero swap growth. Allocator408MiB.
Independent saved-body assertions pass.

## Provenance and scope

Command python3 scripts/probe_bonsai_reasoning_render.py. Frozen plan/source/spec/
launcher/version and host/OS/storage/cache/thermal records external at
/Users/chad/Models/agentwing/evidence/AW-0143. Every raw hash in
evidence/AW-0143-reasoning-render.json. No source, model or active profile change.
This is a minimal controlled request, not the exact failed Pi accumulated prompt.
It weakens missing default-medium forwarding, but does not identify the timeout
cause or prove cache fidelity. Retain medium; no unsupported effort fix, reasoning
restriction, deadline waiver, performance comparison or promotion. Next compare
the same saved accumulated prefix across cache arms with declared fidelity gates.
