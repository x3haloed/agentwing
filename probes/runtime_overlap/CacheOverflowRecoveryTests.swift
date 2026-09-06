import Foundation
import Metal
import Testing
@testable import SwiftletCore

/// Real valid expert IDs and the frozen 0.5 GiB budget; cache/reader only,
/// without loading a model or executing a generation. Run explicitly.
@Suite struct CacheOverflowRecoveryTests {
    @Test func rejected161ExpertBatchCannotPublishUnfilledHits() throws {
        let path = try #require(ProcessInfo.processInfo.environment["AW46_QPACK_DIR"])
        let container = URL(fileURLWithPath: path)
        let device = try #require(MTLCreateSystemDefaultDevice())
        let cache = try ExpertCache(containerDir: container, device: device,
                                    budgetBytes: 536_870_912)
        #expect(cache.slotCount == 160)
        #expect(cache.reader.layout.expertCount >= 161)
        #expect(throws: Checkpoint.Error.self) {
            try cache.buffers(layer: 0, experts: Array(0..<161))
        }
        let falselyResident = (0..<160).filter { cache.residentSlot(layer: 0, expert: $0) != nil }.count
        #expect(falselyResident == 0)
        let oracle = try QpackExpertReader(containerDir: container)
        var scratch = [UInt8](repeating: 0, count: cache.stride)
        try scratch.withUnsafeMutableBytes {
            try oracle.readExpert(layer: 0, expert: 0, into: $0.baseAddress!)
        }
        let missesBefore = cache.misses
        let buffer = try #require(try cache.buffers(layer: 0, experts: [0]).first)
        let recovered = Array(UnsafeRawBufferPointer(start: buffer.contents(), count: cache.stride))
        let bytesMatch = recovered == scratch
        #expect(bytesMatch)
        #expect(cache.misses == missesBefore + 1)
        #expect(cache.allocatedBytes <= cache.budgetBytes)
        print("AW46 recovery stale=\(falselyResident) bytesMatch=\(bytesMatch) allocated=\(cache.allocatedBytes) slots=\(cache.slotCount)")
    }
}
