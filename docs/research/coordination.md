# OpenCode and OmO: current naming and safe coordination

**Snapshot: 2026-11-26.** No global configuration, credential store, plugin installation or migration was changed by this research work. This is an adoption note, not a claim the optional plugin executed any task.

## What was verified upstream

1. The GitHub API request for `code-yeongyu/oh-my-opencode` resolves to repository identity **`code-yeongyu/oh-my-openagent`**. This is direct evidence of the renamed upstream, not a third-party fork. (P29.)
2. GitHub's latest stable-release endpoint returned **v5.1.84**, published **November 26, 2026 at 15:59:30 UTC**. The npm `latest` records for both **`oh-my-openagent`** and **`omo-ai`** returned **5.1.84** at access. These are time-specific observations, not version ranges to leave floating in a reproducible build. (P30–P32.)
3. The pinned development README now foregrounds native **OmO**, the `omo` command and package **`omo-ai`**, running on **senpi**, a pi fork. The same repository retains OpenCode-edition code/docs; the package metadata and registry distinguish the plugin from the native package. A rename does **not** mean the native CLI is an interchangeable OpenCode plugin. (R15 README/package; P31–P32.)
4. Its license file is a **Sustainable Use License** with separate third-party terms. Do not relabel the project as permissively licensed merely because the public source is available. This is a license inventory observation, not legal advice. (R15 LICENSE.)

Exact URLs, inspected commit `59b4ac1f67e83a6f2cd99a762aefda575df17ad7`, and all documentation files are in [the source index](source-index.json). No “hundreds of agents” or “ten thousand sources” marketing statement is adopted as evidence of work performed here.

## Configuration families must not be mixed

| Surface | Current documented shape / caveat |
|---|---|
| **Native OpenCode V2** | Project `opencode.json(c)` or `.opencode` configuration; custom roles under **`agents`**, permissions as ordered **`permissions`** rules; current plugin guide uses **`plugins`**. Agent Markdown is another supported project-local format. (P06, P08–P09.) |
| **OmO unified config** | Pinned reference specifies user `~/.omo/omo.jsonc` and project **`.omo/omo.jsonc`**, with shared keys plus `[opencode]`, `[native]` or `[codex]` harness blocks. Legacy `oh-my-openagent.json[c]`/`oh-my-opencode.json[c]` names are migration inputs, not the preferred new files. (R15 configuration.) |
| **OmO Team Mode OpenCode edition** | Pinned guide says off by default; enable under the `[opencode]` block, then verify actual `team_*` tool registration. Documented per-team member bounds are not a universal limit on native OpenCode agents or a reason to change global settings. (R15 team guide.) |
| **Existing installed environment** | An observed `oh-my-openagent@latest` config string establishes intent to load a package, **not** the resolved version, successful startup, model authentication, tool registration or runtime use. Check those separately before claiming execution. |

The OmO installation guide still includes an older singular OpenCode `plugin` registration example, while current OpenCode V2 documents plural `plugins`; its team page also contains restart-oriented instructions. These are real edition/version-boundary warnings. Use the installed host's current official docs and a reviewed compatibility test, not a blind copy of every upstream installation example. No migration/install command is required for this research deliverable.

## Recommended setup for this repository

Use native OpenCode V2 agent roles and the already available subagent tool surface as the baseline. The parent session reports project-local roles; this branch does not overwrite its config. A minimal **illustrative**, read-only project role follows the current agent documentation:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agents": {
    "source-reviewer": {
      "description": "Review official sources without changing files",
      "mode": "subagent",
      "system": "Return evidence and uncertainties. Do not modify files.",
      "permissions": [
        { "action": "*", "resource": "*", "effect": "deny" },
        { "action": "read", "resource": "*", "effect": "allow" },
        { "action": "glob", "resource": "*", "effect": "allow" },
        { "action": "grep", "resource": "*", "effect": "allow" },
        { "action": "webfetch", "resource": "*", "effect": "allow" },
        { "action": "websearch", "resource": "*", "effect": "allow" }
      ]
    }
  }
}
```

Merge such a role only when requested; do not replace an existing config or hard-code an unverified model name. This example allows broad reads for illustration; scope paths and domains to the actual task for sensitive projects. OpenCode documents that subagents use **their own** permissions, not the parent's automatic permission subset. The default-deny rule also blocks unknown write-capable plugin/MCP tools and shell; a prose “read-only” instruction alone would not. (P08, P41.)

An optional OpenCode-edition Team Mode configuration, **only after compatible installation/version checks and explicit approval**, is project-local `.omo/omo.jsonc` with `[opencode].team_mode.enabled=true`. The guide's member/worktree/mailbox settings are a separate coordination system, not fields to paste into OpenCode's `agents`. Do not run native `omo setup`: upstream describes it as migrating provider keys/configuration across harnesses, which is outside this task. (R15 README/config/team docs.)

## Work ownership and evidence

- Assign each writer a distinct branch/worktree and explicit file scope. Read-only researchers return findings; they do not race over shared documentation. The lead integrates after checking the exact commits.
- Split research, implementation, security review, browser/visual testing and release checks by concrete deliverable, not by an arbitrary agent-count target. Parallelize independent tasks; serialize shared schema edits.
- Treat child completion messages as claims until their diffs/tests/artifacts are checked. Record commands, exit codes, commit hashes, source dates and unsupported paths.
- Use fresh read-only review of the integrated change, followed by focused fixes and reruns. A self-authored review or a configured-but-unused agent is not independent verification.
- Respect recursion/depth controls. OpenCode V2 documents a default subagent depth of one; this research child attempted a nested research dispatch and received **“Subagent depth limit reached (1)”**. It continued locally; no extra child research or runtime plugin use is fabricated. (P06 plus observed tool error.)
- Keep secrets, source datasets and global configuration out of commits. Push only the authorized task branch; no merge, issue creation or global permission broadening is implied by delegation.
