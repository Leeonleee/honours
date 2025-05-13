import os
import subprocess
import sys
import json
import csv
from pathlib import Path

DUCKDB_REPO_PATH = "../../duckdb"
BENCHMARK_DIR = "../../benchmark_problems"
RESULTS_CSV = "ai_patch_test_results.csv"

def run(cmd, cwd=None, check=True, log_path=None):
    process = subprocess.Popen(
        cmd,
        cwd = cwd,
        shell = True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()

    if log_path:
        with open(log_path, "w") as f:
            f.write(f"$ {cmd}\n\n")
            f.write("=== STDOUT ===\n")
            f.write(stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(stderr)

    if check and process.returncode != 0:
        print(f"[Error] Command failed: {cmd}")
        return None
    return stdout

def reset_repo(repo_path):
    run("git reset --hard", cwd=repo_path)
    run("git clean -fd", cwd=repo_path)

def apply_patch(patch_path, repo_path):
    return run(f"git apply {patch_path}", cwd=repo_path)

def build(repo_path):
    print(f"Building {repo_path}")
    return run("make -j$(nproc)", cwd=repo_path)

def get_test_paths_from_patch(patch_path):
    test_paths = []
    with open(patch_path) as f:
        for line in f:
            if line.startswith("+++ b/"):
                file_path = line[len("+++ b/"):].strip()
                # Heuristic: include anything with 'test' in the filename or directory
                if "test" in os.path.basename(file_path).lower() or "/test" in file_path.lower():
                    test_paths.append(file_path)
    return test_paths

def run_tests(test_paths, unittest_binary, repo_path, log_path=None):
    for path in test_paths:
        result = run(f"{unittest_binary} {path}", cwd=repo_path, check=False, log_path=log_path)
        if result is None or "All tests passed" not in result: # TODO Modify so that it works for other repos, not just DuckDB
            return False
    return True

def test_all(model):
    print(f" === Testing {model} ===")
    results = []

    for problem in sorted(os.listdir(BENCHMARK_DIR)):
        problem_path = os.path.join(BENCHMARK_DIR, problem)
        if not os.path.isdir(problem_path):
            continue

        test_patch_path = os.path.join(problem_path, "test.patch")
        ai_patch_dir = os.path.join(problem_path, "ai_patches")
        if not os.path.exists(test_patch_path) or not os.path.isdir(ai_patch_dir):
            print("⚠️ Missing test.patch or ai_patches")
            continue

        test_paths = get_test_paths_from_patch(test_patch_path)
        if not test_paths:
            print("⚠️ No testable paths found")
            continue
            
        total = 0
        applied = 0
        passed = 0
        failed_apply = 0
        failed_test = 0

        logs_dir = os.path.join(problem_path, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        for ai_patch_file in sorted(os.listdir(ai_patch_dir)):
            # reset repo to original state before patches
            reset_repo(DUCKDB_REPO_PATH)

            # checkout to correct commit
            with open(os.path.join(problem_path, f"{problem}.json")) as f:
                commit_hash = json.load(f)["base_commit"]
                print(commit_hash)
            if not run(f"git checkout {commit_hash}", cwd=DUCKDB_REPO_PATH):
                print(f"❌ Failed to checkout to base commit for {problem}")
                continue
            
            # make initial build (optional since the build should be valid)
            if not build(DUCKDB_REPO_PATH):
                print(f"❌ Initial build failed")
                continue

            if not apply_patch(test_patch_path, DUCKDB_REPO_PATH):
                print(f"❌ Failed to apply test.patch for {problem}")
                continue

            ai_patch_path = os.path.join(ai_patch_dir, ai_patch_file)
            total += 1

            if not apply_patch(ai_patch_path, DUCKDB_REPO_PATH):
                print(f"❌ {ai_patch_file} failed to apply")
                failed_apply += 1
                continue
        
            applied += 1

            if not build(DUCKDB_REPO_PATH):
                print(f"❌ Build failed after applying {ai_patch_file}")
                failed_test += 1
                continue
            
            unittest_binary = os.path.join(DUCKDB_REPO_PATH, "build/release/test/unittest")
            log_path = os.path.join(logs_dir, f"{ai_patch_file}.log")
            if run_tests(test_paths, unittest_binary, DUCKDB_REPO_PATH, log_path):
                print(f"✅ {ai_patch_file} passed")
                passed += 1
            else:
                print(f"❌ {ai_patch_file} failed the test")
                failed_test += 1
        results.append([
            problem,
            total,
            applied,
            failed_apply,
            passed,
            failed_test
        ])
    # print results
    print(f"\n=== {model} Patch Summary ===")
    print(f"{'Problem':<10} {'Total':<6} {'Applied':<8} {'FailedApply':<12} {'Passed':<7} {'FailedTest':<11}")
    for row in results:
        print(f"{row[0]:<10} {row[1]:<6} {row[2]:<8} {row[3]:<12} {row[4]:<7} {row[5]:<11}")

    # write to CSV
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Problem", "TotalPatches", "Applied", "FailedToApply", "PassedTest", "FailedTest"])
        writer.writerows(results)
    
    print(f"\n📄 Results written to {RESULTS_CSV}")

