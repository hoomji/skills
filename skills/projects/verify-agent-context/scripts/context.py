#!/usr/bin/env python3
"""Read-only harness for a Gas City's agent context: prompts, seat memory, mayor memory.

  context.py doctor                  every check below, one line each; exit 1 on any finding
  context.py render <agent> <out>    write what <agent> loads on wake to <out>/: <agent>.prompt.md
                                     (gc prime --strict), <agent>.memory.md (its memory index) and,
                                     for a seat, <agent>.wake.md (agent.toml nudge + pass formula);
                                     the gc prime budget line goes to stderr
  context.py refs [--also DIR] <file>...
                                     every backticked path in <file>: `ok` or `MISS`; `<x>`
                                     placeholders match by glob; --also adds a root (a product repo)
  context.py memory                  mayor-memory index, [[link]], See/Related name and frontmatter checks
  context.py seat-memory <seat>      that seat's lines from seat_memory_sync.py check; exit 1 on any
  context.py last-pass <seat>        the seat's newest closed pass bead, and whether its prompt,
                                     nudge or formula changed after it closed (prompt_newer)
  context.py primed <agent>          the agent's session state and whether its template changed
                                     since it last primed

Nothing here writes to the city, its store or its memory. --city defaults to $GC_CITY or ~/city."""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

AGENTS = ('mayor', 'ci-controller', 'fleet-watcher', 'receipt-grader', 'backlog-curator')
SEATS = AGENTS[1:]
TICK_RE = re.compile(r'`([^`\n]+)`')
ROOTED = r'(?:agents|dispatch|docs|orders|formulas|hooks|prompts|archive|scripts|lib|\.gc|\.claude-memory|\.claude)/'
PATH_RE = re.compile(r'^(?:\./)?(' + ROOTED + r'[\w./<>*-]*|[\w.<>-]+\.(?:py|sh|toml|md|json|jsonl|tsv|txt|mjs|ts))$')
PLACEHOLDER_RE = re.compile(r'<[^>]*>')
FM_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)
# "See x-y-z" / "Related: x-y-z, [[a]]" in a memory body: plain names that must still be memories.
SEE_RE = re.compile(r'(?:\bSee|\bsee|Related:)\s+((?:\[\[[^\]]+\]\]|[a-z0-9]+(?:-[a-z0-9]+)+)(?:\s*(?:,|and)\s*(?:\[\[[^\]]+\]\]|[a-z0-9]+(?:-[a-z0-9]+)+))*)')
SLUG_RE = re.compile(r'(?<![\w-])([a-z0-9]+(?:-[a-z0-9]+){2,})(?![\w-])')
SKILL_DIRS = (Path.home() / '.claude' / 'skills',)
# Where a bare file name (`fleet.py`, `seat-check.sh`, `pending.txt`) is looked up, and the gc
# docs corpus that prompts cite as `gc-docs docs/...`.
BARE_DIRS = ('', 'dispatch', 'orders/scripts', 'docs')
BARE_GLOBS = ('agents/*/{}', 'agents/*/memory/{}', '.gc/runtime/fleet/{}', '.gc/runtime/fleet/seats/*/{}')
GC_DOCS = Path.home() / '.cache' / 'gascity-docs'


def sh(*cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def memory_dir(city):
    return (city / '.claude-memory').resolve()


def exists(root, token):
    pattern = PLACEHOLDER_RE.sub('*', token)
    if '*' in pattern:
        return bool(glob.glob(str(root / pattern)))
    return (root / token).exists()


def refs(city, path, also=()):
    """(ref, exists) for each backticked token in path that names a file or directory."""
    out, seen = [], set()
    for span in TICK_RE.findall(Path(path).read_text()):
        words = span.split()
        if not words:
            continue
        token = words[1] if words[0] in ('python3', 'bash', 'gc-docs') and len(words) > 1 else words[0]
        token = token.rstrip('.,;:')
        if any(c in token for c in '$~{}|') or token in seen or not PATH_RE.match(token):
            continue
        seen.add(token)
        roots = [city, GC_DOCS, *also]
        if '/' in token:
            ok = any(exists(r, token) for r in roots)
        else:
            ok = (any(exists(city / d, token) for d in BARE_DIRS)
                  or any(exists(city, g.format(token)) for g in BARE_GLOBS)
                  or any(exists(r, token) for r in also))
        out.append((token, ok))
    return out


def memory_findings(city):
    mem = memory_dir(city)
    index = (mem / 'MEMORY.md').read_text()
    files = {p.name for p in mem.glob('*.md') if p.name != 'MEMORY.md'}
    listed = set(re.findall(r'\]\(([^)]+\.md)\)', index))
    names = {f[:-3] for f in files}
    found = [f'memory: index lists missing {f}' for f in sorted(listed - files)]
    found += [f'memory: {f} not in MEMORY.md' for f in sorted(files - listed)]
    for f in sorted(files):
        text = (mem / f).read_text()
        for link in re.findall(r'\[\[([^\]]+)\]\]', text):
            if link not in names:
                found.append(f'memory: {f} links missing [[{link}]]')
        for group in SEE_RE.findall(text):
            for name in SLUG_RE.findall(re.sub(r'\[\[[^\]]+\]\]', ' ', group)):
                if (name not in names and not (city / 'docs' / f'{name}.md').exists()
                        and not (city / '.claude' / 'skills' / name).exists()
                        and not any((d / name).exists() for d in SKILL_DIRS)):
                    found.append(f'memory: {f} names missing memory {name} (plain text)')
        fm = FM_RE.match(text)
        if not fm:
            found.append(f'memory: {f} has no frontmatter')
            continue
        try:
            meta = yaml.safe_load(fm.group(1)) or {}
        except yaml.YAMLError as e:
            found.append(f'memory: {f} frontmatter is invalid YAML ({str(e).splitlines()[0]})')
            continue
        if not meta.get('name') or not meta.get('description'):
            found.append(f'memory: {f} frontmatter lacks name or description')
    return found


def seat_memory(city, seat=None):
    _, out, _ = sh(sys.executable, 'dispatch/seat_memory_sync.py', 'check', cwd=city)
    lines = [l for l in out.splitlines() if ':' in l]
    return [l for l in lines if seat is None or l.startswith(f'{seat}:')]


def prompt_file(city, agent):
    return city / 'agents' / agent / 'prompt.template.md'


def wake_files(city, agent):
    files = [prompt_file(city, agent)]
    if agent in SEATS:
        files += [city / 'agents' / agent / 'agent.toml', city / 'formulas' / f'{agent}-pass.toml']
    return files


def last_commit(city, paths):
    """UTC datetime of the newest commit touching any of paths, or None."""
    _, out, _ = sh('git', 'log', '-1', '--format=%cI', '--', *map(str, paths), cwd=city)
    return dt.datetime.fromisoformat(out.strip()).astimezone(dt.timezone.utc) if out.strip() else None


def utc(stamp):
    return dt.datetime.fromisoformat(stamp.replace('Z', '+00:00')) if stamp else None


def doctor(city):
    found = []
    if not (city / 'city.toml').is_file():
        return [f'city: no city.toml under {city}']
    code, _, err = sh('gc', 'status', cwd=city)
    if code:
        found.append(f'city: gc status failed: {err.strip()[:120]}')
    for agent in AGENTS:
        code, out, err = sh('gc', 'prime', '--strict', agent, cwd=city)
        if code or not out.strip() or 'hard_fail=true' in err:
            found.append(f'{agent}: gc prime --strict failed: {err.strip()[:160]}')
        for ref, ok in refs(city, prompt_file(city, agent)):
            if not ok:
                found.append(f'{agent}: prompt names missing {ref}')
    for doc in ('docs/delegated-seats.md',):
        for ref, ok in refs(city, city / doc):
            if not ok:
                found.append(f'{doc}: names missing {ref}')
    found += [f'seat-memory: {line}' for line in seat_memory(city)]
    found += memory_findings(city)
    return found


def render(city, agent, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    code, out, err = sh('gc', 'prime', '--strict', agent, cwd=city)
    sys.stderr.write(err)
    if code:
        sys.exit(f'gc prime --strict {agent} failed')
    (out_dir / f'{agent}.prompt.md').write_text(out)
    index = memory_dir(city) / 'MEMORY.md' if agent == 'mayor' else city / 'agents' / agent / 'memory' / 'MEMORY.md'
    (out_dir / f'{agent}.memory.md').write_text(index.read_text())
    written = [f'{agent}.prompt.md ({len(out.splitlines())} lines)', f'{agent}.memory.md']
    if agent in SEATS:
        toml = (city / 'agents' / agent / 'agent.toml').read_text()
        nudge = re.search(r'^nudge\s*=\s*(.+)$', toml, re.M)
        formula = city / 'formulas' / f'{agent}-pass.toml'
        (out_dir / f'{agent}.wake.md').write_text(
            f'# {agent} wake text\n\n## agent.toml nudge\n\n{nudge.group(1) if nudge else "(none)"}\n\n'
            f'## {formula.relative_to(city)}\n\n{formula.read_text() if formula.exists() else "(missing)"}\n')
        written.append(f'{agent}.wake.md')
    print(f'{out_dir}: ' + ', '.join(written))


def show_bead(city, bead):
    code, out, _ = sh('gc', 'bd', 'show', bead, '--json', cwd=city)
    if code:
        return None
    data = json.loads(out)
    return data[0] if isinstance(data, list) else data


def last_pass(city, seat):
    code, out, err = sh('gc', 'order', 'history', f'{seat}-pass', cwd=city)
    if code:
        sys.exit(f'gc order history {seat}-pass failed: {err.strip()}')
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2 or '-wisp-' in parts[1]:
            continue
        data = show_bead(city, parts[1])
        if not data or data.get('status') != 'closed':
            continue
        changed = last_commit(city, wake_files(city, seat))
        closed = utc(data.get('closed_at'))
        print(json.dumps({**{k: data.get(k) for k in ('id', 'closed_at', 'close_reason')},
                          'context_changed_at': changed.isoformat() if changed else None,
                          'prompt_newer': bool(changed and closed and changed > closed)}, indent=1))
        return 0
    print(f'{seat}: no closed pass bead in order history')
    return 1


def primed(city, agent):
    code, out, err = sh('gc', 'session', 'list', '--json', cwd=city)
    if code:
        sys.exit(f'gc session list failed: {err.strip()}')
    sessions = json.loads(out)
    sessions = sessions if isinstance(sessions, list) else sessions.get('sessions', [])
    live = [s for s in sessions if s.get('template') == agent or s.get('agent_name') == agent
            or (s.get('template') or '').endswith(f'{agent}-pool')]
    changed = last_commit(city, wake_files(city, agent))
    if not live:
        print(json.dumps({'agent': agent, 'session': None, 'context_changed_at': changed and changed.isoformat()}))
        return 1
    for s in live:
        meta = (show_bead(city, s['id']) or {}).get('metadata', {})
        primed_at = utc(meta.get('primed_at'))
        print(json.dumps({
            'agent': agent, 'session': s['id'], 'state': s.get('state'),
            'primed_at': meta.get('primed_at') or None,
            'reset_pending': meta.get('continuation_reset_pending') == 'true' or meta.get('restart_requested') == 'true',
            'context_changed_at': changed.isoformat() if changed else None,
            'on_current_context': bool(primed_at and changed and primed_at >= changed),
        }, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--city', type=Path, default=Path(os.environ.get('GC_CITY', Path.home() / 'city')))
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('doctor')
    p = sub.add_parser('render')
    p.add_argument('agent', choices=AGENTS)
    p.add_argument('out', type=Path)
    p = sub.add_parser('refs')
    p.add_argument('--also', type=Path, action='append', default=[])
    p.add_argument('files', nargs='+')
    sub.add_parser('memory')
    p = sub.add_parser('seat-memory')
    p.add_argument('seat', choices=SEATS)
    p = sub.add_parser('last-pass')
    p.add_argument('seat', choices=SEATS)
    p = sub.add_parser('primed')
    p.add_argument('agent', choices=AGENTS)
    args = ap.parse_args(argv)
    city = args.city.resolve()
    if args.cmd == 'doctor':
        found = doctor(city)
        print('\n'.join(found) or 'doctor: clean')
        return 1 if found else 0
    if args.cmd == 'render':
        render(city, args.agent, args.out)
        return 0
    if args.cmd == 'refs':
        bad = 0
        for f in args.files:
            for ref, ok in refs(city, f, [a.expanduser() for a in args.also]):
                print(f'{"ok  " if ok else "MISS"} {f}: {ref}')
                bad += not ok
        return 1 if bad else 0
    if args.cmd == 'memory':
        found = memory_findings(city)
        print('\n'.join(found) or 'memory: clean')
        return 1 if found else 0
    if args.cmd == 'seat-memory':
        lines = seat_memory(city, args.seat)
        print('\n'.join(lines) or f'{args.seat}: seat memory in step')
        return 1 if lines else 0
    if args.cmd == 'primed':
        return primed(city, args.agent)
    return last_pass(city, args.seat)


if __name__ == '__main__':
    sys.exit(main())
