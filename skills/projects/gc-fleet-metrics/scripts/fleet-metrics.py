#!/usr/bin/env python3
"""Fleet metrics the city's other scripts do not print: per agent type, per node, stalls,
config changes, and a before/after split around any one change. Read-only.

    fleet-metrics.py [--days N] [--json]                  agents, nodes, stalls, bottlenecks, changes
    fleet-metrics.py --around <sha|ISO> [--hours H]       same metrics, H hours before vs after a change
    fleet-metrics.py --since ISO --until ISO              an explicit window

Sources (all local, Ryzen):
  session-facts.jsonl  one row per agent session on all three hosts (agent, models, effort, tokens, wall,
                       waste); refreshed nightly by `dispatch/session_facts.py collect`
  jobs/, receipts/     one per fleet dispatch; receipt mtime is the finish time
  route.log(+.gz)      ROUTED gives launch time and host; stall verbs (QUEUED, LAUNCH-STALL, FAIR-WAIT ...)
  model-grades.tsv     mayor grade per dispatch (WORKED / BLOCKED-JUSTIFIED / BLOCKED-UNJUSTIFIED)
  events.jsonl         session lifecycle (stranded, idle_killed, draining, crashed) since its last rotation
  city git log         commits touching config-bearing paths: the change epochs
$ is re-priced from city.toml [[pricing]] via dispatch/prices.py; a model with no rate is UNPRICED, never $0.
A source that cannot be read, or whose newest row is older than the window end, is flagged in `coverage`.
"""
import argparse, collections, datetime as dt, glob, gzip, json, os, re, subprocess, sys, time
from pathlib import Path

CITY = Path(os.environ.get("GC_CITY", "/home/coolhenrylinux/city"))
FLEET = CITY / ".gc/runtime/fleet"
ROUTE = CITY / ".gc/runtime/route.log"
GRADES = CITY / "dispatch/ledgers/model-grades.tsv"
DECISIONS = CITY / "dispatch/ledgers/decisions.tsv"
EVENTS = CITY / ".gc/events.jsonl"
sys.path.insert(0, str(CITY / "dispatch"))
try:
    import prices
    RATES = prices.load()
except Exception:  # noqa: BLE001 - prices is optional; cost then reads UNPRICED
    prices, RATES = None, {}

# Paths whose commits change how lanes are routed, prompted, paced or priced.
CHANGE_PATHS = ["city.toml", "pack.toml", "agents", "prompts", "formulas", "orders", "hooks",
                "dispatch/fleet.py", "dispatch/route.sh", "dispatch/resource_policy.py",
                "dispatch/resource_guard.py", "dispatch/codex-fallback.py", "dispatch/pareto_shadow.py",
                "dispatch/merge-queue.sh", "dispatch/land.sh", "dispatch/merge-train.sh"]
STALL_VERBS = ("QUEUED", "QUEUE-FULL", "REQUEUED", "LAUNCH-STALL", "FAIR-WAIT", "UNREACHABLE", "ORPHAN",
               "HELD", "HOLD", "WITHDRAWN", "RETRY", "STRANDED-BASE", "PARENT-GONE", "PR-CONFLICT")
STALL_EVENTS = ("session.stranded", "session.idle_killed", "session.draining", "session.crashed",
                "session.drain_acked_with_assigned_work", "session.demand_claim_divergence",
                "bead.dead_assignee_reopened", "bead.claim_rejected", "order.failed")
HOSTS = ("ryzen", "dell", "gtx")
DONE = ("PASS", "ALREADY-FIXED")
LOW_N = 20
ROUTED = re.compile(r"^(\S+Z) ROUTED (\S+) -> (\w+)/\S*?run([0-9a-f]{20})\b")
LINE = re.compile(r"^(\S+Z) ([A-Z][A-Z-]+) (\S+)?(.*)$")
HEX20 = re.compile(r"^[0-9a-f]{20}$")


def iso(s):
    s = re.sub(r"(\.\d{6})\d+", r"\1", str(s).replace("Z", "+00:00"))
    return dt.datetime.fromisoformat(s).timestamp()


def utc(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ") if t else "-"


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return round(xs[min(len(xs) - 1, int(q * len(xs)))], 1) if xs else None


def share(n, d):
    return round(100 * n / d, 1) if d else None


def agent_type(agent):
    """gateway-llm-gtx/dsh-muse-3 -> dsh-muse; bd.dog-1 -> bd.dog; no agent -> (interactive): the owner's own sessions."""
    if not agent:
        return "(interactive)"
    return re.sub(r"-\d+$", "", agent.rsplit("/", 1)[-1])


def load_jobs():
    jobs = {}
    for p in glob.glob(str(FLEET / "jobs/*.json")):
        try:
            j = json.load(open(p))
            jobs[j["id"]] = j
        except (ValueError, KeyError, OSError):
            pass
    return jobs


def load_receipts():
    out = {}
    for p in glob.glob(str(FLEET / "receipts/*.json")):
        try:
            r = json.load(open(p))
            r["_done"] = os.path.getmtime(p)
            out[r["id"]] = r
        except (ValueError, KeyError, OSError):
            pass
    return out


def load_grades():
    g = {}
    try:
        for line in open(GRADES):
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            g[f[0]] = {"grade": f[1], "kind": f[2] if len(f) > 2 else "", "cause": f[3] if len(f) > 3 else ""}
    except OSError:
        pass
    return g


def route_lines():
    paths = sorted(glob.glob(str(ROUTE) + ".*.gz")) + [str(ROUTE)]
    for p in paths:
        try:
            fh = gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")
        except OSError:
            continue
        with fh:
            yield from fh


def parse_route(since, until, jobs):
    launch, stalls, first = {}, collections.Counter(), None
    distinct = collections.defaultdict(set)
    by_host = collections.defaultdict(collections.Counter)
    by_day = collections.defaultdict(collections.Counter)
    samples = collections.defaultdict(list)
    for line in route_lines():
        m = ROUTED.match(line)
        if m:
            t = iso(m[1])
            first = first or t
            launch.setdefault(m[4], (t, m[3]))
            continue
        m = LINE.match(line)
        if not m or m[2] not in STALL_VERBS:
            continue
        t = iso(m[1])
        first = first or t
        if not since <= t < until:
            continue
        verb, tok, rest = m[2], (m[3] or ""), m[4] or ""
        if verb == "QUEUED" and "no free slot" not in rest:
            continue  # QUEUED also logs ordinary enqueues; only the no-slot ones are waits
        host = (jobs.get(tok) or {}).get("host") if HEX20.match(tok) else None
        host = host or next((h for h in HOSTS if re.search(rf"\b{h}\b", tok + rest[:60])), "-")
        stalls[verb] += 1
        distinct[verb].add(tok.rstrip(":"))
        by_host[verb][host] += 1
        by_day[verb][utc(t)[:10]] += 1
        if len(samples[verb]) < 3:
            samples[verb].append(line.strip()[:220])
    return launch, first, {"counts": dict(stalls), "distinct_subjects": {k: len(v) for k, v in distinct.items()},
                           "by_host": {k: dict(v) for k, v in by_host.items()},
                           "by_day": {k: dict(sorted(v.items())) for k, v in by_day.items()},
                           "samples": dict(samples)}


def facts(since, until):
    rows, newest = [], None
    try:
        fh = open(FLEET / "session-facts.jsonl")
    except OSError:
        return None, None
    with fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            s = r.get("start") or 0
            newest = max(newest or 0, r.get("end") or s)
            if since <= s < until:
                rows.append(r)
    return rows, newest


def usd(r):
    if not prices:
        return None
    tk = r.get("tokens") or {}
    models = r.get("models") or []
    if len(models) != 1:
        return None  # a mixed-model session cannot be split from session totals
    c = prices.cost(RATES, models[0], tk.get("input", 0), tk.get("output", 0), tk.get("cache_read", 0),
                    tk.get("cache_write", 0), codex=r.get("provider") == "codex")
    return c


def agents_table(rows, receipts, grades):
    by_gc = {}
    for rc in receipts.values():
        if rc.get("session_id"):
            by_gc[rc["session_id"]] = rc
    agg = collections.defaultdict(lambda: collections.defaultdict(float))
    meta = collections.defaultdict(lambda: {"hosts": collections.Counter(), "models": collections.Counter(),
                                            "efforts": collections.Counter(), "walls": [], "verdicts": collections.Counter(),
                                            "grades": collections.Counter(), "dispatches": set()})
    for r in rows:
        a = agent_type(r.get("agent"))
        A, M = agg[a], meta[a]
        tk = r.get("tokens") or {}
        A["sessions"] += 1
        A["wall_h"] += (r.get("wall_s") or 0) / 3600
        A["idle_h"] += (r.get("idle_s") or 0) / 3600
        for k in ("input", "output", "cache_read", "cache_write"):
            A["tok_" + k] += tk.get(k, 0) or 0
        c = usd(r)
        if c is None:
            A["unpriced"] += 1
        else:
            A["usd"] += c
        w = r.get("waste") or {}
        A["fail_s"] += w.get("fail_s", 0) or 0
        A["poll_s"] += (w.get("poll_repeat_s", 0) or 0) + (w.get("stale_repeat_s", 0) or 0)
        A["compactions"] += r.get("compactions") or 0
        A["ctx_peak_max"] = max(A["ctx_peak_max"], r.get("ctx_peak") or 0)
        M["hosts"][r.get("host") or "?"] += 1
        for x in r.get("models") or ["?"]:
            M["models"][x] += 1
        for x in r.get("efforts") or ["?"]:
            M["efforts"][x] += 1
        M["walls"].append((r.get("wall_s") or 0) / 60)
        rc = receipts.get(r.get("dispatch_id") or "") or next((by_gc[s] for s in r.get("gc_sessions") or [] if s in by_gc), None)
        if rc and rc["id"] not in M["dispatches"]:
            M["dispatches"].add(rc["id"])
            M["verdicts"][rc.get("verdict") or "?"] += 1
            M["grades"][(grades.get(rc["id"][:8]) or {}).get("grade", "UNGRADED")] += 1
    out = {}
    for a, A in sorted(agg.items(), key=lambda kv: -kv[1]["wall_h"]):
        M = meta[a]
        n_disp = len(M["dispatches"])
        graded = sum(v for k, v in M["grades"].items() if k != "UNGRADED")
        worked = M["grades"]["WORKED"]
        priced = A["sessions"] - A["unpriced"]
        out[a] = {
            "sessions": int(A["sessions"]), "dispatches": n_disp,
            "sessions_per_dispatch": round(A["sessions"] / n_disp, 1) if n_disp else None,
            "hosts": dict(M["hosts"]), "models": dict(M["models"]), "efforts": dict(M["efforts"]),
            "wall_h": round(A["wall_h"], 1), "idle_pct": share(A["idle_h"], A["wall_h"]),
            "wall_min_p50": pct(M["walls"], .5), "wall_min_p90": pct(M["walls"], .9),
            "tokens_m": {k: round(A["tok_" + k] / 1e6, 2) for k in ("input", "output", "cache_read", "cache_write")},
            "usd": round(A["usd"], 2) if priced else None, "unpriced_sessions": int(A["unpriced"]),
            "usd_per_session": round(A["usd"] / priced, 3) if priced else None,
            "usd_per_dispatch": round(A["usd"] / n_disp, 3) if priced and n_disp else None,
            "usd_per_worked": round(A["usd"] / worked, 3) if priced and worked else None,
            "verdicts": dict(M["verdicts"]), "pass_pct": share(sum(M["verdicts"][v] for v in DONE), n_disp),
            "worked_pct": share(worked, graded), "graded": graded,
            "waste_fail_min": round(A["fail_s"] / 60, 1), "waste_poll_min": round(A["poll_s"] / 60, 1),
            "compactions": int(A["compactions"]), "ctx_peak_max_k": round(A["ctx_peak_max"] / 1000),
            "low_n": A["sessions"] < LOW_N,
        }
    return out


def nodes_table(since, until, jobs, receipts, grades, launch):
    N = {h: {"filed": 0, "launched": 0, "receipts": collections.Counter(), "classes": collections.Counter(),
             "grades": collections.Counter(), "queue": [], "run": [], "unfinished": [], "withdrawn": 0,
             "failure_class": collections.Counter()} for h in HOSTS + ("unplaced",)}
    now = time.time()
    for jid, j in jobs.items():
        c = float(j.get("created") or 0)
        if not since <= c < until:
            continue
        L = launch.get(jid)
        h = (L[1] if L else j.get("host")) or "unplaced"
        h = h if h in N else "unplaced"
        n = N[h]
        n["filed"] += 1
        if j.get("state") == "withdrawn":
            n["withdrawn"] += 1
        if L:
            n["launched"] += 1
            n["queue"].append((L[0] - c) / 60)
        rc = receipts.get(jid)
        if rc:
            v = rc.get("verdict") or "?"
            n["receipts"][v] += 1
            n["classes"][(rc.get("class") or "?") + ":" + v] += 1
            if rc.get("failure_class"):
                n["failure_class"][rc["failure_class"]] += 1
            n["grades"][(grades.get(jid[:8]) or {}).get("grade", "UNGRADED")] += 1
            if L:
                n["run"].append((rc["_done"] - L[0]) / 60)
        elif j.get("state") in ("launched", "reserved") or (L and j.get("state") not in ("withdrawn", "superseded", "cancelled")):
            n["unfinished"].append({"id": jid[:8], "age_min": round((now - (L[0] if L else c)) / 60),
                                    "state": j.get("state"), "title": (j.get("title") or "")[:70]})
    out = {}
    for h, n in N.items():
        if not n["filed"]:
            continue
        got = sum(n["receipts"].values())
        graded = sum(v for k, v in n["grades"].items() if k != "UNGRADED")
        # Stuck: still running past this node's own p90 run time (floor 60 min), so it is an outlier, not a slow normal.
        bar = max(60, pct(n["run"], .9) or 0)
        stuck = [u for u in n["unfinished"] if u["age_min"] > bar]
        out[h] = {
            "filed": n["filed"], "launched": n["launched"], "receipts": got, "withdrawn": n["withdrawn"],
            "completed": sum(n["receipts"][v] for v in DONE), "prepared": n["receipts"]["PREPARED"],
            "completed_pct_of_receipts": share(sum(n["receipts"][v] for v in DONE), got),
            "verdicts": dict(n["receipts"]), "by_class": dict(n["classes"]),
            "worked_pct": share(n["grades"]["WORKED"], graded), "graded": graded,
            "blocked_unjustified": n["grades"]["BLOCKED-UNJUSTIFIED"],
            "failure_class": dict(n["failure_class"].most_common(6)),
            "queue_min_p50": pct(n["queue"], .5), "queue_min_p90": pct(n["queue"], .9),
            "run_min_p50": pct(n["run"], .5), "run_min_p90": pct(n["run"], .9),
            "unfinished": sorted(n["unfinished"], key=lambda x: -x["age_min"])[:8],
            "unfinished_n": len(n["unfinished"]), "stuck_over_min": round(bar), "stuck": stuck[:8], "stuck_n": len(stuck),
        }
    return out


def events(since, until):
    counts, agents, first = collections.Counter(), collections.defaultdict(collections.Counter), None
    try:
        fh = open(EVENTS, errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            if '"session.' not in line and '"bead.' not in line and '"order.failed"' not in line:
                continue
            try:
                e = json.loads(line)
                t = iso(e["ts"])
            except (ValueError, KeyError):
                continue
            first = first or t
            if e.get("type") in STALL_EVENTS and since <= t < until:
                counts[e["type"]] += 1
                who = (e.get("payload") or {}).get("template") or (e.get("payload") or {}).get("agent") or e.get("actor") or "?"
                agents[e["type"]][agent_type(str(who))] += 1
    return {"since": utc(first), "counts": dict(counts), "by_agent": {k: dict(v.most_common(6)) for k, v in agents.items()}}


def changes(since, until):
    try:
        out = subprocess.run(["git", "-C", str(CITY), "log", f"--since=@{int(since)}", f"--until=@{int(until)}",
                              "--format=%H\t%ct\t%s", "--", *CHANGE_PATHS], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return "UNREAD"
    commits = [dict(sha=s[:9], at=utc(int(t)), subject=m[:110]) for s, t, m in
               (l.split("\t", 2) for l in out.splitlines() if l.count("\t") >= 2)]
    rulings = []
    try:
        for line in open(DECISIONS):
            f = line.rstrip("\n").split("\t")
            if len(f) > 3 and f[1] in ("ruling", "config", "routing", "policy") and since <= iso(f[0]) < until:
                rulings.append(dict(at=f[0], phase=f[1], decision=f[2][:90]))
    except (OSError, ValueError):
        pass
    return {"commits": commits[::-1], "rulings": rulings}


def change_time(ref):
    if re.fullmatch(r"[0-9a-f]{6,40}", ref):
        out = subprocess.run(["git", "-C", str(CITY), "show", "-s", "--format=%ct\t%s", ref], capture_output=True, text=True)
        if out.returncode == 0:
            t, s = out.stdout.strip().split("\t", 1)
            return float(t), f"{ref[:9]} {s[:90]}"
        sys.exit(f"unknown commit {ref}")
    return iso(ref), ref


def bottlenecks(nodes, stalls):
    """Rank waiting stages: where a lane spends the most p90 minutes not running, and where it runs longest."""
    rows = []
    for h, n in nodes.items():
        if n.get("queue_min_p90") is not None:
            rows.append((n["queue_min_p90"], f"queue wait on {h}", f"p50 {n['queue_min_p50']} / p90 {n['queue_min_p90']} min"))
        if n.get("run_min_p90") is not None:
            rows.append((n["run_min_p90"], f"lane run on {h}", f"p50 {n['run_min_p50']} / p90 {n['run_min_p90']} min"))
        if n["stuck_n"]:
            rows.append((n["stuck"][0]["age_min"], f"stuck lanes on {h}",
                         f"{n['stuck_n']} running past {n['stuck_over_min']} min; oldest {n['stuck'][0]['id']} {n['stuck'][0]['age_min']} min"))
    c, d = stalls["counts"], stalls["distinct_subjects"]
    for verb in ("QUEUED", "QUEUE-FULL", "LAUNCH-STALL", "FAIR-WAIT", "UNREACHABLE", "REQUEUED", "ORPHAN", "HELD"):
        if c.get(verb):
            rows.append((None, f"route.log {verb}", f"{c[verb]} lines, {d.get(verb)} distinct; by host {stalls['by_host'].get(verb)}"))
    rows.sort(key=lambda r: -(r[0] or 0))
    return [{"stage": s, "detail": d} for _, s, d in rows]


def coverage(since, until, route_first, facts_newest, ev):
    def age(p):
        try:
            return round((time.time() - os.path.getmtime(p)) / 3600, 1)
        except OSError:
            return "UNREAD"
    cov = {"route_log_from": utc(route_first), "session_facts_newest": utc(facts_newest),
           "events_from": ev["since"] if ev else "UNREAD", "grades_age_h": age(GRADES),
           "session_ledger_age_h": age(FLEET / "session-ledger.jsonl")}
    warn = []
    if route_first and route_first > since:
        warn.append("route.log starts after the window start: launches, queue and run times are partial before " + utc(route_first))
    if not facts_newest or facts_newest < until - 2 * 3600:
        warn.append("session-facts is older than the window end: run `dispatch/session_facts.py collect --since <days>` first")
    if ev and ev["since"] != "-" and iso(ev["since"].replace(" ", "T").replace("Z", ":00Z")) > since:
        warn.append("events.jsonl rotated inside the window: lifecycle counts start at " + ev["since"])
    cov["warnings"] = warn
    return cov


def collect(since, until):
    jobs, receipts, grades = load_jobs(), load_receipts(), load_grades()
    launch, route_first, stalls = parse_route(since, until, jobs)
    rows, newest = facts(since, until)
    nodes = nodes_table(since, until, jobs, receipts, grades, launch)
    ev = events(since, until)
    return {
        "window": {"since": utc(since), "until": utc(until), "days": round((until - since) / 86400, 2)},
        "coverage": coverage(since, until, route_first, newest, ev),
        "agents": agents_table(rows, receipts, grades) if rows is not None else "UNREAD",
        "nodes": nodes, "stalls": stalls, "lifecycle_events": ev or "UNREAD",
        "bottlenecks": bottlenecks(nodes, stalls),
    }


HEADLINE = ("sessions", "dispatches", "usd", "usd_per_dispatch", "usd_per_worked", "pass_pct", "worked_pct", "wall_min_p50")
NODE_HEAD = ("filed", "receipts", "completed_pct_of_receipts", "worked_pct", "queue_min_p90", "run_min_p50", "run_min_p90", "unfinished_n")


def compare(before, after):
    def pick(d, keys):
        return {k: d.get(k) for k in keys} if isinstance(d, dict) else d
    agents = {}
    for a in sorted(set(before["agents"]) | set(after["agents"])) if isinstance(before["agents"], dict) else []:
        agents[a] = {"before": pick(before["agents"].get(a, {}), HEADLINE), "after": pick(after["agents"].get(a, {}), HEADLINE)}
    nodes = {h: {"before": pick(before["nodes"].get(h, {}), NODE_HEAD), "after": pick(after["nodes"].get(h, {}), NODE_HEAD)}
             for h in sorted(set(before["nodes"]) | set(after["nodes"]))}
    stalls = {v: [before["stalls"]["counts"].get(v, 0), after["stalls"]["counts"].get(v, 0)]
              for v in sorted(set(before["stalls"]["counts"]) | set(after["stalls"]["counts"]))}
    return {"agents": agents, "nodes": nodes, "stalls_before_after": stalls,
            "coverage": {"before": before["coverage"], "after": after["coverage"]}}


def table(title, rows, cols):
    """rows: {name: dict}; cols: [(header, key or callable)]. None prints '-'."""
    if not isinstance(rows, dict) or not rows:
        print(f"\n{title}: {rows or 'none'}")
        return
    cells = [[name] + [str((k(r) if callable(k) else r.get(k)) if (k(r) if callable(k) else r.get(k)) is not None else "-")
                       for _, k in cols] for name, r in rows.items()]
    heads = [""] + [h for h, _ in cols]
    w = [max(len(x) for x in col) for col in zip(heads, *cells)]
    print(f"\n{title}")
    for line in [heads] + cells:
        print("  " + "  ".join(c.ljust(w[i]) if i == 0 else c.rjust(w[i]) for i, c in enumerate(line)))


def top(d, n=2):
    return ",".join(f"{k}:{v}" for k, v in sorted((d or {}).items(), key=lambda kv: -kv[1])[:n])


def render(res):
    print(f"window {res['window']}")
    for w in res["coverage"].pop("warnings"):
        print(f"WARNING {w}")
    print(f"coverage {res['coverage']}")
    table("AGENTS (by wall time; $ list-price estimate; '-' = unpriced or no dispatch)", res["agents"], [
        ("sess", "sessions"), ("disp", "dispatches"), ("s/disp", "sessions_per_dispatch"),
        ("hosts", lambda r: top(r["hosts"], 3)), ("model", lambda r: top(r["models"], 1)), ("effort", lambda r: top(r["efforts"], 2)),
        ("wall_h", "wall_h"), ("idle%", "idle_pct"), ("p50m", "wall_min_p50"), ("p90m", "wall_min_p90"),
        ("$", "usd"), ("$/disp", "usd_per_dispatch"), ("$/WORKED", "usd_per_worked"),
        ("pass%", "pass_pct"), ("WORKED%", "worked_pct"), ("failmin", "waste_fail_min"), ("pollmin", "waste_poll_min"),
        ("lowN", lambda r: "low" if r["low_n"] else "")])
    table("NODES (lanes filed in window, by host they ran on)", res["nodes"], [
        ("filed", "filed"), ("launch", "launched"), ("rcpt", "receipts"), ("done", "completed"), ("prep", "prepared"),
        ("fail", lambda r: r["verdicts"].get("FAIL", 0)), ("blocked", lambda r: r["verdicts"].get("BLOCKED", 0)),
        ("done%", "completed_pct_of_receipts"), ("WORKED%", "worked_pct"), ("unjust", "blocked_unjustified"),
        ("q50", "queue_min_p50"), ("q90", "queue_min_p90"), ("run50", "run_min_p50"), ("run90", "run_min_p90"),
        ("running", "unfinished_n"), ("stuck", "stuck_n"), ("top fail class", lambda r: top(r["failure_class"], 2))])
    for h, n in res["nodes"].items():
        for u in n["stuck"]:
            print(f"  STUCK {h} {u['id']} {u['age_min']}m {u['state']}: {u['title']}")
    s = res["stalls"]
    table("STALLS (route.log lines in window; distinct = jobs/beads/hosts named)",
          {v: {"lines": c, "distinct": s["distinct_subjects"].get(v), "hosts": top(s["by_host"].get(v), 3),
               "days": top(s["by_day"].get(v), 3)} for v, c in sorted(s["counts"].items(), key=lambda kv: -kv[1])},
          [("lines", "lines"), ("distinct", "distinct"), ("by host", "hosts"), ("busiest days", "days")])
    ev = res["lifecycle_events"]
    if isinstance(ev, dict):
        print(f"\nLIFECYCLE EVENTS since {ev['since']}")
        for t, c in sorted(ev["counts"].items(), key=lambda kv: -kv[1]):
            print(f"  {t:45} {c:5}  {top(ev['by_agent'].get(t), 4)}")
    print("\nBOTTLENECKS (ranked by minutes)")
    for b in res["bottlenecks"]:
        print(f"  {b['stage']:32} {b['detail']}")
    ch = res.get("changes")
    if isinstance(ch, dict):
        print(f"\nCHANGES in window ({len(ch['commits'])} config-bearing commits, oldest first; compare with --around <sha>)")
        for c in ch["commits"]:
            print(f"  {c['sha']} {c['at']} {c['subject']}")
        for r in ch["rulings"]:
            print(f"  RULING {r['at']} {r['decision']}")


def dash(d, f):
    return d.get(f) if isinstance(d, dict) and d.get(f) is not None else "-"


def render_compare(res):
    print(f"change {res['change']} at {res['at']}; {res['hours_each_side']} h each side {res.get('note', '')}")
    for side in ("before", "after"):
        for w in res["coverage"][side].get("warnings", []):
            print(f"WARNING ({side}) {w}")
    for name, keys in (("AGENTS", HEADLINE), ("NODES", NODE_HEAD)):
        rows = {}
        for k, v in res[name.lower()].items():
            rows[k] = {f: f"{dash(v['before'], f)} -> {dash(v['after'], f)}" for f in keys}
        table(f"{name} before -> after", rows, [(f, f) for f in keys])
    print("\nSTALLS before -> after")
    for v, (b, a) in res["stalls_before_after"].items():
        print(f"  {v:15} {b:6} -> {a}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--around", help="commit sha or ISO time of a change: compare equal windows before and after")
    ap.add_argument("--hours", type=float, default=24, help="window each side of --around (default 24)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    now = time.time()
    if a.around:
        t, label = change_time(a.around)
        hrs = min(a.hours, (now - t) / 3600)
        res = {"change": label, "at": utc(t), "hours_each_side": round(hrs, 1),
               **compare(collect(t - hrs * 3600, t), collect(t, t + hrs * 3600))}
        if hrs < a.hours:
            res["note"] = f"after-window capped at {hrs:.1f} h (now); before-window matched to it"
    else:
        until = iso(a.until) if a.until else now
        since = iso(a.since) if a.since else until - a.days * 86400
        res = collect(since, until)
        res["changes"] = changes(since, until)
    if a.json:
        json.dump(res, sys.stdout, indent=1, default=str)
        print()
    elif a.around:
        render_compare(res)
    else:
        render(res)


if __name__ == "__main__":
    main()
