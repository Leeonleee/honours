import os
import subprocess
import json

# Configurations
PR_FOLDER_PATH = "../test_in_progress_prs"
DUCKDB_REPO_PATH = "../duckdb"
PROCESS_SCRIPT_PATH = "process_single_pr.py"

def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[Error] Command failed: {cmd}")
        print(result.stdout)
        print(result.stderr)
        return None
    return result

def apply_patch(patch_path, repo_path):
    return run(f"git apply {patch_path}", cwd=repo_path)

def build_duckdb(repo_path):
    return run("make -j$(nproc)", cwd=repo_path)

def run_test(test_path, repo_path):
    result = run(f"./build/release/test/unittest {test_path}", cwd=repo_path, check=False)
    if result is None:
        return False
    return "All tests passed" in result.stdout

def get_test_path_from_patch(patch_path):
    with open(patch_path) as f:
        for line in f:
            if line.startswith("+++ b/test/"):
                return os.path.join("test", line.split("+++ b/test/")[1].strip())
    return None

def main():
    valid_prs = []

    for pr in os.listdir(PR_FOLDER_PATH):
        pr_path = os.path.join(PR_FOLDER_PATH, pr)
        if not os.path.isdir(pr_path):
            continue

        print(f"\n--- Testing PR {pr} ---")

        # Reset DuckDB repo
        run("git reset --hard", cwd=DUCKDB_REPO_PATH)
        run("git clean -fd", cwd=DUCKDB_REPO_PATH)

        # Process PR
        process = run(f"python3 {PROCESS_SCRIPT_PATH} {pr_path} {DUCKDB_REPO_PATH}")
        if process is None:
            continue

        # Checkout to PR commit
        with open(os.path.join(pr_path, f"{pr}.json")) as f:
            commit_hash = json.load(f)["base_commit"]
        if not run(f"git checkout {commit_hash}", cwd=DUCKDB_REPO_PATH):
            continue

        # Compile baseline code
        if not build_duckdb(DUCKDB_REPO_PATH):
            continue

        # Get test path
        test_patch_path = os.path.join(pr_path, "test.patch")
        test_rel_path = get_test_path_from_patch(test_patch_path)
        if not test_rel_path:
            print(f"Could not determine test path for PR {pr}")
            continue

        # Run baseline test (should pass)
        if not run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("Baseline test failed")
            continue

        # Apply test.patch and rerun test (should fail)
        run("git reset --hard", cwd=DUCKDB_REPO_PATH)
        if not apply_patch(test_patch_path, DUCKDB_REPO_PATH):
            continue
        if build_duckdb(DUCKDB_REPO_PATH) is None:
            continue
        if run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("Test did not fail after applying test.patch")
            continue

        # Apply fix.patch and rerun test (should pass)
        run("git reset --hard", cwd=DUCKDB_REPO_PATH)
        if not apply_patch(test_patch_path, DUCKDB_REPO_PATH):
            continue
        if not apply_patch(os.path.join(pr_path, "fix.patch"), DUCKDB_REPO_PATH):
            continue
        if build_duckdb(DUCKDB_REPO_PATH) is None:
            continue
        if not run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("Fix did not make the test pass")
            continue

        print(f"✅ PR {pr} is valid")
        valid_prs.append(pr)

    print("\n=== Valid PRs ===")
    for pr in valid_prs:
        print(pr)

if __name__ == "__main__":
    main()
