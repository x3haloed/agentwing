# Learnings

This file is append-only. Supersede beliefs explicitly rather than rewriting
history.

## 2026-09-03 — Initial baseline choice

**Belief:** Qwen3.6-35B-A3B 8-bit through Swiftlet and Pi is the best current
capability-first starting configuration for the 16 GB M1 target.

**Evidence:** Qwen3.6 has strong published coding-agent results. A controlled
same-model harness sweep reports Pi ahead of Qwen Code, Claude Code, OpenCode,
and OpenClaw on SWE-bench Verified, and ahead of OpenCode and OpenClaw on
Terminal-Bench 2.0. Swiftlet reports that the 8-bit representation runs on a
base 16 GB M1 at about 1.74 decode tokens/s and removes repetition artifacts
observed in its 4-bit build.

**Qualification:** Swiftlet's public server documentation does not yet claim
function-tool support, and prompt prefill reportedly runs near decode speed on
the base M1. B0 is not established until AW-0001 validates the complete Pi tool
loop and measures repeated-turn latency.

**Disposition:** retained as B0 candidate; unverified locally.

## 2026-09-03 — Throughput control

**Belief:** TurboFieldfare + Gemma 4 26B-A4B + OpenCode is the strongest
ready-to-connect control.

**Evidence:** TurboFieldfare documents function tools, streaming, single-prefix
reuse, chunked prefill, a roughly 2 GB runtime footprint, and an OpenCode setup.
Gemma 4 publishes strong coding and tool-use results.

**Qualification:** No controlled Gemma harness sweep comparable to the Qwen3.6
sweep has been identified. TurboFieldfare has no published base-M1 endpoint
throughput measurement.

**Disposition:** retained as C0; unverified locally.

## 2026-09-03 — K2 Horizon admitted as an option

**Belief:** IFM K2 Horizon MoVA 36B-A4B is a credible capability challenger to
Qwen3.6 at nearly the same stored and active parameter scale.

**Evidence:** The publisher reports 36B total and approximately 4B active
parameters, a native 512K context, native reasoning and tool-call parsers, 58.6
on Terminal-Bench 2.1, and 26.8 on tau3-Banking. Its comparison table reports
Qwen3.6-35B-A3B at 44.9 and 9.3 respectively under the cited evaluation source.
The release includes official GGUF and FP8 variants and is Apache-2.0 licensed.

**Qualification:** The model was released the same day as this entry. Results
are publisher-reported, independent agentic replication is not yet available,
the validated serving recipes target server hardware, and no M1 streaming
runtime or throughput measurement has been established. Mixture-of-Values
attention may require runtime work beyond ordinary expert streaming.

**Disposition:** admitted as K0, an emerging unverified candidate; B0 unchanged.

## 2026-09-03 — B0 first local smoke stopped on swap growth

**Belief:** The Qwen3.6 8-bit/Swiftlet pair is computationally viable on this
base M1, but the initial 2 GB expert-cache arm is not yet host-safe enough to
serve as the fixed baseline under the observed ambient state.

**Evidence:** All 50 artifact payload hashes matched, Swiftlet's 162 tests
passed, and a real 16-token generation decoded at 1.87 tok/s. During the 22.30 s
process, the system memory-free estimate fell from 51% to 33% and allocated swap
rose by 1,614.94 MiB. The run was stopped before repeated turns or a 30-minute
pressure fixture.

**Qualification:** This is one conservative pre/post observation with 2.04 GiB
of swap already allocated; it does not establish a sustained swap slope or
separate Agentwing pressure from unrelated host processes. The process itself
reported 2.42 GiB maximum RSS and a 4.11 GiB peak footprint.

**Disposition:** exact B0 2 GB-cache arm stopped; lower-cache or clean-state arm
required before promotion.

## 2026-09-03 — Pi protocol works; stock Swiftlet tool transport does not

**Belief:** Pi 0.84.4 is a reproducible harness endpoint, while Swiftlet's stock
Chat Completions server is not yet an agent endpoint.

**Evidence:** An isolated two-request fixture verified Pi's tool declaration,
call ID, file result, result association, and continuation. Source inspection
of pinned Swiftlet shows unknown top-level `tools` are ignored, assistant
`tool_calls` are dropped from history, and only text deltas are returned. The
downloaded Qwen template and pinned tokenizer both already support tool specs.

**Qualification:** The fixture validates Pi's side, not model tool selection.
A native Swiftlet bridge must preserve tool declarations, calls, results, and
streaming response structure before Stage A can run against the model.

**Disposition:** retain Pi; implement and test the Swiftlet boundary next.

## 2026-09-03 — Strict Qwen3.6 tool syntax rejected locally

**Belief:** The 8-bit Qwen3.6/Swiftlet/Pi arm cannot yet serve as a strict tool
baseline, although a 0.5 GB cache is promising for host safety.

**Evidence:** Two instrumented real-model trials selected the correct `read`
function but emitted invalid parameter markup after complete generations. The
greedy replication repeated the same alternate `<path>…</path>` syntax. TTFT
was 116.1–116.4 s for 446–447 prompt tokens; decode was 2.06–2.12 tok/s. Across
three short trials, swap did not grow and pressure peaked at level 2.

**Qualification:** This establishes neither general tool-call failure rate nor
endpoint utility. It is one task with two sampling settings. Official Qwen/vLLM
grammar expects `<parameter=name>…</parameter>`; the observed property-name tag
is not standard parser output.

**Disposition:** reject the strict AW-0002 arm; test an explicit, logged,
schema-bounded normalization arm separately as AW-0004.

## 2026-09-03 — Schema-bounded normalization completes the first tool loop

**Belief:** Qwen3.6 8-bit through Swiftlet and Pi is now a viable experimental
agent endpoint when its repeatable schema-property tag dialect is accepted by
an explicit, logged, schema-bounded parser arm.

**Evidence:** AW-0004 completed a real `read` call and continuation. The first
turn normalized only the declared `path` property; Pi executed the tool and the
second turn correctly reported `# Target`. First- and second-turn TTFT were
115.8 s and 172.2 s, with 2.13 and 1.97 decode tok/s. All 63 pressure samples
were level 1 and swap growth was 0 MiB with a 0.5 GB cache.

**Qualification:** This is one task and one normalization event. It does not
measure correctness across tools, false-accept risk, sustained pressure, or
verified utility. The result belongs to the normalization arm, not strict
Qwen tool-call accuracy.

**Disposition:** retain AW-0004 for the full Stage A protocol fixture; prioritize
repeated-turn prefill because 670 prompt tokens took 172.2 s before the final
12-token answer.

## 2026-09-03 — Exact reuse works; tool-result volume becomes dominant

**Belief:** Exact token-prefix reuse is viable for Swiftlet tool continuations,
but bounded tool output is required before it can materially improve Agentwing
work rate on this host.

**Evidence:** AW-0007 T6 replayed an accepted raw tool call only after IDs,
types, names, and canonical arguments matched. The next prompt matched and
reused all 469 cached tokens. Because the call omitted a line limit, the new
tool-result suffix was still 684 tokens and took 171.9 s TTFT. A non-interleaved
full-file trial without reuse processed 1,155 tokens in 295.6 s. Pi returned the
correct heading; pressure peaked at 2 and swap decreased 8 MiB.

**Qualification:** The observed 1.72× diagnostic improvement is not a causal
benchmark: runs were not interleaved and first-turn prompts differed. AW-0007
also missed its predeclared 86.1 s threshold, and three of six trials failed
before continuation on malformed model syntax.

**Disposition:** retain exact-prefix reuse as a prototype, not a promoted
baseline. Optimize tool-result budgets and compact history next; separately
measure malformed-call recovery because it is now a large endpoint failure
mode.

## 2026-09-04 — First Stage A task confirms malformed suffix bottleneck

**Belief:** Exact-prefix reuse has removed most repeated-turn prefill when the
history is unchanged, but strict all-or-nothing parsing makes partially valid
multi-call generations a first-order endpoint failure mode.

**Evidence:** The strict `01-navigation` Stage A run scored zero in 445 endpoint
seconds. Its 1,450-token initial prompt took 391.3 seconds to first token. After
one valid `ls` call, all 1,489 prior tokens were reused and the continuation
reached first token in 6.5 seconds. That continuation contained a complete
valid `ls` call followed by an incomplete `read` block; strict parsing rejected
the entire generation. Pressure peaked at 1 with -8 MiB swap change.

**Qualification:** This is one task and one deterministic trial. Salvaging a
valid prefix may merely postpone failure, and it must not broaden acceptance of
unknown tools, invalid arguments, or unstructured suffix text.

**Disposition:** retain strict B0 evidence; test a separately flagged,
observable maximal-valid-prefix recovery arm as AW-0009.

## 2026-09-04 — Prefix salvage extends trajectories but loses live-state reuse

**Belief:** Truncating a malformed generation after its last complete tool call
is safe and observable, but it is not an effective throughput policy when the
truncated tokens already entered the model's live state.

**Evidence:** AW-0009 executed three tools and salvaged two malformed suffixes,
but `01-navigation` timed out at 910 endpoint seconds with zero utility. After
one exact continuation reused 1,489 tokens at 6.5-second TTFT, truncation caused
the next request to match 1,540 tokens but reuse zero; it paid 412.3 seconds of
prefill again. Pressure peaked at 1 and swap changed by -8 MiB.

**Qualification:** This rejects the tested truncated-history policy, not every
possible recovery policy. Replaying the full malformed state might retain
speed but would feed structurally invalid assistant history back to the model.

**Disposition:** reject AW-0009 as a performance arm and retain it only as an
off-by-default prototype. Reduce the tool schema and syntax surface next.

## 2026-09-04 — One universal shell tool cuts cold prompt cost by two thirds

**Belief:** For this small local model/runtime pair, a single universal shell
action is a substantially better inference surface than seven specialized Pi
tools, although recovery is still needed for trailing malformed call markers.

**Evidence:** AW-0010 reduced the frozen navigation task's initial prompt from
1,450 to 457 tokens and TTFT from 391.3 to 118.0 seconds. Total endpoint time
fell from 445 to 227 seconds. It executed one productive shell call, but the
next generation appended an incomplete call marker after a valid `cat` call;
strict parsing rejected it and utility remained zero. Pressure peaked at 1 and
swap growth was zero.

**Qualification:** This is one non-interleaved task and both arms scored zero.
It demonstrates component throughput, not improved verified utility.

**Disposition:** retain the shell-only profile as a candidate component and
test it with explicit, observable recovery as AW-0011.

## 2026-09-04 — Shell plus recovery produces first semantic Stage A success

**Belief:** The shell-only interface plus observable prefix salvage is the
first B0-derived configuration able to complete a frozen Stage A task, but
absolute paths and redundant calls materially depress its work rate.

**Evidence:** AW-0011 found the correct production value, wrote `2750`, reread
it, and stopped normally after 746 endpoint seconds, seven shell calls, and one
salvage. The original verifier rejected the missing newline even though the
task requested only the integer; Stage A v1.1 corrects that pre-baseline defect
and scores the preserved workspace 1 (4.83 utility/hour). One long absolute
path was corrupted in a validation command and recovered on the next turn.
Pressure peaked at 1 and swap grew 0.88 MiB.

**Qualification:** This is a corrected rescore of one non-interleaved task, not
a suite baseline or promotion result. Prefix salvage remains an explicit
policy difference.

**Disposition:** retain AW-0011 as the first functional candidate. Freeze v1.1
and test a relative-path, action-minimizing shell prompt next.

## 2026-09-04 — Compact shell policy raises verified work rate 25 percent

**Belief:** The compact shell-oriented agent prompt is the strongest current B0
configuration and is ready for a full Stage A floor measurement.

**Evidence:** AW-0012 retained utility 1 on `01-navigation` while reducing
endpoint time from 746 to 591 seconds, increasing the one-task diagnostic from
4.83 to 6.09 verified utility/hour. Tool calls fell from seven to five and
failed calls from one to zero. Pressure peaked at 1 with zero swap growth.

**Qualification:** This is a single non-interleaved task. The model continued
to use absolute paths, and one salvage forced an 809-token, 205.3-second refill.

**Disposition:** retain the compact shell + prefix-recovery configuration as
the Stage A floor candidate and run all eight frozen v1.1 tasks.

## 2026-09-04 — First full-suite attempt invalidated by orphaned task agents

**Belief:** Per-task process-tree ownership is a prerequisite for a valid
multi-task baseline; killing only Pi's wrapper shell does not enforce timeout or
task isolation.

**Evidence:** In the `20260904T164953Z` all-task attempt, timed-out Node agents
continued submitting requests after their wrapper PIDs were signaled. Task
08's server log includes a generation operating on task 05's workspace. Prompt
sizes and live state from orphaned trajectories leaked across nominal task
boundaries. The run's aggregate 1 utility / 6,931 seconds is therefore invalid.

**Qualification:** Task 01 completed before any timeout and remains a usable
replicate of AW-0012. Later task results and aggregate work rate are corrupted.

**Disposition:** preserve the run as negative runner evidence. Require a new
POSIX session per Pi task, group termination, a cancellation drain, and a
process-tree regression test before rerunning the suite.

## 2026-09-04 — Process groups and terminal barriers restore task isolation

**Belief:** The Stage A runner now enforces and evidences clean process and
model-request boundaries across timed-out tasks.

**Evidence:** AW-0013's barrier-enabled eight-task diagnostic completed seven
successive timeout transitions in 400 seconds. Every task observed its own
terminal cancellation metric, each server segment contained exactly one
473–496-token cold prompt with zero prefix match/reuse, no segment referenced a
foreign workspace, and no benchmark process remained afterward. Pressure
peaked at 1 and swap growth was zero. Synthetic tests also terminate a wrapper
and descendant from one process-group signal.

**Qualification:** The diagnostic uses a recorded 30-second integrity timeout
and is not a performance result. A valid floor still requires the frozen
900-second suite.

**Disposition:** promote the process-isolation runner infrastructure and rerun
the full Stage A v1.1 floor.

## 2026-09-04 — First full Stage A floor recovered and audited

**Belief:** Compact shell + explicit prefix salvage establishes a measurable
local engineering floor, but coding reliability remains the immediate limit.

**Evidence:** Run `20260904T190356Z` completed eight tasks in 5,231 seconds,
scoring 3/8 and 2.064615 verified utility/hour, with pressure level 1 and zero
peak swap growth. Three tasks timed out and two finished without valid
artifacts. Offline checksum, transcript, task-boundary, supplied-test, and
copied-workspace verifier checks pass. See AW-0008 and its committed audit.

**Qualification:** This supersedes the claim that the full floor is still
pending. It is one warm-server suite, not a promotion or an externally valid
capability result. Common prefix matches reused zero state across tasks.
Task working directories and startup-offline mode do not enforce shell
filesystem/network isolation. Some visible tests have narrow coverage.

**Disposition:** retain the floor. Test generic environment guidance separately
from output-budget changes; keep KV compression conditional on memory profiling.
The existing five-replicate and broader-validation gates remain unchanged.

## 2026-09-04 — Cancellation requires a terminal metric, not log activity

**Belief:** New log activity alone is insufficient to establish a completed
cancellation; a missing terminal metric must stop the suite.

**Evidence:** AW-0014 rejects stale metrics, diagnostic noise, and partial
writes in fixtures. Real run `20260904T203854Z` observed one complete terminal
metric after a 30-second timeout, finished in 56 endpoint seconds, and left no
benchmark process. Pressure peaked at 1 with zero swap growth.

**Qualification:** One-task integrity diagnostic, not throughput evidence or a
repeat of eight-task isolation. The barrier relies on serialized generation.

**Disposition:** promote the fail-closed terminal-metric guard. Keep the
AW-0008 measured floor and performance thresholds unchanged.

## 2026-09-04 — User activates the promotion goal

**Contract revision:** The newly active user goal explicitly requires two
interleaved replications for local promotion and authorizes measured cleanup
of verified-reproducible project-scoped data. This supersedes the earlier
five-replicate continuation note for this goal. Spec and validation protocol
now encode both paired 2× improvement and the historical floor (3 successes,
2.064615 utility/hour). Broader validation remains separately labeled.

**Capacity:** 304 GiB available on the project volume. No deletion warranted.

## 2026-09-04 — Hard trigram suppression obstructs normal code and tool syntax

**Belief:** Some apparent model failures are forced by the current sampler.

**Evidence:** Swiftlet's greedy preset retains a hard no-repeat-ngram size of
3. With the pinned tokenizer, the required third period of `127.0.0.1`, a
second `: int,` in a three-parameter signature, a repeated path, and a second
tool block all complete previously emitted trigrams. The guard therefore
bans their ordinary token continuations. A two-parameter signature does not
hit this condition. See AW-0016 and its tokenizer fixture report.

**Qualification:** These are canonical-tokenization checks, not an endpoint
score or proof that the guard explains every error. Alternative segmentations,
frequency penalties, reasoning policy, and true repetition remain relevant.

**Disposition:** prioritize an explicit no-hard-ngram-ban arm while leaving
other sampling controls unchanged. Do not promote before real task evidence.

## 2026-09-04 — Installed KV representation differs from the earlier estimate

**Belief:** KV compression becomes material earlier in long contexts than the
earlier FP16 estimate suggested, but is not the current short-task bottleneck.

**Evidence:** The pinned config has 10 full-attention layers, not 12. Swiftlet
allocates FP32 K/V plus FP32 CPU mirrors, giving 80 KiB of logical payload per
position across both copies. The baseline's largest reported sequence, 2,038
tokens, implies 159.219 MiB before spare capacity and transient allocations.
At 32K positions the same logical payload is 2.5 GiB. See `docs/KV_MEMORY.md`.

**Qualification:** Source-derived accounting, not measured allocation peaks;
the baseline still had pressure level 1 and no swap growth. No KV code changed.

**Disposition:** supersede the previous thread's layer-count/precision estimate.
Retain TurboQuant/PolarQuant and CPU-mirror removal as longer-context arms.

## 2026-09-04 — Environment facts alone do not rescue coding

**Belief:** Avoiding missing-tool guesses is insufficient while generation
itself corrupts necessary code structure.

**Evidence:** AW-0015 avoided missing Python/pytest commands but still wrote a
broken signature and expression, scoring zero before timeout. Prefix salvage
caused a 229.1-second refill. The terminal cancellation metric was not observed
within 30 seconds, so the strengthened runner stopped the suite. Pressure was
1, swap growth zero, and no benchmark process remained.

**Qualification:** One failed development task, not a causal full-suite
comparison. The unconfirmed drain also excludes a completed-suite claim.

**Disposition:** reject this exact prompt arm and prioritize AW-0016's sampler
change, keeping the original compact-shell prompt for that comparison.

## 2026-09-04 — Removing the hard ban repairs the artifact but not the finish

**Belief:** Necessary token repetition was one concrete obstacle; output
truncation and discarded prefix state remain independent obstacles.

**Evidence:** AW-0016 wrote a correct configuration and scored utility 1 in
687 endpoint seconds, where the earlier configuration task failed. It still
salvaged a partial multi-call generation, paid 247.4 seconds for a refill, and
ended with a rejected incomplete call. Pi returned exit 0 despite its final
assistant stop reason being `error`. Pressure was 1 and swap growth zero.

**Qualification:** The frozen verifier score is preserved, but the experiment's
normal-finish condition is unmet. This is not a suite speedup. The runner now
records model-error replies separately without changing the scoring rule.

**Disposition:** retain the no-hard-ngram-ban component and test a complete
retained tool boundary as AW-0017 before broader measurement.

## 2026-09-04 — Retained tool boundaries remove refill overhead

**Belief:** Ending after a complete call can preserve useful exact state and
avoid the large cost of recovering a truncated multi-call response.

**Evidence:** AW-0017 retained config-task utility 1 and completed in 409
endpoint seconds versus AW-0016's 687. Every continuation reused its complete
prefix; salvage fell from one to zero. Pressure remained 1 with zero swap
growth. The final longer test-discovery call still hit the 192-token cap and
was rejected, exposing a separate output-budget limit.

**Qualification:** Non-interleaved one-task diagnostic. The artifact is correct,
but a model-error reply remains; no default promotion is warranted.

**Disposition:** retain the boundary component and test 512 tokens as AW-0019,
with all other settings and the task timeout unchanged.

## 2026-09-04 — A larger call budget permits clean validation

**Belief:** Complete-call boundaries need enough output budget for the longest
legitimate call; stopping at a valid delimiter does not itself prevent truncation.

**Evidence:** AW-0019 completed config repair and its test in 620 endpoint seconds,
with utility 1, zero model errors/rejections/salvage, seven complete prefix reuse
hits, pressure 1, and zero swap growth. The discovery command needed 287 tokens.
One shell failure was recovered. The copied-workspace evidence audit passed.

**Qualification:** This is one task. AW-0017's shorter 409-second run stopped on
an error, so the extra time buys a clean finish and does not establish a speedup.

**Disposition:** retain the 512-token arm for the single-file repair gate.

## 2026-09-04 — No ready alternative in the known model locations

**Belief:** The older runtime projects do not currently provide an installed
alternative checkpoint for a cheap Agentwing comparison.

**Evidence:** AW-0020 found only Agentwing's Qwen qpack in the known checkpoint
locations. Firewing/Prismwing payloads are absent; both Hugging Face cache
entries contain a 40-byte file and no snapshot payloads. OpenCode is installed,
but the checked alternative runtime commands and common model stores are not.

**Qualification:** Bounded inventory, not a disk-wide proof of absence or a
performance rejection. Newly acquired models remain an option.

**Disposition:** no immediate alternate endpoint trial; continue the live Qwen
repair gate. No storage reclamation was needed or performed.

## 2026-09-04 — The repaired transport/sampler also completes a code fix

**Evidence:** AW-0019's single-file repair passed in 641 endpoint seconds with
seven calls, full prefix reuse, zero model errors/rejections/salvage, pressure
1, and no swap growth. The agent recovered from a missing Python command,
reproduced failing tests, then repaired and validated the implementation.
The copied-workspace audit passed and protected tests remained unchanged.

**Qualification:** Two successful development tasks do not establish suite
coverage, causal speedup, or promotion. Environment-command and path overhead
remain visible. The optional AW-0021 cwd-hint extension is prepared but unused.

**Disposition:** advance the unchanged AW-0019 candidate to the eight-task screen.

## 2026-09-04 — Current tool outputs are already mostly short

**Evidence:** AW-0023's actual 1,024-code-point hook saves only 12 tokens across
47 baseline tool results and 37 tokens across the clean repair's seven results.
The pinned tokenizer and all transcript/extension hashes are recorded.

**Qualification:** Offline counterfactual text accounting, not changed agent
behavior or endpoint latency. A rough repair-task projection is about 10 seconds
(1.55%), below the arm's 10% threshold, before any cost of recovering omitted text.

**Disposition:** deprioritize this exact cap without spending an endpoint trial.
Keep the current full-suite screen unchanged and prioritize cwd-hint overhead.
Reconsider bounded delivery if later output profiles are materially larger.

## 2026-09-04 — Keep pair assessment aligned with verified utility

**Correction:** AW-0022 initially added an unnecessary blanket failure gate for
model-error replies, rejected generations, and declared prefix salvage. The
frozen scorer can accept a completed, independently verified artifact after
such events. Explicit recorded recovery is not inherently protocol corruption.

**Change:** retain these counters as diagnostics, require salvage to be declared,
and preserve the existing utility rule. Protocol integrity audits and the
required protocol fixtures remain separate requirements. Ten Python tests pass;
a regression ensures these diagnostic counters do not silently rescore utility.
The real partial-run example still fails full-suite and success-count gates.

## 2026-09-05 — Latest-tool replay does not preserve all older raw history

**Evidence:** AW-0019 task 05 passed but incurred a 1,076-token continuation
refill (283.8-second TTFT). Its debug log also reported a tool-replay hit.
The pinned cache overwrites its single raw-reply entry after each tool turn;
older turns then use structured serialization. Tasks 01–04 had no such refill.

**Qualification:** Source-supported mechanism; the exact differing bytes in the
real prompt were not captured. A replay lookup hit and actual KV reuse are
separate measurements. Safe refill preserves correctness but costs time.

**Disposition:** record AW-0025's bounded retained-history option and defer any
runtime change until the current suite ends and its complete profile is known.

## 2026-09-05 — First complete candidate screen passes all eight tasks

**Evidence:** AW-0019 passed 8/8 in 4,469 endpoint seconds (6.444395 utility/hour),
with no model errors/rejections/salvage, pressure 1, and zero swap growth. The
full copied-workspace and integrity audit passes. Its rate is about 3.12 times
the historical 3/8 floor, but this comparison is non-interleaved.

**Disposition:** retain for paired validation, not promotion. AW-0024's inherited
write/network canaries and real Pi fixture pass; its opt-in policy needs a short
real-model gate and must be identical in both subsequent paired arms.

## 2026-09-05 — Clean source reproduction and installed payloads verified

AW-0026 independently built the pinned runtime and passed all 180 Swift tests
in 29 suites, with clean tracked files. All 50 installed model payload hashes
match the pinned manifest. The clean executable differs in bytes from the
original, so AW-0027 pins the original executable across all four runs. This
is source/build reproduction, not bit-identical compilation. AW-0024's real
model boundary gate also passed, permitting identical scoped policy in both
arms. No default is promoted before the two interleaved comparisons.

## 2026-09-05 — Terminal metrics can precede parser diagnostics

C1's full audit exposed an overly strict offline last-line predicate. Runtime
source confirms generation metrics precede request-scoped parse diagnostics.
Preserve the original failing audit; accept only known trailing diagnostics for
the same terminal request. Unknown/new activity remains rejected. All13 Python
tests and the corrected C1 audit pass. This changes observation only, not scoring
or any measured execution input; AW-0027 plan v2 records the amendment.

## 2026-09-05 — First interleaved pair passes

AW-0027 A1 passed8/8 in4559 seconds,6.317175 utility/hour,3.67098 times
paired C1. Both evidence audits and all first-pair gates pass; pressure1 and
zero swap growth. Retain unchanged for the required second interleaved pair.
No promotion from this single pair. See AW-0027-pair-1.json.

## 2026-09-05 — Second control is audited

AW-0027 C2 again passed01/06/07,3/8 overall, in5582 seconds (1.934790/hour).
Its data-transform failure exited earlier than C1's timeout; the same frozen
scoring retains that failure and all overhead. Four timeout drains and the
full evidence audit pass. Pressure1, swap growth0.31MiB. Advance unchanged A2.

## 2026-09-05 — Both interleaved candidate replications pass

AW-0027 A2 passed8/8 in4534 seconds,6.352007 utility/hour,3.28305 times
paired C2. Its full audit passes, with pressure1 and zero swap growth.
Together with A1's8/8 and3.67098 times C1, this satisfies both numerical
replication gates. Complete the final requirement audit and exact usable
configuration/reproduction documentation before marking the goal complete.

## 2026-09-05 — P1 promoted and task handoff verified

Both interleaved full-suite candidates passed8/8 at3.67x and3.28x their
controls, pressure1 with zero swap growth. Protocol, reconstruction and clean
build evidence pass. The final task launcher additionally passes19 Python
tests, real Pi protocol and an independently verified model smoke; Darwin
cleanup races and a TIME_WAIT preflight issue were fixed and preserved in AW-0028.
Promote P1 in spec/validated-local-agent.json. Use scripts/run_local_agent.py
and docs/LOCAL_AGENT.md; the frozen benchmark files remain unchanged.
Source/build reproduction is established, not identical compiled bytes or
held-out performance. The promotion stopping condition is met; optional
history, KV and alternative-model work remains a separate future campaign.

## 2026-09-05 — Larger expert cache is not yet a speed win

AW-0029 bracketed0.5/0.75/0.5GB with the same short greedy CLI workload. Expert
fetch accounts for about35% of decode time, but higher hit rate did not reduce
fetch or model-step time. Startup-inclusive timing alone would have suggested
a misleading win. All outputs matched and pressure/swap remained low. Retain
expert movement as a target; do not increase P1's cache from this diagnostic.
Batch reads already exist. The next useful distinction is bookkeeping/copy/
physical I/O, with bounded direct GPU mapping as an unimplemented alternative.
This exploration preserves agentic capability as the invariant; it introduces
no restrictions on the agent's work, tools or reasoning. P1 remains unchanged.

## 2026-09-05 — Removing an expert copy can increase total work latency

AW-0030's standalone Metal probe validates input bytes and GPU scan results.
Short-lived direct mappings lost to concurrent pread copies. Retained mappings
showed a small win on a reused64-expert set, then lost on128-expert churn under
a64-mapping budget. Strict-cap repeat:66–70ms mapped versus44–45ms copied.
All timed arms reported zero disk-read bytes; lower fetch setup moved cost to
command completion waits outside the measured GPU kernel interval. The exact
VM/driver cause remains unproven. Do not integrate this transport or claim
agentic speedup. P1 remains unchanged; actual routed-access/physical-I/O traces
are needed to choose the next structural experiment. Locality-specific wins
are not accepted as general agent improvements.

## 2026-09-05 — Real routing reveals sustained disk demand and weak adjacent reuse

AW-0031's isolated trace captures 2120 actual token-layer routes and 1000 cache
batches; hashes, route/batch reconciliation and exact LFU replay pass. Same
output and hit/miss counts with trace off/on/off. Model-step tracing overhead
observed 1.5–2.4%; not a performance win. Process-attributed disk reads 21–22 GiB
versus 28.79 GiB logical expert reads show the warm mapping microbench was missing
real I/O demand. Cache selection 58 ms is tiny next to 6.98 seconds read batches.
Each decoded step requests 320 layer/expert pairs (~1 GiB), with mean 29.9%
adjacent-step overlap. A doubled cache removes only 9.2% logical reads in fixed-
route replay, without accounting for OS residency or pressure. Keep P1 unchanged.
Use actual routing/I/O traces for further transport work; reducing expert bytes
or overlapping reads merits investigation with capability gates, not narrower
agent behavior. All raw traces, isolated patch and failed relocated-cache build
are preserved in AW-0031. Process disk accounting is not per-expert media I/O.

## 2026-09-05 — Four-read cap fails the real-route transport replay

AW-0032 replays all 1,000 actual miss batches across 40 layers with GPU scans
consuming every word. Interleaved full/4/full/4/full dispatch yields candidate
wall times 1.60% and 2.59% above bracketed controls. Scan outputs match; pressure
1 and no swap growth. Reject this concurrency cap for now. Every arm incurs
about 16 GiB of process-attributed disk reads, so this exercises real I/O rather
than the earlier hot mapping set. It still differs from full inference: staging
buffers, no retained LFU contents or model state, scan rather than matrix work,
and reference output storage affect residency. The ~16 versus ~21–22 GiB disk
read difference reinforces that replay is a filter, not endpoint evidence.
Preserve the replay for further layout/transport experiments; P1 unchanged.

## 2026-09-05 — P2 needs executable savings and broader capability evidence

The P2 campaign contract preserves P1 and requires 25% greater verified utility
per hour in two interleaved comparisons, no loss of control-solved tasks, and
an expanded 24-task evaluation including 16 held-out tasks. Corpus construction
and freeze remain pending; this is not an implemented acceptance check yet.
Prismwing and Firewing teach separate SSD/decode/install/executable-memory
accounting and representative routed plus candidate-accumulated fidelity.
AW-0033 rejects raw/even-odd zlib-1 as half-size representations on 12 selected
real experts (best page-aligned ratios 60.29%/60.78%). All round trips pass.
At AW-0031's 36.63% read fraction, halving read time alone gives only 1.224x;
this is a conditional model-step calculation, not a general endpoint bound.
Do not promise the goal from smaller files alone. Direct execution savings and
broader workload measurements remain necessary. P1 is unchanged.

## 2026-09-05 — P2 independent capability grading begins

AW-0034 adds the first three development repositories and external behavioral
authorities: deployment precedence, interval debugging, and API/CLI pagination.
All three pristine and incomplete repairs fail; reference repairs pass; deleting
visible tests does not grant success. The grader copies submissions and drains
owned processes. This is authority validation, not model capability evidence.
The panel is explicitly incomplete and unfrozen: five development and sixteen
held-out tasks, run integration and control measurements remain. P1 is unchanged.

## 2026-09-05 — All eight P2 development categories have audited authorities

AW-0034 now covers refactoring, tool recovery, data processing, configuration
migration and longer investigation in addition to its first three categories.
All eight pristine/test-deletion cases fail, reference repairs pass, and
syntax-valid incomplete semantic repairs fail. Initial newline-generation bugs
in two graders were caught and preserved before any model run. This completes
the development-category scaffold, not the 24-task panel: sixteen substantively
distinct held-out tasks and full-path integration remain. Corpus is not frozen.

## 2026-09-05 — Full P2 capability corpus is frozen before model comparisons

AW-0034 now contains all 24 tasks, eight development and sixteen held out across
eight categories. Every independent authority accepts its reference and rejects
pristine and semantic-mutant submissions. A 215-file receipt pins inputs and
authorities; copied-tree checks reject changed, additional and missing inputs.
Fixture-generation failures were preserved and repaired before any model run.
No held-out model outcomes have been observed or used for tuning. Corpus coverage
is local and authored, not universal capability evidence. Next: full-path runner
integration and development-only P1 measurements while representation work proceeds.
P1's original frozen inputs remain intact.

## 2026-09-05 — P2 development runner reaches live P1 execution

AW-0035 adds a development-only adapter around P1's unchanged execution and task
boundary. It verifies the frozen corpus, refuses held-out selection, uses fresh
model/workspace state per task, charges full wall and independently grades output.
Initial tests reject malformed event pairing, model errors and reused state.
A first dev-debugging run is active with stable host readings; completion and
utility are not yet established. Full paired promotion support remains separate.

## 2026-09-05 — Broader development task exposes P1 output-budget failure

AW-0035 dev-debugging earns 0/1 in 773.7 seconds. P1 reads the repository and
reproduces both visible failures, then spends 512 generated tokens explaining
and drafting a repair that truncates inside a tool call. The server rejects it;
source remains unchanged. Independent failure replay passes; pressure 1, swap
0 growth and post-run preflight pass. This is a measured limit of P1 beyond its
original suite, not a reason to narrow tasks or silently change the comparison.
Preserve this failure while proceeding with the representation/capability campaign.

## 2026-09-05 — Real multi-layer activation fixtures admitted

AW-0036's isolated observer preserves greedy outputs and route sequences in nine
control/capture/control runs across coding, arithmetic and structured prompts.
All 72 exact-bit input/weight records reconcile to source layer/position routes:
576 selections, 250 distinct layer/expert identities, layers 0/20/39, prefill and
single-token coverage. Pressure 1, zero swap growth, P1 preflight passes after
cleanup. These are source fixtures, not quantization or agent-performance gains.
Use original fast8 GPU execution to establish the next projection/mixture rung;
production rarity and candidate-accumulated behavior remain unresolved.

## 2026-09-05 — Original fast8 projection/mixture references pass independent checks

AW-0037 replays all 72 real input fixtures and 576 experts using P1's original
Metal kernels. Independent double dequantization/projection checks differ by at
most 7.42e-6 relative L2; SwiGLU and isolated routed-mixture discrepancies are
1.21e-7 and 7.63e-8, below the predeclared 1e-4 implementation gate. Raw F32 stages
and source hashes are preserved and audited. This resolves a reference needed
for recoding tests, not full-model parity or smaller-representation fidelity.
A compiler macro-name collision was repaired and its failed build preserved.
Pressure 1, swap growth 0 and post-run P1 preflight pass. Next compare executable
recodings against these source references before any bank conversion.

## 2026-09-05 — First direct four-bit representation rejected before bank conversion

AW-0038 maps each source group64 q8 code to q4 with a BF16 scale-times-17
adjustment, using the original fast4 kernel. Artifact bytes fall to 52.94% of P1,
but 71/72 source-activation mixtures exceed the predeclared 5% relative-L2 screen;
the maximum is 38.67%. 473/576 expert-down outputs exceed 10%. Independent
candidate arithmetic checks pass (maximum projection error 4.293e-6), so the
observed discrepancy belongs to this representation rather than a broken
implementation. Reject this form; preserve the references and negative evidence.
No accumulated-model or agent-capability conclusion follows, and other four-bit
forms remain untested. Source-sized diagnostic buffers and on-the-fly recoding
do not establish physical residency or throughput savings. Pressure 1, zero swap
growth, and post-run P1 preflight pass. No production or frozen input changed.

## 2026-09-05 — Causal expert submission clears a cached integrity screen

AW-0039 launches eight original expert reads together and submits each expert's
GPU chain after its own read completes, retaining original routed order. All
2,880 executions across C/A/C/A/C reproduce AW-0037 stage hashes exactly. The
candidate uses 89.46% and 89.04% of neighboring-control mean wall time in this
small cached diagnostic. All input-block deltas are zero; no SSD or endpoint
gain is established. The diagnostic omits production LFU/shared/chunk scheduling,
and its control groups operations differently from P1. Retain for isolated
runtime investigation, preserving those costs and comparing real trajectories.
Pressure 1, zero swap growth, post-run P1 preflight passes. This changes execution
submission only; it removes no expert bytes and supplies no representation gain.

## 2026-09-06 — Runtime overlap survives real disk traffic and short trajectories

AW-0040 integrates opt-in single-token read/compute overlap in isolated Swiftlet
revision 2340281. Eleven focused tests pass, including cancellation after GPU
submission and fresh-state recovery. Nine three-prompt C/A/C runs preserve text,
every route and all cache decisions. Candidate decode time is 88.54%, 88.80%,
and 80.38% of neighboring-control means; full-process wall is 84.74%, 98.25%,
and 83.04%. Observed disk traffic is substantial (12.53–16.86 GiB/arm), unlike the
cached AW-0039 screen. Pressure 1, zero swap growth and P1 preflight pass.
Retain this mechanism, not promote: logical expert bytes are unchanged, startup
and OS residency vary, and only short development trajectories were exercised.
Chunked prefill remains original; extra submissions and shared-memory traffic
must stay charged. Broader capability and >=25% verified utility/hour remain
unproven. Initial test-fixture and command-directory failures are preserved.

## 2026-09-06 — Chunk gate/up overlap adds a viable prefill path

AW-0041 retains token-batched gate/up projections while submitting each union
expert as its read becomes ready. Original SwiGLU/down/shared/accumulation stay
deferred. Thirteen focused tests pass, including chunk cancellation and recovery;
a missing cancellation-parameter build failure is preserved. Three short C/A/C
comparisons with both overlap paths preserve text, routes and every cache decision.
Prefill wall ratios are 0.905/0.913/0.892, decode 0.792/0.808/0.819 and full-process
wall 0.810/0.821/0.815. Pressure 1, zero swap growth, P1 preflight passes.
Retain revision d44752e for longer/uncommon accumulated-trajectory checks. Its
roughly 1.22–1.23x diagnostic speedup is not the 1.25x autonomous utility goal.
Expert bytes are unchanged; sampled disk and startup variation prevent assigning
all full-wall savings to overlap. No held-out execution or promotion occurred.

## 2026-09-06 — Accumulated overlap checks pass, but longer speed gains shrink

AW-0042 compares two new 64-token development trajectories with checkpoints at
layers 0/20/39 through decode ordinal 63. All 171 records across six arms match
corresponding input/weight bit patterns; text, full routing and cache decisions
also match. Captures include 55/67 identities outside AW-0036 fixtures and 32/50
absent from AW-0031, plus historically infrequent identities. These are explicit
historical coverage measures, not exhaustive rarity or general capability proof.
Full-wall candidate ratios are 0.891 and 0.895; decode ratios about 0.846/0.849.
Thus longer trajectories weaken the performance extrapolation from AW-0041's
short runs: roughly 1.12x full-process speedup remains well below the 1.25x
utility objective. Retain the exact mechanism, pursue further cost reduction,
and keep expensive promotion comparisons pending a stronger performance case.
Pressure 1, zero swap growth, P1 preflight passes; no held-out exposure. Candidate
observer revision f0ae501 and all setup/build/evidence provenance are preserved.

## 2026-09-06 — Complete chunk expert overlap survives accumulated checks

AW-0043 adds an indexed SwiGLU batch so each ready prefill expert can execute its
whole chain while preserving token-batched GEMVs and final sum order. Fifteen
focused tests pass. Six longer C/A/C runs retain all 171 activation records,
outputs, routes and cache decisions exactly. Full-wall ratios are 0.842/0.870,
prefill 0.895/0.909 and decode 0.830/0.821. Pressure 1, zero swap growth; P1 and
corpus preflight pass. Retain e707647 for a development agent comparison, not
promotion: approximately 1.15–1.19x model-process speedup still does not establish
the >=1.25x utility goal. The increment over prior runs is not causally isolated
from OS/startup variation, and expert bytes are unchanged. AW-0044 will test the
actual tool-driven path with an explicitly pinned server and kernel resource.

## 2026-09-06 — First navigation control fails evidence contract and exposes prefix refill

AW-0044 C1 finishes normally in 1617.62 seconds but scores 0: its evidence list
substitutes config/edge.json for required deploy/launch.sh. Eleven valid tool
calls, no tool errors/repeats, protocol pass, pressure 1 and zero swap growth do
not imply task success. Independent grader replay preserves the failure.
The final request re-prefills 2425 tokens despite a 2237-token common prefix;
TTFT is 654.1 seconds. SwiftletSession only reuses an entire matching cached
sequence for tools, so a partial match cannot restore state. The particular
mismatch still needs tracing. This identifies potentially large redundant model
work without narrowing agent capability; keep it separate from the ongoing fixed
AW-0044 comparison. Candidate A1 is now active; no relative utility result yet.

## 2026-09-06 — Agent candidate exposes an oversized expert union

AW-0044 A1 ends in 1181.98 seconds with utility 0. It repeats C1's evidence-set
error and fails protocol completion: the final request asks for 161 experts in
a cache with 160 physical slots. Pressure 1 and zero swap growth pass, but the
model-error and terminal-metric gates fail. Shorter elapsed time cannot be called
a speedup. The whole-batch-fit assumption is inherited from P1; attribution of
this particular union to path/context variation versus arithmetic remains open.
Full expert-chain execution offers a possible bounded-memory repair: drain a
subset before reusing its cache slots, while keeping routed output and final
accumulation order. Increasing memory or narrowing tasks is not required by that
design. No repair is implemented yet; finish fixed C2 before follow-up builds.

## 2026-09-06 — Completed development comparison establishes no utility gain

AW-0044 C2 finishes in 1476.44 seconds with utility 0 on the same evidence-set
contract, ten valid tool calls, passing protocol, pressure 1 and 0.75 MiB swap
growth. Its final 2234-token full refill costs 599.4 seconds TTFT despite 2046
matched tokens. All three records pass independent integrity/grader replay;
all three utilities are zero, so no finite utility-rate improvement is established.
A1's shorter failed execution cannot supply a speedup. Its protocol error rejects
promotion; the overlap mechanism remains available for isolated repair. The
repeated large prefix refill strengthens the priority of historical-token replay
investigation, while its exact causal mismatch remains unproven. P1 preflight
passes after cleanup. No held-out execution or acceptance threshold changed.

## 2026-09-06 — Historical tool replay removes a reproduced token rewrite

AW-0045 confirms that a second accepted reply displaces the first in the original
cache. Bounded history retention passes 39 focused tests and the real tokenizer:
a constructed noncanonical earlier reply changes a 281-token history to 291
tokens in original mode (247-token common prefix), while history mode retains
all 281 tokens and exactly renders both accepted raw replies. Strict call and
visible-content bindings plus byte/count eviction preserve fallback semantics.
This supports removing redundant prefill as a real mechanism without restricting
agent work. It does not identify the exact C1/C2 mismatch or prove saved task
time, RSS bounds, accumulated model behavior or capability. Retain isolated
0843311 for further validation; no promotion. Build/test fixture failures,
reconstructed patch and tokenizer/source/binary hashes are preserved; P1 passes
preflight after tests.

## 2026-09-06 — Oversized-cache errors can poison recovery; bounded repair passes

AW-0046's real-cache falsifier confirms that a rejected 161-expert cold batch
leaves 160 keys pointing at unread buffers. A subsequent fetch falsely hits and
returns bytes unequal to disk. This is an inherited selection-error cleanup gap,
separate from windowed execution. Cleanup now invalidates pending fills across
every throwing exit; the same test leaves zero stale entries and recovers exact
disk bytes, with the unchanged 534,773,760-byte physical allocation/160 slots.
Eighteen tests pass, including forced tiny-model window trajectories, cancellation
and original cache/scheduling checks. Retain isolated 62e4a08; a full-model union
larger than 160 still needs functional validation. No real-agent repair, utility
gain or promotion is established by these tests. Failed evidence, reconstruction
and source/binary hashes are preserved; P1 preflight passes afterward.

## 2026-09-06 — Real-model streaming crosses the physical cache boundary exactly

AW-0046's synthetic full-model C/A/C diagnostic reaches five unions above 160,
maximum 217. At the unchanged 0.5 GiB budget, candidate executes 33 drained
windows and matches all nine complete logit vectors, 10,560 route records per
arm, union sets and eight greedy continuation tokens against both references.
The functional references use 1 GiB and all arms a diagnostic 256-token chunk;
their timings are not comparable endpoint or production-throughput evidence.
Pressure 1, zero swap growth and P1 preflight pass. This validates actual
oversized-union streaming, beyond the previous forced tiny-model test, while
ordinary accumulated trajectories and tool-driven capability remain required.

## 2026-09-06 — Streaming repair preserves ordinary accumulated trajectories

AW-0046's ordinary Rust/Unicode C/A/C runs match text, complete routes and cache
decisions, and all 171 sampled accumulated activations exactly. Candidate wall
ratios are 0.831/0.893 with pressure 1 and no swap growth; they are model-only
diagnostics. Combined with the separate real oversized-union boundary check,
this supports integrating the repair with AW-0045 historical replay for tool
evaluation. It does not yet establish repaired autonomous capability or utility.

## 2026-09-06 — P1 establishes a successful expanded recovery control

AW-0047 recovery C1 independently scores 1 in 1415.47 seconds. It recovers from
its own invalid Python API repair, completes validation and documentation, and
passes protocol with 18 tool calls, two failures and three repeated commands.
Pressure 1, zero swap growth, integrity/grader replay and post-run P1 preflight
pass. This is demonstrated development-task success to preserve, not a candidate
gain. The frozen joint candidate has not run yet.

## 2026-09-06 — Joint candidate loses the solved recovery task

AW-0047 recovery A1 finishes in 630.19 seconds but scores 0: unnecessary NFKD
decomposition violates accented-character preservation despite passing the local
validator. Protocol, pressure 1 and zero swap growth pass. Eleven tool calls and
one failure replace C1's 18/two, but lost verified utility disqualifies the apparent
elapsed-time saving. Preserve the semantic failure and the successful P1 outcome;
do not weaken Unicode grading or infer general capability from protocol success.
Specific attribution to history retention versus different path/context tokens
remains open. Continue the frozen comparison unchanged; no promotion claim.

## 2026-09-06 — Both recovery controls succeed; joint candidate fails preservation

AW-0047 recovery C2 scores 1 in 1163.16 seconds, with protocol pass, pressure 1
and 1.06 MiB swap growth. Independent three-arm audit confirms C1=1, A1=0, C2=1.
The candidate utility-rate ratio is zero and solved-task preservation fails;
reject promotion despite a much shorter candidate run. Both controls' repeated
validation and error correction are charged. Continue the frozen multi-file
diagnostic unchanged; additional results cannot erase this failed requirement.

## 2026-09-06 — Recovery divergence follows a visible workspace-path difference

Independent completed-trace audit finds identical first-seven commands and
structured assistant contents (ignoring generated call IDs) across recovery
C1/A1/C2. First-six tool results match exactly; seventh results differ only in
the workspace path. First repair commands then differ across all three runs.
This supports testing stable paths as a measurement-control improvement, not
blaming or exonerating the runtime: exact wire tokens and raw accepted spellings
were not captured. Candidate grade 0 and failed preservation remain unchanged.
Do not alter the ongoing fixed multi-file comparison or weaken the verifier.

## 2026-09-06 — Multi-file code passes but final tool protocol fails

AW-0047 multi-file C1 saves code that independently grades 1, then emits a
repetitive 512-token test-writing block without completing its tool call. Strict
parser rejection and assistant error correctly reduce accepted utility to 0
after 1152.77 seconds. Ten earlier tool calls, pressure 1 and zero swap growth
do not override the protocol gate. The declared stop policy leaves multi-file
A1/C2 unattempted; their results must not be inferred. AW-0047 is terminal with
the joint candidate rejected on recovery preservation, not a completed goal.
Preserve artifact-only success separately from fully valid autonomous completion.

## 2026-09-06 — Fixed-path recovery control succeeds and still incurs a full refill

AW-0048 C1 scores 1 in 1163.36 seconds with 12 tool calls, protocol pass,
pressure 1 and no swap growth. Receipt/grader replay, frozen harness pins,
actual fixed cwd and workspace/private-state archival pass. Its first repair
passes validation without the earlier controls' invalid Unicode API detour.
One subsequent 1561-token full refill costs 405.6 seconds TTFT despite 1466
matching prefix tokens. Fixed paths remove one between-arm input difference;
this single control cannot prove causality, determinism or candidate utility.
Continue the unchanged frozen A1/C2 sequence. AW-0047's negative result remains.

## 2026-09-06 — Fixed-path candidate preserves recovery success and avoids refill

AW-0048 A1 scores 1 in 645.06 seconds, with protocol pass, pressure 1 and zero
swap growth. Receipt/grader replay and source/profile/path checks pass. Its first
18 structured visible events match C1, including the repair and validation.
The next command also matches, while narration differs: A1 reuses 1540 tokens
and processes 21 new ones in 5.4 seconds TTFT, versus C1's 1561-token full refill
and 405.6 seconds. The preliminary single-control utility-rate ratio is 1.80x.
This supports the redundant-prefill mechanism in a successful agent task without
narrowing work. C2, broader capability and replicated promotion accounting are
still required; AW-0047's negative result remains unchanged.

## 2026-09-06 — Fixed-path recovery comparison closes with preserved utility

AW-0048 C2 scores 1 in 1167.82 seconds, protocol pass, pressure 1 and zero swap
growth. Both controls' complete 25-event structured visible transcripts match
after removing call IDs; their first repairs agree, supporting the declared
repeatability diagnostic. C2 repeats the 1561-token refill at 408.3 seconds TTFT.
All three receipts, grades, configuration pins, paths and run order audit cleanly.
With all utilities equal to 1, candidate utility/hour is 1.80695x the pooled
controls. This is positive task-level development evidence for avoiding redundant
prefill, not broad generalization or promotion. Retain the candidate and fixed
workspace harness for the other development categories. Keep AW-0047's negative
result and require the original suite, held-out panel and replicated full-path
acceptance before declaring the project goal achieved.

## 2026-09-06 — Broader task still degenerates with prefix replay working

AW-0049 dev-multi-file fails in 866.45 seconds: the final response reuses 2198
tokens with only 21 new prompt tokens and 5.3 seconds TTFT, then repeats test
definitions through the 512-token cap without closing its tool call. Protocol
rejection is correct. The saved API also accepts Boolean True as a limit, so
the independent artifact grader scores 0. Pressure 1 and zero swap growth pass;
record/configuration audits preserve the failure. The frozen stop leaves six
later development tasks unattempted. AW-0048's 1.807x recovery gain remains, but
removing redundant prefill does not solve long code-generation degeneration.

## 2026-09-06 — Functional grading does not cover every requested artifact

The multi-file prompt asks for added regression coverage; its frozen grader
checks API/CLI behavior without executing or inspecting submitted tests.
AW-0050 confirms AW-0049 left the original test unchanged. Both submitted and
original tests pass even when opt-in archived inclusion is broken in a copy.
A synthetic added assertion kills that same verified mutation, validating the
auditor's positive path. All real source receipts remain intact and frozen
scores unchanged. Full acceptance needs explicit evidence for requested tests
and other artifacts beyond whichever behaviors a grader happens to check.

## 2026-09-06 — Sampling trace reproduces failure and implicates newline penalties

AW-0051 reproduces AW-0049's complete structured visible trajectory and rejected
output. All 1439 decisions across 13 requests pass trace, finite-logit, selected
score arithmetic, argmax and mask checks. Accepted utility remains 0 after
874.13 seconds; pressure 1 and zero swap growth pass. In the final 512-token
response, penalties change the raw winner 29 times, displacing a newline 22
times. At position 302, 25 earlier newlines subtract 12.5 from its raw score,
leading into redundant expressions and later repeated definitions. This
supersedes any presumption that correctly implemented repetition penalties are
necessarily suitable for code. It does not establish counterfactual causality:
test reduced penalty on the captured input, first checking that fresh-prefill
control reproduces the incrementally cached failure. No promotion or frozen
sampling/acceptance changes follow from this diagnostic.

## 2026-09-06 — SwiftPM testing helpers can escape wrapper process groups

AW-0052 launch inspection found swift-test's model-owning testing helper in a
separate process group. Wrapper-group cleanup alone was insufficient. Stopped
and retained the 39.03-second attempt with pressure 1 and no swap growth before
interpreting model results. Launch the pinned helper directly as the process
owner, supply its Testing framework path, and verify ownership on the real run.
Prior completed diagnostic probes are not thereby shown contaminated, but
future timeout guarantees must follow the actual model owner rather than the
SwiftPM wrapper. P1's server/Pi runner is unchanged.
