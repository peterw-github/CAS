import json
import os

# --- CONFIGURATION ---
INPUT_FILENAME = 'input.json'
OUTPUT_FILENAME = 'output.md'


def convert_json_to_md():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILENAME)
    output_path = os.path.join(script_dir, OUTPUT_FILENAME)

    print(f"Reading from: {INPUT_FILENAME}")

    try:
        # 1. Load the JSON data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Locate the list of chunks (messages)
        chunks = data.get('chunkedPrompt', {}).get('chunks', [])

        # 3. Open the output file
        with open(output_path, 'w', encoding='utf-8') as md:

            # --- START TAG (with backticks) ---
            # Writes `<file name="output.md">`
            md.write(f'`<file name="{OUTPUT_FILENAME}">`\n\n')

            # (Removed the empty ### header here)

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

        print(f"SUCCESS! Created '{OUTPUT_FILENAME}' (Clean version).")

    except FileNotFoundError:
        print(f"ERROR: Could not find '{INPUT_FILENAME}'. Make sure it is in the same folder.")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    convert_json_to_md()