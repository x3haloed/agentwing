# P1 local promotion report

Status: both interleaved performance comparisons passed; final task-launcher
smoke is running. Do not mark the goal complete until that smoke is verified.

## Measured result

Frozen Stage A v1.1, eight tasks,900-second task deadline, independent verifiers,
all failures and endpoint overhead counted. Hardware: Macmini9,1, Apple M1,
16GB, internal SSD, macOS26.6.2 build25G83. Runs were sequential C1→A1→C2→A2.

| Run | Verified successes | Endpoint seconds | Verified tasks/hour | Candidate/control ratio | Peak pressure | Swap growth MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Historical AW-0008 floor | 3/8 | 5231 | 2.064615 | — | 1 | 0 |
| C1 | 3/8 | 6276 | 1.720841 | — | 1 | 0 |
| A1 | 8/8 | 4559 | 6.317175 | 3.670980 | 1 | 0 |
| C2 | 3/8 | 5582 | 1.934790 | — | 1 | 0.31 |
| A2 | 8/8 | 4534 | 6.352007 | 3.283047 | 1 | 0 |

Each candidate preserves both the historical and paired-control success count,
exceeds twice its paired control's rate, and exceeds4.129230 tasks/hour (twice
the historical floor). Both candidates have52 tool calls,8 failed tool calls,
and zero model-error replies, rejected outputs or prefix salvages. Failed tool
calls are observable task work and remain included in elapsed time.

The complete model-runtime-harness configuration is the experimental subject.
Both arms share model/runtime executable, task permissions, prompt, harness,
cache, storage and timeouts. Controls use max192 output tokens and a hard
trigram ban; candidates use max512, repeated ngrams allowed and retained
complete tool-call boundaries. These results support the combined candidate,
not separate causal speedup claims for each setting.

## Requirement audit

| Goal requirement | Evidence and coverage |
| --- | --- |
| Frozen eight-task instrument and measured baseline | Stage A manifest/input/verifiers, AW-0008 full audit; all four AW-0027 suite hashes match |
| Two interleaved replications | Four launch receipts and identity/order check; full C1/A1/C2/A2 audits; pair-1 and pair-2 reports pass every check |
| Preserve successes and double utility | Each pair independently satisfies minimum3, candidate>=control, ratio>=2 and historical rate floor; table above |
| Bounded resource use and sustained operation | Each candidate ran over75 minutes with repeated tool turns; full pressure/swap traces pass, covering the30-minute Stage1 requirement |
| Valid, observable tool protocol |180 Swift tests/29 suites from clean build; AW-0024 inherited boundary canaries and real Pi fixtures; per-run paired tool events, request ownership, transcript hashes and copied-workspace verifier replay |
| Loopback and one model owner |127.0.0.1:8080 observed at each launch, manifests record bind, sequential owned process exits and free-port checks; no concurrent measured model |
| Reproduction | Nine archived patches reconstruct exact source tree; clean independent build/test passes;50 model payload hashes match; frozen execution preflight passes after comparison |
| Optimization families | AW-0014–0025 record attempted, retained, rejected, optional and deferred arms as discussed below |
| Capacity management | Internal SSD free-space measurements remained adequate (about301GiB after A2); no deletion was required or performed |
| Document best configuration and make it usable | Exact machine-readable P1 profile, byte-identical prompt/Pi settings, LOCAL_AGENT.md, separate task launcher; final smoke verification pending |

The original C1 observer audit rejected known same-request diagnostics after a
terminal generation metric. Runtime source establishes that ordering. The
strictly scoped offline predicate fix and regression tests are recorded in
plan v2; original plan and failed observer report remain. Measured execution
and scoring did not change. Timeouts remain zero utility even when an artifact
passes verification. Control rejection/salvage diagnostics are recorded under
the declared recovery policy; they are not silently erased or rescored.

## Optimization decisions and preserved failures

- Bounded tool results: compact bash guidance is used. AW-0023's optional1024-
  character cap saved only12 tokens over the historical full run and37 on repair
  replay, so that implementation was deprioritized rather than loaded.
- Malformed calls and recovery: strict early tool syntax, environment-guidance
  and short-output arms failed and are preserved. Declared schema normalization,
  complete-prefix salvage and retained tool boundaries established the usable
  path. No candidate replication needed a rejected-output salvage.
- Prompt and prefix reuse: compact-shell prompt and exact continuation matching
  are retained. AW-0021's relative-cwd extension remains unloaded. A replay
  lookup hit alone is not proof that KV tokens were reused.
- History: AW-0025 traces a remaining single-entry raw-history limitation;
  task05 refilled context in both candidates. Bounded history retention was
  proposed, not implemented or claimed as a speedup.
- KV: corrected source accounting gives80KiB/position across logical FP32 GPU
  KV and CPU mirrors, with additional allocation overhead unmeasured. Short
  measured workloads show low pressure and no candidate swap growth. TurboQuant/
  PolarQuant is deferred until longer contexts make KV memory material; no
  quantized-cache claim is made. See KV_MEMORY.md and its source evidence.
- Alternatives: AW-0020's bounded inventory found no immediately usable other
  weights/runtime in known local locations. This is a practical local screen,
  not proof that no alternative exists or a performance comparison.

AW-0019's8/8 development screen remains non-interleaved evidence. The aborted
mistaken navigation-only launch, timeout/drain failures, negative sampler arms,
and AW-0028 launcher cleanup/preflight failures remain recorded. None are
substituted for the required four completed comparison runs.

## Limits and stopping condition

This establishes a first local Stage A configuration, not held-out20-task or
external benchmark performance, general model superiority, long-context safety
or broad sandbox certification. The scoped policy limits writes and outbound
network; reads and other capabilities remain allowed. The advertised context
window is not validated local capacity. Two pairs offer limited variability
coverage; the reported ratios are observed, not confidence bounds.

Clean-build executable bytes differ from the measured original. Source/build
reproduction passes; bit-identical compilation and performance equivalence of
the clean binary were not established. P1 pins the measured original binary.

The applicable stopping branch is successful promotion, not exhaustion of every
optimization family. Once the final handoff smoke passes and the profile is
marked promoted, the remaining optional research does not prevent completion
of the user's stated goal. Preserve it as follow-up work instead of silently
expanding the goal into the broader Stage2/Stage3 roadmap.
