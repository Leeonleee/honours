# Scripts

This folder contains helpful scripts

## create_prompt.py

Creates a complete .prompt file given a .jsonl file

### Usage

```
python create_prompt.py instance.json path_to_repo output.txt
```

## tasks_to_json.py

Given a `task-instances.jsonl` file (from SWE-bench script output), create individual folders for each PR containing a `<pull_number>.json` file

### Usage

```
python tasks_to_json.py input.jsonl output_directory
```