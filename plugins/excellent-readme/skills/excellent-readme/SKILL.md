---
name: excellent-readme
description: Create, improve, or audit a software project's README.md. Use when the user asks to write a README, organize project documentation, improve a GitHub project homepage, add installation and usage instructions, or check whether a README is accurate, runnable, and easy to understand; do not use for a complete API manual or a general article unrelated to a repository.
---

# Excellent README

A README is a project's entry point, not its complete manual. Help the right reader quickly answer: “What is this, is it relevant to me, how do I start, and what should I know before adopting it?” The reader should be able to reach a first successful result without reading the source code.

## Work modes

First identify the requested outcome:

- **Create**: no README exists; build a first draft from repository facts.
- **Improve**: preserve correct content while fixing structure, clarity, gaps, and stale information.
- **Audit**: do not edit first; report evidence, problems, risks, and priority-ordered recommendations.
- **Synchronize**: update README content affected by code or configuration changes.

If the user does not specify a mode, default to “improve and verify.” Unless explicitly requested, do not turn the README into a complete documentation website.

## Invariants

1. **Evidence first**: gather facts from the repository before writing. Never invent features, commands, versions, environment variables, deployment methods, performance numbers, badges, screenshots, or license details.
2. **Reader-led**: order information around the reader's decisions, not the author's implementation order. The top of the README must independently explain the project's purpose and smallest useful path.
3. **Cognitive funnel**: move from broad to specific: one-line purpose → minimal runnable example → installation → configuration and limitations → API or architecture details → contribution, license, and acknowledgements.
4. **Runnable**: README installation, startup, test, and usage examples must correspond to files, scripts, CLI help, or tests that exist in the repository. Run safe examples when practical.
5. **Single source of truth**: do not copy information that readers can directly inspect in the environment and that is likely to drift. Use the README for background, rationale, limitations, and workflows that the files do not reveal.
6. **Right-sized**: the 15 sections from the reference article are candidates, not mandatory headings. Keep small projects short; add architecture, project structure, security, API, contribution, and roadmap sections only when they help.
7. **Honest gaps**: when required information cannot be found, keep an explicit `TODO:` or report the gap. Never fill missing facts with plausible guesses.

## Workflow

### 1. Establish the goal and audience

Identify the README language, audience, purpose, and output path. At minimum, identify whether the primary reader is an end user, package integrator, CLI user, deployer, contributor, or maintainer. If information is missing, make the smallest reasonable assumption from the repository and state it in the result.

Completion criterion: state in one sentence who the README helps and what decision or task it supports.

### 2. Build an evidence inventory

Prefer the available codebase knowledge graph: use `search_graph` for symbols and entry points, `trace_path` for important flows, and `get_code_snippet` for necessary implementations. If the graph is unavailable or insufficient, inspect:

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

Do not add empty sections just to fill a template. Omit sections without useful evidence or mark the gap explicitly.

### 4. Draft the README

Usually use this order, adapting it to the project:

1. Title and one-line description; add meaningful badges, a demo, or a screenshot only when useful. Follow the badge rules in `references/readme-framework.md`. If the repository already contains a logo or icon asset, use it in the header; do not source or generate one.
2. Table of contents; include it only when the README is long enough to benefit from navigation.
3. About, context, and use cases: explain the problem, scope, and non-goals.
4. Minimal runnable example: show real input, output, or screen state.
5. Installation and Getting Started: provide the complete path from clone or installation to the first successful run.
6. Features: describe user-visible capabilities without unnecessary implementation detail.
7. Tech Stack, Architecture, and Project Structure: include them when they help understanding, integration, or contribution.
8. Configuration: document required settings, defaults, formats, and handling of sensitive information.
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

Use `scripts/validate_readme.py` for static checks when useful; read its output before making corrections.

Completion criterion: every retained command and link passes a traceability check, and every unverified item is explicitly marked.

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
