#!/usr/bin/env bash
# Symlinks all skill directories into ~/.claude/skills/ (Claude Code)
# and ~/.agents/skills/ (Codex).
# Run once after cloning, and again after adding new skills.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

link_skills() {
  local target_dir="$1"
  mkdir -p "$target_dir"
  while IFS= read -r -d '' skill_file; do
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    ln -sfn "$skill_dir" "$target_dir/$skill_name"
    echo "  linked: $skill_name -> $target_dir/$skill_name"
  done < <(find "$SCRIPT_DIR/skills" -type f -name SKILL.md -print0)
}

echo "Installing skills..."
link_skills "$HOME/.claude/skills"
link_skills "$HOME/.agents/skills"
echo "Done."
