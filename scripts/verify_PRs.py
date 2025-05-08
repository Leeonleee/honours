import os
import subprocess
import json
import sys

# Configurations
PR_FOLDER_PATH = "../test_in_progress_prs"
DUCKDB_REPO_PATH = "../duckdb"
PROCESS_SCRIPT_PATH = "process_single_pr.py"

# def run(cmd, cwd=None, check=True):
#     result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
#     if check and result.returncode != 0:
#         print(f"[Error] Command failed: {cmd}")
#         print(result.stdout)
#         print(result.stderr)
#         return None
#     return result

# run with full terminal output
def run(cmd, cwd=None, check=True):
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    stdout, stderr = [], []

    for line in process.stdout:
        print(line, end='')
        stdout.append(line)
    for line in process.stderr:
        print(line, end='', file=sys.stderr)
        stderr.append(line)

    process.wait()

    if check and process.returncode != 0:
        print(f"[Error] Command failed: {cmd}")
        return None

    class Result:
        def __init__(self, stdout, stderr, returncode):
            self.stdout = ''.join(stdout)
            self.stderr = ''.join(stderr)
            self.returncode = returncode

    return Result(stdout, stderr, process.returncode)



def apply_patch(patch_path, repo_path):
    return run(f"git apply {patch_path}", cwd=repo_path)

def build_duckdb(repo_path):
    return run("make -j$(nproc)", cwd=repo_path)

def run_test(test_paths, repo_path):
    unittest_path = "build/release/test/unittest"
    for test_path in test_paths:
        result = run(f"{unittest_path} {test_path}", cwd=repo_path, check=False)
        if result is None or "All tests passed" not in result.stdout:
            return False
    return True


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

def main():
    valid_prs = []

    for pr in sorted(os.listdir(PR_FOLDER_PATH), key=lambda x: int(x) if x.isdigit() else float('inf')):
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
        print("🔧 Compiling code...")
        if not build_duckdb(DUCKDB_REPO_PATH):
            print("❌ Compilation failed")
            continue
        print("✅ Compilation succeeded (Expected behaviour)")
        # Get test path
        test_patch_path = os.path.join(pr_path, "test.patch")
        test_rel_path = get_test_paths_from_patch(test_patch_path)
        if not test_rel_path:
            print(f"Could not determine test path for PR {pr}")
            continue

        # Run baseline test (should pass)
        print("✅ Running baseline test... (should pass)")
        if not run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("❌ Baseline test failed")
            continue
        print("✅ Baseline test passed (Expected behaviour)")

        # Apply test.patch and rerun test (should fail)
        print("📄 Applying test.patch...")
        if not apply_patch(test_patch_path, DUCKDB_REPO_PATH):
            print("❌ Failed to apply test.patch")
            continue
        print("✅ test.patch applied (Expected behaviour)")
        print("🔧 Compiling code...")
        if build_duckdb(DUCKDB_REPO_PATH) is None:
            print("❌ Compilation failed")
            continue
        print("✅ Compilation succeeded (Expected behaviour)")
        print("🧪 Running modified test (should fail)...")
        if run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("❌ Test did not fail after applying test.patch")
            continue
        print("✅ Modified test failed (Expected behaviour)")

        # Apply fix.patch and rerun test (should pass)
        print("📄 Applying fix.patch...")
        if not apply_patch(os.path.join(pr_path, "fix.patch"), DUCKDB_REPO_PATH):
            print("❌ Failed to apply fix.patch")
            continue
        print("✅ fix.patch applied (Expected behaviour)")
        print("🔧 Compiling code...")
        if build_duckdb(DUCKDB_REPO_PATH) is None:
            print("❌ Compilation failed")
            continue
        print("✅ Compilation succeeded (Expected behaviour)")
        print("🧪 Running fixed test (should pass)...")
        if not run_test(test_rel_path, DUCKDB_REPO_PATH):
            print("❌ Final test failed")
            continue

        print(f"✅ PR {pr} is valid")
        valid_prs.append(pr)

        # Reset DuckDB repo
        run("git reset --hard", cwd=DUCKDB_REPO_PATH)
        run("git clean -fd", cwd=DUCKDB_REPO_PATH)

    print("\n=== Valid PRs ===")
    for pr in valid_prs:
        print(pr)

if __name__ == "__main__":
    main()
