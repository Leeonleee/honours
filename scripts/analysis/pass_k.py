"""
Usage: python3 pass_k.py --dir <directory> --k <k_value> [--detailed]

"""
import csv
import math
import sys
import os
import argparse

def comb(n, k):
    if k > n:
        return 0
    return math.comb(n, k)

def pass_at_k(n, c, k):
    if c == 0 or k > n:
        return 0.0
    return 1.0 - comb(n - c, k) / comb(n, k)

def compute_pass_at_k_for_file(file_path, k, detailed=False):
    scores = []
    problems = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        total_generations_list = [int(row["total_generations"]) for row in reader]

    max_n = max(total_generations_list)
    if k > max_n:
        if detailed:
            print(f"Skipping {os.path.basename(file_path)}: k = {k} > max total_generations = {max_n}")
        return None

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            problem_id = row["problem"]
            n = int(row["total_generations"])
            c = int(row["passed_tests"])

            if n >= k:
                score = pass_at_k(n, c, k)
                scores.append(score)
                problems.append((problem_id, score))
            else:
                if detailed:
                    print(f"Problem {problem_id} in {os.path.basename(file_path)}: skipped (n={n} < k={k})")

    if not scores:
        if detailed:
            print(f"No valid problems in {os.path.basename(file_path)}\n")
        return None

    file_avg = sum(scores) / len(scores)

    if detailed:
        print(f"\nFile: {os.path.basename(file_path)}")
        for pid, score in problems:
            print(f"  Problem {pid}: pass@{k} = {score:.4f}")
        print(f"Average pass@{k} for {os.path.basename(file_path)}: {file_avg:.4f}\n")
    else:
        print(f"{os.path.basename(file_path)}: {file_avg:.4f}")

    return file_avg

def main():
    parser = argparse.ArgumentParser(description="Compute pass@k for all CSV files in a directory.")
    parser.add_argument('--dir', required=True, help="Directory containing CSV files")
    parser.add_argument('--k', type=int, required=True, help="Value of k for pass@k")
    parser.add_argument('--detailed', action='store_true', help="Print detailed per-problem output")

    args = parser.parse_args()

    for filename in sorted(os.listdir(args.dir)):
        if filename.endswith(".csv"):
            filepath = os.path.join(args.dir, filename)
            compute_pass_at_k_for_file(filepath, args.k, args.detailed)

if __name__ == "__main__":
    main()