from pathlib import Path
import hashlib,json,os,sys
import pytest
import deepviz.models as models
OUT=Path(os.environ['R25_OUT']);SNAP=Path.cwd();record=json.loads((OUT/'source-identity.json').read_text());expected=SNAP/'python/deepviz/src/deepviz/models.py';assert Path(models.__file__).resolve()==expected.resolve();assert hashlib.sha256(expected.read_bytes()).hexdigest()==record['all_tree_files']['python/deepviz/src/deepviz/models.py']['sha256'];print(json.dumps({'source':record['source'],'actual_model':models.__file__,'model_sha256':hashlib.sha256(expected.read_bytes()).hexdigest(),'same_process_before_new_test':True}));sys.exit(pytest.main(['-q','--strict-markers','--tb=short','-p','no:cacheprovider','--junitxml',str(OUT/'new-mapping-boundary.xml'),os.environ['R25_NEW_PROBE']]))