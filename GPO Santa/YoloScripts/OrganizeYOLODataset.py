import os
import shutil
from pathlib import Path

class YOLODatasetOrganizer:
    def __init__(self):
        # Get parent directory (GPO Santa)
        self.base_dir = Path(__file__).parent
        
        # Define source folders with their corresponding image folders
        self.datasets = [
            {
                'name': 'Santa2',
                'labels': self.base_dir / "Santa Haki",  # Labels from Santa Haki
                'images': self.base_dir / "500ImageFolders" / "Santa2"  # Images from Santa2
            }
        ]
        
        self.output_dir = self.base_dir / "YOLODataset"
        
    def get_available_folders(self):
        """Get available datasets"""
        available = []
        for dataset in self.datasets:
            if dataset['labels'].exists():
                available.append(dataset)
            else:
                print(f"WARNING: {dataset['labels']} does not exist!")
        
        if not available:
            print(f"ERROR: No dataset folders found!")
        
        return available
    
    def display_folders(self, folders):
        """Display available datasets"""
        print("\n=== Available Datasets ===")
        for i, dataset in enumerate(folders, 1):
            print(f"{i}. {dataset['name']}")
            print(f"   Labels: {dataset['labels']}")
            print(f"   Images: {dataset['images']}")
        print()
    
    def select_folders(self, folders):
        """Return all folders (no selection needed)"""
        return folders
    
    def organize_dataset(self, selected_folders):
        """Organize the dataset into YOLO format"""
        print("\n=== Organizing Dataset ===")
        
        # Clear existing dataset to prevent accumulation
        if self.output_dir.exists():
            print(f"Clearing existing dataset at {self.output_dir}...")
            shutil.rmtree(self.output_dir)
            print("✓ Old dataset cleared")
        
        # Create output directories
        train_images_dir = self.output_dir / "images" / "train"
        train_labels_dir = self.output_dir / "labels" / "train"
        
        train_images_dir.mkdir(parents=True, exist_ok=True)
        train_labels_dir.mkdir(parents=True, exist_ok=True)
        
        total_images = 0
        total_labels = 0
        
        for dataset in selected_folders:
            dataset_name = dataset['name']
            labels_path = dataset['labels']
            images_path = dataset['images']
            
            print(f"\nProcessing: {dataset_name}")
            
            # Check for labels - try both direct labels folder and labels/train structure
            labels_source = None
            if (labels_path / "labels" / "train").exists():
                labels_source = labels_path / "labels" / "train"
            elif (labels_path / "labels").exists():
                labels_source = labels_path / "labels"
            elif labels_path.exists():
                # Check if labels_path itself contains .txt files
                txt_files = list(labels_path.glob("*.txt"))
                if txt_files:
                    labels_source = labels_path
            
            if not labels_source or not labels_source.exists():
                print(f"  WARNING: No label files found in {labels_path}")
                continue
            
            # Check for images - try both direct and images/train structure
            images_source = None
            if (images_path / "images" / "train").exists():
                images_source = images_path / "images" / "train"
            elif (images_path / "images").exists():
                images_source = images_path / "images"
            elif images_path.exists():
                images_source = images_path
            
            if not images_source or not images_source.exists():
                print(f"  WARNING: Images folder not found at {images_path}")
                continue
            
            # Get all label files
            label_files = list(labels_source.glob("*.txt"))
            print(f"  Found {len(label_files)} label files")
            print(f"  Labels from: {labels_source}")
            print(f"  Images from: {images_source}")
            
            copied_images = 0
            copied_labels = 0
            missing_images = []
            
            for label_file in label_files:
                # Get the base name (e.g., "1" from "1.txt")
                base_name = label_file.stem
                
                # Look for matching image (try .png, .jpg, .jpeg)
                image_file = None
                for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                    potential_image = images_source / f"{base_name}{ext}"
                    if potential_image.exists():
                        image_file = potential_image
                        break
                
                if not image_file:
                    missing_images.append(base_name)
                    continue
                
                # Create unique filename using dataset name prefix
                unique_name = f"{dataset_name.replace(' ', '_')}_{base_name}"
                
                # Copy image
                dest_image = train_images_dir / f"{unique_name}{image_file.suffix}"
                shutil.copy2(image_file, dest_image)
                copied_images += 1
                
                # Copy label
                dest_label = train_labels_dir / f"{unique_name}.txt"
                shutil.copy2(label_file, dest_label)
                copied_labels += 1
            
            print(f"  ✓ Copied {copied_images} images")
            print(f"  ✓ Copied {copied_labels} labels")
            
            if missing_images:
                print(f"  ⚠ Missing images for: {', '.join(missing_images[:5])}"
                      f"{' ...' if len(missing_images) > 5 else ''}")
            
            total_images += copied_images
            total_labels += copied_labels
        
        # Create data.yaml
        self.create_data_yaml(selected_folders)
        
        print(f"\n=== Summary ===")
        print(f"Total images copied: {total_images}")
        print(f"Total labels copied: {total_labels}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"\nDataset structure:")
        print(f"  {self.output_dir}/")
        print(f"    ├── images/")
        print(f"    │   └── train/")
        print(f"    ├── labels/")
        print(f"    │   └── train/")
        print(f"    └── data.yaml")
        
        return total_images
    
    def create_data_yaml(self, selected_folders):
        """Create data.yaml for YOLO training"""
        dataset_names = ", ".join([d['name'] for d in selected_folders])
        
        yaml_content = f"""# YOLO Dataset Configuration
# Generated from: {dataset_names}

path: {self.output_dir.absolute()}
train: images/train
val: images/train  # Using same as train for now

names:
  0: Icon
  1: Santa

nc: 2  # number of classes
"""
        
        yaml_path = self.output_dir / "data.yaml"
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"\n✓ Created data.yaml at {yaml_path}")
    
    def run(self):
        """Main execution flow"""
        print("=" * 50)
        print("YOLO Dataset Organizer")
        print("=" * 50)
        
        # Get available folders
        folders = self.get_available_folders()
        
        if not folders:
            print("No datasets found!")
            return
        
        # Display folders
        self.display_folders(folders)
        
        # Auto-select (no user input needed)
        selected = self.select_folders(folders)
        
        if not selected:
            print("No dataset found. Exiting.")
            return
        
        # Confirm
        confirm = input("\nProceed with organizing? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        
        # Organize
        total = self.organize_dataset(selected)
        
        if total > 0:
            print("\n✓ Dataset organized successfully!")
            print(f"\nTo train with YOLO12:")
            print(f"  from ultralytics import YOLO")
            print(f"  model = YOLO('yolo12n.pt')")
            print(f"  model.train(data='{self.output_dir / 'data.yaml'}', epochs=100)")
        else:
            print("\n⚠ No images were copied. Check your folder structure.")


if __name__ == "__main__":
    organizer = YOLODatasetOrganizer()
    organizer.run()
