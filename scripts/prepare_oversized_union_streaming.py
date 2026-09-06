#!/usr/bin/env python3
"""Draft AW-0046 isolated overflow streaming; do not apply during AW-0044."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0046')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()=='e707647e9139dbcca86403a1e0a06a705ddabaa3'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=p,text=True).strip()
f=p/'Sources/SwiftletCore/QwenMetalModel.swift';s=f.read_text()
def replace(old,new):
 global s
 assert s.count(old)==1,(old[:80],s.count(old));s=s.replace(old,new)
replace('''    var overlapChunkFull = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_FULL_OVERLAP"] == "1"''','''    var overlapChunkFull = ProcessInfo.processInfo.environment["SWIFTLET_CHUNK_FULL_OVERLAP"] == "1"
    var streamOversizedUnions = ProcessInfo.processInfo.environment["SWIFTLET_STREAM_OVERSIZED_UNIONS"] == "1"
    // Test/diagnostic scheduling cap only; production uses actual cache capacity.
    var oversizedUnionWindowLimit: Int?
    private(set) var streamedExpertUnionWindows = 0''')
replace('''                for (i, e) in union.enumerated() { buffers[e] = bufs[i] }''','''                // Full chains have already written every routed down output.
                // Their source buffers need not remain pinned in pending MoE.
                if !overlapChunkFull {
                    for (i, e) in union.enumerated() { buffers[e] = bufs[i] }
                }''')
a=s.index('    private func fetchAndEncodeChunkGateUp(');b=s.index('    private func encodeChunkMoE(',a);part=s[a:b]
old='''        let inter = config.moeIntermediateSize'''
new='''        let effectiveCapacity = max(1, min(cache.slotCount,
            oversizedUnionWindowLimit ?? cache.slotCount))
        if streamOversizedUnions && overlapChunkFull && union.count > effectiveCapacity {
            var start = 0
            while start < union.count {
                try checkGenerationCancellation(shouldCancel)
                // Re-read capacity each window; cache allocation may discover a
                // smaller physical cap. Never keep an oversized protected set.
                let width = max(1, min(32, min(cache.slotCount,
                    oversizedUnionWindowLimit ?? cache.slotCount)))
                let end = min(start + width, union.count)
                _ = try fetchAndEncodeChunkGateUp(cache, layer: layer,
                    union: Array(union[start..<end]), perToken: perToken,
                    shouldCancel: shouldCancel)
                // The recursive call drains reads and GPU commands on all exits.
                // Only completed outputs remain live before slots can be reused.
                streamedExpertUnionWindows += 1
                start = end
            }
            return []
        }
        let inter = config.moeIntermediateSize'''
assert part.count(old)==1;part=part.replace(old,new);s=s[:a]+part+s[b:];f.write_text(s)
(p/'Tests/SwiftletCoreTests/OversizedUnionTests.swift').write_bytes((ROOT/'probes/runtime_overlap/OversizedUnionTests.swift').read_bytes())
print('Applied isolated overflow draft; build, boundedness and real failure replay required')
