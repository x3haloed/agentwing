import Foundation
import Testing
@testable import SwiftletCore

@Suite struct FullChunkOverlapTests {
    @Test func chunkBoundariesAndDecodeRemainBitIdentical() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let model = try QwenMetalModel(modelDir: out, cacheBudgetGB: 0.05)
        model.prefillMode = .layerMajor(chunkTokens: 3)
        var results: [[UInt32]] = []
        var observed: [[Int]] = []
        model.routedExpertObserver = { layer, experts in observed.append([layer] + experts) }
        for enabled in [false, true, false] {
            model.overlapChunkFull = enabled
            model.overlapExperts = enabled
            let state = QwenCPUModel.DecodeState()
            observed = []
            var logits = try model.step([1, 5, 9, 2, 4, 7, 3], state: state)
            for token in [6, 8, 2] { logits += try model.step([token], state: state) }
            results.append(logits.map(\.bitPattern))
            if enabled { #expect(!observed.isEmpty) }
        }
        #expect(results[0] == results[1] && results[1] == results[2])
    }

    @Test func cancellationInsideChunkSubmissionDrains() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let model = try QwenMetalModel(modelDir: out, cacheBudgetGB: 0.05)
        model.overlapChunkFull = true
        model.prefillMode = .layerMajor(chunkTokens: 4)
        var routed = false
        var checks = 0
        model.prefillExpertUnionObserver = { _, _ in routed = true }
        #expect(throws: GenerationInterruption.cancelled) {
            try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState(), shouldCancel: {
                if routed { checks += 1 }
                return checks >= 2
            })
        }
        #expect(checks == 2)
        model.prefillExpertUnionObserver = nil
        let recovered = try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState())
        model.overlapChunkFull = false
        let control = try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState())
        #expect(recovered.map(\.bitPattern) == control.map(\.bitPattern))
    }
}
