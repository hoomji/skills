#!/usr/bin/env python3
"""Read-only checks and drives for the city's resource guard (verify-city feature `resource-guard`).

Usage:
  resource_guard_check.py [--city DIR] doctor        findings, one per line; exit 1 on any
  resource_guard_check.py [--city DIR] state         live lane reservations, permits and tickets vs the pool
  resource_guard_check.py [--city DIR] classes       policy classes, code-default drift, who names each class
  resource_guard_check.py [--city DIR] prove-permit  run `true` under the smallest permit class (writes, see below)

doctor, state and classes only read: files under the city, /proc, /sys/fs/cgroup and
`systemctl --user show/list-units`. They never call resource_guard's own helpers
(permit_tickets() and friends unlink dead files as a side effect) and never print the
supervisor environment beyond its PATH (it carries provider API keys).

prove-permit is the one drive that acts: it runs
  python3 <city>/dispatch/resource_guard.py --permit <class> --timeout 60 -- true
where <class> is the permit class with the smallest reserve. The guard writes a transient
ticket and grant record under .gc/runtime/fleet/permits/ (both removed in its `finally`),
starts a `fleet-permit-*.scope` in fleet-permits.slice, and on a grant appends one record
to .gc/runtime/fleet/resource-results/commands/. It exits 0 on a grant or 75
(RESOURCE-BLOCKED) when 60 s of queueing behind older tickets ran out; both prove the path.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys

GIB = 1 << 30
SHIM_NAMES = ('pnpm', 'npm', 'npx', 'tsc', 'vitest', 'node', 'bazel')
PERMIT_RE = re.compile(r'--permit[ =]([a-z][a-z0-9_-]*)\b')
SCAN_DIRS = ('docs', 'agents', 'formulas', 'orders', 'prompts', 'dispatch')
SKIP_PARTS = ('evidence-', 'worktrees', '__pycache__', 'ledgers', 'node_modules')
MEMORY = Path.home() / '.claude/projects/-home-coolhenrylinux-city/memory'


def city_path(arg):
    return Path(arg or os.environ.get('GC_CITY') or Path.home() / 'city').expanduser().resolve()


def fleet(city):
    return city / '.gc/runtime/fleet'


def load_policy(city):
    """(raw json or None, error, validated policy via the city's own resource_policy)."""
    path = fleet(city) / 'resource-policy.json'
    raw, err = None, None
    try:
        raw = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        err = str(exc)
    sys.path.insert(0, str(city / 'dispatch'))
    try:
        import resource_policy  # definitions only at import time
    finally:
        sys.path.pop(0)
    return raw, err, resource_policy.load(city), resource_policy


def lane_classes(city):
    """Keys of resource_guard.POLICY, read by AST (importing the guard runs host probes)."""
    tree = ast.parse((city / 'dispatch/resource_guard.py').read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'POLICY' for t in node.targets) \
                and isinstance(node.value, ast.Dict):
            return [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    return []


def boot_id():
    try:
        return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    except OSError:
        return ''


def alive(rec):
    try:
        return rec['boot'] == boot_id() and Path('/proc/%s/stat' % rec['pid']).read_text().split()[21] == rec['start']
    except (OSError, KeyError, IndexError, TypeError):
        return False


def populated(cgroup):
    if not cgroup:
        return False
    try:
        return 'populated 1' in (Path('/sys/fs/cgroup') / cgroup.lstrip('/') / 'cgroup.events').read_text()
    except OSError:
        return False


def mem_current(cgroup):
    try:
        return int((Path('/sys/fs/cgroup') / cgroup.lstrip('/') / 'memory.current').read_text())
    except (OSError, ValueError, AttributeError):
        return 0


def units(pattern):
    """{unit: (load, active, sub)} for user units matching pattern, all states."""
    out = subprocess.run(['systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend', pattern],
                         capture_output=True, text=True, timeout=15).stdout
    rows = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 4:
            rows[f[0]] = (f[1], f[2], f[3])
    return rows


def unit_prop(unit, prop):
    return subprocess.run(['systemctl', '--user', 'show', unit, '-p', prop, '--value'],
                          capture_output=True, text=True, timeout=10).stdout.strip()


def supervisor_path():
    env = unit_prop('gascity-supervisor', 'Environment')
    m = re.search(r'(?:^|\s)PATH=(\S+)', env)
    return m.group(1) if m else ''


def mem_available():
    m = re.search(r'^MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text(), re.M)
    return int(m.group(1)) * 1024


def permit_files(city):
    rows = []
    for p in sorted((fleet(city) / 'permits').glob('*')):
        kind = p.name.rsplit('.', 1)[-1]
        try:
            rec = json.loads(p.read_text())
            err = None
        except (OSError, ValueError) as exc:
            rec, err = {}, 'unparsable (%s bytes): %s' % (p.stat().st_size if p.exists() else '?', exc)
        rows.append({'path': p, 'kind': kind, 'rec': rec, 'err': err, 'alive': alive(rec) if rec else False,
                     'populated': populated(rec.get('cgroup')) if rec else False})
    return rows


def resource_records(city):
    rows = []
    for p in (fleet(city) / 'resources').glob('*.json'):
        try:
            rec = json.loads(p.read_text())
        except (OSError, ValueError):
            rec = {}
        rows.append((p, rec, alive(rec), populated(rec.get('cgroup'))))
    return rows


def scan_permit_names(city):
    """[(file:line, class)] for every `--permit <name>` in the city's docs, prompts, scripts and memory."""
    hits = []
    files = []
    for d in SCAN_DIRS:
        base = city / d
        if base.is_dir():
            files += [p for p in base.rglob('*') if p.is_file() and p.suffix in ('.md', '.toml', '.sh', '.py', '.template', '')
                      and not any(s in str(p.relative_to(city)) for s in SKIP_PARTS)
                      and not (d == 'dispatch' and p.suffix == '.md')]  # dispatch/*.md are run reports
    files += sorted(MEMORY.glob('*.md')) if MEMORY.is_dir() else []
    for p in files:
        try:
            text = p.read_text(errors='replace')
        except OSError:
            continue
        if '--permit' not in text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in PERMIT_RE.finditer(line):
                if m.group(1) in ('class',):
                    continue
                hits.append(('%s:%d' % (p, i), m.group(1)))
    return hits


def doctor(city):
    f = []
    raw, err, pol, _ = load_policy(city)
    if err:
        f.append('policy-parse: .gc/runtime/fleet/resource-policy.json does not parse: ' + err)
    elif not pol['source'].endswith('resource-policy.json'):
        f.append('policy-rejected: guard falls back to ' + pol['source'])
    elif pol['mode'] != 'active':
        f.append('policy-mode: mode is %s; --permit execs commands unguarded' % pol['mode'])
    cmds = pol['commands']
    for where, name in scan_permit_names(city):
        if name not in cmds:
            f.append('permit-unknown-class: %s names --permit %s, not a policy class; the guard execs it with no permit' % (where, name))
        elif not cmds[name]['permit']:
            f.append('permit-false-class: %s names --permit %s, a permit:false class; it runs with no permit' % (where, name))
    for p in sorted((city / 'docs').rglob('*.md')):
        for i, line in enumerate(p.read_text(errors='replace').splitlines(), 1):
            if '.gc/runtime/resource-policy.json' in line:
                f.append('doc-policy-path: %s:%d names .gc/runtime/resource-policy.json; the file is .gc/runtime/fleet/resource-policy.json' % (p, i))
    rb = city / 'dispatch/resource-bin'
    shim = rb / 'heavy-shim'
    if not os.access(shim, os.X_OK):
        f.append('shim-missing: %s not executable' % shim)
    for n in SHIM_NAMES:
        p = rb / n
        if not p.is_symlink() or os.readlink(p) != 'heavy-shim':
            f.append('shim-link: %s is not a symlink to heavy-shim' % p)
    if not os.access(rb / 'systemd-run', os.X_OK):
        f.append('shim-missing: %s not executable' % (rb / 'systemd-run'))
    path = supervisor_path()
    first = path.split(':')[0] if path else ''
    if not first or os.path.realpath(first) != os.path.realpath(rb):
        f.append('supervisor-path: gascity-supervisor PATH starts %r, not %s' % (first or '(unset)', rb))
    active_permit_units = {u for u, s in units('fleet-permit-*').items() if s[1] == 'active'}
    granted = set()
    for r in permit_files(city):
        name = r['path'].name
        if r['err']:
            f.append('permit-orphan: %s %s; the guard skips it and never reaps it' % (r['path'], r['err']))
            continue
        unit = name.rsplit('.', 1)[0]
        if r['kind'] == 'json':
            granted.add(unit)
            if not r['alive'] and not r['populated'] and unit not in active_permit_units:
                f.append('permit-orphan: %s pid %s dead and %s inactive' % (r['path'], r['rec'].get('pid'), unit))
        elif not r['alive']:
            f.append('permit-orphan: %s (%s) pid %s dead' % (r['path'], r['kind'], r['rec'].get('pid')))
    for u in sorted(active_permit_units - granted):
        f.append('permit-unaccounted: %s is active with no permits/%s.json record' % (u, u))
    for u, (load, act, sub) in sorted({**units('fleet-permit-*'), **units('fleet-resource-*')}.items()):
        if act == 'failed':
            f.append('unit-failed: %s lingers failed (systemctl --user status %s)' % (u, u))
    recs = resource_records(city)
    stale = [p for p, rec, a, pop in recs if not a and not pop]
    if stale:
        f.append('resource-records-stale: %d of %d resources/*.json have a dead pid and an empty scope (oldest %s); active() re-reads them every admission poll'
                 % (len(stale), len(recs), min(stale, key=lambda p: p.stat().st_mtime).name))
    for line in f:
        print(line)
    if not f:
        print('resource-guard: clean')
    return 1 if f else 0


def state(city):
    _, _, pol, _ = load_policy(city)
    out = {'policy_source': pol['source'], 'mode': pol['mode'], 'baseline_gib': pol['baseline_gib'],
           'reserve_gib': pol['reserve_gib'], 'permit_gib': pol['permit_gib'],
           'permit_gib_max': pol.get('permit_gib_max'), 'permit_step_gib': pol.get('permit_step_gib'),
           'mem_available_gib': round(mem_available() / GIB, 2)}
    lanes = []
    for p, rec, a, pop in resource_records(city):
        if a or pop:
            lanes.append({'unit': rec.get('unit'), 'job': rec.get('job'), 'resource': rec.get('resource'),
                          'reserve_gib': round((rec.get('memory') or 0) / GIB, 2),
                          'max_gib': round((rec.get('memory_max') or 0) / GIB, 2),
                          'current_gib': round(mem_current(rec.get('cgroup')) / GIB, 2), 'guard_alive': a})
    out['lane_reservations'] = sorted(lanes, key=lambda r: r['unit'] or '')
    live_units = units('fleet-resource-*')
    out['fleet_resource_scopes_active'] = sorted(u for u, s in live_units.items() if u.endswith('.scope') and s[1] == 'active')
    granted, tickets, starve = [], [], []
    for r in permit_files(city):
        rec = r['rec']
        row = {'file': r['path'].name, 'class': rec.get('class'), 'reserve_gib': round((rec.get('reserve') or 0) / GIB, 2),
               'alive': r['alive'], 'err': r['err']}
        if r['kind'] == 'json':
            row.update(limit_gib=round((rec.get('limit') or 0) / GIB, 2), current_gib=round(mem_current(rec.get('cgroup')) / GIB, 2),
                       lane=rec.get('lane'), waited_s=rec.get('waited_s'), command=(rec.get('command') or '')[:120])
            granted.append(row)
        elif r['kind'] == 'ticket':
            row['since_utc'] = rec.get('since')
            tickets.append(row)
        else:
            starve.append(row)
    tickets.sort(key=lambda r: float(r.get('since_utc') or 0))
    live_tickets = sum(1 for t in tickets if t['alive'])
    pool = min(pol.get('permit_gib_max', pol['permit_gib']), pol['permit_gib'] + pol.get('permit_step_gib', 0) * live_tickets)
    out.update(permits_granted=granted, permit_tickets_oldest_first=tickets, permit_starving=starve,
               pool_now_gib=pool, held_gib=round(sum(g['reserve_gib'] for g in granted if g['alive']), 2),
               queued_gib=round(sum(t['reserve_gib'] for t in tickets if t['alive']), 2),
               permits_slice_current_gib=round(mem_current(unit_prop('fleet-permits.slice', 'ControlGroup')) / GIB, 2),
               supervisor_path_first=(supervisor_path().split(':') or [''])[0])
    print(json.dumps(out, indent=2))
    return 0


def classes(city):
    raw, _, pol, rp = load_policy(city)
    default = rp.DEFAULT['commands']
    docs_text = '\n'.join(p.read_text(errors='replace') for p in sorted((city / 'docs').rglob('*.md')))
    mem_text = '\n'.join(p.read_text(errors='replace') for p in sorted(MEMORY.glob('*.md'))) if MEMORY.is_dir() else ''
    rows = []
    for i, (name, c) in enumerate(pol['commands'].items()):
        d = default.get(name)
        drift = []
        if d is None:
            drift.append('not in code DEFAULT')
        else:
            for k in ('reserve_gib', 'limit_gib', 'cpus', 'workers'):
                dv = d.get(k, 2 if k == 'cpus' else 1)
                if float(dv) != float(c[k]):
                    drift.append('%s %s (code %s)' % (k, c[k], dv))
            if [p.pattern for p in c['match']] != list(d['match']):
                drift.append('match differs from code')
        word = re.compile(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])')
        rows.append({'order': i, 'class': name, 'reserve_gib': c['reserve_gib'], 'limit_gib': c['limit_gib'],
                     'cpus': c['cpus'], 'workers': c['workers'], 'permit': c['permit'],
                     'fits_pool': c['reserve_gib'] <= pol['permit_gib'],
                     'docs_mentions': len(word.findall(docs_text)), 'memory_mentions': len(word.findall(mem_text)),
                     'runtime_vs_code': drift or ['same']})
    order_rt = list(pol['commands'])
    order_code = [n for n in default if n in pol['commands']]
    print(json.dumps({'policy_source': pol['source'], 'mode': pol['mode'], 'classes': rows,
                      'code_only_classes': sorted(set(default) - set(pol['commands'])),
                      'order_matches_code': [n for n in order_rt if n in default] == order_code,
                      'lane_classes_resource_flag': lane_classes(city),
                      'permit_names_in_city': [{'where': w, 'class': n, 'known': n in pol['commands']}
                                               for w, n in scan_permit_names(city)]}, indent=2))
    return 0


def prove_permit(city):
    _, _, pol, _ = load_policy(city)
    cands = sorted((c['reserve_gib'], n) for n, c in pol['commands'].items() if c['permit'])
    if pol['mode'] != 'active' or not cands:
        print('verified-unreachable: policy mode %s, %d permit classes' % (pol['mode'], len(cands)))
        return 2
    cls = cands[0][1]
    before = sorted(p.name for p in (fleet(city) / 'permits').glob('*'))
    argv = [sys.executable, str(city / 'dispatch/resource_guard.py'), '--permit', cls, '--timeout', '60', '--', 'true']
    print('command:', ' '.join(argv), flush=True)
    r = subprocess.run(argv, capture_output=True, text=True, timeout=120, cwd=str(city))
    after = sorted(p.name for p in (fleet(city) / 'permits').glob('*'))
    print('exit:', r.returncode)
    print('stdout:', r.stdout.strip())
    print('stderr:', r.stderr.strip())
    print('permits_before:', before)
    print('permits_after:', after)
    print('left_behind_by_drive:', sorted(set(after) - set(before)))
    ok = r.returncode in (0, 75) and ('RESOURCE-PERMIT: class=' + cls in r.stderr or 'RESOURCE-BLOCKED: permit' in r.stderr)
    print('verdict:', 'permit path exercised (%s)' % ('granted' if r.returncode == 0 else 'queued then timed out') if ok else 'UNEXPECTED')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--city', help='city root (default $GC_CITY or ~/city)')
    ap.add_argument('cmd', choices=('doctor', 'state', 'classes', 'prove-permit'))
    a = ap.parse_args()
    city = city_path(a.city)
    return {'doctor': doctor, 'state': state, 'classes': classes, 'prove-permit': prove_permit}[a.cmd](city)


if __name__ == '__main__':
    sys.exit(main())
