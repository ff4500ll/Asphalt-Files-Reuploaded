"""
Color Picker Script - Click on an image to get RGB/BGR/Hex color values
Usage: Run script, click anywhere on the image to see color values
Press ESC to exit
"""

import cv2
import numpy as np
from PIL import ImageGrab
import tkinter as tk
from tkinter import filedialog

# Global variables
current_color = None
window_name = "Color Picker - Click to get color (ESC to exit)"

def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks to get color at clicked position"""
    global current_color
    image = param
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Get color at clicked position
        bgr_color = image[y, x]
        rgb_color = bgr_color[::-1]  # Reverse BGR to RGB
        
        # Print color information
        print("\n" + "="*60)
        print(f"📍 Clicked position: ({x}, {y})")
        print("-"*60)
        print(f"🎨 RGB: ({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})")
        print(f"🎨 BGR: ({bgr_color[0]}, {bgr_color[1]}, {bgr_color[2]})")
        print(f"🎨 Hex: #{rgb_color[0]:02X}{rgb_color[1]:02X}{rgb_color[2]:02X}")
        print("-"*60)
        print(f"Python code (RGB): np.array([{rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}])")
        print(f"Python code (BGR): np.array([{bgr_color[0]}, {bgr_color[1]}, {bgr_color[2]}])")
        print("="*60)
        
        current_color = bgr_color
        
        # Draw a circle at clicked position and show color
        display_image = image.copy()
        cv2.circle(display_image, (x, y), 10, (0, 0, 255), 2)  # Red circle
        
        # Create small color swatch
        swatch_size = 50
        color_swatch = np.full((swatch_size, swatch_size, 3), bgr_color, dtype=np.uint8)
        
        # Position swatch in top-left corner
        display_image[10:10+swatch_size, 10:10+swatch_size] = color_swatch
        
        # Add text with color values
        text = f"RGB: ({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})"
        cv2.putText(display_image, text, (70, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        cv2.putText(display_image, text, (70, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (0, 0, 0), 1)
        
        cv2.imshow(window_name, display_image)

def main():
    print("\n" + "="*60)
    print("🎨 COLOR PICKER TOOL")
    print("="*60)
    print("This tool helps you identify exact color values from images.")
    print("\nOptions:")
    print("1. Select image file")
    print("2. Capture screen region")
    print("="*60)
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        # File selection
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        root.destroy()
        
        if not file_path:
            print("No file selected. Exiting.")
            return
        
        # Load image
        image = cv2.imread(file_path)
        if image is None:
            print(f"Error: Could not load image from {file_path}")
            return
        
        print(f"\n✓ Loaded image: {file_path}")
        
    elif choice == "2":
        # Screen capture
        print("\n📸 Capturing screen in 3 seconds...")
        print("Position your window/area to capture...")
        import time
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # Capture screen
        screenshot = ImageGrab.grab()
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        print("✓ Screen captured!")
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Display instructions
    print("\n" + "="*60)
    print("📌 INSTRUCTIONS:")
    print("- Click anywhere on the image to see color values")
    print("- Press ESC to exit")
    print("- Press 'r' to reset view")
    print("="*60 + "\n")
    
    # Create window and set mouse callback
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback, image)
    
    # Display image
    cv2.imshow(window_name, image)
    
    # Main loop
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            print("\n👋 Exiting...")
            break
        elif key == ord('r'):  # Reset
            cv2.imshow(window_name, image)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
