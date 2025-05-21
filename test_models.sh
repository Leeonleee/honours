#!/bin/bash

models=(
    "o3"
)

# number of completions per model
k=3

# path to benchmark script
SCRIPT="scripts/benchmark/run_benchmark.py"

# loop through models and run the benchmark
for model in "${models[@]}"; do
    echo "🚀 Running benchmark for model: $model"
    python3 $SCRIPT \
        --m $model \
        --k $k
    echo "✅ Benchmark for model $model completed"
    echo ""
done