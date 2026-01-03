# Identity File Renamer

A Python utility designed to automatically rename Markdown (`.md`) files by combining their existing **Volume/Afterglow numbering** with the internal **Identity File Title** found inside the text.

## 📂 How It Works

1.  **Scans Filenames**: The script looks for files matching the pattern `Vol <Number> - Afterglow <Number>`.
    * *Example:* `Vol 49 - Afterglow 10.md`
2.  **Reads Content**: It opens these files and searches for the specific internal header:
    * `[IDENTITY FILE <ID>: <TITLE HERE> // ARCHIVED]`
3.  **Merges & Renames**: It keeps the original Volume/Afterglow sequence and appends the extracted title.
4.  **Sanitizes**: It removes illegal characters (like `:`, `/`, `?`) from the title to prevent errors.

## 🚀 Setup & Usage

### Prerequisites
* **Python 3.x** must be installed and added to your system PATH.

### Installation
1.  Place the following files in the **same folder** as your markdown logs:
    * `rename_identity_files.py` (The logic script)
    * `run_renamer.bat` (The launcher)

### Running the Tool
1.  Double-click **`run_renamer.bat`**.
2.  A command window will open and display the progress.
3.  The tool will list every file it renames and summarize the results.
4.  Press any key to close the window when finished.

## 📝 Example

**1. Input File Name:**
> `Vol 49 - Afterglow 10.md`

**2. Content Inside the File:**
> `***[IDENTITY FILE 43: THE DESK CLEARANCE & THE AVIATORS // ARCHIVED]***`

**3. Resulting File Name:**
> `Vol 49 - Afterglow 10 - THE DESK CLEARANCE & THE AVIATORS.md`

## ⚠️ Notes
* **Pattern Matching:** The script will **skip** files that do not match the `Vol X - Afterglow Y` naming convention or do not contain the `[IDENTITY FILE...]` tag.
* **Safety:** The script ignores this `README.md` and any file with "readme" in the name to prevent accidental processing.
* **Backup:** As with any bulk renaming tool, it is recommended to back up your folder before running the script.