import os
import json

def is_easy_pr(pr_data):
    patch = pr_data.get("patch", "")
    test_patch = pr_data.get("test_patch", "")
    problem_statement = pr_data.get("problem_statement", "")

    # Criteria
    patch_lines = patch.count('\n')
    test_lines = test_patch.count('\n')
    changed_files = patch.count('diff --git')

    # Heuristics
    if patch_lines > 40:   # You can tweak this threshold
        return False
    if changed_files > 1:
        return False
    if any(keyword in patch for keyword in ['if (', 'for (', 'while (']):
        return False
    if len(problem_statement) > 1000:
        return False

    return True

# Path to your extracted folders
base_dir = "/home/leon/Documents/university/honours/prs"

# Sort PR folders numerically
pr_folders = sorted(
    (f for f in os.listdir(base_dir) if f.isdigit()), 
    key=lambda x: int(x)
)

for pr_folder in pr_folders:
    pr_path = os.path.join(base_dir, pr_folder, f"{pr_folder}.json")
    if not os.path.isfile(pr_path):
        continue
    with open(pr_path) as f:
        pr_data = json.load(f)
    if is_easy_pr(pr_data):
        print(f"Found easy PR: {pr_folder}")
