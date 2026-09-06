"""Checks for selection and observable protocol corruption, no model needed."""
import json
from pathlib import Path
import tempfile
import unittest
from run_p2_development import protocol_audit, select_tasks

class RunnerTests(unittest.TestCase):
    def test_heldout_excluded(self):
        m={'tasks':[{'id':'d','split':'development'},{'id':'h','split':'held-out'}]}
        self.assertEqual(select_tasks(m,'all'),[m['tasks'][0]])
        with self.assertRaises(ValueError):select_tasks(m,'h')

    def audit(self,events,log=None):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'pi.jsonl').write_text('\n'.join(json.dumps(e) for e in events))
            (p/'server.log').write_text(log or '[chatcmpl-x] 20 prompt + 0 reused (0 prefix matched) + 8 generated, ttft 1.0s, 2.0 tok/s\n')
            return protocol_audit(p)

    def test_valid_and_unpaired(self):
        start={'type':'tool_execution_start','toolCallId':'a','toolName':'bash','args':{'command':'pwd'}}
        end={'type':'tool_execution_end','toolCallId':'a','isError':False}
        self.assertTrue(self.audit([start,end])['passed'])
        self.assertFalse(self.audit([start])['passed'])
        self.assertFalse(self.audit([start,end,start,end])['passed'])

    def test_errors_and_state_reuse(self):
        self.assertFalse(self.audit([{'type':'message_end','message':{'stopReason':'error'}}])['passed'])
        self.assertFalse(self.audit([{'type':'agent_end'}], '[chatcmpl-x] 20 prompt + 1 reused (1 prefix matched) + 8 generated, ttft 1.0s, 2.0 tok/s\n')['passed'])

if __name__=='__main__':unittest.main()
