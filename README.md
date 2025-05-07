# honours

## Repositories

- duckdb/duckdb

## Docker

- To run the benchmark, run it using an Amazon Linux 2023 Docker Image
- Once setup, run these commands:

```bash
dnf update -y
dnf groupinstall "Development Tools" -y
dnf install gcc cmake git wget -y

```

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

## Manually Verify Individual PRs

1. Git Clone `ducksdb`
2. Choose a PR/issue
    - Create the `.prompt`, `fix.patch`, and `test.patch` files by running `process_single_pr.py <path_to_pr_folder> <path_to_duckdb_repo>`
3. `git checkout` to the PRs commit
4. Compile the code using `make -j$(nproc)` and run tests to make sure no tests fail (if time matters, only run the test that is modified in the patch)
    - May need to change `cmake` or `gcc`
5. Apply the `test.patch`, recompile if necessary and run the modified test
    - This time the test should fail
    - If time is not a concern, run all test suites to ensure there is no other bug in the codebase
6. Apply the `fix.patch`, recompile then run the modified test
    - This time the test should pass
    - If time is not a concern, run all test suites to ensure there is no other bug in the codebase

If the tests behave as expected after step 6, the PR has been verified and is ready for the LLM to test a fix


## Manually Verified PRs

- 5805


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


