from generate_patches import generate_patches
from test_patches import test_all
from archive_logs import archive_results
import argparse, os, shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_DIR = (SCRIPT_DIR.parent.parent / "benchmark_problems")
DEFAULT_OUTPUT_DIR = (SCRIPT_DIR.parent.parent / "archive").resolve()

# def parse_arguments():
#     parser = argparse.ArgumentParser(description="Run benchmark pipeline")
#     parser.add_argument("--m", required=True, help="Model to use")
#     parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
#     parser.add_argument("--dir", default="../../benchmark_problems", help="Path to benchmark directory")
#     parser.add_argument("--out", default="./archive", help="Where to move organized results")

#     return parser.parse_args()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run benchmark pipeline")
    parser.add_argument("--m", required=True, help="Model to use")
    parser.add_argument("--k", type=int, required=True, help="Number of completions per problem")
    parser.add_argument("--dir", type=Path, default=DEFAULT_BENCHMARK_DIR, help="Path to benchmark directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="Where to move organized results")
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
    benchmark_dir = args.dir.resolve()
    logs_output_dir = args.out.resolve()

    print("🔧 Generating patches...")
    generate_patches(args.m, args.k, benchmark_dir)

    print("🧪 Testing patches...")
    test_all(args.m)

    print("📦 Archiving generated patches and results...")
    archive_results(args.m, benchmark_dir, logs_output_dir)

    print("🧹 Cleaning up patches...")
    cleanup_patches(benchmark_dir)



if __name__ == "__main__":
    main()