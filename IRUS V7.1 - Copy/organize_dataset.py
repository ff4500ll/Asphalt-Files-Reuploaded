import os
import shutil
from pathlib import Path

def find_available_datasets():
    """Find all available datasets in Images/Processed/"""
    base_dir = Path(__file__).parent
    processed_dir = base_dir / "Images" / "Processed"

    if not processed_dir.exists():
        return []

    # Find all directories in Processed/
    datasets = [d for d in processed_dir.iterdir() if d.is_dir()]
    return datasets

def find_raw_images():
    """Find all raw image folders in Images/"""
    base_dir = Path(__file__).parent
    images_dir = base_dir / "Images"

    if not images_dir.exists():
        return []

    # Find all directories in Images/ that contain .png files (excluding Processed)
    raw_folders = []
    for item in images_dir.iterdir():
        if item.is_dir() and item.name != "Processed":
            # Check if it contains any .png files
            if list(item.glob("*.png")):
                raw_folders.append(item)

    return raw_folders

def organize_yolo_dataset(dataset_name=None, raw_images_folder=None):
    """Organize the CVAT exported dataset into proper YOLO format"""

    base_dir = Path(__file__).parent

    # If no dataset specified, let user choose
    if dataset_name is None:
        available_datasets = find_available_datasets()

        if not available_datasets:
            print("❌ No datasets found in Images/Processed/")
            print("\nPlease ensure you have exported your CVAT annotations to:")
            print("   Images/Processed/[Dataset Name]/")
            return False

        print("=" * 60)
        print("Available Datasets in Images/Processed/:")
        print("=" * 60)
        for idx, dataset in enumerate(available_datasets, 1):
            print(f"  {idx}. {dataset.name}")

        choice = input("\nSelect dataset number to organize: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_datasets):
                dataset_name = available_datasets[choice_idx].name
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False

    # If no raw images folder specified, let user choose
    if raw_images_folder is None:
        raw_folders = find_raw_images()

        if not raw_folders:
            print("\n❌ No raw image folders found in Images/")
            print("\nPlease ensure you have captured screenshots using a.py")
            return False

        print("\n" + "=" * 60)
        print("Available Raw Image Folders:")
        print("=" * 60)
        for idx, folder in enumerate(raw_folders, 1):
            num_images = len(list(folder.glob("*.png")))
            print(f"  {idx}. {folder.name} ({num_images} images)")

        choice = input("\nSelect raw images folder number: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(raw_folders):
                raw_images_folder = raw_folders[choice_idx].name
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False

    # Source directories
    images_source = base_dir / "Images" / raw_images_folder
    labels_source = base_dir / "Images" / "Processed" / dataset_name / "labels" / "train"

    # Destination directory
    dataset_dir = base_dir / "Images" / "Processed" / dataset_name

    # Create proper YOLO structure
    train_images_dir = dataset_dir / "images" / "train"
    train_labels_dir = dataset_dir / "labels" / "train"
    val_images_dir = dataset_dir / "images" / "val"
    val_labels_dir = dataset_dir / "labels" / "val"

    # Create directories
    train_images_dir.mkdir(parents=True, exist_ok=True)
    train_labels_dir.mkdir(parents=True, exist_ok=True)
    val_images_dir.mkdir(parents=True, exist_ok=True)
    val_labels_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Organizing YOLO Dataset")
    print("=" * 60)

    # Get all images
    all_images = sorted(list(images_source.glob("*.png")))
    print(f"\nFound {len(all_images)} images in {images_source}")

    if len(all_images) == 0:
        print(f"❌ No images found in {images_source}")
        return False

    # Split 80/20 for train/val
    split_idx = int(len(all_images) * 0.8)
    train_images = all_images[:split_idx]
    val_images = all_images[split_idx:]

    print(f"Split: {len(train_images)} train, {len(val_images)} val")

    # Copy training images and labels
    print("\nCopying training data...")
    for img_path in train_images:
        # Copy image
        dest_img = train_images_dir / img_path.name
        if not dest_img.exists():
            shutil.copy2(img_path, dest_img)

        # Copy corresponding label
        label_name = img_path.stem + ".txt"
        label_path = labels_source / label_name
        dest_label = train_labels_dir / label_name

        if label_path.exists() and not dest_label.exists():
            shutil.copy2(label_path, dest_label)

    print(f"✓ Copied {len(train_images)} training images and labels")

    # Copy validation images and labels
    print("\nCopying validation data...")
    for img_path in val_images:
        # Copy image
        dest_img = val_images_dir / img_path.name
        if not dest_img.exists():
            shutil.copy2(img_path, dest_img)

        # Copy corresponding label
        label_name = img_path.stem + ".txt"
        label_path = labels_source / label_name
        dest_label = val_labels_dir / label_name

        if label_path.exists() and not dest_label.exists():
            shutil.copy2(label_path, dest_label)

    print(f"✓ Copied {len(val_images)} validation images and labels")

    # Create data.yaml
    yaml_content = f"""# YOLO Dataset Configuration
path: {dataset_dir.as_posix()}
train: images/train
val: images/val

# Classes
names:
  0: Target Line
  1: Fish Bar

# Number of classes
nc: 2
"""

    yaml_path = dataset_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"\n✓ Created data.yaml at {yaml_path}")

    # Verify structure
    print("\n" + "=" * 60)
    print("Dataset Structure:")
    print("=" * 60)
    print(f"📁 {dataset_dir}")
    print(f"  ├── data.yaml")
    print(f"  ├── images/")
    print(f"  │   ├── train/ ({len(list(train_images_dir.glob('*.png')))} images)")
    print(f"  │   └── val/ ({len(list(val_images_dir.glob('*.png')))} images)")
    print(f"  └── labels/")
    print(f"      ├── train/ ({len(list(train_labels_dir.glob('*.txt')))} labels)")
    print(f"      └── val/ ({len(list(val_labels_dir.glob('*.txt')))} labels)")

    print("\n✅ Dataset organized successfully!")
    print("\nYou can now run: python train.py")

    return True

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("YOLO Dataset Organizer")
        print("=" * 60)
        print("\nThis script will organize your CVAT-exported dataset")
        print("into the proper YOLO training format.\n")

        organize_yolo_dataset()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
