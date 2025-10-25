#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -e

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DART_API_SCHEMA_URL="${DART_HOST:-https://app.dartai.com}/api/v0/public/schema/"
GENERATED_PATH=$(pwd | sed 's:/admin$::')/dart/generated

uv run openapi-python-client generate --url $DART_API_SCHEMA_URL --output-path $GENERATED_PATH --overwrite --meta none

# Optimize API import paths
api_dir="$GENERATED_PATH/api"
init_file="$api_dir/__init__.py"

find "$api_dir" -type f -name "*.py" ! -name "__init__.py" | while read -r file; do
    service=$(basename "$(dirname "$file")")
    method=$(basename "$file" .py)
    echo "from .$service import $method" >> "$init_file"
done

# Fix enum naming issues (VALUE_0, VALUE_1, etc. -> descriptive names)
python3 $(dirname "$0")/fix_enum_names.py
