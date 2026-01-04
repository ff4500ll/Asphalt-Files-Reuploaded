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


class FishScreenshotCapture:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.should_exit = False
        self.screenshot_dir = "FullScreenScreenshots"
        self.max_screenshots = 500
        self.capture_interval = 1  # 1 second
        self.manual_mode = False
        self.manual_capture_requested = False
        
        # Ensure screenshot directory exists
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            print(f"Created directory: {self.screenshot_dir}")
        
        # Find missing screenshot numbers
        self.missing_numbers = self._find_missing_numbers()
        
        if not self.missing_numbers:
            print("All 500 screenshots already exist! Nothing to capture.")
            sys.exit(0)
        
        print(f"Need to capture {len(self.missing_numbers)} screenshots: {self.missing_numbers[:10]}{'...' if len(self.missing_numbers) > 10 else ''}")
        
        # Setup hotkeys
        self._setup_hotkeys()
        
        print("\n=== 500 Full Screen Screenshot Capture ===")
        print("F3 = Start capturing")
        print("F4 = Pause/Resume")
        print("F5 = Manual capture (take 1 screenshot)")
        print("F6 = Toggle manual/auto mode")
        print("F1 = Exit")
        print(f"\nCapturing: Full Screen")
        print(f"\nMode: {'MANUAL' if self.manual_mode else 'AUTO'}")
        print("Waiting for F3 to start...\n")
        
    def _find_missing_numbers(self):
        """Find which screenshot numbers are missing (1-500)"""
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
        
        # Find all missing numbers from 1 to 500
        all_numbers = set(range(1, self.max_screenshots + 1))
        missing = sorted(all_numbers - existing_numbers)
        
        return missing
    
    def _setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        keyboard.on_press_key('F3', lambda _: self._on_start())
        keyboard.on_press_key('F4', lambda _: self._on_pause())
        keyboard.on_press_key('F5', lambda _: self._on_manual_capture())
        keyboard.on_press_key('F6', lambda _: self._on_toggle_mode())
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
    
    def _on_manual_capture(self):
        """Handle F5 - Manual capture"""
        if self.is_running and self.manual_mode:
            self.manual_capture_requested = True
            print(">>> Manual capture requested (F5)")
    
    def _on_toggle_mode(self):
        """Handle F6 - Toggle manual/auto mode"""
        self.manual_mode = not self.manual_mode
        mode_str = "MANUAL" if self.manual_mode else "AUTO"
        print(f">>> Mode switched to: {mode_str}")
        if self.manual_mode:
            print("    Press F5 to capture each screenshot manually")
        else:
            print(f"    Auto-capturing every {self.capture_interval}s")
    
    def capture_screenshot(self, number):
        """Capture a screenshot of the full screen"""
        try:
            # Capture the entire screen
            screenshot = ImageGrab.grab()
            
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
                
                # Manual mode - wait for F5 press
                if self.manual_mode:
                    if self.manual_capture_requested:
                        self.manual_capture_requested = False
                        number = self.missing_numbers[current_index]
                        
                        if self.capture_screenshot(number):
                            current_index += 1
                    
                    time.sleep(0.05)
                    continue
                
                # Auto mode - capture based on time interval
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
    app = FishScreenshotCapture()
    app.run()
