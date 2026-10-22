#!/usr/bin/env python3
"""trunk_promotion.py -- read-only verification harness for the trunk-to-develop promotion flow.

Subcommands (all read-only: file reads under the city, `gc order list/history`, `git rev-parse/
rev-list/merge-base/cat-file/ls-remote` in ~/projects/Gateway-LLM (never fetch, checkout or switch),
`gh pr list/view` and `gh api` GETs; never promotion.sh, promotion-cadence.py without a patched-out
fetch, land.sh, merge-train.sh, wall-land/wall-ready, mail, or a write under .gc/runtime/):

  doctor      one line per drift finding, exit 1 on any; else `trunk-promotion: clean`, exit 0
  state       markers (deployable, green, verified, ci-green) and their shas, trunk and develop tips,
              trunk commits develop lacks, open promotion PRs (marker sha, held, queued, extra
              commits), last cadence rows, last promotion.tsv rows, mergify.jsonl rows, switches
  promotable  what the next promotion-cadence run would decide: imports dispatch/promotion-cadence.py
              and runs its own decide() in dry mode with the `git fetch` call patched out (its
              --dry-run still fetches in Gateway-LLM); also lists the newest push-green shas with
              their gate reds (wall-tip-red.tsv) and critical reds
  gate        per open promotion PR: the gate-4 evidence verdict for its head (merge-train.sh
              gate4_lens_evidence's python, extracted and run on the fleet's job/receipt files), each
              lens at its pin with its receipt verdict and failure_class, and the migration-order
              verdict (dispatch/migration-order.py, git reads only) plus the release/* restamp skip

--city defaults to $GC_CITY, then ~/city.
"""
import argparse
import datetime as dt
import glob
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

GH_REPO = os.environ.get("GH_REPO", "Uniblock-dev/Gateway-LLM")
GL_REPO = Path(os.environ.get("WALL_REPO", os.path.expanduser("~/projects/Gateway-LLM")))
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
MARKER = re.compile(r"<!-- promotion\.sh sha=([0-9a-f]{40}) merge=([0-9a-f]{40}|none)(?: [^>]*)?-->")
HELD_MARK = "**Held (preflight):**"

# Scripts the feature names: path -> must be executable.
SCRIPTS = ["dispatch/promotion.sh", "dispatch/promotion-cadence.py", "dispatch/wall-deployable.py",
           "dispatch/land.sh", "dispatch/merge-train.sh", "dispatch/migration-restamp.py",
           "dispatch/migration-order.py", "dispatch/develop-watch.py"]
ORDER = "promotion-cadence"
ORDER_MAX_MIN = 45  # elapsed-check 900 s: 3x the interval
# Ledger shapes per the writers' printf/write lines.
PROMO_STATES = {"DRY-RUN", "DRY-RUN-HELD", "QUEUED", "CURRENT", "HELD", "QUEUE-FAILED", "FAILED",
                "CONFLICT", "REFUSED", "MERGED-BY-HAND"}
CADENCE_VERDICTS = {"UP-TO-DATE", "HELD", "IN-FLIGHT", "DEQUEUED", "SPACING", "CUT", "STARVED",
                    "WAIT", "GATE-RED"}
SWITCHES = ["wall.off", "promotion-cadence.off", "wall-deploy.off", "verify.off", "land-validated.on",
            "ci-gate.off", "tip-red-rounds.off", "sync-pending"]
MARKERS = ["deployable", "green", "verified", "ci-green"]


def run(cmd, cwd=None, timeout=90, env=None, stdin=None):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env, input=stdin)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def now():
    return dt.datetime.now(dt.timezone.utc)


def age_min(ts):
    try:
        return int((now() - dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() // 60)
    except (ValueError, AttributeError):
        return None


def rows(path):
    try:
        return [l.rstrip("\n").split("\t") for l in Path(path).read_text().splitlines() if l.strip()]
    except OSError:
        return None


def gl_git(*args, timeout=60):
    return run(["git", "-C", str(GL_REPO), *args], timeout=timeout)


def trunk(city):
    try:
        return (city / "dispatch/integration-branch").read_text().split()[0]
    except (OSError, IndexError):
        return "develop"


def wall_ci(city):
    return city / ".gc/runtime/wall-ci"


def marker(city, name):
    p = wall_ci(city) / name
    try:
        return p.read_text().strip().split()[0], dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc)
    except (OSError, IndexError):
        return None, None


def first_parents(t, n=2000):
    rc, out, _ = gl_git("rev-list", "--first-parent", "-n", str(n), f"origin/{t}")
    return out.split() if rc == 0 else []


def in_develop(sha):
    return gl_git("merge-base", "--is-ancestor", sha, "origin/develop")[0] == 0


def gh_json(args, timeout=60):
    rc, out, err = run(["gh", *args], timeout=timeout)
    if rc != 0:
        return None, (err or out).strip()[:200]
    try:
        return json.loads(out or "null"), ""
    except ValueError as e:
        return None, str(e)


def promotions():
    """Open release/* PRs into develop with marker, held, queued and extra-commit facts."""
    prs, err = gh_json(["pr", "list", "-R", GH_REPO, "--base", "develop", "--state", "open", "--limit", "100",
                        "--json", "number,headRefName,headRefOid,body,createdAt,labels,mergeStateStatus"])
    if prs is None:
        return None, err
    out = []
    for p in prs:
        if not p["headRefName"].startswith("release/"):
            continue
        body = p.get("body") or ""
        m = MARKER.search(body)
        p["sha"], p["merge"] = (m.group(1), m.group(2)) if m else (None, None)
        p["held"] = HELD_MARK in body
        cr, _ = gh_json(["api", f"repos/{GH_REPO}/commits/{p['headRefOid']}/check-runs?check_name=Mergify%20Merge%20Queue&per_page=10"])
        runs = (cr or {}).get("check_runs") or []
        p["queue_runs"] = [(c.get("status"), c.get("conclusion"), c.get("started_at"), (c.get("output") or {}).get("title")) for c in runs]
        p["queued"] = any(c.get("status") != "completed" for c in runs)
        p["extra"] = []
        if m:
            cut = p["sha"] if p["merge"] == "none" else p["merge"]
            if p["headRefOid"] != cut:
                cmp_, err2 = gh_json(["api", f"repos/{GH_REPO}/compare/{cut}...{p['headRefOid']}"])
                if cmp_ is None:
                    p["extra"] = [f"(compare failed: {err2})"]
                else:
                    p["extra"] = ["%s %s %s" % (c["sha"][:8], c["commit"]["author"]["name"], c["commit"]["message"].splitlines()[0][:80])
                                  for c in cmp_.get("commits") or []] or [f"(head {p['headRefOid'][:8]} != cut {cut[:8]}, compare lists no commit)"]
        p["body"] = None
        out.append(p)
    return out, ""


def order_info(city):
    rc, out, err = run(["gc", "order", "list", "--json", "--city", str(city)])
    if rc != 0:
        return None, (err or out).strip()[:200]
    try:
        return {o["name"]: o for o in json.loads(out).get("orders", [])}.get(ORDER, {}), ""
    except (ValueError, KeyError) as e:
        return None, str(e)


def last_run(city, name):
    rc, out, _ = run(["gc", "order", "history", name, "--limit", "1", "--json", "--city", str(city)])
    if rc != 0:
        return None
    try:
        e = json.loads(out).get("entries") or []
        return e[0].get("executed") if e else None
    except ValueError:
        return None


# --------------------------------------------------------------------------------------- doctor
def doctor(city):
    f = []
    t = trunk(city)
    for rel in SCRIPTS:
        p = city / rel
        if not p.is_file():
            f.append(f"script-missing {rel}")
        elif not os.access(p, os.X_OK):
            f.append(f"script-not-executable {rel}")

    # Paths named in docs/trunk-and-promotion.md "## Promotion" (city paths; scripts/ is Gateway-LLM's).
    try:
        text = (city / "docs/trunk-and-promotion.md").read_text()
        i = text.find("## Promotion")
        if i < 0:
            f.append("doc-section-missing docs/trunk-and-promotion.md has no '## Promotion'")
        sec = ""
        if i >= 0:
            m = re.search(r"^## ", text[i + 1:], re.M)
            sec = text[i:i + 1 + m.start()] if m else text[i:]
        for tok in sorted(set(re.findall(r"`((?:dispatch|orders|scripts|docs|\.gc)/[A-Za-z0-9_./*<>-]+)`", sec))):
            if "<" in tok or "*" in tok:
                continue
            if tok.startswith("scripts/"):
                if gl_git("cat-file", "-e", f"origin/{t}:{tok}")[0] != 0:
                    f.append(f"doc-path-missing docs/trunk-and-promotion.md Promotion names {tok}; not on Gateway-LLM origin/{t}")
            elif not (city / tok).exists():
                f.append(f"doc-path-missing docs/trunk-and-promotion.md Promotion names {tok}")
    except OSError:
        f.append("doc-missing docs/trunk-and-promotion.md")

    o, err = order_info(city)
    if o is None:
        f.append(f"gc-order-list-failed {err}")
    elif not o:
        f.append(f"order-missing {ORDER}")
    else:
        if not o.get("enabled", True):
            f.append(f"order-disabled {ORDER} ({o.get('source')})")
        for tok in re.findall(r"(/\S+\.(?:sh|py))", o.get("exec") or ""):
            if not Path(tok).is_file():
                f.append(f"order-exec-missing {ORDER} runs {tok}")
        off = [s for s in ("wall.off", "promotion-cadence.off") if (wall_ci(city) / s).exists()]
        ts = last_run(city, ORDER)
        a = age_min(ts) if ts else None
        if a is None:
            f.append(f"order-never-ran {ORDER}")
        elif a > ORDER_MAX_MIN and not off:
            f.append(f"order-stale {ORDER} last ran {ts} ({a} min ago, want <= {ORDER_MAX_MIN})")

    for rel, n, check, cols in (
        ("dispatch/ledgers/promotion.tsv", 6,
         lambda r: ISO.match(r[0]) and r[1] in PROMO_STATES and (r[2] == "-" or r[2].isdigit()) and (r[3] == "-" or HEX40.match(r[3])),
         "ts state pr sha branch preflight"),
        (".gc/runtime/wall-ci/promotion-cadence.tsv", 5,
         lambda r: ISO.match(r[0]) and r[1] in CADENCE_VERDICTS and (r[2] == "-" or HEX40.match(r[2])) and (r[3] == "-" or r[3].isdigit()),
         "ts verdict sha pr detail"),
    ):
        rs = rows(city / rel)
        if rs is None:
            f.append(f"ledger-missing {rel}")
            continue
        bad = [(i, r) for i, r in enumerate(rs, 1) if len(r) != n or not check(r)]
        for i, r in bad[:3]:
            f.append(f"ledger-row-bad {rel}:{i} want {n} cols ({cols}), got {len(r)}: {chr(9).join(r)[:120]}")
        if len(bad) > 3:
            f.append(f"ledger-row-bad {rel}: {len(bad) - 3} more bad rows")

    fp = set(first_parents(t))
    if not fp:
        f.append(f"trunk-unreadable git rev-list origin/{t} failed in {GL_REPO}")
    else:
        for name in ("ci-green", "deployable"):
            sha, _ = marker(city, name)
            if sha and sha not in fp:
                f.append(f"marker-off-trunk {name}={sha[:8]} is not on origin/{t} first-parent history (local ref)")

    prs, err = promotions()
    if prs is None:
        f.append(f"gh-pr-list-failed {err}")
    else:
        for p in prs:
            if not p["sha"]:
                f.append(f"promotion-unmarked #{p['number']} {p['headRefName']} carries no promotion.sh marker")
            elif p["extra"]:
                f.append(f"promotion-extra-commits #{p['number']} {p['headRefName']} head {p['headRefOid'][:8]} carries "
                         f"{len(p['extra'])} commit(s) beyond the cut: {'; '.join(p['extra'])[:200]}")

    for line in f:
        print(line)
    if not f:
        print("trunk-promotion: clean")
    return 1 if f else 0


# ---------------------------------------------------------------------------------------- state
def state(city):
    t = trunk(city)
    print(f"now                 {now():%Y-%m-%dT%H:%M:%SZ}")
    print(f"trunk               {t}  (dispatch/integration-branch)")
    fp = first_parents(t)
    for name in MARKERS:
        sha, mt = marker(city, name)
        if not sha:
            print(f"{name:<19} (absent)")
            continue
        pos = fp.index(sha) if sha in fp else None
        print(f"{name:<19} {sha[:12]}  written {mt:%Y-%m-%dT%H:%MZ}  "
              f"{'first-parent #%d from trunk tip' % pos if pos is not None else 'NOT on trunk first-parent'}  "
              f"{'in develop' if in_develop(sha) else 'not in develop'}")
    rc, out, _ = gl_git("ls-remote", "origin", "refs/heads/develop", f"refs/heads/{t}", timeout=30)
    for l in out.splitlines():
        sha, ref = l.split("\t")
        print(f"remote {ref:<22} {sha[:12]}")
    for ref in ("develop", t):
        print(f"local origin/{ref:<12} {gl_git('rev-parse', 'origin/' + ref)[1].strip()[:12]}  (no fetch; may trail the remote)")
    rc, out, _ = gl_git("rev-list", "--count", "--first-parent", f"origin/develop..origin/{t}")
    print(f"trunk first-parent commits develop lacks: {out.strip()}")
    print("switches (.gc/runtime/wall-ci/):")
    for s in SWITCHES:
        p = wall_ci(city) / s
        print(f"  {s:<22} {'present: ' + p.read_text().strip()[:80].replace(chr(10), ' ') if p.exists() else 'absent'}")
    prs, err = promotions()
    print("open promotion PRs (release/* -> develop):" if prs is not None else f"gh pr list failed: {err}")
    for p in prs or []:
        q = p["queue_runs"][0] if p["queue_runs"] else None
        print(f"  #{p['number']} {p['headRefName']} head {p['headRefOid'][:8]} marker sha={str(p['sha'])[:8]} "
              f"merge={str(p['merge'])[:8]} held={'yes' if p['held'] else 'no'} queued={'yes' if p['queued'] else 'no'} "
              f"mss={p.get('mergeStateStatus')} labels={','.join(l['name'] for l in p.get('labels') or []) or '-'}")
        if q:
            print(f"      Mergify Merge Queue: {q[0]}/{q[1] or '-'} since {q[2]} \"{q[3] or ''}\"")
        for e in p["extra"]:
            print(f"      EXTRA COMMIT {e}")
    cad = rows(wall_ci(city) / "promotion-cadence.tsv") or []
    print(f"promotion-cadence.tsv ({len(cad)} rows), last 5:")
    for r in cad[-5:]:
        print("  " + "  ".join(c[:40] if i == 2 else c[:90] for i, c in enumerate(r)))
    pl = rows(city / "dispatch/ledgers/promotion.tsv") or []
    print(f"promotion.tsv ({len(pl)} rows), last 6:")
    for r in pl[-6:]:
        print("  " + "  ".join(c[:12] if i == 3 else c[:60] for i, c in enumerate(r)))
    nums = {p["number"] for p in prs or []} | {int(r[2]) for r in pl[-6:] if len(r) > 2 and r[2].isdigit()}
    mj = []
    try:
        for l in (city / "dispatch/ledgers/mergify.jsonl").read_text().splitlines():
            try:
                j = json.loads(l)
            except ValueError:
                continue
            if j.get("pr") in nums:
                mj.append(j)
    except OSError:
        pass
    print(f"mergify.jsonl rows for promotion PRs {sorted(nums)}: {len(mj)}")
    for j in mj[-6:]:
        print(f"  {j.get('at')} {j.get('event')} #{j.get('pr')} {str(j.get('head'))[:8]}")
    ts = last_run(city, ORDER)
    print(f"order {ORDER} last run {ts or '-'} ({age_min(ts) if ts else '-'} min ago)")
    return 0


# ----------------------------------------------------------------------------------- promotable
def load_cadence(city):
    spec = importlib.util.spec_from_file_location("promotion_cadence", city / "dispatch/promotion-cadence.py")
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)
    return pc


def promotable(city):
    pc = load_cadence(city)
    # The module's paths derive from its own file location; point them at --city explicitly.
    pc.WALL_CI = str(wall_ci(city))
    pc.TRUNK_FILE = str(city / "dispatch/integration-branch")
    pc.LEDGER = str(city / "dispatch/ledgers/promotion.tsv")
    pc.GL = str(GL_REPO)
    real_git = pc.git

    def git_no_fetch(*args, ok=(0,)):
        if args and args[0] == "fetch":
            print(f"(skipped: git fetch {' '.join(args[1:])})")
            return real_sub.CompletedProcess(args, 0, "", "")
        return real_git(*args, ok=ok)

    real_sub = pc.subprocess

    class GuardedSubprocess:  # decide() runs promotion.sh and State.mail runs gc mail only when not dry
        CompletedProcess = real_sub.CompletedProcess

        @staticmethod
        def run(cmd, *a, **k):
            if cmd and (cmd[0] in (pc.PROMOTION, pc.GC) or str(cmd[0]).endswith("promotion.sh")):
                raise RuntimeError("refused: %s must never run from this harness" % cmd[0])
            return real_sub.run(cmd, *a, **k)

    pc.git = git_no_fetch
    pc.subprocess = GuardedSubprocess
    t = pc.trunk()
    shas = pc.first_parents(t)
    runs, err = gh_json(["api", f"repos/{GH_REPO}/actions/runs?branch={t}&event=push&per_page=100"])
    if runs is None:
        print(f"gh runs read failed: {err}")
        return 1
    latest = {}
    for r in runs["workflow_runs"]:
        k = (r["head_sha"], r["name"])
        if k not in latest or (r.get("run_attempt", 1), r["created_at"]) > (latest[k].get("run_attempt", 1), latest[k]["created_at"]):
            latest[k] = r
    print(f"trunk {t}; required push workflows: {', '.join(pc.REQUIRED)}")
    print("newest first-parent trunk shas (push CI per required workflow, local reds):")
    shown = 0
    for i, sha in enumerate(shas[:40]):
        concl = [latest.get((sha, w), {}).get("conclusion") or "-" for w in pc.REQUIRED]
        if all(c == "-" for c in concl) and shown >= 3:
            continue
        green = all(c == "success" for c in concl)
        crit = pc.critical_local(sha)
        gr = pc.gate_reds(sha)
        verdict = ("PROMOTABLE" if green and not crit and not gr else
                   "GATE-RED" if green and gr else "CRITICAL" if green and crit else "not push-green")
        print(f"  #{i:<3}{sha[:8]} {'/'.join(c[:7] for c in concl):<34} critical={'y' if crit else 'n'} "
              f"gate_reds={' '.join(gr) or '-'} develop={'has' if pc.in_develop(sha) else 'lacks'} -> {verdict}")
        shown += 1
        if verdict == "PROMOTABLE" or shown >= 12:
            break
    print("cadence decide() in dry mode (fetch skipped, no tsv/json/marker write, no mail, no promotion.sh):")
    a = argparse.Namespace(dry_run=True, spacing_h=4.0, starve_h=24.0)
    st = pc.State(True)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = pc.decide(a, st)
    except pc.Err as e:
        print(buf.getvalue(), end="")
        print(f"PROMOTION-CADENCE ERROR {e}")
        return 1
    print("".join("  " + l + "\n" for l in buf.getvalue().splitlines()), end="")
    print(f"decide() exit {rc}; ci-green marker on disk: {marker(city, 'ci-green')[0] or '(absent)'}")
    return 0


# ----------------------------------------------------------------------------------------- gate
def gate4_script(city):
    src = (city / "dispatch/merge-train.sh").read_text()
    i = src.find("gate4_lens_evidence() {")
    j = src.find("<<'PY'\n", i)
    k = src.find("\nPY\n", j)
    if i < 0 or j < 0 or k < 0:
        return None
    return src[j + len("<<'PY'\n"):k + 1]


def gate(city):
    script = gate4_script(city)
    if script is None:
        print("gate4_lens_evidence python heredoc not found in dispatch/merge-train.sh")
        return 1
    fleet = city / ".gc/runtime/fleet"
    jobs, receipts = fleet / "jobs", fleet / "receipts"
    prs, err = promotions()
    if prs is None:
        print(f"gh pr list failed: {err}")
        return 1
    if not prs:
        print("no open promotion PR (release/* -> develop): gate is verified-unreachable")
        return 0
    restamp_src = (city / "dispatch/migration-restamp.py").read_text()
    restamp_skips = 'a.cmd == "queue" and a.branch.startswith("release/")' in restamp_src
    for p in prs:
        n, head = str(p["number"]), p["headRefOid"]
        print(f"#{n} {p['headRefName']} head {head[:8]} marker sha={str(p['sha'])[:8]} merge={str(p['merge'])[:8]} "
              f"held={'yes' if p['held'] else 'no'} queued={'yes' if p['queued'] else 'no'} extra_commits={len(p['extra'])}")
        env = dict(os.environ, JOBS=str(jobs), RECEIPTS=str(receipts), REVIEWS=str(fleet / "reviews"),
                   WAIVERS=str(fleet / "trains"), GATE_PR=n, GATE_HEAD=head, GATE_HEAD_ALIASES=head)
        rc, out, e = run(["python3", "-"], env=env, stdin=script, timeout=60)
        verdict = out.strip().splitlines()[-1] if out.strip() else f"(no output; rc={rc} {e.strip()[:120]})"
        print(f"  gate-4 evidence: {verdict.replace('|', ': ', 1)}  (aliases = head only: head_aliases fetches)")
        pat = re.compile(r"^Review PR #" + re.escape(n) + r", pinned head ([0-9a-fA-F]{7,40})\b")
        lenses = []
        for path in glob.glob(str(jobs / "*.json")):
            try:
                j = json.load(open(path))
            except (OSError, ValueError):
                continue
            m = pat.match(str(j.get("body") or ""))
            if j.get("class") != "read" or not m:
                continue
            did = os.path.basename(path)[:-5]
            try:
                rec = json.load(open(receipts / f"{did}.json"))
            except (OSError, ValueError):
                rec = {}
            lenses.append((float(j.get("created") or 0), did, j.get("title"), m.group(1), rec.get("verdict"), rec.get("failure_class") or ("withdrawn" if rec.get("verdict") == "WITHDRAWN" or str(rec.get("report") or "").startswith("Withdrawn by") else None)))
        for c, did, title, pin, v, fc in sorted(lenses):
            at = "at head" if head.startswith(pin.lower()) else f"at {pin[:8]}"
            note = ""
            if fc == "withdrawn":
                named = did[:8] in verdict
                note = ("  WITHDRAWN: the gate names it as a verdict (reads as FAIL; since fix D a withdrawn lens must read NEEDS: regression)"
                        if named and "NEEDS" not in verdict else "  WITHDRAWN: not named by the gate verdict (no evidence either way)")
            print(f"    lens {did[:8]} {title:<12} {at:<12} receipt={v or '(none: live)'} failure_class={fc or '-'}{note}")
        if not lenses:
            print("    (no lens job pinned for this PR)")
        if gl_git("cat-file", "-e", f"{head}^{{commit}}")[0] != 0:
            print(f"  migration-order: head {head[:8]} not in the local clone (no fetch): unreadable here")
        else:
            rc, out, e = run(["python3", str(city / "dispatch/migration-order.py"), head, "develop", "--repo", str(GL_REPO)], timeout=60)
            print(f"  migration-order.py: {'clean' if rc == 0 and not out.strip() else out.strip()[:300] or e.strip()[:200]} (exit {rc})")
        print(f"  restamp at queue: {'skipped for release/* (migration-restamp.py queue returns 0; RELEASE_ORDER_EXCEPTIONS judges in Mergify)' if restamp_skips else 'NOT skipped: migration-restamp.py lacks the release/* guard'}")
        print("  proves: gate-4 reads the fleet's own lens pins and receipts for this exact head; migration-order is "
              "the ready-time finding land.sh notes for a single PR. Neither proves Mergify's checks pass.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", default=os.environ.get("GC_CITY") or os.path.expanduser("~/city"))
    ap.add_argument("cmd", choices=["doctor", "state", "promotable", "gate"])
    a = ap.parse_args()
    city = Path(a.city).expanduser().resolve()
    sys.exit({"doctor": doctor, "state": state, "promotable": promotable, "gate": gate}[a.cmd](city))


if __name__ == "__main__":
    main()
