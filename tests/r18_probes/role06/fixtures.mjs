// Literal test inputs and domains: never read expectations from generated renderer payloads.
export const sourceSha = '5e595a8f893955ce34a0e26553bb7bf257ea93ae';
export const profiles = [
  {id:'positive', ys:[2,8,5,3], domain:[0,8], ticks:['8.000','0.000']},
  {id:'negative', ys:[-987654.4321,-250000.25,-500000.5,-125000.125],
    domain:[-987654.4321,1], ticks:['1.000','-9.877e+5']},
  {id:'scientific', ys:[-1.234567e24,2.5e23,9.876543e24,-2.5e23],
    domain:[-1.234567e24,9.876543e24], ticks:['9.877e+24','-1.235e+24']},
  {id:'zero',ys:[-4,0,8,2],domain:[-4,8],ticks:['8.000','-4.000']},
];
export const cases = profiles.flatMap(profile => ['line','scatter','area','bubble'].flatMap(kind =>
  [240,960].map(width => ({id:`${kind}-${profile.id}-${width}`,kind,width,height:width,
    profile:profile.id, domain:profile.domain, ticks:profile.ticks,
    rows:[1,2,4,8].map((x,i)=>({x,y:profile.ys[i],size:[1,4,9,16][i]}))}))));
cases.push({id:'pie-scientific-240',kind:'pie',width:240,height:240,
  rows:[{x:'Alpha',y:2e24},{x:'Beta',y:3e24},{x:'Gamma',y:5e24}],
  radius:55, center:[120,120], fractions:[0.2,0.3,0.5]});
