#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "==> Running VHS tapes..."
for tape in docs/vhs/*.tape; do
    echo "  Running: $tape"
    vhs "$tape"
done

echo "==> Cleaning up demo artifacts..."

# Files created by tapes (skip any that are git-tracked)
for f in \
    remote-demo.yaml \
    remote-example.yaml \
    project-with-mapping.yaml \
    team-mapping.yaml \
    company-info.yaml \
    environments.yaml \
    multi-mapping-project.yaml \
    my-project.yaml \
    .vscode/struct-schema.json \
    .vscode/struct-plugins.schema.json; do
    git ls-files --error-unmatch "$f" &>/dev/null || rm -f "$f"
done

# Directories created by tapes
rm -rf \
    remote-project/ \
    remote-demo/ \
    my-python-app/ \
    backend-project/ \
    dev-app/ \
    my-custom-project/

# Remove .vscode dir if now empty
[ -d .vscode ] && rmdir --ignore-fail-on-non-empty .vscode

echo "==> Done! GIFs are in docs/vhs/"
