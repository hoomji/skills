---
name: auditing-tests
description: Judge a test by whether a plausible wrong implementation fails it. Use when a test goes red and you must decide whether the code or the test is wrong, when writing or changing a test, or when reviewing or auditing a suite for tautologies.
---

# Auditing tests

A test earns its place when it asserts **behavior** the unit's contract promises and a plausible **wrong implementation** fails it. Every step below serves that one test: name the wrong implementation, then prove the assertion catches it.

The weak-assertion shapes (no assertion, mock-only, self-referential, constant pin, fixture asserts fixture) live in [`test-behavior-not-implementation`](../verification-principles/test-behavior-not-implementation.md). Read it when grading an existing assertion.

## Red test: who is wrong?

1. **Read the contract** from the requirement, spec, PR, or caller — never from the implementation under test. Done when you can state the expected result for the failing input in one sentence, with its source.
2. **Work the expected value by hand** for the failing input. Done when you have a literal value derived without calling production helpers.
3. **Decide.** Code disagrees with the hand-worked value: fix the code, keep the test. Test disagrees: the test was asserting something other than the contract (an internal call order, a private structure, a value computed through the same helper). Rewrite it to assert the contract. Done when the decision cites step 2's value.
4. **Run the lens below** on every test you touched. A test edited only to turn green, with no named wrong implementation, is not done.

## Writing or changing a test

1. **Assert observable outcomes**: return values, errors, state changes, externally visible effects. Leave private helpers, internal data shapes, and incidental call order unasserted unless the contract names them. A behavior-preserving refactor keeps the test green.
2. **Derive the expectation independently** — requirement, hand-worked example, or independent reference. Computing it through the code under test reproduces the code's mistake.
3. **Build fixtures that discriminate**: competing eligible and ineligible records, distinct old and new values, both sides of each boundary. A count alone cannot show who was selected; identical before and after contents cannot show an update happened.
4. **Run the lens.**

## The lens

Ask: **could the implementation be wrong while this test still agrees with it?**

For each touched test, name one plausible wrong implementation — drop the eligibility filter, keep the old value, flip the boundary comparison, return the input unchanged. Then, for a suspected gap or a high-consequence path (money, auth, data writes), prove it with a **mutation**:

1. Baseline: the test passes on the real code.
2. Apply the small mutation in an isolated checkout.
3. The relevant assertion fails, for the intended reason. An import error, a missing dependency, or a crash elsewhere is not a catch.
4. Restore the code and rerun green.

Done when every touched test has a named wrong implementation it catches, and every mutation you ran is recorded as `test → mutation → failing assertion`. This is a per-test review technique; a whole-repository mutation campaign is out of scope.

Structural and repeatability checks keep their place for the contract they establish. A deterministic wrong answer is still deterministic, so pair them with a behavior assertion when behavior is the claim.

## Report

End with one line per touched test:

`TEST-LENS: <test name> catches <wrong implementation> (<mutated|reasoned>)`

or `TEST-LENS: none touched`.
