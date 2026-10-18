#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
generic_archive="$repo_root/dist/top-down-staging-skill.zip"
claude_archive="$repo_root/dist/top-down-staging.skill"

mkdir -p "$repo_root/dist"
rm -f "$generic_archive" "$claude_archive"
(cd "$repo_root/skills" && zip -qr "$generic_archive" top-down-staging)
cp "$generic_archive" "$claude_archive"
printf 'Built %s\n' "$generic_archive"
printf 'Built %s\n' "$claude_archive"
