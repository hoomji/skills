# Development

## Prerequisites

- Python 3.11 or newer
- Git for worktree-aware namespace output; the scripts have a deterministic fallback when Git is unavailable
- No package installation, service, secret, or network access

## Cold start

```powershell
python scripts/setup.py
python scripts/check.py
python scripts/test.py
python scripts/harness-validate.py .
```

`setup.py` is idempotent and read-only. It checks the runtime and required repository files.

## Change loop

1. Read the product spec and active ExecPlan.
2. Add or update an acceptance test.
3. Make the smallest behavior change.
4. Run `python scripts/check.py`.
5. Run `python scripts/test.py`.
6. Run `python scripts/start.py` when output or observability changes.
7. Fill an evidence bundle and self-review the diff.

## Isolation

Use one Git worktree per concurrent mutating task. The example writes no local state. A real service should namespace ports, databases, containers, fixtures, logs, and telemetry using the task namespace described in [`isolation.md`](isolation.md).
