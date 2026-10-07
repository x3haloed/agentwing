#!/usr/bin/env python3
"""AW230 independent functional, protocol, host and reviewed tool audit."""
import argparse,base64,hashlib,json,re,struct,zlib
from pathlib import Path
import numpy as np
from bonsai_diagnostic_protocol_bytes import protocol
from run_local_agent import ROOT,digest
PLAN=ROOT/'evidence/AW-0230-multimodal-plan.json';R=Path('/Users/chad/Models/agentwing/evidence/AW-0230')
def strict_object(pairs):
 out={}
 for k,v in pairs:
  assert k not in out,'Duplicate tool argument key';out[k]=v
 return out
def main(partial=False):
 plan=json.loads(PLAN.read_text())
 for name,h in plan['pins'].items():assert digest(ROOT/name)==h
 for name,h in plan['runtime_libraries'].items():assert digest(Path('/Users/chad/Models/agentwing/runtime-builds/prism-gen-checkpoints-full/bin')/name)==h
 review=json.loads((R/'tool-review.json').read_text());records=[]
 for rep in range(2):
  runs=[p for p in R.glob(f'*-rep{rep}') if (p/'result.json').exists() and (p/'plan.json').read_bytes()==PLAN.read_bytes()]
  if not runs and partial:continue
  assert len(runs)==1;run=runs[0];result=json.loads((run/'result.json').read_text());assert result['passed']
  for name,h in json.loads((run/'sha256.json').read_text()).items():assert digest(run/name)==h
  samples=[json.loads(l) for l in (run/'pressure.jsonl').read_text().splitlines()];assert samples and max(s['pressure'] for s in samples)<4;assert max(s['swap_mib']-samples[0]['swap_mib'] for s in samples)<=1024;assert min(s['free_bytes'] for s in samples)>=8*1024**3
  cmd=json.loads((run/'command.json').read_text());expected={'--host':'127.0.0.1','--ctx-size':'16384','--parallel':'1','--cache-type-k':'f16','--cache-type-v':'f16','--ctx-checkpoints':'2','--cache-ram':'0','--reasoning-effort':'medium','--image-max-tokens':'1024'}
  for flag,value in expected.items():assert cmd.count(flag)==1 and cmd[cmd.index(flag)+1]==value
  assert '--mmproj' in cmd and '--no-context-shift' in cmd
  native_log=(run/'server.log').read_bytes().decode('utf-8',errors='surrogateescape');assert json.loads((run/'environment.json').read_text())=={'AGENTWING_GENERATION_CHECKPOINTS':'1'};assert any('16384 cells' in l and 'K (f16):' in l and 'V (f16):' in l for l in native_log.splitlines())
  text=json.loads((run/'text.json').read_text());assert text['response']['choices'][0]['message']['content'].strip()=='42'
  image=(run/'vision.png').read_bytes();pos=8;compressed=b'';assert image[:8]==b'\x89PNG\r\n\x1a\n'
  while pos<len(image):
   n=struct.unpack('>I',image[pos:pos+4])[0];kind=image[pos+4:pos+8];data=image[pos+8:pos+8+n];assert zlib.crc32(kind+data)&0xffffffff==struct.unpack('>I',image[pos+8+n:pos+12+n])[0]
   if kind==b'IHDR':assert struct.unpack('>IIBBBBB',data)==(256,128,8,2,0,0,0)
   if kind==b'IDAT':compressed+=data
   pos+=n+12
  raster=np.frombuffer(zlib.decompress(compressed),dtype=np.uint8).reshape(128,769);assert not raster[:,0].any();rgb=raster[:,1:].reshape(128,256,3);left,right=((255,0,0),(0,0,255)) if rep==0 else ((0,0,255),(255,0,0));assert np.all(rgb[:,:128]==left) and np.all(rgb[:,128:]==right)
  vision=json.loads((run/'vision.json').read_text());url=vision['request']['messages'][0]['content'][1]['image_url']['url'];assert base64.b64decode(url.split(',')[1])==image;colors=re.findall(r'\b(red|blue)\b',vision['response']['choices'][0]['message']['content'].lower());assert colors==(['red','blue'] if rep==0 else ['blue','red'])
  native=json.loads((run/'tool-selection.json').read_text());calls=native['response']['choices'][0]['message']['tool_calls'];assert len(calls)==1 and calls[0]['function']['name']=='lookup_local_code';assert json.loads(calls[0]['function']['arguments'],object_pairs_hook=strict_object)=={'key':'orchard'}
  continuation=json.loads((run/'tool-continuation.json').read_text());toolmsg=next(m for m in continuation['request']['messages'] if m['role']=='tool');code='AW62-'+hashlib.sha256(image+str(rep).encode()).hexdigest()[:10];assert toolmsg['tool_call_id']==calls[0]['id'] and toolmsg['content']==code;msg=continuation['response']['choices'][0]['message'];assert code in msg['content'] and not msg.get('tool_calls')
  expected_bytes=('LOCAL-'+hashlib.sha256(str(run).encode()).hexdigest()[:12]+'\n').encode();assert (run/'pi-workspace/source.txt').read_bytes()==expected_bytes and (run/'pi-workspace/answer.txt').read_bytes()==expected_bytes;pa=protocol(run);assert pa['passed'];reviewed=review[str(rep)];assert reviewed['commands']==pa['commands'];assert reviewed['pi_jsonl_sha256']==digest(run/'pi.jsonl');account=reviewed['accounting'];assert account['attempted']==account['valid']==len(pa['commands']);assert account['productive']+account['redundant']==account['attempted'];assert all(account[k]==0 for k in ['malformed','denied','failed'])
  ends=[json.loads(l) for l in (run/'pi.jsonl').read_text().splitlines() if l.strip()];assert not any(e.get('isError') for e in ends if e.get('type')=='tool_execution_end')
  records.append({'replicate':rep,'run':str(run),'result_sha256':digest(run/'result.json'),'wall_seconds':result['wall_seconds'],'pressure_peak':result['pressure_peak'],'swap_growth_peak_mib':result['swap_growth_peak_mib'],'minimum_free_bytes':min(s['free_bytes'] for s in samples),'vision_colors':colors,'native_tool_accounting':native['tool_accounting'],'reviewed_pi_tool_accounting':account,'pi_protocol':pa,'pi_commands':pa['commands'],'artifact_sha256':digest(run/'pi-workspace/answer.txt')})
 receipt={'experiment':'AW-0230','complete':len(records)==2,'passed':len(records)==2,'plan_sha256':digest(PLAN),'records':records,'auditor_sha256':digest(Path(__file__)),'tool_review_sha256':digest(R/'tool-review.json'),'canonical_protocol_sha256':digest(ROOT/'scripts/run_bonsai_budget_debugging_v2.py'),'scope':'Fullmultimodal/toolfunctionaladmission only, no fixedcorpus endpoint/utility claim'};(R/('partial-admission-audit.json' if partial else 'terminal-admission-audit.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');a=p.parse_args();main(a.partial)
