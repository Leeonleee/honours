# honours

## Repositories

- duckdb/duckdb

## Folder Structure

```none
project
│   README.md
│   requirements.txt  
│
└───prs
|   |   duckdb-task-instances.jsonl
│   │
│   └───15277
|   |   └───15277.json
│   └───15287
│   |   └───15287.json
│   └───...
│   
└───scripts
    │   create_prompt.py
    │   decode_patch.py
    |   tasks_to_json.py
    |   README.md
```

- `prs`: contains individual valid PRs, with the following format:

```json
{
    "repo": "repo/repo",
    "pull_number": 12345,
    "instance_id": "repo__repo-12345",
    "issue_numbers": [
        "11111"
    ],
    "base_commit": "commit_sha",
    "patch": "diff file_1 file_2",
    "test_patch": "diff file_1 file_2",
    "problem_statement": "problem statement",
    "hints_text": "\n",
    "created_at": "date"
}
```

## Manually Test Issues

1. Git Clone `ducksdb`
2. Choose an issue
    1. checkout to the base commit `git checkout <base_commit>`
    2. Create the `test.patch` by turning the diff in the `test_patch` field of the JSON into a `test.patch` file
    3. Apply the `test.patch`
    4. Run the test using `build/debug/test/unittest path_to_test/test_name.test`
        - It should fail
    5. Create the `fix.patch

## Easy PRs

A PR is considered easy if:

- the patch line length <= 40
- changes files <= 1
- problem statement length <= 1000
- if it doesn't contain new control flow `if (,` `for (`, `while (`

### List of Easy PRs

- 342
- 4250
- 4654
- 4713
- 4810
- 4973
- 5805
- 7443
- 12942
