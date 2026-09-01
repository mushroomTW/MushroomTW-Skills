---
name: excellent-readme
description: Create, improve, audit, or synchronize a software project's README.md. Use when the user asks to write a README, organize project documentation, improve a GitHub project homepage, add installation and usage instructions, update a README after code or configuration changes, or check whether a README is accurate, runnable, and easy to understand; do not use for a complete API manual or a general article unrelated to a repository.
---

# Excellent README

A README is an entry point, not a complete manual. Help the reader decide “Is this for me?” and reach a first success without reading source code. Put disqualifying prerequisites and limitations early; helping a non-fit reader leave quickly is success.

## Work modes

First identify the requested outcome:

- **Create**: no README exists; build a first draft from repository facts.
- **Improve**: preserve correct content while fixing structure, clarity, gaps, and drift. Prefer in-place edits. 🔴 **STOP** before a full rewrite: inventory the current README's unique content and wait for explicit approval; without it, edit in place.
- **Audit**: do not edit first; report evidence, problems, risks, and priority-ordered recommendations.
- **Synchronize**: update README facts affected by code or configuration changes; treat drift as functional damage.

If the user does not specify a mode, default to “improve and verify.” Unless explicitly requested, do not turn the README into a complete documentation website.

Treat translated variants as one document: update every variant you can write accurately and report any divergence. For new variants use BCP 47 names (`README.zh-TW.md`) with English in `README.md`; preserve an established repository naming scheme.

## Invariants

1. **Evidence first**: gather facts from the repository before writing. Never invent features, commands, versions, environment variables, deployment methods, performance numbers, badges, screenshots, or license details.
2. **Reader-led**: order information around the reader's decisions, not the author's implementation order. The top of the README must independently explain the project's purpose and smallest useful path.
3. **Cognitive funnel**: move from broad to specific: one-line purpose → minimal runnable example → installation → configuration and limitations → API or architecture details → contribution, license, and acknowledgements.
4. **Runnable**: commands must trace to repository files, scripts, CLI help, or tests. Run examples that need no network, credentials, paid services, dependency installation, or data changes. Otherwise 🔴 **STOP** for authorization; absent approval means `unrun`, never passed.
5. **Single source of truth**: do not copy information that readers can directly inspect in the environment and that is likely to drift. Use the README for background, rationale, limitations, and workflows that the files do not reveal.
6. **Right-sized**: the 15 sections from the reference article are candidates, not mandatory headings. Keep small projects short; add architecture, project structure, security, API, contribution, and roadmap sections only when they help.
7. **Honest gaps**: 🔴 **STOP** and ask before choosing a license, contribution channel, contact, or roadmap. If nobody can answer, omit the section and report the question; never ship `TODO:`. State adoption-relevant absences (for example, no LICENSE) as facts, not placeholders. Omit rather than invent.

## Workflow

### 1. Establish the goal and audience

Identify language, audience, purpose, and output path. Audience gates section choice, depth, and tone. If evidence is ambiguous and the user can answer, 🔴 **STOP** and offer plausible reader types. If nobody can answer, make the smallest evidence-based assumption and disclose it. Do not ask when evidence settles it: a published library implies integrators; a CLI manifest implies CLI users.

Completion criterion: state in one sentence who the README helps and what decision or task it supports — confirmed by the user when the choice was ambiguous.

### 2. Build an evidence inventory

Inspect directly:

- `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `go.mod`, and other manifests
- `Makefile`, Taskfile, CI workflows, Dockerfiles, compose files, and deployment configuration
- `.env.example`, configuration files, CLI `--help`, tests, and existing examples
- `LICENSE`, `CONTRIBUTING`, `SECURITY`, `docs/`, images, and demo assets
- the existing README and recent changes, to identify likely drift

Classify facts as **verified**, **plausible but unverified**, or **missing**; only verified facts may be unqualified.

Completion criterion: every command, path, environment variable, feature, and link retained in the README has a traceable source.

### 3. Choose the README shape

Choose sections from evidence, using these project-type emphases:

- **CLI / application**: quick start, usage examples, configuration, output, limitations, deployment.
- **Library / SDK**: one-line purpose, minimal API example, installation, API, compatibility, license.
- **Service / API**: architecture, startup, environment variables, health checks, API entry points, security, deployment.
- **Frontend / full-stack product**: demo or screenshots, features, stack, architecture, local development, deployment.
- **Tool / research project**: problem context, method, reproduction steps, inputs and outputs, limitations, citations.

Never add empty template sections. Omit unsupported sections and report consequential gaps.

Completion criterion: the section list is written down before drafting, and every section on it names the evidence that justifies its presence.

### 4. Draft the README

Follow the cognitive funnel, section rules, and anti-patterns in [readme-framework](references/readme-framework.md), and calibrate tone, density, and section rhythm against [exemplars](references/exemplars.md).

Keep the first screen independently useful. Put a real example before abstract internals; link deeper material instead of copying it. Never imply `.env`, configuration, or deployment behavior that code does not implement. Use GFM, sparse admonitions for must-not-miss facts, sparse emoji, and shallow lists. A badge, logo, demo, or screenshot must answer a reader question and cannot carry the only copy of a fact; use repository assets only and follow the framework's badge rules.

Completion criterion: a reader can understand the project's purpose and complete the smallest useful path without reading the source code.

### 5. Verify content and examples

Run proportional checks:

- Check Markdown headings, table-of-contents anchors, external links, and local links.
- Confirm that local images, GIFs, videos, and example files exist.
- Compare commands against manifests, Makefiles, or `--help`; do not merely check that the text appears somewhere.
- Run minimal installation, startup, and usage examples subject to invariant 4. Unauthorized commands are `unrun`, never verified.
- Re-evaluate the section set against the current repository; do not add filler merely to satisfy a checklist.

Run the checker that ships with this skill before delivering any create, improve, or synchronize result. It lives at `scripts/validate_readme.py` in the same directory as this SKILL.md file, so resolve the path from wherever you read this file: `python <that directory>/scripts/validate_readme.py <readme-path> --project <repository-root>`. It ignores code blocks, and its warnings are heuristic leads: read each flagged line and judge it before editing. If a check cannot run, do not stall — follow the matching row in **Failure recovery** and continue.

Completion criterion: every retained command and link passes a traceability check, and every unverified item is either qualified in plain wording or listed in the delivery report — never left as a placeholder.

### 6. Perform a final reader review

Read once from the reader's perspective and apply [quality-checklist](references/quality-checklist.md).

For an audit or a delivery, write the report in this shape:

```markdown
**Mode**: create | improve | audit | synchronize
**Audience**: <who this README helps, and what decision it supports> — confirmed by the user | assumed from <evidence>

**Changed**
- <section> — <what changed, and the evidence behind it>

**Verified**
- <command, link, or path> — <how: ran it / matched `package.json` / compared against `--help`>

**Unrun checks**
- <check> — <why it could not run, and what would unblock it>

**Open questions**
- <question only the user can answer> — <the section it would unlock>

**Deliberately omitted**
- <fact left out> — <where it lives instead>
```

Drop any heading with no entries, with two exceptions: **Unrun checks** and **Open questions** always appear, and read `none` when they are empty — their emptiness is the reader's only evidence that nothing was quietly skipped. In audit mode, order entries under each heading by how much they affect an adoption decision, not by where they sit in the file.

Completion criterion: the report exists in the shape above, and every line in it names a file, a command that was actually run, or a question that was actually asked.

## Failure recovery

Checks fail routinely. Apply the first-line fix, then the fallback; never stall or replace evidence with a guess.

| Trigger | First-line fix | Fallback if that also fails |
|---|---|---|
| The validator cannot be located, errors, or no Python interpreter is available | Look for `scripts/validate_readme.py` beside this SKILL.md; retry with `python3`; if the script itself raises, check headings, anchors, and local link targets by hand against the repository | Record the static check as unrun in the delivery report and deliver the rest — never treat a skipped check as a passed one |
| A documented command fails when run | Correct it against the manifest, `Makefile`, CI workflow, or `--help` output, then rerun once | Downgrade the command to unverified: keep it only if evidence in a file supports it, and list it under unrun checks |
| An external link is unreachable | Retry once, then try the project's canonical domain or its repository page | Drop the link and keep the plain-text name; report the removal |
| The repository has no manifest, CI, or tests to read from | Derive facts from entry-point source files, directory layout, and recent commits | Ship only the verifiable minimum — purpose, what exists, known limitations — and list every gap as an open question |
| Translated variants cannot all be updated well | Update the variants you can write correctly | Name each untouched variant and the specific divergence in the delivery report |
| The README and the code contradict each other and neither is clearly right | Use git history to establish which changed last | Leave both readings in the report as an open question; do not silently pick one |

## Never do these

Reject a draft that does any of these:

- presents planned work as shipped behavior;
- invents expected output instead of using real output or clearly labeled illustration;
- deletes existing content it did not understand instead of preserving and reporting it;
- trusts an inherited claim without re-verifying it, especially a license claim without a LICENSE file.

