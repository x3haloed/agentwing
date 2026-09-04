#!/usr/bin/env python3
"""Offline tokenizer accounting through the actual optional output-limit hook."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
NODE = '/Users/chad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
NODE_REPLAY = r'''
const fs=require('fs'); let hook;
require(process.argv[1])({on:(_,fn)=>hook=fn});
const messages=JSON.parse(fs.readFileSync(0,'utf8'));
console.log(JSON.stringify(messages.map(m=> {
 const changed=hook(m);
 return {original:m.content.filter(c=>c.type==='text').map(c=>c.text).join('\n'),
 bounded:(changed||m).content.filter(c=>c.type==='text').map(c=>c.text).join('\n'),
 changed:!!changed};
})));
'''


def profile(run):
    dependencies = json.loads((ROOT / 'spec/dependencies.json').read_text())
    tokenizer_path = Path(dependencies['qwen3_6_35b_a3b_8bit_qpack']['local_path']) / 'tokenizer.json'
    tokenizer = Tokenizer.from_file(str(tokenizer_path))
    count = lambda text: len(tokenizer.encode(text, add_special_tokens=False).ids)
    rows = []
    for transcript in sorted((run / 'tasks').glob('*/pi.jsonl')):
        raw = transcript.read_bytes()
        messages = [e['message'] for e in map(json.loads, raw.splitlines())
                    if e.get('type') == 'message_end' and e.get('message', {}).get('role') == 'toolResult']
        results = json.loads(subprocess.check_output(
            [NODE, '-e', NODE_REPLAY, str(ROOT / 'extensions/bounded-bash-result.js')],
            input=json.dumps(messages), text=True))
        original = [count(r['original']) for r in results]
        bounded = [count(r['bounded']) for r in results]
        rows.append({'task_id': transcript.parent.name,
                     'transcript_sha256': hashlib.sha256(raw).hexdigest(),
                     'tool_result_count': len(results),
                     'changed_result_count': sum(r['changed'] for r in results),
                     'original_text_tokens': sum(original),
                     'bounded_text_tokens': sum(bounded),
                     'token_difference': sum(original) - sum(bounded),
                     'largest_original_result_tokens': max(original, default=0)})
    return {'schema_version': 1, 'run': str(run),
            'tokenizer_sha256': hashlib.sha256(tokenizer_path.read_bytes()).hexdigest(),
            'extension_sha256': hashlib.sha256((ROOT / 'extensions/bounded-bash-result.js').read_bytes()).hexdigest(),
            'tasks': rows,
            'scope': 'Offline accounting of tool-result text through the actual hook. No endpoint timing, semantic equivalence, recovery, or changed-generation claim; protocol overhead excluded.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(profile(args.run.resolve()), indent=2))
