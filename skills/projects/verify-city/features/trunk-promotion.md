# trunk-promotion

How a trunk change reaches `develop`. The trunk (`dispatch/integration-branch`, today `wall/develop`)
is verified after merge. `dispatch/wall-deployable.py` ratchets each post-merge check into a
`deployable` marker. The `promotion-cadence` order picks the promotable sha (push CI green, no critical
red, no gate red) and writes it to `ci-green`. It then runs `dispatch/promotion.sh --yes --sha <sha>`,
which cuts `release/trunk-<ts>` (the sha plus a develop merge), runs the migration preflight, opens the
PR into develop and queues it with `land.sh <pr> --yes` (gates 2, 4 and 5; gate 4 is a merge review).
Mergify then runs the full suites. Method docs: `docs/trunk-and-promotion.md` ("Deployable ratchet",
"Promotion"), ADR 0002, ADR 0003, and `CONTEXT.md` (cut, recut, promotion delta, merge review,
promotion evidence, promotable sha, gate red).

## Sub-features

- `tp-deployable` The deployable ratchet (R-20261021-02). `wall-deployable.py --tip <sha>` judges
  each post-merge check. It writes `.gc/runtime/wall-ci/deployable` when the tip adds no new red since
  the previous check, has no critical red (typecheck, install, `build:*`, migration-order or
  migration-prefix-unique tests) and is the newest check. It appends `deployable.tsv` (ts sha prev_sha
  new_reds verdict reason; verdict `green|deployable|held`). `verified` is the last judged tip and
  `green` the last green one. `deployable` is what wall-deploy may ship; it is not what promotion
  ships (see `tp-promotable`).
- `tp-promotable` The promotable sha (R-20261021-15, R-20261022-06). It is the newest first-parent
  trunk sha with all four required push workflows (`lint`, `services test`, `apps test`,
  `tooling test`) at `success` on their latest attempt, no critical red in its `wall-tip-red.tsv` row,
  and no gate red. A gate red is any `GATE_STEPS` step (in `promotion-cadence.py`: the repo-wide,
  specs and checks jobs Mergify's develop queue requires, e.g. `plan-ids`, `biome`, `gitleaks`)
  named red in the sha's newest `wall-tip-red.tsv` row. The cadence writes it to `ci-green`.
- `tp-cut` The cut (`promotion.sh`). `release/trunk-<YYYYMMDD-HHMM>` is the sha plus a develop merge
  built with `git merge-tree`/`commit-tree` (merge `none` when develop is already contained). The PR
  body ends with `<!-- promotion.sh sha=<sha> merge=<merge|none> -->`. The branch takes no other
  commit: `--requeue` refuses one with extra commits (exit 4). With `--yes` a new cut closes every
  older open `release/*` PR as superseded. A recut (ADR 0003) is a new cut at a newer sha; evidence
  carrying across the promotion delta is ADR policy, and the harness shows whether the live code
  does it yet.
- `tp-preflight` The migration preflight (`scripts/release-migration-preflight.mjs --source develop
  --develop-ref <merge>`, a Gateway-LLM script). FAIL or UNAVAILABLE opens the PR unqueued with
  `**Held (preflight):**` in the body (`PROMOTION HELD`, exit 5). `promotion.sh --requeue <pr>
  --ack-preflight "<reason>" --yes` comments the reason and queues it.
- `tp-queue` The queue path. `land.sh <pr> --yes` runs `merge-train.sh ready` (gate 4 evidence
  through `gate4_lens_evidence`; under ADR 0003 it is a merge review of the migration surface, the
  develop-merge conflict hunks and the promotion delta, never the member PRs). It then runs gate 2
  (review provider), gate 5 (open, non-draft, mergeable) and posts `@mergifyio queue`. It writes
  `queued` to `dispatch/ledgers/mergify.jsonl`. A `release/*` head skips the migration restamp:
  `migration-restamp.py queue` returns 0 for it, and Mergify's guard judges order through
  `RELEASE_ORDER_EXCEPTIONS`.
- `tp-cadence` The `promotion-cadence` order (every 15 min, `elapsed-check.sh promotion-cadence
  900`). It appends one `.gc/runtime/wall-ci/promotion-cadence.tsv` row (ts verdict sha pr detail)
  only when the verdict changes. Verdicts: `GATE-RED` (newest push-green sha has a gate red; older shas
  are tried), `UP-TO-DATE`, `HELD #N`, `IN-FLIGHT #N` (a "Mergify Merge Queue" check-run on the PR
  head is not completed), `DEQUEUED #N` (an open promotion at the promotable sha is out of the queue),
  `SPACING` (last cut under 4 h), `CUT`, `STARVED` (24 h, exit 1, mailed) and `WAIT`. Mail
  dedup and slots live in `promotion-cadence.json`.
- `tp-ledgers` `dispatch/ledgers/promotion.tsv`: ts state pr sha branch preflight. promotion.sh
  writes it only with `--yes`, and only these states appear: `QUEUED`, `HELD`, `QUEUE-FAILED`,
  `CURRENT`, `CONFLICT`, `REFUSED`, `FAILED`, plus the `MERGED-BY-HAND` backfill. Also
  `dispatch/ledgers/mergify.jsonl` `queued`/`merged`/`dequeued` rows for promotion PR numbers
  (land.sh writers only).
- `tp-switches` `.gc/runtime/wall-ci/promotion-cadence.off` and `wall.off` stop the cadence
  (`PROMOTION-CADENCE off`). `wall-deploy.off` (R-20261021-14) keeps the ratchet from deploying, so
  promotion plus develop CD is the only route to development.

## How to get to it (user POV)

- Nobody starts it: the `promotion-cadence` order cuts and queues on its own. The mayor reads the
  outcome in `promotion-cadence.tsv`, `promotion.tsv`, the PR into develop and mail
  (`PROMOTION HELD`, `PROMOTION DEQUEUED`, `PROMOTION STARVED`, `PROMOTION CUT FAILED`).
- A held promotion: the owner or mayor settles the preflight findings on the trunk, or runs
  `promotion.sh --requeue <pr> --ack-preflight "<reason>" --yes`.
- A dequeued promotion: the cause is fixed on the trunk and the next promotable sha is recut. The
  release branch takes no fix commit.
- Stopping it: `touch .gc/runtime/wall-ci/promotion-cadence.off`.

## Driving it with trunk_promotion.py

`.claude/skills/verify-city/scripts/trunk_promotion.py [--city DIR] doctor|state|promotable|gate`.
Every subcommand is read-only: file reads, `gc order list/history`, git reads in
`~/projects/Gateway-LLM` with no fetch (local `origin/*` refs trail the remote by up to one cadence
run), `gh pr list` and `gh api` GETs (about 3 calls per open promotion).

Preconditions:

- Baseline preconditions hold, and `mkdir -p $EV/trunk-promotion`.
- `gh auth status` succeeds.

- **Doctor.** Run `trunk_promotion.py doctor > $EV/trunk-promotion/doctor.txt; echo $?`. A clean run
  prints `trunk-promotion: clean` and exits 0. Findings, one per line:
  - `script-missing` / `script-not-executable`: one of promotion.sh, promotion-cadence.py,
    wall-deployable.py, land.sh, merge-train.sh, migration-restamp.py, migration-order.py or
    develop-watch.py.
  - `doc-path-missing`: a backticked path in trunk-and-promotion.md's `## Promotion` section is
    missing. `scripts/` paths are checked on Gateway-LLM `origin/<trunk>`.
  - `order-missing`, `order-disabled`, `order-exec-missing`, `order-never-ran`, `order-stale`: the
    last run is over 45 min old with neither off switch set.
  - `ledger-missing` / `ledger-row-bad`: promotion.tsv (6 columns, known state) or
    promotion-cadence.tsv (5 columns, known verdict).
  - `marker-off-trunk`: `ci-green` or `deployable` is not on the trunk's first-parent history.
  - `promotion-unmarked` / `promotion-extra-commits`: an open `release/*` PR has no promotion.sh
    marker, or its head is not the marker's cut. The second is live state (someone committed to the
    release branch), never map drift.
- **State** (`tp-deployable`, `tp-promotable`, `tp-cut`, `tp-cadence`, `tp-ledgers`,
  `tp-switches`). Run `trunk_promotion.py state > $EV/trunk-promotion/state.txt`. Read each marker's
  sha, its position on the trunk's first parents and whether develop has it. Then the remote and
  local tips, the number of trunk commits develop lacks, the switches, and each open promotion with
  marker sha/merge, `held`, `queued` (Mergify Merge Queue check-run) and any `EXTRA COMMIT`. Last come
  the last cadence and promotion.tsv rows and the mergify.jsonl rows for those PR numbers. `0` rows
  for a queued promotion means it was queued by hand.
- **Promotable** (`tp-promotable`, `tp-cadence`). Run `trunk_promotion.py promotable >
  $EV/trunk-promotion/promotable.txt`. It lists the newest trunk shas with each required workflow's
  conclusion, critical and gate reds, and a verdict, stopping at the first `PROMOTABLE`. It then
  imports `promotion-cadence.py` and runs its own `decide()` in dry mode, with the `git fetch`
  patched out and promotion.sh and `gc` refused. The `PROMOTION-CADENCE <verdict>` line is what the
  next order run would print, against the local refs.
- **Gate** (`tp-queue`). Run `trunk_promotion.py gate > $EV/trunk-promotion/gate.txt`. Per open
  promotion:
  - the gate-4 verdict from the `gate4_lens_evidence` python in `merge-train.sh`, run on the fleet's
    jobs, receipts, reviews and round-cap waivers at the PR head (head only: `head_aliases` fetches,
    so patch-identical pins are not credited);
  - every lens pinned to the PR with its receipt verdict and `failure_class`. A `withdrawn` lens
    that the gate verdict names is flagged: since fix D it must read NEEDS, never FAIL;
  - `migration-order.py <head> develop`;
  - whether `migration-restamp.py` still skips `release/*`.

  It proves what land.sh gate 4 would read, not that Mergify's checks pass. No open promotion makes
  this `verified-unreachable`.
- **Preflight** (`tp-preflight`). There is no safe drive: the preflight runs only inside promotion.sh.
  Read the verdict from the PR body ("Migration preflight: PASS|FAIL|UNAVAILABLE") and
  promotion.tsv column 6.

## Gotchas

- Never run these to "check" something:
  - `promotion.sh` without `--yes`: it takes `promotion.lock`, fetches, writes a merge object with
    `commit-tree`, adds and removes a git worktree, and runs the preflight under node.
  - `promotion-cadence.py --dry-run`: it skips the tsv, json, `ci-green` and mail writes, but
    `decide()` still runs `git fetch origin develop <trunk>` in Gateway-LLM. The harness imports it
    and patches the fetch out.
  - `land.sh <pr>` without `--yes`: it runs `merge-train.sh ready` (`head_aliases` fetches), may
    rewrite the `develop-health.json` cache, and `restamp --dry-run` fetches.
- `deployable` is not `ci-green`. On 10-22 `deployable`=`ebef41f9` carried a `plan-ids` gate red
  (wall-tip-red.tsv 12:45Z), and its push CI was green. Mergify's `checks` job is diff-relative, so the
  push run passed while the local whole-tree step was red. #6382 (marker sha bdc34f58) was dequeued
  at 12:50Z on "No code comment gains a plan identifier". R-20261022-06 (`GATE_STEPS`) now skips such a
  sha (`GATE-RED`).
- The 10-22 recut: #6376 (ebef41f9, `merge=none`) was HELD on its preflight. It hit QUEUE-FAILED
  three times (12:13-12:22Z) because `migration-restamp.py` refused release migrations, since fixed by
  the `release/*` skip. It was closed as superseded by #6382 (bdc34f58) at 12:35Z, which threw away a
  PASS lens and an owner-signed preflight (ADR 0003).
- A hand `@mergifyio queue` or `@mergifyio requeue` comment leaves no mergify.jsonl row. #6382 was
  queued by hand at 12:41Z and requeued at 12:55Z, and has 0 rows. Its last promotion.tsv state reads
  `QUEUE-FAILED` while Mergify holds it. Use the check-run (`state`'s `queued`), not the ledgers.
- A fix pushed onto the release branch breaks the cut. #6382's head `2fe4b4b2` (a plan-ids comment
  fix) sits on top of the cut merge `2f09f623`. `doctor` reports `promotion-extra-commits`, and
  `promotion.sh --requeue 6382` would refuse with exit 4. The same fix went to the trunk separately.
- A withdrawn lens has a receipt with `verdict: FAIL`, `failure_class: withdrawn` and a report
  starting "Withdrawn by" (6b49bd1f on #6382, withdrawn when the owner waived the delta lens). Before
  fix D (`merge-train.sh` gate 4, live 2026-10-22 about 13:10Z), the gate read such a newest pin as
  `gate-4 lens <id> FAIL`. Since fix D it is no evidence: with only that lens, the gate reads
  `NEEDS gate-4 lenses`. Proved by running the extracted gate-4 python on a scratch copy holding only
  6b49bd1f. The `gate` drive flags a withdrawn lens that the verdict names as a regression.
- ADR 0003 is ahead of the live code. Check these before calling them verified:
  - the marker carrying a superseded sha;
  - lens and preflight carry across a runtime-equal delta;
  - spacing counting only queued or merged cuts. The live `CUT_STATES` still includes `HELD` and
    `QUEUE-FAILED`, so after #6382 `SPACING` holds the next cut until 4 h after 12:36Z.
- `migration-order.py <release head> develop` lists trunk migrations that sort before develop's
  newest. For a promotion that is expected, not a WAIT: land.sh defers it to the restamp, which skips
  `release/*`. Mergify's guard decides through `RELEASE_ORDER_EXCEPTIONS`.
- `promotion-cadence.tsv` records a row only when the verdict changes, so a quiet tsv with a recent
  `gc order history` run is normal. The `ci-green` marker still moves on every run.
- Local `origin/*` refs in Gateway-LLM move only when the cadence or another script fetches. Compare
  `state`'s `remote` and `local` lines before trusting a position.
