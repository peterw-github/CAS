It is very simple. Since you already have the file, you just need to open it in your text editor and add the names of the folders you want to ignore on new lines.

Here is exactly what to paste into your `.gitignore`:

```gitignore
TextFiles/
AudioFiles/
```

**That's it!**

The trailing slash (`/`) tells Git, "Ignore this entire folder and everything inside it."

**One Important Note:**
If you had accidentally committed any files from those folders *before* adding this rule, Git will keep tracking them. To stop tracking them (but keep them on your computer), run this in your terminal:

```bash
git rm -r --cached TextFiles AudioFiles
```

But if those folders are new, just saving the `.gitignore` file is all you need to do.