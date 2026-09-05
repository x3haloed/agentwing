"""Real Pi, synthetic server, production task-launch lifecycle; no model load."""
import datetime
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('agent', ROOT / 'scripts/run_local_agent.py')
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)
agent.preflight()
run = Path('/Users/chad/Models/agentwing/evidence/AW-0028') / ('protocol-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
run.mkdir(parents=True)
(run / 'workspace').mkdir()
(run / 'workspace/INPUT.txt').write_text('status=old\n')
report = agent.execute(run, ['/usr/bin/python3', str(ROOT / 'tests/shell_protocol_fixture_server.py')],
                       agent.pi_command(run / 'workspace', ROOT / 'config/pi-models-validated.json',
                                        'Read INPUT.txt, update its status in OUTPUT.txt, recover from a failed command, and verify.'), timeout=30)
print(run)
print(json.dumps(report, indent=2))
assert report['status'] == 'client-completed'
assert (run / 'workspace/OUTPUT.txt').read_text().strip() == 'status=new'
events = [json.loads(x) for x in (run / 'pi.jsonl').read_text().splitlines()]
ends = [x for x in events if x.get('type') == 'tool_execution_end']
assert len(ends) == 5
assert sum(x.get('isError', False) for x in ends) == 1
assert 'shell protocol fixture: PASS' in (run / 'server.log').read_text()
(ROOT / 'evidence/AW-0028-launcher-protocol.json').write_text(json.dumps({
    'run': str(run), 'report': report, 'five_tool_results': True, 'one_expected_failure': True,
    'artifact_passed': True, 'launcher_sha256': agent.digest(ROOT / 'scripts/run_local_agent.py')}, indent=2) + '\n')
