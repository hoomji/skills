#!/usr/bin/env python3
"""verify-city harness for the gc-promotion feature (read-only).

  gc_promotion.py [--city DIR] [--fork DIR] doctor
  gc_promotion.py [--city DIR] [--fork DIR] installed
  gc_promotion.py [--city DIR] [--fork DIR] patches
  gc_promotion.py [--city DIR] [--fork DIR] shadow

--city defaults to $GC_CITY or ~/city. --fork defaults to $GC_UPGRADE_FORK or
~/src/gascity-city15x, the checkout dispatch/gc_upgrade.py reads (a worktree of ~/src/gascity;
both see the same refs).

doctor     one line per finding, exit 1 on any; else "gc-promotion: clean", exit 0.
installed  live gc version/commit, where ~/go/bin/gc resolves, supervisor and gc process
           names against GT_PROCESS_NAMES, the rollback copy, bd against the go.mod pair.
patches    each dispatch/city-patches.toml entry: merge-base ancestry and the promoter's own
           presence mode (gc_upgrade.patch_presence) against the installed commit.
shadow     timer state and schedule, last service result, latest shadow report summary.

Never builds, installs, fetches, restarts or writes. Never prints process environments
(the supervisor unit carries provider keys).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path

HOME = Path.home()
LIVE = HOME / "go/bin/gc"
PATH_GC = HOME / ".local/bin/gc"
STAGED = HOME / "src/gc-staged"
UNIT = "gascity-supervisor.service"
SHADOW_TIMER = "gc-shadow-build.timer"
SHADOW_SERVICE = "gc-shadow-build.service"
SHADOW_MAX_AGE_H = 36


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def git(fork, *args):
    return sh(["git", "-C", str(fork), *args], timeout=300)


def unit_prop(unit, prop):
    return sh(["systemctl", "--user", "show", unit, "-p", prop, "--value"])[1]


def strip_d(path: Path) -> Path:
    """<x>.d/gc -> <x> (the gc-promote hard-link layout, a085900f2)."""
    if path.name == "gc" and path.parent.name.endswith(".d"):
        return path.parent.with_name(path.parent.name[:-2])
    return path


def gc_version():
    rc, out, _ = sh([str(LIVE), "version", "--json"], timeout=30)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def bd_version():
    rc, out, _ = sh(["bd", "version"], timeout=30)
    m = re.search(r"(\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?)", out)
    return (m.group(1) if m else None), out


def gomod_beads(fork, sha):
    rc, out, _ = git(fork, "show", f"{sha}:go.mod")
    m = re.search(r"github\.com/steveyegge/beads\s+v(\S+)", out) if rc == 0 else None
    return m.group(1) if m else None


def proc_env_value(pid, key):
    try:
        raw = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:
        return None
    for item in raw.split(b"\0"):
        if item.startswith(key.encode() + b"="):
            return item.split(b"=", 1)[1].decode(errors="replace")
    return None


def gc_processes():
    """Processes whose executable is a staged gc or the live symlink target."""
    rows = []
    staged = str(STAGED) + "/"
    for d in glob.glob("/proc/[0-9]*"):
        pid = d.rsplit("/", 1)[1]
        try:
            exe = os.readlink(f"{d}/exe")
        except OSError:
            continue
        if not (exe.startswith(staged) or exe.startswith(str(HOME / "go/bin/gc"))):
            continue
        try:
            comm = Path(f"{d}/comm").read_text().strip()
            args = Path(f"{d}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except OSError:
            continue
        names = proc_env_value(pid, "GT_PROCESS_NAMES")
        rows.append({"pid": int(pid), "comm": comm, "exe": exe, "args": args[:120],
                     "gt_process_names": names})
    return sorted(rows, key=lambda r: r["pid"])


def promote_records(city):
    out = []
    for f in sorted((city / ".gc/runtime/gc-upgrade").glob("promote-*.json")):
        try:
            d = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        d["_file"] = f.name
        out.append(d)
    return out


def rollback_copy(city, live_target):
    """Newest installed promote record whose `previous` is a binary other than the live one."""
    for rec in reversed(promote_records(city)):
        if not rec.get("installed"):
            continue
        prev = (rec.get("steps") or {}).get("previous")
        if not prev:
            continue
        if Path(os.path.realpath(prev)) == live_target:
            continue
        p = Path(prev)
        return {"record": rec["_file"], "previous": prev,
                "exists": p.is_file() and os.access(p, os.X_OK)}
    return None


def installed_facts(city, fork):
    f = {}
    f["live_link"] = os.readlink(LIVE) if LIVE.is_symlink() else None
    f["live_real"] = os.path.realpath(LIVE)
    live_target = strip_d(Path(f["live_real"]))
    f["live_target"] = str(live_target)
    f["hard_link_ok"] = (Path(f["live_real"]).exists() and live_target.exists()
                         and os.path.samefile(f["live_real"], live_target))
    f["path_gc_link"] = os.readlink(PATH_GC) if PATH_GC.is_symlink() else None
    f["path_gc_real"] = os.path.realpath(PATH_GC)
    v = gc_version()
    f["gc_version"] = v.get("version") if v else None
    f["gc_commit_short"] = v.get("commit") if v else None
    f["gc_built"] = v.get("date") if v else None
    rc, full, _ = git(fork, "rev-parse", "--verify", "--quiet", f"{f['gc_commit_short']}^{{commit}}") \
        if f["gc_commit_short"] else (1, "", "")
    f["gc_commit"] = full if rc == 0 else None
    rc, nx, _ = git(fork, "rev-parse", "--verify", "--quiet", "origin/city-next^{commit}")
    f["origin_city_next"] = nx if rc == 0 else None
    if f["gc_commit"] and f["origin_city_next"]:
        rc, cnt, _ = git(fork, "rev-list", "--count", f"{f['gc_commit']}..{f['origin_city_next']}")
        f["city_next_ahead_of_installed"] = int(cnt) if rc == 0 else None
    # supervisor
    pid = unit_prop(UNIT, "MainPID")
    f["supervisor_active"] = unit_prop(UNIT, "ActiveState")
    f["supervisor_pid"] = int(pid) if pid.isdigit() else 0
    if f["supervisor_pid"]:
        try:
            f["supervisor_exe"] = os.readlink(f"/proc/{pid}/exe")
            f["supervisor_comm"] = Path(f"/proc/{pid}/comm").read_text().strip()
        except OSError:
            f["supervisor_exe"] = f["supervisor_comm"] = None
    f["gc_processes"] = gc_processes()
    # bd pair
    f["bd_version"], f["bd_version_raw"] = bd_version()
    f["bd_path"] = sh(["sh", "-c", "command -v bd"])[1] or None
    f["gomod_beads"] = gomod_beads(fork, f["gc_commit"]) if f["gc_commit"] else None
    f["rollback"] = rollback_copy(city, live_target)
    f["staged"] = sorted(p.name for p in STAGED.iterdir()) if STAGED.is_dir() else []
    return f


def load_gc_upgrade(city):
    os.environ.setdefault("GC_UPGRADE_CITY", str(city))
    sys.dont_write_bytecode = True  # read-only: no __pycache__ in the city
    sys.path.insert(0, str(city / "dispatch"))
    try:
        import gc_upgrade  # noqa: PLC0415  (the promoter's own gate code)
        return gc_upgrade
    except Exception as e:  # report, fall back to plain ancestry
        print(f"note: cannot import {city}/dispatch/gc_upgrade.py ({e}); ancestry only", file=sys.stderr)
        return None


def patch_rows(city, fork, commit):
    with open(city / "dispatch/city-patches.toml", "rb") as fh:
        entries = tomllib.load(fh).get("patch", [])
    G = load_gc_upgrade(city)
    subjects = G.subjects_since(fork, commit) if G else None
    rows = []
    for e in entries:
        e.setdefault("aliases", [])
        e.setdefault("upstream_pr", 0)
        e.setdefault("status", "carry")
        anc = None
        for s in [e["sha"], *e["aliases"]]:
            rc, full, _ = git(fork, "rev-parse", "--verify", "--quiet", f"{s}^{{commit}}")
            if rc != 0:
                continue
            if git(fork, "merge-base", "--is-ancestor", full, commit)[0] == 0:
                anc = s[:9]
                break
        mode = None
        if e["status"] == "retired":
            mode = "retired"
        elif G:
            mode = G.patch_presence(fork, commit, e, subjects)
        elif anc:
            mode = "ancestor"
        rows.append({"sha": e["sha"][:9], "status": e["status"], "upstream_pr": e["upstream_pr"],
                     "ancestor_via": anc, "present": mode, "subject": e.get("subject", "")[:70]})
    return rows


def shadow_facts(city):
    f = {
        "timer_active": unit_prop(SHADOW_TIMER, "ActiveState"),
        "timer_enabled": unit_prop(SHADOW_TIMER, "UnitFileState"),
        "timer_calendar": sh(["systemctl", "--user", "cat", SHADOW_TIMER])[1],
        "next": unit_prop(SHADOW_TIMER, "NextElapseUSecRealtime"),
        "last_trigger": unit_prop(SHADOW_TIMER, "LastTriggerUSec"),
        "service_result": unit_prop(SHADOW_SERVICE, "Result"),
        "service_status": unit_prop(SHADOW_SERVICE, "ExecMainStatus"),
        "service_exit": unit_prop(SHADOW_SERVICE, "ExecMainExitTimestamp"),
        "service_active": unit_prop(SHADOW_SERVICE, "ActiveState"),
    }
    m = re.search(r"^OnCalendar=(.*)$", f["timer_calendar"], re.M)
    f["timer_calendar"] = m.group(1) if m else None
    rep = city / ".gc/runtime/gc-upgrade/latest-shadow.json"
    f["report"] = os.path.realpath(rep) if rep.exists() else None
    if f["report"]:
        f["report_age_h"] = round((time.time() - os.path.getmtime(f["report"])) / 3600, 1)
        try:
            d = json.loads(Path(f["report"]).read_text())
            f["stamp"] = d.get("stamp")
            f["base"] = d.get("base")
            f["base_sha"] = d.get("base_short")
            f["summary"] = d.get("summary")
            f["interrupted_runs"] = [r.get("run") for r in d.get("interrupted_runs") or []]
        except (OSError, json.JSONDecodeError) as e:
            f["report_error"] = str(e)
    rc, out, _ = sh(["journalctl", "--user", "-u", SHADOW_SERVICE, "-n", "200", "--no-pager", "-o", "cat"])
    f["journal_last_summary"] = next((ln for ln in reversed(out.splitlines()) if ln.startswith("gc-shadow:")), None)
    return f


# ---------------------------------------------------------------- commands

def cmd_installed(a):
    f = installed_facts(a.city, a.fork)
    print(json.dumps(f, indent=1, default=str))
    return 0


def cmd_patches(a):
    v = gc_version()
    short = v.get("commit") if v else None
    rc, commit, _ = git(a.fork, "rev-parse", "--verify", "--quiet", f"{short}^{{commit}}")
    if not short or rc != 0:
        print(f"cannot resolve installed commit {short!r} in {a.fork}")
        return 1
    print(f"installed {commit[:9]} ({v.get('version')}); fork {a.fork}")
    print(f"{'sha':9}  {'status':10} {'pr':>5}  {'ancestor':9}  {'present':11} subject")
    for r in patch_rows(a.city, a.fork, commit):
        print(f"{r['sha']:9}  {r['status']:10} {r['upstream_pr'] or '':>5}  {r['ancestor_via'] or '-':9}  "
              f"{r['present'] or 'MISSING':11} {r['subject']}")
    return 0


def cmd_shadow(a):
    print(json.dumps(shadow_facts(a.city), indent=1, default=str))
    return 0


def cmd_doctor(a):
    findings = []
    add = findings.append
    f = installed_facts(a.city, a.fork)
    # live binary layout
    if not f["live_link"]:
        add(f"live: {LIVE} is not a symlink (gc-promote swaps by symlink)")
    elif not (Path(f["live_real"]).name == "gc" and Path(f["live_real"]).parent.name.endswith(".d")):
        add(f"live: {LIVE} -> {f['live_real']} is not a <staged>.d/gc hard link; processes will be named "
            f"{Path(f['live_real']).name!r}, not gc")
    elif not f["hard_link_ok"]:
        add(f"live: {f['live_real']} is not the same file as {f['live_target']}")
    if os.path.realpath(PATH_GC) != f["live_real"]:
        add(f"live: {PATH_GC} resolves to {f['path_gc_real']}, not the live {f['live_real']}")
    if not f["gc_version"]:
        add(f"live: `{LIVE} version --json` failed")
    elif not f["gc_commit"]:
        add(f"live: installed commit {f['gc_commit_short']!r} not found in {a.fork}")
    elif Path(f["live_target"]).name != f"gc-{f['gc_commit_short']}" and \
            not Path(f["live_target"]).name.startswith(f"gc-{f['gc_commit_short'][:9]}"):
        add(f"live: staged name {Path(f['live_target']).name} disagrees with reported commit {f['gc_commit_short']}")
    # supervisor and process names
    if f["supervisor_active"] != "active":
        add(f"supervisor: {UNIT} is {f['supervisor_active']}")
    elif f.get("supervisor_exe") and os.path.realpath(f["supervisor_exe"].removesuffix(" (deleted)")) != f["live_real"]:
        add(f"supervisor: pid {f['supervisor_pid']} runs {f['supervisor_exe']}, not the live {f['live_real']} "
            "(swapped without restart?)")
    for p in f["gc_processes"]:
        # Every staged-gc process must be named gc (a085900f2). GT_PROCESS_NAMES is the
        # session's agent list: gc hooks inside a claude session inherit "node,claude", so it
        # only constrains sessions whose agent is gc itself (the control-dispatcher).
        names = [n for n in (p["gt_process_names"] or "").split(",") if n]
        if p["comm"] != "gc":
            add(f"process: pid {p['pid']} comm {p['comm']!r} is not 'gc' ({p['args']})")
        elif names and any(n.startswith("gc") for n in names) and p["comm"] not in names:
            add(f"process: pid {p['pid']} comm {p['comm']!r} not in GT_PROCESS_NAMES={','.join(names)} ({p['args']})")
        if p["exe"].endswith("(deleted)") or os.path.realpath(p["exe"]) != f["live_real"]:
            add(f"process: pid {p['pid']} runs {p['exe']}, not the live binary ({p['args']})")
    # gc/bd pair
    if not f["bd_version"]:
        add(f"bd: `bd version` gave no version ({f['bd_version_raw']!r})")
    elif f["gomod_beads"] and f["bd_version"] != f["gomod_beads"]:
        add(f"bd: bd {f['bd_version']} != beads {f['gomod_beads']} in go.mod of installed {f['gc_commit_short']} "
            "(gc and bd move together)")
    elif not f["gomod_beads"] and f["gc_commit"]:
        add(f"bd: no github.com/steveyegge/beads line in go.mod at {f['gc_commit_short']}")
    # rollback copy
    rb = f["rollback"]
    if not rb:
        add("rollback: no installed promote record names a previous binary other than the live one")
    elif not rb["exists"]:
        add(f"rollback: previous binary {rb['previous']} (from {rb['record']}) is missing or not executable")
    # patches
    if f["gc_commit"]:
        for r in patch_rows(a.city, a.fork, f["gc_commit"]):
            if r["present"] is None:
                add(f"patch: {r['sha']} ({r['status']}) missing from installed {f['gc_commit_short']}: {r['subject']}")
    # shadow
    s = shadow_facts(a.city)
    if s["timer_active"] != "active" or s["timer_enabled"] != "enabled":
        add(f"shadow: {SHADOW_TIMER} is {s['timer_active']}/{s['timer_enabled']}")
    if s["service_active"] != "activating" and s["service_result"] != "success":
        add(f"shadow: last {SHADOW_SERVICE} result {s['service_result']} (status {s['service_status']})")
    if not s["report"]:
        add("shadow: no latest-shadow.json report")
    elif s["report_age_h"] > SHADOW_MAX_AGE_H:
        add(f"shadow: latest report {s['report']} is {s['report_age_h']}h old (> {SHADOW_MAX_AGE_H}h)")
    for line in findings:
        print(f"gc-promotion: {line}")
    if findings:
        return 1
    print("gc-promotion: clean")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", type=Path, default=Path(os.environ.get("GC_CITY") or HOME / "city"))
    ap.add_argument("--fork", type=Path,
                    default=Path(os.environ.get("GC_UPGRADE_FORK") or HOME / "src/gascity-city15x"))
    ap.add_argument("command", choices=["doctor", "installed", "patches", "shadow"])
    a = ap.parse_args()
    a.city = a.city.expanduser().resolve()
    return {"doctor": cmd_doctor, "installed": cmd_installed,
            "patches": cmd_patches, "shadow": cmd_shadow}[a.command](a)


if __name__ == "__main__":
    sys.exit(main())
