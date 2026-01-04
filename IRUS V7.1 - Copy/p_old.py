import tkinter as tk
from tkinter import ttk
import os
import json
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import keyboard

class HotkeyConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotkey Configuration")
        self.root.geometry("500x450")

        # First Launch Config - Default settings
        self.first_launch_config = {
            "Start": "F3",
            "Stop": "F4",
            "Modify Area": "F5",
            "Exit": "F6",
            "fish_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300},
            "always_on_top": True
        }

        # Active Settings - Will be loaded from config or defaults
        self.active_settings = {}

        # Area selection state
        self.area_selector = None
        self.is_modifying_area = False

        # Config file path
        self.config_file = os.path.join(os.path.dirname(__file__), "Config.txt")

        # Load or create config
        self.load_config()

        # Build GUI
        self.build_gui()

        # Apply always on top setting
        self.apply_always_on_top()

        # Setup keyboard hotkeys
        self.setup_hotkeys()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """Load config from file or create it with first launch defaults"""
        if not os.path.exists(self.config_file):
            # First launch - create config with defaults
            self.active_settings = self.first_launch_config.copy()
            self.save_config()
        else:
            # Load existing config into active settings
            try:
                with open(self.config_file, 'r') as f:
                    self.active_settings = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                # Fall back to defaults if config is corrupted
                self.active_settings = self.first_launch_config.copy()

    def save_config(self):
        """Save active settings to Config.txt"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.active_settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def build_gui(self):
        """Build the GUI interface"""
        # Configure root window
        self.root.configure(bg="#f5f5f5")
        self.root.resizable(True, True)
        self.root.minsize(450, 400)

        # Header frame with gradient-like appearance
        header_frame = tk.Frame(self.root, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Title label
        title_label = tk.Label(
            header_frame,
            text="⌨️ Hotkey Configuration",
            font=("Segoe UI", 18, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=25)

        # Main content frame with padding
        content_frame = tk.Frame(self.root, bg="#f5f5f5")
        content_frame.pack(pady=30, padx=40, fill="both", expand=True)

        # Settings frame with border
        settings_container = tk.Frame(content_frame, bg="white", relief="solid", bd=1)
        settings_container.pack(fill="both", expand=True)

        settings_frame = tk.Frame(settings_container, bg="white")
        settings_frame.pack(pady=20, padx=20)

        # Available keys for dropdown
        self.available_keys = [
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24"
        ]

        # Dictionary to store dropdown widgets
        self.dropdown_widgets = {}

        # Actions to display (exclude fish_box from GUI)
        display_actions = ["Start", "Stop", "Modify Area", "Exit"]
        action_icons = {
            "Start": "▶️",
            "Stop": "⏹️",
            "Modify Area": "🎯",
            "Exit": "🚪"
        }

        # Create a row for each hotkey setting
        for idx, action in enumerate(display_actions):
            # Get current key value
            current_key = self.active_settings.get(action, self.first_launch_config.get(action, "F1"))

            # Action label with icon
            icon = action_icons.get(action, "⚙️")
            action_label = tk.Label(
                settings_frame,
                text=f"{icon}  {action}",
                font=("Segoe UI", 11),
                bg="white",
                fg="#333333",
                anchor="w",
                width=18
            )
            action_label.grid(row=idx, column=0, padx=15, pady=12, sticky="w")

            # Dropdown for key selection
            key_var = tk.StringVar(value=current_key)
            key_dropdown = ttk.Combobox(
                settings_frame,
                textvariable=key_var,
                values=self.available_keys,
                state="readonly",
                font=("Segoe UI", 10),
                width=12
            )
            key_dropdown.set(current_key)
            key_dropdown.grid(row=idx, column=1, padx=15, pady=12)

            # Store reference to dropdown widget
            self.dropdown_widgets[action] = key_var

        # Separator
        separator = tk.Frame(settings_container, bg="#e0e0e0", height=1)
        separator.pack(fill="x", padx=20, pady=10)

        # Always on top option
        options_frame = tk.Frame(settings_container, bg="white")
        options_frame.pack(pady=15, padx=20)

        self.always_on_top_var = tk.BooleanVar(value=self.active_settings.get("always_on_top", False))
        always_on_top_check = tk.Checkbutton(
            options_frame,
            text="📌 Always on Top",
            variable=self.always_on_top_var,
            font=("Segoe UI", 11),
            bg="white",
            fg="#333333",
            activebackground="white",
            selectcolor="white",
            command=self.toggle_always_on_top,
            cursor="hand2"
        )
        always_on_top_check.pack(anchor="w")

        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg="#f5f5f5")
        buttons_frame.pack(pady=20, padx=40)

        # Save button with modern style
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Save Settings",
            font=("Segoe UI", 11, "bold"),
            command=self.save_changes,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2",
            activebackground="#45a049"
        )
        save_btn.pack(side="left", padx=8)

        # Reset to defaults button
        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Reset to Defaults",
            font=("Segoe UI", 11),
            command=self.reset_to_defaults,
            bg="#ff9800",
            fg="white",
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2",
            activebackground="#e68900"
        )
        reset_btn.pack(side="left", padx=8)

    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        def on_modify_area_hotkey():
            self.toggle_modify_area()

        def on_exit_hotkey():
            self.on_closing()

        # Get the hotkeys
        modify_key = self.active_settings.get("Modify Area", "F6")
        exit_key = self.active_settings.get("Exit", "F7")

        try:
            keyboard.add_hotkey(modify_key.lower(), on_modify_area_hotkey)
        except:
            print(f"Could not bind hotkey: {modify_key}")

        try:
            keyboard.add_hotkey(exit_key.lower(), on_exit_hotkey)
        except:
            print(f"Could not bind hotkey: {exit_key}")

    def toggle_modify_area(self):
        """Toggle the modify area mode"""
        if not self.is_modifying_area:
            # Start area modification
            self.is_modifying_area = True
            self.open_area_selector()
        else:
            # Stop area modification - save and close the selector if it exists
            if self.area_selector:
                self.area_selector.finish_selection()
                # Note: finish_selection will call on_area_selected callback
                # which sets is_modifying_area to False

    def open_area_selector(self):
        """Open the area selector overlay"""
        # Take a screenshot of the entire screen
        screenshot = ImageGrab.grab()

        # Get current fish box coordinates if they exist
        fish_box = self.active_settings.get("fish_box", {"x1": 100, "y1": 100, "x2": 300, "y2": 300})

        # Create the area selector window
        self.area_selector = AreaSelector(self.root, screenshot, fish_box, self.on_area_selected)

    def on_area_selected(self, box_coords):
        """Called when area selection is complete"""
        self.is_modifying_area = False
        self.area_selector = None

        # Save the new box coordinates to active settings
        self.active_settings["fish_box"] = box_coords

        # Auto-save to config
        self.save_config()

        print(f"Fish Box saved: {box_coords}")

    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        is_on_top = self.always_on_top_var.get()
        self.root.attributes('-topmost', is_on_top)
        self.active_settings["always_on_top"] = is_on_top
        self.save_config()

    def apply_always_on_top(self):
        """Apply the always on top setting from config"""
        is_on_top = self.active_settings.get("always_on_top", False)
        self.root.attributes('-topmost', is_on_top)

    def save_changes(self):
        """Save current GUI values to active settings and config file"""
        # Update active settings from dropdown widgets
        for action, key_var in self.dropdown_widgets.items():
            self.active_settings[action] = key_var.get()

        # Update always on top setting
        self.active_settings["always_on_top"] = self.always_on_top_var.get()

        # Save to config file
        self.save_config()

        # Reload hotkeys
        keyboard.unhook_all()
        self.setup_hotkeys()

        # Show confirmation
        self.show_message("✓ Settings saved successfully!", "#4CAF50")

    def reset_to_defaults(self):
        """Reset all settings to first launch defaults"""
        # Reset only the hotkey settings, preserve fish_box
        fish_box = self.active_settings.get("fish_box", self.first_launch_config["fish_box"])
        self.active_settings = self.first_launch_config.copy()
        self.active_settings["fish_box"] = fish_box

        # Update GUI dropdowns
        for action, key_var in self.dropdown_widgets.items():
            default_key = self.first_launch_config.get(action, "F1")
            key_var.set(default_key)

        # Update always on top checkbox
        self.always_on_top_var.set(self.first_launch_config["always_on_top"])
        self.apply_always_on_top()

        # Show confirmation
        self.show_message("✓ Reset to default settings!", "#ff9800")

    def show_message(self, message, color="#4CAF50"):
        """Show a temporary message"""
        msg_label = tk.Label(
            self.root,
            text=message,
            font=("Segoe UI", 10, "bold"),
            fg=color,
            bg="#f5f5f5"
        )
        msg_label.pack(pady=5)

        # Remove message after 2 seconds
        self.root.after(2000, msg_label.destroy)

    def on_closing(self):
        """Handle window close event - save active settings"""
        self.save_config()
        keyboard.unhook_all()
        self.root.destroy()


class AreaSelector:
    """Full-screen overlay for selecting the fish box area with frozen screenshot"""

    def __init__(self, parent, screenshot, initial_box, callback):
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

        # Initialize box coordinates
        self.box = initial_box.copy()
        self.x1, self.y1 = self.box["x1"], self.box["y1"]
        self.x2, self.y2 = self.box["x2"], self.box["y2"]

        # Drawing state
        self.dragging = False
        self.drag_corner = None
        self.resize_threshold = 10

        # Create the blue box rectangle with transparent fill
        self.rect = self.canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            outline='#2196F3',
            width=2,
            fill='#2196F3',
            stipple='gray50',  # Makes it semi-transparent
            tags='box'
        )

        # Create label
        label_x = self.x1 + (self.x2 - self.x1) // 2
        label_y = self.y1 - 20
        self.label = self.canvas.create_text(
            label_x, label_y,
            text="Fish Box",
            font=("Arial", 12, "bold"),
            fill='#2196F3',
            tags='label'
        )

        # Create corner handles (small squares)
        self.handles = []
        self.create_handles()

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

    def create_handles(self):
        """Create corner handles for resizing - pixel perfect corners"""
        handle_size = 12  # Larger for visibility
        corner_marker_size = 3  # Small precise corner marker

        corners = [
            (self.x1, self.y1, 'nw'),
            (self.x2, self.y1, 'ne'),
            (self.x1, self.y2, 'sw'),
            (self.x2, self.y2, 'se')
        ]

        # Delete old handles
        for handle in self.handles:
            self.canvas.delete(handle)
        self.handles = []

        # Create new handles with precise corner markers
        for x, y, corner in corners:
            # Outer handle (for grabbing)
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline='#2196F3',
                width=2,
                tags=f'handle_{corner}'
            )
            self.handles.append(handle)

            # Inner precise corner marker (shows exact pixel)
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='red',
                outline='white',
                width=1,
                tags=f'corner_{corner}'
            )
            self.handles.append(corner_marker)

            # Crosshair for even more precision
            line1 = self.canvas.create_line(
                x - handle_size, y, x + handle_size, y,
                fill='yellow',
                width=1,
                tags=f'cross_{corner}'
            )
            line2 = self.canvas.create_line(
                x, y - handle_size, x, y + handle_size,
                fill='yellow',
                width=1,
                tags=f'cross_{corner}'
            )
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

        # Check if clicking on a corner
        corner = self.get_corner_at_position(event.x, event.y)
        if corner:
            self.dragging = True
            self.drag_corner = corner
        elif self.is_inside_box(event.x, event.y):
            # Moving the entire box
            self.dragging = True
            self.drag_corner = 'move'

    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging:
            return

        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        if self.drag_corner == 'move':
            # Move entire box
            self.x1 += dx
            self.y1 += dy
            self.x2 += dx
            self.y2 += dy
        elif self.drag_corner == 'nw':
            self.x1 = event.x
            self.y1 = event.y
        elif self.drag_corner == 'ne':
            self.x2 = event.x
            self.y1 = event.y
        elif self.drag_corner == 'sw':
            self.x1 = event.x
            self.y2 = event.y
        elif self.drag_corner == 'se':
            self.x2 = event.x
            self.y2 = event.y

        # Ensure x1 < x2 and y1 < y2
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1

        # Update visuals
        self.update_box()

        # Update zoom window while dragging
        self.show_zoom(event.x, event.y)

        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.dragging = False
        self.drag_corner = None

    def on_mouse_move(self, event):
        """Handle mouse movement - update zoom window"""
        # Update cursor based on position
        corner = self.get_corner_at_position(event.x, event.y)
        if corner:
            cursors = {'nw': 'top_left_corner', 'ne': 'top_right_corner',
                      'sw': 'bottom_left_corner', 'se': 'bottom_right_corner'}
            self.window.configure(cursor=cursors.get(corner, 'cross'))
        elif self.is_inside_box(event.x, event.y):
            self.window.configure(cursor='fleur')
        else:
            self.window.configure(cursor='cross')

        # Show zoom window
        self.show_zoom(event.x, event.y)

    def show_zoom(self, x, y):
        """Display mini zoom window around cursor"""
        # Delete previous zoom elements
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
        if self.zoom_image_id:
            self.canvas.delete(self.zoom_image_id)

        # Calculate zoom region from screenshot
        zoom_src_size = self.zoom_window_size // self.zoom_factor
        x1_src = max(0, x - zoom_src_size // 2)
        y1_src = max(0, y - zoom_src_size // 2)
        x2_src = min(self.screen_width, x1_src + zoom_src_size)
        y2_src = min(self.screen_height, y1_src + zoom_src_size)

        # Crop and zoom
        cropped = self.screenshot.crop((x1_src, y1_src, x2_src, y2_src))
        zoomed = cropped.resize((self.zoom_window_size, self.zoom_window_size), Image.NEAREST)

        # Draw crosshair on zoomed image
        draw = ImageDraw.Draw(zoomed)
        center = self.zoom_window_size // 2
        crosshair_size = 10
        draw.line([(center - crosshair_size, center), (center + crosshair_size, center)], fill='red', width=2)
        draw.line([(center, center - crosshair_size), (center, center + crosshair_size)], fill='red', width=2)

        self.zoom_photo = ImageTk.PhotoImage(zoomed)

        # Position zoom window near cursor (offset to not block view)
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

    def update_box(self):
        """Update the box and label positions"""
        self.canvas.coords(self.rect, self.x1, self.y1, self.x2, self.y2)

        # Update label position
        label_x = self.x1 + (self.x2 - self.x1) // 2
        label_y = self.y1 - 20
        self.canvas.coords(self.label, label_x, label_y)

        # Update handles
        self.create_handles()

    def finish_selection(self):
        """Close the selector and return the box coordinates"""
        box_coords = {
            "x1": int(self.x1),
            "y1": int(self.y1),
            "x2": int(self.x2),
            "y2": int(self.y2)
        }
        self.window.destroy()
        self.callback(box_coords)

    def close_without_saving(self):
        """Close the selector without saving (for toggle off)"""
        self.window.destroy()


def main():
    root = tk.Tk()
    app = HotkeyConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
