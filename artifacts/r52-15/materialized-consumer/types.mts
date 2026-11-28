import {render, normalizeStream, type ChartSpecInput, type HtmlArtifact} from '@deepviz/agent-toolkit';
const spec: ChartSpecInput = {kind:'bar', x:'x', y:'y'};
const artifact: HtmlArtifact = render([{x:'A', y:2}], spec, 'svg');
const records = await normalizeStream((async function*(){yield {x:1};})());
void [artifact, records];
