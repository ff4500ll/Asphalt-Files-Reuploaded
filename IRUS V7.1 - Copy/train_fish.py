import os
import json
from ultralytics import YOLO

class ModelTrainer:
    def __init__(self):
        # Paths
        self.base_dir = os.path.dirname(__file__)
        self.dataset_path = os.path.join(self.base_dir, "Images", "Processed", "100 Flimsy Rod")
        self.model_save_path = os.path.join(self.base_dir, "fishing_model.pt")

        print("=" * 60)
        print("YOLO Model Training - Fishing Detection")
        print("=" * 60)
        print(f"Dataset Path: {self.dataset_path}")
        print(f"Model will be saved to: {self.model_save_path}")

    def check_dataset(self):
        """Check if dataset exists and is properly formatted"""
        if not os.path.exists(self.dataset_path):
            print(f"\n❌ Error: Dataset not found at {self.dataset_path}")
            print("\nPlease ensure your YOLO dataset is located at:")
            print(f"   {self.dataset_path}")
            print("\nDataset structure should be:")
            print("   100 Flimsy Rod/")
            print("   ├── data.yaml")
            print("   ├── images/")
            print("   │   ├── train/")
            print("   │   └── val/")
            print("   └── labels/")
            print("       ├── train/")
            print("       └── val/")
            return False

        # Check for data.yaml
        yaml_path = os.path.join(self.dataset_path, "data.yaml")
        if not os.path.exists(yaml_path):
            print(f"\n⚠️ Warning: data.yaml not found. Creating default configuration...")
            self.create_data_yaml()
        else:
            print(f"\n✓ Found data.yaml at: {yaml_path}")

        print(f"✓ Dataset found at: {self.dataset_path}")
        return True

    def create_data_yaml(self):
        """Create a data.yaml file for YOLO training"""
        yaml_content = f"""# Dataset configuration for YOLO
path: {self.dataset_path}
train: images/train
val: images/val

# Classes
names:
  0: Target Line
  1: Fish Bar
"""
        yaml_path = os.path.join(self.dataset_path, "data.yaml")
        try:
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            print(f"✓ Created data.yaml at {yaml_path}")
        except Exception as e:
            print(f"❌ Error creating data.yaml: {e}")

    def train_model(self, epochs=100, batch=16, imgsz=320, device='cpu', base_model='yolo11n.pt'):
        """Train the YOLO model"""
        print("\n" + "=" * 60)
        print("Starting Model Training")
        print("=" * 60)

        try:
            # Initialize YOLO model
            print(f"\n📦 Loading base model ({base_model})...")
            model = YOLO(base_model)

            # Get yaml path
            yaml_path = os.path.join(self.dataset_path, "data.yaml")

            # Training parameters
            print(f"\nTraining Parameters:")
            print(f"  Base Model: {base_model}")
            print(f"  Epochs: {epochs}")
            print(f"  Batch Size: {batch}")
            print(f"  Image Size: {imgsz}")
            print(f"  Device: {device}")
            print(f"  Dataset: {yaml_path}")

            print("\n🚀 Training started...")
            print("This may take several minutes to hours depending on your hardware.")
            print("You can monitor the progress below:\n")

            # Train the model with EXTREMELY LENIENT settings - MAXIMUM RECALL for thin Target Line
            results = model.train(
                data=yaml_path,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch,
                rect=True,  # Rectangular training - better for wide/thin fish bar
                name='fishing_detection',
                patience=50,  # Higher patience - let it train longer before stopping (50 epochs no improvement)
                save=True,
                plots=True,
                device=device,
                project=os.path.join(self.base_dir, 'runs'),
                exist_ok=True,
                
                # OPTIMIZER - More permissive learning
                optimizer='auto',  # Let YOLO choose best optimizer
                lr0=0.01,          # Default learning rate
                lrf=0.01,          # Final learning rate = 1% of initial
                momentum=0.937,    # Default momentum
                weight_decay=0.0,  # NO weight decay = no regularization = maximum permissiveness
                
                # LOSS WEIGHTS - EXTREMELY LENIENT (Target Line is hard to detect, be very permissive)
                box=5.0,           # LOWER box loss = less strict about exact box position
                cls=0.1,           # Class loss weight - EXTREMELY LOW = will detect with 10-20% confidence
                dfl=1.0,           # LOWER DFL = less strict about box distribution
                
                # NMS (Non-Maximum Suppression) - Extremely permissive
                iou=0.1,           # EXTREMELY LOW IoU = allows massively overlapping detections
                conf=0.001,        # Confidence threshold during training (kept very low)
                
                # AUGMENTATION - MAXIMUM diversity for robust detection in ANY condition
                hsv_h=0.05,        # LARGE hue variation (handles different lighting/colors)
                hsv_s=0.9,         # VERY HIGH saturation variation (handles any color intensity)
                hsv_v=0.7,         # VERY HIGH brightness variation (handles dark/bright/occlusion)
                translate=0.2,     # 20% position shift (massive movement tolerance)
                scale=0.3,         # 30% scale variation (massive size tolerance)
                degrees=0,         # No rotation (UI elements don't rotate)
                flipud=0.0,        # No vertical flip
                fliplr=0.0,        # No horizontal flip
                mosaic=1.0,        # MAXIMUM mosaic = sees objects in every possible context
                mixup=0.2,         # More mixup = better generalization through blending
                shear=0,           # No shear (UI is always rectangular)
                perspective=0.0,   # No perspective distortion
                copy_paste=0.0,    # Disable copy-paste augmentation
                
                # VALIDATION - Strict validation for catching overfitting
                val=True,          # Run validation
                save_period=10,    # Save checkpoint every 10 epochs
                
                # ADVANCED - For maximum recall
                close_mosaic=0,    # Disable mosaic from the start (we already have it at 0)
                amp=True,          # Automatic mixed precision (faster without accuracy loss)
                fraction=1.0,      # Use 100% of training data
                profile=False,     # Disable profiling (slightly faster)
                freeze=None,       # Don't freeze any layers
                
                # MULTI-SCALE - Disabled for consistent detection
                multi_scale=False, # Single scale training (better for fixed UI size)
            )

            # Get the best model path
            best_model_path = os.path.join(self.base_dir, 'runs', 'fishing_detection', 'weights', 'best.pt')

            if os.path.exists(best_model_path):
                # Copy best model to root directory
                import shutil
                shutil.copy(best_model_path, self.model_save_path)
                print(f"\n💾 Best model saved to: {self.model_save_path}")
            else:
                print(f"\n⚠️ Warning: Could not find best model at {best_model_path}")

            print("\n✅ Training complete!")
            print(f"\nTraining results saved in: {os.path.join(self.base_dir, 'runs', 'fishing_detection')}")
            print("You can view training plots and metrics in the results folder.")

            return True

        except Exception as e:
            print(f"\n❌ Error during training: {e}")
            import traceback
            traceback.print_exc()
            return False

    def select_dataset(self):
        """Let user select which dataset to train on"""
        import os
        processed_dir = os.path.join(self.base_dir, "Images", "Processed")

        if not os.path.exists(processed_dir):
            return None

        # Find all dataset directories
        datasets = []
        for item in os.listdir(processed_dir):
            item_path = os.path.join(processed_dir, item)
            if os.path.isdir(item_path):
                # Check if it has data.yaml or proper structure
                yaml_path = os.path.join(item_path, "data.yaml")
                if os.path.exists(yaml_path) or os.path.exists(os.path.join(item_path, "images")):
                    datasets.append(item)

        if not datasets:
            return None

        print("\n" + "=" * 60)
        print("Available Datasets:")
        print("=" * 60)
        for idx, dataset in enumerate(datasets, 1):
            print(f"  {idx}. {dataset}")

        choice = input("\nSelect dataset number to train on: ").strip()
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(datasets):
                selected = datasets[choice_idx]
                self.dataset_path = os.path.join(processed_dir, selected)
                print(f"\n✓ Selected: {selected}")
                return True
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False

    def run(self):
        """Main execution flow"""
        # Let user select dataset
        if not self.select_dataset():
            print("\n❌ No datasets available.")
            return False

        # Check dataset
        if not self.check_dataset():
            print("\n❌ Cannot proceed without dataset.")
            return False

        # Check for GPU availability
        import torch
        has_cuda = torch.cuda.is_available()

        if has_cuda:
            print(f"\n✓ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            default_device = '0'
        else:
            print("\n⚠️ No CUDA GPU detected. Training will use CPU (slower).")
            default_device = 'cpu'

        # Ask for training parameters
        print("\n" + "=" * 60)
        print("Training Configuration - MAXIMUM ACCURACY MODE")
        print("=" * 60)
        print("\n⚡ IMAGE SIZE:")
        print("   320 = 4x faster inference (recommended - still accurate)")
        print("   416 = 2x faster inference (balanced)")
        print("   640 = Best accuracy but slower")
        
        print("\n📦 MODEL OPTIONS:")
        print("   yolo11n.pt = Nano (fastest, recommended for UI detection)")
        print("   yolo11s.pt = Small (more accurate, slightly slower)")
        print("   yolo11m.pt = Medium (overkill for UI, very slow)")
        
        print("\n🎯 EPOCHS:")
        print("   50-100 = Quick training (usually sufficient)")
        print("   150-200 = Extended training")
        print("   Note: Early stopping will kick in if validation stops improving")

        try:
            base_model = input("\nBase model (default: yolo11n.pt): ").strip()
            base_model = base_model if base_model else 'yolo11n.pt'
            
            epochs = input("Number of epochs (default: 100): ").strip()
            epochs = int(epochs) if epochs else 100

            batch = input("Batch size (default: 16): ").strip()
            batch = int(batch) if batch else 16

            imgsz = input("Image size - 320/416/640 (default: 320 for speed): ").strip()
            imgsz = int(imgsz) if imgsz else 320

            if has_cuda:
                device = input(f"Device - 'cpu' or '0' for GPU (default: {default_device}): ").strip()
                device = device if device else default_device
            else:
                device = 'cpu'
                print(f"Device: cpu (no GPU available)")

        except ValueError:
            print("\n⚠️ Invalid input. Using default balanced values.")
            base_model = 'yolo11n.pt'
            epochs = 100
            batch = 16
            imgsz = 320
            device = default_device

        # Confirm before training
        print("\n" + "=" * 60)
        print("Ready to start training with the following configuration:")
        print(f"  Base Model: {base_model}")
        print(f"  Epochs: {epochs}")
        print(f"  Batch Size: {batch}")
        print(f"  Image Size: {imgsz}")
        print(f"  Device: {device}")
        print("=" * 60)

        confirm = input("\nProceed with training? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Training cancelled.")
            return False

        # Start training
        success = self.train_model(epochs=epochs, batch=batch, imgsz=imgsz, device=device, base_model=base_model)

        if success:
            print("\n" + "=" * 60)
            print("✅ Training Complete!")
            print("=" * 60)
            print(f"\nYou can now run 'b.py' to use the trained model for live detection.")
        else:
            print("\n" + "=" * 60)
            print("❌ Training Failed")
            print("=" * 60)

        return success

def main():
    trainer = ModelTrainer()
    trainer.run()

if __name__ == "__main__":
    main()
