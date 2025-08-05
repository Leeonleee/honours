
import csv
import math
import sys

def comb(n, k):
    if k > n:
        return 0
    return math.comb(n, k)

def pass_at_k(n, c, k):
    if c == 0 or k > n:
        return 0.0
    return 1.0 - comb(n - c, k) / comb(n, k)

def compute_pass_at_k_from_csv(file_path, k):
    # check for maximum total_generations
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        total_generations_list = [int(row["total_generations"]) for row in reader]
    
    max_n = max(total_generations_list)
    if k > max_n:
        print(f"Error: k = {k} exceeds the maximum total_generations = {max_n}")
        sys.exit(1)

    total_score = 0.0
    count = 0

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            problem_id = row["problem"]
            n = int(row["total_generations"])
            c = int(row["passed_tests"])

            if n >= k:
                score = pass_at_k(n, c, k)
                print(f"Problem {problem_id}: pass@{k} = {score:.4f}")
                total_score += score
                count += 1
            else:
                print(f"Problem {problem_id}: skipped (n={n} < k={k})")

    if count > 0:
        avg = total_score / count
        print(f"\nAverage pass@{k} = {avg:.4f} over {count} problems")
    else:
        print(f"No problems with n ≥ k={k}, cannot compute pass@{k}.")

compute_pass_at_k_from_csv("useful_results/2025-08-01_15:06:51_openai_o3_k3.csv", k=3)  