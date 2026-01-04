import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import threading
import time
from pathlib import Path
import keyboard  # pip install keyboard
import mss
import numpy as np
import win32api
import win32con
import win32gui
from pynput import mouse as pynput_mouse
import webbrowser


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
        self.resize_threshold = 10
        
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


class GPOFishingMacro:
    def __init__(self, root):
        self.root = root
        self.root.title("GPO Fishing Macro")
        self.root.geometry("350x350")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Determine the correct settings path for both dev and exe
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.settings_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.settings_dir = Path(__file__).parent
        
        self.settings_file = self.settings_dir / "GPOsettings.json"
        
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
        # Default area box - relative to 2560x1440 (your settings: 1296,546,1550,963)
        # Calculate as percentage: x1=50.625%, y1=37.917%, x2=60.547%, y2=66.875%
        self.area_selector = None
        self.area_box = {
            "x1": int(screen_width * 0.50625),
            "y1": int(screen_height * 0.37917),
            "x2": int(screen_width * 0.60547),
            "y2": int(screen_height * 0.66875)
        }
        
        # Default timeouts (initialize before loading)
        self.bite_timeout = 30.0
        self.end_fish_timeout = 2.0
        
        # Default rod keys (initialize before loading)
        self.rod_key = '1'
        self.not_rod_key = '2'
        
        # Default PD controller gains (initialize before loading)
        self.kp = 0.05
        self.kd = 1.0
        
        # Default color tolerances (initialize before loading)
        self.blue_tolerance = 0
        self.white_tolerance = 0
        self.gray_tolerance = 0
        
        # Auto-buy bait settings (initialize before loading)
        # Default points - relative to 2560x1440
        # water_point: (1003, 425) = (39.18%, 29.51%)
        # yes_point: (1057, 1309) = (41.29%, 90.90%)
        # no_point: (1511, 1303) = (59.02%, 90.49%)
        # number_point: (1288, 1307) = (50.31%, 90.76%)
        self.auto_buy_bait = False
        self.loops_per_purchase = 100
        self.water_point = (int(screen_width * 0.3918), int(screen_height * 0.2951))
        self.yes_point = (int(screen_width * 0.4129), int(screen_height * 0.9090))
        self.no_point = (int(screen_width * 0.5902), int(screen_height * 0.9049))
        self.number_point = (int(screen_width * 0.5031), int(screen_height * 0.9076))
        
        # Load settings (will update area_box and auto-buy settings if exists in file)
        self.keybindings = self.load_settings()
        
        # Running state
        self.is_running = False
        self.area_change_enabled = False
        self.main_thread = None
        
        # Scan area outline
        self.scan_outline = None
        self.scan_outline_canvas = None
        # Arrow overlay (separate non-transparent window)
        self.arrow_overlay = None
        self.arrow_canvas = None
        self.arrow_ids = {'white': None, 'biggest': None}
        
        # PD controller parameters (will be loaded from settings)
        self.previous_error = 0
        self.is_clicking = False  # Track if left click is currently held
        
        # Fishing state
        self.has_cast = False  # Track if rod has been cast
        self.waiting_for_bite = False  # Track if waiting for fish to bite
        self.waiting_for_bite_time = None  # Track when started waiting for bite
        self.color_not_found_time = None  # Track when color was first not found after catching
        self.fish_caught_count = 0  # Track number of fish caught for auto-buy
        
        # Create GUI elements
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
    def load_settings(self):
        """Load keybindings, area box, and timeouts from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Load area box if exists
                    if 'area_box' in settings:
                        self.area_box = settings['area_box']
                    # Load timeouts if exist
                    self.bite_timeout = settings.get('bite_timeout', 15.0)
                    self.end_fish_timeout = settings.get('end_fish_timeout', 2.0)
                    # Load rod keys
                    self.rod_key = settings.get('rod_key', '1')
                    self.not_rod_key = settings.get('not_rod_key', '2')
                    # Load PD controller gains
                    self.kp = settings.get('kp', 0.1)
                    self.kd = settings.get('kd', 0.5)
                    # Load color tolerances
                    self.blue_tolerance = settings.get('blue_tolerance', 0)
                    self.white_tolerance = settings.get('white_tolerance', 0)
                    self.gray_tolerance = settings.get('gray_tolerance', 0)
                    # Load auto-buy bait settings
                    self.auto_buy_bait = settings.get('auto_buy_bait', False)
                    self.loops_per_purchase = settings.get('loops_per_purchase', 50)
                    # Convert lists to tuples for point coordinates
                    self.water_point = tuple(settings['water_point']) if settings.get('water_point') else None
                    self.yes_point = tuple(settings['yes_point']) if settings.get('yes_point') else None
                    self.no_point = tuple(settings['no_point']) if settings.get('no_point') else None
                    self.number_point = tuple(settings['number_point']) if settings.get('number_point') else None
                    return settings.get("keybindings", self.default_bindings)
        except Exception as e:
            messagebox.showwarning("Settings", f"Could not load settings: {e}\nUsing defaults.")
            # Get screen resolution for relative defaults
            import ctypes
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            self.bite_timeout = 30.0
            self.end_fish_timeout = 2.0
            self.rod_key = '1'
            self.not_rod_key = '2'
            self.kp = 0.05
            self.kd = 1.0
            self.blue_tolerance = 0
            self.white_tolerance = 0
            self.gray_tolerance = 0
            self.auto_buy_bait = False
            self.loops_per_purchase = 10
            self.water_point = (int(screen_width * 0.3918), int(screen_height * 0.2951))
            self.yes_point = (int(screen_width * 0.4129), int(screen_height * 0.9090))
            self.no_point = (int(screen_width * 0.5902), int(screen_height * 0.9049))
            self.number_point = (int(screen_width * 0.5031), int(screen_height * 0.9076))
        return self.default_bindings.copy()
    
    def save_settings(self):
        """Save keybindings, area box, and timeouts to JSON file"""
        try:
            settings = {
                "keybindings": self.keybindings,
                "area_box": self.area_box,
                "bite_timeout": self.bite_timeout,
                "end_fish_timeout": self.end_fish_timeout,
                "rod_key": self.rod_key,
                "not_rod_key": self.not_rod_key,
                "kp": self.kp,
                "kd": self.kd,
                "blue_tolerance": self.blue_tolerance,
                "white_tolerance": self.white_tolerance,
                "gray_tolerance": self.gray_tolerance,
                "auto_buy_bait": self.auto_buy_bait,
                "loops_per_purchase": self.loops_per_purchase,
                "water_point": self.water_point,
                "yes_point": self.yes_point,
                "no_point": self.no_point,
                "number_point": self.number_point
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
        tk.Label(self.root, text="GPO Fishing Macro").pack(pady=5)
        
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
        
        # Bite Timeout
        frame4 = tk.Frame(self.root)
        frame4.pack(pady=2)
        tk.Label(frame4, text="Bite Timeout (s):").pack(side="left", padx=2)
        self.bite_timeout_entry = tk.Entry(frame4, width=10)
        self.bite_timeout_entry.insert(0, str(self.bite_timeout))
        self.bite_timeout_entry.pack(side="left", padx=2)
        tk.Button(frame4, text="Save", command=self.save_timeouts, width=8).pack(side="left")
        
        # End Fish Timeout
        frame5 = tk.Frame(self.root)
        frame5.pack(pady=2)
        tk.Label(frame5, text="End Fish Timeout (s):").pack(side="left", padx=2)
        self.end_fish_timeout_entry = tk.Entry(frame5, width=10)
        self.end_fish_timeout_entry.insert(0, str(self.end_fish_timeout))
        self.end_fish_timeout_entry.pack(side="left", padx=2)
        tk.Button(frame5, text="Save", command=self.save_timeouts, width=8).pack(side="left")
        
        # Rod Key
        frame6 = tk.Frame(self.root)
        frame6.pack(pady=2)
        tk.Label(frame6, text="Rod:").pack(side="left", padx=2)
        self.rod_key_var = tk.StringVar(value=self.rod_key)
        rod_dropdown = tk.OptionMenu(frame6, self.rod_key_var, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
        rod_dropdown.config(width=5)
        rod_dropdown.pack(side="left", padx=2)
        tk.Label(frame6, text="Not Rod:").pack(side="left", padx=5)
        self.not_rod_key_var = tk.StringVar(value=self.not_rod_key)
        not_rod_dropdown = tk.OptionMenu(frame6, self.not_rod_key_var, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
        not_rod_dropdown.config(width=5)
        not_rod_dropdown.pack(side="left", padx=2)
        tk.Button(frame6, text="Save", command=self.save_rod_keys, width=8).pack(side="left")
        
        # PD Controller Gains
        frame7 = tk.Frame(self.root)
        frame7.pack(pady=2)
        tk.Label(frame7, text="Kp:").pack(side="left", padx=2)
        self.kp_entry = tk.Entry(frame7, width=8)
        self.kp_entry.insert(0, str(self.kp))
        self.kp_entry.pack(side="left", padx=2)
        tk.Label(frame7, text="Kd:").pack(side="left", padx=5)
        self.kd_entry = tk.Entry(frame7, width=8)
        self.kd_entry.insert(0, str(self.kd))
        self.kd_entry.pack(side="left", padx=2)
        tk.Button(frame7, text="Save", command=self.save_pd_gains, width=8).pack(side="left")
        
        # Color Tolerances
        frame_color1 = tk.Frame(self.root)
        frame_color1.pack(pady=2)
        tk.Label(frame_color1, text="Blue Tolerance:").pack(side="left", padx=2)
        self.blue_tolerance_entry = tk.Entry(frame_color1, width=8)
        self.blue_tolerance_entry.insert(0, str(self.blue_tolerance))
        self.blue_tolerance_entry.pack(side="left", padx=2)
        tk.Label(frame_color1, text="White Tolerance:").pack(side="left", padx=5)
        self.white_tolerance_entry = tk.Entry(frame_color1, width=8)
        self.white_tolerance_entry.insert(0, str(self.white_tolerance))
        self.white_tolerance_entry.pack(side="left", padx=2)
        
        frame_color2 = tk.Frame(self.root)
        frame_color2.pack(pady=2)
        tk.Label(frame_color2, text="Gray Tolerance:").pack(side="left", padx=2)
        self.gray_tolerance_entry = tk.Entry(frame_color2, width=8)
        self.gray_tolerance_entry.insert(0, str(self.gray_tolerance))
        self.gray_tolerance_entry.pack(side="left", padx=2)
        tk.Button(frame_color2, text="Save", command=self.save_color_tolerances, width=8).pack(side="left", padx=5)
        
        # Auto Buy Bait Checkbox
        frame8 = tk.Frame(self.root)
        frame8.pack(pady=2)
        self.auto_buy_var = tk.BooleanVar(value=self.auto_buy_bait)
        tk.Checkbutton(frame8, text="Auto Buy Common Bait", variable=self.auto_buy_var, 
                      command=self.toggle_auto_buy).pack()
        
        # Auto Buy Bait Settings (initially hidden)
        self.auto_buy_frame = tk.Frame(self.root)
        
        # Loops Per Purchase
        loops_frame = tk.Frame(self.auto_buy_frame)
        loops_frame.pack(pady=2)
        tk.Label(loops_frame, text="Loops Per Purchase:").pack(side="left", padx=2)
        self.loops_entry = tk.Entry(loops_frame, width=10)
        self.loops_entry.insert(0, str(self.loops_per_purchase))
        self.loops_entry.pack(side="left", padx=2)
        
        # Water Point
        water_frame = tk.Frame(self.auto_buy_frame)
        water_frame.pack(pady=2)
        self.water_btn = tk.Button(water_frame, text="Water Point: Not Set", 
                                    command=lambda: self.capture_point('water'), width=25)
        self.water_btn.pack()
        
        # Yes Point
        yes_frame = tk.Frame(self.auto_buy_frame)
        yes_frame.pack(pady=2)
        self.yes_btn = tk.Button(yes_frame, text="Yes Point: Not Set", 
                                 command=lambda: self.capture_point('yes'), width=25)
        self.yes_btn.pack()
        
        # No Point
        no_frame = tk.Frame(self.auto_buy_frame)
        no_frame.pack(pady=2)
        self.no_btn = tk.Button(no_frame, text="No Point: Not Set", 
                                command=lambda: self.capture_point('no'), width=25)
        self.no_btn.pack()
        
        # Number Point
        number_frame = tk.Frame(self.auto_buy_frame)
        number_frame.pack(pady=2)
        self.number_btn = tk.Button(number_frame, text="Number Point: Not Set", 
                                     command=lambda: self.capture_point('number'), width=25)
        self.number_btn.pack()
        
        # Save Auto Buy Settings Button
        save_auto_frame = tk.Frame(self.auto_buy_frame)
        save_auto_frame.pack(pady=5)
        tk.Button(save_auto_frame, text="Save Auto Buy Settings", 
                 command=self.save_auto_buy_settings, width=25).pack()
        
        # Update button labels if points are set
        self.update_point_buttons()
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=5)
        
        # Show/hide auto buy frame based on checkbox (after status label is created)
        if self.auto_buy_bait:
            self.auto_buy_frame.pack(pady=5, before=self.status_label)
            self.root.geometry("350x550")
    
    def save_timeouts(self):
        """Save timeout values from entry fields"""
        try:
            self.bite_timeout = float(self.bite_timeout_entry.get())
            self.end_fish_timeout = float(self.end_fish_timeout_entry.get())
            self.save_settings()
            self.status_label.config(text="Timeouts saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped"
            ))
        except ValueError:
            messagebox.showerror("Error", "Invalid timeout value. Please enter numbers only.")
    
    def save_rod_keys(self):
        """Save rod key values from dropdowns"""
        self.rod_key = self.rod_key_var.get()
        self.not_rod_key = self.not_rod_key_var.get()
        self.save_settings()
        self.status_label.config(text="Rod keys saved!")
        self.root.after(2000, lambda: self.status_label.config(
            text="Status: Running" if self.is_running else "Status: Stopped"
        ))
    
    def save_pd_gains(self):
        """Save PD controller gains from entry fields"""
        try:
            self.kp = float(self.kp_entry.get())
            self.kd = float(self.kd_entry.get())
            self.save_settings()
            self.status_label.config(text="PD gains saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped"
            ))
        except ValueError:
            messagebox.showerror("Error", "Invalid PD gain value. Please enter numbers only.")
    
    def save_color_tolerances(self):
        """Save color tolerances from entry fields"""
        try:
            self.blue_tolerance = int(self.blue_tolerance_entry.get())
            self.white_tolerance = int(self.white_tolerance_entry.get())
            self.gray_tolerance = int(self.gray_tolerance_entry.get())
            self.save_settings()
            self.status_label.config(text="Color tolerances saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped"
            ))
        except ValueError:
            messagebox.showerror("Error", "Invalid tolerance value. Please enter integers only.")
    
    def toggle_auto_buy(self):
        """Toggle the visibility of auto buy settings"""
        self.auto_buy_bait = self.auto_buy_var.get()
        if self.auto_buy_bait:
            self.auto_buy_frame.pack(pady=5, before=self.status_label)
            self.root.geometry("350x550")
        else:
            self.auto_buy_frame.pack_forget()
            self.root.geometry("350x350")
        self.save_settings()
    
    def capture_point(self, point_name):
        """Start a listener to capture the next mouse click for a point"""
        self.status_label.config(text=f"Click anywhere to set {point_name.title()} Point...")
        
        def _on_click(x, y, button, pressed):
            if pressed:
                # Save coordinates
                if point_name == 'water':
                    self.water_point = (x, y)
                elif point_name == 'yes':
                    self.yes_point = (x, y)
                elif point_name == 'no':
                    self.no_point = (x, y)
                elif point_name == 'number':
                    self.number_point = (x, y)
                
                # Update UI
                self.root.after(0, self.update_point_buttons)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"{point_name.title()} Point set: ({x}, {y})"))
                self.root.after(2000, lambda: self.status_label.config(
                    text="Status: Running" if self.is_running else "Status: Stopped"))
                
                return False  # Stop listener
        
        listener = pynput_mouse.Listener(on_click=_on_click)
        listener.start()
    
    def update_point_buttons(self):
        """Update button labels to show current point coordinates"""
        if self.water_point:
            self.water_btn.config(text=f"Water Point: {self.water_point}")
        if self.yes_point:
            self.yes_btn.config(text=f"Yes Point: {self.yes_point}")
        if self.no_point:
            self.no_btn.config(text=f"No Point: {self.no_point}")
        if self.number_point:
            self.number_btn.config(text=f"Number Point: {self.number_point}")
    
    def save_auto_buy_settings(self):
        """Save auto buy settings"""
        try:
            self.loops_per_purchase = int(self.loops_entry.get())
            self.save_settings()
            self.status_label.config(text="Auto buy settings saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped"
            ))
        except ValueError:
            messagebox.showerror("Error", "Invalid loops value. Please enter a number.")
    
    def perform_auto_buy(self):
        """Perform the auto-buy sequence"""
        if not self.auto_buy_bait or not all([self.water_point, self.yes_point, self.no_point, self.number_point]):
            return
        
        print("Starting auto-buy sequence...")
        
        # 1) Press E (then wait 1 second)
        keyboard.press('e')
        keyboard.release('e')
        time.sleep(1.0)
        
        # 2) Click yes point (then wait 500ms)
        win32api.SetCursorPos(self.yes_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # 3) Click number point (then wait 200ms)
        win32api.SetCursorPos(self.number_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.2)
        
        # 4) Type out loops per purchase value (then wait 200ms)
        keyboard.write(str(self.loops_per_purchase))
        time.sleep(0.2)
        
        # 5) Click on yes point (then wait 300ms)
        win32api.SetCursorPos(self.yes_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)
        
        # 6) Click on no point (then wait 300ms)
        win32api.SetCursorPos(self.no_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.3)
        
        # 7) Click on number point (then wait 1s)
        win32api.SetCursorPos(self.number_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(1.0)
        
        # 8) Move cursor to water point (no click)
        win32api.SetCursorPos(self.water_point)
        # anti-roblox: perform a tiny relative move so the client registers the cursor reposition
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(1.0)
        
        print("Auto-buy sequence completed!")
    
    def find_color_positions(self, image_array, target_color, tolerance=0):
        """Find the leftmost and rightmost positions of a target color in the image"""
        # Target color: RGB (85, 170, 255)
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
            return None, None  # Color not found
        
        # Get x coordinates (column indices)
        x_coords = positions[:, 1]
        
        # Find leftmost and rightmost x positions
        leftmost_x = np.min(x_coords)
        rightmost_x = np.max(x_coords)
        
        # Get corresponding y coordinates for these positions
        left_positions = positions[x_coords == leftmost_x]
        right_positions = positions[x_coords == rightmost_x]
        
        # Take the first occurrence for each
        leftmost_y = left_positions[0, 0]
        rightmost_y = right_positions[0, 0]
        
        return (leftmost_x, leftmost_y), (rightmost_x, rightmost_y)
    
    def cast_rod(self):
        """Cast the fishing rod with proper key sequence"""
        print("Casting rod...")
        # Press not rod key first
        keyboard.press(self.not_rod_key)
        keyboard.release(self.not_rod_key)
        time.sleep(0.3)  # Wait 300ms
        # Press rod key
        keyboard.press(self.rod_key)
        keyboard.release(self.rod_key)
        time.sleep(0.1)
        # Click to cast (with anti-roblox relative move)
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        except:
            pass
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    def main_loop(self):
        """Main macro loop - runs continuously when is_running is True"""
        # Cast rod once at start
        if not self.has_cast:
            self.cast_rod()
            self.has_cast = True
            self.waiting_for_bite = True
            self.waiting_for_bite_time = time.time()
            print("Waiting for bite...")
            time.sleep(0.5)  # Wait a bit after casting
        
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
                    
                    # Target color: RGB (85, 170, 255)
                    target_color = (85, 170, 255)
                    
                    # Find leftmost and rightmost positions of the color
                    left_pos, right_pos = self.find_color_positions(img_array, target_color, self.blue_tolerance)
                    
                    if left_pos and right_pos:
                        # Get x coordinates only
                        leftmost_x = int(x1 + left_pos[0])
                        rightmost_x = int(x1 + right_pos[0])
                        
                        # Crop the image between leftmost and rightmost X
                        # Coordinates are relative to the captured area
                        cropped_img = img_array[:, left_pos[0]:right_pos[0]+1]
                        
                        # Find gray color in cropped image: RGB (25, 25, 25)
                        gray_color = (25, 25, 25)
                        if self.gray_tolerance == 0:
                            gray_mask = (cropped_img[:, :, 2] == gray_color[0]) & \
                                       (cropped_img[:, :, 1] == gray_color[1]) & \
                                       (cropped_img[:, :, 0] == gray_color[2])
                        else:
                            gray_mask = (np.abs(cropped_img[:, :, 2] - gray_color[0]) <= self.gray_tolerance) & \
                                       (np.abs(cropped_img[:, :, 1] - gray_color[1]) <= self.gray_tolerance) & \
                                       (np.abs(cropped_img[:, :, 0] - gray_color[2]) <= self.gray_tolerance)
                        
                        gray_positions = np.argwhere(gray_mask)
                        
                        if len(gray_positions) > 0:
                            # Get y coordinates (row indices)
                            y_coords = gray_positions[:, 0]
                            
                            # Find topmost and bottommost y positions
                            topmost_y = int(np.min(y_coords))
                            bottommost_y = int(np.max(y_coords))
                            
                            # Crop again to just the gray bounding box
                            final_cropped = cropped_img[topmost_y:bottommost_y+1, :]
                            
                            # Find white color in final cropped image: RGB (255, 255, 255)
                            white_color = (255, 255, 255)
                            if self.white_tolerance == 0:
                                white_mask = (final_cropped[:, :, 2] == white_color[0]) & \
                                            (final_cropped[:, :, 1] == white_color[1]) & \
                                            (final_cropped[:, :, 0] == white_color[2])
                            else:
                                white_mask = (np.abs(final_cropped[:, :, 2] - white_color[0]) <= self.white_tolerance) & \
                                            (np.abs(final_cropped[:, :, 1] - white_color[1]) <= self.white_tolerance) & \
                                            (np.abs(final_cropped[:, :, 0] - white_color[2]) <= self.white_tolerance)
                            
                            white_positions = np.argwhere(white_mask)
                            
                            if len(white_positions) > 0:
                                # All colors found - start minigame if waiting for bite
                                if self.waiting_for_bite:
                                    print("Fish detected! Starting minigame...")
                                    self.waiting_for_bite = False
                                    self.waiting_for_bite_time = None
                                # Reset end fish timeout
                                self.color_not_found_time = None
                                
                                # Get y coordinates of white pixels
                                white_y_coords = white_positions[:, 0]
                                
                                # Find topmost and bottommost white pixels (relative to final_cropped)
                                white_top = int(np.min(white_y_coords))
                                white_bottom = int(np.max(white_y_coords))
                                
                                # Calculate height
                                white_height = white_bottom - white_top + 1
                                
                                # Convert to screen coordinates
                                white_top_screen = y1 + topmost_y + white_top
                                white_bottom_screen = y1 + topmost_y + white_bottom
                                
                                # Store white Y coordinates for future use
                                self.white_y_top = white_top_screen
                                self.white_y_bottom = white_bottom_screen
                                
                                # Calculate middle of white bar
                                self.white_middle_y = (white_top_screen + white_bottom_screen) // 2
                                
                                # Calculate double the height (allowable gap)
                                self.white_double_height = white_height * 2
                                
                                # Find rows WITHOUT blue color in final_cropped image
                                blue_color = (85, 170, 255)
                                rows_without_blue = []
                                
                                for row_idx in range(final_cropped.shape[0]):
                                    row = final_cropped[row_idx, :]
                                    # Check if blue color exists in this row
                                    has_blue = np.any(
                                        (row[:, 2] == blue_color[0]) &
                                        (row[:, 1] == blue_color[1]) &
                                        (row[:, 0] == blue_color[2])
                                    )
                                    if not has_blue:
                                        rows_without_blue.append(row_idx)
                                
                                if len(rows_without_blue) > 0:
                                    # Group rows into sections with allowable gap
                                    sections = []
                                    current_section_start = rows_without_blue[0]
                                    current_section_end = rows_without_blue[0]
                                    
                                    for i in range(1, len(rows_without_blue)):
                                        gap = rows_without_blue[i] - current_section_end
                                        
                                        if gap <= self.white_double_height:
                                            # Within allowable gap, extend section
                                            current_section_end = rows_without_blue[i]
                                        else:
                                            # Gap too large, save current section and start new one
                                            sections.append((current_section_start, current_section_end))
                                            current_section_start = rows_without_blue[i]
                                            current_section_end = rows_without_blue[i]
                                    
                                    # Add the last section
                                    sections.append((current_section_start, current_section_end))
                                    
                                    # Find the biggest section
                                    biggest_section = max(sections, key=lambda s: s[1] - s[0])
                                    biggest_section_start = biggest_section[0]
                                    biggest_section_end = biggest_section[1]
                                    
                                    # Calculate middle of biggest section (relative to final_cropped)
                                    biggest_section_middle = (biggest_section_start + biggest_section_end) // 2
                                    
                                    # Convert to screen coordinates
                                    self.biggest_section_y = y1 + topmost_y + biggest_section_middle
                                    
                                    # PD Controller
                                    # Error: positive = white is below biggest (need to go down = release click)
                                    #        negative = white is above biggest (need to go up = hold click)
                                    raw_error = self.white_middle_y - self.biggest_section_y
                                    
                                    # Normalize error by white_double_height
                                    normalized_error = raw_error / max(self.white_double_height, 1)
                                    
                                    # Calculate derivative
                                    derivative = normalized_error - self.previous_error
                                    self.previous_error = normalized_error
                                    
                                    # PD output
                                    pd_output = (self.kp * normalized_error) + (self.kd * derivative)
                                    
                                    print(f"Biggest: {self.biggest_section_y}, White: {self.white_middle_y}, PD: {pd_output:.2f}")
                                    
                                    # Update arrows if arrow overlay is visible
                                    if self.arrow_canvas is not None:
                                        self.update_or_create_arrow('white', self.white_middle_y, leftmost_x, 'white')
                                        self.update_or_create_arrow('biggest', self.biggest_section_y, leftmost_x, 'red')
                                    
                                    # Positive output = need to go down = release click
                                    # Negative output = need to go up = hold click
                                    if pd_output < 0:
                                        if not self.is_clicking:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                            self.is_clicking = True
                                    else:
                                        if self.is_clicking:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                            self.is_clicking = False
                                else:
                                    print(f"Biggest: None, White: {self.white_middle_y}")
                                    # Release click if no valid section found
                                    if self.is_clicking:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        self.is_clicking = False
                                # Continue to next frame
                                time.sleep(0.01)
                                continue
                    
                    # If we get here, we didn't find all colors - treat as not found
                    if not left_pos or not right_pos:
                        if self.waiting_for_bite:
                            # Still waiting for fish to bite - check bite timeout
                            elapsed = time.time() - self.waiting_for_bite_time
                            if elapsed >= self.bite_timeout:
                                print(f"Bite Timeout ({self.bite_timeout}s) - Re-casting rod...")
                                # Release any held click first
                                if self.is_clicking:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    self.is_clicking = False
                                # Cast rod again
                                self.cast_rod()
                                # Reset state
                                self.waiting_for_bite_time = time.time()
                                print("Waiting for bite...")
                                time.sleep(0.5)  # Wait a bit after casting
                        else:
                            # Fish was caught, now checking end fish timeout
                            if self.color_not_found_time is None:
                                self.color_not_found_time = time.time()
                                print("Target color not found in area")
                            else:
                                elapsed = time.time() - self.color_not_found_time
                                if elapsed >= self.end_fish_timeout:
                                    print(f"End Fish Timeout ({self.end_fish_timeout}s) - Re-casting rod...")
                                    # Increment fish caught counter
                                    self.fish_caught_count += 1
                                    print(f"Fish caught: {self.fish_caught_count}/{self.loops_per_purchase}")
                                    
                                    # Release any held click first
                                    if self.is_clicking:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        self.is_clicking = False
                                    # Clear arrows
                                    if self.arrow_canvas is not None:
                                        for arrow_key in self.arrow_ids:
                                            if self.arrow_ids[arrow_key]:
                                                try:
                                                    self.arrow_canvas.delete(self.arrow_ids[arrow_key])
                                                except:
                                                    pass
                                                self.arrow_ids[arrow_key] = None
                                    
                                    # Check if we need to buy more bait
                                    if self.auto_buy_bait and self.fish_caught_count >= self.loops_per_purchase:
                                        print(f"Reached {self.loops_per_purchase} fish - Purchasing more bait...")
                                        self.perform_auto_buy()
                                        self.fish_caught_count = 0
                                    
                                    # Cast rod again
                                    self.cast_rod()
                                    # Reset state
                                    self.color_not_found_time = None
                                    self.waiting_for_bite = True
                                    self.waiting_for_bite_time = time.time()
                                    print("Waiting for bite...")
                                    time.sleep(0.5)  # Wait a bit after casting
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(0.1)
    
    def show_scan_outline(self):
        """Show outline of the scanning area"""
        if self.scan_outline is None:
            self.scan_outline = tk.Toplevel(self.root)
            self.scan_outline.attributes('-alpha', 0.7)
            self.scan_outline.attributes('-topmost', True)
            self.scan_outline.overrideredirect(True)
            
            x1, y1 = self.area_box["x1"], self.area_box["y1"]
            x2, y2 = self.area_box["x2"], self.area_box["y2"]
            width = x2 - x1
            height = y2 - y1
            
            self.scan_outline.geometry(f"{width}x{height}+{x1}+{y1}")
            
            # Create canvas with transparent center and colored border
            self.scan_outline_canvas = tk.Canvas(self.scan_outline, bg='black', highlightthickness=0)
            self.scan_outline_canvas.pack(fill='both', expand=True)
            canvas = self.scan_outline_canvas
            
            # Draw border lines (4 lines making a rectangle)
            border_color = 'lime'
            border_width = 3
            canvas.create_line(0, 0, width, 0, fill=border_color, width=border_width)  # Top
            canvas.create_line(0, 0, 0, height, fill=border_color, width=border_width)  # Left
            canvas.create_line(width, 0, width, height, fill=border_color, width=border_width)  # Right
            canvas.create_line(0, height, width, height, fill=border_color, width=border_width)  # Bottom
            
            # Make center transparent by setting window shape
            self.scan_outline.wm_attributes('-transparentcolor', 'black')
            
            # Create arrow overlay (non-transparent, separate window)
            self.arrow_overlay = tk.Toplevel(self.root)
            self.arrow_overlay.attributes('-topmost', True)
            self.arrow_overlay.overrideredirect(True)
            self.arrow_overlay.geometry(f"{width}x{height}+{x1}+{y1}")
            self.arrow_overlay.configure(bg='black')
            
            # Create canvas for arrows
            self.arrow_canvas = tk.Canvas(self.arrow_overlay, bg='black', highlightthickness=0)
            self.arrow_canvas.pack(fill='both', expand=True)
            
            # Make canvas background transparent
            self.arrow_overlay.wm_attributes('-transparentcolor', 'black')
    
    def hide_scan_outline(self):
        """Hide the scan outline and arrow overlay"""
        if self.scan_outline is not None:
            self.scan_outline.destroy()
            self.scan_outline = None
            self.scan_outline_canvas = None
        if self.arrow_overlay is not None:
            self.arrow_overlay.destroy()
            self.arrow_overlay = None
            self.arrow_canvas = None
            self.arrow_ids = {'white': None, 'biggest': None}
    
    def get_arrow_coords_horizontal_left(self, x_relative, y_relative):
        """Get coordinates for left-pointing arrow (pointing to the left edge of cropped area)"""
        size = 15
        arrow_offset = 5  # Distance from the element
        x = x_relative + arrow_offset  # Position to the right of the element
        y = y_relative
        # Arrow pointing left: triangle pointing to the left (toward the element)
        return [x, y, x+size, y-size//2, x+size, y+size//2]
    
    def update_or_create_arrow(self, arrow_key, y_screen, x_screen, color):
        """Update or create an arrow at the given screen coordinates"""
        if self.arrow_canvas is None:
            return
        
        # Convert screen coordinates to relative coordinates within the arrow overlay window
        x_relative = x_screen - self.area_box["x1"]
        y_relative = y_screen - self.area_box["y1"]
        
        # Get arrow coordinates
        coords = self.get_arrow_coords_horizontal_left(x_relative, y_relative)
        
        # Update or create the arrow
        if self.arrow_ids[arrow_key]:
            try:
                self.arrow_canvas.coords(self.arrow_ids[arrow_key], *coords)
                self.arrow_canvas.itemconfig(self.arrow_ids[arrow_key], fill=color)
            except:
                self.arrow_ids[arrow_key] = self.arrow_canvas.create_polygon(coords, fill=color, outline=color)
        else:
            self.arrow_ids[arrow_key] = self.arrow_canvas.create_polygon(coords, fill=color, outline=color)
    
    def toggle_start_stop(self):
        """Toggle the start/stop state"""
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running")
            # Reset fishing state
            self.has_cast = False
            self.waiting_for_bite = False
            self.waiting_for_bite_time = None
            self.color_not_found_time = None
            self.fish_caught_count = 0
            # Perform auto-buy at start if enabled
            if self.auto_buy_bait:
                self.perform_auto_buy()
            # Show scan area outline
            self.show_scan_outline()
            # Start the main loop in a separate thread
            self.main_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.main_thread.start()
        else:
            self.status_label.config(text="Status: Stopped")
            # Hide scan area outline
            self.hide_scan_outline()
            # Release click if stopping
            if self.is_clicking:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                self.is_clicking = False
            # Reset PD controller and fishing state
            self.previous_error = 0
            self.has_cast = False
            self.waiting_for_bite = False
            self.waiting_for_bite_time = None
            self.color_not_found_time = None
            # Main loop will stop automatically when is_running becomes False
    
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
                text="Status: Running" if self.is_running else "Status: Stopped"
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
        """Rebind a key for an action - clean approach like uma.py"""
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
           GPO FISHING MACRO - TERMS OF USE
                    by AsphaltCake
═════════════════════════════════════════════════════

⚠️ IMPORTANT NOTICE ⚠️

This application is NOT a virus or malware!
  • Fishing automation tool for Roblox GPO
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
        "Terms of Use - GPO Fishing Macro",
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
    
    settings_file = settings_dir / "GPOsettings.json"
    
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
    app = GPOFishingMacro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
