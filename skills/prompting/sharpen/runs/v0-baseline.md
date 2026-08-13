# v0 — baseline

- **Skill version:** `d7c2d70` (before any already-sharp handling)
- **Runs/case:** 3
- **Judge:** LLM-as-judge, D1–D5 rubric + per-case checks
- **Provenance:** summary matrix carried over from an earlier session. Per-run D1–D5
  detail was not retained; only the pass counts + notes below are real. Not reconstructed.

## Matrix

| Case | Target | Result |
|------|--------|--------|
| C1 | explicitness (scope unstated) | PASS 3/3 |
| C2 | decision frame (+ latent lead) | PASS 3/3 |
| C3 | don't-lead (Redis pre-named) | PASS 3/3 |
| C4 | altitude (loud + micromanaged) | FAIL 1/3 |
| C5 | show-don't-tell (format in prose) | PASS 2/3 — 1 run dropped the edge case |
| C6 | blank trap (don't fabricate) | PASS 3/3 |
| C7 | already-sharp (don't over-edit) | **FAIL 0/3** |
| C8 | survey exception (don't force a pick) | PASS 3/3 |
| C9 | heavyweight + escalate (Fable + workflow) | FAIL 1/3 |
| C10 | security + effort (not Fable, not max) | PASS 3/3 |

**Case-level:** pass = C1, C2, C3, C5, C6, C8, C10 (7). fail = C4, C7, C9 (3).

## Notes

- C7 (already-sharp) fails outright — the skill over-edits a prompt that is already explicit,
  framed, and right-altitude. This is the failure v1/v2 target.
- C4, C5, C9 are the marginal/noisy cases (C4 already failing here at 1/3).
