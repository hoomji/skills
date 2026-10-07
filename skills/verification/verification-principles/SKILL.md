---
name: verification-principles
description: Six verification principles, one file each - prove it works, sequence verifiable units, test behavior not implementation, fix root causes, build the lever, encode lessons in structure. Read before declaring a task done, before keeping or writing a test, when a fix is a guard around a symptom, or when the same instruction is being written a second time.
---

# Verification principles

Short rules from pstack (MIT, see `../LICENSE-pstack`). Read the one the moment calls for; each is under thirty lines.

| When | Read |
|---|---|
| About to say "done". A proxy (compiles, mtime, self-report, cached screenshot) is standing in for the real artifact. | [prove-it-works](prove-it-works.md) |
| Multi-step work: a sweep, a migration, a stack of commits or PRs. | [sequence-verifiable-units](sequence-verifiable-units.md) |
| Writing, changing or keeping a test. Would it still pass if every import returned `undefined`? | [test-behavior-not-implementation](test-behavior-not-implementation.md) |
| Debugging. Tempted to add a nil check or a retry around a symptom. | [fix-root-causes](fix-root-causes.md) |
| Non-trivial work done by hand, or a check a reviewer could not rerun. | [build-the-lever](build-the-lever.md) |
| Writing the same instruction twice, or a correction that keeps recurring. | [encode-lessons-in-structure](encode-lessons-in-structure.md) |

The rung a proof sits on, lowest to highest: you said so; you pointed at the line; you walked the failure and it cannot reach; you ran it and it fails loud when wrong; you reproduced it in the running app. Say which rung each claim reached. `blast-radius` applies this ladder to a diff.
