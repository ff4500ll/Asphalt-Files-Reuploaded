"""
Color Picker Tool
Displays RGB color values at cursor position in real-time.
Press ESC to exit.
"""

import pyautogui
import keyboard
import time
import sys


def get_color_at_cursor():
    """Get RGB color at current mouse position"""
    try:
        x, y = pyautogui.position()
        color = pyautogui.pixel(x, y)
        return x, y, color
    except:
        return None, None, (0, 0, 0)


def main():
    print("=" * 60)
    print("COLOR PICKER - Real-time RGB values at cursor")
    print("=" * 60)
    print("Press ESC to exit\n")
    
    try:
        while True:
            # Check if ESC is pressed
            if keyboard.is_pressed('esc'):
                print("\nExiting Color Picker...")
                break
            
            # Get color at cursor
            x, y, color = get_color_at_cursor()
            
            if color:
                r, g, b = color
                
                # Clear line and print color info
                print(f"\rPosition: ({x:4d}, {y:4d}) | RGB: ({r:3d}, {g:3d}, {b:3d}) | "
                      f"Hex: #{r:02X}{g:02X}{b:02X}", end='', flush=True)
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\nExiting Color Picker...")
    except Exception as e:
        print(f"\n\nError: {e}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
