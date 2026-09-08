"""Compare sealed navigation arms; remove generated call IDs only."""
import copy
import json
from pathlib import Path
import sys
from run_local_agent import digest


def read(run):
    receipt=json.loads((run/'sha256-recursive.json').read_text())
    actual={str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and not p.is_symlink() and p.name!='sha256-recursive.json'}
    assert actual==receipt
    events=[json.loads(s) for s in (run/'01-navigation/pi.jsonl').read_text().splitlines() if s.strip()]
    visible=[]
    for e in events:
        if e.get('type')=='message_end' and e.get('message',{}).get('role')=='assistant':
            content=copy.deepcopy(e['message']['content'])
            for block in content:
                if block.get('type')=='toolCall':block.pop('id',None)
            visible.append({'kind':'assistant','content':content})
        elif e.get('type')=='tool_execution_end':
            visible.append({'kind':'tool_result','result':e.get('result'),'isError':bool(e.get('isError'))})
    sessions=[e for e in events if e.get('type')=='session'];assert len(sessions)==1
    return {'run':str(run),'receipt_sha256':digest(run/'sha256-recursive.json'),'cwd':sessions[0]['cwd'],'visible':visible}


def compare(left,right):
    a,b=left['visible'],right['visible'];n=0
    for x,y in zip(a,b):
        if x!=y:break
        n+=1
    same=n==len(a)==len(b)
    return {'left':left['run'],'right':right['run'],'same_cwd':left['cwd']==right['cwd'],'complete_visible_transcripts_equal':same,'equal_prefix_events':n,'event_counts':[len(a),len(b)],'first_difference':None if same else [a[n] if n<len(a) else None,b[n] if n<len(b) else None]}

if __name__=='__main__':
    assert len(sys.argv)==4,'Provide C1 A1 C2 in frozen order'
    rows=[read(Path(p)) for p in sys.argv[1:]]
    print(json.dumps({'arms':[{k:v for k,v in r.items() if k!='visible'} for r in rows],'comparisons':[compare(rows[0],rows[1]),compare(rows[1],rows[2]),compare(rows[0],rows[2])],'scope':'Exact structured visible content and tool results, excluding generated call IDs only. No hidden-state/token equivalence, causal speedup or grade changes.'},indent=2))
