# Learnings

`LEARNINGS.md` is for durable engineering wisdom that should survive refactors. Use the scope ladder when deciding where a new insight should live:

- Repo-wide and durable: put it in `LEARNINGS.md`.
- App-specific architecture/policy: put it in `ARCHITECTURE.md`.
- Symbol-local contract: put it in code docblocks near the symbol.
- Naming/API smell: prefer renaming or reshaping the API over adding prose.
- Quick test: if it remains true after renaming modules and shipping new features, it likely belongs in `LEARNINGS.md`; if it depends on current product behavior, it belongs in architecture docs.

## Engineering Discipline

- Every warning is harmful. Warnings indicate mismatch between intent and reality; either fix immediately or stop and design a clean fix.
- Don't guess; inspect first. Confirm reality from code/runtime state before recommending changes.
- Derive contracts from essential data flow. Identify the minimum data required for correct output; remove extra inputs and document staleness/invariant implications.
- Recover intent before deleting code. Assume dead-looking code had a purpose; verify whether that purpose is now met elsewhere before removal.
- Generalize local cleanups into pattern audits. A good fix in one site is a signal to scan similar call paths for consistency and quality.
- Fix prerequisites cleanly. If goal X requires Y first, solve Y properly rather than layering hacks.
- Don't defer quality fixes. Bugs, races, and invariant leaks are cheapest to fix immediately.
- Debug tools must be single-purpose. A diagnostic control should expose bugs, not compensate for them.
- Treat design-doc silence as "no." Do not invent unspecified behavior; document any new behavior explicitly.
- Look for existing code first. If adding something, reuse existing code or cleanly refactor existing code when appropriate.
- Be willing to refactor when it materially improves code health.

## Architecture And Refactorability

- Bias toward purity from the first implementation. Pure input-to-output logic is easier to move, test, and recombine than mixed logic/effects.
- Separate decision logic from effects early. Keep computation in pure helpers/reducers; keep I/O, storage, UI, and network writes in thin orchestration layers.
- Design modules around effect boundaries. A module should either decide what should happen or perform side effects, not both.
- Treat modularity as a maintenance multiplier, not a cleanup pass.

## TypeScript And Testability

- Derive flags from existing data instead of threading redundant booleans through call chains.
- Write optional-chain conditions in forms TypeScript can narrow correctly.
- Test async engines with state-change callbacks, not arbitrary sleeps.
- DI test stubs for expected side effects should sink calls, not throw.
- Test-only dependency/global overrides must be explicitly named and idempotent.

## Testing Practice

- Avoid readiness checks that wait on background traffic to go idle.
- Run short timeout-based probes before full suites.
- Inspect test logs incrementally during long runs.
