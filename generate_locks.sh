#!/usr/bin/env bash
# Regenerate all lock files for UV and Poetry experiments.
set -e

echo "Generating UV lock files..."
for tier in light medium heavy; do
    echo "  uv lock: $tier"
    (cd "experiments/$tier/uv" && uv lock)
done

echo "Generating Poetry lock files..."
for tier in light medium heavy; do
    echo "  poetry lock: $tier"
    (cd "experiments/$tier/poetry" && poetry lock)
done

echo "Done."
