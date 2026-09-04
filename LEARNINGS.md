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
