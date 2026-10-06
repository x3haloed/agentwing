#!/usr/bin/env python3
"""Replay saved AW-0141 evidence; no inference or benchmark changes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnose(run):
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    assert all(digest(run/name)==h for name,h in receipt.items())
    task=run/'dev-multi-file'
    events=[json.loads(line) for line in (task/'pi.jsonl').read_text().splitlines()]
    turns=[];current=None
    for event in events:
        if event.get('type')=='message_start' and event.get('message',{}).get('role')=='assistant':
            current={'thinking_chunks':0,'thinking_chars':0,'text_chunks':0,'ended':False,'thought':''};turns.append(current)
        delta=event.get('assistantMessageEvent',{})
        if current is not None and delta.get('type')=='thinking_delta':
            fragment=delta.get('delta','');current['thinking_chunks']+=1;current['thinking_chars']+=len(fragment);current['thought']+=fragment
        if current is not None and delta.get('type')=='text_delta':current['text_chunks']+=1
        if current is not None and event.get('type')=='message_end' and event.get('message',{}).get('role')=='assistant':
            current['ended']=True;current['stop_reason']=event['message'].get('stopReason');current['usage']=event['message'].get('usage')
    for turn in turns:
        words=re.findall(r'\w+',turn.pop('thought').lower());grams=Counter(tuple(words[i:i+12]) for i in range(max(0,len(words)-11)))
        turn['word_count']=len(words);turn['maximum_exact_12_word_repeat']=max(grams.values(),default=0)
    settings=[];timings=[];progress=[]
    for line in (task/'server.log').read_text().splitlines():
        if 'print_timing:' in line and 'n_gen =' in line:progress.append(line)
        elif 'print_timing:' in line and ('eval time =' in line or 'total time =' in line):timings.append(line)
        marker='http: streamed chunk: data: '
        if marker not in line:continue
        try: chunk=json.loads(line.split(marker,1)[1])
        except json.JSONDecodeError:continue
        verbose=chunk.get('__verbose',{})
        if 'generation_settings' in verbose:
            s=verbose['generation_settings'];settings.append({k:s.get(k) for k in ['temperature','top_p','top_k','min_p','presence_penalty','frequency_penalty','repeat_penalty','max_tokens','seed','chat_format','generation_prompt']})
    return {'experiment':'AW-0142','source_experiment':'AW-0141','raw_receipt_sha256':digest(run/'sha256-recursive.json'),'raw_hashes_verified':True,'turns':turns,'terminal_generation_settings':settings,'completed_request_timings':timings,'generation_progress_samples':len(progress),'first_generation_progress':progress[0] if progress else None,'last_generation_progress':progress[-1] if progress else None,'interpretation':'Final turn continued emitting thinking deltas until deadline, not a silent runtime stall. No final-turn terminal usage exists. Exact repetition counts are descriptive, not a quality gate or causal cache comparison. Server/adapter medium intent remains pinned; this trace alone does not prove rendered effort semantics.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);args=parser.parse_args();print(json.dumps(diagnose(args.run),indent=2))
