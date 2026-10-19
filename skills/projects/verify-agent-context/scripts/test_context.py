#!/usr/bin/env python3
"""Unit tier: skill_findings and hook_findings over a scratch city. No gc, no store, no network.

  python3 .claude/skills/verify-agent-context/scripts/test_context.py
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import context  # noqa: E402

GOOD_HOOKS = {
    'hooks': {
        'SessionStart': [{'matcher': 'startup', 'hooks': [{'type': 'command', 'command': 'gc prime --hook'}]}],
        'UserPromptSubmit': [{'matcher': '', 'hooks': [{'type': 'command', 'command': 'gc hook run -- mail check'}]}],
    }
}


def skill(root, name, desc='Does a thing.', extra='', body='# Skill\n', dirname=None):
    d = root / (dirname or name)
    d.mkdir(parents=True)
    (d / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: {desc}\n{extra}---\n{body}')
    return d


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.city = Path(self.tmp.name) / 'city'
        (self.city / 'agents' / 'mayor').mkdir(parents=True)
        (self.city / 'agents' / 'mayor' / 'prompt.template.md').write_text('# Mayor\n')
        (self.city / '.claude-memory').mkdir()
        (self.city / 'hooks').mkdir()
        (self.city / 'hooks' / 'claude.json').write_text(json.dumps(GOOD_HOOKS))
        self.skills = self.city / '.claude' / 'skills'
        self.skills.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_hooks(self, rel, data):
        p = self.city / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data if isinstance(data, str) else json.dumps(data))


class SkillFindings(Scratch):
    def test_pack_prefixed_dir_matches_bare_name(self):
        skill(self.skills, 'foo', desc='Use when asked.', dirname='bmad.foo')
        self.assertEqual(context.skill_findings(self.city), [])

    def test_dir_name_mismatch_is_a_finding(self):
        skill(self.skills, 'bar', desc='Use when asked.', dirname='foo')
        found = context.skill_findings(self.city)
        self.assertEqual(len(found), 1)
        self.assertIn('name bar does not match its directory', found[0])

    def test_frontmatter_shapes(self):
        d = self.skills / 'none'
        d.mkdir()
        (d / 'SKILL.md').write_text('# no frontmatter\n')
        skill(self.skills, 'nodesc', desc='')
        d = self.skills / 'badyaml'
        d.mkdir()
        (d / 'SKILL.md').write_text('---\nname: [oops\n---\n')
        found = context.skill_findings(self.city)
        self.assertEqual(sorted(f.split(' ', 2)[2][:14] for f in found),
                         sorted(['has no frontma', 'frontmatter la', 'frontmatter is']))

    def test_untriggered_owned_skill(self):
        skill(self.skills, 'quiet')
        found = context.skill_findings(self.city)
        self.assertEqual(len(found), 1)
        self.assertIn('quiet is untriggered', found[0])

    def test_when_clause_triggers(self):
        skill(self.skills, 'quiet', desc='Does a thing. Use whenever the owner asks.')
        self.assertEqual(context.skill_findings(self.city), [])

    def test_user_invoked_skill_is_triggered(self):
        skill(self.skills, 'quiet', extra='disable-model-invocation: true\n')
        self.assertEqual(context.skill_findings(self.city), [])

    def test_always_on_mention_triggers(self):
        skill(self.skills, 'quiet')
        (self.city / 'agents' / 'mayor' / 'prompt.template.md').write_text('Run the `quiet` skill first.\n')
        self.assertEqual(context.skill_findings(self.city), [])

    def test_pack_skill_is_never_untriggered(self):
        target = Path(self.tmp.name) / 'cache' / 'quiet'
        skill(target.parent, 'quiet')
        os.symlink(target, self.skills / 'quiet')
        self.assertEqual(context.skill_findings(self.city), [])

    def test_scripts_compile(self):
        d = skill(self.skills, 'tool', desc='Use when needed.')
        (d / 'scripts').mkdir()
        (d / 'scripts' / 'ok.py').write_text('print(1)\n')
        (d / 'scripts' / 'bad.py').write_text('def (:\n')
        (d / 'scripts' / 'bad.sh').write_text('if [ 1 ]; then\n')
        (d / 'scripts' / 'ok.sh').write_text('echo hi\n')
        found = sorted(context.skill_findings(self.city))
        self.assertEqual(len(found), 2)
        self.assertIn('tool/scripts/bad.py does not compile: line 1', found[0])
        self.assertIn('tool/scripts/bad.sh does not compile', found[1])

    def test_scripts_in_linked_pack_skill_compile_once(self):
        target = Path(self.tmp.name) / 'cache' / 'pack'
        d = skill(target.parent, 'pack', desc='Use when needed.')
        (d / 'bad.py').write_text('def (:\n')
        os.symlink(target, self.skills / 'pack')
        codex = self.city / '.agents' / 'skills'
        codex.mkdir(parents=True)
        os.symlink(target, codex / 'pack')
        found = context.skill_findings(self.city)
        self.assertEqual(len(found), 1, found)
        self.assertIn('does not compile', found[0])

    def test_refs_rooted_paths_only(self):
        skill(self.skills, 'refs', desc='Use when needed.',
              body='Read `dispatch/missing.py`, write `plan.md`, run `nothere.sh`.\n')
        found = sorted(context.skill_findings(self.city))
        self.assertEqual([f.rsplit(' ', 1)[1] for f in found], ['dispatch/missing.py', 'nothere.sh'])

    def test_refs_resolve_inside_the_skill(self):
        d = skill(self.skills, 'refs', desc='Use when needed.', body='Run `scripts/go.py`.\n')
        (d / 'scripts').mkdir()
        (d / 'scripts' / 'go.py').write_text('pass\n')
        self.assertEqual(context.skill_findings(self.city), [])


class HookFindings(Scratch):
    def test_valid_files_are_clean(self):
        self.write_hooks('.gc/settings.json', GOOD_HOOKS)
        self.assertEqual(context.hook_findings(self.city), [])

    def test_invalid_json(self):
        self.write_hooks('.codex/hooks.json', '{"hooks": ')
        found = context.hook_findings(self.city)
        self.assertEqual(len(found), 1)
        self.assertIn('.codex/hooks.json is invalid JSON', found[0])

    def test_unknown_event_type_and_empty_command(self):
        self.write_hooks('hooks/claude.json', {'hooks': {
            'OnWake': [{'matcher': '', 'hooks': [{'type': 'command', 'command': 'x'}]}],
            'Stop': [{'matcher': '', 'hooks': [{'type': 'shell', 'command': 'x'}, {'type': 'command', 'command': ' '}]}],
        }})
        found = context.hook_findings(self.city)
        self.assertEqual(len(found), 3, found)
        self.assertIn('OnWake is not a hook event', found[0])
        self.assertIn('Stop[0].hooks[0] type is not one of', found[1])
        self.assertIn('Stop[0].hooks[1] has no command', found[2])

    def test_duplicate_matcher_is_a_finding(self):
        hook = {'type': 'command', 'command': 'true'}
        self.write_hooks('hooks/claude.json', {'hooks': {'SessionStart': [
            {'matcher': 'startup', 'hooks': [hook]}, {'matcher': 'compact', 'hooks': [hook]},
            {'matcher': 'startup', 'hooks': [hook]}]}})
        found = context.hook_findings(self.city)
        self.assertEqual(found, ['hooks: hooks/claude.json SessionStart has 2 blocks with matcher "startup" (gc keeps one)'])

    def test_named_scripts_must_exist_and_compile(self):
        (self.city / 'hooks' / 'guard.sh').write_text('if [ 1 ]; then\n')
        guard = self.city / 'hooks' / 'guard.sh'
        self.write_hooks('hooks/claude.json', {'hooks': {'Stop': [{'matcher': '', 'hooks': [
            {'type': 'command', 'command': f'timeout 5 bash {guard} || true'},
            {'type': 'command', 'command': f'python3 {self.city}/dispatch/gone.py show'},
            {'type': 'command', 'command': 'bash $CITY/hooks/unknown.sh'},
        ]}]}})
        found = context.hook_findings(self.city)
        self.assertEqual(len(found), 2, found)
        self.assertIn(f'script {guard} does not compile', found[0])
        self.assertIn('names missing', found[1])
        self.assertIn('dispatch/gone.py', found[1])

    def test_render_dropped_an_override_hook(self):
        rendered = json.loads(json.dumps(GOOD_HOOKS))
        rendered['hooks']['SessionStart'][0]['hooks'] = [{'type': 'command', 'command': 'gc prime --hook'}]
        self.write_hooks('hooks/claude.json', {'hooks': {'SessionStart': [{'matcher': 'startup', 'hooks': [
            {'type': 'command', 'command': 'gc prime --hook'},
            {'type': 'command', 'command': 'bash install-guard'}]}]}})
        self.write_hooks('.gc/settings.json', rendered)
        found = context.hook_findings(self.city)
        self.assertEqual(found, ['hooks: .gc/settings.json dropped the hooks/claude.json SessionStart hook: bash install-guard'])

    def test_no_rendered_file_means_no_drop_check(self):
        self.assertEqual(context.hook_findings(self.city), [])


if __name__ == '__main__':
    unittest.main()
