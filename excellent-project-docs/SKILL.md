---
name: excellent-project-docs
description: Write, improve, audit, or synchronize a repository's README.md and the companion files GitHub reads from the root, .github/, or docs/ (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, CHANGELOG, ARCHITECTURE, ROADMAP, GOVERNANCE, issue and PR templates), with every claim traced to repository evidence. Use when the user asks for a README or project homepage, a contributing, security, or architecture file or a GitHub community profile, docs brought back in step after code or configuration changes, or a check that the docs are accurate, runnable, and consistent with each other. Not for an API manual, a documentation website or the other pages under docs/, or writing unrelated to a repository.
---

# Excellent Project Docs

A repository's documentation is a hub and its satellites. The README is the hub: an entry point, not a complete manual, that helps the reader decide “Is this for me?” and reach a first success without reading source code. Companion documents — `CONTRIBUTING.md`, `SECURITY.md`, `ARCHITECTURE.md`, and the others in [companion-documents](references/companion-documents.md) — are satellites: each holds one topic that would bloat the README, and the README links to it. Put disqualifying prerequisites and limitations early; helping a non-fit reader leave quickly is success.

## Work modes

Identify the requested outcome first:

- **Create**: the target document does not exist; build a first draft from repository facts.
- **Improve**: preserve correct content while fixing structure, clarity, gaps, and drift. Prefer in-place edits. 🔴 **CHECKPOINT** before a full rewrite, and before removing a whole section rather than rewording it: inventory the unique content that would go, wait for explicit approval, and without it edit in place and list the proposed removal in the report.
- **Audit**: do not edit first; report evidence, problems, risks, and priority-ordered recommendations across the whole set.
- **Synchronize**: update facts affected by code or configuration changes in every document that states them; treat drift as functional damage.

No mode given: default to “improve and verify”. No document named: the README is the target and companions enter only through the step 3 checkpoint. Do not turn a document into a complete documentation website unless asked.

Translated variants are one document: update every variant you can write accurately and report any divergence. Add a variant only when the user chose that language at the step 3 checkpoint; name it with a BCP 47 tag (`README.zh-TW.md`) with English in the base file, preserving an established naming scheme.

## Invariants

1. **Evidence first**: gather facts from the repository before writing. Never invent features, commands, versions, environment variables, deployment methods, performance numbers, badges, screenshots, license details, contribution rules, security contacts, or release history.
2. **Reader-led**: order information around the reader's decisions, not the author's implementation order. The top of the README must independently explain the project's purpose and smallest useful path; the top of each companion document must state its one topic and who it is for.
3. **Cognitive funnel**: one-line purpose → minimal runnable example → installation → configuration and limitations → API or architecture details → contribution and acknowledgements. The license stays in the LICENSE file, which GitHub surfaces itself; a one-line License section only when the licensing needs explaining ([readme-framework](references/readme-framework.md)). A stage that outgrows the README moves to a companion document, leaving a summary and a link.
4. **Runnable**: commands trace to repository files, scripts, CLI help, or tests. Run the examples that need no network, credentials, paid services, dependency installation, or data changes; for any other, 🔴 **CHECKPOINT** for authorization, and absent approval it is `unrun`, never passed.
5. **Single source of truth**: one fact lives in one file. No document restates another's content, and none copies what a reader can inspect directly and what drifts. Prose carries background, rationale, limitations, and workflows the files do not reveal.
6. **Right-sized**: candidate sections and companion documents are options, not a completeness score. Keep small projects to a README.
7. **Propose, then create**: a companion document the user did not name is created only after approval at the step 3 checkpoint; a document the user named is handled directly.
8. **Honest gaps**: 🔴 **CHECKPOINT** before choosing a license, contribution channel, security contact, conduct standard, roadmap, the language set, or whether the README carries badges and images and in which style. Every such question known before drafting goes into the one step 3 checkpoint rather than a message of its own. If nobody can answer, omit the section or document and report the question — never ship `TODO:`. State adoption-relevant absences (no LICENSE) as facts. Omit rather than invent.

## Workflow

### 1. Establish the goal and audience

Identify language, audience, purpose, target documents, and output paths. Audience gates section choice, depth, and tone, and a companion document may serve a different reader than the README. When evidence leaves the audience ambiguous and the user can answer, record plausible reader types as a question for the step 3 checkpoint; otherwise make the smallest evidence-based assumption and disclose it. Do not ask when evidence settles it: a published library implies integrators, a CLI manifest implies CLI users, an open `CONTRIBUTING.md` implies external contributors.

Languages are the user's decision. Record which languages the set carries as a question for the step 3 checkpoint when creating a README, or when the existing set is in one language and the user writes in another. Without an answer, a new README is written in English alone and the language is reported as assumed; an existing set keeps its languages. Never add a variant the user did not choose; an existing one is maintained as it stands.

Completion criterion: one sentence per target document naming who it helps and what decision it supports, and a language set inherited from the repository or recorded as a step 3 question.

### 2. Build an evidence inventory

Inspect directly:

- manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `*.csproj`, `go.mod`
- build and deployment configuration: `Makefile`, Taskfile, CI workflows, Dockerfiles, compose files
- `.env.example`, other configuration, CLI `--help`, tests, and examples
- `LICENSE`, every existing companion document in the root, `.github/`, and `docs/`, plus `.github/ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE`, `FUNDING.yml`, `CODEOWNERS`, and `dependabot.yml`
- release tags, `CHANGELOG`, and commits since the last release
- the existing README, images, demo assets, and recent changes, to spot likely drift

Classify each fact **verified**, **plausible but unverified**, or **missing**; only verified facts may be unqualified. Record which document currently states each fact, because a fact in two places is a drift risk to resolve in step 5.

Completion criterion: every command, path, environment variable, feature, and link retained anywhere has a traceable source, and every existing companion document is listed with its topic.

### 3. Choose the document set and each document's shape

Choose README sections from evidence, using these project-type emphases:

- **CLI / application**: quick start, usage examples, configuration, output, limitations, deployment.
- **Library / SDK**: one-line purpose, minimal API example, installation, API, compatibility.
- **Service / API**: architecture, startup, environment variables, health checks, API entry points, security, deployment.
- **Frontend / full-stack product**: demo or screenshots, features, stack, architecture, local development, deployment.
- **Tool / research project**: problem context, method, reproduction steps, inputs and outputs, limitations, citations.

Four choices belong to the user, not the evidence. Put them in one 🔴 **CHECKPOINT** together with the audience and language questions recorded in step 1 and the companion-document proposal below, so every question known before drafting reaches the user in a single message:

- **Presentation level**: **plain** (the default: text, tables, code, and the badges or images chosen below) or **showcase**, the designed page in [visual-readme](references/visual-readme.md). Offer showcase as an option; do not recommend it. Include the style proposal the recipe derives from the project — accent, mood, domain cue, banner direction — with one alternative, so the user picks a look rather than answering an open question. In showcase the banner is drafted and rendered first, and the recipe's 🔴 **CHECKPOINT** on its PNG precedes the rest of the draft.
- **Visual elements**: the badges the evidence supports, each with its dynamic endpoint or recorded source ([readme-framework](references/readme-framework.md)), and the logo, screenshots, or demo assets already in the repository. Ask whether to include any, which ones, and which badge style — a shields.io style, or a fully hand-drawn static SVG row when no dynamic endpoint exists and the project's identity needs it; offer to keep an existing style.
- **Primary path**: when several install or run channels exist, ask which one leads Getting Started; the others follow it.
- **Tagline** (create mode): offer two or three one-line descriptions from the evidence to pick or rewrite.

Without an answer: plain; no badges or images; lead with the channel the manifests and CI document most completely and disclose the assumption; keep the tagline and mark it assumed in the report. A user who declines badges or images gets none, even when the evidence supports them.

Then decide the companion documents. Read [companion-documents](references/companion-documents.md) and record each candidate as **exists** (keep, improve, or synchronize), **justified** (the evidence threshold is met and the document is missing), or **not justified**. A README section that has outgrown the funnel — a contribution guide longer than the quick start, an architecture walkthrough before the first example — is evidence for one.

When any candidate is **justified** and the user did not name it, the same 🔴 **CHECKPOINT** presents the proposed files, the evidence behind each, and the questions only the user can answer (security contact, contribution policy, conduct standard), then waits. Create only what the user approves; report the rest as recommendations. Leave the proposal out when the user named the documents or nothing new is justified.

Never add empty template sections or files. Omit unsupported sections and report consequential gaps.

Completion criterion: the document set and every section list written down before drafting, each entry naming its evidence, and every new companion file explicitly approved.

### 4. Draft the documents

Follow the cognitive funnel, section rules, and anti-patterns in [readme-framework](references/readme-framework.md); the palette, header block, banner, diagram, card, and collapse rules in [visual-readme](references/visual-readme.md) only when the user chose showcase; and each companion document's row in [companion-documents](references/companion-documents.md). Calibrate tone, density, and rhythm against [exemplars](references/exemplars.md).

Keep the first screen of every document independently useful, and put a real example before abstract internals. Link deeper material instead of copying it; where a fact moves into a companion document, leave a one-line summary and a relative link in the README and open the companion with a link back. Never imply `.env`, configuration, deployment, review, or release behavior that code, CI, or history does not implement. Use GFM, sparse admonitions for must-not-miss facts, sparse emoji, and shallow lists. A badge, logo, demo, or screenshot appears only if the user chose it at step 3, must answer a reader question, and cannot carry the only copy of a fact; use repository assets only.

Completion criterion: a reader understands the purpose and completes the smallest useful path from the README alone, and reaches every companion document in one click.

### 5. Verify content, examples, and cross-document consistency

Per document:

- Markdown headings, table-of-contents anchors, external links, and local links.
- Local images, GIFs, videos, and example files exist.
- Commands match manifests, Makefiles, CI workflows, or `--help` — not merely that the text appears somewhere.
- Minimal installation, startup, and usage examples run, subject to invariant 4. Unauthorized commands are `unrun`, never verified.
- For a showcase README, the banner is rendered the way GitHub will: through an `<img>` at the desktop and phone container widths and over a dark page. A preview at the canvas width shows nothing about sizing, the reader's fonts, the ground, or whitespace. When the change is already on github.com, open the rendered README there once; when it is not yet pushed — the usual case before delivery — list the GitHub-side render under **Unrun checks** instead.
- The section and document sets still match the current repository; no filler was added to satisfy a checklist.

For the set:

- Every companion document is linked from the README and links back.
- No fact is stated in two documents with different values (version, command, contact, supported platform); one owner and a link.
- Companion documents live where GitHub reads them: the root, `.github/`, or `docs/`; templates under `.github/`.
- `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` name a channel the evidence or the user confirmed.

Then run the checker that ships with this skill before delivering any create, improve, or synchronize result. It lives at `scripts/validate_docs.py` in the same directory as this SKILL.md file, so resolve the path from wherever you read this file: `python <that directory>/scripts/validate_docs.py <document>... --project <repository-root>`, passing every document you touched. It ignores code blocks, and its warnings are heuristic leads — read each flagged line and judge it before editing. If a check cannot run, do not stall: follow the matching row in **Failure recovery** and continue.

Completion criterion: every retained command and link passes a traceability check, no fact has two owners, and every unverified item is qualified in plain wording or listed in the report — never a placeholder.

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

Drop any heading with no entries, except **Unrun checks** and **Open questions**, which always appear and read `none` when empty — their emptiness is the reader's only evidence that nothing was quietly skipped. In audit mode order entries under each heading by how much they affect an adoption or contribution decision, not by position in the file.

Completion criterion: the report exists in that shape, and every line names a file, a command that was actually run, or a question that was actually asked.

## Failure recovery

Checks fail routinely. Apply the first-line fix, then the fallback; never stall or replace evidence with a guess.

| Trigger | First-line fix | Fallback if that also fails |
|---|---|---|
| The validator cannot be located, errors, or no Python interpreter is available | Look for `scripts/validate_docs.py` beside this SKILL.md; retry with `python3`; if the script raises, check headings, anchors, and local link targets by hand | Record the static check as unrun in the report and deliver the rest — never treat a skipped check as a passed one |
| A documented command fails when run | Correct it against the manifest, `Makefile`, CI workflow, or `--help`, then rerun once | Downgrade it to unverified: keep it only if a file supports it, and list it under unrun checks |
| An external link is unreachable | Retry once, then try the project's canonical domain or repository page | Drop the link, keep the plain-text name, report the removal |
| The repository has no manifest, CI, or tests to read from | Derive facts from entry-point source files, directory layout, and recent commits | Ship only the verifiable minimum — purpose, what exists, known limitations — and list every gap as an open question |
| Translated variants cannot all be updated well | Update the variants you can write correctly | Name each untouched variant and its specific divergence in the report |
| Two documents, or a document and the code, contradict each other and neither is clearly right | Use git history to establish which changed last | Leave both readings in the report as an open question; do not silently pick one |
| A justified companion document needs an answer nobody can give | Ask the user once at the step 3 checkpoint | Do not create the file; list it under **Documents** as proposed, not created, with the missing answer as an open question |
| The same companion document exists in two recognized locations | Keep the one GitHub resolves first and the one the README links to, if they agree | Report the duplicate as an open question; do not delete either without approval |

## Never do these

A last pass over the draft, for the four prohibitions no other rule states. Every other prohibition in this file is stated where it belongs — in the invariants, the work modes, or the step that acts on it.

- presents planned work as shipped behavior;
- invents expected output instead of using real output or a clearly labeled illustration;
- deletes existing content it did not understand instead of preserving and reporting it;
- trusts an inherited claim without re-verifying it, especially a license claim with no LICENSE file.
