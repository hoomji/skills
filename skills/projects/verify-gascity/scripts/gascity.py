#!/usr/bin/env python3
"""Harness for verifying the Gas City `gc` binary: an isolated throwaway city, plus a
read-only door onto the live city.

  gascity.py build [--ref REF] [--src DIR] [--out DIR]
        git-archive REF (default city-next) of ~/src/gascity into DIR/src (never touches the
        checkout) and build gc into DIR/bin/gc under resource_guard --permit go.
        DIR defaults to /tmp/vgc-build-<shortsha>. Prints the binary path.
  gascity.py launch [--bin PATH] [--run RUN]
        create /tmp/vgc-<RUN>/ (own GC_HOME, HOME, XDG_RUNTIME_DIR, TMUX_TMPDIR, free port,
        file beads, fake sessions, no dolt), gc init a city there, start a bare supervisor
        with setsid, register the city, wait for /health. --bin defaults to the live gc
        (`command -v gc`). Prints RUN; evidence goes to ~/.local/state/verify-gascity/RUN/.
  gascity.py doctor (RUN | live)
        read-only health lines; exit 1 on any finding, `doctor: clean` otherwise.
  gascity.py env RUN
        `export` lines for the isolated env: eval "$(gascity.py env RUN)" then plain gc.
  gascity.py gc RUN [--name LABEL] -- <gc args>
        run gc against the isolated city; transcript to EV/transcripts/<n>-<label>.txt.
  gascity.py live [--name LABEL] -- <gc args>
        run an ALLOWLISTED read-only gc command against ~/city; refuses anything else.
  gascity.py api (RUN | live) [--name LABEL] [--max-time S] <path>
        HTTP GET only, against the instance's supervisor (or the live :8372); `{city}` in
        <path> becomes the city name. Body to EV/api/<n>-<label>.<ext>, status and headers
        to EV/transcripts/<n>-api-<label>.txt.
  gascity.py cleanup RUN [--keep-instance]
        stop the supervisor this run started (by recorded pid/pgid, never by name), check
        the port is free and no process of the run survives, copy logs into EV, remove the
        instance dir. EV stays.

Nothing here writes to ~/city, ~/.gc, ~/src/gascity, the `city` tmux socket or a systemd
unit. A live-mode run's evidence goes to ~/.local/state/verify-gascity/live-<ts>/ unless
VGC_RUN names one."""
import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()
SRC = HOME / 'src' / 'gascity'
LIVE_CITY = HOME / 'city'
LIVE_API = 'http://127.0.0.1:8372'
STATE = HOME / '.local' / 'state' / 'verify-gascity'
GUARD = LIVE_CITY / 'dispatch' / 'resource_guard.py'
GO_BIN = HOME / '.local' / 'go' / 'bin'
INHERIT = ('PATH', 'TMPDIR', 'LANG', 'LC_ALL', 'USER', 'LOGNAME', 'SHELL', 'TERM')
SHIMS = ('systemctl', 'launchctl', 'loginctl', 'systemd-run')
GITCONFIG = '[user]\n\tname = gc-verify\n\temail = gc-verify@test.local\n[beads]\n\trole = maintainer\n[safe]\n\tdirectory = *\n'

# Live allowlist: (argv prefix, forbidden flags). Every entry is a pure read in city-next
# 1bd67220c. `mail read` marks read, `events rotate`/`reemit-execution` write, `session peek`
# reads the `city` tmux socket, `order check/run`, `formula cook` and `bd create/update/close`
# write: none are here.
LIVE_ALLOW = [
    (('version',), ()),
    (('status',), ()),
    (('cities',), ()),
    (('session', 'list'), ()),
    (('order', 'list'), ()),
    (('order', 'show'), ()),
    (('order', 'history'), ()),
    (('formula', 'list'), ()),
    (('formula', 'show'), ()),
    (('bd', 'list'), ()),
    (('bd', 'show'), ()),
    (('bd', 'ready'), ()),
    (('bd', 'count'), ()),
    (('mail', 'inbox'), ()),
    (('mail', 'count'), ()),
    (('events',), ('--follow', '--watch')),
    (('supervisor', 'status'), ()),
    (('dashboard', 'serve'), ()),
    (('dashboard',), ()),  # only with --no-open, checked below
    (('metrics', 'status'), ()),
]
# Live API paths that are GETs but costly or unbounded: /runs* starts a lazy cold replay of
# the whole events.jsonl inside the live supervisor (+1-3 GiB RSS for minutes on first use),
# /stream never ends, /orders/check runs order triggers.
LIVE_API_DENY = ('/runs', '/stream', '/orders/check')
LIVE_DENY_WORDS = {'rotate', 'reemit-execution', 'run', 'check', 'cook', 'create', 'update',
                   'close', 'delete', 'send', 'read', 'kill', 'nudge', 'peek', 'archive',
                   'mark-read', 'mark-unread', 'reload', 'start', 'stop', 'restart'}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def inst_dir(run):
    return Path('/tmp') / f'vgc-{run}'


def ev_dir(run):
    d = STATE / run
    (d / 'transcripts').mkdir(parents=True, exist_ok=True)
    (d / 'api').mkdir(parents=True, exist_ok=True)
    return d


def load_instance(run):
    p = inst_dir(run) / 'instance.json'
    if not p.exists():
        sys.exit(f'no instance {run}: {p} missing (launch first, or it was cleaned up)')
    return json.loads(p.read_text())


def isolated_env(inst):
    env = {k: os.environ[k] for k in INHERIT if k in os.environ}
    root = Path(inst['root'])
    env['PATH'] = f"{root / 'shims'}:{Path(inst['bin']).parent}:{env.get('PATH', '/usr/bin:/bin')}"
    env.update({
        'HOME': str(root / 'home'),
        'GC_HOME': str(root / 'gc-home'),
        'GC_SUPERVISOR_ISOLATED_HOME': '1',
        'XDG_RUNTIME_DIR': str(root / 'xdg'),
        'TMUX_TMPDIR': str(root / 'xdg' / 'tmux'),
        'DOLT_ROOT_PATH': str(root / 'gc-home'),
        'GIT_CONFIG_GLOBAL': str(root / 'gitconfig'),
        'GIT_CONFIG_NOSYSTEM': '1',
        'GC_DOLT': 'skip',
        'GC_BEADS': 'file',
        'GC_SESSION': 'fake',
        'BEADS_DOLT_SHARED_SERVER': 'false',
    })
    return env


def next_seq(ev):
    seqs = [int(f.name.split('-', 1)[0]) for d in ('transcripts', 'api') for f in (ev / d).iterdir()
            if f.name.split('-', 1)[0].isdigit()]
    return f'{max(seqs, default=0) + 1:02d}'


def record(ev, label, cmd, cwd, rc, out, err, extra=''):
    path = ev / 'transcripts' / f'{next_seq(ev)}-{label}.txt'
    path.write_text(f'# {now()} cwd={cwd}\n$ {shlex.join(cmd)}\n# exit {rc}\n{extra}'
                    f'--- stdout\n{out}--- stderr\n{err}')
    return path


def run_cmd(cmd, env=None, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or ''), f'timeout after {timeout}s\n'


def free_port():
    # Below the kernel's ephemeral range (32768+): gc warns on an ephemeral API port.
    for port in range(18300, 19000):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', port))
            except OSError:
                continue
            return port
    sys.exit('no free port in 18300-18999')


def http_get(url, max_time=10):
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=max_time) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:  # noqa: BLE001 — report any transport error as status 0
        return 0, {}, str(e).encode()


def port_owner(port):
    rc, out, _ = run_cmd(['ss', '-ltnpH', f'sport = :{port}'])
    return out.strip()


def run_pids(root):
    """PIDs whose cwd, exe or environment points into the instance root."""
    pids = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            env = (p / 'environ').read_bytes()
        except OSError:
            continue
        if f'GC_HOME={root}/gc-home'.encode() in env:
            pids.append(int(p.name))
    return sorted(pids)


# ---------------------------------------------------------------- build
def cmd_build(a):
    ref = a.ref
    sha = subprocess.check_output(['git', '-C', str(a.src), 'rev-parse', '--short', ref], text=True).strip()
    date = subprocess.check_output(['git', '-C', str(a.src), 'show', '-s', '--format=%cI', ref], text=True).strip()
    out = Path(a.out or f'/tmp/vgc-build-{sha}')
    src = out / 'src'
    binp = out / 'bin' / 'gc'
    if binp.exists():
        print(binp)
        return 0
    src.mkdir(parents=True, exist_ok=True)
    arch = subprocess.Popen(['git', '-C', str(a.src), 'archive', ref], stdout=subprocess.PIPE)
    subprocess.run(['tar', '-x', '-C', str(src)], stdin=arch.stdout, check=True)
    arch.wait()
    env = dict(os.environ, PATH=f'{GO_BIN}:{os.environ["PATH"]}', CGO_ENABLED='0')
    ld = f'-X main.version=1.5.1-next -X main.commit={sha}-verify -X main.date={date}'
    cmd = ['python3', str(GUARD), '--permit', 'go', '--timeout', '1800', '--',
           'go', 'build', '-buildvcs=false', '-ldflags', ld, '-o', str(binp), './cmd/gc']
    print('+', shlex.join(cmd), file=sys.stderr)
    r = subprocess.run(cmd, cwd=src, env=env)
    if r.returncode or not binp.exists():
        sys.exit(f'build failed (exit {r.returncode}); source left at {src}')
    print(binp)
    return 0


# ---------------------------------------------------------------- launch
def cmd_launch(a):
    run = a.run or now()
    root = inst_dir(run)
    if root.exists():
        sys.exit(f'{root} exists: pick another --run or clean up {run}')
    binp = Path(a.bin or shutil.which('gc') or '').resolve()
    if not binp.is_file():
        sys.exit('no gc binary: pass --bin or build first')
    for d in ('shims', 'home', 'gc-home', 'xdg/tmux'):
        (root / d).mkdir(parents=True, exist_ok=True)
    os.chmod(root / 'xdg', 0o700)
    os.chmod(root / 'xdg' / 'tmux', 0o700)
    for name in SHIMS:
        s = root / 'shims' / name
        s.write_text('#!/bin/sh\n# verify-gascity shim: refuse host service managers so gc bare-starts.\nexit 1\n')
        s.chmod(0o755)
    (root / 'gitconfig').write_text(GITCONFIG)
    # gc must be invoked as `gc` (GT_PROCESS_NAMES liveness); link it into the instance.
    (root / 'bin').mkdir()
    (root / 'bin' / 'gc').symlink_to(binp)
    port = free_port()
    (root / 'gc-home' / 'supervisor.toml').write_text(f'[supervisor]\nport = {port}\nbind = "127.0.0.1"\n')
    city = root / 'city'
    inst = {'run': run, 'root': str(root), 'bin': str(root / 'bin' / 'gc'), 'bin_target': str(binp),
            'city': str(city), 'city_name': f'vgc-{run}'.lower(), 'port': port,
            'api': f'http://127.0.0.1:{port}', 'created': now()}
    ev = ev_dir(run)
    env = isolated_env(inst)
    gc = inst['bin']

    rc, out, err = run_cmd([gc, 'version', '--long'], env=env)
    inst['version'] = out.strip()
    record(ev, 'version', [gc, 'version', '--long'], root, rc, out, err)

    init = [gc, 'init', '--no-start', '--skip-provider-readiness', '--template', 'minimal', '--providers', 'claude', '--default-provider', 'claude',
            '--name', inst['city_name'], str(city)]
    rc, out, err = run_cmd(init, env=env, cwd=root, timeout=300)
    record(ev, 'init', init, root, rc, out, err)
    if rc:
        (root / 'instance.json').write_text(json.dumps(inst, indent=1))
        sys.exit(f'gc init failed (exit {rc}); see {ev}/transcripts. Run cleanup {run}.')

    log = open(root / 'supervisor.out', 'ab')
    proc = subprocess.Popen([gc, 'supervisor', 'run'], env=env, cwd=root, stdout=log,
                            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    inst['supervisor_pid'] = proc.pid
    inst['supervisor_pgid'] = os.getpgid(proc.pid)
    (root / 'instance.json').write_text(json.dumps(inst, indent=1))
    deadline = time.time() + 60
    while time.time() < deadline:
        st, _, body = http_get(inst['api'] + '/health', 2)
        if st == 200:
            break
        if proc.poll() is not None:
            sys.exit(f'supervisor exited {proc.returncode}; see {root}/supervisor.out. Run cleanup {run}.')
        time.sleep(1)
    else:
        sys.exit(f'/health never answered on {port}; run cleanup {run}')

    reg = [gc, 'register', '--city', str(city), str(city)]
    rc, out, err = run_cmd(reg, env=env, cwd=city, timeout=180)
    record(ev, 'register', reg, city, rc, out, err)
    if rc:
        sys.exit(f'gc register failed (exit {rc}); see transcripts. Run cleanup {run}.')
    deadline = time.time() + 90
    while time.time() < deadline:
        st, _, body = http_get(f"{inst['api']}/v0/city/{inst['city_name']}/status", 5)
        if st == 200:
            break
        time.sleep(2)
    inst['ready'] = now()
    (root / 'instance.json').write_text(json.dumps(inst, indent=1))
    shutil.copy(root / 'instance.json', ev / 'instance.json')
    print(run)
    print(f"instance {root}  api {inst['api']}  city {inst['city_name']}  evidence {ev}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- doctor
def doctor_isolated(run):
    inst = load_instance(run)
    root = Path(inst['root'])
    f = []
    pid = inst.get('supervisor_pid')
    alive = pid and Path(f'/proc/{pid}').exists()
    if not alive:
        f.append(f'supervisor: pid {pid} not running')
    owner = port_owner(inst['port'])
    if f'pid={pid},' not in owner:
        f.append(f"port {inst['port']}: not owned by our supervisor pid {pid}: {owner or 'nothing listening'}")
    st, _, body = http_get(inst['api'] + '/health', 3)
    if st != 200:
        f.append(f'/health: {st} {body[:120]!r}')
    st, _, body = http_get(f"{inst['api']}/v0/city/{inst['city_name']}/status", 10)
    if st != 200:
        f.append(f"city status API: {st} {body[:160]!r}")
    env = isolated_env(inst)
    rc, out, err = run_cmd([inst['bin'], 'version', '--long'], env=env)
    if out.strip() != inst.get('version'):
        f.append(f"version drift: launched {inst.get('version')!r}, binary now says {out.strip()!r}")
    rc, out, err = run_cmd([inst['bin'], 'status', '--city', inst['city']], env=env, cwd=inst['city'], timeout=60)
    if rc:
        f.append(f'gc status: exit {rc}: {(err or out).strip()[:200]}')
    # Isolation: our supervisor must not have touched the live home or socket.
    if str(HOME / '.gc') in json.dumps(inst):
        f.append('instance names the live ~/.gc')
    for p in run_pids(root):
        try:
            exe = os.readlink(f'/proc/{p}/exe')
        except OSError:
            continue
        if 'tmux' in exe or 'dolt' in exe:
            f.append(f'unexpected child {p} {exe} (fake sessions and GC_DOLT=skip should spawn neither)')
    print(f"run {run}: version {inst.get('version')}; supervisor pid {pid}; api {inst['api']}; "
          f"city {inst['city_name']} at {inst['city']}; processes of this run: {run_pids(root)}")
    return f


def doctor_live():
    f = []
    rc, out, _ = run_cmd(['systemctl', '--user', 'is-active', 'gascity-supervisor.service'])
    if out.strip() != 'active':
        f.append(f'gascity-supervisor.service: {out.strip() or rc}')
    st, _, body = http_get(LIVE_API + '/health', 3)
    if st != 200:
        f.append(f'live /health: {st} {body[:120]!r}')
    gc = shutil.which('gc')
    rc, out, err = run_cmd([gc, 'version', '--long'])
    ver = out.strip()
    rc2, staged, _ = run_cmd(['git', '-C', str(SRC), 'rev-parse', '--short', 'city-next'])
    if staged.strip() and staged.strip() not in ver:
        f.append(f'live gc {ver!r} is not city-next {staged.strip()} (staged binary trails or leads the fork)')
    rc, out, err = run_cmd([gc, 'status', '--city', str(LIVE_CITY)], cwd=LIVE_CITY, timeout=60)
    if rc:
        f.append(f'gc status (live): exit {rc}: {(err or out).strip()[:200]}')
    print(f'live: gc {ver} at {os.path.realpath(gc)}; city-next {staged.strip()}; api {LIVE_API}')
    return f


def cmd_doctor(a):
    f = doctor_live() if a.live else doctor_isolated(a.run)
    for line in f:
        print(line)
    if not f:
        print('doctor: clean')
    return 1 if f else 0


# ---------------------------------------------------------------- env / gc / live / api
def cmd_env(a):
    inst = load_instance(a.run)
    for k, v in isolated_env(inst).items():
        print(f'export {k}={shlex.quote(v)}')
    print(f"export VGC_RUN={shlex.quote(a.run)} VGC_CITY={shlex.quote(inst['city'])} "
          f"VGC_API={shlex.quote(inst['api'])}")
    print(f"cd {shlex.quote(inst['city'])}")
    return 0


def cmd_gc(a):
    inst = load_instance(a.run)
    args = a.args[1:] if a.args[:1] == ['--'] else a.args
    cmd = [inst['bin']] + args
    rc, out, err = run_cmd(cmd, env=isolated_env(inst), cwd=inst['city'], timeout=a.timeout)
    p = record(ev_dir(a.run), a.name or (args[0] if args else 'gc'), cmd, inst['city'], rc, out, err)
    sys.stdout.write(out)
    sys.stderr.write(err)
    print(f'[transcript {p}]', file=sys.stderr)
    return rc


def live_allowed(args):
    words = [x for x in args if not x.startswith('-')]
    if any(w in LIVE_DENY_WORDS for w in words[:2]):
        return False, f'{words[:2]} is denied (writes, or reads the city tmux socket)'
    if args[:1] == ['dashboard'] and args[1:2] != ['serve'] and '--no-open' not in args:
        return False, 'gc dashboard without --no-open opens a browser'
    for prefix, banned in LIVE_ALLOW:
        if tuple(words[:len(prefix)]) == prefix:
            bad = [b for b in banned if b in args]
            if bad:
                return False, f'flag {bad} not allowed against the live city'
            return True, ''
    return False, 'not on the live read allowlist (see LIVE_ALLOW in gascity.py)'


def cmd_live(a):
    args = a.args[1:] if a.args[:1] == ['--'] else a.args
    ok, why = live_allowed(args)
    if not ok:
        print(f'refused: gc {shlex.join(args)}: {why}', file=sys.stderr)
        return 2
    run = os.environ.get('VGC_RUN') or f'live-{now()}'
    gc = shutil.which('gc')
    cmd = [gc, '--city', str(LIVE_CITY)] + args
    env = {k: v for k, v in os.environ.items() if not k.startswith('GC_')}
    # The live supervisor's control socket is $XDG_RUNTIME_DIR/gc/supervisor.sock; agent
    # shells often lack XDG_RUNTIME_DIR, and then gc falls back to ~/.gc and cannot find it.
    env.setdefault('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')
    rc, out, err = run_cmd(cmd, env=env, cwd=LIVE_CITY, timeout=a.timeout)
    p = record(ev_dir(run), a.name or 'live-' + (args[0] if args else 'gc'), cmd, LIVE_CITY, rc, out, err)
    sys.stdout.write(out)
    sys.stderr.write(err)
    print(f'[transcript {p}]', file=sys.stderr)
    return rc


def cmd_api(a):
    if a.live:
        base, run = LIVE_API, os.environ.get('VGC_RUN') or f'live-{now()}'
    else:
        inst = load_instance(a.run)
        base, run = inst['api'], a.run
        a.path = a.path.replace('{city}', inst['city_name'])
    if a.live:
        a.path = a.path.replace('{city}', 'city')
        bad = [d for d in LIVE_API_DENY if d in a.path.split('?')[0]]
        if bad:
            print(f'refused: GET {a.path} on the live supervisor: {bad[0]} is denied (see LIVE_API_DENY)',
                  file=sys.stderr)
            return 2
    url = base + (a.path if a.path.startswith('/') else '/' + a.path)
    st, headers, body = http_get(url, a.max_time)
    ev = ev_dir(run)
    ctype = headers.get('Content-Type', '')
    ext = 'json' if 'json' in ctype else 'html' if 'html' in ctype else 'txt'
    label = a.name or a.path.strip('/').replace('/', '_')[:60] or 'root'
    seq = next_seq(ev)
    (ev / 'api' / f'{seq}-{label}.{ext}').write_bytes(body)
    hdr = ''.join(f'{k}: {v}\n' for k, v in headers.items())
    (ev / 'transcripts' / f'{seq}-api-{label}.txt').write_text(
        f'# {now()}\nGET {url}\n# status {st}\n{hdr}--- body in api/{seq}-{label}.{ext} ({len(body)} bytes)\n')
    if 'json' in ctype:
        try:
            print(json.dumps(json.loads(body), indent=1)[:a.print_limit])
        except ValueError:
            print(body[:a.print_limit].decode(errors='replace'))
    else:
        print(body[:a.print_limit].decode(errors='replace'))
    print(f'[GET {url} -> {st}; body api/{seq}-{label}.{ext} in {ev}]', file=sys.stderr)
    return 0 if 200 <= st < 300 else 1


# ---------------------------------------------------------------- cleanup
def cmd_cleanup(a):
    root = inst_dir(a.run)
    ev = ev_dir(a.run)
    if not root.exists():
        print(f'{root} already gone; evidence at {ev}')
        return 0
    inst = json.loads((root / 'instance.json').read_text()) if (root / 'instance.json').exists() else {}
    pid, pgid = inst.get('supervisor_pid'), inst.get('supervisor_pgid')
    # Logs into the evidence dir before anything is torn down.
    for src, dst in ((root / 'supervisor.out', 'supervisor.out'),
                     (root / 'gc-home' / 'supervisor.log', 'supervisor.log'),
                     (root / 'gc-home' / 'events.jsonl', 'supervisor-events.jsonl'),
                     (root / 'city' / '.gc' / 'events.jsonl', 'city-events.jsonl'),
                     (root / 'city' / 'city.toml', 'city.toml'),
                     (root / 'instance.json', 'instance.json')):
        if src.exists():
            shutil.copy(src, ev / dst)
    # Signals only, to the pgid and pids recorded for this run: `gc supervisor stop` is not used
    # because a mis-set GC_HOME would aim it at the live supervisor.
    for sig in (signal.SIGTERM, signal.SIGKILL):
        left = run_pids(root)
        if pgid:
            try:
                os.killpg(pgid, sig)
            except ProcessLookupError:
                pass
        for p in left:
            try:
                os.kill(p, sig)
            except ProcessLookupError:
                pass
        time.sleep(2)
    left = run_pids(root)
    port = inst.get('port')
    held = port_owner(port) if port else ''
    lines = [f'cleanup {a.run}: {now()}', f'survivors: {left or "none"}',
             f"port {port}: {held or 'free'}"]
    if not a.keep_instance and not left:
        shutil.rmtree(root, ignore_errors=True)
        lines.append(f'removed {root}')
    else:
        lines.append(f'kept {root}')
    (ev / 'cleanup.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print(f'evidence: {ev}')
    return 1 if left or held else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--ref', default='city-next')
    b.add_argument('--src', type=Path, default=SRC)
    b.add_argument('--out')
    l = sub.add_parser('launch')
    l.add_argument('--bin')
    l.add_argument('--run')
    d = sub.add_parser('doctor')
    d.add_argument('run', help='RUN id, or `live` for the live city')
    e = sub.add_parser('env')
    e.add_argument('run')
    c = sub.add_parser('gc')
    c.add_argument('run')
    c.add_argument('--name')
    c.add_argument('--timeout', type=int, default=120)
    c.add_argument('args', nargs=argparse.REMAINDER)
    v = sub.add_parser('live')
    v.add_argument('--name')
    v.add_argument('--timeout', type=int, default=120)
    v.add_argument('args', nargs=argparse.REMAINDER)
    p = sub.add_parser('api')
    p.add_argument('run', help='RUN id, or `live` for the live supervisor on :8372')
    p.add_argument('--name')
    p.add_argument('--max-time', type=float, default=10)
    p.add_argument('--print-limit', type=int, default=4000)
    p.add_argument('path')
    k = sub.add_parser('cleanup')
    k.add_argument('run')
    k.add_argument('--keep-instance', action='store_true')
    a = ap.parse_args()
    if a.cmd in ('gc', 'live'):
        # REMAINDER swallows options written after RUN; take ours back up to the `--`.
        rest = a.args
        while rest and rest[0] in ('--name', '--timeout') and len(rest) > 1:
            setattr(a, rest[0][2:], rest[1] if rest[0] == '--name' else int(rest[1]))
            rest = rest[2:]
        a.args = rest
    if a.cmd in ('api', 'doctor'):
        a.live = a.run == 'live'
    return {'build': cmd_build, 'launch': cmd_launch, 'doctor': cmd_doctor, 'env': cmd_env,
            'gc': cmd_gc, 'live': cmd_live, 'api': cmd_api, 'cleanup': cmd_cleanup}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
