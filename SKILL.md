---
name: library-first
description: Use before hand-rolling a general mechanism such as retry, backoff, validation, date/time handling, state management, authentication/authorization, caching, serialization, CLI argument parsing, or cryptographic hashing, to evaluate existing library solutions before deciding to write it yourself. Does not apply to domain-specific business logic.
---

# Library-First

When about to write code for a problem someone else has certainly already solved, spend one search to evaluate existing solutions first.
Every line of custom code is a liability: it must be maintained, tested, documented, and made to handle edge cases nobody thought of.

## Process

1. **Name the problem** — describe it in domain vocabulary, not in your own variable names.
   Example: "exponential backoff retry", not "the logic in callApiAgain".
2. **Search the ecosystem for that language** — do not assume npm. Python has PyPI, C# has NuGet, Go has pkg.go.dev, Rust has crates.io.
   Check the standard library at the same time: many needs (Python's `functools` and `datetime`, C#'s built-in `HttpClient` resilience handlers) require no new dependency at all.
3. **Apply the quality gate** (below) — a package that fails the gate does not count as an existing solution; writing it yourself is better.
4. **Decide and state the reason** — say explicitly "used X because Y" or "wrote it manually because Z". Do not make this decision silently.

## Quality gate

To replace custom code, a package must meet all of these:

- **Still maintained**: commits within the last 12 months; not marked deprecated or unmaintained
- **Reasonable dependency tree**: pulling in dozens of transitive dependencies for one small feature is usually a bad trade
- **License compatible**: confirm no conflict with the project's license (GPL in a closed-source project is a hard stop)
- **Size proportional to the use case**: when frontend bundle size matters, a 200KB package replacing 20 lines does not add up
- **API surface not invasive**: adopting it should not require restructuring surrounding architecture

When unsure whether a package meets these, **look it up — do not guess**.

## Four cases where writing it yourself is correct

- **Domain-specific business logic** — order discount rules, premium calculation, game rules. No package exists for these, and none should.
- **Performance-critical path** — a general library's abstraction cost is unacceptable on a hot path, backed by actual measurement.
- **Security-sensitive, needs full control** — every line must be auditable; opaque dependencies are unacceptable.
- **Existing solutions evaluated and genuinely insufficient** — note: *evaluated*, not assumed insufficient.

## Do not hand-roll these

Mature solutions exist in every language:

| Need | Do not write your own |
|---|---|
| Retry / circuit breaker | `cockatiel` (TS), `Polly` (C#), `tenacity` (Py) |
| Authentication / authorization | Auth0, Supabase, Keycloak, ASP.NET Identity |
| Frontend state management | Zustand, Redux, Jotai |
| Schema validation | Zod, Pydantic, FluentValidation |
| Date / time | `date-fns`, Temporal, NodaTime |

Conversely, **a three-line helper used once does not need a package**. This rule targets mechanisms that have edge cases, carry state, and will grow — not every helper function.
