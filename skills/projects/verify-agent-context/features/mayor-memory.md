# Mayor memory

The mayor's memory (`.claude-memory/`, a symlink to the mayor's Claude Code project memory)
is one fact per file with a `MEMORY.md` index the mayor reads every wake. Seats read copies
of chosen files, listed in `agents/<seat>/memory/seeded.txt`. The contract is
`memory-earns-its-line.md` in that dir.

## Sub-features

- `mem-index` MEMORY.md lists every file and only existing files.
- `mem-links` every `[[link]]` and every plain name after `See`/`Related:` resolves.
- `mem-frontmatter` every file's frontmatter parses with a name and description.
- `mem-live` every bead, PR, path, script, flag, pool and provider a memory names still exists and still behaves as stated.
- `mem-seats` seat copies match their mayor source.

## How to get to it (user POV)

- Claude Code loads MEMORY.md into the mayor's context every session, and the mayor prompt's
  "Every wake" step tells it to read the index on either provider.
- Seats read `agents/<seat>/memory/MEMORY.md` on wake (Seat contract).
- `orders/board-memory-prune.toml` wakes the mayor on its schedule to prune memory with the
  gc-board-and-memory-prune skill.

## Driving it with context.py

Preconditions:

- Doctor ran this pass.

- **Index, links, frontmatter.** Run `context.py memory`. Output is `memory: clean`; findings
  read `memory: <file> not in MEMORY.md`, `… links missing [[x]]`, `… names missing memory x
  (plain text)` or `… frontmatter is invalid YAML (…)`.
- **Live facts.** Run `context.py refs --also ~/projects/Gateway-LLM .claude-memory/*.md`;
  a `MISS` on a bare product file name (`renderedness-corpus.test.ts`) is checked with
  `git -C ~/projects/Gateway-LLM ls-files | grep <name>`. Then, per file, check every bead
  (`gc bd show <id> --json`), PR (`gh pr view`), flag (read the script) and config key
  (`grep city.toml`) it names. Grade KEEP, REWRITE (the lesson stands, a named thing changed)
  or DELETE (trigger retired, or a doc, config comment or `--help` now holds the fact).
- **Seats.** Run `python3 dispatch/seat_memory_sync.py check`. Output is `seat memory in step`;
  findings read `<seat>: copy|retired <file>` or `<seat>: MEMORY.md index`, and `sync` fixes them.

## Gotchas

- Other sessions edit this dir live (the mayor itself). Re-read a file before changing it and
  merge, never revert; a fresh mayor edit makes the seat copies stale until `sync` runs.
- A memory that restates a doc or `--help` is a cache; DELETE it when the source holds the fact.
- `city/docs/...` in old memories means repo-root `docs/...`; no `city/docs` dir exists.
