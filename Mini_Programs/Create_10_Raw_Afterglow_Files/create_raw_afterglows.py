import os

def create_markdown_files():
    # 1. Get the Volume number from the user
    vol_num = input("Enter the Volume number (X): ").strip()

    print(f"\nGenerating files for Volume {vol_num}...\n")

    # 2. Loop from 1 to 10
    for i in range(1, 11):
        # Format the filename: Swapped 'Ch' for 'Afterglow'
        filename = f"Vol {vol_num} - Afterglow {i:02}.md"
        
        # 3. Create the empty file
        with open(filename, 'w') as f:
            pass  
            
        print(f"Created: {filename}")

    print("\nAll done!")

if __name__ == "__main__":
    create_markdown_files()