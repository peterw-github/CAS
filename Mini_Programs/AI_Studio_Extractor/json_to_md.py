import json
import os

def convert_single_file(input_path, output_path, filename_only):
    """
    Reads a single JSON file and writes the converted MD file.
    """
    print(f"Processing: {os.path.basename(input_path)}...")

    try:
        # 1. Load the JSON data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Locate the list of chunks (messages)
        # Note: Keeps your original safe get() logic in case structure varies
        chunks = data.get('chunkedPrompt', {}).get('chunks', [])

        # 3. Open the output file
        with open(output_path, 'w', encoding='utf-8') as md:

            # --- START TAG (with backticks) ---
            # Uses the dynamic filename for the XML tag
            md.write(f'`<file name="{filename_only}">`\n\n')

            for chunk in chunks:
                role = chunk.get('role', 'unknown')
                text = chunk.get('text', '')
                is_thought = chunk.get('isThought', False)

                # Skip "Thinking" blocks or empty text
                if is_thought or not text.strip():
                    continue

                # Map roles
                if role == 'user':
                    speaker_header = "### **Speaker_1:**"
                elif role == 'model':
                    speaker_header = "### **Speaker_2:**"
                else:
                    speaker_header = f"### **{role}:**"

                # Write to file
                md.write(f"{speaker_header}\n\n{text}\n\n")

            # --- END TAG (with backticks) ---
            md.write("`</file>`")

        print(f" -> Created: {filename_only}")

    except Exception as e:
        print(f" -> ERROR converting {filename_only}: {e}")


def process_all_json_files():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get a list of all files in the directory
    all_files = os.listdir(script_dir)

    # Filter for .json files
    json_files = [f for f in all_files if f.lower().endswith('.json')]

    if not json_files:
        print("No JSON files found in the script directory.")
        return

    print(f"Found {len(json_files)} JSON file(s). Starting conversion...\n")

    for json_file in json_files:
        # construct full input path
        input_path = os.path.join(script_dir, json_file)

        # construct output filename (replace .json with .md)
        # os.path.splitext handles filenames with multiple dots correctly
        base_name = os.path.splitext(json_file)[0]
        output_filename = f"{base_name}.md"
        output_path = os.path.join(script_dir, output_filename)

        # Run the conversion for this specific file
        convert_single_file(input_path, output_path, output_filename)

    print("\nBatch conversion complete.")


if __name__ == "__main__":
    process_all_json_files()