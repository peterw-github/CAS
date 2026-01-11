# **Volume Afterglow Generator**

This is a simple automation tool designed to generate 10 blank Markdown files for a specific Volume sequence. It ensures consistent naming conventions (e.g., `Vol X - Afterglow 01.md`).

## 📂 Files Included

-   **create\_raw\_afterglows.py**: The main logic script written in Python.
    
-   **run\_generator.bat**: A Windows batch file to easily launch the script.
    

## 🚀 How to Run

### Method 1: The Easy Way (Windows)

1.  Double-click on `run_generator.bat`.
    
2.  A terminal window will open.
    
3.  Type the Volume Number (e.g., `3`, `IV`, `Final`) when prompted.
    
4.  Press **Enter**.
    

### Method 2: Via Command Line

1.  Open your terminal in this folder.
    
2.  Run the command:
    
        python create_raw_afterglows.py
    
    

## ⚙️ How It Works

1.  The script asks for a **Volume Input** (X).
    
2.  It automatically generates **10 markdown files**.
    
3.  It uses zero-padding for numbers (e.g., `01` instead of `1`) for proper sorting.
    

### Output Example

If you enter `5` as the volume, the script creates:

-   `Vol 5 - Afterglow 01.md`
    
-   `Vol 5 - Afterglow 02.md`
    
-   ...
    
-   `Vol 5 - Afterglow 10.md`
    

_Created for the Afterglow project._