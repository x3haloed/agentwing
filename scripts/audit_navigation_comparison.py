"""Audit the frozen AW-0059 C1/A1/C2 diagnostic without promotion claims."""
import datetime
import json
from pathlib import Path
import sys
from audit_matched_navigation import audit
from compare_navigation_transcripts import read,compare
from run_local_agent import ROOT,digest


def assess(runs):
    assert len(runs)==3
    audits=[audit(r) for r in runs]
    assert [a['slot'] for a in audits]==['C1','A1','C2']
    assert all(a['complete_arm'] and a['record_integrity_passed'] for a in audits)
    manifests=[json.loads((r/'manifest.json').read_text()) for r in runs]
    for key in ['workspace_policy','selection','task_timeout_seconds','original_suite_hashes','source_hashes','screen_plan_sha256','inherited_runtime_environment']:
        assert all(m[key]==manifests[0][key] for m in manifests),key
    assert manifests[0]['server_command']==manifests[2]['server_command']
    assert manifests[0]['server_binary_sha256']==manifests[2]['server_binary_sha256']
    times=[]
    for run in runs:
        rows=(run/'01-navigation/pressure.tsv').read_text().splitlines()
        times.append([datetime.datetime.fromisoformat(s.split('\t')[0]) for s in (rows[0],rows[-1])])
    assert times[0][1]<times[1][0] and times[1][1]<times[2][0]
    visible=[read(r) for r in runs]
    comparisons=[compare(visible[0],visible[1]),compare(visible[1],visible[2]),compare(visible[0],visible[2])]
    utilities=[a['accepted_utility'] for a in audits]
    shared_failure=utilities==[0,0,0] and all(c['complete_visible_transcripts_equal'] for c in comparisons)
    return {'experiment':'AW-0059','record_and_configuration_audits_passed':True,'observed_pressure_intervals_interleaved_without_overlap':True,'arms':audits,'visible_comparisons':comparisons,'shared_visible_failure_reproduced':shared_failure,'sum_charged_arm_wall_seconds':sum(a['wall_seconds'] for a in audits),'accepted_utilities':utilities,'utility_rate_gain_established':False,'scope':'One matched navigation diagnostic. Zero utility cannot establish speedup; visible equality does not prove hidden-state equality or explain historical-path sensitivity. Full preservation/performance goal remains unmet.','auditor_sha256':digest(Path(__file__))}

if __name__=='__main__':print(json.dumps(assess([Path(p) for p in sys.argv[1:]]),indent=2))
