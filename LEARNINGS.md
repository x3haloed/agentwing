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
