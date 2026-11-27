import assert from 'node:assert/strict';
import test from 'node:test';
import {normalize} from '@deepviz/agent-toolkit';

const identity={kind:'table',aggregation:'none'};

for(const [format,delimiter] of [['csv',','],['tsv','\t']]) {
  test(`Python whitespace rejects blank ${format} headers but preserves a mapped FEFF header`,()=>{
    assert.throws(()=>normalize(`"\u001f\u0085"${delimiter}v\nx${delimiter}1\n`,{...identity,format}),/header|empty/i);
    const result=normalize(`"\uFEFF"${delimiter}v\nx${delimiter}1\n`,{...identity,format,x:'\uFEFF'});
    assert.deepEqual(result.records,[{'\uFEFF':'x',v:1}]);
    assert.deepEqual(result.warnings,[]);
  });
}

test('Python blank text lines are skipped but a noninitial JSONL FEFF is not silently discarded',()=>{
  assert.deepEqual(normalize('\u001c\u001d\u001e\u001f\u0085',identity).records,[]);
  assert.deepEqual(normalize('{"v":1}\n\u001c\u0085\n{"v":2}',{...identity,format:'jsonl'}).records,[{v:1},{v:2}]);
  assert.throws(()=>normalize('{"v":1}\n\uFEFF\n{"v":2}',{...identity,format:'jsonl'}),/JSON/i);
});
