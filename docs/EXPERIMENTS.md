# Experiment roadmap

## Phase A — establish endpoints

1. `AW-0001`: Qwen3.6 8-bit + Swiftlet + Pi tool-loop and pressure bring-up
2. `AW-0002`: Gemma 4 + TurboFieldfare + OpenCode tool-loop and pressure bring-up
3. `AW-0003`: K2 Horizon artifact, parser, runtime, and host-fit feasibility
4. `AW-0004`: interleaved 20-task B0/C0/K0 screening comparison

## Phase B — remove agent-loop bottlenecks

5. Measure and minimize repeated static-prefix prefill
6. Preserve only behaviorally useful history and tool results
7. Compare reasoning budgets by verified utility/hour
8. Measure expert locality on real agent trajectories

## Phase C — representation

9. REAP calibration on held-out agent trajectories
10. Pruned 8-bit versus unpruned 8-bit Qwen
11. Mixed expert precision using routing and trajectory salience
12. Higher-bit hot experts under a fixed disk and read budget

## Phase D — scheduling

13. Tool-time inference overlap
14. Speculative decoding and native MTP where supported
15. Single-model batching
16. Multiple specialized agents only after single-rollout saturation is known
