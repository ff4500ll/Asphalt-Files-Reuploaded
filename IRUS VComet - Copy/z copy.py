import customtkinter as ctk
import keyboard
import tkinter as tk
import time
from PIL import ImageGrab, ImageDraw, ImageTk, Image
import pygetwindow as gw
import webbrowser
import mouse
import win32api
import win32con


class DualAreaSelector:
    """Full-screen overlay for selecting both Fish Box and Shake Box simultaneously"""

    def __init__(self, parent, screenshot, shake_area, fish_area, callback):
        self.callback = callback
        self.screenshot = screenshot
        self.freeze_enabled = screenshot is not None

        # Create fullscreen window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.configure(cursor='cross')

        # Get screen dimensions
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        # Create canvas
        self.canvas = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.pack()
        
        # Only display screenshot if freeze is enabled
        if self.freeze_enabled:
            self.photo = ImageTk.PhotoImage(screenshot)
            self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        else:
            # Make canvas transparent so user can see through to their actual screen
            self.canvas.configure(bg='black')
            # Make the window mostly transparent (only boxes will be visible)
            self.window.attributes('-alpha', 0.01)  # Almost fully transparent
            self.window.update()  # Force update
            # Now make canvas visible again for drawing boxes
            self.window.attributes('-alpha', 1.0)
            self.window.configure(bg='')
            # Use a transparent color for canvas
            try:
                self.window.wm_attributes('-transparentcolor', 'black')
            except:
                pass  # Some systems don't support this

        # Initialize box coordinates
        self.shake_x1, self.shake_y1 = shake_area["x"], shake_area["y"]
        self.shake_x2, self.shake_y2 = self.shake_x1 + shake_area["width"], self.shake_y1 + shake_area["height"]
        self.fish_x1, self.fish_y1 = fish_area["x"], fish_area["y"]
        self.fish_x2, self.fish_y2 = self.fish_x1 + fish_area["width"], self.fish_y1 + fish_area["height"]

        # Drawing state
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
        self.resize_threshold = 10

        # Create Shake Box (Red)
        self.shake_rect = self.canvas.create_rectangle(
            self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2,
            outline='#f44336', width=2, fill='#f44336', stipple='gray50'
        )
        shake_label_x = self.shake_x1 + (self.shake_x2 - self.shake_x1) // 2
        self.shake_label = self.canvas.create_text(
            shake_label_x, self.shake_y1 - 20, text="Shake Area",
            font=("Arial", 12, "bold"), fill='#f44336'
        )

        # Create Fish Box (Blue)
        self.fish_rect = self.canvas.create_rectangle(
            self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2,
            outline='#2196F3', width=2, fill='#2196F3', stipple='gray50'
        )
        fish_label_x = self.fish_x1 + (self.fish_x2 - self.fish_x1) // 2
        self.fish_label = self.canvas.create_text(
            fish_label_x, self.fish_y1 - 20, text="Fish Area",
            font=("Arial", 12, "bold"), fill='#2196F3'
        )

        # Corner handles
        self.fish_handles = []
        self.shake_handles = []
        self.create_all_handles()

        # Zoom window
        self.zoom_window_size = 150
        self.zoom_factor = 4
        self.zoom_rect = None
        self.zoom_image_id = None

        # Bind events (canvas only, not window)
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
        # Close on Escape key
        self.window.bind('<Escape>', lambda e: self.window.destroy())

    def create_all_handles(self):
        """Create corner handles for both boxes"""
        self.create_handles_for_box('fish')
        self.create_handles_for_box('shake')

    def create_handles_for_box(self, box_type):
        """Create corner handles for a specific box"""
        handle_size = 12
        corner_marker_size = 3

        if box_type == 'fish':
            x1, y1, x2, y2 = self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2
            color = '#2196F3'
            handles_list = self.fish_handles
        else:
            x1, y1, x2, y2 = self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2
            color = '#f44336'
            handles_list = self.shake_handles

        for handle in handles_list:
            self.canvas.delete(handle)
        handles_list.clear()

        corners = [(x1, y1, 'nw'), (x2, y1, 'ne'), (x1, y2, 'sw'), (x2, y2, 'se')]

        for x, y, corner in corners:
            # Outer handle
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='', outline=color, width=2
            )
            handles_list.append(handle)

            # Corner marker
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='red', outline='white', width=1
            )
            handles_list.append(corner_marker)

            # Crosshair
            line1 = self.canvas.create_line(x - handle_size, y, x + handle_size, y, fill='yellow', width=1)
            line2 = self.canvas.create_line(x, y - handle_size, x, y + handle_size, fill='yellow', width=1)
            handles_list.append(line1)
            handles_list.append(line2)

    def get_corner_at_position(self, x, y, box_type):
        """Determine which corner is near the cursor"""
        if box_type == 'fish':
            x1, y1, x2, y2 = self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2
        else:
            x1, y1, x2, y2 = self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2

        corners = {'nw': (x1, y1), 'ne': (x2, y1), 'sw': (x1, y2), 'se': (x2, y2)}
        
        for corner, (cx, cy) in corners.items():
            if abs(x - cx) < self.resize_threshold and abs(y - cy) < self.resize_threshold:
                return corner
        return None

    def is_inside_box(self, x, y, box_type):
        """Check if point is inside a specific box"""
        if box_type == 'fish':
            return self.fish_x1 < x < self.fish_x2 and self.fish_y1 < y < self.fish_y2
        else:
            return self.shake_x1 < x < self.shake_x2 and self.shake_y1 < y < self.shake_y2

    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        for box in ['fish', 'shake']:
            corner = self.get_corner_at_position(event.x, event.y, box)
            if corner:
                self.dragging = True
                self.active_box = box
                self.drag_corner = corner
                return

            if self.is_inside_box(event.x, event.y, box):
                self.dragging = True
                self.active_box = box
                self.drag_corner = 'move'
                return

    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging or not self.active_box:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        if self.active_box == 'fish':
            if self.drag_corner == 'move':
                self.fish_x1 += dx
                self.fish_y1 += dy
                self.fish_x2 += dx
                self.fish_y2 += dy
            elif self.drag_corner == 'nw':
                self.fish_x1, self.fish_y1 = event.x, event.y
            elif self.drag_corner == 'ne':
                self.fish_x2, self.fish_y1 = event.x, event.y
            elif self.drag_corner == 'sw':
                self.fish_x1, self.fish_y2 = event.x, event.y
            elif self.drag_corner == 'se':
                self.fish_x2, self.fish_y2 = event.x, event.y

            if self.fish_x1 > self.fish_x2:
                self.fish_x1, self.fish_x2 = self.fish_x2, self.fish_x1
            if self.fish_y1 > self.fish_y2:
                self.fish_y1, self.fish_y2 = self.fish_y2, self.fish_y1
        else:
            if self.drag_corner == 'move':
                self.shake_x1 += dx
                self.shake_y1 += dy
                self.shake_x2 += dx
                self.shake_y2 += dy
            elif self.drag_corner == 'nw':
                self.shake_x1, self.shake_y1 = event.x, event.y
            elif self.drag_corner == 'ne':
                self.shake_x2, self.shake_y1 = event.x, event.y
            elif self.drag_corner == 'sw':
                self.shake_x1, self.shake_y2 = event.x, event.y
            elif self.drag_corner == 'se':
                self.shake_x2, self.shake_y2 = event.x, event.y

            if self.shake_x1 > self.shake_x2:
                self.shake_x1, self.shake_x2 = self.shake_x2, self.shake_x1
            if self.shake_y1 > self.shake_y2:
                self.shake_y1, self.shake_y2 = self.shake_y2, self.shake_y1

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
        fish_corner = self.get_corner_at_position(event.x, event.y, 'fish')
        shake_corner = self.get_corner_at_position(event.x, event.y, 'shake')

        if fish_corner or shake_corner:
            corner = fish_corner or shake_corner
            cursors = {'nw': 'top_left_corner', 'ne': 'top_right_corner',
                      'sw': 'bottom_left_corner', 'se': 'bottom_right_corner'}
            self.window.configure(cursor=cursors.get(corner, 'cross'))
        elif self.is_inside_box(event.x, event.y, 'fish') or self.is_inside_box(event.x, event.y, 'shake'):
            self.window.configure(cursor='fleur')
        else:
            self.window.configure(cursor='cross')

        # Update zoom on every mouse move for both freeze and live modes
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

        # If freeze is enabled, use the frozen screenshot
        # If freeze is disabled, take a live screenshot for the zoom
        if self.freeze_enabled:
            cropped = self.screenshot.crop((x1_src, y1_src, x2_src, y2_src))
        else:
            # Take a live screenshot of just the area we need
            live_screenshot = ImageGrab.grab(bbox=(x1_src, y1_src, x2_src, y2_src))
            cropped = live_screenshot
        
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
            fill='black', outline='white', width=2
        )

        self.zoom_image_id = self.canvas.create_image(zoom_x, zoom_y, image=self.zoom_photo, anchor='nw')

    def update_boxes(self):
        """Update both boxes and their labels"""
        self.canvas.coords(self.shake_rect, self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2)
        self.canvas.coords(self.shake_label, self.shake_x1 + (self.shake_x2 - self.shake_x1) // 2, self.shake_y1 - 20)

        self.canvas.coords(self.fish_rect, self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2)
        self.canvas.coords(self.fish_label, self.fish_x1 + (self.fish_x2 - self.fish_x1) // 2, self.fish_y1 - 20)

        self.create_all_handles()


class SimpleApp:
    storage = {
        "config": {
            "hotkeys": {"start_stop": "F3", "change_scan": "F1", "exit": "F4", "freeze_while_toggled": True},
            "areas": {"shake": {"x": 530, "y": 235, "width": 1500, "height": 665},
                     "fish": {"x": 765, "y": 1217, "width": 1032, "height": 38}},
            "toggles": {"always_on_top": True, "auto_minimize": True, "auto_focus_roblox": True, "auto_zoom_in": True, "auto_select_rod": True},
            "hotbar": {"fishing_rod": "1", "equipment_bag": "2"},
            "auto_select_rod": {"delay1": "0.0", "delay2": "0.5", "delay3": "0.5"},
            "auto_zoom_in": {"delay1": "0.0", "zoom_in_amount": "12", "delay2": "0.25", "zoom_out_amount": "1", "delay3": "0.0"},
            "cast": {"method": "Perfect", "auto_look_down": True, "green_tolerance": 5, "white_tolerance": 5,
                     "delay1": "0.0", "delay2": "0.0", "delay3": "0.0", "delay4": "0.0", "delay5": "0.0"},
        },
    }

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("IRUS Idiotproof")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(int(screen_width * 0.8), 800)
        window_height = min(int(screen_height * 0.8), 600)

        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(500, 300)
        self.root.resizable(True, True)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Resolution scaling
        self.current_width = screen_width
        self.current_height = screen_height
        self.scale_x = self.current_width / 2560
        self.scale_y = self.current_height / 1440

        self._scale_default_areas()
        self.root.after(0, self._center_window)

        # Hotkey state
        self.hotkey_labels = {"start_stop": None, "change_scan": None, "exit": None}
        self.waiting_for_hotkey = False
        self.hotkey_waiting_for = None
        self.hotkey_listeners = {}
        self.freeze_while_toggled = self.storage["config"]["hotkeys"]["freeze_while_toggled"]

        # Hotbar state
        self.waiting_for_hotbar = False
        self.hotbar_waiting_for = None
        self.fishing_rod_hotbar = self.storage["config"]["hotbar"]["fishing_rod"]
        self.equipment_bag_hotbar = self.storage["config"]["hotbar"]["equipment_bag"]

        # Auto Select Rod delays
        self.auto_rod_delay1 = self.storage["config"]["auto_select_rod"]["delay1"]
        self.auto_rod_delay2 = self.storage["config"]["auto_select_rod"]["delay2"]
        self.auto_rod_delay3 = self.storage["config"]["auto_select_rod"]["delay3"]

        # Area selector state
        self.area_selector_active = False

        # Loop state
        self.is_running = False

        # Toggle states (load from centralized storage)
        self.always_on_top = self.storage["config"]["toggles"]["always_on_top"]
        self.auto_minimize = self.storage["config"]["toggles"]["auto_minimize"]
        self.auto_focus_roblox = self.storage["config"]["toggles"]["auto_focus_roblox"]
        self.auto_zoom_in = self.storage["config"]["toggles"]["auto_zoom_in"]
        self.auto_select_rod = self.storage["config"]["toggles"]["auto_select_rod"]

        # Auto Zoom In settings
        self.auto_zoom_in_delay1 = self.storage["config"]["auto_zoom_in"]["delay1"]
        self.auto_zoom_in_amount = self.storage["config"]["auto_zoom_in"]["zoom_in_amount"]
        self.auto_zoom_in_delay2 = self.storage["config"]["auto_zoom_in"]["delay2"]
        self.auto_zoom_out_amount = self.storage["config"]["auto_zoom_in"]["zoom_out_amount"]
        self.auto_zoom_in_delay3 = self.storage["config"]["auto_zoom_in"]["delay3"]

        # Cast settings
        self.auto_look_down = self.storage["config"]["cast"]["auto_look_down"]
        self.green_tolerance = self.storage["config"]["cast"]["green_tolerance"]
        self.white_tolerance = self.storage["config"]["cast"]["white_tolerance"]
        self.cast_delay1 = self.storage["config"]["cast"]["delay1"]
        self.cast_delay2 = self.storage["config"]["cast"]["delay2"]
        self.cast_delay3 = self.storage["config"]["cast"]["delay3"]
        self.cast_delay4 = self.storage["config"]["cast"]["delay4"]
        self.cast_delay5 = self.storage["config"]["cast"]["delay5"]

        # Setup hotkeys after window is fully created
        self.root.after(100, self._setup_global_hotkeys)
        self.root.bind("<Key>", self._on_key_press)
        self.create_widgets()
        
        # Apply always on top at startup if enabled
        if self.always_on_top:
            self.root.attributes('-topmost', True)
            self.root.bind('<FocusIn>', self._maintain_topmost)
            self.root.bind('<Visibility>', self._maintain_topmost)

    def _scale_default_areas(self):
        """Scale areas based on resolution"""
        fish_presets = {
            (1920, 1200): {"x": 573, "y": 1015, "width": 772, "height": 30},
            (1920, 1080): {"x": 573, "y": 909, "width": 773, "height": 30},
            (1680, 1050): {"x": 502, "y": 886, "width": 675, "height": 26},
            (1600, 1200): {"x": 477, "y": 1019, "width": 644, "height": 26},
            (1280, 1024): {"x": 382, "y": 869, "width": 515, "height": 20},
            (1280, 800): {"x": 382, "y": 672, "width": 514, "height": 19},
            (1280, 720): {"x": 382, "y": 602, "width": 514, "height": 19},
            (1024, 768): {"x": 304, "y": 647, "width": 414, "height": 17},
            (800, 600): {"x": 238, "y": 502, "width": 322, "height": 13},
            (2560, 1440): {"x": 765, "y": 1222, "width": 1030, "height": 34},
        }

        shake_presets = {(2560, 1440): {"x": 530, "y": 235, "width": 1500, "height": 665}}

        current_res = (self.current_width, self.current_height)

        # Fish area
        if current_res in fish_presets:
            scaled_fish = fish_presets[current_res]
        else:
            scaled_fish = {
                "x": round(0.299414 * self.current_width - 1.63),
                "y": round(0.858462 * self.current_height - 14.01),
                "width": round(0.401687 * self.current_width + 0.87),
                "height": round(0.024583 * self.current_height - 0.84),
            }

        # Shake area
        if current_res in shake_presets:
            scaled_shake = shake_presets[current_res]
        else:
            shake_default = {"x": 530, "y": 235, "width": 1500, "height": 665}
            scaled_shake = {
                "x": round(shake_default["x"] * self.scale_x),
                "y": round(shake_default["y"] * self.scale_y),
                "width": round(shake_default["width"] * self.scale_x),
                "height": round(shake_default["height"] * self.scale_y),
            }

        self.storage["config"]["areas"]["fish"] = scaled_fish
        self.storage["config"]["areas"]["shake"] = scaled_shake

    def _validate_delay_input(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        """Validate that input is a valid decimal number"""
        # Allow empty string
        if value_if_allowed == "":
            return True
        
        # Allow deletion
        if action == "0":  # deletion
            return True
        
        # Check if the result would be a valid number format
        try:
            # Allow just a decimal point or numbers with decimal
            if value_if_allowed == ".":
                return True
            # Allow numbers that start with decimal
            if value_if_allowed.startswith(".") and value_if_allowed[1:].replace(".", "").isdigit():
                return True
            # Check if it's a valid float format (allows multiple decimals during typing)
            if value_if_allowed.replace(".", "", 1).isdigit():
                return True
            return False
        except:
            return False

    def _save_delay_values(self, event=None):
        """Save delay values to storage"""
        try:
            value1 = self.auto_rod_delay1_entry.get()
            self.storage["config"]["auto_select_rod"]["delay1"] = value1 if value1 else "0.0"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value2 = self.auto_rod_delay2_entry.get()
            self.storage["config"]["auto_select_rod"]["delay2"] = value2 if value2 else "0.0"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value3 = self.auto_rod_delay3_entry.get()
            self.storage["config"]["auto_select_rod"]["delay3"] = value3 if value3 else "0.0"
        except (AttributeError, tk.TclError):
            pass

    def _save_zoom_values(self, event=None):
        """Save zoom values to storage"""
        try:
            value1 = self.auto_zoom_in_delay1_entry.get()
            self.storage["config"]["auto_zoom_in"]["delay1"] = value1 if value1 else "0.0"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value2 = self.auto_zoom_in_amount_entry.get()
            self.storage["config"]["auto_zoom_in"]["zoom_in_amount"] = value2 if value2 else "12"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value3 = self.auto_zoom_in_delay2_entry.get()
            self.storage["config"]["auto_zoom_in"]["delay2"] = value3 if value3 else "0.0"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value4 = self.auto_zoom_out_amount_entry.get()
            self.storage["config"]["auto_zoom_in"]["zoom_out_amount"] = value4 if value4 else "1"
        except (AttributeError, tk.TclError):
            pass
        
        try:
            value5 = self.auto_zoom_in_delay3_entry.get()
            self.storage["config"]["auto_zoom_in"]["delay3"] = value5 if value5 else "0.0"
        except (AttributeError, tk.TclError):
            pass

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create the main GUI"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(4, weight=1)  # Make column 4 expand to fill space

        # Title
        title_label = ctk.CTkLabel(main_frame, text="IRUS Idiotproof - made for the disabled", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, pady=15, sticky="w", padx=10)

        # YouTube button
        youtube_btn = ctk.CTkButton(main_frame, text="Youtube", width=100,
                                    command=lambda: webbrowser.open("https://www.youtube.com/@AsphaltCake/?sub_confirmation=1"))
        youtube_btn.grid(row=0, column=1, pady=15, padx=5, sticky="w")

        # Discord button
        discord_btn = ctk.CTkButton(main_frame, text="Discord", width=100,
                                   command=lambda: webbrowser.open("https://discord.gg/vKVBbyfHTD"))
        discord_btn.grid(row=0, column=2, pady=15, padx=5, sticky="w")

        # PayPal button
        paypal_btn = ctk.CTkButton(main_frame, text="Paypal", width=100,
                                  command=lambda: webbrowser.open("https://www.paypal.com/paypalme/JLim862"))
        paypal_btn.grid(row=0, column=3, pady=15, padx=5, sticky="w")

        # Tabs
        self.tabview = ctk.CTkTabview(main_frame, anchor="w")
        self.tabview.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        self.tabview.add("Basic")
        self.tabview.add("Misc")
        self.tabview.add("Cast")
        self.tabview.add("Shake")
        self.tabview.add("Fish")

        self._create_basic_tab()
        self._create_misc_tab()
        self._create_cast_tab()

    def _create_basic_tab(self):
        """Create the Basic tab with hotkey settings"""
        parent = self.tabview.tab("Basic")
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_frame.grid_columnconfigure(3, weight=1)  # Make column 3 expand to fill space

        row = 0  # Dynamic row counter
        
        # Hotkey Settings Section
        hotkeys_label = ctk.CTkLabel(scroll_frame, text="Hotkey Settings", 
                                     font=ctk.CTkFont(size=14, weight="bold"))
        hotkeys_label.grid(row=row, column=0, columnspan=4, sticky="w", padx=10, pady=(10, 5))
        row += 1

        hotkeys = self.storage["config"]["hotkeys"]

        # Start/Stop hotkey
        label = ctk.CTkLabel(scroll_frame, text="Start/Stop:", font=ctk.CTkFont(size=12))
        label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.hotkey_labels["start_stop"] = ctk.CTkLabel(
            scroll_frame, text=hotkeys["start_stop"],
            font=ctk.CTkFont(size=12, weight="bold"), text_color="green"
        )
        self.hotkey_labels["start_stop"].grid(row=row, column=1, sticky="w", padx=10, pady=8)
        btn = ctk.CTkButton(scroll_frame, text="Rebind Hotkey", command=lambda: self._start_rebind("start_stop"), width=120)
        btn.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        row += 1

        # Change Scan Area hotkey
        label = ctk.CTkLabel(scroll_frame, text="Change Scan Area:", font=ctk.CTkFont(size=12))
        label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.hotkey_labels["change_scan"] = ctk.CTkLabel(
            scroll_frame, text=hotkeys["change_scan"],
            font=ctk.CTkFont(size=12, weight="bold"), text_color="green"
        )
        self.hotkey_labels["change_scan"].grid(row=row, column=1, sticky="w", padx=10, pady=8)
        btn = ctk.CTkButton(scroll_frame, text="Rebind Hotkey", command=lambda: self._start_rebind("change_scan"), width=120)
        btn.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        row += 1

        # Freeze While Toggled
        freeze_toggle_label = ctk.CTkLabel(scroll_frame, text="Freeze While Toggled:", font=ctk.CTkFont(size=12))
        freeze_toggle_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.freeze_while_toggled_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.freeze_while_toggled else "OFF", width=100,
            command=self._toggle_freeze_while_toggled,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.freeze_while_toggled:
            self.freeze_while_toggled_switch.select()
        else:
            self.freeze_while_toggled_switch.deselect()
        self.freeze_while_toggled_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        row += 1

        # Exit hotkey
        label = ctk.CTkLabel(scroll_frame, text="Exit:", font=ctk.CTkFont(size=12))
        label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        self.hotkey_labels["exit"] = ctk.CTkLabel(
            scroll_frame, text=hotkeys["exit"],
            font=ctk.CTkFont(size=12, weight="bold"), text_color="green"
        )
        self.hotkey_labels["exit"].grid(row=row, column=1, sticky="w", padx=10, pady=8)
        btn = ctk.CTkButton(scroll_frame, text="Rebind Hotkey", command=lambda: self._start_rebind("exit"), width=120)
        btn.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        row += 1

        # Separator (spans full width)
        separator1 = ctk.CTkFrame(scroll_frame, height=2, fg_color="gray30")
        separator1.grid(row=row, column=0, columnspan=4, sticky="ew", padx=0, pady=15)
        row += 1

        # Hotbar Settings Section
        hotbar_label = ctk.CTkLabel(scroll_frame, text="Hotbar Settings", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        hotbar_label.grid(row=row, column=0, columnspan=4, sticky="w", padx=10, pady=(5, 5))
        row += 1

        # Fishing Rod hotbar
        fishing_rod_label = ctk.CTkLabel(scroll_frame, text="Fishing Rod:", font=ctk.CTkFont(size=12))
        fishing_rod_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.fishing_rod_value = ctk.CTkLabel(
            scroll_frame, text=self.fishing_rod_hotbar,
            font=ctk.CTkFont(size=12, weight="bold"), text_color="green"
        )
        self.fishing_rod_value.grid(row=row, column=1, sticky="w", padx=10, pady=8)

        fishing_rod_btn = ctk.CTkButton(scroll_frame, text="Rebind Hotbar", command=lambda: self._start_rebind_hotbar("fishing_rod"), width=120)
        fishing_rod_btn.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        row += 1

        # Equipment Bag hotbar
        equipment_bag_label = ctk.CTkLabel(scroll_frame, text="Equipment Bag:", font=ctk.CTkFont(size=12))
        equipment_bag_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.equipment_bag_value = ctk.CTkLabel(
            scroll_frame, text=self.equipment_bag_hotbar,
            font=ctk.CTkFont(size=12, weight="bold"), text_color="green"
        )
        self.equipment_bag_value.grid(row=row, column=1, sticky="w", padx=10, pady=8)

        equipment_bag_btn = ctk.CTkButton(scroll_frame, text="Rebind Hotbar", command=lambda: self._start_rebind_hotbar("equipment_bag"), width=120)
        equipment_bag_btn.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        row += 1

        # Separator (spans full width)
        separator2 = ctk.CTkFrame(scroll_frame, height=2, fg_color="gray30")
        separator2.grid(row=row, column=0, columnspan=4, sticky="ew", padx=0, pady=15)
        row += 1

        # Options Section
        options_label = ctk.CTkLabel(scroll_frame, text="Options", 
                                     font=ctk.CTkFont(size=14, weight="bold"))
        options_label.grid(row=row, column=0, columnspan=4, sticky="w", padx=10, pady=(5, 5))
        row += 1

        # Always On Top
        always_on_top_label = ctk.CTkLabel(scroll_frame, text="Always On Top:", font=ctk.CTkFont(size=12))
        always_on_top_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.always_on_top_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.always_on_top else "OFF", width=100,
            command=self._toggle_always_on_top,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.always_on_top:
            self.always_on_top_switch.select()
        else:
            self.always_on_top_switch.deselect()
        self.always_on_top_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        row += 1

        # Auto Minimize
        auto_minimize_label = ctk.CTkLabel(scroll_frame, text="Auto Minimize:", font=ctk.CTkFont(size=12))
        auto_minimize_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.auto_minimize_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.auto_minimize else "OFF", width=100,
            command=self._toggle_auto_minimize,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.auto_minimize:
            self.auto_minimize_switch.select()
        else:
            self.auto_minimize_switch.deselect()
        self.auto_minimize_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)
        row += 1

        # Auto Focus Roblox
        auto_focus_label = ctk.CTkLabel(scroll_frame, text="Auto Focus Roblox:", font=ctk.CTkFont(size=12))
        auto_focus_label.grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        self.auto_focus_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.auto_focus_roblox else "OFF", width=100,
            command=self._toggle_auto_focus_roblox,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.auto_focus_roblox:
            self.auto_focus_switch.select()
        else:
            self.auto_focus_switch.deselect()
        self.auto_focus_switch.grid(row=row, column=1, sticky="w", padx=10, pady=8)


    def _create_misc_tab(self):
        """Create the Misc tab with settings"""
        parent = self.tabview.tab("Misc")
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_frame.grid_columnconfigure(1, weight=1)
        scroll_frame.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # Misc Settings Section
        misc_label = ctk.CTkLabel(scroll_frame, text="Misc Settings", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        misc_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        misc_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # Auto Zoom In
        auto_zoom_in_label = ctk.CTkLabel(scroll_frame, text="Auto Zoom In:", font=ctk.CTkFont(size=12))
        auto_zoom_in_label.grid(row=1, column=0, sticky="w", padx=10, pady=8)
        auto_zoom_in_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_in_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.auto_zoom_in else "OFF", width=100,
            command=self._toggle_auto_zoom_in,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.auto_zoom_in:
            self.auto_zoom_in_switch.select()
        else:
            self.auto_zoom_in_switch.deselect()
        self.auto_zoom_in_switch.grid(row=1, column=1, sticky="w", padx=10, pady=8)

        # Auto Zoom In Options Frame (collapsible section)
        self.auto_zoom_in_frame = ctk.CTkFrame(scroll_frame, fg_color="gray25")
        self.auto_zoom_in_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 10))
        # Bind click on frame to unfocus entries
        self.auto_zoom_in_frame.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        # Hide frame if toggle is off
        if not self.auto_zoom_in:
            self.auto_zoom_in_frame.grid_remove()

        # Register validation command with all parameters
        vcmd = (self.root.register(self._validate_delay_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # AutoZoomDelay1
        auto_zoom_delay1_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay1_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        auto_zoom_delay1_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_in_delay1_entry = ctk.CTkEntry(
            self.auto_zoom_in_frame,
            width=60,
            justify="center"
        )
        self.auto_zoom_in_delay1_entry.grid(row=0, column=1, padx=(10, 5), pady=(15, 5), sticky="w")
        self.auto_zoom_in_delay1_entry.insert(0, self.auto_zoom_in_delay1)
        self.auto_zoom_in_delay1_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_zoom_in_delay1_entry.bind("<Return>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        auto_zoom_delay1_s_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay1_s_label.grid(row=0, column=2, padx=(0, 20), pady=(15, 5), sticky="w")
        auto_zoom_delay1_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # Zoom In Amount
        zoom_in_amount_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="Zoom In Amount:",
            font=ctk.CTkFont(size=12)
        )
        zoom_in_amount_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        zoom_in_amount_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_in_amount_entry = ctk.CTkEntry(
            self.auto_zoom_in_frame,
            width=60,
            justify="center"
        )
        self.auto_zoom_in_amount_entry.grid(row=1, column=1, padx=(10, 20), pady=5, sticky="w")
        self.auto_zoom_in_amount_entry.insert(0, self.auto_zoom_in_amount)
        self.auto_zoom_in_amount_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_zoom_in_amount_entry.bind("<Return>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # AutoZoomDelay2
        auto_zoom_delay2_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay2_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        auto_zoom_delay2_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_in_delay2_entry = ctk.CTkEntry(
            self.auto_zoom_in_frame,
            width=60,
            justify="center"
        )
        self.auto_zoom_in_delay2_entry.grid(row=2, column=1, padx=(10, 5), pady=5, sticky="w")
        self.auto_zoom_in_delay2_entry.insert(0, self.auto_zoom_in_delay2)
        self.auto_zoom_in_delay2_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_zoom_in_delay2_entry.bind("<Return>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        auto_zoom_delay2_s_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay2_s_label.grid(row=2, column=2, padx=(0, 20), pady=5, sticky="w")
        auto_zoom_delay2_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # Zoom Out Amount
        zoom_out_amount_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="Zoom Out Amount:",
            font=ctk.CTkFont(size=12)
        )
        zoom_out_amount_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        zoom_out_amount_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_out_amount_entry = ctk.CTkEntry(
            self.auto_zoom_in_frame,
            width=60,
            justify="center"
        )
        self.auto_zoom_out_amount_entry.grid(row=3, column=1, padx=(10, 20), pady=5, sticky="w")
        self.auto_zoom_out_amount_entry.insert(0, self.auto_zoom_out_amount)
        self.auto_zoom_out_amount_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_zoom_out_amount_entry.bind("<Return>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # AutoZoomDelay3
        auto_zoom_delay3_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay3_label.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="w")
        auto_zoom_delay3_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_zoom_in_delay3_entry = ctk.CTkEntry(
            self.auto_zoom_in_frame,
            width=60,
            justify="center"
        )
        self.auto_zoom_in_delay3_entry.grid(row=4, column=1, padx=(10, 5), pady=(5, 15), sticky="w")
        self.auto_zoom_in_delay3_entry.insert(0, self.auto_zoom_in_delay3)
        self.auto_zoom_in_delay3_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_zoom_in_delay3_entry.bind("<Return>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        auto_zoom_delay3_s_label = ctk.CTkLabel(
            self.auto_zoom_in_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_zoom_delay3_s_label.grid(row=4, column=2, padx=(0, 20), pady=(5, 15), sticky="w")
        auto_zoom_delay3_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))

        # Auto Select Rod
        auto_select_rod_label = ctk.CTkLabel(scroll_frame, text="Auto Select Rod:", font=ctk.CTkFont(size=12))
        auto_select_rod_label.grid(row=3, column=0, sticky="w", padx=10, pady=8)
        auto_select_rod_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        self.auto_select_rod_switch = ctk.CTkSwitch(
            scroll_frame, text="ON" if self.auto_select_rod else "OFF", width=100,
            command=self._toggle_auto_select_rod,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.auto_select_rod:
            self.auto_select_rod_switch.select()
        else:
            self.auto_select_rod_switch.deselect()
        self.auto_select_rod_switch.grid(row=3, column=1, sticky="w", padx=10, pady=8)

        # Auto Select Rod Options Frame (collapsible section)
        self.auto_select_rod_frame = ctk.CTkFrame(scroll_frame, fg_color="gray25")
        self.auto_select_rod_frame.grid(row=4, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 10))
        # Bind click on frame to unfocus entries
        self.auto_select_rod_frame.bind("<Button-1>", lambda e: (self._save_delay_values(), self._save_zoom_values(), self.root.focus()))
        
        # Hide frame if toggle is off
        if not self.auto_select_rod:
            self.auto_select_rod_frame.grid_remove()

        # Register validation command with all parameters
        vcmd = (self.root.register(self._validate_delay_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # AutoRodDelay1
        auto_rod_delay1_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay1_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        auto_rod_delay1_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        self.auto_rod_delay1_entry = ctk.CTkEntry(
            self.auto_select_rod_frame,
            width=60,
            justify="center"
        )
        self.auto_rod_delay1_entry.grid(row=0, column=1, padx=(10, 5), pady=(15, 5), sticky="w")
        self.auto_rod_delay1_entry.insert(0, self.auto_rod_delay1)
        self.auto_rod_delay1_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_rod_delay1_entry.bind("<Return>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        auto_rod_delay1_s_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay1_s_label.grid(row=0, column=2, padx=(0, 20), pady=(15, 5), sticky="w")
        auto_rod_delay1_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))

        # AutoRodEquipmentBag
        auto_rod_equipment_bag_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="Equipment Bag:",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_equipment_bag_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        auto_rod_equipment_bag_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        self.auto_rod_equipment_bag_entry = ctk.CTkEntry(
            self.auto_select_rod_frame,
            width=60,
            state="disabled",
            justify="center"
        )
        self.auto_rod_equipment_bag_entry.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="w")
        self.auto_rod_equipment_bag_entry.configure(state="normal")
        self.auto_rod_equipment_bag_entry.insert(0, self.equipment_bag_hotbar)
        self.auto_rod_equipment_bag_entry.configure(state="disabled")

        # AutoRodDelay2
        auto_rod_delay2_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay2_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        auto_rod_delay2_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        self.auto_rod_delay2_entry = ctk.CTkEntry(
            self.auto_select_rod_frame,
            width=60,
            justify="center"
        )
        self.auto_rod_delay2_entry.grid(row=2, column=1, padx=(10, 5), pady=5, sticky="w")
        self.auto_rod_delay2_entry.insert(0, self.auto_rod_delay2)
        self.auto_rod_delay2_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_rod_delay2_entry.bind("<Return>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        auto_rod_delay2_s_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay2_s_label.grid(row=2, column=2, padx=(0, 20), pady=5, sticky="w")
        auto_rod_delay2_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))

        # AutoRodFishingRod
        auto_rod_fishing_rod_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="Fishing Rod:",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_fishing_rod_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        auto_rod_fishing_rod_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        self.auto_rod_fishing_rod_entry = ctk.CTkEntry(
            self.auto_select_rod_frame,
            width=60,
            state="disabled",
            justify="center"
        )
        self.auto_rod_fishing_rod_entry.grid(row=3, column=1, padx=(10, 5), pady=5, sticky="w")
        self.auto_rod_fishing_rod_entry.configure(state="normal")
        self.auto_rod_fishing_rod_entry.insert(0, self.fishing_rod_hotbar)
        self.auto_rod_fishing_rod_entry.configure(state="disabled")

        # AutoRodDelay3
        auto_rod_delay3_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="Delay:",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay3_label.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="w")
        auto_rod_delay3_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        self.auto_rod_delay3_entry = ctk.CTkEntry(
            self.auto_select_rod_frame,
            width=60,
            justify="center"
        )
        self.auto_rod_delay3_entry.grid(row=4, column=1, padx=(10, 5), pady=(5, 15), sticky="w")
        self.auto_rod_delay3_entry.insert(0, self.auto_rod_delay3)
        self.auto_rod_delay3_entry.configure(validate="key", validatecommand=vcmd)
        self.auto_rod_delay3_entry.bind("<Return>", lambda e: (self._save_delay_values(), self.root.focus()))
        
        auto_rod_delay3_s_label = ctk.CTkLabel(
            self.auto_select_rod_frame,
            text="s",
            font=ctk.CTkFont(size=12)
        )
        auto_rod_delay3_s_label.grid(row=4, column=2, padx=(0, 20), pady=(5, 15), sticky="w")
        auto_rod_delay3_s_label.bind("<Button-1>", lambda e: (self._save_delay_values(), self.root.focus()))

    def _create_cast_tab(self):
        """Create the Cast tab with cast method settings"""
        parent = self.tabview.tab("Cast")
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_frame.grid_columnconfigure(1, weight=1)

        # Cast Settings Section
        cast_label = ctk.CTkLabel(scroll_frame, text="Cast Settings", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        cast_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        # Cast Method
        cast_method_label = ctk.CTkLabel(scroll_frame, text="Cast Method:", font=ctk.CTkFont(size=12))
        cast_method_label.grid(row=1, column=0, sticky="w", padx=10, pady=8)
        
        self.cast_method_var = tk.StringVar(value=self.storage["config"]["cast"]["method"])
        cast_method_menu = ctk.CTkOptionMenu(
            scroll_frame,
            variable=self.cast_method_var,
            values=["Disabled", "Normal", "Perfect"],
            width=150,
            command=self._on_cast_method_change
        )
        cast_method_menu.grid(row=1, column=1, sticky="w", padx=10, pady=8)

        # Perfect Cast Section (initially visible if Perfect is selected)
        self.perfect_cast_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.perfect_cast_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        # Perfect Cast Settings Label
        perfect_label = ctk.CTkLabel(self.perfect_cast_frame, text="Perfect Cast Settings", 
                                     font=ctk.CTkFont(size=13, weight="bold"))
        perfect_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=0, pady=(5, 10))
        
        # Green Color Tolerance Slider
        green_tolerance_label = ctk.CTkLabel(self.perfect_cast_frame, text="Green Color Tolerance:", font=ctk.CTkFont(size=12))
        green_tolerance_label.grid(row=1, column=0, sticky="w", padx=0, pady=8)

        # Create a frame to hold value and slider together
        green_controls_frame = ctk.CTkFrame(self.perfect_cast_frame, fg_color="transparent")
        green_controls_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=8)

        self.green_tolerance_value_label = ctk.CTkLabel(green_controls_frame, text=f"{self.green_tolerance}",
                                                        font=ctk.CTkFont(size=12))
        self.green_tolerance_value_label.pack(side="left", padx=(0, 5))

        self.green_tolerance_slider = ctk.CTkSlider(
            green_controls_frame,
            from_=0,
            to=20,
            number_of_steps=20,
            width=200,
            command=self._on_green_tolerance_change
        )
        self.green_tolerance_slider.set(self.green_tolerance)
        self.green_tolerance_slider.pack(side="left")
        
        # White Color Tolerance Slider
        white_tolerance_label = ctk.CTkLabel(self.perfect_cast_frame, text="White Color Tolerance:", font=ctk.CTkFont(size=12))
        white_tolerance_label.grid(row=2, column=0, sticky="w", padx=0, pady=8)

        # Create a frame to hold value and slider together
        white_controls_frame = ctk.CTkFrame(self.perfect_cast_frame, fg_color="transparent")
        white_controls_frame.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=8)

        self.white_tolerance_value_label = ctk.CTkLabel(white_controls_frame, text=f"{self.white_tolerance}",
                                                        font=ctk.CTkFont(size=12))
        self.white_tolerance_value_label.pack(side="left", padx=(0, 5))

        self.white_tolerance_slider = ctk.CTkSlider(
            white_controls_frame,
            from_=0,
            to=20,
            number_of_steps=20,
            width=200,
            command=self._on_white_tolerance_change
        )
        self.white_tolerance_slider.set(self.white_tolerance)
        self.white_tolerance_slider.pack(side="left")
        
        # Auto Look Down checkbox
        auto_look_down_label = ctk.CTkLabel(self.perfect_cast_frame, text="Auto Look Down:", font=ctk.CTkFont(size=12))
        auto_look_down_label.grid(row=3, column=0, sticky="w", padx=0, pady=8)
        
        self.auto_look_down_switch = ctk.CTkSwitch(
            self.perfect_cast_frame, text="ON" if self.auto_look_down else "OFF", width=100,
            command=self._toggle_auto_look_down,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        if self.auto_look_down:
            self.auto_look_down_switch.select()
        else:
            self.auto_look_down_switch.deselect()
        self.auto_look_down_switch.grid(row=3, column=1, sticky="w", padx=10, pady=8)
        
        # Perfect Cast Flow Frame (collapsible section)
        self.perfect_cast_flow_frame = ctk.CTkFrame(self.perfect_cast_frame, fg_color="gray25")
        self.perfect_cast_flow_frame.grid(row=4, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 10))
        self.perfect_cast_flow_frame.bind("<Button-1>", lambda e: (self._save_cast_delay_values(), self.root.focus()))
        
        # Create the single unified flow
        self._create_perfect_cast_flow()
        
        # Update visibility based on initial value
        self._update_perfect_cast_visibility()

    def _on_cast_method_change(self, value):
        """Save cast method to storage when changed"""
        self.storage["config"]["cast"]["method"] = value
        self._update_perfect_cast_visibility()
    
    def _update_perfect_cast_visibility(self):
        """Show or hide the Perfect Cast settings based on cast method"""
        if self.cast_method_var.get() == "Perfect":
            self.perfect_cast_frame.grid()
        else:
            self.perfect_cast_frame.grid_remove()
    
    def _on_green_tolerance_change(self, value):
        """Update green tolerance when slider changes"""
        tolerance = int(value)
        self.green_tolerance = tolerance
        self.storage["config"]["cast"]["green_tolerance"] = tolerance
        self.green_tolerance_value_label.configure(text=f"{tolerance}")
    
    def _on_white_tolerance_change(self, value):
        """Update white tolerance when slider changes"""
        tolerance = int(value)
        self.white_tolerance = tolerance
        self.storage["config"]["cast"]["white_tolerance"] = tolerance
        self.white_tolerance_value_label.configure(text=f"{tolerance}")
    
    def _toggle_auto_look_down(self):
        """Toggle Auto Look Down and save to storage"""
        self.auto_look_down = not self.auto_look_down
        self.storage["config"]["cast"]["auto_look_down"] = self.auto_look_down
        self.auto_look_down_switch.configure(text="ON" if self.auto_look_down else "OFF")
    
    def _create_perfect_cast_flow(self):
        """Create single unified flow for Perfect Cast"""
        vcmd = (self.root.register(self._validate_delay_input), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        row = 0
        
        # Delay 1
        delay1_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Delay:", font=ctk.CTkFont(size=12))
        delay1_label.grid(row=row, column=0, padx=20, pady=(15, 5), sticky="w")
        delay1_label.bind("<Button-1>", lambda e: self.root.focus())
        
        self.cast_delay1_var = tk.StringVar(value=self.cast_delay1)
        self.cast_delay1_var.trace_add("write", lambda *args: self._on_cast_delay1_change())
        self.cast_delay1_entry = ctk.CTkEntry(self.perfect_cast_flow_frame, width=60, justify="center", textvariable=self.cast_delay1_var)
        self.cast_delay1_entry.grid(row=row, column=1, padx=(10, 5), pady=(15, 5), sticky="w")
        self.cast_delay1_entry.configure(validate="key", validatecommand=vcmd)
        self.cast_delay1_entry.bind("<Return>", lambda e: self.root.focus())
        
        delay1_s_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="s", font=ctk.CTkFont(size=12))
        delay1_s_label.grid(row=row, column=2, padx=(0, 20), pady=(15, 5), sticky="w")
        delay1_s_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Auto Look Down (if enabled)
        look_down_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Auto Look Down (if enabled)", font=ctk.CTkFont(size=12))
        look_down_label.grid(row=row, column=0, columnspan=3, padx=20, pady=5, sticky="w")
        look_down_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Delay 2
        delay2_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Delay:", font=ctk.CTkFont(size=12))
        delay2_label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
        delay2_label.bind("<Button-1>", lambda e: self.root.focus())
        
        self.cast_delay2_var = tk.StringVar(value=self.cast_delay2)
        self.cast_delay2_var.trace_add("write", lambda *args: self._on_cast_delay2_change())
        self.cast_delay2_entry = ctk.CTkEntry(self.perfect_cast_flow_frame, width=60, justify="center", textvariable=self.cast_delay2_var)
        self.cast_delay2_entry.grid(row=row, column=1, padx=(10, 5), pady=5, sticky="w")
        self.cast_delay2_entry.configure(validate="key", validatecommand=vcmd)
        self.cast_delay2_entry.bind("<Return>", lambda e: self.root.focus())
        
        delay2_s_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="s", font=ctk.CTkFont(size=12))
        delay2_s_label.grid(row=row, column=2, padx=(0, 20), pady=5, sticky="w")
        delay2_s_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Hold Left Click
        hold_click_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Hold Left Click", font=ctk.CTkFont(size=12))
        hold_click_label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
        hold_click_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Delay 3
        delay3_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Delay:", font=ctk.CTkFont(size=12))
        delay3_label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
        delay3_label.bind("<Button-1>", lambda e: self.root.focus())
        
        self.cast_delay3_var = tk.StringVar(value=self.cast_delay3)
        self.cast_delay3_var.trace_add("write", lambda *args: self._on_cast_delay3_change())
        self.cast_delay3_entry = ctk.CTkEntry(self.perfect_cast_flow_frame, width=60, justify="center", textvariable=self.cast_delay3_var)
        self.cast_delay3_entry.grid(row=row, column=1, padx=(10, 5), pady=5, sticky="w")
        self.cast_delay3_entry.configure(validate="key", validatecommand=vcmd)
        self.cast_delay3_entry.bind("<Return>", lambda e: self.root.focus())
        
        delay3_s_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="s", font=ctk.CTkFont(size=12))
        delay3_s_label.grid(row=row, column=2, padx=(0, 20), pady=5, sticky="w")
        delay3_s_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Perfect Cast Release
        release_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Perfect Cast Release", font=ctk.CTkFont(size=12))
        release_label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
        release_label.bind("<Button-1>", lambda e: self.root.focus())
        row += 1
        
        # Delay 4
        delay4_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="Delay:", font=ctk.CTkFont(size=12))
        delay4_label.grid(row=row, column=0, padx=20, pady=(5, 15), sticky="w")
        delay4_label.bind("<Button-1>", lambda e: self.root.focus())
        
        self.cast_delay4_var = tk.StringVar(value=self.cast_delay4)
        self.cast_delay4_var.trace_add("write", lambda *args: self._on_cast_delay4_change())
        self.cast_delay4_entry = ctk.CTkEntry(self.perfect_cast_flow_frame, width=60, justify="center", textvariable=self.cast_delay4_var)
        self.cast_delay4_entry.grid(row=row, column=1, padx=(10, 5), pady=(5, 15), sticky="w")
        self.cast_delay4_entry.configure(validate="key", validatecommand=vcmd)
        self.cast_delay4_entry.bind("<Return>", lambda e: self.root.focus())
        
        delay4_s_label = ctk.CTkLabel(self.perfect_cast_flow_frame, text="s", font=ctk.CTkFont(size=12))
        delay4_s_label.grid(row=row, column=2, padx=(0, 20), pady=(5, 15), sticky="w")
        delay4_s_label.bind("<Button-1>", lambda e: self.root.focus())
    
    def _on_cast_delay1_change(self):
        """Save delay1 immediately when changed"""
        value = self.cast_delay1_var.get()
        self.storage["config"]["cast"]["delay1"] = value if value else "0.0"
        self.cast_delay1 = value if value else "0.0"
    
    def _on_cast_delay2_change(self):
        """Save delay2 immediately when changed"""
        value = self.cast_delay2_var.get()
        self.storage["config"]["cast"]["delay2"] = value if value else "0.0"
        self.cast_delay2 = value if value else "0.0"
    
    def _on_cast_delay3_change(self):
        """Save delay3 immediately when changed"""
        value = self.cast_delay3_var.get()
        self.storage["config"]["cast"]["delay3"] = value if value else "0.0"
        self.cast_delay3 = value if value else "0.0"
    
    def _on_cast_delay4_change(self):
        """Save delay4 immediately when changed"""
        value = self.cast_delay4_var.get()
        self.storage["config"]["cast"]["delay4"] = value if value else "0.0"
        self.cast_delay4 = value if value else "0.0"
    
    def _save_cast_delay_values(self):
        """Save cast delay values from entries to storage"""
        try:
            value1 = self.cast_delay1_entry.get()
            self.storage["config"]["cast"]["delay1"] = value1 if value1 else "0.0"
            self.cast_delay1 = value1 if value1 else "0.0"
        except:
            pass
        
        try:
            value2 = self.cast_delay2_entry.get()
            self.storage["config"]["cast"]["delay2"] = value2 if value2 else "0.0"
            self.cast_delay2 = value2 if value2 else "0.0"
        except:
            pass
        
        try:
            value3 = self.cast_delay3_entry.get()
            self.storage["config"]["cast"]["delay3"] = value3 if value3 else "0.0"
            self.cast_delay3 = value3 if value3 else "0.0"
        except:
            pass
        
        try:
            value4 = self.cast_delay4_entry.get()
            self.storage["config"]["cast"]["delay4"] = value4 if value4 else "0.0"
            self.cast_delay4 = value4 if value4 else "0.0"
        except:
            pass

    def _start_rebind(self, hotkey_name):
        """Start hotkey rebinding"""
        if self.waiting_for_hotkey:
            return
        self.waiting_for_hotkey = True
        self.hotkey_waiting_for = hotkey_name
        self.hotkey_labels[hotkey_name].configure(text="PRESS A KEY")
        
        # Temporarily disable all global hotkeys to prevent conflicts during rebinding
        try:
            keyboard.unhook_all()
        except:
            pass

    def _start_rebind_hotbar(self, hotbar_name):
        """Start hotbar rebinding"""
        if self.waiting_for_hotbar:
            return
        self.waiting_for_hotbar = True
        self.hotbar_waiting_for = hotbar_name
        
        if hotbar_name == "fishing_rod":
            self.fishing_rod_value.configure(text="PRESS A KEY")
        elif hotbar_name == "equipment_bag":
            self.equipment_bag_value.configure(text="PRESS A KEY")

    def _get_auto_rod_delay1(self):
        """Get the first auto rod delay value"""
        try:
            value = self.auto_rod_delay1_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_select_rod"]["delay1"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _get_auto_rod_delay2(self):
        """Get the second auto rod delay value"""
        try:
            value = self.auto_rod_delay2_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_select_rod"]["delay2"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _get_auto_rod_delay3(self):
        """Get the third auto rod delay value"""
        try:
            value = self.auto_rod_delay3_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_select_rod"]["delay3"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _get_auto_zoom_delay1(self):
        """Get the first auto zoom delay value"""
        try:
            value = self.auto_zoom_in_delay1_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_zoom_in"]["delay1"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _get_auto_zoom_in_amount(self):
        """Get the zoom in amount value"""
        try:
            value = self.auto_zoom_in_amount_entry.get()
            amount = int(value) if value else 12
            self.storage["config"]["auto_zoom_in"]["zoom_in_amount"] = value
            return amount
        except (ValueError, AttributeError):
            return 12

    def _get_auto_zoom_delay2(self):
        """Get the second auto zoom delay value"""
        try:
            value = self.auto_zoom_in_delay2_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_zoom_in"]["delay2"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _get_auto_zoom_out_amount(self):
        """Get the zoom out amount value"""
        try:
            value = self.auto_zoom_out_amount_entry.get()
            amount = int(value) if value else 1
            self.storage["config"]["auto_zoom_in"]["zoom_out_amount"] = value
            return amount
        except (ValueError, AttributeError):
            return 1

    def _get_auto_zoom_delay3(self):
        """Get the third auto zoom delay value"""
        try:
            value = self.auto_zoom_in_delay3_entry.get()
            delay = float(value) if value else 0.0
            self.storage["config"]["auto_zoom_in"]["delay3"] = value
            return delay
        except (ValueError, AttributeError):
            return 0.0

    def _toggle_freeze_while_toggled(self):
        """Toggle freeze while toggled"""
        self.freeze_while_toggled = not self.freeze_while_toggled
        self.storage["config"]["hotkeys"]["freeze_while_toggled"] = self.freeze_while_toggled
        if self.freeze_while_toggled:
            self.freeze_while_toggled_switch.configure(text="ON")
        else:
            self.freeze_while_toggled_switch.configure(text="OFF")

    def _toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top = not self.always_on_top
        self.storage["config"]["toggles"]["always_on_top"] = self.always_on_top
        if self.always_on_top:
            self.always_on_top_switch.configure(text="ON")
            # Enable always on top
            self.root.attributes('-topmost', True)
            # Bind events to maintain topmost status
            self.root.bind('<FocusIn>', self._maintain_topmost)
            self.root.bind('<Visibility>', self._maintain_topmost)
        else:
            self.always_on_top_switch.configure(text="OFF")
            # Disable always on top
            self.root.attributes('-topmost', False)
            # Unbind events
            self.root.unbind('<FocusIn>')
            self.root.unbind('<Visibility>')

    def _maintain_topmost(self, event=None):
        """Maintain topmost status when focus changes (only if enabled)"""
        if self.always_on_top:
            self.root.attributes('-topmost', True)

    def _toggle_auto_minimize(self):
        """Toggle auto minimize"""
        self.auto_minimize = not self.auto_minimize
        self.storage["config"]["toggles"]["auto_minimize"] = self.auto_minimize
        if self.auto_minimize:
            self.auto_minimize_switch.configure(text="ON")
        else:
            self.auto_minimize_switch.configure(text="OFF")

    def _toggle_auto_focus_roblox(self):
        """Toggle auto focus Roblox"""
        self.auto_focus_roblox = not self.auto_focus_roblox
        self.storage["config"]["toggles"]["auto_focus_roblox"] = self.auto_focus_roblox
        if self.auto_focus_roblox:
            self.auto_focus_switch.configure(text="ON")
        else:
            self.auto_focus_switch.configure(text="OFF")

    def _toggle_auto_zoom_in(self):
        """Toggle auto zoom in"""
        self.auto_zoom_in = not self.auto_zoom_in
        self.storage["config"]["toggles"]["auto_zoom_in"] = self.auto_zoom_in
        if self.auto_zoom_in:
            self.auto_zoom_in_switch.configure(text="ON")
            # Show the options frame
            self.auto_zoom_in_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 10))
        else:
            self.auto_zoom_in_switch.configure(text="OFF")
            # Hide the options frame
            self.auto_zoom_in_frame.grid_remove()

    def _toggle_auto_select_rod(self):
        """Toggle auto select rod"""
        self.auto_select_rod = not self.auto_select_rod
        self.storage["config"]["toggles"]["auto_select_rod"] = self.auto_select_rod
        if self.auto_select_rod:
            self.auto_select_rod_switch.configure(text="ON")
            # Show the options frame
            self.auto_select_rod_frame.grid(row=4, column=0, columnspan=3, sticky="w", padx=30, pady=(0, 10))
        else:
            self.auto_select_rod_switch.configure(text="OFF")
            # Hide the options frame
            self.auto_select_rod_frame.grid_remove()

    def _setup_global_hotkeys(self):
        """Setup global hotkey listeners"""
        # Remove all existing hotkeys first
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # Register new hotkeys
        hotkeys = self.storage["config"]["hotkeys"]
        keyboard.add_hotkey(hotkeys["exit"], lambda: self.root.after(0, self._exit_application))
        keyboard.add_hotkey(hotkeys["change_scan"], lambda: self.root.after(0, self._toggle_area_selector))
        keyboard.add_hotkey(hotkeys["start_stop"], lambda: self.root.after(0, self._toggle_start_stop))

    def _exit_application(self):
        """Exit the application"""
        self.root.quit()

    def _on_key_press(self, event):
        """Handle key press events for hotkey rebinding and hotbar rebinding"""
        # Handle hotbar rebinding
        if self.waiting_for_hotbar:
            key_name = event.keysym
            
            # Only accept numeric keys 0-9
            if key_name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                # Update the hotbar value
                if self.hotbar_waiting_for == "fishing_rod":
                    self.fishing_rod_hotbar = key_name
                    self.storage["config"]["hotbar"]["fishing_rod"] = key_name
                    self.fishing_rod_value.configure(text=key_name)
                    # Also update Auto Select Rod entry if it exists
                    if hasattr(self, 'auto_rod_fishing_rod_entry'):
                        self.auto_rod_fishing_rod_entry.configure(state="normal")
                        self.auto_rod_fishing_rod_entry.delete(0, tk.END)
                        self.auto_rod_fishing_rod_entry.insert(0, key_name)
                        self.auto_rod_fishing_rod_entry.configure(state="disabled")
                elif self.hotbar_waiting_for == "equipment_bag":
                    self.equipment_bag_hotbar = key_name
                    self.storage["config"]["hotbar"]["equipment_bag"] = key_name
                    self.equipment_bag_value.configure(text=key_name)
                    # Also update Auto Select Rod entry if it exists
                    if hasattr(self, 'auto_rod_equipment_bag_entry'):
                        self.auto_rod_equipment_bag_entry.configure(state="normal")
                        self.auto_rod_equipment_bag_entry.delete(0, tk.END)
                        self.auto_rod_equipment_bag_entry.insert(0, key_name)
                        self.auto_rod_equipment_bag_entry.configure(state="disabled")
                
                # Reset state
                self.waiting_for_hotbar = False
                self.hotbar_waiting_for = None
            else:
                # Invalid key - restore original value
                if self.hotbar_waiting_for == "fishing_rod":
                    self.fishing_rod_value.configure(text=self.fishing_rod_hotbar)
                elif self.hotbar_waiting_for == "equipment_bag":
                    self.equipment_bag_value.configure(text=self.equipment_bag_hotbar)
                
                # Reset state
                self.waiting_for_hotbar = False
                self.hotbar_waiting_for = None
            
            return "break"
        
        # Handle hotkey rebinding
        if not self.waiting_for_hotkey:
            return "break"

        key_name = event.keysym
        old_hotkey = self.storage["config"]["hotkeys"][self.hotkey_waiting_for]

        # Check if this key is already in use by another hotkey
        for hotkey_type, assigned_key in self.storage["config"]["hotkeys"].items():
            if hotkey_type != self.hotkey_waiting_for and assigned_key.lower() == key_name.lower():
                # Key is already in use - reject and restore original
                self.hotkey_labels[self.hotkey_waiting_for].configure(text=old_hotkey)
                self.waiting_for_hotkey = False
                self.hotkey_waiting_for = None
                
                # Show error message briefly
                self.hotkey_labels[hotkey_type].configure(text_color="red")
                self.root.after(500, lambda: self.hotkey_labels[hotkey_type].configure(text_color="green"))
                
                # Re-enable hotkeys
                self._setup_global_hotkeys()
                return "break"

        # Update the hotkey in storage
        self.storage["config"]["hotkeys"][self.hotkey_waiting_for] = key_name
        display_name = key_name.upper() if len(key_name) == 1 else key_name
        self.hotkey_labels[self.hotkey_waiting_for].configure(text=display_name)

        # Reset state
        self.waiting_for_hotkey = False
        self.hotkey_waiting_for = None
        
        # Re-register all global hotkeys with the new binding
        self._setup_global_hotkeys()
        
        return "break"

    def _toggle_area_selector(self):
        """Toggle the area selector overlay"""
        if self.area_selector_active:
            if hasattr(self, 'area_selector') and self.area_selector:
                try:
                    shake_coords = {
                        "x": int(self.area_selector.shake_x1),
                        "y": int(self.area_selector.shake_y1),
                        "width": int(self.area_selector.shake_x2 - self.area_selector.shake_x1),
                        "height": int(self.area_selector.shake_y2 - self.area_selector.shake_y1)
                    }
                    fish_coords = {
                        "x": int(self.area_selector.fish_x1),
                        "y": int(self.area_selector.fish_y1),
                        "width": int(self.area_selector.fish_x2 - self.area_selector.fish_x1),
                        "height": int(self.area_selector.fish_y2 - self.area_selector.fish_y1)
                    }
                    self.storage["config"]["areas"]["shake"] = shake_coords
                    self.storage["config"]["areas"]["fish"] = fish_coords
                except:
                    pass

                try:
                    self.area_selector.window.destroy()
                except:
                    pass
            
            self.area_selector_active = False
            
            # Restore window if auto minimize is enabled
            if self.auto_minimize:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
        else:
            # Minimize window before opening area selector if auto minimize is enabled
            if self.auto_minimize:
                self.root.iconify()
                # Small delay to ensure window is minimized before screenshot
                self.root.after(100, self._open_area_selector)
            else:
                self._open_area_selector()

    def _open_area_selector(self):
        """Open the area selector overlay"""
        if self.area_selector_active:
            return

        self.area_selector_active = True
        
        # Only take screenshot if freeze while toggled is enabled
        if self.freeze_while_toggled:
            screenshot = ImageGrab.grab()
        else:
            screenshot = None
        
        shake_area = self.storage["config"]["areas"]["shake"]
        fish_area = self.storage["config"]["areas"]["fish"]

        self.area_selector = DualAreaSelector(self.root, screenshot, shake_area, fish_area, None)

    def _toggle_start_stop(self):
        """Toggle the main loop on/off"""
        # Don't allow start/stop while area selector is active
        if self.area_selector_active:
            print("Cannot start/stop while area selector is open")
            return
        
        if self.is_running:
            # Stop the loop - cleanup will run after loop actually stops
            self.is_running = False
            print("STOPPING...")
        else:
            # Start the loop from the beginning
            self.is_running = True
            print("STARTED")
            
            # Run one-time initialization before starting the loop
            self._on_start()
            
            # Start the main loop
            self._run_loop()

    def _on_start(self):
        """Runs once when the loop starts"""
        print("Running one-time setup on start...")
        
        # Initialize auto zoom ran once flag
        if self.auto_zoom_in:
            # If Cast Method is Perfect, skip auto zoom
            if self.cast_method_var.get() == "Perfect":
                self.auto_zoom_ran_once = True
            else:
                self.auto_zoom_ran_once = False
        
        # Auto minimize if enabled
        if self.auto_minimize:
            self.root.iconify()
        
        # Auto focus Roblox if enabled
        if self.auto_focus_roblox:
            self._focus_roblox_window()
        
        # Add any one-time initialization here

    def _focus_roblox_window(self):
        """Focus on the Roblox window"""
        try:
            # Move cursor to center of screen first
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            center_x = screen_width // 2
            center_y = screen_height // 2
            win32api.SetCursorPos((center_x, center_y))
            
            # Search for Roblox window (case-insensitive)
            windows = gw.getWindowsWithTitle('Roblox')
            if windows:
                roblox_window = windows[0]
                roblox_window.activate()
                print("Focused on Roblox window")
            else:
                print("Roblox window not found")
        except Exception as e:
            print(f"Error focusing Roblox window: {e}")

    def _on_stop(self):
        """Runs once when the loop stops (called after loop actually stops)"""
        print("Running one-time cleanup on stop...")
        
        # Restore window if auto minimize was enabled
        if self.auto_minimize:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        
        # Add any one-time cleanup here

    def _run_loop(self):
        """Main loop that cycles through Misc > Cast > Shake > Fish"""
        if not self.is_running:
            # Loop has stopped - run cleanup now
            self._on_stop()
            print("STOPPED")
            return
        
        # Execute Misc
        self._misc()
        if not self.is_running:
            return
        
        # Execute Cast
        self._cast()
        if not self.is_running:
            return
        
        # Execute Shake
        self._shake()
        if not self.is_running:
            return
        
        # Execute Fish
        self._fish()
        if not self.is_running:
            return
        
        # Loop back to the start
        self.root.after(0, self._run_loop)

    def _misc(self):
        """Misc function - Auto Zoom In and Auto Select Rod"""
        # Auto Zoom In (runs once per session)
        if self.auto_zoom_in and not self.auto_zoom_ran_once:
            self.auto_zoom_ran_once = True
            
            # Get zoom values
            delay1 = self._get_auto_zoom_delay1()
            zoom_in_amount = self._get_auto_zoom_in_amount()
            delay2 = self._get_auto_zoom_delay2()
            zoom_out_amount = self._get_auto_zoom_out_amount()
            delay3 = self._get_auto_zoom_delay3()
            
            print(f"Auto Zoom In: Delay {delay1}s")
            time.sleep(delay1)
            
            if not self.is_running:
                return
            
            print(f"Auto Zoom In: Zooming in {zoom_in_amount} times")
            for i in range(zoom_in_amount):
                if not self.is_running:
                    return
                mouse.wheel(1)  # Scroll up to zoom in
                time.sleep(0.025)  # Delay for better reliability
            
            print(f"Auto Zoom In: Delay {delay2}s")
            time.sleep(delay2)
            
            if not self.is_running:
                return
            
            print(f"Auto Zoom In: Zooming out {zoom_out_amount} times")
            for i in range(zoom_out_amount):
                if not self.is_running:
                    return
                mouse.wheel(-1)  # Scroll down to zoom out
                time.sleep(0.025)  # Delay for better reliability
            
            print(f"Auto Zoom In: Delay {delay3}s")
            time.sleep(delay3)
            
            print("Auto Zoom In: Complete")
        
        # Auto Select Rod
        if self.auto_select_rod:
            # Get delay values
            delay1 = self._get_auto_rod_delay1()
            delay2 = self._get_auto_rod_delay2()
            delay3 = self._get_auto_rod_delay3()
            
            print(f"Auto Select Rod: Delay {delay1}s")
            time.sleep(delay1)
            
            print(f"Auto Select Rod: Pressing Equipment Bag ({self.equipment_bag_hotbar})")
            keyboard.send(self.equipment_bag_hotbar)
            
            print(f"Auto Select Rod: Delay {delay2}s")
            time.sleep(delay2)
            
            print(f"Auto Select Rod: Pressing Fishing Rod ({self.fishing_rod_hotbar})")
            keyboard.send(self.fishing_rod_hotbar)
            
            print(f"Auto Select Rod: Delay {delay3}s")
            time.sleep(delay3)
            
            print("Auto Select Rod: Complete")
        
        # If both are disabled
        if not self.auto_zoom_in and not self.auto_select_rod:
            print("Misc (All features disabled)")

    def _auto_look_down(self):
        """
        Automatically look down in Roblox.
        Moves cursor to center of screen, then simulates right-click drag downward.
        """
        # Get screen dimensions and calculate center
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Move cursor to center of screen
        win32api.SetCursorPos((center_x, center_y))
        time.sleep(0.05)
        
        # Press right mouse button
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        
        # Send relative movement events to look down
        for i in range(100):
            if not self.is_running:
                # Release right mouse button before stopping
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                return
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 100, 0, 0)
            time.sleep(0.001)
        
        time.sleep(0.05)
        
        # Release right mouse button
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def _cast(self):
        """Cast function"""
        # Get cast method from storage
        cast_method = self.storage["config"]["cast"]["method"]
        
        if cast_method == "Disabled":
            print("Cast: Disabled")
            return
        
        elif cast_method == "Normal":
            print("Cast: Normal mode")
            # Normal mode - leave empty for now
            pass
        
        elif cast_method == "Perfect":
            print("Cast: Perfect mode")
            
            # Get delay1
            try:
                delay1 = float(self.storage["config"]["cast"]["delay1"])
            except (ValueError, KeyError):
                delay1 = 0.0
            
            print(f"Cast: Delay {delay1}s")
            time.sleep(delay1)
            
            if not self.is_running:
                return
            
            # Execute auto look down (only if enabled)
            if self.storage["config"]["cast"]["auto_look_down"]:
                print("Cast: Auto Look Down")
                self._auto_look_down()
                
                if not self.is_running:
                    return
            else:
                print("Cast: Auto Look Down (skipped - disabled)")
            
            # Get delay2
            try:
                delay2 = float(self.storage["config"]["cast"]["delay2"])
            except (ValueError, KeyError):
                delay2 = 0.0
            
            print(f"Cast: Delay {delay2}s")
            time.sleep(delay2)
            
            if not self.is_running:
                return
            
            # Hold left click down
            print("Cast: Holding Left Click Down")
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            
            # Get delay3
            try:
                delay3 = float(self.storage["config"]["cast"]["delay3"])
            except (ValueError, KeyError):
                delay3 = 0.0
            
            print(f"Cast: Delay {delay3}s")
            time.sleep(delay3)
            
            if not self.is_running:
                return
            
            # Perfect cast release (placeholder)
            print("Cast: Perfect Cast Release (placeholder)")
            # TODO: Implement perfect cast release logic here
            
            # Get delay4
            try:
                delay4 = float(self.storage["config"]["cast"]["delay4"])
            except (ValueError, KeyError):
                delay4 = 0.0
            
            print(f"Cast: Delay {delay4}s")
            time.sleep(delay4)

    def _shake(self):
        """Shake function"""
        print("Shake")

    def _fish(self):
        """Fish function"""
        print("Fish")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        finally:
            try:
                keyboard.remove_all_hotkeys()
            except:
                pass


if __name__ == "__main__":
    app = SimpleApp()
    app.run()