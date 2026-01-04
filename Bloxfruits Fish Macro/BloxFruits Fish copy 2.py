import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import json
import os
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import numpy as np
import win32api
import win32con
import time
import dxcam


# ============================================================================
# COLOR DEFINITIONS
# ============================================================================
COLORS = {
    # Bar colors
    "BAR": (12, 131, 11),           # #0C830B - Green bar
    "FISH_BAR": (5, 140, 133),      # #058C85 - Cyan bar
    "TREASURE_BAR": (168, 165, 41), # #A8A529 - Yellow bar
    "OFF_BAR": (85, 85, 83),        # #555553 - Gray bar
    "ARROW": (213, 213, 213),       # #D5D5D5 - White arrow
    
    # Fish colors
    "FISH": (25, 133, 253),         # #1985FD - Bright blue
    "FISH_2": (0, 54, 129),         # #003681 - Dark blue
    
    # Treasure colors
    "TREASURE": (196, 83, 2),       # #C45302 - Orange
    "TREASURE_2": (254, 233, 109)   # #FEE96D - Yellow
}


# ============================================================================
# DUAL AREA SELECTOR CLASS
# ============================================================================
class DualAreaSelector:
    """Full-screen overlay for selecting 2 areas simultaneously"""
    
    def __init__(self, parent, screenshot, indicator_box, fish_box, callback):
        self.callback = callback
        self.screenshot = screenshot
        
        # Create fullscreen window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.configure(cursor='cross')
        
        # Get screen dimensions
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        # Convert PIL image to PhotoImage
        self.photo = ImageTk.PhotoImage(screenshot)
        
        # Create canvas with screenshot
        self.canvas = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.pack()
        
        # Display frozen screenshot
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        
        # Initialize boxes
        self.boxes = {
            'indicator': {'coords': indicator_box.copy(), 'color': '#00ff00', 'name': 'Indicator_Area'},  # Green
            'fish': {'coords': fish_box.copy(), 'color': '#ff0000', 'name': 'Fish_Area'}                 # Red
        }
        
        # Drawing state
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
        self.resize_threshold = 10
        
        # Create rectangles and handles for all boxes
        self.rects = {}
        self.labels = {}
        self.handles = {}
        
        for box_id, box_data in self.boxes.items():
            self.create_box(box_id)
        
        # Zoom window settings
        self.zoom_window_size = 150
        self.zoom_factor = 4
        self.zoom_rect = None
        self.zoom_image_id = None
        self.zoom_photo = None
        
        # Instructions
        self.create_instructions()
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.focus_set()
    
    def create_instructions(self):
        """Create instruction text at the top of the screen"""
        instructions = [
            "Select Indicator Area (Green) and Fish Area (Red)",
            "Drag corners to resize | Drag inside to move",
            "Press F1 again to confirm and save"
        ]
        
        y_pos = 20
        for i, text in enumerate(instructions):
            self.canvas.create_text(
                self.screen_width // 2, y_pos + (i * 30),
                text=text,
                font=("Arial", 16, "bold"),
                fill='white',
                tags='instructions'
            )
            # Add shadow for better visibility
            self.canvas.create_text(
                self.screen_width // 2 + 2, y_pos + (i * 30) + 2,
                text=text,
                font=("Arial", 16, "bold"),
                fill='black',
                tags='instructions_shadow'
            )
            self.canvas.tag_lower('instructions_shadow')
    
    def create_box(self, box_id):
        """Create a box with its rectangle, label, and handles"""
        box_data = self.boxes[box_id]
        coords = box_data['coords']
        color = box_data['color']
        name = box_data['name']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        # Create rectangle
        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=3,
            fill=color,
            stipple='gray50',
            tags=f'{box_id}_box'
        )
        self.rects[box_id] = rect
        
        # Create label
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        label = self.canvas.create_text(
            label_x, label_y,
            text=name,
            font=("Arial", 14, "bold"),
            fill=color,
            tags=f'{box_id}_label'
        )
        self.labels[box_id] = label
        
        # Create handles
        self.create_handles_for_box(box_id)
    
    def create_handles_for_box(self, box_id):
        """Create corner handles for a specific box"""
        handle_size = 12
        corner_marker_size = 3
        
        box_data = self.boxes[box_id]
        coords = box_data['coords']
        color = box_data['color']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        corners = [
            (x1, y1, 'nw'),
            (x2, y1, 'ne'),
            (x1, y2, 'sw'),
            (x2, y2, 'se')
        ]
        
        # Delete old handles
        if box_id in self.handles:
            for handle in self.handles[box_id]:
                self.canvas.delete(handle)
        
        self.handles[box_id] = []
        
        # Create new handles
        for x, y, corner in corners:
            # Outer handle
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline=color,
                width=2,
                tags=f'{box_id}_handle_{corner}'
            )
            self.handles[box_id].append(handle)
            
            # Corner marker
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='white',
                outline=color,
                width=1,
                tags=f'{box_id}_corner_{corner}'
            )
            self.handles[box_id].append(corner_marker)
            
            # Crosshair
            line1 = self.canvas.create_line(
                x - handle_size, y, x + handle_size, y,
                fill='white',
                width=1,
                tags=f'{box_id}_cross_{corner}'
            )
            line2 = self.canvas.create_line(
                x, y - handle_size, x, y + handle_size,
                fill='white',
                width=1,
                tags=f'{box_id}_cross_{corner}'
            )
            self.handles[box_id].append(line1)
            self.handles[box_id].append(line2)
    
    def get_corner_at_position(self, x, y, box_id):
        """Determine which corner is near the cursor for a specific box"""
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        corners = {
            'nw': (x1, y1),
            'ne': (x2, y1),
            'sw': (x1, y2),
            'se': (x2, y2)
        }
        
        for corner, (cx, cy) in corners.items():
            if abs(x - cx) < self.resize_threshold and abs(y - cy) < self.resize_threshold:
                return corner
        
        return None
    
    def is_inside_box(self, x, y, box_id):
        """Check if point is inside a specific box"""
        coords = self.boxes[box_id]['coords']
        return coords['x1'] < x < coords['x2'] and coords['y1'] < y < coords['y2']
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Check all boxes for corner or inside click
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = corner
                return
            
            if self.is_inside_box(event.x, event.y, box_id):
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = 'move'
                return
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging or not self.active_box:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        coords = self.boxes[self.active_box]['coords']
        
        if self.drag_corner == 'move':
            # Move entire box using delta
            coords['x1'] += dx
            coords['y1'] += dy
            coords['x2'] += dx
            coords['y2'] += dy
        else:
            # Resize from corner - snap directly to cursor position
            if self.drag_corner == 'nw':
                coords['x1'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'ne':
                coords['x2'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'sw':
                coords['x1'] = event.x
                coords['y2'] = event.y
            elif self.drag_corner == 'se':
                coords['x2'] = event.x
                coords['y2'] = event.y
            
            # Ensure valid rectangle
            if coords['x1'] > coords['x2']:
                coords['x1'], coords['x2'] = coords['x2'], coords['x1']
            if coords['y1'] > coords['y2']:
                coords['y1'], coords['y2'] = coords['y2'], coords['y1']
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.update_box(self.active_box)
        self.show_zoom(event.x, event.y)
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
    
    def on_mouse_move(self, event):
        """Handle mouse movement for cursor changes"""
        cursor = 'cross'
        
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                cursor_map = {
                    'nw': 'size_nw_se',
                    'ne': 'size_ne_sw',
                    'sw': 'size_ne_sw',
                    'se': 'size_nw_se'
                }
                cursor = cursor_map[corner]
                break
            elif self.is_inside_box(event.x, event.y, box_id):
                cursor = 'fleur'
                break
        
        self.window.configure(cursor=cursor)
        self.show_zoom(event.x, event.y)
    
    def update_box(self, box_id):
        """Update box rectangle, label, and handles"""
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        # Update rectangle
        self.canvas.coords(self.rects[box_id], x1, y1, x2, y2)
        
        # Update label
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        self.canvas.coords(self.labels[box_id], label_x, label_y)
        
        # Update handles
        self.create_handles_for_box(box_id)
    
    def show_zoom(self, x, y):
        """Display mini zoom window following cursor"""
        # Delete previous zoom elements
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
        if self.zoom_image_id:
            self.canvas.delete(self.zoom_image_id)
        
        # Calculate source region to zoom
        zoom_src_size = self.zoom_window_size // self.zoom_factor
        x1_src = max(0, x - zoom_src_size // 2)
        y1_src = max(0, y - zoom_src_size // 2)
        x2_src = min(self.screen_width, x1_src + zoom_src_size)
        y2_src = min(self.screen_height, y1_src + zoom_src_size)
        
        # Crop and zoom the screenshot
        cropped = self.screenshot.crop((x1_src, y1_src, x2_src, y2_src))
        zoomed = cropped.resize((self.zoom_window_size, self.zoom_window_size), Image.NEAREST)
        
        # Draw crosshair on zoomed image
        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_window_size // 2
        crosshair_size = 10
        draw.line([(center - crosshair_size, center), (center + crosshair_size, center)], fill='red', width=2)
        draw.line([(center, center - crosshair_size), (center, center + crosshair_size)], fill='red', width=2)
        
        # Convert to PhotoImage
        self.zoom_photo = ImageTk.PhotoImage(zoomed)
        
        # Position zoom window near cursor
        zoom_x = x + 30
        zoom_y = y + 30
        
        # Keep zoom window on screen
        if zoom_x + self.zoom_window_size > self.screen_width:
            zoom_x = x - self.zoom_window_size - 30
        if zoom_y + self.zoom_window_size > self.screen_height:
            zoom_y = y - self.zoom_window_size - 30
        
        # Draw zoom window background
        self.zoom_rect = self.canvas.create_rectangle(
            zoom_x, zoom_y,
            zoom_x + self.zoom_window_size, zoom_y + self.zoom_window_size,
            fill='black',
            outline='white',
            width=2
        )
        
        # Draw zoomed image
        self.zoom_image_id = self.canvas.create_image(
            zoom_x, zoom_y,
            image=self.zoom_photo,
            anchor='nw'
        )
    
    def finish_selection(self):
        """Close the selector and return the selected areas"""
        indicator_box = self.boxes['indicator']['coords']
        fish_box = self.boxes['fish']['coords']
        
        self.window.destroy()
        self.callback(indicator_box, fish_box)


# ============================================================================
# CENTRAL STORAGE CLASS
# ============================================================================
class CentralStorage:
    """
    Central storage for all GUI settings and options.
    Automatically saves to and loads from a JSON file.
    """
    
    def __init__(self, config_file="bloxfruits_config.json"):
        """Initialize central storage with default values."""
        self.config_file = config_file
        
        # Get current screen resolution
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Base resolution these coordinates were designed for
        base_width = 2560
        base_height = 1440
        
        # Scale factors
        scale_x = screen_width / base_width
        scale_y = screen_height / base_height
        
        # Original coordinates scaled to current resolution
        self.settings = {
            # Hotkey settings (persisted)
            "hotkeys": {
                "start_stop": "F3",
                "change_area": "F1",
                "exit": "F4"
            },
            # Area boxes (persisted)
            "area_boxes": {
                "indicator_box": {
                    "x1": int(1213 * scale_x),
                    "y1": int(511 * scale_y),
                    "x2": int(1348 * scale_x),
                    "y2": int(655 * scale_y)
                },
                "fish_box": {
                    "x1": int(695 * scale_x),
                    "y1": int(1075 * scale_y),
                    "x2": int(1856 * scale_x),
                    "y2": int(1105 * scale_y)
                }
            },
            # Detection settings (persisted)
            "detection_settings": {
                "color_tolerance": 5,
                "lure_timeout": 10,
                "fish_timeout": 3,
                "bar_tolerance": 5,
                "arrow_tolerance": 5,
                "fish_tolerance": 5,
                "treasure_tolerance": 5,
                "kp": 1.0,
                "kd": 0.5,
                "click_duration": 3.0
            },
            # Keybind settings (persisted)
            "keybind_settings": {
                "not_rod_keybind": None,
                "rod_keybind": None
            },
            # Feature toggles (persisted)
            "feature_toggles": {
                "get_chest": False,
                "new_fish_wait": False
            }
        }
        
        # Runtime states (NOT persisted - always start at False)
        self.runtime_states = {
            "is_running": False,
            "change_area_enabled": False
        }
        
        # Load existing settings if file exists
        self.load()
    
    def load(self):
        """Load settings from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values (preserves new defaults)
                    self._merge_settings(loaded_settings)
                print(f"Settings loaded from {self.config_file}")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save(self):
        """Save current settings to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _merge_settings(self, loaded_settings):
        """Merge loaded settings with current settings."""
        for key, value in loaded_settings.items():
            if isinstance(value, dict) and key in self.settings:
                self.settings[key].update(value)
            else:
                self.settings[key] = value
    
    def get_hotkey(self, key_name):
        """Get hotkey string for a specific action."""
        return self.settings["hotkeys"].get(key_name, "F3")
    
    def set_hotkey(self, key_name, key_value):
        """Set hotkey for a specific action and save."""
        self.settings["hotkeys"][key_name] = key_value
        self.save()
    
    def get_state(self, state_name):
        """Get runtime state value (not persisted)."""
        return self.runtime_states.get(state_name, False)
    
    def set_state(self, state_name, value):
        """Set runtime state value (not persisted)."""
        self.runtime_states[state_name] = value
    
    def toggle_state(self, state_name):
        """Toggle a boolean runtime state (not persisted)."""
        current = self.get_state(state_name)
        self.set_state(state_name, not current)
        return not current
    
    def get_area_box(self, box_name):
        """Get area box coordinates."""
        return self.settings["area_boxes"].get(box_name, {"x1": 0, "y1": 0, "x2": 100, "y2": 100})
    
    def set_area_boxes(self, indicator_box, fish_box):
        """Set area box coordinates and save."""
        self.settings["area_boxes"]["indicator_box"] = indicator_box
        self.settings["area_boxes"]["fish_box"] = fish_box
        self.save()
    
    def get_detection_setting(self, setting_name):
        """Get detection setting value."""
        defaults = {
            "color_tolerance": 5, 
            "lure_timeout": 10,
            "fish_timeout": 3,
            "bar_tolerance": 5,
            "arrow_tolerance": 5,
            "fish_tolerance": 5,
            "treasure_tolerance": 5,
            "kp": 1.0,
            "kd": 0.5,
            "click_duration": 3.0
        }
        return self.settings["detection_settings"].get(setting_name, defaults.get(setting_name))
    
    def set_detection_setting(self, setting_name, value):
        """Set detection setting value and save."""
        self.settings["detection_settings"][setting_name] = value
        self.save()
    
    def get_keybind_setting(self, setting_name):
        """Get keybind setting value."""
        return self.settings["keybind_settings"].get(setting_name)
    
    def set_keybind_setting(self, setting_name, value):
        """Set keybind setting value and save."""
        self.settings["keybind_settings"][setting_name] = value
        self.save()
    
    def get_feature_toggle(self, toggle_name):
        """Get feature toggle value."""
        defaults = {"get_chest": False, "new_fish_wait": False}
        return self.settings["feature_toggles"].get(toggle_name, defaults.get(toggle_name))
    
    def set_feature_toggle(self, toggle_name, value):
        """Set feature toggle value and save."""
        self.settings["feature_toggles"][toggle_name] = value
        self.save()


# ============================================================================
# MAIN GUI CLASS
# ============================================================================
class BloxfruitsAutofishGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloxfruits Autofish - Made by AsphaltCake")
        self.root.geometry("550x550")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)
        
        # Initialize central storage
        self.storage = CentralStorage()
        
        # Rebinding state
        self.rebinding = None
        
        # Area selector reference
        self.area_selector = None
        
        # Setup GUI
        self.setup_gui()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        # Title label
        title_label = tk.Label(self.root, text="Bloxfruits Autofish", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        author_label = tk.Label(self.root, text="Made by AsphaltCake", 
                               font=("Arial", 10))
        author_label.pack(pady=5)
        
        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Start/Stop button
        self.start_stop_frame = tk.Frame(button_frame)
        self.start_stop_frame.pack(pady=10, fill="x")
        
        start_hotkey = self.storage.get_hotkey('start_stop')
        self.start_stop_btn = tk.Button(self.start_stop_frame, text=f"▶ Start ({start_hotkey})", 
                                        width=18, height=1, bg="#4CAF50", fg="white",
                                        font=("Arial", 9, "bold"),
                                        command=self.toggle_start_stop)
        self.start_stop_btn.pack(side="left", padx=5)
        
        rebind_start_btn = tk.Button(self.start_stop_frame, text="Rebind", 
                                     width=8, command=lambda: self.rebind_hotkey('start_stop'))
        rebind_start_btn.pack(side="left", padx=5)
        
        # Change Area button
        self.change_area_frame = tk.Frame(button_frame)
        self.change_area_frame.pack(pady=10, fill="x")
        
        change_hotkey = self.storage.get_hotkey('change_area')
        self.change_area_btn = tk.Button(self.change_area_frame, 
                                         text=f"Change Area: OFF ({change_hotkey})", 
                                         width=18, height=1, bg="#2196F3", fg="white",
                                         font=("Arial", 9, "bold"),
                                         command=self.toggle_change_area)
        self.change_area_btn.pack(side="left", padx=5)
        
        rebind_area_btn = tk.Button(self.change_area_frame, text="Rebind", 
                                    width=8, command=lambda: self.rebind_hotkey('change_area'))
        rebind_area_btn.pack(side="left", padx=5)
        
        # Exit button
        self.exit_frame = tk.Frame(button_frame)
        self.exit_frame.pack(pady=10, fill="x")
        
        exit_hotkey = self.storage.get_hotkey('exit')
        self.exit_btn = tk.Button(self.exit_frame, text=f"✕ Exit ({exit_hotkey})", 
                                  width=18, height=1, bg="#f44336", fg="white",
                                  font=("Arial", 9, "bold"),
                                  command=self.exit_app)
        self.exit_btn.pack(side="left", padx=5)
        
        rebind_exit_btn = tk.Button(self.exit_frame, text="Rebind", 
                                    width=8, command=lambda: self.rebind_hotkey('exit'))
        rebind_exit_btn.pack(side="left", padx=5)
        
        # Settings frame 1
        settings_frame1 = tk.Frame(self.root)
        settings_frame1.pack(pady=5, padx=20, fill="x")
        
        # Color tolerance setting
        tolerance_label = tk.Label(settings_frame1, text="Color Tolerance:", 
                                   font=("Arial", 9))
        tolerance_label.pack(side="left", padx=5)
        
        self.tolerance_var = tk.StringVar(value=str(self.storage.get_detection_setting('color_tolerance')))
        tolerance_spinbox = tk.Spinbox(settings_frame1, from_=0, to=50, 
                                      textvariable=self.tolerance_var,
                                      width=5, font=("Arial", 9),
                                      command=self.on_tolerance_change)
        tolerance_spinbox.pack(side="left", padx=5)
        tolerance_spinbox.bind('<Return>', lambda e: self.on_tolerance_change())
        tolerance_spinbox.bind('<FocusOut>', lambda e: self.on_tolerance_change())
        
        # Lure timeout setting
        timeout_label = tk.Label(settings_frame1, text="Lure Timeout (sec):", 
                                font=("Arial", 9))
        timeout_label.pack(side="left", padx=5)
        
        self.timeout_var = tk.StringVar(value=str(self.storage.get_detection_setting('lure_timeout')))
        timeout_spinbox = tk.Spinbox(settings_frame1, from_=1, to=60, 
                                    textvariable=self.timeout_var,
                                    width=5, font=("Arial", 9),
                                    command=self.on_timeout_change)
        timeout_spinbox.pack(side="left", padx=5)
        timeout_spinbox.bind('<Return>', lambda e: self.on_timeout_change())
        timeout_spinbox.bind('<FocusOut>', lambda e: self.on_timeout_change())
        
        # Fish timeout setting
        fish_timeout_label = tk.Label(settings_frame1, text="Fish Timeout (sec):", 
                                      font=("Arial", 9))
        fish_timeout_label.pack(side="left", padx=5)
        
        self.fish_timeout_var = tk.StringVar(value=str(self.storage.get_detection_setting('fish_timeout')))
        fish_timeout_spinbox = tk.Spinbox(settings_frame1, from_=1, to=60, 
                                         textvariable=self.fish_timeout_var,
                                         width=5, font=("Arial", 9),
                                         command=self.on_fish_timeout_change)
        fish_timeout_spinbox.pack(side="left", padx=5)
        fish_timeout_spinbox.bind('<Return>', lambda e: self.on_fish_timeout_change())
        fish_timeout_spinbox.bind('<FocusOut>', lambda e: self.on_fish_timeout_change())
        
        # Settings frame 2 - Tolerance settings
        settings_frame2 = tk.Frame(self.root)
        settings_frame2.pack(pady=5, padx=20, fill="x")
        
        # Bar tolerance
        bar_tol_label = tk.Label(settings_frame2, text="Bar Tol:", 
                                font=("Arial", 9))
        bar_tol_label.pack(side="left", padx=2)
        
        self.bar_tol_var = tk.StringVar(value=str(self.storage.get_detection_setting('bar_tolerance')))
        bar_tol_spinbox = tk.Spinbox(settings_frame2, from_=0, to=50, 
                                     textvariable=self.bar_tol_var,
                                     width=4, font=("Arial", 9),
                                     command=lambda: self.on_specific_tolerance_change('bar_tolerance', self.bar_tol_var))
        bar_tol_spinbox.pack(side="left", padx=2)
        bar_tol_spinbox.bind('<Return>', lambda e: self.on_specific_tolerance_change('bar_tolerance', self.bar_tol_var))
        bar_tol_spinbox.bind('<FocusOut>', lambda e: self.on_specific_tolerance_change('bar_tolerance', self.bar_tol_var))
        
        # Arrow tolerance
        arrow_tol_label = tk.Label(settings_frame2, text="Arrow Tol:", 
                                   font=("Arial", 9))
        arrow_tol_label.pack(side="left", padx=2)
        
        self.arrow_tol_var = tk.StringVar(value=str(self.storage.get_detection_setting('arrow_tolerance')))
        arrow_tol_spinbox = tk.Spinbox(settings_frame2, from_=0, to=50, 
                                       textvariable=self.arrow_tol_var,
                                       width=4, font=("Arial", 9),
                                       command=lambda: self.on_specific_tolerance_change('arrow_tolerance', self.arrow_tol_var))
        arrow_tol_spinbox.pack(side="left", padx=2)
        arrow_tol_spinbox.bind('<Return>', lambda e: self.on_specific_tolerance_change('arrow_tolerance', self.arrow_tol_var))
        arrow_tol_spinbox.bind('<FocusOut>', lambda e: self.on_specific_tolerance_change('arrow_tolerance', self.arrow_tol_var))
        
        # Fish tolerance
        fish_tol_label = tk.Label(settings_frame2, text="Fish Tol:", 
                                  font=("Arial", 9))
        fish_tol_label.pack(side="left", padx=2)
        
        self.fish_tol_var = tk.StringVar(value=str(self.storage.get_detection_setting('fish_tolerance')))
        fish_tol_spinbox = tk.Spinbox(settings_frame2, from_=0, to=50, 
                                      textvariable=self.fish_tol_var,
                                      width=4, font=("Arial", 9),
                                      command=lambda: self.on_specific_tolerance_change('fish_tolerance', self.fish_tol_var))
        fish_tol_spinbox.pack(side="left", padx=2)
        fish_tol_spinbox.bind('<Return>', lambda e: self.on_specific_tolerance_change('fish_tolerance', self.fish_tol_var))
        fish_tol_spinbox.bind('<FocusOut>', lambda e: self.on_specific_tolerance_change('fish_tolerance', self.fish_tol_var))
        
        # Treasure tolerance
        treasure_tol_label = tk.Label(settings_frame2, text="Treasure Tol:", 
                                      font=("Arial", 9))
        treasure_tol_label.pack(side="left", padx=2)
        
        self.treasure_tol_var = tk.StringVar(value=str(self.storage.get_detection_setting('treasure_tolerance')))
        treasure_tol_spinbox = tk.Spinbox(settings_frame2, from_=0, to=50, 
                                         textvariable=self.treasure_tol_var,
                                         width=4, font=("Arial", 9),
                                         command=lambda: self.on_specific_tolerance_change('treasure_tolerance', self.treasure_tol_var))
        treasure_tol_spinbox.pack(side="left", padx=2)
        treasure_tol_spinbox.bind('<Return>', lambda e: self.on_specific_tolerance_change('treasure_tolerance', self.treasure_tol_var))
        treasure_tol_spinbox.bind('<FocusOut>', lambda e: self.on_specific_tolerance_change('treasure_tolerance', self.treasure_tol_var))
        
        # Settings frame 3 - PD Controller settings
        settings_frame3 = tk.Frame(self.root)
        settings_frame3.pack(pady=5, padx=20, fill="x")
        
        # Kp (Proportional gain)
        kp_label = tk.Label(settings_frame3, text="Kp (Proportional):", 
                           font=("Arial", 9))
        kp_label.pack(side="left", padx=5)
        
        self.kp_var = tk.StringVar(value=str(self.storage.get_detection_setting('kp')))
        kp_spinbox = tk.Spinbox(settings_frame3, from_=0, to=10, increment=0.1,
                                textvariable=self.kp_var,
                                width=5, font=("Arial", 9),
                                command=lambda: self.on_pd_change('kp', self.kp_var))
        kp_spinbox.pack(side="left", padx=5)
        kp_spinbox.bind('<Return>', lambda e: self.on_pd_change('kp', self.kp_var))
        kp_spinbox.bind('<FocusOut>', lambda e: self.on_pd_change('kp', self.kp_var))
        
        # Kd (Derivative gain)
        kd_label = tk.Label(settings_frame3, text="Kd (Derivative):", 
                           font=("Arial", 9))
        kd_label.pack(side="left", padx=5)
        
        self.kd_var = tk.StringVar(value=str(self.storage.get_detection_setting('kd')))
        kd_spinbox = tk.Spinbox(settings_frame3, from_=0, to=10, increment=0.1,
                                textvariable=self.kd_var,
                                width=5, font=("Arial", 9),
                                command=lambda: self.on_pd_change('kd', self.kd_var))
        kd_spinbox.pack(side="left", padx=5)
        kd_spinbox.bind('<Return>', lambda e: self.on_pd_change('kd', self.kd_var))
        kd_spinbox.bind('<FocusOut>', lambda e: self.on_pd_change('kd', self.kd_var))
        
        # Click duration setting
        click_dur_label = tk.Label(settings_frame3, text="Click Duration (sec):", 
                                   font=("Arial", 9))
        click_dur_label.pack(side="left", padx=5)
        
        self.click_dur_var = tk.StringVar(value=str(self.storage.get_detection_setting('click_duration')))
        click_dur_spinbox = tk.Spinbox(settings_frame3, from_=0.1, to=10, increment=0.1,
                                       textvariable=self.click_dur_var,
                                       width=5, font=("Arial", 9),
                                       command=lambda: self.on_click_duration_change())
        click_dur_spinbox.pack(side="left", padx=5)
        click_dur_spinbox.bind('<Return>', lambda e: self.on_click_duration_change())
        click_dur_spinbox.bind('<FocusOut>', lambda e: self.on_click_duration_change())
        
        # Keybind settings frame
        keybind_frame = tk.Frame(self.root)
        keybind_frame.pack(pady=5, padx=20, fill="x")
        
        # Not Rod Keybind
        not_rod_label = tk.Label(keybind_frame, text="Not Rod Keybind:", 
                                 font=("Arial", 9))
        not_rod_label.grid(row=0, column=0, padx=5, sticky="w")
        
        not_rod_value = self.storage.get_keybind_setting('not_rod_keybind')
        self.not_rod_var = tk.StringVar(value=str(not_rod_value) if not_rod_value else "N/A")
        not_rod_combo = ttk.Combobox(keybind_frame, textvariable=self.not_rod_var,
                                     values=["N/A", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                                     width=5, font=("Arial", 9), state="readonly")
        not_rod_combo.grid(row=0, column=1, padx=5)
        not_rod_combo.bind('<<ComboboxSelected>>', lambda e: self.on_not_rod_change())
        
        # Rod Keybind
        rod_label = tk.Label(keybind_frame, text="Rod Keybind:", 
                            font=("Arial", 9))
        rod_label.grid(row=1, column=0, padx=5, sticky="w")
        
        rod_value = self.storage.get_keybind_setting('rod_keybind')
        self.rod_var = tk.StringVar(value=str(rod_value) if rod_value else "N/A")
        rod_combo = ttk.Combobox(keybind_frame, textvariable=self.rod_var,
                                values=["N/A", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                                width=5, font=("Arial", 9), state="readonly")
        rod_combo.grid(row=1, column=1, padx=5)
        rod_combo.bind('<<ComboboxSelected>>', lambda e: self.on_rod_change())
        
        # Feature toggles frame
        toggles_frame = tk.Frame(self.root)
        toggles_frame.pack(pady=5, padx=20, fill="x")
        
        # Get Chest checkbox
        self.get_chest_var = tk.BooleanVar(value=self.storage.get_feature_toggle('get_chest'))
        get_chest_check = tk.Checkbutton(toggles_frame, text="Get Chest", 
                                         variable=self.get_chest_var,
                                         font=("Arial", 9),
                                         command=self.on_get_chest_toggle)
        get_chest_check.pack(side="left", padx=5)
        
        # New Fish Wait checkbox
        self.new_fish_wait_var = tk.BooleanVar(value=self.storage.get_feature_toggle('new_fish_wait'))
        new_fish_wait_check = tk.Checkbutton(toggles_frame, text="New Fish Wait", 
                                             variable=self.new_fish_wait_var,
                                             font=("Arial", 9),
                                             command=self.on_new_fish_wait_toggle)
        new_fish_wait_check.pack(side="left", padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Idle", 
                                     font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=10)
    
    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        try:
            keyboard.add_hotkey(self.storage.get_hotkey('start_stop'), self.toggle_start_stop)
            keyboard.add_hotkey(self.storage.get_hotkey('change_area'), self.toggle_change_area)
            keyboard.add_hotkey(self.storage.get_hotkey('exit'), self.exit_app)
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Failed to setup hotkeys: {e}")
    
    def clear_hotkeys(self):
        """Clear all hotkeys"""
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
    
    def toggle_start_stop(self):
        """Toggle the main loop on/off"""
        if self.rebinding:
            return
        
        # Toggle state using storage
        is_running = self.storage.toggle_state('is_running')
        
        if is_running:
            # Validate keybinds before starting
            not_rod = self.storage.get_keybind_setting('not_rod_keybind')
            rod = self.storage.get_keybind_setting('rod_keybind')
            
            if not_rod is None or rod is None:
                # Stop and show error
                self.storage.set_state('is_running', False)
                messagebox.showerror("Keybind Error", 
                                   "Please set both 'Not Rod Keybind' and 'Rod Keybind' before starting!\n\n"
                                   "Select numbers 1-9 for each keybind in the settings below.")
                self.status_label.config(text="Status: Missing keybinds!", fg="red")
                self.root.after(3000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
                return
            
            hotkey = self.storage.get_hotkey('start_stop')
            self.start_stop_btn.config(text=f"⏸ Stop ({hotkey})", 
                                      bg="#FF9800")
            self.status_label.config(text="Status: Running", fg="green")
            # Start your main loop here
            threading.Thread(target=self.main_loop, daemon=True).start()
        else:
            hotkey = self.storage.get_hotkey('start_stop')
            self.start_stop_btn.config(text=f"▶ Start ({hotkey})", 
                                      bg="#4CAF50")
            self.status_label.config(text="Status: Stopped", fg="red")
    
    def toggle_change_area(self):
        """Open area selector to define Indicator and Fish areas"""
        if self.rebinding:
            return
        
        # Check if area selector is already open
        if hasattr(self, 'area_selector') and self.area_selector:
            # Confirm and save current selection
            self.area_selector.finish_selection()
            self.area_selector = None
            return
        
        # Take screenshot
        self.status_label.config(text="Status: Taking screenshot...", fg="orange")
        self.root.update()
        
        try:
            screenshot = ImageGrab.grab()
            
            # Get current box settings
            indicator_box = self.storage.get_area_box('indicator_box')
            fish_box = self.storage.get_area_box('fish_box')
            
            # Open area selector
            self.status_label.config(text="Status: Select areas on screen", fg="blue")
            self.area_selector = DualAreaSelector(self.root, screenshot, indicator_box, fish_box, self.on_areas_selected)
        except Exception as e:
            messagebox.showerror("Screenshot Error", f"Failed to capture screen: {e}")
            self.status_label.config(text="Status: Idle", fg="gray")
    
    def on_areas_selected(self, indicator_box, fish_box):
        """Callback when areas are selected"""
        self.storage.set_area_boxes(indicator_box, fish_box)
        self.status_label.config(text="Status: Areas saved!", fg="green")
        self.area_selector = None
        
        # Reset to idle after a moment
        self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
    
    def on_tolerance_change(self):
        """Handle color tolerance change"""
        try:
            tolerance = int(self.tolerance_var.get())
            if 0 <= tolerance <= 50:
                self.storage.set_detection_setting('color_tolerance', tolerance)
                self.status_label.config(text=f"Tolerance set to {tolerance}", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                self.tolerance_var.set(str(self.storage.get_detection_setting('color_tolerance')))
        except ValueError:
            self.tolerance_var.set(str(self.storage.get_detection_setting('color_tolerance')))
    
    def on_timeout_change(self):
        """Handle lure timeout change"""
        try:
            timeout = int(self.timeout_var.get())
            if 1 <= timeout <= 60:
                self.storage.set_detection_setting('lure_timeout', timeout)
                self.status_label.config(text=f"Lure Timeout set to {timeout}s", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                self.timeout_var.set(str(self.storage.get_detection_setting('lure_timeout')))
        except ValueError:
            self.timeout_var.set(str(self.storage.get_detection_setting('lure_timeout')))
    
    def on_fish_timeout_change(self):
        """Handle fish timeout change"""
        try:
            timeout = int(self.fish_timeout_var.get())
            if 1 <= timeout <= 60:
                self.storage.set_detection_setting('fish_timeout', timeout)
                self.status_label.config(text=f"Fish Timeout set to {timeout}s", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                self.fish_timeout_var.set(str(self.storage.get_detection_setting('fish_timeout')))
        except ValueError:
            self.fish_timeout_var.set(str(self.storage.get_detection_setting('fish_timeout')))
    
    def on_not_rod_change(self):
        """Handle not rod keybind change"""
        value = self.not_rod_var.get()
        if value == "N/A":
            self.storage.set_keybind_setting('not_rod_keybind', None)
            self.status_label.config(text="Not Rod Keybind cleared", fg="orange")
        else:
            self.storage.set_keybind_setting('not_rod_keybind', int(value))
            self.status_label.config(text=f"Not Rod Keybind set to {value}", fg="green")
        self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
    
    def on_rod_change(self):
        """Handle rod keybind change"""
        value = self.rod_var.get()
        if value == "N/A":
            self.storage.set_keybind_setting('rod_keybind', None)
            self.status_label.config(text="Rod Keybind cleared", fg="orange")
        else:
            self.storage.set_keybind_setting('rod_keybind', int(value))
            self.status_label.config(text=f"Rod Keybind set to {value}", fg="green")
        self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
    
    def on_get_chest_toggle(self):
        """Handle get chest toggle"""
        value = self.get_chest_var.get()
        self.storage.set_feature_toggle('get_chest', value)
        status = "enabled" if value else "disabled"
        self.status_label.config(text=f"Get Chest {status}", fg="green")
        self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
    
    def on_new_fish_wait_toggle(self):
        """Handle new fish wait toggle"""
        value = self.new_fish_wait_var.get()
        self.storage.set_feature_toggle('new_fish_wait', value)
        status = "enabled" if value else "disabled"
        self.status_label.config(text=f"New Fish Wait {status}", fg="green")
        self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
    
    def on_specific_tolerance_change(self, setting_name, var):
        """Handle specific tolerance setting change"""
        try:
            tolerance = int(var.get())
            if 0 <= tolerance <= 50:
                self.storage.set_detection_setting(setting_name, tolerance)
                display_name = setting_name.replace('_', ' ').title()
                self.status_label.config(text=f"{display_name} set to {tolerance}", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                var.set(str(self.storage.get_detection_setting(setting_name)))
        except ValueError:
            var.set(str(self.storage.get_detection_setting(setting_name)))
    
    def on_pd_change(self, setting_name, var):
        """Handle PD controller parameter change"""
        try:
            value = float(var.get())
            if 0 <= value <= 10:
                self.storage.set_detection_setting(setting_name, value)
                display_name = setting_name.upper()
                self.status_label.config(text=f"{display_name} set to {value:.2f}", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                var.set(str(self.storage.get_detection_setting(setting_name)))
        except ValueError:
            var.set(str(self.storage.get_detection_setting(setting_name)))
    
    def on_click_duration_change(self):
        """Handle click duration change"""
        try:
            duration = float(self.click_dur_var.get())
            if 0.1 <= duration <= 10:
                self.storage.set_detection_setting('click_duration', duration)
                self.status_label.config(text=f"Click Duration set to {duration:.1f}s", fg="green")
                self.root.after(2000, lambda: self.status_label.config(text="Status: Idle", fg="gray"))
            else:
                self.click_dur_var.set(str(self.storage.get_detection_setting('click_duration')))
        except ValueError:
            self.click_dur_var.set(str(self.storage.get_detection_setting('click_duration')))
    
    def exit_app(self):
        """Exit the application"""
        if self.rebinding:
            return
            
        self.on_closing()
    
    def rebind_hotkey(self, hotkey_name):
        """Rebind a hotkey"""
        self.rebinding = hotkey_name
        self.status_label.config(text=f"Press a key to rebind {hotkey_name.replace('_', ' ')}...", 
                                fg="orange")
        
        # Disable all hotkeys temporarily
        self.clear_hotkeys()
        
        def on_key_press(event):
            new_key = event.name.upper()
            
            # Check if key is already in use
            all_hotkeys = {
                'start_stop': self.storage.get_hotkey('start_stop'),
                'change_area': self.storage.get_hotkey('change_area'),
                'exit': self.storage.get_hotkey('exit')
            }
            
            for key, value in all_hotkeys.items():
                if key != hotkey_name and value.upper() == new_key:
                    messagebox.showwarning("Key In Use", 
                                          f"Key {new_key} is already assigned to {key.replace('_', ' ')}!")
                    self.rebinding = None
                    self.setup_hotkeys()
                    self.status_label.config(text="Status: Idle", fg="gray")
                    keyboard.unhook(hook)
                    return
            
            # Update hotkey in storage
            old_key = self.storage.get_hotkey(hotkey_name)
            self.storage.set_hotkey(hotkey_name, new_key)
            
            # Update button text
            is_running = self.storage.get_state('is_running')
            change_area_enabled = self.storage.get_state('change_area_enabled')
            
            if hotkey_name == 'start_stop':
                if is_running:
                    self.start_stop_btn.config(text=f"⏸ Stop ({new_key})")
                else:
                    self.start_stop_btn.config(text=f"▶ Start ({new_key})")
            elif hotkey_name == 'change_area':
                if change_area_enabled:
                    self.change_area_btn.config(text=f"Change Area: ON ({new_key})")
                else:
                    self.change_area_btn.config(text=f"Change Area: OFF ({new_key})")
            elif hotkey_name == 'exit':
                self.exit_btn.config(text=f"✕ Exit ({new_key})")
            
            self.rebinding = None
            self.status_label.config(text=f"Hotkey rebound: {old_key} → {new_key}", fg="green")
            
            # Re-setup all hotkeys
            self.setup_hotkeys()
            
            # Unhook this temporary listener
            keyboard.unhook(hook)
        
        # Listen for next key press
        hook = keyboard.on_press(on_key_press, suppress=True)
    
    def check_color_in_area(self, x1, y1, x2, y2, target_color, tolerance=0):
        """
        Check if target_color exists in the specified area.
        
        Args:
            x1, y1, x2, y2: Area coordinates
            target_color: Tuple (R, G, B)
            tolerance: Color matching tolerance (0-255)
        
        Returns:
            True if color found, False otherwise
        """
        # Grab screenshot of area
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        # Convert to numpy array for fast processing
        img_array = np.array(screenshot)
        
        # Check if exact color exists (if tolerance = 0)
        if tolerance == 0:
            # Fast exact match
            matches = np.all(img_array == target_color, axis=-1)
            return np.any(matches)
        else:
            # Check with tolerance
            r, g, b = target_color
            matches = (
                (np.abs(img_array[:, :, 0] - r) <= tolerance) &
                (np.abs(img_array[:, :, 1] - g) <= tolerance) &
                (np.abs(img_array[:, :, 2] - b) <= tolerance)
            )
            return np.any(matches)
    
    def _cast(self):
        """Cast the fishing rod"""
        print("[CAST] Starting cast sequence...")
        
        # Get keybinds
        not_rod_key = self.storage.get_keybind_setting('not_rod_keybind')
        rod_key = self.storage.get_keybind_setting('rod_keybind')
        
        # Press not rod keybind
        print(f"[CAST] Pressing Not Rod key: {not_rod_key}")
        keyboard.press_and_release(str(not_rod_key))
        time.sleep(0.5)
        
        # Press rod keybind
        print(f"[CAST] Pressing Rod key: {rod_key}")
        keyboard.press_and_release(str(rod_key))
        time.sleep(0.5)
        
        # Hold left click
        print("[CAST] Holding left click...")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        
        # Wait 1 second
        time.sleep(1)
        
        # Release left click
        print("[CAST] Releasing left click...")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        # Wait 1 second
        time.sleep(1)
        
        print("[CAST] Cast sequence complete!")
    
    def _reel(self):
        """Reel in the fishing line"""
        print("[REEL] Starting reel sequence...")
        
        # Get indicator box, tolerance, and timeout
        indicator_box = self.storage.get_area_box('indicator_box')
        tolerance = self.storage.get_detection_setting('color_tolerance')
        lure_timeout = self.storage.get_detection_setting('lure_timeout')
        target_color = (255, 171, 171)  # RGB: #FFABAB
        
        print(f"[REEL] Searching for color {target_color} with tolerance {tolerance}")
        print(f"[REEL] Search area: ({indicator_box['x1']}, {indicator_box['y1']}) to ({indicator_box['x2']}, {indicator_box['y2']})")
        print(f"[REEL] Timeout: {lure_timeout} seconds")
        
        # Loop to search for the color with timeout
        search_count = 0
        start_time = time.time()
        
        while self.storage.get_state('is_running'):
            search_count += 1
            elapsed_time = time.time() - start_time
            
            # Check for timeout
            if elapsed_time >= lure_timeout:
                print(f"[REEL] ⏱ Timeout reached after {lure_timeout}s ({search_count} checks). No indicator found.")
                print("[REEL] Exiting reel to retry cast...")
                return False  # Return False to indicate timeout
            
            if search_count % 100 == 0:  # Print every 100 checks to avoid spam
                print(f"[REEL] Still searching... (check #{search_count}, {elapsed_time:.1f}s elapsed)")
            
            if self.check_color_in_area(
                indicator_box['x1'],
                indicator_box['y1'],
                indicator_box['x2'],
                indicator_box['y2'],
                target_color,
                tolerance
            ):
                # Color found! Click once
                print(f"[REEL] ✓ Color detected after {search_count} checks ({elapsed_time:.1f}s)! Clicking...")
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print("[REEL] Reel sequence complete!")
                return True  # Return True to indicate success
            
            # Small delay to prevent CPU overuse
            time.sleep(0.01)
    
    def find_color_in_image(self, img_array, target_colors, tolerance):
        """
        Find if any of the target colors exist in the image.
        Returns True if found, False otherwise.
        """
        for color in target_colors:
            r, g, b = color
            matches = (
                (np.abs(img_array[:, :, 0] - r) <= tolerance) &
                (np.abs(img_array[:, :, 1] - g) <= tolerance) &
                (np.abs(img_array[:, :, 2] - b) <= tolerance)
            )
            if np.any(matches):
                return True
        return False
    
    def find_target_x_coordinate(self, img_array, target_colors, tolerance):
        """
        Find the x coordinate of the first occurrence of target colors.
        Returns x coordinate or None if not found.
        """
        for color in target_colors:
            r, g, b = color
            matches = (
                (np.abs(img_array[:, :, 0] - r) <= tolerance) &
                (np.abs(img_array[:, :, 1] - g) <= tolerance) &
                (np.abs(img_array[:, :, 2] - b) <= tolerance)
            )
            if np.any(matches):
                # Get coordinates where color is found
                coords = np.where(matches)
                # Return first x coordinate (column index)
                return coords[1][0]
        return None
    
    def find_leftmost_bar(self, img_array, bar_colors, tolerance):
        """
        Find the leftmost x coordinate of any bar color.
        Returns x coordinate or None if not found.
        """
        for color in bar_colors:
            r, g, b = color
            matches = (
                (np.abs(img_array[:, :, 0] - r) <= tolerance) &
                (np.abs(img_array[:, :, 1] - g) <= tolerance) &
                (np.abs(img_array[:, :, 2] - b) <= tolerance)
            )
            if np.any(matches):
                coords = np.where(matches)
                # Return minimum x coordinate (leftmost)
                return np.min(coords[1])
        return None
    
    def find_rightmost_bar(self, img_array, bar_colors, tolerance):
        """
        Find the rightmost x coordinate of any bar color.
        Returns x coordinate or None if not found.
        """
        for color in bar_colors:
            r, g, b = color
            matches = (
                (np.abs(img_array[:, :, 0] - r) <= tolerance) &
                (np.abs(img_array[:, :, 1] - g) <= tolerance) &
                (np.abs(img_array[:, :, 2] - b) <= tolerance)
            )
            if np.any(matches):
                coords = np.where(matches)
                # Return maximum x coordinate (rightmost)
                return np.max(coords[1])
        return None
    
    def _fish(self):
        """Complete fishing action (detect and catch) using PD bang bang controller"""
        print("[FISH] Starting fish detection sequence...")
        
        # Get fish area box
        fish_box = self.storage.get_area_box('fish_box')
        region = (fish_box['x1'], fish_box['y1'], fish_box['x2'], fish_box['y2'])
        
        # Get settings
        get_chest_enabled = self.storage.get_feature_toggle('get_chest')
        fish_timeout = self.storage.get_detection_setting('fish_timeout')
        
        # Get tolerances
        fish_tolerance = self.storage.get_detection_setting('fish_tolerance')
        treasure_tolerance = self.storage.get_detection_setting('treasure_tolerance')
        bar_tolerance = self.storage.get_detection_setting('bar_tolerance')
        arrow_tolerance = self.storage.get_detection_setting('arrow_tolerance')
        
        # Get PD controller parameters
        kp = self.storage.get_detection_setting('kp')
        kd = self.storage.get_detection_setting('kd')
        
        # Define color sets
        treasure_colors = [COLORS["TREASURE"], COLORS["TREASURE_2"]]
        fish_colors = [COLORS["FISH"], COLORS["FISH_2"]]
        bar_colors = [COLORS["BAR"], COLORS["FISH_BAR"], COLORS["TREASURE_BAR"], COLORS["OFF_BAR"], COLORS["ARROW"]]
        
        print(f"[FISH] Get Chest: {get_chest_enabled}")
        print(f"[FISH] Fish Timeout: {fish_timeout}s")
        print(f"[FISH] PD Controller - Kp: {kp}, Kd: {kd}")
        print(f"[FISH] Monitoring area: {region}")
        
        # Initialize dxcam camera
        camera = dxcam.create()
        camera.start(region=region, target_fps=60)
        
        # PD controller variables
        last_error = 0
        last_time = time.time()
        
        # Timeout tracking
        timeout_start = None
        target_found = False
        
        try:
            while self.storage.get_state('is_running'):
                # Capture frame from dxcam
                frame = camera.get_latest_frame()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Convert to numpy array if needed
                img_array = np.array(frame)
                
                # Search for target
                target_x = None
                
                if get_chest_enabled:
                    # Search for treasure first when Get Chest is enabled
                    target_x = self.find_target_x_coordinate(img_array, treasure_colors, treasure_tolerance)
                    if target_x is not None:
                        if not target_found or timeout_start is not None:
                            print(f"[FISH] 💎 Treasure found at x={target_x}")
                        target_found = True
                        timeout_start = None
                
                # Search for fish (always, or if treasure not found)
                if target_x is None:
                    target_x = self.find_target_x_coordinate(img_array, fish_colors, fish_tolerance)
                    if target_x is not None:
                        if not target_found or timeout_start is not None:
                            print(f"[FISH] 🐟 Fish found at x={target_x}")
                        target_found = True
                        timeout_start = None
                
                # Handle timeout if no target found
                if target_x is None:
                    if timeout_start is None:
                        timeout_start = time.time()
                        print(f"[FISH] ⚠ No target found, starting timeout...")
                    else:
                        elapsed = time.time() - timeout_start
                        if elapsed >= fish_timeout:
                            print(f"[FISH] ⏱ Timeout reached ({fish_timeout}s). Exiting fish sequence.")
                            break
                        if int(elapsed) != int(elapsed - 0.05):  # Print every second
                            print(f"[FISH] Waiting for target... ({elapsed:.1f}s / {fish_timeout}s)")
                    
                    time.sleep(0.01)
                    continue
                
                # Target established - find user position
                left_bar = self.find_leftmost_bar(img_array, bar_colors, max(bar_tolerance, arrow_tolerance))
                right_bar = self.find_rightmost_bar(img_array, bar_colors, max(bar_tolerance, arrow_tolerance))
                
                if left_bar is None or right_bar is None:
                    time.sleep(0.01)
                    continue
                
                # Calculate user position (middle of bars)
                user_x = (left_bar + right_bar) // 2
                
                # PD Bang Bang Controller
                error = target_x - user_x
                current_time = time.time()
                dt = current_time - last_time
                
                if dt > 0:
                    # Derivative term
                    error_derivative = (error - last_error) / dt
                    
                    # Bang bang control: hold click to go right, release to go left
                    # PD control with configurable gains
                    control_signal = (kp * error) + (kd * error_derivative)
                    
                    if control_signal > 2:  # Threshold for holding
                        # Hold left click to move right
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    else:
                        # Release left click to move left
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                    last_error = error
                    last_time = current_time
                
                time.sleep(0.01)
        
        finally:
            # Cleanup
            camera.stop()
            camera.release()
            # Make sure mouse is released
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            print("[FISH] Fish sequence complete!")
            
            # Check if New Fish Wait is enabled
            if self.storage.get_feature_toggle('new_fish_wait'):
                print("[FISH] New Fish Wait enabled - executing sequence...")
                
                # Get not rod keybind
                not_rod_key = self.storage.get_keybind_setting('not_rod_keybind')
                
                # Press not rod keybind
                print(f"[FISH] Pressing Not Rod key: {not_rod_key}")
                keyboard.press_and_release(str(not_rod_key))
                time.sleep(0.5)
                
                # Press not rod keybind again
                print(f"[FISH] Pressing Not Rod key again: {not_rod_key}")
                keyboard.press_and_release(str(not_rod_key))
                time.sleep(0.5)
                
                # Get click duration from settings
                click_duration = self.storage.get_detection_setting('click_duration')
                num_clicks = 10
                delay_per_click = click_duration / num_clicks
                
                # Click 10 times over the specified duration
                print(f"[FISH] Clicking {num_clicks} times over {click_duration}s ({delay_per_click:.3f}s per click)...")
                for i in range(num_clicks):
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    time.sleep(delay_per_click)
                
                # Wait 500ms
                time.sleep(0.5)
                print("[FISH] New Fish Wait sequence complete!")
    
    def main_loop(self):
        """Main automation loop - fishing cycle"""
        print("\n" + "="*50)
        print("MAIN LOOP STARTED")
        print("="*50 + "\n")
        
        cycle_count = 0
        while self.storage.get_state('is_running'):
            try:
                cycle_count += 1
                print(f"\n{'='*50}")
                print(f"FISHING CYCLE #{cycle_count}")
                print(f"{'='*50}")
                
                # Fishing cycle
                self._cast()
                
                # Reel returns True on success, False on timeout
                reel_success = self._reel()
                
                if not reel_success:
                    # Timeout during reel, skip fish and restart cycle
                    print("[MAIN] Reel timeout - restarting cycle...")
                    continue
                
                self._fish()
                
                print(f"\n[MAIN] Cycle #{cycle_count} complete! Waiting before next cycle...")
                
                # Small delay between cycles
                time.sleep(0.1)
            except Exception as e:
                print(f"\n[ERROR] Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)  # Wait before retry
        
        print("\n" + "="*50)
        print("MAIN LOOP STOPPED")
        print("="*50 + "\n")
    
    def on_closing(self):
        """Handle window closing"""
        # Stop running
        self.storage.set_state('is_running', False)
        self.clear_hotkeys()
        self.root.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = BloxfruitsAutofishGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
