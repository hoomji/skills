# v1 — already-sharp handling

- **Skill version:** `d7c2d70` + already-sharp edits to Steps 1 & 4 (uncommitted intermediate;
  later folded into `a527096`)
- **Variable changed vs v0:** Step 1 marks a satisfied move as **present** (a finding, not a
  gap); Step 4 returns an already-sharp prompt unchanged with a one-line note.
- **Runs/case:** 3
- **Judge:** LLM-as-judge, D1–D5 rubric + per-case checks
- **Provenance:** summary matrix carried over from an earlier session. Per-run D1–D5 detail
  was not retained; only the pass counts + notes below are real. Not reconstructed.

## Matrix (v0 → v1)

| Case | v0 | v1 | Note |
|------|----|----|------|
| C1 | 3/3 | pass | stable |
| C2 | 3/3 | pass | stable |
| C3 | 3/3 | pass | stable |
| C4 | 1/3 | 2/3 | flipped up — nothing changed here (noise) |
| C5 | 2/3 | 3/3 | flipped up — nothing changed here (noise) |
| C6 | 3/3 | pass | stable |
| C7 | 0/3 | **0/3** | **fix target — v1 did NOT move it** |
| C8 | 3/3 | pass | stable |
| C9 | 1/3 | 3/3 | flipped up — nothing changed here (noise) |
| C10 | 3/3 | pass | stable |

**Case-level:** pass = all except C7 (9). fail = C7 (1).

## Notes

- The already-sharp language was necessary scaffolding but **did not crack C7** (still 0/3):
  the skill kept over-editing the already-sharp prompt.
- C4/C5/C9 moved vs v0 with no change touching them → confirms these cases are variance-prone.
  Do not attribute their movement to the (C7-targeted) change.
