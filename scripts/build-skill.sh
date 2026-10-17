#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
archive="$repo_root/dist/top-down-staging.skill"

mkdir -p "$repo_root/dist"
rm -f "$archive"
(cd "$repo_root/skills" && zip -qr "$archive" top-down-staging)
printf 'Built %s\n' "$archive"
