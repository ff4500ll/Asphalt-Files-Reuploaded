import os
import json
import keyboard
from PIL import ImageGrab

class ShakeScreenshotCapture:
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

        # Screenshot settings
        self.total_screenshots = 100
        self.current_count = 0

        # State
        self.should_exit = False

        # Create Images folder
        self.images_folder = os.path.join(os.path.dirname(__file__), "Images")
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
            print(f"Created folder: {self.images_folder}")

        print("=" * 50)
        print("Shake Screenshot Capture - Manual Mode")
        print("=" * 50)
        print(f"Shake Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Screenshots will be saved to: {self.images_folder}")
        print("\nControls:")
        print("  F1 - Take screenshot (manual, one per press)")
        print("  F3 - Emergency shutdown")
        print(f"\nTarget: {self.total_screenshots} screenshots")
        print(f"Current: {self.current_count}/{self.total_screenshots}\n")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default shake_box coordinates")
            return {"shake_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def capture_screenshot(self):
        """Capture screenshot of the shake_box area"""
        if self.current_count >= self.total_screenshots:
            print(f"\n✓ All {self.total_screenshots} screenshots already captured!")
            print("Cannot take more screenshots. Restart the script to capture a new batch.")
            return False

        try:
            # Capture the specific area
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))

            # Generate filename
            filename = f"Shake_{self.current_count + 1}.png"
            filepath = os.path.join(self.images_folder, filename)

            # Save the screenshot
            screenshot.save(filepath)

            self.current_count += 1
            print(f"[{self.current_count}/{self.total_screenshots}] Saved: {filename}")

            if self.current_count >= self.total_screenshots:
                print(f"\n✅ Complete! All {self.total_screenshots} screenshots captured!")

            return True
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return False

    def on_f1_press(self):
        """Handle F1 press - take one screenshot"""
        self.capture_screenshot()

    def emergency_shutdown(self):
        """Emergency shutdown"""
        print(f"\n🛑 Emergency shutdown activated!")
        print(f"Captured {self.current_count}/{self.total_screenshots} screenshots before shutdown")
        self.should_exit = True

    def run(self):
        """Main loop"""
        # Setup hotkeys
        keyboard.add_hotkey('f1', self.on_f1_press)
        keyboard.add_hotkey('f3', self.emergency_shutdown)

        print("Ready! Press F1 to take a screenshot...\n")

        try:
            # Wait for input
            keyboard.wait('f3')  # Wait until F3 is pressed
        except KeyboardInterrupt:
            print("\n\nScript interrupted by user")
        finally:
            keyboard.unhook_all()
            print(f"\nFinal count: {self.current_count}/{self.total_screenshots} screenshots")
            print("Script terminated.")

def main():
    print("=" * 50)
    print("Shake Screenshot Capture Tool - Manual Mode")
    print("=" * 50)

    capture = ShakeScreenshotCapture()
    capture.run()

if __name__ == "__main__":
    main()
