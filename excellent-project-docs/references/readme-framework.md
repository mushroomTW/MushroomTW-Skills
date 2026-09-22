# README Design Framework

This framework combines CodeLove's “15 Essential Sections Every README Needs” with hackergrrl's “The Art of README.” Together they support three decisions: treat the README as an entry point, move from broad understanding to concrete usage, and make examples, installation, and limitations more important than decoration.

## The cognitive funnel

Order information around the reader's adoption decision:

1. **Identify**: title, one-line description, use case, and necessary context.
2. **Evaluate**: minimal usage example, main features, compatibility, and limitations.
3. **Try**: installation, prerequisites, configuration, startup, and expected output.
4. **Integrate**: API or CLI reference, tech stack, architecture, and project structure.
5. **Participate**: security, contribution, roadmap, acknowledgements, and author information.

Order the top of the page by how quickly each element lets a non-fit reader short-circuit and leave; a fast, honest “not for me” serves that reader as well as an adoption does. Content near the top should be short, concrete, and easy to evaluate. Put deeper background and maintenance information lower down. If a section does not help the target reader make a decision or complete a task, move it to a separate document, link to it, or omit it.

## Fifteen candidate sections

| Section | Keep it when | Minimum content |
| --- | --- | --- |
| Title and introduction | Always | One sentence explaining what the project does and who it helps; when creating, chosen by the user from two or three evidence-based options |
| Table of contents | The README is long | Working anchor links; do not list empty sections |
| About | There is meaningful context or a use case | Problem, purpose, and scope |
| Features | There are multiple user-facing capabilities | Outcomes rather than internal implementation |
| Tech Stack | Technology choices affect use or contribution | The main technologies actually used |
| Architecture | The system spans multiple components | Components and data or control flow; add a diagram when useful |
| Project Structure | Contributors need repository orientation | The purpose of important directories and files |
| Getting Started | Almost always | The path from installation to first successful result, led by the channel the user chose when several exist |
| Configuration | There are environment variables, config files, or external services | Name, purpose, requiredness, default, and secret-handling rules |
| Security | There are credentials, user data, networks, or deployment risks | Security boundaries, prohibited practices, and reporting path |
| API or CLI | It is a library, SDK, or CLI | Copyable calls or commands and their output |
| How to Contribute | External contributions are welcome | Where to ask questions, whether PRs are accepted, and the development, testing, submission, and conduct entry points |
| What's Next | There is a confirmed public roadmap | Short-term direction without invented commitments |
| License | Only when the licensing needs explaining: dual or multi-licensing, a non-OSI license, terms that differ by version or subdirectory, or the user asks for it | One line at the end of the README: the [SPDX identifier](https://spdx.org/licenses/) (`MIT`, `Apache-2.0`) and a link to the license file; never the license text or a paragraph about it |
| Acknowledgements / Author | It helps readers use or trust the project | Confirmed credits and contact information |

These are candidate sections, not a completeness score. A short, accurate README is better than a long README full of filler.

The sections are the same at both presentation levels. Plain is the default; when the user chose showcase at the step 3 checkpoint, [visual-readme](visual-readme.md) adds a palette, a header block with a banner and facts line, themed diagrams, feature cards, and collapsed reference tables on top of the same section set and the same evidence.

### The license lives in the LICENSE file

GitHub reads `LICENSE` and shows the license in the repository sidebar, so a README section that repeats it is a second owner for the same fact. Half of the most-starred repositories carry no License section at all; the rest keep it to a single line such as `[MIT](LICENSE)`. Follow that: when a LICENSE file exists and the licensing is plain, write no License section and no license badge. Write the one-line form only for the exceptions in the table above. When auditing, a License section that merely restates the LICENSE file is reported as removable redundancy; a section that contradicts the file, or names a license with no file behind it, stays an error.

## When a section becomes its own file

Architecture, Security, How to Contribute, and What's Next each have a companion-document form (`ARCHITECTURE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `ROADMAP.md`). Keep the README section while it fits in a few lines; once it needs its own headings, or GitHub would surface it from a dedicated file (the community profile, the Security tab, the new-issue flow), move the body to the companion document and leave a one- or two-line summary with a relative link. The thresholds and minimum content for each file are in [companion-documents](companion-documents.md); the README never restates what the companion file owns.

## Usage-example rules

- Lead with the smallest complete, copyable success case.
- For a CLI, show both the command and representative output.
- For an API, show the input, call, and return value; document optional parameters, defaults, and types.
- If an example needs extra files, keep an executable example in the repository and link to it.
- Do not make critical information available only through a screenshot, animation, badge, or external video.
- When the project installs or runs through several channels, lead with the one the user chose at the step 3 checkpoint and list the others after it; do not give every channel equal weight.

## Badge rules

A badge is a compact status line, not decoration. Add one only when it answers a question the reader would otherwise have to open another file to answer — and only after the user has said yes: the evidence decides which badges are *possible*, the user decides whether the README carries any and in which style (the step 3 checkpoint in SKILL.md). The same applies to a logo, screenshot, or demo asset: offer what exists in the repository, add only what the user picked.

Choose the badge type in this order:

1. **Dynamic**: the value is fetched when the page renders, so it cannot drift. Prefer this for package versions, build or coverage status, and the latest release.
2. **Static with a recorded source**: use only when no dynamic endpoint exists. Record the origin beside the badge so a later synchronize pass can verify the value. Two ways to draw it:
   - **2a Shields.io static** — the default: a `https://img.shields.io/badge/…` URL, styled with the rest of the row.
   - **2b Hand-drawn SVG in the repository** — only when the user chose badges at the step 3 checkpoint, the value is static with a recorded source, and the project's own visual identity needs the badge row to match it (or shields.io cannot express the datum). Put the file where the repository already keeps images (`assets/`, `docs/images/`, `.github/`); give it a fixed `viewBox`, no `width`/`height`, the same palette as the rest of the page, and `role="img"` plus an `aria-label` that carries the same fact as the alt text. Keep the whole row in one style — every badge hand-drawn, or every badge shields.io — because a mixed row reads as a collage. The pixel or stepped look, when the domain cue asks for it, follows [visual-readme](visual-readme.md)'s SVG composition grammar; the license badge ban below applies to hand-drawn badges exactly as it does to shields.io.
3. **Static without a note**: acceptable only for values that cannot drift, such as a stack label that names a dependency rather than its version.

A static value and its recorded source look like this:

```markdown
<!-- badge source: rust-toolchain.toml (channel) -->
[![Rust 1.97.1](https://img.shields.io/badge/Rust-1.97.1-000000.svg)](https://www.rust-lang.org/)
```

Apply these rules to every badge:

- Link it to something the reader can verify: the registry page, the CI run, or the project's own documentation.
- Write alt text that carries the same fact as the image, because the image may fail to load. `[![npm version]` works; `[![badge]` does not.
- Do not add a license badge; the LICENSE file already puts the license in GitHub's sidebar. A License section, when one is justified, is a one-line link, not a badge.
- Keep the set small enough to read at a glance; each extra badge lowers the value of the others.

### Choosing a style

Shields.io accepts `flat` (the default), `flat-square`, `plastic`, `for-the-badge`, and `social`. The style is part of the badge question put to the user: offer the table below, propose `flat` when they have no preference, and keep an existing README's style unless they ask for a change. Apply the chosen style to every badge in the file; a mixed set reads as a collage rather than a status line.

| Style | Renders as | Reach for it when |
| --- | --- | --- |
| `flat` | Small, rounded, muted | The default. Several badges that should stay secondary to the title. |
| `flat-square` | Small, sharp corners | Same density as `flat`, matching a squared-off visual identity. |
| `for-the-badge` | Large, uppercase, wide | Two to four badges used as a deliberate header block. |
| `plastic` | Small with a gradient | The project's existing assets already use that older style. |
| `social` | GitHub-button styling | Star, fork, follow, or watch counts specifically. |

A hand-drawn SVG badge (2b above) is a sixth style outside this table: when the user picks it, draw every badge in the row that way and skip the shields.io `style=` parameter entirely.

The same badge in three styles, so the difference is visible before choosing:

```markdown
[![npm version](https://img.shields.io/npm/v/example.svg)](https://www.npmjs.com/package/example)
[![npm version](https://img.shields.io/npm/v/example.svg?style=flat-square)](https://www.npmjs.com/package/example)
[![npm version](https://img.shields.io/npm/v/example.svg?style=for-the-badge)](https://www.npmjs.com/package/example)
```

Add `logo=` with a [simple-icons](https://simpleicons.org/) slug, plus `logoColor=`, when the icon speeds recognition rather than merely decorating:

```markdown
[![Runtime: Tokio](https://img.shields.io/badge/runtime-Tokio-4c8eda.svg?style=for-the-badge&logo=rust&logoColor=white)](https://tokio.rs/)
```

## Maintenance status

When the evidence shows the project is dormant, archived, or in maintenance mode — a long-quiet commit history, an archive flag, or the user saying so — state it near the top of the README instead of leaving readers to infer it. A short note about what still works, what will not be fixed, and whether new maintainers are welcome protects the adoption decision better than silence. Never conclude a project is unmaintained from age alone: activity can live in branches, forks, or another repository of a monorepo, so treat dormancy as a fact to verify like any other.

## Anti-patterns

- A slogan with no use case.
- Architecture and technology details before installation and examples.
- Commands, environment variables, paths, or deployment steps that do not exist.
- A sentence written only so its section can exist — a License section that repeats what the LICENSE file and GitHub's sidebar already say, a contribution section with no real channel behind it.
- Installation steps that assume the reader already lives in the project's ecosystem: `make install` with no word about prerequisites, build tools, or supported platforms.
- A large badge wall used as a substitute for limitations, maintenance status, or evidence.
- Every API, design decision, and tutorial forced into the README until it loses focus.
- Internal protocol tables, data-structure dumps, or module walkthroughs in a README whose identified reader is an end user rather than a contributor.
- A copied list that can drift from the manifest or configuration without a verification mechanism.

## Sources

- [15 Essential Sections Every README Needs](https://codelove.tw/@tony/post/am2Gjq)
- [The Art of README — Traditional Chinese](https://github.com/hackergrrl/art-of-readme/blob/master/README-zh-TW.md)
- [standard-readme](https://github.com/RichardLitt/standard-readme) — contributing answers and i18n file naming
- [Make a README](https://www.makeareadme.com/) — maintenance-status disclosure
