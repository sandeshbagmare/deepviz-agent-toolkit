const near=(a,b,tolerance=0.03)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tolerance;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function assess(fixture,row){
  const checks=[];
  const check=(name,pass,observed)=>checks.push({name,pass:!!pass,observed});
  check('original-input-not-mutated',same(row.inputAfter,fixture.records),row.inputAfter);
  check('independent-normalize-preserves-literal-finite-values-and-order',same(row.normalized?.records,fixture.records),row.normalized);
  check('independent-normalize-exact-count-none-no-warning',row.normalized?.input_count===4&&row.normalized?.strategy==='none'&&same(row.normalized?.warnings,[]),row.normalized);
  if(row.error){
    // Safe explicit rejection is visible as a separate result, never called a rendered success.
    check('clear-explicit-layout-rejection-only-for-extreme',fixture.extreme&&row.error.name==='ValidationError'&&
      /(?:finite|range|layout|represent|overflow|dimensions?)/i.test(row.error.message)&&!row.artifactReturned,row.error);
    return checks;
  }
  const {artifact,state,native}=row;
  check('public-artifact-counts-none-no-warning',artifact?.input_count===4&&artifact?.output_count===4&&artifact?.strategy==='none'&&same(artifact?.warnings,[]),artifact);
  check('public-normalized-original-values-and-order',same(artifact?.records,fixture.records),artifact?.records);
  check('native-serialization-no-NaN-or-Infinity',!/(?:NaN|[+-]?Infinity)/.test(native.svg),native.attributes);
  check('native-complete-finite-coordinate-count',native.marks.length===(['line','area'].includes(fixture.kind)?1:4)&&
    native.points.length===(fixture.kind==='area'?6:4)&&native.points.every(pair=>pair.length===2&&pair.every(Number.isFinite)),native.points);
  check('zero-unexpected-browser-console-page-or-readiness-errors',state?.errors?.length===0&&same(state?.deepvizErrors,[]),{errors:state?.errors,deepvizErrors:state?.deepvizErrors});
  check('public-html-ready-no-external-requests',state?.ready===true&&state?.requests?.length===0,state?.requests);
  check('root-title-and-dimensions',state?.title===fixture.spec.title&&state?.width===960&&state?.height===520,state&&{title:state.title,width:state.width,height:state.height});
  const axis=state?.axis;
  const validAxis=axis&&[axis.left,axis.right,axis.top,axis.bottom].every(Number.isFinite)&&axis.right-axis.left>400&&axis.bottom-axis.top>200;
  check('finite-nondegenerate-quantitative-plot',validAxis,axis);
  // Only small pixel extents are interpolated, using separately literal fractions; input domain subtraction is NEVER done.
  const x=i=>axis.left+fixture.xFractions[i]*(axis.right-axis.left);
  const y=i=>axis.top+fixture.yFractionsFromTop[i]*(axis.bottom-axis.top);
  const points=fixture.kind==='area'?state?.points?.slice(1,-1):state?.points;
  const expected=validAxis?fixture.records.map((_,i)=>[x(i),y(i)]):[];
  check('all-four-literal-points-correct-independent-finite-fractions',validAxis&&points?.length===4&&
    points.every((pair,i)=>near(pair[0],expected[i][0])&&near(pair[1],expected[i][1])),{actual:points,expected});
  const gaps=points?.length===4?[points[1][0]-points[0][0],points[2][0]-points[1][0],points[3][0]-points[2][0]]:[];
  check('unequal-quantitative-x-gaps-1-1-2-not-collapsed',gaps.length===3&&gaps[0]>0&&near(gaps[1]/gaps[0],1,1e-4)&&near(gaps[2]/gaps[0],2,1e-4),gaps);
  check('complete-native-browser-point-count-and-real-paint',state?.points?.length===(fixture.kind==='area'?6:4)&&state?.painted===true,{points:state?.points,marks:state?.marks});
  check('all-literal-table-cell-values-and-order',same(state?.table,fixture.records.map(record=>Object.values(record).map(String))),state?.table);
  check('all-full-literal-x-tick-labels-and-finite-alignment',state?.ticks?.length===4&&state.ticks.every((tick,i)=>
    tick.literal===String(fixture.xs[i])&&validAxis&&near(tick.x,x(i))),state?.ticks);
  check('native-text-not-clipped-or-pairwise-overlapping',state?.textInside===true&&state?.tickOverlap===false,{text:state?.textBoxes,tickOverlap:state?.tickOverlap});
  if(fixture.extreme)check('actual-zero-sample-at-midpoint',validAxis&&points?.length===4&&near(points[2][1],(axis.top+axis.bottom)/2),points?.[2]);
  if(fixture.kind==='area'){
    const zero=validAxis?axis.top+fixture.zeroFromTop*(axis.bottom-axis.top):null;
    check('area-endpoints-share-literal-common-zero',validAxis&&state.points?.length===6&&near(state.points[0][0],axis.left)&&
      near(state.points[5][0],axis.right)&&near(state.points[0][1],zero)&&near(state.points[5][1],zero),{points:state?.points,zero});
  }
  if(fixture.kind==='bubble')check('original-size-radii-retained',same(state?.marks?.map(mark=>mark.r),[7.5,15,22.5,30]),state?.marks);
  return checks;
}
