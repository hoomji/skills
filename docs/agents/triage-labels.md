# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Canonical role    | Label in this repo | Meaning                                  |
| ----------------- | ------------------ | ---------------------------------------- |
| `needs-triage`    | `needs-triage`     | Maintainer needs to evaluate this issue  |
| `needs-info`      | `needs-info`       | Waiting on reporter for more information |
| `ready-for-agent` | `ready-for-agent`  | Fully specified, ready for an AFK agent  |
| `ready-for-human` | `ready-for-human`  | Requires human implementation            |
| `wontfix`         | `wontfix`          | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Work in flight

The five roles say what an issue _needs_. None says whether someone already took it, so an issue whose PR is written and waiting to merge reads exactly like untouched work. This is a separate axis, not a sixth role.

| Label    | Label in this repo | Meaning                                                            |
| -------- | ------------------ | ------------------------------------------------------------------ |
| `has-pr` | `has-pr`           | An open PR implements this (fully or as a slice) — closes on merge |

Apply it only where an open PR **delivers** the issue's work. A PR that merely mentions the issue — coordinating with an overlapping branch, citing a base it builds on, naming the reason its CI is blocked — does not qualify. `has-pr-labelling` owns that test.
