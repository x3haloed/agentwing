import Foundation
import Testing
@testable import SwiftletCore

@Suite struct OversizedUnionTests {
    @Test func forcedWindowsPreserveWholeTrajectory() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let model = try QwenMetalModel(modelDir: out, cacheBudgetGB: 0.05)
        model.prefillMode = .layerMajor(chunkTokens: 4)
        model.overlapChunkFull = true
        let controlState = QwenCPUModel.DecodeState()
        var control = try model.step([1, 5, 9, 2, 4, 7, 3], state: controlState)
        for token in [6, 8, 2] { control += try model.step([token], state: controlState) }
        let cache = try #require(model.expertCache)
        let budget = cache.budgetBytes
        model.streamOversizedUnions = true
        model.oversizedUnionWindowLimit = 1
        let state = QwenCPUModel.DecodeState()
        var candidate = try model.step([1, 5, 9, 2, 4, 7, 3], state: state)
        for token in [6, 8, 2] { candidate += try model.step([token], state: state) }
        #expect(candidate.map(\.bitPattern) == control.map(\.bitPattern))
        #expect(model.streamedExpertUnionWindows > 0)
        #expect(cache.budgetBytes == budget && cache.allocatedBytes <= budget)
    }

    @Test func cancellationAfterFirstWindowAndRecovery() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let model = try QwenMetalModel(modelDir: out, cacheBudgetGB: 0.05)
        model.prefillMode = .layerMajor(chunkTokens: 4)
        model.overlapChunkFull = true
        model.streamOversizedUnions = true
        model.oversizedUnionWindowLimit = 1
        var routed = false
        var checks = 0
        model.prefillExpertUnionObserver = { _, _ in routed = true }
        #expect(throws: GenerationInterruption.cancelled) {
            try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState(), shouldCancel: {
                if routed { checks += 1 }
                return checks >= 3
            })
        }
        #expect(checks == 3 && model.streamedExpertUnionWindows == 1)
        model.prefillExpertUnionObserver = nil
        let recovered = try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState())
        model.streamOversizedUnions = false
        let control = try model.step([1, 5, 9, 2], state: QwenCPUModel.DecodeState())
        #expect(recovered.map(\.bitPattern) == control.map(\.bitPattern))
    }
}
