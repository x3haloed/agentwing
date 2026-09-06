#!/usr/bin/env python3
"""AW-0041 reconstruct isolated causal prefill gate/up overlap from AW-0040."""
from pathlib import Path
import subprocess
p=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0041')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()=='234028121de5fe4d082b3198105466ff34f36cb6'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=p,text=True).strip()
f=p/'Sources/SwiftletCore/QwenMetalModel.swift';s=f.read_text()
def replace(old,new):
 global s
 assert s.count(old)==1,(old[:80],s.count(old));s=s.replace(old,new)
replace('''    var overlapExperts = ProcessInfo.processInfo.environment["SWIFTLET_EXPERT_OVERLAP"] == "1"''','''    var overlapExperts = ProcessInfo.processInfo.environment["SWIFTLET_EXPERT_OVERLAP"] == "1"
    var overlapChunkGateUp = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_OVERLAP"] == "1"''')
replace('''        var perToken: [(picks: [(Int, Float)], weights: [Float])]
    }''','''        var perToken: [(picks: [(Int, Float)], weights: [Float])]
        var gateUpAlreadyEncoded = false
    }''')
replace('''                let bufs = try fetchExperts(cache, layer: li, experts: union)
                for (i, e) in union.enumerated() { buffers[e] = bufs[i] }
            }
            pending = PendingChunkMoE(
                layer: li, union: union, buffers: buffers, perToken: perToken)''','''                let bufs: [MTLBuffer]
                if overlapChunkGateUp {
                    bufs = try fetchAndEncodeChunkGateUp(cache, layer: li, union: union,
                                                        perToken: perToken, shouldCancel: shouldCancel)
                } else {
                    bufs = try fetchExperts(cache, layer: li, experts: union)
                }
                for (i, e) in union.enumerated() { buffers[e] = bufs[i] }
            }
            pending = PendingChunkMoE(
                layer: li, union: union, buffers: buffers, perToken: perToken,
                gateUpAlreadyEncoded: overlapChunkGateUp && expertCache != nil)''')
# Only first routed gate/up loop is skipped; original batch SwiGLU/down remain.
a=s.index('    private func encodeChunkMoE(');b=s.index('        for expert in pend.union {',a)
s=s[:b]+s[b:].replace('        for expert in pend.union {','        for expert in pend.union where !pend.gateUpAlreadyEncoded {',1)
helper='''    /// AW-0041: preserve per-expert token batching; issue gate/up after the
    /// corresponding union read is ready. Original strided SwiGLU/down stay
    /// deferred, avoiding a per-assignment dispatch expansion.
    private func fetchAndEncodeChunkGateUp(
        _ cache: ExpertCache, layer: Int, union: [Int],
        perToken: [(picks: [(Int, Float)], weights: [Float])],
        shouldCancel: () -> Bool
    ) throws -> [MTLBuffer] {
        guard let projs = expertProjs else {
            throw Checkpoint.Error.badShape("chunk overlap requires qpack projections")
        }
        let inter = config.moeIntermediateSize
        var assignments: [Int: [(t: Int, ki: Int)]] = [:]
        for (t, entry) in perToken.enumerated() {
            for (ki, pick) in entry.picks.enumerated() {
                assignments[pick.0, default: []].append((t, ki))
            }
        }
        var commands: [MTLCommandBuffer] = []
        defer { for cb in commands { cb.waitUntilCompleted() } }
        var failure: Swift.Error?
        let bufs = try withoutActuallyEscaping(shouldCancel) { cancellation in
            try cache.buffers(layer: layer, experts: union) { [self] i, buf in
                guard failure == nil else { return }
                do {
                    try checkGenerationCancellation(cancellation)
                    guard let cb = engine.queue.makeCommandBuffer(),
                          let enc = cb.makeComputeCommandEncoder() else {
                        throw Checkpoint.Error.badShape("chunk overlap command allocation")
                    }
                    do {
                        let assigned = assignments[union[i]] ?? []
                        try engine.encodeGemvBatch(enc, projs.gate.linear(on: buf), rows: inter,
                            x: prefillScratchBuf!, y: prefillScratchBuf!,
                            slots: assigned.map { a in
                                (xOff: a.t * reg.total + reg.xmoe,
                                 yOff: a.t * reg.total + reg.exp + a.ki * inter)
                            })
                        try engine.encodeGemvBatch(enc, projs.up.linear(on: buf), rows: inter,
                            x: prefillScratchBuf!, y: prefillScratchBuf!,
                            slots: assigned.map { a in
                                let K = perToken[a.t].picks.count
                                return (xOff: a.t * reg.total + reg.xmoe,
                                        yOff: a.t * reg.total + reg.exp + K * inter + a.ki * inter)
                            })
                        enc.endEncoding(); cb.commit(); commands.append(cb)
                    } catch { enc.endEncoding(); throw error }
                } catch { failure = error }
            }
        }
        if let failure { throw failure }
        for cb in commands {
            cb.waitUntilCompleted()
            guard cb.status == .completed else {
                throw cb.error ?? Checkpoint.Error.badShape("chunk overlap GPU failure")
            }
        }
        return bufs
    }

'''
replace('    private func encodeChunkMoE(',helper+'    private func encodeChunkMoE(')
replace('''                projectLogits: end == tokens.count
            )''','''                projectLogits: end == tokens.count, shouldCancel: shouldCancel
            )''')
replace('''        _ chunk: [Int], state: QwenCPUModel.DecodeState, projectLogits: Bool
    ) throws -> [Float] {''','''        _ chunk: [Int], state: QwenCPUModel.DecodeState, projectLogits: Bool,
        shouldCancel: () -> Bool
    ) throws -> [Float] {''')
f.write_text(s)
(p/'Tests/SwiftletCoreTests/ChunkOverlapTests.swift').write_bytes((Path(__file__).resolve().parents[1]/'probes/runtime_overlap/ChunkOverlapTests.swift').read_bytes())
print('Applied isolated AW-0041; requires build and validation')
