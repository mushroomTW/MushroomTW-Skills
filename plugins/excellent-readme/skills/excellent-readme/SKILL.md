---
name: excellent-readme
description: Create, improve, audit, or synchronize a software project's README.md. Use when the user asks to write a README, organize project documentation, improve a GitHub project homepage, add installation and usage instructions, update a README after code or configuration changes, or check whether a README is accurate, runnable, and easy to understand; do not use for a complete API manual or a general article unrelated to a repository.
---

# Excellent README

A README is a project's entry point, not its complete manual. Help the right reader quickly answer: “What is this, is it relevant to me, how do I start, and what should I know before adopting it?” The reader should be able to reach a first successful result without reading the source code. Order information by how quickly it lets the wrong reader bail out: a reader who discovers early that the project does not fit their needs has been served, not lost.

## Work modes

First identify the requested outcome:

- **Create**: no README exists; build a first draft from repository facts.
- **Improve**: preserve correct content while fixing structure, clarity, gaps, and stale information. Prefer in-place edits; replacing an existing README wholesale discards content, so confirm with the user before a full rewrite.
- **Audit**: do not edit first; report evidence, problems, risks, and priority-ordered recommendations.
- **Synchronize**: update README content affected by code or configuration changes. An outdated README misleads more actively than a missing one, so treat drift as damage rather than cosmetics.

If the user does not specify a mode, default to “improve and verify.” Unless explicitly requested, do not turn the README into a complete documentation website.

When the repository keeps translated variants of the README (`README_ZH.md`, `README.fr.md`, files under `docs/` or `translations/`), treat them as one document in several languages: apply content changes to every variant you can write well, and report any variant left out of sync instead of letting it drift silently. Name a new translation with a BCP 47 language tag (`README.zh-TW.md`, `README.de.md`) and keep `README.md` for English when several languages coexist; when the repository already uses another naming scheme, follow it.

## Invariants

1. **Evidence first**: gather facts from the repository before writing. Never invent features, commands, versions, environment variables, deployment methods, performance numbers, badges, screenshots, or license details.
2. **Reader-led**: order information around the reader's decisions, not the author's implementation order. The top of the README must independently explain the project's purpose and smallest useful path.
3. **Cognitive funnel**: move from broad to specific: one-line purpose → minimal runnable example → installation → configuration and limitations → API or architecture details → contribution, license, and acknowledgements.
4. **Runnable**: README installation, startup, test, and usage examples must correspond to files, scripts, CLI help, or tests that exist in the repository. Run every example that needs no network, credentials, paid services, or data changes; for the rest, obtain authorization first or report the check as unrun.
5. **Single source of truth**: do not copy information that readers can directly inspect in the environment and that is likely to drift. Use the README for background, rationale, limitations, and workflows that the files do not reveal.
6. **Right-sized**: the 15 sections from the reference article are candidates, not mandatory headings. Keep small projects short; add architecture, project structure, security, API, contribution, and roadmap sections only when they help.
7. **Honest gaps**: information only the user can decide — license choice, contribution channels, contact points, roadmap — is asked, not written around. When nobody can answer, omit the section and list the open question in the delivery report; the README never ships `TODO:` placeholders. When an absence itself affects adoption (no license file, no support channel), state the absence as a plain fact in the appropriate section — a fact, not a placeholder. Never fill missing facts with plausible guesses, and never write a sentence just so a candidate section can exist — omitting a section is always better than inventing its content.

## Workflow

### 1. Establish the goal and audience

Identify the README language, audience, purpose, and output path. At minimum, identify whether the primary reader is an end user, package integrator, CLI user, deployer, contributor, or maintainer. The audience decision gates everything downstream — the section set, how much implementation depth is allowed, and the tone — so when repository evidence leaves it genuinely ambiguous and the user can answer, ask them, offering the plausible reader types, instead of guessing. Only when nobody can answer, make the smallest reasonable assumption from the repository and state it in the delivery report. Do not ask when the evidence already settles it: a published library implies integrators, a CLI manifest implies CLI users.

Completion criterion: state in one sentence who the README helps and what decision or task it supports — confirmed by the user when the choice was ambiguous.

### 2. Build an evidence inventory

Inspect the repository directly:

- `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `go.mod`, and other manifests
- `Makefile`, Taskfile, CI workflows, Dockerfiles, compose files, and deployment configuration
- `.env.example`, configuration files, CLI `--help`, tests, and existing examples
- `LICENSE`, `CONTRIBUTING`, `SECURITY`, `docs/`, images, and demo assets
- the existing README and recent changes, to identify likely drift

Classify each candidate fact as **verified**, **plausible but unverified**, or **missing**. Do not write the latter two as unqualified facts.

Completion criterion: every command, path, environment variable, feature, and link retained in the README has a traceable source.

### 3. Choose the README shape

Adapt the structure to the project type:

- **CLI / application**: quick start, usage examples, configuration, output, limitations, deployment.
- **Library / SDK**: one-line purpose, minimal API example, installation, API, compatibility, license.
- **Service / API**: architecture, startup, environment variables, health checks, API entry points, security, deployment.
- **Frontend / full-stack product**: demo or screenshots, features, stack, architecture, local development, deployment.
- **Tool / research project**: problem context, method, reproduction steps, inputs and outputs, limitations, citations.

Do not add empty sections just to fill a template. Omit sections without useful evidence and report the gap in the delivery summary.

### 4. Draft the README

Usually use this order, adapting it to the project:

1. Title and one-line description; add a badge, demo, or screenshot only when it answers a question the reader would otherwise open another file to answer. Follow the badge rules in `references/readme-framework.md`. If the repository already contains a logo or icon asset, use it in the header; do not source or generate one.
2. Table of contents; include it only when the README is long enough to benefit from navigation.
3. About, context, and use cases: explain the problem, scope, and non-goals.
4. Minimal runnable example: show real input, output, or screen state.
5. Installation and Getting Started: provide the complete path from clone or installation to the first successful run.
6. Features: describe user-visible capabilities without unnecessary implementation detail.
7. Tech Stack, Architecture, and Project Structure: include them when they help understanding, integration, or contribution. Keep implementation internals — wire protocols, internal data structures, module walkthroughs — out of a README whose reader is an end user; keep an internal fact only when it carries a consequence the reader acts on (a port to change in two places, a file that must not be committed), phrased as that consequence, and link to code or separate docs for the rest.
8. Configuration: document required settings, defaults, formats, and handling of sensitive information. Describe how settings are actually loaded — never imply a `.env` file or an environment variable takes effect when no code reads it.
9. API or CLI Reference: document important parameters, types, optionality, defaults, return values, and examples.
10. Security, limitations, compatibility, and common issues: disclose adoption risks early.
11. Contribution, roadmap, license, acknowledgements, and author: include only confirmed, useful information.

Apply these formatting rules while drafting:

- Write GitHub Flavored Markdown. Use [GitHub admonitions](https://github.com/orgs/community/discussions/16925) — `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` — to lift prerequisites, breaking changes, security warnings, and known limitations out of the surrounding prose. Reserve them for facts a reader must not miss; a page full of them stops working.
- Keep emoji sparse. At most use them as stable section markers, never inside body prose, and never as the only carrier of meaning.
- Prefer a short paragraph or a table over a deeply nested list.

Link unfamiliar terms, important background, and external projects to reliable sources. Never make an important fact available only through an image or badge.

Completion criterion: a reader can understand the project's purpose and complete the smallest useful path without reading the source code.

### 5. Verify content and examples

Run checks proportional to the task and available authorization:

- Check Markdown headings, table-of-contents anchors, external links, and local links.
- Confirm that local images, GIFs, videos, and example files exist.
- Compare commands against manifests, Makefiles, or `--help`; do not merely check that the text appears somewhere.
- When safe, run the minimal installation, startup, or usage example. Obtain necessary authorization before actions involving networks, credentials, paid services, or data changes.
- Re-evaluate the section set against the current repository; do not add filler merely to satisfy a checklist.

Run `python <skill-dir>/scripts/validate_readme.py <readme-path> --project <repository-root>` before delivering any create, improve, or synchronize result. It ignores code blocks, and its warnings are heuristic leads: read each flagged line and judge it before editing. If a check cannot run — the validator errors, an example fails to execute, a link is unreachable — do not stall: record it as an unrun check in the delivery report and continue.

Completion criterion: every retained command and link passes a traceability check, and every unverified item is either qualified in plain wording or listed in the delivery report — never left as a placeholder.

### 6. Perform a final reader review

Read the result once from the reader's perspective:

- Does the first screen clearly explain what the project is and who it is for?
- Can a reader quickly find installation and the smallest example?
- Does the example appear before abstract implementation detail?
- Are limitations, prerequisites, security notes, and license information disclosed early enough?
- Is the README too long, repetitive, or trying to become a complete manual?
- Does any sentence sound certain despite having no repository evidence?

For an audit or delivery, report the change summary, verified items, missing information, unrun checks, and recommended locations for follow-up documentation.

## References

- Read [references/readme-framework.md](references/readme-framework.md) when choosing sections, applying the cognitive funnel, or planning the reader journey.
- Read [references/quality-checklist.md](references/quality-checklist.md) for a full audit or delivery review.
- Read [references/exemplars.md](references/exemplars.md) when calibrating tone, density, and section rhythm against real, well-regarded READMEs.
