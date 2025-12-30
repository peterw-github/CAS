import os

# Updated output filename
output_filename = "output.md"


def merge_markdown_files():
    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for .md files, excluding the output file itself to prevent loops
    md_files = [f for f in all_files if f.endswith('.md') and f != output_filename]

    # Sort the files alphabetically
    md_files.sort()

    if not md_files:
        print("No Markdown files found in this directory.")
        return

    print(f"--- STARTING MERGE ---")
    print(f"Target: {len(md_files)} files found.")
    print("-" * 30)

    # Open the output file in write mode
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for index, filename in enumerate(md_files):
            # Echo to the console which file is being processed
            print(f"[+] Merging: {filename}")

            try:
                with open(filename, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                    outfile.write(content)

                    # Add separator if it's not the last file
                    if index < len(md_files) - 1:
                        outfile.write("\n\n---\n\n")

            except Exception as e:
                print(f"[!] Error reading {filename}: {e}")

    print("-" * 30)
    print(f"SUCCESS: {len(md_files)} files merged into '{output_filename}'.")


if __name__ == "__main__":
    merge_markdown_files()