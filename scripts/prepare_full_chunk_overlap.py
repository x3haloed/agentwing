#!/usr/bin/env python3
"""AW-0043 full expert chain overlap with indexed batched SwiGLU."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0043')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()=='f0ae501b4658a138cb77dd7cdd4e34947c70db80'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=p,text=True).strip()
f=p/'Sources/SwiftletCore/QwenMetalModel.swift';s=f.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a[:80],s.count(a));s=s.replace(a,b)
replace('''    var overlapChunkGateUp = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_OVERLAP"] == "1"''','''    var overlapChunkGateUp = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_OVERLAP"] == "1"
    var overlapChunkFull = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_FULL_OVERLAP"] == "1"''')
replace('''        var gateUpAlreadyEncoded = false''','''        var gateUpAlreadyEncoded = false
        var fullChainAlreadyEncoded = false''')
replace('''                if overlapChunkGateUp {''','''                if overlapChunkGateUp || overlapChunkFull {''')
replace('''                gateUpAlreadyEncoded: overlapChunkGateUp && expertCache != nil)''','''                gateUpAlreadyEncoded: (overlapChunkGateUp || overlapChunkFull) && expertCache != nil,
                fullChainAlreadyEncoded: overlapChunkFull && expertCache != nil)''')
a=s.index('    private func fetchAndEncodeChunkGateUp(');b=s.index('    private func encodeChunkMoE(',a);part=s[a:b]
needle='''                        enc.endEncoding(); cb.commit(); commands.append(cb)'''
extra='''                        if overlapChunkFull {
                            barrier(enc)
                            let slots = assigned.map { a -> SIMD4<UInt32> in
                                let K = perToken[a.t].picks.count
                                return SIMD4(UInt32(inter),
                                    UInt32(a.t * reg.total + reg.exp + a.ki * inter),
                                    UInt32(a.t * reg.total + reg.exp + K * inter + a.ki * inter),
                                    UInt32(a.t * reg.total + reg.exp + 2 * K * inter + a.ki * inter))
                            }
                            enc.setComputePipelineState(try engine.pipeline("silu_mul_indexed"))
                            for index in 0..<3 { enc.setBuffer(prefillScratchBuf!, offset: 0, index: index) }
                            // Metal's inline argument limit is 4096 bytes; chunk
                            // the offset table without constraining model context.
                            for start in stride(from: 0, to: slots.count, by: 256) {
                                let batch = Array(slots[start..<min(start + 256, slots.count)])
                                batch.withUnsafeBytes { enc.setBytes($0.baseAddress!, length: $0.count, index: 3) }
                                enc.dispatchThreads(MTLSize(width: inter, height: batch.count, depth: 1),
                                    threadsPerThreadgroup: MTLSize(width: 64, height: 1, depth: 1))
                            }
                            barrier(enc)
                            try engine.encodeGemvBatch(enc, projs.down.linear(on: buf), rows: config.hiddenSize,
                                x: prefillScratchBuf!, y: prefillScratchBuf!,
                                slots: assigned.map { a in
                                    let K = perToken[a.t].picks.count
                                    return (xOff: a.t * reg.total + reg.exp + 2 * K * inter + a.ki * inter,
                                            yOff: a.t * reg.total + reg.dexp + a.ki * config.hiddenSize)
                                })
                        }
'''
assert part.count(needle)==1;part=part.replace(needle,extra+needle);s=s[:a]+part+s[b:]
a=s.index('    private func encodeChunkMoE(');part=s[a:]
part=part.replace('for ki in 0..<topK {','for ki in 0..<topK where !pend.fullChainAlreadyEncoded {').replace('for ki in 0..<K {','for ki in 0..<K where !pend.fullChainAlreadyEncoded {').replace('for expert in pend.union {','for expert in pend.union where !pend.fullChainAlreadyEncoded {')
s=s[:a]+part;f.write_text(s)
k=p/'Sources/SwiftletCore/Kernels.metal.txt';k.write_text(k.read_text()+'\n'+(ROOT/'probes/runtime_overlap/silu_mul_indexed.metal').read_text())
(p/'Tests/SwiftletCoreTests/FullChunkOverlapTests.swift').write_bytes((ROOT/'probes/runtime_overlap/FullChunkOverlapTests.swift').read_bytes())
print('Applied isolated AW-0043; build and validation required')
