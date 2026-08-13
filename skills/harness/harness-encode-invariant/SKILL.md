---
name: harness-encode-invariant
description: Convert a repeated repository correction or architectural rule into mechanical enforcement. Use when review feedback recurs, an ADR or boundary needs executable protection, or the user wants a custom lint, structural test, schema, hook, or CI gate with actionable remediation.
---

# Harness Encode Invariant

Read [`../harness/references/contracts.md`](../harness/references/contracts.md). Encode
high-value boundaries, not personal taste.

## 1. Prove the invariant

Gather at least one concrete violation or recurring correction, the authoritative rule,
scope, impact, and legitimate exceptions. Separate a universally checkable predicate
from contextual judgment.

Completion criterion: a machine can classify representative valid and invalid cases;
otherwise return a documentation or review-checklist proposal instead of enforcement.

## 2. Choose the enforcement seam

Prefer the earliest existing mechanism that can classify the rule accurately: type or
schema boundary, unit/structural test, linter, hook, then CI. Define owner, exception
path, rollout mode, and recovery. Avoid a new framework when an existing one fits.

Completion criterion: the seam catches the known violation with acceptable false-positive
risk and does not require unavailable production state.

## 3. Implement red/green evidence

Add a negative fixture that fails for the intended reason and a valid fixture that
passes. Write the failure message as an agent interface: name the rule, relevant location,
smallest valid repair, and deeper reference. Then implement the check and repository gate.

Completion criterion: the bad case fails, the good case passes, and the normal validation
path runs the invariant.

## 4. Record and hand off

Update policy evidence in the harness manifest and close or link the learning-ledger
entry. Return the shared evidence bundle, exception policy, and false-positive caveats.
