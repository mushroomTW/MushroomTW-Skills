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
