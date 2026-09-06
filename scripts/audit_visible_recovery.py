#!/usr/bin/env python3
"""Compare completed recovery transcripts without pretending to observe wire tokens."""
import argparse
import copy
import json
from pathlib import Path
from run_local_agent import digest


def read_run(run):
    receipt = json.loads((run/'sha256-recursive.json').read_text())
    current = {str(p.relative_to(run)): digest(p) for p in run.rglob('*')
               if p.is_file() and not p.is_symlink() and p.name != 'sha256-recursive.json'}
    if current != receipt:
        raise ValueError(f'Changed or incomplete evidence: {run}')
    events = [json.loads(line) for line in (run/'dev-recovery/pi.jsonl').read_text().splitlines() if line.strip()]
    sessions = [e for e in events if e.get('type') == 'session']
    if len(sessions) != 1:
        raise ValueError('Expected one Pi session')
    commands, replies, results, visible = [], [], [], []
    for event in events:
        if event.get('type') == 'tool_execution_start':
            commands.append(event.get('args', {}).get('command'))
        elif event.get('type') == 'message_end' and event.get('message', {}).get('role') == 'assistant':
            content = copy.deepcopy(event['message']['content'])
            for block in content:
                if block.get('type') == 'toolCall':
                    block.pop('id', None)
            replies.append(content)
            visible.append({'kind': 'assistant', 'content': content})
        elif event.get('type') == 'tool_execution_end':
            result = {'result': event.get('result'), 'isError': bool(event.get('isError'))}
            results.append(result)
            visible.append({'kind': 'tool_result', **result})
    return {'run': str(run), 'receipt_sha256': digest(run/'sha256-recursive.json'),
            'cwd': sessions[0]['cwd'], 'commands': commands, 'replies': replies,
            'results': results, 'visible': visible}


def compare(left, right):
    count = 0
    for a, b in zip(left['visible'], right['visible']):
        if a != b:
            break
        count += 1
    complete = count == len(left['visible']) == len(right['visible'])
    enough = all(len(r[key]) >= n for r in [left, right]
                 for key, n in [('commands', 8), ('replies', 7), ('results', 7)])
    prefix_equal = enough and all(left[k][:7] == right[k][:7] for k in ['commands', 'replies', 'results'])
    # The seven inspection/validation calls and eighth first repair are the
    # explicitly observed AW-0047 trajectory, not a general repair classifier.
    original_inspection = ['find . -maxdepth 3 -type f | head -80', 'cat README.md',
                           'cat docs/tooling.md', 'cat tools/check.py', 'cat queue_names.py',
                           'cat scripts/validate.sh', 'python3 tools/check.py 2>&1']
    return {'left': left['run'], 'right': right['run'],
            'same_cwd': left['cwd'] == right['cwd'],
            'equal_visible_event_prefix_length': count,
            'complete_visible_transcripts_equal': complete,
            'first_differing_visible_events': None if complete else {
                'left': left['visible'][count] if count < len(left['visible']) else None,
                'right': right['visible'][count] if count < len(right['visible']) else None},
            'enough_events_for_seven_call_comparison': enough,
            'first_seven_commands': [left['commands'][:7], right['commands'][:7]],
            'first_seven_commands_match_original_inspection_spelling': all(r['commands'][:7] == original_inspection for r in [left, right]),
            'identical_seven_call_structured_visible_prefix': prefix_equal,
            'eighth_commands_equal_given_identical_prefix': left['commands'][7] == right['commands'][7] if prefix_equal else None,
            'eighth_commands': [r['commands'][7] if len(r['commands']) > 7 else None for r in [left, right]]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('runs', nargs='+', type=Path)
    args = parser.parse_args()
    if len(args.runs) not in [2, 3]:
        parser.error('Provide C1 C2, or C1 A1 C2')
    rows = [read_run(run) for run in args.runs]
    result = {'arms': [{k: r[k] for k in ['run', 'receipt_sha256', 'cwd']} for r in rows],
              'control_comparison': compare(rows[0], rows[-1]),
              'candidate_comparisons': [compare(rows[0], rows[1]), compare(rows[-1], rows[1])] if len(rows) == 3 else [],
              'limits': ['Only generated call IDs are removed from structured assistant content; tool results are exact, with no workspace substitution',
                         'Unrecorded wire tokens, raw accepted spellings and runtime arithmetic cannot be equated from visible transcript equality',
                         'An eighth command is only the first repair when manual inspection establishes that trajectory; differing earlier exploration makes that index inconclusive',
                         'This audit does not change any grade, protocol gate or prior negative result']}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
