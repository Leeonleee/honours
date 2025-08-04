#!/bin/bash

models=(
    "o3",
    "gemini/gemini-2.5-pro"
)

# number of completions per model
k=1

# path to benchmark script
SCRIPT="scripts/aider_scripts/aider_benchmark.py"

# loop through models and run the benchmark
for model in "${models[@]}"; do
    echo "🚀 Running benchmark for model: $model"
    python3 $SCRIPT \
        --m $model \
        --k $k
    echo "✅ Benchmark for model $model completed"
    echo ""
done