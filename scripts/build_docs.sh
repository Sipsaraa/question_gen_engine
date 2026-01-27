#!/bin/bash
set -e

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install doc dependencies if needed
pip install mkdocs mkdocs-material

# Build the site
mkdocs build

echo "Documentation built successfully in 'site/' directory."
