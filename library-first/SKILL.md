---
name: library-first
description: Use before hand-rolling a general mechanism such as retry, backoff, validation, date/time handling, state management, authentication/authorization, caching, serialization, CLI argument parsing, or cryptographic hashing, to evaluate existing library solutions before deciding to write it yourself. Does not apply to domain-specific business logic.
---

# Library-First

> Search before hand-writing a general mechanism; every line of custom code is a liability.

## Invariants

1. Emit exactly one terminal decision: `used`, `wrote manually`, or `deferred`. Use `deferred` only when a missing project fact makes a gate undecidable, and state both that nothing is to be implemented yet and the evidence that would unblock it.
2. A third-party package that fails the Quality Gate does not exist; judge a standard library by fitness and version support instead.
3. Verify what you are unsure of; never guess.

## Workflow

| Step | Action | Input | Output | Format |
|------|--------|-------|--------|--------|
| 1 | Name and route | requirement, variable names | domain term + `search`/`manual` | e.g. `exponential backoff retry`, not `callApiAgain`; domain logic or a genuine three-line helper routes to `manual` |
| 2 | Search the ecosystem | `search` domain term + language | 1-3 candidates | cover the standard library + npm/PyPI/NuGet/pkg.go.dev/crates.io; `manual` skips to Step 4 |
| 3 | Evaluate candidates | candidates | `Pass`/`Fail`/`Unknown`/`N/A` | apply the Quality Gate to third-party packages; confirm fitness and version support for a standard library |
| 4 | Terminal decision | evaluation results | `used`/`wrote manually`/`deferred` | exactly one; see the templates |

🔴 CHECKPOINT 1 · 🛑 STOP — pause after Step 2 on the `search` path: confirm the standard library was covered, mainstream packages were covered, and the query used a domain term rather than a variable name. The `manual` path never fakes a search; it goes straight to Step 4.

### Quality Gate (a third-party package is adopted only when all six pass)

Record each gate as `Pass`, `Fail`, `Unknown`, or `N/A`. `Unknown` is not a pass; `N/A` must state why the gate does not apply to this project. All `Pass`/`N/A` allows `used`; any `Fail` moves to the next candidate, and only after every candidate fails do you `wrote manually`; when `Unknown` is all that remains you must `deferred`, never a conditional sentence pretending the package was adopted.

| # | Check | Condition | Otherwise |
|---|------|------|--------|
| 0 | Identity | the exact name resolves in that language's registry, and the resolved version is what `<ver>` reports | the name does not resolve — it was recalled, not found; discard it and never adopt it |
| 1 | Maintenance | a commit within 12 months, not deprecated | exclude |
| 2 | Dependency tree | does not pull dozens of dependencies for a small feature | exclude |
| 3 | License | compatible with the project (closed source + GPL is a hard stop) | exclude |
| 4 | Size | only where frontend bundle size matters: 200KB to replace 20 lines does not pay | exclude |
| 5 | API | needs no refactor of surrounding code | exclude |

> Gate 0 evidence is the registry's own resolution output (`npm view <pkg> version`, `pip index versions <pkg>`) or the package's registry page. A name you recalled is a search term, never evidence that the package exists — a plausible-looking name that no registry resolves is the failure mode attackers register against.

> Unsure → read the repo, the registry entry, and the LICENSE file.

> A standard library adds no dependency, so the registry-identity, maintenance-commit, dependency-tree, and bundle-size thresholds do not apply; confirm instead that the target version ships it, the license is compatible, and the API fits.

### Decision templates

```
Decision: used <pkg>@<ver> because gate 0-5 pass, <reason>.
Decision: used standard library <API> because target version <ver> supports it and API fits.
Decision: wrote manually because domain-specific business logic.
Decision: wrote manually because performance-critical, measured <library> <metric> at <value> against budget <threshold>, so overhead is unacceptable.
Decision: wrote manually because security-sensitive, full auditability is required and opaque dependencies are unacceptable.
Decision: wrote manually because evaluated <pkg> failed gate #<n>.
Decision: wrote manually because no suitable candidate exists after checking <sources>.
Decision: wrote manually because this is a one-off three-line helper with no edge cases, state, or growth.
Decision: deferred because gate #<n> depends on <missing project fact>; immediate action: do not implement until <evidence> is confirmed.
```

## The four cases that are hand-written

Domain logic (discounts, premiums, game rules), performance-critical code (with measurements), security-sensitive code (full auditability required), and evaluated-and-insufficient candidates (*evaluated*, not assumed).

## Do not hand-write these

| Need | Do not write your own |
|---|---|
| Retry / circuit breaker | `cockatiel` (TS), `Polly` (C#), `tenacity` (Py) |
| Auth | Auth0, Supabase, Keycloak, ASP.NET Identity |
| Frontend state | Zustand, Redux, Jotai |
| Schema validation | Zod, Pydantic, FluentValidation |
| Date/time | `date-fns`, Temporal, NodaTime |
| Cache / serialization / CLI / hashing | search the ecosystem's mainstream solution first |

> The names above are recalled search starting points, not adoptable identities: each still passes Gate 0 before it may appear in a decision.

> Three-line-helper exception: a three-line helper used once, with no edge cases or state, that will not grow, may be written by hand.

🔴 CHECKPOINT 2 — self-check before submitting Step 4: exactly one terminal state among `used`/`wrote manually`/`deferred`; the decision sentence contains because; it matches the evaluation result or the hand-writing reason; a `deferred` spells out `do not implement` and the evidence needed; no hedging (never "could consider", "depends on the situation", "use judgement" — it is pass or fail).

## Failure Handling

| Trigger | First-line fix | Fallback if that also fails |
|---|---|---|
| No candidate found | re-search with a different domain term + check the standard library | write it by hand, recording the sources checked and "no suitable candidate" |
| The registry does not resolve a candidate's name | drop that name and re-search with the domain term; a recalled name is never adopted on its own authority | nothing resolves → write it by hand, recording the names checked and that none exist |
| Any gate fails | move to the next-best candidate | all fail → write it by hand and record the failing gate # |
| A package's license identity is unclear | read the package LICENSE and the registry field | still unconfirmable → `Fail`, exclude that candidate |
| Project version, license policy, or integration constraints are missing | read the manifest, lockfile, LICENSE, and existing dependencies | still missing → `deferred`, and ask one precise answerable question |
| Too many candidates | filter by gate down to 1-3 for a deep look | list the exclusion reasons in the decision sentence |
| Edge cases explode after hand-writing | rerun Steps 2-3 to evaluate a replacement | wrap it as an internal module rather than letting it swell inside business code |

## Never Do

1. Search by variable name — `callApiAgain` will never find `exponential backoff`.
2. Adopt on fame — a high-star package that fails a gate is still excluded.

## Examples

| Scenario | Step 1 naming | Step 2 candidates | Gate result | Decision |
|---|---|---|---|---|
| Exponential backoff retry (Node) | `exponential backoff retry` | `cockatiel`/`p-retry` + standard library | `cockatiel` 0-5 pass | `Decision: used cockatiel@<ver> because gate 0-5 pass, non-invasive API and light dependencies` |
| Discount of 100 on orders over 1000 | `order discount rule (domain)` | not applicable (business rule) | no search needed | `Decision: wrote manually because domain-specific business logic` |
