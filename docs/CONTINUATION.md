# Continuation state

Ownership transferred from the idle Codex thread **Evaluate maximum local
agentic speed** (`01a06974-8ce6-7ef1-8307-10f3fadb9e04`) on 2026-09-04.
The repository and external evidence are the continuation authority. No model
process was running at takeover. The prior 12 local commits were preserved.

## Completed during takeover

- Recovered and audited the previously unrecorded full Stage A run.
- Recorded its 3/8, 2.064615 utility/hour floor in AW-0008 and LEARNINGS.
- Added a repeatable offline auditor with copied-workspace verification.
- Tightened cancellation handling and completed AW-0014's real-model timeout
  diagnostic: terminal metric observed, no residual process, no swap growth.
- Preserved all benchmark inputs, verifiers, runtime patches, and acceptance
  thresholds.

## Next bounded work

1. Freeze AW-0015 for generic environment guidance: tell the agent the actual
   available Python executable and how to discover the project's test command.
   Change only the prompt, not packages, benchmark tasks, output limits, or
   verifier. Use the existing single-file task as a cheap development falsifier
   before interleaved full-suite measurement. Keep task-specific answers out of
   the prompt.
2. Test output budgeting as a separate arm; hitting 192 tokens does not imply
   that more generation repairs semantic corruption or raises utility/hour.
3. Address enforceable tool permissions before promotion. A working directory
   and Pi startup-offline mode do not establish a sandbox.
4. Screen alternate configurations, bounded tool results/history, and
   TurboQuant/PolarQuant KV compression as profiling warrants. The inherited
   preference for KV compression is retained; these short trajectories have
   not demonstrated KV pressure as their bottleneck.

Do not reduce the repository's five-replicate promotion rule to the earlier
thread's proposed two-replication goal wording. Preserve the held-out Stage 2
and external-validity gates. No new goal or background automation was created
as part of transferring ownership.
