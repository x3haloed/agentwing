#!/usr/bin/env python3
"""Prepare AW-0045 only after the fixed AW-0044 comparison is complete."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=Path('/Users/chad/Models/agentwing/reproductions/Swiftlet-AW0045')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()=='e707647e9139dbcca86403a1e0a06a705ddabaa3'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=p,text=True).strip()
f=p/'Sources/SwiftletServer/ToolProtocol.swift';s=f.read_text();a=s.index('final class ToolReplayCache:');b=s.index('\n/// Strict parser',a)
f.write_text(s[:a]+(ROOT/'probes/prefix_replay/ToolReplayCache.swift').read_text()+s[b:])
f=p/'Sources/SwiftletServer/main.swift';s=f.read_text();old='replayCache?.replayText(for: tool_calls)';assert s.count(old)==1;f.write_text(s.replace(old,'replayCache?.replayText(for: tool_calls, content: content.text)'))
for name in ['ReplayRetentionTests.swift','ReplayHistoryTests.swift']:
 (p/'Tests/SwiftletServerTests'/name).write_bytes((ROOT/'probes/prefix_replay'/name).read_bytes())
print('Applied isolated history draft; build, protocol and tokenizer validation required')
