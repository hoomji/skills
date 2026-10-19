#!/usr/bin/env python3
"""quota-routing harness for verify-city: quota readings, backend fallback and Pareto lane placement.

usage: quota_routing.py [--city DIR] doctor      one line per drift finding, exit 1 on any;
                                                  else "quota-routing: clean", exit 0
       quota_routing.py [--city DIR] readings    every quota reading with its age and the max age the code allows
       quota_routing.py [--city DIR] placement   from the CURRENT readings: the pool a fresh write, a hard
                                                  write, a retry, a gateway review and a browser walk get, and why
       quota_routing.py [--city DIR] orders      the T1 write and gateway-review orders the code actually
                                                  enumerates per quota switch, beside the routing contract's
       quota_routing.py [--city DIR] supply      runs `orders/scripts/fleet-supply-probe.py providers` (read-only arm)

--city defaults to $GC_CITY, else ~/city. Strictly read-only:
- dispatch/codex-fallback.py is NEVER executed or imported (it has no --help; any flag runs a full
  pass with remote writes). Its constants are read from its AST.
- dispatch/fleet.py IS imported (its module level only reads files: integration-branch, city.toml via
  resource_guard policy loaders). `orders` monkeypatches the imported module's quota predicates in
  memory only; nothing is written.
- fleet-supply-probe.py runs only with `providers`; its `aa` arm (and the no-argument default) calls
  wrangler and writes .gc/runtime/fleet/seats/fleet-watcher/aa-pointer.json.
- quota-runway.py is never run here (no-argument mode is read-only, `record` appends to history).
"""
import ast, importlib.util, itertools, json, os, re, subprocess, sys, time, tomllib
from pathlib import Path

ALLOWED = (ast.Constant, ast.BinOp, ast.UnaryOp, ast.Tuple, ast.List, ast.Dict, ast.Set, ast.Name,
           ast.Load, ast.operator, ast.unaryop)
CONTRACT_REV = "routing-contract-v1.8"
# docs/model-routing-contract.md v1.8, "Distinct routing paths" plus "Write-order modifiers" (families: sol, claude, agy, muse).
DOC_T1 = {"fresh": ["codex-sol", "claude-review", "agy-flash", "muse-code"],
          "sonnet_first": ["claude-review", "codex-sol", "agy-flash", "muse-code"],
          "hard": ["claude-review", "codex-sol", "agy-flash", "muse-code"]}
DOC_REVIEW = {"normal": ["muse", "sol", "gemini", "sonnet"], "gemini_first": ["muse", "gemini", "sol", "sonnet"]}


def city_dir(argv):
    if "--city" in argv:
        return Path(argv[argv.index("--city") + 1]).expanduser()
    return Path(os.environ.get("GC_CITY") or Path.home() / "city")


def consts(path):
    """Top-level NAME = <literal or arithmetic on earlier literals>, from the AST; never executes the file."""
    out = {}
    tree = ast.parse(Path(path).read_text())
    for n in tree.body:
        if not (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)):
            continue
        if not all(isinstance(x, ALLOWED) for x in ast.walk(n.value)):
            continue
        try:
            out[n.targets[0].id] = eval(compile(ast.Expression(n.value), str(path), "eval"), {"__builtins__": {}}, dict(out))
        except Exception:
            pass
    return out


def func_src(path, name):
    for n in ast.parse(Path(path).read_text()).body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.unparse(n)
    return ""


def load_json(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def last_history(city):
    p = city / ".gc/runtime/fleet/quota-history.jsonl"
    try:
        with open(p, "rb") as f:
            f.seek(max(0, p.stat().st_size - 65536))
            lines = [l for l in f.read().decode(errors="replace").splitlines() if l.strip()]
        return json.loads(lines[-1])
    except (OSError, ValueError, IndexError):
        return None


def import_fleet(city):
    sys.dont_write_bytecode = True  # no __pycache__ writes into the city checkout
    os.environ.setdefault("FLEET_CITY", str(city))
    spec = importlib.util.spec_from_file_location("fleet_verify", city / "dispatch/fleet.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(city / "dispatch"))
    spec.loader.exec_module(mod)
    return mod


def age(t, now):
    return None if not isinstance(t, (int, float)) else now - t


def fmt_age(s):
    return "missing" if s is None else f"{s / 60:.0f}m" if s < 7200 else f"{s / 3600:.1f}h"


# ---------------------------------------------------------------------------------------------- readings

def reading_rows(city, now):
    """(name, path, at, max_age_s, source of the max age, detail)."""
    D = city / "dispatch"
    fl, cf = consts(D / "fleet.py"), consts(D / "codex-fallback.py")
    qr, sp = consts(D / "quota-runway.py"), consts(city / "orders/scripts/fleet-supply-probe.py")
    st = city / ".gc/runtime/fleet"
    qw, mu, hop = load_json(st / "quota-windows.json"), load_json(st / "muse-code-usage.json"), load_json(st / "hopscotch-credit.json")
    hist = last_history(city)
    agy = load_json(Path.home() / ".gemini/antigravity-cli/state/rate-limits.json")
    rows = [
        ("quota-windows.json", st / "quota-windows.json", (qw or {}).get("at"), fl.get("CODEX_PRESSURE_MAX_AGE_S"),
         "fleet.CODEX_PRESSURE_MAX_AGE_S",
         "codex %s%% (threshold %s), claude 5h %s 7d %s, agy 5h %s 7d %s" % (
             ((qw or {}).get("codex") or {}).get("used_percent"), ((qw or {}).get("codex") or {}).get("threshold"),
             (((qw or {}).get("claude") or {}).get("five_hour") or {}).get("utilization"),
             (((qw or {}).get("claude") or {}).get("seven_day") or {}).get("utilization"),
             (((qw or {}).get("agy") or {}).get("five_hour") or {}).get("used_percent"),
             (((qw or {}).get("agy") or {}).get("seven_day") or {}).get("used_percent"))),
        ("muse-code-usage.json", st / "muse-code-usage.json", (mu or {}).get("at"), fl.get("MUSE_PROBE_MAX_AGE_S"),
         "fleet.MUSE_PROBE_MAX_AGE_S", "ok=%s %s" % ((mu or {}).get("ok"), (mu or {}).get("detail"))),
        ("quota-history.jsonl (last line)", st / "quota-history.jsonl", (hist or {}).get("at"), sp.get("CONTROLLER_STALE_S"),
         "fleet-supply-probe.CONTROLLER_STALE_S", "%d pools" % len((hist or {}).get("pools") or {})),
        ("hopscotch-credit.json (prod)", st / "hopscotch-credit.json", ((hop or {}).get("prod") or {}).get("at"),
         cf.get("CREDIT_MAX_AGE_S"), "codex-fallback.CREDIT_MAX_AGE_S",
         "prod $%.2f (dsh floor $%s)" % ((((hop or {}).get("prod") or {}).get("availableBalanceMicros") or 0) / 1e6, cf.get("DSH_FLOOR_USD"))),
        # codex-fallback refreshes the agy cache when older than AGY_MAX_AGE_S, once per 10-min pass.
        ("agy rate-limits cache", Path.home() / ".gemini/antigravity-cli/state/rate-limits.json", (agy or {}).get("at"),
         (qr.get("AGY_MAX_AGE_S") or 0) + 15 * 60, "quota-runway.AGY_MAX_AGE_S + one pass",
         "windows %s" % sorted(((agy or {}).get("rate_limits") or {}).keys())),
    ]
    return rows


def cmd_readings(city):
    now = time.time()
    print(f"now {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))}")
    for name, path, at, max_s, src, detail in reading_rows(city, now):
        a = age(at, now)
        state = "MISSING" if a is None else "STALE" if max_s and a > max_s else "fresh"
        print(f"{name:<34} age {fmt_age(a):>7}  max {fmt_age(max_s):>5} ({src})  {state}  {detail}")
    hist = last_history(city) or {}
    for pool, r in sorted((hist.get("pools") or {}).items()):
        if "usd" in r:
            print(f"  history {pool:<22} ${r['usd']:.2f}")
        else:
            left = (r.get("resets_at") or now) - now
            print(f"  history {pool:<22} {r.get('used'):>5}%  resets in {fmt_age(left) if left > 0 else 'PAST'}")
    try:
        be = (city / ".gc/runtime/fleet/pool-backend").read_text().strip()
    except OSError:
        be = "(absent: codex)"
    print(f"pool-backend (this host): {be}")
    return 0


# ---------------------------------------------------------------------------------------------- placement

def cmd_placement(city):
    f = import_fleet(city)
    now = time.time()
    backend = f.pool_backend()
    quota = f.quota_reading()
    reading = f.muse_reading()
    print(f"host {f.NODE}  backend {backend}  quota-windows {'fresh' if quota else 'NONE/STALE (Sol-first defaults)'}")
    print(f"  codex swap at {f.codex_swap_percent(quota):.0f}%  codex window {f._window((quota or {}).get('codex'), now)}")
    print(f"  claude_spent {f.claude_spent(quota)}  sonnet_first {f.sonnet_first(quota)}  "
          f"muse_before_sonnet {f.muse_before_sonnet(quota)}  gemini_first {f.gemini_first(quota)}")
    mq = f.muse_quota(reading, now)
    print(f"  muse_available {f.muse_available()}  (binary {f.MUSE_BIN.exists()}, auth {f.MUSE_AUTH.exists()}, quota {mq[0]}: {mq[1]})"
          f"  muse_walled {f.muse_walled(reading, now)}")
    print(f"  agy_available {f.agy_available(quota, 'gateway-llm')}  (binary {f.AGY_BIN.exists()}, token {f.AGY_TOKEN.exists()})")
    jobs = [("fresh write", {"class": "write", "repo": "gateway-llm"}),
            ("hard write (effort high)", {"class": "write", "repo": "gateway-llm", "opts": {"effort": "high"}}),
            ("retry write", {"class": "write", "repo": "gateway-llm", "key": "retry:verify"}),
            ("plain read", {"class": "read", "repo": "gateway-llm"}),
            ("browser walk", {"class": "read", "repo": "gateway-llm", "provider": "browser"})]
    for label, job in jobs:
        t1 = f.t1_pool(job, backend)
        pool = f.placement_pool(job, backend)
        why = f"t1_pool -> {t1}" if t1 else f"pool_for -> {f.pool_for(job['class'], job.get('provider'), backend)}"
        print(f"{label:<26} pool {pool:<14} effort {f.t1_effort(job, pool) or '(default)':<10} {why}")
    pick = f.gateway_review_provider(backend)
    job = {"class": "read", "repo": "gateway-llm", "provider": pick}
    pool = f.placement_pool(job, backend)
    print(f"{'gateway review (no author)':<26} pool {pool:<14} effort {f.t1_effort(job, pool) or '(default)':<10} "
          f"gateway_review_provider -> {pick}")
    return 0


# ---------------------------------------------------------------------------------------------- orders

def enumerate_t1(f, hard, sonnet_first, muse_before):
    """The T1 order the code walks, found by removing each winner from the available set."""
    orig = (f.sonnet_first, f.muse_before_sonnet, f.claude_spent)
    f.sonnet_first = lambda q, now=None: sonnet_first
    f.muse_before_sonnet = lambda q, reading=None, now=None: muse_before
    f.claude_spent = lambda q, now=None: False
    try:
        avail, order = {"codex-sol", "claude-review", "agy-flash", "muse-code"}, []
        job = {"class": "write", "repo": "gateway-llm"}
        if hard:
            job["opts"] = {"effort": "high"}
        while avail:
            sol, cl = "codex-sol" in avail, "claude-review" in avail
            backend = "codex" if sol and cl else "codex-all" if sol else "claude" if cl else "dsh"
            got = f.t1_pool(job, backend, muse_ok="muse-code" in avail, quota={}, agy_ok="agy-flash" in avail)
            if got not in avail:
                order.append(f"?{got}")
                break
            order.append(got)
            avail.discard(got)
        return order
    finally:
        f.sonnet_first, f.muse_before_sonnet, f.claude_spent = orig


def enumerate_review(f, gem_first):
    orig = f.gemini_first
    f.gemini_first = lambda q, now=None: gem_first
    try:
        fam = {"muse": "muse", "sol": "sol", "gemini": "gemini", "sonnet": "claude"}
        authors, order = set(), []
        for _ in range(4):
            got = f.gateway_review_provider("codex", authors=tuple(authors), muse_ok=True, agy_ok=True, quota={})
            if fam.get(got) in authors:
                break
            order.append(got)
            authors.add(fam[got])
        return order
    finally:
        f.gemini_first = orig


def order_findings(city, verbose=False):
    f = import_fleet(city)
    out = []
    for hard, sf, mb in itertools.product((False, True), (False, True), (False, True)):
        got = enumerate_t1(f, hard, sf, mb)
        doc = list(DOC_T1["hard" if hard else "sonnet_first" if sf else "fresh"])
        if mb:  # v1.8 "Write-order modifiers": Muse moves to just ahead of Sonnet
            doc.remove("muse-code"); doc.insert(doc.index("claude-review"), "muse-code")
        label = f"t1 {'hard' if hard else 'fresh'} sonnet_first={sf} muse_before_sonnet={mb}"
        if verbose:
            print(f"{label:<52} code {' > '.join(got):<52} contract {' > '.join(doc)}")
        if got != doc:
            out.append(f"order drift: {label}: code {'>'.join(got)}, {CONTRACT_REV} documents {'>'.join(doc)}")
    for gf in (False, True):
        got, doc = enumerate_review(f, gf), DOC_REVIEW["gemini_first" if gf else "normal"]
        label = f"gateway review gemini_first={gf}"
        if verbose:
            print(f"{label:<52} code {' > '.join(got):<52} contract {' > '.join(doc)}")
        if got != doc:
            out.append(f"order drift: {label}: code {'>'.join(got)}, {CONTRACT_REV} documents {'>'.join(doc)}")
    return out


def cmd_orders(city):
    found = order_findings(city, verbose=True)
    for line in found:
        print(line)
    return 0


# ---------------------------------------------------------------------------------------------- doctor

def doctor(city):
    now, out = time.time(), []
    D = city / "dispatch"
    fl, cf = consts(D / "fleet.py"), consts(D / "codex-fallback.py")
    qr, sp = consts(D / "quota-runway.py"), consts(city / "orders/scripts/fleet-supply-probe.py")

    # 1. readings fresh against the max ages the code uses
    for name, path, at, max_s, src, detail in reading_rows(city, now):
        a = age(at, now)
        if a is None:
            out.append(f"reading missing: {name} ({path})")
        elif max_s and a > max_s:
            out.append(f"reading stale: {name} {fmt_age(a)} > {fmt_age(max_s)} ({src})")
    mu = load_json(city / ".gc/runtime/fleet/muse-code-usage.json")
    if isinstance(mu, dict) and mu.get("ok") is False:
        out.append(f"reading failing: muse-code-usage.json ok=false ({mu.get('detail')})")
    qw = load_json(city / ".gc/runtime/fleet/quota-windows.json") or {}
    if not ((qw.get("agy") or {}).get("seven_day")):
        out.append("reading missing: quota-windows.json has no agy.seven_day (agy_available reads unavailable)")

    # 2. constants mirrored across the four files agree
    pairs = [("fleet.CODEX_REVIEW_HEADROOM", fl, "CODEX_REVIEW_HEADROOM", "codex-fallback.FLEET_SWAP_HEADROOM", cf, "FLEET_SWAP_HEADROOM"),
             ("fleet.CLAUDE_BURST_PERCENT", fl, "CLAUDE_BURST_PERCENT", "codex-fallback.CLAUDE_BURST_PERCENT", cf, "CLAUDE_BURST_PERCENT"),
             ("fleet.AGY_SPENT_PERCENT", fl, "AGY_SPENT_PERCENT", "codex-fallback.AGY_SPENT_PERCENT", cf, "AGY_SPENT_PERCENT"),
             ("fleet.MUSE_PROBE_MAX_AGE_S", fl, "MUSE_PROBE_MAX_AGE_S", "fleet-supply-probe.MUSE_STALE_S", sp, "MUSE_STALE_S"),
             ("fleet.CODEX_PRESSURE_MAX_AGE_S", fl, "CODEX_PRESSURE_MAX_AGE_S", "fleet-supply-probe.CONTROLLER_STALE_S", sp, "CONTROLLER_STALE_S"),
             ("codex-fallback.DSH_FLOOR_USD", cf, "DSH_FLOOR_USD", "fleet-supply-probe.HOP_FLOOR_USD", sp, "HOP_FLOOR_USD"),
             ("codex-fallback.CREDIT_MAX_AGE_S", cf, "CREDIT_MAX_AGE_S", "fleet-supply-probe.HOP_STALE_S", sp, "HOP_STALE_S"),
             ("codex-fallback.LOGIN", cf, "LOGIN", "quota-runway.CODEX_LOGIN", qr, "CODEX_LOGIN")]
    for an, a, ak, bn, b, bk in pairs:
        if a.get(ak) != b.get(bk):
            out.append(f"constant drift: {an}={a.get(ak)!r} != {bn}={b.get(bk)!r}")
    if fl.get("CODEX_SWAP_PERCENT") != (cf.get("THRESHOLD") or 0) - (fl.get("CODEX_REVIEW_HEADROOM") or 0):
        out.append(f"constant drift: fleet.CODEX_SWAP_PERCENT={fl.get('CODEX_SWAP_PERCENT')} != codex-fallback.THRESHOLD-"
                   f"CODEX_REVIEW_HEADROOM={cf.get('THRESHOLD')}-{fl.get('CODEX_REVIEW_HEADROOM')}")
    if (qr.get("MUSE_MAX_AGE_S") or 0) < (cf.get("MUSE_REFRESH_S") or 0):
        out.append(f"constant drift: quota-runway.MUSE_MAX_AGE_S={qr.get('MUSE_MAX_AGE_S')}s < codex-fallback.MUSE_REFRESH_S="
                   f"{cf.get('MUSE_REFRESH_S')}s: history drops muse:5h/7d whenever the hourly reading is past 30m "
                   f"(dispatch/quota-runway.py MUSE_MAX_AGE_S comment says 'probed every 10-min pass')")

    # 3. every pool the code maps to is a provider in city.toml
    cfg = tomllib.loads((city / "city.toml").read_text())
    providers = set(cfg.get("providers", {}))
    named = {}
    for k in ("POOL_BACKENDS",):
        for be, m in (fl.get(k) or {}).items():
            for v in (m or {}).values():
                named.setdefault(v, f"fleet.{k}[{be}]")
    for k in ("EXPERIMENTAL_POOLS",):
        for alias, v in (fl.get(k) or {}).items():
            named.setdefault(v, f"fleet.{k}[{alias}]")
    for k in ("MUSE_POOL", "AGY_POOL", "BROWSER_FALLBACK_POOL"):
        if fl.get(k):
            named.setdefault(fl[k], f"fleet.{k}")
    named.setdefault((fl.get("POOLS") or {}).get("read"), "fleet.POOLS[read]")
    for k in ("SEAT_PROVIDER", "LIGHT_SEAT_PROVIDER", "IMPL_PROVIDER", "REVIEW_PROVIDER", "LIGHT_PROVIDER", "REVIEW_POOL_PROVIDER"):
        for be, v in (cf.get(k) or {}).items():
            named.setdefault(v, f"codex-fallback.{k}[{be}]")
    for login, m in (cf.get("CLAUDE_ON_LOGIN") or {}).items():
        for v in m.values():
            named.setdefault(v, f"codex-fallback.CLAUDE_ON_LOGIN[{login}]")
    for v in ("codex-sol", "claude-review", "claude-sonnet-high", "codex-sol-medium", "claude-browser", "claude-haiku", "claude-haiku-high"):
        named.setdefault(v, "codex-fallback literal")
    for pool, src in sorted(named.items(), key=lambda kv: str(kv[0])):
        if pool and pool not in providers and pool != "write-pool":
            out.append(f"provider missing: {pool} (named by {src}) has no [providers.{pool}] in city.toml")

    # 4. mayor provider, model and login
    mayor = tomllib.loads((city / "agents/mayor/agent.toml").read_text()).get("provider")
    if mayor != "claude-mayor":
        out.append(f"mayor drift: agents/mayor/agent.toml provider {mayor!r}, docs/mayor-provider.md says claude-mayor")
    cm = cfg.get("providers", {}).get("claude-mayor", {})
    flags = [a for o in cm.get("options_schema", []) if o.get("key") == "model" for c in o.get("choices", [])
             if c.get("value") == (cm.get("option_defaults") or {}).get("model") for a in c.get("flag_args", [])]
    if "claude-opus-5-5" not in flags:
        out.append(f"mayor drift: claude-mayor default model resolves to {flags}, docs/mayor-provider.md pins claude-opus-5-5")
    if (cm.get("option_defaults") or {}).get("effort") != "low":
        out.append(f"mayor drift: claude-mayor effort {(cm.get('option_defaults') or {}).get('effort')!r}, docs say low")
    cfg_dir = (cm.get("env") or {}).get("CLAUDE_CONFIG_DIR")
    dirs = cf.get("MAYOR_CONFIG_DIR") or {}
    pinned = next((n for n, d in dirs.items() if d == cfg_dir), None)
    hist = (last_history(city) or {}).get("pools") or {}
    want, known = None, False
    for name in cf.get("MAYOR_LOGINS") or ():
        wins = [hist.get(f"claude-{name}:{t}") for t in ("5h", "7d")]
        wins = [w for w in wins if isinstance(w, dict)]
        if not wins:
            continue
        known = True
        if not any((w.get("resets_at") or now + 1) > now and (w.get("used") or 0) >= (cf.get("MAYOR_THRESHOLD") or 95) for w in wins):
            want = name
            break
    if pinned is None:
        out.append(f"mayor drift: claude-mayor CLAUDE_CONFIG_DIR {cfg_dir!r} is not a MAYOR_CONFIG_DIR login")
    elif known and want and want != pinned:
        out.append(f"mayor drift: latest readings pick login {want} (MAYOR_LOGINS order, <{cf.get('MAYOR_THRESHOLD')}%), city.toml pins {pinned}")

    # 5. host backend consistent with the readings it was chosen from
    try:
        be = (city / ".gc/runtime/fleet/pool-backend").read_text().strip()
    except OSError:
        be = "codex"
    codex = qw.get("codex") or {}
    if be not in (fl.get("POOL_BACKENDS") or {}):
        out.append(f"backend drift: pool-backend {be!r} unknown to fleet.POOL_BACKENDS (reads as codex)")
    if be in ("codex", "codex-sol", "codex-all") and isinstance(codex.get("used_percent"), (int, float)) \
            and isinstance(codex.get("threshold"), (int, float)) and codex["used_percent"] >= codex["threshold"] \
            and (codex.get("resets_at") or 0) > now:
        out.append(f"backend drift: pool-backend {be} serves Sol but codex reads {codex['used_percent']}% >= threshold {codex['threshold']}")
    if be == "dsh":
        hop = load_json(city / ".gc/runtime/fleet/hopscotch-credit.json") or {}
        bal = ((hop.get("prod") or {}).get("availableBalanceMicros") or 0) / 1e6
        if bal < (cf.get("DSH_FLOOR_USD") or 5):
            out.append(f"backend drift: pool-backend dsh with prod balance ${bal:.2f} under the floor")

    # 6. docs agree with the code
    contract = (city / "docs/model-routing-contract.md").read_text()
    qf = (city / "docs/quota-fallback.md").read_text()
    if CONTRACT_REV not in contract:
        out.append(f"harness stale: docs/model-routing-contract.md no longer says {CONTRACT_REV}; re-read it and update DOC_T1/DOC_REVIEW")
    m = re.search(r"`T1_HARD_EFFORTS` is exactly ((?:`\w+`(?:, )?)+)", contract)
    if not m or tuple(re.findall(r"`(\w+)`", m.group(1))) != tuple(fl.get("T1_HARD_EFFORTS") or ()):
        out.append(f"doc drift: contract T1_HARD_EFFORTS {m and m.group(1)} vs code {fl.get('T1_HARD_EFFORTS')}")
    m = re.search(r"T1 considers Sonnet available only on ((?:`[\w-]+`(?:, )?)+)", contract)
    if not m or set(re.findall(r"`([\w-]+)`", m.group(1))) != set(fl.get("CLAUDE_BACKENDS") or ()):
        out.append(f"doc drift: contract Sonnet backends {m and m.group(1)} vs fleet.CLAUDE_BACKENDS {fl.get('CLAUDE_BACKENDS')}")
    checks = [(contract, r"five-hour window under (\d+)%", "MUSE_WINDOW_SPENT", fl), (contract, r"no window at (\d+)%", "MUSE_HARD_WALL", fl),
              (contract, r"five-hour window is ≥ (\d+)%", "CLAUDE_BURST_PERCENT", fl),
              (contract, r"`CODEX_REVIEW_HEADROOM` (\d+) points", "CODEX_REVIEW_HEADROOM", fl),
              (contract, r"no Antigravity window at (\d+)%", "AGY_SPENT_PERCENT", fl),
              (qf, r"\| `claude` \| codex ≥(\d+)%", "THRESHOLD", cf), (qf, r"both Claude logins ≥(\d+)%", "CLAUDE_THRESHOLD", cf),
              (qf, r"balance ≥ \$(\d+)", "DSH_FLOOR_USD", cf)]
    for text, rx, key, src in checks:
        m = re.search(rx, text)
        if not m or float(m.group(1)) != float(src.get(key) or -1):
            out.append(f"doc drift: /{rx}/ reads {m and m.group(1)} vs {key}={src.get(key)}")
    for rx, key in ((r"at most (\d+) h old", "MUSE_PROBE_MAX_AGE_S"), (r"a reading older than (\d+) min", "CODEX_PRESSURE_MAX_AGE_S")):
        m = re.search(rx, contract)
        unit = 3600 if " h " in rx else 60
        if not m or int(m.group(1)) * unit != fl.get(key):
            out.append(f"doc drift: contract /{rx}/ reads {m and m.group(1)} vs fleet.{key}={fl.get(key)}s")
    # quota-fallback.md backend table: writes, reads, seats columns
    for be, writes, reads, seats in re.findall(r"^\| `([\w-]+)` \|[^|]*\| ([\w-]+) \| ([\w-]+) \| ([\w-]+) \|", qf, re.M):
        pm = (fl.get("POOL_BACKENDS") or {}).get(be, {})
        if pm.get("write-pool", "write-pool") != writes:
            out.append(f"doc drift: quota-fallback.md backend {be} writes {writes}, fleet.POOL_BACKENDS maps write-pool to {pm.get('write-pool')}")
        if pm.get("claude-review", "claude-review") != reads:
            out.append(f"doc drift: quota-fallback.md backend {be} reads {reads}, fleet.POOL_BACKENDS maps claude-review to {pm.get('claude-review', 'claude-review')}")
        code_seats = {(cf.get("SEAT_PROVIDER") or {}).get(be), (cf.get("LIGHT_SEAT_PROVIDER") or {}).get(be)}
        if seats not in code_seats:
            out.append(f"doc drift: quota-fallback.md backend {be} seats {seats}, codex-fallback SEAT_PROVIDER/LIGHT_SEAT_PROVIDER give {sorted(map(str, code_seats))}")
    if "not in `MUSE_HOSTS`" in qf and "hailey" in (cf.get("MUSE_HOSTS") or ()):
        out.append("doc drift: docs/quota-fallback.md says Hailey is 'not in `MUSE_HOSTS`', codex-fallback.MUSE_HOSTS includes hailey")
    # rules t1_pool applies but the contract never names
    t1 = func_src(D / "fleet.py", "t1_pool") + func_src(D / "fleet.py", "placement_pool")
    for rule in ("sonnet_first", "muse_before_sonnet", "claude_spent", "agy_available", "muse_available"):
        if rule + "(" in t1 and rule not in contract:
            out.append(f"doc drift: fleet.t1_pool/placement_pool apply {rule}, docs/model-routing-contract.md never names it")
    # the implementer role pins claim "same order as fresh writes"
    impl = func_src(D / "codex-fallback.py", "implementer_provider")
    for rule in ("sonnet_first", "muse_before_sonnet"):
        if (rule + "(" in func_src(D / "fleet.py", "t1_pool") and rule not in impl
                and f"do\nnot yet apply `{rule}`" not in contract and f"do not yet apply `{rule}`" not in contract):
            out.append(f"code drift: fleet.t1_pool applies {rule}, codex-fallback.implementer_provider does not "
                       f"(contract: implementer pins follow the same order as fresh writes)")

    # 7. the code's actual orders vs the contract's tables
    try:
        out += order_findings(city)
    except Exception as e:
        out.append(f"order check failed: {type(e).__name__}: {e}")

    # 8. the controller timer is armed
    try:
        st = subprocess.run(["systemctl", "--user", "is-active", "codex-fallback.timer"], capture_output=True, text=True, timeout=10).stdout.strip()
        if st != "active":
            out.append(f"controller: codex-fallback.timer is {st or 'unknown'}")
    except Exception:
        pass
    return out


def cmd_doctor(city):
    found = doctor(city)
    for line in found:
        print(line)
    if not found:
        print("quota-routing: clean")
    return 1 if found else 0


def cmd_supply(city):
    p = subprocess.run([sys.executable, str(city / "orders/scripts/fleet-supply-probe.py"), "providers"],
                       capture_output=True, text=True, timeout=120, env={**os.environ, "FLEET_CITY": str(city)})
    sys.stdout.write(p.stdout or "(no tripped probe)\n")
    sys.stderr.write(p.stderr)
    return p.returncode


def main(argv):
    args = [a for i, a in enumerate(argv) if a != "--city" and (i == 0 or argv[i - 1] != "--city")]
    if not args or args[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    city = city_dir(argv)
    cmds = {"doctor": cmd_doctor, "readings": cmd_readings, "placement": cmd_placement, "orders": cmd_orders, "supply": cmd_supply}
    if args[0] not in cmds:
        print(f"unknown subcommand {args[0]!r}; see --help", file=sys.stderr)
        return 2
    return cmds[args[0]](city)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
