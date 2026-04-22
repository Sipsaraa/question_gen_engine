#!/bin/bash
set -e

echo "Syncing documentation dependencies with uv..."
uv sync

echo "Building MkDocs site..."
uv run mkdocs build

echo "Documentation built successfully in 'site/' directory."
