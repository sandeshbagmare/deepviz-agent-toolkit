// Independent literal fractions: no arithmetic on any ±1e308 range is used by the oracle.
const positive={xs:[1,2,3,5],ys:[2,4,6,8],xFractions:[0,0.25,0.5,1],yFractionsFromTop:[0.75,0.5,0.25,0],zeroFromTop:1};
const signedY={xs:[-2,-1,0,2],ys:[-1e308,-5e307,0,1e308],xFractions:[0,0.25,0.5,1],yFractionsFromTop:[1,0.75,0.5,0],zeroFromTop:0.5};
const signedX={xs:[-1e308,-5e307,0,1e308],ys:[-8,-4,0,8],xFractions:[0,0.25,0.5,1],yFractionsFromTop:[1,0.75,0.5,0],zeroFromTop:0.5};
const signedBoth={...signedY,xs:[-1e308,-5e307,0,1e308]};
export const fixtures=['line','area','scatter','bubble'].flatMap(kind=>[
  {id:`${kind}-control`,kind,extreme:false,...positive},
  {id:`${kind}-extreme`,kind,extreme:true,...(kind==='line'?signedY:kind==='scatter'?signedX:signedBoth)},
]).map(fixture=>({...fixture,width:960,height:520,
  records:fixture.xs.map((x,i)=>({x,y:fixture.ys[i],...(fixture.kind==='bubble'?{size:[1,4,9,16][i]}:{})})),
  spec:{kind:fixture.kind,title:`R24 ${fixture.id}`,x:'x',y:'y',aggregation:'none',width:960,height:520,
    ...(fixture.kind==='bubble'?{size:'size'}:{})},
}));
