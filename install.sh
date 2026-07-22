#!/usr/bin/env bash
# Symlinks all skill directories into ~/.claude/skills/ (Claude Code)
# and ~/.agents/skills/ (Codex).
# Run once after cloning, and again after adding new skills.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

link_skills() {
  local target_dir="$1"
  mkdir -p "$target_dir"
  for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    skill_name="$(basename "$skill_dir")"
    if [ -f "$skill_dir/SKILL.md" ]; then
      ln -sfn "$skill_dir" "$target_dir/$skill_name"
      echo "  linked: $skill_name -> $target_dir/$skill_name"
    fi
  done
}

echo "Installing skills..."
link_skills "$HOME/.claude/skills"
link_skills "$HOME/.agents/skills"
echo "Done."
