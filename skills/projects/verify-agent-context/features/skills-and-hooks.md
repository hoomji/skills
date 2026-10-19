# Skills and hooks

Beyond its prompt and memory, an agent loads two trees it never reads aloud: the skills under
its provider sink (`.claude/skills/` for Claude, `.agents/skills/` for Codex, `.opencode/skills/`
for OpenCode) and the hook file gc renders for it (`.gc/settings.json` for Claude,
`.codex/hooks.json` for Codex) from the owner override `hooks/claude.json`. A skill with a bad
frontmatter never loads, a skill nothing triggers is dead weight, a script that does not compile
fails at the moment it is needed, and a hook block gc collapsed is a guard that silently stopped
firing. These three checks are the ones worth borrowing from harness-tree validators
(owner 2026-10-19: Harness² itself is not adopted; its tree checks are).

## Sub-features

- Skill frontmatter: present, valid YAML, `name` and `description` set, `name` equal to the
  directory or the directory is `<binding>.<name>` (a pack skill; gc namespaces it).
- Untriggered city-owned skill: a real directory (not a pack symlink) that no prompt template,
  memory index, memory body or `hooks/claude.json` names, whose description has no `when`
  clause, and that is not `disable-model-invocation: true`.
- Skill refs: rooted paths and `.py`/`.sh` names in a city-owned SKILL.md exist in the city, the
  gc docs corpus or the skill directory. Bare `plan.md`-style names are artifacts and are skipped.
- Skill scripts: every `.py` and `.sh` under any skill, pack symlinks followed, compiles. One
  pack skill linked from three sinks is compiled once.
- Hook shape: `hooks` is an object keyed by known event names; each block has a `hooks` list and
  a string `matcher`; each hook has a known `type` and a non-empty `command`, `prompt` or `url`.
- Duplicate matcher: two blocks with one matcher under one event in one file. gc merges hook
  arrays by matcher, so only one survives (see memory `hook-blocks-merge-by-matcher`).
- Hook scripts: every `.sh`/`.py` path a command names exists and compiles; `$HOME/` and `~/`
  resolve, any other `$VAR` path is skipped.
- Render drift: every `command` in `hooks/claude.json` appears under the same event in
  `.gc/settings.json`. Skipped when either file is absent.

## How to get to it (user POV)

The agent wakes. Claude Code reads `.gc/settings.json` and lists `.claude/skills/*/SKILL.md`
descriptions into context; Codex reads `.codex/hooks.json` and `.agents/skills/`. A skill is
invoked when the model matches its description, when a prompt names it, or when the user types
`/<name>`. A hook fires on its event; a dropped hook fires nowhere, with no error.

## Driving it with context.py

- `context.py skills` prints one line per finding or `skills: clean`; exit 1 on any.
- `context.py hooks` likewise; `hooks: clean` on exit 0.
- `context.py doctor` includes both.
- `python3 .claude/skills/verify-agent-context/scripts/test_context.py` runs the unit tier over
  a scratch city: 19 cases, each paired with a shape that must produce the finding.
- To prove a finding fires on the live city without editing it, copy a hook file to a scratch
  dir and break it there; the checks take `--city <dir>` and need only `city.toml` to exist for
  `doctor` (not for `skills` or `hooks`).

## Gotchas

- `gc start` regenerates `.gc/settings.json` and `.codex/hooks.json`. A finding against those
  files is drift in the render, so the fix goes in `hooks/claude.json`, then `gc start` or a
  session restart, then the check again.
- Pack skills (symlinks into `~/.gc/cache/repos/...`) are checked for frontmatter and scripts
  only; their triggers and refs are the pack's, and a finding there is for the pack author.
- The trigger rule reads `when` in the description because Claude Code auto-invokes on the
  description; a skill whose only trigger is a prompt line is one prompt edit from dead.
- `.sh` checks are `bash -n`: a script with a bad sourced file or a runtime error passes.
- `HOOK_EVENTS` is a fixed set. A new Claude Code event lands as a false `is not a hook event`
  until the set is extended; the list is in `scripts/context.py`.
