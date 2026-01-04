import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import json
import os
import sys
import time
import mss
import numpy as np
import ctypes
from ctypes import windll

# Mouse event constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class AreaSelector:
    """Transparent draggable and resizable area selector box"""
    
    def __init__(self, parent, initial_box, callback):
        self.callback = callback
        self.parent = parent
        
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

class FishingMacroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPO Fishing Macro")
        self.root.geometry("500x500")
        self.root.resizable(True, True)
        
        # Configuration file for hotkey bindings
        self.config_file = "GPOsettings8.json"
        
        # Load or create default settings
        self.hotkeys = {
            "start_stop": "f1",
            "change_area": "f2",
            "exit": "f3"
        }
        self.always_on_top = True
        
        # Default area box and points (proportional to screen size)
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Default coordinates (based on 2560x1440 resolution, scaled proportionally)
        self.area_box = {
            "x1": int(screen_width * 0.52461),
            "y1": int(screen_height * 0.29167),
            "x2": int(screen_width * 0.68477),
            "y2": int(screen_height * 0.79097)
        }
        
        self.water_point = {
            "x": int(screen_width * 0.42070),
            "y": int(screen_height * 0.15347)
        }
        
        # PD control parameters
        self.kp = 0.9
        self.kd = 0.3
        self.pd_clamp = 1.0
        # Casting parameters
        self.cast_hold_duration = 1.0
        self.recast_timeout = 30.0
        # Fishing parameters
        self.fish_end_delay = 2.0
        # Hotkey parameters
        self.rod_hotkey = "1"
        self.anything_else_hotkey = "2"
        # Pre-cast parameters
        self.auto_buy_common_bait = True
        self.auto_store_devil_fruit = False
        
        # Default buy bait points (proportional to screen size)
        self.left_point = {
            "x": int(screen_width * 0.41133),
            "y": int(screen_height * 0.90694)
        }
        self.middle_point = {
            "x": int(screen_width * 0.50078),
            "y": int(screen_height * 0.90556)
        }
        self.right_point = {
            "x": int(screen_width * 0.59023),
            "y": int(screen_height * 0.90486)
        }
        
        self.loops_per_purchase = 100
        
        # Default store fruit point (proportional to screen size)
        self.store_fruit_point = {
            "x": int(screen_width * 0.50195),
            "y": int(screen_height * 0.80139)
        }
        
        self.devil_fruit_hotkey = "3"
        
        self.load_settings()
        
        # Main loop state
        self.is_running = False
        self.is_rebinding = None
        self.area_selector = None
        self.area_selector_active = False
        
        # DEBUG: Arrow overlay system
        self.debug_overlay = None
        self.debug_canvas = None
        self.debug_arrow_ids = {}
        
        # PD control state for frictionless system
        self.last_error = None
        self.last_dark_gray_y = None
        self.last_scan_time = time.time()
        self.is_holding_click = False
        
        # Roblox focus tracking
        self.has_focused_roblox = False
        
        # Bait purchase loop counter
        self.bait_purchase_loop_counter = 0
        
        # Create GUI
        self.create_widgets()
        self.setup_hotkeys()
        self.main_loop_thread = None
        
    def load_settings(self):
        """Load hotkey settings from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.hotkeys.update(data.get("hotkeys", {}))
                    self.area_box.update(data.get("area_box", {}))
                    self.always_on_top = data.get("always_on_top", False)
                    self.water_point = data.get("water_point", None)
                    self.kp = data.get("kp", 0.9)
                    self.kd = data.get("kd", 0.3)
                    self.pd_clamp = data.get("pd_clamp", 1.0)
                    self.cast_hold_duration = data.get("cast_hold_duration", 1.0)
                    self.recast_timeout = data.get("recast_timeout", 30.0)
                    self.fish_end_delay = data.get("fish_end_delay", 2.0)
                    self.rod_hotkey = data.get("rod_hotkey", "1")
                    self.anything_else_hotkey = data.get("anything_else_hotkey", "2")
                    self.auto_buy_common_bait = data.get("auto_buy_common_bait", True)
                    self.auto_store_devil_fruit = data.get("auto_store_devil_fruit", False)
                    self.left_point = data.get("left_point", None)
                    self.middle_point = data.get("middle_point", None)
                    self.right_point = data.get("right_point", None)
                    self.loops_per_purchase = data.get("loops_per_purchase", 100)
                    self.store_fruit_point = data.get("store_fruit_point", None)
                    self.devil_fruit_hotkey = data.get("devil_fruit_hotkey", "3")
            except:
                pass
    
    def save_settings(self):
        """Save hotkey settings and area box to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump({
                "hotkeys": self.hotkeys, 
                "area_box": self.area_box,
                "always_on_top": self.always_on_top,
                "water_point": self.water_point,
                "kp": self.kp,
                "kd": self.kd,
                "pd_clamp": self.pd_clamp,
                "cast_hold_duration": self.cast_hold_duration,
                "recast_timeout": self.recast_timeout,
                "fish_end_delay": self.fish_end_delay,
                "rod_hotkey": self.rod_hotkey,
                "anything_else_hotkey": self.anything_else_hotkey,
                "auto_buy_common_bait": self.auto_buy_common_bait,
                "auto_store_devil_fruit": self.auto_store_devil_fruit,
                "left_point": self.left_point,
                "middle_point": self.middle_point,
                "right_point": self.right_point,
                "loops_per_purchase": self.loops_per_purchase,
                "store_fruit_point": self.store_fruit_point,
                "devil_fruit_hotkey": self.devil_fruit_hotkey
            }, f, indent=4)
    
    def create_widgets(self):
        """Create the GUI elements"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="GPO Fishing Macro Controls", 
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", 
                                      font=("Arial", 10), foreground="red")
        self.status_label.pack(pady=5)
        
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # === General Tab ===
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        
        # Hotkeys section (compact)
        hotkeys_frame = ttk.LabelFrame(general_tab, text="Hotkeys", padding=10)
        hotkeys_frame.pack(fill="x", padx=5, pady=5)
        
        self.hotkey_displays = {}
        
        # Start/Stop hotkey
        self.create_compact_hotkey_row(hotkeys_frame, "Start/Stop:", "start_stop", self.toggle_macro)
        
        # Change Area hotkey
        self.create_compact_hotkey_row(hotkeys_frame, "Change Area:", "change_area", self.change_area)
        
        # Exit hotkey
        self.create_compact_hotkey_row(hotkeys_frame, "Exit:", "exit", self.force_exit)
        
        # Separator
        ttk.Separator(general_tab, orient="horizontal").pack(fill="x", pady=10)
        
        # Always on top checkbox
        self.always_on_top_var = tk.BooleanVar(value=self.always_on_top)
        always_on_top_checkbox = ttk.Checkbutton(general_tab, text="Always on Top", 
                                                 variable=self.always_on_top_var,
                                                 command=self.toggle_always_on_top)
        always_on_top_checkbox.pack(padx=5, pady=10)
        # Apply always on top setting
        self.root.attributes('-topmost', self.always_on_top)
        
        # Hotkey Selectors section
        hotkey_selector_frame = ttk.LabelFrame(general_tab, text="Number Hotkeys", padding=10)
        hotkey_selector_frame.pack(fill="x", padx=5, pady=5)
        
        # Rod Hotkey
        rod_hotkey_frame = ttk.Frame(hotkey_selector_frame)
        rod_hotkey_frame.pack(fill="x", pady=3)
        ttk.Label(rod_hotkey_frame, text="Rod Hotkey:", width=20, anchor="w").pack(side="left", padx=5)
        self.rod_hotkey_var = tk.StringVar(value=self.rod_hotkey)
        rod_hotkey_dropdown = ttk.Combobox(rod_hotkey_frame, textvariable=self.rod_hotkey_var, 
                                           values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 
                                           state="readonly", width=10)
        rod_hotkey_dropdown.pack(side="left", padx=5)
        rod_hotkey_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_number_hotkeys())
        
        # Anything Else Hotkey
        anything_else_frame = ttk.Frame(hotkey_selector_frame)
        anything_else_frame.pack(fill="x", pady=3)
        ttk.Label(anything_else_frame, text="Anything Else Hotkey:", width=20, anchor="w").pack(side="left", padx=5)
        self.anything_else_hotkey_var = tk.StringVar(value=self.anything_else_hotkey)
        anything_else_dropdown = ttk.Combobox(anything_else_frame, textvariable=self.anything_else_hotkey_var, 
                                              values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 
                                              state="readonly", width=10)
        anything_else_dropdown.pack(side="left", padx=5)
        anything_else_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_number_hotkeys())
        
        # === Casting Tab ===
        casting_tab = ttk.Frame(notebook)
        notebook.add(casting_tab, text="Casting")
        
        # Water Point section
        water_point_frame = ttk.LabelFrame(casting_tab, text="Water Point", padding=10)
        water_point_frame.pack(fill="x", padx=5, pady=5)
        
        # Water Point button and coordinates display
        wp_button_frame = ttk.Frame(water_point_frame)
        wp_button_frame.pack(fill="x", pady=5)
        
        self.water_point_button = ttk.Button(wp_button_frame, text="Set Water Point", 
                                            command=self.set_water_point, width=20)
        self.water_point_button.pack(side="left", padx=5)
        
        self.water_point_label = ttk.Label(wp_button_frame, text="Not Set", 
                                          font=("Arial", 9), foreground="red")
        if self.water_point:
            self.water_point_label.config(text=f"X: {self.water_point['x']}, Y: {self.water_point['y']}", 
                                         foreground="green")
        self.water_point_label.pack(side="left", padx=5)
        
        # Cast Timing section
        timing_frame = ttk.LabelFrame(casting_tab, text="Cast Timing", padding=10)
        timing_frame.pack(fill="x", padx=5, pady=5)
        
        # Cast Hold Duration
        hold_duration_frame = ttk.Frame(timing_frame)
        hold_duration_frame.pack(fill="x", pady=3)
        ttk.Label(hold_duration_frame, text="Cast Hold Duration:", width=20, anchor="w").pack(side="left", padx=5)
        self.cast_hold_var = tk.DoubleVar(value=self.cast_hold_duration)
        hold_spinbox = ttk.Spinbox(hold_duration_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.cast_hold_var, width=10)
        hold_spinbox.pack(side="left", padx=5)
        hold_spinbox.bind('<Return>', lambda e: self.update_cast_timing())
        hold_spinbox.bind('<FocusOut>', lambda e: self.update_cast_timing())
        ttk.Label(hold_duration_frame, text="s").pack(side="left", padx=2)
        
        # Recast Timeout
        recast_frame = ttk.Frame(timing_frame)
        recast_frame.pack(fill="x", pady=3)
        ttk.Label(recast_frame, text="Recast Timeout:", width=20, anchor="w").pack(side="left", padx=5)
        self.recast_timeout_var = tk.DoubleVar(value=self.recast_timeout)
        recast_spinbox = ttk.Spinbox(recast_frame, from_=1.0, to=120.0, increment=1.0, textvariable=self.recast_timeout_var, width=10)
        recast_spinbox.pack(side="left", padx=5)
        recast_spinbox.bind('<Return>', lambda e: self.update_cast_timing())
        recast_spinbox.bind('<FocusOut>', lambda e: self.update_cast_timing())
        ttk.Label(recast_frame, text="s").pack(side="left", padx=2)
        
        # === Fishing Tab ===
        fishing_tab = ttk.Frame(notebook)
        notebook.add(fishing_tab, text="Fishing")
        
        # PD Control Parameters section
        pd_frame = ttk.LabelFrame(fishing_tab, text="PD Control Parameters", padding=10)
        pd_frame.pack(fill="x", padx=5, pady=5)
        
        # KP parameter
        kp_frame = ttk.Frame(pd_frame)
        kp_frame.pack(fill="x", pady=3)
        ttk.Label(kp_frame, text="Kp (Proportional):", width=20, anchor="w").pack(side="left", padx=5)
        self.kp_var = tk.DoubleVar(value=self.kp)
        kp_spinbox = ttk.Spinbox(kp_frame, from_=0.0, to=5.0, increment=0.1, textvariable=self.kp_var, width=10)
        kp_spinbox.pack(side="left", padx=5)
        kp_spinbox.bind('<Return>', lambda e: self.update_pd_params())
        kp_spinbox.bind('<FocusOut>', lambda e: self.update_pd_params())
        
        # KD parameter
        kd_frame = ttk.Frame(pd_frame)
        kd_frame.pack(fill="x", pady=3)
        ttk.Label(kd_frame, text="Kd (Derivative):", width=20, anchor="w").pack(side="left", padx=5)
        self.kd_var = tk.DoubleVar(value=self.kd)
        kd_spinbox = ttk.Spinbox(kd_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.kd_var, width=10)
        kd_spinbox.pack(side="left", padx=5)
        kd_spinbox.bind('<Return>', lambda e: self.update_pd_params())
        kd_spinbox.bind('<FocusOut>', lambda e: self.update_pd_params())
        
        # PD Clamp parameter
        clamp_frame = ttk.Frame(pd_frame)
        clamp_frame.pack(fill="x", pady=3)
        ttk.Label(clamp_frame, text="PD Clamp:", width=20, anchor="w").pack(side="left", padx=5)
        self.pd_clamp_var = tk.DoubleVar(value=self.pd_clamp)
        clamp_spinbox = ttk.Spinbox(clamp_frame, from_=0.1, to=5.0, increment=0.1, textvariable=self.pd_clamp_var, width=10)
        clamp_spinbox.pack(side="left", padx=5)
        clamp_spinbox.bind('<Return>', lambda e: self.update_pd_params())
        clamp_spinbox.bind('<FocusOut>', lambda e: self.update_pd_params())
        
        # Fish End Delay section
        delay_frame = ttk.LabelFrame(fishing_tab, text="Timing", padding=10)
        delay_frame.pack(fill="x", padx=5, pady=5)
        
        # Fish End Delay parameter
        fish_delay_frame = ttk.Frame(delay_frame)
        fish_delay_frame.pack(fill="x", pady=3)
        ttk.Label(fish_delay_frame, text="Fish End Delay:", width=20, anchor="w").pack(side="left", padx=5)
        self.fish_end_delay_var = tk.DoubleVar(value=self.fish_end_delay)
        fish_delay_spinbox = ttk.Spinbox(fish_delay_frame, from_=0.0, to=10.0, increment=0.1, textvariable=self.fish_end_delay_var, width=10)
        fish_delay_spinbox.pack(side="left", padx=5)
        fish_delay_spinbox.bind('<Return>', lambda e: self.update_fish_timing())
        fish_delay_spinbox.bind('<FocusOut>', lambda e: self.update_fish_timing())
        ttk.Label(fish_delay_frame, text="s").pack(side="left", padx=2)
        
        # === Pre-Cast Tab ===
        precast_tab = ttk.Frame(notebook)
        notebook.add(precast_tab, text="Pre-Cast")
        
        # Auto Buy Common Bait checkbox
        self.auto_buy_common_bait_var = tk.BooleanVar(value=self.auto_buy_common_bait)
        auto_buy_checkbox = ttk.Checkbutton(precast_tab, text="Auto Buy Common Bait", 
                                           variable=self.auto_buy_common_bait_var,
                                           command=self.toggle_auto_buy_section)
        auto_buy_checkbox.pack(padx=5, pady=5, anchor="w")
        
        # Auto Buy Common Bait section (collapsible)
        self.auto_buy_section = ttk.LabelFrame(precast_tab, text="Auto Buy Common Bait Settings", padding=10)
        if self.auto_buy_common_bait:
            self.auto_buy_section.pack(fill="x", padx=5, pady=5)
        
        # Left Point
        left_point_frame = ttk.Frame(self.auto_buy_section)
        left_point_frame.pack(fill="x", pady=3)
        
        self.left_point_button = ttk.Button(left_point_frame, text="Set Left Point", 
                                           command=self.set_left_point, width=20)
        self.left_point_button.pack(side="left", padx=5)
        
        self.left_point_label = ttk.Label(left_point_frame, text="Not Set", 
                                         font=("Arial", 9), foreground="red")
        if self.left_point:
            self.left_point_label.config(text=f"X: {self.left_point['x']}, Y: {self.left_point['y']}", 
                                        foreground="green")
        self.left_point_label.pack(side="left", padx=5)
        
        # Middle Point
        middle_point_frame = ttk.Frame(self.auto_buy_section)
        middle_point_frame.pack(fill="x", pady=3)
        
        self.middle_point_button = ttk.Button(middle_point_frame, text="Set Middle Point", 
                                             command=self.set_middle_point, width=20)
        self.middle_point_button.pack(side="left", padx=5)
        
        self.middle_point_label = ttk.Label(middle_point_frame, text="Not Set", 
                                           font=("Arial", 9), foreground="red")
        if self.middle_point:
            self.middle_point_label.config(text=f"X: {self.middle_point['x']}, Y: {self.middle_point['y']}", 
                                          foreground="green")
        self.middle_point_label.pack(side="left", padx=5)
        
        # Right Point
        right_point_frame = ttk.Frame(self.auto_buy_section)
        right_point_frame.pack(fill="x", pady=3)
        
        self.right_point_button = ttk.Button(right_point_frame, text="Set Right Point", 
                                            command=self.set_right_point, width=20)
        self.right_point_button.pack(side="left", padx=5)
        
        self.right_point_label = ttk.Label(right_point_frame, text="Not Set", 
                                          font=("Arial", 9), foreground="red")
        if self.right_point:
            self.right_point_label.config(text=f"X: {self.right_point['x']}, Y: {self.right_point['y']}", 
                                         foreground="green")
        self.right_point_label.pack(side="left", padx=5)
        
        # Loops Per Purchase
        loops_frame = ttk.Frame(self.auto_buy_section)
        loops_frame.pack(fill="x", pady=3)
        ttk.Label(loops_frame, text="Loops Per Purchase:", width=20, anchor="w").pack(side="left", padx=5)
        self.loops_per_purchase_var = tk.IntVar(value=self.loops_per_purchase)
        loops_spinbox = ttk.Spinbox(loops_frame, from_=1, to=1000, increment=1, 
                                   textvariable=self.loops_per_purchase_var, width=10)
        loops_spinbox.pack(side="left", padx=5)
        loops_spinbox.bind('<Return>', lambda e: self.update_loops_per_purchase())
        loops_spinbox.bind('<FocusOut>', lambda e: self.update_loops_per_purchase())
        
        # Auto Store Devil Fruit checkbox
        self.auto_store_devil_fruit_var = tk.BooleanVar(value=self.auto_store_devil_fruit)
        auto_store_checkbox = ttk.Checkbutton(precast_tab, text="Auto Store Devil Fruit", 
                                             variable=self.auto_store_devil_fruit_var,
                                             command=self.toggle_auto_store_section)
        auto_store_checkbox.pack(padx=5, pady=5, anchor="w")
        
        # Auto Store Devil Fruit section (collapsible)
        self.auto_store_section = ttk.LabelFrame(precast_tab, text="Auto Store Devil Fruit Settings", padding=10)
        if self.auto_store_devil_fruit:
            self.auto_store_section.pack(fill="x", padx=5, pady=5)
        
        # Store Fruit Point
        store_fruit_point_frame = ttk.Frame(self.auto_store_section)
        store_fruit_point_frame.pack(fill="x", pady=3)
        
        self.store_fruit_point_button = ttk.Button(store_fruit_point_frame, text="Set Store Fruit Point", 
                                                   command=self.set_store_fruit_point, width=20)
        self.store_fruit_point_button.pack(side="left", padx=5)
        
        self.store_fruit_point_label = ttk.Label(store_fruit_point_frame, text="Not Set", 
                                                 font=("Arial", 9), foreground="red")
        if self.store_fruit_point:
            self.store_fruit_point_label.config(text=f"X: {self.store_fruit_point['x']}, Y: {self.store_fruit_point['y']}", 
                                               foreground="green")
        self.store_fruit_point_label.pack(side="left", padx=5)
        
        # Devil Fruit Hotkey
        devil_fruit_hotkey_frame = ttk.Frame(self.auto_store_section)
        devil_fruit_hotkey_frame.pack(fill="x", pady=3)
        ttk.Label(devil_fruit_hotkey_frame, text="Devil Fruit Hotkey:", width=20, anchor="w").pack(side="left", padx=5)
        self.devil_fruit_hotkey_var = tk.StringVar(value=self.devil_fruit_hotkey)
        devil_fruit_hotkey_dropdown = ttk.Combobox(devil_fruit_hotkey_frame, textvariable=self.devil_fruit_hotkey_var, 
                                                   values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 
                                                   state="readonly", width=10)
        devil_fruit_hotkey_dropdown.pack(side="left", padx=5)
        devil_fruit_hotkey_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_devil_fruit_hotkey())
    
    def create_compact_hotkey_row(self, parent, label_text, key, callback):
        """Create a compact hotkey row with label, hotkey, and rebind button"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill="x", pady=3)
        
        # Label
        label = ttk.Label(row_frame, text=label_text, font=("Arial", 10), width=12, anchor="w")
        label.pack(side="left", padx=5)
        
        # Hotkey display
        hotkey_display = ttk.Label(row_frame, text=self.hotkeys[key].upper(), 
                                   font=("Arial", 10, "bold"), foreground="blue", width=8)
        hotkey_display.pack(side="left", padx=5)
        self.hotkey_displays[key] = hotkey_display
        
        # Rebind button
        rebind_button = ttk.Button(row_frame, text="Rebind", 
                                  command=lambda: self.start_rebind(key),
                                  width=10)
        rebind_button.pack(side="left", padx=5)
    
    def start_rebind(self, key):
        """Start listening for a new hotkey"""
        self.is_rebinding = key
        
        try:
            # Remove old hotkey
            keyboard.remove_hotkey(self.hotkeys[key])
        except:
            pass
        
        # Listen for one key
        def on_key_event(event):
            if self.is_rebinding == key:
                new_hotkey = event.name.lower()
                self.hotkeys[key] = new_hotkey
                self.hotkey_displays[key].config(text=new_hotkey.upper())
                self.save_settings()
                self.is_rebinding = None
                
                # Re-register the hotkey
                self.register_hotkey(key)
        
        keyboard.on_release(on_key_event, suppress=False)
    
    def setup_hotkeys(self):
        """Setup all hotkey bindings"""
        for key in self.hotkeys.keys():
            self.register_hotkey(key)
    
    def register_hotkey(self, key):
        """Register a single hotkey"""
        if key == "start_stop":
            keyboard.add_hotkey(self.hotkeys[key], self.toggle_macro)
        elif key == "change_area":
            keyboard.add_hotkey(self.hotkeys[key], self.change_area)
        elif key == "exit":
            keyboard.add_hotkey(self.hotkeys[key], self.force_exit)
    
    def toggle_macro(self):
        """Toggle the macro on/off"""
        # Don't allow starting if area selector is active
        if not self.is_running and self.area_selector_active:
            print("Cannot start macro while area selector is active")
            return
        
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_label.config(text="Status: Running", foreground="green")
            # Minimize GUI to background
            self.root.iconify()
            print("GUI minimized to background")
            # Reset Roblox focus flag when starting
            self.has_focused_roblox = False
            # Start main loop in a separate thread
            if self.main_loop_thread is None or not self.main_loop_thread.is_alive():
                self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
                self.main_loop_thread.start()
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            # Restore GUI window
            self.root.deiconify()
            print("GUI restored")
    
    def pre_cast(self):
        """Stage 1: Pre-cast - Prepare and cast the fishing rod"""
        # Focus on Roblox window (only once per macro session)
        if not self.has_focused_roblox:
            try:
                import win32gui
                import win32con
                
                def find_roblox_window(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if "Roblox" in title:
                            windows.append(hwnd)
                
                windows = []
                win32gui.EnumWindows(find_roblox_window, windows)
                
                if windows:
                    # Focus the first Roblox window found
                    win32gui.SetForegroundWindow(windows[0])
                    time.sleep(0.2)  # Small delay to ensure window is focused
                    print("Focused on Roblox window")
                    self.has_focused_roblox = True
                else:
                    print("Warning: No Roblox window found")
            except Exception as e:
                print(f"Could not focus Roblox window: {e}")
        
        # Auto Buy Common Bait sequence (with loop counter)
        if self.auto_buy_common_bait:
            # Check if it's time to purchase (first run or counter reached)
            if self.bait_purchase_loop_counter == 0 or self.bait_purchase_loop_counter >= self.loops_per_purchase:
                print(f"=== Auto Buy Common Bait: Starting (Loop: {self.bait_purchase_loop_counter}/{self.loops_per_purchase}) ===")
                
                # Check if all required points are set
                if not self.left_point or not self.middle_point or not self.right_point:
                    print("Warning: Auto Buy Common Bait enabled but not all points are set!")
                    print(f"  Left Point: {'SET' if self.left_point else 'NOT SET'}")
                    print(f"  Middle Point: {'SET' if self.middle_point else 'NOT SET'}")
                    print(f"  Right Point: {'SET' if self.right_point else 'NOT SET'}")
                else:
                    # 1) Press 'e'
                    keyboard.press_and_release('e')
                    print("  Pressed 'e'")
                    time.sleep(3)
                    
                    # 2) Click left point
                    ctypes.windll.user32.SetCursorPos(self.left_point['x'], self.left_point['y'])
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print(f"  Clicked Left Point: X={self.left_point['x']}, Y={self.left_point['y']}")
                    time.sleep(3)
                    
                    # 3) Click middle point
                    ctypes.windll.user32.SetCursorPos(self.middle_point['x'], self.middle_point['y'])
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print(f"  Clicked Middle Point: X={self.middle_point['x']}, Y={self.middle_point['y']}")
                    time.sleep(3)
                    
                    # 4) Type number (loops_per_purchase)
                    keyboard.write(str(self.loops_per_purchase))
                    print(f"  Typed number: {self.loops_per_purchase}")
                    time.sleep(3)
                    
                    # 5) Click left point
                    ctypes.windll.user32.SetCursorPos(self.left_point['x'], self.left_point['y'])
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print(f"  Clicked Left Point: X={self.left_point['x']}, Y={self.left_point['y']}")
                    time.sleep(3)
                    
                    # 6) Click right point
                    ctypes.windll.user32.SetCursorPos(self.right_point['x'], self.right_point['y'])
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print(f"  Clicked Right Point: X={self.right_point['x']}, Y={self.right_point['y']}")
                    time.sleep(3)
                    
                    # 7) Click middle point
                    ctypes.windll.user32.SetCursorPos(self.middle_point['x'], self.middle_point['y'])
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                    time.sleep(0.05)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print(f"  Clicked Middle Point: X={self.middle_point['x']}, Y={self.middle_point['y']}")
                    time.sleep(3)
                    
                    print("=== Auto Buy Common Bait: Complete ===")
                
                # Reset counter after purchase
                self.bait_purchase_loop_counter = 1
            else:
                # Increment counter
                self.bait_purchase_loop_counter += 1
                print(f"Auto Buy Common Bait: Skipping (Loop: {self.bait_purchase_loop_counter}/{self.loops_per_purchase})")
        
        # Auto Store Devil Fruit sequence
        if self.auto_store_devil_fruit:
            print("=== Auto Store Devil Fruit: Starting ===")
            
            # Check if store fruit point is set
            if not self.store_fruit_point:
                print("Warning: Auto Store Devil Fruit enabled but Store Fruit Point not set!")
            else:
                # 1) Press devil fruit hotkey to select it
                keyboard.press_and_release(self.devil_fruit_hotkey)
                print(f"  Pressed Devil Fruit Hotkey: {self.devil_fruit_hotkey}")
                time.sleep(1)
                
                # 2) Click store fruit point
                ctypes.windll.user32.SetCursorPos(self.store_fruit_point['x'], self.store_fruit_point['y'])
                time.sleep(0.05)
                ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # Anti-Roblox detection
                time.sleep(0.05)
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print(f"  Clicked Store Fruit Point: X={self.store_fruit_point['x']}, Y={self.store_fruit_point['y']}")
                time.sleep(2)
                
                # 3) Press shift
                keyboard.press_and_release('shift')
                print("  Pressed Shift")
                time.sleep(0.5)
                
                # 4) Press backspace
                keyboard.press_and_release('backspace')
                print("  Pressed Backspace")
                time.sleep(1.5)
                
                # 5) Press shift
                keyboard.press_and_release('shift')
                print("  Pressed Shift")
                
                print("=== Auto Store Devil Fruit: Complete ===")
        
        return True  # Return False to restart from beginning
    
    def check_black_screen(self):
        """Check if at least half of the screen is black (0, 0, 0) - anti-macro detection"""
        with mss.mss() as sct:
            monitor = {
                "top": self.area_box["y1"],
                "left": self.area_box["x1"],
                "width": self.area_box["x2"] - self.area_box["x1"],
                "height": self.area_box["y2"] - self.area_box["y1"]
            }
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
        
        # Check for black color (0, 0, 0)
        black_mask = (
            (img[:, :, 2] == 0) &  # Red
            (img[:, :, 1] == 0) &  # Green
            (img[:, :, 0] == 0)    # Blue
        )
        
        # Count black pixels
        black_pixel_count = np.sum(black_mask)
        total_pixels = img.shape[0] * img.shape[1]
        black_percentage = black_pixel_count / total_pixels
        
        # Return True if at least half is black
        return black_percentage >= 0.5
    
    def handle_anti_macro_screen(self):
        """Handle anti-macro black screen by spamming anything_else_hotkey"""
        print("⚠️ Anti-macro black screen detected! Spamming hotkey...")
        
        while self.is_running:
            # Check if screen is still black
            if not self.check_black_screen():
                print("✓ Black screen cleared! Restarting from beginning...")
                return True  # Signal to restart from beginning
            
            # Spam anything_else_hotkey
            keyboard.press_and_release(self.anything_else_hotkey)
            print(f"  Pressed {self.anything_else_hotkey}")
            time.sleep(0.25)  # 250ms delay
        
        return False  # is_running became False
    
    def waiting(self):
        """Stage 2: Waiting - Wait for fish to bite"""
        # Ensure rod is selected by pressing hotkeys
        keyboard.press_and_release(self.anything_else_hotkey)
        time.sleep(0.5)
        keyboard.press_and_release(self.rod_hotkey)
        time.sleep(0.5)
        print(f"Pressed hotkeys: {self.anything_else_hotkey} then {self.rod_hotkey} to select rod")
        
        # Check if water point is set
        if not self.water_point:
            print("Water point not set! Please set water point in Casting tab.")
            return False
        
        # Step 1: Move cursor to water point using anti-Roblox detection technique
        # SetCursorPos first, then relative mouse movement
        ctypes.windll.user32.SetCursorPos(self.water_point['x'], self.water_point['y'])
        time.sleep(0.05)  # Small delay for cursor to register
        ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # MOUSEEVENTF_MOVE with relative (0, 1)
        print(f"Cursor moved to water point: X={self.water_point['x']}, Y={self.water_point['y']}")
        
        # Step 2: Hold left click
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        print("Left click held")
        
        # Step 3: Wait for cast_hold_duration
        time.sleep(self.cast_hold_duration)
        print(f"Waited {self.cast_hold_duration}s for cast")
        
        # Step 4: Release left click
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print("Left click released")
        
        # Step 5: Scan for all 3 colors with timeout
        start_time = time.time()
        target_blue = np.array([85, 170, 255])
        target_white = np.array([255, 255, 255])
        target_dark_gray = np.array([25, 25, 25])
        
        print(f"Scanning for colors (timeout: {self.recast_timeout}s)...")
        
        while self.is_running:
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.recast_timeout:
                print(f"Timeout reached ({self.recast_timeout}s) - No colors found, restarting...")
                return False  # Restart from pre_cast
            
            # Take screenshot of the area
            with mss.mss() as sct:
                monitor = {
                    "top": self.area_box["y1"],
                    "left": self.area_box["x1"],
                    "width": self.area_box["x2"] - self.area_box["x1"],
                    "height": self.area_box["y2"] - self.area_box["y1"]
                }
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
            
            # Check for anti-macro black screen
            if self.check_black_screen():
                if self.handle_anti_macro_screen():
                    return False  # Restart from beginning
                else:
                    return False  # is_running became False
            
            # Check for blue color (85, 170, 255)
            blue_mask = (
                (img[:, :, 2] == target_blue[0]) &  # Red
                (img[:, :, 1] == target_blue[1]) &  # Green
                (img[:, :, 0] == target_blue[2])    # Blue
            )
            blue_found = np.any(blue_mask)
            
            # Check for white color (255, 255, 255)
            white_mask = (
                (img[:, :, 2] == target_white[0]) &  # Red
                (img[:, :, 1] == target_white[1]) &  # Green
                (img[:, :, 0] == target_white[2])    # Blue
            )
            white_found = np.any(white_mask)
            
            # Check for dark gray color (25, 25, 25)
            dark_gray_mask = (
                (img[:, :, 2] == target_dark_gray[0]) &  # Red
                (img[:, :, 1] == target_dark_gray[1]) &  # Green
                (img[:, :, 0] == target_dark_gray[2])    # Blue
            )
            dark_gray_found = np.any(dark_gray_mask)
            
            # If all 3 colors found, proceed to fishing stage
            if blue_found and white_found and dark_gray_found:
                print(f"✓ All colors detected! (Blue, White, Dark Gray) - Proceeding to fishing stage...")
                return True
            
            # Small delay before next scan
            time.sleep(0.1)
        
        # If loop exits due to is_running being False
        return False
    
    def fishing(self):
        """Stage 3: Fishing - Reel in the fish"""
        # DEBUG: Create overlay if not exists
        if not self.debug_overlay:
            self.debug_create_overlay()
        
        # Take screenshot of the defined area
        with mss.mss() as sct:
            monitor = {
                "top": self.area_box["y1"],
                "left": self.area_box["x1"],
                "width": self.area_box["x2"] - self.area_box["x1"],
                "height": self.area_box["y2"] - self.area_box["y1"]
            }
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
        
        # Target color: RGB (85, 170, 255)
        target_color = np.array([85, 170, 255])
        
        # Check if color exists in the screenshot
        # mss returns BGRA format, so we need to check BGR channels
        color_mask = (
            (img[:, :, 2] == target_color[0]) &  # Red
            (img[:, :, 1] == target_color[1]) &  # Green
            (img[:, :, 0] == target_color[2])    # Blue
        )
        
        if np.any(color_mask):
            # Find all Y, X coordinates where color exists
            y_coords, x_coords = np.where(color_mask)
            
            # Calculate the middle X coordinate
            middle_x = int(np.mean(x_coords))
            
            # Crop the existing image to just the middle X column (full Y height, 1 pixel wide)
            cropped_slice = img[:, middle_x:middle_x+1, :]  # Shape: (height, 1, 4)
            
            # Search for dark gray color RGB (25, 25, 25) in the slice
            target_gray = np.array([25, 25, 25])
            gray_mask = (
                (cropped_slice[:, 0, 2] == target_gray[0]) &  # Red
                (cropped_slice[:, 0, 1] == target_gray[1]) &  # Green
                (cropped_slice[:, 0, 0] == target_gray[2])    # Blue
            )
            
            if np.any(gray_mask):
                # Find Y coordinates where gray exists
                gray_y_coords = np.where(gray_mask)[0]
                top_gray_y = gray_y_coords[0]  # Topmost
                bottom_gray_y = gray_y_coords[-1]  # Bottommost
                
                # Crop the slice again to only include pixels between top and bottom gray
                final_slice = cropped_slice[top_gray_y:bottom_gray_y+1, :, :]
                
                # Search for white color RGB (255, 255, 255) in the final slice
                target_white = np.array([255, 255, 255])
                white_mask = (
                    (final_slice[:, 0, 2] == target_white[0]) &  # Red
                    (final_slice[:, 0, 1] == target_white[1]) &  # Green
                    (final_slice[:, 0, 0] == target_white[2])    # Blue
                )
                
                if np.any(white_mask):
                    # Find Y coordinates where white exists (relative to final_slice)
                    white_y_coords = np.where(white_mask)[0]
                    top_white_y_relative = white_y_coords[0]  # Topmost in final_slice
                    bottom_white_y_relative = white_y_coords[-1]  # Bottommost in final_slice
                    
                    # Calculate height in pixels
                    white_height = bottom_white_y_relative - top_white_y_relative + 1
                    
                    # Convert to screen coordinates
                    top_white_y_screen = self.area_box["y1"] + top_gray_y + top_white_y_relative
                    bottom_white_y_screen = self.area_box["y1"] + top_gray_y + bottom_white_y_relative
                    middle_white_y_screen = (top_white_y_screen + bottom_white_y_screen) // 2
                    
                    # DEBUG: Draw arrow pointing to the middle of white section (from right side)
                    offset = 50
                    if self.debug_overlay:
                        screen_middle_x = self.area_box["x1"] + middle_x
                        self.debug_arrow_ids['white_middle'] = self.debug_update_or_create_arrow(
                            self.debug_arrow_ids.get('white_middle'),
                            self.debug_get_arrow_coords_horizontal(self.area_box["x2"] + offset, middle_white_y_screen, 'left'), 'cyan')
                    
                    print(f"White found | Height: {white_height}px | Top Y: {top_white_y_screen} | Bottom Y: {bottom_white_y_screen}")
                    
                    # Search for dark gray color RGB (25, 25, 25) in the final slice
                    target_dark_gray = np.array([25, 25, 25])
                    dark_gray_mask = (
                        (final_slice[:, 0, 2] == target_dark_gray[0]) &  # Red
                        (final_slice[:, 0, 1] == target_dark_gray[1]) &  # Green
                        (final_slice[:, 0, 0] == target_dark_gray[2])    # Blue
                    )
                    
                    if np.any(dark_gray_mask):
                        # Find Y coordinates where dark gray exists (relative to final_slice)
                        dark_gray_y_coords = np.where(dark_gray_mask)[0]
                        
                        # Group dark gray pixels with gap tolerance of white_height * 2
                        gap_tolerance = white_height * 2
                        groups = []
                        current_group = [dark_gray_y_coords[0]]
                        
                        for i in range(1, len(dark_gray_y_coords)):
                            if dark_gray_y_coords[i] - dark_gray_y_coords[i-1] <= gap_tolerance:
                                # Same group (within gap tolerance)
                                current_group.append(dark_gray_y_coords[i])
                            else:
                                # New group
                                groups.append(current_group)
                                current_group = [dark_gray_y_coords[i]]
                        groups.append(current_group)  # Add last group
                        
                        # Find biggest group
                        biggest_group = max(groups, key=len)
                        biggest_group_top = biggest_group[0]
                        biggest_group_bottom = biggest_group[-1]
                        biggest_group_middle = (biggest_group_top + biggest_group_bottom) // 2
                        
                        # Convert to screen coordinates
                        biggest_group_middle_y_screen = self.area_box["y1"] + top_gray_y + biggest_group_middle
                        
                        # DEBUG: Draw arrow pointing to the middle of biggest dark gray group (from right side)
                        offset = 50
                        if self.debug_overlay:
                            self.debug_arrow_ids['dark_gray_middle'] = self.debug_update_or_create_arrow(
                                self.debug_arrow_ids.get('dark_gray_middle'),
                                self.debug_get_arrow_coords_horizontal(self.area_box["x2"] + offset, biggest_group_middle_y_screen, 'left'), 'yellow')
                        
                        print(f"Dark gray found | Biggest group size: {len(biggest_group)} | Middle Y: {biggest_group_middle_y_screen} | Gap tolerance: {gap_tolerance}px")
                
                # Convert to screen coordinates
                screen_top_gray_y = self.area_box["y1"] + top_gray_y
                screen_bottom_gray_y = self.area_box["y1"] + bottom_gray_y
                
                # DEBUG: Draw arrows pointing left at the gray positions (from right side)
                offset = 50
                if self.debug_overlay:
                    self.debug_arrow_ids['gray_top'] = self.debug_update_or_create_arrow(
                        self.debug_arrow_ids.get('gray_top'),
                        self.debug_get_arrow_coords_horizontal(self.area_box["x2"] + offset, screen_top_gray_y, 'left'), 'lime')
                    self.debug_arrow_ids['gray_bottom'] = self.debug_update_or_create_arrow(
                        self.debug_arrow_ids.get('gray_bottom'),
                        self.debug_get_arrow_coords_horizontal(self.area_box["x2"] + offset, screen_bottom_gray_y, 'left'), 'lime')
                
                print(f"Gray found | Top Y: {screen_top_gray_y} | Bottom Y: {screen_bottom_gray_y} | Final slice shape: {final_slice.shape}")
            
            # Convert to screen coordinates
            screen_middle_x = self.area_box["x1"] + middle_x
            
            # DEBUG: Point arrow at the middle X coordinate (above the box, pointing down)
            offset = 50
            if self.debug_overlay:
                self.debug_arrow_ids['blue_middle'] = self.debug_update_or_create_arrow(
                    self.debug_arrow_ids.get('blue_middle'),
                    self.debug_get_arrow_coords_vertical(screen_middle_x, self.area_box["y1"] - offset, 'down'), 'red')
            
            print(f"Color FOUND: RGB(85, 170, 255) | Middle X: {screen_middle_x} | Slice shape: {cropped_slice.shape}")
            
            # PD Control for frictionless system (only if both white and dark gray are detected)
            if 'middle_white_y_screen' in locals() and 'biggest_group_middle_y_screen' in locals():
                # PD control parameters (from settings)
                kp = self.kp
                kd = self.kd
                pd_clamp = self.pd_clamp
                
                # Calculate error (target - current)
                # Positive error = white is BELOW dark gray (need to move down = hold click)
                # Negative error = white is ABOVE dark gray (need to move up = release click)
                error = middle_white_y_screen - biggest_group_middle_y_screen
                
                # P term - proportional to error
                p_term = kp * error
                
                # D term - velocity-based damping
                d_term = 0.0
                current_time = time.time()
                time_delta = current_time - self.last_scan_time
                
                if self.last_error is not None and self.last_dark_gray_y is not None and time_delta > 0.001:
                    # Calculate dark gray velocity (how fast it's moving)
                    dark_gray_velocity = (biggest_group_middle_y_screen - self.last_dark_gray_y) / time_delta
                    
                    # Determine if we're approaching or chasing
                    error_magnitude_decreasing = abs(error) < abs(self.last_error)
                    
                    # Check if dark gray is moving toward white target
                    # If error > 0 (white below dark gray) and velocity > 0 (dark gray moving down), approaching
                    # If error < 0 (white above dark gray) and velocity < 0 (dark gray moving up), approaching
                    bar_moving_toward_target = (dark_gray_velocity > 0 and error > 0) or (dark_gray_velocity < 0 and error < 0)
                    
                    if error_magnitude_decreasing and bar_moving_toward_target:
                        # APPROACHING TARGET - Strong damping to prevent overshoot (2x)
                        damping_multiplier = 2.0
                        d_term = -kd * damping_multiplier * dark_gray_velocity
                        print(f"  PD: APPROACHING - Strong damping {damping_multiplier}x")
                    else:
                        # CHASING TARGET - Minimal damping to allow fast movement (0.5x)
                        damping_multiplier = 0.5
                        d_term = -kd * damping_multiplier * dark_gray_velocity
                        print(f"  PD: CHASING - Minimal damping {damping_multiplier}x")
                
                # Combined control signal
                control_signal = p_term + d_term
                control_signal = max(-pd_clamp, min(pd_clamp, control_signal))
                
                # Binary decision: control_signal > 0 = release, <= 0 = hold (flipped)
                should_hold = control_signal <= 0
                
                # Execute mouse action
                if should_hold and not self.is_holding_click:
                    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
                    self.is_holding_click = True
                    print(f"🔒 HOLD - Error: {error:.1f}, Control: {control_signal:.3f}, P: {p_term:.3f}, D: {d_term:.3f}")
                elif not should_hold and self.is_holding_click:
                    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                    self.is_holding_click = False
                    print(f"🔓 RELEASE - Error: {error:.1f}, Control: {control_signal:.3f}, P: {p_term:.3f}, D: {d_term:.3f}")
                else:
                    current_state = "HOLDING" if self.is_holding_click else "RELEASED"
                    print(f"⚡ {current_state} - Error: {error:.1f}, Control: {control_signal:.3f}, P: {p_term:.3f}, D: {d_term:.3f}")
                
                # Update state for next iteration
                self.last_error = error
                self.last_dark_gray_y = biggest_group_middle_y_screen
                self.last_scan_time = current_time
        else:
            # Release click if currently holding when exiting fishing stage
            if self.is_holding_click:
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                self.is_holding_click = False
                print("Released click (fishing stage exit)")
            
            # DEBUG: Clear arrows when color not found
            self.debug_clear_arrows()
            print("Color NOT FOUND: RGB(85, 170, 255) - Exiting fishing stage")
            
            # Check for anti-macro black screen after fishing ends
            if self.check_black_screen():
                self.handle_anti_macro_screen()
            
            return False  # Exit fishing stage and restart from beginning
        
        return True  # Continue fishing stage
    
    def main_loop(self):
        """Main fishing macro loop"""
        print("Macro loop started...")
        while self.is_running:
            try:
                # Reset all state variables at the start of each cycle
                self.last_error = None
                self.last_dark_gray_y = None
                self.last_scan_time = time.time()
                if self.is_holding_click:
                    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                    self.is_holding_click = False
                    print("Reset: Released click at start of cycle")
                
                # Stage 1: Pre-cast
                if not self.is_running:
                    break
                if not self.pre_cast():
                    continue  # Restart from beginning
                
                # Stage 2: Waiting
                if not self.is_running:
                    break
                if not self.waiting():
                    continue  # Restart from beginning
                
                # Stage 3: Fishing (loop until blue color disappears)
                while self.is_running:
                    if not self.fishing():
                        break  # Exit fishing loop, restart from beginning
                
                # Wait for fish end delay before restarting
                if self.is_running:
                    print(f"Fishing ended, waiting {self.fish_end_delay}s before recasting...")
                    time.sleep(self.fish_end_delay)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                break
        print("Macro loop stopped...")
    
    def change_area(self):
        """Toggle area selector"""
        # Don't allow activating area selector if main loop is running
        if not self.area_selector_active and self.is_running:
            print("Cannot activate area selector while macro is running")
            return
        
        self.area_selector_active = not self.area_selector_active
        
        if self.area_selector_active:
            # Show area selector
            self.area_selector = AreaSelector(self.root, self.area_box, self.on_area_selected)
        else:
            # Hide area selector and save coordinates
            if self.area_selector:
                self.area_selector.close()
    
    def on_area_selected(self, coords):
        """Callback when area selector is closed"""
        self.area_box = coords
        self.save_settings()
        self.area_selector = None
        self.area_selector_active = False
        print(f"Area saved: {coords}")
    
    def force_exit(self):
        """Force close the application"""
        print("Force exiting...")
        self.is_running = False
        try:
            self.root.destroy()
        except:
            pass
        os._exit(0)
    
    def toggle_always_on_top(self):
        """Toggle window always on top"""
        self.always_on_top = self.always_on_top_var.get()
        self.root.attributes('-topmost', self.always_on_top)
        self.save_settings()
    
    def set_water_point(self):
        """Allow user to click on screen to set water point coordinates"""
        self.water_point_button.config(state="disabled", text="Click anywhere...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.water_point = {"x": x, "y": y}
                self.water_point_label.config(text=f"X: {x}, Y: {y}", foreground="green")
                self.save_settings()
                self.water_point_button.config(state="normal", text="Set Water Point")
                print(f"Water point set to: X={x}, Y={y}")
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_left_point(self):
        """Allow user to click on screen to set left point coordinates"""
        self.left_point_button.config(state="disabled", text="Click anywhere...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.left_point = {"x": x, "y": y}
                self.left_point_label.config(text=f"X: {x}, Y: {y}", foreground="green")
                self.save_settings()
                self.left_point_button.config(state="normal", text="Set Left Point")
                print(f"Left point set to: X={x}, Y={y}")
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_middle_point(self):
        """Allow user to click on screen to set middle point coordinates"""
        self.middle_point_button.config(state="disabled", text="Click anywhere...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.middle_point = {"x": x, "y": y}
                self.middle_point_label.config(text=f"X: {x}, Y: {y}", foreground="green")
                self.save_settings()
                self.middle_point_button.config(state="normal", text="Set Middle Point")
                print(f"Middle point set to: X={x}, Y={y}")
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_right_point(self):
        """Allow user to click on screen to set right point coordinates"""
        self.right_point_button.config(state="disabled", text="Click anywhere...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.right_point = {"x": x, "y": y}
                self.right_point_label.config(text=f"X: {x}, Y: {y}", foreground="green")
                self.save_settings()
                self.right_point_button.config(state="normal", text="Set Right Point")
                print(f"Right point set to: X={x}, Y={y}")
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_store_fruit_point(self):
        """Allow user to click on screen to set store fruit point coordinates"""
        self.store_fruit_point_button.config(state="disabled", text="Click anywhere...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.store_fruit_point = {"x": x, "y": y}
                self.store_fruit_point_label.config(text=f"X: {x}, Y: {y}", foreground="green")
                self.save_settings()
                self.store_fruit_point_button.config(state="normal", text="Set Store Fruit Point")
                print(f"Store fruit point set to: X={x}, Y={y}")
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def update_pd_params(self):
        """Update PD control parameters from GUI and save to settings"""
        self.kp = self.kp_var.get()
        self.kd = self.kd_var.get()
        self.pd_clamp = self.pd_clamp_var.get()
        self.save_settings()
        print(f"PD parameters updated: Kp={self.kp}, Kd={self.kd}, Clamp={self.pd_clamp}")
    
    def update_cast_timing(self):
        """Update cast timing parameters from GUI and save to settings"""
        self.cast_hold_duration = self.cast_hold_var.get()
        self.recast_timeout = self.recast_timeout_var.get()
        self.save_settings()
        print(f"Cast timing updated: Hold={self.cast_hold_duration}s, Timeout={self.recast_timeout}s")
    
    def update_fish_timing(self):
        """Update fish timing parameters from GUI and save to settings"""
        self.fish_end_delay = self.fish_end_delay_var.get()
        self.save_settings()
        print(f"Fish timing updated: End Delay={self.fish_end_delay}s")
    
    def update_number_hotkeys(self):
        """Update number hotkey parameters from GUI and save to settings"""
        self.rod_hotkey = self.rod_hotkey_var.get()
        self.anything_else_hotkey = self.anything_else_hotkey_var.get()
        self.save_settings()
        print(f"Number hotkeys updated: Rod={self.rod_hotkey}, Anything Else={self.anything_else_hotkey}")
    
    def toggle_auto_buy_section(self):
        """Toggle visibility of Auto Buy Common Bait section"""
        self.auto_buy_common_bait = self.auto_buy_common_bait_var.get()
        if self.auto_buy_common_bait:
            self.auto_buy_section.pack(fill="x", padx=5, pady=5)
        else:
            self.auto_buy_section.pack_forget()
        self.save_settings()
        print(f"Auto Buy Common Bait: {'Enabled' if self.auto_buy_common_bait else 'Disabled'}")
    
    def toggle_auto_store_section(self):
        """Toggle visibility of Auto Store Devil Fruit section"""
        self.auto_store_devil_fruit = self.auto_store_devil_fruit_var.get()
        if self.auto_store_devil_fruit:
            self.auto_store_section.pack(fill="x", padx=5, pady=5)
        else:
            self.auto_store_section.pack_forget()
        self.save_settings()
        print(f"Auto Store Devil Fruit: {'Enabled' if self.auto_store_devil_fruit else 'Disabled'}")
    
    def update_loops_per_purchase(self):
        """Update loops per purchase parameter from GUI and save to settings"""
        self.loops_per_purchase = self.loops_per_purchase_var.get()
        self.save_settings()
        print(f"Loops Per Purchase updated: {self.loops_per_purchase}")
    
    def update_devil_fruit_hotkey(self):
        """Update devil fruit hotkey parameter from GUI and save to settings"""
        self.devil_fruit_hotkey = self.devil_fruit_hotkey_var.get()
        self.save_settings()
        print(f"Devil Fruit Hotkey updated: {self.devil_fruit_hotkey}")
    
    # ===== DEBUG ARROW SYSTEM - EASY TO REMOVE =====
    def debug_create_overlay(self):
        """Create debug arrow overlay"""
        if self.debug_overlay is None:
            import ctypes
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            self.debug_overlay = tk.Toplevel(self.root)
            self.debug_overlay.attributes('-topmost', True)
            self.debug_overlay.attributes('-transparentcolor', 'black')
            self.debug_overlay.overrideredirect(True)
            self.debug_overlay.geometry(f"{screen_width}x{screen_height}+0+0")
            self.debug_overlay.configure(bg='black')
            
            self.debug_canvas = tk.Canvas(self.debug_overlay, bg='black', highlightthickness=0)
            self.debug_canvas.pack(fill='both', expand=True)
            self.debug_arrow_ids = {}
    
    def debug_destroy_overlay(self):
        """Destroy debug arrow overlay"""
        if self.debug_overlay:
            self.debug_overlay.destroy()
            self.debug_overlay = None
            self.debug_canvas = None
            self.debug_arrow_ids = {}
    
    def debug_get_arrow_coords_horizontal(self, x, y, direction):
        """Get coordinates for horizontal arrow"""
        size = 15
        if direction == 'left':
            return [x-size, y, x, y-size//2, x, y+size//2]
        else:
            return [x+size, y, x, y-size//2, x, y+size//2]
    
    def debug_get_arrow_coords_vertical(self, x, y, direction):
        """Get coordinates for vertical arrow"""
        size = 15
        if direction == 'up':
            return [x, y-size, x-size//2, y, x+size//2, y]
        else:
            return [x, y+size, x-size//2, y, x+size//2, y]
    
    def debug_update_or_create_arrow(self, arrow_id, coords, color):
        """Update or create arrow on canvas"""
        if arrow_id:
            try:
                self.debug_canvas.coords(arrow_id, *coords)
                return arrow_id
            except:
                return self.debug_canvas.create_polygon(coords, fill=color, outline=color)
        else:
            return self.debug_canvas.create_polygon(coords, fill=color, outline=color)
    
    def debug_point_at(self, x, y, color='red', arrow_name='default'):
        """Point arrows at specific screen coordinates"""
        if not self.debug_overlay:
            self.debug_create_overlay()
        
        offset = 30
        # Create 4 arrows pointing at the coordinate from all sides
        self.debug_arrow_ids[f'{arrow_name}_left'] = self.debug_update_or_create_arrow(
            self.debug_arrow_ids.get(f'{arrow_name}_left'),
            self.debug_get_arrow_coords_horizontal(x - offset, y, 'right'), color)
        self.debug_arrow_ids[f'{arrow_name}_right'] = self.debug_update_or_create_arrow(
            self.debug_arrow_ids.get(f'{arrow_name}_right'),
            self.debug_get_arrow_coords_horizontal(x + offset, y, 'left'), color)
        self.debug_arrow_ids[f'{arrow_name}_top'] = self.debug_update_or_create_arrow(
            self.debug_arrow_ids.get(f'{arrow_name}_top'),
            self.debug_get_arrow_coords_vertical(x, y - offset, 'down'), color)
        self.debug_arrow_ids[f'{arrow_name}_bottom'] = self.debug_update_or_create_arrow(
            self.debug_arrow_ids.get(f'{arrow_name}_bottom'),
            self.debug_get_arrow_coords_vertical(x, y + offset, 'up'), color)
    
    def debug_clear_arrows(self):
        """Clear all debug arrows"""
        if self.debug_canvas:
            self.debug_canvas.delete('all')
            self.debug_arrow_ids = {}
    # ===== END DEBUG ARROW SYSTEM =====


def main():
    root = tk.Tk()
    app = FishingMacroGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
