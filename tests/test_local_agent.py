import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch, Mock

SPEC = importlib.util.spec_from_file_location('local_agent', Path(__file__).resolve().parents[1] / 'scripts/run_local_agent.py')
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class LifecycleTests(unittest.TestCase):
    def launch(self, code):
        p = subprocess.Popen(['/usr/bin/python3', '-c', code], start_new_session=True)
        self.addCleanup(agent.stop_group, p)
        return p

    def test_darwin_disappeared_group_permission_race(self):
        with patch.object(agent.os, 'killpg', side_effect=PermissionError), patch.object(agent.subprocess, 'run') as probe:
            probe.return_value = Mock(returncode=1)
            agent.signal_group(123456, signal.SIGKILL)
            probe.return_value = Mock(returncode=0)
            with self.assertRaises(PermissionError):
                agent.signal_group(123456, signal.SIGKILL)

    def test_success_and_client_failure(self):
        server = self.launch('import time; time.sleep(30)')
        for code in (0, 7):
            client = self.launch(f'raise SystemExit({code})')
            self.assertEqual(agent.supervise(client, server, 700, lambda: (1, 700), lambda x: None, 2, .01), code)

    def test_deadline_and_host_stops(self):
        server = self.launch('import time; time.sleep(30)')
        client = self.launch('import time; time.sleep(30)')
        for sample, timeout, error in [(lambda: (1, 700), .05, 'stopped-timeout'),
                                       (lambda: (4, 700), 2, 'stopped-critical-pressure'),
                                       (lambda: (1, 1725), 2, 'stopped-swap-growth')]:
            with self.assertRaisesRegex(RuntimeError, error):
                agent.supervise(client, server, 700, sample, lambda x: None, timeout, .01)

    def test_server_failure(self):
        server = self.launch('raise SystemExit(1)'); server.wait()
        client = self.launch('import time; time.sleep(30)')
        with self.assertRaisesRegex(RuntimeError, 'server-exited'):
            agent.supervise(client, server, 700, lambda: (1, 700), lambda x: None)

    def test_execute_always_cleans_and_records_timeout(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(agent, 'ready', return_value=True):
            report = agent.execute(Path(directory), ['/bin/sleep', '30'], ['/bin/sleep', '30'],
                                   timeout=.02, sample=lambda: (1, 700))
            self.assertEqual(report['error'], 'stopped-timeout')
            self.assertTrue((Path(directory) / 'result.json').is_file())
            self.assertTrue((Path(directory) / 'sha256.json').is_file())
            for pid in (report['server_pid'], report['client_pid']):
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def test_cleanup_after_parent_exits(self):
        with tempfile.TemporaryDirectory() as directory:
            pidfile = Path(directory) / 'child'
            parent = self.launch('import subprocess; from pathlib import Path; '
                                 f'p=subprocess.Popen(["/bin/sleep", "30"]); Path({str(pidfile)!r}).write_text(str(p.pid))')
            parent.wait(timeout=3)
            child = int(pidfile.read_text())
            agent.stop_group(parent)
            for _ in range(100):
                try:
                    os.kill(child, 0)
                except ProcessLookupError:
                    break
                time.sleep(.01)
            else:
                self.fail('descendant survived cleanup')


if __name__ == '__main__':
    unittest.main()
