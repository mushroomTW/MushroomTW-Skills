# Platform Adapters

Capabilities are identical everywhere; this file maps them to hosts.

## Capability map

| Capability | Claude Code | Claude Apps | Codex |
| --- | --- | --- | --- |
| Startup choice UI | `AskUserQuestion` (ask both modes at once) | Numbered prose | Numbered prose |
| Independent reviewers | Subagent tool | Unavailable | Parallel agents where supported |
| Read working tree | `Read`/`Grep`/`Glob` | Uploaded files | Native file tools |
| Repo-configured checks | Shell tool | Sandbox shell | Native shell |
| Write artifacts | `Write` → `.docs/` | Sandbox FS | Native write |
| Skill directory | `~/.claude/skills/...` · `<repo>/.claude/skills/...` | Uploaded folder | `~/.agents/skills/...` · `<repo>/.agents/skills/...` |

## Claude Code

- Ask **both** startup choices in one `AskUserQuestion`; skip what user already stated.
- Execution is always Multi-agent partitioned (one subagent per partition); if subagents are unavailable, explain and 🛑 STOP — never fall back to single-agent.
- Resolve validator relative to `references/` (e.g. `../scripts/validate_bug_audit.py`). On Windows use `/` and `py -3 -X utf8` if `python` is missing. It requires a preinstalled `jsonschema`; if absent, follow the SKILL failure matrix and do not install it during the audit.
- Stay read-only: only `.docs/` pair; only run repo-configured checks. No tool install / repro probes.
- Multi-agent: one subagent per partition (inventory, flows, candidates, limitations); cross-review High without revealing original verdict. Prefer LSP/graph over grep.

## Claude Apps

No subagents — 🛑 STOP and explain that Multi-agent is required; do not fall back to a single-agent Standard run. Scope = uploaded files; mark inaccessible as `unreadable`. Validator: add `--repo-root <tree>` if `.docs/` is not under the tree. `unavailable` checks are legitimate but cap Comprehensive confidence below High.

## Codex

`agents/openai.yaml` drives the picker. Ask modes as numbered prose. Multi-agent via parallel runs with same cross-review rule. Resolve `validate_bug_audit.py` relative to `references/`.

## When a capability is missing

Never silently downgrade — `execution.review_mode` is always `multi-agent` and is a factual claim. If Multi-agent is unavailable, 🛑 STOP, state what is missing and its impact, and let the user decide how to proceed; record consequence in `limitations` and re-check `provisional`.
