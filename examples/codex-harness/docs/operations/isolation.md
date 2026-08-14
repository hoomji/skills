# Isolation

## Namespace contract

Every task computes a namespace from the resolved worktree path. A real runtime uses that namespace for:

- port offsets;
- container and network names;
- local database schemas or files;
- fixture identities;
- log, metric, and trace labels;
- temporary artifacts and screenshots.

## Requirements

- Never share mutable test data between concurrent worktrees.
- Never infer that local isolation permits production access.
- Teardown must target the exact task namespace.
- Cleanup commands must refuse broad or unresolved targets.

The example creates no mutable runtime resources, so teardown is not applicable.
