# receipt-grader

The receipt-grader seat (Codex, `agents/receipt-grader/`) grades fleet lane receipts against
remote evidence, appends one row per receipt to `dispatch/ledgers/model-grades.tsv`, comments
the acceptance bead and mails the mayor `GRADES:`. It wakes on `receipt-grader-pass` when
ungraded receipt ids appear in `pending.txt`.

## Sub-features

- `rg-wake` the nudge and the pass formula give the Seat contract's wake order.
- `rg-refs` every path and script the prompt names exists.
- `rg-ledger` the grade vocabulary in the prompt matches the ledger header.
- `rg-memory` the seat's memory copies are in step.
- `rg-pass` the last pass graded, committed, commented and mailed as the prompt asks.

## How to get to it (user POV)

- `orders/receipt-grader-pass.toml` fires when `orders/scripts/receipt-grader-check.sh` finds ungraded receipts.
- The mayor reads the seat's `GRADES:` mail instead of grading itself.

## Driving it with context.py

Preconditions:

- Doctor ran this pass.

- **Render.** Run `context.py render receipt-grader $EV`.
- **Wake order.** Compare `$EV/receipt-grader.wake.md` with `docs/delegated-seats.md` "Seat
  contract". Each difference is recorded.
- **Paths.** Run `context.py refs agents/receipt-grader/prompt.template.md`. Every line reads
  `ok`. `sed -n 1,20p dispatch/receipt-show.py` shows the usage the prompt relies on
  (`<id>`, `--job-only`, `--receipt-only`); its `--help` exits 2 by design.
- **Ledger.** Run `head -5 dispatch/ledgers/model-grades.tsv`. The prompt's grade words
  (`WORKED`, `BLOCKED-JUSTIFIED`, `BLOCKED-UNJUSTIFIED`) are the header's.
- **Memory.** Run `context.py seat-memory receipt-grader`. Output is `receipt-grader: seat memory in step`.
- **Last pass.** Run `context.py last-pass receipt-grader > $EV/receipt-grader.last-pass.json`
  and `git log -5 --format='%h %cI %s' -- dispatch/ledgers/model-grades.tsv`. The pass names
  the receipt id; a `grades:` commit containing it exists, often minutes before the claim,
  because the session grades and commits before it claims.

## Gotchas

- The mayor prompt must not also tell the mayor to grade; check its "Every wake" step 3.
- A remote-store bead takes `dispatch/<host>.sh bd comment`, not `gc bd comment`.
