#!/usr/bin/env python3
"""Create once or verify the P2 corpus receipt; runner freeze is separate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from verify_p2_task import ROOT, SUITE

RECEIPT=ROOT/'evidence/AW-0034-corpus-freeze-v1.json'


def inputs():
    return sorted([p for p in SUITE.rglob('*') if p.is_file()]+[ROOT/p for p in [
        'scripts/verify_p2_task.py','scripts/audit_p2_suite.py','scripts/freeze_p2_suite.py',
        'scripts/run_local_agent.py','spec/p2-acceptance.json','spec/validated-local-agent.json',
        'evidence/AW-0034-full-authority-audit.json']])


def main():
    p=argparse.ArgumentParser();p.add_argument('--create',action='store_true');args=p.parse_args()
    manifest=json.loads((SUITE/'manifest.json').read_text());tasks=manifest['tasks']
    contract=json.loads((ROOT/'spec/p2-acceptance.json').read_text())['capability_evaluation']
    assert len(tasks)==24 and len({t['id'] for t in tasks})==24
    assert Counter(t['split'] for t in tasks)=={'development':8,'held-out':16}
    for split,count in [('development',1),('held-out',2)]:
        assert Counter(t['category'] for t in tasks if t['split']==split)=={c:count for c in contract['categories']}
    assert not any(p.is_symlink() for p in SUITE.rglob('*'))
    for t in tasks:
        assert (SUITE/'tasks'/t['id']/'input').is_dir()
        assert (SUITE/'authorities'/t['id']/'grade.py').is_file()
        assert (SUITE/'authorities'/t['id']/'solution').is_dir()
    audit=json.loads((ROOT/'evidence/AW-0034-full-authority-audit.json').read_text())
    assert audit['tasks_audited']==24 and {r['task_id'] for r in audit['results']}=={t['id'] for t in tasks}
    assert all(all(r[k] for k in ['pristine_rejected','reference_passed','incomplete_repair_rejected','visible_test_deletion_rejected']) for r in audit['results'])
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs()}
    if args.create:
        assert not RECEIPT.exists(),'Receipt already exists; do not overwrite a freeze'
        RECEIPT.write_text(json.dumps({'scope':'P2 corpus and authorities only; full-path runner and candidate identity must be frozen separately','task_count':24,'development':8,'held_out':16,'sha256':hashes},indent=2)+'\n')
    else:
        frozen=json.loads(RECEIPT.read_text());assert hashes==frozen['sha256'],'Frozen corpus changed'
    print(json.dumps({'corpus_receipt_sha256':hashlib.sha256(RECEIPT.read_bytes()).hexdigest(),'files':len(hashes),'corpus_integrity':'pass','scope':'No model evaluation or runner validation implied'}))


if __name__=='__main__':main()
