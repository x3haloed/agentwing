# Experiment roadmap

## Phase A — establish endpoints

1. `AW-0001`: Qwen3.6 8-bit + Swiftlet + Pi artifact and pressure bring-up
2. `AW-0002`: strict native Swiftlet/Pi tool-bridge smoke
3. `AW-0003`: K2 Horizon artifact, parser, runtime, and host-fit feasibility
4. `AW-0004`: explicit schema-tag normalization arm
5. `AW-0005`: Gemma 4 + TurboFieldfare + OpenCode tool-loop and pressure bring-up
6. `AW-0006`: interleaved 20-task B0/C0/K0 screening comparison

## Phase B — remove agent-loop bottlenecks

7. `AW-0007`: exact-prefix reuse for tool continuations
8. `AW-0008`: freeze an eight-task deterministic agentic pre-screen and B0 floor
9. `AW-0009`: salvage maximal fully valid tool-call prefixes before malformed suffixes
10. `AW-0010`: compare the full Pi tool surface with a shell-only profile
11. `AW-0011`: test shell-only action with explicit prefix recovery
12. Preserve only behaviorally useful history and tool results
13. Compare reasoning budgets by verified utility/hour
14. Measure expert locality on real agent trajectories

## Phase C — representation

15. REAP calibration on held-out agent trajectories
16. Pruned 8-bit versus unpruned 8-bit Qwen
17. Mixed expert precision using routing and trajectory salience
18. Higher-bit hot experts under a fixed disk and read budget

## Phase D — scheduling

19. Tool-time inference overlap
20. Speculative decoding and native MTP where supported
21. Single-model batching
22. Multiple specialized agents only after single-rollout saturation is known
