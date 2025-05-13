import shutil
from pathlib import Path
from datetime import datetime


def archive_ai_patches(model: str, benchmark_dir: Path, archive_root: Path):
    patches_root = archive_root / "patches"
    for problem_path in benchmark_dir.iterdir():
        if not problem_path.is_dir():
            continue
        ai_patch_dir = problem_path / "ai_patches"
        if ai_patch_dir.exists():
            problem_dest = patches_root / problem_path.name
            problem_dest.mkdir(parents=True, exist_ok=True)
            for patch_file in ai_patch_dir.glob("*.patch"):
                shutil.copy2(patch_file, problem_dest / patch_file.name)
            print(f"📄 Archived patches for {problem_path.name} to {problem_dest}")


def archive_results(model: str, benchmark_dir: Path, results_root: Path):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_root = results_root / timestamp / model
    archive_root.mkdir(parents=True, exist_ok=True)

    # Move CSV to the model root
    csv_name = f"ai_patch_test_results_{model}.csv"
    csv_path = Path(__file__).resolve().parent / csv_name
    if csv_path.exists():
        shutil.move(str(csv_path), archive_root / csv_name)
        print(f"📄 Moved {csv_name} to {archive_root}")

    # Move logs to logs/<problem>
    logs_root = archive_root / "logs"
    for problem_path in benchmark_dir.iterdir():
        if not problem_path.is_dir():
            continue
        logs_dir = problem_path / "logs"
        if logs_dir.exists():
            problem_dest = logs_root / problem_path.name
            problem_dest.mkdir(parents=True, exist_ok=True)
            for log_file in logs_dir.glob("*.log"):
                shutil.move(str(log_file), problem_dest / log_file.name)
            shutil.rmtree(logs_dir)
            print(f"📁 Moved logs for {problem_path.name} to {problem_dest}")

    # Archive patches to patches/<problem>
    archive_ai_patches(model, benchmark_dir, archive_root)

    print(f"\n✅ Archived results to: {archive_root}")
