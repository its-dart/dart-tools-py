#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -e

rm -rf dart/generated
uv run openapi-python-client generate --url https://app.itsdart.com/api/v0/public/schema/ --overwrite --meta none
mv dart_public_api_client dart/generated
rm -rf dart_public_api_client

# Optimize API import paths
api_dir="dart/generated/api"
init_file="$api_dir/__init__.py"

find "$api_dir" -type f -name "*.py" ! -name "__init__.py" | while read -r file; do
    service=$(basename "$(dirname "$file")")
    method=$(basename "$file" .py)
    echo "from .$service import $method" >> "$init_file"
done
