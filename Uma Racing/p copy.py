import tkinter as tk
from tkinter import ttk
from pynput import keyboard, mouse
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import json
import os
import threading
import time
import mss
import cv2
import numpy as np
import win32api
import win32con

# ========== USER SETTINGS - EDIT HERE ==========

# Color detection settings
COLOR_BLUE_RGB = (107, 243, 246)  # Blue box color (R:107 G:243 B:246)
COLOR_RED_RGB = (255, 69, 150)     # Red box color (R:255 G:69 B:150)

# Mode delays (in seconds) for Q/E alternation
MODE_DELAYS = {
    'z': None,   # Disabled - no Q/E alternation
    'x': 0.229,  # 225ms between Q/E presses
    'c': 0,      # Fast mode - instant alternation
    'v': 0.12    # 120ms (xbutton4 toggle)
}

# Default mode on startup (z/x/c/v/n)
DEFAULT_MODE = 'z'

# Template matching confidence threshold (0.0 to 1.0)
# Lower = more lenient, Higher = more strict
TEMPLATE_CONFIDENCE = 0.8

# Template confirmation - how many times it must be found before pressing
TEMPLATE_CONFIRM_COUNT = 5

# ================================================

class DualAreaSelector:
    """Full-screen overlay for selecting Start Box and Corner Box"""

    def __init__(self, parent, screenshot, start_box, corner_box, callback):
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

        # Initialize Start Box
        self.start_box = start_box.copy()
        self.start_x1, self.start_y1 = self.start_box["x1"], self.start_box["y1"]
        self.start_x2, self.start_y2 = self.start_box["x2"], self.start_box["y2"]

        # Initialize Corner Box
        self.corner_box = corner_box.copy()
        self.corner_x1, self.corner_y1 = self.corner_box["x1"], self.corner_box["y1"]
        self.corner_x2, self.corner_y2 = self.corner_box["x2"], self.corner_box["y2"]

        # Drawing state
        self.dragging = False
        self.active_box = None  # 'start' or 'corner'
        self.drag_corner = None
        self.resize_threshold = 10

        # Create Start Box (Green)
        self.start_rect = self.canvas.create_rectangle(
            self.start_x1, self.start_y1, self.start_x2, self.start_y2,
            outline='#4CAF50',
            width=2,
            fill='#4CAF50',
            stipple='gray50',
            tags='start_box'
        )

        # Start Box label
        start_label_x = self.start_x1 + (self.start_x2 - self.start_x1) // 2
        start_label_y = self.start_y1 - 20
        self.start_label = self.canvas.create_text(
            start_label_x, start_label_y,
            text="Start Box",
            font=("Arial", 12, "bold"),
            fill='#4CAF50',
            tags='start_label'
        )

        # Create Corner Box (Purple)
        self.corner_rect = self.canvas.create_rectangle(
            self.corner_x1, self.corner_y1, self.corner_x2, self.corner_y2,
            outline='#9C27B0',
            width=2,
            fill='#9C27B0',
            stipple='gray50',
            tags='corner_box'
        )

        # Corner Box label
        corner_label_x = self.corner_x1 + (self.corner_x2 - self.corner_x1) // 2
        corner_label_y = self.corner_y1 - 20
        self.corner_label = self.canvas.create_text(
            corner_label_x, corner_label_y,
            text="Corner Box",
            font=("Arial", 12, "bold"),
            fill='#9C27B0',
            tags='corner_label'
        )

        # Create corner handles for both boxes
        self.start_handles = []
        self.corner_handles = []
        self.create_all_handles()

        # Zoom window
        self.zoom_window_size = 150
        self.zoom_factor = 4
        self.zoom_rect = None
        self.zoom_image_id = None

        # Bind events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.window.bind('<Escape>', lambda e: self.finish_selection())
        self.window.bind('<Return>', lambda e: self.finish_selection())

    def create_all_handles(self):
        """Create corner handles for both boxes"""
        self.create_handles_for_box('start')
        self.create_handles_for_box('corner')

    def create_handles_for_box(self, box_type):
        """Create corner handles for a specific box"""
        handle_size = 12
        corner_marker_size = 3

        if box_type == 'start':
            x1, y1, x2, y2 = self.start_x1, self.start_y1, self.start_x2, self.start_y2
            color = '#4CAF50'
            handles_list = self.start_handles
        else:  # corner
            x1, y1, x2, y2 = self.corner_x1, self.corner_y1, self.corner_x2, self.corner_y2
            color = '#9C27B0'
            handles_list = self.corner_handles

        corners = [
            (x1, y1, 'nw'),
            (x2, y1, 'ne'),
            (x1, y2, 'sw'),
            (x2, y2, 'se')
        ]

        # Delete old handles
        for handle in handles_list:
            self.canvas.delete(handle)
        handles_list.clear()

        # Create new handles
        for x, y, corner in corners:
            # Outer handle
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline=color,
                width=2,
                tags=f'{box_type}_handle_{corner}'
            )
            handles_list.append(handle)

            # Corner marker
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='red',
                outline='white',
                width=1,
                tags=f'{box_type}_corner_{corner}'
            )
            handles_list.append(corner_marker)

            # Crosshair
            line1 = self.canvas.create_line(
                x - handle_size, y, x + handle_size, y,
                fill='yellow',
                width=1,
                tags=f'{box_type}_cross_{corner}'
            )
            line2 = self.canvas.create_line(
                x, y - handle_size, x, y + handle_size,
                fill='yellow',
                width=1,
                tags=f'{box_type}_cross_{corner}'
            )
            handles_list.append(line1)
            handles_list.append(line2)

    def get_corner_at_position(self, x, y, box_type):
        """Determine which corner is near the cursor for a specific box"""
        if box_type == 'start':
            x1, y1, x2, y2 = self.start_x1, self.start_y1, self.start_x2, self.start_y2
        else:  # corner
            x1, y1, x2, y2 = self.corner_x1, self.corner_y1, self.corner_x2, self.corner_y2

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

    def is_inside_box(self, x, y, box_type):
        """Check if point is inside a specific box"""
        if box_type == 'start':
            return self.start_x1 < x < self.start_x2 and self.start_y1 < y < self.start_y2
        else:  # corner
            return self.corner_x1 < x < self.corner_x2 and self.corner_y1 < y < self.corner_y2

    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Check Start Box first
        corner = self.get_corner_at_position(event.x, event.y, 'start')
        if corner:
            self.dragging = True
            self.active_box = 'start'
            self.drag_corner = corner
            return

        if self.is_inside_box(event.x, event.y, 'start'):
            self.dragging = True
            self.active_box = 'start'
            self.drag_corner = 'move'
            return

        # Check Corner Box
        corner = self.get_corner_at_position(event.x, event.y, 'corner')
        if corner:
            self.dragging = True
            self.active_box = 'corner'
            self.drag_corner = corner
            return

        if self.is_inside_box(event.x, event.y, 'corner'):
            self.dragging = True
            self.active_box = 'corner'
            self.drag_corner = 'move'
            return

    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging or not self.active_box:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        if self.active_box == 'start':
            if self.drag_corner == 'move':
                self.start_x1 += dx
                self.start_y1 += dy
                self.start_x2 += dx
                self.start_y2 += dy
            elif self.drag_corner == 'nw':
                self.start_x1 = event.x
                self.start_y1 = event.y
            elif self.drag_corner == 'ne':
                self.start_x2 = event.x
                self.start_y1 = event.y
            elif self.drag_corner == 'sw':
                self.start_x1 = event.x
                self.start_y2 = event.y
            elif self.drag_corner == 'se':
                self.start_x2 = event.x
                self.start_y2 = event.y

            if self.start_x1 > self.start_x2:
                self.start_x1, self.start_x2 = self.start_x2, self.start_x1
            if self.start_y1 > self.start_y2:
                self.start_y1, self.start_y2 = self.start_y2, self.start_y1

        elif self.active_box == 'corner':
            if self.drag_corner == 'move':
                self.corner_x1 += dx
                self.corner_y1 += dy
                self.corner_x2 += dx
                self.corner_y2 += dy
            elif self.drag_corner == 'nw':
                self.corner_x1 = event.x
                self.corner_y1 = event.y
            elif self.drag_corner == 'ne':
                self.corner_x2 = event.x
                self.corner_y1 = event.y
            elif self.drag_corner == 'sw':
                self.corner_x1 = event.x
                self.corner_y2 = event.y
            elif self.drag_corner == 'se':
                self.corner_x2 = event.x
                self.corner_y2 = event.y

            if self.corner_x1 > self.corner_x2:
                self.corner_x1, self.corner_x2 = self.corner_x2, self.corner_x1
            if self.corner_y1 > self.corner_y2:
                self.corner_y1, self.corner_y2 = self.corner_y2, self.corner_y1

        self.update_boxes()
        self.show_zoom(event.x, event.y)

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.dragging = False
        self.active_box = None
        self.drag_corner = None

    def on_mouse_move(self, event):
        """Handle mouse movement"""
        # Check which box cursor is over
        start_corner = self.get_corner_at_position(event.x, event.y, 'start')
        corner_corner = self.get_corner_at_position(event.x, event.y, 'corner')

        if start_corner or corner_corner:
            corner = start_corner or corner_corner
            cursors = {'nw': 'top_left_corner', 'ne': 'top_right_corner',
                      'sw': 'bottom_left_corner', 'se': 'bottom_right_corner'}
            self.window.configure(cursor=cursors.get(corner, 'cross'))
        elif (self.is_inside_box(event.x, event.y, 'start') or 
              self.is_inside_box(event.x, event.y, 'corner')):
            self.window.configure(cursor='fleur')
        else:
            self.window.configure(cursor='cross')

        self.show_zoom(event.x, event.y)

    def show_zoom(self, x, y):
        """Display mini zoom window"""
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
        if self.zoom_image_id:
            self.canvas.delete(self.zoom_image_id)

        zoom_src_size = self.zoom_window_size // self.zoom_factor
        x1_src = max(0, x - zoom_src_size // 2)
        y1_src = max(0, y - zoom_src_size // 2)
        x2_src = min(self.screen_width, x1_src + zoom_src_size)
        y2_src = min(self.screen_height, y1_src + zoom_src_size)

        cropped = self.screenshot.crop((x1_src, y1_src, x2_src, y2_src))
        zoomed = cropped.resize((self.zoom_window_size, self.zoom_window_size), Image.NEAREST)

        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_window_size // 2
        crosshair_size = 10
        draw.line([(center - crosshair_size, center), (center + crosshair_size, center)], fill='red', width=2)
        draw.line([(center, center - crosshair_size), (center, center + crosshair_size)], fill='red', width=2)

        self.zoom_photo = ImageTk.PhotoImage(zoomed)

        zoom_x = x + 30
        zoom_y = y + 30

        if zoom_x + self.zoom_window_size > self.screen_width:
            zoom_x = x - self.zoom_window_size - 30
        if zoom_y + self.zoom_window_size > self.screen_height:
            zoom_y = y - self.zoom_window_size - 30

        self.zoom_rect = self.canvas.create_rectangle(
            zoom_x, zoom_y,
            zoom_x + self.zoom_window_size, zoom_y + self.zoom_window_size,
            outline='white',
            width=2
        )

        self.zoom_image_id = self.canvas.create_image(
            zoom_x, zoom_y,
            image=self.zoom_photo,
            anchor='nw'
        )

    def update_boxes(self):
        """Update box positions and labels"""
        # Update Start Box
        self.canvas.coords(self.start_rect, self.start_x1, self.start_y1, self.start_x2, self.start_y2)
        start_label_x = self.start_x1 + (self.start_x2 - self.start_x1) // 2
        start_label_y = self.start_y1 - 20
        self.canvas.coords(self.start_label, start_label_x, start_label_y)

        # Update Corner Box
        self.canvas.coords(self.corner_rect, self.corner_x1, self.corner_y1, self.corner_x2, self.corner_y2)
        corner_label_x = self.corner_x1 + (self.corner_x2 - self.corner_x1) // 2
        corner_label_y = self.corner_y1 - 20
        self.canvas.coords(self.corner_label, corner_label_x, corner_label_y)

        # Recreate handles
        self.create_all_handles()

    def finish_selection(self):
        """Finish selection and return coordinates"""
        start_coords = {
            "x1": self.start_x1,
            "y1": self.start_y1,
            "x2": self.start_x2,
            "y2": self.start_y2
        }
        corner_coords = {
            "x1": self.corner_x1,
            "y1": self.corner_y1,
            "x2": self.corner_x2,
            "y2": self.corner_y2
        }
        self.window.destroy()
        self.callback(start_coords, corner_coords)


class HotkeyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotkey Manager")
        self.root.geometry("300x280")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Default hotkeys
        self.hotkeys = {
            'start_stop': keyboard.Key.f1,
            'change_area': keyboard.Key.f2,
            'exit': keyboard.Key.f3
        }
        
        # State
        self.is_running = False
        self.listener = None
        self.mouse_listener = None
        self.rebinding = None
        self.area_selector = None
        
        # Loop state
        self.detection_thread = None
        self.qe_thread = None
        self.flag = False
        self.corner_flag = False
        self.stop_detection = False
        self.stop_qe = False
        
        # Template confirmation counters
        self.template_counters = {'f': 0, 'e': 0, 'q': 0, 'r': 0}
        
        # PNG detection tracking for auto Fast mode
        self.last_png_detected_time = 0  # Timestamp when PNG was last detected
        self.png_was_found = False  # Track if we were previously detecting a PNG
        self.auto_fast_triggered = False  # Prevent multiple fast mode switches
        
        # Corner pattern detection system - linear state machine
        self.corner_press_count = 0  # How many times we've pressed (0, 1, 2, 3)
        self.corner_state = 'waiting_color'  # States: waiting_color, wait_on, wait_off, wait_on2
        self.corner_last_seen_time = 0  # Timestamp when ANY corner color was last detected (3s timeout)
        
        # Cached templates - load once at startup
        self.templates_cache = {}
        self.template_sizes = {}  # Cache template dimensions
        
        # Mode system
        self.mode = DEFAULT_MODE
        self.previous_mode = DEFAULT_MODE  # Track mode before xbutton toggle
        self.mode_delays = MODE_DELAYS.copy()  # Make a copy to avoid reference issues
        self.last_qe_time = 0
        self.last_qe_key = 'q'
        self.xbutton_press_count = 0  # Track if xbutton was pressed (allow at least one Q/E cycle)
        
        # Config file path
        self.config_file = "p_settings.json"
        
        # Default area boxes
        self.start_box = {"x1": 1230, "y1": 817, "x2": 1331, "y2": 915}
        self.corner_box = {"x1": 1169, "y1": 823, "x2": 1394, "y2": 1047}
        
        # Pre-compute color bounds for faster detection
        self.red_lower = np.array([max(0, c - 10) for c in COLOR_RED_RGB], dtype=np.uint8)
        self.red_upper = np.array([min(255, c + 10) for c in COLOR_RED_RGB], dtype=np.uint8)
        self.blue_lower = np.array([max(0, c - 10) for c in COLOR_BLUE_RGB], dtype=np.uint8)
        self.blue_upper = np.array([min(255, c + 10) for c in COLOR_BLUE_RGB], dtype=np.uint8)
        
        # Load saved settings
        self.load_settings()
        
        # Load templates after settings
        self.load_templates()
        
        self.create_widgets()
        self.start_listener()
    
    def load_templates(self):
        """Pre-load all templates at startup for faster detection"""
        template_files = ["E.png", "F.png", "Q.png", "R.png"]
        for template_file in template_files:
            if os.path.exists(template_file):
                template = cv2.imread(template_file, cv2.IMREAD_COLOR)
                if template is not None:
                    self.templates_cache[template_file] = template
                    self.template_sizes[template_file] = (template.shape[0], template.shape[1])
                    print(f"Loaded template: {template_file}")
                else:
                    print(f"Failed to load template: {template_file}")
            else:
                print(f"Template not found: {template_file}")
    
    def get_mode_name(self, mode_key):
        """Get display name for a mode based on its delay value"""
        delay = self.mode_delays[mode_key]
        if delay is None:
            return 'Disabled'
        elif delay == 0:
            return 'Fast'
        else:
            return f'{int(delay*1000)}ms'
        
    def create_widgets(self):
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5)
        
        # Start/Stop row
        frame1 = ttk.Frame(self.root, padding="10")
        frame1.pack(fill='x')
        ttk.Label(frame1, text="Start/Stop:", width=15).pack(side='left')
        self.start_stop_label = ttk.Label(frame1, text="F1", width=10, relief='sunken', anchor='center')
        self.start_stop_label.pack(side='left', padx=5)
        ttk.Button(frame1, text="Rebind", command=lambda: self.rebind_key('start_stop')).pack(side='left')
        
        # Change Area row
        frame2 = ttk.Frame(self.root, padding="10")
        frame2.pack(fill='x')
        ttk.Label(frame2, text="Change Area:", width=15).pack(side='left')
        self.change_area_label = ttk.Label(frame2, text="F2", width=10, relief='sunken', anchor='center')
        self.change_area_label.pack(side='left', padx=5)
        ttk.Button(frame2, text="Rebind", command=lambda: self.rebind_key('change_area')).pack(side='left')
        
        # Exit row
        frame3 = ttk.Frame(self.root, padding="10")
        frame3.pack(fill='x')
        ttk.Label(frame3, text="Exit:", width=15).pack(side='left')
        self.exit_label = ttk.Label(frame3, text="F3", width=10, relief='sunken', anchor='center')
        self.exit_label.pack(side='left', padx=5)
        ttk.Button(frame3, text="Rebind", command=lambda: self.rebind_key('exit')).pack(side='left')
        
        # Status frame with colored background
        self.status_frame = tk.Frame(self.root, relief='solid', borderwidth=3)
        self.status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Large status label
        self.status_label = tk.Label(
            self.status_frame, 
            text="● STOPPED",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="red",
            pady=15
        )
        self.status_label.pack(fill='x')
        
        # Mode timing label
        self.mode_label = tk.Label(
            self.status_frame,
            text=f"Mode: {self.get_mode_name(self.mode)}",
            font=("Arial", 12),
            fg="black",
            bg="lightgray",
            pady=5
        )
        self.mode_label.pack(fill='x')
        
    def start_listener(self):
        """Start keyboard and mouse listeners"""
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self.on_key_press)
            self.listener.start()
        if self.mouse_listener is None:
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
    
    def on_key_press(self, key):
        """Handle key press events"""
        if self.rebinding:
            # Rebinding mode
            self.hotkeys[self.rebinding] = key
            key_name = self.get_key_name(key)
            
            if self.rebinding == 'start_stop':
                self.start_stop_label.config(text=key_name)
            elif self.rebinding == 'change_area':
                self.change_area_label.config(text=key_name)
            elif self.rebinding == 'exit':
                self.exit_label.config(text=key_name)
            
            self.rebinding = None
            self.status_label.config(text=f"Status: {'Running' if self.is_running else 'Stopped'}")
            self.save_settings()
            return
        
        # Normal mode - check for hotkey actions
        if key == self.hotkeys['start_stop']:
            self.toggle_start_stop()
        elif key == self.hotkeys['change_area']:
            self.toggle_change_area()
        elif key == self.hotkeys['exit']:
            self.exit_app()
        # Mode switching (Z/X/C only - permanent modes)
        elif hasattr(key, 'char') and key.char in ['z', 'x', 'c']:
            self.mode = key.char
            self.previous_mode = key.char  # Update previous for toggle return
            mode_name = self.get_mode_name(self.mode)
            print(f"Mode changed to: {mode_name}")
            # Update mode label
            self.mode_label.config(text=f"Mode: {mode_name}")
        # X mode timing adjustment ([ = increase, ] = decrease)
        elif hasattr(key, 'char') and key.char == '[':
            if self.mode_delays['x'] is not None:
                self.mode_delays['x'] = round(self.mode_delays['x'] + 0.001, 3)
                print(f"X mode timing increased to {int(self.mode_delays['x']*1000)}ms")
                self.save_settings()
                # Update mode label if in X mode
                if self.mode == 'x':
                    self.mode_label.config(text=f"Mode: {self.get_mode_name('x')}")
        elif hasattr(key, 'char') and key.char == ']':
            if self.mode_delays['x'] is not None and self.mode_delays['x'] > 0:
                self.mode_delays['x'] = round(self.mode_delays['x'] - 0.001, 3)
                print(f"X mode timing decreased to {int(self.mode_delays['x']*1000)}ms")
                self.save_settings()
                # Update mode label if in X mode
                if self.mode == 'x':
                    self.mode_label.config(text=f"Mode: {self.get_mode_name('x')}")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse button events for XButton4/5 toggle modes"""
        # XButton4 = z mode (disabled), XButton5 = v mode (toggle while held)
        if button == mouse.Button.x1:  # XButton4 -> z mode (disabled)
            if pressed:
                # Store current mode before switching
                if self.mode not in ['v', 'z']:  # Only store if not already in toggle mode
                    self.previous_mode = self.mode
                self.mode = 'z'
                self.xbutton_press_count = 0  # Reset counter on new press
                mode_name = self.get_mode_name('z')
                print(f"Mode toggled to: {mode_name}")
                self.mode_label.config(text=f"Mode: {mode_name}")
            else:
                # Return to X mode when released
                self.mode = 'x'
                self.previous_mode = 'x'
                mode_name = self.get_mode_name('x')
                print(f"Mode returned to: {mode_name}")
                self.mode_label.config(text=f"Mode: {mode_name}")
        
        elif button == mouse.Button.x2:  # XButton5 -> v mode
            if pressed:
                # Store current mode before switching
                if self.mode not in ['v', 'z']:  # Only store if not already in toggle mode
                    self.previous_mode = self.mode
                self.mode = 'v'
                self.xbutton_press_count = 0  # Reset counter on new press
                mode_name = self.get_mode_name('v')
                print(f"Mode toggled to: {mode_name}")
                self.mode_label.config(text=f"Mode: {mode_name}")
            else:
                # Return to X mode when released
                self.mode = 'x'
                self.previous_mode = 'x'
                mode_name = self.get_mode_name('x')
                print(f"Mode returned to: {mode_name}")
                self.mode_label.config(text=f"Mode: {mode_name}")
    
    def get_key_name(self, key):
        """Get readable name for key"""
        try:
            if hasattr(key, 'name'):
                return key.name.upper()
            else:
                return str(key.char).upper()
        except:
            return str(key)
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                
                # Load area boxes
                if 'start_box' in settings:
                    self.start_box = settings['start_box']
                if 'corner_box' in settings:
                    self.corner_box = settings['corner_box']
                
                # Load hotkeys
                if 'hotkeys' in settings:
                    for action, key_str in settings['hotkeys'].items():
                        if action in self.hotkeys:
                            # Convert string back to key object
                            if key_str.startswith('Key.'):
                                key_name = key_str.replace('Key.', '')
                                self.hotkeys[action] = getattr(keyboard.Key, key_name, self.hotkeys[action])
                            else:
                                self.hotkeys[action] = keyboard.KeyCode.from_char(key_str.lower())
                
                # Load mode delays
                if 'mode_delays' in settings:
                    self.mode_delays = settings['mode_delays']
                
                print("Settings loaded successfully")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            # Convert hotkeys to serializable format
            hotkeys_dict = {}
            for action, key in self.hotkeys.items():
                if hasattr(key, 'name'):
                    hotkeys_dict[action] = f"Key.{key.name}"
                elif hasattr(key, 'char'):
                    hotkeys_dict[action] = key.char
                else:
                    hotkeys_dict[action] = str(key)
            
            settings = {
                'start_box': self.start_box,
                'corner_box': self.corner_box,
                'hotkeys': hotkeys_dict,
                'mode_delays': self.mode_delays
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def rebind_key(self, action):
        """Start rebinding process"""
        self.rebinding = action
        self.status_label.config(text="Press any key to rebind...")
        self.save_settings()
    
    def toggle_start_stop(self):
        """Toggle start/stop state"""
        self.is_running = not self.is_running
        
        if self.is_running:
            # Safety feature: Set mode to disabled (z) when starting
            self.mode = 'z'
            self.previous_mode = 'z'
            mode_name = self.get_mode_name('z')
            self.mode_label.config(text=f"Mode: {mode_name}")
            print(f"Safety: Mode set to {mode_name} on start")
            
            self.status_label.config(text="● RUNNING", bg="green")
            self.start_detection_loop()
        else:
            self.status_label.config(text="● STOPPED", bg="red")
            self.stop_detection_loop()
        
        print(f"Start/Stop toggled: {'Running' if self.is_running else 'Stopped'}")
    
    def toggle_change_area(self):
        """Toggle area selector - open if closed, save and close if open"""
        if self.area_selector is None:
            # Open area selector
            screenshot = ImageGrab.grab()
            self.area_selector = DualAreaSelector(
                self.root, 
                screenshot, 
                self.start_box, 
                self.corner_box,
                self.on_areas_selected
            )
            self.status_label.config(text="Area selection mode - Press F2 to save")
        else:
            # Save and close area selector
            self.area_selector.finish_selection()
    
    def on_areas_selected(self, start_coords, corner_coords):
        """Called when area selections are complete"""
        self.start_box = start_coords
        self.corner_box = corner_coords
        self.area_selector = None
        print(f"Start Box: {self.start_box}")
        print(f"Corner Box: {self.corner_box}")
        self.save_settings()
        self.status_label.config(text="Areas saved!")
        self.root.after(2000, lambda: self.status_label.config(
            text=f"Status: {'Running' if self.is_running else 'Stopped'}"
        ))
    
    def calculate_capture_region(self):
        """Calculate minimum rectangle containing all boxes"""
        min_x = min(self.start_box["x1"], self.corner_box["x1"])
        min_y = min(self.start_box["y1"], self.corner_box["y1"])
        max_x = max(self.start_box["x2"], self.corner_box["x2"])
        max_y = max(self.start_box["y2"], self.corner_box["y2"])
        
        return {"top": min_y, "left": min_x, "width": max_x - min_x, "height": max_y - min_y}
    
    @staticmethod
    def crop_box_from_capture(capture_array, box, capture_left, capture_top):
        """Crop a specific box from the captured region"""
        # Calculate relative position within the capture
        rel_x1 = box["x1"] - capture_left
        rel_y1 = box["y1"] - capture_top
        rel_x2 = box["x2"] - capture_left
        rel_y2 = box["y2"] - capture_top
        
        return capture_array[rel_y1:rel_y2, rel_x1:rel_x2]
    
    def find_image_in_region(self, region, template_path, threshold=TEMPLATE_CONFIDENCE):
        """Check if template image exists in region using cached templates"""
        # Use cached template
        template = self.templates_cache.get(template_path)
        if template is None:
            return False
        
        # Early exit using cached dimensions
        template_h, template_w = self.template_sizes.get(template_path, (0, 0))
        if region.shape[0] < template_h or region.shape[1] < template_w:
            return False
        
        result = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        return max_val >= threshold
    
    def find_color_bounding_box_fast(self, region_rgb, lower_bound, upper_bound):
        """Optimized color bounding box detection with pre-computed bounds"""
        mask = cv2.inRange(region_rgb, lower_bound, upper_bound)
        
        # Find all pixels that match - using nonzero is faster
        y_coords, x_coords = np.nonzero(mask)
        
        if len(x_coords) == 0:
            return None
        
        # Using array min/max is faster than Python min/max
        return {
            'left': int(x_coords.min()),
            'right': int(x_coords.max()),
            'top': int(y_coords.min()),
            'bottom': int(y_coords.max())
        }
    
    @staticmethod
    def is_point_inside_box(x, y, box):
        """Check if a point (x, y) is inside a bounding box"""
        return box['left'] <= x <= box['right'] and box['top'] <= y <= box['bottom']
    
    @staticmethod
    def calculate_box_center(box):
        """Calculate the center point of a bounding box"""
        return (box['left'] + box['right']) >> 1, (box['top'] + box['bottom']) >> 1
    
    def send_key_press(self, key_char):
        """Send a keyboard key press using win32api"""
        # Handle special key names
        if key_char.lower() == "enter":
            vk_code = win32con.VK_RETURN
            scan_code = 0
        elif len(key_char) == 1:
            # Use VkKeyScan to get the correct virtual key and shift state
            result = win32api.VkKeyScan(key_char)
            if result == -1:
                print(f"Cannot map key: {key_char}")
                return
            
            vk_code = result & 0xFF
            shift_state = (result >> 8) & 0xFF
            
            # Handle shift state if needed
            need_shift = (shift_state & 1) != 0
            need_ctrl = (shift_state & 2) != 0
            need_alt = (shift_state & 4) != 0
            
            # Press modifier keys if needed
            if need_shift:
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            if need_ctrl:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            if need_alt:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            
            # Press the main key
            scan_code = win32api.MapVirtualKey(vk_code, 0)
            win32api.keybd_event(vk_code, scan_code, 0, 0)  # Key down
            win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            
            # Release modifier keys if needed
            if need_alt:
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            if need_ctrl:
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            if need_shift:
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            return
        else:
            print(f"Unsupported key format: {key_char}")
            return

        # For special keys like Enter
        scan_code = win32api.MapVirtualKey(vk_code, 0)
        win32api.keybd_event(vk_code, scan_code, 0, 0)  # Key down
        time.sleep(0.01)
        win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)  # Key up
    
    def detection_loop(self):
        """Main detection loop running in background thread"""
        sct = mss.mss()
        capture_region = self.calculate_capture_region()
        
        # Templates to check: (filename, key_to_press) - order matters for priority
        templates = [
            ("F.png", "f"),
            ("E.png", "e"),
            ("Q.png", "q"),
            ("R.png", "r")
        ]
        
        print(f"Detection loop started. Capture region: {capture_region}")
        
        # Cache for reduced allocations
        last_corner_status = "NO CORNER"
        corner_check_counter = 0
        capture_left = capture_region["left"]
        capture_top = capture_region["top"]
        
        # Throttle detection to avoid interfering with Q/E timing
        last_loop_time = time.perf_counter()
        min_loop_interval = 0.016  # ~60 FPS max for detection
        
        while not self.stop_detection:
            if not self.is_running:
                time.sleep(0.1)
                continue
            
            try:
                # Throttle loop to consistent frame rate at start (prevents CPU spikes)
                elapsed = time.perf_counter() - last_loop_time
                if elapsed < min_loop_interval:
                    time.sleep(min_loop_interval - elapsed)
                last_loop_time = time.perf_counter()
                
                # Capture the region using MSS
                screenshot = sct.grab(capture_region)
                capture_array = np.array(screenshot)
                capture_bgr = cv2.cvtColor(capture_array, cv2.COLOR_BGRA2BGR)
                
                # Crop start_box from the capture
                start_region = self.crop_box_from_capture(capture_bgr, self.start_box, capture_left, capture_top)
                
                # Check for each template - early exit on first match
                found_key = None
                for template_file, key in templates:
                    if self.find_image_in_region(start_region, template_file):
                        found_key = key
                        break
                
                if found_key:
                    # Increment counter for found template
                    self.template_counters[found_key] += 1
                    
                    # Reset other counters
                    for k in self.template_counters:
                        if k != found_key:
                            self.template_counters[k] = 0
                    
                    # Only press if counter reaches threshold
                    if self.template_counters[found_key] >= TEMPLATE_CONFIRM_COUNT and not self.flag:
                        self.send_key_press(found_key)
                        self.flag = True
                        self.template_counters[found_key] = 0
                    
                    # PNG detected - update tracking
                    self.last_png_detected_time = time.time()
                    self.png_was_found = True
                    self.auto_fast_triggered = False  # Reset flag when PNG is found
                else:
                    # Reset all counters when nothing is found
                    if any(self.template_counters.values()):
                        for k in self.template_counters:
                            self.template_counters[k] = 0
                    self.flag = False
                    
                    # PNG not detected - check if we should auto-switch to Fast mode
                    if self.png_was_found and not self.auto_fast_triggered:
                        # PNG was detected before, now it's not - check 2 second timeout
                        time_since_last = time.time() - self.last_png_detected_time
                        if time_since_last >= 2.0:
                            print("PNG not detected for 2 seconds - auto-switching to Fast mode")
                            self.mode = 'c'
                            self.previous_mode = 'c'
                            mode_name = self.get_mode_name('c')
                            self.mode_label.config(text=f"Mode: {mode_name}")
                            self.auto_fast_triggered = True  # Only trigger once per detection loss
                            
                            # Send right click down after 2 seconds of PNG loss
                            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                            print("Right click down sent (after 2 seconds PNG loss)")
                
                # Corner detection - only check every few frames for performance
                corner_check_counter += 1
                if corner_check_counter >= 2:  # Check every 2nd frame
                    corner_check_counter = 0
                    
                    # Crop corner_box from the capture
                    corner_region = self.crop_box_from_capture(capture_bgr, self.corner_box, capture_left, capture_top)
                    corner_region_rgb = cv2.cvtColor(corner_region, cv2.COLOR_BGR2RGB)
                    
                    # Find bounding box of red using pre-computed bounds
                    red_box = self.find_color_bounding_box_fast(corner_region_rgb, self.red_lower, self.red_upper)
                    
                    if red_box is None:
                        corner_status = "NO CORNER"
                    else:
                        # Find bounding box of blue
                        blue_box = self.find_color_bounding_box_fast(corner_region_rgb, self.blue_lower, self.blue_upper)
                        
                        if blue_box is None:
                            corner_status = "NO CORNER"
                        else:
                            # Calculate center of blue bounding box using optimized function
                            blue_center_x, blue_center_y = self.calculate_box_center(blue_box)
                            
                            # Check if blue center is inside red box
                            corner_status = "FOUND CORNER" if self.is_point_inside_box(blue_center_x, blue_center_y, red_box) else "NOT INSIDE RED"
                    
                    # Store for next iteration
                    last_corner_status = corner_status
                else:
                    # Reuse last status to skip expensive color detection
                    corner_status = last_corner_status
                
                # Linear corner detection state machine
                corner_found_now = (corner_status == "FOUND CORNER")
                
                # Update timeout timer whenever ANY corner color is detected (red or blue found)
                current_time = time.time()
                if corner_status != "NO CORNER":
                    self.corner_last_seen_time = current_time
                
                # Failsafe: If no corner color detected for 3 seconds, reset everything
                if self.corner_last_seen_time > 0 and (current_time - self.corner_last_seen_time >= 3.0):
                    if self.corner_state != 'waiting_color' or self.corner_press_count > 0:
                        print("3-second timeout (no color detected) - resetting all corner state")
                        self.corner_press_count = 0
                        self.corner_state = 'waiting_color'
                        self.corner_last_seen_time = 0
                
                # Linear state machine
                if self.corner_state == 'waiting_color':
                    # Waiting for any color to appear
                    if corner_status != "NO CORNER":
                        print(f"Color detected - starting press #{self.corner_press_count + 1} cycle")
                        self.corner_state = 'wait_on'
                
                elif self.corner_state == 'wait_on':
                    # Wait for corner ON
                    if corner_found_now:
                        print(f"Press #{self.corner_press_count + 1} - Corner ON (1st)")
                        self.corner_state = 'wait_off'
                
                elif self.corner_state == 'wait_off':
                    # Wait for corner OFF
                    if not corner_found_now:
                        print(f"Press #{self.corner_press_count + 1} - Corner OFF")
                        # Special case for 3rd press: switch to v mode
                        if self.corner_press_count == 2:
                            print("3rd press detected - switching to v mode immediately")
                            self.previous_mode = self.mode
                            self.mode = 'v'
                            mode_name = self.get_mode_name('v')
                            print(f"Mode switched to: {mode_name}")
                            self.mode_label.config(text=f"Mode: {mode_name}")
                        self.corner_state = 'wait_on2'
                
                elif self.corner_state == 'wait_on2':
                    # Wait for corner ON again (2nd appearance)
                    if corner_found_now:
                        print(f"Press #{self.corner_press_count + 1} - Corner ON (2nd) - PRESSING SPACEBAR")
                        self.send_key_press(" ")
                        self.corner_press_count += 1
                        
                        # Check if we completed 3rd press
                        if self.corner_press_count >= 3:
                            print("3rd press complete - resetting counter for next race")
                            self.corner_press_count = 0
                        
                        # Wait for color to disappear before next cycle
                        self.corner_state = 'wait_color_off'
                
                elif self.corner_state == 'wait_color_off':
                    # Wait for any color to disappear completely
                    if corner_status == "NO CORNER":
                        print(f"Color cleared - ready for next detection")
                        self.corner_state = 'waiting_color'
                
            except Exception as e:
                print(f"Detection error: {e}")
        
        print("Detection loop stopped")
    
    def qe_loop(self):
        """Dedicated Q/E alternation loop with precise timing - runs independently"""
        print("Q/E alternation loop started")
        
        # Pre-cache key values to avoid string lookups
        key_q = 'q'
        key_e = 'e'
        
        while not self.stop_qe:
            if not self.is_running:
                time.sleep(0.05)
                continue
            
            try:
                # Handle Q/E alternation based on mode
                current_mode = self.mode  # Cache mode to avoid race conditions
                
                # For z mode (disabled) - but allow at least 1 cycle if xbutton was tapped
                if current_mode == 'z':
                    if self.xbutton_press_count < 1:
                        # Allow one Q/E cycle for micro adjustments
                        self.xbutton_press_count += 1
                    else:
                        # After first cycle, stop executing
                        time.sleep(0.05)
                        continue
                elif current_mode in ['v', 'x', 'c']:
                    # For active modes, keep resetting counter so it stays active while held
                    self.xbutton_press_count = 0
                
                delay = self.mode_delays[current_mode]
                if delay is None:
                    time.sleep(0.05)
                    continue
                
                # Alternate between Q and E
                if self.last_qe_key == key_q:
                    self.send_key_press(key_e)
                    self.last_qe_key = key_e
                else:
                    self.send_key_press(key_q)
                    self.last_qe_key = key_q
                
                # Sleep for exact delay time (minimum 1ms for CPU efficiency)
                time.sleep(max(delay, 0.001))
                    
            except Exception as e:
                print(f"Q/E alternation error: {e}")
                time.sleep(0.05)
        
        print("Q/E alternation loop stopped")
    
    def start_detection_loop(self):
        """Start the detection loop in a background thread"""
        # Start dedicated Q/E alternation thread FIRST (higher priority for timing)
        if self.qe_thread is None or not self.qe_thread.is_alive():
            self.stop_qe = False
            self.last_qe_time = time.time()
            self.qe_thread = threading.Thread(target=self.qe_loop, daemon=True, name="QE-Loop")
            self.qe_thread.start()
        
        if self.detection_thread is None or not self.detection_thread.is_alive():
            self.stop_detection = False
            self.flag = False
            self.corner_flag = False
            # Reset corner detection state
            self.corner_press_count = 0
            self.corner_state = 'waiting_color'
            self.corner_last_seen_time = 0
            # Reset PNG detection tracking
            self.last_png_detected_time = 0
            self.png_was_found = False
            self.auto_fast_triggered = False
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True, name="Detection-Loop")
            self.detection_thread.start()
    
    def stop_detection_loop(self):
        """Stop the detection loop"""
        self.stop_detection = True
        self.stop_qe = True
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
        if self.qe_thread:
            self.qe_thread.join(timeout=1.0)
        
        # After everything stops, send right click up and ESC twice
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        print("Right click up sent (after stop)")
    
    def exit_app(self):
        """Exit the application"""
        print("Exiting application")
        self.stop_detection_loop()
        self.save_settings()
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HotkeyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
