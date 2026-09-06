#!/usr/bin/env python3
"""Check P2 authorities against pristine, repaired, and deliberately wrong work."""
import ast
import json
from pathlib import Path
import shutil
import tempfile
from verify_p2_task import SUITE, verify


def main():
    tasks=json.loads((SUITE/'manifest.json').read_text())['tasks']
    rows=[]
    for task in tasks:
        task_id=task['id']
        with tempfile.TemporaryDirectory(prefix='agentwing-p2-audit-') as tmp:
            workspace=Path(tmp)/'workspace'
            shutil.copytree(SUITE/'tasks'/task_id/'input',workspace)
            pristine=verify(task_id,workspace)
            assert pristine['utility']==0,(task_id,'pristine accepted')
            for p in workspace.rglob('test_*.py'):p.unlink()
            erased=verify(task_id,workspace)
            assert erased['utility']==0,(task_id,'deleting tests accepted')
            solution=SUITE/'authorities'/task_id/'solution'
            for p in solution.rglob('*'):
                if p.is_file():
                    dst=workspace/p.relative_to(solution);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
            repaired=verify(task_id,workspace)
            assert repaired['utility']==1,(task_id,repaired)
            # Known incomplete fix for each contract; never exposed to task model.
            if task_id=='dev-navigation':
                p=workspace/'ANSWER.json';value=json.loads(p.read_text());value['retry_ms']=7000;p.write_text(json.dumps(value))
            elif task_id=='dev-debugging':
                p=workspace/'windows.py';p.write_text(p.read_text().replace('max(result[-1][1], end)','end'))
            elif task_id=='dev-multi-file':
                p=workspace/'ledger/cli.py';p.write_text(p.read_text().replace('a.limit,a.include_archived','a.limit,False'))
            else:
                mutation=json.loads((SUITE/'authorities'/task_id/'mutation.json').read_text())
                p=workspace/mutation['path'];source=p.read_text()
                assert mutation['old'] in source, 'mutation does not apply'
                p.write_text(source.replace(mutation['old'],mutation['new']))
            for source_file in workspace.rglob('*.py'):
                ast.parse(source_file.read_text(), str(source_file))
            mutated=verify(task_id,workspace)
            assert mutated['utility']==0,(task_id,'incomplete fix accepted')
            rows.append({'task_id':task_id,'pristine_rejected':True,'visible_test_deletion_rejected':True,'reference_passed':True,'incomplete_repair_rejected':True})
    print(json.dumps({'tasks_audited':len(rows),'results':rows,'scope':'Author correctness and mutation smoke, not model capability; suite construction ongoing'},indent=2))


if __name__=='__main__':main()
