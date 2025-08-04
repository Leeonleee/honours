import argparse, os
import llm


def get_prompt(folder_path, folder_name):
    prompt_path = os.path.join(folder_path, f"{folder_name}.prompt")
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    with open(prompt_path, "r") as f:
        return f.read()
 
def generate_outputs(model_name, prompt, k, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    model = llm.get_model(model_name)
    for i in range(k):
        response = str(model.prompt(prompt))
        output_path = os.path.join(output_dir, f"ai_fix{i + 1}.patch")
        with open(output_path, "w") as f:
            f.write(response)

def generate_patches(model_name, k, benchmark_dir):
    for folder_name in sorted(os.listdir(benchmark_dir)):
        folder_path = os.path.join(benchmark_dir, folder_name)
        if not os.path.isdir(folder_path):
            print(f"{folder_path} is not a directory, skipping")
            continue
        try:
            prompt = get_prompt(folder_path, folder_name)
            output_dir = os.path.join(folder_path, "ai_patches")
            generate_outputs(model_name, prompt, k, output_dir)
            print(f"✅ Generated {k} patches for {folder_name}")
        except Exception as e:
            print(f"⚠️ Skipping {folder_name}: {e}")


