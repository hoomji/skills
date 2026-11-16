---
name: gc-troubleshoot
description: Troubleshoot a Gas City by walking upstream's troubleshooting pages (docs/troubleshooting and the runbooks they link) and translating each check for this city's bd-owned Dolt stores. Use when gc start prints FATAL or gc-fatal, when asked to troubleshoot a city or follow the gc troubleshooting docs, when a store's .beads/dolt or .beads/backup keeps growing, or when gc sling accepts work that agents never see.
---

# Gas City troubleshooting

Upstream's troubleshooting section is written for a city whose Dolt server **gc** manages.
Here **bd** owns every store's Dolt (a proxied server per store, since 2026-10-13), so half
of each page's commands are no-ops and `gc doctor` skips its Dolt checks. Every doc check
therefore needs a **translation**: the doc's probe, the probe that actually answers it in
this city, and the pass condition. The translations live in
[`references/page-checks.md`](references/page-checks.md); read it before step 3.

The report is one verdict per page section, PASS / DRIFT / N-A, each with the probe that
proved it. A section is never PASS because `gc doctor` printed a ✓: a check that says
`skipped (... external dolt endpoint ...)` is a **blind spot** and needs its own probe.

Neighbours: reclaiming a slow or erroring store is `gc-store-reclaim`; a broad
autonomy/context/efficiency audit is `gc-city-audit`; any gc fact outside these pages is
`gc-docs`.

## 1. Read the pages

```bash
~/.claude/skills/gc-docs/sync.sh main
```

Use `main`: the city runs stock upstream main (`gc version` = `1.5.1-upstream+<sha>`),
which reaches no release tag. Read `docs/troubleshooting/index.md` and every page it links
in full, both Diagnose and Operate. Pages are added often, so take the list from the
index, not from the reference file.

Done when: each linked page is listed with the docs sha, and every page the index links
has a section in `references/page-checks.md`. A page with no section yet is new: write
its translation there before probing.

## 2. Baseline

From `~/city`, read-only:

```bash
gc version; gc bd version; dolt version
readlink /proc/$(systemctl --user show -p MainPID --value gascity-supervisor)/exe
readlink -f "$(command -v gc)"
df -h /
timeout 300 gc doctor --verbose > <scratch>/doctor.txt 2>&1   # takes ~4 min
```

Done when: versions, the supervisor exe next to the on-disk gc, `/` usage, and the doctor
summary line (`N passed, N warnings, N failed`) are in the report draft.

## 3. Walk every page

For each page, run every row of its table in `references/page-checks.md` and record the
verdict. The rig stores are the recurring blind spot: run the per-store sweep in that
file over every path in `~/city/.beads/routes.jsonl`, not only `~/city/.beads/dolt`.

Done when: every row of every page has a verdict and a probe output.

## 4. Triage the rest of the doctor output

List every `✗` and `⚠` from `doctor.txt` that no page covered. Fix those that act on what
this run found. Propose the rest as separate tasks, each with its doctor line quoted.

Done when: every `✗` line is fixed, proposed, or named as owner-held with the memory row
that holds it (for example the detached WD drive behind `gl-dolt-push`).

## 5. Fix city-side

The city's gc is stock upstream, so fixes land in `~/city` (scripts, `city.toml`, packs).
Follow the city commit rules in the mayor memory: a fresh worktree, named paths only, a
test that goes red on the old logic, `dispatch/` scripts swapped by atomic rename, landing
by ref, then `dispatch/city-golive`. Cite the page path and docs sha in the commit.

Done when: each fix is on `main`, live, and re-probed with the same row's probe.

## 6. Record

Add each new finding to `references/page-checks.md` with its date (a new translation or
a new blind spot), so the next run starts from it. Report gaps where the docs and the
binary disagree; the binary wins.
