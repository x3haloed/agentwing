#!/usr/bin/env python3
"""AW-0040 isolated single-token overlap; never edits P1."""
from pathlib import Path
import subprocess
p=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0040')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).startswith('406f992')
assert not subprocess.check_output(['git','status','--porcelain'],cwd=p,text=True).strip()
def edit(name,old,new):
 f=p/'Sources/SwiftletCore'/name;s=f.read_text();assert s.count(old)==1,(name,old[:60],s.count(old));f.write_text(s.replace(old,new))
edit('Qpack.swift','layer: Int, _ requests: [(expert: Int, into: UnsafeMutableRawPointer)]\n    ) throws {','layer: Int, _ requests: [(expert: Int, into: UnsafeMutableRawPointer)],\n        ready: ((Int) -> Void)? = nil\n    ) throws {')
edit('Qpack.swift','''        if requests.count == 1 {''','''        if let ready {
            // Descriptor is opened on the caller before workers start. Callback
            // runs only on the caller; all workers drain before return or throw.
            let group = DispatchGroup()
            let semaphores = requests.map { _ in DispatchSemaphore(value: 0) }
            let lock = NSLock()
            var failures: [Swift.Error?] = Array(repeating: nil, count: requests.count)
            for i in requests.indices {
                group.enter()
                DispatchQueue.global(qos: .userInitiated).async {
                    do {
                        try Self.readBlob(fd, layer: layer, expert: requests[i].expert,
                                          stride: stride, into: requests[i].into)
                    } catch {
                        lock.lock(); failures[i] = error; lock.unlock()
                    }
                    semaphores[i].signal()
                    group.leave()
                }
            }
            defer { group.wait() }
            var firstFailure: Swift.Error?
            for i in requests.indices {
                semaphores[i].wait()
                lock.lock(); let failure = failures[i]; lock.unlock()
                if let failure { if firstFailure == nil { firstFailure = failure } }
                else if firstFailure == nil { ready(i) }
            }
            if let firstFailure { throw firstFailure }
            return
        }
        if requests.count == 1 {''')
edit('ExpertCache.swift','func buffers(layer: Int, experts: [Int]) throws -> [MTLBuffer] {','func buffers(layer: Int, experts: [Int], ready: ((Int, MTLBuffer) -> Void)? = nil) throws -> [MTLBuffer] {')
edit('ExpertCache.swift','''        if !fills.isEmpty {
            do {''','''        if let ready {
            let missed = Set(fills.map { $0.expert })
            for (i, expert) in experts.enumerated() where !missed.contains(expert) {
                ready(i, result[i])
            }
        }
        if !fills.isEmpty {
            do {''')
edit('ExpertCache.swift','''                    fills.map { (expert: $0.expert, into: slots[$0.slot].contents()) })''','''                    fills.map { (expert: $0.expert, into: slots[$0.slot].contents()) },
                    ready: ready.map { callback in { i in
                        let expert = fills[i].expert
                        callback(experts.firstIndex(of: expert)!, self.slots[fills[i].slot])
                    } })''')
edit('QwenMetalModel.swift','''        var picks: [(Int, Float)]
    }''','''        var picks: [(Int, Float)]
        var routedAlreadyEncoded = false
    }
    var overlapExperts = ProcessInfo.processInfo.environment["SWIFTLET_EXPERT_OVERLAP"] == "1"''')
# Guard original routed-only loops, preserving shared expert and accumulation.
f=p/'Sources/SwiftletCore/QwenMetalModel.swift';s=f.read_text();a=s.index('    private func encodePendingMoE(');b=s.index('    /// h[slot]',a);part=s[a:b]
part=part.replace('for (ki, pick) in pend.picks.enumerated() {','for (ki, pick) in pend.picks.enumerated() where !pend.routedAlreadyEncoded {').replace('for ki in 0..<K {','for ki in 0..<K where !pend.routedAlreadyEncoded {');s=s[:a]+part+s[b:];f.write_text(s)
edit('QwenMetalModel.swift','''                bufs = try fetchExperts(cache, layer: li, experts: picks.map { $0.0 })
            }
            pending = PendingMoE(bufs: bufs, weights: weights, stacksLayer: li, picks: picks)''','''                if overlapExperts {
                    bufs = try fetchAndEncodeExperts(cache, layer: li, picks: picks,
                                                    slot: slot, shouldCancel: shouldCancel)
                } else {
                    bufs = try fetchExperts(cache, layer: li, experts: picks.map { $0.0 })
                }
            }
            pending = PendingMoE(bufs: bufs, weights: weights, stacksLayer: li, picks: picks,
                                 routedAlreadyEncoded: overlapExperts && expertCache != nil)''')
helper='''    /// AW-0040: caller-thread encoding while distinct cache-slot reads run.
    /// Drain committed GPU work even on read, encoding or cancellation failure.
    private func fetchAndEncodeExperts(
        _ cache: ExpertCache, layer: Int, picks: [(Int, Float)], slot: TokenSlot,
        shouldCancel: () -> Bool
    ) throws -> [MTLBuffer] {
        guard let projs = expertProjs else {
            throw Checkpoint.Error.badShape("overlap requires qpack projections")
        }
        let D = config.hiddenSize, inter = config.moeIntermediateSize, K = picks.count
        var commands: [MTLCommandBuffer] = []
        defer { for cb in commands { cb.waitUntilCompleted() } }
        var failure: Swift.Error?
        let bufs = try withoutActuallyEscaping(shouldCancel) { cancellation in
            try cache.buffers(layer: layer, experts: picks.map { $0.0 }) { [self] ki, buf in
            guard failure == nil else { return }
            do {
                try checkGenerationCancellation(cancellation)
                guard let cb = engine.queue.makeCommandBuffer(),
                      let enc = cb.makeComputeCommandEncoder() else {
                    throw Checkpoint.Error.badShape("overlap command allocation")
                }
                do {
                    try engine.encodeGemv(enc, projs.gate.linear(on: buf), rows: inter,
                        x: slot.scratch, xOff: slot.base + reg.xmoe,
                        y: slot.scratch, yOff: slot.base + reg.exp + ki * inter)
                    try engine.encodeGemv(enc, projs.up.linear(on: buf), rows: inter,
                        x: slot.scratch, xOff: slot.base + reg.xmoe,
                        y: slot.scratch, yOff: slot.base + reg.exp + K * inter + ki * inter)
                    barrier(enc)
                    try engine.encodeSiluMul(enc, buf: slot.scratch, count: inter,
                        gOff: slot.base + reg.exp + ki * inter,
                        uOff: slot.base + reg.exp + K * inter + ki * inter,
                        dstOff: slot.base + reg.exp + 2 * K * inter + ki * inter)
                    barrier(enc)
                    try engine.encodeGemv(enc, projs.down.linear(on: buf), rows: D,
                        x: slot.scratch, xOff: slot.base + reg.exp + 2 * K * inter + ki * inter,
                        y: slot.scratch, yOff: slot.base + reg.dexp + ki * D)
                    enc.endEncoding(); cb.commit(); commands.append(cb)
                } catch { enc.endEncoding(); throw error }
            } catch { failure = error }
        }
        }
        if let failure { throw failure }
        for cb in commands {
            cb.waitUntilCompleted()
            guard cb.status == .completed else {
                throw cb.error ?? Checkpoint.Error.badShape("overlap GPU failure")
            }
        }
        return bufs
    }

'''
edit('QwenMetalModel.swift','    private func encodePendingMoE(',helper+'    private func encodePendingMoE(')
(p/'Tests/SwiftletCoreTests/ExpertOverlapTests.swift').write_bytes((Path(__file__).resolve().parents[1]/'probes/runtime_overlap/ExpertOverlapTests.swift').read_bytes())
print('Applied AW-0040 isolated runtime candidate; not validated')
