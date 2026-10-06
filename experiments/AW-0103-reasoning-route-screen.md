# AW-0103 — Read-only medium-effort routing screen

## Status and hypothesis

Complete static screen. Hypothesis: an absent effort forwarding path could
explain long thinking despite configured medium. Before any runtime fix,
inspect pinned CLI/server/Jinja and installed Pi adapter paths plus actual
model template. Do not change the active task's effort, token budget or deadline.

## Results

Pinned CLI writes --reasoning-effort into default_template_kwargs; server context
passes those defaults, and OAI reasoning_effort overrides the same kwarg. Chat
renderer copies kwargs into extra_context. Installed Pi's supported generic
compatibility branch forwards requested effort (no custom thinkingLevelMap in
current profile); provider reasoning and supportsReasoningEffort are enabled.
Model template reads reasoning_effort with xhigh fallback and accepts medium.
All eight source/config routing checks pass. There is no source evidence for
patching a missing-medium path from this screen.

This is conditional source-path evidence, not an actual request/rendered-prompt
capture or empirical guarantee of shorter reasoning. Low's syntactic template
acceptance does not override the publisher warning that low is ineffective.
No change to medium, native sampling, reasoning budget, runtime or benchmark.

## Configuration and provenance

Runtime sources exact Prism adfffbe41b2cabcd51fff326ab045662265062bb from
official repository; all downloaded bytes hashed. Installed Pi0.84.4 provider
chunk SHA3ef9e2c266064fea04c076ae8b9e0a8317ebc68f0b543efb4b01da32b394b628.
Pinned base model HF revision b072e1d3b35a0a630cece372c2127528e0994386,
base SHA53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3;
8952-byte chat template SHA
c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041.
Selective artifact has identical complete metadata (AW-0097). No inference,
performance measurement or hardware/OS change; bounded16MiB local metadata
read and small source downloads are incidental concurrent work while AW-0100
runs. Its full wall includes that activity; not a clean comparative endpoint.

## Command, evidence and disposition

python3 scripts/check_bonsai_reasoning_route.py (exit0).
External /Users/chad/Models/agentwing/evidence/AW-0103 holds source bodies,
receipt, extracted template, executed checker/result and hashes. Small
 evidence/AW-0103-reasoning-route-screen.json records identities/limitations.
Retain expected source route; do not apply an unsupported missing-effort fix.
Actual rendering verification remains possible after the frozen task terminates.
Goal remains open; current task continues unchanged.
