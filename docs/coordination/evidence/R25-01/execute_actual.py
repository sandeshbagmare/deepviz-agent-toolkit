from __future__ import annotations
from collections import UserDict
import hashlib,importlib.metadata,json,os,sys
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
import deepviz.models as loaded

OUT=Path(os.environ['R25_OUT']);SNAP=Path.cwd();EXPECTED=SNAP/'python/deepviz/src/deepviz/models.py';identity=json.loads((OUT/'source-identity.json').read_text())
assert Path(loaded.__file__).resolve()==EXPECTED.resolve()
assert hashlib.sha256(EXPECTED.read_bytes()).hexdigest()==identity['all_tree_files']['python/deepviz/src/deepviz/models.py']['sha256']
assert all(hashlib.sha256((SNAP/rel).read_bytes()).hexdigest()==meta['sha256'] for rel,meta in identity['all_tree_files'].items())
proof={'source':identity['source'],'base':identity['base'],'actual_model_path':loaded.__file__,'actual_model_sha256':hashlib.sha256(EXPECTED.read_bytes()).hexdigest(),'all14Gitblobs_exact':True,'same_process_pytest':True,'python':sys.version,'versions':{name:importlib.metadata.version(name) for name in ['pydantic','pytest','jsonschema','ruff','mypy']},'path':sys.path};(OUT/'actual-import-proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(proof))
rc=pytest.main(['-q','--strict-markers','--tb=short','-p','no:cacheprovider','--junitxml',str(OUT/'actual998-47.xml'),'tests',os.environ['R25_OWN_PROBE']]);print('ACTUAL47_EXIT',rc)
schema=loaded.ChartSpec.model_json_schema();Draft202012Validator.check_schema(schema);generated=(json.dumps(schema,indent=2)+'\n').encode();published=(SNAP/'schemas/chart-spec.schema.json').read_bytes();assert generated==published;(OUT/'actual-generated.schema.json').write_bytes(generated)
fixtures=json.loads((SNAP/'docs/verification/r22-contract/validation-output.json').read_text());validator=Draft202012Validator(schema);accepted=[];rejected=[]
for fixture in fixtures['accepted']:
    parsed=loaded.ChartSpec.model_validate_json(json.dumps(fixture['input']));actual=json.loads(parsed.model_dump_json());validator.validate(actual);assert actual==fixture['actual_json_output'];assert fixture['schema_valid'] is True;accepted.append({'input':fixture['input'],'actual_json_output':actual,'schema_valid':True})
for fixture in fixtures['rejected']:
    payload=fixture['input'];assert validator.is_valid(payload) is False
    try:loaded.ChartSpec.model_validate_json(json.dumps(payload))
    except ValidationError as error:
        errors=[{key:item[key] if key!='loc' else list(item[key]) for key in ['type','loc','msg']} for item in error.errors(include_url=False)];assert errors==fixture['actual_errors'];rejected.append({'input':payload,'schema_valid':False,'actual_errors':errors})
    else:raise AssertionError('Provided negative unexpectedly accepted')
output={'source':identity['source'],'scope':'Actual same-process model JSON outputs independently regenerated and compared to ALL10 committed fixtures','accepted':accepted,'rejected':rejected,'accepted_count':len(accepted),'rejected_count':len(rejected),'schema_bytes_match_commit':True,'schema_sha256':hashlib.sha256(generated).hexdigest(),'parent_e44_executed':False};(OUT/'independent-validation-output.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'independent_committed_outputs':{'accepted':len(accepted),'rejected':len(rejected),'schema_sha256':output['schema_sha256']}}))
# One uncovered native-input diagnostic, NOT a baseline replay or a test pass.
diagnostics=[]
for field,value in [('width','900'),('version',True),('columns',True),('width',900)]:
    for kind,constructor in [('dict',dict),('UserDict',UserDict)]:
        payload=constructor({field:value})
        try:parsed=loaded.ChartSpec.model_validate(payload)
        except ValidationError:record={'field':field,'value':value,'native_input_type':kind,'accepted':False}
        else:record={'field':field,'value':value,'native_input_type':kind,'accepted':True,'coerced_actual':parsed.model_dump()[field]}
        diagnostics.append(record)
(OUT/'native-mapping-diagnostic.json').write_text(json.dumps({'source':identity['source'],'actual_import':proof,'diagnostics':diagnostics,'classification':'observational counterexample investigation, not pytest pass or policy disposition'},indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'native_mapping_diagnostic':diagnostics}));sys.exit(rc)