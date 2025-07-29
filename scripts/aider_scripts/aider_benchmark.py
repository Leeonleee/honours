"""
This script runs the benchmark

Process:

1. Parse command line arguments to get model, number of completions, benchmark directory, and output directory.
2. Using Aider, generates code fixes for each of the specified problems in the benchmark directory.
3. Tests the generated patches using the respective test cases
4. Archives the results and generated patches into a specified output directory.
"""

import argparse, shutil, os, json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_DIR = (SCRIPT_DIR.parent.parent / "benchmark_problems")
DEFAULT_OUTPUT_DIR = (SCRIPT_DIR.parent.parent / "archive").resolve()
DUCKDB_REPO = (SCRIPT_DIR.parent.parent / "duckdb").resolve()
AIDERIGNORE_SRC = SCRIPT_DIR / ".aiderignore"

# print(SCRIPT_DIR)
# print(DEFAULT_BENCHMARK_DIR)
# print(DEFAULT_OUTPUT_DIR)
# print(DUCKDB_REPO)
# print(AIDERIGNORE_SRC)

def parse_arguments():
    """
    Parse command line arguments for the benchmark script.
    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run benchmark pipeline")
    parser.add_argument("--m", required=True, help="Model to use")
    parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
    parser.add_argument("--dir", type=Path, default=DEFAULT_BENCHMARK_DIR, help="Path to benchmark directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="Where to move organized results")
    return parser.parse_args()

def get_files_from_json(json_path, filter_string):
    if filter_string not in ["modified_files", "modified_test_files"]:
        raise ValueError("filter_string must be 'modified_files' or 'modified_test_files'")
    # Load the JSON file
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Return the list of files based on the filter_string
    return data.get(filter_string, [])

def run(cmd, cwd=None, check=True, log_path=None, verbose=True):
    print(f"Running command: {cmd}")
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    returncode = process.returncode
    if log_path:
        with open(log_path, "a") as f:
            f.write(f"\n cwd: {cwd}")
            f.write(f"\n$ {cmd}\n\n")
            f.write("=== STDOUT ===\n")
            f.write(stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(stderr)
            f.write(f"\n\n=== EXIT CODE: {returncode} ===\n")
    if check and returncode != 0:
        print(f"[Error] Command failed: {cmd}")
        return None
    class Result:
        def __init__(self, stdout, stderr, returncode):
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode
    return Result(stdout, stderr, returncode)

def reset_repo(repo_path, log_path=None):
    run("git reset --hard", cwd=repo_path, log_path=log_path)
    run("git clean -fd", cwd=repo_path, log_path=log_path)
    run("make clean", cwd=repo_path, log_path=log_path)

def run_aider(model, prompt_path, modified_files, problem_dir, attempt_num, log_path=None):
    # convert modified_files to absolute paths within the repo
    repo_files = [str(DUCKDB_REPO / file) for file in modified_files]

    # copy aiderignore to duckdb repo
    aiderignore_dest = DUCKDB_REPO / ".aiderignore"
    shutil.copy(AIDERIGNORE_SRC, aiderignore_dest)

    # build the aider command
    aider_cmd = f"aider --model {model} --yes --no-gitignore -f {prompt_path} {' '.join(repo_files)}"
    print(f"Running Aider command: {aider_cmd}")
    print("Running Aider attempt: ", attempt_num)
    result = run(aider_cmd, cwd=DUCKDB_REPO, check=False)

    print(result)

def main():
    args = parse_arguments()
    benchmark_dir = args.dir.resolve()
    logs_output_dir = args.out.resolve()
    model = args.m
    k = args.k

    for folder in sorted(benchmark_dir.iterdir(), key=lambda x: int(x.name)):
        if not folder.is_dir():
            print(f"Skipping {folder} as it is not a directory")
            continue
        
        print(f"🔍Processing {folder.name}...")

        prompt_path = folder / f"{folder.name}.prompt"
        json_path = folder / f"{folder.name}.json"
        test_patch = folder / "test.patch"

        print(f"📄 Prompt: {prompt_path}")
        print(f"📄 JSON: {json_path}")
        print(f"📄 Test Patch: {test_patch}")

        if not prompt_path.exists() or not json_path.exists() or not test_patch.exists():
            print(f"⚠️ Missing required files in {folder.name}, skipping")
            continue

        with open(json_path) as f:
            base_commit = json.load(f)["base_commit"]

        modified_code_files = get_files_from_json(json_path, "modified_files")
        modified_test_files = get_files_from_json(json_path, "modified_test_files")
        print(f"Modified code files: {modified_code_files}")
        print(f"Modified test files: {modified_test_files}")

        reset_repo(DUCKDB_REPO)
        run(f"git checkout {base_commit}", cwd=DUCKDB_REPO)

        print("🔧 Generating and testing model")
        for i in range(1, k + 1):
            # reset repo to base commit
            reset_repo(DUCKDB_REPO)
            run(f"git checkout {base_commit}", cwd=DUCKDB_REPO)

            # apply test.patch
            run(f"git apply {test_patch}", cwd=DUCKDB_REPO)

            print(f"Attempt {i}/{k} for {folder.name}")

            # run aider to generate code fix
            aider_result = run_aider(
                model=model,
                prompt_path=prompt_path,
                modified_files=modified_code_files,
                problem_dir=folder,
                attempt_num=i,
                log_path=folder / f"aider_attempt_{i}.log"
            )

        # Generate code fixes using aider k times, each time generating a fix, then running the tests

        break # for debugging
        

    # Ensure the problem directory exists
    

    print("📦 Archiving generated patches and results...")

    print("🧹 Cleaning up patches...")

if __name__ == "__main__":
    main()