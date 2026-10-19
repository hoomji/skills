#!/usr/bin/env python3
"""observability: read-only checks and drives for the city's operator views (verify-city).

    observability.py doctor                 one line per finding, exit 1 on any; else "observability: clean"
    observability.py mobile [--ev DIR]      GET every gc-mobile route; status, size, sanitized excerpt, parity
    observability.py top    [--ev DIR]      gc-top.py --once, then the live TUI in a private tmux socket
    observability.py facts  [--ev DIR]      fleet_facts classification and ui-drift-check.py --dry-run
    observability.py views  [--ev DIR]      gc-visualize.py summary and mergify-metrics.py (7 days)

--city defaults to $GC_CITY or ~/city. --ev saves each drive's output there (the skill passes
$EV/observability). Read-only: GET only (never ?refresh=, which wakes a collector), no POST, no
restart, the only tmux server touched is the private socket TMUX_SOCKET this script creates and
kills. gc-pr-top.py and city-metrics.py are not run directly: gc-pr-top rewrites
.gc/runtime/fleet/pr-pipeline-cache.json and city-metrics report takes ~2 min of gh and bd; their
output is read from gc-mobile's /api/prs and /api/flow, which run them on schedule.
"""

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8390"
TMUX_SOCKET = "verify-city-obs"
# Display files that render or describe the muse-code state (gc-top terminal, gc-mobile phone).
DISPLAY_FILES = ("gc-top.py", "mobile/server.py", "mobile/alerts.py", "mobile/static/app.js", "mobile/test_mobile.py")
# Modules gc-mobile's server loads once at start (gc-top caches fleet.py in _ROUTING_MOD forever).
SERVER_LOADS = ("mobile/server.py", "mobile/alerts.py", "mobile/webpush.py", "gc-top.py",
                "dispatch/fleet.py", "dispatch/fleet_facts.py", "dispatch/codex-fallback.py")
# Every script this feature covers, at its real location.
SCRIPTS = ("gc-top.py", "gc-pr-top.py", "gc-visualize.py", "mobile/server.py", "dispatch/fleet_facts.py",
           "orders/scripts/ui-drift-check.py", "dispatch/city-metrics.py", "dispatch/mergify-metrics.py",
           "orders/ui-drift.toml", "docs/gc-mobile.md", "docs/city-metrics.md")


# ------------------------------------------------------------------ helpers
def get(path, timeout=20):
    """(status, bytes) for a GET to gc-mobile; status 0 when nothing answers."""
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, method="GET"), timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        return 0, str(e).encode()


def sanitize(text, n=160):
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<email>", text)
    text = re.sub(r"https://[^\s\"']+", "<url>", text)
    text = re.sub(r"[A-Za-z0-9_+/=-]{32,}", "<redacted>", text)
    return " ".join(text.split())[:n]


def strip_ansi(s):
    return re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", s)


def fn_source(path, name):
    src = path.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node) or ""
    return ""


def server_routes(city):
    """(api names, collector intervals) parsed from mobile/server.py."""
    src = (city / "mobile/server.py").read_text()
    jobs = {m[1]: int(m[2]) for m in re.finditer(r'"([\w.]+)": \((\d+), lambda', src)}
    m = re.search(r"if name in \(([^)]*)\):", src)
    cached = re.findall(r'"([\w.]+)"', m[1]) if m else []
    api = ["health", "vapid", "alerts"]
    for name in cached:
        if name.startswith("metrics"):
            q = {"metrics0.25": "metrics?days=0.25", "metrics1": "metrics", "metrics7": "metrics?days=7"}[name]
        elif name.startswith("costs"):
            q = {"costs0.25": "costs?days=0.25", "costs": "costs", "costs7": "costs?days=7"}[name]
        else:
            q = name
        api.append(q)
    return api, jobs


def static_routes(city):
    return ["/"] + sorted("/" + p.name for p in (city / "mobile/static").iterdir() if p.is_file())


def fleet_muse_states(city):
    """The state words fleet.muse_state can return, from its source."""
    body = fn_source(city / "dispatch/fleet.py", "muse_state")
    return set(re.findall(r'state = "([\w-]+)"', body)) | set(re.findall(r'"state": "([\w-]+)"', body))


def display_muse_states(city):
    """{file: set(state keys)} the displays map to a colour/word."""
    out = {}
    src = (city / "gc-top.py").read_text()
    m = re.search(r"MUSE_STATE_STYLE = \{(.*?)\}\n", src, re.S)
    out["gc-top.py"] = set(re.findall(r'"([\w-]+)": \(', m[1])) if m else set()
    js = (city / "mobile/static/app.js").read_text()
    m = re.search(r"const st = \{(.*?)\}\[m\.state\]", js, re.S)
    out["mobile/static/app.js"] = set(re.findall(r'"?([\w-]+)"?: \[', m[1])) if m else set()
    return out


def pace_gated(city):
    """True when fleet.muse_quota still refuses a lane on weekly pace."""
    body = fn_source(city / "dispatch/fleet.py", "muse_quota")
    return bool(re.search(r"^\s*if [^\n]*pace", body, re.M))


def fresh_muse_state(city):
    code = ("import importlib.util,json,sys,time\n"
            "s=importlib.util.spec_from_file_location('f',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
            "print(json.dumps(m.muse_state(m.muse_reading(),time.time())))")
    p = subprocess.run([sys.executable, "-I", "-c", code, str(city / "dispatch/fleet.py")], cwd=city,
                       capture_output=True, text=True, timeout=60)
    return json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 and p.stdout.strip() else None


def fleet_hosts(city):
    tree = ast.parse((city / "dispatch/fleet.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "HOSTS" for t in node.targets):
            return [k.value for k in node.value.keys]
    return []


def server_pid():
    p = subprocess.run(["systemctl", "--user", "show", "gc-mobile", "-p", "ExecMainPID", "--value"],
                       capture_output=True, text=True, timeout=10)
    try:
        pid = int(p.stdout.strip() or 0)
    except ValueError:
        pid = 0
    return pid or None


def proc_start(pid):
    stat = Path(f"/proc/{pid}/stat").read_text()
    ticks = int(stat.rsplit(")", 1)[1].split()[19])
    boot = next(float(l.split()[1]) for l in Path("/proc/stat").read_text().splitlines() if l.startswith("btime"))
    return boot + ticks / os.sysconf("SC_CLK_TCK")


def save(ev, name, text):
    if ev:
        ev.mkdir(parents=True, exist_ok=True)
        (ev / name).write_text(text)


# ------------------------------------------------------------------ doctor
def doctor(city):
    f = []
    # obs-docs: every script the feature covers exists where this map says.
    for s in SCRIPTS:
        if not (city / s).exists():
            f.append(f"obs-docs: {s} missing")
    # obs-docs: every path docs/gc-mobile.md names in backticks exists.
    doc = (city / "docs/gc-mobile.md").read_text()
    for tok in sorted(set(re.findall(r"`([^`\s]+)`", doc))):
        if "://" in tok or tok.startswith(("-", "/api")) or not re.search(r"\.(py|toml|json|md|pem|jsonl)$|/$", tok):
            continue
        cands = [city / tok, city / "dispatch" / tok, city / "mobile" / tok,
                 Path.home() / ".claude/skills/gc-fleet-metrics/scripts" / tok]
        if tok.startswith(".gc/runtime/mobile/") or tok in ("vapid.pem", "subscriptions.json", "alerts.json"):
            cands.append(city / ".gc/runtime/mobile" / tok)
        cands.append(city / ".gc/runtime/fleet" / tok)
        found = any(city.glob(tok)) if "*" in tok else any(c.exists() for c in cands)
        if not found:
            f.append(f"obs-docs: docs/gc-mobile.md names `{tok}`, not found")
    # obs-mobile-up: health answers and each source is fresh and error-free.
    st, body = get("/api/health")
    if st != 200:
        f.append(f"obs-mobile-up: GET /api/health -> {st} {sanitize(body.decode('utf-8', 'replace'), 80)}")
        health = {}
    else:
        health = json.loads(body)
    api, jobs = server_routes(city)
    jobs["now"] = 10
    for name, src in (health.get("sources") or {}).items():
        if src.get("error"):
            f.append(f"obs-mobile-up: source {name} error: {sanitize(str(src['error']), 120)}")
        age, iv = src.get("age_s"), jobs.get(name)
        if age is None:
            f.append(f"obs-mobile-up: source {name} never collected")
        elif iv and age > 3 * iv + 120:
            f.append(f"obs-mobile-up: source {name} {age:.0f}s old, interval {iv}s")
    for name in jobs:
        if health and name not in (health.get("sources") or {}):
            f.append(f"obs-mobile-up: collector {name} absent from /api/health sources")
    # obs-mobile-routes: every route the server registers answers 200 (GET only, no refresh).
    for path in ["/api/" + a for a in api] + static_routes(city):
        st, _ = get(path, timeout=30)
        if st != 200:
            f.append(f"obs-mobile-routes: GET {path} -> {st}")
    # obs-states: displays map exactly fleet.muse_state's words.
    fleet_states = fleet_muse_states(city)
    for fn, keys in display_muse_states(city).items():
        for k in sorted(keys - fleet_states):
            f.append(f"obs-states: {fn} maps muse state '{k}', fleet.muse_state never returns it")
        for k in sorted(fleet_states - keys):
            f.append(f"obs-states: {fn} has no style for fleet.muse_state '{k}'")
    retired = set().union(*display_muse_states(city).values()) - fleet_states
    for fn in DISPLAY_FILES:
        for i, line in enumerate((city / fn).read_text().splitlines(), 1):
            if any(f'"{w}"' in line for w in retired):
                f.append(f"obs-states: {fn}:{i} uses retired muse state: {line.strip()[:110]}")
    # obs-states: pace wording in displays when placement no longer gates on pace.
    if not pace_gated(city):
        pat = re.compile(r"over[- ]pace|within pace|≤ pace|\\u2264 pace|<= pace|while (it|its quota) paces", re.I)
        for fn in DISPLAY_FILES:
            if fn == "mobile/test_mobile.py":
                continue
            for i, line in enumerate((city / fn).read_text().splitlines(), 1):
                if pat.search(line) and not any(f'"{w}"' in line for w in retired):
                    f.append(f"obs-states: {fn}:{i} describes a pace gate fleet.muse_quota no longer has: {line.strip()[:110]}")
    # obs-parity: the phone's muse state equals fleet.muse_state now; host order equals fleet.HOSTS.
    st, body = get("/api/now", timeout=30)
    if st == 200:
        now = json.loads(body).get("data") or {}
        shown = ((now.get("quota") or {}).get("muse") or {}).get("state")
        fresh = fresh_muse_state(city)
        if fresh is None:
            f.append("obs-parity: fleet.muse_state could not be computed")
        elif shown != fresh.get("state"):
            f.append(f"obs-parity: gc-mobile /api/now muse state '{shown}', fleet.muse_state now '{fresh.get('state')}'")
        hosts = [h.get("name") for h in now.get("hosts") or []]
        if hosts != fleet_hosts(city):
            f.append(f"obs-parity: gc-mobile hosts {hosts} != fleet.HOSTS {fleet_hosts(city)}")
    # obs-mobile-fresh: the running server loaded every module it caches after that file last changed.
    pid = server_pid()
    if not pid:
        f.append("obs-mobile-fresh: gc-mobile service has no main PID")
    else:
        started = proc_start(pid)
        for s in SERVER_LOADS:
            mt = (city / s).stat().st_mtime
            if mt > started:
                f.append(f"obs-mobile-fresh: gc-mobile pid {pid} started {time.strftime('%FT%TZ', time.gmtime(started))}, "
                         f"{s} changed {time.strftime('%FT%TZ', time.gmtime(mt))} (server runs the old code)")
    # obs-gaps: lane gap kinds agree across gc-top, alerts.GAP_KINDS and the doc table.
    top_kinds = set(re.findall(r'"([\w-]+)": 0', fn_source(city / "gc-top.py", "classify_gaps").split("\n    for", 1)[0]))
    m = re.search(r"GAP_KINDS = \(([^)]*)\)", (city / "mobile/alerts.py").read_text())
    alert_kinds = set(re.findall(r'"([\w-]+)"', m[1])) if m else set()
    m = re.search(r"`GAP_KINDS`: ([^)]*)\)", doc)
    doc_kinds = {k.strip() for k in m[1].split(",")} if m else set()
    if not (top_kinds == alert_kinds == doc_kinds):
        f.append(f"obs-gaps: classify_gaps {sorted(top_kinds)} alerts.GAP_KINDS {sorted(alert_kinds)} doc {sorted(doc_kinds)}")
    # obs-drift: ui-drift-check's dry run (read-only: returns before any write or mail).
    p = subprocess.run([sys.executable, "orders/scripts/ui-drift-check.py", "--dry-run"], cwd=city,
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        f.append(f"obs-drift: ui-drift-check.py --dry-run exit {p.returncode}: {sanitize(p.stderr, 120)}")
    else:
        for d in json.loads(p.stdout).get("drift") or []:
            f.append(f"obs-drift: ui-drift-check: {d}")
    return f


# ------------------------------------------------------------------ drives
def drive_mobile(city, ev):
    out = []
    api, _ = server_routes(city)
    bodies = {}
    for path in ["/api/" + a for a in api] + static_routes(city):
        t0 = time.time()
        st, body = get(path, timeout=30)
        ms = (time.time() - t0) * 1000
        text = body.decode("utf-8", "replace")
        if path.startswith("/api/"):
            bodies[path] = text
            try:
                j = json.loads(text)
                meta = f"at={j.get('at')} error={j.get('error')!r}" if isinstance(j, dict) and "data" in j else ""
            except ValueError:
                meta = ""
            out.append(f"GET {path} {st} {len(body)}B {ms:.0f}ms {meta} | {sanitize(text)}")
        else:
            out.append(f"GET {path} {st} {len(body)}B {ms:.0f}ms")
    out.append("")
    try:
        now = json.loads(bodies["/api/now"])["data"]
        shown = now["quota"]["muse"]
        fresh = fresh_muse_state(city) or {}
        out.append(f"parity muse: phone state={shown.get('state')} window={(shown.get('window') or {}).get('pct')} "
                   f"weekly={(shown.get('weekly') or {}).get('pct')} | fleet.muse_state={fresh.get('state')} "
                   f"window={(fresh.get('window') or {}).get('pct')} weekly={(fresh.get('weekly') or {}).get('pct')} "
                   f"-> {'agree' if shown.get('state') == fresh.get('state') else 'DISAGREE'}")
        hosts = [h["name"] for h in now["hosts"]]
        out.append(f"parity hosts: phone {hosts} fleet.HOSTS {fleet_hosts(city)} -> "
                   f"{'agree' if hosts == fleet_hosts(city) else 'DISAGREE'}")
        out.append(f"now: polled_at={now.get('polled_at')} lanes={len(now.get('lanes') or [])} gaps={now.get('gaps')} "
                   f"unmapped={len(now.get('unmapped') or [])} queued={now['coordinator'].get('queued')}/{now['coordinator'].get('queue_cap')}")
        reading = json.loads((city / ".gc/runtime/fleet/muse-code-usage.json").read_text())
        out.append(f"source muse-code-usage.json: ok={reading.get('ok')} at={reading.get('at')} "
                   f"window={(reading.get('window') or {}).get('usedPercent')} weekly={(reading.get('weekly') or {}).get('usedPercent')}")
    except (KeyError, ValueError, OSError, TypeError) as e:
        out.append(f"parity: unavailable ({type(e).__name__}: {e})")
    try:
        prs = json.loads(bodies["/api/prs"])["data"] or {}
        out.append(f"prs (gc-pr-top --json via server): develop_health={(prs.get('develop_health') or {}).get('conclusion')} "
                   f"open={len(prs.get('prs') or [])}")
        flow = json.loads(bodies["/api/flow"])["data"] or {}
        out.append(f"flow (city-metrics report --days 1 --json via server): keys={sorted(flow)[:12]}")
    except (KeyError, ValueError, TypeError) as e:
        out.append(f"prs/flow: unavailable ({type(e).__name__}: {e})")
    text = "\n".join(out) + "\n"
    save(ev, "mobile.txt", text)
    print(text, end="")
    return 0 if all(" 200 " in l for l in out if l.startswith("GET ")) else 1


def drive_top(city, ev):
    env = dict(os.environ, COLUMNS="180")
    p = subprocess.run([sys.executable, "gc-top.py", "--once"], cwd=city, env=env, capture_output=True, text=True, timeout=120)
    once = strip_ansi(p.stdout)
    save(ev, "gc-top-once.txt", once)
    print(f"gc-top --once exit {p.returncode}, {len(once.splitlines())} lines")
    for l in once.splitlines():
        if l.strip().startswith(("GAS CITY DASHBOARD", "muse-code ")) or "UNMAPPED" in l:
            print("  " + l.strip()[:170])
    if not shutil.which("tmux"):
        print("tmux: not installed; TUI capture skipped")
        return p.returncode
    tm = ["tmux", "-L", TMUX_SOCKET, "-f", "/dev/null"]
    if subprocess.run(tm + ["has-session"], capture_output=True).returncode == 0:
        print(f"tmux: leftover private socket {TMUX_SOCKET} from an earlier run; killing it")
        subprocess.run(tm + ["kill-server"], capture_output=True)
    rc = 1
    try:
        subprocess.run(tm + ["new-session", "-d", "-s", "obs", "-x", "180", "-y", "200", "-c", str(city),
                             f"{sys.executable} gc-top.py -n 5"], check=True, timeout=20)
        pane, deadline = "", time.time() + 60
        while time.time() < deadline:
            time.sleep(3)
            pane = subprocess.run(tm + ["capture-pane", "-p", "-S", "-400", "-t", "obs"], capture_output=True, text=True).stdout
            if "GAS CITY DASHBOARD" in pane and "PROVIDERS" in pane:
                time.sleep(2)
                pane = subprocess.run(tm + ["capture-pane", "-p", "-S", "-400", "-t", "obs"], capture_output=True, text=True).stdout
                rc = 0
                break
        ansi = subprocess.run(tm + ["capture-pane", "-p", "-e", "-S", "-400", "-t", "obs"], capture_output=True, text=True).stdout
        save(ev, "gc-top-pane.txt", pane)
        save(ev, "gc-top-pane.ansi", ansi)
        print(f"tmux pane capture: {'rendered' if rc == 0 else 'NOT rendered in 60s'}, {len(pane.splitlines())} lines")
    finally:
        subprocess.run(tm + ["kill-server"], capture_output=True)
        gone = subprocess.run(tm + ["has-session"], capture_output=True).returncode != 0
        print(f"tmux: private socket {TMUX_SOCKET} killed: {gone}")
    return max(rc, p.returncode)


def drive_facts(city, ev):
    sys.path.insert(0, str(city / "dispatch"))
    import fleet_facts  # noqa: E402
    facts = fleet_facts.for_city(city)
    out = ["provider  family  quota_sub  pin_label"]
    for prov in sorted(facts.city_providers()):
        out.append(f"{prov}  {facts.provider_family(prov)}  {facts.quota_sub(prov)}  {facts.pin_label(prov)}")
    out.append(f"sub_order: {list(facts.sub_order())}")
    out.append(f"claude_logins: {facts.claude_logins()}")
    login, alt = facts.codex_logins()
    out.append(f"codex LOGIN: {login} ALTERNATE: {alt}")
    out.append(f"unmapped: {list(facts.unmapped.values())}")
    p = subprocess.run([sys.executable, "orders/scripts/ui-drift-check.py", "--dry-run"], cwd=city,
                       capture_output=True, text=True, timeout=120)
    try:
        rep = json.loads(p.stdout)
        out.append(f"ui-drift-check --dry-run exit {p.returncode}: drift={rep.get('drift')} facts={sorted(rep.get('facts') or {})}")
        last = json.loads((city / ".gc/runtime/ui-drift.json").read_text())
        out.append(f"last order run .gc/runtime/ui-drift.json at={last.get('at')} drift={last.get('drift')}")
    except (ValueError, OSError) as e:
        out.append(f"ui-drift-check: unreadable ({type(e).__name__}: {e}); stderr {sanitize(p.stderr)}")
    text = "\n".join(out) + "\n"
    save(ev, "facts.txt", text)
    print(text, end="")
    return 0 if p.returncode == 0 else 1


def drive_views(city, ev):
    rc = 0
    since = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400))
    for name, cmd in (("gc-visualize-summary.txt", [sys.executable, "gc-visualize.py", "summary", "--no-color"]),
                      ("mergify-metrics.txt", [sys.executable, "dispatch/mergify-metrics.py", "--since", since])):
        p = subprocess.run(cmd, cwd=city, capture_output=True, text=True, timeout=300)
        save(ev, name, p.stdout + (("\n--- stderr\n" + p.stderr) if p.stderr else ""))
        print(f"== {' '.join(cmd[1:])} exit {p.returncode}")
        print("\n".join(p.stdout.splitlines()[:14]))
        rc = max(rc, p.returncode)
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["doctor", "mobile", "top", "facts", "views"])
    ap.add_argument("--city", type=Path, default=Path(os.environ.get("GC_CITY") or Path.home() / "city"))
    ap.add_argument("--ev", type=Path, default=None, help="evidence dir for the drive's output files")
    a = ap.parse_args()
    city = a.city.expanduser().resolve()
    if a.cmd == "doctor":
        findings = doctor(city)
        text = "\n".join(findings) if findings else "observability: clean"
        save(a.ev, "doctor.txt", text + "\n")
        print(text)
        return 1 if findings else 0
    return {"mobile": drive_mobile, "top": drive_top, "facts": drive_facts, "views": drive_views}[a.cmd](city, a.ev)


if __name__ == "__main__":
    sys.exit(main())
