# AW-0064 — Bonsai original capability preservation screen

## Status

Completed negative screen, 2026-10-05. Active successor campaign remains incomplete.

## Hypothesis and primary metric

The admitted Bonsai 2 PTQ1_0 + Q8 vision / Prism Metal / Pi configuration
preserves all eight original Stage A v1.1 task successes under unchanged task
prompts, verifiers, permissions and deadlines. Primary metric: eight independently
verified successes with protocol and host gates. Stop at first failure and
preserve all unattempted tasks. A single success cannot pass this gate.

## Configuration identities

Candidate: spec/bonsai-local.json and config/pi-bonsai-models.json, frozen by
AW-0064-original-plan.json. Control: unchanged spec/validated-local-agent.json,
model bytes and original Swiftlet binary. This is not an interleaved comparison.
The candidate retains its admitted medium reasoning and 2048 output ceiling;
P1 historically used reasoning off and 512. Sampling and context also differ.
No matched-P1 speed or promotion claim is permitted from this screen.

## Fixed conditions

16 GB M1 Macmini9,1, internal SSD, macOS 27.0.1 (26A434). Same Pi 0.84.4,
P1 compact system instruction, bash tool availability, workspace/state write and
loopback outbound boundary, 900-second Pi task limit, 60-second startup cap.
Fresh model process and same fixed workspace path per task; archive by rename
once both owned process groups stop. OS page cache and existing allocated swap
are recorded, not assumed clean. Monitor pressure and swap continuously; stop
at pressure >=4 or peak growth >1024 MiB. No concurrent model, build or large
integrity-read work. Charge model hash admission once, staging, startup, failures,
tools, cancellation, grading and recursive receipt generation to diagnostic wall.
The operational chat server is stopped during the screen.

## Prior cost and mechanism evidence

- Agentwing AW-0031 observed 28.790 GiB logical expert reads, about 21–22 GiB
  process-attributed disk reads and only 29.9% average adjacent routed overlap
  on its short real trace. Cache-only synthetic results did not transfer.
- AW-0032 rejected a four-reader cap on the same real miss sequence; prior
  AW-0056/0057 quantization screens rejected mixture fidelity despite smaller
  storage. Do not reopen those completed forms through incidental rounding.
- Firewing's current frontier rejects expanded BF16's memory traffic and several
  uncorrected INT8 forms; residual-corrected forms still need accumulated-route
  evidence. Prismwing's current frontier rejects its composed onboard portfolio
  even under favorable cost grants, and prioritizes corrected endpoint breadth.
- User-directed Bonsai is a changed model and execution premise: a dense packed
  language backbone plus vision, not a recoding of P1 routed experts. Its
  artifacts are 5,946,648,928 + 629,246,976 bytes; the previous qpack occupies
  about 34 GiB. PTQ is consumed by a Hadamard-aware pinned runtime. AW-0063
  established two full local text/vision/Pi loops without incremental swap.
  Runtime archive, installed executable and weight hashes are pinned. These
  observations screen deployability, not a task-rate or disk-read speedup.
- Same-model early/middle/late mixture equivalence and numeric thresholds cannot
  transfer between different architectures. Preserve the old route/fidelity
  evidence; evaluate this model-change branch on frozen endpoint capability.
  No dense-model capability inference follows from old MoE numeric probes.

## Cheap falsifier and freeze

Verify P1 source/profile and all 215 frozen expanded-corpus inputs; held-out tasks
remain unexposed. Audit native terminal request and paired tool-event checks on
both saved AW-0063 trials before freezing this runner. Then run the complete
original task selection in manifest order, stopping at first failure.

Commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_capability.py --freeze
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_capability.py --check-only
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_bonsai_capability.py
```

## Results and evidence

Run /Users/chad/Models/agentwing/evidence/AW-0064/20261006T024451.079850Z terminated as a recorded capability failure. Navigation, single-file debugging, multi-file repair and refactoring passed; data transformation failed. Utility 4 across five attempted tasks in 781.323 diagnostic seconds. Recovery, bounded-read and config-sync remain unattempted, not removed from the gate. All five runs passed protocol, had pressure peak 1 and zero swap growth. All original test files stayed unchanged. Sixteen valid calls: fifteen productive and one valid but incorrect-result write; zero redundant, malformed, denied or failed shell calls. The data task manually wrote successful_events=3, although the source has four ok rows; JSON syntax/readback checks did not validate this statistic.

Independent recursive-hash, frozen-grader replay, protocol and arithmetic audit passes in evidence/AW-0064-terminal-audit.json. Audit pass confirms the failure is correctly recorded. Three temporary-copy falsifiers reject unexpected evidence, inflated success with refreshed hashes, and changed artifacts with refreshed hashes (evidence/AW-0064-auditor-mutations.json).

Bounded GGUF-directory inspection confirmed a 26,895,998,464-element qwen35 language artifact and 460,730,096-element clip vision artifact, with no expert-named tensors. Language directory is 11,120,982 bytes, alignment padding 10 bytes and payload 5,935,527,936 bytes; vision directory 19,646 bytes, padding 2 and payload 629,227,328. The language payload averages about 1.7655 bits per logical tensor element, counting storage overhead; this is serialized size, not decoder work or memory-read savings. Exact report in evidence/AW-0064-artifact-layout.json. It confirms the changed dense model premise, not cross-model numeric equivalence.
All source/task/model/runtime pins, commands, thermal state, host samples,
transcripts, independent grades and hashes are recorded.

## Disposition

Reject the exact medium-reasoning/temperature-1 original-capability preservation arm. Retain operational local multimodal admission as a different scope. AW-0065 separately tests only temperature zero on the failed task; a positive result still requires a new full original screen and expanded development. Even eight successes only allow expanded development work. Required
25% replicated interleaved original-plus-expanded work-rate gains, every
control-solved task, category preservation and matched comparison policy are
still unproven. P1 and the 24-task corpus stay frozen.

## Accounting limitation identified during inspection

The runner records final summary wall before recursive receipt creation. This
small post-summary receipt cost is not included in the printed diagnostic rate.
Preserve this ordering as a declared deviation; it cannot support the final
all-overhead promotion claim. Source/profile integrity preflight before timer
start is also not final promotion accounting. The primary capability metric
remains the predeclared eight successes. No held-out exposure or task change.
