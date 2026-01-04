import tkinter as tk
from tkinter import ttk
import os
import json
from PIL import ImageGrab, Image, ImageTk, ImageDraw
import keyboard
import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO
from ctypes import windll
from pynput import keyboard as pynput_keyboard
import mss

# Mouse event constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

# windll helper functions to replace pyautogui
def mouse_down():
    """Replace pyautogui.mouseDown() - left click down"""
    windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

def mouse_up():
    """Replace pyautogui.mouseUp() - left click up"""
    windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def mouse_down_right():
    """Replace pyautogui.mouseDown(button='right') - right click down"""
    windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)

def mouse_up_right():
    """Replace pyautogui.mouseUp(button='right') - right click up"""
    windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

def mouse_click():
    """Replace pyautogui.click() - left click"""
    windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def mouse_move_to(x, y):
    """Replace pyautogui.moveTo(x, y) - absolute mouse positioning"""
    # Convert screen coords to normalized 0-65535 range
    screen_width = windll.user32.GetSystemMetrics(0)
    screen_height = windll.user32.GetSystemMetrics(1)
    normalized_x = int(x * 65535 / screen_width)
    normalized_y = int(y * 65535 / screen_height)
    windll.user32.mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, normalized_x, normalized_y, 0, 0)

def mouse_scroll(clicks):
    """Replace pyautogui.scroll(clicks) - mouse wheel scroll"""
    # Positive = scroll up, negative = scroll down
    # Windows uses WHEEL_DELTA = 120 per "click"
    windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, clicks * 120, 0)

# ==================== FISHING CONTROL SYSTEM ====================

class HotkeyConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IRUS V7 - Fishing Automation")
        self.root.geometry("750x650")

        # Get screen resolution for scaling
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Reference resolution (2560x1440 - your resolution)
        ref_width = 2560
        ref_height = 1440

        # Scale factors (store as instance variables for use throughout the app)
        self.scale_x = screen_width / ref_width
        self.scale_y = screen_height / ref_height
        self.scale_avg = (self.scale_x + self.scale_y) / 2  # Average scale for pixel thresholds

        # Keep local variables for initial setup
        scale_x = self.scale_x
        scale_y = self.scale_y

        # Original coordinates at 2560x1440
        fish_box_ref = {"x1": 762, "y1": 1215, "x2": 1797, "y2": 1258}
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
            "flow_misc_enabled": True,
            "flow_cast_enabled": True,
            "flow_shake_enabled": True,
            "flow_fish_enabled": True,
            "shake_timeout": 3.0,
            "fish_timeout": 3.0,
            "shake_confidence_threshold": 0.8,  # Lowered from 0.8 for fewer missed detections
            "fishing_confidence_threshold": 0,  # Lowered to match b.py for better Target Line detection
            "auto_minimize": True,
            "cast_mode": "Normal",
            "cast_delay1": 0.0,
            "cast_delay2": 0.3,
            "cast_delay3": 0.0,
            "cast_perfect_delay1": 0.0,
            "cast_zoom_out_scrolls": 20,
            "cast_zoom_out_enabled": True,
            "cast_perfect_delay2": 0.0,
            "cast_zoom_in_scrolls": 6,
            "cast_zoom_in_enabled": True,
            "cast_perfect_delay3": 0.0,
            "cast_look_down_enabled": True,
            "cast_perfect_delay4": 0.0,
            "cast_perfect_delay5": 0.0,
            "cast_perfect_delay6": 0.0,
            "discord_enabled": False,
            "discord_webhook_url": "",
            "discord_mode": "Text",
            "discord_screenshot_loops": 10,
            "discord_text_loops": 10,
            "look_down_distance": 2000,
            "shake_position_threshold": 20,
            "auto_refresh_rod_enabled": False,
            "misc_key1": "2",
            "misc_key2": "1",
            "misc_delay1": 0.0,
            "misc_delay2": 1.0,
            "misc_delay3": 1.0,

            # Fishing Control Parameters (V4-Style PD Controller)
            "fish_kp": 0.8,                    # Proportional gain (KP)
            "fish_kd": 0.0,                    # Derivative gain (KD) - disabled for YOLO
            "fish_target_tol_px": 10.0,        # Dead zone tolerance in pixels
            "fish_pd_clamp": 100.0,            # Maximum control signal clamp (±100)
            "fish_boundary_factor": 0.15,      # Boundary override margin (15% of box length)
            "fish_cooldown_duration": 1.0,     # Grace period for lost tracking (seconds)
            "fish_show_live_feed": True
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
        self.loop_counter = 0  # Track completed loops for Discord notifications

        # V4-Style Fishing State Machine Variables
        self.fishing_state = "IDLE"                  # State: IDLE or FISHING
        self.estimated_box_length = 0.0              # Estimated fish bar length
        self.has_calculated_length_once = False      # Whether box length has been calculated
        self.last_left_x = None                      # Last detected left edge of fish bar
        self.last_right_x = None                     # Last detected right edge of fish bar
        self.box_center_x = None                     # Center of fish bar
        self.lost_target_line_time = 0.0             # Timer for target line lost cooldown
        self.tracking_lost_time = 0.0                # Timer for tracking lost grace period
        self.last_error = None                       # Last PD control error
        self.last_target_x = None                    # Last target line position
        self.is_holding_click = False                # Current mouse button state

        # Debug overlay window for fish detection visualization
        self.debug_overlay_window = None
        self.debug_overlay_canvas = None

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
        """Load config from file or use first launch defaults"""
        if not os.path.exists(self.config_file):
            # First launch - use defaults (don't create config yet - will save on exit)
            self.active_settings = self.first_launch_config.copy()
            print("[Config] First launch - using defaults (will create config on exit)")
        else:
            # Load existing config into active settings
            try:
                with open(self.config_file, 'r') as f:
                    self.active_settings = json.load(f)
                print("[Config] Loaded existing config from file")
            except Exception as e:
                print(f"[Config] Error loading config: {e}")
                # Fall back to defaults if config is corrupted
                self.active_settings = self.first_launch_config.copy()
                print("[Config] Using defaults due to corrupted config")

    def save_config(self):
        """Save active settings to Config.txt"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.active_settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_scrollable_frame(self, parent):
        """Create a scrollable frame with canvas and scrollbar"""
        # Create canvas and scrollbars for scrolling
        canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y", before=canvas)
        h_scrollbar.pack(side="bottom", fill="x")

        # Enable mousewheel scrolling - bind to canvas, not all widgets
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind to the canvas and the scrollable frame to capture mouse events
        def on_enter(e):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            canvas.bind_all("<Shift-MouseWheel>", on_shift_mousewheel)

        def on_leave(e):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Shift-MouseWheel>")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        return scrollable_frame

    def build_gui(self):
        """Build the GUI interface"""
        # Configure root window
        self.root.configure(bg="#f0f2f5")
        self.root.resizable(True, True)
        self.root.minsize(700, 550)

        # Header frame with gradient effect (simulated with two frames)
        header_frame = tk.Frame(self.root, bg="#1976D2", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Title and subtitle container
        title_container = tk.Frame(header_frame, bg="#1976D2")
        title_container.pack(expand=True)

        # Title label
        title_label = tk.Label(
            title_container,
            text="IRUS V7",
            font=("Segoe UI", 22, "bold"),
            bg="#1976D2",
            fg="white"
        )
        title_label.pack(pady=(15, 0))

        # Subtitle
        subtitle_label = tk.Label(
            title_container,
            text="Advanced Fishing Automation System",
            font=("Segoe UI", 9),
            bg="#1976D2",
            fg="#E3F2FD"
        )
        subtitle_label.pack(pady=(2, 15))

        # Create notebook (tabbed interface)
        style = ttk.Style()
        style.theme_create("irus_theme", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": "#f0f2f5"}},
            "TNotebook.Tab": {
                "configure": {"padding": [25, 12], "background": "#e8eaf0", "foreground": "#424242", "font": ("Segoe UI", 10)},
                "map": {
                    "background": [("selected", "#1976D2"), ("active", "#d0d0d0")],
                    "foreground": [("selected", "white"), ("active", "#1976D2")],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        style.theme_use("irus_theme")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        # Create tabs
        self.create_basic_settings_tab()
        self.create_flow_configuration_tab()
        self.create_discord_settings_tab()
        self.create_support_tab()

    def create_basic_settings_tab(self):
        """Create the Basic Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="⚙️ Settings")

        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(tab)

        # Main container
        container = tk.Frame(scrollable_frame, bg="white")
        container.pack(fill="both", expand=True, padx=35, pady=25)

        # Title with description
        title_frame = tk.Frame(container, bg="white")
        title_frame.pack(fill="x", pady=(0, 25))

        title = tk.Label(
            title_frame,
            text="⌨️ Hotkey Configuration",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#1976D2"
        )
        title.pack(anchor="w")

        desc = tk.Label(
            title_frame,
            text="Configure keyboard shortcuts to control the automation",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        desc.pack(anchor="w", pady=(5, 0))

        # Settings frame with border
        settings_outer_frame = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        settings_outer_frame.pack(fill="x", pady=(0, 20))

        settings_frame = tk.Frame(settings_outer_frame, bg="#f8f9fa")
        settings_frame.pack(fill="x", padx=20, pady=20)

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
            "Start": "▶",
            "Stop": "⏹",
            "Modify Area": "🎯",
            "Exit": "🚪"
        }
        action_colors = {
            "Start": "#4CAF50",
            "Stop": "#f44336",
            "Modify Area": "#FF9800",
            "Exit": "#9E9E9E"
        }

        # Create a row for each hotkey setting
        for idx, action in enumerate(display_actions):
            # Get current key value
            current_key = self.active_settings.get(action, self.first_launch_config.get(action, "F1"))

            # Row container
            row_frame = tk.Frame(settings_frame, bg="#f8f9fa")
            row_frame.grid(row=idx, column=0, columnspan=2, sticky="ew", pady=8)

            # Icon with colored background
            icon = action_icons.get(action, "⚙")
            color = action_colors.get(action, "#757575")
            icon_label = tk.Label(
                row_frame,
                text=icon,
                font=("Segoe UI", 14),
                bg=color,
                fg="white",
                width=2,
                height=1,
                relief="flat"
            )
            icon_label.pack(side="left", padx=(0, 15))

            # Action label
            action_label = tk.Label(
                row_frame,
                text=action,
                font=("Segoe UI", 11),
                bg="#f8f9fa",
                fg="#424242",
                anchor="w",
                width=15
            )
            action_label.pack(side="left")

            # Dropdown for key selection
            key_var = tk.StringVar(value=current_key)
            key_dropdown = ttk.Combobox(
                row_frame,
                textvariable=key_var,
                values=self.available_keys,
                state="readonly",
                font=("Segoe UI", 10),
                width=15
            )
            key_dropdown.set(current_key)
            key_dropdown.pack(side="left", padx=10)

            # Store reference to dropdown widget
            self.dropdown_widgets[action] = key_var

        # Configure grid column weights
        settings_frame.columnconfigure(0, weight=1)

        # Options section
        options_title_frame = tk.Frame(container, bg="white")
        options_title_frame.pack(fill="x", pady=(5, 20))

        options_title = tk.Label(
            options_title_frame,
            text="🔧 Application Options",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#1976D2"
        )
        options_title.pack(anchor="w")

        options_desc = tk.Label(
            options_title_frame,
            text="Customize window behavior and preferences",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        options_desc.pack(anchor="w", pady=(5, 0))

        # Options frame with border
        options_outer_frame = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        options_outer_frame.pack(fill="x", pady=(0, 25))

        options_frame = tk.Frame(options_outer_frame, bg="#f8f9fa")
        options_frame.pack(fill="x", padx=20, pady=20)

        # Always on top option
        self.always_on_top_var = tk.BooleanVar(value=self.active_settings.get("always_on_top", self.first_launch_config.get("always_on_top", False)))
        always_on_top_frame = tk.Frame(options_frame, bg="#f8f9fa")
        always_on_top_frame.pack(fill="x", pady=8)

        always_on_top_check = tk.Checkbutton(
            always_on_top_frame,
            text="📌 Always on Top",
            variable=self.always_on_top_var,
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            fg="#424242",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.toggle_always_on_top,
            cursor="hand2"
        )
        always_on_top_check.pack(anchor="w", side="left")

        always_on_top_hint = tk.Label(
            always_on_top_frame,
            text="Keep window above other applications",
            font=("Segoe UI", 9, "italic"),
            bg="#f8f9fa",
            fg="#757575"
        )
        always_on_top_hint.pack(anchor="w", side="left", padx=(10, 0))

        # Auto minimize option
        self.auto_minimize_var = tk.BooleanVar(value=self.active_settings.get("auto_minimize", self.first_launch_config.get("auto_minimize", False)))
        auto_minimize_frame = tk.Frame(options_frame, bg="#f8f9fa")
        auto_minimize_frame.pack(fill="x", pady=8)

        auto_minimize_check = tk.Checkbutton(
            auto_minimize_frame,
            text="🗕 Auto Minimize",
            variable=self.auto_minimize_var,
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            fg="#424242",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.toggle_auto_minimize,
            cursor="hand2"
        )
        auto_minimize_check.pack(anchor="w", side="left")

        auto_minimize_hint = tk.Label(
            auto_minimize_frame,
            text="Minimize window automatically when starting automation",
            font=("Segoe UI", 9, "italic"),
            bg="#f8f9fa",
            fg="#757575"
        )
        auto_minimize_hint.pack(anchor="w", side="left", padx=(10, 0))

        # Buttons and notice frame
        bottom_frame = tk.Frame(container, bg="white")
        bottom_frame.pack(fill="x", pady=10)

        # Reset to defaults button
        reset_btn = tk.Button(
            bottom_frame,
            text="🔄 Reset to Defaults",
            font=("Segoe UI", 10, "bold"),
            command=self.reset_to_defaults,
            bg="#FF9800",
            fg="white",
            padx=30,
            pady=10,
            relief="flat",
            cursor="hand2",
            activebackground="#F57C00",
            borderwidth=0
        )
        reset_btn.pack()

        # Auto-save notice with icon
        notice_frame = tk.Frame(container, bg="#E8F5E9", relief="solid", bd=1, highlightbackground="#C8E6C9", highlightthickness=1)
        notice_frame.pack(fill="x", pady=(15, 0))

        notice_content = tk.Frame(notice_frame, bg="#E8F5E9")
        notice_content.pack(padx=15, pady=12)

        notice_icon = tk.Label(
            notice_content,
            text="✓",
            font=("Segoe UI", 12, "bold"),
            bg="#E8F5E9",
            fg="#4CAF50"
        )
        notice_icon.pack(side="left", padx=(0, 10))

        notice = tk.Label(
            notice_content,
            text="All settings are automatically saved",
            font=("Segoe UI", 10),
            bg="#E8F5E9",
            fg="#2E7D32"
        )
        notice.pack(side="left")

    def create_flow_configuration_tab(self):
        """Create the Flow Configuration tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="🔄 Flow Config")

        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(tab)

        # Main container
        container = tk.Frame(scrollable_frame, bg="white")
        container.pack(fill="both", expand=True, padx=35, pady=25)

        # Title with description
        title_frame = tk.Frame(container, bg="white")
        title_frame.pack(fill="x", pady=(0, 20))

        title = tk.Label(
            title_frame,
            text="🎣 Fishing Automation Flow",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#1976D2"
        )
        title.pack(anchor="w")

        desc = tk.Label(
            title_frame,
            text="Configure the automated fishing sequence and timing",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        desc.pack(anchor="w", pady=(5, 0))

        # Flow visualization frame with better styling
        flow_visual_outer = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        flow_visual_outer.pack(fill="x", pady=(0, 20))

        flow_frame = tk.Frame(flow_visual_outer, bg="#f8f9fa")
        flow_frame.pack(pady=25, padx=20)

        # Misc step
        misc_frame = tk.Frame(flow_frame, bg="#f8f9fa")
        misc_frame.grid(row=0, column=0, padx=15, pady=10)

        self.misc_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_misc_enabled", True))
        misc_check = tk.Checkbutton(
            misc_frame,
            variable=self.misc_enabled_var,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.save_flow_settings,
            cursor="hand2"
        )
        misc_check.pack(side="left")

        misc_box = tk.Label(
            misc_frame,
            text="Misc",
            font=("Segoe UI", 11, "bold"),
            bg="#9C27B0",
            fg="white",
            padx=35,
            pady=18,
            relief="flat",
            borderwidth=0
        )
        misc_box.pack(side="left", padx=(8, 0))

        # Arrow 0 (Misc to Cast)
        arrow0 = tk.Label(
            flow_frame,
            text="→",
            font=("Segoe UI", 20),
            bg="#f8f9fa",
            fg="#9E9E9E"
        )
        arrow0.grid(row=0, column=1, padx=8)

        # Cast step
        cast_frame = tk.Frame(flow_frame, bg="#f8f9fa")
        cast_frame.grid(row=0, column=2, padx=15, pady=10)

        self.cast_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_cast_enabled", True))
        cast_check = tk.Checkbutton(
            cast_frame,
            variable=self.cast_enabled_var,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.save_flow_settings,
            cursor="hand2"
        )
        cast_check.pack(side="left")

        cast_box = tk.Label(
            cast_frame,
            text="Cast",
            font=("Segoe UI", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=35,
            pady=18,
            relief="flat",
            borderwidth=0
        )
        cast_box.pack(side="left", padx=(8, 0))

        # Arrow 1 (Cast to Shake)
        arrow1 = tk.Label(
            flow_frame,
            text="→",
            font=("Segoe UI", 20),
            bg="#f8f9fa",
            fg="#9E9E9E"
        )
        arrow1.grid(row=0, column=3, padx=8)

        # Shake step
        shake_frame = tk.Frame(flow_frame, bg="#f8f9fa")
        shake_frame.grid(row=0, column=4, padx=15, pady=10)

        self.shake_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_shake_enabled", True))
        shake_check = tk.Checkbutton(
            shake_frame,
            variable=self.shake_enabled_var,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.save_flow_settings,
            cursor="hand2"
        )
        shake_check.pack(side="left")

        shake_box = tk.Label(
            shake_frame,
            text="Shake",
            font=("Segoe UI", 11, "bold"),
            bg="#FF9800",
            fg="white",
            padx=35,
            pady=18,
            relief="flat",
            borderwidth=0
        )
        shake_box.pack(side="left", padx=(8, 0))

        # Arrow 2 (Shake to Fish)
        arrow2 = tk.Label(
            flow_frame,
            text="→",
            font=("Segoe UI", 20),
            bg="#f8f9fa",
            fg="#9E9E9E"
        )
        arrow2.grid(row=0, column=5, padx=8)

        # Fish step
        fish_frame = tk.Frame(flow_frame, bg="#f8f9fa")
        fish_frame.grid(row=0, column=6, padx=15, pady=10)

        self.fish_enabled_var = tk.BooleanVar(value=self.active_settings.get("flow_fish_enabled", True))
        fish_check = tk.Checkbutton(
            fish_frame,
            variable=self.fish_enabled_var,
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            command=self.save_flow_settings,
            cursor="hand2"
        )
        fish_check.pack(side="left")

        fish_box = tk.Label(
            fish_frame,
            text="Fish",
            font=("Segoe UI", 11, "bold"),
            bg="#1976D2",
            fg="white",
            padx=35,
            pady=18,
            relief="flat",
            borderwidth=0
        )
        fish_box.pack(side="left", padx=(8, 0))

        # Loop back arrow
        loop_arrow = tk.Label(
            flow_frame,
            text="↻",
            font=("Segoe UI", 22),
            bg="#f8f9fa",
            fg="#9E9E9E"
        )
        loop_arrow.grid(row=1, column=3, pady=15)

        # Description with better styling
        desc_frame = tk.Frame(container, bg="#E3F2FD", relief="solid", bd=1, highlightbackground="#90CAF9", highlightthickness=1)
        desc_frame.pack(fill="x", pady=(0, 15))

        desc_inner = tk.Frame(desc_frame, bg="#E3F2FD")
        desc_inner.pack(padx=20, pady=15)

        desc_icon = tk.Label(
            desc_inner,
            text="ℹ",
            font=("Segoe UI", 14, "bold"),
            bg="#E3F2FD",
            fg="#1976D2"
        )
        desc_icon.pack(side="left", padx=(0, 12))

        desc_text = tk.Label(
            desc_inner,
            text="The loop continuously cycles through enabled steps. Uncheck a step to skip it.\nUse your configured hotkeys to Start and Stop the automation.",
            font=("Segoe UI", 10),
            bg="#E3F2FD",
            fg="#1565C0",
            justify="left"
        )
        desc_text.pack(side="left")

        # Loop status indicator with better styling
        status_outer = tk.Frame(container, bg="white")
        status_outer.pack(pady=(0, 20))

        self.loop_status_label = tk.Label(
            status_outer,
            text="● Status: Stopped",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#f44336"
        )
        self.loop_status_label.pack()

        # Miscellaneous Flow Section
        misc_title_frame = tk.Frame(container, bg="white")
        misc_title_frame.pack(fill="x", pady=(0, 15))

        misc_flow_title = tk.Label(
            misc_title_frame,
            text="⚙️ Miscellaneous Flow Configuration",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#9C27B0"
        )
        misc_flow_title.pack(anchor="w")

        misc_desc = tk.Label(
            misc_title_frame,
            text="Configure miscellaneous actions before casting",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        misc_desc.pack(anchor="w", pady=(3, 0))

        misc_flow_frame = tk.Frame(container, bg="#faf5fb", relief="solid", bd=1, highlightbackground="#E1BEE7", highlightthickness=1)
        misc_flow_frame.pack(fill="x", pady=(0, 20))

        # Misc Flow Details Frame
        self.misc_flow_details_frame = tk.Frame(misc_flow_frame, bg="#faf5fb")
        self.misc_flow_details_frame.pack(fill="x", padx=20, pady=15)

        # Initialize the auto refresh rod variable
        self.auto_refresh_rod_var = tk.BooleanVar(value=self.active_settings.get("auto_refresh_rod_enabled", False))

        # Initialize misc flow details
        self.update_misc_flow_details()

        # Cast Flow Section
        cast_title_frame = tk.Frame(container, bg="white")
        cast_title_frame.pack(fill="x", pady=(0, 15))

        cast_flow_title = tk.Label(
            cast_title_frame,
            text="🎯 Cast Flow Configuration",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#4CAF50"
        )
        cast_flow_title.pack(anchor="w")

        cast_desc = tk.Label(
            cast_title_frame,
            text="Configure the casting sequence and delays",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        cast_desc.pack(anchor="w", pady=(3, 0))

        cast_flow_frame = tk.Frame(container, bg="#f8fdf8", relief="solid", bd=1, highlightbackground="#C8E6C9", highlightthickness=1)
        cast_flow_frame.pack(fill="x", pady=(0, 20))

        # Cast Mode Selection
        self.cast_mode_frame = tk.Frame(cast_flow_frame, bg="#f8fdf8")
        self.cast_mode_frame.pack(fill="x", padx=20, pady=15)

        cast_mode_label = tk.Label(
            self.cast_mode_frame,
            text="Cast Mode:",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fdf8",
            fg="#2E7D32"
        )
        cast_mode_label.pack(side="left", padx=(0, 10))

        self.cast_mode_var = tk.StringVar(value=self.active_settings.get("cast_mode", "Normal"))
        cast_mode_dropdown = ttk.Combobox(
            self.cast_mode_frame,
            textvariable=self.cast_mode_var,
            values=["Normal", "Perfect"],
            state="readonly",
            font=("Segoe UI", 10),
            width=18
        )
        cast_mode_dropdown.set(self.active_settings.get("cast_mode", "Normal"))
        cast_mode_dropdown.bind("<<ComboboxSelected>>", self.on_cast_mode_changed)
        cast_mode_dropdown.pack(side="left")

        # Cast Flow Details Frame (content changes based on mode)
        self.cast_flow_details_frame = tk.Frame(cast_flow_frame, bg="#f8fdf8")
        self.cast_flow_details_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Initialize cast flow details
        self.update_cast_flow_details()

        # Shake Flow Section
        shake_title_frame = tk.Frame(container, bg="white")
        shake_title_frame.pack(fill="x", pady=(0, 15))

        shake_flow_title = tk.Label(
            shake_title_frame,
            text="⚡ Shake Flow Configuration",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#FF9800"
        )
        shake_flow_title.pack(anchor="w")

        shake_desc = tk.Label(
            shake_title_frame,
            text="Configure shake detection and response timing",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        shake_desc.pack(anchor="w", pady=(3, 0))

        shake_flow_frame = tk.Frame(container, bg="#fffbf5", relief="solid", bd=1, highlightbackground="#FFE0B2", highlightthickness=1)
        shake_flow_frame.pack(fill="x", pady=(0, 20))

        # Shake Flow Details Frame (content changes based on enabled state)
        self.shake_flow_details_frame = tk.Frame(shake_flow_frame, bg="#fffbf5")
        self.shake_flow_details_frame.pack(fill="x", padx=20, pady=15)

        # Fish Flow Section
        fish_title_frame = tk.Frame(container, bg="white")
        fish_title_frame.pack(fill="x", pady=(0, 15))

        fish_flow_title = tk.Label(
            fish_title_frame,
            text="🐟 Fish Flow Configuration",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#1976D2"
        )
        fish_flow_title.pack(anchor="w")

        fish_desc = tk.Label(
            fish_title_frame,
            text="Configure fish detection and control system parameters",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        fish_desc.pack(anchor="w", pady=(3, 0))

        fish_flow_frame = tk.Frame(container, bg="#f5f9fd", relief="solid", bd=1, highlightbackground="#BBDEFB", highlightthickness=1)
        fish_flow_frame.pack(fill="x", pady=(0, 20))

        # Fish Flow Details Frame (content changes based on enabled state)
        self.fish_flow_details_frame = tk.Frame(fish_flow_frame, bg="#f5f9fd")
        self.fish_flow_details_frame.pack(fill="x", padx=20, pady=15)

        # Initialize flow details
        self.update_shake_flow_details()
        self.update_fish_flow_details()

    def on_cast_mode_changed(self, event=None):
        """Handle cast mode dropdown change from Flow Configuration tab"""
        new_mode = self.cast_mode_var.get()
        self.active_settings["cast_mode"] = new_mode
        self.update_cast_flow_details()

    def update_cast_flow_details(self):
        """Update cast flow details based on selected mode"""
        # Clear existing widgets
        for widget in self.cast_flow_details_frame.winfo_children():
            widget.destroy()

        # Check if Cast is enabled
        if not self.active_settings.get("flow_cast_enabled", True):
            # Hide the cast mode dropdown
            self.cast_mode_frame.pack_forget()

            disabled_label = tk.Label(
                self.cast_flow_details_frame,
                text="Disabled",
                font=("Segoe UI", 12, "italic"),
                bg="#f5f5f5",
                fg="#999999"
            )
            disabled_label.pack(anchor="w", pady=10)
            return

        # Show the cast mode dropdown when enabled
        self.cast_mode_frame.pack(fill="x", padx=20, pady=15)

        mode = self.cast_mode_var.get()

        if mode == "Normal":
            # Normal mode: Delay 1 > Hold Left Click > Delay 2 > Release Left Click > Delay 3
            flow_text = tk.Label(
                self.cast_flow_details_frame,
                text="Flow: Delay 1 → Hold Left Click → Delay 2 → Release Left Click → Delay 3",
                font=("Segoe UI", 9),
                bg="#f5f5f5",
                fg="#666666"
            )
            flow_text.pack(anchor="w", pady=(5, 10))

            # Delay settings frame
            delays_frame = tk.Frame(self.cast_flow_details_frame, bg="#f5f5f5")
            delays_frame.pack(fill="x")

            # Delay 1
            delay1_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            delay1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            delay1_label = tk.Label(
                delay1_frame,
                text="Delay 1:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=10,
                anchor="w"
            )
            delay1_label.pack(side="left")

            self.cast_delay1_var = tk.StringVar(value=str(self.active_settings.get("cast_delay1", 0.0)))
            self.cast_delay1_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_delay1", self.cast_delay1_var))
            delay1_entry = tk.Entry(
                delay1_frame,
                textvariable=self.cast_delay1_var,
                font=("Segoe UI", 10),
                width=8
            )
            delay1_entry.pack(side="left", padx=5)

            delay1_unit = tk.Label(
                delay1_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            delay1_unit.pack(side="left")

            # Delay 2
            delay2_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            delay2_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            delay2_label = tk.Label(
                delay2_frame,
                text="Delay 2:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=10,
                anchor="w"
            )
            delay2_label.pack(side="left")

            self.cast_delay2_var = tk.StringVar(value=str(self.active_settings.get("cast_delay2", 1.0)))
            self.cast_delay2_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_delay2", self.cast_delay2_var))
            delay2_entry = tk.Entry(
                delay2_frame,
                textvariable=self.cast_delay2_var,
                font=("Segoe UI", 10),
                width=8
            )
            delay2_entry.pack(side="left", padx=5)

            delay2_unit = tk.Label(
                delay2_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            delay2_unit.pack(side="left")

            # Delay 3
            delay3_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            delay3_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            delay3_label = tk.Label(
                delay3_frame,
                text="Delay 3:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=10,
                anchor="w"
            )
            delay3_label.pack(side="left")

            self.cast_delay3_var = tk.StringVar(value=str(self.active_settings.get("cast_delay3", 2.0)))
            self.cast_delay3_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_delay3", self.cast_delay3_var))
            delay3_entry = tk.Entry(
                delay3_frame,
                textvariable=self.cast_delay3_var,
                font=("Segoe UI", 10),
                width=8
            )
            delay3_entry.pack(side="left", padx=5)

            delay3_unit = tk.Label(
                delay3_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            delay3_unit.pack(side="left")

        elif mode == "Perfect":
            # Perfect mode: Delay 1 > Zoom Out > Delay 2 > Zoom In > Delay 3 > Look Down > Delay 4 > Hold Left Click > Delay 5 > Perfect Cast Release > Delay 6
            flow_text = tk.Label(
                self.cast_flow_details_frame,
                text="Flow: Delay 1 → Zoom Out → Delay 2 → Zoom In → Delay 3 → Look Down → Delay 4 → Hold Left Click → Delay 5 → Perfect Cast Release → Delay 6",
                font=("Segoe UI", 9),
                bg="#f5f5f5",
                fg="#666666"
            )
            flow_text.pack(anchor="w", pady=(5, 10))

            # Delay settings frame
            delays_frame = tk.Frame(self.cast_flow_details_frame, bg="#f5f5f5")
            delays_frame.pack(fill="x")

            # Perfect Delay 1
            pdelay1_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            pdelay1_label = tk.Label(
                pdelay1_frame,
                text="Delay 1:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay1_label.pack(side="left")

            self.cast_perfect_delay1_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay1", 0.0)))
            self.cast_perfect_delay1_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay1", self.cast_perfect_delay1_var))
            pdelay1_entry = tk.Entry(
                pdelay1_frame,
                textvariable=self.cast_perfect_delay1_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay1_entry.pack(side="left", padx=5)

            pdelay1_unit = tk.Label(
                pdelay1_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay1_unit.pack(side="left")

            # Zoom Out
            zoom_out_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            zoom_out_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            self.cast_zoom_out_enabled_var = tk.BooleanVar(value=self.active_settings.get("cast_zoom_out_enabled", True))
            zoom_out_check = tk.Checkbutton(
                zoom_out_frame,
                variable=self.cast_zoom_out_enabled_var,
                bg="#f5f5f5",
                command=lambda: self.save_cast_toggle_setting("cast_zoom_out_enabled", self.cast_zoom_out_enabled_var)
            )
            zoom_out_check.pack(side="left", padx=(0, 5))

            zoom_out_label = tk.Label(
                zoom_out_frame,
                text="Zoom Out:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            zoom_out_label.pack(side="left")

            self.cast_zoom_out_var = tk.StringVar(value=str(self.active_settings.get("cast_zoom_out_scrolls", 20)))
            self.cast_zoom_out_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_zoom_out_scrolls", self.cast_zoom_out_var, is_int=True))
            zoom_out_entry = tk.Entry(
                zoom_out_frame,
                textvariable=self.cast_zoom_out_var,
                font=("Segoe UI", 10),
                width=8
            )
            zoom_out_entry.pack(side="left", padx=5)

            zoom_out_unit = tk.Label(
                zoom_out_frame,
                text="scrolls",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            zoom_out_unit.pack(side="left")

            # Perfect Delay 2
            pdelay2_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay2_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            pdelay2_label = tk.Label(
                pdelay2_frame,
                text="Delay 2:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay2_label.pack(side="left")

            self.cast_perfect_delay2_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay2", 0.0)))
            self.cast_perfect_delay2_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay2", self.cast_perfect_delay2_var))
            pdelay2_entry = tk.Entry(
                pdelay2_frame,
                textvariable=self.cast_perfect_delay2_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay2_entry.pack(side="left", padx=5)

            pdelay2_unit = tk.Label(
                pdelay2_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay2_unit.pack(side="left")

            # Zoom In
            zoom_in_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            zoom_in_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            self.cast_zoom_in_enabled_var = tk.BooleanVar(value=self.active_settings.get("cast_zoom_in_enabled", True))
            zoom_in_check = tk.Checkbutton(
                zoom_in_frame,
                variable=self.cast_zoom_in_enabled_var,
                bg="#f5f5f5",
                command=lambda: self.save_cast_toggle_setting("cast_zoom_in_enabled", self.cast_zoom_in_enabled_var)
            )
            zoom_in_check.pack(side="left", padx=(0, 5))

            zoom_in_label = tk.Label(
                zoom_in_frame,
                text="Zoom In:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            zoom_in_label.pack(side="left")

            self.cast_zoom_in_var = tk.StringVar(value=str(self.active_settings.get("cast_zoom_in_scrolls", 6)))
            self.cast_zoom_in_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_zoom_in_scrolls", self.cast_zoom_in_var, is_int=True))
            zoom_in_entry = tk.Entry(
                zoom_in_frame,
                textvariable=self.cast_zoom_in_var,
                font=("Segoe UI", 10),
                width=8
            )
            zoom_in_entry.pack(side="left", padx=5)

            zoom_in_unit = tk.Label(
                zoom_in_frame,
                text="scrolls",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            zoom_in_unit.pack(side="left")

            # Perfect Delay 3
            pdelay3_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay3_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            pdelay3_label = tk.Label(
                pdelay3_frame,
                text="Delay 3:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay3_label.pack(side="left")

            self.cast_perfect_delay3_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay3", 0.0)))
            self.cast_perfect_delay3_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay3", self.cast_perfect_delay3_var))
            pdelay3_entry = tk.Entry(
                pdelay3_frame,
                textvariable=self.cast_perfect_delay3_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay3_entry.pack(side="left", padx=5)

            pdelay3_unit = tk.Label(
                pdelay3_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay3_unit.pack(side="left")

            # Look Down
            look_down_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            look_down_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")

            self.cast_look_down_enabled_var = tk.BooleanVar(value=self.active_settings.get("cast_look_down_enabled", True))
            look_down_check = tk.Checkbutton(
                look_down_frame,
                variable=self.cast_look_down_enabled_var,
                bg="#f5f5f5",
                command=lambda: self.save_cast_toggle_setting("cast_look_down_enabled", self.cast_look_down_enabled_var)
            )
            look_down_check.pack(side="left", padx=(0, 5))

            look_down_label = tk.Label(
                look_down_frame,
                text="Look Down:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            look_down_label.pack(side="left")

            self.look_down_distance_var = tk.StringVar(value=str(self.active_settings.get("look_down_distance", 2000)))
            self.look_down_distance_var.trace_add("write", lambda *args: self.save_cast_delay_setting("look_down_distance", self.look_down_distance_var, is_int=True))
            look_down_entry = tk.Entry(
                look_down_frame,
                textvariable=self.look_down_distance_var,
                font=("Segoe UI", 10),
                width=8
            )
            look_down_entry.pack(side="left", padx=5)

            look_down_unit = tk.Label(
                look_down_frame,
                text="px",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            look_down_unit.pack(side="left")

            # Perfect Delay 4
            pdelay4_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay4_frame.grid(row=3, column=0, padx=10, pady=5, sticky="w")

            pdelay4_label = tk.Label(
                pdelay4_frame,
                text="Delay 4:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay4_label.pack(side="left")

            self.cast_perfect_delay4_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay4", 0.0)))
            self.cast_perfect_delay4_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay4", self.cast_perfect_delay4_var))
            pdelay4_entry = tk.Entry(
                pdelay4_frame,
                textvariable=self.cast_perfect_delay4_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay4_entry.pack(side="left", padx=5)

            pdelay4_unit = tk.Label(
                pdelay4_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay4_unit.pack(side="left")

            # Hold Left Click
            hold_click_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            hold_click_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

            hold_click_label = tk.Label(
                hold_click_frame,
                text="Hold Left Click:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            hold_click_label.pack(side="left")

            hold_click_info = tk.Label(
                hold_click_frame,
                text="(Auto)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            hold_click_info.pack(side="left", padx=5)

            # Perfect Delay 5
            pdelay5_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay5_frame.grid(row=4, column=0, padx=10, pady=5, sticky="w")

            pdelay5_label = tk.Label(
                pdelay5_frame,
                text="Delay 5:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay5_label.pack(side="left")

            self.cast_perfect_delay5_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay5", 0.0)))
            self.cast_perfect_delay5_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay5", self.cast_perfect_delay5_var))
            pdelay5_entry = tk.Entry(
                pdelay5_frame,
                textvariable=self.cast_perfect_delay5_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay5_entry.pack(side="left", padx=5)

            pdelay5_unit = tk.Label(
                pdelay5_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay5_unit.pack(side="left")

            # Perfect Cast Release
            release_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            release_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")

            release_label = tk.Label(
                release_frame,
                text="Perfect Cast Release:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=17,
                anchor="w"
            )
            release_label.pack(side="left")

            release_info = tk.Label(
                release_frame,
                text="(Auto)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            release_info.pack(side="left", padx=5)

            # Perfect Delay 6
            pdelay6_frame = tk.Frame(delays_frame, bg="#f5f5f5")
            pdelay6_frame.grid(row=5, column=0, padx=10, pady=5, sticky="w")

            pdelay6_label = tk.Label(
                pdelay6_frame,
                text="Delay 6:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=12,
                anchor="w"
            )
            pdelay6_label.pack(side="left")

            self.cast_perfect_delay6_var = tk.StringVar(value=str(self.active_settings.get("cast_perfect_delay6", 0.0)))
            self.cast_perfect_delay6_var.trace_add("write", lambda *args: self.save_cast_delay_setting("cast_perfect_delay6", self.cast_perfect_delay6_var))
            pdelay6_entry = tk.Entry(
                pdelay6_frame,
                textvariable=self.cast_perfect_delay6_var,
                font=("Segoe UI", 10),
                width=8
            )
            pdelay6_entry.pack(side="left", padx=5)

            pdelay6_unit = tk.Label(
                pdelay6_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            pdelay6_unit.pack(side="left")

    def update_shake_flow_details(self):
        """Update shake flow details based on enabled state"""
        # Clear existing widgets
        for widget in self.shake_flow_details_frame.winfo_children():
            widget.destroy()

        # Check if Shake is enabled
        if not self.active_settings.get("flow_shake_enabled", True):
            disabled_label = tk.Label(
                self.shake_flow_details_frame,
                text="Disabled",
                font=("Segoe UI", 12, "italic"),
                bg="#f5f5f5",
                fg="#999999"
            )
            disabled_label.pack(anchor="w", pady=10)
        else:
            # Settings frame
            settings_frame = tk.Frame(self.shake_flow_details_frame, bg="#f5f5f5")
            settings_frame.pack(fill="x", pady=5)

            # Shake Timeout setting
            timeout_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            timeout_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            timeout_label = tk.Label(
                timeout_frame,
                text="Shake Timeout:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            timeout_label.pack(side="left")

            self.shake_timeout_var = tk.StringVar(value=str(self.active_settings.get("shake_timeout", 3.0)))
            self.shake_timeout_var.trace_add("write", lambda *args: self.save_setting("shake_timeout", self.shake_timeout_var))
            timeout_entry = tk.Entry(
                timeout_frame,
                textvariable=self.shake_timeout_var,
                font=("Segoe UI", 10),
                width=8
            )
            timeout_entry.pack(side="left", padx=5)

            timeout_unit = tk.Label(
                timeout_frame,
                text="s",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            timeout_unit.pack(side="left")

            # Description for Shake Timeout
            timeout_desc = tk.Label(
                settings_frame,
                text="Max time to wait for shake detection before timing out",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            timeout_desc.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

            # Shake Confidence Threshold setting
            confidence_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            confidence_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            confidence_label = tk.Label(
                confidence_frame,
                text="Detection Confidence:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            confidence_label.pack(side="left")

            self.shake_confidence_var = tk.StringVar(value=str(self.active_settings.get("shake_confidence_threshold", 0.5)))
            self.shake_confidence_var.trace_add("write", lambda *args: self.save_setting("shake_confidence_threshold", self.shake_confidence_var))
            confidence_entry = tk.Entry(
                confidence_frame,
                textvariable=self.shake_confidence_var,
                font=("Segoe UI", 10),
                width=8
            )
            confidence_entry.pack(side="left", padx=5)

            confidence_range = tk.Label(
                confidence_frame,
                text="(0.0-1.0)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            confidence_range.pack(side="left", padx=5)

            # Description for Confidence
            confidence_desc = tk.Label(
                settings_frame,
                text="Minimum confidence level to detect shake (higher = more accurate, may miss shakes)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            confidence_desc.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

            # Shake Position Threshold setting
            position_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            position_frame.grid(row=4, column=0, padx=10, pady=5, sticky="w")

            position_label = tk.Label(
                position_frame,
                text="Position Threshold:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            position_label.pack(side="left")

            self.shake_position_var = tk.StringVar(value=str(self.active_settings.get("shake_position_threshold", 10)))
            self.shake_position_var.trace_add("write", lambda *args: self.save_setting("shake_position_threshold", self.shake_position_var, is_int=True))
            position_entry = tk.Entry(
                position_frame,
                textvariable=self.shake_position_var,
                font=("Segoe UI", 10),
                width=8
            )
            position_entry.pack(side="left", padx=5)

            position_unit = tk.Label(
                position_frame,
                text="px",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#666666"
            )
            position_unit.pack(side="left")

            # Description for Position Threshold
            position_desc = tk.Label(
                settings_frame,
                text="Ignore shake clicks within this pixel distance (auto-scales with resolution)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            position_desc.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="w")

    def update_fish_flow_details(self):
        """Update fish flow details based on enabled state"""
        # Clear existing widgets
        for widget in self.fish_flow_details_frame.winfo_children():
            widget.destroy()

        # Check if Fish is enabled
        if not self.active_settings.get("flow_fish_enabled", True):
            disabled_label = tk.Label(
                self.fish_flow_details_frame,
                text="Disabled",
                font=("Segoe UI", 12, "italic"),
                bg="#f5f5f5",
                fg="#999999"
            )
            disabled_label.pack(anchor="w", pady=10)
        else:
            # Settings frame
            settings_frame = tk.Frame(self.fish_flow_details_frame, bg="#f5f5f5")
            settings_frame.pack(fill="x", pady=5)

            # Fishing Confidence Threshold
            confidence_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            confidence_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            confidence_label = tk.Label(
                confidence_frame,
                text="Confidence Threshold:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            confidence_label.pack(side="left")

            self.fishing_confidence_var = tk.StringVar(value=str(self.active_settings.get("fishing_confidence_threshold", 0.5)))
            self.fishing_confidence_var.trace_add("write", lambda *args: self.save_setting("fishing_confidence_threshold", self.fishing_confidence_var))
            confidence_entry = tk.Entry(
                confidence_frame,
                textvariable=self.fishing_confidence_var,
                font=("Segoe UI", 10),
                width=8
            )
            confidence_entry.pack(side="left", padx=5)

            confidence_unit = tk.Label(
                confidence_frame,
                text="(0.0-1.0)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            confidence_unit.pack(side="left")

            # Description for Confidence Threshold
            confidence_desc = tk.Label(
                settings_frame,
                text="Minimum YOLO confidence to detect Target Line and Fish Bar (0.5 = 50% confidence)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            confidence_desc.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

            # PD Controller - KP (Proportional Gain)
            kp_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            kp_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

            kp_label = tk.Label(
                kp_frame,
                text="KP (Proportional):",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            kp_label.pack(side="left")

            self.fish_kp_var = tk.StringVar(value=str(self.active_settings.get("fish_kp", 0.8)))
            self.fish_kp_var.trace_add("write", lambda *args: self.save_setting("fish_kp", self.fish_kp_var))
            kp_entry = tk.Entry(
                kp_frame,
                textvariable=self.fish_kp_var,
                font=("Segoe UI", 10),
                width=8
            )
            kp_entry.pack(side="left", padx=5)

            # Description for KP
            kp_desc = tk.Label(
                settings_frame,
                text="Proportional gain - how strongly to react to position error (0.8 = balanced, higher = more aggressive)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            kp_desc.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")

            # KD (Derivative Gain) - Disabled for YOLO but included for completeness
            kd_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            kd_frame.grid(row=4, column=0, padx=10, pady=5, sticky="w")

            kd_label = tk.Label(
                kd_frame,
                text="KD (Derivative):",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            kd_label.pack(side="left")

            self.fish_kd_var = tk.StringVar(value=str(self.active_settings.get("fish_kd", 0.0)))
            self.fish_kd_var.trace_add("write", lambda *args: self.save_setting("fish_kd", self.fish_kd_var))
            kd_entry = tk.Entry(
                kd_frame,
                textvariable=self.fish_kd_var,
                font=("Segoe UI", 10),
                width=8
            )
            kd_entry.pack(side="left", padx=5)

            # Description for KD
            kd_desc = tk.Label(
                settings_frame,
                text="Derivative gain - dampens based on error change rate (0.0 recommended for YOLO, can experiment)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            kd_desc.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="w")

            # Target Tolerance (Dead Zone)
            target_tol_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            target_tol_frame.grid(row=6, column=0, padx=10, pady=5, sticky="w")

            target_tol_label = tk.Label(
                target_tol_frame,
                text="Dead Zone (Target Tol):",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            target_tol_label.pack(side="left")

            self.fish_target_tol_var = tk.StringVar(value=str(self.active_settings.get("fish_target_tol_px", 10.0)))
            self.fish_target_tol_var.trace_add("write", lambda *args: self.save_setting("fish_target_tol_px", self.fish_target_tol_var))
            target_tol_entry = tk.Entry(
                target_tol_frame,
                textvariable=self.fish_target_tol_var,
                font=("Segoe UI", 10),
                width=8
            )
            target_tol_entry.pack(side="left", padx=5)

            target_tol_unit = tk.Label(
                target_tol_frame,
                text="pixels",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            target_tol_unit.pack(side="left")

            # Description for Dead Zone
            target_tol_desc = tk.Label(
                settings_frame,
                text="Dead zone - spam click if error < this value (v4 style, try 5-15px)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            target_tol_desc.grid(row=7, column=0, padx=10, pady=(0, 5), sticky="w")

            # PD Clamp
            pd_clamp_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            pd_clamp_frame.grid(row=8, column=0, padx=10, pady=5, sticky="w")

            pd_clamp_label = tk.Label(
                pd_clamp_frame,
                text="PD Clamp:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            pd_clamp_label.pack(side="left")

            self.fish_pd_clamp_var = tk.StringVar(value=str(self.active_settings.get("fish_pd_clamp", 100.0)))
            self.fish_pd_clamp_var.trace_add("write", lambda *args: self.save_setting("fish_pd_clamp", self.fish_pd_clamp_var))
            pd_clamp_entry = tk.Entry(
                pd_clamp_frame,
                textvariable=self.fish_pd_clamp_var,
                font=("Segoe UI", 10),
                width=8
            )
            pd_clamp_entry.pack(side="left", padx=5)

            # Description for PD Clamp
            pd_clamp_desc = tk.Label(
                settings_frame,
                text="Maximum control signal magnitude (±100 standard)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            pd_clamp_desc.grid(row=9, column=0, padx=10, pady=(0, 5), sticky="w")

            # Boundary Factor
            boundary_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            boundary_frame.grid(row=10, column=0, padx=10, pady=5, sticky="w")

            boundary_label = tk.Label(
                boundary_frame,
                text="Boundary Override Factor:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            boundary_label.pack(side="left")

            self.fish_boundary_var = tk.StringVar(value=str(self.active_settings.get("fish_boundary_factor", 0.15)))
            self.fish_boundary_var.trace_add("write", lambda *args: self.save_setting("fish_boundary_factor", self.fish_boundary_var))
            boundary_entry = tk.Entry(
                boundary_frame,
                textvariable=self.fish_boundary_var,
                font=("Segoe UI", 10),
                width=8
            )
            boundary_entry.pack(side="left", padx=5)

            # Description for Boundary Factor
            boundary_desc = tk.Label(
                settings_frame,
                text="Boundary margin as fraction of box length (0.15 = 15%, v4 style emergency override)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            boundary_desc.grid(row=11, column=0, padx=10, pady=(0, 5), sticky="w")

            # Cooldown Duration (Grace Period)
            cooldown_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            cooldown_frame.grid(row=12, column=0, padx=10, pady=5, sticky="w")

            cooldown_label = tk.Label(
                cooldown_frame,
                text="Grace Period (Cooldown):",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            cooldown_label.pack(side="left")

            self.fish_cooldown_var = tk.StringVar(value=str(self.active_settings.get("fish_cooldown_duration", 1.0)))
            self.fish_cooldown_var.trace_add("write", lambda *args: self.save_setting("fish_cooldown_duration", self.fish_cooldown_var))
            cooldown_entry = tk.Entry(
                cooldown_frame,
                textvariable=self.fish_cooldown_var,
                font=("Segoe UI", 10),
                width=8
            )
            cooldown_entry.pack(side="left", padx=5)

            cooldown_unit = tk.Label(
                cooldown_frame,
                text="seconds",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            cooldown_unit.pack(side="left")

            # Description for Cooldown
            cooldown_desc = tk.Label(
                settings_frame,
                text="Grace period when tracking is lost before engaging spam click (1.0s = v4 default)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            cooldown_desc.grid(row=13, column=0, padx=10, pady=(0, 15), sticky="w")

            # Fish Timeout
            fish_timeout_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            fish_timeout_frame.grid(row=14, column=0, padx=10, pady=5, sticky="w")

            fish_timeout_label = tk.Label(
                fish_timeout_frame,
                text="Fish Timeout:",
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                fg="#333333",
                width=20,
                anchor="w"
            )
            fish_timeout_label.pack(side="left")

            self.fish_timeout_var = tk.StringVar(value=str(self.active_settings.get("fish_timeout", 30.0)))
            self.fish_timeout_var.trace_add("write", lambda *_args: self.save_setting("fish_timeout", self.fish_timeout_var))
            fish_timeout_entry = tk.Entry(
                fish_timeout_frame,
                textvariable=self.fish_timeout_var,
                font=("Segoe UI", 10),
                width=8
            )
            fish_timeout_entry.pack(side="left", padx=5)

            fish_timeout_unit = tk.Label(
                fish_timeout_frame,
                text="seconds",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            fish_timeout_unit.pack(side="left")

            # Description for Fish Timeout
            fish_timeout_desc = tk.Label(
                settings_frame,
                text="Maximum time to attempt fishing before returning to cast (0 = no timeout)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            fish_timeout_desc.grid(row=15, column=0, padx=10, pady=(0, 5), sticky="w")

            # Show Live Feed Checkbox
            live_feed_frame = tk.Frame(settings_frame, bg="#f5f5f5")
            live_feed_frame.grid(row=16, column=0, padx=10, pady=10, sticky="w")

            self.fish_show_live_feed_var = tk.BooleanVar(value=bool(self.active_settings.get("fish_show_live_feed", False)))
            live_feed_check = tk.Checkbutton(
                live_feed_frame,
                text="Show Live Feed (Debug Overlay)",
                variable=self.fish_show_live_feed_var,
                font=("Segoe UI", 10),
                bg="#f5f5f5",
                activebackground="#f5f5f5",
                selectcolor="#f5f5f5",
                command=lambda: self.toggle_live_feed(),
                cursor="hand2"
            )
            live_feed_check.pack(side="left")

            # Description for Show Live Feed
            live_feed_desc = tk.Label(
                settings_frame,
                text="Display visual indicators above fish box showing YOLO detection positions (may impact performance)",
                font=("Segoe UI", 9, "italic"),
                bg="#f5f5f5",
                fg="#666666"
            )
            live_feed_desc.grid(row=17, column=0, padx=10, pady=(0, 5), sticky="w")

    def update_misc_flow_details(self):
        """Update misc flow details based on Auto Refresh Rod checkbox and Misc enabled state"""
        # Clear existing widgets in the entire misc flow details frame
        for widget in self.misc_flow_details_frame.winfo_children():
            widget.destroy()

        # Check if Misc step is disabled in the main flow
        if not self.active_settings.get("flow_misc_enabled", True):
            disabled_label = tk.Label(
                self.misc_flow_details_frame,
                text="Disabled",
                font=("Segoe UI", 12, "italic"),
                bg="#faf5fb",
                fg="#999999"
            )
            disabled_label.pack(anchor="w", pady=10)
            return

        # Recreate the Auto Refresh Rod Checkbox
        auto_refresh_frame = tk.Frame(self.misc_flow_details_frame, bg="#faf5fb")
        auto_refresh_frame.pack(fill="x", pady=(5, 10))

        auto_refresh_check = tk.Checkbutton(
            auto_refresh_frame,
            text="Auto Refresh Rod",
            variable=self.auto_refresh_rod_var,
            font=("Segoe UI", 10, "bold"),
            bg="#faf5fb",
            activebackground="#faf5fb",
            fg="#9C27B0",
            command=self.update_auto_refresh_details,
            cursor="hand2"
        )
        auto_refresh_check.pack(side="left")

        # Auto Refresh Rod Details Frame
        self.auto_refresh_details_frame = tk.Frame(self.misc_flow_details_frame, bg="#faf5fb")

        # Update auto refresh details
        self.update_auto_refresh_details()

    def update_auto_refresh_details(self):
        """Update auto refresh rod details based on checkbox"""
        # Clear existing widgets
        for widget in self.auto_refresh_details_frame.winfo_children():
            widget.destroy()

        # Save the checkbox state
        self.active_settings["auto_refresh_rod_enabled"] = self.auto_refresh_rod_var.get()

        # Check if Auto Refresh Rod is enabled
        if not self.auto_refresh_rod_var.get():
            # Unpack the frame to remove empty space
            self.auto_refresh_details_frame.pack_forget()
            return

        # Repack the frame when enabled
        self.auto_refresh_details_frame.pack(fill="x")

        # Flow description
        flow_text = tk.Label(
            self.auto_refresh_details_frame,
            text="Flow: Delay 1 → Press Key 1 → Delay 2 → Press Key 2 → Delay 3",
            font=("Segoe UI", 9),
            bg="#faf5fb",
            fg="#666666"
        )
        flow_text.pack(anchor="w", pady=(5, 10))

        # Delay and Key settings frame
        settings_frame = tk.Frame(self.auto_refresh_details_frame, bg="#f5f5f5")
        settings_frame.pack(fill="x")

        # Delay 1
        delay1_frame = tk.Frame(settings_frame, bg="#f5f5f5")
        delay1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        delay1_label = tk.Label(
            delay1_frame,
            text="Delay 1:",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            width=12,
            anchor="w"
        )
        delay1_label.pack(side="left")

        self.misc_delay1_var = tk.StringVar(value=str(self.active_settings.get("misc_delay1", 0.0)))
        self.misc_delay1_var.trace_add("write", lambda *args: self.save_setting("misc_delay1", self.misc_delay1_var))
        delay1_entry = tk.Entry(
            delay1_frame,
            textvariable=self.misc_delay1_var,
            font=("Segoe UI", 10),
            width=8
        )
        delay1_entry.pack(side="left", padx=5)

        delay1_unit = tk.Label(
            delay1_frame,
            text="s",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#666666"
        )
        delay1_unit.pack(side="left")

        # Press Key 1
        key1_frame = tk.Frame(settings_frame, bg="#f5f5f5")
        key1_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        key1_label = tk.Label(
            key1_frame,
            text="Press Key 1:",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            width=12,
            anchor="w"
        )
        key1_label.pack(side="left")

        self.misc_key1_var = tk.StringVar(value=str(self.active_settings.get("misc_key1", "2")))
        key1_dropdown = ttk.Combobox(
            key1_frame,
            textvariable=self.misc_key1_var,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            state="readonly",
            font=("Segoe UI", 10),
            width=6
        )
        key1_dropdown.set(self.active_settings.get("misc_key1", "2"))
        key1_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_misc_key_setting("misc_key1", self.misc_key1_var))
        key1_dropdown.pack(side="left", padx=5)

        # Delay 2
        delay2_frame = tk.Frame(settings_frame, bg="#f5f5f5")
        delay2_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        delay2_label = tk.Label(
            delay2_frame,
            text="Delay 2:",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            width=12,
            anchor="w"
        )
        delay2_label.pack(side="left")

        self.misc_delay2_var = tk.StringVar(value=str(self.active_settings.get("misc_delay2", 1.0)))
        self.misc_delay2_var.trace_add("write", lambda *args: self.save_setting("misc_delay2", self.misc_delay2_var))
        delay2_entry = tk.Entry(
            delay2_frame,
            textvariable=self.misc_delay2_var,
            font=("Segoe UI", 10),
            width=8
        )
        delay2_entry.pack(side="left", padx=5)

        delay2_unit = tk.Label(
            delay2_frame,
            text="s",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#666666"
        )
        delay2_unit.pack(side="left")

        # Press Key 2
        key2_frame = tk.Frame(settings_frame, bg="#f5f5f5")
        key2_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        key2_label = tk.Label(
            key2_frame,
            text="Press Key 2:",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            width=12,
            anchor="w"
        )
        key2_label.pack(side="left")

        self.misc_key2_var = tk.StringVar(value=str(self.active_settings.get("misc_key2", "1")))
        key2_dropdown = ttk.Combobox(
            key2_frame,
            textvariable=self.misc_key2_var,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            state="readonly",
            font=("Segoe UI", 10),
            width=6
        )
        key2_dropdown.set(self.active_settings.get("misc_key2", "1"))
        key2_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_misc_key_setting("misc_key2", self.misc_key2_var))
        key2_dropdown.pack(side="left", padx=5)

        # Delay 3
        delay3_frame = tk.Frame(settings_frame, bg="#f5f5f5")
        delay3_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        delay3_label = tk.Label(
            delay3_frame,
            text="Delay 3:",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333333",
            width=12,
            anchor="w"
        )
        delay3_label.pack(side="left")

        self.misc_delay3_var = tk.StringVar(value=str(self.active_settings.get("misc_delay3", 1.0)))
        self.misc_delay3_var.trace_add("write", lambda *args: self.save_setting("misc_delay3", self.misc_delay3_var))
        delay3_entry = tk.Entry(
            delay3_frame,
            textvariable=self.misc_delay3_var,
            font=("Segoe UI", 10),
            width=8
        )
        delay3_entry.pack(side="left", padx=5)

        delay3_unit = tk.Label(
            delay3_frame,
            text="s",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#666666"
        )
        delay3_unit.pack(side="left")

    def save_misc_key_setting(self, setting_name, var):
        """Save misc key setting to active_settings"""
        value = var.get()
        self.active_settings[setting_name] = value

    def save_cast_delay_setting(self, setting_name, var, is_int=False):
        """Auto-save cast delay setting to active_settings (not config file)"""
        try:
            if is_int:
                value = int(var.get())
            else:
                value = float(var.get())

            if value < 0:
                return  # Silently ignore negative values

            self.active_settings[setting_name] = value
        except ValueError:
            # Silently ignore invalid values during typing
            pass

    def save_cast_toggle_setting(self, setting_name, var):
        """Auto-save cast toggle setting to active_settings (not config file)"""
        self.active_settings[setting_name] = var.get()

    def save_setting(self, setting_name, var, is_int=False):
        """Auto-save general setting to active_settings (not config file)"""
        try:
            if is_int:
                value = int(var.get())
            else:
                value = float(var.get())

            if value < 0:
                return  # Silently ignore negative values

            self.active_settings[setting_name] = value
        except ValueError:
            # Silently ignore invalid values during typing
            pass

    def create_discord_settings_tab(self):
        """Create the Discord Settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="💬 Discord")

        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(tab)

        # Main container
        container = tk.Frame(scrollable_frame, bg="white")
        container.pack(fill="both", expand=True, padx=35, pady=25)

        # Title with description
        title_frame = tk.Frame(container, bg="white")
        title_frame.pack(fill="x", pady=(0, 25))

        title = tk.Label(
            title_frame,
            text="💬 Discord Notifications",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#1976D2"
        )
        title.pack(anchor="w")

        desc = tk.Label(
            title_frame,
            text="Get notified via Discord webhook when fishing milestones are reached",
            font=("Segoe UI", 9),
            bg="white",
            fg="#757575"
        )
        desc.pack(anchor="w", pady=(5, 0))

        # Enable/Disable toggle with frame
        enable_outer_frame = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        enable_outer_frame.pack(fill="x", pady=(0, 20))

        enable_frame = tk.Frame(enable_outer_frame, bg="#f8f9fa")
        enable_frame.pack(padx=20, pady=18)

        self.discord_enabled_var = tk.BooleanVar(value=self.active_settings.get("discord_enabled", False))
        enable_check = tk.Checkbutton(
            enable_frame,
            text="Enable Discord Notifications",
            variable=self.discord_enabled_var,
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            selectcolor="#f8f9fa",
            fg="#5865F2",
            cursor="hand2",
            command=lambda: self.save_discord_setting("discord_enabled", self.discord_enabled_var.get())
        )
        enable_check.pack(anchor="w")

        # Webhook URL section
        webhook_title = tk.Label(
            container,
            text="🔗 Webhook Configuration",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#424242"
        )
        webhook_title.pack(anchor="w", pady=(0, 10))

        webhook_frame = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        webhook_frame.pack(fill="x", pady=(0, 20))

        webhook_inner = tk.Frame(webhook_frame, bg="#f8f9fa")
        webhook_inner.pack(fill="x", padx=20, pady=18)

        webhook_label = tk.Label(
            webhook_inner,
            text="Webhook URL:",
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa",
            fg="#424242",
            anchor="w"
        )
        webhook_label.pack(anchor="w", pady=(0, 8))

        # URL entry and test button frame
        url_controls_frame = tk.Frame(webhook_inner, bg="#f8f9fa")
        url_controls_frame.pack(fill="x")

        self.discord_webhook_var = tk.StringVar(value=self.active_settings.get("discord_webhook_url", ""))
        self.discord_webhook_var.trace_add("write", lambda *args: self.save_discord_setting("discord_webhook_url", self.discord_webhook_var.get()))
        webhook_entry = tk.Entry(
            url_controls_frame,
            textvariable=self.discord_webhook_var,
            font=("Segoe UI", 10),
            width=50,
            relief="solid",
            bd=1
        )
        webhook_entry.pack(side="left", fill="x", expand=True, ipady=6)

        test_button = tk.Button(
            url_controls_frame,
            text="Test Webhook",
            font=("Segoe UI", 10, "bold"),
            bg="#5865F2",
            fg="white",
            activebackground="#4752C4",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2",
            borderwidth=0,
            command=self.test_discord_webhook
        )
        test_button.pack(side="left", padx=(12, 0))

        webhook_hint = tk.Label(
            webhook_inner,
            text="Create a webhook in your Discord server settings → Integrations → Webhooks",
            font=("Segoe UI", 9, "italic"),
            bg="#f8f9fa",
            fg="#757575"
        )
        webhook_hint.pack(anchor="w", pady=(8, 0))

        # Notification Mode section
        mode_title = tk.Label(
            container,
            text="📊 Notification Settings",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#424242"
        )
        mode_title.pack(anchor="w", pady=(0, 10))

        mode_outer_frame = tk.Frame(container, bg="#f8f9fa", relief="solid", bd=1, highlightbackground="#e0e0e0", highlightthickness=1)
        mode_outer_frame.pack(fill="x", pady=(0, 20))

        mode_frame = tk.Frame(mode_outer_frame, bg="#f8f9fa")
        mode_frame.pack(fill="x", padx=20, pady=18)

        mode_label = tk.Label(
            mode_frame,
            text="Notification Mode:",
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa",
            fg="#424242",
            anchor="w"
        )
        mode_label.pack(anchor="w", pady=(0, 8))

        self.discord_mode_var = tk.StringVar(value=self.active_settings.get("discord_mode", "Screenshot"))
        mode_dropdown = ttk.Combobox(
            mode_frame,
            textvariable=self.discord_mode_var,
            values=["Screenshot", "Text"],
            state="readonly",
            font=("Segoe UI", 10),
            width=25
        )
        mode_dropdown.set(self.active_settings.get("discord_mode", "Screenshot"))
        mode_dropdown.bind("<<ComboboxSelected>>", self.on_discord_mode_changed)
        mode_dropdown.pack(anchor="w")

        # Mode-specific options frame
        self.discord_options_frame = tk.Frame(mode_frame, bg="#f8f9fa")
        self.discord_options_frame.pack(fill="x", pady=(15, 0))

        # Initialize mode-specific options
        self.update_discord_options()

    def on_discord_mode_changed(self, event=None):
        """Handle discord mode dropdown change"""
        new_mode = self.discord_mode_var.get()
        self.active_settings["discord_mode"] = new_mode
        self.update_discord_options()

    def update_discord_options(self):
        """Update discord options based on selected mode"""
        # Clear existing widgets
        for widget in self.discord_options_frame.winfo_children():
            widget.destroy()

        mode = self.discord_mode_var.get()

        if mode == "Screenshot":
            # Loops Per Screenshot option
            loops_frame = tk.Frame(self.discord_options_frame, bg="#f8f9fa")
            loops_frame.pack(anchor="w", pady=5)

            loops_label = tk.Label(
                loops_frame,
                text="Loops Per Screenshot:",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#424242",
                width=22,
                anchor="w"
            )
            loops_label.pack(side="left")

            self.discord_screenshot_loops_var = tk.StringVar(value=str(self.active_settings.get("discord_screenshot_loops", 10)))
            self.discord_screenshot_loops_var.trace_add("write", lambda *args: self.save_discord_int_setting("discord_screenshot_loops", self.discord_screenshot_loops_var))
            loops_entry = tk.Entry(
                loops_frame,
                textvariable=self.discord_screenshot_loops_var,
                font=("Segoe UI", 10),
                width=10,
                relief="solid",
                bd=1
            )
            loops_entry.pack(side="left", padx=5, ipady=3)

            loops_unit = tk.Label(
                loops_frame,
                text="loops",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#757575"
            )
            loops_unit.pack(side="left")

        elif mode == "Text":
            # Loops Per Text option
            loops_frame = tk.Frame(self.discord_options_frame, bg="#f8f9fa")
            loops_frame.pack(anchor="w", pady=5)

            loops_label = tk.Label(
                loops_frame,
                text="Loops Per Text:",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#424242",
                width=22,
                anchor="w"
            )
            loops_label.pack(side="left")

            self.discord_text_loops_var = tk.StringVar(value=str(self.active_settings.get("discord_text_loops", 10)))
            self.discord_text_loops_var.trace_add("write", lambda *args: self.save_discord_int_setting("discord_text_loops", self.discord_text_loops_var))
            loops_entry = tk.Entry(
                loops_frame,
                textvariable=self.discord_text_loops_var,
                font=("Segoe UI", 10),
                width=10,
                relief="solid",
                bd=1
            )
            loops_entry.pack(side="left", padx=5, ipady=3)

            loops_unit = tk.Label(
                loops_frame,
                text="loops",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#757575"
            )
            loops_unit.pack(side="left")

    def save_discord_setting(self, setting_name, value):
        """Save discord string setting to active_settings"""
        self.active_settings[setting_name] = value

    def save_discord_int_setting(self, setting_name, var):
        """Save discord integer setting to active_settings"""
        try:
            value = int(var.get())
            if value > 0:
                self.active_settings[setting_name] = value
        except ValueError:
            pass  # Ignore invalid values

    def test_discord_webhook(self):
        """Test the discord webhook based on selected mode"""
        webhook_url = self.discord_webhook_var.get()
        if not webhook_url:
            print("[Discord] Error: No webhook URL provided")
            return

        mode = self.discord_mode_var.get()

        if mode == "Screenshot":
            # Send both text and screenshot
            print("[Discord] Sending test screenshot...")
            try:
                import requests
                import io
                from datetime import datetime

                # Capture full screen screenshot
                screenshot = ImageGrab.grab()

                # Convert to bytes
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                # Prepare the file and message
                files = {
                    'file': ('test_screenshot.png', img_bytes, 'image/png')
                }

                data = {
                    "content": f"🎣 **IRUS V7 - Webhook Test**\n✅ Screenshot mode is working!\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }

                response = requests.post(webhook_url, data=data, files=files)
                if response.status_code == 204 or response.status_code == 200:
                    print("[Discord] Test screenshot sent successfully!")
                else:
                    print(f"[Discord] Test failed with status code: {response.status_code}")
            except Exception as e:
                print(f"[Discord] Error sending test screenshot: {e}")

        elif mode == "Text":
            # Send text only
            print("[Discord] Sending test text...")
            try:
                import requests
                from datetime import datetime

                data = {
                    "content": f"🎣 **IRUS V7 - Webhook Test**\n"
                              f"✅ Text mode is working!\n"
                              f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }

                response = requests.post(webhook_url, json=data)
                if response.status_code == 204 or response.status_code == 200:
                    print("[Discord] Test text sent successfully!")
                else:
                    print(f"[Discord] Test failed with status code: {response.status_code}")
            except Exception as e:
                print(f"[Discord] Error sending test text: {e}")

    def discord_send_screenshot(self):
        """Send a screenshot to Discord webhook"""
        webhook_url = self.active_settings.get("discord_webhook_url", "")
        if not webhook_url:
            print("[Discord] No webhook URL configured")
            return

        try:
            import requests
            import io
            from datetime import datetime

            # Capture full screen screenshot
            screenshot = ImageGrab.grab()

            # Convert to bytes
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Prepare the file and message
            files = {
                'file': ('fishing_bot_screenshot.png', img_bytes, 'image/png')
            }

            data = {
                "content": f"🎣 IRUS V7 - Fishing Loop Screenshot\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }

            response = requests.post(webhook_url, data=data, files=files)
            if response.status_code == 204 or response.status_code == 200:
                print("[Discord] Screenshot sent successfully!")
            else:
                print(f"[Discord] Failed to send screenshot: {response.status_code}")
        except Exception as e:
            print(f"[Discord] Error sending screenshot: {e}")

    def discord_send_text(self, loops_completed):
        """Send a text notification to Discord webhook"""
        webhook_url = self.active_settings.get("discord_webhook_url", "")
        if not webhook_url:
            print("[Discord] No webhook URL configured")
            return

        try:
            import requests
            from datetime import datetime

            data = {
                "content": f"🎣 **IRUS V7 - Fishing Loop Update**\n"
                          f"📊 Loops Completed: **{loops_completed}**\n"
                          f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"✅ Bot is running smoothly!"
            }

            response = requests.post(webhook_url, json=data)
            if response.status_code == 204 or response.status_code == 200:
                print(f"[Discord] Text notification sent! (Loops: {loops_completed})")
            else:
                print(f"[Discord] Failed to send text: {response.status_code}")
        except Exception as e:
            print(f"[Discord] Error sending text notification: {e}")

    def discord_send_start_notification(self):
        """Send a simple text notification when bot starts"""
        webhook_url = self.active_settings.get("discord_webhook_url", "")
        if not webhook_url:
            print("[Discord] No webhook URL configured")
            return

        try:
            import requests
            from datetime import datetime

            data = {
                "content": f"🎣 **IRUS V7 Started**\n"
                          f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"🤖 Fishing bot is now running!"
            }

            response = requests.post(webhook_url, json=data)
            if response.status_code == 204 or response.status_code == 200:
                print("[Discord] Start notification sent!")
            else:
                print(f"[Discord] Failed to send start notification: {response.status_code}")
        except Exception as e:
            print(f"[Discord] Error sending start notification: {e}")

    def create_support_tab(self):
        """Create the Support The Creators tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="❤️ Support")

        # Create scrollable frame
        scrollable_frame = self.create_scrollable_frame(tab)

        # Main container
        container = tk.Frame(scrollable_frame, bg="white")
        container.pack(fill="both", expand=True, padx=35, pady=25)

        # Title with description
        title_frame = tk.Frame(container, bg="white")
        title_frame.pack(fill="x", pady=(0, 30))

        title = tk.Label(
            title_frame,
            text="❤️ Support The Creators",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#1976D2"
        )
        title.pack(anchor="w")

        # Subtitle
        subtitle = tk.Label(
            title_frame,
            text="Enjoying IRUS V7? Show your appreciation and help us continue development!",
            font=("Segoe UI", 10),
            bg="white",
            fg="#757575"
        )
        subtitle.pack(anchor="w", pady=(8, 0))

        # Discord Section
        discord_frame = tk.Frame(container, bg="#f0f4ff", relief="solid", bd=1, highlightbackground="#5865F2", highlightthickness=2)
        discord_frame.pack(fill="x", pady=(0, 18))

        discord_inner = tk.Frame(discord_frame, bg="#f0f4ff")
        discord_inner.pack(padx=25, pady=22)

        discord_icon = tk.Label(
            discord_inner,
            text="💬",
            font=("Segoe UI", 28),
            bg="#f0f4ff"
        )
        discord_icon.pack(side="left", padx=(0, 18))

        discord_text_frame = tk.Frame(discord_inner, bg="#f0f4ff")
        discord_text_frame.pack(side="left", fill="x", expand=True)

        discord_title = tk.Label(
            discord_text_frame,
            text="Join Our Discord Community",
            font=("Segoe UI", 13, "bold"),
            bg="#f0f4ff",
            fg="#5865F2"
        )
        discord_title.pack(anchor="w")

        discord_desc = tk.Label(
            discord_text_frame,
            text="Get help, share feedback, and connect with other users",
            font=("Segoe UI", 9),
            bg="#f0f4ff",
            fg="#757575"
        )
        discord_desc.pack(anchor="w", pady=(3, 5))

        discord_link = tk.Label(
            discord_text_frame,
            text="https://discord.gg/vKVBbyfHTD",
            font=("Segoe UI", 10, "underline"),
            bg="#f0f4ff",
            fg="#0066cc",
            cursor="hand2"
        )
        discord_link.pack(anchor="w")
        discord_link.bind("<Button-1>", lambda e: self.open_url("https://discord.gg/vKVBbyfHTD"))

        # YouTube Section
        youtube_frame = tk.Frame(container, bg="#fff5f5", relief="solid", bd=1, highlightbackground="#FF0000", highlightthickness=2)
        youtube_frame.pack(fill="x", pady=(0, 18))

        youtube_inner = tk.Frame(youtube_frame, bg="#fff5f5")
        youtube_inner.pack(padx=25, pady=22)

        youtube_icon = tk.Label(
            youtube_inner,
            text="🎥",
            font=("Segoe UI", 28),
            bg="#fff5f5"
        )
        youtube_icon.pack(side="left", padx=(0, 18))

        youtube_text_frame = tk.Frame(youtube_inner, bg="#fff5f5")
        youtube_text_frame.pack(side="left", fill="x", expand=True)

        youtube_title = tk.Label(
            youtube_text_frame,
            text="Subscribe on YouTube",
            font=("Segoe UI", 13, "bold"),
            bg="#fff5f5",
            fg="#FF0000"
        )
        youtube_title.pack(anchor="w")

        youtube_desc = tk.Label(
            youtube_text_frame,
            text="Watch tutorials, updates, and gameplay videos",
            font=("Segoe UI", 9),
            bg="#fff5f5",
            fg="#757575"
        )
        youtube_desc.pack(anchor="w", pady=(3, 5))

        youtube_link = tk.Label(
            youtube_text_frame,
            text="https://www.youtube.com/channel/UCNYFFWcJAgYSZGa4_-Rf-ug",
            font=("Segoe UI", 10, "underline"),
            bg="#fff5f5",
            fg="#0066cc",
            cursor="hand2"
        )
        youtube_link.pack(anchor="w")
        youtube_link.bind("<Button-1>", lambda e: self.open_url("https://www.youtube.com/channel/UCNYFFWcJAgYSZGa4_-Rf-ug"))

        # PayPal Section
        paypal_frame = tk.Frame(container, bg="#f0f8ff", relief="solid", bd=1, highlightbackground="#0070BA", highlightthickness=2)
        paypal_frame.pack(fill="x", pady=(0, 18))

        paypal_inner = tk.Frame(paypal_frame, bg="#f0f8ff")
        paypal_inner.pack(padx=25, pady=22)

        paypal_icon = tk.Label(
            paypal_inner,
            text="💰",
            font=("Segoe UI", 28),
            bg="#f0f8ff"
        )
        paypal_icon.pack(side="left", padx=(0, 18))

        paypal_text_frame = tk.Frame(paypal_inner, bg="#f0f8ff")
        paypal_text_frame.pack(side="left", fill="x", expand=True)

        paypal_title = tk.Label(
            paypal_text_frame,
            text="Support via PayPal",
            font=("Segoe UI", 13, "bold"),
            bg="#f0f8ff",
            fg="#0070BA"
        )
        paypal_title.pack(anchor="w")

        paypal_desc = tk.Label(
            paypal_text_frame,
            text="Buy us a coffee and support future development",
            font=("Segoe UI", 9),
            bg="#f0f8ff",
            fg="#757575"
        )
        paypal_desc.pack(anchor="w", pady=(3, 5))

        paypal_link = tk.Label(
            paypal_text_frame,
            text="https://www.paypal.com/paypalme/JLim862",
            font=("Segoe UI", 10, "underline"),
            bg="#f0f8ff",
            fg="#0066cc",
            cursor="hand2"
        )
        paypal_link.pack(anchor="w")
        paypal_link.bind("<Button-1>", lambda e: self.open_url("https://www.paypal.com/paypalme/JLim862"))

        # Thank you message
        thanks_frame = tk.Frame(container, bg="#E8F5E9", relief="solid", bd=1, highlightbackground="#4CAF50", highlightthickness=1)
        thanks_frame.pack(fill="x", pady=(10, 0))

        thanks_inner = tk.Frame(thanks_frame, bg="#E8F5E9")
        thanks_inner.pack(padx=20, pady=15)

        thanks_icon = tk.Label(
            thanks_inner,
            text="🎣",
            font=("Segoe UI", 20),
            bg="#E8F5E9"
        )
        thanks_icon.pack(side="left", padx=(0, 12))

        thanks_label = tk.Label(
            thanks_inner,
            text="Thank you for using IRUS V7 and supporting our work!",
            font=("Segoe UI", 11, "bold"),
            bg="#E8F5E9",
            fg="#2E7D32"
        )
        thanks_label.pack(side="left")

    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open(url)
        print(f"[System] Opening: {url}")

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
        # Don't save immediately - will save on exit
        print(f"{box_type} updated (will save on exit): {box_coords}")

    def on_both_areas_selected(self, fish_coords, shake_coords):
        """Called when both area selections are complete"""
        self.is_modifying_area = False
        self.area_selector = None
        self.active_settings["fish_box"] = fish_coords
        self.active_settings["shake_box"] = shake_coords
        # Don't save immediately - will save on exit
        print(f"Fish Box updated (will save on exit): {fish_coords}")
        print(f"Shake Box updated (will save on exit): {shake_coords}")

        # Auto restore if enabled and minimized
        if self.active_settings.get("auto_minimize", False):
            self.root.deiconify()

    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        is_on_top = self.always_on_top_var.get()
        self.root.attributes('-topmost', is_on_top)
        self.active_settings["always_on_top"] = is_on_top
        # Don't save immediately - will save on exit

    def toggle_auto_minimize(self):
        """Toggle auto minimize setting"""
        auto_minimize = self.auto_minimize_var.get()
        self.active_settings["auto_minimize"] = auto_minimize
        # Don't save immediately - will save on exit

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
        """Reset active_settings to first_launch_config and update ALL GUI elements"""
        # Reset active_settings to defaults (don't modify Config.txt yet - only on exit)
        self.active_settings = self.first_launch_config.copy()
        
        # Update ALL GUI elements to reflect defaults
        
        # 1. Hotkey dropdowns
        for action, key_var in self.dropdown_widgets.items():
            default_key = self.active_settings.get(action, "F1")
            key_var.set(default_key)
        
        # 2. Always on top checkbox
        self.always_on_top_var.set(self.active_settings.get("always_on_top", False))
        self.apply_always_on_top()
        
        # 3. Auto minimize checkbox
        self.auto_minimize_var.set(self.active_settings.get("auto_minimize", False))
        
        # 4. Fishing control parameters (V4-style)
        self.fish_kp_var.set(str(self.active_settings.get("fish_kp", 0.8)))
        self.fish_kd_var.set(str(self.active_settings.get("fish_kd", 0.0)))
        self.fish_target_tol_var.set(str(self.active_settings.get("fish_target_tol_px", 10.0)))
        self.fish_pd_clamp_var.set(str(self.active_settings.get("fish_pd_clamp", 100.0)))
        self.fish_boundary_var.set(str(self.active_settings.get("fish_boundary_factor", 0.15)))
        self.fish_cooldown_var.set(str(self.active_settings.get("fish_cooldown_duration", 1.0)))
        
        # 5. Confidence thresholds
        self.shake_confidence_var.set(str(self.active_settings.get("shake_confidence_threshold", 0.5)))
        self.fishing_confidence_var.set(str(self.active_settings.get("fishing_confidence_threshold", 0.5)))
        
        # 6. Show live feed checkbox
        self.fish_show_live_feed_var.set(self.active_settings.get("fish_show_live_feed", True))
        
        # 7. Flow checkboxes
        self.misc_enabled_var.set(self.active_settings.get("flow_misc_enabled", True))
        self.cast_enabled_var.set(self.active_settings.get("flow_cast_enabled", True))
        self.shake_enabled_var.set(self.active_settings.get("flow_shake_enabled", True))
        self.fish_enabled_var.set(self.active_settings.get("flow_fish_enabled", True))
        
        # 8. Discord settings
        self.discord_enabled_var.set(self.active_settings.get("discord_enabled", False))
        self.discord_mode_var.set(self.active_settings.get("discord_mode", "Screenshot"))
        self.discord_webhook_var.set(self.active_settings.get("discord_webhook_url", ""))
        self.discord_screenshot_loops_var.set(str(self.active_settings.get("discord_screenshot_loops", 10)))
        self.discord_text_loops_var.set(str(self.active_settings.get("discord_text_loops", 10)))
        
        # Reload hotkeys
        keyboard.unhook_all()
        self.setup_hotkeys()
        
        print("[Reset] All settings reset to defaults (will save on exit)")

    def save_flow_settings(self):
        """Save flow configuration settings to active_settings (not config file)"""
        self.active_settings["flow_misc_enabled"] = self.misc_enabled_var.get()
        self.active_settings["flow_cast_enabled"] = self.cast_enabled_var.get()
        self.active_settings["flow_shake_enabled"] = self.shake_enabled_var.get()
        self.active_settings["flow_fish_enabled"] = self.fish_enabled_var.get()
        # Refresh the flow details to show "Disabled" if needed
        self.update_misc_flow_details()
        self.update_cast_flow_details()
        self.update_shake_flow_details()
        self.update_fish_flow_details()


    def start_loop(self):
        """Start the fishing loop"""
        if self.loop_running:
            print("Loop already running")
            return

        self.loop_running = True
        self.loop_counter = 0  # Reset loop counter
        self.update_loop_status(True)
        print("Loop started!")

        # Send Discord start notification if enabled
        if self.active_settings.get("discord_enabled", False):
            self.discord_send_start_notification()

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
        # Close debug overlay if open
        self.close_debug_overlay()
        self.update_loop_status(False)
        print("Loop stopped!")

        # Auto restore if enabled and minimized
        if self.active_settings.get("auto_minimize", False):
            self.root.deiconify()

    def run_loop(self):
        """Main loop execution"""
        # Initialize mss for fast screen capture
        sct = mss.mss()
        
        # Load models once at the start
        try:
            import torch
            shake_model = YOLO("shake_model.pt")
            fishing_model = YOLO("fishing_model.pt")

            # Use half precision (FP16) on GPU for 2x faster inference
            if torch.cuda.is_available():
                shake_model.half()
                fishing_model.half()
                print("[Loop] Models loaded successfully with FP16 (GPU half precision - 2x faster)")
            else:
                print("[Loop] Models loaded successfully (CPU mode)")
        except Exception as e:
            print(f"[Loop] Error loading models: {e}")
            self.loop_running = False
            self.update_loop_status(False)
            sct.close()
            return

        try:
            while self.loop_running:
                # Misc step
                if self.active_settings.get("flow_misc_enabled", True):
                    # Check if auto refresh rod is enabled
                    if self.active_settings.get("auto_refresh_rod_enabled", False):
                        print("[Loop] Executing: Misc (Auto Refresh Rod)")
                        # Flow: Delay 1 → Press Key 1 → Delay 2 → Press Key 2 → Delay 3
                        delay1 = self.active_settings.get("misc_delay1", 0.0)
                        key1 = self.active_settings.get("misc_key1", "2")
                        delay2 = self.active_settings.get("misc_delay2", 1.0)
                        key2 = self.active_settings.get("misc_key2", "1")
                        delay3 = self.active_settings.get("misc_delay3", 1.0)

                        # Create pynput keyboard controller for Roblox-compatible input
                        kb = pynput_keyboard.Controller()

                        time.sleep(delay1)
                        print(f"[Loop] Misc: Pressing key '{key1}'")
                        kb.press(key1)
                        time.sleep(0.05)  # Short press duration
                        kb.release(key1)

                        time.sleep(delay2)
                        print(f"[Loop] Misc: Pressing key '{key2}'")
                        kb.press(key2)
                        time.sleep(0.05)  # Short press duration
                        kb.release(key2)

                        time.sleep(delay3)
                    else:
                        print("[Loop] Misc step: Auto Refresh Rod disabled")

                if not self.loop_running:
                    break

                # Cast step
                if self.active_settings.get("flow_cast_enabled", True):
                    cast_mode = self.active_settings.get("cast_mode", "Normal")

                    if cast_mode == "Normal":
                        print("[Loop] Executing: Cast (Normal mode)")
                        # Normal mode: Delay 1 > Hold Left Click > Delay 2 > Release Left Click > Delay 3
                        delay1 = self.active_settings.get("cast_delay1", 0.0)
                        delay2 = self.active_settings.get("cast_delay2", 1.0)
                        delay3 = self.active_settings.get("cast_delay3", 2.0)

                        time.sleep(delay1)
                        mouse_down()
                        time.sleep(delay2)
                        mouse_up()
                        time.sleep(delay3)

                    elif cast_mode == "Perfect":
                        print("[Loop] Executing: Cast (Perfect mode)")
                        # Perfect mode: Delay 1 > Zoom Out > Delay 2 > Zoom In > Delay 3 > Look Down > Delay 4 > Hold Left Click > Delay 5 > Perfect Cast Release > Delay 6
                        delay1 = self.active_settings.get("cast_perfect_delay1", 0.0)
                        zoom_out_scrolls = self.active_settings.get("cast_zoom_out_scrolls", 20)
                        delay2 = self.active_settings.get("cast_perfect_delay2", 0.0)
                        zoom_in_scrolls = self.active_settings.get("cast_zoom_in_scrolls", 6)
                        delay3 = self.active_settings.get("cast_perfect_delay3", 0.0)
                        delay4 = self.active_settings.get("cast_perfect_delay4", 0.0)
                        delay5 = self.active_settings.get("cast_perfect_delay5", 0.0)
                        delay6 = self.active_settings.get("cast_perfect_delay6", 0.0)

                        # Delay 1
                        time.sleep(delay1)

                        # Zoom Out
                        if self.active_settings.get("cast_zoom_out_enabled", True):
                            for _ in range(zoom_out_scrolls):
                                mouse_scroll(-1)

                        # Delay 2
                        time.sleep(delay2)

                        # Zoom In
                        if self.active_settings.get("cast_zoom_in_enabled", True):
                            for _ in range(zoom_in_scrolls):
                                mouse_scroll(1)

                        # Delay 3
                        time.sleep(delay3)

                        # Look Down
                        if self.active_settings.get("cast_look_down_enabled", True):
                            shake_box = self.active_settings.get("shake_box")
                            if shake_box:
                                # Calculate center of shake_box
                                shake_center_x = (shake_box["x1"] + shake_box["x2"]) // 2
                                shake_center_y = (shake_box["y1"] + shake_box["y2"]) // 2

                                # Teleport mouse to center of shake_box
                                mouse_move_to(shake_center_x, shake_center_y)

                                # Nudge mouse by 1 pixel so Roblox registers the position
                                windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)

                                # Hold right click
                                mouse_down_right()

                                # Move mouse down by configured distance
                                look_down_distance = self.active_settings.get("look_down_distance", 2000)
                                windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, look_down_distance, 0, 0)

                                # Release right click
                                mouse_up_right()

                                # Teleport mouse back to center of shake_box
                                mouse_move_to(shake_center_x, shake_center_y)

                                # Nudge mouse by 1 pixel so Roblox registers the position
                                windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)

                        # Delay 4
                        time.sleep(delay4)

                        # Hold Left Click
                        mouse_down()

                        # Delay 5
                        time.sleep(delay5)

                        # Perfect Cast Release
                        mouse_up()

                        # Delay 6
                        time.sleep(delay6)

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
                    # Track when duplicate was first detected
                    duplicate_start_time = None

                    while not shake_complete and self.loop_running:
                        # Check timeout
                        if time.time() - shake_start_time > shake_timeout:
                            print("[Loop] Shake timeout - returning to cast")
                            break

                        # Capture shake_box area for shake detection
                        shake_box = self.active_settings.get("shake_box")
                        shake_x1, shake_y1 = shake_box["x1"], shake_box["y1"]
                        shake_x2, shake_y2 = shake_box["x2"], shake_box["y2"]

                        # Use mss for faster capture (10x faster than PIL)
                        monitor = {"top": shake_y1, "left": shake_x1, "width": shake_x2 - shake_x1, "height": shake_y2 - shake_y1}
                        sct_img = sct.grab(monitor)
                        shake_frame = np.array(sct_img)
                        shake_frame = cv2.cvtColor(shake_frame, cv2.COLOR_BGRA2BGR)

                        # Get confidence threshold from settings
                        shake_confidence_threshold = self.active_settings.get("shake_confidence_threshold", 0.5)

                        # Run shake model detection on shake_box
                        shake_results = shake_model(
                            shake_frame,
                            verbose=False,
                            conf=shake_confidence_threshold,
                            max_det=1  # Only 1 shake indicator at a time
                        )

                        shake_found = False

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

                                    # If shake hasn't moved much (within threshold), skip it
                                    # Scale the threshold based on resolution (user sets value for 1440p reference)
                                    position_threshold_base = self.active_settings.get("shake_position_threshold", 10)
                                    position_threshold = int(position_threshold_base * self.scale_avg)
                                    if dist_x < position_threshold and dist_y < position_threshold:
                                        # Start duplicate timer if not already started
                                        if duplicate_start_time is None:
                                            duplicate_start_time = time.time()
                                            print(f"[Shake] Duplicate detected - starting 1s force-click timer")

                                        # Check if duplicate has persisted for more than the timeout
                                        duplicate_timeout = self.active_settings.get("shake_duplicate_timeout", 1.0)
                                        if time.time() - duplicate_start_time > duplicate_timeout:
                                            print(f"[Shake] Duplicate timeout ({duplicate_timeout}s) - forcing click to break loop")
                                            # Force click the duplicate and reset position tracking
                                            mouse_move_to(screen_x, screen_y)
                                            windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                            mouse_click()
                                            self.last_shake_position = None  # Reset so next detection won't be duplicate
                                            duplicate_start_time = None  # Reset duplicate timer
                                            shake_found = True
                                            shake_start_time = time.time()  # Reset main timeout
                                            break

                                        print(f"[Shake] Ignoring duplicate - movement ({dist_x}px, {dist_y}px) within threshold {position_threshold}px (base: {position_threshold_base}px)")
                                        shake_found = True  # Still consider shake as found
                                        shake_start_time = time.time()  # Reset timeout
                                        break

                                print(f"[Loop] Shake detected at ({screen_x}, {screen_y}) with confidence {confidence:.2f}")
                                # Move mouse to position
                                mouse_move_to(screen_x, screen_y)
                                # Nudge mouse by 1 pixel so Roblox registers the position
                                windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                # Click after Roblox registers the position
                                mouse_click()

                                # Update last clicked position
                                self.last_shake_position = current_position
                                duplicate_start_time = None  # Reset duplicate timer since we clicked a new position
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

                        # Use mss for faster capture (10x faster than PIL)
                        monitor = {"top": fish_y1, "left": fish_x1, "width": fish_x2 - fish_x1, "height": fish_y2 - fish_y1}
                        sct_img = sct.grab(monitor)
                        fish_frame = np.array(sct_img)
                        fish_frame = cv2.cvtColor(fish_frame, cv2.COLOR_BGRA2BGR)

                        # Run fishing model detection on fish_box (transition check from shake to fish)
                        fishing_confidence_threshold = self.active_settings.get("fishing_confidence_threshold", 0.5)
                        fishing_results = fishing_model(
                            fish_frame,
                            verbose=False,
                            conf=fishing_confidence_threshold,
                            iou=0.3,      # Lower IoU for overlapping Target Line and Fish Bar
                            max_det=2     # Only 2 objects: Target Line + Fish Bar
                        )

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

                        # Print detection summary
                        print(f"[Debug] Detection Summary - Target Line: {'YES' if target_line_found else 'NO'} ({target_line_conf:.2f}), Fish Bar: {'YES' if fish_bar_found else 'NO'} ({fish_bar_conf:.2f})")

                        # Check if both Target Line AND Fish Bar are detected
                        if target_line_found and fish_bar_found:
                            print(f"[Loop] Both Target Line ({target_line_conf:.2f}) and Fish Bar ({fish_bar_conf:.2f}) detected - proceeding to Fish stage")
                            shake_complete = True
                        # No delay - run as fast as possible

                    # If shake didn't complete (timed out), restart from cast
                    if not shake_complete:
                        continue

                if not self.loop_running:
                    break

                # Fish step
                if self.active_settings.get("flow_fish_enabled", True):
                    print("[Loop] Fish stage started")

                    # Cache debug overlay setting 
                    show_live_feed = self.active_settings.get("fish_show_live_feed", False)

                    # Create debug overlay for visual feedback if enabled
                    if show_live_feed:
                        self.create_debug_overlay()

                    # Get fish box coordinates
                    fish_box = self.active_settings.get("fish_box")
                    fish_x1, fish_y1 = fish_box["x1"], fish_box["y1"]
                    fish_x2, fish_y2 = fish_box["x2"], fish_box["y2"]
                    capture_width = fish_x2 - fish_x1
                    capture_height = fish_y2 - fish_y1
                
                    confidence_threshold = self.active_settings.get("fishing_confidence_threshold", 0.1)  # Very low = accept low confidence
                
                    # V4-Style Controller Parameters
                    KP = self.active_settings.get("fish_kp", 0.8)
                    KD = self.active_settings.get("fish_kd", 0.0)
                    target_tol_px = self.active_settings.get("fish_target_tol_px", 10.0)
                    pd_clamp = self.active_settings.get("fish_pd_clamp", 100.0)
                    boundary_factor = self.active_settings.get("fish_boundary_factor", 0.15)
                    cooldown_duration = self.active_settings.get("fish_cooldown_duration", 1.0)
                
                    print("[Fish] V4-Style State Machine Initialized")
                    print(f"[Fish] Confidence Threshold: {confidence_threshold}")
                    print(f"[Fish] KP={KP}, KD={KD}, Target_Tol={target_tol_px}px, PD_Clamp=±{pd_clamp}")
                    print(f"[Fish] Boundary={boundary_factor}, Cooldown={cooldown_duration}s")
                    print(f"[Fish] Running at YOLO speed (~50 FPS)")
                
                    # Reset state machine for this fishing attempt
                    self.estimated_box_length = 0.0
                    self.has_calculated_length_once = False
                    self.last_left_x = None
                    self.last_right_x = None
                    self.box_center_x = None
                    self.lost_target_line_time = 0.0
                    self.tracking_lost_time = 0.0
                    self.last_error = None
                    self.last_target_x = None
                    self.is_holding_click = False
                
                    # Track last loop time for time delta calculations
                    last_time = time.time()
                
                    # Main control loop (V4-style state machine)
                    while self.loop_running:
                    
                        current_time = time.time()
                        time_delta = current_time - last_time
                        last_time = current_time
                    
                        # ==================== YOLO DETECTION (Replaces v4 Pixel Detection) ====================
                        monitor = {"top": fish_y1, "left": fish_x1, "width": capture_width, "height": capture_height}
                        sct_img = sct.grab(monitor)
                        fish_frame = np.array(sct_img)
                        fish_frame = cv2.cvtColor(fish_frame, cv2.COLOR_BGRA2BGR)
                    
                        fishing_results = fishing_model(
                            fish_frame,
                            verbose=False,
                            conf=confidence_threshold,
                            iou=0.3,
                            max_det=2
                        )
                    
                        # Extract YOLO detections
                        target_line_x = None
                        target_line_conf = None  # Track confidence for debug
                        bar_left_x = None
                        bar_right_x = None
                        bar_center_x = None
                        bar_conf = None  # Track confidence for debug
                        target_line_pixel_count = 0  # For v4 idle threshold check
                        box_pixel_count = 0
                    
                        for result in fishing_results:
                            for box in result.boxes:
                                class_id = int(box.cls[0].item())
                                class_name = fishing_model.names[class_id]
                                confidence = float(box.conf[0].item())
                            
                                if confidence < confidence_threshold:
                                    continue
                                
                                # Get bounding box coordinates
                                xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                                x_center = int((xyxy[0] + xyxy[2]) / 2)
                                box_width = int(xyxy[2] - xyxy[0])
                                box_height = int(xyxy[3] - xyxy[1])
                            
                                if class_name == "Target Line":
                                    target_line_x = x_center
                                    target_line_conf = confidence
                                    target_line_pixel_count = box_width * box_height  # Approximate pixel count
                                elif class_name == "Fish Bar":
                                    bar_left_x = int(xyxy[0])
                                    bar_right_x = int(xyxy[2])
                                    bar_center_x = x_center
                                    bar_conf = confidence
                                    box_pixel_count = box_width * box_height
                    
                        # Update debug overlay if enabled
                        if show_live_feed:
                            self.update_debug_overlay(target_line_x, bar_left_x, bar_right_x, bar_center_x)
                    
                        # ==================== V4 FISHING CONTROL ====================
                        
                        # Calculate initial box length on first detection
                        if not self.has_calculated_length_once and bar_left_x is not None and bar_right_x is not None:
                            new_length = bar_right_x - bar_left_x
                            if 10 < new_length < capture_width:
                                self.estimated_box_length = new_length
                                self.last_left_x = float(bar_left_x)
                                self.last_right_x = float(bar_right_x)
                                self.box_center_x = (self.last_left_x + self.last_right_x) / 2.0
                                self.has_calculated_length_once = True
                                print(f"[Fish] Initial Box Length: {new_length:.1f}px, Center: {self.box_center_x:.1f}px")
                    
                        # --- Target Line LOST Cooldown ---
                        if target_line_x is None:
                            # Target line lost - start or continue cooldown
                            if self.lost_target_line_time == 0.0:
                                self.lost_target_line_time = current_time
                                print(f"[Fish] Target line LOST. Starting {cooldown_duration}s cooldown...")
                        
                            # Check if cooldown expired
                            if current_time - self.lost_target_line_time >= cooldown_duration:
                                print("[Fish] Target line lost for too long. Returning to cast.")
                                break  # Exit fishing loop, return to cast
                        
                            # Still in cooldown - release mouse and wait
                            if self.is_holding_click:
                                mouse_up()
                                self.is_holding_click = False
                        
                            time_left = cooldown_duration - (current_time - self.lost_target_line_time)
                            print(f"[Fish] Line Lost Cooldown | Time Left: {time_left:.2f}s | RELEASE")
                        
                            # Reset PD state
                            self.last_target_x = None
                            self.last_error = None
                        
                            continue  # Skip control logic this frame
                        else:
                            # Target line found - reset cooldown and remember position
                            self.lost_target_line_time = 0.0
                            self.last_target_x = target_line_x  # Remember last known position
                    
                        # --- Tracking Logic (Color Detection → YOLO Detection) ---
                        tracking_successful = False
                    
                        # Direct YOLO Tracking (replaces v4's color tracking)
                        if box_pixel_count > 100 and bar_left_x is not None and bar_right_x is not None:
                            new_length = bar_right_x - bar_left_x
                        
                            if 10 < new_length < capture_width:
                                self.estimated_box_length = new_length
                                self.last_left_x = float(bar_left_x)
                                self.last_right_x = float(bar_right_x)
                                self.box_center_x = (self.last_left_x + self.last_right_x) / 2.0
                                self.has_calculated_length_once = True
                                tracking_successful = True
                                status_color_mode = "Direct YOLO Tracking"
                            else:
                                status_color_mode = "YOLO Tracking Failed (Bad Size)"
                        else:
                            status_color_mode = "YOLO Tracking Failed (No Box Detected)"
                    
                        # --- CRITICAL FALLBACK: BAR LOST but TARGET LINE PRESENT ---
                        # If bar is lost but target line exists, spam click (dead zone mode)
                        if target_line_x is not None and not tracking_successful:
                            # Toggle hold state every frame for spam clicking
                            should_hold = not self.is_holding_click
                        
                            # Execute spam click
                            if should_hold and not self.is_holding_click:
                                mouse_down()
                                self.is_holding_click = True
                            elif not should_hold and self.is_holding_click:
                                mouse_up()
                                self.is_holding_click = False
                        
                            control_state = "HOLD" if self.is_holding_click else "RELEASE"
                            print(f"[Fish] Bar Lost - SPAM CLICK | {control_state}")
                        
                            continue  # Skip normal PD control
                    
                        if not tracking_fully_lost:
                            # Tracking is back (or never lost), reset timer
                            self.tracking_lost_time = 0.0
                    
                        if tracking_fully_lost:
                            if self.tracking_lost_time == 0.0:
                                self.tracking_lost_time = current_time
                                print(f"[Fish] Box tracking LOST. Starting {cooldown_duration}s grace period...")
                        
                            # --- GRACE PERIOD ACTIVE (No Spam Click - Release Mouse) ---
                            if current_time - self.tracking_lost_time < cooldown_duration:
                                if self.is_holding_click:
                                    mouse_up()
                                    self.is_holding_click = False
                            
                                # Reset PD state
                                self.last_error = None
                                self.last_target_x = None
                            
                                time_left = cooldown_duration - (current_time - self.tracking_lost_time)
                                print(f"[Fish] Grace Period | Time Left: {time_left:.2f}s | RELEASE")
                            
                                continue  # Skip PD control
                        
                            # --- GRACE PERIOD EXPIRED (Engage Spam Click) ---
                            else:
                                # Toggle hold state every frame for spam clicking
                                should_hold = not self.is_holding_click
                            
                                # Align box center to target line to prevent runaway
                                self.box_center_x = target_line_x
                                self.last_left_x = None
                                self.last_right_x = None
                            
                                # Reset PD state
                                self.last_error = None
                                self.last_target_x = None
                            
                                status_color_mode = "CRITICAL SPAM (Grace Expired)"
                            
                                # Execute spam click
                                if should_hold and not self.is_holding_click:
                                    mouse_down()
                                    self.is_holding_click = True
                                elif not should_hold and self.is_holding_click:
                                    mouse_up()
                                    self.is_holding_click = False
                            
                                control_state = "HOLD" if self.is_holding_click else "RELEASE"
                                box_len = f"{self.estimated_box_length:.1f}" if self.has_calculated_length_once else "..."
                                print(f"[Fish] {status_color_mode} | Ctrl: {control_state} | Box Len: {box_len}px")
                            
                                continue  # Skip standard PD control
                    
                        # --- CONTROL LOGIC (V4-Style PD Controller with Boundary Override) ---
                        if target_line_x is not None and self.box_center_x is not None and self.has_calculated_length_once:
                            
                                error = target_line_x - self.box_center_x  # Positive = target RIGHT of bar (need HOLD)
                            
                                # Boundary margin calculation
                                boundary_px_margin = self.estimated_box_length * boundary_factor
                            
                                # --- A. Boundary Override Check (V4 Emergency Mode) ---
                                is_near_left_boundary = (target_line_x < boundary_px_margin)
                                is_near_right_boundary = (target_line_x > capture_width - boundary_px_margin)
                            
                                if is_near_left_boundary:
                                    # Emergency: Direct mouse control - RELEASE
                                    if self.is_holding_click:
                                        mouse_up()
                                        self.is_holding_click = False
                                    status_suffix = " | Boundary Override: RELEASE"
                                    control_state = "RELEASE"
                                    # Skip PD control calculation
                                    print(f"[Boundary Override] Left Edge | {control_state}{status_suffix}")
                                    continue  # Skip to next frame
                                    
                                elif is_near_right_boundary:
                                    # Emergency: Direct mouse control - HOLD
                                    if not self.is_holding_click:
                                        mouse_down()
                                        self.is_holding_click = True
                                    status_suffix = " | Boundary Override: HOLD"
                                    control_state = "HOLD"
                                    # Skip PD control calculation
                                    print(f"[Boundary Override] Right Edge | {control_state}{status_suffix}")
                                    continue  # Skip to next frame
                                    
                                # --- B. PD Control Calculation (Normal Mode) ---
                                P_term = KP * error
                                D_term = 0.0
                            
                                if self.last_error is not None and time_delta > 0.001:
                                    error_rate = (error - self.last_error) / time_delta
                                    D_term = KD * error_rate
                            
                                control_signal = P_term + D_term
                                control_signal = np.clip(control_signal, -pd_clamp, pd_clamp)
                                status_suffix = f" | PD Control: Signal={control_signal:+.2f}"
                            
                                # Update PD state
                                self.last_error = error
                                self.last_target_x = target_line_x
                            
                                # --- C. Convert Control Signal to Action (Dead Zone = Spam Click) ---
                                action_threshold = target_tol_px
                            
                                if control_signal > action_threshold:
                                    # Target far right - HOLD
                                    should_hold = True
                                elif control_signal < -action_threshold:
                                    # Target far left - RELEASE
                                    should_hold = False
                                else:
                                    # Within dead zone: Spam Click (alternate hold state)
                                    should_hold = not self.is_holding_click
                                    status_color_mode = "Dead Zone SPAM"
                                    status_suffix = " | Dead Zone SPAM"
                            
                                # --- D. Execute Mouse Action ---
                                if should_hold and not self.is_holding_click:
                                    mouse_down()
                                    self.is_holding_click = True
                                elif not should_hold and self.is_holding_click:
                                    mouse_up()
                                    self.is_holding_click = False
                            
                                # Debug output
                                control_state = "HOLD" if self.is_holding_click else "RELEASE"
                                print(f"[PD Control] Error: {error:+4.0f}px | P: {P_term:+6.1f} | Signal: {control_signal:+6.1f} | {control_state}{status_suffix}")
                    
                        else:
                            # Fallback - lost tracking data but not fully lost
                            if self.is_holding_click:
                                mouse_up()
                                self.is_holding_click = False
                            print(f"[Fish] Tracking Lost/Waiting | RELEASE")
                        
                            # Reset PD state
                            self.last_target_x = None
                        
                        # NO SLEEP - run at YOLO speed (~50 FPS)
                        # ============================================================
                
                    # Cleanup
                    if self.is_holding_click:
                        mouse_up()
                        self.is_holding_click = False
                
                    print("[Fish] Fish stage stopped")
                    print("[Loop] Fish stage complete")

                    # Increment loop counter and send Discord notification if enabled
                    self.loop_counter += 1
                    print(f"[Loop] Loop #{self.loop_counter} completed")

                    if self.active_settings.get("discord_enabled", False):
                        discord_mode = self.active_settings.get("discord_mode", "Screenshot")

                        if discord_mode == "Screenshot":
                            loops_per_screenshot = self.active_settings.get("discord_screenshot_loops", 10)
                            if self.loop_counter % loops_per_screenshot == 0:
                                print(f"[Discord] Sending screenshot notification (Loop {self.loop_counter})")
                                self.discord_send_screenshot()
                        elif discord_mode == "Text":
                            loops_per_text = self.active_settings.get("discord_text_loops", 10)
                            if self.loop_counter % loops_per_text == 0:
                                print(f"[Discord] Sending text notification (Loop {self.loop_counter})")
                                self.discord_send_text(self.loop_counter)

                if not self.loop_running:
                    break

                print("[Loop] Cycle complete, restarting...")
        finally:
            # Always clean up mss instance when loop ends
            sct.close()
            print("[Loop] Screen capture resources cleaned up")

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

    def create_debug_overlay(self):
        """Create a transparent overlay window above the fish area for debug visualization"""
        if self.debug_overlay_window is not None:
            return  # Already created

        fish_box = self.active_settings.get("fish_box")
        if not fish_box:
            return

        fish_x1, fish_y1 = fish_box["x1"], fish_box["y1"]
        fish_x2 = fish_box["x2"]
        fish_width = fish_x2 - fish_x1

        # Create overlay window above the fish box with safety margin
        overlay_height = 40
        safety_margin = 10  # Extra pixels between overlay and fish box to prevent any overlap
        self.debug_overlay_window = tk.Toplevel(self.root)
        self.debug_overlay_window.title("Fish Debug Overlay")
        self.debug_overlay_window.attributes('-topmost', True)
        self.debug_overlay_window.attributes('-alpha', 0.85)  # Semi-transparent
        self.debug_overlay_window.overrideredirect(True)  # No window decorations

        # Position above fish box with safety margin to avoid interfering with YOLO screenshot
        overlay_y = fish_y1 - overlay_height - safety_margin
        self.debug_overlay_window.geometry(f"{fish_width}x{overlay_height}+{fish_x1}+{overlay_y}")

        # Create canvas for drawing
        self.debug_overlay_canvas = tk.Canvas(
            self.debug_overlay_window,
            width=fish_width,
            height=overlay_height,
            bg='black',
            highlightthickness=0
        )
        self.debug_overlay_canvas.pack()

    def update_debug_overlay(self, target_line_x, bar_left_x, bar_right_x, bar_center_x):
        """Update debug overlay with current detection positions"""
        if self.debug_overlay_canvas is None or self.debug_overlay_window is None:
            return

        # Check if window still exists (not destroyed)
        try:
            if not self.debug_overlay_window.winfo_exists():
                self.debug_overlay_canvas = None
                self.debug_overlay_window = None
                return
        except:
            # Exception means window was destroyed
            self.debug_overlay_canvas = None
            self.debug_overlay_window = None
            return

        # Clear previous drawings
        try:
            self.debug_overlay_canvas.delete("all")
        except:
            # Canvas was destroyed
            self.debug_overlay_canvas = None
            self.debug_overlay_window = None
            return

        # Get canvas dimensions
        canvas_height = 40

        # Draw indicators - wrap all canvas operations in try-except
        try:
            if target_line_x is not None:
                # Target line - Green vertical line
                self.debug_overlay_canvas.create_line(
                    target_line_x, 0, target_line_x, canvas_height,
                    fill='#00FF00', width=3, tags="target_line"
                )
                self.debug_overlay_canvas.create_text(
                    target_line_x, 5, text="TARGET", fill='#00FF00',
                    font=("Arial", 8, "bold"), anchor="n", tags="target_line"
                )

            if bar_center_x is not None:
                # Bar center - Yellow dot
                self.debug_overlay_canvas.create_oval(
                    bar_center_x - 5, canvas_height // 2 - 5,
                    bar_center_x + 5, canvas_height // 2 + 5,
                    fill='#FFFF00', outline='#FFFF00', tags="bar_center"
                )
                self.debug_overlay_canvas.create_text(
                    bar_center_x, canvas_height - 5, text="CENTER", fill='#FFFF00',
                    font=("Arial", 8, "bold"), anchor="s", tags="bar_center"
                )

            if bar_left_x is not None:
                # Bar left edge - Red vertical line
                self.debug_overlay_canvas.create_line(
                    bar_left_x, 0, bar_left_x, canvas_height // 2,
                    fill='#FF0000', width=2, tags="bar_left"
                )
                self.debug_overlay_canvas.create_text(
                    bar_left_x, 2, text="L", fill='#FF0000',
                    font=("Arial", 7), anchor="n", tags="bar_left"
                )

            if bar_right_x is not None:
                # Bar right edge - Cyan vertical line
                self.debug_overlay_canvas.create_line(
                    bar_right_x, 0, bar_right_x, canvas_height // 2,
                    fill='#00FFFF', width=2, tags="bar_right"
                )
                self.debug_overlay_canvas.create_text(
                    bar_right_x, 2, text="R", fill='#00FFFF',
                    font=("Arial", 7), anchor="n", tags="bar_right"
                )
        except:
            # Canvas was destroyed mid-operation
            self.debug_overlay_canvas = None
            self.debug_overlay_window = None
            return

        # Force update
        try:
            self.debug_overlay_canvas.update_idletasks()
        except:
            # Canvas was destroyed
            self.debug_overlay_canvas = None
            self.debug_overlay_window = None

    def close_debug_overlay(self):
        """Close and destroy the debug overlay window"""
        if self.debug_overlay_window is not None:
            self.debug_overlay_window.destroy()
            self.debug_overlay_window = None
            self.debug_overlay_canvas = None

    def toggle_live_feed(self):
        """Handle live feed checkbox toggle"""
        # Save the setting directly (it's a boolean, not a StringVar)
        value = self.fish_show_live_feed_var.get()
        self.active_settings["fish_show_live_feed"] = value
        print(f"[Debug] Live feed toggled: {value}")

        # If unchecked, close the debug overlay immediately
        if not value:
            self.close_debug_overlay()
            print("[Debug] Debug overlay closed")

    def on_closing(self):
        """Handle window close event - save active settings"""
        # Stop loop if running
        self.loop_running = False
        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=2)

        # Close debug overlay if open
        self.close_debug_overlay()

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
