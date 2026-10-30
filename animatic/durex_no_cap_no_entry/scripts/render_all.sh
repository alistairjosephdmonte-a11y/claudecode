#!/usr/bin/env bash
# Render shots one Blender process per shot (bounds memory; resumes by skipping existing frames).
# Usage: scripts/render_all.sh <pass> <pct> <samples> <shot> [<shot> ...]
set -u
cd "$(dirname "$0")/.."
B=${BLENDER:-blender}
pass=$1; pct=$2; samples=$3; shift 3
for n in "$@"; do
  "$B" -b DUREX_NO_CAP_animatic.blend --python scripts/render_shots.py -- \
    --pass "$pass" --engine EEVEE --pct "$pct" --samples "$samples" --shots "$n" || echo "SHOT_FAILED $n"
done
