# skills

Personal agent skills for Claude Code and Codex.

## Setup

```bash
git clone git@github.com:hoomji/skills.git ~/Documents/VS/Github/skills
cd ~/Documents/VS/Github/skills
chmod +x install.sh
./install.sh
```

This symlinks all skills into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex).

## Adding a new skill

```
skills/
  my-new-skill/        ← new directory
    SKILL.md           ← required
    assets/            ← optional supporting files
    scripts/           ← optional scripts
```

Run `./install.sh` again after adding a new skill to link it.

## Skills

| Skill                                                        | Description                                                                         |
|--------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [orchestration-bootstrap](orchestration-bootstrap/SKILL.md) | Set up a file-driven Codex/Claude orchestration workflow in an existing repository  |
