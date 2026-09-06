"""Owned, fixed-path workspace staging; archive every attempt without deletion."""
from contextlib import contextmanager
from pathlib import Path
import shutil

OWNER = 'Agentwing fixed-path workspace staging v1\n'

@contextmanager
def staged_workspace(root: Path, source: Path, archive: Path):
    marker = root / '.agentwing-owner'
    if root.is_symlink():
        raise RuntimeError('Staging root must not be a symlink')
    if not root.exists():
        root.mkdir(mode=0o700)
        marker.write_text(OWNER)
    if not marker.is_file() or marker.is_symlink() or marker.read_text() != OWNER:
        raise RuntimeError('Unowned staging root; preserve existing contents')
    if set(root.iterdir()) != {marker}:
        raise RuntimeError('Staging root contains an unfinished or unexpected artifact; preserve it')
    if not archive.is_dir() or any((archive/n).exists() or (archive/n).is_symlink()
                                   for n in ['workspace', 'agentwing-task-state']):
        raise RuntimeError('Archive must exist with unused workspace/state destinations')
    workspace = root / 'workspace'
    try:
        shutil.copytree(source, workspace)
        yield workspace
    finally:
        # Caller must stop its owned processes before leaving this context.
        # Rename on the same filesystem; do not copy through or delete symlinks.
        for name in ['workspace', 'agentwing-task-state']:
            item = root/name
            if item.exists() or item.is_symlink():
                destination = archive/name
                if destination.exists() or destination.is_symlink():
                    raise RuntimeError('Archive collision; preserve staging artifacts')
                item.rename(destination)
