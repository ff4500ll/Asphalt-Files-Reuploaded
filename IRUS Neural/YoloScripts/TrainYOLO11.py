from ultralytics import YOLO
from pathlib import Path
import torch

class YOLO11Trainer:
    def __init__(self):
        # Get parent directory (IRUS Neural) from YoloScripts
        self.base_dir = Path(__file__).parent.parent
        self.dataset_path = self.base_dir / "YOLODataset" / "data.yaml"
        self.model_name = "yolo11n.pt"
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
        """Train YOLO11n model with augmentation for different aspect ratios"""
        print("\n" + "=" * 60)
        print("YOLO11n Training - Multi-Resolution & Aspect Ratio Support")
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
        print("\nAugmentation (handles different aspect ratios & stretching):")
        print("  • Scale: ±50% to handle different object sizes")
        print("  • Horizontal Flip: 50% probability")
        print("  • Mosaic: Enabled (mixes 4 images)")
        print("  • HSV Color Jitter: Enabled")
        print("  • Perspective Transform: Enabled")
        print("  • Degrees: ±10° rotation")
        print("  • Translate: ±10% translation")
        print("-" * 60)
        
        confirm = input("\nStart training? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Training cancelled.")
            return
        
        print("\n🚀 Starting training...\n")
        
        # Training parameters optimized for handling different resolutions/aspect ratios
        results = model.train(
            data=str(self.dataset_path),
            epochs=100,
            imgsz=640,  # Standard YOLO size (will letterbox to preserve aspect ratio)
            batch=-1 if device == 'cuda' else 8,  # Auto batch size for GPU, 8 for CPU
            device=device,
            
            # Augmentation parameters for handling stretched/scaled images
            scale=0.5,  # Scale images ±50% (handles different sizes)
            fliplr=0.5,  # Horizontal flip 50% of the time
            flipud=0.0,  # No vertical flip (fish bars are always upright)
            mosaic=1.0,  # Mosaic augmentation (combines 4 images)
            mixup=0.1,  # Mixup augmentation 10% of the time
            
            # Color/appearance augmentation
            hsv_h=0.015,  # Hue augmentation
            hsv_s=0.7,    # Saturation augmentation
            hsv_v=0.4,    # Value/brightness augmentation
            
            # Geometric augmentation (helps with different aspect ratios)
            degrees=10.0,      # Rotation ±10 degrees
            translate=0.1,     # Translation ±10%
            shear=0.0,         # No shear (keeps rectangles rectangular)
            perspective=0.0005, # Slight perspective transform
            
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
            name='yolo11n_fish_bar',
            exist_ok=True
        )
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        
        # Get best model path
        best_model = self.output_dir / "yolo11n_fish_bar" / "weights" / "best.pt"
        last_model = self.output_dir / "yolo11n_fish_bar" / "weights" / "last.pt"
        
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
        print(f"   {self.output_dir / 'yolo11n_fish_bar'}")


if __name__ == "__main__":
    trainer = YOLO11Trainer()
    trainer.train()
