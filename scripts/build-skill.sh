#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
generic_archive="$repo_root/dist/staging-with-manimgx-skill.zip"
claude_archive="$repo_root/dist/staging-with-manimgx.skill"

mkdir -p "$repo_root/dist"
rm -f "$generic_archive" "$claude_archive"
(cd "$repo_root/skills" && zip -q "$generic_archive" \
  staging-with-manimgx/SKILL.md \
  staging-with-manimgx/references/scene.schema.json \
  staging-with-manimgx/references/staging-craft.md \
  staging-with-manimgx/scripts/staging_render.py)
cp "$generic_archive" "$claude_archive"
printf 'Built %s\n' "$generic_archive"
printf 'Built %s\n' "$claude_archive"
