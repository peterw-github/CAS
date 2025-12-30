import os
import re

# Output filename
output_filename = "output.md"
readme_filename = "readme.md"


def merge_markdown_files():
    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for .md files.
    # Excludes:
    # 1. The output file itself (output.md)
    # 2. The readme file (case-insensitive check)
    md_files = [
        f for f in all_files
        if f.endswith('.md')
           and f != output_filename
           and f.lower() != readme_filename
    ]

    # Sort the files alphabetically
    md_files.sort()

    if not md_files:
        print("No Markdown files found in this directory.")
        return

    print(f"--- STARTING MERGE ---")
    print(f"Target: {len(md_files)} files found.")
    print("-" * 30)

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for index, filename in enumerate(md_files):
            print(f"[+] Merging: {filename}")

            try:
                with open(filename, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                    # --- CLEANING STEP ---

                    # 1. Remove opening tag: `<file name="...">` (handles optional backticks)
                    content = re.sub(r'`?<file name=".*?">`?\s*', '', content, count=1)

                    # 2. Remove closing tag: `</file>` (handles optional backticks)
                    content = re.sub(r'\s*`?</file>`?\s*', '', content, count=1)

                    # ---------------------

                    outfile.write(content)

                    # Add separator if it's not the last file
                    if index < len(md_files) - 1:
                        outfile.write("\n\n---\n\n")

            except Exception as e:
                print(f"[!] Error reading {filename}: {e}")

    print("-" * 30)
    print(f"SUCCESS: {len(md_files)} files cleaned and merged into '{output_filename}'.")


if __name__ == "__main__":
    merge_markdown_files()