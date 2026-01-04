"""
Color Picker - Shows RGB color at mouse cursor position.
Press ESC to exit.
"""

import sys
import time
from PIL import ImageGrab
from pynput import mouse, keyboard

# Global flag for exit
should_exit = False

def on_press(key):
    """Exit on ESC key."""
    global should_exit
    if key == keyboard.Key.esc:
        should_exit = True
        return False  # Stop listener

def get_color_at_cursor():
    """Get RGB color at current mouse cursor position."""
    # Get current mouse position
    controller = mouse.Controller()
    x, y = controller.position
    
    # Capture 1x1 pixel at cursor position
    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    
    # Get RGB color
    rgb = screenshot.getpixel((0, 0))
    
    return x, y, rgb

def main():
    """Main loop - display color at cursor."""
    print("Color Picker - Hover over any color and see RGB values")
    print("Press ESC to exit\n")
    
    # Start keyboard listener in background
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    try:
        while not should_exit:
            # Get color at cursor
            x, y, rgb = get_color_at_cursor()
            
            # Create output string
            output = f"Position: ({x:4d}, {y:4d}) | RGB: {rgb} | R:{rgb[0]:3d} G:{rgb[1]:3d} B:{rgb[2]:3d}"
            
            # Print with carriage return to overwrite same line
            sys.stdout.write(f"\r{output}")
            sys.stdout.flush()
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)  # 20 updates per second
            
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        print("\n\nExiting Color Picker...")

if __name__ == "__main__":
    main()
