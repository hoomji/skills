# Harness quality score

Quality is reported per plane. This snapshot must be regenerated from commands and artifacts rather than copied into an adopting repository.

| Plane | Level | Evidence | Next gate |
| --- | --- | --- | --- |
| Intent | 3 | Product spec and behavior tests | Independent traceability review |
| Knowledge | 3 | Root map, context, architecture, indexed design docs, ADRs | Cold-start usability trial |
| Execution | 3 | Setup/start/check/test commands | Clean-environment CI history |
| Feedback | 3 | Tests and structured self-check | Persistent runtime surface if needed |
| Policy | 4 | Negative structural checks | Failure-history-driven expansion only |
| Isolation | 1 | Worktree namespace documentation | Task-local service proof |
| Lifecycle | 2 | Lifecycle and executable commands | Real PR evidence |
| Hygiene | 2 | Garden and report scripts | Trend history and false-positive rate |
| Governance | 1 | Risk and escalation documentation | Repository-host permission integration |

Do not average these levels. The next weakest tracer-relevant plane is lifecycle evidence from a real reviewed change.
