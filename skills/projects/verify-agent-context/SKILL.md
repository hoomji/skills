---
name: verify-agent-context
description: Verify a Gas City's agent context — the mayor and delegated-seat prompts, the seats' memory copies and the mayor's memory — against the live city, by rendering what each agent loads on wake and checking every path, script and memory link it names. Use when proving a prompt or memory edit, when an agent acts on a stale fact, or when /maintain-verification-skill audits this map.
---

# Verify agent context

The "app" is the context five agents load when they wake: the mayor (`agents/mayor/`) and the
four delegated seats (`ci-controller`, `fleet-watcher`, `receipt-grader`, `backlog-curator`),
each a prompt template plus a memory index, and the mayor's memory dir (`.claude-memory/`).
A user of this context is the agent: what it reads on wake, and whether every fact it reads
still holds in the city. Drift is a prompt or memory that names a path, script, flag, order or
policy the city no longer has.

Harness: `.claude/skills/verify-agent-context/scripts/context.py` (read-only; `--help` lists
subcommands). Run it from the city root (`~/city`) or pass `--city`. It needs `gc` on PATH and
PyYAML. Feature map: [`features/README.md`](features/README.md).

## Launch

Nothing starts. The instance is the live city on Ryzen: `cd ~/city && gc status` answers, and
`gc session list` shows the `mayor` session active. Pick a run id and evidence dir:
`RUN=$(date -u +%Y%m%dT%H%M%SZ); EV=~/.local/state/verify-agent-context/$RUN; mkdir -p $EV`.
Ready when `gc status` exits 0.

## Doctor

`.claude/skills/verify-agent-context/scripts/context.py doctor` — one line per finding, exit 1
on any, `doctor: clean` and exit 0 otherwise. It checks: `gc status`; `gc prime --strict <agent>`
renders for all five agents; every backticked repo path in each prompt and in
`docs/delegated-seats.md` exists (bare script names resolve under `dispatch/`,
`orders/scripts/`, `docs/`, `agents/*/`; `docs/...` also resolves in the gc docs corpus at
`~/.cache/gascity-docs/`); `dispatch/seat_memory_sync.py check` is in step; the mayor's
MEMORY.md lists exactly the files on disk, every `[[link]]` and every plain name after
`See`/`Related:` resolves to a memory, doc or skill, and every frontmatter parses as YAML with
a name and description. Finding lines: `<agent>: prompt names missing <path>`,
`seat-memory: <seat>: copy|retired <file>`, `memory: <file> …`. Run it first, and again after any edit you prove.

## Drive

Each feature file pairs an agent's wake path with commands. The drives are read-only:

- `context.py render <agent> $EV` writes what the agent loads: the prompt (`gc prime --strict`,
  budget line on stderr), its memory index, and for a seat the wake text (`agent.toml` nudge
  plus `formulas/<seat>-pass.toml`).
- `context.py refs [--also <repo>] <file>` prints `ok`/`MISS` for each backticked path; `<x>`
  placeholders match by glob, and `--also ~/projects/Gateway-LLM` resolves product-repo paths.
- `context.py memory` and `context.py seat-memory <seat>` check the mayor's memory and one
  seat's copies.
- `context.py last-pass <seat>` prints the seat's newest closed pass and `prompt_newer`: true
  means its prompt, nudge or formula changed after that pass, so the pass cannot prove the
  current context.
- `context.py primed <agent>` prints whether the live session primed after the last context
  commit (`on_current_context`).
- `gc session peek <session> --lines 60` or `tmux -L city capture-pane -pt <session>` shows a pane.

Flags and subcommands a prompt names are checked by reading the script: argparse `choices=`
for Python, the usage header and `case` arms for shell. Several city scripts act when given
an unknown argument (`land.sh --help` runs its gates against `--help`; a bare `route.sh` runs
`backlog`), so read them instead of running them.

Never fire a seat's pass order, nudge a seat or send mail to drive a feature: a pass acts on
the fleet. The last real pass is the live evidence.

## Evidence

Under `$EV`: `<agent>.prompt.md` and `<agent>.memory.md` from `render`, `doctor.txt`
(`context.py doctor > $EV/doctor.txt`), `<seat>.last-pass.json`, and a `notes.md` naming each
feature, the command run and the finding. A proof is the rendered context plus a command
output showing the named thing exists (or not) in the live city — never a recollection of
what the prompt used to say. A seat feature is proven when its last pass has
`prompt_newer: false` and its `close_reason` describes steps the current prompt asks for;
with `prompt_newer: true` record it as `awaiting a post-change pass`, not verified.

## Cleanup

Nothing to tear down: no process, session or store write is created. Remove only your own
scratch outside `$EV`. `$EV` stays; confirm with `ls $EV` after you finish.
