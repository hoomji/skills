#!/usr/bin/env python3
"""Read-only harness for how city code reaches the remote hosts (dell, gtx, hailey).

  host_release.py doctor            one line per finding, exit 1 on any; else `host-release: clean`
  host_release.py skew [--host H] [--json] [--list N]
                                    per host: reachable, the release it runs (.gc/runtime/fleet/release.json)
                                    vs Ryzen HEAD and the city mirror, released files behind HEAD,
                                    files edited on the host after install, and off-release copies of
                                    tracked dispatch/ formulas/ orders/ files that differ from HEAD
  host_release.py baseline          host-baseline.sh --check's inventory, shim and lane-tool checks
                                    WITHOUT its bench (the bench writes 512 MiB and loads every thread)
  host_release.py config [--host H] each host's own city.toml: the stage-release overlay holds (dsh pool
                                    commands are its dsh-scoped.sh, every base pool has the resource
                                    schema) and its rig is the one fleet.py HOSTS names

Hosts and their city paths come from HOSTS in dispatch/fleet.py; the released file list from FILES
in dispatch/deploy-resource-routing.py. Remote commands are one `ssh -o BatchMode=yes -o
ConnectTimeout=5 <host> python3 -` per host running a fixed reader (stat, sha256, readlink,
tomllib); nothing is written anywhere. A host that does not answer is `verified-unreachable`, not a
finding. --city defaults to $GC_CITY or ~/city."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FEEDBACK = 'dispatch/ledgers/review-feedback.jsonl'  # merged on install, diverges by design
MIRROR = Path.home() / 'src' / 'city.git'
SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5']

REMOTE = r'''
import hashlib, json, os, sys, tomllib
from pathlib import Path
req = json.loads(REQ)
city = Path(req['city'])
out = {'files': {}, 'release': None, 'toml': None}
def h(p):
    if p.is_symlink(): return 'L:' + os.readlink(p)
    if p.is_file(): return hashlib.sha256(p.read_bytes()).hexdigest()
    return None
for name in req['paths']:
    out['files'][name] = h(city / name)
try: out['release'] = json.loads((city / '.gc/runtime/fleet/release.json').read_text())
except Exception as e: out['release_error'] = repr(e)
try:
    raw = (city / 'city.toml').read_bytes(); out['toml_sha'] = hashlib.sha256(raw).hexdigest()
    t = tomllib.loads(raw.decode())
    out['toml'] = {'rigs': [r.get('name') for r in t.get('rigs', [])],
                   'providers': {k: {'command': v.get('command'), 'base': v.get('base'),
                                     'resource': any(x.get('key') == 'resource' for x in v.get('options_schema', []))}
                                 for k, v in t.get('providers', {}).items() if k.startswith('dsh-')}}
except Exception as e: out['toml_error'] = repr(e)
arch = city / 'archive'
out['archives'] = sum(1 for p in arch.glob('resource-routing-*')) if arch.is_dir() else 0
out['is_git'] = (city / '.git').exists()
print(json.dumps(out))
'''


def sh(*cmd, cwd=None, inp=None, timeout=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, '', 'timeout'


def city_meta(city):
    src = (city / 'dispatch/deploy-resource-routing.py').read_text()
    ns = {}
    for line in src.splitlines():
        if line.startswith(('FILES=', 'LINKS=')):
            exec(line, ns)
    hosts = {}
    for m in re.finditer(r'^\s+"(\w+)": \{"city": "([^"]+)", "rig": "([^"]+)"', (city / 'dispatch/fleet.py').read_text(), re.M):
        hosts[m[1]] = {'city': m[2], 'rig': m[3]}
    sr = (city / 'dispatch/stage-release.sh').read_text()
    m = re.search(r'hosts=\(([a-z ]+)\)\s*$', sr, re.M)
    return ns['FILES'], ns.get('LINKS', {}), hosts, (m[1].split() if m else [])


def head_hashes(city, paths):
    """sha256 of each path's blob at HEAD, symlinks as L:<target>; None when absent at HEAD."""
    rc, ls, _ = sh('git', '-C', str(city), 'ls-tree', '-r', 'HEAD', '--', *paths)
    modes = {}
    for line in ls.splitlines():
        meta, name = line.split('\t', 1)
        mode, _, sha = meta.split()
        modes[name] = (mode, sha)
    out = {p: None for p in paths}
    want = [p for p in paths if p in modes]
    if not want:
        return out
    r = subprocess.run(['git', '-C', str(city), 'cat-file', '--batch'], input=''.join(modes[p][1] + '\n' for p in want).encode(),
                       capture_output=True)
    buf, i = r.stdout, 0
    for p in want:
        nl = buf.index(b'\n', i); size = int(buf[i:nl].split()[2]); data = buf[nl + 1:nl + 1 + size]; i = nl + 2 + size
        out[p] = ('L:' + data.decode()) if modes[p][0] == '120000' else hashlib.sha256(data).hexdigest()
    return out


def git(city, *a):
    rc, out, _ = sh('git', '-C', str(city), *a)
    return out.strip() if rc == 0 else None


def probe(host, info, paths):
    script = 'REQ = %r\n' % json.dumps({'city': info['city'], 'paths': paths}) + REMOTE
    rc, out, err = sh(*SSH, host, 'python3', '-', inp=script, timeout=45)
    if rc != 0 or not out.strip():
        return None, (err.strip().splitlines() or ['exit %d' % rc])[-1]
    return json.loads(out), None


def tracked(city):
    rc, out, _ = sh('git', '-C', str(city), 'ls-files', 'dispatch', 'formulas', 'orders')
    return out.split()


def analyse(city, host, info, files, links, head, data):
    """Return dict of facts for one reachable host."""
    rel = data.get('release') or {}
    release = rel.get('release')
    manifest = rel.get('files', {})
    remote = data['files']
    behind, edited, missing = [], [], []
    for name in files:
        have = remote.get(name)
        if head.get(name) is None:
            continue  # not committed yet: doctor reports it as a FILES entry missing from HEAD
        if have is None:
            missing.append(name); continue
        if name in links:
            if have != 'L:' + links[name]: edited.append(name)
            want_head = head.get(name)
            if want_head != have: behind.append(name)
            continue
        if name == FEEDBACK:
            continue
        if manifest.get(name) and have != manifest[name]:
            edited.append(name)
        if head.get(name) != have:
            behind.append(name)
    off = {'same': 0, 'differ': [], 'absent': 0}
    for name, want in head.items():
        if name in files: continue
        have = remote.get(name)
        if have is None: off['absent'] += 1
        elif have == want: off['same'] += 1
        else: off['differ'].append(name)
    ahead_of = None
    if release:
        rc, _, _ = sh('git', '-C', str(city), 'merge-base', '--is-ancestor', release, 'HEAD')
        ahead_of = rc == 0
    since = int(git(city, 'rev-list', '--count', release + '..HEAD')) if release and ahead_of else None
    changed_since = []
    if release and ahead_of:
        changed_since = (git(city, 'diff', '--name-only', release, 'HEAD', '--', *files) or '').split()
    return {'host': host, 'reachable': True, 'release': release, 'installed': rel.get('installed'),
            'release_error': data.get('release_error'), 'release_in_head_history': ahead_of,
            'commits_behind_head': since,
            'released_files_changed_since_release': changed_since,
            'released_files_behind_head': behind, 'edited_after_install': edited, 'missing': missing,
            'off_release': off, 'is_git': data.get('is_git'), 'archives': data.get('archives'),
            'toml': data.get('toml'), 'toml_error': data.get('toml_error'), 'toml_sha': data.get('toml_sha')}


def collect(city, only=None):
    files, links, hosts, stage_default = city_meta(city)
    paths = sorted(set(files) | set(tracked(city)))
    head = head_hashes(city, paths)
    res = []
    for host, info in hosts.items():
        if host == 'ryzen' or (only and host != only):
            continue
        data, err = probe(host, info, paths)
        if data is None:
            res.append({'host': host, 'reachable': False, 'status': 'verified-unreachable', 'error': err})
        else:
            res.append(analyse(city, host, info, files, links, head, data))
    return files, links, hosts, stage_default, res


def ts(epoch):
    import datetime as dt
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if epoch else '?'


def cmd_skew(a):
    city = a.city
    files, links, hosts, _, res = collect(city, a.host)
    head = git(city, 'rev-parse', 'HEAD')
    mirror = git(MIRROR, 'rev-parse', 'main') if MIRROR.exists() else None
    mirror_behind = git(city, 'rev-list', '--count', mirror + '..HEAD') if mirror and git(city, 'cat-file', '-t', mirror) else None
    dirty = (git(city, 'diff', '--name-only', 'HEAD', '--', *files) or '').split()
    if a.json:
        print(json.dumps({'ryzen_head': head, 'mirror_main': mirror, 'mirror_commits_behind_head': mirror_behind,
                          'ryzen_uncommitted_released_files': dirty, 'hosts': res}, indent=1))
        return 0
    print('ryzen HEAD %s  (%s)' % (head[:9], git(city, 'log', '-1', '--format=%cI %s', 'HEAD')))
    print('city mirror %s main %s  (%s commits behind HEAD)' % (MIRROR, (mirror or '?')[:9], mirror_behind))
    print('ryzen uncommitted edits to released files (live on Ryzen only): %s' % (', '.join(dirty) or 'none'))
    try:
        own = json.loads((city / '.gc/runtime/fleet/release.json').read_text())
        print('ryzen .gc/runtime/fleet/release.json %s installed %s (Ryzen runs its checkout; fleet-session.py stamps this on Ryzen lane records)' % (
            own.get('release', '?')[:9], ts(own.get('installed'))))
    except (OSError, ValueError):
        print('ryzen .gc/runtime/fleet/release.json absent')
    n = a.list
    for r in res:
        if not r['reachable']:
            print('%-7s verified-unreachable (%s)' % (r['host'], r['error'])); continue
        print('%-7s release %s installed %s; %s commits behind HEAD; release in HEAD history: %s' % (
            r['host'], (r['release'] or 'NONE')[:9], ts(r['installed']), r['commits_behind_head'], r['release_in_head_history']))
        print('        released files behind HEAD (%d): %s' % (len(r['released_files_behind_head']), ', '.join(r['released_files_behind_head'][:n]) or '-'))
        print('        edited on host after install (%d): %s' % (len(r['edited_after_install']), ', '.join(r['edited_after_install'][:n]) or '-'))
        print('        released files missing (%d): %s' % (len(r['missing']), ', '.join(r['missing'][:n]) or '-'))
        off = r['off_release']
        print('        off-release dispatch/formulas/orders copies: %d same as HEAD, %d differ, %d absent%s' % (
            off['same'], len(off['differ']), off['absent'], (' e.g. ' + ', '.join(off['differ'][:n])) if off['differ'] else ''))
        print('        git checkout: %s; release archives kept: %s' % (r['is_git'], r['archives']))
    return 0


def doctor_findings(city):
    out, notes = [], []
    files, links, hosts, stage_default, res = collect(city)
    head = git(city, 'rev-parse', 'HEAD')
    for name in files:
        if git(city, 'cat-file', '-e', 'HEAD:' + name) is None:
            out.append('ryzen: FILES entry %s is not in HEAD; stage-release.sh would fail at git show' % name)
    for name in (git(city, 'diff', '--name-only', 'HEAD', '--', *files) or '').split():
        out.append('ryzen: released file %s has an uncommitted edit; live on Ryzen only, no release can carry it' % name)
    out.extend(partial_findings(city, files))
    remotes = sorted(h for h in hosts if h != 'ryzen')
    if sorted(stage_default) != remotes:
        out.append('stage-release.sh default hosts %s != fleet.py HOSTS remotes %s' % (stage_default, remotes))
    for h in remotes:
        for p in ('dispatch/%s.sh' % h, 'dispatch/%s-sync.sh' % h, 'orders/%s-sync.toml' % h):
            if not (city / p).exists():
                out.append('%s: helper %s missing' % (h, p))
    for doc in sorted((city / 'docs').rglob('*.md')):
        for i, line in enumerate(doc.read_text(errors='replace').splitlines(), 1):
            if re.search(r'stage-release\.sh (?:<host>|dell\b|gtx\b|hailey\b)', line):
                out.append('%s:%d: stage-release.sh takes [<commit>] first; a host there fails git rev-parse' % (doc.relative_to(city), i))
    releases = set()
    for r in res:
        h = r['host']
        if not r['reachable']:
            notes.append('%s verified-unreachable' % h); continue
        if not r['release']:
            out.append('%s: no .gc/runtime/fleet/release.json (%s)' % (h, r.get('release_error'))); continue
        releases.add(r['release'])
        if r['release_in_head_history'] is False:
            out.append('%s: release %s is not in Ryzen HEAD history' % (h, r['release'][:9]))
        if r['released_files_behind_head']:
            out.append('%s: release %s (installed %s, %s commits behind HEAD %s) lacks HEAD for %d released file(s): %s' % (
                h, r['release'][:9], ts(r['installed']), r['commits_behind_head'], head[:9],
                len(r['released_files_behind_head']), ', '.join(r['released_files_behind_head'])))
        if r['edited_after_install']:
            out.append('%s: %d released file(s) differ from the installed manifest (hand edit): %s' % (
                h, len(r['edited_after_install']), ', '.join(r['edited_after_install'])))
        if r['missing']:
            out.append('%s: released file(s) missing: %s' % (h, ', '.join(r['missing'])))
        if r['is_git']:
            out.append('%s: ~/city is a git checkout; remote hosts are meant to run a release only' % h)
        t = r.get('toml')
        if r.get('toml_error'):
            out.append('%s: city.toml does not parse: %s' % (h, r['toml_error']))
        elif t:
            out.extend(config_findings(h, hosts[h], t))
    if len(releases) > 1:
        out.append('hosts run different releases: %s' % ', '.join(sorted(x[:9] for x in releases)))
    return out, notes


USE_RE = re.compile(r'\{\{-?\s*template\s+"([^"]+)"')
DEF_RE = re.compile(r'\{\{-?\s*define\s+"([^"]+)"')


def partial_findings(city, files):
    """A released prompt that calls {{ template "x" }} defined only in an unreleased city file
    renders on Ryzen and breaks on every remote host after the next stage-release."""
    defined_in = {}
    frags = city / 'template-fragments'
    for p in [*(city / 'prompts').rglob('*.md'), *(frags.rglob('*') if frags.is_dir() else [])]:
        if p.is_file():
            for name in DEF_RE.findall(p.read_text(errors='replace')):
                defined_in.setdefault(name, set()).add(str(p.relative_to(city)))
    out = []
    for f in files:
        p = city / f
        if not f.startswith('prompts/') or not p.is_file():
            continue
        for name in sorted(set(USE_RE.findall(p.read_text(errors='replace')))):
            homes = defined_in.get(name)
            if homes and not homes & set(files):
                out.append('ryzen: released %s uses template "%s" defined only in unreleased %s' % (f, name, ', '.join(sorted(homes))))
    return out


def config_findings(h, info, t):
    out = []
    if info['rig'] not in t['rigs']:
        out.append('%s: city.toml rigs %s lack fleet.py rig %s' % (h, t['rigs'], info['rig']))
    want = info['city'] + '/dispatch/dsh-scoped.sh'
    for name, p in sorted(t['providers'].items()):
        if p['command'] is not None and p['command'] != want:
            out.append('%s: [providers.%s] command %s, overlay wants %s' % (h, name, p['command'], want))
        if not p['base'] and not p['resource']:
            out.append('%s: [providers.%s] has no resource options_schema' % (h, name))
    return out


def cmd_doctor(a):
    out, notes = doctor_findings(a.city)
    for line in out:
        print(line)
    if out:
        return 1
    print('host-release: clean' + (' (%s)' % '; '.join(notes) if notes else ''))
    return 0


def cmd_config(a):
    _, _, hosts, _, res = collect(a.city, a.host)
    rc = 0
    for r in res:
        h = r['host']
        if not r['reachable']:
            print('%-7s verified-unreachable (%s)' % (h, r['error'])); continue
        t = r.get('toml')
        if not t:
            print('%-7s city.toml unreadable: %s' % (h, r.get('toml_error'))); rc = 1; continue
        f = config_findings(h, hosts[h], t)
        print('%-7s city.toml sha256 %s; rigs %s; %d dsh pools; overlay %s' % (
            h, r['toml_sha'][:12], ','.join(t['rigs']), len(t['providers']), 'holds' if not f else 'BROKEN'))
        for line in f:
            print('        ' + line)
        rc |= bool(f)
    return rc


INV_KEYS = ('cpu', 'threads', 'max_mhz', 'ram_gib', 'swap_gib', 'repo_disk', 'gpu')
INV_PROBE = r'''
lscpu | awk -F: '/^Model name/{gsub(/^ +/,"",$2); print "cpu="$2} /^CPU max MHz/{gsub(/ /,"",$2); printf "max_mhz=%d\n",$2}'
echo "threads=$(nproc)"
free -m | awk '/^Mem:/{printf "ram_gib=%.0f\n",$2/1024} /^Swap:/{printf "swap_gib=%.0f\n",$2/1024}'
repo=$(ls -d "$HOME/projects/Gateway-LLM" 2>/dev/null)
dev=$(df --output=source "${repo:-/}" | tail -1); base=$(lsblk -no pkname "$dev" 2>/dev/null)
echo "repo_disk=$(lsblk -dno MODEL "/dev/${base:-x}" 2>/dev/null | sed 's/ *$//') ($(lsblk -dno SIZE "/dev/${base:-x}" 2>/dev/null | tr -d ' '))"
echo "gpu=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"
sup=$(systemctl --user show -p MainPID --value gascity-supervisor.service 2>/dev/null)
case "$(tr '\0' '\n' < "/proc/${sup:-0}/environ" 2>/dev/null | grep -m1 '^PATH=')" in
  PATH=*/city/dispatch/resource-bin:*) echo "shim_path=ok" ;;
  PATH=*) echo "shim_path=missing" ;;
esac
missing=""; [ -x "$HOME/.local/bin/gitleaks" ] || command -v gitleaks >/dev/null || missing="$missing gitleaks"
[ -f "$HOME/.claude/skills/auditing-tests/SKILL.md" ] || [ -f "$HOME/.codex/skills/auditing-tests/SKILL.md" ] || missing="$missing auditing-tests"
echo "lane_tools=${missing:-ok}"
'''


def cmd_baseline(a):
    city = a.city
    _, _, hosts, _ = city_meta(city)
    ref = json.loads((city / 'docs/host-baseline.json').read_text())
    print('docs/host-baseline.json measured %s at city %s' % (ref.get('measured_at'), ref.get('city_commit')))
    rc = 0
    for h in hosts:
        cmd = ['bash', '-s'] if h == 'ryzen' else [*SSH, h, 'bash', '-s']
        code, out, err = sh(*cmd, inp=INV_PROBE, timeout=45)
        got = dict(l.split('=', 1) for l in out.splitlines() if '=' in l)
        if not got:
            print('%-7s verified-unreachable (%s)' % (h, (err.strip().splitlines() or ['exit %d' % code])[-1])); continue
        want = ref.get('hosts', {}).get(h)
        lines = []
        if want is None:
            lines.append('NEW     not in docs/host-baseline.json')
        else:
            for k in INV_KEYS:
                if not got.get(k):
                    lines.append('UNREAD  %s (file: %s)' % (k, want.get(k)))
                elif str(want.get(k)) != got[k]:
                    lines.append("CHANGED %s: file '%s', now '%s'" % (k, want.get(k), got[k]))
        if got.get('shim_path') != 'ok':
            lines.append('SHIM    supervisor PATH lacks dispatch/resource-bin first (%s)' % got.get('shim_path', 'unread'))
        if got.get('lane_tools') != 'ok':
            lines.append('TOOLS   lanes lack:%s' % got.get('lane_tools', ' unread'))
        print('%-7s %s' % (h, 'matches' if not lines else 'differs'))
        for l in lines:
            print('        ' + l)
        rc |= bool(lines)
    return rc


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--city', type=Path, default=Path(os.environ.get('GC_CITY') or Path.home() / 'city'))
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('doctor')
    s = sub.add_parser('skew'); s.add_argument('--host'); s.add_argument('--json', action='store_true'); s.add_argument('--list', type=int, default=12)
    sub.add_parser('baseline')
    c = sub.add_parser('config'); c.add_argument('--host')
    a = p.parse_args()
    a.city = a.city.expanduser().resolve()
    return {'doctor': cmd_doctor, 'skew': cmd_skew, 'baseline': cmd_baseline, 'config': cmd_config}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
