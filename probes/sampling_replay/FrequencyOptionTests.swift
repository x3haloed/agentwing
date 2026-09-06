import Foundation
import Testing
@testable import SwiftletServer

@Suite struct FrequencyOptionTests {
    @Test func optInChangesOnlyFrequencyAndDefaultIsPreserved() throws {
        for temperature in [0.0, 0.7] {
            let data = try JSONSerialization.data(withJSONObject: ["messages": [["role": "user", "content": "hello"]], "temperature": temperature])
            let request = try JSONDecoder().decode(ChatRequest.self, from: data)
            let baseline = request.generationOptions(allowRepeatedNGrams: true, stopAfterToolCall: true)
            let candidate = request.generationOptions(allowRepeatedNGrams: true, stopAfterToolCall: true, zeroFrequencyPenalty: true)
            #expect(baseline.frequencyPenalty == 0.5)
            #expect(candidate.frequencyPenalty == 0)
            #expect(candidate.temperature == baseline.temperature)
            #expect(candidate.presencePenalty == baseline.presencePenalty)
            #expect(candidate.noRepeatNGram == baseline.noRepeatNGram)
            #expect(candidate.minNew == baseline.minNew)
            #expect(candidate.topK == baseline.topK)
            #expect(candidate.topP == baseline.topP)
            #expect(candidate.stopSequences == baseline.stopSequences)
            #expect(candidate.stopAfterSequences == baseline.stopAfterSequences)
        }
    }
}
