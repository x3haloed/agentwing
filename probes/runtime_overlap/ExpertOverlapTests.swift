import Foundation
import Metal
import Testing
@testable import SwiftletCore

@Suite struct ExpertOverlapTests {
    @Test func readyBytesAndPolicyAcrossEvictions() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let device = try #require(MTLCreateSystemDefaultDevice())
        let cache = try ExpertCache(containerDir: out, device: device,
            budgetBytes: ExpertCacheTests.budget(slots: 16, container: out))
        let oracle = try QpackExpertReader(containerDir: out)
        var reference = ExpertCacheTests.ReferencePolicy(maxSlots: cache.slotCount)
        let caller = Thread.current
        for request in 0..<100 {
            let layer = (request / 2) % 8
            let seed = request / 2
            let experts = [seed % 8, (seed + 2) % 8, (seed + 5) % 8]
            let expectedSlots = reference.buffers(layer: layer, experts: experts)
            var expected: [Data] = []
            for expert in experts {
                var bytes = Data(count: cache.stride)
                try bytes.withUnsafeMutableBytes {
                    try oracle.readExpert(layer: layer, expert: expert, into: $0.baseAddress!)
                }
                expected.append(bytes)
            }
            var seen = Set<Int>()
            let buffers = try cache.buffers(layer: layer, experts: experts) { i, buffer in
                #expect(Thread.current === caller)
                #expect(seen.insert(i).inserted)
                #expect(Data(bytes: buffer.contents(), count: cache.stride) == expected[i])
            }
            #expect(seen == Set(experts.indices))
            #expect(buffers.count == experts.count)
            #expect(cache.hits == reference.hits && cache.misses == reference.misses)
            for (i, expert) in experts.enumerated() {
                #expect(cache.residentSlot(layer: layer, expert: expert) == expectedSlots[i])
            }
        }
        #expect(cache.hits > 0 && cache.misses > 16)
    }

    @Test func cancellationAfterSubmissionDrainsAndFreshStateRecovers() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let model = try QwenMetalModel(modelDir: out, cacheBudgetGB: 0.05)
        model.overlapExperts = true
        var routed = false
        var checks = 0
        model.routedExpertObserver = { _, _ in routed = true }
        #expect(throws: GenerationInterruption.cancelled) {
            try model.step([1], state: QwenCPUModel.DecodeState(), shouldCancel: {
                if routed { checks += 1 }
                return checks >= 3
            })
        }
        #expect(checks == 3)
        model.routedExpertObserver = nil
        let recovered = try model.step([1], state: QwenCPUModel.DecodeState())
        model.overlapExperts = false
        let control = try model.step([1], state: QwenCPUModel.DecodeState())
        #expect(recovered.map(\.bitPattern) == control.map(\.bitPattern))
    }

    @Test func partialFailureInvalidatesAndDrains() throws {
        let out = try ExpertCacheTests.repackedTiny()
        defer { try? FileManager.default.removeItem(at: out) }
        let device = try #require(MTLCreateSystemDefaultDevice())
        let cache = try ExpertCache(containerDir: out, device: device,
            budgetBytes: ExpertCacheTests.budget(slots: 16, container: out))
        _ = try cache.buffers(layer: 2, experts: [0])
        let handle = try FileHandle(forWritingTo: out.appendingPathComponent("packed_experts/layer_02.bin"))
        try handle.truncate(atOffset: UInt64(cache.stride * 5 / 2)); try handle.close()
        var seen: [Int] = []
        #expect(throws: (any Error).self) {
            try cache.buffers(layer: 2, experts: [0, 1, 2, 3]) { i, _ in seen.append(i) }
        }
        #expect(seen == [0, 1])
        for expert in [1, 2, 3] { #expect(cache.residentSlot(layer: 2, expert: expert) == nil) }
        #expect(cache.residentSlot(layer: 2, expert: 0) != nil)
        let count = seen.count
        // Subsequent fills can safely reuse freed storage after every old read drains.
        let recovered = try cache.buffers(layer: 4, experts: Array(0..<8)) { _, _ in }
        #expect(recovered.count == 8 && seen.count == count)
    }
}
