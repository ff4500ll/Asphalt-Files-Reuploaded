import os
import json
import numpy as np
from PIL import ImageGrab
import keyboard
import time

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

        # Paths
        self.base_dir = os.path.dirname(__file__)
        self.screenshot_dir = os.path.join(self.base_dir, "shake_screenshots")

        # Create screenshot directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        # State
        self.should_exit = False
        self.is_paused = False
        self.is_running = False
        self.screenshot_count = 0
        self.max_screenshots = 100

        print("=" * 60)
        print("Shake Box Screenshot Capture")
        print("=" * 60)
        print(f"Shake Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Screenshot Directory: {self.screenshot_dir}")
        print(f"Max Screenshots: {self.max_screenshots}")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"shake_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def capture_screen_area(self):
        """Capture the shake_box area from screen"""
        try:
            # Capture the specific area
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
            return screenshot
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def save_screenshot(self, screenshot):
        """Save screenshot to file"""
        try:
            filename = f"shake_{self.screenshot_count:04d}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)
            return True
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return False

    def run_capture(self):
        """Run screenshot capture"""
        print("\n" + "=" * 60)
        print("Screenshot Capture Controls")
        print("=" * 60)
        print("\nControls:")
        print("  F1 - Start capturing")
        print("  F2 - Pause/Resume")
        print("  F3 - Exit")
        print(f"\nMonitoring area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Interval: 0.1 seconds")
        print(f"Max screenshots: {self.max_screenshots}")
        print("\nPress F1 to start...")

        # Set up keyboard hooks
        keyboard.add_hotkey('f1', self.start_capture)
        keyboard.add_hotkey('f2', self.toggle_pause)
        keyboard.add_hotkey('f3', self.exit_program)

        try:
            while not self.should_exit:
                if self.is_running and not self.is_paused:
                    # Capture screenshot
                    screenshot = self.capture_screen_area()
                    if screenshot is not None:
                        if self.save_screenshot(screenshot):
                            self.screenshot_count += 1
                            print(f"Screenshot {self.screenshot_count}/{self.max_screenshots} captured", end='\r')

                            # Check if we've reached the limit
                            if self.screenshot_count >= self.max_screenshots:
                                print(f"\n\nReached maximum of {self.max_screenshots} screenshots!")
                                self.is_running = False
                                self.is_paused = False
                                print("Capture stopped. Press F1 to start a new session or F3 to exit.")

                    # Wait 0.1 seconds
                    time.sleep(0.1)
                else:
                    # Small sleep to prevent CPU spinning when paused/stopped
                    time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n\nCapture interrupted by user")
        finally:
            keyboard.unhook_all()
            print("\n\nProgram terminated")
            print(f"Total screenshots captured: {self.screenshot_count}")

    def start_capture(self):
        """Start or restart capture"""
        if not self.is_running:
            # Reset counter if starting fresh
            if self.screenshot_count >= self.max_screenshots:
                self.screenshot_count = 0
            self.is_running = True
            self.is_paused = False
            print(f"\n\nCapture started! Taking screenshots every 0.1 seconds...")
        elif self.is_paused:
            self.is_paused = False
            print(f"\n\nCapture resumed from screenshot {self.screenshot_count}...")

    def toggle_pause(self):
        """Toggle pause state"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.is_paused:
                print(f"\n\nCapture paused at screenshot {self.screenshot_count}")
            else:
                print(f"\n\nCapture resumed from screenshot {self.screenshot_count}")

    def exit_program(self):
        """Exit the program"""
        print("\n\nExiting program...")
        self.should_exit = True

    def run(self):
        """Main execution flow"""
        self.run_capture()

        print("\n" + "=" * 60)
        print("Program terminated")
        print(f"Total screenshots: {self.screenshot_count}")
        print("=" * 60)

def main():
    capture = ShakeScreenshotCapture()
    capture.run()

if __name__ == "__main__":
    main()
