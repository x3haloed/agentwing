#!/usr/bin/env python3
"""Compile exact frozen parser declarations for read-only captured-output review."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
from run_local_agent import ROOT, preflight, digest

DRIVER = r'''
import Foundation
let report = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))) as! [String: Any]
let text = report["text"] as! String
var results: [[String: Any]] = []
for normalized in [false, true] {
    var result: [String: Any] = ["schema_tags_and_prefix_salvage": normalized]
    do {
        if let parsed = try parseToolReply(text, declaredTools: ["bash"],
                acceptedSchemaTags: normalized ? ["bash": ["command", "timeout"]] : [:],
                salvageValidPrefix: normalized) {
            result["parser_accepted"] = true
            result["calls"] = parsed.calls.map { ["name": $0.name, "arguments": $0.arguments] }
            result["normalized_schema_tags"] = parsed.normalizedSchemaTags
            result["salvaged_suffix"] = parsed.salvagedMalformedSuffix
        } else {
            result["parser_accepted"] = false
            result["reason"] = "no tool call"
        }
    } catch {
        result["parser_accepted"] = false
        result["reason"] = error.localizedDescription
    }
    results.append(result)
}
let data = try JSONSerialization.data(withJSONObject: results, options: [.sortedKeys, .prettyPrinted])
print(String(decoding: data, as: UTF8.self))
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('reports',nargs='+',type=Path)
    args=parser.parse_args();preflight()
    source=args.runtime/'Sources/SwiftletServer/ToolProtocol.swift';text=source.read_text()
    # Exact declaration slices: exclude unrelated history/cache integration and imports.
    slices=[text[text.index('enum ToolProtocolError:'):text.index('enum JSONValue:')],
            text[text.index('struct ParsedToolCall:'):text.index('private struct ToolCallSignature:')],
            text[text.index('func parseToolReply('):]]
    args.output.mkdir(parents=True,exist_ok=False)
    extracted=args.output/'FrozenParser.swift';extracted.write_text('import Foundation\n'+''.join(slices))
    main=args.output/'main.swift';main.write_text(DRIVER)
    binary=args.output/'review-tool-output'
    command=['swiftc',str(extracted),str(main),'-o',str(binary)]
    build=subprocess.run(command,text=True,capture_output=True,timeout=60)
    (args.output/'build.log').write_text(build.stdout+build.stderr)
    manifest={'source':str(source),'source_sha256':digest(source),'extracted_sha256':digest(extracted),
              'driver_sha256':digest(main),'command':command,'build_exit':build.returncode,'reports':[]}
    if build.returncode==0:
        manifest['binary_sha256']=digest(binary)
        for index,report in enumerate(args.reports):
            result=subprocess.run([str(binary),str(report)],capture_output=True,text=True,timeout=10)
            (args.output/f'review-{index}.json').write_text(result.stdout)
            (args.output/f'review-{index}.stderr').write_text(result.stderr)
            manifest['reports'].append({'input':str(report),'input_sha256':digest(report),'exit':result.returncode,
                'review_file':f'review-{index}.json','review_sha256':digest(args.output/f'review-{index}.json')})
    manifest['scope']='Exact frozen parser declarations only; does not execute commands or validate artifact behavior.'
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
    assert build.returncode==0 and all(r['exit']==0 for r in manifest['reports'])

if __name__=='__main__':
    with (ROOT/'var/local-agent.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        main()
