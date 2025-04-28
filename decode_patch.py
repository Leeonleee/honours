import json

with open('prs/17180/17180.json') as f:
    task = json.load(f)

patch = task["patch"].replace('\\n', '\n')  # IMPORTANT: decode \n to real newlines

with open('fix.patch', 'w') as f:
    f.write(patch)
