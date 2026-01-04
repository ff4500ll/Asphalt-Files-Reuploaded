import tkinter as tk
from tkinter import messagebox
import json
import sys
from pathlib import Path
import keyboard  # pip install keyboard
import mss
import numpy as np
import win32api
import win32con
import time
import threading


class AreaSelector:
    """Transparent draggable and resizable area selector box"""
    
    def __init__(self, parent, initial_box, callback):
        self.callback = callback
        self.parent = parent
        
        # Create transparent window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-alpha', 0.6)  # More visible
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Set initial position and size
        self.x1, self.y1 = initial_box["x1"], initial_box["y1"]
        self.x2, self.y2 = initial_box["x2"], initial_box["y2"]
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        self.window.geometry(f"{width}x{height}+{self.x1}+{self.y1}")
        self.window.configure(bg='green')
        
        # Create canvas for border
        self.canvas = tk.Canvas(self.window, bg='green', highlightthickness=3, 
                               highlightbackground='lime')
        self.canvas.pack(fill='both', expand=True)
        
        # Mouse state
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        self.resize_threshold = 20
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
    def on_mouse_move(self, event):
        """Change cursor based on position"""
        x, y = event.x, event.y
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Check if near edges for resizing
        at_left = x < self.resize_threshold
        at_right = x > width - self.resize_threshold
        at_top = y < self.resize_threshold
        at_bottom = y > height - self.resize_threshold
        
        if at_left and at_top:
            self.canvas.config(cursor='top_left_corner')
        elif at_right and at_top:
            self.canvas.config(cursor='top_right_corner')
        elif at_left and at_bottom:
            self.canvas.config(cursor='bottom_left_corner')
        elif at_right and at_bottom:
            self.canvas.config(cursor='bottom_right_corner')
        elif at_left or at_right:
            self.canvas.config(cursor='sb_h_double_arrow')
        elif at_top or at_bottom:
            self.canvas.config(cursor='sb_v_double_arrow')
        else:
            self.canvas.config(cursor='fleur')
    
    def on_mouse_down(self, event):
        """Start dragging or resizing"""
        self.start_x = event.x
        self.start_y = event.y
        
        x, y = event.x, event.y
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Check if clicking near edges for resizing
        at_left = x < self.resize_threshold
        at_right = x > width - self.resize_threshold
        at_top = y < self.resize_threshold
        at_bottom = y > height - self.resize_threshold
        
        if at_left or at_right or at_top or at_bottom:
            self.resizing = True
            self.resize_edge = {
                'left': at_left,
                'right': at_right,
                'top': at_top,
                'bottom': at_bottom
            }
        else:
            self.dragging = True
    
    def on_mouse_drag(self, event):
        """Handle dragging or resizing"""
        if self.dragging:
            # Move window
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            
            new_x = self.window.winfo_x() + dx
            new_y = self.window.winfo_y() + dy
            
            self.window.geometry(f"+{new_x}+{new_y}")
            
        elif self.resizing:
            # Resize window
            current_x = self.window.winfo_x()
            current_y = self.window.winfo_y()
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            
            new_x = current_x
            new_y = current_y
            new_width = current_width
            new_height = current_height
            
            if self.resize_edge['left']:
                dx = event.x - self.start_x
                new_x = current_x + dx
                new_width = current_width - dx
            elif self.resize_edge['right']:
                new_width = event.x
            
            if self.resize_edge['top']:
                dy = event.y - self.start_y
                new_y = current_y + dy
                new_height = current_height - dy
            elif self.resize_edge['bottom']:
                new_height = event.y
            
            # Minimum size
            if new_width < 50:
                new_width = 50
                new_x = current_x
            if new_height < 50:
                new_height = 50
                new_y = current_y
            
            self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    
    def on_mouse_up(self, event):
        """Stop dragging or resizing"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
    
    def close(self):
        """Close the area selector and return coordinates"""
        x1 = self.window.winfo_x()
        y1 = self.window.winfo_y()
        x2 = x1 + self.window.winfo_width()
        y2 = y1 + self.window.winfo_height()
        
        coords = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        self.callback(coords)
        self.window.destroy()


class FORGEMacro:
    def __init__(self, root):
        self.root = root
        self.root.title("FORGE Macro")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Determine the correct settings path for both dev and exe
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.settings_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.settings_dir = Path(__file__).parent
        
        self.settings_file = self.settings_dir / "FORGEsettings.json"
        
        # Get screen resolution
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Default keybindings
        self.default_bindings = {
            "start_stop": "F1",
            "change_area": "F2",
            "exit": "F3"
        }
        
        # Area selector (initialize before loading settings)
        self.area_selector = None
        self.area_box = {
            "x1": 182,
            "y1": 184,
            "x2": 2396,
            "y2": 1045
        }
        
        # Target color RGB
        self.target_color = (10, 172, 10)
        self.color_tolerance = 70
        
        # Load settings
        self.keybindings = self.load_settings()
        
        # Running state
        self.is_running = False
        self.area_change_enabled = False
        self.main_thread = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
    def load_settings(self):
        """Load keybindings and area box from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Load area box if exists
                    if 'area_box' in settings:
                        self.area_box = settings['area_box']
                    return settings.get("keybindings", self.default_bindings)
        except Exception as e:
            messagebox.showwarning("Settings", f"Could not load settings: {e}\nUsing defaults.")
        return self.default_bindings.copy()
    
    def save_settings(self):
        """Save keybindings and area box to JSON file"""
        try:
            settings = {
                "keybindings": self.keybindings,
                "area_box": self.area_box
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")
            return False
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Title
        tk.Label(self.root, text="FORGE Macro", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Start/Stop
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=2)
        tk.Button(frame1, text=f"Start/Stop ({self.keybindings['start_stop']})", 
                 command=self.toggle_start_stop, width=20).pack(side="left", padx=2)
        tk.Button(frame1, text="Rebind", command=lambda: self.rebind_key("start_stop"), 
                 width=8).pack(side="left")
        
        # Change Area
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=2)
        tk.Button(frame2, text=f"Change Area ({self.keybindings['change_area']})", 
                 command=self.change_area, width=20).pack(side="left", padx=2)
        tk.Button(frame2, text="Rebind", command=lambda: self.rebind_key("change_area"), 
                 width=8).pack(side="left")
        
        # Exit
        frame3 = tk.Frame(self.root)
        frame3.pack(pady=2)
        tk.Button(frame3, text=f"Exit ({self.keybindings['exit']})", 
                 command=self.exit_app, width=20).pack(side="left", padx=2)
        tk.Button(frame3, text="Rebind", command=lambda: self.rebind_key("exit"), 
                 width=8).pack(side="left")
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=10)
    
    def find_color_position(self, image_array, target_color, tolerance):
        """Find leftmost, rightmost, topmost, bottommost positions and return center"""
        target_r, target_g, target_b = target_color
        
        # Create a mask where the color matches (with tolerance)
        if tolerance == 0:
            mask = (image_array[:, :, 2] == target_r) & \
                   (image_array[:, :, 1] == target_g) & \
                   (image_array[:, :, 0] == target_b)
        else:
            mask = (np.abs(image_array[:, :, 2] - target_r) <= tolerance) & \
                   (np.abs(image_array[:, :, 1] - target_g) <= tolerance) & \
                   (np.abs(image_array[:, :, 0] - target_b) <= tolerance)
        
        # Find all positions where the color appears
        positions = np.argwhere(mask)
        
        if len(positions) == 0:
            return None
        
        # Get x and y coordinates (columns and rows)
        y_coords = positions[:, 0]
        x_coords = positions[:, 1]
        
        # Find leftmost and rightmost x positions
        leftmost_x = int(np.min(x_coords))
        rightmost_x = int(np.max(x_coords))
        
        # Find topmost and bottommost y positions
        topmost_y = int(np.min(y_coords))
        bottommost_y = int(np.max(y_coords))
        
        # Calculate center
        center_x = (leftmost_x + rightmost_x) // 2
        center_y = (topmost_y + bottommost_y) // 2
        
        return (center_x, center_y)  # x, y
    
    def main_loop(self):
        """Main macro loop - runs continuously when is_running is True"""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    # Get area box coordinates
                    x1, y1 = self.area_box["x1"], self.area_box["y1"]
                    x2, y2 = self.area_box["x2"], self.area_box["y2"]
                    
                    # Define the screen region to capture
                    monitor = {
                        "top": y1,
                        "left": x1,
                        "width": x2 - x1,
                        "height": y2 - y1
                    }
                    
                    # Capture the screen region
                    screenshot = sct.grab(monitor)
                    
                    # Convert to numpy array (BGR format)
                    img_array = np.array(screenshot)
                    
                    # Find color position
                    position = self.find_color_position(img_array, self.target_color, self.color_tolerance)
                    
                    print("Scanning...")
                    
                    if position:
                        # Calculate screen coordinates
                        screen_x = x1 + position[0]
                        screen_y = y1 + position[1]
                        
                        print(f"Color found at ({screen_x}, {screen_y}), clicking...")
                        
                        # Wait 100ms before clicking
                        time.sleep(0.1)
                        
                        # Move cursor to position
                        win32api.SetCursorPos((screen_x, screen_y))
                        
                        # Anti-roblox: perform a tiny relative move so the client registers the click
                        try:
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        except:
                            pass
                        
                        # Click instantly
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        
                        # Wait 300ms after clicking
                        time.sleep(0.3)
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(0.1)
    
    def toggle_start_stop(self):
        """Toggle the start/stop state"""
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running", fg="green")
            print("Macro started!")
            # Start the main loop in a separate thread
            self.main_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.main_thread.start()
        else:
            self.status_label.config(text="Status: Stopped", fg="red")
            print("Macro stopped!")
    
    def change_area(self):
        """Toggle area selector on/off"""
        if self.area_selector is None:
            # Open area selector
            self.area_change_enabled = True
            self.status_label.config(text="Drag area box (Press F2 to save)")
            self.area_selector = AreaSelector(self.root, self.area_box, self.on_area_selected)
        else:
            # Close and save area selector
            self.area_selector.close()
            self.area_selector = None
            self.area_change_enabled = False
            self.status_label.config(text="Area saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped",
                fg="green" if self.is_running else "red"
            ))
    
    def on_area_selected(self, coords):
        """Called when area selection is complete"""
        self.area_box = coords
        self.save_settings()
        print(f"Area Box saved: {self.area_box}")
    
    def exit_app(self):
        """Exit the application"""
        self.is_running = False  # Stop any running loops
        keyboard.unhook_all()  # Remove all hotkeys
        self.root.quit()  # Stop the mainloop
        self.root.destroy()  # Destroy the window
        sys.exit(0)  # Exit the program completely
    
    def rebind_key(self, action):
        """Rebind a key for an action"""
        self.status_label.config(text=f"Press a key for {action.replace('_', ' ').title()}...", fg="blue")
        
        def on_key_event(event):
            new_key = event.name.upper()
            # Update the keybinding
            self.keybindings[action] = new_key
            if self.save_settings():
                self.status_label.config(text=f"Rebound to {new_key}", fg="green")
                self.update_button_labels()
                self.refresh_hotkeys()  # Refresh hotkeys with new binding
                
                # Clear message after 2 seconds
                self.root.after(2000, lambda: self.status_label.config(
                    text="Status: Running" if self.is_running else "Status: Stopped",
                    fg="green" if self.is_running else "red"
                ))
            
            # Unhook this temporary listener
            keyboard.unhook(hook)
        
        # Hook to capture the next key press
        hook = keyboard.on_press(on_key_event, suppress=False)
    
    def update_button_labels(self):
        """Update GUI after rebinding - recreate widgets"""
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        # Recreate widgets with new keybindings
        self.create_widgets()
    
    def setup_hotkeys(self):
        """Setup global hotkeys that work even when minimized"""
        try:
            # Remove any existing hotkeys first
            keyboard.unhook_all()
            
            # Add hotkeys
            keyboard.add_hotkey(self.keybindings['start_stop'].lower(), self.toggle_start_stop)
            keyboard.add_hotkey(self.keybindings['change_area'].lower(), self.change_area)
            keyboard.add_hotkey(self.keybindings['exit'].lower(), self.exit_app)
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def refresh_hotkeys(self):
        """Refresh hotkeys after rebinding"""
        self.setup_hotkeys()


if __name__ == "__main__":
    root = tk.Tk()
    app = FORGEMacro(root)
    root.mainloop()
