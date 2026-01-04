import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import time
from PIL import Image, ImageTk, ImageGrab, ImageDraw
from pynput import mouse
import json
import os
import sys
import mss
import cv2
import numpy as np
import win32api
import win32con

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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


class HotkeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotkey Controller")
        self.root.geometry("260x280")
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        
        # State variables
        self.running = False
        self.resize_mode = False
        self.main_loop_thread = None
        self.area_selector = None
        self.qe_thread = None
        self.stop_qe = False
        self.mouse_listener = None
        self.detection_thread = None
        self.stop_detection = False
        
        # Detection state machine variables
        self.last_found_png = None
        self.png_found_start_time = None
        self.png_confirmed = False
        self.waiting_for_disappear = False
        self.timer_start_time = None
        self.timer_active = False
        
        # Corner detection state machine
        self.corner_state = 'waiting_on'  # States: waiting_on, wait_off, wait_on2, wait_off_disappear
        self.corner_press_count = 0  # Track which press we're on (1, 2, or 3)
        self.corner_last_seen_time = None  # Track when colors were last detected
        self.corner_off_start_time = None  # Track when corner OFF was first detected (for 500ms confirmation)
        
        # Queue system for quick button taps
        self.queued_mode = None  # Tuple of (mode_key, remaining_cycles)
        
        # Hotkey bindings
        self.hotkeys = {
            'start_stop': 'f1',
            'resize_area': 'f7',
            'exit': 'f8'
        }
        
        # Mode settings: mode_key -> (name, delay_in_seconds)
        self.mode_settings = {
            'x': ('None', None),
            'v': ('Ultra', 0.0),
            'normal': ('Normal', 0.215),
            'xbutton4': ('None', None),
            'xbutton5': ('Fast', 0.1)
        }
        
        # Uma character presets (name -> delay_in_ms)
        self.uma_presets = {
            'Haru Urara': 215,
            'Air Groove': 215,
            'Gold Ship': 260,
            'Daiwa Scarlet': 260,
            'Oguri Cap': 260,
            'Rice Shower': 260,
            'Tamamo Cross': 260,
            'Silence Suzuka': 315
        }
        
        # Current selected uma (will be loaded from settings or default to Haru Urara)
        self.selected_uma = 'Haru Urara'
        
        # Current mode and Q/E timing
        self.current_mode = 'x'  # Start with Disabled
        self.last_qe_key = 'q'
        
        # Default area boxes
        self.start_box = {"x1": 1230, "y1": 817, "x2": 1331, "y2": 915}
        self.corner_box = {"x1": 1169, "y1": 823, "x2": 1394, "y2": 1047}
        
        # Color detection settings
        self.blue_rgb = (107, 243, 246)
        self.red_rgb = (255, 69, 150)
        # Pre-compute color bounds for faster detection
        self.red_lower = np.array([max(0, c - 10) for c in self.red_rgb], dtype=np.uint8)
        self.red_upper = np.array([min(255, c + 10) for c in self.red_rgb], dtype=np.uint8)
        self.blue_lower = np.array([max(0, c - 10) for c in self.blue_rgb], dtype=np.uint8)
        self.blue_upper = np.array([min(255, c + 10) for c in self.blue_rgb], dtype=np.uint8)
        
        # Template cache for PNG detection
        self.templates_cache = {}
        
        # Setup config file path
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                exe_dir = os.path.dirname(sys.executable)
                self.config_file = os.path.join(exe_dir, "UmaRacingSettings.json")
            else:
                # Running as script
                self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UmaRacingSettings.json")
        except:
            self.config_file = "UmaRacingSettings.json"
        
        # Load saved settings
        self.load_settings()
        
        # Load templates for detection
        self.load_templates()
        
        self.setup_ui()
        self.register_hotkeys()
        self.start_mouse_listener()
        
    def start_mouse_listener(self):
        """Start mouse listener for xbutton4/5"""
        if self.mouse_listener is None:
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse button events for XButton4/5 and middle button"""
        if not self.running:
            return  # Only work when script is running
        
        if button == mouse.Button.x1:  # XButton4
            if pressed:
                self.xbutton4_press_time = time.time()
                self.switch_mode('xbutton4')
            else:
                # Check if it was a quick tap (released within 100ms)
                if hasattr(self, 'xbutton4_press_time') and (time.time() - self.xbutton4_press_time) < 0.1:
                    # Queue one disabled cycle at half speed
                    self.queued_mode = ('xbutton4_half', 1)
                    print("Queued 1 disabled cycle at half speed")
                # Return to Normal when released
                self.switch_mode('normal')
        
        elif button == mouse.Button.x2:  # XButton5
            if pressed:
                self.xbutton5_press_time = time.time()
                self.switch_mode('xbutton5')
            else:
                # Check if it was a quick tap (released within 100ms)
                if hasattr(self, 'xbutton5_press_time') and (time.time() - self.xbutton5_press_time) < 0.1:
                    # Queue one fast cycle
                    self.queued_mode = ('xbutton5', 1)
                    print("Queued 1 fast cycle")
                # Return to Normal when released
                self.switch_mode('normal')
        
        elif button == mouse.Button.middle:  # Middle button (scroll wheel click)
            if pressed:
                print("Middle button pressed - holding right click down")
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    
    def switch_mode(self, mode_key):
        """Switch to a specific mode and update display"""
        if mode_key in self.mode_settings:
            self.current_mode = mode_key
            mode_name = self.get_mode_display()
            self.mode_label.config(text=mode_name)
            print(f"Mode switched to: {mode_name}")
    
    def adjust_normal_delay(self, change_ms):
        """Adjust Normal mode delay by change_ms milliseconds"""
        mode_name, current_delay = self.mode_settings['normal']
        if current_delay is not None:
            # Convert to ms, adjust, convert back to seconds
            current_ms = int(current_delay * 1000)
            new_ms = max(0, current_ms + change_ms)  # Don't go below 0
            new_delay = new_ms / 1000.0
            self.mode_settings['normal'] = (mode_name, new_delay)
            
            # Update the selected uma preset with new value
            self.uma_presets[self.selected_uma] = new_ms
            
            print(f"Normal mode delay adjusted to {new_ms}ms for {self.selected_uma}")
            self.save_settings()
            # Update display if currently in Normal mode
            if self.current_mode == 'normal':
                self.mode_label.config(text=self.get_mode_display())
    
    def on_uma_selected(self, event=None):
        """Handle uma dropdown selection change"""
        self.selected_uma = self.uma_var.get()
        # Update Normal mode delay based on selected uma
        uma_delay_ms = self.uma_presets[self.selected_uma]
        uma_delay_sec = uma_delay_ms / 1000.0
        self.mode_settings['normal'] = ('Normal', uma_delay_sec)
        print(f"Uma changed to {self.selected_uma} ({uma_delay_ms}ms)")
        self.save_settings()
        # Update display if currently in Normal mode
        if self.current_mode == 'normal':
            self.mode_label.config(text=self.get_mode_display())
    
    def hold_key(self, key):
        """Hold a key down for 20ms in a separate thread"""
        def hold_thread():
            keyboard.press(key)
            time.sleep(0.02)
            keyboard.release(key)
        
        threading.Thread(target=hold_thread, daemon=True).start()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status indicator
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.status_canvas = tk.Canvas(status_frame, width=30, height=30, highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=5)
        self.status_indicator = self.status_canvas.create_oval(5, 5, 25, 25, fill='red', outline='')
        self.status_label = ttk.Label(status_frame, text="STOPPED", font=('Arial', 12, 'bold'), foreground='red')
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Mode label
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        ttk.Label(mode_frame, text="Mode:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        self.mode_label = ttk.Label(mode_frame, text=self.get_mode_display(), font=('Arial', 12, 'bold'))
        self.mode_label.pack(side=tk.LEFT, padx=5)
        
        # Uma dropdown
        uma_frame = ttk.Frame(main_frame)
        uma_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        ttk.Label(uma_frame, text="Uma:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.uma_var = tk.StringVar(value=self.selected_uma)
        self.uma_dropdown = ttk.Combobox(uma_frame, textvariable=self.uma_var, 
                                         values=list(self.uma_presets.keys()),
                                         state='readonly', width=15)
        self.uma_dropdown.pack(side=tk.LEFT, padx=5)
        self.uma_dropdown.bind('<<ComboboxSelected>>', self.on_uma_selected)
        
        # Hotkey settings
        settings = [
            ("Start/Stop:", "start_stop"),
            ("Resize Area:", "resize_area"),
            ("Exit:", "exit")
        ]
        
        self.hotkey_labels = {}
        
        for idx, (label_text, key) in enumerate(settings):
            # Label
            ttk.Label(main_frame, text=label_text, font=('Arial', 10)).grid(
                row=idx+3, column=0, sticky=tk.W, pady=5
            )
            
            # Hotkey display and rebind button
            hotkey_frame = ttk.Frame(main_frame)
            hotkey_frame.grid(row=idx+3, column=1, sticky=tk.E, pady=5)
            
            hotkey_label = ttk.Label(hotkey_frame, text=self.hotkeys[key].upper(), 
                                    font=('Arial', 10, 'bold'), 
                                    background='#e0e0e0', 
                                    relief=tk.RAISED,
                                    padding=5)
            hotkey_label.pack(side=tk.LEFT, padx=5)
            self.hotkey_labels[key] = hotkey_label
            
            rebind_btn = ttk.Button(hotkey_frame, text="Rebind", 
                                   command=lambda k=key: self.rebind_hotkey(k))
            rebind_btn.pack(side=tk.LEFT)
        
        # Info label
        self.info_label = ttk.Label(main_frame, text="", font=('Arial', 9), foreground='blue')
        self.info_label.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
    def get_mode_display(self):
        """Get display name for current mode"""
        mode_name, delay = self.mode_settings.get(self.current_mode, ('Normal', 0.215))
        if delay is None:
            return f"Disabled - {mode_name}"
        else:
            return f"{int(delay * 1000)}ms {mode_name}"
    
    def register_hotkeys(self):
        """Register all hotkeys"""
        keyboard.unhook_all()
        keyboard.on_press_key(self.hotkeys['start_stop'], lambda _: self.toggle_start_stop())
        keyboard.on_press_key(self.hotkeys['resize_area'], lambda _: self.toggle_resize_area())
        keyboard.on_press_key(self.hotkeys['exit'], lambda _: self.exit_app())
        
        # Register mode switching keys (x, v) - only work when running
        keyboard.on_press_key('x', lambda _: self.switch_mode('x') if self.running else None)
        keyboard.on_press_key('v', lambda _: self.switch_mode('v') if self.running else None)
        
        # Register [ and ] for adjusting Normal mode delay - only work when running
        keyboard.on_press_key('[', lambda _: self.adjust_normal_delay(1) if self.running else None)
        keyboard.on_press_key(']', lambda _: self.adjust_normal_delay(-1) if self.running else None)
        
        # Register Z and C for A/D holds - only work when running
        keyboard.on_press_key('z', lambda _: self.hold_key('a') if self.running else None)
        keyboard.on_press_key('c', lambda _: self.hold_key('d') if self.running else None)
        
    def toggle_start_stop(self):
        """Toggle the main loop on/off"""
        self.running = not self.running
        
        if self.running:
            self.status_canvas.itemconfig(self.status_indicator, fill='green')
            self.status_label.config(text="RUNNING", foreground='green')
            # Start Q/E alternation thread
            if self.qe_thread is None or not self.qe_thread.is_alive():
                self.stop_qe = False
                self.qe_thread = threading.Thread(target=self.qe_loop, daemon=True)
                self.qe_thread.start()
            # Start detection thread
            if self.detection_thread is None or not self.detection_thread.is_alive():
                self.stop_detection = False
                self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
                self.detection_thread.start()
        else:
            self.status_canvas.itemconfig(self.status_indicator, fill='red')
            self.status_label.config(text="STOPPED", foreground='red')
            # Set mode to Disabled when stopping
            self.switch_mode('x')
            # Stop Q/E alternation
            self.stop_qe = True
            if self.qe_thread:
                self.qe_thread.join(timeout=1.0)
            # Stop detection
            self.stop_detection = True
            if self.detection_thread:
                self.detection_thread.join(timeout=1.0)
            
    def toggle_resize_area(self):
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
            self.info_label.config(text="Area selection mode - Press F7 to save")
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
        self.info_label.config(text="Areas saved!")
        self.root.after(2000, lambda: self.info_label.config(text=""))
        
    def qe_loop(self):
        """Q/E alternation loop with precise timing"""
        print("Q/E alternation loop started")
        
        while not self.stop_qe:
            if not self.running:
                time.sleep(0.1)
                continue
            
            try:
                # Check if there's a queued mode
                if self.queued_mode is not None:
                    queued_key, remaining_cycles = self.queued_mode
                    
                    if remaining_cycles > 0:
                        # Use queued mode
                        if queued_key == 'xbutton4_half':
                            # Disabled mode at half speed
                            time.sleep(0.001)
                            # Decrement queue counter
                            self.queued_mode = (queued_key, remaining_cycles - 1)
                            continue
                        elif queued_key == 'xbutton5':
                            # Fast mode for one cycle
                            mode_name, delay = self.mode_settings.get('xbutton5', ('Fast', 0.1))
                            
                            # Alternate between Q and E
                            if self.last_qe_key == 'q':
                                keyboard.press_and_release('e')
                                self.last_qe_key = 'e'
                            else:
                                keyboard.press_and_release('q')
                                self.last_qe_key = 'q'
                            
                            # Sleep for fast mode delay
                            time.sleep(max(delay, 0.001))
                            
                            # Decrement queue counter
                            self.queued_mode = (queued_key, remaining_cycles - 1)
                            continue
                    else:
                        # Queue exhausted
                        self.queued_mode = None
                
                # Get current mode delay
                mode_name, delay = self.mode_settings.get(self.current_mode, ('Normal', 0.215))
                
                # If delay is None (disabled), don't press anything
                if delay is None:
                    time.sleep(0.001)
                    continue
                
                # Alternate between Q and E
                if self.last_qe_key == 'q':
                    keyboard.press_and_release('e')
                    self.last_qe_key = 'e'
                else:
                    keyboard.press_and_release('q')
                    self.last_qe_key = 'q'
                
                # Sleep for the mode's delay (minimum 1ms for CPU efficiency)
                time.sleep(max(delay, 0.001))
                    
            except Exception as e:
                print(f"Q/E alternation error: {e}")
                time.sleep(0.1)
        
        print("Q/E alternation loop stopped")
    
    def load_templates(self):
        """Load PNG templates for detection"""
        template_files = ["E.png", "F.png", "Q.png", "R.png"]
        for template_file in template_files:
            template_path = get_resource_path(template_file)
            if os.path.exists(template_path):
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    self.templates_cache[template_file] = template
                    print(f"Loaded template: {template_file}")
    
    def find_image_in_region(self, region, template, threshold=0.8):
        """Check if template image exists in region"""
        if template is None or region.shape[0] < template.shape[0] or region.shape[1] < template.shape[1]:
            return False
        
        result = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val >= threshold
    
    def find_color_in_region(self, region_rgb, lower_bound, upper_bound):
        """Check if color exists in region"""
        mask = cv2.inRange(region_rgb, lower_bound, upper_bound)
        return np.any(mask)
    
    def find_color_bounding_box(self, region_rgb, lower_bound, upper_bound):
        """Find bounding box of color in region"""
        mask = cv2.inRange(region_rgb, lower_bound, upper_bound)
        
        # Find all pixels that match
        y_coords, x_coords = np.nonzero(mask)
        
        if len(x_coords) == 0:
            return None
        
        # Return bounding box
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
    
    def detection_loop(self):
        """Background detection loop for PNG and color detection with state machine"""
        print("Detection loop started")
        sct = mss.mss()
        
        while not self.stop_detection:
            if not self.running:
                time.sleep(0.1)
                # Reset state when not running
                self.last_found_png = None
                self.png_found_start_time = None
                self.png_confirmed = False
                self.waiting_for_disappear = False
                self.timer_start_time = None
                self.timer_active = False
                self.corner_state = 'waiting_on'
                self.corner_press_count = 0
                self.corner_last_seen_time = None
                self.corner_off_start_time = None
                continue
            
            try:
                current_time = time.time()
                
                # Capture start_box region for PNG detection
                start_region = {
                    "top": self.start_box["y1"],
                    "left": self.start_box["x1"],
                    "width": self.start_box["x2"] - self.start_box["x1"],
                    "height": self.start_box["y2"] - self.start_box["y1"]
                }
                start_screenshot = sct.grab(start_region)
                start_array = np.array(start_screenshot)
                start_bgr = cv2.cvtColor(start_array, cv2.COLOR_BGRA2BGR)
                
                # Check for PNG templates in start_box
                found_png_name = None
                for template_name, template in self.templates_cache.items():
                    if self.find_image_in_region(start_bgr, template):
                        found_png_name = template_name
                        break
                
                # State machine logic
                if self.waiting_for_disappear:
                    # Waiting for PNG to disappear after pressing key
                    if found_png_name is None:
                        print(f"PNG disappeared, starting 2 second timer")
                        self.waiting_for_disappear = False
                        self.timer_active = True
                        self.timer_start_time = current_time
                        self.last_found_png = None
                        self.png_found_start_time = None
                        self.png_confirmed = False
                
                elif self.timer_active:
                    # Timer is running, check if we find a PNG
                    if found_png_name:
                        # PNG found during timer, cancel timer and start new detection
                        print(f"PNG found during timer ({found_png_name}), canceling timer")
                        self.timer_active = False
                        self.timer_start_time = None
                        self.last_found_png = found_png_name
                        self.png_found_start_time = current_time
                        self.png_confirmed = False
                    else:
                        # Check if timer expired (2 seconds)
                        if current_time - self.timer_start_time >= 2.0:
                            print("Timer expired! Holding right click and switching to Ultra mode")
                            # Hold right click down
                            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                            # Switch to Ultra mode (0ms)
                            self.switch_mode('v')
                            # Reset timer
                            self.timer_active = False
                            self.timer_start_time = None
                
                else:
                    # Normal detection state
                    if found_png_name:
                        # PNG detected
                        if self.last_found_png == found_png_name:
                            # Same PNG, check if it's been 300ms
                            if not self.png_confirmed and (current_time - self.png_found_start_time >= 0.3):
                                # Confirmed! Press the key
                                self.png_confirmed = True
                                self.waiting_for_disappear = True
                                key_to_press = found_png_name[0].lower()  # E.png -> e, R.png -> r, etc.
                                print(f"PNG confirmed for 300ms, pressing {key_to_press}")
                                keyboard.press_and_release(key_to_press)
                        else:
                            # New PNG detected
                            if found_png_name != self.last_found_png:
                                print(f"New PNG detected: {found_png_name}")
                                self.last_found_png = found_png_name
                                self.png_found_start_time = current_time
                                self.png_confirmed = False
                    else:
                        # No PNG found, reset detection
                        if self.last_found_png and not self.png_confirmed:
                            # PNG disappeared before 300ms confirmation
                            self.last_found_png = None
                            self.png_found_start_time = None
                
                # Capture corner_box region for color detection
                corner_region = {
                    "top": self.corner_box["y1"],
                    "left": self.corner_box["x1"],
                    "width": self.corner_box["x2"] - self.corner_box["x1"],
                    "height": self.corner_box["y2"] - self.corner_box["y1"]
                }
                corner_screenshot = sct.grab(corner_region)
                corner_array = np.array(corner_screenshot)
                corner_rgb = cv2.cvtColor(corner_array, cv2.COLOR_BGRA2RGB)
                
                # Check for red and blue colors in corner_box with bounding boxes
                red_box = self.find_color_bounding_box(corner_rgb, self.red_lower, self.red_upper)
                blue_box = self.find_color_bounding_box(corner_rgb, self.blue_lower, self.blue_upper)
                
                # Determine corner status
                corner_is_on = False
                colors_detected = False
                
                if red_box is not None and blue_box is not None:
                    colors_detected = True
                    # Calculate center of blue bounding box
                    blue_center_x, blue_center_y = self.calculate_box_center(blue_box)
                    
                    # Check if blue center is inside red box
                    corner_is_on = self.is_point_inside_box(blue_center_x, blue_center_y, red_box)
                
                # Update last seen time when colors are detected
                if colors_detected:
                    self.corner_last_seen_time = current_time
                
                # Check for 2 second timeout (colors not detected)
                if self.corner_last_seen_time is not None and self.corner_press_count > 0:
                    if not colors_detected:
                        time_since_last = current_time - self.corner_last_seen_time
                        if time_since_last >= 2.0:
                            print(f"2-second timeout (no colors) - resetting from press #{self.corner_press_count}")
                            self.corner_state = 'waiting_on'
                            self.corner_press_count = 0
                            self.corner_last_seen_time = None
                
                # Corner detection state machine
                if self.corner_state == 'waiting_on':
                    # Wait for corner to be ON
                    if colors_detected and corner_is_on:
                        print(f"Press #{self.corner_press_count + 1} - Corner ON (1st)")
                        
                        # Special case for 3rd press: switch to Fast mode
                        if self.corner_press_count == 2:
                            print("3rd press detected - switching to Fast mode")
                            self.switch_mode('xbutton5')
                        
                        self.corner_state = 'wait_off'
                        self.corner_off_start_time = None
                
                elif self.corner_state == 'wait_off':
                    # Wait for corner to be OFF (with 500ms confirmation)
                    if colors_detected and not corner_is_on:
                        if self.corner_off_start_time is None:
                            # First time detecting OFF - start tracking
                            self.corner_off_start_time = current_time
                        else:
                            # Check if OFF has been detected for 500ms
                            elapsed = current_time - self.corner_off_start_time
                            if elapsed >= 0.5:
                                print(f"Press #{self.corner_press_count + 1} - Corner OFF")
                                self.corner_state = 'wait_on2'
                                self.corner_off_start_time = None
                    else:
                        # Reset if corner becomes ON again before 500ms
                        self.corner_off_start_time = None
                
                elif self.corner_state == 'wait_on2':
                    # Wait for corner ON again (2nd appearance)
                    if colors_detected and corner_is_on:
                        print(f"Press #{self.corner_press_count + 1} - Corner ON (2nd) - PRESSING SPACEBAR")
                        
                        # Press spacebar
                        keyboard.press_and_release('space')
                        self.corner_press_count += 1
                        
                        # Check if we completed 3rd press
                        if self.corner_press_count >= 3:
                            print("3rd press complete - resetting counter for next race")
                            self.corner_press_count = 0
                        
                        # Wait for color to disappear
                        self.corner_state = 'wait_off_disappear'
                
                elif self.corner_state == 'wait_off_disappear':
                    # Wait for colors to disappear completely
                    if not colors_detected:
                        print("Colors cleared - ready for next detection")
                        self.corner_state = 'waiting_on'
                
                # Sleep to avoid excessive CPU usage (~120 FPS)
                time.sleep(0.008)
                    
            except Exception as e:
                print(f"Detection error: {e}")
                time.sleep(0.1)
        
        print("Detection loop stopped")
            
    def rebind_hotkey(self, key_name):
        """Rebind a specific hotkey"""
        self.info_label.config(text=f"Press a key for {key_name.replace('_', ' ').title()}...")
        
        def on_key_event(event):
            new_key = event.name
            # Update the hotkey
            self.hotkeys[key_name] = new_key
            self.hotkey_labels[key_name].config(text=new_key.upper())
            self.info_label.config(text=f"Rebound to {new_key.upper()}")
            
            # Re-register all hotkeys
            self.register_hotkeys()
            
            # Clear message after 2 seconds
            self.root.after(2000, lambda: self.info_label.config(text=""))
            
            # Unhook this temporary listener
            keyboard.unhook(hook)
        
        # Hook to capture the next key press
        hook = keyboard.on_press(on_key_event, suppress=False)
        
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
                    for action, key in settings['hotkeys'].items():
                        if action in self.hotkeys:
                            self.hotkeys[action] = key
                
                # Load selected uma
                if 'selected_uma' in settings:
                    self.selected_uma = settings['selected_uma']
                
                # Load uma presets (individual delays)
                if 'uma_presets' in settings:
                    for uma_name, delay_ms in settings['uma_presets'].items():
                        if uma_name in self.uma_presets:
                            self.uma_presets[uma_name] = delay_ms
                
                # Update Normal mode delay based on selected uma
                uma_delay_ms = self.uma_presets[self.selected_uma]
                self.mode_settings['normal'] = ('Normal', uma_delay_ms / 1000.0)
                
                print("Settings loaded successfully")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            settings = {
                'start_box': self.start_box,
                'corner_box': self.corner_box,
                'hotkeys': self.hotkeys,
                'selected_uma': self.selected_uma,
                'uma_presets': self.uma_presets
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            print(f"Settings saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def exit_app(self):
        """Exit the application"""
        self.running = False
        self.stop_qe = True
        self.stop_detection = True
        keyboard.unhook_all()
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.qe_thread:
            self.qe_thread.join(timeout=1.0)
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
        self.root.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = HotkeyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()
