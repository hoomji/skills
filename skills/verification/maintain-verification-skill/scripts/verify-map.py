#!/usr/bin/env python3
"""Lint a project-local verification skill and its feature map.

Reads a `verify-<app>/` directory: SKILL.md plus `features/README.md` and one
file per feature. Reports the mechanical drift a human or agent otherwise finds
by hand at the start of every maintenance pass: broken index links, unindexed
feature files, missing or misordered sections, empty sections, and helper
scripts the skill names that the repository no longer ships.

Exit codes, distinct so a caller never parses text:
  0  clean
  1  findings
  2  the command line was wrong
  3  the directory is not a verification skill (no SKILL.md or no features/README.md)
"""

import argparse
import json
import os
import re
import sys

REQUIRED_SKILL_SECTIONS = ("Launch", "Doctor", "Drive", "Evidence", "Cleanup")
REQUIRED_FEATURE_SECTIONS = (
    "Sub-features",
    "How to get to it (user POV)",
    "Driving it with ",
    "Gotchas",
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s#]+)")
H2_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
SCRIPT_RE = re.compile(r"(?<![\w/.-])((?:scripts|bin|e2e|tools)/[\w./-]+\.(?:mjs|js|ts|py|sh))")

EXAMPLES = """\
examples:
  verify-map.py .claude/skills/verify-myapp check
  verify-map.py .claude/skills/verify-myapp check --repo-root . --json
  verify-map.py .claude/skills/verify-myapp list
  verify-map.py .claude/skills/verify-myapp list --json | jq -r '.features[].file'
"""


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def sections(text):
    """Return (title, body) pairs for each H2 in order."""
    heads = list(H2_RE.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((m.group(1).strip(), text[m.end():end].strip()))
    return out


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    block = text[4:end]
    fields = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def finding(findings, file, rule, message):
    findings.append({"file": file, "rule": rule, "message": message})


def check_skill(skill_dir, findings, repo_root):
    path = os.path.join(skill_dir, "SKILL.md")
    text = read(path)
    rel = os.path.relpath(path)
    fm = frontmatter(text)
    if fm is None:
        finding(findings, rel, "frontmatter", "no YAML frontmatter; the skill never registers")
    else:
        for key in ("name", "description"):
            if not fm.get(key):
                finding(findings, rel, "frontmatter", f"frontmatter lacks `{key}`")
        expected = os.path.basename(os.path.abspath(skill_dir))
        if fm.get("name") and fm["name"] != expected:
            finding(findings, rel, "frontmatter", f"name `{fm['name']}` differs from directory `{expected}`")
    titles = [t for t, _ in sections(text)]
    for want in REQUIRED_SKILL_SECTIONS:
        if want not in titles:
            finding(findings, rel, "section", f"missing `## {want}`")
    for title, body in sections(text):
        if title in REQUIRED_SKILL_SECTIONS and not body:
            finding(findings, rel, "section", f"`## {title}` is empty")
    check_scripts(rel, text, findings, repo_root)
    return text


def check_scripts(rel, text, findings, repo_root):
    if repo_root is None:
        return
    seen = set()
    for m in SCRIPT_RE.finditer(text):
        script = m.group(1)
        if script in seen:
            continue
        seen.add(script)
        if not os.path.exists(os.path.join(repo_root, script)):
            finding(findings, rel, "helper", f"names `{script}`, which does not exist under {repo_root}")


def check_features(skill_dir, findings, repo_root):
    feat_dir = os.path.join(skill_dir, "features")
    readme = os.path.join(feat_dir, "README.md")
    readme_rel = os.path.relpath(readme)
    text = read(readme)
    linked = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        norm = os.path.normpath(os.path.join(feat_dir, target))
        if os.path.dirname(norm) != os.path.normpath(feat_dir) or os.path.basename(norm) == "README.md":
            continue
        linked.append(os.path.basename(norm))
    dupes = sorted({x for x in linked if linked.count(x) > 1})
    for d in dupes:
        finding(findings, readme_rel, "index", f"links `{d}` more than once")
    on_disk = sorted(f for f in os.listdir(feat_dir) if f.endswith(".md") and f != "README.md")
    for name in linked:
        if name not in on_disk:
            finding(findings, readme_rel, "index", f"links `{name}`, which does not exist")
    for name in on_disk:
        if name not in linked:
            finding(findings, os.path.relpath(os.path.join(feat_dir, name)), "index", "not linked from README.md")
    features = []
    for name in on_disk:
        path = os.path.join(feat_dir, name)
        rel = os.path.relpath(path)
        body = read(path)
        secs = sections(body)
        titles = [t for t, _ in secs]
        pos = []
        for want in REQUIRED_FEATURE_SECTIONS:
            hit = next((i for i, t in enumerate(titles) if t == want or (want.endswith(" ") and t.startswith(want))), None)
            if hit is None:
                finding(findings, rel, "section", f"missing `## {want.strip()}`")
            else:
                pos.append(hit)
                if not secs[hit][1]:
                    finding(findings, rel, "section", f"`## {titles[hit]}` is empty")
        if pos != sorted(pos):
            finding(findings, rel, "section", "sections are out of the standard order")
        first = next((ln.lstrip("# ").strip() for ln in body.splitlines() if ln.startswith("# ")), name[:-3])
        check_scripts(rel, body, findings, repo_root)
        features.append({"file": name, "title": first, "sections": titles, "indexed": name in linked})
    return features


def main(argv):
    parser = argparse.ArgumentParser(
        prog="verify-map.py",
        description="Lint a verification skill directory and its feature map.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("skill_dir", help="the verify-<app>/ directory holding SKILL.md and features/")
    parser.add_argument("command", choices=("check", "list"), help="check: report drift; list: print the feature index")
    parser.add_argument("--repo-root", help="repository root; enables the helper-exists check for scripts the skill names")
    parser.add_argument("--json", action="store_true", help="one JSON object on stdout instead of lines")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code not in (0, None) else 0

    skill_dir = args.skill_dir
    if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")) or not os.path.isfile(
        os.path.join(skill_dir, "features", "README.md")
    ):
        sys.stderr.write(
            f"error: {skill_dir} is not a verification skill (needs SKILL.md and features/README.md)\n"
            f"  verify-map.py .claude/skills/verify-<app> check\n"
        )
        return 3

    findings = []
    check_skill(skill_dir, findings, args.repo_root)
    features = check_features(skill_dir, findings, args.repo_root)

    if args.command == "list":
        if args.json:
            print(json.dumps({"skill_dir": skill_dir, "features": features}, indent=2))
        else:
            for f in features:
                flag = "" if f["indexed"] else "  (unindexed)"
                print(f"{f['file']:32} {f['title']}{flag}")
            print(f"features: {len(features)}")
        return 0

    if args.json:
        print(json.dumps({"skill_dir": skill_dir, "features": len(features), "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}: [{f['rule']}] {f['message']}")
        print(f"features: {len(features)}  findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
