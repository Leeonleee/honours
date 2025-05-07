import os
import json
import re
import subprocess
import sys

# Usage: python process_single_pr.py path/to/pr_folder path/to/repo

"""
This function will create the .prompt, fix.patch, and test.patch for each PR
"""

pr_folder = sys.argv[1]
repo_path = sys.argv[2]
template_path = "../template.prompt"

# Extract pull number
pull_number = os.path.basename(pr_folder)
json_path = os.path.join(pr_folder, f"{pull_number}.json")

if not os.path.exists(json_path):
    print(f"ERROR: No JSON file found for PR {pull_number}")
    sys.exit(1)

with open(json_path) as f:
    instance = json.load(f)

base_commit = instance.get("base_commit")
if not base_commit:
    print(f"ERROR: No base_commit found in {pull_number}")
    sys.exit(1)

def git_checkout(commit_hash):
    subprocess.run(["git", "checkout", commit_hash], cwd=repo_path, check=True)

def git_checkout_back():
    subprocess.run(["git", "checkout", "-"], cwd=repo_path, check=True)

def load_file_with_line_numbers(filepath):
    if not os.path.exists(filepath):
        print(f"WARNING: File {filepath} not found — skipping.")
        return None
    with open(filepath, 'r') as f:
        lines = f.readlines()
    numbered = [f"{idx}: {line.rstrip()}" for idx, line in enumerate(lines, 1)]
    return "\n".join(numbered)

def build_prompt(instance):
    with open(template_path) as f:
        template = f.read()

    problem_statement = instance["problem_statement"]
    patch = instance["patch"]

    filepaths = []
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            match = re.match(r"diff --git a/(.*?) b/", line)
            if match:
                filepaths.append(match.group(1))

    readme_path = os.path.join(repo_path, "README.md")
    readme_content = load_file_with_line_numbers(readme_path)
    if not readme_content:
        readme_content = ""

    code_blocks = []
    for filepath in filepaths:
        abs_path = os.path.join(repo_path, filepath)
        file_content = load_file_with_line_numbers(abs_path)
        if file_content:
            code_blocks.append(f"[start of {filepath}]\n{file_content}\n[end of {filepath}]")
    full_code = f"[start of README.md]\n{readme_content}\n[end of README.md]\n" + "\n".join(code_blocks)

    filled_prompt = template.replace("<issue>\n</issue>", f"<issue>\n{problem_statement}\n</issue>")
    filled_prompt = filled_prompt.replace(
        "<code>\n[start of README.md]\n[end of README.md]\n</code>",
        f"<code>\n{full_code}\n</code>"
    )

    return filled_prompt

print(f"Processing {pull_number}...")

try:
    git_checkout(base_commit)

    # Save fix.patch
    if "patch" in instance:
        fix_patch_path = os.path.join(pr_folder, "fix.patch")
        with open(fix_patch_path, 'w') as f:
            f.write(instance["patch"].replace('\\n', '\n'))

    # Save test.patch
    if "test_patch" in instance:
        test_patch_path = os.path.join(pr_folder, "test.patch")
        with open(test_patch_path, 'w') as f:
            f.write(instance["test_patch"].replace('\\n', '\n'))

    # Save prompt
    prompt_text = build_prompt(instance)
    prompt_path = os.path.join(pr_folder, f"{pull_number}.prompt")
    with open(prompt_path, 'w') as f:
        f.write(prompt_text)

except subprocess.CalledProcessError as e:
    print(f"ERROR: Git checkout failed: {e}")
finally:
    git_checkout_back()

print(f"Finished processing {pull_number}.")
