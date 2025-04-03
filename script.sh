#!/bin/bash
# TODO: automate so that given a fix commit, it will automatically find the test file and code files that need to be patched
# Run using: bash script.sh <FIX_COMMIT> <TEST_FILE> <CODE_FILES>

# --- Inputs ---
FIX_COMMIT="$1"
TEST_FILE="$2"
CODE_FILES="${@:3}"

ROCKSDB_DIR="./rocksdb"
PRE_FIX_COMMIT=$(git -C "$ROCKSDB_DIR" rev-parse "${FIX_COMMIT}^")
TEST_NAME=$(basename "$TEST_FILE" .cc)
LOG_DIR="./test_logs/$FIX_COMMIT"
RESULT_FILE="$LOG_DIR/result.txt"

mkdir -p "$LOG_DIR"

echo "=== Using FIX_COMMIT: $FIX_COMMIT"
echo "=== Deduced PRE_FIX_COMMIT: $PRE_FIX_COMMIT"
echo "=== Test file: $TEST_FILE"
echo "=== Code files: $CODE_FILES"
echo "=== Log output to: $LOG_DIR"

cd "$ROCKSDB_DIR"

# --- Step 1: Checkout pre-fix commit ---
git reset --hard
git clean -fd
git checkout "$PRE_FIX_COMMIT"

# --- Step 2: Apply test patch ---
echo "Generating and applying test patch..."
git diff "$FIX_COMMIT^" "$FIX_COMMIT" -- "$TEST_FILE" > ../test.patch
git apply ../test.patch

# --- Step 3: Build and run test (should fail) ---
echo "Building RocksDB..."
make -j8

echo "Building test binary: $TEST_NAME"
make "$TEST_NAME"

echo "Running test (expected to FAIL)..."
# set +e
./"$TEST_NAME" > "$LOG_DIR/pre_fix_output.log" 2>&1
PRE_EXIT_CODE=$?
# set -e



if [ "$PRE_EXIT_CODE" -eq 0 ]; then
  echo "❌ Pre-fix test unexpectedly PASSED." | tee "$RESULT_FILE"
else
  echo "✅ Pre-fix test correctly FAILED." | tee "$RESULT_FILE"
fi

echo "yay"

# --- Step 4: Apply code fix patch ---
echo "Generating and applying code fix patch..."
git diff "$FIX_COMMIT^" "$FIX_COMMIT" -- $CODE_FILES > ../fix.patch
git apply ../fix.patch

# --- Step 5: Rebuild and rerun test ---
echo "Rebuilding RocksDB with fix..."
make -j8

echo "Re-running test (expected to PASS)..."
./"$TEST_NAME"
POST_EXIT_CODE=$?

if [ "$POST_EXIT_CODE" -eq 0 ]; then
  echo "✅ Post-fix test PASSED as expected."
else
  echo "❌ Post-fix test FAILED unexpectedly."
fi

# --- Step 6: Clean up ---
git reset --hard
git clean -fd

echo "=== Done! Logs and verdicts saved to $LOG_DIR"
