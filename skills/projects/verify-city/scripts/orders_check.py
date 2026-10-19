#!/usr/bin/env python3
"""orders_check.py: read-only verification harness for the city's orders.

Usage:
  orders_check.py [--city DIR] doctor [--no-history]
  orders_check.py [--city DIR] inventory [--no-history] [--json]
  orders_check.py [--city DIR] order <name>
  orders_check.py [--city DIR] seats

doctor     one line per finding, exit 1 on any; else "orders: clean", exit 0.
inventory  every order gc loads (city files and packs): trigger, schedule or check, target,
           enabled, runs in the last 24h against the declared cadence, the run log it keeps.
order      one order's full picture: file, gc order show, script header, last runs with
           their tracking-bead labels (exec-failed shows here), run log tails.
seats      the delegated-seat wake state under .gc/runtime/fleet/seats/<seat>/.

Read-only by construction: it parses TOML, reads files, and calls only `gc order list --json`,
`gc order show`, `gc order history --json`, `gc order --help` and `gc bd show --json`.
It never runs `gc order check` (that RUNS condition checks), `gc order run`, or any order
script, and never mails or writes beads.
"""
import argparse, json, os, re, shlex, shutil, subprocess, sys, time, tomllib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

GC_DOCS = Path.home() / ".cache/gascity-docs/docs"
TRIGGER_FIELD = {"cooldown": "interval", "cron": "schedule", "condition": "check", "event": "on", "manual": None}
KNOWN_KEYS = {"description", "formula", "exec", "trigger", "gate", "interval", "schedule", "check",
              "check_timeout", "on", "pool", "timeout", "idempotent", "no_work_gate",
              "reserved_dispatch", "requires_backend", "enabled", "scope", "env", "tz"}
INTERPRETERS = {"python3", "python", "bash", "sh", "/usr/bin/python3", "/bin/bash", "/bin/sh", "/usr/bin/env"}
# City-relative paths a comment may name. .gc/runtime state is not a reference.
REF_RE = re.compile(r"(?<![\w/.$-])((?:orders|dispatch|docs|hooks|formulas|agents)/[\w./-]*\w\.(?:sh|py|md|toml|jsonl|json|tsv|txt|mjs))(?![\w.])")
UTC_CLAIM_RE = re.compile(r"\b(\d{1,2}):(\d{2}) ?Z\b")
GC_ORDER_SUB_RE = re.compile(r"\bgc order ([a-z][a-z-]+)")


def run(args, cwd, timeout=120):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 99, "", str(e)


def go_seconds(s):
    if not s:
        return None
    total, n = 0, 0
    for num, unit in re.findall(r"(\d+(?:\.\d+)?)(h|ms|m|s|d)", str(s)):
        total += float(num) * {"d": 86400, "h": 3600, "m": 60, "s": 1, "ms": 0.001}[unit]
        n += 1
    return total if n else None


def cron_per_day(schedule):
    """Approximate firings per day for a 5-field cron (dow-restricted -> fraction)."""
    try:
        mi, hr, dom, mon, dow = schedule.split()
    except ValueError:
        return None

    def count(field, lo, hi):
        vals = set()
        for part in field.split(","):
            step = 1
            if "/" in part:
                part, st = part.split("/")
                step = int(st)
            if part == "*":
                a, b = lo, hi
            elif "-" in part:
                a, b = map(int, part.split("-"))
            else:
                a = int(part)
                b = a if step == 1 else hi
            vals.update(range(a, b + 1, step))
        return len(vals)

    try:
        per = count(mi, 0, 59) * count(hr, 0, 23)
        if dow != "*":
            per *= count(dow, 0, 6) / 7
        if dom != "*":
            per *= count(dom, 1, 31) / 30
        return per
    except ValueError:
        return None


class City:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.orders_dir = self.root / "orders"
        self.cfg = {}
        try:
            self.cfg = tomllib.loads((self.root / "city.toml").read_text())
        except Exception:
            pass
        self._listing = None
        self._history = None

    # ---------- local files ----------
    def files(self):
        out = {}
        for f in sorted(self.orders_dir.glob("*.toml")):
            try:
                data = tomllib.loads(f.read_text())
                out[f.stem] = (f, data.get("order"), None)
            except Exception as e:
                out[f.stem] = (f, None, str(e))
        return out

    def env(self, order_file):
        return {"GC_CITY_PATH": str(self.root), "GC_CITY": str(self.root), "ORDER_DIR": str(order_file.parent),
                "CITY": str(self.root), "HOME": str(Path.home())}

    def expand(self, s, order_file):
        e = self.env(order_file)
        s = re.sub(r"\$\{(\w+)[^}]*\}", lambda m: e.get(m.group(1), m.group(0)), s)
        s = re.sub(r"\$(\w+)", lambda m: e.get(m.group(1), m.group(0)), s)
        return os.path.expanduser(s)

    def targets(self, cmd, order_file):
        """Yield (path_or_cmd, kind) per command segment: kind 'exec' needs +x, 'script' needs
        to exist, 'path-cmd' needs PATH resolution."""
        cmd = self.expand(cmd, order_file)
        for seg in re.split(r"&&|\|\||;|\|", cmd):
            try:
                toks = shlex.split(seg)
            except ValueError:
                toks = seg.split()
            while toks and (re.match(r"^\w+=", toks[0]) or toks[0] == "env"):
                toks.pop(0)
            if not toks:
                continue
            if toks[0] == "cd":
                continue
            if toks[0] in INTERPRETERS:
                rest = [t for t in toks[1:] if not t.startswith("-") and not re.match(r"^\w+=", t)]
                if rest and ("/" in rest[0] or rest[0].endswith((".sh", ".py"))):
                    yield rest[0], "script"
                continue
            yield toks[0], ("exec" if "/" in toks[0] else "path-cmd")

    def script_paths(self, od, order_file):
        paths = []
        for key in ("exec", "check"):
            if od.get(key):
                for t, kind in self.targets(od[key], order_file):
                    if kind != "path-cmd":
                        paths.append(Path(t))
        return paths

    # ---------- gc reads ----------
    def listing(self):
        if self._listing is None:
            rc, out, err = run(["gc", "order", "list", "--json"], self.root)
            try:
                self._listing = {o["name"]: o for o in json.loads(out)["orders"]}
            except Exception:
                self._listing = {"__error__": (rc, (err or out)[:300])}
        return self._listing

    def history24(self):
        if self._history is None:
            rc, out, err = run(["gc", "order", "history", "--json", "--since", "24h", "--limit", "0"], self.root, timeout=180)
            try:
                self._history = json.loads(out).get("entries", [])
            except Exception:
                self._history = None
        return self._history

    def tz(self, od):
        if od.get("tz"):
            return od["tz"]
        ws = (self.cfg.get("workspace") or {}).get("timezone")
        if ws:
            return ws
        if os.environ.get("TZ"):
            return os.environ["TZ"]
        try:
            return str(Path("/etc/localtime").resolve()).split("zoneinfo/")[1]
        except Exception:
            return "local"

    def run_logs(self, name, od, order_file):
        """Run logs/stamps the order's script keeps under .gc/runtime, by name match and by the
        LOG/RUNLOG/STAMP/STATE assignments in the script."""
        rt = self.root / ".gc/runtime"
        found = set()
        stems = {name}
        for p in self.script_paths(od, order_file):
            stems.add(p.stem.replace("_", "-"))
            try:
                text = p.read_text(errors="replace")
            except OSError:
                continue
            for m in re.finditer(r"\.gc/runtime/([\w./-]*\w\.(?:log|last|json|jsonl|tsv))", text):
                found.add(rt / m.group(1))
            for m in re.finditer(r'(?:LOG|STAMP)="?\$\{?\w+\}?/(?:\.gc/)?runtime/([\w.-]+)', text):
                found.add(rt / m.group(1))
            for m in re.finditer(r'(?:LOG|STAMP)=\$\{(?:LOG|STAMP):-\$GCDIR/([\w.-]+)\}', text):
                found.add(rt / m.group(1))
        for s in stems:
            for ext in ("log", "last", "json", "jsonl"):
                found.add(rt / f"{s}.{ext}")
            for f in rt.glob(f"{s}.*.log"):
                found.add(f)
        el = rt / "order-elapsed" / name
        if el.exists():
            found.add(el)
        return sorted(f for f in found if f.is_file())


def header_block(path):
    try:
        lines = path.read_text(errors="replace").splitlines()[:80]
    except OSError:
        return ""
    out, started = [], False
    if path.suffix == ".py":
        text = "\n".join(lines)
        m = re.search(r'^(?:#![^\n]*\n)?(?:#[^\n]*\n)*\s*("""|\'\'\')(.*?)\1', text, re.S)
        if m:
            return m.group(2)
    for ln in lines:
        if ln.startswith("#!"):
            continue
        if ln.startswith("#"):
            out.append(ln)
            started = True
        elif started or ln.strip():
            if started:
                break
    return "\n".join(out)


def comments(path):
    try:
        return "\n".join(l for l in path.read_text().splitlines() if l.lstrip().startswith("#"))
    except OSError:
        return ""


def line_of(path, needle):
    try:
        for i, l in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if needle in l:
                return f":{i}"
    except OSError:
        pass
    return ""


def ref_exists(city, ref):
    if (city.root / ref).exists():
        return True
    if ref.startswith("docs/") and (GC_DOCS / ref[len("docs/"):]).exists():
        return True
    return False


def doctor(city, no_history):
    findings = []
    add = findings.append
    files = city.files()
    listing = city.listing()
    if "__error__" in listing:
        add(f"gc-order-list: failed rc={listing['__error__'][0]}: {listing['__error__'][1]}")
        listing = {}
    skip = set((city.cfg.get("orders") or {}).get("skip") or [])
    rc, out, _ = run(["gc", "order", "--help"], city.root)
    subs = set(re.findall(r"^  ([a-z][a-z-]+)\s+\S", out.split("Available Commands:")[-1].split("Flags:")[0], re.M)) if rc == 0 else set()
    formulas = {p.name.split(".")[0] for p in (city.root / "formulas").glob("*.toml")}
    hist = None if no_history else city.history24()
    runs = Counter(e["order"] for e in hist) if hist is not None else None
    if not no_history and hist is None:
        add("gc-order-history: `gc order history --json --since 24h` did not return JSON")

    for name, (f, od, err) in files.items():
        rel = f.relative_to(city.root)
        if err:
            add(f"{name}: {rel} does not parse: {err}")
            continue
        if not isinstance(od, dict):
            add(f"{name}: {rel} has no [order] table")
            continue
        unknown = set(od) - KNOWN_KEYS
        if unknown:
            add(f"{name}: unknown [order] keys {sorted(unknown)}")
        trig = od.get("trigger") or od.get("gate")
        if trig not in TRIGGER_FIELD:
            add(f"{name}: trigger {trig!r} is not one of {sorted(TRIGGER_FIELD)}")
        elif TRIGGER_FIELD[trig] and not od.get(TRIGGER_FIELD[trig]):
            add(f"{name}: trigger {trig} without `{TRIGGER_FIELD[trig]}`")
        if bool(od.get("formula")) == bool(od.get("exec")):
            add(f"{name}: needs exactly one of formula/exec")
        if od.get("exec") and od.get("pool"):
            add(f"{name}: exec order sets pool (exec orders cannot)")
        if od.get("formula") and od.get("env"):
            add(f"{name}: formula order sets env (env is exec-only)")
        if od.get("formula"):
            layer = Path((listing.get(name) or {}).get("formula_layer") or city.root / "formulas")
            if od["formula"] not in formulas and not list(layer.glob(od["formula"] + ".*toml")):
                add(f"{name}: formula {od['formula']} not in formulas/ or {layer}")
        if trig == "condition" and not od.get("check_timeout"):
            add(f"{name}: condition order has no check_timeout (gc default 10s applies to `{od.get('check')}`)")
        # exec/check targets
        for key in ("exec", "check"):
            if not od.get(key):
                continue
            for t, kind in city.targets(od[key], f):
                if kind == "path-cmd":
                    if not shutil.which(t):
                        add(f"{name}: {key} command `{t}` not on PATH")
                elif not Path(t).exists():
                    add(f"{name}: {key} target {t} does not exist")
                elif kind == "exec" and not os.access(t, os.X_OK):
                    add(f"{name}: {key} target {t} is not executable")
        # in gc order list, from this file
        enabled = od.get("enabled", True)
        if enabled and name not in skip and listing:
            got = listing.get(name)
            if not got:
                add(f"{name}: {rel} is not in `gc order list`")
            elif Path(got.get("source", "")).resolve() != f.resolve():
                add(f"{name}: `gc order list` loads it from {got.get('source')}, not {rel}")
            elif got.get("enabled") is False:
                add(f"{name}: `gc order list` shows it disabled")
        # references in the order's comments and its scripts' headers
        texts = [(rel, comments(f))]
        for p in city.script_paths(od, f):
            if p.exists() and city.root in p.resolve().parents:
                texts.append((p.resolve().relative_to(city.root), header_block(p)))
        for src, text in texts:
            for ref in sorted(set(REF_RE.findall(text))):
                # a ledger the script itself appends to is born on its first record, not a reference
                if ref.startswith("dispatch/ledgers/") and src != rel:
                    continue
                if not ref_exists(city, ref):
                    add(f"{name}: {src}{line_of(city.root / src, ref)} names {ref}, which does not exist")
            for sub in sorted(set(GC_ORDER_SUB_RE.findall(text))):
                if subs and sub not in subs:
                    add(f"{name}: {src}{line_of(city.root / src, 'gc order ' + sub)} cites `gc order {sub}`, not a gc order subcommand ({', '.join(sorted(subs))})")
        # cron comment claims a UTC time but the schedule runs in another zone
        if trig == "cron":
            tz = city.tz(od)
            if tz not in ("UTC", "Etc/UTC", "Z") and UTC_CLAIM_RE.search(comments(f)):
                ln = next(i for i, l in enumerate(f.read_text().splitlines(), 1) if l.startswith("#") and UTC_CLAIM_RE.search(l))
                add(f"{name}: {rel}:{ln} states a UTC time but schedule `{od.get('schedule')}` is evaluated in {tz} (no tz, no [workspace] timezone)")
        # a frequent clock order that never ran in 24h
        if runs is not None and enabled and name not in skip:
            per_day = None
            if trig == "cooldown":
                sec = go_seconds(od.get("interval"))
                per_day = 86400 / sec if sec else None
            elif trig == "cron":
                per_day = cron_per_day(od.get("schedule", ""))
            if per_day and per_day >= 2 and runs.get(name, 0) == 0:
                add(f"{name}: expected ~{per_day:.0f} runs/24h, `gc order history --since 24h` shows none")
    for s in sorted(skip):
        if s not in files and s not in listing:
            pass  # pack orders skipped by name: absent from list by design
    for f in sorted((city.orders_dir / "remote").glob("*.toml")) if (city.orders_dir / "remote").is_dir() else []:
        try:
            od = tomllib.loads(f.read_text()).get("order") or {}
        except Exception as e:
            add(f"remote/{f.name}: does not parse: {e}")
            continue
        for t, kind in city.targets(od.get("exec", ""), city.orders_dir / f.name):
            if kind != "path-cmd" and not Path(t).exists():
                add(f"remote/{f.name}: exec target {t} does not exist in this checkout")
    return findings


def inventory(city, no_history, as_json):
    files = city.files()
    listing = city.listing()
    hist = None if no_history else city.history24()
    runs = Counter(e["order"] for e in hist) if hist else Counter()
    last = {}
    for e in hist or []:
        if e["executed"] > last.get(e["order"], ""):
            last[e["order"]] = e["executed"]
    rows = []
    names = sorted(set(listing) | set(files) - {"__error__"}, key=lambda n: (n not in files, n))
    for n in names:
        if n == "__error__":
            continue
        lo = listing.get(n) or {}
        od = (files.get(n) or (None, None, None))[1] or {}
        trig = lo.get("trigger") or od.get("trigger")
        sched = lo.get("interval") or lo.get("schedule") or od.get("interval") or od.get("schedule") or lo.get("on") or od.get("on") or ""
        if trig == "condition":
            sched = f"check: {od.get('check') or lo.get('check')} (timeout {od.get('check_timeout', '10s default')})"
        tgt = (f"formula {od.get('formula') or lo.get('formula')} -> pool {od.get('pool') or lo.get('pool')}"
               if (od.get("formula") or lo.get("formula")) else f"exec {od.get('exec') or lo.get('exec')}")
        per_day = None
        if trig == "cooldown":
            sec = go_seconds(sched)
            per_day = 86400 / sec if sec else None
        elif trig == "cron":
            per_day = cron_per_day(sched)
        src = "city" if n in files else ("pack" if lo else "?")
        logs = []
        if n in files and files[n][1]:
            logs = [str(p.relative_to(city.root)) + " @" + datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
                    for p in city.run_logs(n, files[n][1], files[n][0])]
        rows.append({"name": n, "source": src, "trigger": trig, "when": sched,
                     "tz": city.tz(od) if trig == "cron" else None, "target": tgt,
                     "enabled": lo.get("enabled", False) if lo else False,
                     "runs_24h": None if hist is None else runs.get(n, 0),
                     "expected_24h": None if per_day is None else round(per_day, 1),
                     "last_run_24h": last.get(n), "run_logs": logs})
    if as_json:
        print(json.dumps(rows, indent=1))
        return
    for r in rows:
        enabled = "enabled" if r["enabled"] else "NOT-LISTED"
        cad = "" if r["runs_24h"] is None else f" runs24h={r['runs_24h']}" + (f"/~{r['expected_24h']:g}" if r["expected_24h"] else "")
        tz = f" [{r['tz']}]" if r["tz"] else ""
        print(f"{r['name']} ({r['source']}, {enabled}) {r['trigger']} {r['when']}{tz} | {r['target']}{cad} last={r['last_run_24h'] or '-'}")
        for lg in r["run_logs"]:
            print(f"    runtime {lg}")
    print(f"orders: {len(rows)} loaded or on disk ({sum(r['source']=='city' for r in rows)} city files)")


def order(city, name):
    files = city.files()
    if name not in files and name not in city.listing():
        print(f"orders: no order {name!r}", file=sys.stderr)
        return 2
    if name in files:
        f, od, err = files[name]
        print(f"== file {f.relative_to(city.root)}")
        print(f.read_text())
    rc, out, err = run(["gc", "order", "show", name], city.root)
    print(f"== gc order show {name} (rc={rc})\n{out}{err}")
    if name in files and files[name][1]:
        f, od, _ = files[name]
        for p in city.script_paths(od, f):
            print(f"== script {p} exists={p.exists()} executable={os.access(p, os.X_OK)}")
            if p.exists():
                print(header_block(p))
    rc, out, err = run(["gc", "order", "history", name, "--json", "--limit", "5"], city.root)
    try:
        entries = json.loads(out).get("entries", [])
    except Exception:
        entries = []
    print(f"== last runs (gc order history keeps ~24h; a weekly order reads empty) rc={rc}")
    if not entries:
        print("   none retained")
    for e in entries:
        rc2, b, _ = run(["gc", "bd", "show", e["bead_id"], "--json"], city.root)
        try:
            bead = json.loads(b[b.index("["):])[0]
            labels = ",".join(bead.get("labels") or [])
            dur = ""
            if bead.get("closed_at"):
                t0 = datetime.fromisoformat(bead["created_at"].replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(bead["closed_at"].replace("Z", "+00:00"))
                dur = f" took {int((t1 - t0).total_seconds())}s"
            print(f"   {e['executed']} {e['bead_id']} {bead.get('status')}{dur} labels={labels} reason={bead.get('close_reason', '')!r}")
        except Exception:
            print(f"   {e['executed']} {e['bead_id']} (bead not readable)")
    if name in files and files[name][1]:
        for p in city.run_logs(name, files[name][1], files[name][0]):
            age = int(time.time() - p.stat().st_mtime)
            print(f"== runtime file {p.relative_to(city.root)} ({p.stat().st_size} B, {age}s old), last 5 lines:")
            try:
                with open(p, "rb") as fh:
                    fh.seek(max(0, p.stat().st_size - 4000))
                    print("\n".join(fh.read().decode(errors="replace").splitlines()[-5:]))
            except OSError as e:
                print(f"   unreadable: {e}")
    return 0


def seats(city):
    root = city.root / ".gc/runtime/fleet/seats"
    if not root.is_dir():
        print(f"orders: no seat state at {root}")
        return 0
    now = time.time()

    def rd(p):
        try:
            return p.read_text().strip()
        except OSError:
            return ""

    def age(p):
        return f"{int(now - p.stat().st_mtime)}s" if p.exists() else "-"

    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        pend, last = rd(d / "pending-signature"), rd(d / "last-signature")
        head = (rd(d / "pending.txt").splitlines() or ["(empty)"])[0]
        lines = len(rd(d / "pending.txt").splitlines())
        state = "idle" if not pend else ("claimed" if pend == last else "UNCLAIMED")
        order_f = city.orders_dir / f"{d.name}-pass.toml"
        print(f"{d.name}: {state} pending={pend or '-'} last={last or '-'} (claimed {age(d / 'last-signature')} ago) "
              f"last-probe {age(d / 'last-probe')} ago, pending.txt {lines} lines, alarm-sent={rd(d / 'alarm-sent') or '-'}, "
              f"order {'orders/' + order_f.name if order_f.exists() else 'NONE'}")
        print(f"    {head}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", default=os.environ.get("GC_CITY") or str(Path.home() / "city"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("doctor", help="one line per finding; exit 1 on any")
    d.add_argument("--no-history", action="store_true", help="skip the 24h history read (~30s)")
    i = sub.add_parser("inventory", help="every order: trigger, schedule, target, runs, logs")
    i.add_argument("--no-history", action="store_true")
    i.add_argument("--json", action="store_true")
    o = sub.add_parser("order", help="one order's full picture")
    o.add_argument("name")
    sub.add_parser("seats", help="delegated-seat wake state")
    a = ap.parse_args()
    city = City(a.city)
    if a.cmd == "doctor":
        fs = doctor(city, a.no_history)
        for f in fs:
            print(f)
        if not fs:
            print("orders: clean")
        return 1 if fs else 0
    if a.cmd == "inventory":
        inventory(city, a.no_history, a.json)
        return 0
    if a.cmd == "order":
        return order(city, a.name)
    return seats(city)


if __name__ == "__main__":
    sys.exit(main())
