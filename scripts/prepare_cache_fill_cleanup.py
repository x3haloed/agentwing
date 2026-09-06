#!/usr/bin/env python3
"""AW-0046: apply only after preserving the failed cache-recovery falsifier."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
p = Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0046')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=p, text=True).strip() == 'e707647e9139dbcca86403a1e0a06a705ddabaa3'
f = p / 'Sources/SwiftletCore/ExpertCache.swift'
s = f.read_text()
old = '        var fills: [(slot: Int, expert: Int)] = []\n'
new = old + '''        var fillsCompleted = false
        defer {
            if !fillsCompleted {
                // Selection can throw before reads begin, too. Never publish
                // assigned keys whose bytes did not successfully arrive.
                for fill in fills {
                    keyToSlot.removeValue(forKey: slotKey[fill.slot])
                    slotKey[fill.slot] = -1
                    slotFreq[fill.slot] = 0
                }
            }
        }
'''
assert s.count(old) == 1
s = s.replace(old, new)
a = s.index('        if !fills.isEmpty {')
b = s.index('        return result', a)
s = s[:a] + '''        if !fills.isEmpty {
            try reader.readExperts(
                layer: layer,
                fills.map { (expert: $0.expert, into: slots[$0.slot].contents()) },
                ready: ready.map { callback in { i in
                    let expert = fills[i].expert
                    callback(experts.firstIndex(of: expert)!, self.slots[fills[i].slot])
                } })
        }
        fillsCompleted = true
''' + s[b:]
f.write_text(s)
(p / 'Tests/SwiftletCoreTests/CacheOverflowRecoveryTests.swift').write_bytes(
    (ROOT / 'probes/runtime_overlap/CacheOverflowRecoveryTests.swift').read_bytes())
print('Applied pending-fill invalidation across selection and read failures')
