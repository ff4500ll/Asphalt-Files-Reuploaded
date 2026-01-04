import tkinter as tk
from tkinter import ttk
import os
import json
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import keyboard
import threading
import time
import pyautogui
import cv2
import numpy as np
from ultralytics import YOLO
from ctypes import windll

# Mouse event constants
MOUSEEVENTF_MOVE = 0x0001

class HotkeyConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRUS V7")
        self.root.geometry("650x600")

        # Get screen resolution for scaling
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Reference resolution (2560x1440 - your resolution)
        ref_width = 2560
        ref_height = 1440

        # Scale factors
        scale_x = screen_width / ref_width
        scale_y = screen_height / ref_height

        # Original coordinates at 2560x1440
        fish_box_ref = {"x1": 764, "y1": 1177, "x2": 1795, "y2": 1216}
        shake_box_ref = {"x1": 530, "y1": 235, "x2": 2030, "y2": 900}

        # Scaled coordinates
        fish_box_scaled = {
            "x1": int(fish_box_ref["x1"] * scale_x),
            "y1": int(fish_box_ref["y1"] * scale_y),
            "x2": int(fish_box_ref["x2"] * scale_x),
            "y2": int(fish_box_ref["y2"] * scale_y)
        }

        shake_box_scaled = {
            "x1": int(shake_box_ref["x1"] * scale_x),
            "y1": int(shake_box_ref["y1"] * scale_y),
            "x2": int(shake_box_ref["x2"] * scale_x),
            "y2": int(shake_box_ref["y2"] * scale_y)
        }

        # First Launch Config - Default settings with scaled coordinates
        self.first_launch_config = {
            "Start": "F3",
            "Stop": "F4",
            "Modify Area": "F5",
            "Exit": "F6",
            "fish_box": fish_box_scaled,
            "shake_box": shake_box_scaled,
            "always_on_top": True,
            "gui_width": 650,
            "gui_height": 600,
            "gui_x": None,  # None means center on screen
            "gui_y": None,
            "flow_cast_enabled": True,
            "flow_shake_enabled": True,
            "flow_fish_enabled": True,
            "shake_timeout": 3.0,
            "shake_confidence_threshold": 0.9,
            "fishing_confidence_threshold": 0.5,
            "auto_minimize": True
        }

        # Active Settings - Will be loaded from config or defaults
        self.active_settings = {}

        # Area selection state
        self.area_selector = None
        self.is_modifying_area = False
        self.current_box_type = None  # Track which box is being modified

        # Loop state
        self.loop_running = False
        self.loop_thread = None
        self.last_shake_position = None  # Track last clicked shake position

        # Config file path
        self.config_file = os.path.join(os.path.dirname(__file__), "Config.txt")

        # Load or create config
        self.load_config()

        # Build GUI
        self.build_gui()

        # Apply GUI size and position from config
        self.apply_gui_geometry()

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
        self.root.minsize(600, 500)

        # Header frame
        header_frame = tk.Frame(self.root, bg="#2196F3", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Title label
        title_label = tk.Label(
            header_frame,
            text="IRUS V7",
            font=("Segoe UI", 20, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=20)

        # Create notebook (tabbed interface)
        style = ttk.Style()
        style.theme_create("irus_theme", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": "#f5f5f5"}},
            "TNotebook.Tab": {
                "configure": {"padding": [20, 10], "background": "#e0e0e0", "foreground": "#333333"},
                "map": {"background": [("selected", "#2196F3")], "foreground": [("selected", "white")], "expand": [("selected", [1, 1, 1, 0])]}
            }
        })
        style.theme_use("irus_theme")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.create_basic_settings_tab()
        self.create_flow_configuration_tab()
        self.create_cast_settings_tab()
        self.create_shake_settings_tab()
        self.create_fishing_settings_tab()
        self.create_discord_settings_tab()
        self.create_support_tab()

    def create_basic_settings_tab(self):
        """Create the Basic Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Basic Settings")

        # Main container
        container = tk.Frame(tab, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title = tk.Label(
            container,
            text="Hotkey Configuration",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#333333"
        )
        title.pack(anchor="w", pady=(0, 20))

        # Settings frame
        settings_frame = tk.Frame(container, bg="white")
        settings_frame.pack(fill="x")

        # Available keys for dropdown
        self.available_keys = [
            # Function keys
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            # Letters
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            # Numbers
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            # Symbols
            "[", "]", ";", "'", ",", ".", "/", "\\", "-", "=",
            # Special keys
            "Space", "Enter", "Tab", "Backspace", "Delete",
            "Home", "End", "Page Up", "Page Down",
            "Up", "Down", "Left", "Right"
        ]

        # Dictionary to store dropdown widgets
        self.dropdown_widgets = {}

        # Actions to display
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
                width=20
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
        separator = tk.Frame(container, bg="#e0e0e0", height=1)
        separator.pack(fill="x", pady=20)

        # Options section
        options_title = tk.Label(
            container,
            text="Options",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#333333"
        )
        options_title.pack(anchor="w", pady=(0, 15))

        options_frame = tk.Frame(container, bg="white")
        options_frame.pack(fill="x")

        # Always on top option
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
        always_on_top_check.pack(anchor="w", pady=5)

        # Auto minimize option
        self.auto_minimize_var = tk.BooleanVar(value=self.active_settings.get("auto_minimize", False))
        auto_minimize_check = tk.Checkbutton(
            options_frame,
            text="🗕 Auto Minimize",
            variable=self.auto_minimize_var,
            font=("Segoe UI", 11),
            bg="white",
            fg="#333333",
            activebackground="white",
            selectcolor="white",
            command=self.toggle_auto_minimize,
            cursor="hand2"
        )
        auto_minimize_check.pack(anchor="w", pady=5)

        # Separator
        separator2 = tk.Frame(container, bg="#e0e0e0", height=1)
        separator2.pack(fill="x", pady=20)

        # Buttons in center
        buttons_frame = tk.Frame(container, bg="white")
        buttons_frame.pack(pady=10)

        # Reset to defaults button (centered)
        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Reset to Defaults",
            font=("Segoe UI", 10),
            command=self.reset_to_defaults,
            bg="#ff9800",
            fg="white",
            padx=25,
            pady=8,
            relief="flat",
            cursor="hand2",
            activebackground="#e68900"
        )
        reset_btn.pack()

        # Auto-save notice
        notice = tk.Label(
            container,
            text="Settings are automatically saved",
            font=("Segoe UI", 9, "italic"),
            bg="white",
            fg="#999999"
        )
        notice.pack(pady=(15, 0))

    def create_flow_configuration_tab(self):
        """Create the Flow Configuration tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Flow Configuration")

        # Main container
        container = tk.Frame(tab, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title = tk.Label(
            container,
            text="Fishing Loop Flow",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#333333"
        )
        title.pack(anchor="w", pady=(0, 20))

        # Flow visualization frame
        flow_frame = tk.Frame(container, bg="white")
        flow_frame.pack(pady=20)

        # Cast step
        cast_frame = tk.Frame(flow_frame, bg="white")
        cast_frame.grid(row=0, column=0, padx=20, pady=10)

        self.cast_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_cast_enabled", True))
        cast_check = tk.Checkbutton(
            cast_frame,
            variable=self.cast_enabled_var,
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="white",
            command=self.save_flow_settings
        )
        cast_check.pack(side="left")

        cast_box = tk.Label(
            cast_frame,
            text="Cast",
            font=("Segoe UI", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=15,
            relief="solid",
            bd=2
        )
        cast_box.pack(side="left", padx=(5, 0))

        # Arrow 1
        arrow1 = tk.Label(
            flow_frame,
            text="→",
            font=("Segoe UI", 24),
            bg="white",
            fg="#333333"
        )
        arrow1.grid(row=0, column=1, padx=5)

        # Shake step
        shake_frame = tk.Frame(flow_frame, bg="white")
        shake_frame.grid(row=0, column=2, padx=20, pady=10)

        self.shake_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_shake_enabled", True))
        shake_check = tk.Checkbutton(
            shake_frame,
            variable=self.shake_enabled_var,
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="white",
            command=self.save_flow_settings
        )
        shake_check.pack(side="left")

        shake_box = tk.Label(
            shake_frame,
            text="Shake",
            font=("Segoe UI", 12, "bold"),
            bg="#FF9800",
            fg="white",
            padx=30,
            pady=15,
            relief="solid",
            bd=2
        )
        shake_box.pack(side="left", padx=(5, 0))

        # Arrow 2
        arrow2 = tk.Label(
            flow_frame,
            text="→",
            font=("Segoe UI", 24),
            bg="white",
            fg="#333333"
        )
        arrow2.grid(row=0, column=3, padx=5)

        # Fish step
        fish_frame = tk.Frame(flow_frame, bg="white")
        fish_frame.grid(row=0, column=4, padx=20, pady=10)

        self.fish_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_fish_enabled", True))
        fish_check = tk.Checkbutton(
            fish_frame,
            variable=self.fish_enabled_var,
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="white",
            command=self.save_flow_settings
        )
        fish_check.pack(side="left")

        fish_box = tk.Label(
            fish_frame,
            text="Fish",
            font=("Segoe UI", 12, "bold"),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=15,
            relief="solid",
            bd=2
        )
        fish_box.pack(side="left", padx=(5, 0))

        # Loop back arrow
        loop_arrow = tk.Label(
            flow_frame,
            text="↻",
            font=("Segoe UI", 24),
            bg="white",
            fg="#333333"
        )
        loop_arrow.grid(row=1, column=2, pady=10)

        # Description
        desc_frame = tk.Frame(container, bg="#f5f5f5", relief="solid", bd=1)
        desc_frame.pack(fill="x", pady=20, padx=10)

        desc_text = tk.Label(
            desc_frame,
            text="The loop will continuously cycle through enabled steps.\n"
                 "Uncheck a step to skip it in the loop.\n\n"
                 "Press Start hotkey to begin, Stop hotkey to pause.",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            justify="left"
        )
        desc_text.pack(padx=15, pady=15)

        # Loop status indicator
        self.loop_status_label = tk.Label(
            container,
            text="● Loop Status: Stopped",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#f44336"
        )
        self.loop_status_label.pack(pady=10)

    def create_cast_settings_tab(self):
        """Create the Cast Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Cast Settings")

        label = tk.Label(
            tab,
            text="Cast Settings\n\nComing Soon...",
            font=("Segoe UI", 14),
            bg="white",
            fg="#999999"
        )
        label.pack(expand=True)

    def create_shake_settings_tab(self):
        """Create the Shake Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Shake Settings")

        # Main container
        container = tk.Frame(tab, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title = tk.Label(
            container,
            text="Shake Detection Settings",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#333333"
        )
        title.pack(anchor="w", pady=(0, 20))

        # Settings frame
        settings_frame = tk.Frame(container, bg="white")
        settings_frame.pack(fill="x")

        # Shake Timeout setting
        timeout_label = tk.Label(
            settings_frame,
            text="Shake Timeout (seconds):",
            font=("Segoe UI", 11),
            bg="white",
            fg="#333333",
            anchor="w"
        )
        timeout_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Timeout input with validation
        self.shake_timeout_var = tk.StringVar(value=str(self.active_settings.get("shake_timeout", 3.0)))
        timeout_entry = tk.Entry(
            settings_frame,
            textvariable=self.shake_timeout_var,
            font=("Segoe UI", 10),
            width=10
        )
        timeout_entry.grid(row=0, column=1, padx=15, pady=12)

        # Save button for timeout
        save_timeout_btn = tk.Button(
            settings_frame,
            text="Apply",
            font=("Segoe UI", 9),
            command=self.save_shake_timeout,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2",
            activebackground="#45a049"
        )
        save_timeout_btn.grid(row=0, column=2, padx=10, pady=12)

        # Shake Confidence Threshold setting
        shake_confidence_label = tk.Label(
            settings_frame,
            text="Shake Detection Confidence:",
            font=("Segoe UI", 11),
            bg="white",
            fg="#333333",
            anchor="w"
        )
        shake_confidence_label.grid(row=1, column=0, padx=15, pady=12, sticky="w")

        # Shake Confidence input with validation
        self.shake_confidence_var = tk.StringVar(value=str(self.active_settings.get("shake_confidence_threshold", 0.5)))
        shake_confidence_entry = tk.Entry(
            settings_frame,
            textvariable=self.shake_confidence_var,
            font=("Segoe UI", 10),
            width=10
        )
        shake_confidence_entry.grid(row=1, column=1, padx=15, pady=12)

        # Save button for shake confidence
        save_shake_confidence_btn = tk.Button(
            settings_frame,
            text="Apply",
            font=("Segoe UI", 9),
            command=self.save_shake_confidence,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2",
            activebackground="#45a049"
        )
        save_shake_confidence_btn.grid(row=1, column=2, padx=10, pady=12)

        # Description
        desc_frame = tk.Frame(container, bg="#f5f5f5", relief="solid", bd=1)
        desc_frame.pack(fill="x", pady=20, padx=10)

        desc_text = tk.Label(
            desc_frame,
            text="Shake Timeout: How long to wait in shake stage before returning to cast.\n\n"
                 "Shake Detection Confidence: Minimum confidence (0.0-1.0) required to accept\n"
                 "shake indicator detections. Higher values reduce false positives.\n"
                 "Recommended: 0.5 (50% confidence) or higher.",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            justify="left"
        )
        desc_text.pack(padx=15, pady=15)

    def create_fishing_settings_tab(self):
        """Create the Fishing Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Fishing Settings")

        # Main container
        container = tk.Frame(tab, bg="white")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title = tk.Label(
            container,
            text="Fishing Detection Settings",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#333333"
        )
        title.pack(anchor="w", pady=(0, 20))

        # Settings frame
        settings_frame = tk.Frame(container, bg="white")
        settings_frame.pack(fill="x")

        # Fishing Confidence Threshold setting
        confidence_label = tk.Label(
            settings_frame,
            text="Detection Confidence Threshold:",
            font=("Segoe UI", 11),
            bg="white",
            fg="#333333",
            anchor="w"
        )
        confidence_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Confidence input with validation
        self.fishing_confidence_var = tk.StringVar(value=str(self.active_settings.get("fishing_confidence_threshold", 0.5)))
        confidence_entry = tk.Entry(
            settings_frame,
            textvariable=self.fishing_confidence_var,
            font=("Segoe UI", 10),
            width=10
        )
        confidence_entry.grid(row=0, column=1, padx=15, pady=12)

        # Save button for confidence
        save_confidence_btn = tk.Button(
            settings_frame,
            text="Apply",
            font=("Segoe UI", 9),
            command=self.save_fishing_confidence,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2",
            activebackground="#45a049"
        )
        save_confidence_btn.grid(row=0, column=2, padx=10, pady=12)

        # Description
        desc_frame = tk.Frame(container, bg="#f5f5f5", relief="solid", bd=1)
        desc_frame.pack(fill="x", pady=20, padx=10)

        desc_text = tk.Label(
            desc_frame,
            text="Detection Confidence Threshold: Minimum confidence (0.0-1.0) required\n"
                 "to accept Target Line and Fish Bar detections.\n\n"
                 "Higher values (e.g., 0.7) reduce false positives but may miss some detections.\n"
                 "Lower values (e.g., 0.3) catch more detections but may have false positives.\n\n"
                 "Recommended: 0.5 (50% confidence)",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            justify="left"
        )
        desc_text.pack(padx=15, pady=15)

    def create_discord_settings_tab(self):
        """Create the Discord Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Discord Settings")

        label = tk.Label(
            tab,
            text="Discord Settings\n\nComing Soon...",
            font=("Segoe UI", 14),
            bg="white",
            fg="#999999"
        )
        label.pack(expand=True)

    def create_support_tab(self):
        """Create the Support The Creators tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Support The Creators")

        label = tk.Label(
            tab,
            text="Support The Creators\n\nComing Soon...",
            font=("Segoe UI", 14),
            bg="white",
            fg="#999999"
        )
        label.pack(expand=True)

    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        def on_start_hotkey():
            self.start_loop()

        def on_stop_hotkey():
            self.stop_loop()

        def on_modify_area_hotkey():
            self.toggle_modify_area()

        def on_exit_hotkey():
            self.on_closing()

        # Get the hotkeys
        start_key = self.active_settings.get("Start", "F3")
        stop_key = self.active_settings.get("Stop", "F4")
        modify_key = self.active_settings.get("Modify Area", "F5")
        exit_key = self.active_settings.get("Exit", "F6")

        try:
            keyboard.add_hotkey(start_key.lower(), on_start_hotkey)
        except:
            print(f"Could not bind hotkey: {start_key}")

        try:
            keyboard.add_hotkey(stop_key.lower(), on_stop_hotkey)
        except:
            print(f"Could not bind hotkey: {stop_key}")

        try:
            keyboard.add_hotkey(modify_key.lower(), on_modify_area_hotkey)
        except:
            print(f"Could not bind hotkey: {modify_key}")

        try:
            keyboard.add_hotkey(exit_key.lower(), on_exit_hotkey)
        except:
            print(f"Could not bind hotkey: {exit_key}")

    def toggle_modify_area(self):
        """Toggle the modify area mode - shows both boxes"""
        if not self.is_modifying_area:
            # Start area modification
            self.is_modifying_area = True

            # Auto minimize if enabled
            if self.active_settings.get("auto_minimize", False):
                self.root.iconify()

            self.open_area_selector_both_boxes()
        else:
            # Stop area modification - save and close the selector if it exists
            if self.area_selector:
                self.area_selector.finish_selection()

    def open_area_selector_both_boxes(self):
        """Open area selector showing both Fish Box and Shake Box"""
        screenshot = ImageGrab.grab()
        fish_box = self.active_settings.get("fish_box", {"x1": 100, "y1": 100, "x2": 300, "y2": 300})
        shake_box = self.active_settings.get("shake_box", {"x1": 400, "y1": 100, "x2": 600, "y2": 300})
        self.area_selector = DualAreaSelector(self.root, screenshot, fish_box, shake_box, self.on_both_areas_selected)

    def open_area_selector_for_box(self, box_type):
        """Open area selector for a specific box (Fish or Shake)"""
        screenshot = ImageGrab.grab()
        box_coords = self.active_settings.get(box_type, {"x1": 100, "y1": 100, "x2": 300, "y2": 300})

        # Determine color and label based on box type
        if box_type == "fish_box":
            color = "#2196F3"  # Blue
            label = "Fish Box"
        else:  # shake_box
            color = "#f44336"  # Red
            label = "Shake Box"

        self.current_box_type = box_type
        self.area_selector = AreaSelector(self.root, screenshot, box_coords,
                                         lambda coords: self.on_single_area_selected(box_type, coords),
                                         color=color, label=label)

    def on_single_area_selected(self, box_type, box_coords):
        """Called when single area selection is complete"""
        self.area_selector = None
        self.active_settings[box_type] = box_coords
        self.save_config()
        print(f"{box_type} saved: {box_coords}")

    def on_both_areas_selected(self, fish_coords, shake_coords):
        """Called when both area selections are complete"""
        self.is_modifying_area = False
        self.area_selector = None
        self.active_settings["fish_box"] = fish_coords
        self.active_settings["shake_box"] = shake_coords
        self.save_config()
        print(f"Fish Box saved: {fish_coords}")
        print(f"Shake Box saved: {shake_coords}")

        # Auto restore if enabled and minimized
        if self.active_settings.get("auto_minimize", False):
            self.root.deiconify()

    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        is_on_top = self.always_on_top_var.get()
        self.root.attributes('-topmost', is_on_top)
        self.active_settings["always_on_top"] = is_on_top
        self.save_config()

    def toggle_auto_minimize(self):
        """Toggle auto minimize setting"""
        auto_minimize = self.auto_minimize_var.get()
        self.active_settings["auto_minimize"] = auto_minimize
        self.save_config()

    def apply_always_on_top(self):
        """Apply the always on top setting from config"""
        is_on_top = self.active_settings.get("always_on_top", False)
        self.root.attributes('-topmost', is_on_top)

    def apply_gui_geometry(self):
        """Apply the GUI size and position from config"""
        width = self.active_settings.get("gui_width", 650)
        height = self.active_settings.get("gui_height", 600)
        x = self.active_settings.get("gui_x")
        y = self.active_settings.get("gui_y")

        if x is not None and y is not None:
            # Use saved position
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            # Center on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")

    def save_gui_geometry(self):
        """Save current GUI size and position to config"""
        # Get current geometry
        geometry = self.root.geometry()
        # Format: WIDTHxHEIGHT+X+Y
        import re
        match = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
        if match:
            width, height, x, y = match.groups()
            self.active_settings["gui_width"] = int(width)
            self.active_settings["gui_height"] = int(height)
            self.active_settings["gui_x"] = int(x)
            self.active_settings["gui_y"] = int(y)

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

        # Save and reload
        self.save_config()
        keyboard.unhook_all()
        self.setup_hotkeys()

    def save_flow_settings(self):
        """Save flow configuration settings"""
        self.active_settings["flow_cast_enabled"] = self.cast_enabled_var.get()
        self.active_settings["flow_shake_enabled"] = self.shake_enabled_var.get()
        self.active_settings["flow_fish_enabled"] = self.fish_enabled_var.get()
        self.save_config()

    def save_shake_timeout(self):
        """Save shake timeout setting with validation"""
        try:
            timeout_value = float(self.shake_timeout_var.get())
            if timeout_value <= 0:
                print("[Error] Shake timeout must be greater than 0")
                return
            self.active_settings["shake_timeout"] = timeout_value
            self.save_config()
            print(f"[Settings] Shake timeout set to {timeout_value} seconds")
        except ValueError:
            print("[Error] Invalid shake timeout value - must be a number")
            # Reset to previous value
            self.shake_timeout_var.set(str(self.active_settings.get("shake_timeout", 3.0)))

    def save_shake_confidence(self):
        """Save shake confidence threshold with validation"""
        try:
            confidence_value = float(self.shake_confidence_var.get())
            if confidence_value < 0.0 or confidence_value > 1.0:
                print("[Error] Shake confidence must be between 0.0 and 1.0")
                return
            self.active_settings["shake_confidence_threshold"] = confidence_value
            self.save_config()
            print(f"[Settings] Shake confidence threshold set to {confidence_value:.2f}")
        except ValueError:
            print("[Error] Invalid confidence value - must be a number between 0.0 and 1.0")
            # Reset to previous value
            self.shake_confidence_var.set(str(self.active_settings.get("shake_confidence_threshold", 0.5)))

    def save_fishing_confidence(self):
        """Save fishing confidence threshold with validation"""
        try:
            confidence_value = float(self.fishing_confidence_var.get())
            if confidence_value < 0.0 or confidence_value > 1.0:
                print("[Error] Fishing confidence must be between 0.0 and 1.0")
                return
            self.active_settings["fishing_confidence_threshold"] = confidence_value
            self.save_config()
            print(f"[Settings] Fishing confidence threshold set to {confidence_value:.2f}")
        except ValueError:
            print("[Error] Invalid confidence value - must be a number between 0.0 and 1.0")
            # Reset to previous value
            self.fishing_confidence_var.set(str(self.active_settings.get("fishing_confidence_threshold", 0.5)))

    def start_loop(self):
        """Start the fishing loop"""
        if self.loop_running:
            print("Loop already running")
            return

        self.loop_running = True
        self.update_loop_status(True)
        print("Loop started!")

        # Auto minimize if enabled
        if self.active_settings.get("auto_minimize", False):
            self.root.iconify()

        # Start loop in a separate thread
        self.loop_thread = threading.Thread(target=self.run_loop, daemon=True)
        self.loop_thread.start()

    def stop_loop(self):
        """Stop the fishing loop"""
        if not self.loop_running:
            print("Loop not running")
            return

        self.loop_running = False
        self.update_loop_status(False)
        print("Loop stopped!")

        # Auto restore if enabled and minimized
        if self.active_settings.get("auto_minimize", False):
            self.root.deiconify()

    def run_loop(self):
        """Main loop execution"""
        # Load models once at the start
        try:
            shake_model = YOLO("shake_model.pt")
            fishing_model = YOLO("fishing_model.pt")
            print("[Loop] Models loaded successfully")
        except Exception as e:
            print(f"[Loop] Error loading models: {e}")
            self.loop_running = False
            self.update_loop_status(False)
            return

        while self.loop_running:
            # Cast step
            if self.active_settings.get("flow_cast_enabled", True):
                print("[Loop] Executing: Cast")
                pyautogui.mouseDown()
                time.sleep(1)
                pyautogui.mouseUp()
                time.sleep(1)

            if not self.loop_running:
                break

            # Shake step
            if self.active_settings.get("flow_shake_enabled", True):
                print("[Loop] Executing: Shake")
                shake_timeout = self.active_settings.get("shake_timeout", 3.0)
                shake_start_time = time.time()
                shake_complete = False
                # Reset last shake position when entering shake stage
                self.last_shake_position = None

                while not shake_complete and self.loop_running:
                    # Check timeout
                    if time.time() - shake_start_time > shake_timeout:
                        print("[Loop] Shake timeout - returning to cast")
                        break

                    # Capture shake_box area for shake detection
                    shake_box = self.active_settings.get("shake_box")
                    shake_x1, shake_y1 = shake_box["x1"], shake_box["y1"]
                    shake_x2, shake_y2 = shake_box["x2"], shake_box["y2"]

                    shake_screenshot = ImageGrab.grab(bbox=(shake_x1, shake_y1, shake_x2, shake_y2))
                    shake_frame = cv2.cvtColor(np.array(shake_screenshot), cv2.COLOR_RGB2BGR)

                    # Run shake model detection on shake_box
                    shake_results = shake_model(shake_frame, verbose=False)

                    shake_found = False
                    shake_confidence_threshold = self.active_settings.get("shake_confidence_threshold", 0.5)

                    for result in shake_results:
                        if len(result.boxes) > 0:
                            # Get the first detection
                            box = result.boxes[0]
                            confidence = float(box.conf[0].item())

                            # Check confidence threshold
                            if confidence < shake_confidence_threshold:
                                print(f"[Debug] Shake detected but confidence {confidence:.2f} below threshold {shake_confidence_threshold:.2f} - ignoring")
                                continue

                            # Shake detected with sufficient confidence - get position
                            x_center = int(box.xywh[0][0].item())
                            y_center = int(box.xywh[0][1].item())

                            # Convert to screen coordinates
                            screen_x = shake_x1 + x_center
                            screen_y = shake_y1 + y_center

                            # Check if this is a new position (not the same box we just clicked)
                            current_position = (screen_x, screen_y)
                            if self.last_shake_position is not None:
                                # Calculate distance from last clicked position
                                dist_x = abs(current_position[0] - self.last_shake_position[0])
                                dist_y = abs(current_position[1] - self.last_shake_position[1])

                                # If shake hasn't moved much (within 10 pixels), skip it
                                if dist_x < 10 and dist_y < 10:
                                    shake_found = True  # Still consider shake as found
                                    shake_start_time = time.time()  # Reset timeout
                                    break

                            print(f"[Loop] Shake detected at ({screen_x}, {screen_y}) with confidence {confidence:.2f}")
                            # Move mouse to position
                            pyautogui.moveTo(screen_x, screen_y)
                            # Nudge mouse by 1 pixel so Roblox registers the position
                            windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            # Click after Roblox registers the position
                            pyautogui.click()

                            # Update last clicked position
                            self.last_shake_position = current_position
                            shake_found = True
                            # Reset timeout since shake was detected
                            shake_start_time = time.time()
                            break

                    # If shake was found, continue loop as fast as possible (no sleep)
                    if shake_found:
                        continue

                    # Only check fishing model if shake was NOT found
                    # Capture fish_box area for fishing detection
                    fish_box = self.active_settings.get("fish_box")
                    fish_x1, fish_y1 = fish_box["x1"], fish_box["y1"]
                    fish_x2, fish_y2 = fish_box["x2"], fish_box["y2"]

                    fish_screenshot = ImageGrab.grab(bbox=(fish_x1, fish_y1, fish_x2, fish_y2))
                    fish_frame = cv2.cvtColor(np.array(fish_screenshot), cv2.COLOR_RGB2BGR)

                    # Run fishing model detection on fish_box
                    fishing_results = fishing_model(fish_frame, verbose=False)

                    target_line_found = False
                    fish_bar_found = False
                    target_line_conf = 0.0
                    fish_bar_conf = 0.0

                    # Get confidence threshold from settings
                    confidence_threshold = self.active_settings.get("fishing_confidence_threshold", 0.5)

                    for result in fishing_results:
                        for box in result.boxes:
                            class_id = int(box.cls[0].item())
                            class_name = fishing_model.names[class_id]
                            confidence = float(box.conf[0].item())

                            # Only accept detections above confidence threshold
                            if confidence < confidence_threshold:
                                print(f"[Debug] {class_name} detected but confidence {confidence:.2f} below threshold {confidence_threshold:.2f} - ignoring")
                                continue

                            # Keep the highest confidence detection for each class
                            if class_name == "Target Line":
                                if confidence > target_line_conf:
                                    target_line_found = True
                                    target_line_conf = confidence
                                    print(f"[Debug] Target Line detected with confidence: {confidence:.2f}")
                            elif class_name == "Fish Bar":
                                if confidence > fish_bar_conf:
                                    fish_bar_found = True
                                    fish_bar_conf = confidence
                                    print(f"[Debug] Fish Bar detected with confidence: {confidence:.2f}")

                    # Check if both Target Line AND Fish Bar are detected
                    if target_line_found and fish_bar_found:
                        print(f"[Loop] Both Target Line ({target_line_conf:.2f}) and Fish Bar ({fish_bar_conf:.2f}) detected - proceeding to Fish stage")
                        shake_complete = True
                    else:
                        # Debug: show what was detected
                        if target_line_found or fish_bar_found:
                            detected = []
                            if target_line_found:
                                detected.append(f"Target Line ({target_line_conf:.2f})")
                            if fish_bar_found:
                                detected.append(f"Fish Bar ({fish_bar_conf:.2f})")
                            print(f"[Loop] Only detected: {', '.join(detected)} - need both to proceed")
                        else:
                            print("[Loop] No fishing bars detected")

                    # Small delay before next iteration
                    time.sleep(0.1)

                # If shake didn't complete (timed out), restart from cast
                if not shake_complete:
                    continue

            if not self.loop_running:
                break

            # Fish step
            if self.active_settings.get("flow_fish_enabled", True):
                print("[Loop] Fishing stage reached")
                self.loop_running = False
                self.update_loop_status(False)
                break

            if not self.loop_running:
                break

            print("[Loop] Cycle complete, restarting...")

    def update_loop_status(self, running):
        """Update the loop status indicator in the GUI"""
        if running:
            self.loop_status_label.config(
                text="● Loop Status: Running",
                fg="#4CAF50"
            )
        else:
            self.loop_status_label.config(
                text="● Loop Status: Stopped",
                fg="#f44336"
            )

    def on_closing(self):
        """Handle window close event - save active settings"""
        # Stop loop if running
        self.loop_running = False
        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=2)

        # Save GUI size and position before closing
        self.save_gui_geometry()
        self.save_config()
        keyboard.unhook_all()
        self.root.destroy()


class AreaSelector:
    """Full-screen overlay for selecting a single box area with frozen screenshot"""

    def __init__(self, parent, screenshot, initial_box, callback, color="#2196F3", label="Fish Box"):
        self.callback = callback
        self.screenshot = screenshot
        self.color = color
        self.label_text = label

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

        # Create the box rectangle with transparent fill
        self.rect = self.canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            outline=self.color,
            width=2,
            fill=self.color,
            stipple='gray50',
            tags='box'
        )

        # Create label
        label_x = self.x1 + (self.x2 - self.x1) // 2
        label_y = self.y1 - 20
        self.label = self.canvas.create_text(
            label_x, label_y,
            text=self.label_text,
            font=("Arial", 12, "bold"),
            fill=self.color,
            tags='label'
        )

        # Create corner handles
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
        """Create corner handles for resizing"""
        handle_size = 12
        corner_marker_size = 3

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

        # Create new handles
        for x, y, corner in corners:
            # Outer handle
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline=self.color,
                width=2,
                tags=f'handle_{corner}'
            )
            self.handles.append(handle)

            # Corner marker
            corner_marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='red',
                outline='white',
                width=1,
                tags=f'corner_{corner}'
            )
            self.handles.append(corner_marker)

            # Crosshair
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

        corner = self.get_corner_at_position(event.x, event.y)
        if corner:
            self.dragging = True
            self.drag_corner = corner
        elif self.is_inside_box(event.x, event.y):
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

        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1

        self.update_box()
        self.show_zoom(event.x, event.y)

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
            cursors = {'nw': 'top_left_corner', 'ne': 'top_right_corner',
                      'sw': 'bottom_left_corner', 'se': 'bottom_right_corner'}
            self.window.configure(cursor=cursors.get(corner, 'cross'))
        elif self.is_inside_box(event.x, event.y):
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
            fill='black',
            outline='white',
            width=2
        )

        self.zoom_image_id = self.canvas.create_image(
            zoom_x, zoom_y,
            image=self.zoom_photo,
            anchor='nw'
        )

    def update_box(self):
        """Update the box and label positions"""
        self.canvas.coords(self.rect, self.x1, self.y1, self.x2, self.y2)

        label_x = self.x1 + (self.x2 - self.x1) // 2
        label_y = self.y1 - 20
        self.canvas.coords(self.label, label_x, label_y)

        self.create_handles()

    def finish_selection(self):
        """Close the selector and return coordinates"""
        box_coords = {
            "x1": int(self.x1),
            "y1": int(self.y1),
            "x2": int(self.x2),
            "y2": int(self.y2)
        }
        self.window.destroy()
        self.callback(box_coords)

    def close_without_saving(self):
        """Close without saving"""
        self.window.destroy()


class DualAreaSelector:
    """Full-screen overlay for selecting both Fish Box and Shake Box simultaneously"""

    def __init__(self, parent, screenshot, fish_box, shake_box, callback):
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

        # Initialize Fish Box
        self.fish_box = fish_box.copy()
        self.fish_x1, self.fish_y1 = self.fish_box["x1"], self.fish_box["y1"]
        self.fish_x2, self.fish_y2 = self.fish_box["x2"], self.fish_box["y2"]

        # Initialize Shake Box
        self.shake_box = shake_box.copy()
        self.shake_x1, self.shake_y1 = self.shake_box["x1"], self.shake_box["y1"]
        self.shake_x2, self.shake_y2 = self.shake_box["x2"], self.shake_box["y2"]

        # Drawing state
        self.dragging = False
        self.active_box = None  # 'fish' or 'shake'
        self.drag_corner = None
        self.resize_threshold = 10

        # Create Fish Box (Blue)
        self.fish_rect = self.canvas.create_rectangle(
            self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2,
            outline='#2196F3',
            width=2,
            fill='#2196F3',
            stipple='gray50',
            tags='fish_box'
        )

        # Fish Box label
        fish_label_x = self.fish_x1 + (self.fish_x2 - self.fish_x1) // 2
        fish_label_y = self.fish_y1 - 20
        self.fish_label = self.canvas.create_text(
            fish_label_x, fish_label_y,
            text="Fish Box",
            font=("Arial", 12, "bold"),
            fill='#2196F3',
            tags='fish_label'
        )

        # Create Shake Box (Red)
        self.shake_rect = self.canvas.create_rectangle(
            self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2,
            outline='#f44336',
            width=2,
            fill='#f44336',
            stipple='gray50',
            tags='shake_box'
        )

        # Shake Box label
        shake_label_x = self.shake_x1 + (self.shake_x2 - self.shake_x1) // 2
        shake_label_y = self.shake_y1 - 20
        self.shake_label = self.canvas.create_text(
            shake_label_x, shake_label_y,
            text="Shake Box",
            font=("Arial", 12, "bold"),
            fill='#f44336',
            tags='shake_label'
        )

        # Create corner handles for both boxes
        self.fish_handles = []
        self.shake_handles = []
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
        else:  # shake
            x1, y1, x2, y2 = self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2
            color = '#f44336'
            handles_list = self.shake_handles

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
        if box_type == 'fish':
            x1, y1, x2, y2 = self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2
        else:  # shake
            x1, y1, x2, y2 = self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2

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
        if box_type == 'fish':
            return self.fish_x1 < x < self.fish_x2 and self.fish_y1 < y < self.fish_y2
        else:  # shake
            return self.shake_x1 < x < self.shake_x2 and self.shake_y1 < y < self.shake_y2

    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Check Fish Box first
        corner = self.get_corner_at_position(event.x, event.y, 'fish')
        if corner:
            self.dragging = True
            self.active_box = 'fish'
            self.drag_corner = corner
            return

        if self.is_inside_box(event.x, event.y, 'fish'):
            self.dragging = True
            self.active_box = 'fish'
            self.drag_corner = 'move'
            return

        # Check Shake Box
        corner = self.get_corner_at_position(event.x, event.y, 'shake')
        if corner:
            self.dragging = True
            self.active_box = 'shake'
            self.drag_corner = corner
            return

        if self.is_inside_box(event.x, event.y, 'shake'):
            self.dragging = True
            self.active_box = 'shake'
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
                self.fish_x1 = event.x
                self.fish_y1 = event.y
            elif self.drag_corner == 'ne':
                self.fish_x2 = event.x
                self.fish_y1 = event.y
            elif self.drag_corner == 'sw':
                self.fish_x1 = event.x
                self.fish_y2 = event.y
            elif self.drag_corner == 'se':
                self.fish_x2 = event.x
                self.fish_y2 = event.y

            if self.fish_x1 > self.fish_x2:
                self.fish_x1, self.fish_x2 = self.fish_x2, self.fish_x1
            if self.fish_y1 > self.fish_y2:
                self.fish_y1, self.fish_y2 = self.fish_y2, self.fish_y1

        else:  # shake
            if self.drag_corner == 'move':
                self.shake_x1 += dx
                self.shake_y1 += dy
                self.shake_x2 += dx
                self.shake_y2 += dy
            elif self.drag_corner == 'nw':
                self.shake_x1 = event.x
                self.shake_y1 = event.y
            elif self.drag_corner == 'ne':
                self.shake_x2 = event.x
                self.shake_y1 = event.y
            elif self.drag_corner == 'sw':
                self.shake_x1 = event.x
                self.shake_y2 = event.y
            elif self.drag_corner == 'se':
                self.shake_x2 = event.x
                self.shake_y2 = event.y

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
        # Check which box cursor is over
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
            fill='black',
            outline='white',
            width=2
        )

        self.zoom_image_id = self.canvas.create_image(
            zoom_x, zoom_y,
            image=self.zoom_photo,
            anchor='nw'
        )

    def update_boxes(self):
        """Update both boxes and their labels"""
        # Update Fish Box
        self.canvas.coords(self.fish_rect, self.fish_x1, self.fish_y1, self.fish_x2, self.fish_y2)
        fish_label_x = self.fish_x1 + (self.fish_x2 - self.fish_x1) // 2
        fish_label_y = self.fish_y1 - 20
        self.canvas.coords(self.fish_label, fish_label_x, fish_label_y)

        # Update Shake Box
        self.canvas.coords(self.shake_rect, self.shake_x1, self.shake_y1, self.shake_x2, self.shake_y2)
        shake_label_x = self.shake_x1 + (self.shake_x2 - self.shake_x1) // 2
        shake_label_y = self.shake_y1 - 20
        self.canvas.coords(self.shake_label, shake_label_x, shake_label_y)

        # Update handles
        self.create_all_handles()

    def finish_selection(self):
        """Close and return both box coordinates"""
        fish_coords = {
            "x1": int(self.fish_x1),
            "y1": int(self.fish_y1),
            "x2": int(self.fish_x2),
            "y2": int(self.fish_y2)
        }
        shake_coords = {
            "x1": int(self.shake_x1),
            "y1": int(self.shake_y1),
            "x2": int(self.shake_x2),
            "y2": int(self.shake_y2)
        }
        self.window.destroy()
        self.callback(fish_coords, shake_coords)


def main():
    root = tk.Tk()
    app = HotkeyConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()