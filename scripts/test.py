import os

def get_test_paths_from_patch(patch_path):
    test_paths = []
    with open(patch_path) as f:
        for line in f:
            if line.startswith("+++ b/"):
                file_path = line[len("+++ b/"):].strip()
                # Heuristic: include anything with 'test' in the filename or directory
                if "test" in os.path.basename(file_path).lower() or "/test" in file_path.lower():
                    test_paths.append(file_path)
    return test_paths

def main():
    patch_path = "/root/Documents/university/honours/test_in_progress_prs/4810/test.patch"
    print(get_test_paths_from_patch(patch_path))

if __name__ == "__main__":
    main()
