import os
import shutil
from pathlib import Path

def setup_blank_dataset():
    """Move Blank_X files to Processed/Blank folder with proper YOLO structure"""
    
    base_dir = Path(__file__).parent
    images_dir = base_dir / "Images"
    processed_dir = images_dir / "Processed"
    blank_dir = processed_dir / "Blank"
    
    # Create directory structure
    train_images = blank_dir / "images" / "train"
    train_labels = blank_dir / "labels" / "train"
    val_images = blank_dir / "images" / "val"
    val_labels = blank_dir / "labels" / "val"
    
    print("=" * 60)
    print("Setup Blank Dataset - Background Images (No Labels)")
    print("=" * 60)
    
    # Create directories
    train_images.mkdir(parents=True, exist_ok=True)
    train_labels.mkdir(parents=True, exist_ok=True)
    val_images.mkdir(parents=True, exist_ok=True)
    val_labels.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Created directory structure at: {blank_dir}")
    
    # Find all Blank_* files in Images folder
    blank_files = sorted(images_dir.glob("Blank_*.png"))
    
    if not blank_files:
        print("\n❌ No files starting with 'Blank_' found in Images folder!")
        print(f"   Looking in: {images_dir}")
        return False
    
    print(f"\nFound {len(blank_files)} Blank_*.png file(s)")
    
    # Split 80/20 train/val
    split_idx = int(len(blank_files) * 0.8)
    train_files = blank_files[:split_idx]
    val_files = blank_files[split_idx:]
    
    print(f"  Train: {len(train_files)} images")
    print(f"  Val: {len(val_files)} images")
    
    confirm = input("\nProceed with moving files? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return False
    
    print("\nMoving files and creating empty labels...")
    
    # Process training files
    for idx, src_file in enumerate(train_files, 1):
        # Copy image
        dst_image = train_images / f"blank_{idx:03d}.png"
        shutil.copy2(src_file, dst_image)
        
        # Create empty label file
        dst_label = train_labels / f"blank_{idx:03d}.txt"
        dst_label.touch()  # Creates empty file
        
        print(f"  ✓ Train {idx:03d}: {src_file.name} → blank_{idx:03d}.png (+ empty .txt)")
    
    # Process validation files
    for idx, src_file in enumerate(val_files, 1):
        # Copy image
        dst_image = val_images / f"blank_val_{idx:03d}.png"
        shutil.copy2(src_file, dst_image)
        
        # Create empty label file
        dst_label = val_labels / f"blank_val_{idx:03d}.txt"
        dst_label.touch()  # Creates empty file
        
        print(f"  ✓ Val {idx:03d}: {src_file.name} → blank_val_{idx:03d}.png (+ empty .txt)")
    
    # Create data.yaml
    yaml_content = f"""# Blank Dataset - Background Images (No Objects)
path: {blank_dir.as_posix()}
train: images/train
val: images/val

# Classes
names:
  0: Target Line
  1: Fish Bar

# Number of classes
nc: 2
"""
    
    yaml_path = blank_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✓ Created data.yaml")
    
    print("\n" + "=" * 60)
    print("✅ Blank Dataset Created Successfully!")
    print("=" * 60)
    print(f"\nDataset location: {blank_dir}")
    print(f"  Train: {len(train_files)} images with empty labels")
    print(f"  Val: {len(val_files)} images with empty labels")
    
    print("\n📋 Next steps:")
    print("1. Run: python combine_fish_datasets.py")
    print("2. Select 'all' to include Blank dataset with your other datasets")
    print("3. Run: train_fish.py to retrain with negative examples")
    
    # Ask if user wants to delete original files
    delete = input("\nDelete original Blank_*.png files from Images folder? (y/n): ").strip().lower()
    if delete == 'y':
        for file in blank_files:
            file.unlink()
        print(f"✓ Deleted {len(blank_files)} original files")
    else:
        print("✓ Original files kept in Images folder")
    
    return True

if __name__ == "__main__":
    try:
        setup_blank_dataset()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
