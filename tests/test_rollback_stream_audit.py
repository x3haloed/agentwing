"""Public synthetic wire failures; never expose benchmark requests."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_bonsai_rollback_full_request import stream

def event(delta=None,finish=None):
 return b'data: '+json.dumps({'id':'completion-a','choices':[{'index':0,'delta':delta or {},'finish_reason':finish}]}).encode()+b'\n\n'

class StreamAudit(unittest.TestCase):
 def audit(self,data):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'response.sse';p.write_bytes(data);return stream(p)
 def tool(self,args='{"command":"true"}',tool_id='call-a',name='bash'):
  return event({'tool_calls':[{'index':0,'id':tool_id,'type':'function','function':{'name':name,'arguments':args}}]})
 def valid(self):return self.tool()+event(finish='tool_calls')+b'data: [DONE]\n\n'
 def test_valid_and_fragmented_tool(self):
  self.assertTrue(self.audit(self.valid())['terminal_protocol_passed'])
  raw=self.tool('{"command":')+event({'tool_calls':[{'index':0,'function':{'arguments':'"true"}'}}]})+event(finish='tool_calls')+b'data: [DONE]\n\n'
  self.assertTrue(self.audit(raw)['terminal_protocol_passed'])
 def test_incomplete_not_counted_as_completed_malformed(self):
  result=self.audit(self.tool('{"command":'))
  self.assertFalse(result['terminal_protocol_passed']);self.assertEqual(result['proposals'][0]['classification'],'incomplete-proposal')
 def test_duplicate_done_and_data_after_done(self):
  for suffix in [b'data: [DONE]\n\n',event({'content':'late'})]:
   self.assertFalse(self.audit(self.valid()+suffix)['terminal_protocol_passed'])
 def test_ambiguous_or_nonfinite_arguments(self):
  for args in ['{"command":"true","command":"false"}','{"command":"true","timeout":NaN}','{"command":"true","timeout":1e400}','{"command":"true","timeout":true}','{"command":""}']:
   raw=self.tool(args)+event(finish='tool_calls')+b'data: [DONE]\n\n'
   self.assertFalse(self.audit(raw)['terminal_protocol_passed'])
 def test_tool_id_cannot_change(self):
  raw=self.tool('{"command":')+event({'tool_calls':[{'index':0,'id':'call-b','function':{'arguments':'"true"}'}}]})+event(finish='tool_calls')+b'data: [DONE]\n\n'
  self.assertFalse(self.audit(raw)['terminal_protocol_passed'])
 def test_wire_json_corruption_and_completion_id_change(self):
  for suffix in [b'data: {"id":"a","id":"b"}\n\n',b'data: {"id":"a","bad":NaN}\n\n',event().replace(b'completion-a',b'completion-b')]:
   self.assertFalse(self.audit(suffix+self.valid())['terminal_protocol_passed'])

if __name__=='__main__':unittest.main()
