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
