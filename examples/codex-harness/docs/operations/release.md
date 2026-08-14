# Release

## Example boundary

This reference repository does not deploy. A branch push or pull request is R2; merge is R3; production deployment and destructive migration are R4.

## Required release gates for an adopting repository

1. All product acceptance criteria have reproducible evidence.
2. Required CI and policy checks pass.
3. The evidence review has no unresolved blocking finding.
4. A recovery or rollback path is tested proportionately to impact.
5. The actor has explicit authority for the risk class.
6. Production secrets and data remain outside repository artifacts and prompts.

## Handoff

Report branch, commit, target, evidence, skipped checks, residual risks, approvals, and rollback instructions. Do not equate pushing a branch with releasing a product.
