#!/bin/bash

set -e

# Usage: ./apply_once.sh <problem_id> <model_name>
# Run from project root directory

# Arguments
PROBLEM_ID="$1"
MODEL_NAME="$2"

# Paths
HONOURS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
DUCKDB_DIR="$HONOURS_DIR/duckdb"
IGNORE_SRC="$HONOURS_DIR/scripts/aider_scripts/.aiderignore"
PROMPT_PATH="$HONOURS_DIR/benchmark_problems/$PROBLEM_ID/$PROBLEM_ID.prompt"
JSON_PATH="$HONOURS_DIR/benchmark_problems/$PROBLEM_ID/$PROBLEM_ID.json"

# Extract modified files
MODIFIED_FILES=$(jq -r '.modified_files[]' "$JSON_PATH")

# Load .env from honours directory
if [ -f "$HONOURS_DIR/.env" ]; then
  set -a
  source "$HONOURS_DIR/.env"
  set +a
  echo "Loaded environment variables from .env"
else
  echo ".env file not found in $HONOURS_DIR"
  exit 1
fi

# Copy .aiderignore into DuckDB
cp "$IGNORE_SRC" "$DUCKDB_DIR/.aiderignore"
echo "Copied .aiderignore into duckdb"

# Run aider from within duckdb
cd "$DUCKDB_DIR" || exit 1
aider --model "$MODEL_NAME" --no-gitignore --yes -f "$PROMPT_PATH" $MODIFIED_FILES

