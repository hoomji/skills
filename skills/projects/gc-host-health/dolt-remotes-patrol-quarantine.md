---
name: dolt-remotes-patrol-quarantine
description: Context regarding the suppression of the dolt-remotes-patrol order
---

# dolt-remotes-patrol Quarantine

`dolt-remotes-patrol` has been temporarily suppressed via shadowing (`orders/dolt-remotes-patrol.toml`) with `enabled = false`.

- **Symptoms**: `dolt-remotes-patrol` was failing every single run (27 failures in 8 hours observed).
- **Cause**: The `hq` store has an integrity quarantine that has persisted since Sept 7, preventing the patrol from succeeding. The resulting failures were pure noise in the event log.
- **Resolution Path**: The fix requires resolving the `hq` quarantine, not fixing the patrol itself. 
- **Next Steps**: Re-enable the built-in order (by removing or editing `orders/dolt-remotes-patrol.toml`) once the `hq` quarantine is cleared.
