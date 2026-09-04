#!/usr/bin/env python3
"""Optional scoped write/outbound-network boundary; not a general sandbox."""
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--models-file', type=Path)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or not 1 <= args.port <= 65535:
        parser.error('a command and a port in 1..65535 are required')
    workspace = args.workspace.resolve(strict=True)
    if not workspace.is_dir() or workspace == workspace.parent:
        parser.error('workspace must be a non-root directory')
    # Fresh, adjacent state stays outside the benchmark's input workspace.
    state = workspace.parent / 'agentwing-task-state'
    state.mkdir(mode=0o700)  # Reject pre-existing state rather than silently reuse it.
    for name in ('pi', 'tmp', 'cache'):
        (state / name).mkdir(mode=0o700)
    if args.models_file is not None:
        (state / 'pi/models.json').write_bytes(args.models_file.read_bytes())
    env = {**os.environ, 'PI_CODING_AGENT_DIR': str(state / 'pi'),
           'TMPDIR': str(state / 'tmp'), 'XDG_CACHE_HOME': str(state / 'cache'),
           'PYTHONDONTWRITEBYTECODE': '1'}
    os.chdir(workspace)
    os.execve('/usr/bin/sandbox-exec', [
        '/usr/bin/sandbox-exec', '-f', str(ROOT / 'config/task-boundary.sb'),
        '-D', f'WORKSPACE={workspace}', '-D', f'STATE={state}',
        '-D', f'ENDPOINT=localhost:{args.port}', *command], env)


if __name__ == '__main__':
    main()
