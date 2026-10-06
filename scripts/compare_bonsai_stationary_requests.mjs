// Offline AW-0195 request reconstruction with the installed Pi adapter.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {convertMessages} from '../node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/openai-completions-ERMU2SS7.js';
const root='/Users/chad/Models/agentwing/evidence/AW-0195';
mkdirSync(root,{recursive:true});
const run='/Users/chad/Models/agentwing/evidence/AW-0194/20261006T170250.455912Z/dev-multi-file';
const hash=x=>createHash('sha256').update(x).digest('hex');
const save=(name,x)=>writeFileSync(`${root}/${name}`,JSON.stringify(x,null,2)+'\n');
const events=readFileSync(`${run}/pi.jsonl`,'utf8').trim().split('\n').map(JSON.parse);
const messages=events.filter(x=>x.type==='message_end').map(x=>x.message);
if(messages.length!==7 || messages.map(x=>x.role).join(',')!=='user,assistant,toolResult,assistant,toolResult,assistant,toolResult')throw Error('Unexpected completed history');
const provider=JSON.parse(readFileSync(new URL('../config/pi-bonsai-turbo-models.json',import.meta.url))).providers['agentwing-bonsai'];
const model={...provider.models[0],provider:'agentwing-bonsai',api:provider.api};
const command=JSON.parse(readFileSync(`${run}/client-command.json`));
const cwd=command[command.indexOf('--workspace')+1];
const context={messages,systemPrompt:readFileSync(`${run}/system-prompt.txt`,'utf8').replace(/\n$/,'')+'\nCurrent working directory: '+cwd};
const previous=JSON.parse(readFileSync('/Users/chad/Models/agentwing/evidence/AW-0145/fourth-request.json'));
const current={messages:convertMessages(model,context,provider.compat),tools:previous.tools,reasoning_effort:'medium',add_generation_prompt:true};
save('fourth-context.json',context);save('fourth-request.json',current);
function normalize(body){const x=structuredClone(body);const ids=new Map();let n=0;for(const m of x.messages){for(const c of m.tool_calls??[]){ids.set(c.id,`call-${n}`);c.id=`call-${n++}`;}if(m.tool_call_id)m.tool_call_id=ids.get(m.tool_call_id)??m.tool_call_id;}return x;}
const a=normalize(previous),b=normalize(current),differences=[];
function diff(x,y,path){if(JSON.stringify(x)===JSON.stringify(y))return;if(x&&y&&typeof x==='object'&&typeof y==='object'){for(const key of new Set([...Object.keys(x),...Object.keys(y)]))diff(x[key],y[key],`${path}/${key}`);return;}differences.push({path,previous_sha256:hash(JSON.stringify(x)??'undefined'),current_sha256:hash(JSON.stringify(y)??'undefined'),previous_characters:typeof x==='string'?x.length:null,current_characters:typeof y==='string'?y.length:null});}
diff(a,b,'');
const receipt={experiment:'AW-0195',scope:'Offline installed-adapter reconstruction; not wire capture or runtime replay',tools_source:'AW-0145 frozen native tool schema; installed Pi unchanged under AW-0194 pins',completed_messages:messages.length,normalized_requests_equal:JSON.stringify(a)===JSON.stringify(b),differences,raw_sha256:Object.fromEntries(['fourth-context.json','fourth-request.json'].map(n=>[n,hash(readFileSync(`${root}/${n}`))])),input_sha256:{transcript:hash(readFileSync(`${run}/pi.jsonl`)),system_prompt:hash(readFileSync(`${run}/system-prompt.txt`)),previous_request:hash(readFileSync('/Users/chad/Models/agentwing/evidence/AW-0145/fourth-request.json')),prompt_builder:hash(readFileSync(new URL('../node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/chunk-OMWWHBTG.js',import.meta.url))),adapter:hash(readFileSync(new URL('../node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/openai-completions-ERMU2SS7.js',import.meta.url))),script:hash(readFileSync(new URL(import.meta.url)))}};
save('comparison.json',receipt);console.log(JSON.stringify(receipt,null,2));
