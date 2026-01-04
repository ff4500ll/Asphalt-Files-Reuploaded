from ultralytics import YOLO
from pathlib import Path
import torch

class YOLO12Trainer:
    def __init__(self):
        # Get parent directory (GPO Santa) from YoloScripts
        self.base_dir = Path(__file__).parent.parent
        self.dataset_path = self.base_dir / "YOLODataset" / "data.yaml"
        self.model_name = "yolo12n.pt"
        self.output_dir = self.base_dir / "runs" / "train"
        
    def check_dataset(self):
        """Verify dataset exists"""
        if not self.dataset_path.exists():
            print(f"ERROR: Dataset not found at {self.dataset_path}")
            print("Please run OrganizeYOLODataset.py first!")
            return False
        
        print(f"✓ Dataset found: {self.dataset_path}")
        return True
    
    def train(self):
        """Train YOLO12n model with augmentation for different aspect ratios"""
        print("\n" + "=" * 60)
        print("YOLO12n Training - Santa & Icon Detection")
        print("=" * 60)
        
        if not self.check_dataset():
            return
        
        # Check CUDA availability
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"\nUsing device: {device.upper()}")
        if device == 'cpu':
            print("⚠ Training on CPU will be VERY slow. GPU recommended.")
        
        print(f"\nLoading model: {self.model_name}")
        model = YOLO(self.model_name)
        
        print("\n" + "-" * 60)
        print("Training Configuration:")
        print("-" * 60)
        print("Epochs: 100")
        print("Image Size: 640x640")
        print("Batch Size: Auto (or 16 if GPU, 8 if CPU)")
        print("\nAugmentation (optimized for 3D objects):")
        print("  • Scale: ±60% (distance variation)")
        print("  • Horizontal Flip: 50%")
        print("  • Rotation: ±30° (3D rotation)")
        print("  • Perspective: Enhanced (3D depth)")
        print("  • Shear: 3.0 (3D transformations)")
        print("  • Translate: ±15% (position variation)")
        print("  • Mosaic: 4-image mixing")
        print("  • Mixup: 15% (occlusion/overlap)")
        print("  • Copy-Paste: 10%")
        print("  Note: Strong augmentation for 3D objects in various angles")
        print("-" * 60)
        
        confirm = input("\nStart training? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Training cancelled.")
            return
        
        print("\n🚀 Starting training...\n")
        
        # Training parameters optimized for 3D objects with varied perspectives
        results = model.train(
            data=str(self.dataset_path),
            epochs=100,
            imgsz=640,  # Standard YOLO size (will letterbox to preserve aspect ratio)
            batch=-1 if device == 'cuda' else 8,  # Auto batch size for GPU, 8 for CPU
            device=device,
            
            # Augmentation parameters - enhanced for 3D objects
            scale=0.6,  # Scale ±60% (handles distance variation)
            fliplr=0.5,  # Horizontal flip 50%
            flipud=0.0,  # No vertical flip (objects have up/down orientation)
            mosaic=1.0,  # Mosaic augmentation
            mixup=0.15,  # Mixup 15% (occlusion/overlap)
            copy_paste=0.1,  # Copy-paste 10%
            
            # Color/appearance augmentation
            hsv_h=0.02,  # Hue augmentation (lighting changes)
            hsv_s=0.7,    # Saturation augmentation
            hsv_v=0.5,    # Value/brightness augmentation (shadows)
            
            # Geometric augmentation - enhanced for 3D perspective
            degrees=30.0,      # Rotation ±30° (camera angle variation)
            translate=0.15,     # Translation ±15% (position variation)
            shear=3.0,         # Shear 3.0 (3D perspective distortion)
            perspective=0.0008, # Enhanced perspective (3D depth effect)
            
            # Training settings
            patience=50,       # Early stopping patience
            save=True,         # Save checkpoints
            save_period=10,    # Save every 10 epochs
            
            # Validation
            val=True,
            plots=True,        # Generate training plots
            
            # Performance
            workers=8 if device == 'cuda' else 4,
            amp=True if device == 'cuda' else False,  # Automatic Mixed Precision (GPU only)
            
            # Prevent overfitting
            dropout=0.0,
            
            # Project organization
            project=str(self.output_dir),
            name='yolo12n_santa',
            exist_ok=True
        )
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        
        # Get best model path
        best_model = self.output_dir / "yolo12n_santa" / "weights" / "best.pt"
        last_model = self.output_dir / "yolo12n_santa" / "weights" / "last.pt"
        
        print(f"\n✓ Best model saved to: {best_model}")
        print(f"✓ Last model saved to: {last_model}")
        
        print("\n" + "-" * 60)
        print("Training Results:")
        print("-" * 60)
        print(f"Final mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
        print(f"Final mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
        
        print("\n" + "-" * 60)
        print("Test the model:")
        print("-" * 60)
        print(f"from ultralytics import YOLO")
        print(f"model = YOLO('{best_model}')")
        print(f"results = model.predict('test_image.png', conf=0.25)")
        print("-" * 60)
        
        # Validate on training set to see final performance
        print("\n📊 Running validation...")
        val_results = model.val()
        
        print("\n✓ All done! Check the plots in:")
        print(f"   {self.output_dir / 'yolo12n_santa'}")


if __name__ == "__main__":
    trainer = YOLO12Trainer()
    trainer.train()
