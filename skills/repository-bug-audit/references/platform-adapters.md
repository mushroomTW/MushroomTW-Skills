# Platform Adapters

This skill describes its requirements in terms of capabilities — a choice interface, independent
reviewers, a way to run repository-configured checks — so that the audit rules stay identical
everywhere. This file maps those capabilities onto each host. Read the section for the host you are
running in; ignore the others.

## Contents

- [Capability map](#capability-map)
- [Claude Code](#claude-code)
- [Claude apps and the web interface](#claude-apps-and-the-web-interface)
- [OpenAI Codex](#openai-codex)
- [When a capability is missing](#when-a-capability-is-missing)

## Capability map

| Capability | Claude Code | Claude apps | Codex |
| --- | --- | --- | --- |
| Startup choice interface | `AskUserQuestion` | Numbered prose question | Numbered prose question |
| Independent reviewers | Subagent tool | Unavailable | Parallel agent runs where supported |
| Reading the working tree | `Read`, `Grep`, `Glob` | Uploaded project files | Native file tools |
| Repository-configured checks | `Bash` / `PowerShell` | Sandbox shell | Native shell |
| Writing the two artifacts | `Write` | Sandbox filesystem | Native file write |
| Skill directory | See below | Uploaded skill folder | Installed skill folder |

## Claude Code

**Ask both startup choices in one `AskUserQuestion` call.** Send two questions — audit mode and
execution mode — rather than two sequential calls, because the user answers them together and a
second round trip only adds latency. Skip a question the user already answered explicitly in their
request; do not re-ask what they have already told you.

**Resolve the skill directory before running the validator.** The path depends on how the skill was
installed:

| Installation | Skill directory |
| --- | --- |
| Plugin | `${CLAUDE_PLUGIN_ROOT}/skills/repository-bug-audit` |
| Personal skill | `~/.claude/skills/repository-bug-audit` |
| Project skill | `<repo>/.claude/skills/repository-bug-audit` |

`${CLAUDE_PLUGIN_ROOT}` is substituted by Claude Code and points at the plugin root, one level above
the `skills/` directory. Quote it in shell commands
(`"${CLAUDE_PLUGIN_ROOT}"/skills/repository-bug-audit/scripts/validate_bug_audit.py`) — installed
plugin paths contain a version segment and, on Windows, spaces. When the variable is unavailable,
locate `scripts/validate_bug_audit.py` relative to the `references/` file you are already reading
rather than guessing a path.

**Stay read-only.** Claude Code gives you `Edit` and `Write`, which the audit must not use on project
files. Write exactly the two artifacts named in SKILL.md and nothing else — both go into the
repository's `.docs/` directory, created when it is missing. Restrict `Bash` and
`PowerShell` to checks the repository already configures — a test, build, lint, type-check, or
analyzer command that exists in its manifests or CI. Installing a tool, or writing a scratch
reproduction script anywhere including the scratchpad, is out of scope for this skill.

**Multi-agent partitioned execution** uses the subagent tool: one subagent per scope partition, each
returning inventory states, traced flows, structured candidate findings, and limitations. Give each
subagent the partition boundary and the evidence field requirements in its prompt, because a subagent
does not inherit your conversation. Cross-review every candidate High finding in a separate subagent
that is not told the original conclusion — a reviewer shown the prior verdict tends to confirm it,
which defeats the point of independent confirmation.

**Prefer repository code-navigation tools** — LSP definitions and references, or an indexed code graph
when the workspace provides one — over text search for tracing callers and callees. Text search finds
strings; the audit needs call relationships, and a search miss only ever supports "not found within
the reviewed scope."

**On Windows**, invoke the validator through the `Bash` tool with forward slashes, or through
`PowerShell`. If `python` is not on `PATH`, try the launcher: `py -3 -X utf8`. Keep `-X utf8` on every
platform so the emoji severity values in the evidence JSON round-trip correctly.

**Model choice**: Comprehensive mode reads every in-scope file and holds cross-file state while
reasoning about contracts and concurrency. Opus-class models handle that materially better. Rapid mode
is comfortable on a mid-tier model.

## Claude apps and the web interface

There is no subagent mechanism here, so Multi-agent partitioned execution is unavailable. Say so and
ask the user to choose Standard; do not run a single-agent audit while labelling it multi-agent, since
`execution.review_mode` in the evidence JSON is a factual claim about how the audit was performed.

Ask the startup choices as one short numbered prose question. Scope is whatever project files the user
supplied — record anything you could not access as `unreadable` with a reason, and let the coverage
percentage fall honestly rather than excluding what you simply could not open.

Run the validator with the bundled Python script in the analysis sandbox. Repository-configured checks
are usually unavailable, which is a legitimate `unavailable` verification state, not a failure — but it
caps Comprehensive confidence below High, because High requires at least one passed configured check.

## OpenAI Codex

`agents/openai.yaml` supplies the display name, short description, and default prompt for the skill
picker. Ask the startup choices as a numbered prose question. Use parallel agent runs for Multi-agent
execution where the host supports them, applying the same independent cross-review rule described in
the Claude Code section.

Skills load from `.agents/skills` inside the repository, `$HOME/.agents/skills` for the user scope,
or the plugin cache when installed from a marketplace. Rather than reconstructing a cache path that
carries a marketplace, plugin, and version segment, resolve `scripts/validate_bug_audit.py` relative
to this `references/` file.

## When a capability is missing

Never silently downgrade. The mode the user picked is recorded in the evidence JSON and shapes how much
the report is allowed to claim, so a silent fallback turns the artifact into a false record. State which
capability is unavailable, say what it changes, and let the user choose. If the audit proceeds with a
reduced capability, record the consequence in `limitations` and re-check whether the affected conclusion
now needs `provisional` status.
