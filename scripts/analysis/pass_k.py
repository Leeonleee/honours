# from math import comb

# def pass_at_k(n: int, c: int, k: int) -> float:
#     if k > n:
#         raise ValueError(f"k={k} cannot be greater than n={n}")
#     if c == 0:
#         return 0.0
#     if n == c:
#         return 1.0
    

#     return 1.0 - comb(n - c, k) / comb(n, k)


# print(pass_at_k(n=10, c=3, k=10)) 


import csv
import math

def comb(n, k):
    if k > n:
        return 0
    return math.comb(n, k)

def pass_at_k(n, c, k):
    if c == 0 or k > n:
        return 0.0
    return 1.0 - comb(n - c, k) / comb(n, k)

def main(csv_path, k):
    total_pass_at_k = 0.0
    count = 0

    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = int(row["TotalPatches"])
            c = int(row["PassedTest"])

            if n >= k:
                score = pass_at_k(n, c, k)
                print(f"Problem {row['Problem']}: pass@{k} = {score:.4f}")
                total_pass_at_k += score
                count += 1
            else:
                print(f"Problem {row['Problem']}: skipped (n={n} < k={k})")

    if count == 0:
        print("No valid problems to compute pass@k")
    else:
        avg = total_pass_at_k / count
        print(f"\nAverage pass@{k}: {avg:.4f} over {count} problems")

if __name__ == "__main__":
    csv_path = "/root/Documents/university/honours/scripts/benchmark/ai_patch_test_results_o3.csv"
    k = 2
    main(csv_path, k)
