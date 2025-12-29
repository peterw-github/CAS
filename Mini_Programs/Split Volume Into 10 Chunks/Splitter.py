import os
import re
import glob


def split_markdown_by_speaker(parts=10):
    # 1. Scan folder for a markdown file
    md_files = glob.glob("*.md")

    # Filter out files that look like generated parts (contain "- Ch")
    source_files = [f for f in md_files if " - Ch " not in f]

    if not source_files:
        print("Error: No source markdown (.md) files found in this folder.")
        print("(Make sure your source file doesn't already have ' - Ch ' in the name)")
        input("Press Enter to exit...")
        return

    filename = source_files[0]
    print(f"Found source file: {filename}")

    # 2. Read the content
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    total_length = len(content)

    # 3. Calculate mathematical targets
    target_sizes = [total_length * (i + 1) / parts for i in range(parts - 1)]

    # 4. Find all valid split points (Heading 3)
    header_matches = list(re.finditer(r'(?m)^### ', content))
    valid_split_indices = [m.start() for m in header_matches]

    if not valid_split_indices:
        print("Error: No '###' headers found in the file. Cannot split by speaker.")
        input("Press Enter to exit...")
        return

    # 5. Find closest split points
    final_cut_points = [0]
    for target in target_sizes:
        closest_index = min(valid_split_indices, key=lambda x: abs(x - target))
        if closest_index != final_cut_points[-1]:
            final_cut_points.append(closest_index)
    final_cut_points.append(total_length)

    # 6. Determine Output Filename Format
    vol_match = re.search(r'(Vol\s*\d+)', filename, re.IGNORECASE)

    if vol_match:
        file_prefix = vol_match.group(1)
    else:
        file_prefix = os.path.splitext(filename)[0]

    print(f"Splitting into {len(final_cut_points) - 1} parts...")

    # 7. Create the files with XML Tags
    for i in range(len(final_cut_points) - 1):
        start = final_cut_points[i]
        end = final_cut_points[i + 1]

        chunk_content = content[start:end]

        if i > 0:
            chunk_content = chunk_content.lstrip('\n')

        # Naming format: Vol X - Ch 01.md
        output_filename = f"{file_prefix} - Ch {i + 1:02}.md"

        # Create the XML Tags
        start_tag = f'`<file name="{output_filename}">`\n'
        end_tag = f'\n`</file>`'

        # Combine everything
        final_content = start_tag + chunk_content + end_tag

        with open(output_filename, 'w', encoding='utf-8') as out:
            out.write(final_content)

        print(f" -> Created: {output_filename}")

    print("Done!")


if __name__ == "__main__":
    split_markdown_by_speaker()