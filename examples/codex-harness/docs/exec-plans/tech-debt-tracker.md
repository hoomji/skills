# Technical debt

| Item | Impact | Trigger | Owner | State |
| --- | --- | --- | --- | --- |
| Persistent-runtime example | Runtime surface coverage is limited to a finite CLI | Add when a real tracer requires UI, server logs, metrics, or traces | Example maintainers | Deferred by design |
| Markdown anchor validation | The bundled validator checks file targets but not headings | Add after a broken anchor recurs | Example maintainers | Observed once; not encoded |
