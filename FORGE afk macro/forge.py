import tkinter as tk
from tkinter import messagebox
import json
import sys
from pathlib import Path
import keyboard  # pip install keyboard
import threading
import mss
import numpy as np
import time
import win32api
import win32con
import win32gui
import webbrowser


class AreaSelector:
    """Transparent draggable and resizable area selector box"""
    
    def __init__(self, parent, initial_box, callback, title="Area"):
        self.callback = callback
        self.parent = parent
        self.title = title
        
        # Create transparent window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-alpha', 0.6)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # Set initial position and size
        self.x1, self.y1 = initial_box["x1"], initial_box["y1"]
        self.x2, self.y2 = initial_box["x2"], initial_box["y2"]
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        self.window.geometry(f"{width}x{height}+{self.x1}+{self.y1}")
        self.window.configure(bg='green')
        
        # Create canvas for border and title
        self.canvas = tk.Canvas(self.window, bg='green', highlightthickness=3, 
                               highlightbackground='lime')
        self.canvas.pack(fill='both', expand=True)
        
        # Add title label
        self.title_label = tk.Label(self.window, text=title, bg='green', fg='white', 
                                    font=('Arial', 14, 'bold'))
        self.title_label.place(x=10, y=10)
        
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
        self.root.geometry("300x300")
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
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        
        # Reference resolution (2560x1440) - the resolution these default coordinates are designed for
        self.reference_width = 2560
        self.reference_height = 1440
        
        # Calculate scale factors for resolution adjustment
        self.scale_x = self.screen_width / self.reference_width
        self.scale_y = self.screen_height / self.reference_height
        
        # Default keybindings
        self.default_bindings = {
            "start_stop": "F1",
            "change_area": "F2",
            "exit": "F3"
        }
        
        # Area boxes for Fill, Pour, and Forge (default coordinates for 2560x1440)
        self.area_selectors = []
        self.default_areas = {
            "fill": {"x1": 388, "y1": 489, "x2": 593, "y2": 993},
            "pour": {"x1": 2270, "y1": 236, "x2": 2406, "y2": 1211},
            "forge": {"x1": 355, "y1": 356, "x2": 2271, "y2": 1063}
        }
        
        # Scale default areas if not at reference resolution
        self.areas = self.scale_areas(self.default_areas)
        
        # Load settings
        self.keybindings = self.load_settings()
        
        # Running state
        self.is_running = False
        self.area_change_enabled = False
        self.main_thread = None
        
        # Green tolerance for Forge stage
        self.green_tolerance = 10
        
        # Fast Forge Gamepass mode
        self.fast_forge_mode = False
        
        # Create GUI elements
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
    def scale_areas(self, areas):
        """Scale area coordinates based on current resolution"""
        if self.scale_x == 1.0 and self.scale_y == 1.0:
            return areas
        
        scaled_areas = {}
        for area_name, coords in areas.items():
            scaled_areas[area_name] = {
                "x1": int(coords["x1"] * self.scale_x),
                "y1": int(coords["y1"] * self.scale_y),
                "x2": int(coords["x2"] * self.scale_x),
                "y2": int(coords["y2"] * self.scale_y)
            }
        return scaled_areas
    
    def scale_coordinate(self, x, y):
        """Scale a single coordinate based on current resolution"""
        return int(x * self.scale_x), int(y * self.scale_y)
    
    def load_settings(self):
        """Load keybindings and areas from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Load areas if exist, and scale them if needed
                    if 'areas' in settings:
                        loaded_areas = settings['areas']
                        # Check if areas need scaling (assuming saved at reference resolution)
                        if self.scale_x != 1.0 or self.scale_y != 1.0:
                            self.areas = self.scale_areas(loaded_areas)
                        else:
                            self.areas = loaded_areas
                    # Load green tolerance if exists
                    if 'green_tolerance' in settings:
                        self.green_tolerance = settings['green_tolerance']
                    # Load fast forge mode if exists
                    if 'fast_forge_mode' in settings:
                        self.fast_forge_mode = settings['fast_forge_mode']
                    return settings.get("keybindings", self.default_bindings)
        except Exception as e:
            messagebox.showwarning("Settings", f"Could not load settings: {e}\nUsing defaults.")
        return self.default_bindings.copy()
    
    def save_settings(self):
        """Save keybindings and areas to JSON file"""
        try:
            settings = {
                "keybindings": self.keybindings,
                "areas": self.areas,
                "green_tolerance": self.green_tolerance,
                "fast_forge_mode": self.fast_forge_mode
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
        tk.Label(self.root, text="FORGE Macro - by AsphaltCake", font=("Arial", 12, "bold")).pack(pady=10)
        
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
        
        # Green Tolerance for Forge
        tk.Label(self.root, text="Forge Green Tolerance:", font=("Arial", 10, "bold")).pack(pady=(10,5))
        tolerance_frame = tk.Frame(self.root)
        tolerance_frame.pack(pady=5)
        tk.Label(tolerance_frame, text="Tolerance:").pack(side="left", padx=5)
        self.green_tolerance_entry = tk.Entry(tolerance_frame, width=10)
        self.green_tolerance_entry.insert(0, str(self.green_tolerance))
        self.green_tolerance_entry.pack(side="left", padx=5)
        tk.Button(tolerance_frame, text="Save", command=self.save_green_tolerance, width=8).pack(side="left", padx=5)
        
        # Fast Forge Gamepass checkbox
        self.fast_forge_var = tk.BooleanVar(value=self.fast_forge_mode)
        fast_forge_check = tk.Checkbutton(self.root, text="Fast Forge Gamepass", 
                                         variable=self.fast_forge_var, 
                                         command=self.toggle_fast_forge)
        fast_forge_check.pack(pady=10)
    
    def toggle_fast_forge(self):
        """Toggle Fast Forge Gamepass mode"""
        self.fast_forge_mode = self.fast_forge_var.get()
        self.save_settings()
        mode_status = "enabled" if self.fast_forge_mode else "disabled"
        print(f"Fast Forge Gamepass mode {mode_status}")
    
    def save_green_tolerance(self):
        """Save the green tolerance value"""
        try:
            tolerance = int(self.green_tolerance_entry.get())
            if tolerance < 0:
                messagebox.showerror("Error", "Tolerance must be 0 or greater")
                return
            self.green_tolerance = tolerance
            self.save_settings()
            messagebox.showinfo("Success", f"Green tolerance set to {tolerance}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def fast_forge_loop(self):
        """Fast Forge Gamepass mode - only scan for green circles and click forever"""
        with mss.mss() as sct:
            if self.is_running:
                self.root.after(0, lambda: self.status_label.config(text="Status: Fast Forge Mode", fg="purple"))
            print("Fast Forge Gamepass mode active - scanning for white color only...")
            
            # Get Forge area coordinates
            forge_x1 = self.areas["forge"]["x1"]
            forge_y1 = self.areas["forge"]["y1"]
            forge_x2 = self.areas["forge"]["x2"]
            forge_y2 = self.areas["forge"]["y2"]
            
            forge_monitor = {
                "top": forge_y1,
                "left": forge_x1,
                "width": forge_x2 - forge_x1,
                "height": forge_y2 - forge_y1
            }
            
            # Target white color RGB(247, 247, 247)
            white_r, white_g, white_b = 247, 247, 247
            white_tolerance = 10
            
            # Move cursor to bottom middle of Forge area to avoid blocking view
            forge_bottom_middle_x = (forge_x1 + forge_x2) // 2
            forge_bottom_middle_y = forge_y2 - 10
            win32api.SetCursorPos((forge_bottom_middle_x, forge_bottom_middle_y))
            
            # Click threshold: 150 pixels height (scaled for resolution)
            click_height_threshold = int(150 * max(self.scale_x, self.scale_y))
            
            while self.is_running:
                try:
                    # Scan forge area for white color
                    screenshot = sct.grab(forge_monitor)
                    img_array = np.array(screenshot)
                    
                    # Check for white color
                    white_mask = (np.abs(img_array[:, :, 2] - white_r) <= white_tolerance) & \
                                (np.abs(img_array[:, :, 1] - white_g) <= white_tolerance) & \
                                (np.abs(img_array[:, :, 0] - white_b) <= white_tolerance)
                    
                    if np.any(white_mask):
                        # Get top and bottom pixels of white color
                        white_positions = np.argwhere(white_mask)
                        min_y = white_positions[:, 0].min()
                        max_y = white_positions[:, 0].max()
                        
                        # Calculate height (vertical distance from top to bottom)
                        height = max_y - min_y
                        
                        # Calculate middle Y coordinate (between top and bottom)
                        middle_y = (min_y + max_y) // 2
                        middle_x = int(np.mean(white_positions[:, 1]))
                        
                        # Convert to screen coordinates
                        screen_x = forge_x1 + middle_x
                        screen_y = forge_y1 + middle_y
                        
                        # Print every loop iteration
                        print(f"Top: {forge_y1 + min_y}, Bottom: {forge_y1 + max_y}, Height: {height}px")
                        
                        # Check if height is less than threshold
                        if height < click_height_threshold:
                            print(f"Height < {click_height_threshold}px! Clicking at middle ({screen_x}, {screen_y})")
                            
                            win32api.SetCursorPos((screen_x, screen_y))
                            try:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            except:
                                pass
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            
                            # Wait 200ms before continuing
                            time.sleep(0.2)
                            
                            # Move cursor back to bottom middle
                            win32api.SetCursorPos((forge_bottom_middle_x, forge_bottom_middle_y))
                    
                    time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                    
                except Exception as e:
                    print(f"Error in fast forge loop: {e}")
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
    
    def main_loop(self):
        """Main macro loop - runs continuously when is_running is True"""
        # Check if Fast Forge Gamepass mode is enabled
        if self.fast_forge_mode:
            self.fast_forge_loop()
            return
        
        with mss.mss() as sct:
            while self.is_running:
                try:
                    # Get Fill area coordinates
                    x1 = self.areas["fill"]["x1"]
                    y1 = self.areas["fill"]["y1"]
                    x2 = self.areas["fill"]["x2"]
                    y2 = self.areas["fill"]["y2"]
                    
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
                    
                    # Target color RGB (109, 174, 32)
                    target_r, target_g, target_b = 109, 174, 32
                    tolerance = 10
                    
                    # Create a mask where the color matches
                    mask = (np.abs(img_array[:, :, 2] - target_r) <= tolerance) & \
                           (np.abs(img_array[:, :, 1] - target_g) <= tolerance) & \
                           (np.abs(img_array[:, :, 0] - target_b) <= tolerance)
                    
                    # Check if color found
                    if np.any(mask):
                        if self.is_running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Filling", fg="blue"))
                        print("Green color found in Fill area!")
                        
                        # Find first position of green
                        positions = np.argwhere(mask)
                        first_pos = positions[0]
                        
                        # Calculate screen coordinates of green
                        green_x = x1 + first_pos[1]
                        green_y = y1 + first_pos[0]
                        
                        # Move cursor to green position
                        win32api.SetCursorPos((green_x, green_y))
                        
                        # Anti-roblox: relative move down by 1 pixel
                        try:
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        except:
                            pass
                        
                        # Hold left click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        
                        # Calculate middle X and top/bottom Y for alternating
                        middle_x = (x1 + x2) // 2
                        top_y = y1
                        bottom_y = y2
                        
                        # Alternate between top and bottom until green disappears
                        at_top = True
                        while self.is_running:
                            # Capture and check for green
                            screenshot = sct.grab(monitor)
                            img_array = np.array(screenshot)
                            
                            mask = (np.abs(img_array[:, :, 2] - target_r) <= tolerance) & \
                                   (np.abs(img_array[:, :, 1] - target_g) <= tolerance) & \
                                   (np.abs(img_array[:, :, 0] - target_b) <= tolerance)
                            
                            # If green is gone, break
                            if not np.any(mask):
                                print("Green disappeared!")
                                break
                            
                            # Alternate between top and bottom
                            if at_top:
                                win32api.SetCursorPos((middle_x, bottom_y))
                                # Anti-roblox move
                                try:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                except:
                                    pass
                                at_top = False
                            else:
                                win32api.SetCursorPos((middle_x, top_y))
                                # Anti-roblox move
                                try:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                except:
                                    pass
                                at_top = True
                        
                        # Release left click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        print("Released click! Fill complete, moving to Pour stage...")
                        if self.is_running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Waiting For Pour", fg="orange"))
                        
                        # STAGE 2: POUR
                        # Get Pour area coordinates
                        pour_x1 = self.areas["pour"]["x1"]
                        pour_y1 = self.areas["pour"]["y1"]
                        pour_x2 = self.areas["pour"]["x2"]
                        pour_y2 = self.areas["pour"]["y2"]
                        
                        pour_monitor = {
                            "top": pour_y1,
                            "left": pour_x1,
                            "width": pour_x2 - pour_x1,
                            "height": pour_y2 - pour_y1
                        }
                        
                        # Wait for yellow color RGB: (183, 164, 74)
                        yellow_r, yellow_g, yellow_b = 183, 164, 74
                        white_r, white_g, white_b = 207, 207, 207
                        yellow_tolerance = 10
                        white_tolerance = 10
                        
                        print("Waiting for yellow in Pour area...")
                        yellow_found = False
                        while self.is_running and not yellow_found:
                            screenshot = sct.grab(pour_monitor)
                            img_array = np.array(screenshot)
                            
                            yellow_mask = (np.abs(img_array[:, :, 2] - yellow_r) <= yellow_tolerance) & \
                                         (np.abs(img_array[:, :, 1] - yellow_g) <= yellow_tolerance) & \
                                         (np.abs(img_array[:, :, 0] - yellow_b) <= yellow_tolerance)
                            
                            if np.any(yellow_mask):
                                print("Yellow found in Pour area!")
                                if self.is_running:
                                    self.root.after(0, lambda: self.status_label.config(text="Status: Pouring", fg="blue"))
                                yellow_found = True
                        
                        # Pour stage: compare yellow and white Y positions
                        click_held = False
                        while self.is_running:
                            screenshot = sct.grab(pour_monitor)
                            img_array = np.array(screenshot)
                            
                            # Check for yellow
                            yellow_mask = (np.abs(img_array[:, :, 2] - yellow_r) <= yellow_tolerance) & \
                                         (np.abs(img_array[:, :, 1] - yellow_g) <= yellow_tolerance) & \
                                         (np.abs(img_array[:, :, 0] - yellow_b) <= yellow_tolerance)
                            
                            # If yellow disappeared, break
                            if not np.any(yellow_mask):
                                print("Yellow disappeared! Pour complete, moving to Forge stage...")
                                # Make sure to release click if held
                                if click_held:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                break
                            
                            # Find middle of yellow
                            yellow_positions = np.argwhere(yellow_mask)
                            yellow_middle_y = int(np.mean(yellow_positions[:, 0]))
                            yellow_middle_x = int(np.mean(yellow_positions[:, 1]))
                            
                            # Check for white
                            white_mask = (np.abs(img_array[:, :, 2] - white_r) <= white_tolerance) & \
                                        (np.abs(img_array[:, :, 1] - white_g) <= white_tolerance) & \
                                        (np.abs(img_array[:, :, 0] - white_b) <= white_tolerance)
                            
                            if np.any(white_mask):
                                # Find middle of white
                                white_positions = np.argwhere(white_mask)
                                white_middle_y = int(np.mean(white_positions[:, 0]))
                                white_middle_x = int(np.mean(white_positions[:, 1]))
                                
                                # Compare Y coordinates
                                if white_middle_y > yellow_middle_y:
                                    # White is below yellow - hold left click
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    click_held = True
                                    print("Holding click - white below yellow")
                                else:
                                    # White is above yellow - release left click
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    click_held = False
                                    print("Released click - white above yellow")
                        
                        # STAGE 3: FORGE
                        print("Starting Forge stage...")
                        if self.is_running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Waiting For Forge", fg="orange"))
                        
                        # Wait 2 seconds
                        time.sleep(4)
                        
                        # Spam click at 9 grid positions for 3 seconds (scaled for resolution)
                        # Reference positions for 2560x1440: X [1100, 1300, 1500], Y [500, 700, 900]
                        forge_click_positions = []
                        for y in [500, 700, 900]:
                            for x in [1100, 1300, 1500]:
                                forge_click_positions.append((
                                    int(x * self.scale_x),
                                    int(y * self.scale_y)
                                ))
                        
                        click_index = 0
                        print(f"Spam clicking at 9 grid positions (scaled for {self.screen_width}x{self.screen_height})...")
                        
                        start_time = time.time()
                        while time.time() - start_time < 3:
                            forge_click_x, forge_click_y = forge_click_positions[click_index]
                            win32api.SetCursorPos((forge_click_x, forge_click_y))
                            try:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            except:
                                pass
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            # Cycle through the 9 grid positions
                            click_index = (click_index + 1) % 9
                            time.sleep(0.001)  # 1ms delay to prevent lag
                        
                        print("Forge clicking complete, watching for circles...")
                        if self.is_running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Forging", fg="blue"))
                        
                        # Check for circles in Forge area
                        forge_x1 = self.areas["forge"]["x1"]
                        forge_y1 = self.areas["forge"]["y1"]
                        forge_x2 = self.areas["forge"]["x2"]
                        forge_y2 = self.areas["forge"]["y2"]
                        
                        forge_monitor = {
                            "top": forge_y1,
                            "left": forge_x1,
                            "width": forge_x2 - forge_x1,
                            "height": forge_y2 - forge_y1
                        }
                        
                        # Green color for circles
                        green_r, green_g, green_b = 11, 172, 10
                        green_tolerance = self.green_tolerance
                        
                        # Move cursor to bottom middle of Forge area to avoid covering circles
                        forge_bottom_middle_x = (forge_x1 + forge_x2) // 2
                        forge_bottom_middle_y = forge_y2 - 10
                        win32api.SetCursorPos((forge_bottom_middle_x, forge_bottom_middle_y))
                        
                        # Track last click time for exit condition
                        last_click_time = time.time()
                        
                        # Target white color RGB(247, 247, 247)
                        white_r, white_g, white_b = 247, 247, 247
                        white_tolerance = 10
                        
                        # Click threshold: 150 pixels height (scaled for resolution)
                        click_height_threshold = int(150 * max(self.scale_x, self.scale_y))
                        
                        while self.is_running:
                            # Scan full forge area for white color
                            screenshot = sct.grab(forge_monitor)
                            img_array = np.array(screenshot)
                            
                            # Check if 8 seconds have passed without clicking
                            if time.time() - last_click_time > 8:
                                print("No clicks for 8 seconds, exiting Forge stage...")
                                break
                            
                            # Check for white color
                            white_mask = (np.abs(img_array[:, :, 2] - white_r) <= white_tolerance) & \
                                        (np.abs(img_array[:, :, 1] - white_g) <= white_tolerance) & \
                                        (np.abs(img_array[:, :, 0] - white_b) <= white_tolerance)
                            
                            if np.any(white_mask):
                                # Get top and bottom pixels of white color
                                white_positions = np.argwhere(white_mask)
                                min_y = white_positions[:, 0].min()
                                max_y = white_positions[:, 0].max()
                                
                                # Calculate height (vertical distance from top to bottom)
                                height = max_y - min_y
                                
                                # Calculate middle Y coordinate (between top and bottom)
                                middle_y = (min_y + max_y) // 2
                                middle_x = int(np.mean(white_positions[:, 1]))
                                
                                # Convert to screen coordinates
                                screen_x = forge_x1 + middle_x
                                screen_y = forge_y1 + middle_y
                                
                                # Print every loop iteration
                                print(f"Top: {forge_y1 + min_y}, Bottom: {forge_y1 + max_y}, Height: {height}px")
                                
                                # Check if height is less than threshold
                                if height < click_height_threshold:
                                    print(f"Height < {click_height_threshold}px! Clicking at middle ({screen_x}, {screen_y})")
                                    
                                    win32api.SetCursorPos((screen_x, screen_y))
                                    try:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                    except:
                                        pass
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    
                                    # Update last click time
                                    last_click_time = time.time()
                                    
                                    # Wait 200ms before continuing
                                    time.sleep(0.5)
                                    
                                    # Move cursor back to bottom middle
                                    win32api.SetCursorPos((forge_bottom_middle_x, forge_bottom_middle_y))
                        
                    else:
                        if self.is_running:
                            self.root.after(0, lambda: self.status_label.config(text="Status: Waiting For Fill", fg="orange"))
                        print("Scanning Fill area...")
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
    
    def change_area(self):
        """Toggle area selectors on/off"""
        if len(self.area_selectors) == 0:
            # Open all 3 area selectors
            self.area_change_enabled = True
            self.status_label.config(text="Drag area boxes (Press F2 to save)")
            
            # Create selectors for Fill, Pour, and Forge
            self.area_selectors.append(
                AreaSelector(self.root, self.areas["fill"], 
                           lambda coords: self.on_area_selected("fill", coords), "Fill")
            )
            self.area_selectors.append(
                AreaSelector(self.root, self.areas["pour"], 
                           lambda coords: self.on_area_selected("pour", coords), "Pour")
            )
            self.area_selectors.append(
                AreaSelector(self.root, self.areas["forge"], 
                           lambda coords: self.on_area_selected("forge", coords), "Forge")
            )
        else:
            # Close all area selectors
            for selector in self.area_selectors:
                selector.close()
            self.area_selectors.clear()
            self.area_change_enabled = False
            self.status_label.config(text="Areas saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped",
                fg="green" if self.is_running else "red"
            ))
    
    def on_area_selected(self, area_name, coords):
        """Called when area selection is complete"""
        self.areas[area_name] = coords
        self.save_settings()
        print(f"{area_name.capitalize()} area saved: {coords}")
    
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


def auto_subscribe_to_youtube():
    """
    Attempt to auto-subscribe to YouTube channel.
    Opens browser with subscribe link and attempts automated subscription.
    """
    YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@AsphaltCake?sub_confirmation=1"
    
    print("\n" + "="*50)
    print("AUTO-SUBSCRIBE TO YOUTUBE CHANNEL")
    print("="*50)
    
    try:
        # Open YouTube channel with subscribe confirmation
        print(f"🌐 Opening YouTube channel in browser...")
        webbrowser.open(YOUTUBE_CHANNEL_URL)
        
        # Wait for browser to load
        print("⏳ Waiting for browser to load...")
        start_time = time.time()
        browser_found = False
        
        # Try to find browser window (timeout after a few seconds)
        while time.time() - start_time < 5:
            try:
                def window_enum_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        browser_keywords = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave', 'YouTube']
                        if any(keyword.lower() in window_text.lower() for keyword in browser_keywords):
                            windows.append((hwnd, window_text))
                    return True
                
                windows = []
                win32gui.EnumWindows(window_enum_callback, windows)
                
                if windows:
                    browser_found = True
                    print(f"✅ Browser window found: {windows[0][1]}")
                    break
                
                time.sleep(0.2)
            except Exception as e:
                print(f"⚠️ Error checking for browser: {e}")
                break
        
        if not browser_found:
            print("⚠️ Browser window not detected, continuing anyway...")
            time.sleep(3)
            return False
        
        # Wait for YouTube page to load
        print("⏳ Waiting for YouTube page to load...")
        time.sleep(3.5)
        
        # Try to focus browser window
        print("🖱️ Attempting to focus browser...")
        try:
            if windows:
                hwnd = windows[0][0]
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Could not focus browser: {e}")
        
        # Navigate to subscribe button using Tab and Enter
        print("🧭 Navigating to Subscribe button...")
        try:
            keyboard.press_and_release('tab')
            time.sleep(0.2)
            keyboard.press_and_release('tab')
            time.sleep(0.2)
            keyboard.press_and_release('enter')
            time.sleep(0.5)
            
            print("✅ Subscribe sequence executed!")
        except Exception as e:
            print(f"⚠️ Error during navigation: {e}")
        
        # Close the tab
        print("❌ Closing YouTube tab...")
        try:
            keyboard.press_and_release('ctrl+w')
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Error closing tab: {e}")
        
        print("✅ Auto-subscribe sequence completed!")
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Auto-subscribe failed: {e}")
        print("Continuing to main application...")
        return False


def show_terms_and_conditions():
    """Show terms of use dialog on first launch - must accept to continue"""
    # Create temporary root for dialog
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    # Message text
    message = """═════════════════════════════════════════════════════
           FORGE MACRO - TERMS OF USE
                    by AsphaltCake
═════════════════════════════════════════════════════

⚠️ IMPORTANT NOTICE ⚠️

This application is NOT a virus or malware!
  • Forge automation tool for Roblox GPO
  • Antivirus may flag it (automates mouse/keyboard - this is normal)
  • Safe to use - built with Python 3.14 & PyInstaller
  • You can decompile it if you want to verify the code
  • No data collection or malicious behavior

═════════════════════════════════════════════════════

BY USING THIS SOFTWARE:
  ✓ You understand this is automation software
  ✓ You will NOT redistribute as your own work
  ✓ You will credit AsphaltCake if sharing/modifying

═════════════════════════════════════════════════════

ON FIRST LAUNCH:
  • Opens YouTube (AsphaltCake's channel) in browser
  • Auto-clicks Subscribe button to support the creator
  • Closes browser tab automatically

═════════════════════════════════════════════════════

ACCEPT: Agree to terms & continue (auto-subscribes)
DECLINE: Exit application

Creator: AsphaltCake (@AsphaltCake on YouTube)"""
    
    # Show messagebox with Yes/No
    result = messagebox.askyesno(
        "Terms of Use - FORGE Macro",
        message,
        icon='info'
    )
    
    temp_root.destroy()
    return result


def main():
    # Check if settings file exists
    if getattr(sys, 'frozen', False):
        settings_dir = Path(sys.executable).parent
    else:
        settings_dir = Path(__file__).parent
    
    settings_file = settings_dir / "FORGEsettings.json"
    
    # If settings don't exist, show terms and do auto-subscribe
    if not settings_file.exists():
        print("\n🎉 First launch detected - showing terms...")
        
        # Show terms dialog - must accept to continue
        if not show_terms_and_conditions():
            print("User declined terms - exiting application...")
            sys.exit(0)  # Exit if they decline
        
        print("Terms accepted - proceeding with auto-subscribe...")
        try:
            auto_subscribe_to_youtube()
        except Exception as e:
            print(f"Auto-subscribe error (non-critical): {e}")
        
        # Small delay before launching main app
        time.sleep(0.5)
    
    # Create and run the app
    root = tk.Tk()
    app = FORGEMacro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
