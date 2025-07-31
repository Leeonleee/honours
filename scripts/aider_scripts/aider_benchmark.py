"""
Usage: python aider_benchmark.py --m <model_name>A --k <num_completions>
"""

# TODO: add logging for built/test failures to try identify the cause

import argparse, shutil
from pathlib import Path
import subprocess
from datetime import datetime
import json
import csv
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import time

debug = True

# Constants
HONOURS_DIR = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_DIR = (SCRIPT_DIR.parent.parent / "benchmark_problems").resolve()
DEFAULT_OUTPUT_DIR = (SCRIPT_DIR.parent.parent / "archive").resolve()

load_dotenv(dotenv_path=HONOURS_DIR / ".env")

if debug:
    DEFAULT_BENCHMARK_DIR = (SCRIPT_DIR.parent.parent / "benchmark_problems_debug").resolve()

def send_email_notification(subject, body, sender_email, app_password, recipient_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run benchmark pipeline")
    parser.add_argument("--m", required=True, help="Model to use")
    parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
    parser.add_argument("--dir", type=str, default=DEFAULT_BENCHMARK_DIR, help="Path to benchmark directory")
    parser.add_argument("--out", type=str, default=DEFAULT_OUTPUT_DIR, help="Where to move organized results")
    return parser.parse_args()

def run(cmd, cwd=None, env=None, capture_output=True, check=True, log_file=None):
    """
    Run a shell command and log the output

    :param cmd: List[str] or str - command and arguments
    :param cwd: working directory
    :param env: environment variables
    :param capture_output: bool - whether to capture output
    :param check: bool - whether to raise an error on non-zero exit code
    :param log_file: file to log output
    :return: CompletedProcess - result of the command execution
    """
    # Convert command to list if it's a string
    if isinstance(cmd, str):
        shell = True
        printable_cmd = cmd
    else:
        shell = False
        printable_cmd = " ".join(cmd)
    # print(f"Running command: {printable_cmd} in {cwd if cwd else 'current directory'}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] Running command: {printable_cmd}\n"

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            shell=shell,
            text=True,
            capture_output=capture_output,
            check=check,
        )
    except subprocess.CalledProcessError as e:
        result = e

    # Prepare output
    stdout = result.stdout if hasattr(result, 'stdout') else ""
    stderr = result.stderr if hasattr(result, 'stderr') else ""
    return_code = result.returncode

    footer = f"Exit code: {return_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}\n"

    if log_file:
        with open(log_file, 'a') as f:
            f.write(header)
            f.write(footer)
    if check and return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd, output=stdout, stderr=stderr)
    return result
        
def main():
    args = parse_arguments()
    start_time = time.time()
    print(f"Model: {args.m}, Completions: {args.k}, Benchmark Directory: {args.dir}, Output Directory: {args.out}")

    # Logging setup
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = Path(f"logs/{timestamp}.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Tracking results
    results = {}
    # main loop
    problems = sorted(
        [p for p in Path(args.dir).iterdir() if p.is_dir()],
        key=lambda p: int(p.name)
    )
    for problem in problems:
        print(f"Processing problem: {problem.name}")

        results[problem.name] = {
            "problem": problem.name,
            "total_generations": 0,
            "successful_builds": 0,
            "failed_builds": 0,
            "passed_tests": 0,
            "failed_tests": 0,
        }

        # Parse json file to get problem details
        problem_json = problem / f"{problem.name}.json"
        if not problem_json.exists():
            print(f"Problem JSON file not found for {problem.name}, skipping.")
            continue
        # Load problem details
        with open(problem_json, 'r') as f:
            problem_data = json.load(f)
        
        base_commit = problem_data.get("base_commit")
        modified_files = problem_data.get("modified_files", [])
        modified_test_files = problem_data.get("modified_test_files", [])

        for i in range(args.k):
            print(f"Generating completion {i+1} for {problem.name} using model {args.m}")
            
            # cleanup repo for fresh start
            run(
                ["bash", "scripts/aider_scripts/clean_repo.sh", str(HONOURS_DIR)],
                log_file=log_path
            )
            # checkout to correct commit
            run(
                ["bash", "scripts/aider_scripts/checkout.sh", str(HONOURS_DIR), base_commit],
                log_file=log_path
            )

            # apply test patches
            test_patch_path = problem / "test.patch"
            run(
                ["bash", "scripts/aider_scripts/apply_test_patch.sh", str(HONOURS_DIR), str(test_patch_path)],
                log_file=log_path
            )
            # generate fix

            res = run(
                ["bash", "scripts/aider_scripts/generate_fix.sh", str(HONOURS_DIR), str(problem), str(problem.name), str(args.m)],
                log_file=log_path,
                check=False
            )

            if res.returncode != 0:
                print(f"Completion generation failed for {problem.name} completion {i+1}, skipping tests.")
                results[problem.name]["total_generations"] += 1
                continue
            print(f"Completion generated for {problem.name} completion {i+1}")
            results[problem.name]["total_generations"] += 1

            # build

            res = run (
                ["bash", "scripts/aider_scripts/build.sh", str(HONOURS_DIR)],
                log_file=log_path,
                check=False
            )

            if res.returncode != 0:
                print(f"Build failed for {problem.name} completion {i+1}, skipping tests.")
                results[problem.name]["failed_builds"] += 1
                continue
            print(f"Build successful for {problem.name} completion {i+1}")
            results[problem.name]["successful_builds"] += 1

            # test
            test_args = [str(HONOURS_DIR)] + modified_test_files
            res = run(
                ["bash", "scripts/aider_scripts/run_tests.sh", str(HONOURS_DIR)] + modified_test_files,
                log_file=log_path,
                check=False
            )

            tests_passed = (res.returncode == 0)
            if tests_passed:
                print(f"Tests passed for {problem.name} completion {i+1}")
                results[problem.name]["passed_tests"] += 1
            else:
                print(f"Tests failed for {problem.name} completion {i+1}")
                results[problem.name]["failed_tests"] += 1

            # store results
    print(results)
    # archive results

    csv_filename = f"{timestamp}_{args.m}.csv"
    csv_path = Path("results") / csv_filename
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["problem", "total_generations", "successful_builds", "failed_builds", "passed_tests", "failed_tests"]
        )
        writer.writeheader()
        for row in results.values():
            writer.writerow(row)
    print(f"Results saved to {csv_path}")

    # cleanup everything


    # Send email notification
    elapsed_seconds = int(time.time() - start_time)
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_str = f"{hours}h {minutes}m {seconds}s"

    body = (
        f"Model: {args.m}\n"
        f"Results saved to: {csv_path.resolve()}\n"
        f"Total runtime: {elapsed_str}\n"
        f"Results:\n"
        + "\n".join(
            f"{problem}: {data['total_generations']} generations, "
            f"{data['successful_builds']} successful builds, "
            f"{data['failed_builds']} failed builds, "
            f"{data['passed_tests']} passed tests, "
            f"{data['failed_tests']} failed tests"
            for problem, data in results.items()
        )
    )


    send_email_notification(
        subject="✅ Benchmark Completed!",
        body=body,
        sender_email=os.getenv("EMAIL_USER"),
        app_password=os.getenv("EMAIL_PASS"),
        recipient_email=os.getenv("EMAIL_USER")
    )
if __name__ == "__main__":
    main()