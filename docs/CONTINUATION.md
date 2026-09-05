# Continuation state

P1 is promoted. The local goal's evidence and deliverables are complete.
No Agentwing model or task process remains running. The final smoke session
90423 exited0; runner11351/server11373/client11399 are gone and port8080 is free.

Use `scripts/run_local_agent.py` and `docs/LOCAL_AGENT.md` for a new user task.
The source workspace is copied and preserved. Exact settings are in
`spec/validated-local-agent.json`. `docs/PROMOTION_REPORT.md` contains the full
requirement audit and limitations. Do not resume completed benchmark slots.

AW-0027 full run order:
- C1 `20260905T010110Z`:3/8,6276sec,1.720841/hour.
- A1 `20260905T024837Z`:8/8,4559sec,6.317175/hour,3.67098xC1.
- C2 `20260905T040519Z`:3/8,5582sec,1.934790/hour.
- A2 `20260905T053919Z`:8/8,4534sec,6.352007/hour,3.28305xC2.
All audits pass. Pressure1; candidate swap growth zero. Same frozen arms,
original executable and identical permission boundary in both pairs.

Final AW-0028 launcher smoke:
`/Users/chad/Models/agentwing/tasks/20260905T070814.339390Z`,355.40sec,
independent bounded-read verifier pass, pressure1,zero swap growth. Source and
raw evidence hashes match. All19 Python tests and real Pi fixture pass. Earlier
handoff failures and first smoke are preserved; see the AW-0028 record.

Ownership was transferred from idle thread “Evaluate maximum local agentic
speed” (`01a06974-8ce6-7ef1-8307-10f3fadb9e04`) on2026-09-04. The prior12
local commits, source, raw evidence and model provenance were preserved.
No deletion was needed. Frozen benchmark execution files remain unchanged;
original/v2 plan amendment and original failing observer audit are retained.

The applicable stopping branch is successful promotion. No optional research
must run to complete this goal. Future work could examine bounded raw-history
retention, materially larger KV workloads or newly practical local alternatives;
these require new scoped experiments, not silent changes to completed evidence.
