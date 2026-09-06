#!/usr/bin/env python3
"""Apply opt-in AW-0051 observation hooks to its isolated runtime only."""
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CHECKOUT=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0051')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip()=='4dff62e867d62288d4224974c4add523dad50437'
p=CHECKOUT/'Sources/SwiftletCore/SwiftletSession.swift';source=p.read_text()
def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)
replace('    private let suppressedIds: Set<Int>',
        '    var samplingTrace = SamplingTrace.fromEnvironment()\n\n    private let suppressedIds: Set<Int>')
replace('generated: [Int], seen: [Int: Int], banEOS: Bool) -> Int {',
        'generated: [Int], seen: [Int: Int], banEOS: Bool, traceRequest: Int? = nil) -> Int {')
replace('            return best\n        }\n        // Partial top-k',
'''            samplingTrace?.decision(request: traceRequest, generated: generated.count,
                raw: logitsIn, adjusted: logits, vocabulary: vocab, selected: best,
                seen: seen[best, default: 0], banEOS: banEOS, isEOS: generator.eosTokens.contains(best))
            return best
        }
        // Partial top-k''')
replace('                    let start = Date()\n                    var firstTokenAt:',
'''                    let traceRequest = self.samplingTrace?.begin([
                        "actual_prompt_ids": tokensBeforeGeneration, "rendered_prompt_ids": fullPrompt,
                        "new_prompt_tokens": suffix.count, "reused_prompt_tokens": reusedPromptTokens,
                        "matched_prompt_tokens": matchedPromptTokens, "admitted_max_new": admittedMaxNew,
                        "temperature": options.temperature, "frequency_penalty": options.frequencyPenalty,
                        "presence_penalty": options.presencePenalty, "no_repeat_ngram": options.noRepeatNGram,
                        "min_new": options.minNew, "top_k": options.topK, "top_p": options.topP,
                        "eos_ids": self.generator.eosTokens.sorted(), "suppressed_ids": self.suppressedIds.sorted(),
                        "stop_sequences": options.stopSequences, "stop_after_sequences": options.stopAfterSequences,
                        "greedy_observation_supported": options.temperature <= 0
                    ])
                    let start = Date()
                    var firstTokenAt:''')
replace('seen: generatedCounts, banEOS: !eosAllowed\n',
        'seen: generatedCounts, banEOS: !eosAllowed, traceRequest: traceRequest\n')
replace('                    self.storeMetrics(Metrics(\n                        promptTokens: suffix.count,',
'''                    self.samplingTrace?.end(request: traceRequest, generated: generated,
                        text: stopFilter.output, reason: finishReason.rawValue, cached: self.cachedTokens.count)
                    self.storeMetrics(Metrics(
                        promptTokens: suffix.count,''')
p.write_text(source)
shutil.copyfile(ROOT/'probes/sampling_trace/SamplingTrace.swift',CHECKOUT/'Sources/SwiftletCore/SamplingTrace.swift')
shutil.copyfile(ROOT/'probes/sampling_trace/SamplingTraceTests.swift',CHECKOUT/'Tests/SwiftletCoreTests/SamplingTraceTests.swift')
print('Applied observer without changing sampling choices or runtime settings')
