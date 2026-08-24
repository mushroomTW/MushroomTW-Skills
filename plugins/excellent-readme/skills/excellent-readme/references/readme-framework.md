# README Design Framework

This framework combines CodeLove's “15 Essential Sections Every README Needs” with hackergrrl's “The Art of README.” Together they support three decisions: treat the README as an entry point, move from broad understanding to concrete usage, and make examples, installation, and limitations more important than decoration.

## The cognitive funnel

Order information around the reader's adoption decision:

1. **Identify**: title, one-line description, use case, and necessary context.
2. **Evaluate**: minimal usage example, main features, compatibility, limitations, and license.
3. **Try**: installation, prerequisites, configuration, startup, and expected output.
4. **Integrate**: API or CLI reference, tech stack, architecture, and project structure.
5. **Participate**: security, contribution, roadmap, acknowledgements, and author information.

Content near the top should be short, concrete, and easy to evaluate. Put deeper background and maintenance information lower down. If a section does not help the target reader make a decision or complete a task, move it to a separate document, link to it, or omit it.

## Fifteen candidate sections

| Section | Keep it when | Minimum content |
| --- | --- | --- |
| Title and introduction | Always | One sentence explaining what the project does and who it helps |
| Table of contents | The README is long | Working anchor links; do not list empty sections |
| About | There is meaningful context or a use case | Problem, purpose, and scope |
| Features | There are multiple user-facing capabilities | Outcomes rather than internal implementation |
| Tech Stack | Technology choices affect use or contribution | The main technologies actually used |
| Architecture | The system spans multiple components | Components and data or control flow; add a diagram when useful |
| Project Structure | Contributors need repository orientation | The purpose of important directories and files |
| Getting Started | Almost always | The path from installation to first successful result |
| Configuration | There are environment variables, config files, or external services | Name, purpose, requiredness, default, and secret-handling rules |
| Security | There are credentials, user data, networks, or deployment risks | Security boundaries, prohibited practices, and reporting path |
| API or CLI | It is a library, SDK, or CLI | Copyable calls or commands and their output |
| How to Contribute | External contributions are welcome | Development, testing, submission, and conduct entry points |
| What's Next | There is a confirmed public roadmap | Short-term direction without invented commitments |
| License | The repository contains license information | License type and link to the license file |
| Acknowledgements / Author | It helps readers use or trust the project | Confirmed credits and contact information |

These are candidate sections, not a completeness score. A short, accurate README is better than a long README full of filler.

## Usage-example rules

- Lead with the smallest complete, copyable success case.
- For a CLI, show both the command and representative output.
- For an API, show the input, call, and return value; document optional parameters, defaults, and types.
- If an example needs extra files, keep an executable example in the repository and link to it.
- Do not make critical information available only through a screenshot, animation, badge, or external video.

## Badge rules

A badge is a compact status line, not decoration. Add one only when it answers a question the reader would otherwise have to open another file to answer.

Choose the badge type in this order:

1. **Dynamic**: the value is fetched when the page renders, so it cannot drift. Prefer this for package versions, build or coverage status, and the latest release.
2. **Static with a recorded source**: use only when no dynamic endpoint exists. Record the origin beside the badge so a later synchronize pass can verify the value.
3. **Static without a note**: acceptable only for values that cannot drift, such as a stack label that names a dependency rather than its version.

A static value and its recorded source look like this:

```markdown
<!-- badge source: rust-toolchain.toml (channel) -->
[![Rust 1.97.1](https://img.shields.io/badge/Rust-1.97.1-000000.svg)](https://www.rust-lang.org/)
```

Apply these rules to every badge:

- Link it to something the reader can verify: the license file, the registry page, the CI run, or the project's own documentation.
- Write alt text that carries the same fact as the image, because the image may fail to load. `[![License: MIT]` works; `[![badge]` does not.
- Add a license badge only when a LICENSE file exists and its type matches.
- Keep the set small enough to read at a glance; each extra badge lowers the value of the others.

### Choosing a style

Shields.io accepts `flat` (the default), `flat-square`, `plastic`, `for-the-badge`, and `social`. Pick one and apply it to every badge in the file; a mixed set reads as a collage rather than a status line.

| Style | Renders as | Reach for it when |
| --- | --- | --- |
| `flat` | Small, rounded, muted | The default. Several badges that should stay secondary to the title. |
| `flat-square` | Small, sharp corners | Same density as `flat`, matching a squared-off visual identity. |
| `for-the-badge` | Large, uppercase, wide | Two to four badges used as a deliberate header block. |
| `plastic` | Small with a gradient | The project's existing assets already use that older style. |
| `social` | GitHub-button styling | Star, fork, follow, or watch counts specifically. |

The same badge in three styles, so the difference is visible before choosing:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
```

Add `logo=` with a [simple-icons](https://simpleicons.org/) slug, plus `logoColor=`, when the icon speeds recognition rather than merely decorating:

```markdown
[![Runtime: Tokio](https://img.shields.io/badge/runtime-Tokio-4c8eda.svg?style=for-the-badge&logo=rust&logoColor=white)](https://tokio.rs/)
```

## Anti-patterns

- A slogan with no use case.
- Architecture and technology details before installation and examples.
- Commands, environment variables, paths, or deployment steps that do not exist.
- A large badge wall used as a substitute for limitations, maintenance status, or evidence.
- Every API, design decision, and tutorial forced into the README until it loses focus.
- A copied list that can drift from the manifest or configuration without a verification mechanism.

## Sources

- [15 Essential Sections Every README Needs](https://codelove.tw/@tony/post/am2Gjq)
- [The Art of README — Traditional Chinese](https://github.com/hackergrrl/art-of-readme/blob/master/README-zh-TW.md)
