# Product context

## Purpose

The example application turns a collection of check results into one deterministic status summary. Its small domain exists to make the complete harness flow observable.

## Canonical language

| Term | Meaning | Avoid |
| --- | --- | --- |
| Check result | One named observation with `pass`, `fail`, or `unknown` state | test result, probe |
| Status summary | The aggregate state, counts, and failed check names returned to a caller | health blob, report object |
| Aggregate state | `healthy`, `degraded`, or `unknown` derived from all check results | success flag |
| Evidence bundle | The repository record supporting a completion claim | notes, proof dump |
| Tracer workflow | The representative end-to-end change used to prove the harness | demo task |
| Capability claim | A manifest statement backed by repository evidence | aspiration |

## Behavioral rules

- Any failed check makes the aggregate state `degraded`.
- With no failures, any unknown check makes the aggregate state `unknown`.
- Only all-pass input produces `healthy`.
- Output order is deterministic and preserves input order for failed and unknown names.
- Empty input is `unknown`, because absence of evidence is not health.

## Ownership boundary

This example owns summary calculation, its CLI self-check, documentation, and harness artifacts. It does not own service discovery, production monitoring, alerting, deployment, credentials, or remote actions.
