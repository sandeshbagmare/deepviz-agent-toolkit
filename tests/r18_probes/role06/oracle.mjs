const close=(a,b,tolerance=0.02)=>Math.abs(a-b)<=tolerance;
export function assess(fixture,state,format){
  const checks=[];
  const check=(name,pass,observed)=>checks.push({name,pass:!!pass,observed});
  const {width,height}=fixture;
  const inside=(box,pad=0)=>box && box.x-pad>=-0.05 && box.y-pad>=-0.05 &&
    box.x+box.width+pad<=width+0.05 && box.y+box.height+pad<=height+0.05;
  check('real-root-svg-dimensions',state.root && state.root.width===width && state.root.height===height,state.root);
  check('browser-errors',state.errors.length===0,state.errors);
  check('no-network-failures-or-external-dependencies',state.networkFailures.length===0 && state.externalRequests.length===0,
    {failures:state.networkFailures,external:state.externalRequests});
  check('nonblank-visible-painted-marks',state.marks.length>0 && state.marks.every(mark=>
    mark.box.width>0 && mark.box.height>0 && mark.display!=='none' && mark.visibility==='visible' &&
    Number(mark.opacity)>0 && (mark.fill!=='none' || mark.stroke!=='none')),state.marks);
  check('all-native-text-inside-svg',state.texts.every(text=>inside(text.box)),state.texts);
  check('all-native-mark-bounds-inside-svg',state.marks.every(mark=>inside(mark.box,mark.stroke==='none'?0:mark.strokeWidth/2)),
    state.marks.map(mark=>({box:mark.box,stroke:mark.stroke,strokeWidth:mark.strokeWidth})));
  if(format==='html'){
    check('HTML-readiness',state.ready===true && state.deepvizErrors.length===0,
      {ready:state.ready,errors:state.deepvizErrors});
    check('literal-normalized-table-order-values',JSON.stringify(state.tableRows)===JSON.stringify(fixture.rows.map(row=>Object.values(row).map(String))),
      state.tableRows);
  }
  if(fixture.kind==='pie'){
    check('pie-no-cartesian-axis',state.axis===null && state.texts.length===0,state.axis);
    check('pie-exact-three-sectors',state.marks.length===3 && state.marks.every(mark=>mark.tag==='path'),state.marks.length);
    check('pie-literal-category-values',JSON.stringify(state.marks.map(mark=>mark.title))===
      JSON.stringify(['Alpha: 2e+24','Beta: 3e+24','Gamma: 5e+24']),state.marks.map(mark=>mark.title));
    let angle=-Math.PI/2;
    const sectors=state.marks.map((mark,i)=>{
      const values=(mark.d||'').match(/-?(?:\d*\.)?\d+(?:e[-+]?\d+)?/ig)?.map(Number)||[];
      const end=angle+fixture.fractions[i]*Math.PI*2;
      const expected=[120,120,120+55*Math.cos(angle),120+55*Math.sin(angle),55,55,0,0,1,
        120+55*Math.cos(end),120+55*Math.sin(end)];
      angle=end;
      // A literal half-circle can serialize either large-arc flag after finite IEEE-754 division.
      return {values,expected,pass:values.length===expected.length && values.every((v,j)=>
        j===7 && fixture.fractions[i]===0.5 ? v===0 || v===1 : close(v,expected[j]))};
    });
    check('pie-radius-center-proportions-unshifted',sectors.every(sector=>sector.pass),sectors);
    if(format==='html'){
      check('pie-category-key-order',JSON.stringify(state.legend.map(item=>item.label))===JSON.stringify(['Alpha','Beta','Gamma']),state.legend);
      check('pie-legend-matches-distinct-sector-colors',new Set(state.marks.map(mark=>mark.fill)).size===3 &&
        state.legend.length===3 && state.legend.every((item,i)=>item.fill===state.marks[i].fill),state.legend);
      check('pie-legend-visible-unclipped-separated',state.legend.length===3 && state.legend.every((item,i)=>
        item.rect.width>0 && item.rect.height>0 && item.rect.x>=0 && item.rect.y>=state.rootViewport.bottom &&
        item.rect.right<=state.viewport.width && item.rect.bottom<=state.viewport.height &&
        (i===0 || item.rect.y>=state.legend[i-1].rect.bottom)),state.legend);
    }
    return checks;
  }
  const axis=state.axis;
  check('quantitative-axis-present-positive-plot-size',axis && axis.width>0 && axis.height>0 && inside(axis),axis);
  check('literal-extreme-y-ticks',JSON.stringify(state.yTicks.map(tick=>tick.text))===JSON.stringify(fixture.ticks),state.yTicks);
  check('both-extreme-tick-bboxes-visible',state.yTicks.length===2 && state.yTicks.every(tick=>inside(tick.box)),state.yTicks);
  check('literal-all-unequal-numeric-x-ticks',JSON.stringify(state.categoryTicks.map(tick=>tick.text))===JSON.stringify(['1','2','4','8']),state.categoryTicks);
  check('native-field-labels',state.texts.some(text=>text.text==='x') && state.texts.some(text=>text.text==='y'),state.texts.map(text=>text.text));
  const expectedCount=['line','area'].includes(fixture.kind)?1:4;
  check('native-mark-count',state.marks.length===expectedCount,{actual:state.marks.length,expected:expectedCount});
  if(!axis)return checks;
  const [low,high]=fixture.domain;
  const position=(x,y)=>[axis.x+(x-1)/7*axis.width,axis.y+axis.height-(y-low)/(high-low)*axis.height];
  const expected=fixture.rows.map(row=>position(row.x,row.y));
  let points=[];
  if(['line','area'].includes(fixture.kind)){
    const mark=state.marks[0],allPoints=mark?.points||[];
    points=fixture.kind==='area'?allPoints.slice(1,-1):allPoints;
    check('native-polyline-not-fallback',state.marks.length===1 && mark?.tag==='polyline',mark?.tag);
    check('polyline-full-vertex-count',allPoints.length===(fixture.kind==='area'?6:4),allPoints);
    if(fixture.kind==='area'){
      const baseline=position(1,0)[1];
      check('area-common-literal-zero-baseline',allPoints.length===6 && close(allPoints[0][0],expected[0][0]) &&
        close(allPoints.at(-1)[0],expected.at(-1)[0]) && close(allPoints[0][1],baseline) && close(allPoints.at(-1)[1],baseline),
        {allPoints,expectedZero:baseline});
      check('area-visible-fill-and-stroke',mark && mark.fill!=='none' && mark.fillOpacity>0 && mark.stroke!=='none',mark);
    }else check('line-open-unfilled-connected',mark && mark.fill==='none' && mark.stroke!=='none',mark);
  }else{
    points=state.marks.map(mark=>[mark.cx,mark.cy]);
    check('native-circles-not-fallback',state.marks.every(mark=>mark.tag==='circle'),state.marks.map(mark=>mark.tag));
    const expectedRadii=fixture.kind==='bubble'?[7.5,15,22.5,30]:[4,4,4,4];
    check('literal-scatter-or-size-radius',state.marks.length===4 && state.marks.every((mark,i)=>close(mark.r,expectedRadii[i])),state.marks.map(mark=>mark.r));
    check('literal-mark-title-values',JSON.stringify(state.marks.map(mark=>mark.title))===
      JSON.stringify(fixture.rows.map(row=>`${row.x}: ${row.y}`)),state.marks.map(mark=>mark.title));
  }
  check('all-literal-point-values-order-and-scale',points.length===4 && points.every((point,i)=>close(point[0],expected[i][0]) && close(point[1],expected[i][1])),{points,expected});
  if(fixture.profile==='zero')check('actual-literal-zero-point-shares-zero-baseline',points.length===4 &&
    close(points[1][1],position(2,0)[1]),{actual:points[1],expected:position(2,0)});
  const gaps=points.slice(1).map((point,i)=>point[0]-points[i][0]);
  // SVGPointList and SVG animated lengths expose float32 centers; 1e-4 ratio tolerance stays subpixel here.
  check('quantitative-x-gap-ratios-1-2-4',gaps.length===3 && gaps[0]>0 && close(gaps[1]/gaps[0],2,1e-4) && close(gaps[2]/gaps[0],4,1e-4),gaps);
  check('x-ticks-align-actual-point-centers',state.categoryTicks.length===4 && points.length===4 && state.categoryTicks.every((tick,i)=>close(tick.x,points[i][0])),
    state.categoryTicks.map(tick=>tick.x));
  check('common-cartesian-axes-literal-insets',close(axis.x+axis.width,width-65) && close(axis.y,65) && close(axis.y+axis.height,height-65),axis);
  return checks;
}

export function negativeControls(fixture,state,format){
  const mutations={blank:s=>{s.marks=[];},wrongValue:s=>{s.marks[0].points[2][1]+=10;},
    ordinalX:s=>{s.marks[0].points[3][0]=s.marks[0].points[2][0]+9;},
    wrongZero:s=>{s.marks[0].points[0][1]+=9;},missingTick:s=>{s.yTicks.pop();},
    clippedTick:s=>{s.yTicks[0].box.x=-8;s.texts[0].box.x=-8;},
    browserError:s=>{s.errors.push('deliberate observer-control error');}};
  return Object.entries(mutations).map(([name,mutate])=>{
    const corrupted=structuredClone(state);mutate(corrupted);let failures;
    try{failures=assess(fixture,corrupted,format).filter(check=>!check.pass).map(check=>check.name);}
    catch(error){failures=[`oracle unexpectedly threw: ${error}`];}
    return {name,rejected:failures.length>0 && !failures.some(item=>item.startsWith('oracle unexpectedly threw')),failures};
  });
}
