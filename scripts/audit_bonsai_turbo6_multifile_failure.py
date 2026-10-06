#!/usr/bin/env python3
"""Audit preserved AW215 timeout; byte-preserving diagnostic log decode only."""
import json,hashlib
from pathlib import Path
from run_local_agent import ROOT,digest
from verify_p2_task import SUITE,verify
R=Path('/Users/chad/Models/agentwing/evidence/AW-0215/20261006T214746.364246Z')
def audit():
    receipt=json.loads((R/'sha256-recursive.json').read_text())
    actual={str(p.relative_to(R)):digest(p) for p in R.rglob('*') if p.is_file() and p.name!='sha256-recursive.json'}
    assert actual==receipt
    plan=json.loads((R/'plan.json').read_text());manifest=json.loads((R/'manifest.json').read_text())
    assert digest(R/'plan.json')==manifest['plan_sha256']
    for name,h in plan['pins'].items():
        assert digest(ROOT/name)==h and digest(R/'source-snapshot'/name)==h
    d=R/'dev-multi-file';execution=json.loads((d/'result.json').read_text())
    assert execution['error']=='stopped-timeout'
    b=(d/'server.log').read_bytes();invalid=[];pos=0
    while pos<len(b):
        try:b[pos:].decode('utf-8');break
        except UnicodeDecodeError as e:
            invalid.append({'start':pos+e.start,'end':pos+e.end,'bytes_hex':b[pos+e.start:pos+e.end].hex()});pos+=e.end
    # Preserve every byte with surrogateescape; no wire JSON is repaired.
    source=(ROOT/'scripts/run_bonsai_budget_debugging_v2.py').read_text()
    assert source.count("log=(directory/'server.log').read_text()")==1
    namespace={'__name__':'aw215_diagnostic_protocol'}
    exec(compile(source.replace("log=(directory/'server.log').read_text()","log=(directory/'server.log').read_bytes().decode('utf-8',errors='surrogateescape')"),'AW215-preserved-protocol','exec'),namespace)
    protocol=namespace['protocol'](d)
    events=[json.loads(l) for l in (d/'pi.jsonl').read_text().splitlines()]
    starts=[e for e in events if e.get('type')=='tool_execution_start']
    assert len(starts)==5 and protocol['tool_accounting']['failed']==1
    # Manual transcript review: four useful reads, one unsupported cat-A failure.
    assert starts[2]['args']['command'].startswith('cat -A ')
    account={**protocol['tool_accounting'],'productive':4,'redundant':0,'denied':0}
    samples=[l.split() for l in (d/'pressure.tsv').read_text().splitlines()]
    assert max(int(s[1]) for s in samples)==execution['pressure_peak']
    capacity=[json.loads(l) for l in (d/'capacity.jsonl').read_text().splitlines()]
    minimum=min(x['free_bytes'] for x in capacity)
    assert minimum>=plan['disk_policy']['runtime_minimum_free_bytes']
    unchanged={str(p.relative_to(SUITE/'tasks/dev-multi-file/input')):digest(p)==digest(d/'workspace'/p.relative_to(SUITE/'tasks/dev-multi-file/input')) for p in (SUITE/'tasks/dev-multi-file/input').rglob('*') if p.is_file()}
    grade=verify('dev-multi-file',d/'workspace')
    return {'experiment':'AW-0215','evidence_integrity_passed':True,'screen_passed':False,'charged_utility':0,'execution':execution,'collector_error':json.loads((R/'summary.json').read_text())['error'],'raw_receipt_sha256':digest(R/'sha256-recursive.json'),'plan_sha256':digest(R/'plan.json'),'external_evidence':str(R),'protocol_checks':protocol['checks'],'protocol_passed':protocol['passed'],'tool_accounting':account,'command_sha256':[hashlib.sha256(e['args']['command'].encode()).hexdigest() for e in starts],'invalid_utf8_spans':invalid,'diagnostic_log_policy':'surrogateescape preserves raw bytes; strict Pi JSON remains unchanged; no protocol gate waived','workspace_input_files_unchanged':unchanged,'all_input_files_unchanged':all(unchanged.values()),'grader_utility':grade['utility'],'minimum_sampled_free_bytes':minimum,'host_passed':execution['pressure_peak']<4 and execution['swap_growth_peak_mib']<=1024,'scope':'Negative development evidence; original frozen summary untouched, task attempted despite collector listing it unattempted, no endpoint qualification'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
