import Foundation
import Testing
@testable import SwiftletCore

/// Functional stress oracle, not a task or throughput benchmark. Each arm
/// runs in its own process. No test-only cache window limit is used.
@Suite struct RealUnionBoundaryTests {
    @Test func fullModelOversizedUnion() throws {
        let env = ProcessInfo.processInfo.environment
        let path = try #require(env["AW46_QPACK_DIR"])
        let output = URL(fileURLWithPath: try #require(env["AW46_BOUNDARY_OUTPUT"]))
        let arm = try #require(env["AW46_BOUNDARY_ARM"])
        try #require(arm == "reference" || arm == "candidate")
        let candidate = arm == "candidate"
        let model = try QwenMetalModel(modelDir: URL(fileURLWithPath: path),
                                      cacheBudgetGB: candidate ? 0.5 : 1.0)
        model.prefillMode = .layerMajor(chunkTokens: 256)
        model.overlapExperts = true
        model.overlapChunkFull = true
        model.streamOversizedUnions = candidate
        var seed: UInt64 = 0x41573436424F554E
        let tokens = (0..<256).map { _ -> Int in
            seed = seed &* 6364136223846793005 &+ 1442695040888963407
            return 32 + Int((seed >> 32) % UInt64(min(100_000, model.config.vocabSize) - 32))
        }
        var routes: [[Int]] = []
        var unions: [[Int]] = []
        model.routedExpertObserver = { layer, experts in routes.append([layer] + experts) }
        model.prefillExpertUnionObserver = { layer, experts in unions.append([layer] + experts) }
        let state = QwenCPUModel.DecodeState()
        var logits = try model.step(tokens, state: state)
        var generated: [Int] = []
        for index in 0...8 {
            try #require(logits.allSatisfy { $0.isFinite })
            try logits.withUnsafeBytes { try Data($0).write(to: output.appendingPathComponent("logits-\(index).bin")) }
            if index < 8 {
                let next = try #require(logits.indices.max { logits[$0] < logits[$1] })
                generated.append(next)
                logits = try model.step([next], state: state)
            }
        }
        let cache = try #require(model.expertCache)
        let maxUnion = unions.map { $0.count - 1 }.max() ?? 0
        let report: [String: Any] = ["arm": arm, "tokens": tokens, "generated": generated,
            "routes": routes, "unions": unions, "maximum_union": maxUnion,
            "streamed_windows": model.streamedExpertUnionWindows,
            "cache_budget_bytes": cache.budgetBytes, "allocated_bytes": cache.allocatedBytes,
            "cache_slots": cache.slotCount, "cache_hits": cache.hits, "cache_misses": cache.misses]
        try JSONSerialization.data(withJSONObject: report, options: [.sortedKeys])
            .write(to: output.appendingPathComponent("model-report.json"))
        #expect(maxUnion > 160, "Without a real oversized union this diagnostic is inconclusive")
        #expect(candidate ? model.streamedExpertUnionWindows > 0 : model.streamedExpertUnionWindows == 0)
        #expect(cache.allocatedBytes <= cache.budgetBytes)
        print("AW46 full-model arm=\(arm) maxUnion=\(maxUnion) windows=\(model.streamedExpertUnionWindows) slots=\(cache.slotCount)")
    }
}
