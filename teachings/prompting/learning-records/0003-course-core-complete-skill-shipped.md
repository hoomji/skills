# Course core complete; `sharpen` shipped with effort + ultracode logic

Lessons 6–8 are built: **Max effort** (the effort dial / overthinking trap), **ultracode**
(depth→breadth, workflows + adversarial verification), and **Iterating like an engineer**
(evals + the one-variable debug loop — the capstone that makes 1–7 compound). Lessons 6–8 were
themselves produced with ultracode workflows (parallel draft → adversarial fact/quiz/pedagogy
verify → revise), which is the pattern Lesson 7 teaches.

The course now spans: the five prompt-craft moves (L1–4), model selection (L5), the compute
axis — depth vs breadth (L6–7), and the iteration meta-skill (L8). The [[prompting-cheat-sheet]]
covers all of it.

The `sharpen` skill is now the applied capstone and lives in git, not just `~/.claude`:
- Canonical home: `github.com/hoomji/skills` → `sharpen/`, pushed to `main` (commit 1463bc4).
- Extended with **effort-tuning** (sweep, max trap, define-done, latency-is-separate) and an
  **ultracode-escalation** decision (comprehensiveness / confidence / scale; opt-in + costly).
- Synced into `~/.claude/skills/` and `~/.agents/skills/` as symlinks via `install.sh` (no longer
  a standalone copy).
- Henry further refined it himself: the model decision now precedes the rewrite, and per-model
  prompt-adaptation refs (`FABLE_5.md`, `OPUS_4_8.md`) were added — evidence he's now actively
  authoring, not just receiving.

Open next (optional): a `Structured output` appendix, or building a real eval set for `sharpen`
using the L8 loop. See [[MISSION.md]].
