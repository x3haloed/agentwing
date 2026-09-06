import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from stable_workspace import OWNER, staged_workspace

class StableWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name).resolve()
        self.root=self.base/'active';self.source=self.base/'input';self.source.mkdir()
        (self.source/'file.txt').write_text('original')
        self.archive=self.base/'archive';self.archive.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def test_fresh_repeated_path_and_archived_state(self):
        seen=[]
        for i in range(2):
            archive=self.archive/str(i);archive.mkdir()
            with staged_workspace(self.root,self.source,archive) as workspace:
                seen.append(workspace)
                self.assertEqual((workspace/'file.txt').read_text(),'original')
                (workspace/'file.txt').write_text(str(i))
                (self.root/'agentwing-task-state').mkdir()
                (self.root/'agentwing-task-state'/'state').write_text(str(i))
            self.assertEqual((archive/'workspace/file.txt').read_text(),str(i))
            self.assertEqual((archive/'agentwing-task-state/state').read_text(),str(i))
        self.assertEqual(seen[0],seen[1])
        self.assertEqual(set(self.root.iterdir()),{self.root/'.agentwing-owner'})
    def test_exception_preserves_changed_workspace(self):
        with self.assertRaisesRegex(RuntimeError,'attempt failed'):
            with staged_workspace(self.root,self.source,self.archive) as workspace:
                (workspace/'file.txt').write_text('partial')
                raise RuntimeError('attempt failed')
        self.assertEqual((self.archive/'workspace/file.txt').read_text(),'partial')
    def test_unowned_or_unfinished_content_is_not_removed(self):
        self.root.mkdir();(self.root/'important').write_text('keep')
        with self.assertRaisesRegex(RuntimeError,'Unowned'):
            with staged_workspace(self.root,self.source,self.archive):pass
        (self.root/'.agentwing-owner').write_text(OWNER)
        with self.assertRaisesRegex(RuntimeError,'unfinished'):
            with staged_workspace(self.root,self.source,self.archive):pass
        self.assertEqual((self.root/'important').read_text(),'keep')
    def test_archive_collision_is_not_overwritten(self):
        (self.archive/'workspace').mkdir()
        with self.assertRaisesRegex(RuntimeError,'unused'):
            with staged_workspace(self.root,self.source,self.archive):pass
    def test_original_boundary_uses_stable_cwd_and_scoped_writes(self):
        wrapper=Path(__file__).resolve().with_name('run_task_boundary.py')
        forbidden=self.base/'outside.txt'
        code="""import os,json
from pathlib import Path
Path('allowed.txt').write_text('ok')
Path(os.environ['TMPDIR'],'state.txt').write_text('ok')
denied=False
try: Path(%r).write_text('forbidden')
except PermissionError: denied=True
print(json.dumps({'cwd':os.getcwd(),'denied':denied}))
""" % str(forbidden)
        with staged_workspace(self.root,self.source,self.archive) as workspace:
            result=subprocess.run([sys.executable,str(wrapper),'--workspace',str(workspace),
                                   '--',sys.executable,'-c',code],capture_output=True,text=True,check=True)
            report=json.loads(result.stdout)
            self.assertEqual(report,{'cwd':str(workspace),'denied':True})
        self.assertFalse(forbidden.exists())
        self.assertTrue((self.archive/'workspace/allowed.txt').is_file())
        self.assertTrue((self.archive/'agentwing-task-state/tmp/state.txt').is_file())

if __name__=='__main__':unittest.main()
