# AW-0055 — Explicit truncation feedback before runtime integration

## Hypothesis and scope

One explicit notification of a rejected, unexecuted truncated response induces
a complete smaller tool call that makes concrete progress on the remaining
work. Test on the captured AW-0054 failure with the original 512-token ceiling
and zero frequency penalty. This is a single model-only recovery falsifier,
not a server implementation, full-task success, speed comparison or promotion.

## Exact input construction

Preserve AW-0054 request 12's actual prompt IDs followed by all 512 generated
IDs from its rejected response. No command from that response was executed.
Append the model template's assistant-message terminator, then a user-role
runtime-feedback turn from `config/truncation-feedback.txt`, followed by the
normal non-thinking assistant generation prefix. Use the real tokenizer and
chat template. A tokenizer-only preparation test must prove its rendered
feedback suffix equals the explicit template spelling before any model run.
Record original IDs, suffix IDs and prepared input outside Git, with hashes.
This is an explicit internal feedback message in a diagnostic, not a claim
that the human user wrote it or that a tool returned it.

Keep the original prefix byte/token-identical, including the unfinished tool
markup. Do not salvage or execute that markup. The new response must contain
its own complete tool block; continuing only the old command is failure. Use
fresh prefill of the prepared IDs. It is not asserted identical to future live
cached-state recovery, which would require separate verification and accounting.

## Fixed settings and primary diagnostic

Same frozen q8 qpack, tokenizer, M1/internal SSD, 0.5 GiB expert cache, joint
runtime core, temperature 0, presence 0, frequency 0, no-repeat-ngram 0,
minNew 8, suppressed/EOS tokens and complete-tool boundary stop. Requested
output ceiling 512, diagnostic deadline 1800 seconds, existing pressure/swap
gates. No model or heavy build concurrently. Use the directly owned testing
helper and opt-in sampling trace. No executable tools or network listener.

Primary diagnostic: the unchanged parser accepts a new complete declared bash
call within 512 tokens, and independent source review finds concrete useful
progress on remaining work. A partial continuation, empty/no-op call, fabricated
validation claim, or dropping required remaining work is not success. The
probe may produce one portion of the requested tests because subsequent calls
remain available; full requested coverage is still mandatory for any later
endpoint evaluation. No model-generated command is executed in this probe.

## Cheap checks and stop

Prepare suffix with tokenizer only, verify exact prefix preservation and
round-trip/template boundaries, build release with two jobs, run focused
session/observer checks, then freeze source/binary/input/helper/runner pins.
One attempted feedback generation only. Stop on host/deadline failure and
preserve it; do not tune feedback after observing output in this experiment.
If it fails, reject this exact feedback strategy. If it passes, retain only as
a possible recovery component requiring runtime integration tests, complete
cost accounting, full autonomous development tasks and all promotion gates.

## Limitations and acceptance

This changes the diagnostic conversation by adding explicit failure feedback.
It does not change frozen P1, corpus, graders or acceptance. Any future recovery
implementation must expose attempted/rejected calls, prohibit partial execution,
bind accepted history correctly and charge retries/refills. Matched-prompt and
sampling requirements for promotion remain unresolved for changed configurations;
this diagnostic alone cannot satisfy or override them.

## Status

Preparation; no model execution yet.
