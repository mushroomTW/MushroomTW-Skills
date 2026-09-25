---
name: ponytail-audit-lite
disable-model-invocation: true
description: Manually run a whole-repository simplification audit and produce a one-shot report.
---

Repo-wide. Scan the whole tree instead of a diff. Rank
findings biggest cut first. Skip generated, vendored, and dependency
directories (`node_modules/`, `vendor/`, build output) and anything
`.gitignore` excludes.

## Tags

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

## Hunt

Deps the stdlib or platform already ships, single-implementation interfaces,
factories with one product, wrappers that only delegate, files exporting one
thing, dead flags and config, hand-rolled stdlib.

Before tagging anything `delete:` or `yagni:`, search the whole tree for
references, including string names, config, and build files. Code reached by
reflection, dependency injection, framework conventions, an entry point, or a
published library's public API is not dead: leave it out.

## Output

A Markdown table, one row per finding, ranked biggest cut first:

```md
| # | Tag | Cut | Replacement | Path |
|---|-----|-----|-------------|------|
| 1 | `yagni:` | <what to cut> | <replacement> | `<path>` |
```

Escape `|` inside cells as `\|`. Keep every cell to one line: a `shrink:` row
says `shorter form in #<n>` in Replacement, and the shorter form goes below the
table as a fenced code block headed `#<n>`. Past 20 findings, keep the 20
biggest and say how many were left out. Then end with
`net: -<N> lines, -<M> deps possible.` N is the sum of the lines every finding
removes, the ones left out of the table included, counted from the files, not
guessed; M counts the dependencies they remove. Nothing to cut: no table, just `Lean already. Ship.`

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security holes,
and performance are explicitly out of scope. Route them to a normal review
pass. Lists findings, applies nothing. One-shot.
