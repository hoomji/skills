---
name: harness-review-evidence
description: Review a software change against its originating spec, repository standards, and claimed verification evidence. Use when a diff or PR needs a harness-aware review, an evidence bundle must be audited, or the user wants product-judgment gaps separated from mechanically repairable defects.
---

# Harness Review Evidence

Read [`../harness/references/contracts.md`](../harness/references/contracts.md) and
[`../harness/references/composition.md`](../harness/references/composition.md).

## 1. Recover the review contract

Identify the fixed comparison point, originating spec or issue, acceptance criteria,
repository guidance, relevant decisions, and claimed evidence. State missing sources
instead of substituting likely intent. Freeze the comparison base and record dirty or
untracked files that are excluded from the review.

Completion criterion: standards and spec axes each have an authoritative source or an
explicitly bounded gap.

## 2. Wrap code review

Use the installed Matt Pocock `code-review` capability for standards and spec review.
Add harness-specific inspection of the evidence bundle: commands actually run, runtime
proof, skipped checks, environment limits, and residual risk. Inspect raw outputs when a
claim is consequential. Treat a named command without retained output as uncorroborated,
not passed.

Completion criterion: every changed behavior is checked against the spec and every
material evidence claim is corroborated or marked unsupported.

Treat contradictory meanings or avoided synonyms from the relevant domain glossary as a
finding. If the implementation intentionally changes the domain model, require
`harness-model-domain` to reconcile the canonical language and affected consumers.

Treat an unexplained contradiction with an accepted ADR as a finding. A change may depart
from the decision only when an authoritative source reopens it and
`harness-record-decision` records the resulting lifecycle transition.

## 3. Classify findings

Use [`assets/review-report.md.template`](assets/review-report.md.template). Report
actionable defects first with tight locations and causal explanations. Separate:

- correctness, security, regression, or spec failures;
- repository-standard violations;
- missing or invalid evidence;
- product/architecture judgments requiring a human;
- repeated patterns suitable for `harness-capture-learning`.

Completion criterion: each finding states impact, evidence, and the smallest valid repair;
non-actionable taste is excluded.

## 4. Conclude

State whether the evidence supports completion, which checks remain, and whether autonomy
may advance for this workflow. A clean review explicitly says no actionable findings were
found and names residual uncertainty. Reviewing is R0; repair, comment, push, or PR
mutation requires the user's corresponding authorization.

Completion criterion: every acceptance criterion has a supported, failed, or unknown
result; every actionable finding names the smallest repair; product judgment is left to a
human rather than disguised as a defect.
