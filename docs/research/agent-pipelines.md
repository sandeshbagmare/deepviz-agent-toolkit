# Agent visualization: what is public and what is inferred

**Official sources retrieved 2026-11-26.** Product features and eligibility change; this is a dated public-documentation comparison, not a live entitlement test or proprietary reverse-engineering. Source IDs map to [exact URLs](source-index.json). A vendor can change implementation without changing its public UI.

## Publicly documented surfaces

| Product / source | Documented behavior | What is not established |
|---|---|---|
| **ChatGPT data analysis** — P01, P33 | For some analysis tasks, generated Python runs in a stateful Jupyter environment; interactive tables, static charts and interactive bar/line/pie/scatter charts are documented. Chart downloads default to PNG. The analysis Python environment cannot make external web/API requests. | The exact private interactive chart renderer, its source schema, internal sampling/recommendation pipeline, and all backend resource policies. Do not attribute a JS library from a familiar visual appearance. |
| **Claude custom inline visuals** — P02 | Generated **HTML** visualizations appear inline, can update during conversation, and are ephemeral by default. Users can copy a snapshot, download SVG/HTML, or save as an artifact. | A fixed chart grammar or exclusive charting dependency; the document describes HTML creation, not a universal JSON chart format. |
| **Claude artifacts** — P03 | Persistent, revisitable/shareable outputs open beside the conversation. Current templates and legacy artifacts have different behavior; the current article defines legacy chat artifacts as those made **before September 16, 2026**. | That a pre-September artifact tutorial describes all current artifact storage, permissions, export or network behavior. |
| **Claude code/file creation** — P34 | A private computing environment writes/runs Python or JavaScript and creates downloadable files, including analyses with charts. Network controls are separately configurable for applicable plans. | That every chart is an HTML artifact or that every execution environment has the same network restrictions as ChatGPT. |
| **Claude Data** — P35 | Query-backed dashboards expose chart queries and refresh information. Connection/sharing permissions matter; live sharing can expose results from the editor's connection to recipients. | That uploading a CSV into a code session is the same workflow as a governed warehouse dashboard. |
| **Gemini spreadsheet charts** — P04 | Attached spreadsheets can produce charts in the web app; users can zoom and edit chart type/labels. | The private renderer, exact internal schema, or guarantee that every uploaded row is processed despite context/file limits. |
| **Gemini Canvas/tasks** — P36–P37 | Canvas can build and preview apps/code and export content; tasks can produce code, HTML, graphics and other files. | That app preview, an attached-spreadsheet chart and a generated PNG share one private rendering engine. |
| **Microsoft 365 Copilot code interpreter** — P38–P39 | Generated Python can analyze files and produce charts/downloads. Microsoft describes isolated Azure VMs, no inbound/outbound network, resource quotas, and temporary session artifacts. | That “declarative agent” means the chart itself uses a declarative visualization specification; the term names an agent configuration product. |
| **OpenCode** — P05–P09, P40–P42 | Coding-agent tools, shell/file/browser capabilities, permission checks, attachments and custom/plugin/MCP tools are documented. GUI plugins can register explicit code-block renderers. | A general built-in chart tool/schema shared by every OpenCode client. The reviewed tool docs do not document one; absence from those docs is not proof no plugin/client can render charts. |

The three Claude **execution/presentation families** to keep separate are inline visuals, persistent artifacts (including Data), and code/file creation. Query-backed Claude Data deserves its own row because refresh and source authorization are materially different from generic file generation. They may integrate in the product, but the public pages do not establish one identical pipeline behind all of them. (P02–P03, P34–P35.)

## A reconstruction we can build, clearly labeled inference

For DeepViz, a useful conceptual workflow is:

```text
Question + authorized dataset
  -> inspect schema/profile and clarify semantics
  -> select chart and validated field mappings
  -> execute deterministic transformations/reductions
  -> emit renderer-native spec + preview/HTML + provenance
  -> validate results and iterate from feedback
```

**This is our architecture recommendation**, assembled from documented capabilities and open visualization systems. It is not a recovered ChatGPT/Claude/Gemini private implementation. The public evidence supports similar user-facing stages, not the vendors' hidden prompts, model routing, chart libraries, code, cache design or optimizers.

OpenCode can host a generated-code/artifact workflow through its ordinary tools or an MCP service; that is an inference from the documented extensibility/tool surface, **not** a claim that an intrinsic chart subsystem exists. A renderer plugin would be a separate trusted extension with an explicit host contract and lifecycle. (P07, P09, P42.)

## Practical consequences for DeepViz

1. **Artifact contract first.** Return actual files and counts/warnings; let each host decide how to display them. Do not advertise native inline integration merely because HTML opens in a browser.
2. **Separate query correctness from rendering quality.** A beautiful chart with the wrong join/filter is still wrong. Retain the validated transform plan and source counts; query-backed dashboards illustrate why provenance belongs with the visual. (P35; design inference.)
3. **Isolate execution deliberately.** Host shell permission is not proof of a no-network VM. Never claim DeepViz inherits a vendor's sandbox merely because an agent calls it. OpenCode subagents have their own permissions, not an automatic subset of the parent. (P39, P41.)
4. **Do not confuse persistence with a screenshot.** A static snapshot, re-runnable spec, executable HTML page, persistent app and live data dashboard have different data/permission lifecycles. Name the produced artifact truthfully.
5. **Treat availability as conditional.** Model/plan/admin/account/client settings and feature rollouts differ. These docs do not constitute a test of the user's entitlements.
6. **Keep sensitive data local by default.** Use bounded profiles/redacted samples for optional recommendation; generated output must not fetch arbitrary URLs or publish private data without authority.

## Direct primary references

- ChatGPT: [analysis environment and charts](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt); [interactive output and downloads](https://help.openai.com/en/articles/9213685-extracting-insights-with-chatgpt-data-analysis).
- Claude: [inline visuals](https://support.claude.com/en/articles/13979539-custom-visuals-in-chat-and-cowork); [artifacts](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them); [file/code execution](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude); [Data](https://support.claude.com/en/articles/17454700-get-started-with-claude-data).
- Gemini: [attached-file charts](https://support.google.com/gemini/answer/14903178?hl=en); [Canvas](https://support.google.com/gemini/answer/16047321?hl=en); [tasks](https://support.google.com/gemini/answer/17094507?hl=en).
- Microsoft: [code interpreter](https://learn.microsoft.com/en-us/plugins/code-interpreter); [security architecture](https://learn.microsoft.com/en-us/plugins/code-interpreter-security).
- OpenCode: [tools](https://opencode.ai/docs/tools/); [attachments](https://opencode.ai/docs/attachments/); [permissions](https://opencode.ai/docs/permissions/); [GUI extension surface](https://opencode.ai/docs/build/plugins/gui/).
