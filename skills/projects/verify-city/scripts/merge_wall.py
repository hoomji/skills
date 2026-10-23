#!/usr/bin/env python3
"""merge_wall.py -- read-only verification harness for trunk landing and the per-PR develop gate.

Subcommands (all read-only: file reads, `gc order list/history`, `git rev-parse/merge-base/
ls-remote`, `gh pr list/view`; never land.sh, wall-land.sh, queue-ready.sh, merge-queue.sh run,
gc order run/check, mail, bead writes or pushes):

  doctor      one line per drift finding, exit 1 on any; else `merge-wall: clean`, exit 0
  state       the wall as it stands: integration branch, switches, tips, last landing and its age,
              verify/deploy state, last red rows, wall orders (enabled, last run)
  holds       red-heads.tsv rows against each PR's current head, and whether red-fix-rounds filed
              a round at that head (gh pr view per held PR)
  candidates  what the next wall-land run would take: gh pr list on both bases piped through
              dispatch/wall-candidates.py (imported, not run), with the landed/held reasoning

--city defaults to $GC_CITY, then ~/city.
"""
import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

GH_REPO = os.environ.get("GH_REPO", "Uniblock-dev/Gateway-LLM")
GL_REPO = Path(os.environ.get("WALL_REPO", os.path.expanduser("~/projects/Gateway-LLM")))
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

# Scripts the feature names: path -> must be executable (wall-checks.sh is sourced, not run).
SCRIPTS = {
    "dispatch/merge-queue.sh": True, "dispatch/land.sh": True, "dispatch/merge-train.sh": True,
    "dispatch/queue-ready.sh": True, "dispatch/wall-land.sh": True, "dispatch/wall-ready.sh": True,
    "dispatch/wall-deploy.sh": True, "dispatch/wall-candidates.py": True,
    "dispatch/gitbutler-radar.sh": True, "dispatch/kept-beads.py": True,
    "dispatch/red-fix-rounds.py": True, "dispatch/tip-red-rounds.py": True,
    "dispatch/develop-watch.py": True, "orders/scripts/conflict-sweep.sh": True,
    "orders/scripts/conflict-sweep.py": True, "orders/scripts/elapsed-check.sh": True,
    "dispatch/wall-checks.sh": False,
}
# Orders the feature owns: name -> max minutes since its last run while the trunk orders run (no wall.off).
WALL_ORDERS = {"wall-land": 60, "wall-verify": 120, "wall-deploy": 120, "pr-conflict-sweep": 30,
               "red-fix-rounds": 60, "tip-red-rounds": 120, "develop-watch": 60}
OTHER_ORDERS = {"queue-ready": 30, "kept-beads": 60}
# Subcommands docs and seat prompts drive: script -> case arms that must exist.
ARMS = {
    "dispatch/merge-train.sh": ["ready", "prune", "pin-aliases", "repin-waiver", "lane-blockers"],
    "dispatch/merge-queue.sh": ["status", "plan", "run", "metrics", "snapshot", "zero-lens", "hold",
                                "held", "release"],
    "dispatch/wall-ready.sh": ["land", "verify"],
}
# Ledger shapes (column counts) per the writers' printf lines.
LEDGERS = {
    "dispatch/ledgers/wall-land.tsv": ({5}, "time pr head tip host"),
    ".gc/runtime/wall-ci/red-heads.tsv": ({3, 4}, "pr head time [steps]"),
    ".gc/runtime/wall-ci/land-all-red.tsv": ({4}, "time tip prs checks"),
    ".gc/runtime/wall-ci/wall-tip-red.tsv": ({5}, "time tip fails files log"),
    "dispatch/ledgers/wall-deploy.tsv": ({5}, "time worker sha verdict host"),
}


def run(cmd, cwd=None, timeout=90):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def now():
    return dt.datetime.now(dt.timezone.utc)


def age_min(ts):
    try:
        t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return int((now() - t).total_seconds() // 60)
    except (ValueError, AttributeError):
        return None


def rows(path):
    try:
        return [l.rstrip("\n").split("\t") for l in path.read_text().splitlines() if l.strip()]
    except OSError:
        return None


def integration(city):
    try:
        return (city / "dispatch/integration-branch").read_text().split()[0]
    except (OSError, IndexError):
        return "develop"


def orders(city):
    rc, out, err = run(["gc", "order", "list", "--json", "--city", str(city)])
    if rc != 0:
        return None, (err or out).strip()[:200]
    try:
        return {o["name"]: o for o in json.loads(out).get("orders", [])}, ""
    except (ValueError, KeyError) as e:
        return None, f"unparseable gc order list --json: {e}"


def last_run(city, name):
    rc, out, _ = run(["gc", "order", "history", name, "--limit", "1", "--json", "--city", str(city)])
    if rc != 0:
        return None
    try:
        e = json.loads(out).get("entries") or []
        return e[0].get("executed") if e else None
    except ValueError:
        return None


def gl_git(*args, timeout=60):
    return run(["git", "-C", str(GL_REPO), *args], timeout=timeout)


def city_toml(city):
    try:
        return tomllib.loads((city / "city.toml").read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return None


def formula_base_branches(conf):
    rigs = conf.get("rigs")
    out = []
    for r in (rigs if isinstance(rigs, list) else [rigs] if isinstance(rigs, dict) else []):
        fv = (r or {}).get("formula_vars") or {}
        if "base_branch" in fv:
            out.append(fv["base_branch"])
    return out


def monitor_bases(conf):
    out = []
    for m in conf.get("github", {}).get("pr_monitor", []) or []:
        if m.get("repo") == "Gateway-LLM":
            out.append(m.get("base_branches") or [])
    return out


def doc_section(city, start, stop_re=r"^## ", doc="docs/trunk-and-promotion.md"):
    try:
        text = (city / doc).read_text()
    except OSError:
        return ""
    i = text.find(start)
    if i < 0:
        return ""
    m = re.search(stop_re, text[i + len(start):], re.M)
    return text[i:i + len(start) + (m.start() if m else len(text))]


# --------------------------------------------------------------------------------------- doctor
def doctor(city):
    f = []
    wall_ci = city / ".gc/runtime/wall-ci"
    I = integration(city)
    walled = I != "develop"

    for rel, need_x in SCRIPTS.items():
        p = city / rel
        if not p.is_file():
            f.append(f"script-missing {rel}")
        elif need_x and not os.access(p, os.X_OK):
            f.append(f"script-not-executable {rel}")

    for doc in ("docs/trunk-and-promotion.md", "docs/merge-queue.md", "docs/merge-train.md"):
        try:
            text = (city / doc).read_text()
        except OSError:
            f.append(f"doc-missing {doc}")
            continue
        for tok in sorted(set(re.findall(r"\b((?:dispatch|orders/scripts)/[A-Za-z0-9_./-]+)", text))):
            tok = tok.rstrip(".,;:)")
            if tok.endswith("-") or tok.startswith("dispatch/ledgers/") or "<" in tok:
                continue
            if not (city / tok).exists():
                f.append(f"doc-path-missing {doc} names {tok}")

    for rel, arms in ARMS.items():
        try:
            src = (city / rel).read_text()
        except OSError:
            continue
        for a in arms:
            if not re.search(rf"^\s+(?:[a-z|-]+\|)?{re.escape(a)}(?:\|[a-z|-]+)?\)", src, re.M):
                f.append(f"subcommand-missing {rel} has no case arm '{a}'")

    ords, err = orders(city)
    if ords is None:
        f.append(f"gc-order-list-failed {err}")
        ords = {}
    else:
        # The trunk method page names every trunk order ("The `wall-land` order ...").
        section = doc_section(city, "# Trunk and promotion", stop_re=r"^## History")
        named = set(re.findall(r"order `([a-z0-9-]+)`|`([a-z0-9-]+)` order", section))
        for name in sorted({a or b for a, b in named}):
            if name not in ords:
                f.append(f"doc-order-missing docs/trunk-and-promotion.md names order {name}; gc order list lacks it")
        for name in list(WALL_ORDERS) + list(OTHER_ORDERS):
            o = ords.get(name)
            if not o:
                f.append(f"order-missing {name}")
                continue
            if not o.get("enabled", True):
                f.append(f"order-disabled {name} ({o.get('source')})")
            ex = (o.get("exec") or "").replace("$GC_CITY_PATH", str(city))
            for tok in re.findall(r"(/\S+\.(?:sh|py))", ex):
                if not Path(tok).is_file():
                    f.append(f"order-exec-missing {name} runs {tok}")

    for rel, (ncols, cols) in LEDGERS.items():
        rs = rows(city / rel)
        if rs is None:
            # wall-deploy.tsv appears with the first deploy, which needs a green tip.
            if rel.endswith("wall-deploy.tsv") and not (wall_ci / "green").exists():
                continue
            if walled:
                f.append(f"ledger-missing {rel}")
            continue
        bad = 0
        for i, r in enumerate(rs, 1):
            ok = len(r) in ncols
            if ok and rel.endswith("wall-land.tsv"):
                ok = bool(ISO.match(r[0]) and r[1].isdigit() and HEX40.match(r[2]) and HEX40.match(r[3]))
            elif ok and rel.endswith("red-heads.tsv"):
                ok = bool(r[0].isdigit() and HEX40.match(r[1]) and ISO.match(r[2]))
            elif ok:
                ok = bool(ISO.match(r[0]))
            if not ok:
                bad += 1
                if bad <= 3:
                    f.append(f"ledger-row-bad {rel}:{i} want {sorted(ncols)} cols ({cols}), got {len(r)}: {chr(9).join(r)[:120]}")
        if bad > 3:
            f.append(f"ledger-row-bad {rel}: {bad - 3} more bad rows")

    # Switch agreement: dispatch/integration-branch vs wall.off, queue-ready.off, city.toml, wall-land.sh.
    off = (wall_ci / "wall.off").exists()
    qr_off = (city / ".gc/runtime/fleet/merge-queue/queue-ready.off").exists()
    if walled and off:
        f.append(f"switch-split integration-branch={I} but wall.off is present: wall autopilot stopped (big-bang in progress?)")
    if not walled and not off:
        f.append("switch-split integration-branch=develop but wall.off absent: wall orders still land on wall/develop")
    if walled and not off and not qr_off:
        f.append("switch-split wall stands but queue-ready.off is absent: develop queueing runs during the wall")
    if not walled and qr_off:
        f.append("switch-split integration-branch=develop but queue-ready.off is present: nothing queues in Mergify")
    conf = city_toml(city)
    if conf is None:
        f.append("city-toml-unreadable city.toml")
    else:
        for b in formula_base_branches(conf):
            if b != I:
                f.append(f"switch-split city.toml rigs.formula_vars.base_branch={b} vs integration-branch={I}")
        for bases in monitor_bases(conf):
            if I not in bases:
                f.append(f"switch-split city.toml github.pr_monitor.base_branches {bases} lacks {I}")
    try:
        src = (city / "dispatch/wall-land.sh").read_text()
        m = re.search(r"^WALL=([^;\s]+)", src, re.M)
        if m and m.group(1).startswith("$"):
            # Read from dispatch/integration-branch; only the ${WALL:-...} fallback is literal.
            m = re.search(r"WALL=\$\{WALL:-([^}]+)\}", src)
        if walled and m and m.group(1) != I:
            f.append(f"switch-split dispatch/wall-land.sh hardcodes WALL={m.group(1)} but integration-branch={I}")
    except OSError:
        pass

    if walled and not off:
        for name, mx in WALL_ORDERS.items():
            if name not in ords:
                continue
            ts = last_run(city, name)
            a = age_min(ts) if ts else None
            if a is None:
                f.append(f"order-never-ran {name}")
            elif a > mx:
                f.append(f"order-stale {name} last ran {ts} ({a} min ago, want <= {mx})")
        wl = rows(city / "dispatch/ledgers/wall-land.tsv") or []
        if wl:
            tip = wl[-1][3]
            rc, wall_tip, _ = gl_git("rev-parse", f"origin/{I}")
            wall_tip = wall_tip.strip()
            if rc == 0 and wall_tip and tip != wall_tip:
                rc2, _, _ = gl_git("merge-base", "--is-ancestor", tip, wall_tip)
                if rc2 == 1:
                    f.append(f"wall-tip-diverged last wall-land.tsv tip {tip[:8]} is not an ancestor of origin/{I} {wall_tip[:8]} (local ref)")
        try:
            verified = (wall_ci / "verified").read_text().strip()
        except OSError:
            verified = ""
        green = (wall_ci / "green").read_text().strip() if (wall_ci / "green").exists() else ""
        reds = {r[1] for r in rows(wall_ci / "wall-tip-red.tsv") or [] if len(r) > 1}
        if verified and verified != green and verified not in reds:
            f.append(f"verify-unrecorded verified={verified[:8]} is neither green nor a wall-tip-red.tsv row")

    for line in f:
        print(line)
    if not f:
        print("merge-wall: clean")
    return 1 if f else 0


# ---------------------------------------------------------------------------------------- state
def state(city):
    wall_ci = city / ".gc/runtime/wall-ci"
    I = integration(city)
    print(f"now                 {now():%Y-%m-%dT%H:%M:%SZ}")
    print(f"integration-branch  {I}  (dispatch/integration-branch)")
    print(f"wall.off            {'present' if (wall_ci / 'wall.off').exists() else 'absent'}")
    print(f"verify.off          {'present' if (wall_ci / 'verify.off').exists() else 'absent'}")
    qr = city / ".gc/runtime/fleet/merge-queue/queue-ready.off"
    print(f"queue-ready.off     {'present: ' + qr.read_text().strip()[:140] if qr.exists() else 'absent'}")
    conf = city_toml(city) or {}
    print(f"city.toml           base_branch={formula_base_branches(conf)} pr_monitor.base_branches={monitor_bases(conf)}")
    rc, out, _ = gl_git("ls-remote", "origin", "refs/heads/develop", f"refs/heads/{I}", timeout=30)
    for l in out.splitlines():
        sha, ref = l.split("\t")
        print(f"remote {ref:<22} {sha}")
    wl = rows(city / "dispatch/ledgers/wall-land.tsv") or []
    if wl:
        r = wl[-1]
        print(f"last wall-land row  {r[0]} pr #{r[1]} head {r[2][:8]} tip {r[3][:8]} host {r[4]} ({age_min(r[0])} min ago); {len(wl)} rows")
        today = now().strftime("%Y-%m-%d")
        print(f"landed today        {sum(1 for x in wl if x[0].startswith(today))} rows")
    for name in ("verified", "green"):
        p = wall_ci / name
        print(f"{name:<19} {p.read_text().strip()[:12] if p.exists() else '(absent)'}")
    for rel in ("wall-tip-red.tsv", "land-all-red.tsv", "red-heads.tsv"):
        rs = rows(wall_ci / rel) or []
        last = rs[-1] if rs else []
        print(f"{rel:<19} {len(rs)} rows; last: {chr(9).join(c[:60] for c in last[:4])}")
    dep = wall_ci / "deployed"
    print(f"deployed/           {', '.join(f'{p.name}={p.read_text().strip()[:8]}' for p in sorted(dep.glob('*'))) if dep.is_dir() else '(absent: nothing deployed yet)'}")
    ords, err = orders(city)
    print("orders (enabled, last run):")
    for name in list(WALL_ORDERS) + list(OTHER_ORDERS) + ["wall-e2e", "tip-red-revert"]:
        o = (ords or {}).get(name)
        ts = last_run(city, name) if o else None
        en = "MISSING" if not o else ("enabled" if o.get("enabled", True) else "DISABLED")
        print(f"  {name:<18} {en:<8} {ts or '-'} ({age_min(ts) if ts else '-'} min ago)")
    return 0


# ---------------------------------------------------------------------------------------- holds
def holds(city):
    rh = rows(city / ".gc/runtime/wall-ci/red-heads.tsv") or []
    try:
        rfr = json.loads((city / ".gc/runtime/fleet/red-fix-rounds.json").read_text())
    except (OSError, ValueError):
        rfr = {}
    latest = {}
    for r in rh:
        latest[r[0]] = r  # last hold per PR
    print("pr\theld_head\theld_at\tsteps\tcurrent_head\tstate\tverdict\tfix_round_at_head")
    for pr, r in latest.items():
        rc, out, _ = run(["gh", "pr", "view", "-R", GH_REPO, pr, "--json", "headRefOid,state,baseRefName"], timeout=30)
        try:
            j = json.loads(out)
        except ValueError:
            j = {}
        cur = j.get("headRefOid", "?")
        verdict = "HELD" if cur == r[1] else "MOVED"
        if j.get("state") and j["state"] != "OPEN":
            verdict = j["state"]
        fr = rfr.get(pr) or {}
        filed = "yes job " + str(fr.get("job", "-")) if fr.get("head") == r[1] else "no"
        print(f"#{pr}\t{r[1][:8]}\t{r[2]}\t{r[3] if len(r) > 3 else '-'}\t{cur[:8]}\t{j.get('state', '?')}/{j.get('baseRefName', '?')}\t{verdict}\t{filed}")
    return 0


# ----------------------------------------------------------------------------------- candidates
def candidates(city):
    """Mirror wall-ready.sh land: one PR query (every base), then wall-candidates.py's candidates() with
    the same landed (git ancestry of origin/<trunk>), held and live-lane inputs. Read-only."""
    rc, out, err = run(["gh", "pr", "list", "-R", GH_REPO, "--state", "open", "--author", "hoomji", "--limit", "300",
                        "--json", "number,isDraft,labels,createdAt,headRefOid,headRefName,baseRefName,author"], timeout=60)
    if rc != 0:
        print(f"gh pr list failed: {err.strip()[:200]}")
        return 1
    prs = json.loads(out)
    by_base = {}
    for p in prs:
        by_base[p.get("baseRefName")] = by_base.get(p.get("baseRefName"), 0) + 1
    print("open hoomji PRs: %d (%s)" % (len(prs), ", ".join(f"{b} {n}" for b, n in sorted(by_base.items()))))
    spec = importlib.util.spec_from_file_location("wall_candidates", city / "dispatch/wall-candidates.py")
    wc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wc)
    landed = wc.on_trunk(wc.wall_repo(), wc.trunk_name())
    held = wc.held_heads(str(city / ".gc/runtime/wall-ci/red-heads.tsv"))
    live = wc.fleet_facts(city / ".gc/runtime/fleet")["live"]
    skipped = {}
    picks = wc.candidates(prs, landed, held, live, skip=lambda n, why: skipped.__setitem__(n, why))
    print(f"next wall-land candidates before the validated/CI gates ({len(picks)}): {','.join(map(str, picks)) or '(none)'}")
    for p in sorted(prs, key=lambda p: p["number"]):
        n, h = p["number"], p.get("headRefOid", "")
        why = ("draft" if p.get("isDraft") else "held at head" if h in held.get(str(n), ())
               else "landed at head" if landed(h) else skipped.get(n) or "CANDIDATE")
        print(f"  #{n}\t{p.get('baseRefName')}\t{h[:8]}\t{why}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", default=os.environ.get("GC_CITY") or os.path.expanduser("~/city"))
    ap.add_argument("cmd", choices=["doctor", "state", "holds", "candidates"])
    a = ap.parse_args()
    city = Path(a.city).expanduser().resolve()
    sys.exit({"doctor": doctor, "state": state, "holds": holds, "candidates": candidates}[a.cmd](city))


if __name__ == "__main__":
    main()
