#!/usr/bin/env python3
"""
Color Picker Tool
Tracks the color at the cursor position and displays it in real-time.
Controls:
- F1: Exit the application
- F2: Copy current color to clipboard
- ESC: Exit the application
"""

import tkinter as tk
from tkinter import ttk
import pyautogui
import pyperclip
import keyboard
import time
import threading
import sys
from PIL import ImageGrab

class ColorPicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Color Picker - Cursor Tracking")
        self.root.geometry("320x180")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        # Make window semi-transparent
        self.root.attributes('-alpha', 0.9)
        
        # Variables
        self.current_color = "#000000"
        self.running = True
        
        self.setup_ui()
        self.setup_hotkeys()
        self.start_color_tracking()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎨 Color Picker", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Color display frame
        color_frame = ttk.Frame(main_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Color preview box
        self.color_canvas = tk.Canvas(color_frame, width=60, height=60, relief=tk.RAISED, borderwidth=2)
        self.color_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Color info frame
        info_frame = ttk.Frame(color_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Color values
        ttk.Label(info_frame, text="Hex Color:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.hex_label = ttk.Label(info_frame, text="#000000", font=('Arial', 11), foreground='blue')
        self.hex_label.pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(info_frame, text="RGB Values:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.rgb_label = ttk.Label(info_frame, text="R:0 G:0 B:0", font=('Arial', 10))
        self.rgb_label.pack(anchor=tk.W)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        instructions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(instructions_frame, text="• F1 or ESC: Exit", font=('Arial', 9)).pack(anchor=tk.W)
        ttk.Label(instructions_frame, text="• F2: Copy color to clipboard", font=('Arial', 9)).pack(anchor=tk.W)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Move cursor to pick colors...", 
                                     foreground='gray', font=('Arial', 8))
        self.status_label.pack(pady=(10, 0))
        
    def setup_hotkeys(self):
        """Setup global hotkeys."""
        try:
            keyboard.add_hotkey('f1', self.exit_app)
            keyboard.add_hotkey('esc', self.exit_app)
            keyboard.add_hotkey('f2', self.copy_color)
            print("Hotkeys registered: F1/ESC=Exit, F2=Copy")
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
            
    def start_color_tracking(self):
        """Start the color tracking thread."""
        self.tracking_thread = threading.Thread(target=self.track_color, daemon=True)
        self.tracking_thread.start()
        
    def track_color(self):
        """Continuously track the color at cursor position."""
        while self.running:
            try:
                # Get cursor position
                x, y = pyautogui.position()
                
                # Get pixel color at cursor position
                # Using PIL for more reliable color capture
                screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                pixel_color = screenshot.getpixel((0, 0))
                
                # Convert to hex
                hex_color = "#{:02x}{:02x}{:02x}".format(pixel_color[0], pixel_color[1], pixel_color[2])
                
                # Update UI if color changed
                if hex_color != self.current_color:
                    self.current_color = hex_color
                    self.root.after(0, self.update_color_display, pixel_color, hex_color)
                
                time.sleep(0.05)  # Update 20 times per second
                
            except Exception as e:
                print(f"Error tracking color: {e}")
                time.sleep(0.1)
                
    def update_color_display(self, rgb_color, hex_color):
        """Update the color display in the UI."""
        try:
            # Update color preview
            self.color_canvas.configure(bg=hex_color)
            
            # Update hex label
            self.hex_label.configure(text=hex_color.upper())
            
            # Update RGB label
            self.rgb_label.configure(text=f"R:{rgb_color[0]} G:{rgb_color[1]} B:{rgb_color[2]}")
            
            # Update cursor position in status
            x, y = pyautogui.position()
            self.status_label.configure(text=f"Cursor: ({x}, {y}) | Color: {hex_color.upper()}")
            
        except Exception as e:
            print(f"Error updating display: {e}")
            
    def copy_color(self):
        """Copy current color to clipboard."""
        try:
            # Copy hex color to clipboard
            pyperclip.copy(self.current_color.upper())
            
            # Show feedback
            original_text = self.status_label.cget('text')
            self.status_label.configure(text=f"✓ Copied {self.current_color.upper()} to clipboard!", 
                                       foreground='green')
            
            # Reset status after 2 seconds
            self.root.after(2000, lambda: self.status_label.configure(text=original_text, 
                                                                     foreground='gray'))
            
            print(f"Copied color {self.current_color.upper()} to clipboard")
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            self.status_label.configure(text="Error copying to clipboard!", foreground='red')
            
    def exit_app(self):
        """Exit the application."""
        print("Exiting Color Picker...")
        self.running = False
        
        try:
            # Remove hotkeys
            keyboard.unhook_all()
        except:
            pass
            
        # Close window
        self.root.after(0, self.root.quit)
        
    def run(self):
        """Run the application."""
        try:
            print("Color Picker started!")
            print("Controls:")
            print("- F1 or ESC: Exit")
            print("- F2: Copy current color to clipboard")
            print("Move your cursor around to pick colors...")
            
            # Handle window close button
            self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
            
            # Start the GUI
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.exit_app()
        except Exception as e:
            print(f"Error running application: {e}")
        finally:
            self.running = False
            sys.exit(0)

def main():
    """Main function."""
    try:
        # Check if required modules are available
        import pyautogui
        import pyperclip
        import keyboard
        from PIL import ImageGrab
        
        print("Starting Color Picker Tool...")
        app = ColorPicker()
        app.run()
        
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Please install required packages:")
        print("pip install pyautogui pyperclip keyboard Pillow pywin32")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()