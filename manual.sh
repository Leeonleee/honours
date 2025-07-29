#!/bin/bash

# clean up repo
cd duckdb
make clean
git stash
git checkout main
git checkout faf428bcd389308029792504251575d47f525233

# apply patch
git apply /root/Documents/university/honours/benchmark_problems/7638/test.patch

# copy aiderignore
cp ../.aiderignore .

# Run aider command

aider --model o3 --yes --no-gitignore --no-show-model-warnings \
    -f /root/Documents/university/honours/benchmark_problems/7638/7638.prompt \
    src/parser/transform/expression/transform_function.cpp 

# Recompile
make -j$(nproc)

# Run test
build/release/test/unittest test/sql/function/list/list_sort.test