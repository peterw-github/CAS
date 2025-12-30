import os
import re
import glob


def rename_all_markdown_files():
    # Find all .md files in the current directory
    md_files = glob.glob("*.md")

    if not md_files:
        print("No markdown files found in this folder.")
        return

    print(f"--- Starting Scan of {len(md_files)} files ---")

    # Counters for our log
    renamed_count = 0
    skipped_count = 0
    error_count = 0

    # Regex to find <file name="...">
    pattern = r'<file\s+name=["\'](.*?)["\']'

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.search(pattern, content)

            if match:
                new_filename = match.group(1)

                # Sanitize filename (remove illegal characters if any exist in the tag)
                # This keeps windows happy: remove < > : " / \ | ? *
                new_filename = re.sub(r'[<>:"/\\|?*]', '', new_filename)

                # Ensure it ends in .md if the tag didn't include it (optional safety)
                if not new_filename.lower().endswith('.md'):
                    new_filename += ".md"

                # Check if name is already correct
                if os.path.basename(file_path) == new_filename:
                    skipped_count += 1
                    # verbose: print(f"[Skip] {file_path} (Name already correct)")
                    continue

                # Check for collision
                if os.path.exists(new_filename):
                    print(f"[!] Conflict: Can't rename '{file_path}' -> '{new_filename}' (File exists)")
                    error_count += 1
                    continue

                # Rename
                os.rename(file_path, new_filename)
                print(f"[OK] Renamed: '{file_path}'  -->  '{new_filename}'")
                renamed_count += 1
            else:
                # No tag found
                skipped_count += 1

        except Exception as e:
            print(f"[!] Error processing '{file_path}': {e}")
            error_count += 1

    # Final Summary Log
    print("-" * 40)
    print("SUMMARY REPORT")
    print(f"Total Files Scanned: {len(md_files)}")
    print(f"Renamed:             {renamed_count}")
    print(f"Skipped (No tag/Same): {skipped_count}")
    print(f"Errors:              {error_count}")
    print("-" * 40)


if __name__ == "__main__":
    rename_all_markdown_files()