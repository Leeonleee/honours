from generate_patches import generate_patches
from test_patches import test_all
import argparse, os, shutil
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run benchmark pipeline")
    parser.add_argument("--m", required=True, help="Model to use")
    parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
    parser.add_argument("--dir", default="../../benchmark_problems", help="Path to benchmark directory")
    return parser.parse_args()

def cleanup_patches(benchmark_dir):
    for folder_path in benchmark_dir.iterdir():
        if not folder_path.is_dir():
            continue
        for subfolder in ["ai_patches", "logs"]:
            target= folder_path / subfolder
            if target.exists() and target.is_dir():
                shutil.rmtree(target)
                print(f"🧹 Deleted {target}")

def main():
    args = parse_arguments()
    benchmark_dir = Path(args.dir).resolve()

    print("🔧 Generating patches...")
    generate_patches(args.m, args.k, args.dir)

    print("🧪 Testing patches...")
    test_all(args.m)

    # print("🧹 Cleaning up patches...")
    # cleanup_patches(args.dir)



if __name__ == "__main__":
    main()