import os
import json
import cv2
import numpy as np
from PIL import ImageGrab
from ultralytics import YOLO
import keyboard
import time

class ShakeDetector:
    def __init__(self):
        # Load configuration
        self.config_file = os.path.join(os.path.dirname(__file__), "Config.txt")
        self.config = self.load_config()

        # Get shake_box coordinates
        self.shake_box = self.config.get("shake_box", {"x1": 100, "y1": 100, "x2": 300, "y2": 300})
        self.x1 = self.shake_box["x1"]
        self.y1 = self.shake_box["y1"]
        self.x2 = self.shake_box["x2"]
        self.y2 = self.shake_box["y2"]

        # Paths
        self.base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(self.base_dir, "shake_model.pt")

        # Model
        self.model = None

        # State
        self.should_exit = False

        print("=" * 60)
        print("Shake Detection - Live Detection")
        print("=" * 60)
        print(f"Shake Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Model Path: {self.model_path}")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"shake_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            print(f"\n❌ Error: Model not found at {self.model_path}")
            print("\nPlease train a model first by running:")
            print("   python train_shake.py")
            return False

        print(f"\n📦 Loading model from {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            print("✓ Model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def capture_screen_area(self):
        """Capture the shake_box area from screen"""
        try:
            # Capture the specific area
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))

            # Convert PIL image to OpenCV format (BGR)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            return frame
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def run_live_detection(self):
        """Run live detection on the shake_box area"""
        print("\n" + "=" * 60)
        print("Starting Live Detection")
        print("=" * 60)
        print("\nControls:")
        print("  ESC or Q - Exit live detection")
        print(f"\nMonitoring area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print("\nStarting in 3 seconds...")
        time.sleep(3)

        # Class names - adjust based on your shake dataset labels
        class_names = {0: "Shake Indicator"}  # Modify this based on your actual classes
        class_colors = {0: (0, 255, 0)}  # Green

        fps_time = time.time()
        fps = 0

        try:
            while not self.should_exit:
                # Capture screen area
                frame = self.capture_screen_area()
                if frame is None:
                    continue

                # Run detection
                results = self.model(frame, conf=0.25, verbose=False)

                # Draw detections
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # Get confidence and class
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])

                        # Get class name and color
                        label = class_names.get(cls, f"Class {cls}")
                        color = class_colors.get(cls, (255, 255, 255))

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        # Draw label background
                        label_text = f"{label}: {conf:.2f}"
                        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)

                        # Draw label text
                        cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # Calculate FPS
                fps = 1.0 / (time.time() - fps_time)
                fps_time = time.time()

                # Draw FPS counter
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                # Display the frame
                cv2.imshow('Shake Detection - Live Feed', frame)

                # Set window to always on top
                cv2.setWindowProperty('Shake Detection - Live Feed', cv2.WND_PROP_TOPMOST, 1)

                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q or ESC
                    break

                # Check for keyboard interrupt
                if keyboard.is_pressed('esc'):
                    break

        except KeyboardInterrupt:
            print("\n\nDetection interrupted by user")
        finally:
            cv2.destroyAllWindows()
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
    detector = ShakeDetector()
    detector.run()

if __name__ == "__main__":
    main()
