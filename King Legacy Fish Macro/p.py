import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import time
from PIL import ImageGrab, ImageDraw, ImageTk
import json
import os
import ctypes
import mss
import numpy as np
import win32api
import win32con
import win32gui
import webbrowser
import sys
try:
    import pyautogui
except ImportError:
    pyautogui = None

# Set DPI awareness to handle Windows scaling properly
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

# Helper function to get the correct path for settings file
def get_settings_path():
    """Get the correct path for settings file, works with PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, "KingLegacySettings.txt")


class SingleBoxSelector:
    """Fullscreen overlay for selecting a single box area"""
    
    def __init__(self, parent, screenshot, initial_area, box_name, callback):
        self.callback = callback
        self.screenshot = screenshot
        self.box_name = box_name
        
        # Create fullscreen window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.configure(cursor='cross')
        
        # Get screen dimensions
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        # Create canvas
        self.canvas = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, 
                               highlightthickness=0)
        self.canvas.pack()
        
        # Display screenshot
        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        
        # Initialize box coordinates
        self.x1 = initial_area["x"]
        self.y1 = initial_area["y"]
        self.x2 = self.x1 + initial_area["width"]
        self.y2 = self.y1 + initial_area["height"]
        
        # Drawing state
        self.dragging = False
        self.drag_corner = None
        self.resize_threshold = 10
        
        # Create box
        self.rect = self.canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            outline='#2196F3', width=3, fill='#2196F3', stipple='gray50'
        )
        
        label_x = self.x1 + (self.x2 - self.x1) // 2
        self.label = self.canvas.create_text(
            label_x, self.y1 - 20, text=box_name,
            font=("Arial", 14, "bold"), fill='#2196F3'
        )
        
        # Corner handles
        self.handles = []
        self.create_handles()
        
        # Instructions
        instructions = "Drag corners to resize | Drag box to move | Press ENTER to save | ESC to cancel"
        self.canvas.create_text(
            self.screen_width // 2, 30,
            text=instructions,
            font=("Arial", 12, "bold"),
            fill='white',
            tags='instructions'
        )
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.window.bind('<Return>', lambda e: self.save_and_close())
        self.window.bind('<Escape>', lambda e: self.cancel())
        
    def create_handles(self):
        """Create corner handles"""
        handle_size = 12
        
        for handle in self.handles:
            self.canvas.delete(handle)
        self.handles.clear()
        
        corners = [(self.x1, self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)]
        
        for x, y in corners:
            # Outer handle
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='', outline='#2196F3', width=2
            )
            self.handles.append(handle)
            
            # Corner marker
            corner_marker = self.canvas.create_rectangle(
                x - 3, y - 3, x + 3, y + 3,
                fill='red', outline='white', width=1
            )
            self.handles.append(corner_marker)
            
            # Crosshair
            line1 = self.canvas.create_line(x - handle_size, y, x + handle_size, y, fill='yellow', width=1)
            line2 = self.canvas.create_line(x, y - handle_size, x, y + handle_size, fill='yellow', width=1)
            self.handles.append(line1)
            self.handles.append(line2)
    
    def get_corner_at_position(self, x, y):
        """Determine which corner is near the cursor"""
        corners = {
            'nw': (self.x1, self.y1),
            'ne': (self.x2, self.y1),
            'sw': (self.x1, self.y2),
            'se': (self.x2, self.y2)
        }
        
        for corner, (cx, cy) in corners.items():
            if abs(x - cx) < self.resize_threshold and abs(y - cy) < self.resize_threshold:
                return corner
        return None
    
    def is_inside_box(self, x, y):
        """Check if point is inside the box"""
        return self.x1 < x < self.x2 and self.y1 < y < self.y2
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        corner = self.get_corner_at_position(event.x, event.y)
        if corner:
            self.dragging = True
            self.drag_corner = corner
            return
        
        if self.is_inside_box(event.x, event.y):
            self.dragging = True
            self.drag_corner = 'move'
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        if self.drag_corner == 'move':
            self.x1 += dx
            self.y1 += dy
            self.x2 += dx
            self.y2 += dy
        elif self.drag_corner == 'nw':
            self.x1, self.y1 = event.x, event.y
        elif self.drag_corner == 'ne':
            self.x2, self.y1 = event.x, event.y
        elif self.drag_corner == 'sw':
            self.x1, self.y2 = event.x, event.y
        elif self.drag_corner == 'se':
            self.x2, self.y2 = event.x, event.y
        
        # Ensure x1 < x2 and y1 < y2
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
        
        self.update_box()
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.dragging = False
        self.drag_corner = None
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        corner = self.get_corner_at_position(event.x, event.y)
        
        if corner:
            cursors = {
                'nw': 'top_left_corner',
                'ne': 'top_right_corner',
                'sw': 'bottom_left_corner',
                'se': 'bottom_right_corner'
            }
            self.window.configure(cursor=cursors.get(corner, 'cross'))
        elif self.is_inside_box(event.x, event.y):
            self.window.configure(cursor='fleur')
        else:
            self.window.configure(cursor='cross')
    
    def update_box(self):
        """Update box and label positions"""
        self.canvas.coords(self.rect, self.x1, self.y1, self.x2, self.y2)
        self.canvas.coords(self.label, self.x1 + (self.x2 - self.x1) // 2, self.y1 - 20)
        self.create_handles()
    
    def save_and_close(self):
        """Save coordinates and close"""
        coords = {
            "x": int(self.x1),
            "y": int(self.y1),
            "width": int(self.x2 - self.x1),
            "height": int(self.y2 - self.y1)
        }
        if self.callback:
            self.callback(coords)
        self.window.destroy()
    
    def cancel(self):
        """Close without saving"""
        self.window.destroy()


class MacroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("King Legacy Fish Macro")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # State variables
        self.is_running = False
        self.change_area_enabled = False
        self.area_selector = None
        self.main_loop_thread = None
        
        # Settings file
        self.settings_file = get_settings_path()
        
        # Default hotkeys
        self.hotkeys = {
            'start_stop': 'f1',
            'change_area': 'f2',
            'exit': 'f3'
        }
        
        # Default fish box area (for 2560x1440 resolution)
        self.default_resolution = (2560, 1440)
        self.default_fish_box = {
            "x": 820,
            "y": 992,
            "width": 921,
            "height": 39
        }
        self.fish_box = self.default_fish_box.copy()
        
        # Load settings (will scale on first launch if needed)
        self.load_settings()
        
        # Store current rebind target
        self.rebinding_key = None
        self.rebind_hook = None
        
        # Setup GUI
        self.setup_gui()
        
        # Setup global hotkeys
        self.setup_hotkeys()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header = ttk.Label(main_frame, text="Hotkeys", font=('Arial', 12, 'bold'))
        header.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Start/Stop
        ttk.Label(main_frame, text="Start/Stop:", width=15).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_stop_label = ttk.Label(main_frame, text=self.hotkeys['start_stop'].upper(), 
                                          font=('Arial', 10, 'bold'), width=10, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.start_stop_label.grid(row=1, column=1, padx=5)
        self.start_stop_btn = ttk.Button(main_frame, text="Rebind", width=8, 
                                         command=lambda: self.start_rebind('start_stop'))
        self.start_stop_btn.grid(row=1, column=2, padx=5)
        
        # Change Area
        ttk.Label(main_frame, text="Change Area:", width=15).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.change_area_label = ttk.Label(main_frame, text=self.hotkeys['change_area'].upper(), 
                                           font=('Arial', 10, 'bold'), width=10, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.change_area_label.grid(row=2, column=1, padx=5)
        self.change_area_btn = ttk.Button(main_frame, text="Rebind", width=8, 
                                          command=lambda: self.start_rebind('change_area'))
        self.change_area_btn.grid(row=2, column=2, padx=5)
        
        # Exit
        ttk.Label(main_frame, text="Exit:", width=15).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.exit_label = ttk.Label(main_frame, text=self.hotkeys['exit'].upper(), 
                                    font=('Arial', 10, 'bold'), width=10, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.exit_label.grid(row=3, column=1, padx=5)
        self.exit_btn = ttk.Button(main_frame, text="Rebind", width=8, 
                                   command=lambda: self.start_rebind('exit'))
        self.exit_btn.grid(row=3, column=2, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=(20, 0))
        
    def setup_hotkeys(self):
        # Remove all previous hotkeys
        keyboard.unhook_all()
        
        # Add hotkeys
        keyboard.add_hotkey(self.hotkeys['start_stop'], self.toggle_start_stop)
        keyboard.add_hotkey(self.hotkeys['change_area'], self.toggle_change_area)
        keyboard.add_hotkey(self.hotkeys['exit'], self.exit_program)
        
    def start_rebind(self, key_name):
        """Start the rebinding process for a specific hotkey"""
        if self.rebinding_key is not None:
            return  # Already rebinding
        
        self.rebinding_key = key_name
        
        # Update the label to show waiting state
        if key_name == 'start_stop':
            self.start_stop_label.config(text="Press key...", foreground="blue")
        elif key_name == 'change_area':
            self.change_area_label.config(text="Press key...", foreground="blue")
        elif key_name == 'exit':
            self.exit_label.config(text="Press key...", foreground="blue")
        
        # Disable all rebind buttons
        self.start_stop_btn.config(state=tk.DISABLED)
        self.change_area_btn.config(state=tk.DISABLED)
        self.exit_btn.config(state=tk.DISABLED)
        
        # Listen for key press and store the hook reference
        self.rebind_hook = keyboard.on_press(self.on_rebind_key_press, suppress=True)
        
    def on_rebind_key_press(self, event):
        """Handle key press during rebinding"""
        if self.rebinding_key is None:
            return
        
        new_key = event.name
        
        # Update the hotkey
        self.hotkeys[self.rebinding_key] = new_key
        
        # Update the label
        if self.rebinding_key == 'start_stop':
            self.start_stop_label.config(text=new_key.upper(), foreground="black")
        elif self.rebinding_key == 'change_area':
            self.change_area_label.config(text=new_key.upper(), foreground="black")
        elif self.rebinding_key == 'exit':
            self.exit_label.config(text=new_key.upper(), foreground="black")
        
        # Re-enable buttons
        self.start_stop_btn.config(state=tk.NORMAL)
        self.change_area_btn.config(state=tk.NORMAL)
        self.exit_btn.config(state=tk.NORMAL)
        
        # Clean up
        if self.rebind_hook is not None:
            keyboard.unhook(self.rebind_hook)
            self.rebind_hook = None
        self.rebinding_key = None
        
        # Re-setup hotkeys with new bindings
        self.setup_hotkeys()
        
    def toggle_start_stop(self):
        """Toggle the main loop on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_label.config(text="Status: Running", foreground="green")
            # Start main loop in a separate thread
            self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.main_loop_thread.start()
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            
    def toggle_change_area(self):
        """Toggle change area on/off - opens area selector when ON, closes when OFF"""
        self.change_area_enabled = not self.change_area_enabled
        
        if self.change_area_enabled:
            # Turn ON - freeze screen and open selector
            print("Change Area: ON - Opening area selector...")
            self.open_area_selector()
        else:
            # Turn OFF - save current position and close selector
            print("Change Area: OFF - Saving and closing area selector...")
            if self.area_selector and self.area_selector.window.winfo_exists():
                # Get current coordinates before closing
                coords = {
                    "x": int(self.area_selector.x1),
                    "y": int(self.area_selector.y1),
                    "width": int(self.area_selector.x2 - self.area_selector.x1),
                    "height": int(self.area_selector.y2 - self.area_selector.y1)
                }
                self.fish_box = coords
                self.save_settings()
                print(f"Fish Box saved: x={coords['x']}, y={coords['y']}, width={coords['width']}, height={coords['height']}")
                self.area_selector.window.destroy()
                self.area_selector = None
        
    def is_white_with_tolerance(self, r, g, b, tolerance=3):
        """Check if pixel is white within tolerance"""
        return (abs(r - 255) <= tolerance and 
                abs(g - 255) <= tolerance and 
                abs(b - 255) <= tolerance)
    
    def main_loop(self):
        """Main loop that runs when Start/Stop is active"""
        print("Main loop started")
        
        offset = None
        calibrated = False
        mouse_down = False
        last_line_found_time = None
        fishing_state = "idle"  # idle, casting, waiting_for_line, tracking
        
        def cast_rod():
            """Cast the fishing rod by holding left click for 700ms"""
            print("Casting rod...")
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            print("Rod cast!")
        
        # Initial cast when starting
        cast_rod()
        fishing_state = "waiting_for_line"
        last_line_found_time = time.time()
        
        with mss.mss() as sct:
            while self.is_running:
                # Capture the fish box area
                monitor = {
                    "left": self.fish_box["x"],
                    "top": self.fish_box["y"],
                    "width": self.fish_box["width"],
                    "height": self.fish_box["height"]
                }
                
                # Grab screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array (BGRA format)
                img = np.array(screenshot)
                
                # 1. Search for line (top row, left to right)
                line_x = None
                found_line = False
                for y in range(img.shape[0]):  # Top to bottom
                    for x in range(img.shape[1]):  # Left to right
                        b, g, r = img[y, x, 0], img[y, x, 1], img[y, x, 2]
                        
                        if r == 255 and g == 255 and b == 255:
                            line_x = self.fish_box["x"] + x
                            found_line = True
                            break
                    
                    if found_line:
                        break
                
                # Handle line not found
                if not found_line:
                    # Check if we've been waiting too long (20 seconds)
                    if fishing_state == "waiting_for_line":
                        elapsed = time.time() - last_line_found_time
                        if elapsed > 20:
                            print(f"No line detected for {elapsed:.1f}s - clicking once then recasting...")
                            print("Recasting...")
                            cast_rod()
                            fishing_state = "waiting_for_line"
                            last_line_found_time = time.time()
                            calibrated = False
                            offset = None
                    elif fishing_state == "tracking":
                        # Line disappeared after tracking - fish caught, recast
                        print("Line disappeared - fish caught! Waiting 500ms...")
                        time.sleep(1.5)  # Wait 500ms after fishing ends
                        print("Recasting...")
                        cast_rod()
                        fishing_state = "waiting_for_line"
                        last_line_found_time = time.time()
                        calibrated = False
                        offset = None
                    
                    # Release mouse if held
                    if mouse_down:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        mouse_down = False
                    
                    continue
                
                # Line found - update state and time
                if fishing_state == "waiting_for_line":
                    print("Line detected! Starting to track...")
                    fishing_state = "tracking"
                last_line_found_time = time.time()
                
                # 2. Search for bar (bottom row, right to left) with tolerance 3
                bar_x = None
                found_bar = False
                bottom_y = img.shape[0] - 1
                right_bar_pos = None
                
                for x in range(img.shape[1] - 1, -1, -1):  # Right to left
                    b, g, r = img[bottom_y, x, 0], img[bottom_y, x, 1], img[bottom_y, x, 2]
                    
                    # Check if white with tolerance 3
                    if (abs(int(r) - 255) <= 3 and abs(int(g) - 255) <= 3 and abs(int(b) - 255) <= 3):
                        right_bar_pos = x
                        found_bar = True
                        break
                
                # Calibrate offset on first bar detection
                if found_bar and not calibrated:
                    print("Calibrating bar offset...")
                    # Find left side of bar (left to right)
                    left_bar_pos = None
                    for x in range(img.shape[1]):  # Left to right
                        b, g, r = img[bottom_y, x, 0], img[bottom_y, x, 1], img[bottom_y, x, 2]
                        
                        if (abs(int(r) - 255) <= 3 and abs(int(g) - 255) <= 3 and abs(int(b) - 255) <= 3):
                            left_bar_pos = x
                            break
                    
                    if left_bar_pos is not None and right_bar_pos is not None:
                        width = right_bar_pos - left_bar_pos
                        offset = width // 2
                        calibrated = True
                        print(f"Calibrated - Left: {left_bar_pos}, Right: {right_bar_pos}, Width: {width}, Offset: {offset}")
                
                # Calculate final bar position (right side - offset)
                if found_bar and calibrated:
                    right_bar_absolute = self.fish_box["x"] + right_bar_pos
                    bar_x = right_bar_absolute - offset
                elif found_bar and not calibrated:
                    bar_x = None  # Still calibrating
                
                # Mouse control logic - update every loop based on position
                if found_bar and calibrated and bar_x is not None and line_x is not None:
                    if bar_x < line_x:
                        # Bar is to the left of line - need to hold left click
                        if not mouse_down:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            mouse_down = True
                    elif bar_x >= line_x:
                        # Bar is to the right or equal - need to release left click
                        if mouse_down:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            mouse_down = False
                else:
                    # Can't track - release mouse if held
                    if mouse_down:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        mouse_down = False
                
                # Print results
                line_str = str(line_x) if found_line else "Not found"
                bar_str = str(bar_x) if (found_bar and calibrated and bar_x is not None) else "Not found"
                print(f"Line: {line_str} | Bar: {bar_str}")
        
        # Release mouse on exit
        if mouse_down:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        print("Main loop stopped")
        
    def open_area_selector(self):
        """Open the area selector with frozen screenshot"""
        if self.area_selector is not None:
            return  # Already open
        
        # Take screenshot
        screenshot = ImageGrab.grab()
        
        # Create selector
        self.area_selector = SingleBoxSelector(
            self.root,
            screenshot,
            self.fish_box,
            "Fish Box",
            self.on_area_selected
        )
    
    def close_area_selector(self):
        """Close the area selector without saving"""
        if self.area_selector and self.area_selector.window.winfo_exists():
            self.area_selector.window.destroy()
        self.area_selector = None
        self.change_area_enabled = False
    
    def on_area_selected(self, coords):
        """Callback when area is selected and saved"""
        self.fish_box = coords
        self.area_selector = None
        self.change_area_enabled = False
        self.save_settings()
        print(f"Fish Box saved: x={coords['x']}, y={coords['y']}, width={coords['width']}, height={coords['height']}")
    
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.hotkeys = data.get('hotkeys', self.hotkeys)
                    self.fish_box = data.get('fish_box', self.fish_box)
                print(f"Settings loaded from {self.settings_file}")
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            # First launch - scale default box to current resolution
            print("First launch detected - scaling default fish box to current resolution...")
            self.scale_fish_box_to_resolution()
            self.save_settings()
    
    def scale_fish_box_to_resolution(self):
        """Scale the fish box from default resolution to current screen resolution"""
        # Get current screen resolution
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        default_width, default_height = self.default_resolution
        
        # Calculate scaling factors
        scale_x = screen_width / default_width
        scale_y = screen_height / default_height
        
        # Scale the fish box
        self.fish_box = {
            "x": int(self.default_fish_box["x"] * scale_x),
            "y": int(self.default_fish_box["y"] * scale_y),
            "width": int(self.default_fish_box["width"] * scale_x),
            "height": int(self.default_fish_box["height"] * scale_y)
        }
        
        print(f"Scaled from {default_width}x{default_height} to {screen_width}x{screen_height}")
        print(f"Fish Box: x={self.fish_box['x']}, y={self.fish_box['y']}, width={self.fish_box['width']}, height={self.fish_box['height']}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            data = {
                'hotkeys': self.hotkeys,
                'fish_box': self.fish_box
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def exit_program(self):
        """Exit the program"""
        self.is_running = False
        self.save_settings()
        keyboard.unhook_all()
        self.root.quit()
        self.root.destroy()
        
def check_first_launch_and_terms():
    """Check if this is first launch and show terms if needed"""
    settings_file = get_settings_path()
    
    # If settings exist, not first launch
    if os.path.exists(settings_file):
        return (True, False)  # (accepted, is_first_launch)
    
    # First launch - show terms of use
    print("First launch detected - showing Terms of Use...")
    
    terms_text = """═════════════════════════════════════════════════════
                    KING LEGACY FISHING MACRO
                          by AsphaltCake
═════════════════════════════════════════════════════

By using this macro, you agree to the following:

1. USAGE & LIABILITY
   • This macro is for King Legacy fishing automation
   • Author is NOT responsible for any issues
   • No guarantee of functionality

2. COMPLIANCE
   • You are responsible for following game rules
   • Use responsibly and at your own discretion

3. CREDITS
   • Original Author: AsphaltCake
   • YouTube: https://www.youtube.com/@AsphaltCake
   • If you share or modify, credit the original author

By clicking OK, you accept these terms.
═════════════════════════════════════════════════════
"""
    
    # Create simple terms dialog
    root = tk.Tk()
    root.withdraw()
    
    result = messagebox.askokcancel(
        "Terms of Use - King Legacy Fishing Macro",
        terms_text,
        icon='info'
    )
    
    root.destroy()
    
    if result:
        print("Terms accepted!")
        return (True, True)  # (accepted, is_first_launch)
    else:
        print("Terms declined. Exiting...")
        return (False, False)

def main():
    # Check first launch and show terms
    terms_accepted, is_first_launch = check_first_launch_and_terms()
    
    if not terms_accepted:
        sys.exit(0)
    
    # Auto-subscribe to YouTube ONLY on first launch
    if is_first_launch:
        print("\n" + "="*50)
        print("🎉 First launch - attempting auto-subscribe...")
        print("="*50)
        try:
            print("🌐 Opening YouTube channel in browser...")
            webbrowser.open("https://www.youtube.com/@AsphaltCake?sub_confirmation=1")
            
            if pyautogui:
                # Wait for browser to load
                print("⏳ Waiting for browser to load...")
                time.sleep(4)
                
                # Try to find and focus browser window
                print("🔍 Looking for browser window...")
                browser_found = False
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
                        hwnd = windows[0][0]
                        print(f"✅ Browser found: {windows[0][1]}")
                        
                        # Focus the browser window
                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.5)
                except Exception as e:
                    print(f"⚠️ Could not focus browser: {e}")
                
                if browser_found:
                    # Navigate to subscribe button using Tab and Enter
                    print("🧭 Navigating to Subscribe button...")
                    try:
                        pyautogui.press('tab')
                        time.sleep(0.2)
                        pyautogui.press('tab')
                        time.sleep(0.2)
                        pyautogui.press('enter')
                        time.sleep(0.5)
                        print("✅ Subscribe sequence executed!")
                        
                        # Close the tab
                        print("❌ Closing YouTube tab...")
                        pyautogui.hotkey('ctrl', 'w')
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"⚠️ Navigation error: {e}")
                else:
                    print("⚠️ Browser not detected, continuing anyway...")
                    time.sleep(2)
            else:
                print("⚠️ pyautogui not installed - skipping auto-click")
                time.sleep(3)
            
            print("✅ Auto-subscribe sequence completed!")
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ Auto-subscribe error: {e}")
    
    root = tk.Tk()
    app = MacroGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
