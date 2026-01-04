import keyboard
import json
import os
import sys
import time
import ctypes
from PIL import ImageGrab

# Set DPI awareness to handle Windows scaling properly
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
    except:
        pass


class ShakeScreenshotCapture:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.should_exit = False
        self.shake_area = None
        self.screenshot_dir = "100ShakeScreenshots"
        self.max_screenshots = 100
        self.capture_interval = 0.5  # 500ms
        
        # Ensure screenshot directory exists
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            print(f"Created directory: {self.screenshot_dir}")
        
        # Load shake area coordinates
        self._load_shake_area()
        
        # Find missing screenshot numbers
        self.missing_numbers = self._find_missing_numbers()
        
        if not self.missing_numbers:
            print("All 100 screenshots already exist! Nothing to capture.")
            sys.exit(0)
        
        print(f"Need to capture {len(self.missing_numbers)} screenshots: {self.missing_numbers[:10]}{'...' if len(self.missing_numbers) > 10 else ''}")
        
        # Setup hotkeys
        self._setup_hotkeys()
        
        print("\n=== 100 Shake Screenshot Capture ===")
        print("F3 = Start capturing")
        print("F4 = Pause/Resume")
        print("F1 = Exit")
        print(f"\nShake Area: x={self.shake_area['x']}, y={self.shake_area['y']}, "
              f"width={self.shake_area['width']}, height={self.shake_area['height']}")
        print("\nWaiting for F3 to start...\n")
        
    def _get_settings_path(self):
        """Get the path to NeuralSettings.json"""
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            # Go up one level from YoloScripts to main directory
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(app_dir, "NeuralSettings.json")
    
    def _load_shake_area(self):
        """Load shake area coordinates from NeuralSettings.json"""
        settings_path = self._get_settings_path()
        
        if not os.path.exists(settings_path):
            print(f"ERROR: NeuralSettings.json not found at {settings_path}")
            print("Please run IRUS Neural.py first to create the settings file.")
            sys.exit(1)
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                self.shake_area = settings.get("shake_area")
                
                if not self.shake_area:
                    print("ERROR: shake_area not found in NeuralSettings.json")
                    sys.exit(1)
                    
                print(f"Loaded shake area from: {settings_path}")
        except Exception as e:
            print(f"ERROR loading settings: {e}")
            sys.exit(1)
    
    def _find_missing_numbers(self):
        """Find which screenshot numbers are missing (1-100)"""
        existing_files = os.listdir(self.screenshot_dir)
        existing_numbers = set()
        
        for filename in existing_files:
            if filename.endswith('.png'):
                try:
                    # Extract number from filename (e.g., "1.png" -> 1)
                    num = int(os.path.splitext(filename)[0])
                    if 1 <= num <= self.max_screenshots:
                        existing_numbers.add(num)
                except ValueError:
                    continue
        
        # Find all missing numbers from 1 to 100
        all_numbers = set(range(1, self.max_screenshots + 1))
        missing = sorted(all_numbers - existing_numbers)
        
        return missing
    
    def _setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        keyboard.on_press_key('F3', lambda _: self._on_start())
        keyboard.on_press_key('F4', lambda _: self._on_pause())
        keyboard.on_press_key('F1', lambda _: self._on_exit())
    
    def _on_start(self):
        """Handle F3 - Start capturing"""
        if not self.is_running and not self.should_exit:
            self.is_running = True
            self.is_paused = False
            print(">>> STARTED capturing screenshots...")
    
    def _on_pause(self):
        """Handle F4 - Pause/Resume"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.is_paused:
                print(">>> PAUSED (press F4 to resume)")
            else:
                print(">>> RESUMED capturing...")
    
    def _on_exit(self):
        """Handle F1 - Exit"""
        print(">>> EXIT requested...")
        self.should_exit = True
        self.is_running = False
    
    def capture_screenshot(self, number):
        """Capture a screenshot of the shake area"""
        try:
            # Calculate the bounding box for the shake area
            x1 = self.shake_area['x']
            y1 = self.shake_area['y']
            x2 = x1 + self.shake_area['width']
            y2 = y1 + self.shake_area['height']
            
            # Capture the region
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Save with number as filename
            filepath = os.path.join(self.screenshot_dir, f"{number}.png")
            screenshot.save(filepath)
            
            print(f"Captured screenshot {number}/{self.max_screenshots}")
            return True
        except Exception as e:
            print(f"ERROR capturing screenshot {number}: {e}")
            return False
    
    def run(self):
        """Main capture loop"""
        current_index = 0
        last_capture_time = 0
        
        try:
            while not self.should_exit:
                # Wait for start
                if not self.is_running:
                    time.sleep(0.1)
                    continue
                
                # Check if paused
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                # Check if we're done
                if current_index >= len(self.missing_numbers):
                    print("\n=== All screenshots captured! ===")
                    print(f"Total captured: {len(self.missing_numbers)}")
                    print(f"Saved to: {os.path.abspath(self.screenshot_dir)}")
                    break
                
                # Check if enough time has passed since last capture
                current_time = time.time()
                if current_time - last_capture_time >= self.capture_interval:
                    number = self.missing_numbers[current_index]
                    
                    if self.capture_screenshot(number):
                        current_index += 1
                        last_capture_time = current_time
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\n>>> Interrupted by user")
        finally:
            keyboard.unhook_all()
            print("Exiting...")


if __name__ == "__main__":
    app = ShakeScreenshotCapture()
    app.run()
