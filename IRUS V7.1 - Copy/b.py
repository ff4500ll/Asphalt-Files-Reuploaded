import os
import json
import cv2
import numpy as np
from PIL import ImageGrab
from ultralytics import YOLO
import keyboard
import time

class FishingDetector:
    def __init__(self):
        # Load configuration
        self.config_file = os.path.join(os.path.dirname(__file__), "Config.txt")
        self.config = self.load_config()

        # Get fish_box coordinates
        self.fish_box = self.config.get("fish_box", {"x1": 100, "y1": 100, "x2": 300, "y2": 300})
        self.x1 = self.fish_box["x1"]
        self.y1 = self.fish_box["y1"]
        self.x2 = self.fish_box["x2"]
        self.y2 = self.fish_box["y2"]

        # Paths
        self.base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(self.base_dir, "fishing_model.pt")

        # Model
        self.model = None

        # State
        self.should_exit = False
        self.use_half_res = False  # Toggle for half resolution (press 'H' to toggle)
        
        # Initialize mss for faster screen capture
        import mss
        self.sct = mss.mss()

        print("=" * 60)
        print("Fishing Detection - Live Detection")
        print("=" * 60)
        print(f"Fish Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Model Path: {self.model_path}")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"fish_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            print(f"\n❌ Error: Model not found at {self.model_path}")
            print("\nPlease train a model first by running:")
            print("   python train.py")
            return False

        print(f"\n📦 Loading model from {self.model_path}")
        try:
            import torch
            self.model = YOLO(self.model_path)
            
            # Enable half precision (FP16) on GPU for 2x speed
            if torch.cuda.is_available():
                self.model.half()
                print("✓ Model loaded successfully with FP16 (GPU)")
            else:
                print("✓ Model loaded successfully (CPU)")
            
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def capture_screen_area(self):
        """Capture the fish_box area from screen using mss (faster than PIL)"""
        try:
            # Define monitor region
            monitor = {
                "top": self.y1,
                "left": self.x1,
                "width": self.x2 - self.x1,
                "height": self.y2 - self.y1
            }
            
            # Capture using mss (much faster than PIL)
            sct_img = self.sct.grab(monitor)
            
            # Convert to numpy array and BGR format for OpenCV
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            return frame
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def run_live_detection(self):
        """Run live detection on the fish_box area"""
        print("\n" + "=" * 60)
        print("Starting Live Detection")
        print("=" * 60)
        print("\nControls:")
        print("  H - Toggle half resolution (faster but lower quality)")
        print("  ESC or Q - Exit live detection")
        print(f"\nMonitoring area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print("\nStarting in 3 seconds...")
        time.sleep(3)

        # Class names
        class_names = {0: "Target Line", 1: "Fish Bar"}
        class_colors = {0: (0, 255, 0), 1: (0, 0, 255)}  # Green for Target Line, Red for Fish Bar

        fps_time = time.time()
        fps = 0
        
        # Timing variables
        capture_time = 0
        resize_time = 0
        inference_time = 0
        draw_time = 0

        try:
            while not self.should_exit:
                loop_start = time.time()
                
                # Capture screen area
                t1 = time.time()
                frame = self.capture_screen_area()
                if frame is None:
                    continue
                capture_time = (time.time() - t1) * 1000  # ms

                # Resize to half resolution for 4x faster inference (if enabled)
                t2 = time.time()
                original_height, original_width = frame.shape[:2]
                
                if self.use_half_res:
                    frame_small = cv2.resize(frame, (original_width // 2, original_height // 2))
                    scale_factor = 2.0
                else:
                    frame_small = frame
                    scale_factor = 1.0
                    
                resize_time = (time.time() - t2) * 1000  # ms

                # Run detection on smaller frame
                t3 = time.time()
                results = self.model(frame_small, conf=0.1, verbose=False)  # Lower threshold to see more detections
                inference_time = (time.time() - t3) * 1000  # ms
                
                t4 = time.time()

                # Draw detections (scale back to original resolution for display)
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Get box coordinates (in processed image)
                        x1_s, y1_s, x2_s, y2_s = box.xyxy[0].cpu().numpy()
                        
                        # Scale back to original resolution if needed
                        x1 = int(x1_s * scale_factor)
                        y1 = int(y1_s * scale_factor)
                        x2 = int(x2_s * scale_factor)
                        y2 = int(y2_s * scale_factor)

                        # Get confidence and class
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])

                        # Get class name and color
                        label = class_names.get(cls, f"Class {cls}")
                        color = class_colors.get(cls, (255, 255, 255))
                        
                        # Use different color for low confidence detections
                        if conf < 0.5:
                            color = (0, 165, 255)  # Orange for low confidence (< 0.5)
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        # Draw label
                        label_text = f"{label}: {conf:.2f}"
                        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                        # Position label inside the box at the top if it would go above frame
                        if y1 - text_height - 10 < 0:
                            # Draw inside the box at the top
                            label_y = y1 + text_height + 5
                            cv2.rectangle(frame, (x1, y1), (x1 + text_width, y1 + text_height + 10), color, -1)
                        else:
                            # Draw above the box as normal
                            label_y = y1 - 5
                            cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)

                        # Draw label text
                        cv2.putText(frame, label_text, (x1, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                draw_time = (time.time() - t4) * 1000  # ms
                
                # Calculate FPS
                fps = 1.0 / (time.time() - loop_start)

                # Print timing to terminal
                total_time = capture_time + resize_time + inference_time + draw_time
                print(f"FPS: {fps:5.1f} | Total: {total_time:5.1f}ms | Capture: {capture_time:4.1f}ms | Resize: {resize_time:4.1f}ms | YOLO: {inference_time:5.1f}ms | Draw: {draw_time:4.1f}ms | Mode: {'Half-Res' if self.use_half_res else 'Full-Res'}")

                # Draw FPS counter and timing breakdown
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                mode_text = "Half-Res ON" if self.use_half_res else "Full-Res"
                cv2.putText(frame, f"Mode: {mode_text} (Press H)", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.putText(frame, f"Capture: {capture_time:.1f}ms", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"Resize: {resize_time:.1f}ms", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"YOLO: {inference_time:.1f}ms", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Draw: {draw_time:.1f}ms", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Display the frame
                cv2.imshow('Fishing Detection - Live Feed', frame)

                # Set window to always on top
                cv2.setWindowProperty('Fishing Detection - Live Feed', cv2.WND_PROP_TOPMOST, 1)

                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q or ESC
                    break
                elif key == ord('h') or key == ord('H'):  # H to toggle half resolution
                    self.use_half_res = not self.use_half_res
                    print(f"\n{'Enabled' if self.use_half_res else 'Disabled'} half resolution mode")

                # Check for keyboard interrupt
                if keyboard.is_pressed('esc'):
                    break

        except KeyboardInterrupt:
            print("\n\nDetection interrupted by user")
        finally:
            cv2.destroyAllWindows()
            self.sct.close()
            print("\n✓ Live detection stopped")

    def run(self):
        """Main execution flow"""
        # Load model
        if not self.load_model():
            return

        # Start live detection
        self.run_live_detection()

        print("\n" + "=" * 60)
        print("Program terminated")
        print("=" * 60)

def main():
    detector = FishingDetector()
    detector.run()

if __name__ == "__main__":
    main()
