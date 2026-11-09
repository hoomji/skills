# hoppy-trunk

The Hoppy-city trunk flow (R-20261109-04), described in the city's `docs/trunk-and-promotion.md`
section "Hoppy-city trunk flow". Lane PRs target `trunk`. Three exec orders do the rest: `hoppy-gate`
runs selective gates in parallel, `hoppy-land` merges PASS heads, and `hoppy-promote` runs a full gate
on the trunk tip and fast-forwards `main`.

## Sub-features

- `ht-orders` `gc order list` shows hoppy-gate, hoppy-land and hoppy-promote enabled, and
  `.gc/runtime/hoppy-trunk/off` is absent.
- `ht-gate` every open, non-draft trunk PR head has one of three things: a verdict, a live
  `.running` marker, or a slot wait under the cap (`status` lists each).
- `ht-land` every PASS head at its current PR head is merged, or is listed REBASE-NEEDED, within
  one land tick. Read the rows in `dispatch/ledgers/hoppy-land.tsv`.
- `ht-promote` main is an ancestor of trunk. Either main is the newest first-parent `ref-` PASS, or
  a full run on the tip is live or has a verdict.
- `ht-red` each break on trunk has one open bead in `state.json` `red`, and later tips with the same
  failed steps carry `dup_of`.
- `ht-regate` no open PR holds a FAIL whose failure is inherited from a trunk break that is over
  (`due()` would re-gate it).

## Driving it

Run `dispatch/hoppy-trunk.py status`. It is read-only and takes no lock. To see what the next tick
would do, run `dispatch/hoppy-trunk.py gate-next --dry-run`, then `land --dry-run`, then
`promote --dry-run` (promote refreshes only its private mirror cache). The state is in
`.gc/runtime/hoppy-trunk/state.json`, and the verdicts are in `~/.cache/hoppy-gate/verdicts/`.
