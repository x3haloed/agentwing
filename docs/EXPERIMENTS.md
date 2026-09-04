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
8. Preserve only behaviorally useful history and tool results
9. Compare reasoning budgets by verified utility/hour
10. Measure expert locality on real agent trajectories

## Phase C — representation

11. REAP calibration on held-out agent trajectories
12. Pruned 8-bit versus unpruned 8-bit Qwen
13. Mixed expert precision using routing and trajectory salience
14. Higher-bit hot experts under a fixed disk and read budget

## Phase D — scheduling

15. Tool-time inference overlap
16. Speculative decoding and native MTP where supported
17. Single-model batching
18. Multiple specialized agents only after single-rollout saturation is known
