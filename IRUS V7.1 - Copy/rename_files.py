import os
from pathlib import Path

def rename_bar_to_blank():
    """Rename Bar_X files to Blank_X in Images folder"""
    
    images_dir = Path(__file__).parent / "Images"
    
    if not images_dir.exists():
        print(f"❌ Error: {images_dir} not found!")
        return
    
    print("=" * 60)
    print("File Renamer - Bar_X → Blank_X")
    print("=" * 60)
    print(f"\nScanning: {images_dir}")
    
    # Find all files starting with "Bar_"
    bar_files = []
    for file in images_dir.glob("Bar_*"):
        if file.is_file():
            bar_files.append(file)
    
    if not bar_files:
        print("\n❌ No files starting with 'Bar_' found!")
        return
    
    print(f"\nFound {len(bar_files)} file(s) to rename:")
    for file in sorted(bar_files)[:10]:  # Show first 10
        print(f"  {file.name}")
    if len(bar_files) > 10:
        print(f"  ... and {len(bar_files) - 10} more")
    
    # Confirm
    confirm = input(f"\nRename {len(bar_files)} files? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Rename files
    renamed_count = 0
    for file in bar_files:
        # Get new name by replacing "Bar_" with "Blank_"
        new_name = file.name.replace("Bar_", "Blank_")
        new_path = file.parent / new_name
        
        try:
            file.rename(new_path)
            renamed_count += 1
            print(f"✓ {file.name} → {new_name}")
        except Exception as e:
            print(f"❌ Failed to rename {file.name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully renamed {renamed_count} file(s)")
    print("=" * 60)

if __name__ == "__main__":
    rename_bar_to_blank()
