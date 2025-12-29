import os
import glob

def add_xml_tags_to_markdown():
    # 1. Find all markdown files
    md_files = glob.glob("*.md")

    if not md_files:
        print("No markdown files found.")
        return

    print(f"Found {len(md_files)} markdown files. Processing...")

    count = 0

    for filename in md_files:
        try:
            # 2. Read the original content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # 3. Safety Check: Check if it already starts with a backtick and tag
            if content.lstrip().startswith('`<file name="'):
                print(f"Skipping: {filename} (Already tagged)")
                continue

            # 4. Create the tags with EXTRA NEWLINES (\n\n)
            # This creates a blank line between the tag and the content
            start_tag = f'`<file name="{filename}">`\n\n'
            end_tag = f'\n\n`</file>`'

            # 5. Combine them
            new_content = start_tag + content + end_tag

            # 6. Overwrite the file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Tagged: {filename}")
            count += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("-" * 30)
    print(f"Process complete. Tagged {count} files.")

if __name__ == "__main__":
    add_xml_tags_to_markdown()