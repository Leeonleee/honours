from generate_patches import generate_patches
import argparse, os, shutil

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run benchmark pipeline")
    parser.add_argument("--model", required=True, help="Model to use")
    parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
    parser.add_argument("--dir", default="../../benchmark_problems", help="Path to benchmark directory")
    return parser.parse_args()

def cleanup_patches(benchmark_dir):
    for folder_name in os.listdir(benchmark_dir):
        patch_dir = os.path.join(benchmark_dir, folder_name, "ai_patches")
        if os.path.isdir(patch_dir):
            shutil.rmtree(patch_dir)
            print(f"🧹 Deleted {patch_dir}")

def main():
    args = parse_arguments()

    print("🔧 Generating Patches...")
    # generate_patches(args.model, args.k, args.dir)

    print("🧹 Cleaning up patches...")
    cleanup_patches(args.dir)



if __name__ == "__main__":
    main()