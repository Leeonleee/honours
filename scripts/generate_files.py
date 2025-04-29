import os
import json
import re
import subprocess

# Path to prs folder
prs_dir = "../prs"
# Path to your cloned duckdb repo
repo_path = "../duckdb"

def git_checkout(commit_hash):
    """Temporarily checkout the repo to a given commit."""
    subprocess.run(["git", "checkout", commit_hash], cwd=repo_path, check=True)

def git_checkout_back():
    """Return to the original branch."""
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
    problem_statement = instance["problem_statement"]
    patch = instance["patch"]

    # Extract modified filepaths
    filepaths = []
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            match = re.match(r"diff --git a/(.*?) b/", line)
            if match:
                filepaths.append(match.group(1))

    code_blocks = []

    # Add README.md
    readme_path = os.path.join(repo_path, "README.md")
    readme_content = load_file_with_line_numbers(readme_path)
    if readme_content:
        code_blocks.append(f"[start of README.md]\n{readme_content}\n[end of README.md]")

    # Add each modified file
    for filepath in filepaths:
        abs_path = os.path.join(repo_path, filepath)
        file_content = load_file_with_line_numbers(abs_path)
        if file_content:
            code_blocks.append(f"[start of {filepath}]\n{file_content}\n[end of {filepath}]")

    prompt = f"""You will be provided with a partial code base and an issue statement explaining a problem to resolve.

<issue>
{problem_statement}
</issue>
<code>
{chr(10).join(code_blocks)}
</code>
Here is an example of a patch file. It consists of changes to the code base. It specifies the file names, the line numbers of each change, and the removed and added lines. A single patch file can contain changes to multiple files.
<patch>
--- a/file.py
+++ b/file.py
@@ -1,27 +1,35 @@
def euclidean(a, b):
-    while b:
-        a, b = b, a % b
-    return a
+    if b == 0:
+        return a
+    return euclidean(b, a % b)

def bresenham(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
-    sx = 1 if x0 < x1 else -1
-    sy = 1 if y0 < y1 else -1
-    err = dx - dy
+    x, y = x0, y0
+    sx = -1 if x0 > x1 else 1
+    sy = -1 if y0 > y1 else 1
    
-    while True:
-        points.append((x, y))
-        if x == x1 and y == y1:
-            break
-        e2 = 2 * err
-        if e2 > -dy:
+    if dx > dy:
+        err = dx / 2.0
+        while x != x1:
+            points.append((x, y))
             err -= dy
-            x0 += sx
-        if e2 < dx:
-            err += dx
-            y0 += sy
+            if err < 0:
+               y += sy
+               err += dx
+            x += sx       
+    else:
+        err = dy / 2.0
+        while y != y1:
+            points.append((x, y))
+            err -= dx
+            if err < 0:
+                x += sx
+                err += dy
+            y += sy

+    points.append((x, y))
    return points
</patch>

I need you to solve the provided issue by generating a single patch file that I can apply directly to this repository using git apply.
Please respond with a single patch file in the format shown above.

Respond below:"""
    return prompt

def main():
    for pr_folder in os.listdir(prs_dir):
        pr_path = os.path.join(prs_dir, pr_folder)
        if not os.path.isdir(pr_path):
            continue

        json_path = os.path.join(pr_path, f"{pr_folder}.json")
        if not os.path.exists(json_path):
            print(f"Skipping {pr_folder}: no JSON found")
            continue

        with open(json_path) as f:
            instance = json.load(f)

        base_commit = instance.get("base_commit")
        if not base_commit:
            print(f"Skipping {pr_folder}: no base_commit found")
            continue

        print(f"Processing PR {pr_folder} at commit {base_commit}...")

        try:
            git_checkout(base_commit)

            # Save fix.patch
            if "patch" in instance:
                fix_patch_path = os.path.join(pr_path, "fix.patch")
                with open(fix_patch_path, 'w') as f:
                    f.write(instance["patch"].replace('\\n', '\n'))

            # Save test.patch
            if "test_patch" in instance:
                test_patch_path = os.path.join(pr_path, "test.patch")
                with open(test_patch_path, 'w') as f:
                    f.write(instance["test_patch"].replace('\\n', '\n'))

            # Save prompt
            prompt = build_prompt(instance)
            prompt_path = os.path.join(pr_path, f"{pr_folder}.prompt")
            with open(prompt_path, 'w') as f:
                f.write(prompt)

        except subprocess.CalledProcessError:
            print(f"ERROR: Failed to checkout commit {base_commit} for PR {pr_folder}")
        finally:
            git_checkout_back()

if __name__ == "__main__":
    main()
