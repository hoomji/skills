# Observability

## Surface

`python scripts/start.py` emits newline-delimited JSON to standard output. The final `status_summary.completed` event contains:

- `task_namespace`: stable identifier derived from the current worktree path;
- `event`: machine-readable event name;
- `summary`: aggregate state, counts, and ordered failure names.

## Query path

For the example, run the command and inspect standard output. Tests parse the last line and assert its schema.

## Sensitive data

Check names in this example are public fixture values. A real repository must define redaction, retention, access, and customer-data boundaries before exposing logs or traces to an agent.

## Extension points

When a real tracer requires them, add worktree-local UI access, logs, metrics, traces, performance thresholds, database inspection, or external API observation. Each surface needs fixtures, access scope, expected evidence, and teardown.
