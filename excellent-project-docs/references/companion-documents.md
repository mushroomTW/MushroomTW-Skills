# Companion Documents

The README is the hub. Each file below is a satellite: one topic, one reader, one file, linked from the README and linking back. Read this before step 3 to decide which satellites the evidence justifies, and again in step 4 for the minimum content of each one you write.

## Where GitHub looks

GitHub resolves community health files from three locations, with this precedence when the same file exists in more than one: `.github/`, then the repository root, then `docs/`. `CODE_OF_CONDUCT`, `CONTRIBUTING`, `GOVERNANCE`, `SECURITY`, `SUPPORT`, and issue and pull request templates are recognized this way and surface in the repository's community profile, the new-issue and new-pull-request flows, and the Security tab; `FUNDING.yml` is read from `.github/` only. `CHANGELOG`, `ARCHITECTURE`, and `ROADMAP` are conventions readers expect at the root, not files GitHub processes.

Keep an existing file where it is. For a new file prefer the root, or `.github/` when the repository already keeps its community files there. A file that lives in an unrecognized place (for example `doc/`, `.github/docs/`) is a finding to report, not silently move.

## Candidate files

| File | Reader | Create or keep it when | Minimum content | Only the user can answer |
| --- | --- | --- | --- | --- |
| `CONTRIBUTING.md` | Would-be contributor | Contributions are accepted from outside the maintainers: an existing file, a public issue tracker with external PRs merged, a `good first issue` label, or the user says so | How to set up a development environment, run the tests, and submit a change; what a PR must include; where to ask before starting | Whether external PRs are wanted at all; review expectations; DCO or CLA requirements |
| `CODE_OF_CONDUCT.md` | Contributor, participant | A community exists: external contributors, a discussion forum, or a chat channel. A one-maintainer repository does not need one | The standard adopted (for example Contributor Covenant, cited by version), the scope, and the enforcement contact | Which standard, and who receives reports |
| `SECURITY.md` | Vulnerability reporter | Anything is deployed, published to a registry, or handles user data or credentials | How to report privately (GitHub private vulnerability reporting, a security address), which versions receive fixes, and the expected response window | The contact, the supported versions, and the response commitment |
| `SUPPORT.md` | User with a question | The README's contribution section would otherwise mix "how to ask" with "how to contribute", or issues are not the support channel | Where to ask (discussions, chat, mailing list) and what belongs in an issue instead | The channel |
| `CHANGELOG.md` | Upgrader, integrator | The project publishes versions: tags, releases, or a registry version, and does not already generate release notes elsewhere | One entry per released version, newest first, dated, grouped by change type, with an `Unreleased` section; every entry traceable to a tag or commit range | Nothing, if history and tags exist; the file must not be reconstructed from memory |
| `ARCHITECTURE.md` | New contributor, reviewer | The code spans several components, services, or crates, and a newcomer cannot see the shape from the directory tree alone | A bird's-eye map: the main modules, their responsibilities, the data or control flow between them, and the boundaries or invariants a change must respect. Point at code by module name, not by line number | Design rationale that neither code nor history records |
| `ROADMAP.md` | Adopter deciding on timing | A confirmed public roadmap exists: milestones, a project board, or the user supplies one | Direction and rough ordering; no dates or commitments the evidence does not contain | Everything — a roadmap is a maintainer statement, never inferred |
| `GOVERNANCE.md` | Contributor, downstream | More than one maintainer organization, a foundation, or a formal decision process exists | Who decides what, how maintainers are added or removed, and how disputes are settled | The whole content |
| `.github/ISSUE_TEMPLATE/*.md` or `.yml`, `config.yml` | Issue reporter | Issues are open and the maintainers want specific information (reproduction, environment, logs) | One template per issue type actually triaged; each field maps to something the maintainers use | Which issue types and which fields |
| `.github/PULL_REQUEST_TEMPLATE.md` | Contributor | External PRs are accepted and a checklist would shorten review | The checks a reviewer will apply, mirroring `CONTRIBUTING.md` rather than restating it | Review expectations |
| `.github/FUNDING.yml` | Sponsor | The user names a funding platform | Only platforms the user confirmed | The platforms and handles |

`LICENSE` is not a document this skill writes. Choosing a license is the user's decision; the skill states its presence, absence, or mismatch as a fact. It is also the sole owner of the license: the README does not restate it (see [readme-framework](readme-framework.md)).

## Hub-and-satellite rules

- **One owner per fact.** The README summarizes a satellite in one or two lines and links to it; the satellite does not restate the README's quick start, feature list, or license. When a fact appears in both, delete it from one and link.
- **Both directions.** The README links to every satellite it justified; every satellite opens with, or ends with, a relative link back to the README so a reader who lands on it from GitHub's UI can orient.
- **Same evidence bar.** A command in `CONTRIBUTING.md` needs the same manifest, script, or CI trace as a command in the README. A version in `CHANGELOG.md` needs a tag. A component in `ARCHITECTURE.md` needs a directory or module that exists.
- **Same language set.** A satellite gets a translated variant only when the README already has one in that language and the user wants it; otherwise report the asymmetry.
- **Template files are configuration.** Issue and PR templates are read by GitHub, not by people browsing the repository, so keep them short, keep the front matter valid, and do not copy prose from `CONTRIBUTING.md` into them.

## Anti-patterns

- A `CONTRIBUTING.md` copied from another project, describing a workflow this repository does not run.
- A `SECURITY.md` that says "please report responsibly" with no address, form, or version table.
- A `CODE_OF_CONDUCT.md` that adopts a standard but names no enforcement contact.
- A `CHANGELOG.md` written from memory, or one that duplicates GitHub Releases without saying which is canonical.
- An `ARCHITECTURE.md` that walks every file in order instead of drawing the map a newcomer needs.
- A `ROADMAP.md` whose milestones exist nowhere else.
- An empty `.github/ISSUE_TEMPLATE/` directory, or a template with fields nobody reads.
- A satellite that exists but that the README never mentions.

## Sources

- [Creating a default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) — the recognized files and lookup order
- [Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) — `CONTRIBUTING`
- [Adding a security policy to your repository](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository) — `SECURITY`
- [About issue and pull request templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) — `CHANGELOG` entry shape
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) — what a bird's-eye architecture document is for
