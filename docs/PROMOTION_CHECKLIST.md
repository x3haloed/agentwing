# Completed local promotion checklist

P1 promoted on 2026-09-05. See [the promotion report](PROMOTION_REPORT.md) for
scope and requirement-by-requirement reasoning, and [usage](LOCAL_AGENT.md).

- Frozen Stage A eight-task inputs/verifiers and audited AW-0008 floor: passed.
- C1→A1→C2→A2 identity and chronology: passed.
- Both independent full-suite pair checks: passed, 3.67× and 3.28×.
- Candidate successes: 8/8 in both, preserving all required success counts.
- Candidate pressure below4 and swap growth at most1GiB: passed,1 and zero.
- Runtime/Pi protocol and inherited permission-boundary checks: passed.
- Loopback listeners and sequential owned-process cleanup: observed.
- Exact source reconstruction and independent clean build/test: passed.
- Fifty installed model payload hashes: matched before the comparison.
- Failed, rejected and deferred arms: retained in experiment records.
- Capacity: about301GiB free; no reclamation or user-data deletion required.
- Exact profile, task launcher and reproduction guide: delivered.
- Final launcher smoke: independent artifact verifier and raw/source hashes
  pass; owned processes gone and port8080 free.

The source/build reproduction limitation remains explicit: independently built
executable bytes differ, and all measured pairs use the pinned original binary.
The result is local Stage A promotion. Optional broader research is not a
remaining condition of this completed promotion checklist.
