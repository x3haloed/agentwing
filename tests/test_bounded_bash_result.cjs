const { test } = require('node:test');
const assert = require('node:assert/strict');
let hook;
require('../extensions/bounded-bash-result.js')({ on: (name, fn) => {
  assert.equal(name, 'tool_result'); hook = fn;
} });

test('long failed output preserves diagnostics, evidence, and Unicode within cap', () => {
  const text = 'ERROR: first failure\n' + '🦉'.repeat(1500) + '\nFAILED (failures=2)';
  const result = hook({toolName:'bash', content:[{type:'text',text}], isError:true,
                       details:{fullOutputPath:'/owned/output.txt'}});
  assert.equal(Array.from(result.content[0].text).length,1024);
  assert.ok(result.content[0].text.startsWith('ERROR: first failure'));
  assert.ok(result.content[0].text.endsWith('FAILED (failures=2)'));
  assert.ok(result.content[0].text.includes('output truncated'));
  assert.equal(result.isError,true);
  assert.equal(result.details.agentwingBoundedResult.originalText,text);
  assert.equal(result.details.fullOutputPath,'/owned/output.txt');
  assert.equal(result.content[0].text.includes('\uFFFD'),false);
});

test('ordinary success, non-bash, and mixed media remain untouched', () => {
  const e={toolName:'bash',content:[{type:'text',text:'OK'}],isError:false};
  assert.equal(hook(e),undefined);
  assert.equal(hook({...e,toolName:'read',content:[{type:'text',text:'x'.repeat(2000)}]}),undefined);
  assert.equal(hook({...e,content:[{type:'text',text:'x'.repeat(2000)},{type:'image',data:'fixture'}]}),undefined);
});
