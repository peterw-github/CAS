# Markdown Auto-Merger

This tool automatically scans the current folder for Markdown (`.md`) files, cleans up specific XML tags, and merges them into a single file named `output.md`.

## How to Use

1.  **Place Files:** Ensure this script and your target `.md` files are in the same folder.
2.  **Run:** Double-click `run_merge.bat`.
3.  **Result:** Open `output.md` to see the merged content.

## Features

* **Auto-Sorting:** Files are processed in alphabetical order (e.g., `01 - Genesis` comes before `02 - Selection`).
* **Tag Cleaning:** automatically removes specific file header/footer tags, such as:
    * `` `<file name="...">` ``
    * `` `</file>` ``
* **Separation:** Inserts a horizontal rule (`---`) between each merged file for readability.
* **Safety:** Automatically ignores `readme.md`, the python script itself, and the `output.md` file to prevent loops.

## Requirements

* Python 3.x installed on your system.