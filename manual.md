# Manual Steps
Once you've identified an issue that has:
- An associated PR
- Reproducible bug
- Tests for testing the bug
# Process:
1. Identify the commit SHA of the fix + test
2. Identify the commit SHA of the pre-fix commit (parent commit)

Now we want to test the pre-fix code on the fixed test:

3. Make sure you're on the pre-fix commit using `git checkout <pre_fix_commit>`
<!-- 4. Run this command `git checkout <fix_commit> -- path/to/test_file.cc`
    - This pulls the fixed test file to your current working tree -->

4. Generate the patch file for the test file `git diff <fix_commit>^ <fix_commit> -- path/to/test_file.cc > test.patch`
5. Apply the patch to the test file `git apply test.patch`
6. Compile the program
7. Compile the tests using `make <test_name>`
8. Run the tests using `./<test_name>`. They should fail

9. Generate the patch for the code fix `git diff <fix_commit>^ <fix_commit> -- path/to/fixed/code/files > fix.patch`
10. Apply the patch to the test file `git apply fix.patch`
11. Compile the program again
12. Run the tests again. They should pass



bash script.sh
  abcdef123456 \
  db/version_builder_test.cc \
  db/version_builder.cc db/version_set.cc


bash script.sh e28251ca729ed42a5a8d7181b703b2e059506573 db/version_builder_test.cc db/version_builder.cc

bash script.sh <FIX_COMMIT> <TEST_FILE> <CODE_FILE1> <CODE_FILE2> ...
