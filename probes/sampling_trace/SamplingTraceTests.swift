import Foundation
import Testing
@testable import SwiftletCore

@Suite struct SamplingTraceTests {
    private final class ProbeModel: InferenceModel, @unchecked Sendable {
        let config: QwenConfig
        let modelDir: URL
        let contextCapacity = 128
        private let lock = NSLock()
        private var callsStorage: [[Int]] = []
        var calls: [[Int]] { lock.lock(); defer { lock.unlock() }; return callsStorage }
        init() throws {
            modelDir = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
                .deletingLastPathComponent().deletingLastPathComponent()
                .appendingPathComponent("fixtures/tiny-model")
            config = try QwenConfig(url: modelDir.appendingPathComponent("config.json"))
        }
        func step(_ tokens: [Int], state: QwenCPUModel.DecodeState) throws -> [Float] {
            lock.lock(); callsStorage.append(tokens); lock.unlock()
            state.position += tokens.count
            var logits = [Float](repeating: 0, count: config.vocabSize)
            logits[65 + state.position % 3] = 10
            return logits
        }
    }

    @Test func observerDoesNotChangeSessionCallsOrText() async throws {
        func session(_ model: ProbeModel) -> SwiftletSession {
            SwiftletSession(testingModel: model, modelDir: model.modelDir,
                encodeText: { _ in [10,11,12] },
                decodeTokens: { String(String.UnicodeScalarView($0.compactMap { Unicode.Scalar($0) })) },
                renderMessages: { _ in [10,11,12] })
        }
        func collect(_ session: SwiftletSession) async throws -> String {
            var options = SwiftletSession.GenerationOptions.greedy
            options.minNew = 0; options.noRepeatNGram = 0
            var output = ""
            for try await delta in session.streamChat(messages: [["role":"user","content":"test"]], maxNew:12, options:options) { output += delta }
            return output
        }
        let offModel = try ProbeModel(), onModel = try ProbeModel()
        let off = session(offModel), on = session(onModel)
        off.samplingTrace = nil
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: url) }
        on.samplingTrace = try SamplingTrace(path: url.path)
        let offText = try await collect(off), onText = try await collect(on)
        #expect(offText == onText)
        #expect(offModel.calls == onModel.calls)
        #expect(off.lastMetrics.generatedTokens == on.lastMetrics.generatedTokens)
        let rows = try String(contentsOf: url, encoding: .utf8).split(separator: "\n").map {
            try #require(JSONSerialization.jsonObject(with: Data($0.utf8)) as? [String:Any])
        }
        #expect(rows.count == 14)
        #expect(rows.first?["actual_prompt_ids"] as? [Int] == [10,11,12])
        #expect(rows.last?["text"] as? String == onText)
    }

    @Test func boundedRankingAndNonfiniteSerialization() throws {
        let values: [Float] = [0, 5, 5, .nan, .infinity, -.infinity, 1, 2, 3, 4, 6, 7]
        let record = SamplingTrace.describe(values, vocabulary: values.count)
        let top = try #require(record["top"] as? [[String: Any]])
        #expect(top.compactMap { $0["id"] as? Int } == [4,11,10,1,2,9,8,7])
        #expect(record["nonfinite"] as? Int == 3)
        #expect(record["finite_min"] as? Double == 0)
        #expect(record["finite_max"] as? Double == 7)
        _ = try JSONSerialization.data(withJSONObject: record)
    }

    @Test func noOverwriteAndExactDecisionFields() throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: url) }
        let trace = try SamplingTrace(path: url.path)
        let id = trace.begin(["actual_prompt_ids": [10,11], "frequency_penalty": 0.5])
        let raw: [Float] = [1,4,3]; let adjusted: [Float] = [1,2,3]
        trace.decision(request: id, generated: 4, raw: raw, adjusted: adjusted,
                       vocabulary: 3, selected: 2, seen: 0, banEOS: false, isEOS: false)
        trace.end(request: id, generated: [2], text: "x", reason: "length", cached: 3)
        let before = try Data(contentsOf: url)
        #expect(throws: (any Error).self) { _ = try SamplingTrace(path: url.path) }
        #expect(try Data(contentsOf: url) == before)
        let rows = try String(decoding: before, as: UTF8.self).split(separator: "\n").map {
            try #require(JSONSerialization.jsonObject(with: Data($0.utf8)) as? [String: Any])
        }
        #expect(rows.count == 3)
        #expect(rows[1]["selected"] as? Int == 2)
        #expect(rows[1]["generated_before"] as? Int == 4)
        #expect(rows[1]["selected_raw"] as? Double == 3)
        #expect(rows[2]["generated_ids"] as? [Int] == [2])
        #expect(raw == [1,4,3] && adjusted == [1,2,3])
    }
}
