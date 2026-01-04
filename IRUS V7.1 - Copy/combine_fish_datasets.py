import os
import shutil
from pathlib import Path

def combine_fish_datasets():
    """Combine multiple fish datasets into one for training"""

    base_dir = Path(__file__).parent
    processed_dir = base_dir / "Images" / "Processed"

    # Scan for available datasets
    print("=" * 60)
    print("Fish Dataset Combiner")
    print("=" * 60)
    print(f"\nScanning: {processed_dir}")

    # Find all directories in processed folder
    available_datasets = []
    if processed_dir.exists():
        for item in processed_dir.iterdir():
            if item.is_dir() and item.name != "Combined_Fish_Dataset":
                # Check if it has YOLO structure (images/labels folders)
                has_images = (item / "images").exists()
                has_labels = (item / "labels").exists()
                if has_images and has_labels:
                    available_datasets.append(item)

    if not available_datasets:
        print("\n❌ Error: No datasets found in processed folder")
        print("Expected structure: Images/Processed/[DatasetName]/images/")
        return False

    # Display available datasets
    print(f"\nFound {len(available_datasets)} dataset(s):")
    for idx, dataset in enumerate(available_datasets, 1):
        print(f"  [{idx}] {dataset.name}")

    # Get user selection
    print("\n" + "=" * 60)
    print("Select datasets to combine:")
    print("  - Enter numbers separated by spaces (e.g., 1 2 3)")
    print("  - Or type 'all' to select all datasets")
    print("=" * 60)

    user_input = input("\nYour selection: ").strip().lower()

    # Parse user selection
    selected_datasets = []
    if user_input == "all":
        selected_datasets = available_datasets
    else:
        try:
            indices = [int(x.strip()) for x in user_input.split()]
            for idx in indices:
                if 1 <= idx <= len(available_datasets):
                    selected_datasets.append(available_datasets[idx - 1])
                else:
                    print(f"\n⚠️  Warning: Index {idx} is out of range, skipping...")
        except ValueError:
            print("\n❌ Error: Invalid input. Please enter numbers or 'all'")
            return False

    if not selected_datasets:
        print("\n❌ Error: No datasets selected")
        return False

    # Show selected datasets
    print("\n" + "=" * 60)
    print("Selected Datasets:")
    print("=" * 60)
    for idx, dataset in enumerate(selected_datasets, 1):
        print(f"  {idx}. {dataset.name}")

    # Combined dataset destination
    combined_dir = processed_dir / "Combined_Fish_Dataset"
    print(f"\nOutput: {combined_dir}")

    # Confirm
    confirm = input("\nProceed with combining? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Operation cancelled by user")
        return False

    # Clean up old combined dataset if it exists
    if combined_dir.exists():
        print(f"\n🗑️  Removing old combined dataset...")
        shutil.rmtree(combined_dir)
        print("✓ Old dataset removed")

    # Create combined directory structure
    combined_train_images = combined_dir / "images" / "train"
    combined_train_labels = combined_dir / "labels" / "train"
    combined_val_images = combined_dir / "images" / "val"
    combined_val_labels = combined_dir / "labels" / "val"

    combined_train_images.mkdir(parents=True, exist_ok=True)
    combined_train_labels.mkdir(parents=True, exist_ok=True)
    combined_val_images.mkdir(parents=True, exist_ok=True)
    combined_val_labels.mkdir(parents=True, exist_ok=True)

    print("\n✓ Created combined dataset structure")

    # Function to copy files with prefix
    def copy_dataset(source_dir, prefix):
        """Copy dataset files with a prefix to avoid name conflicts"""
        train_img_src = source_dir / "images" / "train"
        train_lbl_src = source_dir / "labels" / "train"
        val_img_src = source_dir / "images" / "val"
        val_lbl_src = source_dir / "labels" / "val"

        counts = {"train_images": 0, "train_labels": 0, "val_images": 0, "val_labels": 0}

        # Copy training images
        if train_img_src.exists():
            for img in train_img_src.glob("*.png"):
                new_name = f"{prefix}_{img.name}"
                shutil.copy2(img, combined_train_images / new_name)
                counts["train_images"] += 1

        # Copy training labels
        if train_lbl_src.exists():
            for lbl in train_lbl_src.glob("*.txt"):
                new_name = f"{prefix}_{lbl.name}"
                shutil.copy2(lbl, combined_train_labels / new_name)
                counts["train_labels"] += 1

        # Copy validation images
        if val_img_src.exists():
            for img in val_img_src.glob("*.png"):
                new_name = f"{prefix}_{img.name}"
                shutil.copy2(img, combined_val_images / new_name)
                counts["val_images"] += 1

        # Copy validation labels
        if val_lbl_src.exists():
            for lbl in val_lbl_src.glob("*.txt"):
                new_name = f"{prefix}_{lbl.name}"
                shutil.copy2(lbl, combined_val_labels / new_name)
                counts["val_labels"] += 1

        return counts

    # Copy all selected datasets
    all_counts = []
    for idx, dataset in enumerate(selected_datasets, 1):
        prefix = f"d{idx}"
        print(f"\nCopying Dataset {idx} ({dataset.name})...")
        counts = copy_dataset(dataset, prefix)
        print(f"  Train: {counts['train_images']} images, {counts['train_labels']} labels")
        print(f"  Val: {counts['val_images']} images, {counts['val_labels']} labels")
        all_counts.append(counts)

    # Calculate totals
    total_train_images = sum(c['train_images'] for c in all_counts)
    total_train_labels = sum(c['train_labels'] for c in all_counts)
    total_val_images = sum(c['val_images'] for c in all_counts)
    total_val_labels = sum(c['val_labels'] for c in all_counts)

    print("\n" + "=" * 60)
    print("Combined Dataset Summary:")
    print("=" * 60)
    print(f"Training:   {total_train_images} images, {total_train_labels} labels")
    print(f"Validation: {total_val_images} images, {total_val_labels} labels")
    print(f"Total:      {total_train_images + total_val_images} images")

    # Create data.yaml
    yaml_content = f"""# Combined Fish Dataset Configuration
path: {combined_dir.as_posix()}
train: images/train
val: images/val

# Classes
names:
  0: Target Line
  1: Fish Bar

# Number of classes
nc: 2
"""

    yaml_path = combined_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"\n✓ Created data.yaml at {yaml_path}")

    print("\n" + "=" * 60)
    print("✅ Datasets Combined Successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: train_gpu.bat")
    print("2. When prompted, select to train on the combined dataset")
    print(f"3. Dataset location: {combined_dir}")
    print("\nThis will update your fishing_model.pt with the combined data.")

    return True

if __name__ == "__main__":
    try:
        combine_fish_datasets()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
