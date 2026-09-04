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
