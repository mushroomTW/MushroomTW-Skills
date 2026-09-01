# Library-First

**English** | [繁體中文](library-first.zh.md)

> This document lives in `docs/`. The skill itself is at [`library-first/SKILL.md`](../library-first/SKILL.md).

A skill that interrupts once before you hand-roll a general mechanism: spend one search evaluating existing solutions, then decide whether to write it yourself.

Every line of custom code is a liability — it has to be maintained, tested, documented, and made to handle edge cases nobody thought of. This skill does not demand that you always reach for a package; it demands that the decision be **stated out loud** rather than defaulting to writing your own.

## When It Applies

Before hand-rolling general mechanisms such as:

retry and backoff, validation, date/time handling, state management, authentication/authorization, caching, serialization, CLI argument parsing, cryptographic hashing.

It does **not** apply to domain-specific business logic — order discount rules, premium calculation, game rules. No package exists for these, and none should.

## Process

1. **Name the problem** — describe it in domain vocabulary, not in your own variable names. It is "exponential backoff retry", not "the logic in `callApiAgain`".
2. **Search the right ecosystem** — do not assume npm. Python has PyPI, C# has NuGet, Go has pkg.go.dev, Rust has crates.io. Check the standard library at the same time: many needs require no new dependency at all.
3. **Apply the quality gate** — a package that fails the gate does not count as an existing solution, and writing it yourself is then the right call.
4. **Decide and state the reason** — say explicitly "used X because Y" or "wrote it manually because Z". Do not make this decision silently.

## Quality Gate

To replace custom code, a package must meet **all** of these:

- **Actually exists**: the exact name resolves in that language's registry, and the version cited in the decision comes from that lookup. A name recalled from memory is a search term, not a package — plausible-looking names that resolve nowhere are what supply-chain attackers register against
- **Still maintained**: commits within the last 12 months; not marked deprecated or unmaintained
- **Reasonable dependency tree**: pulling in dozens of transitive dependencies for one small feature is usually a bad trade
- **License compatible**: no conflict with the project's license (GPL in a closed-source project is a hard stop)
- **Size proportional to the use case**: where frontend bundle size matters, a 200KB package replacing 20 lines does not add up
- **API surface not invasive**: adopting it should not require restructuring surrounding architecture

When unsure whether a package meets these, **look it up — do not guess**.

## Four Cases Where Writing It Yourself Is Correct

- **Domain-specific business logic**
- **Performance-critical path** — a general library's abstraction cost is unacceptable on a hot path, backed by actual measurement
- **Security-sensitive, needs full control** — every line must be auditable; opaque dependencies are unacceptable
- **Existing solutions evaluated and genuinely insufficient** — note: *evaluated*, not assumed insufficient

## Install

From the repository root, let the `skills` CLI discover supported agents and install this skill:

```bash
npx skills add . --skill library-first
```

Add `--global` for personal scope; without it, the CLI installs at project scope. For a manual installation, copy `library-first/` to a skills directory documented by the host instead of assuming a runtime-specific path.

> [!NOTE]
> The first `npx` invocation may download the CLI. Reload or restart the host when it only discovers skills at session start.
