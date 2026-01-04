import os
import json
import time
import keyboard
from PIL import ImageGrab
from datetime import datetime

class ScreenshotCapture:
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

        # Screenshot settings
        self.total_screenshots = 100
        self.interval = 0.25  # 500 milliseconds
        self.current_count = 0

        # State
        self.is_running = False
        self.is_paused = False
        self.should_exit = False

        # Create Images folder
        self.images_folder = os.path.join(os.path.dirname(__file__), "Images")
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
            print(f"Created folder: {self.images_folder}")

        print("Screenshot Capture Ready")
        print(f"Fish Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Screenshots will be saved to: {self.images_folder}")
        print("\nControls:")
        print("  F1 - Start/Resume capturing")
        print("  F2 - Pause capturing")
        print("  F3 - Emergency shutdown")
        print(f"\nTarget: {self.total_screenshots} screenshots")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default fish_box coordinates")
            return {"fish_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def capture_screenshot(self):
        """Capture screenshot of the fish_box area"""
        try:
            # Capture the specific area
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))

            # Generate filename
            filename = f"Bar_{self.current_count + 1}.png"
            filepath = os.path.join(self.images_folder, filename)

            # Save the screenshot
            screenshot.save(filepath)

            self.current_count += 1
            print(f"[{self.current_count}/{self.total_screenshots}] Saved: {filename}")

            return True
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return False

    def start_capture(self):
        """Start or resume capturing"""
        if self.current_count >= self.total_screenshots:
            print(f"\n✓ All {self.total_screenshots} screenshots already captured!")
            print("Reset the script to start a new batch.")
            return

        self.is_running = True
        self.is_paused = False
        print(f"\n▶️ Starting capture from screenshot {self.current_count + 1}...")

    def pause_capture(self):
        """Pause capturing"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            print(f"\n⏸️ Paused at {self.current_count}/{self.total_screenshots} screenshots")

    def emergency_shutdown(self):
        """Emergency shutdown"""
        print(f"\n🛑 Emergency shutdown activated!")
        print(f"Captured {self.current_count}/{self.total_screenshots} screenshots before shutdown")
        self.should_exit = True

    def run(self):
        """Main loop"""
        # Setup hotkeys
        keyboard.add_hotkey('f1', self.start_capture)
        keyboard.add_hotkey('f2', self.pause_capture)
        keyboard.add_hotkey('f3', self.emergency_shutdown)

        print("\nWaiting for input... Press F1 to start")

        try:
            while not self.should_exit:
                # Check if we should capture
                if self.is_running and not self.is_paused and self.current_count < self.total_screenshots:
                    self.capture_screenshot()

                    # Check if we've reached the target
                    if self.current_count >= self.total_screenshots:
                        print(f"\n✅ Complete! All {self.total_screenshots} screenshots captured!")
                        self.is_running = False
                    else:
                        # Wait for the interval
                        time.sleep(self.interval)
                else:
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nScript interrupted by user")
        finally:
            keyboard.unhook_all()
            print(f"\nFinal count: {self.current_count}/{self.total_screenshots} screenshots")
            print("Script terminated.")

def main():
    print("=" * 50)
    print("Screenshot Capture Tool")
    print("=" * 50)

    capture = ScreenshotCapture()
    capture.run()

if __name__ == "__main__":
    main()
