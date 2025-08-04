
import os
import sys

# Usage: python cleanup_old_format.py path/to/problem_folders

if len(sys.argv) != 2:
    print("Usage: python cleanup_old_format.py <parent_folder>")
    sys.exit(1)

parent_folder = sys.argv[1]

for subfolder in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, subfolder)
    if not os.path.isdir(folder_path):
        continue

    for filename in os.listdir(folder_path):
        if filename.endswith(".prompt") or filename.endswith(".patch"):
            file_path = os.path.join(folder_path, filename)
            os.remove(file_path)
            print(f"🗑️  Deleted {file_path}")