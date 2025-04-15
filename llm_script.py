#!/usr/bin/env python3

import argparse
import sys
import llm

def main(prompt_path, output_path, model_id):
    # Load the prompt text
    try:
        with open(prompt_path, 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file '{prompt_path}' not found.")
        sys.exit(1)

    # Load the model
    try:
        model = llm.get_model(model_id)
    except Exception as e:
        print(f"Error loading model '{model_id}': {e}")
        sys.exit(1)

    # Generate the response
    response = model.prompt(prompt)

    # Save the output
    with open(output_path, 'w') as f:
        f.write(response.text())

    print(f"✅ Output written to '{output_path}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a prompt through an LLM and save the result.')
    parser.add_argument('prompt_file', help='Path to input .prompt file')
    parser.add_argument('--output', '-o', help='Path to output file (default: .out.prompt)', default=None)
    parser.add_argument('--model', '-m', help='LLM model ID (as configured in `llm`)', default='gpt-4o')
    args = parser.parse_args()

    if not args.output:
        args.output = args.prompt_file.replace('.prompt', '.out.prompt')

    main(args.prompt_file, args.output, args.model)
