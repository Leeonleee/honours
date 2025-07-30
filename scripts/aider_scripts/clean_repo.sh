#!/bin/bash

HONOURS_DIR="$1"

DUCKDB_DIR="$HONOURS_DIR/duckdb"

cd "$DUCKDB_DIR" || exit 1

git reset --hard
git clean -fd
make clean
git checkout main

