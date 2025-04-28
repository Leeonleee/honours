"""
Usage: python save_patch.py instance.json output.txt patch_key
patch_key must be one of: patch, test_patch, problem_statement
"""

import json
import sys

input_json = sys.argv[1]
output_path = sys.argv[2]
patch_key = sys.argv[3]  # Added this: "patch" or "test_patch"

with open(input_json) as f:
    task = json.load(f)

# Read the right field: patch or test_patch
patch_content = task[patch_key].replace('\\n', '\n')

with open(output_path, 'w') as f:
    f.write(patch_content)
