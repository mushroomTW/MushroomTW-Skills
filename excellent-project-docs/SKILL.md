---
name: excellent-project-docs
description: Write, improve, audit, or synchronize a repository's README.md and the companion files GitHub reads from the root or .github/ (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, CHANGELOG, ARCHITECTURE, ROADMAP, GOVERNANCE, issue and PR templates), with every claim traced to repository evidence. Use when the user asks for a README or project homepage, a contributing, security, or architecture file or a GitHub community profile, docs brought back in step after code or configuration changes, or a check that the docs are accurate, runnable, and consistent with each other. Not for an API manual, a documentation website or the pages under docs/, or writing unrelated to a repository.
---

# Excellent Project Docs

A repository's documentation is a hub and its satellites. The README is the hub: an entry point, not a complete manual, that helps the reader decide “Is this for me?” and reach a first success without reading source code. Companion documents — `CONTRIBUTING.md`, `SECURITY.md`, `ARCHITECTURE.md`, and the others in [companion-documents](references/companion-documents.md) — are satellites: each holds one topic that would bloat the README, and the README links to it. Put disqualifying prerequisites and limitations early; helping a non-fit reader leave quickly is success.

## Work modes

First identify the requested outcome:

- **Create**: the target document does not exist; build a first draft from repository facts.
- **Improve**: preserve correct content while fixing structure, clarity, gaps, and drift. Prefer in-place edits. 🔴 **CHECKPOINT** before a full rewrite of any existing document, and before removing an entire existing section rather than rewording it: inventory the unique content that would go and wait for explicit approval; without it, edit in place and list the proposed removal in the report.
- **Audit**: do not edit first; report evidence, problems, risks, and priority-ordered recommendations across the whole document set.
- **Synchronize**: update facts affected by code or configuration changes in every document that states them; treat drift as functional damage.

If the user does not specify a mode, default to “improve and verify.” If the user names no document, the README is the target and companion documents enter only through the proposal checkpoint in step 3. Unless explicitly requested, do not turn any document into a complete documentation website.

Treat translated variants as one document: update every variant you can write accurately and report any divergence. A new variant is added only when the user chose that language at the step 1 checkpoint; name it with a BCP 47 tag (`README.zh-TW.md`, `CONTRIBUTING.zh-TW.md`) with English in the base file, and preserve an established repository naming scheme.

## Invariants

1. **Evidence first**: gather facts from the repository before writing. Never invent features, commands, versions, environment variables, deployment methods, performance numbers, badges, screenshots, license details, contribution rules, security contacts, or release history.
2. **Reader-led**: order information around the reader's decisions, not the author's implementation order. The top of the README must independently explain the project's purpose and smallest useful path; the top of each companion document must state its one topic and who it is for.
3. **Cognitive funnel**: move from broad to specific: one-line purpose → minimal runnable example → installation → configuration and limitations → API or architecture details → contribution and acknowledgements. The license stays in the LICENSE file, which GitHub surfaces itself; the README gets a one-line License section only when the licensing needs explaining (see [readme-framework](references/readme-framework.md)). Once a stage outgrows the README, it moves to a companion document and the README keeps a summary plus a link.
4. **Runnable**: commands must trace to repository files, scripts, CLI help, or tests. Run examples that need no network, credentials, paid services, dependency installation, or data changes. Otherwise 🔴 **CHECKPOINT** for authorization; absent approval means `unrun`, never passed.
5. **Single source of truth**: one fact lives in one file. The README does not restate a companion document, a companion document does not restate the README's quick start, and neither copies information that readers can directly inspect in the environment and that is likely to drift. Use prose for background, rationale, limitations, and workflows that the files do not reveal.
6. **Right-sized**: candidate sections and candidate companion documents are options, not a completeness score. Keep small projects to a README; add companion documents only when the evidence in [companion-documents](references/companion-documents.md) justifies each one.
7. **Propose, then create**: a companion document the user did not name is created only after the user approves it at the step 3 checkpoint. A document the user named is handled directly.
8. **Honest gaps**: 🔴 **CHECKPOINT** and ask before choosing a license, contribution channel, security contact, code-of-conduct standard, roadmap, which languages the document set carries, or whether the README carries badges and images and in which style. If nobody can answer, omit the section or document and report the question; never ship `TODO:`. State adoption-relevant absences (for example, no LICENSE) as facts, not placeholders. Omit rather than invent.

## Workflow

### 1. Establish the goal and audience

Identify language, audience, purpose, target documents, and output paths. Audience gates section choice, depth, and tone; a companion document may serve a different reader than the README (contributors rather than users). If evidence is ambiguous and the user can answer, 🔴 **CHECKPOINT** and offer plausible reader types. If nobody can answer, make the smallest evidence-based assumption and disclose it. Do not ask when evidence settles it: a published library implies integrators; a CLI manifest implies CLI users; an open `CONTRIBUTING.md` implies external contributors.

Languages are the user's decision. When creating a README, or when the existing document set is in one language and the user writes in another, 🔴 **CHECKPOINT**: ask which languages the set should carry. Never add a translated variant the user did not choose; an existing variant is maintained as it stands.

Completion criterion: state in one sentence per target document who it helps and what decision or task it supports — confirmed by the user when the choice was ambiguous — and the language set is either inherited from the repository or chosen by the user.

### 2. Build an evidence inventory

Inspect directly:

- `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `go.mod`, and other manifests
- `Makefile`, Taskfile, CI workflows, Dockerfiles, compose files, and deployment configuration
- `.env.example`, configuration files, CLI `--help`, tests, and existing examples
- `LICENSE`, every existing companion document in the root, `.github/`, and `docs/`, plus `.github/ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE`, `FUNDING.yml`, `CODEOWNERS`, and `dependabot.yml`
- release tags, `CHANGELOG`, and the commit history since the last release
- the existing README, images, demo assets, and recent changes, to identify likely drift

Classify facts as **verified**, **plausible but unverified**, or **missing**; only verified facts may be unqualified. Record which existing document currently states each fact, because a fact stated in two places is a drift risk to resolve in step 5.

Completion criterion: every command, path, environment variable, feature, and link retained in any target document has a traceable source, and every existing companion document is listed with its current topic.

### 3. Choose the document set and each document's shape

Choose README sections from evidence, using these project-type emphases:

- **CLI / application**: quick start, usage examples, configuration, output, limitations, deployment.
- **Library / SDK**: one-line purpose, minimal API example, installation, API, compatibility.
- **Service / API**: architecture, startup, environment variables, health checks, API entry points, security, deployment.
- **Frontend / full-stack product**: demo or screenshots, features, stack, architecture, local development, deployment.
- **Tool / research project**: problem context, method, reproduction steps, inputs and outputs, limitations, citations.

Some README choices are the user's, not the evidence's. Collect the ones below and put them to the user in one 🔴 **CHECKPOINT**, folded into the companion-document checkpoint further down when both apply:

- **Presentation level**: **plain** (the default: text, tables, code, and whatever badges or images the user picks below) or **showcase** (a centered header block with a banner, one Mermaid diagram per concept section, panel-style section breaks — the recipe in [visual-readme](references/visual-readme.md)). Offer showcase as an option; do not recommend it.
- **Visual elements**: the badges the evidence supports (each with its dynamic endpoint or recorded source, per the badge rules in [readme-framework](references/readme-framework.md)) and the logo, screenshots, or demo assets that exist in the repository. Ask whether to include any, which ones, and which shields.io style; when the README already has badges, offer to keep their existing style.
- **Primary path**: when the project installs or runs through several channels — registry package, container image, source build, installer — ask which one leads Getting Started; the others follow it.
- **Tagline** (create mode): offer two or three one-line descriptions drawn from the evidence for the user to pick or rewrite.

Without an answer: plain; no badges or images; lead with the channel the manifests and CI document most completely and disclose that assumption; keep the tagline and mark it assumed in the report. A user who says no badges or images gets none, even when the evidence supports them.

Then decide the companion documents. Read [companion-documents](references/companion-documents.md) and, for each candidate, record one of: **exists** (keep, improve, or synchronize), **justified** (the evidence threshold is met and the document is missing), or **not justified**. A README section that has outgrown the funnel — a contribution guide longer than the quick start, an architecture walkthrough before the first example — is evidence for a companion document.

🔴 **CHECKPOINT** when any candidate is **justified** and the user did not name it: present the proposed files, the evidence behind each, and the questions only the user can answer (security contact, contribution policy, conduct standard), then wait. Create only the files the user approves; report the rest as recommendations. Skip the checkpoint when the user already named the documents or when nothing new is justified.

Never add empty template sections or empty template files. Omit unsupported sections and report consequential gaps.

Completion criterion: the document set and every document's section list are written down before drafting, every entry names the evidence that justifies it, and every new companion file has explicit approval.

### 4. Draft the documents

For the README follow the cognitive funnel, section rules, and anti-patterns in [readme-framework](references/readme-framework.md) — and, only when the user chose showcase, the header block, banner, and diagram rules in [visual-readme](references/visual-readme.md); for each companion document follow its row in [companion-documents](references/companion-documents.md). Calibrate tone, density, and section rhythm against [exemplars](references/exemplars.md).

Keep the first screen of every document independently useful. Put a real example before abstract internals; link deeper material instead of copying it. Where a fact moves from the README into a companion document, leave a one-line summary and a relative link in the README, and open the companion document with a link back. Never imply `.env`, configuration, deployment, review, or release behavior that code, CI, or history does not implement. Use GFM, sparse admonitions for must-not-miss facts, sparse emoji, and shallow lists. A badge, logo, demo, or screenshot appears only if the user chose it at the step 3 checkpoint, must answer a reader question, and cannot carry the only copy of a fact; use repository assets only and follow the framework's badge rules.

Completion criterion: a reader can understand the project's purpose and complete the smallest useful path from the README alone, and can reach every companion document from it in one click.

### 5. Verify content, examples, and cross-document consistency

Run proportional checks on every target document:

- Check Markdown headings, table-of-contents anchors, external links, and local links.
- Confirm that local images, GIFs, videos, and example files exist.
- Compare commands against manifests, Makefiles, CI workflows, or `--help`; do not merely check that the text appears somewhere.
- Run minimal installation, startup, and usage examples subject to invariant 4. Unauthorized commands are `unrun`, never verified.
- Re-evaluate the section set and the document set against the current repository; do not add filler merely to satisfy a checklist.

Then check the set as a whole:

- Every companion document is linked from the README, and links back to it.
- No fact is stated in two documents with different values (version, command, contact, supported platform); resolve it to one owner and a link.
- Companion documents that GitHub reads live where GitHub looks: the root, `.github/`, or `docs/`; a template lives under `.github/`.
- `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` name a real channel that the evidence or the user confirmed.

Run the checker that ships with this skill before delivering any create, improve, or synchronize result. It lives at `scripts/validate_docs.py` in the same directory as this SKILL.md file, so resolve the path from wherever you read this file: `python <that directory>/scripts/validate_docs.py <document-path>... --project <repository-root>`, passing every document you touched. It ignores code blocks, and its warnings are heuristic leads: read each flagged line and judge it before editing. If a check cannot run, do not stall — follow the matching row in **Failure recovery** and continue.

Completion criterion: every retained command and link passes a traceability check, no fact has two owners, and every unverified item is either qualified in plain wording or listed in the delivery report — never left as a placeholder.

### 6. Perform a final reader review

Read each document once from its reader's perspective and apply [quality-checklist](references/quality-checklist.md).

For an audit or a delivery, write the report in this shape:

```markdown
**Mode**: create | improve | audit | synchronize
**Audience**: <who this documentation helps, and what decision it supports> — confirmed by the user | assumed from <evidence>

**Documents**
- <path> — created | improved | synchronized | audited only | proposed, not created (<why>)

**Changed**
- <document › section> — <what changed, and the evidence behind it>

**Verified**
- <command, link, or path> — <how: ran it / matched `package.json` / compared against `--help`>

**Unrun checks**
- <check> — <why it could not run, and what would unblock it>

**Open questions**
- <question only the user can answer> — <the section or document it would unlock>

**Deliberately omitted**
- <fact or document left out> — <where it lives instead, or why it is not justified>
```

Drop any heading with no entries, with two exceptions: **Unrun checks** and **Open questions** always appear, and read `none` when they are empty — their emptiness is the reader's only evidence that nothing was quietly skipped. In audit mode, order entries under each heading by how much they affect an adoption or contribution decision, not by where they sit in the file.

Completion criterion: the report exists in the shape above, and every line in it names a file, a command that was actually run, or a question that was actually asked.

## Failure recovery

Checks fail routinely. Apply the first-line fix, then the fallback; never stall or replace evidence with a guess.

| Trigger | First-line fix | Fallback if that also fails |
|---|---|---|
| The validator cannot be located, errors, or no Python interpreter is available | Look for `scripts/validate_docs.py` beside this SKILL.md; retry with `python3`; if the script itself raises, check headings, anchors, and local link targets by hand against the repository | Record the static check as unrun in the delivery report and deliver the rest — never treat a skipped check as a passed one |
| A documented command fails when run | Correct it against the manifest, `Makefile`, CI workflow, or `--help` output, then rerun once | Downgrade the command to unverified: keep it only if evidence in a file supports it, and list it under unrun checks |
| An external link is unreachable | Retry once, then try the project's canonical domain or its repository page | Drop the link and keep the plain-text name; report the removal |
| The repository has no manifest, CI, or tests to read from | Derive facts from entry-point source files, directory layout, and recent commits | Ship only the verifiable minimum — purpose, what exists, known limitations — and list every gap as an open question |
| Translated variants cannot all be updated well | Update the variants you can write correctly | Name each untouched variant and the specific divergence in the delivery report |
| Two documents, or a document and the code, contradict each other and neither is clearly right | Use git history to establish which changed last | Leave both readings in the report as an open question; do not silently pick one |
| A justified companion document needs an answer nobody can give (security contact, contribution policy, conduct standard) | Ask the user once at the step 3 checkpoint | Do not create the file; list it under **Documents** as proposed, not created, with the missing answer as an open question |
| The same companion document exists in two recognized locations (for example root and `.github/`) | Keep the one GitHub resolves first and the one the README links to, if they agree | Report the duplicate as an open question; do not delete either without approval |

## Never do these

Reject a draft that does any of these:

- presents planned work as shipped behavior;
- invents expected output instead of using real output or clearly labeled illustration;
- deletes existing content it did not understand instead of preserving and reporting it;
- trusts an inherited claim without re-verifying it, especially a license claim without a LICENSE file;
- adds a License section or license badge that only repeats the LICENSE file;
- adds badges or images, or changes their style, without the user's answer at the step 3 checkpoint;
- applies the showcase level, or draws a diagram of components the code does not contain, when the user did not choose showcase;
- adds a translated variant the user did not choose;
- removes an entire existing section without the approval the improve-mode checkpoint requires;
- creates a companion document the user neither named nor approved;
- leaves a companion document unreachable from the README, or lets two documents own the same fact;
- fills `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` with a contact, policy, or standard that no evidence and no user confirmed.
