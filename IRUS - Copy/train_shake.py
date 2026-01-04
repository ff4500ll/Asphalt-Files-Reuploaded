import os
import json
from ultralytics import YOLO

class ShakeModelTrainer:
    def __init__(self):
        # Paths
        self.base_dir = os.path.dirname(__file__)
        self.dataset_path = os.path.join(self.base_dir, "Images", "Processed", "Shake")
        self.model_save_path = os.path.join(self.base_dir, "shake_model.pt")

        print("=" * 60)
        print("YOLO Model Training - Shake Detection")
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
            print("   Shake/")
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
        yaml_content = f"""# Dataset configuration for YOLO - Shake Detection
path: {self.dataset_path}
train: images/train
val: images/val

# Classes - Modify these based on your actual annotations
names:
  0: Shake Indicator

# Number of classes
nc: 1
"""
        yaml_path = os.path.join(self.dataset_path, "data.yaml")
        try:
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            print(f"✓ Created data.yaml at {yaml_path}")
        except Exception as e:
            print(f"❌ Error creating data.yaml: {e}")

    def train_model(self, epochs=100, batch=16, imgsz=640, device='cpu'):
        """Train the YOLO model"""
        print("\n" + "=" * 60)
        print("Starting Model Training")
        print("=" * 60)

        try:
            # Initialize YOLO model
            print("\n📦 Loading YOLO11 nano model (yolo11n.pt)...")
            model = YOLO('yolo11n.pt')  # Use YOLO11 nano for best speed/accuracy balance

            # Get yaml path
            yaml_path = os.path.join(self.dataset_path, "data.yaml")

            # Training parameters
            print(f"\nTraining Parameters:")
            print(f"  Epochs: {epochs}")
            print(f"  Batch Size: {batch}")
            print(f"  Image Size: {imgsz}")
            print(f"  Device: {device}")
            print(f"  Dataset: {yaml_path}")

            print("\n🚀 Training started...")
            print("This may take several minutes to hours depending on your hardware.")
            print("You can monitor the progress below:\n")

            # Train the model
            results = model.train(
                data=yaml_path,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch,
                rect=True,  # Rectangular training - preserves aspect ratio
                name='shake_detection',
                patience=20,  # Early stopping patience
                save=True,
                plots=True,
                device=device,
                project=os.path.join(self.base_dir, 'runs'),
                exist_ok=True,
                # Augmentation for robustness
                hsv_h=0.015,    # Hue variation for different lighting
                hsv_s=0.7,      # Saturation variation
                hsv_v=0.4,      # Brightness variation
                translate=0.1,  # 10% position shift (shake can appear anywhere)
                scale=0.15,     # 15% scale variation
                degrees=0,      # No rotation (UI elements don't rotate)
                flipud=False,   # Don't flip vertically
                fliplr=False,   # Don't flip horizontally
                mosaic=0.0      # Disable mosaic (not needed for fixed UI)
            )

            # Get the best model path
            best_model_path = os.path.join(self.base_dir, 'runs', 'shake_detection', 'weights', 'best.pt')

            if os.path.exists(best_model_path):
                # Copy best model to root directory
                import shutil
                shutil.copy(best_model_path, self.model_save_path)
                print(f"\n💾 Best model saved to: {self.model_save_path}")
            else:
                print(f"\n⚠️ Warning: Could not find best model at {best_model_path}")

            print("\n✅ Training complete!")
            print(f"\nTraining results saved in: {os.path.join(self.base_dir, 'runs', 'shake_detection')}")
            print("You can view training plots and metrics in the results folder.")

            return True

        except Exception as e:
            print(f"\n❌ Error during training: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Main execution flow"""
        # Check dataset
        if not self.check_dataset():
            print("\n❌ Cannot proceed without dataset.")
            return False

        # Ask for training parameters
        print("\n" + "=" * 60)
        print("Training Configuration")
        print("=" * 60)

        # Check for GPU availability
        import torch
        has_cuda = torch.cuda.is_available()

        if has_cuda:
            print(f"\n✓ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            default_device = '0'
        else:
            print("\n⚠️ No CUDA GPU detected. Training will use CPU (slower).")
            default_device = 'cpu'

        try:
            epochs = input("\nNumber of epochs (default: 100): ").strip()
            epochs = int(epochs) if epochs else 100

            batch = input("Batch size (default: 16): ").strip()
            batch = int(batch) if batch else 16

            imgsz = input("Image size (default: 640): ").strip()
            imgsz = int(imgsz) if imgsz else 640

            if has_cuda:
                device = input(f"Device - 'cpu' or '0' for GPU (default: {default_device}): ").strip()
                device = device if device else default_device
            else:
                device = 'cpu'
                print(f"Device: cpu (no GPU available)")

        except ValueError:
            print("\n⚠️ Invalid input. Using default values.")
            epochs = 100
            batch = 16
            imgsz = 640
            device = default_device

        # Confirm before training
        print("\n" + "=" * 60)
        print("Ready to start training with the following configuration:")
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
        success = self.train_model(epochs=epochs, batch=batch, imgsz=imgsz, device=device)

        if success:
            print("\n" + "=" * 60)
            print("✅ Training Complete!")
            print("=" * 60)
            print(f"\nYou can now run 'python a.py' to use the trained model for live shake detection.")
        else:
            print("\n" + "=" * 60)
            print("❌ Training Failed")
            print("=" * 60)

        return success

def main():
    trainer = ShakeModelTrainer()
    trainer.run()

if __name__ == "__main__":
    main()
