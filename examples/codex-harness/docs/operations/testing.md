# Testing

## Layers

| Layer | Command | Evidence |
| --- | --- | --- |
| Static and structural | `python scripts/check.py` | Python compilation, dependency direction, required files |
| Behavior | `python scripts/test.py` | Unit and CLI contract tests |
| Runtime self-check | `python scripts/start.py` | Structured status event |
| Harness contract | `python scripts/harness-validate.py .` | Manifest, commands, evidence, guidance, ledger |
| Hygiene | `python scripts/garden.py` | Read-only stale/broken artifact scan |
| Quality | `python scripts/quality_report.py` | Evidence-backed plane report |

## Completion rule

A green command is evidence only for the behavior it actually observes. Do not use passing unit tests to claim runtime, deployment, security, or production health.
