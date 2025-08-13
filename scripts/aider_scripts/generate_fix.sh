# This script generates one completion

#!/bin/bash

set -e

# Usage: ./apply_once.sh <honours_dir> <problem_directory> <problem_id> <model_name>
# Run from project root directory

# Arguments
HONOURS_DIR="$1"
PROBLEM_DIR="$2"
PROBLEM_ID="$3"
MODEL_NAME="$4"

# Paths
DUCKDB_DIR="$HONOURS_DIR/repos/duckdb"
IGNORE_SRC="$HONOURS_DIR/scripts/aider_scripts/.aiderignore"
PROMPT_PATH="$PROBLEM_DIR/$PROBLEM_ID.prompt"
JSON_PATH="$PROBLEM_DIR/$PROBLEM_ID.json"


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
aider --model "$MODEL_NAME" --no-gitignore --yes --disable-playwright -f "$PROMPT_PATH" $MODIFIED_FILES


# Track success
if [ $? -eq 0 ]; then
  echo "Fix generation succeeded"
  exit 0
else
  echo "Fix generation failed"
  exit 1
fi
