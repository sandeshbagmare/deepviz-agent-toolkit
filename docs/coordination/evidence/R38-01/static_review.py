from pathlib import Path
import ast,hashlib,json,subprocess
ROOT=Path.cwd();MAIN=Path('C:/Users/bagma/deepviz-agent-toolkit');OUT=ROOT/'artifacts/local/R38-01';SNAP=OUT/'source-c1b';SRC='c1b0b29a84c3f6cb69c6be9cc73cf0330043cf19';PARENT='79232fb2f402bf21d455fbc021f1c238d19abe80';rel='python/deepviz/src/deepviz/normalize.py';raw=(SNAP/rel).read_bytes();assert raw==subprocess.check_output(['git','show',SRC+':'+rel]);old=ast.parse(subprocess.check_output(['git','show',PARENT+':'+rel]));new=ast.parse(raw)
def units(tree):
    result={}
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            result[node.name]=node
        elif isinstance(node,ast.ClassDef):
            for item in node.body:
                if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)):result[node.name+'.'+item.name]=item
    return result
before=units(old);after=units(new);assert set(before)==set(after);changed=[name for name in before if ast.dump(before[name],include_attributes=False)!=ast.dump(after[name],include_attributes=False)];assert changed==['_Reducer.add','_Reducer.finish'];retained=[]
for name,node in after.items():retained.append({'unit':name,'path':rel,'start':node.lineno,'end':node.end_lineno,'AST_sha256':hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest(),'changed':name in changed,'reviewed_full_unit':True})
static={'source':SRC,'parent':PARENT,'product_runtime_calls':0,'pytest_tests_run':0,'new_counterexamples_needed':False,'changed_Python_function_units':changed,'all_other_'+str(len(after)-2)+'_units_AST_exact_parent':True,'full_normalizer_read_range':[1,776],'all_relevant_units':retained,'public_callers_reviewed':{'python/deepviz/src/deepviz/__init__.py':[1,27],'python/deepviz/src/deepviz/models.py':[1,92],'python/deepviz/src/deepviz/render.py':[1,229],'python/deepviz/src/deepviz/tools.py':[1,191],'python/deepviz/src/deepviz/cli.py':[1,60],'python/deepviz/src/deepviz/mcp_server.py':[1,115]},'producer_mean_oracles_full_read':'python/deepviz/tests/test_r17_normalizer_boundaries.py:1-139','source_finding':'no new mustfix in narrow c1b Python mean delta','later546_or_actualmain_approval':False}
for path in static['public_callers_reviewed']:assert subprocess.check_output(['git','show',PARENT+':'+path])==(SNAP/path).read_bytes()
testpath='python/deepviz/tests/test_r17_normalizer_boundaries.py';oldtests=units(ast.parse(subprocess.check_output(['git','show',PARENT+':'+testpath])));newtests=units(ast.parse((SNAP/testpath).read_bytes()));assert all(ast.dump(node,include_attributes=False)==ast.dump(newtests[name],include_attributes=False) for name,node in oldtests.items());static['original_lifetime_test_functions_unchanged_AST']=list(oldtests);static['new_producer_test_functions']=list(set(newtests)-set(oldtests));(OUT/'static-source-review.json').write_text(json.dumps(static,indent=2)+'\n',encoding='utf-8',newline='\n')
text='''

## R38 meaningful full SOURCE review checkpoint / no runtime padding

- FULLactualnormalize.py1-776 read; full_sum_units565-568/_Reducer571-684/normalize687-776/adaptersandscalarread. Connectedpublicexports/models/render1-229/tools1-191/CLI1-60/MCP1-115 andcompleteNEWproducerboundarytest1-139 read. Actualc1bGit/rawSHAf3cc6e78e188ed97f62133a954154dbfdd416128c97cd4b154144ae62f778296. StaticASTonlychangedPythonunits_Reducer.add/finish; allotherhelper/lifetime/state/publiccallerunitsparentexact. OriginalproducerlifetimefunctionsASTunchanged.
- Exact units are value.as_integer_ratio numerator*2^(1074-log2denominator); meansaccumulateONEintegernumeratorandvalidcount, finalintegertruediv(n,count<<1074), nofloatprefix/correctionrounding/rescaling. Othersharelaststateandaddrawvalidobservations, notmean-of-means. null/bool/non-numericexcludedbeforedenominator;allnullstateNone/nozero-div. Negativeunderflowkeepsnegativeintsign; exactzerohascanonicalpositivezero asrationalreference/inheritedbehavior, notsign-preservationpromise. Float-onlyfiniteobservationmeanwithinrange; hugePythonintunrepresentableresultgoesexistingnullwarningpolicy.
- StatebytebudgetcheckedBEFOREreplacement/changingretainedpayload, oneboundednumericstate/group/other; no growinginput/partialslist. Bitlength finitefloat numerator<=2098+log2validN; denominator1075+log2N, notO(N)storage;16MiBpayloadbudgetnotRSS. Sourceclose/one-pass/count/schema/warningspathsunmodified; no newfilesystem/HTML/authoritysinks.
- NO concreteNEWmeanbugfound; SOURCE-only narrowclear, 0productruntimecalls/0pytest/0benchmark/0newprobes. Avoidduplicating05meanacceptance/11crosslanguagecost. OldprefixSUM/scalar/GraphQL/546notcleared, c1bNOTmain/wholetoolkit signoff. Next executableaction finalizeownedR38source-review/evidence staticAST/hash/ranges thenONEmeaningfulOWNnonforcepublication/exactremoteSHAandreturnR04.
'''
for path in [MAIN/'docs/agent-state/ses_de5678335ffeI7xJrod5l25Q0Q.md',MAIN/'docs/coordination/reports/R38-01-mean-source-review.md']:path.write_text(path.read_text(encoding='utf-8')+text,encoding='utf-8',newline='\n')
print(json.dumps({'source':SRC,'changed_Python_units':changed,'total_units_reviewed':len(after),'public_callers_parent_exact':True,'original_lifetime_functions_AST_unchanged':True,'product_runtime_count':0,'pytest_count':0,'new_mustfix_findings':0,'later546_notapproved':True},indent=2))