# Experiment roadmap

## Phase A — establish endpoints

1. `AW-0001`: Qwen3.6 8-bit + Swiftlet + Pi tool-loop and pressure bring-up
2. `AW-0002`: Gemma 4 + TurboFieldfare + OpenCode tool-loop and pressure bring-up
3. `AW-0003`: interleaved 20-task B0/C0 screening comparison

## Phase B — remove agent-loop bottlenecks

4. Measure and minimize repeated static-prefix prefill
5. Preserve only behaviorally useful history and tool results
6. Compare reasoning budgets by verified utility/hour
7. Measure expert locality on real agent trajectories

## Phase C — representation

8. REAP calibration on held-out agent trajectories
9. Pruned 8-bit versus unpruned 8-bit Qwen
10. Mixed expert precision using routing and trajectory salience
11. Higher-bit hot experts under a fixed disk and read budget

## Phase D — scheduling

12. Tool-time inference overlap
13. Speculative decoding and native MTP where supported
14. Single-model batching
15. Multiple specialized agents only after single-rollout saturation is known

