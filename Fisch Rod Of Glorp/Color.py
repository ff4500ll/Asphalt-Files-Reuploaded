import keyboard
from PIL import ImageGrab
import pyautogui
import time

def get_color_at_coordinates():
    print("Press ESC to stop...")
    print("")
    
    try:
        while True:
            # Check if ESC is pressed
            if keyboard.is_pressed('esc'):
                print("\nStopped.")
                break
            
            # Get current mouse position
            x, y = pyautogui.position()
            
            # Get pixel color at mouse position
            screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
            color = screenshot.getpixel((0, 0))
            
            # Format RGB color
            if len(color) == 3:
                r, g, b = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                output = f"Mouse: ({x}, {y}) | RGB: ({r}, {g}, {b}) | Hex: {hex_color}"
            else:
                r, g, b, a = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                output = f"Mouse: ({x}, {y}) | RGB: ({r}, {g}, {b}) | Hex: {hex_color} | Alpha: {a}"
            
            # Print on same line (carriage return)
            print(f"\r{output}", end='', flush=True)
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    get_color_at_coordinates()
