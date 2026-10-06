import {readFileSync,writeFileSync} from 'node:fs';
import {convertMessages} from '../node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/openai-completions-ERMU2SS7.js';
const root='/Users/chad/Models/agentwing/evidence/AW-0145';
const provider=JSON.parse(readFileSync(new URL('../config/pi-bonsai-turbo-models.json',import.meta.url))).providers['agentwing-bonsai'];
const model={...provider.models[0],provider:'agentwing-bonsai',api:provider.api};
for(const name of ['prior','fourth']) {
 const context=JSON.parse(readFileSync(`${root}/${name}-context.json`));
 const body={messages:convertMessages(model,context,provider.compat),tools:JSON.parse(readFileSync(`${root}/${name}-tools.json`)),reasoning_effort:'medium',add_generation_prompt:true};
 writeFileSync(`${root}/${name}-request.json`,JSON.stringify(body,null,2)+'\n');
}
