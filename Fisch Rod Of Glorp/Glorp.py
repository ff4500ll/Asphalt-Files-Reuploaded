import tkinter as tk
from tkinter import ttk
import keyboard
import sys
import json
import os
import threading
import time
import mss
import numpy as np
import win32api
import win32con

class AreaSelector:
    def __init__(self, x=100, y=100, width=300, height=200):
        self.window = tk.Toplevel()
        self.window.title("Area Selector")
        self.window.attributes('-alpha', 0.5)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # Set initial position and size
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure window background
        self.window.configure(bg='red')
        
        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        # Variables for resizing
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0
        self.resize_start_win_x = 0
        self.resize_start_win_y = 0
        self.is_resizing = False
        self.resize_edge = None
        
        # Create border frame (for resize handles)
        border_frame = tk.Frame(self.window, bg='red')
        border_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create resize handles (corners and edges)
        # Corner resize handles
        self.create_resize_handle(border_frame, 'nw', tk.NW)
        self.create_resize_handle(border_frame, 'ne', tk.NE)
        self.create_resize_handle(border_frame, 'sw', tk.SW)
        self.create_resize_handle(border_frame, 'se', tk.SE)
        
        # Edge resize handles
        self.create_resize_handle(border_frame, 'n', tk.N)
        self.create_resize_handle(border_frame, 's', tk.S)
        self.create_resize_handle(border_frame, 'e', tk.E)
        self.create_resize_handle(border_frame, 'w', tk.W)
        
        # Create draggable center area
        self.center = tk.Frame(border_frame, bg='red')
        self.center.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.8)
        
        # Bind dragging only to center area
        self.center.bind('<Button-1>', self.start_drag)
        self.center.bind('<B1-Motion>', self.drag)
        self.center.bind('<ButtonRelease-1>', self.stop_drag)
    
    def create_resize_handle(self, parent, edge, anchor):
        handle_size = 10
        handle = tk.Frame(parent, bg='red', cursor=self.get_cursor(edge))
        
        if edge == 'nw':
            handle.place(x=0, y=0, width=handle_size, height=handle_size)
        elif edge == 'ne':
            handle.place(relx=1, x=-handle_size, y=0, width=handle_size, height=handle_size)
        elif edge == 'sw':
            handle.place(x=0, rely=1, y=-handle_size, width=handle_size, height=handle_size)
        elif edge == 'se':
            handle.place(relx=1, x=-handle_size, rely=1, y=-handle_size, width=handle_size, height=handle_size)
        elif edge == 'n':
            handle.place(relx=0.5, x=-handle_size//2, y=0, width=handle_size, height=handle_size)
        elif edge == 's':
            handle.place(relx=0.5, x=-handle_size//2, rely=1, y=-handle_size, width=handle_size, height=handle_size)
        elif edge == 'e':
            handle.place(relx=1, x=-handle_size, rely=0.5, y=-handle_size//2, width=handle_size, height=handle_size)
        elif edge == 'w':
            handle.place(x=0, rely=0.5, y=-handle_size//2, width=handle_size, height=handle_size)
        
        handle.bind('<Button-1>', lambda e, ed=edge: self.start_resize(e, ed))
        handle.bind('<B1-Motion>', self.resize)
        handle.bind('<ButtonRelease-1>', self.stop_resize)
    
    def get_cursor(self, edge):
        cursors = {
            'nw': 'size_nw_se', 'ne': 'size_ne_sw',
            'sw': 'size_ne_sw', 'se': 'size_nw_se',
            'n': 'size_ns', 's': 'size_ns',
            'e': 'size_we', 'w': 'size_we'
        }
        return cursors.get(edge, 'arrow')
        
    def start_drag(self, event):
        if not self.is_resizing:
            self.is_dragging = True
            self.drag_start_x = event.x_root - self.window.winfo_x()
            self.drag_start_y = event.y_root - self.window.winfo_y()
    
    def drag(self, event):
        if self.is_dragging and not self.is_resizing:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.window.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        self.is_dragging = False
    
    def start_resize(self, event, edge):
        self.is_resizing = True
        self.resize_edge = edge
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_width = self.window.winfo_width()
        self.resize_start_height = self.window.winfo_height()
        self.resize_start_win_x = self.window.winfo_x()
        self.resize_start_win_y = self.window.winfo_y()
    
    def resize(self, event):
        if not self.is_resizing:
            return
            
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        
        new_x = self.resize_start_win_x
        new_y = self.resize_start_win_y
        new_width = self.resize_start_width
        new_height = self.resize_start_height
        
        edge = self.resize_edge
        
        if 'e' in edge:
            new_width = max(10, self.resize_start_width + dx)
        if 'w' in edge:
            new_width = max(10, self.resize_start_width - dx)
            new_x = self.resize_start_win_x + (self.resize_start_width - new_width)
        if 's' in edge:
            new_height = max(10, self.resize_start_height + dy)
        if 'n' in edge:
            new_height = max(10, self.resize_start_height - dy)
            new_y = self.resize_start_win_y + (self.resize_start_height - new_height)
        
        self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    
    def stop_resize(self, event):
        self.is_resizing = False
        self.resize_edge = None
    
    def get_coordinates(self):
        return {
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y(),
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height()
        }
    
    def close(self):
        self.window.destroy()

class MatchIndicator:
    def __init__(self, x, y):
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', 'black')
        
        # Create canvas for arrow
        canvas = tk.Canvas(self.window, width=30, height=30, bg='black', highlightthickness=0)
        canvas.pack()
        
        # Draw downward pointing arrow using polygon
        # Arrow coordinates: top point, left point, right point
        size = 15
        arrow_coords = [
            15, 25,         # bottom point (pointing down)
            15-size//2, 10, # left point
            15+size//2, 10  # right point
        ]
        canvas.create_polygon(arrow_coords, fill='green', outline='green')
        
        # Position above the match point
        self.window.geometry(f"+{x - 15}+{y - 30}")
    
    def close(self):
        self.window.destroy()

class GlorpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Glorp Controller")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Settings file path - handle both development and PyInstaller exe
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(__file__)
        self.settings_file = os.path.join(app_dir, 'GlorpSettings.json')
        
        # States
        self.start_stop_state = False
        self.change_area_state = False
        
        # Hotkey bindings
        self.start_stop_key = 'f3'
        self.change_area_key = 'f1'
        self.exit_key = 'f4'
        
        # Area selector
        self.area_selector = None
        self.area_coords = {'x': 100, 'y': 100, 'width': 300, 'height': 200}
        
        # Match indicator overlay
        self.indicator_overlay = None
        self.indicator_canvas = None
        self.indicator_arrow_id = None
        self.left_arrow_id = None
        self.right_arrow_id = None
        
        # Calculate scaled arrow size based on resolution
        screen_width = win32api.GetSystemMetrics(0)
        ref_width = 2560  # Reference resolution width
        scale_factor = screen_width / ref_width
        self.arrow_size = int(15 * scale_factor)  # Scale arrow size with resolution
        print(f"Arrow size scaled to {self.arrow_size}px for {screen_width}px width")
        
        # PD Controller variables (675.py reference values)
        self.last_error = None
        self.last_time_pd = None
        self.kp = 15.0  # Proportional gain (675.py default)
        self.kd = 30.0  # Derivative gain (675.py default)
        self.pd_clamp = 30.0  # Clamp control signal to ±30
        self.action_threshold = 2.0  # Dead zone threshold in pixels
        self.mouse_down = False
        
        # Auto-cast settings
        self.cast_hold_time = 0.5  # Hold left click for 500ms
        self.cast_wait_time = 2.0  # Wait 2 seconds after release (configurable)
        self.detection_timeout = 5.0  # 5 seconds to detect green before recasting
        self.recast_delay = 0.5  # Wait 500ms after green disappears before recasting
        self.tolerance = 20  # Color detection tolerance
        self.cast_state = "idle"  # States: idle, holding, waiting, detecting, active, ended
        self.cast_timer = 0.0
        self.green_lost_time = None  # Track when green was lost during active play
        
        # Main loop thread
        self.main_loop_thread = None
        
        # Rebinding state
        self.waiting_for_key = None
        
        # Load settings
        self.load_settings()
        
        # Create main frame with scrollbar
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hotkey section
        ttk.Label(scrollable_frame, text="=== Hotkeys ===", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        self.start_stop_label = ttk.Label(scrollable_frame, text=f"Start/Stop: {self.start_stop_key.upper()} [OFF]", font=("Arial", 10))
        self.start_stop_label.grid(row=1, column=0, pady=5, sticky=tk.W)
        start_stop_btn = ttk.Button(scrollable_frame, text="Rebind", command=lambda: self.start_rebind('start_stop'))
        start_stop_btn.grid(row=1, column=1, padx=10)
        
        self.change_area_label = ttk.Label(scrollable_frame, text=f"Change Area: {self.change_area_key.upper()} [OFF]", font=("Arial", 10))
        self.change_area_label.grid(row=2, column=0, pady=5, sticky=tk.W)
        change_area_btn = ttk.Button(scrollable_frame, text="Rebind", command=lambda: self.start_rebind('change_area'))
        change_area_btn.grid(row=2, column=1, padx=10)
        
        self.exit_label = ttk.Label(scrollable_frame, text=f"Exit: {self.exit_key.upper()}", font=("Arial", 10))
        self.exit_label.grid(row=3, column=0, pady=5, sticky=tk.W)
        exit_btn = ttk.Button(scrollable_frame, text="Rebind", command=lambda: self.start_rebind('exit'))
        exit_btn.grid(row=3, column=1, padx=10)
        
        # PD Controller section
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
        ttk.Label(scrollable_frame, text="=== PD Controller ===", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        self.kp_var = tk.StringVar(value=str(self.kp))
        ttk.Label(scrollable_frame, text="KP (Proportional):").grid(row=6, column=0, pady=5, sticky=tk.W)
        kp_entry = ttk.Entry(scrollable_frame, textvariable=self.kp_var, width=10)
        kp_entry.grid(row=6, column=1, pady=5, sticky=tk.W)
        kp_entry.bind('<FocusOut>', lambda e: self.update_setting('kp', self.kp_var))
        kp_entry.bind('<Return>', lambda e: self.update_setting('kp', self.kp_var))
        
        self.kd_var = tk.StringVar(value=str(self.kd))
        ttk.Label(scrollable_frame, text="KD (Derivative):").grid(row=7, column=0, pady=5, sticky=tk.W)
        kd_entry = ttk.Entry(scrollable_frame, textvariable=self.kd_var, width=10)
        kd_entry.grid(row=7, column=1, pady=5, sticky=tk.W)
        kd_entry.bind('<FocusOut>', lambda e: self.update_setting('kd', self.kd_var))
        kd_entry.bind('<Return>', lambda e: self.update_setting('kd', self.kd_var))
        
        self.pd_clamp_var = tk.StringVar(value=str(self.pd_clamp))
        ttk.Label(scrollable_frame, text="PD Clamp:").grid(row=8, column=0, pady=5, sticky=tk.W)
        pd_clamp_entry = ttk.Entry(scrollable_frame, textvariable=self.pd_clamp_var, width=10)
        pd_clamp_entry.grid(row=8, column=1, pady=5, sticky=tk.W)
        pd_clamp_entry.bind('<FocusOut>', lambda e: self.update_setting('pd_clamp', self.pd_clamp_var))
        pd_clamp_entry.bind('<Return>', lambda e: self.update_setting('pd_clamp', self.pd_clamp_var))
        
        self.action_threshold_var = tk.StringVar(value=str(self.action_threshold))
        ttk.Label(scrollable_frame, text="Action Threshold (px):").grid(row=9, column=0, pady=5, sticky=tk.W)
        action_threshold_entry = ttk.Entry(scrollable_frame, textvariable=self.action_threshold_var, width=10)
        action_threshold_entry.grid(row=9, column=1, pady=5, sticky=tk.W)
        action_threshold_entry.bind('<FocusOut>', lambda e: self.update_setting('action_threshold', self.action_threshold_var))
        action_threshold_entry.bind('<Return>', lambda e: self.update_setting('action_threshold', self.action_threshold_var))
        
        # Auto-cast section
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=10, column=0, columnspan=3, sticky='ew', pady=10)
        ttk.Label(scrollable_frame, text="=== Auto-Cast Settings ===", font=("Arial", 12, "bold")).grid(row=11, column=0, columnspan=3, pady=(0, 10))
        
        self.cast_hold_time_var = tk.StringVar(value=str(self.cast_hold_time))
        ttk.Label(scrollable_frame, text="Cast Hold Time (s):").grid(row=12, column=0, pady=5, sticky=tk.W)
        cast_hold_entry = ttk.Entry(scrollable_frame, textvariable=self.cast_hold_time_var, width=10)
        cast_hold_entry.grid(row=12, column=1, pady=5, sticky=tk.W)
        cast_hold_entry.bind('<FocusOut>', lambda e: self.update_setting('cast_hold_time', self.cast_hold_time_var))
        cast_hold_entry.bind('<Return>', lambda e: self.update_setting('cast_hold_time', self.cast_hold_time_var))
        
        self.wait_time_var = tk.StringVar(value=str(self.cast_wait_time))
        ttk.Label(scrollable_frame, text="Cast Wait Time (s):").grid(row=13, column=0, pady=5, sticky=tk.W)
        wait_entry = ttk.Entry(scrollable_frame, textvariable=self.wait_time_var, width=10)
        wait_entry.grid(row=13, column=1, pady=5, sticky=tk.W)
        wait_entry.bind('<FocusOut>', lambda e: self.update_setting('cast_wait_time', self.wait_time_var))
        wait_entry.bind('<Return>', lambda e: self.update_setting('cast_wait_time', self.wait_time_var))
        
        self.detection_timeout_var = tk.StringVar(value=str(self.detection_timeout))
        ttk.Label(scrollable_frame, text="Detection Timeout (s):").grid(row=14, column=0, pady=5, sticky=tk.W)
        detection_entry = ttk.Entry(scrollable_frame, textvariable=self.detection_timeout_var, width=10)
        detection_entry.grid(row=14, column=1, pady=5, sticky=tk.W)
        detection_entry.bind('<FocusOut>', lambda e: self.update_setting('detection_timeout', self.detection_timeout_var))
        detection_entry.bind('<Return>', lambda e: self.update_setting('detection_timeout', self.detection_timeout_var))
        
        self.recast_delay_var = tk.StringVar(value=str(self.recast_delay))
        ttk.Label(scrollable_frame, text="Recast Delay (s):").grid(row=15, column=0, pady=5, sticky=tk.W)
        recast_entry = ttk.Entry(scrollable_frame, textvariable=self.recast_delay_var, width=10)
        recast_entry.grid(row=15, column=1, pady=5, sticky=tk.W)
        recast_entry.bind('<FocusOut>', lambda e: self.update_setting('recast_delay', self.recast_delay_var))
        recast_entry.bind('<Return>', lambda e: self.update_setting('recast_delay', self.recast_delay_var))        
        self.tolerance_var = tk.StringVar(value=str(self.tolerance))
        ttk.Label(scrollable_frame, text="Color Tolerance:").grid(row=15, column=0, pady=5, sticky=tk.W)
        tolerance_entry = ttk.Entry(scrollable_frame, textvariable=self.tolerance_var, width=10)
        tolerance_entry.grid(row=15, column=1, pady=5, sticky=tk.W)
        tolerance_entry.bind('<FocusOut>', lambda e: self.update_setting('tolerance', self.tolerance_var))
        tolerance_entry.bind('<Return>', lambda e: self.update_setting('tolerance', self.tolerance_var))        
        # Register hotkeys
        self.register_hotkeys()
    
    def update_setting(self, setting_name, var, event=None):
        """Generic method to update any numeric setting"""
        try:
            new_value = float(var.get())
            if new_value >= 0:  # Allow 0 for some settings
                setattr(self, setting_name, new_value)
                self.save_settings()
                print(f"Updated {setting_name} to {new_value}")
        except ValueError:
            # Revert to current value if invalid
            var.set(str(getattr(self, setting_name)))
            print(f"Invalid value for {setting_name}, reverted to {getattr(self, setting_name)}")
    
    def register_hotkeys(self):
        keyboard.unhook_all()
        keyboard.add_hotkey(self.start_stop_key, self.toggle_start_stop)
        keyboard.add_hotkey(self.change_area_key, self.toggle_change_area)
        keyboard.add_hotkey(self.exit_key, self.exit_app)
    
    def start_rebind(self, action):
        self.waiting_for_key = action
        if action == 'start_stop':
            state_text = "ON" if self.start_stop_state else "OFF"
            self.start_stop_label.config(text=f"Start/Stop: Press a key... [{state_text}]")
        elif action == 'change_area':
            state_text = "ON" if self.change_area_state else "OFF"
            self.change_area_label.config(text=f"Change Area: Press a key... [{state_text}]")
        elif action == 'exit':
            self.exit_label.config(text="Exit: Press a key...")
        
        keyboard.hook(self.on_key_event)
    
    def on_key_event(self, event):
        if self.waiting_for_key and event.event_type == 'down':
            new_key = event.name
            
            if self.waiting_for_key == 'start_stop':
                self.start_stop_key = new_key
                state_text = "ON" if self.start_stop_state else "OFF"
                self.start_stop_label.config(text=f"Start/Stop: {new_key.upper()} [{state_text}]")
            elif self.waiting_for_key == 'change_area':
                self.change_area_key = new_key
                state_text = "ON" if self.change_area_state else "OFF"
                self.change_area_label.config(text=f"Change Area: {new_key.upper()} [{state_text}]")
            elif self.waiting_for_key == 'exit':
                self.exit_key = new_key
                self.exit_label.config(text=f"Exit: {new_key.upper()}")
            
            self.waiting_for_key = None
            self.save_settings()
            self.register_hotkeys()
        
    def toggle_start_stop(self):
        self.start_stop_state = not self.start_stop_state
        state_text = "ON" if self.start_stop_state else "OFF"
        key_display = self.start_stop_key.upper()
        self.start_stop_label.config(text=f"Start/Stop: {key_display} [{state_text}]")
        
        if self.start_stop_state:
            # Create overlay if it doesn't exist
            if not self.indicator_overlay:
                self.create_indicator_overlay()
            # Start the main loop in a background thread
            self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.main_loop_thread.start()
        else:
            # Hide overlay when stopped
            if self.indicator_overlay:
                self.indicator_overlay.withdraw()
    
    def create_indicator_overlay(self):
        """Create a persistent transparent overlay for the indicator arrow"""
        import win32api
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        self.indicator_overlay = tk.Toplevel(self.root)
        self.indicator_overlay.attributes('-topmost', True)
        self.indicator_overlay.attributes('-transparentcolor', 'black')
        self.indicator_overlay.overrideredirect(True)
        self.indicator_overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.indicator_overlay.configure(bg='black')
        
        self.indicator_canvas = tk.Canvas(self.indicator_overlay, bg='black', highlightthickness=0)
        self.indicator_canvas.pack(fill='both', expand=True)
        self.indicator_arrow_id = None
    
    def update_indicator_arrow(self, x, y):
        """Update or create arrow at specified position"""
        size = self.arrow_size
        arrow_coords = [
            x, y,              # bottom point (pointing down)
            x-size//2, y-size,   # left point
            x+size//2, y-size    # right point
        ]
        
        if self.indicator_arrow_id:
            try:
                self.indicator_canvas.coords(self.indicator_arrow_id, *arrow_coords)
            except:
                self.indicator_arrow_id = self.indicator_canvas.create_polygon(arrow_coords, fill='green', outline='green')
        else:
            self.indicator_arrow_id = self.indicator_canvas.create_polygon(arrow_coords, fill='green', outline='green')
        
        # Show overlay if hidden
        if self.indicator_overlay.state() == 'withdrawn':
            self.indicator_overlay.deiconify()
    
    def hide_indicator_arrow(self):
        """Hide the indicator arrow"""
        if self.indicator_arrow_id and self.indicator_canvas:
            try:
                self.indicator_canvas.delete(self.indicator_arrow_id)
                self.indicator_arrow_id = None
            except:
                pass
    
    def update_side_arrow(self, x, y, is_left):
        """Update or create upward-pointing arrow at specified position"""
        size = self.arrow_size
        # Upward pointing arrow (opposite of downward)
        arrow_coords = [
            x, y,              # top point (pointing up)
            x-size//2, y+size,   # bottom-left point
            x+size//2, y+size    # bottom-right point
        ]
        
        arrow_id_attr = 'left_arrow_id' if is_left else 'right_arrow_id'
        arrow_id = getattr(self, arrow_id_attr)
        
        if arrow_id:
            try:
                self.indicator_canvas.coords(arrow_id, *arrow_coords)
            except:
                new_id = self.indicator_canvas.create_polygon(arrow_coords, fill='red', outline='red')
                setattr(self, arrow_id_attr, new_id)
        else:
            new_id = self.indicator_canvas.create_polygon(arrow_coords, fill='red', outline='red')
            setattr(self, arrow_id_attr, new_id)
        
        # Show overlay if hidden
        if self.indicator_overlay.state() == 'withdrawn':
            self.indicator_overlay.deiconify()
    
    def hide_side_arrows(self):
        """Hide the left and right arrows"""
        if self.indicator_canvas:
            try:
                if self.left_arrow_id:
                    self.indicator_canvas.delete(self.left_arrow_id)
                    self.left_arrow_id = None
                if self.right_arrow_id:
                    self.indicator_canvas.delete(self.right_arrow_id)
                    self.right_arrow_id = None
            except:
                pass
    
    def main_loop(self):
        """Main loop that runs when Start/Stop is ON"""
        print("Main loop started")
        
        # Reset cast state
        self.cast_state = "holding"
        self.cast_timer = time.time()
        
        # Initial cast: Hold left click for 500ms
        print("Initial cast: Holding left click...")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        self.mouse_down = True
        time.sleep(self.cast_hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.mouse_down = False
        print(f"Released. Waiting {self.cast_wait_time}s...")
        
        # Wait for configured time
        self.cast_state = "waiting"
        self.cast_timer = time.time()
        time.sleep(self.cast_wait_time)
        
        # Start detection phase
        self.cast_state = "detecting"
        self.cast_timer = time.time()
        print("Starting detection phase...")
        
        # Color range with tolerance for first search (green icon)
        tolerance = int(self.tolerance)
        r_min, r_max = 155 - tolerance, 180 + tolerance
        g_min, g_max = 190 - tolerance, 225 + tolerance
        b_min, b_max = 115 - tolerance, 150 + tolerance
        
        # Color ranges for second search (left/right points)
        # Color 1: (156, 217, 120)
        c1_r_min, c1_r_max = 156 - tolerance, 156 + tolerance
        c1_g_min, c1_g_max = 217 - tolerance, 217 + tolerance
        c1_b_min, c1_b_max = 120 - tolerance, 120 + tolerance
        
        # Color 2: (221, 254, 112)
        c2_r_min, c2_r_max = 221 - tolerance, 221 + tolerance
        c2_g_min, c2_g_max = 254 - tolerance, 254 + tolerance
        c2_b_min, c2_b_max = 112 - tolerance, 112 + tolerance
        
        with mss.mss() as sct:
            while self.start_stop_state:
                # Define the monitor area from settings
                monitor = {
                    "left": self.area_coords['x'],
                    "top": self.area_coords['y'],
                    "width": self.area_coords['width'],
                    "height": self.area_coords['height']
                }
                
                # Capture the area
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array for processing (BGRA format)
                img = np.array(screenshot)
                
                # FIRST SEARCH: Search from top to bottom for matching color (green icon)
                found = False
                target_x = None
                for y in range(img.shape[0]):
                    for x in range(img.shape[1]):
                        b, g, r = img[y, x, 0], img[y, x, 1], img[y, x, 2]
                        
                        # Check if pixel is within color range
                        if (r_min <= r <= r_max and 
                            g_min <= g <= g_max and 
                            b_min <= b <= b_max):
                            # Calculate absolute coordinates
                            abs_x = self.area_coords['x'] + x
                            abs_y = self.area_coords['y'] + y
                            target_x = abs_x
                            print(f"Match found at: ({abs_x}, {abs_y}) | RGB: ({r}, {g}, {b})")
                            
                            # Update indicator arrow
                            self.update_indicator_arrow(abs_x, abs_y)
                            
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    print("No match found")
                    # Hide indicator if no match
                    self.hide_indicator_arrow()
                    self.hide_side_arrows()
                    # Release mouse if held
                    if self.mouse_down:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        self.mouse_down = False
                    
                    # Handle different states when green is not found
                    if self.cast_state == "detecting":
                        # Initial detection phase - check timeout
                        elapsed = time.time() - self.cast_timer
                        if elapsed > self.detection_timeout:
                            print(f"Detection timeout ({self.detection_timeout}s). Recasting...")
                            
                            # Hold left click for 500ms
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            self.mouse_down = True
                            time.sleep(self.cast_hold_time)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            self.mouse_down = False
                            print(f"Recast complete. Waiting {self.cast_wait_time}s...")
                            
                            # Wait and restart detection
                            time.sleep(self.cast_wait_time)
                            self.cast_state = "detecting"
                            self.cast_timer = time.time()
                            print("Restarting detection phase...")
                    
                    elif self.cast_state == "active":
                        # Green disappeared during active minigame - start recast timer
                        if self.green_lost_time is None:
                            self.green_lost_time = time.time()
                            print("Green lost during minigame. Starting recast timer...")
                        else:
                            # Check if we've waited long enough
                            elapsed = time.time() - self.green_lost_time
                            print(f"Waiting for recast... {elapsed:.2f}s / {self.recast_delay}s")
                            if elapsed >= self.recast_delay:
                                print(f"Minigame ended. Recasting now...")
                                self.green_lost_time = None
                                
                                # Hold left click for 500ms
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                self.mouse_down = True
                                time.sleep(self.cast_hold_time)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                self.mouse_down = False
                                print(f"Recast complete. Waiting {self.cast_wait_time}s...")
                                
                                # Wait and restart detection
                                time.sleep(self.cast_wait_time)
                                self.cast_state = "detecting"
                                self.cast_timer = time.time()
                                print("Restarting detection phase...")
                else:
                    # Found target
                    if self.cast_state == "detecting":
                        self.cast_state = "active"
                        self.green_lost_time = None
                        print("Target found! Switching to active tracking mode.")
                    elif self.cast_state == "active":
                        # Reset green lost timer since we found it again
                        self.green_lost_time = None
                    # SECOND SEARCH: Search from bottom to top for left and right points
                    left_point = None
                    right_point = None
                    
                    # Search from bottom to top
                    for y in range(img.shape[0] - 1, -1, -1):
                        # Search left to right for left point (if not found yet)
                        if left_point is None:
                            for x in range(img.shape[1]):
                                b, g, r = img[y, x, 0], img[y, x, 1], img[y, x, 2]
                                
                                # Check if matches either color
                                if ((c1_r_min <= r <= c1_r_max and c1_g_min <= g <= c1_g_max and c1_b_min <= b <= c1_b_max) or
                                    (c2_r_min <= r <= c2_r_max and c2_g_min <= g <= c2_g_max and c2_b_min <= b <= c2_b_max)):
                                    left_point = (self.area_coords['x'] + x, self.area_coords['y'] + y)
                                    print(f"Left point found at: {left_point} | RGB: ({r}, {g}, {b})")
                                    # Update left arrow (pointing upward, positioned below the point)
                                    self.update_side_arrow(left_point[0], left_point[1] + self.arrow_size, True)
                                    break
                        
                        # Search right to left for right point (if not found yet)
                        if right_point is None:
                            for x in range(img.shape[1] - 1, -1, -1):
                                b, g, r = img[y, x, 0], img[y, x, 1], img[y, x, 2]
                                
                                # Check if matches either color
                                if ((c1_r_min <= r <= c1_r_max and c1_g_min <= g <= c1_g_max and c1_b_min <= b <= c1_b_max) or
                                    (c2_r_min <= r <= c2_r_max and c2_g_min <= g <= c2_g_max and c2_b_min <= b <= c2_b_max)):
                                    right_point = (self.area_coords['x'] + x, self.area_coords['y'] + y)
                                    print(f"Right point found at: {right_point} | RGB: ({r}, {g}, {b})")
                                    # Update right arrow (pointing upward, positioned below the point)
                                    self.update_side_arrow(right_point[0], right_point[1] + self.arrow_size, False)
                                    break
                        
                        # If both points found, exit search
                        if left_point and right_point:
                            break
                    
                    if not left_point or not right_point:
                        if not left_point:
                            print("Left point not found")
                        if not right_point:
                            print("Right point not found")
                        # Hide arrows for any points not found
                        if not left_point and self.left_arrow_id:
                            self.indicator_canvas.delete(self.left_arrow_id)
                            self.left_arrow_id = None
                        if not right_point and self.right_arrow_id:
                            self.indicator_canvas.delete(self.right_arrow_id)
                            self.right_arrow_id = None
                    else:
                        # Both points found - calculate middle point
                        middle_x = (left_point[0] + right_point[0]) // 2
                        middle_y = (left_point[1] + right_point[1]) // 2
                        print(f"Middle point: ({middle_x}, {middle_y})")
                        
                        # PD Controller logic (675.py exact implementation)
                        if target_x is not None:
                            error = target_x - middle_x  # Positive = target is RIGHT, need HOLD
                            
                            # Calculate time delta for derivative
                            current_time_pd = time.time()
                            if self.last_time_pd is None:
                                self.last_time_pd = current_time_pd
                            time_delta = current_time_pd - self.last_time_pd
                            self.last_time_pd = current_time_pd
                            
                            # Calculate P term
                            P_term = self.kp * error
                            
                            # Calculate D term (only if we have previous error and valid time delta)
                            D_term = 0.0
                            if self.last_error is not None and time_delta > 0.001:
                                error_rate = (error - self.last_error) / time_delta
                                D_term = self.kd * error_rate
                            
                            # Combine into control signal
                            control_signal = P_term + D_term
                            
                            # Clamp control signal
                            control_signal = np.clip(control_signal, -self.pd_clamp, self.pd_clamp)
                            
                            # Determine action based on control signal
                            if control_signal > self.action_threshold:
                                # Target is RIGHT, needs HOLD
                                should_hold = True
                                control_mode = "HOLD"
                            elif control_signal < -self.action_threshold:
                                # Target is LEFT, needs RELEASE
                                should_hold = False
                                control_mode = "RELEASE"
                            else:
                                # Within dead zone: SPAM CLICK
                                should_hold = not self.mouse_down
                                control_mode = "SPAM"
                            
                            # Execute mouse action
                            if should_hold and not self.mouse_down:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                self.mouse_down = True
                            elif not should_hold and self.mouse_down:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                self.mouse_down = False
                            
                            print(f"{control_mode} | Error: {error:.1f}px | P: {P_term:.2f} | D: {D_term:.2f} | Signal: {control_signal:.2f}")
                            
                            # Update for next iteration
                            self.last_error = error
        
        # Release mouse and hide overlay when loop stops
        if self.mouse_down:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            self.mouse_down = False
        if self.indicator_overlay:
            self.indicator_overlay.withdraw()
        print("Main loop stopped")
        
    def toggle_change_area(self):
        self.change_area_state = not self.change_area_state
        state_text = "ON" if self.change_area_state else "OFF"
        key_display = self.change_area_key.upper()
        self.change_area_label.config(text=f"Change Area: {key_display} [{state_text}]")
        
        if self.change_area_state:
            # Open area selector with saved coordinates
            self.area_selector = AreaSelector(
                x=self.area_coords['x'],
                y=self.area_coords['y'],
                width=self.area_coords['width'],
                height=self.area_coords['height']
            )
        else:
            # Close area selector and save coordinates
            if self.area_selector:
                self.area_coords = self.area_selector.get_coordinates()
                self.area_selector.close()
                self.area_selector = None
                self.save_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.start_stop_key = settings.get('start_stop_key', 'f3')
                    self.change_area_key = settings.get('change_area_key', 'f1')
                    self.exit_key = settings.get('exit_key', 'f4')
                    self.area_coords = settings.get('area_coords', self.get_scaled_default_area())
                    
                    # Load all tunable parameters
                    self.kp = settings.get('kp', 15.0)
                    self.kd = settings.get('kd', 30.0)
                    self.pd_clamp = settings.get('pd_clamp', 30.0)
                    self.action_threshold = settings.get('action_threshold', 2.0)
                    self.cast_hold_time = settings.get('cast_hold_time', 0.5)
                    self.cast_wait_time = settings.get('cast_wait_time', 2.0)
                    self.detection_timeout = settings.get('detection_timeout', 5.0)
                    self.recast_delay = settings.get('recast_delay', 0.5)
                    self.tolerance = settings.get('tolerance', 20)
                    
                    # Update GUI variables if they exist
                    if hasattr(self, 'kp_var'):
                        self.kp_var.set(str(self.kp))
                    if hasattr(self, 'kd_var'):
                        self.kd_var.set(str(self.kd))
                    if hasattr(self, 'pd_clamp_var'):
                        self.pd_clamp_var.set(str(self.pd_clamp))
                    if hasattr(self, 'action_threshold_var'):
                        self.action_threshold_var.set(str(self.action_threshold))
                    if hasattr(self, 'cast_hold_time_var'):
                        self.cast_hold_time_var.set(str(self.cast_hold_time))
                    if hasattr(self, 'wait_time_var'):
                        self.wait_time_var.set(str(self.cast_wait_time))
                    if hasattr(self, 'detection_timeout_var'):
                        self.detection_timeout_var.set(str(self.detection_timeout))
                    if hasattr(self, 'recast_delay_var'):
                        self.recast_delay_var.set(str(self.recast_delay))
                    if hasattr(self, 'tolerance_var'):
                        self.tolerance_var.set(str(self.tolerance))
            else:
                # First launch - use scaled defaults
                self.area_coords = self.get_scaled_default_area()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Fallback to scaled defaults on error
            self.area_coords = self.get_scaled_default_area()
    
    def get_scaled_default_area(self):
        """Calculate scaled default area based on current screen resolution"""
        # Reference resolution (2560x1440) and reference area
        ref_width, ref_height = 2560, 1440
        ref_x, ref_y = 765, 1138
        ref_area_width, ref_area_height = 1030, 118
        
        # Get current screen resolution
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        # Calculate scale factors
        scale_x = screen_width / ref_width
        scale_y = screen_height / ref_height
        
        # Scale the coordinates
        scaled_x = int(ref_x * scale_x)
        scaled_y = int(ref_y * scale_y)
        scaled_width = int(ref_area_width * scale_x)
        scaled_height = int(ref_area_height * scale_y)
        
        print(f"Screen resolution: {screen_width}x{screen_height}")
        print(f"Scale factors: {scale_x:.2f}x, {scale_y:.2f}y")
        print(f"Scaled area: x={scaled_x}, y={scaled_y}, w={scaled_width}, h={scaled_height}")
        
        return {
            'x': scaled_x,
            'y': scaled_y,
            'width': scaled_width,
            'height': scaled_height
        }
    
    def save_settings(self):
        try:
            settings = {
                'start_stop_key': self.start_stop_key,
                'change_area_key': self.change_area_key,
                'exit_key': self.exit_key,
                'area_coords': self.area_coords,
                'kp': self.kp,
                'kd': self.kd,
                'pd_clamp': self.pd_clamp,
                'action_threshold': self.action_threshold,
                'cast_hold_time': self.cast_hold_time,
                'cast_wait_time': self.cast_wait_time,
                'detection_timeout': self.detection_timeout,
                'recast_delay': self.recast_delay,
                'tolerance': self.tolerance
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def exit_app(self):
        # Close area selector if open
        if self.area_selector:
            self.area_selector.close()
        # Close indicator overlay if open
        if self.indicator_overlay:
            self.indicator_overlay.destroy()
        keyboard.unhook_all()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = GlorpGUI(root)
    root.mainloop()
