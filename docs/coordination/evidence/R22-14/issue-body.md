<!-- deepviz-r22-ready-promise -->
## Reproduced P2: synchronous initialization drops readiness and failure reporting

Exact product source: **7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6**, [engines.py:787-789](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/7bcfb2dcbf99f9deb44a2b5558373bd3aaccd0e6/python/deepviz/src/deepviz/engines.py#L787-L789). Its `payloads.map(...)` initializes renderers before assignment of `window.deepvizReady` and attachment of the intended catch. A missing ECharts/G2 library throws synchronously, bypassing both. Readiness remains **undefined**, `body.dataset.renderError` remains absent, and a naive **await readiness falsely fulfills** despite a blank chart. A host requiring a Promise reaches its own observation deadline instead.

One shared bootstrap cause, not two engine tickets. Existing warnings disclose CDN dependency; successful artifact creation is not itself a browser-readiness claim. Broad related scopes #12/#13/#16/#23 (and trust parent #21) do not already report this specific bug. Complete fresh open-item enumeration/relevant bodies and comments found no duplicate or marker. The known **loaded-G2 all-negative heatmap ASYNC rejection** has an actual readiness Promise and is a different cause.

## Existing independent reproduction and controls -- no rerun for filing

Original immutable QA/probe/evidence: **41477a7d1b2d332dbb3790d31987d3861e4137b5**. [Full report](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/reports/R21-14-offline-host-failure.md), [actual DOM/readiness/network observations](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/host-observations.json), [strict RED log](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/pytest-live.log), [source/import/tool hashes](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/tool-artifacts.json).

Use real `create_tools(NEW_OUTPUT)` StructuredTool.invoke for render_echarts/render_antv with rows [{label:'A & B',value:3},{label:'C < D',value:9}] and spec {kind:'bar',x:'label',y:'value',aggregation:'none',title:'Offline <literal> & host',width:700,height:340}. The actual generator materialized/hash-checked exact7bc source:11files/seven imported modules. Three actual tool calls include the Matplotlib static positive; this is not an end-to-end DeepAgent LLM/provider run.

Load each returned **unchanged** HTML and deliberately abort its external runtime URL:
- https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js
- https://cdn.jsdelivr.net/npm/@antv/g2@5.4.8/dist/g2.min.js

[Probe/README with exact commands](https://github.com/sandeshbagmare/deepviz-agent-toolkit/tree/41477a7d1b2d332dbb3790d31987d3861e4137b5/tests/r21_probes/role14): generate_tools.py, offline_host.mjs, then pytest test_live_host.py with explicit --host-evidence. For a future fixed-head retest QA must explicitly adapt the generator's fixed7bc pin/provenance to the proposed fix while preserving original strict expectations, not accidentally retest7bc or borrow moving HEAD.

Observed per denied case: one expected fixture `net::ERR_FAILED`; separate uncaught `ReferenceError: echarts is not defined` / `ReferenceError: G2 is not defined`; readiness/then undefined, await falsely fulfilled, declared renderError absent, zero chart children/graphics/text. The **1500ms budget belongs only to the observer**, NOT a product timeout. No product spinner/aria-busy or indefinite real-host spinner was demonstrated. This controlled request denial is NOT a live-CDN-health or exploit claim. HTML/bootstrap/nativepayload were not edited; no fake renderer or downloaded-code execution.

Recorded strict result: **exit1,2failed/8passed/0skipped**, no xfail; four separate oracle controls passed. Five real browser cases: two controlled denials and three real positives; seven actual images opened. Windows/Python3.12.16/LangChain-core1.8.5/Playwright1.65.1/Chromium159.0.8154.6. No generation/test/browser/build/advisory replay to file this bug.

## Useful fallback and real positives are preserved

Both denied cases retain exact literal A & B=3 / C < D=9, headers/caption/counts2-to-2/none and inert nativeJSON. Focus the genuine data summary and press Enter: the real table is accessible through the accessibility tree. No data-loss claim. [Blank chart](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/echarts-denied.png), [keyboard-opened fallback](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/echarts-denied-fallback-open.png).

[Matplotlib static positive](https://github.com/sandeshbagmare/deepviz-agent-toolkit/blob/41477a7d1b2d332dbb3790d31987d3861e4137b5/docs/coordination/evidence/R21-14/matplotlib-static-offline.png): zero external requests/runtime scripts/console-pageerrors, real siblingSVG and originalPNG opened with literal3/9bars. Static HTML intentionally needs no interactive readiness Promise.

ECharts/G2 local positives use **real preexisting exact bytes**, explicitly NOT CDN health: ECharts6.1.0 SHA256 b66b25aeb4df84e33199dc21694014d336d222cbd9deb0e5a7c14bd6aa0d0fd0; G2 5.4.8 SHA256 7e7d346cab68c002a889dc6145bfc1f9ae1391be82ce8d514fb106ef3a6e6412. Both actual Promises fulfill; actual graphics/literal3/9values inspected; zero console/pageerrors/failedresources/unexpectedrequests.

## Minimal proposal and acceptance -- owner R04, not an applied fix

- [ ] Assign/create the readiness Promise BEFORE executing callbacks, so synchronous throws and asynchronous rejections both reach the declared catch/error channel. No fake fulfillment/engine.
- [ ] Truthful actionable accessible DOM failure status distinguishes failed interactive rendering from useful data fallback. Preserve literal rows/counts/warnings/keyboard access.
- [ ] At exact proposed fixed head, both strict denial assertions pass with rejected readiness and declared error signal. Separate expected deliberate ERR_FAILED resource events; no unexpected/unhandled initialization errors or silent success.
- [ ] Preserve all three real positives and literal3/9values with no unexpected errors; static output need not have a Promise.
- [ ] Genuine non-author fixed-head review/retest and source-specific CI/default-merge evidence before closure. Original2RED remain failures; no universal-offline/all-engine/all-kind/LLM/security/full900-goal approval.

R04 owns code/policy/integration/closure; the separate _antv-only producer release does not grant the shared HTML wrapper. One cause/one bug; leave open until acceptance is evidenced. No auto-close, second-engine ticket or900-count padding.
