#!/bin/bash

# Paths
HONOURS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
DUCKDB_DIR="$HONOURS_DIR/duckdb"
IGNORE_SRC="$HONOURS_DIR/scripts/aider_scripts/.aiderignore"
PROMPT_PATH="$HONOURS_DIR/benchmark_problems/$1/$1.prompt"
MODIFIED_FILE_REL="src/common/types/vector.cpp"  # Change as needed

echo $DUCKDB_DIR
echo $PROMPT_PATH
echo $MODIFIED_FILE_REL

# Load .env from honours directory
if [ -f "$HONOURS_DIR/.env" ]; then
  set -a
  source "$HONOURS_DIR/.env"
  set +a
  echo "✅ Loaded environment variables from .env"
else
  echo "❌ .env file not found in $HONOURS_DIR"
  exit 1
fi

# Copy .aiderignore into duckdb
cp "$IGNORE_SRC" "$DUCKDB_DIR/.aiderignore"
echo "✅ Copied .aiderignore into duckdb"

# Run aider from within duckdb (so file paths are correct)
cd "$DUCKDB_DIR" || exit 1
aider --model o3 --no-gitignore --yes -f "$PROMPT_PATH" "$MODIFIED_FILE_REL"
