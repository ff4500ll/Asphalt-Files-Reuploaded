import tkinter as tk
from tkinter import ttk
import os
import time
import numpy as np
import threading
import sys
import logging
import asyncio
import aiohttp
import requests
import json
import io
import win32gui
import win32api
import win32ui
import win32con
from PIL import Image

# --- Setup Logging (First step to ensure everything is logged) ---
LOG_FILE = "Debug.txt"
# Initially setup basic logging to console only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(threadName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stderr)]  # Only console initially
)

# Keep track of file handler for later management
_debug_file_handler = None

def _setup_debug_logging():
    """Enable debug logging to file."""
    global _debug_file_handler
    if _debug_file_handler is None:
        _debug_file_handler = logging.FileHandler(LOG_FILE, mode='w')
        _debug_file_handler.setLevel(logging.INFO)
        _debug_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(threadName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logging.getLogger().addHandler(_debug_file_handler)

def _disable_debug_logging():
    """Disable debug logging to file."""
    global _debug_file_handler
    if _debug_file_handler is not None:
        logging.getLogger().removeHandler(_debug_file_handler)
        _debug_file_handler.close()
        _debug_file_handler = None

def _disable_all_logging():
    """Completely disable all logging to prevent performance overhead."""
    # Set logging level to CRITICAL to prevent any log message processing
    logging.getLogger().setLevel(logging.CRITICAL + 1)
    
def _enable_logging():
    """Re-enable logging at INFO level."""
    logging.getLogger().setLevel(logging.INFO)

# Efficient logging wrapper that checks OUTPUT_DEBUG before executing
class ConditionalLogger:
    def __init__(self, app_instance=None):
        self._app = app_instance
    
    def set_app(self, app_instance):
        """Set the application instance for checking OUTPUT_DEBUG state."""
        self._app = app_instance
    
    def _should_log(self):
        """Check if logging is enabled via OUTPUT_DEBUG setting."""
        return self._app is not None and hasattr(self._app, 'output_debug_enabled') and self._app.output_debug_enabled.get()
    
    def info(self, message):
        if self._should_log():
            logging.info(message)
    
    def debug(self, message):
        if self._should_log():
            logging.debug(message)
    
    def warning(self, message):
        if self._should_log():
            logging.warning(message)
    
    def error(self, message):
        if self._should_log():
            logging.error(message)
    
    def critical(self, message):
        if self._should_log():
            logging.critical(message)

# Create global conditional logger instance
conditional_logger = ConditionalLogger()

# Initially don't log to file - will be enabled based on config later
print("Application startup. Setting up imports.")
# --- Imports for Screen Capture ---
try:
    from PIL import Image, ImageTk
    import mss
    # PIL compatibility fixes for resampling (using the recommended constant name)
    try:
        Image.Resampling.LANCZOS
    except AttributeError:
        # Fallback for older PIL versions
        Image.Resampling.LANCZOS = Image.ANTIALIAS

    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False
    print("WARNING: PIL/mss not found. Screen capture is disabled.")

# --- Imports for Computer Vision (Color Detection) ---
try:
    import cv2
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    print("WARNING: OpenCV (cv2) not found. Color detection is disabled.")

# --- Imports for Global Hotkeys ---
try:
    import keyboard
    GLOBAL_HOTKEYS_AVAILABLE = True
except ImportError:
    GLOBAL_HOTKEYS_AVAILABLE = False
    print("WARNING: Keyboard library not found. Global hotkeys are disabled.")

# --- Imports for Mouse Control (Click-and-Hold) ---
try:
    import pyautogui
    # Set fail-safe to False to prevent pyautogui from quitting on mouse movements to screen corners
    pyautogui.FAILSAFE = False
    MOUSE_CONTROL_AVAILABLE = True
except ImportError:
    MOUSE_CONTROL_AVAILABLE = False
    print("WARNING: PyAutoGUI not found. Mouse control (clicking) is disabled.")

# --- Windows API and DPI Setup ---
try:
    import ctypes
    from ctypes import windll
    
    # Set DPI awareness early to ensure consistent coordinate handling
    try:
        windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_PER_MONITOR_DPI_AWARE
        print("DPI awareness set to per-monitor aware")
    except:
        try:
            windll.user32.SetProcessDPIAware()  # Fallback for older Windows
            print("DPI awareness set to system aware (fallback)")
        except:
            print("WARNING: Failed to set DPI awareness - coordinates may be inconsistent")
    
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False
    print("WARNING: Windows API (ctypes) not available - some features may not work properly")
# ----------------------------------

# Security verification function
def _verify_integrity():
    """Verify critical security components haven't been tampered with."""
    import hashlib
    import base64
    try:
        # Check critical encoded data
        _test_data = b'QXNwaGFsdENha2U='
        _decoded = base64.b64decode(_test_data).decode('utf-8')
        if _decoded != 'AsphaltCake':
            import sys
            sys.exit(1)
        
        # Additional checks
        _url_data = b'aHR0cHM6Ly93d3cueW91dHViZS5jb20vQEFzcGhhbHRDYWtlP3N1Yl9jb25maXJtYXRpb249MQ=='
        _url = base64.b64decode(_url_data).decode('utf-8')
        if 'AsphaltCake' not in _url or 'youtube.com' not in _url:
            import sys
            sys.exit(1)
            
        return True
    except:
        import sys
        sys.exit(1)

# Run security check on startup
_verify_integrity()

CONFIG_FILE = "Config.txt"

# Default fallback geometry values (will be replaced with scaled values)
DEFAULT_GUI_GEOM = "648x405+54+877" 
DEFAULT_SHAKE = "1336x796+614+287"
DEFAULT_FISH = "1034x48+763+1213"
DEFAULT_LIVE_FEED_POS = "+760+1033"

# Color Matching Configuration (Adjust these hex values for your game colors)
TARGET_LINE_COLOR_HEX = "0x434B5B"       # The moving line that must be followed
INDICATOR_ARROW_COLOR_HEX = "0x848587"   # The arrows on the player-controlled rectangle
BOX_COLOR_1_HEX = "0xF1F1F1" # Used in Initializing and Fishing (Direct Track)
BOX_COLOR_2_HEX = "0xFFFFFF" # Used in Initializing and Fishing (Direct Track)

# --- ROD-SPECIFIC COLOR CONFIGURATION ---
# Global dictionary to store rod-specific tolerance overrides
_rod_tolerance_overrides = {}

def get_rod_colors(rod_type, config_overrides=None):
    """
    Returns rod-specific color configuration and tolerances.
    Returns None for colors if rod type doesn't have color detection enabled.
    config_overrides: dictionary containing loaded config values to override defaults
    """
    rod_configs = {
        "Default": {
            "target_line": "0x434B5B",
            "indicator_arrow": "0x848587",
            "box_color_1": "0xF1F1F1",
            "box_color_2": "0xFFFFFF",
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 0,  # Updated from 3 to 0
            "box_color_tolerance": 3         # Updated from 1 to 3
        },
        # Other rod types will be added later with their specific colors
        "Evil Pitch Fork": {
            "target_line": "0x671515",  # #671515 (dark red)
            "indicator_arrow": "0x848587",  # Same as default
            "box_color_1": "0xF1F1F1",  # Same as default
            "box_color_2": "0xFFFFFF",   # Same as default
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 3,
            "box_color_tolerance": 3     # Updated from 1 to 3
        },
        "Onirifalx": {
            "target_line": "0x000000",
            "indicator_arrow": None,
            "box_color_1": "0xB4DEF6",
            "box_color_2": "0x6689B5",
            "target_line_tolerance": 0,     # Updated from 2 to 0
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Polaris Serenade": {
            "target_line": "0x29CAF5",      # #29CAF5 in hex format (consistent with other rods)
            "indicator_arrow": "0x848587",
            "box_color_1": "0xF1F1F1",
            "box_color_2": "0xFFFFFF",
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 3,
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Sword of Darkness": {
            "target_line": None,
            "indicator_arrow": None,
            "box_color_1": None,
            "box_color_2": None,
            "target_line_tolerance": 0,     # Updated from 2 to 0
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 0        # Updated from 1 to 0
        },
        "Wingripper": {
            "target_line": "0x707777",  # #707777 (gray)
            "indicator_arrow": None,
            "box_color_1": "0x151515",  # #151515 (dark gray)
            "box_color_2": None,
            "target_line_tolerance": 15,    # Updated from 2 to 15
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Axe of Rhoads": {
            "target_line": None,
            "indicator_arrow": None,
            "box_color_1": None,
            "box_color_2": None,
            "target_line_tolerance": 0,     # Updated from 2 to 0
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 0        # Updated from 1 to 0
        },
        "Chrysalis": {
            "target_line": None,
            "indicator_arrow": None,
            "box_color_1": None,
            "box_color_2": None,
            "target_line_tolerance": 0,     # Updated from 2 to 0
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 0        # Updated from 1 to 0
        },
        "Luminescent Oath": {
            "target_line": "0x434B5B",
            "indicator_arrow": "0x848587",
            "box_color_1": "0xF1F1F1",
            "box_color_2": "0xFFFFFF",
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 5, # Updated from 3 to 5
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Ruinous Oath": {
            "target_line": "0x434B5B",
            "indicator_arrow": "0x848587",
            "box_color_1": "0xF1F1F1",
            "box_color_2": "0xFFFFFF",
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 5, # Updated from 3 to 5
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Duskwire": {
            "target_line": "0xFFFFFF",  # #FFFFFF (white)
            "indicator_arrow": None,
            "box_color_1": "0x2F2F2F",  # #2F2F2F (dark gray)
            "box_color_2": "0x000000",   # #000000 (black)
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 3        # Updated from 1 to 3
        },
        "Sanguine Spire": {
            "target_line": "0x44110F",  # #44110F (dark reddish-brown)
            "indicator_arrow": None,
            "box_color_1": "0x540000",  # #540000 (dark red)
            "box_color_2": "0x220000",   # #220000 (very dark red)
            "target_line_tolerance": 2,
            "indicator_arrow_tolerance": 0, # Updated from 3 to 0
            "box_color_tolerance": 3        # Updated from 1 to 3
        }
    }
    
    # Get the base configuration for the specified rod type, or Default as fallback
    rod_config = rod_configs.get(rod_type, rod_configs["Default"]).copy()
    
    # Apply config overrides if provided
    if config_overrides:
        rod_key = rod_type.replace(' ', '_').upper()
        target_key = f"ROD_{rod_key}_TARGET_LINE_TOLERANCE"
        arrow_key = f"ROD_{rod_key}_INDICATOR_ARROW_TOLERANCE"
        box_key = f"ROD_{rod_key}_BOX_COLOR_TOLERANCE"
        
        # Apply rod-specific overrides if available
        if target_key in config_overrides:
            try:
                rod_config["target_line_tolerance"] = int(config_overrides[target_key])
            except (ValueError, TypeError):
                pass
                
        if arrow_key in config_overrides:
            try:
                rod_config["indicator_arrow_tolerance"] = int(config_overrides[arrow_key])
            except (ValueError, TypeError):
                pass
                
        if box_key in config_overrides:
            try:
                rod_config["box_color_tolerance"] = int(config_overrides[box_key])
            except (ValueError, TypeError):
                pass
    
    return rod_config

def update_rod_tolerances(rod_type, target_tolerance=None, arrow_tolerance=None, box_tolerance=None):
    """
    Update tolerance values for a specific rod type.
    This modifies the rod configuration in memory.
    """
    # This is a simplified approach - in a full implementation, you'd want to 
    # store these changes persistently and modify the actual rod configs
    pass

def get_all_rod_types():
    """
    Returns a list of all available rod types.
    """
    rod_configs = {
        "Default": {}, "Evil Pitch Fork": {}, "Onirifalx": {}, "Polaris Serenade": {},
        "Sword of Darkness": {}, "Wingripper": {}, "Axe of Rhoads": {}, "Chrysalis": {},
        "Luminescent Oath": {}, "Ruinous Oath": {}, "Duskwire": {}, "Sanguine Spire": {}
    }
    return list(rod_configs.keys())
# ------------------------------------------

# --- Multi-Monitor and Coordinate System Helper ---
class MonitorCoordinateHelper:
    """
    Handles multi-monitor setups, DPI scaling, and coordinate conversions to ensure
    consistent behavior across different screen configurations.
    """
    
    def __init__(self):
        self.virtual_screen_left = 0
        self.virtual_screen_top = 0
        self.virtual_screen_width = 0
        self.virtual_screen_height = 0
        self.primary_screen_width = 0
        self.primary_screen_height = 0
        self.refresh_monitor_info()
    
    def refresh_monitor_info(self):
        """Refresh monitor information for current setup"""
        try:
            if WINDOWS_API_AVAILABLE:
                # Get virtual screen (all monitors combined)
                self.virtual_screen_left = windll.user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
                self.virtual_screen_top = windll.user32.GetSystemMetrics(77)    # SM_YVIRTUALSCREEN  
                self.virtual_screen_width = windll.user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
                self.virtual_screen_height = windll.user32.GetSystemMetrics(79) # SM_CYVIRTUALSCREEN
                
                # Get primary monitor size
                self.primary_screen_width = windll.user32.GetSystemMetrics(0)   # SM_CXSCREEN
                self.primary_screen_height = windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
                
                conditional_logger.info(f"Monitor Info - Virtual: {self.virtual_screen_left},{self.virtual_screen_top} {self.virtual_screen_width}x{self.virtual_screen_height}")
                conditional_logger.info(f"Monitor Info - Primary: {self.primary_screen_width}x{self.primary_screen_height}")
            else:
                # Fallback to PyAutoGUI
                import pyautogui
                self.primary_screen_width, self.primary_screen_height = pyautogui.size()
                self.virtual_screen_left = 0
                self.virtual_screen_top = 0
                self.virtual_screen_width = self.primary_screen_width
                self.virtual_screen_height = self.primary_screen_height
                conditional_logger.warning("Using PyAutoGUI fallback for monitor detection")
                
        except Exception as e:
            conditional_logger.error(f"Failed to get monitor info: {e}")
            # Ultra fallback
            self.virtual_screen_left = 0
            self.virtual_screen_top = 0
            self.virtual_screen_width = 1920
            self.virtual_screen_height = 1080
            self.primary_screen_width = 1920 
            self.primary_screen_height = 1080
    
    def validate_coordinates(self, x, y):
        """Check if coordinates are within virtual screen bounds"""
        return (self.virtual_screen_left <= x <= self.virtual_screen_left + self.virtual_screen_width and
                self.virtual_screen_top <= y <= self.virtual_screen_top + self.virtual_screen_height)
    
    def clamp_coordinates(self, x, y):
        """Clamp coordinates to virtual screen bounds"""
        clamped_x = max(self.virtual_screen_left, 
                       min(x, self.virtual_screen_left + self.virtual_screen_width - 1))
        clamped_y = max(self.virtual_screen_top,
                       min(y, self.virtual_screen_top + self.virtual_screen_height - 1))
        return clamped_x, clamped_y
    
    def get_safe_scroll_position(self, target_x=None, target_y=None):
        """Get a safe position for scrolling operations"""
        if target_x is None or target_y is None:
            # Default to center of primary monitor
            return (self.primary_screen_width // 2, 
                   self.primary_screen_height // 2)
        
        # Validate and clamp the provided coordinates
        if self.validate_coordinates(target_x, target_y):
            return target_x, target_y
        else:
            return self.clamp_coordinates(target_x, target_y)

# Global monitor helper instance
monitor_helper = MonitorCoordinateHelper()

def get_scaled_geometry():
    """
    Calculate scaled geometry based on current screen resolution.
    Reference resolution: 2560x1440 (your monitor)
    Returns scaled default geometries for different screen resolutions.
    """
    # Reference values for 2560x1440 resolution
    ref_width, ref_height = 2560, 1440
    
    # Your desired default values for 2560x1440
    ref_gui_geom = "890x823+60+500"
    ref_shake_geom = "1336x796+614+287"
    ref_fish_geom = "1034x48+764+1171"
    ref_live_feed_pos = "+760+1033"
    
    # Get current screen resolution
    current_width = monitor_helper.primary_screen_width
    current_height = monitor_helper.primary_screen_height
    
    # Calculate scaling factors
    scale_x = current_width / ref_width
    scale_y = current_height / ref_height
    
    def scale_geometry_string(geom_str):
        """Scale a geometry string like '890x823+60+500'"""
        if 'x' in geom_str and '+' in geom_str:
            # Parse width x height + x_offset + y_offset
            size_part, pos_part = geom_str.split('+', 1)
            if '+' in pos_part:
                x_offset, y_offset = pos_part.split('+', 1)
            else:
                # Handle negative offsets
                parts = pos_part.split('-')
                if len(parts) == 2:
                    x_offset = parts[0]
                    y_offset = '-' + parts[1]
                else:
                    x_offset, y_offset = '0', '0'
            
            width, height = size_part.split('x')
            
            # Scale all values
            scaled_width = int(int(width) * scale_x)
            scaled_height = int(int(height) * scale_y)
            scaled_x = int(int(x_offset) * scale_x)
            scaled_y = int(int(y_offset) * scale_y)
            
            return f"{scaled_width}x{scaled_height}+{scaled_x}+{scaled_y}"
        return geom_str
    
    def scale_position_string(pos_str):
        """Scale a position string like '+760+1033'"""
        if pos_str.startswith('+'):
            pos_str = pos_str[1:]  # Remove leading +
            if '+' in pos_str:
                x_offset, y_offset = pos_str.split('+', 1)
                scaled_x = int(int(x_offset) * scale_x)
                scaled_y = int(int(y_offset) * scale_y)
                return f"+{scaled_x}+{scaled_y}"
        return pos_str
    
    # Scale the geometries
    scaled_gui_geom = scale_geometry_string(ref_gui_geom)
    scaled_shake_geom = scale_geometry_string(ref_shake_geom)
    scaled_fish_geom = scale_geometry_string(ref_fish_geom)
    scaled_live_feed_pos = scale_position_string(ref_live_feed_pos)
    
    # Log the scaling information
    # Note: These scaling info messages use direct logging since they occur before app initialization
    # They will be suppressed by the logging level when OUTPUT_DEBUG is disabled
    logging.info(f"Screen resolution scaling: {current_width}x{current_height} (scale factors: {scale_x:.2f}x, {scale_y:.2f}y)")
    logging.info(f"Scaled GUI_GEOM: {ref_gui_geom} -> {scaled_gui_geom}")
    logging.info(f"Scaled SHAKE_GEOM: {ref_shake_geom} -> {scaled_shake_geom}")
    logging.info(f"Scaled FISH_GEOM: {ref_fish_geom} -> {scaled_fish_geom}")
    logging.info(f"Scaled LIVE_FEED_POS: {ref_live_feed_pos} -> {scaled_live_feed_pos}")
    
    return {
        'GUI_GEOM': scaled_gui_geom,
        'SHAKE_GEOM': scaled_shake_geom,
        'FISH_GEOM': scaled_fish_geom,
        'LIVE_FEED_POS': scaled_live_feed_pos
    }

# --- Boundary Override Parameters ---
INIT_CLICKS_REQUIRED = 2

def hex_to_bgr(hex_color):
    """Converts a hex color string (e.g., '0x5B4B43') to a BGR tuple (B, G, R)."""
    if isinstance(hex_color, str) and hex_color.startswith('0x'):
        hex_color = hex_color[2:]

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (b, g, r)

def _get_bgr_bounds(bgr_color, tolerance):
    """
    Returns the lower and upper bounds for a BGR color based on a tolerance value.
    """
    B, G, R = bgr_color

    # Ensure bounds stay within the 0-255 range
    lower_bound = np.array([max(0, B - tolerance), max(0, G - tolerance), max(0, R - tolerance)])
    upper_bound = np.array([min(255, B + tolerance), min(255, G + tolerance), min(255, R + tolerance)])

    return lower_bound, upper_bound

# -------------------------------------------------------------------

class LiveFeedbackWindow(tk.Toplevel):
    """
    A borderless window showing a live, color-filtered screen capture,
    and drawing the simulated box. This runs on the MAIN Tkinter thread.
    """
    def __init__(self, master, target_geom_str, window_pos_str, target_fps):
        super().__init__(master)
        self.master_app = master
        self.title("Live Feed (Color Filter & Simulated Box)")
        self.target_geom = target_geom_str

        try:
            fps = int(target_fps)
            # Remove the 30 FPS cap - allow full user-specified FPS for live feed
            self.update_delay_ms = int(1000 / fps)
            # Enforce a minimum 1ms delay (1000 FPS max) to prevent system overload
            if self.update_delay_ms < 1: self.update_delay_ms = 1
        except (ValueError, ZeroDivisionError):
            # Fallback to a safe 30 FPS
            self.update_delay_ms = 33

        try:
            size_str, _ = target_geom_str.split('+', 1)
            width, height = map(int, size_str.split('x'))
        except ValueError:
            width, height = 300, 100

        if window_pos_str and '+' in window_pos_str:
            final_geom = f"{width}x{height}{window_pos_str}"
        else:
            final_geom = f"{width}x{height}{DEFAULT_LIVE_FEED_POS}"

        self.geometry(final_geom)

        self.overrideredirect(True)
        self.wm_attributes("-topmost", 1)

        self.canvas = tk.Canvas(self, bg='#000000', highlightthickness=0, width=width, height=height)
        self.canvas.pack(expand=True, fill="both")

        # FIX: Initialize self.photo and self.canvas_image_id for memory leak prevention
        self.photo = None
        self.canvas_image_id = None
        
        # Overlay element IDs for memory-efficient updates (instead of delete/recreate)
        self.overlay_box_id = None
        self.overlay_center_line_id = None
        self.overlay_target_line_id = None

        # --- MOVING LOGIC ---
        self.moving = False
        self.canvas.bind('<ButtonPress-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.do_drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drag)
        self.config(cursor="fleur")
        # --------------------

        self.after_id = None
        self.update_feedback()

    # --- DRAG METHODS ---
    def start_drag(self, event):
        self.moving = True
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.window_x = self.winfo_x()
        self.window_y = self.winfo_y()

    def do_drag(self, event):
        if self.moving:
            delta_x = event.x_root - self.start_x
            delta_y = event.y_root - self.start_y
            new_x = self.window_x + delta_x
            new_y = self.window_y + delta_y
            self.geometry(f'+{new_x}+{new_y}')

    def stop_drag(self, event):
        if self.moving:
            self.moving = False
            geom = self.winfo_geometry()
            try:
                _, pos_str = geom.split('+', 1)
                self.master_app.live_feed_position.set("+" + pos_str)
            except ValueError:
                pass
    # -------------------------------------------------------------------

    def draw_simulated_box(self, capture_height, capture_width):
        """
        Draws the simulated player-controlled box (RED) using the estimated edge coordinates.
        Uses coordinate updates instead of delete/recreate to prevent memory leaks.
        """
        # Retrieve the latest estimated edges from the main application state
        x0 = self.master_app.last_left_x
        x1 = self.master_app.last_right_x
        center_x = self.master_app.box_center_x
        target_x = self.master_app.last_target_x

        # Define box vertical position (positioned in the middle area like the actual game bar)
        bar_height = capture_height * 0.2  # 20% of the total height
        box_y_top = (capture_height - bar_height) / 2  # Center it vertically
        box_y_bottom = box_y_top + bar_height

        # --- RED SIMULATED BOX ---
        if x0 is not None and x1 is not None and center_x is not None:
            # Ensure coordinates are integers and clamped to the canvas bounds
            x0_int = max(0, min(capture_width, int(x0)))
            x1_int = max(0, min(capture_width, int(x1)))
            center_x_int = max(0, min(capture_width, int(center_x)))

            if self.overlay_box_id is None:
                # Create the box for the first time
                self.overlay_box_id = self.canvas.create_rectangle(
                    x0_int, box_y_top, x1_int, box_y_bottom,
                    outline="#FF0000", width=2, tags="simulated_box"
                )
            else:
                # Update existing box coordinates
                self.canvas.coords(self.overlay_box_id, x0_int, box_y_top, x1_int, box_y_bottom)
                # Make sure it's visible
                self.canvas.itemconfig(self.overlay_box_id, state='normal')

            # --- PINK CENTER LINE ---
            if self.overlay_center_line_id is None:
                # Create the center line for the first time
                self.overlay_center_line_id = self.canvas.create_line(
                    center_x_int, box_y_top, center_x_int, box_y_bottom,
                    fill="#FFC0CB", width=1, dash=(3, 3), tags="simulated_box_center"
                )
            else:
                # Update existing center line coordinates
                self.canvas.coords(self.overlay_center_line_id, center_x_int, box_y_top, center_x_int, box_y_bottom)
                # Make sure it's visible
                self.canvas.itemconfig(self.overlay_center_line_id, state='normal')
        else:
            # Hide box and center line if no valid coordinates
            if self.overlay_box_id is not None:
                self.canvas.itemconfig(self.overlay_box_id, state='hidden')
            if self.overlay_center_line_id is not None:
                self.canvas.itemconfig(self.overlay_center_line_id, state='hidden')

        # --- BLUE TARGET LINE ---
        if target_x is not None:
            target_x_int = max(0, min(capture_width, int(target_x)))
            
            if self.overlay_target_line_id is None:
                # Create the target line for the first time
                self.overlay_target_line_id = self.canvas.create_line(
                    target_x_int, 0, target_x_int, capture_height,
                    fill="#00BFFF", width=3, tags="target_line"
                )
            else:
                # Update existing target line coordinates
                self.canvas.coords(self.overlay_target_line_id, target_x_int, 0, target_x_int, capture_height)
                # Make sure it's visible
                self.canvas.itemconfig(self.overlay_target_line_id, state='normal')
        else:
            # Hide target line if no valid coordinate
            if self.overlay_target_line_id is not None:
                self.canvas.itemconfig(self.overlay_target_line_id, state='hidden')
    
    def force_overlay_update(self):
        """
        Immediately update overlays without waiting for the next scheduled update.
        Called by the main detection loop when box positions change.
        """
        try:
            if self.canvas and self.canvas.winfo_exists():
                canvas_w = self.canvas.winfo_width()
                canvas_h = self.canvas.winfo_height()
                if canvas_w > 1 and canvas_h > 1:  # Valid dimensions
                    self.draw_simulated_box(canvas_h, canvas_w)
        except Exception:
            pass  # Silent fail to prevent log spam


    def update_feedback(self):
        """
        Captures the screen area, applies color filters, and draws the simulated box.
        """
        # CRITICAL CHECK: If the main application has hidden the live feed, stop the loop.
        if not self.master_app.show_live_feed.get():
            self.close()
            return

        global SCREEN_CAPTURE_AVAILABLE, CV_AVAILABLE

        geom = self.target_geom

        # NOTE: No longer delete overlay elements - using persistent elements with show/hide logic
        # to prevent memory leaks and bitmap allocation failures

        canvas_w = self.winfo_width()
        canvas_h = self.winfo_height()

        sct_instance = None # Local mss instance for the main thread

        # Try to parse geometry
        try:
            size_str, pos_str = geom.split('+', 1)
            width, height = map(int, size_str.split('x'))
            x, y = map(int, pos_str.split('+'))
        except ValueError:
            width, height, x, y = 0, 0, 0, 0


        is_capture_valid = (SCREEN_CAPTURE_AVAILABLE and width > 0 and height > 0)

        processed_pil_img = None # Initialize variable for scope

        if is_capture_valid and width == canvas_w and height == canvas_h:
            try:
                # Initialize mss locally for this thread if available
                if SCREEN_CAPTURE_AVAILABLE:
                    sct_instance = mss.mss()
                    monitor = {"top": y, "left": x, "width": width, "height": height}
                    sct_img = sct_instance.grab(monitor)
                    pil_img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                    processed_pil_img = pil_img
                else:
                    raise ImportError("Screen capture not available.")


                # Apply color filtering to show what the detection algorithm sees
                if CV_AVAILABLE:
                    cv_img_rgb = np.array(pil_img)
                    cv_img_bgr = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2BGR)

                    combined_mask = np.zeros((height, width), dtype=np.uint8)

                    # Get rod-specific colors and tolerances
                    rod_type = self.master_app.rod_type_var.get()
                    rod_colors = get_rod_colors(rod_type, self.master_app.loaded_config)
                    
                    # Use rod-specific tolerances (get from rod config, not hardcoded fallbacks)
                    target_line_tol = rod_colors.get("target_line_tolerance")
                    indicator_arrow_tol = rod_colors.get("indicator_arrow_tolerance")
                    box_color_tol = rod_colors.get("box_color_tolerance")

                    # Only apply color masks if the rod type has colors configured
                    if rod_colors["target_line"] is not None:
                        # Mask 1: Target Line Color (Primary)
                        color1_bgr = hex_to_bgr(rod_colors["target_line"])
                        lower1, upper1 = _get_bgr_bounds(color1_bgr, target_line_tol)
                        mask1 = cv2.inRange(cv_img_bgr, lower1, upper1)
                        combined_mask = cv2.bitwise_or(combined_mask, mask1)

                    if rod_colors["indicator_arrow"] is not None:
                        # Mask 2: Indicator Arrow Color
                        color2_bgr = hex_to_bgr(rod_colors["indicator_arrow"])
                        lower2, upper2 = _get_bgr_bounds(color2_bgr, indicator_arrow_tol)
                        mask2 = cv2.inRange(cv_img_bgr, lower2, upper2)
                        combined_mask = cv2.bitwise_or(combined_mask, mask2)

                    if rod_colors["box_color_1"] is not None:
                        # --- Box Color 1 ---
                        color3_bgr = hex_to_bgr(rod_colors["box_color_1"])
                        lower3, upper3 = _get_bgr_bounds(color3_bgr, box_color_tol)
                        mask3 = cv2.inRange(cv_img_bgr, lower3, upper3)
                        combined_mask = cv2.bitwise_or(combined_mask, mask3)

                    if rod_colors["box_color_2"] is not None:
                        # --- Box Color 2 ---
                        color4_bgr = hex_to_bgr(rod_colors["box_color_2"])
                        lower4, upper4 = _get_bgr_bounds(color4_bgr, box_color_tol)
                        mask4 = cv2.inRange(cv_img_bgr, lower4, upper4)
                        combined_mask = cv2.bitwise_or(combined_mask, mask4)

                    # Additional box colors for rods like Duskwire
                    for i in range(3, 7):  # box_color_3 through box_color_6
                        color_key = f"box_color_{i}"
                        if rod_colors.get(color_key) is not None:
                            color_bgr = hex_to_bgr(rod_colors[color_key])
                            lower_bound, upper_bound = _get_bgr_bounds(color_bgr, box_color_tol)
                            mask = cv2.inRange(cv_img_bgr, lower_bound, upper_bound)
                            combined_mask = cv2.bitwise_or(combined_mask, mask)

                    masked_bgr_output = cv2.bitwise_and(cv_img_bgr, cv_img_bgr, mask=combined_mask)
                    processed_pil_img = Image.fromarray(cv2.cvtColor(masked_bgr_output, cv2.COLOR_BGR2RGB))
                else:
                    # Fallback to raw image if CV not available
                    processed_pil_img = pil_img

                # --- MEMORY LEAK FIX: Update the existing PhotoImage or create it once ---
                if self.photo is None:
                    # First run: Create the PhotoImage object and the Canvas item
                    self.photo = ImageTk.PhotoImage(processed_pil_img)
                    self.canvas_image_id = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW, tags="live_feed_image")
                else:
                    # Subsequent runs: Use the existing PhotoImage object to update the image data.
                    self.photo.paste(processed_pil_img)

                # --- DRAW OVERLAYS: Show assumed box and line locations ---
                self.draw_simulated_box(height, width)

            except Exception as e:
                logging.error(f"Runtime error during CV processing (Visual Feed): {e}")
                pass

        # --- FALLBACK / ERROR LOGIC START (Only black screen + red border) ---
        if not is_capture_valid or not CV_AVAILABLE:
            # MEMORY FIX: Hide image instead of deleting it to prevent bitmap allocation failures
            if self.canvas_image_id is not None:
                # Move image off-screen instead of deleting to preserve memory allocation
                try:
                    self.canvas.coords(self.canvas_image_id, -9999, -9999)
                except:
                    pass # Silent error handling for stability

            # CRITICAL FIX: DO NOT call self.canvas.delete("all") here.

            self.canvas.create_rectangle(5, 5, canvas_w - 5, canvas_h - 5,
                                         outline="#e03b3b", width=1)
            # Still attempt to draw the box on the black screen if coordinates exist
            self.draw_simulated_box(canvas_h, canvas_w)

        # --- FALLBACK / ERROR LOGIC END ---

        self.after_id = self.after(self.update_delay_ms, self.update_feedback)

    def close(self):
        self.master_app.save_live_feed_position()
        if self.after_id:
            self.after_cancel(self.after_id)

        # MEMORY FIX: Don't delete canvas elements during shutdown to prevent bitmap errors
        # Just clear references and let the window destruction handle cleanup
        self.canvas_image_id = None
        self.photo = None
        
        self.destroy()


class FloatingArea(tk.Toplevel):
    RESIZE_HANDLE_SIZE = 10

    def __init__(self, master, geom_var, name, color):
        super().__init__(master)
        self.geom_var = geom_var
        self.name = name
        self.geometry(self.geom_var.get())
        self.title(name)

        self.overrideredirect(True)
        self.wm_attributes("-alpha", 0.7)
        self.wm_attributes("-topmost", 1)

        self.frame = tk.Frame(self, bg=color, bd=3, relief="solid")
        self.frame.pack(expand=True, fill="both")

        label = tk.Label(self.frame, text=name, bg=color, fg="white", font=('Arial', 10, 'bold'))
        label.pack(padx=5, pady=5)

        self.resizing = False
        self.moving = False

        # Drag and resize bindings
        self.bind('<ButtonPress-1>', self.start_action)
        self.bind('<B1-Motion>', self.do_action)
        self.bind('<Motion>', self.check_cursor)
        self.bind('<ButtonRelease-1>', self.stop_action)
        label.bind('<ButtonPress-1>', self.start_action)
        label.bind('<B1-Motion>', self.do_action)
        self.bind('<Configure>', self.on_configure)

        self.withdraw()

    # Methods for geometry management
    def on_configure(self, event):
        if self.winfo_width() > 1 and self.winfo_height() > 1:
            self.update_geom_var()

    def update_geom_var(self):
        geom = self.winfo_geometry()
        if geom:
            self.geom_var.set(geom)

    def check_cursor(self, event):
        width = self.winfo_width()
        height = self.winfo_height()

        on_right = width - self.RESIZE_HANDLE_SIZE <= event.x <= width
        on_bottom = height - self.RESIZE_HANDLE_SIZE <= event.y <= height

        if on_right and on_bottom:
            self.config(cursor="sizing")
        elif not self.moving and not self.resizing:
            self.config(cursor="")

    def start_action(self, event):
        width = self.winfo_width()
        height = self.winfo_height()

        on_right = width - self.RESIZE_HANDLE_SIZE <= event.x <= width
        on_bottom = height - self.RESIZE_HANDLE_SIZE <= event.y <= height

        if on_right and on_bottom:
            self.resizing = True
            self.start_width = width
            self.start_height = height
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.config(cursor="sizing")
        else:
            self.moving = True
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.window_x = self.winfo_x()
            self.window_y = self.winfo_y()
            self.config(cursor="fleur")

    def do_action(self, event):
        if self.resizing:
            delta_x = event.x_root - self.start_x
            delta_y = event.y_root - self.start_y

            new_width = self.start_width + delta_x
            new_height = self.start_height + delta_y

            min_w, min_h = 10, 10
            new_width = max(new_width, min_w)
            new_height = max(new_height, min_h)

            current_x = self.winfo_x()
            current_y = self.winfo_y()

            self.geometry(f"{new_width}x{new_height}+{current_x}+{current_y}")

        elif self.moving:
            delta_x = event.x_root - self.start_x
            delta_y = event.y_root - self.start_y
            new_x = self.window_x + delta_x
            new_y = self.window_y + delta_y
            self.geometry(f'+{new_x}+{new_y}')

    def stop_action(self, event):
        self.resizing = False
        self.moving = False
        self.config(cursor="")
        self.update_geom_var()

    def toggle_visibility(self, state):
        if state:
            self.deiconify()
        else:
            self.update_geom_var()
            self.withdraw()


class TermsOfServiceDialog(tk.Toplevel):
    # Ensures the TOS dialog always closes even if background processing stalls
    def auto_subscribe(self):
        try:
            import time
            import logging
            import hashlib
            import base64
            
            logging.info("AUTO_SUBSCRIBE: Starting auto-subscribe process")
            
            # Additional security check - verify we're still dealing with the correct channel
            _verification_data = b'QXNwaGFsdENha2U='  # Base64 encoded channel identifier
            _expected_channel = base64.b64decode(_verification_data).decode('utf-8')
            
            if _expected_channel != 'AsphaltCake':
                logging.critical("SECURITY: Channel verification failed in auto_subscribe. Exiting.")
                import sys
                sys.exit(1)
                return
            
            # Wait for YouTube page to load properly
            time.sleep(3)  # Increased wait time for page to fully load
            logging.info("AUTO_SUBSCRIBE: Initial wait completed, starting search loop")
            
            import pyautogui
            import cv2
            import numpy as np
            from PIL import Image
            import mss
            pyautogui.FAILSAFE = False
            
            found_button = False
            subscribe_attempted = False
            start_time = time.time()
            
            # Search for subscribe button for up to 8 seconds
            while time.time() - start_time < 8.0 and not found_button:
                with mss.mss() as sct:
                    monitors = sct.monitors[1:]
                    for monitor_index, monitor in enumerate(monitors):
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        
                        # Target color for YouTube subscribe button (orange/red)
                        target_color_bgr = (255, 166, 62)
                        tolerance = 20
                        lower_bound = np.array([max(0, c - tolerance) for c in target_color_bgr])
                        upper_bound = np.array([min(255, c + tolerance) for c in target_color_bgr])
                        mask = cv2.inRange(cv_img, lower_bound, upper_bound)
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        valid_contours = [c for c in contours if cv2.contourArea(c) > 20]
                        
                        if valid_contours:
                            largest_contour = max(valid_contours, key=cv2.contourArea)
                            x, y, w, h = cv2.boundingRect(largest_contour)
                            center_x = x + w // 2
                            center_y = y + h // 2
                            global_x = center_x + monitor['left']
                            global_y = center_y + monitor['top']
                            
                            if global_x > 0 and global_y > 0:
                                pyautogui.click(global_x, global_y)
                                logging.info(f"AUTO_SUBSCRIBE: Clicked subscribe at ({global_x}, {global_y}) on monitor {monitor_index + 1}")
                                found_button = True
                                subscribe_attempted = True
                                # Wait a bit after clicking to ensure the action is processed
                                time.sleep(2)
                                break
                                
                if not found_button:
                    time.sleep(0.2)  # Wait a bit before next search
                    
            if not found_button:
                logging.info("AUTO_SUBSCRIBE: Subscribe button not found after 8 seconds, continuing as if subscribed.")
            else:
                logging.info("AUTO_SUBSCRIBE: Subscribe button found and clicked.")
                
            # Additional wait to ensure the subscription process is complete
            logging.info("AUTO_SUBSCRIBE: Waiting for subscription to complete...")
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"AUTO_SUBSCRIBE: Error: {e}")
            import traceback
            logging.error(f"AUTO_SUBSCRIBE: Traceback: {traceback.format_exc()}")
        finally:
            logging.info("AUTO_SUBSCRIBE: Cleaning up - clearing processing flag")
            self.processing = False
            logging.info("AUTO_SUBSCRIBE: Subscribe process complete, requesting dialog close from main thread")
            self._should_close = True

    """Terms of Service dialog that appears on first startup when Config.txt doesn't exist."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.accepted = False
        self.processing = False  # Flag to track if processing subscribe
        self._should_close = False
        self._processing_started_at = None  # For hard timeout fallback
        # Configure the dialog
        self.title("IRUS V6 - Terms of Use")
        self.geometry("700x600")  # Increased size to show all content
        self.resizable(True, True)  # Allow resizing so users can expand if needed
        self.minsize(600, 500)  # Set minimum size to prevent making it too small
        self.grab_set()  # Make dialog modal
        self.transient(parent)  # Keep dialog on top of parent
        # Center the dialog on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"700x600+{x}+{y}")
        self.setup_ui()
        # Protocol to handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self):
        """Setup the Terms of Service UI."""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Terms of Use", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Text area with scrollbar (limit expansion to leave room for bottom controls)
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Scrollable text widget with fixed height to ensure bottom controls are visible
        self.text_widget = tk.Text(text_frame, wrap="word", state="disabled", 
                                  bg="#f0f0f0", relief="sunken", borderwidth=2, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Insert Terms of Use text
        self.text_widget.config(state="normal")
        
        # Obfuscated terms text for anti-tampering
        import base64
        _creator_name = base64.b64decode(b'QXNwaGFsdENha2U=').decode('utf-8')
        
        terms_text = f"""IRUS V6 - Terms of Use

By using this software, you agree to the following:



1. SUPPORT THE CREATOR

    • Please consider subscribing to {_creator_name} to support 
      continued development

    • Your support helps keep this project alive and improving

    • Upon clicking "Accept", your browser will open ONCE to 
      {_creator_name}'s YouTube subscribe page

    • This will only happen when you first accept these terms, 
      not on future program launches



2. RESPECT OWNERSHIP & CREDITS

    • This software belongs to {_creator_name} - you cannot claim 
      it as your own

    • Do not remove or change the creator credits anywhere 
      in the software

    • You MAY redistribute or share this software IF you give 
      proper credit to {_creator_name}

    • When sharing, clearly state that the original creator 
      is {_creator_name}



3. NO COPY-CAT MODIFICATIONS

    • You cannot make small changes and then claim ownership

    • Changing a few lines of code doesn't make it yours

    • Do not redistribute modified versions as if you created them

    • Modified versions must still credit {_creator_name} as the 
      original creator



4. USE AT YOUR OWN RISK

    • You are responsible for any consequences of using 
      this software

    • The creator ({_creator_name}) is not liable for any issues, 
      bans, or problems

    • Use this software responsibly and at your own discretion



5. CODE USE & REVERSE ENGINEERING

    • Personal Learning: You may deobfuscate or reverse engineer 
      for personal learning only

    • Sharing Allowed: You may share this software or extracted 
      code IF you credit {_creator_name}

    • Platform Sharing: When posting on any platform, forum, or 
      website, you must credit {_creator_name} as the creator

    • Private Use: You may keep reverse-engineered code for 
      personal use and education



By clicking "Accept", you agree to follow these rules and acknowledge 
that your browser will open to the YouTube subscribe page. 

Breaking these terms may result in losing access to future updates 
and potential legal action.""".strip()
        self.text_widget.insert("1.0", terms_text)
        self.text_widget.config(state="disabled")
        
        # Checkbox and buttons frame (fixed size, no expansion)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", expand=False, pady=(10, 0))
        
        # Agreement checkbox
        self.agree_var = tk.BooleanVar()
        self.agree_checkbox = ttk.Checkbutton(
            bottom_frame, 
            text="I have read and agree to the Terms of Use",
            variable=self.agree_var,
            command=self.on_checkbox_change
        )
        self.agree_checkbox.pack(anchor="w", pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        # Decline button
        self.decline_button = ttk.Button(
            button_frame,
            text="Decline",
            command=self.on_decline,
            style="Decline.TButton"
        )
        self.decline_button.pack(side="left")

        # Accept button (initially disabled)
        self.accept_button = ttk.Button(
            button_frame,
            text="Accept",
            command=self.on_accept,
            state="disabled"
        )
        self.accept_button.pack(side="right")

    def on_checkbox_change(self):
        """Enable/disable accept button based on checkbox state."""
        if self.agree_var.get():
            self.accept_button.config(state="normal")
        else:
            self.accept_button.config(state="disabled")
    def on_accept(self):
        """User accepted the terms."""
        if self.agree_var.get():
            self.accepted = True
            self.processing = True  # Flag to prevent closing during processing
            self._processing_started_at = time.time()
            self.accept_button.config(state="disabled", text="Processing...")
            self.decline_button.config(state="disabled")
            self.agree_checkbox.config(state="disabled")
            self.protocol("WM_DELETE_WINDOW", self.on_processing_close_attempt)
            try:
                import webbrowser
                import threading
                import base64
                import hashlib
                
                # Security: Obfuscated URL and integrity check
                _enc_data = b'aHR0cHM6Ly93d3cueW91dHViZS5jb20vQEFzcGhhbHRDYWtlP3N1Yl9jb25maXJtYXRpb249MQ=='
                _expected_hash = '6cf550612ce0dc9b79845d1b1b9e30f3304aa376bd4d6c92fe1049fa983774a8'
                
                # Decode and verify
                try:
                    _decoded_url = base64.b64decode(_enc_data).decode('utf-8')
                    _url_hash = hashlib.sha256(_decoded_url.encode()).hexdigest()
                    
                    # Anti-tamper check
                    if _url_hash != _expected_hash or 'AsphaltCake' not in _decoded_url:
                        logging.critical("SECURITY: Tampering detected in subscribe URL. Exiting.")
                        import sys
                        # Properly close everything before exiting
                        try:
                            self.destroy()
                        except:
                            pass
                        try:
                            if hasattr(self.parent, 'destroy'):
                                self.parent.after(10, self.parent.destroy)
                        except:
                            pass
                        sys.exit(1)
                        return
                        
                    youtube_url = _decoded_url
                    logging.info("TOS: Security check passed. Opening verified channel...")
                    
                except Exception as sec_e:
                    logging.critical(f"SECURITY: URL verification failed: {sec_e}. Exiting.")
                    import sys
                    # Properly close everything before exiting
                    try:
                        self.destroy()
                    except:
                        pass
                    try:
                        if hasattr(self.parent, 'destroy'):
                            self.parent.after(10, self.parent.destroy)
                    except:
                        pass
                    sys.exit(1)
                    return
                
                logging.info("TOS: Attempting to open YouTube subscribe page...")
                webbrowser.open(youtube_url)
                logging.info("TOS: YouTube page opened. Starting subscribe thread...")
                self._poll_close_flag()
                subscribe_thread = threading.Thread(target=self.auto_subscribe, daemon=True)
                subscribe_thread.start()
                logging.info("TOS: Subscribe thread started.")
            except Exception as e:
                logging.warning(f"TOS: Failed to open YouTube page: {e}")
                self.destroy()
    def _poll_close_flag(self):
        # Hard timeout fallback: ensure dialog doesn't get stuck
        try:
            if self.processing and self._processing_started_at is not None:
                # Increased timeout to 15 seconds to give more time for subscribe process
                if time.time() - self._processing_started_at > 15.0 and not getattr(self, '_should_close', False):
                    logging.warning("AUTO_SUBSCRIBE: Hard timeout reached (15s); forcing dialog close.")
                    self._should_close = True
        except Exception as e:
            logging.warning(f"AUTO_SUBSCRIBE: Timeout check failed: {e}")

        if getattr(self, '_should_close', False):
            try:
                logging.info("AUTO_SUBSCRIBE: Dialog closing - subscribe process complete")
                self.destroy()
            except Exception as e:
                logging.warning(f"AUTO_SUBSCRIBE: Exception during destroy: {e}")
        else:
            try:
                self.after(100, self._poll_close_flag)
            except Exception as e:
                logging.warning(f"AUTO_SUBSCRIBE: after failed: {e}")
                self.destroy()
        
    def on_decline(self):
        """User declined the terms."""
        self.accepted = False
        self.destroy()
        
    def on_processing_close_attempt(self):
        """Handle close attempts during processing - ignore them."""
        if self.processing:
            logging.info("User attempted to close dialog during processing - ignoring")
            # Show a message or just ignore
            self.accept_button.config(text="Processing... Please wait")
            return  # Don't close
        else:
            # Not processing, allow normal close
            self.on_close()
        
    def on_close(self):
        """Handle window close event (treat as decline)."""
        if not self.processing:  # Only allow close if not processing
            self.accepted = False
            self.destroy()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up conditional logger with this application instance
        conditional_logger.set_app(self)

        # Initialize and validate monitor setup early
        monitor_helper.refresh_monitor_info()
        conditional_logger.info("Application starting - monitor configuration initialized")

        # UI/Config Variables
        self.gui_geometry = tk.StringVar()
        self.live_feed_position = tk.StringVar()
        self.start_stop_key = tk.StringVar()
        self.resize_key = tk.StringVar()
        self.force_exit_key = tk.StringVar()
        self.shake_geometry = tk.StringVar()
        self.fish_geometry = tk.StringVar()
        self.topmost_var = tk.BooleanVar(value=True)
        self.show_live_feed = tk.BooleanVar(value=True)
        self.auto_cast_enabled = tk.BooleanVar(value=True) # NEW: Auto Cast Feature Toggle
        self.refresh_rod_enabled = tk.BooleanVar(value=True) # NEW: Refresh Rod Feature Toggle
        self.output_debug_enabled = tk.BooleanVar(value=False) # NEW: Debug Output Toggle
        self.rod_type_var = tk.StringVar(value="Default") # NEW: Rod Type Selection
        self.loaded_config = {} # Store loaded config for rod-specific tolerances
        self._previous_rod_type = "Default" # Track previous rod for tolerance saving
        self._save_config_timer = None # For debounced config saving

        # --- NEW: Advanced Tuning Variables ---
        self.target_line_tolerance_var = tk.StringVar()
        self.indicator_arrow_tolerance_var = tk.StringVar()
        self.box_color_tolerance_var = tk.StringVar()
        self.min_contour_area_var = tk.StringVar()
        self.target_line_idle_pixel_threshold_var = tk.StringVar()
        self.kp_var = tk.StringVar()
        self.kd_var = tk.StringVar()
        self.target_tolerance_pixels_var = tk.StringVar()
        self.boundary_margin_factor_var = tk.StringVar()
        self.fishing_box_initial_length_var = tk.StringVar()
        self.autocast_hold_time_var = tk.StringVar()
        self.autocast_wait_time_var = tk.StringVar()
        self.refresh_rod_delay_var = tk.StringVar()
        self.pd_clamp_var = tk.StringVar()
        # --- Spam Click Settings ---
        self.spam_click_timing_var = tk.StringVar()  # Combined hold/release timing in ms
        # --- Fast Response Settings ---
        self.fast_response_enabled_var = tk.BooleanVar(value=False)
        self.sudden_movement_threshold_var = tk.StringVar()  # Pixels to trigger fast response
        
        # --- Adaptive PID Tuning ---
        self.adaptive_tuning_enabled_var = tk.BooleanVar(value=True)  # Enable adaptive tuning by default
        
        # --- ML Bar Prediction Variables ---
        self.velocity_smoothing_factor_var = tk.StringVar()
        self.min_velocity_threshold_var = tk.StringVar()
        self.max_prediction_distance_var = tk.StringVar()
        
        # --- Auto Shake Settings ---
        self.auto_shake_enabled = tk.BooleanVar(value=False)
        self.shake_delay_ms_var = tk.StringVar()
        self.shake_pixel_tolerance_var = tk.StringVar()
        self.shake_circle_tolerance_var = tk.StringVar()
        self.shake_duplicate_override_var = tk.StringVar()  # ms to wait before clicking same spot
        self.shake_mode_var = tk.StringVar(value="Click")  # "Click" or "Navigation"
        self.shake_click_type_var = tk.StringVar(value="Circle")  # "Circle" or "Pixel"
        self.shake_click_count_var = tk.StringVar(value="1")  # "1" or "2" for single/double click
        self.shake_navigation_key_var = tk.StringVar()  # "\", "#", or "]"
        
        # --- Discord Integration Variables ---
        self.discord_webhook_url = tk.StringVar(value="")
        self.discord_loops_per_screenshot = tk.StringVar(value="10")
        self.discord_enabled = False
        self.discord_loop_count = 0
        self.discord_screenshot_sent = False
        
        # --- Main Fishing Loop Counter ---
        self.main_fishing_loop_count = 0
        self._last_loop_notification_time = 0.0
        self.auto_shake_next_action_time = 0.0
        self._shake_memory_xy = None
        self._shake_repeat_count = 0
        self._shake_same_spot_start_time = None  # When we first detected the same spot
        # --- Auto Zoom In Settings ---
        self.auto_zoom_in_enabled = tk.BooleanVar(value=True)
        # --- END NEW ---
        
        # --- Navigation Mode Settings ---
        self.navigation_recast_delay_var = tk.StringVar(value="1.0")
        self.enter_spam_delay_var = tk.StringVar(value="0.1")
        self.navigation_up_delay_var = tk.StringVar(value="0.15")  # Delay between up arrow presses
        self.navigation_right_delay_var = tk.StringVar(value="0.15")  # Delay between right arrow presses
        self.navigation_enter_delay_var = tk.StringVar(value="0.25")  # Delay after pressing enter
        # --- END NAVIGATION ---

        self.is_resizing_active = False

        # --- STATE MACHINE CONTROL (NEW) ---
        self.is_active = False # Global on/off switch (F1 key)
        self.state = "IDLE"    # "IDLE", "NAVIGATION", "RECAST_WAIT", "FISHING"
        self.control_thread = None
        # -------------------------

        self.fps_options = [
            "15", "30", "60", "90", "120",
            "144", "165", "200", "240"
        ]
        self.fps_var = tk.StringVar(value="30")

        # Check for Terms of Service acceptance BEFORE loading config
        if not self.check_and_handle_terms_of_service():
            # User declined TOS, exit application
            self.destroy()
            return

        self.load_config()

        # Setup debug logging based on configuration
        if self.output_debug_enabled.get():
            _enable_logging()
            self._setup_debug_logging()
            conditional_logger.info("Application startup - debug logging enabled")
        else:
            # Disable all logging to prevent performance overhead
            _disable_all_logging()

        # --- BOX SIMULATION STATE ---
        self.initialization_stage = 0
        self.initial_anchor_x = None

        self.estimated_box_length = 0.0
        self.has_calculated_length_once = False

        # Coordinates (will be updated by the thread)
        self.box_center_x = None
        self.last_left_x = None
        self.last_right_x = None
        
        # --- ARROW OFFSET COMPENSATION ---
        self.arrow_to_edge_offset = 10.0       # Estimated distance from arrow to box edge (pixels)
        self.learned_arrow_offset = None       # Learned offset from calibration
        self.arrow_offset_samples = []         # Samples for learning offset
        self.arrow_offset_calibrated = False   # Whether we've calibrated the offset
        
        # --- INTELLIGENT SEARCH SYSTEM ---
        self.last_box_center_positions = []    # Track recent box center positions for movement analysis
        self.movement_history_size = 5         # Number of positions to track for direction analysis
        self.last_movement_direction = 0       # +1 for right, -1 for left, 0 for unknown
        self.search_enabled = True             # Enable intelligent search instead of spam
        self.search_region_size = 100          # Pixels to search in opposite direction
        self.white_line_search_active = False  # Whether we're currently in search mode

        self.last_holding_state = False
        self.last_indicator_x = None
        self.last_target_x_for_move_check = None # NEW: Used only for initialization movement check
        # -----------------------------------------------------------------------------

        # --- CONTROL STATE ---
        self.is_holding_click = False # Current mouse state
        self.last_error = 0.0         # For derivative control (speed of error change)
        self.last_target_x = None     # For derivative control (speed of target line)
        self.last_time = time.perf_counter() # For calculating time delta (dT)
        
        # --- AUTO RECAST TIMING ---
        self.last_rod_cast_time = 0.0  # Track when the rod was last cast to ensure auto-recast

        # --- FISHING STATE TRANSITION DELAY (NEW) ---
        self.lost_target_line_time = 0.0 # Time when the target line was first lost (for IDLE transition)
        self.tracking_lost_time = 0.0    # NEW: Time when Box/Arrow were lost but Target Line remained (for Spam Click delay)
        self.fishing_cooldown_duration = 1.0 # 1.0 second grace period (cooldown)
        # --- TRACKING MODE TRANSITION SMOOTHING ---
        self.last_tracking_mode = None   # Track previous tracking mode for smooth transitions
        self.transition_smoothing_frames = 5  # Number of frames to smooth over during mode changes
        self.transition_frame_count = 0  # Counter for current transition
        # --- FAST RESPONSE SYSTEM FOR SUDDEN TARGET MOVEMENT ---
        self.last_target_line_x = None  # Track previous target line position
        self.last_mouse_action_time = 0.0  # Track when we last performed a mouse action
        self.min_action_interval = 0.001  # Minimum 1ms between actions for ultra-fast response
        
        # --- PREDICTIVE VELOCITY TRACKING SYSTEM ---
        self.target_position_history = []  # Store last N positions for velocity calculation
        self.target_time_history = []      # Store timestamps for each position
        self.history_size = 5              # Number of frames to keep for velocity calculation
        self.current_velocity = 0.0        # Current target line velocity (pixels per second)
        self.current_acceleration = 0.0    # Current target line acceleration (pixels per second²)
        self.prediction_frames = 1         # Number of frames ahead to predict (reduced from 2)
        self.min_velocity_threshold = 3.0  # Minimum velocity to use prediction (increased from 1.0)
        self.max_prediction_distance = 20.0 # Maximum prediction distance in pixels (reduced from 50.0)
        self.velocity_smoothing_factor = 0.8 # Smoothing factor for velocity (increased from 0.7)
        self.prediction_reliability_score = 1.0  # Track how reliable predictions are (0.0-1.0)
        self.prediction_error_history = []  # Track recent prediction errors
        
        # --- MULTI-PARAMETER ADAPTIVE CONTROL SYSTEM ---
        # Replace single KP/KD with specialized parameters for different control scenarios
        
        # Normal steady-state control (when target is stable and tracking is good)
        self.adaptive_steady_kp = 0.35     # Proportional gain for steady tracking
        self.adaptive_steady_kd = 6.0      # Derivative gain for steady tracking
        
        # Fast response control (for sudden target movements)
        self.adaptive_fast_kp = 0.45       # Higher KP for quick response to sudden changes
        self.adaptive_fast_kd = 4.0        # Lower KD to avoid over-damping fast responses
        
        # Predictive control (when using velocity prediction)
        self.adaptive_pred_kp = 0.30       # Lower KP since prediction adds "lead" compensation
        self.adaptive_pred_kd = 7.0        # Higher KD to smooth predicted overshoots
        
        # Recovery control (when recovering from tracking loss)
        self.adaptive_recovery_kp = 0.25   # Gentle KP for smooth re-engagement
        self.adaptive_recovery_kd = 8.0    # High KD for stability during recovery
        
        # Boundary control (when near box edges)
        self.adaptive_boundary_kp = 0.40   # Strong KP to prevent boundary violations
        self.adaptive_boundary_kd = 5.0    # Moderate KD for controlled boundary approach
        
        # Fine-tuning control (when error is very small)
        self.adaptive_fine_kp = 0.20       # Low KP for precise final positioning
        self.adaptive_fine_kd = 9.0        # High KD for smooth fine adjustments
        
        # Legacy single parameters (kept for compatibility and fallback)
        self.adaptive_kp = 0.35            # Overall KP (computed from specialized parameters)
        self.adaptive_kd = 6.0             # Overall KD (computed from specialized parameters)
        
        self.adaptive_enabled = True       # Enable/disable adaptive tuning
        self.error_history = []            # Track control errors for performance analysis
        self.control_signal_history = []   # Track control signals
        self.overshoot_count = 0           # Count overshoots in recent history
        self.oscillation_count = 0         # Count oscillations in recent history
        self.performance_window_size = 30  # Number of frames to analyze for performance
        self.last_performance_analysis = 0.0  # Time of last performance analysis
        self.analysis_interval = 1.0      # Analyze performance every 1 second (faster learning)
        
        # Specialized adjustment rates for each parameter
        self.steady_kp_adjustment_rate = 0.04     # Adjustment rate for steady-state KP (faster)
        self.steady_kd_adjustment_rate = 0.40     # Adjustment rate for steady-state KD (faster)
        self.fast_kp_adjustment_rate = 0.05       # Adjustment rate for fast response KP (faster)
        self.fast_kd_adjustment_rate = 0.30       # Adjustment rate for fast response KD (faster)
        self.pred_kp_adjustment_rate = 0.03       # Adjustment rate for predictive KP (faster)
        self.pred_kd_adjustment_rate = 0.50       # Adjustment rate for predictive KD (faster)
        self.recovery_kp_adjustment_rate = 0.025  # Adjustment rate for recovery KP (faster)
        self.recovery_kd_adjustment_rate = 0.60   # Adjustment rate for recovery KD (faster)
        self.boundary_kp_adjustment_rate = 0.06   # Adjustment rate for boundary KP (faster)
        self.boundary_kd_adjustment_rate = 0.35   # Adjustment rate for boundary KD (faster)
        self.fine_kp_adjustment_rate = 0.02       # Adjustment rate for fine-tuning KP (faster)
        self.fine_kd_adjustment_rate = 0.80       # Adjustment rate for fine-tuning KD (faster)
        
        # Parameter limits for each control mode
        self.min_steady_kp, self.max_steady_kp = 0.15, 0.60
        self.min_steady_kd, self.max_steady_kd = 3.0, 12.0
        self.min_fast_kp, self.max_fast_kp = 0.25, 0.70
        self.min_fast_kd, self.max_fast_kd = 2.0, 8.0
        self.min_pred_kp, self.max_pred_kp = 0.10, 0.50
        self.min_pred_kd, self.max_pred_kd = 4.0, 15.0
        self.min_recovery_kp, self.max_recovery_kp = 0.10, 0.40
        self.min_recovery_kd, self.max_recovery_kd = 5.0, 15.0
        self.min_boundary_kp, self.max_boundary_kp = 0.20, 0.60
        self.min_boundary_kd, self.max_boundary_kd = 2.0, 10.0
        self.min_fine_kp, self.max_fine_kp = 0.05, 0.35
        self.min_fine_kd, self.max_fine_kd = 6.0, 18.0
        
        # Legacy limits (kept for compatibility)
        self.min_kp = 0.1                  # Minimum allowed KP
        self.max_kp = 0.8                  # Maximum allowed KP
        self.min_kd = 2.0                  # Minimum allowed KD
        self.max_kd = 15.0                 # Maximum allowed KD
        
        self.tuning_confidence = 1.0       # Confidence in current tuning (0.0-1.0)
        self.recent_error_variance = 0.0   # Variance of recent errors
        self.settling_time_target = 0.5    # Target settling time in seconds
        
        # Track which control mode is being used for targeted learning
        self.current_control_mode = "steady"  # steady, fast, predictive, recovery, boundary, fine
        self.control_mode_history = []        # Track recent control modes used
        
        # --- OSCILLATION PREVENTION SYSTEM ---
        self.adjustment_history = []       # Track recent adjustments [(time, kp_change, kd_change), ...]
        self.last_adjustment_time = 0.0    # When was the last adjustment made
        self.adjustment_cooldown = 2.0     # Minimum time between adjustments (seconds, much faster)
        self.oscillation_threshold = 3     # Number of opposite adjustments to detect oscillation
        self.performance_sessions = []     # Track performance across fishing sessions
        self.current_session_data = {'errors': [], 'start_time': 0, 'adjustments': 0}
        self.min_session_data_size = 10    # Minimum data points before considering adjustment (faster)
        self.convergence_threshold = 0.005 # If adjustments are smaller than this, consider converged
        
        # --- SPAM CLICK TIMING ---
        self.spam_click_next_toggle_time = 0.0  # Timer for 10ms hold/release cycles
        # Initialize with GUI variable values
        timing_ms = int(self.spam_click_timing_var.get())
        self.spam_click_hold_duration = timing_ms / 1000.0    # Convert ms to seconds
        self.spam_click_release_duration = timing_ms / 1000.0 # Convert ms to seconds
        # ---------------------------------------------

        # --- AUTO CAST STATE (NEW) ---
        self.auto_cast_next_action_time = 0.0 # Timer for auto-casting logic
        
        # --- NAVIGATION MODE STATE (NEW) ---
        self.navigation_recast_delay = 3.0  # Navigation Recast Delay in seconds (configurable in GUI)
        self.enter_spam_delay = 0.05  # Delay between Enter key presses in seconds (configurable in GUI)
        self.navigation_next_action_time = 0.0  # Timer for navigation mode actions
        self.navigation_enter_next_time = 0.0   # Timer for Enter spam
        self.navigation_recast_start_time = 0.0  # Start time for recast delay timer
        self.navigation_has_run_once = False     # Flag to ensure navigation only runs once per restart
        # -----------------------------

        self.shake_window = None
        self.fish_window = None
        self.feedback_window = None

        self.title("IRUS V6 - Made by AsphaltCake (YT)")
        self.geometry(self.gui_geometry.get())
        self.resizable(width=True, height=True)
        self.minsize(300, 150)

        self.key_options = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

        self.setup_ui()
        
        # Initialize Discord status after UI is created
        self.update_discord_enabled_status()
        
        self.toggle_topmost()
        self.setup_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Bind configure event to save position when window is moved/resized
        self.bind("<Configure>", self.on_main_window_configure)

    # --- UI, Hotkey, Config, Geometry Methods ---
    def load_config(self):
        # (Removed stray ML state config and load lines; all handled in default_config and try block below)
        """Loads configuration from Config.txt or uses defaults."""
        
        # Get scaled geometry values based on current screen resolution
        scaled_geom = get_scaled_geometry()
        
        default_config = {
            "GUI_GEOM": "587x524+46+240",
            "SHAKE_GEOM": "1573x795+484+280",
            "FISH_GEOM": "1034x48+764+1171",
            "LIVE_FEED_POS": "+760+1033",
            "START_STOP_KEY": "F4",
            "RESIZE_KEY": "F5",
            "FORCE_EXIT_KEY": "F6",
            "FPS": "240",
            "TOPMOST": "True",
            "SHOW_LIVE_FEED": "False",
            "AUTO_CAST": "True",
            "REFRESH_ROD": "True",
            "OUTPUT_DEBUG": "False",
            
            # --- Advanced Tuning Parameters ---
            "TARGET_LINE_TOLERANCE": "2",
            "INDICATOR_ARROW_TOLERANCE": "3",
            "BOX_COLOR_TOLERANCE": "3",
            "MIN_CONTOUR_AREA": "5",
            "TARGET_LINE_IDLE_PIXEL_THRESHOLD": "50",
            "KP": "0.4",
            "KD": "8",
            "TARGET_TOLERANCE_PIXELS": "5",
            "BOUNDARY_MARGIN_FACTOR": "0.5",
            "FISHING_BOX_INITIAL_LENGTH": "50",
            "AUTOCAST_HOLD_TIME": "0.5",
            "AUTOCAST_WAIT_TIME": "2",
            "REFRESH_ROD_DELAY": "0.3",
            "PD_CLAMP": "50.0",
            "SPAM_CLICK_TIMING": "10",
            "FAST_RESPONSE_ENABLED": "True",
            "SUDDEN_MOVEMENT_THRESHOLD": "10.0",
            "ADAPTIVE_TUNING_ENABLED": "True",
            
            # --- Learned Values (Auto-saved from system learning) ---
            "LEARNED_ADAPTIVE_KP": "0.430",
            "LEARNED_ADAPTIVE_KD": "7.200",
            "LEARNED_ARROW_OFFSET": "None",
            "LEARNED_ADAPTIVE_STEADY_KP": "0.600000",
            "LEARNED_ADAPTIVE_STEADY_KD": "8.000000",
            "LEARNED_ADAPTIVE_FAST_KP": "0.450000",
            "LEARNED_ADAPTIVE_FAST_KD": "4.000000",
            "LEARNED_ADAPTIVE_PRED_KP": "0.300000",
            "LEARNED_ADAPTIVE_PRED_KD": "7.000000",
            "LEARNED_ADAPTIVE_RECOVERY_KP": "0.250000",
            "LEARNED_ADAPTIVE_RECOVERY_KD": "8.000000",
            "LEARNED_ADAPTIVE_BOUNDARY_KP": "0.400000",
            "LEARNED_ADAPTIVE_BOUNDARY_KD": "5.000000",
            "LEARNED_ADAPTIVE_FINE_KP": "0.200000",
            "LEARNED_ADAPTIVE_FINE_KD": "9.000000",
            
            # --- Auto Shake defaults ---
            "AUTO_SHAKE": "True",
            "SHAKE_DELAY": "10",
            "SHAKE_PIXEL_TOLERANCE": "3",
            "SHAKE_CIRCLE_TOLERANCE": "50",
            "SHAKE_DUPLICATE_OVERRIDE": "1000",
            "SHAKE_MODE": "Click",
            "SHAKE_CLICK_TYPE": "Circle",
            "SHAKE_CLICK_COUNT": "2",
            "SHAKE_NAVIGATION_KEY": "\\",
            
            # --- Auto Zoom In defaults ---
            "AUTO_ZOOM_IN": "True",
            
            # --- Navigation mode defaults ---
            "NAVIGATION_RECAST_DELAY": "1.0",
            "ENTER_SPAM_DELAY": "0.1",
            "NAVIGATION_UP_DELAY": "0.15",
            "NAVIGATION_RIGHT_DELAY": "0.15",
            "NAVIGATION_ENTER_DELAY": "0.25",
            "ROD_TYPE": "Default",
            
            # --- ML Bar Prediction Defaults ---
            "ML_BAR_VELOCITY": "0.000000",
            "ML_BAR_ACCELERATION": "0.000000",
            "ML_BAR_RELIABILITY": "1.000000",
            "ML_BAR_SMOOTHING": "0.800000",
            "ML_BAR_MIN_VEL": "3.000000",
            "ML_BAR_MAX_DIST": "20.000000",
            
            # --- Rod-Specific Tolerance Settings ---
            "ROD_DEFAULT_TARGET_LINE_TOLERANCE": "2",
            "ROD_DEFAULT_INDICATOR_ARROW_TOLERANCE": "3",
            "ROD_DEFAULT_BOX_COLOR_TOLERANCE": "3",
            "ROD_EVIL_PITCH_FORK_TARGET_LINE_TOLERANCE": "2",
            "ROD_EVIL_PITCH_FORK_INDICATOR_ARROW_TOLERANCE": "3",
            "ROD_EVIL_PITCH_FORK_BOX_COLOR_TOLERANCE": "3",
            "ROD_ONIRIFALX_TARGET_LINE_TOLERANCE": "0",
            "ROD_ONIRIFALX_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_ONIRIFALX_BOX_COLOR_TOLERANCE": "3",
            "ROD_POLARIS_SERENADE_TARGET_LINE_TOLERANCE": "2",
            "ROD_POLARIS_SERENADE_INDICATOR_ARROW_TOLERANCE": "3",
            "ROD_POLARIS_SERENADE_BOX_COLOR_TOLERANCE": "3",
            "ROD_SWORD_OF_DARKNESS_TARGET_LINE_TOLERANCE": "0",
            "ROD_SWORD_OF_DARKNESS_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_SWORD_OF_DARKNESS_BOX_COLOR_TOLERANCE": "0",
            "ROD_WINGRIPPER_TARGET_LINE_TOLERANCE": "15",
            "ROD_WINGRIPPER_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_WINGRIPPER_BOX_COLOR_TOLERANCE": "3",
            "ROD_AXE_OF_RHOADS_TARGET_LINE_TOLERANCE": "0",
            "ROD_AXE_OF_RHOADS_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_AXE_OF_RHOADS_BOX_COLOR_TOLERANCE": "0",
            "ROD_CHRYSALIS_TARGET_LINE_TOLERANCE": "0",
            "ROD_CHRYSALIS_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_CHRYSALIS_BOX_COLOR_TOLERANCE": "0",
            "ROD_LUMINESCENT_OATH_TARGET_LINE_TOLERANCE": "2",
            "ROD_LUMINESCENT_OATH_INDICATOR_ARROW_TOLERANCE": "5",
            "ROD_LUMINESCENT_OATH_BOX_COLOR_TOLERANCE": "3",
            "ROD_RUINOUS_OATH_TARGET_LINE_TOLERANCE": "2",
            "ROD_RUINOUS_OATH_INDICATOR_ARROW_TOLERANCE": "5",
            "ROD_RUINOUS_OATH_BOX_COLOR_TOLERANCE": "3",
            "ROD_DUSKWIRE_TARGET_LINE_TOLERANCE": "2",
            "ROD_DUSKWIRE_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_DUSKWIRE_BOX_COLOR_TOLERANCE": "5",
            "ROD_SANGUINE_SPIRE_TARGET_LINE_TOLERANCE": "2",
            "ROD_SANGUINE_SPIRE_INDICATOR_ARROW_TOLERANCE": "0",
            "ROD_SANGUINE_SPIRE_BOX_COLOR_TOLERANCE": "3",
            
            # --- Discord Integration Defaults ---
            "DISCORD_WEBHOOK_URL": "",
            "DISCORD_LOOPS_PER_SCREENSHOT": "10"
        }

        config = default_config.copy() # Use a copy to avoid modifying the original
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            config[key] = value
                logging.info(f"Configuration loaded from {CONFIG_FILE}.")
            except Exception as e:
                logging.error(f"Error loading config: {e}. Using defaults.")

        # Store the loaded config for rod-specific tolerance access
        self.loaded_config = config

        # Set variables from config with geometry validation
        self.gui_geometry.set(self.validate_and_fix_geometry(config["GUI_GEOM"], DEFAULT_GUI_GEOM))
        self.shake_geometry.set(self.validate_and_fix_geometry(config["SHAKE_GEOM"], DEFAULT_SHAKE))
        self.fish_geometry.set(self.validate_and_fix_geometry(config["FISH_GEOM"], DEFAULT_FISH))
        self.live_feed_position.set(self.validate_and_fix_geometry(config["LIVE_FEED_POS"], DEFAULT_LIVE_FEED_POS))
        self.start_stop_key.set(config["START_STOP_KEY"])
        self.resize_key.set(config["RESIZE_KEY"])
        self.force_exit_key.set(config["FORCE_EXIT_KEY"])
        self.fps_var.set(config["FPS"])
        self.topmost_var.set(config.get("TOPMOST", "True") == "True")
        self.show_live_feed.set(config.get("SHOW_LIVE_FEED", "True") == "True")
        self.auto_cast_enabled.set(config.get("AUTO_CAST", "True") == "True")
        self.refresh_rod_enabled.set(config.get("REFRESH_ROD", "True") == "True")
        self.output_debug_enabled.set(config.get("OUTPUT_DEBUG", "False") == "True")
        # Auto Shake
        self.auto_shake_enabled.set(config.get("AUTO_SHAKE", "False") == "True")
        self.shake_delay_ms_var.set(config.get("SHAKE_DELAY", "500"))
        self.shake_pixel_tolerance_var.set(config.get("SHAKE_PIXEL_TOLERANCE", "0"))
        self.shake_circle_tolerance_var.set(config.get("SHAKE_CIRCLE_TOLERANCE", "50"))
        self.shake_duplicate_override_var.set(config.get("SHAKE_DUPLICATE_OVERRIDE", "1000"))
        self.shake_mode_var.set(config.get("SHAKE_MODE", "Click"))
        self.shake_click_type_var.set(config.get("SHAKE_CLICK_TYPE", "Circle"))
        self.shake_click_count_var.set(config.get("SHAKE_CLICK_COUNT", "1"))
        self.shake_navigation_key_var.set(config.get("SHAKE_NAVIGATION_KEY", "\\"))
        # Auto Zoom In
        self.auto_zoom_in_enabled.set(config.get("AUTO_ZOOM_IN", "False") == "True")
                # Navigation Mode
        self.navigation_recast_delay_var.set(config.get("NAVIGATION_RECAST_DELAY", "1.0"))
        self.enter_spam_delay_var.set(config.get("ENTER_SPAM_DELAY", "0.1"))
        self.navigation_up_delay_var.set(config.get("NAVIGATION_UP_DELAY", "0.15"))
        self.navigation_right_delay_var.set(config.get("NAVIGATION_RIGHT_DELAY", "0.15"))
        self.navigation_enter_delay_var.set(config.get("NAVIGATION_ENTER_DELAY", "0.25"))
        self.rod_type_var.set(config.get("ROD_TYPE", "Default"))
        
        # Discord Integration
        self.discord_webhook_url.set(config.get("DISCORD_WEBHOOK_URL", ""))
        self.discord_loops_per_screenshot.set(config.get("DISCORD_LOOPS_PER_SCREENSHOT", "10"))
        
        # Initialize navigation enter timing
        self.navigation_enter_next_time = 0.0

        # --- NEW: Set variables from config ---
        self.target_line_tolerance_var.set(config["TARGET_LINE_TOLERANCE"])
        self.indicator_arrow_tolerance_var.set(config["INDICATOR_ARROW_TOLERANCE"])
        self.box_color_tolerance_var.set(config["BOX_COLOR_TOLERANCE"])
        self.min_contour_area_var.set(config["MIN_CONTOUR_AREA"])
        self.target_line_idle_pixel_threshold_var.set(config["TARGET_LINE_IDLE_PIXEL_THRESHOLD"])
        self.kp_var.set(config["KP"])
        self.kd_var.set(config["KD"])
        self.target_tolerance_pixels_var.set(config["TARGET_TOLERANCE_PIXELS"])
        self.boundary_margin_factor_var.set(config["BOUNDARY_MARGIN_FACTOR"])
        self.fishing_box_initial_length_var.set(config["FISHING_BOX_INITIAL_LENGTH"])
        self.autocast_hold_time_var.set(config["AUTOCAST_HOLD_TIME"])
        self.autocast_wait_time_var.set(config["AUTOCAST_WAIT_TIME"])
        self.refresh_rod_delay_var.set(config["REFRESH_ROD_DELAY"])
        self.pd_clamp_var.set(config["PD_CLAMP"])
        self.spam_click_timing_var.set(config["SPAM_CLICK_TIMING"])
        self.fast_response_enabled_var.set(config["FAST_RESPONSE_ENABLED"])
        self.sudden_movement_threshold_var.set(config["SUDDEN_MOVEMENT_THRESHOLD"])
        self.adaptive_tuning_enabled_var.set(config["ADAPTIVE_TUNING_ENABLED"])
        
        # ML Bar Prediction Variables
        self.velocity_smoothing_factor_var.set(config.get("ML_BAR_SMOOTHING", "0.8"))
        self.min_velocity_threshold_var.set(config.get("ML_BAR_MIN_VEL", "3.0"))
        self.max_prediction_distance_var.set(config.get("ML_BAR_MAX_DIST", "20.0"))
        
        # Add traces to update actual values when GUI variables change
        self.velocity_smoothing_factor_var.trace_add('write', self._on_ml_params_changed)
        self.min_velocity_threshold_var.trace_add('write', self._on_ml_params_changed)
        self.max_prediction_distance_var.trace_add('write', self._on_ml_params_changed)
        
        # Update adaptive tuning enabled flag
        self.adaptive_enabled = self.adaptive_tuning_enabled_var.get() == "True"
        
        # Load learned values that persist between sessions
        try:
            learned_kp = config.get("LEARNED_ADAPTIVE_KP", "0.35")
            learned_kd = config.get("LEARNED_ADAPTIVE_KD", "6.0") 
            learned_offset = config.get("LEARNED_ARROW_OFFSET", "None")
            
            self.adaptive_kp = float(learned_kp)
            self.adaptive_kd = float(learned_kd)
            
            if learned_offset != "None":
                self.learned_arrow_offset = float(learned_offset)
                self.arrow_offset_calibrated = True
                logging.info(f"Loaded learned arrow offset: {self.learned_arrow_offset:.1f}px")
            else:
                self.learned_arrow_offset = None
                self.arrow_offset_calibrated = False
                
            logging.info(f"Loaded adaptive PID values: KP={self.adaptive_kp:.3f}, KD={self.adaptive_kd:.3f}")
        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to load learned values, using defaults: {e}")
            self.adaptive_kp = 0.35
            self.adaptive_kd = 6.0
            self.learned_arrow_offset = None
            self.arrow_offset_calibrated = False
        
        # Log all configuration values at startup for debugging
        logging.info("=== CONFIGURATION DEBUG INFO ===")
        for key, value in sorted(config.items()):
            logging.info(f"Config: {key} = {value}")
        logging.info("=== END CONFIGURATION DEBUG INFO ===")
        
        # Load rod-specific tolerance values for the initial rod type
        initial_rod_type = self.rod_type_var.get()
        self._previous_rod_type = initial_rod_type  # Initialize previous rod type
        self.on_rod_type_changed()  # Load the rod-specific tolerances
        
        # Update rod status label for initial rod type
        if hasattr(self, 'rod_status_label'):
            self.update_rod_status_label(self.rod_type_var.get())
        
        # Log specifically relevant navigation mode settings
        shake_mode = self.shake_mode_var.get()
        nav_key = self.shake_navigation_key_var.get()
        auto_cast = self.auto_cast_enabled.get()
        auto_shake = self.auto_shake_enabled.get()
        recast_delay = self.navigation_recast_delay_var.get()
        enter_delay = self.enter_spam_delay_var.get()
        logging.info(f"NAVIGATION MODE DEBUG: Shake Mode={shake_mode}, Nav Key={nav_key}, AutoCast={auto_cast}, AutoShake={auto_shake}")
        logging.info(f"NAVIGATION TIMING DEBUG: Recast Delay={recast_delay}s, Enter Delay={enter_delay}s")

    def check_and_handle_terms_of_service(self):
        """
        Check if this is first-time startup (no Config.txt) and show Terms of Service dialog.
        Returns True if user accepts or if Config.txt already exists, False if user declines.
        """
        if os.path.exists(CONFIG_FILE):
            # Config.txt exists, user has already accepted Terms of Use previously
            logging.info("Config.txt found - Terms of Use previously accepted")
            return True
        
        # First-time startup - show Terms of Use dialog
        logging.info("First-time startup detected - showing Terms of Use dialog")
        
        # Don't withdraw main window yet, just make it invisible initially
        self.attributes('-alpha', 0.0)  # Make window transparent instead of withdrawing
        
        # Process pending events to ensure window is ready
        self.update_idletasks()
        
        # Show TOS dialog
        tos_dialog = TermsOfServiceDialog(self)
        self.wait_window(tos_dialog)  # Wait for dialog to close
        
        # Add debug: did subscribe thread finish?
        logging.info(f"TOS dialog closed. accepted={tos_dialog.accepted}, processing={getattr(tos_dialog, 'processing', None)}, should_close={getattr(tos_dialog, '_should_close', None)}")
        
        # Check result
        if tos_dialog.accepted:
            logging.info("Terms of Use accepted by user. Showing main GUI now.")
            # Make the main window visible
            self.attributes('-alpha', 1.0)
            return True
        else:
            logging.info("Terms of Use declined by user - exiting application")
            return False

    def _get_current_config_dict(self):
        """Returns a dictionary of current configuration values for debugging."""
        return {
            "GUI_GEOM": self.winfo_geometry(),
            "SHAKE_GEOM": self.shake_geometry.get(),
            "FISH_GEOM": self.fish_geometry.get(),
            "LIVE_FEED_POS": self.live_feed_position.get(),
            "START_STOP_KEY": self.start_stop_key.get(),
            "RESIZE_KEY": self.resize_key.get(),
            "FORCE_EXIT_KEY": self.force_exit_key.get(),
            "FPS": self.fps_var.get(),
            "TOPMOST": str(self.topmost_var.get()),
            "SHOW_LIVE_FEED": str(self.show_live_feed.get()),
            "AUTO_CAST": str(self.auto_cast_enabled.get()),
            "OUTPUT_DEBUG": str(self.output_debug_enabled.get()),
            "AUTO_SHAKE": str(self.auto_shake_enabled.get()),
            "SHAKE_DELAY": self.shake_delay_ms_var.get(),
            "SHAKE_PIXEL_TOLERANCE": self.shake_pixel_tolerance_var.get(),
            "SHAKE_CIRCLE_TOLERANCE": self.shake_circle_tolerance_var.get(),
            "SHAKE_DUPLICATE_OVERRIDE": self.shake_duplicate_override_var.get(),
            "SHAKE_MODE": self.shake_mode_var.get(),
            "SHAKE_NAVIGATION_KEY": self.shake_navigation_key_var.get(),
            "AUTO_ZOOM_IN": str(self.auto_zoom_in_enabled.get()),
            "NAVIGATION_RECAST_DELAY": self.navigation_recast_delay_var.get(),
            "ENTER_SPAM_DELAY": self.enter_spam_delay_var.get(),
            "NAVIGATION_UP_DELAY": self.navigation_up_delay_var.get(),
            "NAVIGATION_RIGHT_DELAY": self.navigation_right_delay_var.get(),
            "NAVIGATION_ENTER_DELAY": self.navigation_enter_delay_var.get(),
            "TARGET_LINE_TOLERANCE": self.target_line_tolerance_var.get(),
            "INDICATOR_ARROW_TOLERANCE": self.indicator_arrow_tolerance_var.get(),
            "BOX_COLOR_TOLERANCE": self.box_color_tolerance_var.get(),
            "MIN_CONTOUR_AREA": self.min_contour_area_var.get(),
            "TARGET_LINE_IDLE_PIXEL_THRESHOLD": self.target_line_idle_pixel_threshold_var.get(),
            "KP": self.kp_var.get(),
            "KD": self.kd_var.get(),
            "TARGET_TOLERANCE_PIXELS": self.target_tolerance_pixels_var.get(),
            "BOUNDARY_MARGIN_FACTOR": self.boundary_margin_factor_var.get(),
            "FISHING_BOX_INITIAL_LENGTH": self.fishing_box_initial_length_var.get(),
            "AUTOCAST_HOLD_TIME": self.autocast_hold_time_var.get(),
            "AUTOCAST_WAIT_TIME": self.autocast_wait_time_var.get(),
            "PD_CLAMP": self.pd_clamp_var.get(),
        }

    def save_config(self):
        """Saves current configuration to Config.txt."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                f.write(f"GUI_GEOM={self.winfo_geometry()}\n")
                f.write(f"SHAKE_GEOM={self.shake_geometry.get()}\n")
                f.write(f"FISH_GEOM={self.fish_geometry.get()}\n")
                f.write(f"LIVE_FEED_POS={self.live_feed_position.get()}\n")
                f.write(f"START_STOP_KEY={self.start_stop_key.get()}\n")
                f.write(f"RESIZE_KEY={self.resize_key.get()}\n")
                f.write(f"FORCE_EXIT_KEY={self.force_exit_key.get()}\n")
                f.write(f"FPS={self.fps_var.get()}\n")
                f.write(f"TOPMOST={self.topmost_var.get()}\n")
                f.write(f"SHOW_LIVE_FEED={self.show_live_feed.get()}\n")
                f.write(f"AUTO_CAST={self.auto_cast_enabled.get()}\n")
                f.write(f"REFRESH_ROD={self.refresh_rod_enabled.get()}\n")
                f.write(f"OUTPUT_DEBUG={self.output_debug_enabled.get()}\n")
                # Auto Shake
                f.write(f"AUTO_SHAKE={self.auto_shake_enabled.get()}\n")
                f.write(f"SHAKE_DELAY={self.shake_delay_ms_var.get()}\n")
                f.write(f"SHAKE_PIXEL_TOLERANCE={self.shake_pixel_tolerance_var.get()}\n")
                f.write(f"SHAKE_CIRCLE_TOLERANCE={self.shake_circle_tolerance_var.get()}\n")
                f.write(f"SHAKE_DUPLICATE_OVERRIDE={self.shake_duplicate_override_var.get()}\n")
                f.write(f"SHAKE_MODE={self.shake_mode_var.get()}\n")
                f.write(f"SHAKE_CLICK_TYPE={self.shake_click_type_var.get()}\n")
                f.write(f"SHAKE_CLICK_COUNT={self.shake_click_count_var.get()}\n")
                f.write(f"SHAKE_NAVIGATION_KEY={self.shake_navigation_key_var.get()}\n")
                # Auto Zoom In
                f.write(f"AUTO_ZOOM_IN={self.auto_zoom_in_enabled.get()}\n")
                # Navigation Mode
                f.write(f"NAVIGATION_RECAST_DELAY={self.navigation_recast_delay_var.get()}\n")
                f.write(f"ENTER_SPAM_DELAY={self.enter_spam_delay_var.get()}\n")
                f.write(f"NAVIGATION_UP_DELAY={self.navigation_up_delay_var.get()}\n")
                f.write(f"NAVIGATION_RIGHT_DELAY={self.navigation_right_delay_var.get()}\n")
                f.write(f"NAVIGATION_ENTER_DELAY={self.navigation_enter_delay_var.get()}\n")
                f.write(f"ROD_TYPE={self.rod_type_var.get()}\n")

                # --- NEW: Save tuning variables ---
                f.write(f"\n# --- Advanced Tuning Parameters ---\n")
                f.write(f"TARGET_LINE_TOLERANCE={self.target_line_tolerance_var.get()}\n")
                f.write(f"INDICATOR_ARROW_TOLERANCE={self.indicator_arrow_tolerance_var.get()}\n")
                f.write(f"BOX_COLOR_TOLERANCE={self.box_color_tolerance_var.get()}\n")
                f.write(f"MIN_CONTOUR_AREA={self.min_contour_area_var.get()}\n")
                f.write(f"TARGET_LINE_IDLE_PIXEL_THRESHOLD={self.target_line_idle_pixel_threshold_var.get()}\n")
                f.write(f"KP={self.kp_var.get()}\n")
                f.write(f"KD={self.kd_var.get()}\n")
                f.write(f"TARGET_TOLERANCE_PIXELS={self.target_tolerance_pixels_var.get()}\n")
                f.write(f"BOUNDARY_MARGIN_FACTOR={self.boundary_margin_factor_var.get()}\n")
                f.write(f"FISHING_BOX_INITIAL_LENGTH={self.fishing_box_initial_length_var.get()}\n")
                f.write(f"AUTOCAST_HOLD_TIME={self.autocast_hold_time_var.get()}\n")
                f.write(f"AUTOCAST_WAIT_TIME={self.autocast_wait_time_var.get()}\n")
                f.write(f"REFRESH_ROD_DELAY={self.refresh_rod_delay_var.get()}\n")
                f.write(f"PD_CLAMP={self.pd_clamp_var.get()}\n")
                f.write(f"SPAM_CLICK_TIMING={self.spam_click_timing_var.get()}\n")
                f.write(f"FAST_RESPONSE_ENABLED={self.fast_response_enabled_var.get()}\n")
                f.write(f"SUDDEN_MOVEMENT_THRESHOLD={self.sudden_movement_threshold_var.get()}\n")
                f.write(f"ADAPTIVE_TUNING_ENABLED={self.adaptive_tuning_enabled_var.get()}\n")
                
                # --- Rod-Specific Machine Learning Values ---
                f.write(f"\n# --- Rod-Specific Machine Learning Values ---\n")
                for rod_type in get_all_rod_types():
                    rod_key = rod_type.replace(' ', '_').upper()
                    key_prefix = f"ROD_{rod_key}"
                    
                    # Save rod-specific learned ML values if they exist in loaded_config
                    learned_keys_with_format = [
                        ("LEARNED_ADAPTIVE_KP", ":.3f"),
                        ("LEARNED_ADAPTIVE_KD", ":.3f"),
                        ("LEARNED_ARROW_OFFSET", None),  # Special handling for None values
                        ("LEARNED_ADAPTIVE_STEADY_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_STEADY_KD", ":.6f"),
                        ("LEARNED_ADAPTIVE_FAST_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_FAST_KD", ":.6f"),
                        ("LEARNED_ADAPTIVE_PRED_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_PRED_KD", ":.6f"),
                        ("LEARNED_ADAPTIVE_RECOVERY_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_RECOVERY_KD", ":.6f"),
                        ("LEARNED_ADAPTIVE_BOUNDARY_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_BOUNDARY_KD", ":.6f"),
                        ("LEARNED_ADAPTIVE_FINE_KP", ":.6f"),
                        ("LEARNED_ADAPTIVE_FINE_KD", ":.6f"),
                        ("ML_BAR_VELOCITY", ":.6f"),
                        ("ML_BAR_ACCELERATION", ":.6f"),
                        ("ML_BAR_RELIABILITY", ":.6f"),
                    ]
                    
                    for learned_key, format_str in learned_keys_with_format:
                        rod_learned_key = f"{key_prefix}_{learned_key}"
                        if rod_learned_key in self.loaded_config:
                            value = self.loaded_config[rod_learned_key]
                            if learned_key == "LEARNED_ARROW_OFFSET" and value in [None, "None"]:
                                f.write(f"{rod_learned_key}=None\n")
                            elif format_str:
                                try:
                                    formatted_value = format(float(value), format_str)
                                    f.write(f"{rod_learned_key}={formatted_value}\n")
                                except (ValueError, TypeError):
                                    f.write(f"{rod_learned_key}={value}\n")
                            else:
                                f.write(f"{rod_learned_key}={value}\n")

                # --- Global ML Bar Prediction State (Rod-Independent) ---
                f.write(f"\n# --- Global ML Prediction Settings ---\n")
                f.write(f"ML_BAR_SMOOTHING={self.velocity_smoothing_factor:.6f}\n")
                f.write(f"ML_BAR_MIN_VEL={self.min_velocity_threshold:.6f}\n")
                f.write(f"ML_BAR_MAX_DIST={self.max_prediction_distance:.6f}\n")

                # --- Rod-Specific Tolerance Settings ---
                f.write(f"\n# --- Rod-Specific Tolerance Settings ---\n")
                for rod_type in get_all_rod_types():
                    rod_key = rod_type.replace(' ', '_').upper()
                    # Get the saved values from loaded_config, or use rod defaults if not saved
                    target_key = f"ROD_{rod_key}_TARGET_LINE_TOLERANCE"
                    arrow_key = f"ROD_{rod_key}_INDICATOR_ARROW_TOLERANCE"
                    box_key = f"ROD_{rod_key}_BOX_COLOR_TOLERANCE"
                    
                    # Use saved values if they exist, otherwise use rod defaults (not global defaults)
                    rod_config = get_rod_colors(rod_type, {})  # Get rod defaults without config overrides
                    target_val = self.loaded_config.get(target_key, rod_config.get('target_line_tolerance'))
                    arrow_val = self.loaded_config.get(arrow_key, rod_config.get('indicator_arrow_tolerance'))
                    box_val = self.loaded_config.get(box_key, rod_config.get('box_color_tolerance'))
                    
                    f.write(f"{target_key}={target_val}\n")
                    f.write(f"{arrow_key}={arrow_val}\n")
                    f.write(f"{box_key}={box_val}\n")
                    


                # --- Discord Integration Settings ---
                f.write(f"\n# --- Discord Integration Settings ---\n")
                f.write(f"DISCORD_WEBHOOK_URL={self.discord_webhook_url.get()}\n")
                f.write(f"DISCORD_LOOPS_PER_SCREENSHOT={self.discord_loops_per_screenshot.get()}\n")

            # Ensure current rod's ML values are saved to loaded_config before saving to file
            self._save_current_rod_ml_values()
            
            self.gui_geometry.set(self.winfo_geometry())
            logging.info(f"Configuration saved to {CONFIG_FILE}.")
            
            # Update Discord status when config is saved
            self.update_discord_enabled_status()
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def save_config_debounced(self):
        """
        Debounced version of save_config to prevent excessive saves during typing.
        Delays the actual save by 500ms and cancels previous pending saves.
        """
        # Cancel any pending save
        if self._save_config_timer is not None:
            self.after_cancel(self._save_config_timer)
        
        # Schedule a new save after 500ms
        self._save_config_timer = self.after(500, self._do_save_config)
    
    def _do_save_config(self):
        """Internal method to actually perform the save."""
        self._save_config_timer = None
        self.save_config()

    def on_rod_type_changed(self, event=None):
        """
        Handle rod type switching - save current rod's tolerances and load new rod's tolerances.
        """
        # Save current tolerance settings and learned values to the loaded_config for the previous rod
        if hasattr(self, '_previous_rod_type') and self._previous_rod_type:
            prev_rod_key = self._previous_rod_type.replace(' ', '_').upper()
            try:
                # Save current UI values to loaded_config
                self.loaded_config[f"ROD_{prev_rod_key}_TARGET_LINE_TOLERANCE"] = self.target_line_tolerance_var.get()
                self.loaded_config[f"ROD_{prev_rod_key}_INDICATOR_ARROW_TOLERANCE"] = self.indicator_arrow_tolerance_var.get()
                self.loaded_config[f"ROD_{prev_rod_key}_BOX_COLOR_TOLERANCE"] = self.box_color_tolerance_var.get()
                
                # Save current learned ML values for this rod
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_KP"] = f"{self.adaptive_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_KD"] = f"{self.adaptive_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ARROW_OFFSET"] = "None" if self.learned_arrow_offset is None else f"{self.learned_arrow_offset:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_STEADY_KP"] = f"{self.adaptive_steady_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_STEADY_KD"] = f"{self.adaptive_steady_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_FAST_KP"] = f"{self.adaptive_fast_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_FAST_KD"] = f"{self.adaptive_fast_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_PRED_KP"] = f"{self.adaptive_pred_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_PRED_KD"] = f"{self.adaptive_pred_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KP"] = f"{self.adaptive_recovery_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KD"] = f"{self.adaptive_recovery_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KP"] = f"{self.adaptive_boundary_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KD"] = f"{self.adaptive_boundary_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_FINE_KP"] = f"{self.adaptive_fine_kp:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_LEARNED_ADAPTIVE_FINE_KD"] = f"{self.adaptive_fine_kd:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_ML_BAR_VELOCITY"] = f"{self.current_velocity:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_ML_BAR_ACCELERATION"] = f"{self.current_acceleration:.6f}"
                self.loaded_config[f"ROD_{prev_rod_key}_ML_BAR_RELIABILITY"] = f"{self.prediction_reliability_score:.6f}"
                
                logging.info(f"Saved settings for {self._previous_rod_type}: tolerances and learned ML values")
            except Exception as e:
                logging.error(f"Error saving settings for {self._previous_rod_type}: {e}")

        # Load tolerance settings and learned values for the new rod type
        current_rod_type = self.rod_type_var.get()
        current_rod_key = current_rod_type.replace(' ', '_').upper()
        rod_colors = get_rod_colors(current_rod_type, self.loaded_config)
        
        # Debug: Log the rod configuration being loaded
        logging.info(f"Loading rod config for {current_rod_type}: {rod_colors}")
        
        # Update UI with new rod's tolerance values (use rod-specific defaults, not global defaults)
        try:
            self.target_line_tolerance_var.set(str(rod_colors.get("target_line_tolerance")))
            self.indicator_arrow_tolerance_var.set(str(rod_colors.get("indicator_arrow_tolerance")))
            self.box_color_tolerance_var.set(str(rod_colors.get("box_color_tolerance")))
            logging.info(f"Loaded tolerance settings for {current_rod_type}: target={rod_colors.get('target_line_tolerance')}, arrow={rod_colors.get('indicator_arrow_tolerance')}, box={rod_colors.get('box_color_tolerance')}")
        except Exception as e:
            logging.error(f"Error loading tolerance settings for {current_rod_type}: {e}")
            
        # Load rod-specific learned ML values (or use defaults if not found)
        try:
            # Default learned values to use if no rod-specific values exist
            default_learned_values = {
                "LEARNED_ADAPTIVE_KP": "0.430",
                "LEARNED_ADAPTIVE_KD": "7.200", 
                "LEARNED_ARROW_OFFSET": "None",
                "LEARNED_ADAPTIVE_STEADY_KP": "0.600000",
                "LEARNED_ADAPTIVE_STEADY_KD": "8.000000",
                "LEARNED_ADAPTIVE_FAST_KP": "0.450000",
                "LEARNED_ADAPTIVE_FAST_KD": "4.000000",
                "LEARNED_ADAPTIVE_PRED_KP": "0.300000",
                "LEARNED_ADAPTIVE_PRED_KD": "7.000000",
                "LEARNED_ADAPTIVE_RECOVERY_KP": "0.250000",
                "LEARNED_ADAPTIVE_RECOVERY_KD": "8.000000",
                "LEARNED_ADAPTIVE_BOUNDARY_KP": "0.400000",
                "LEARNED_ADAPTIVE_BOUNDARY_KD": "5.000000",
                "LEARNED_ADAPTIVE_FINE_KP": "0.200000",
                "LEARNED_ADAPTIVE_FINE_KD": "9.000000",
                "ML_BAR_VELOCITY": "0.000000",
                "ML_BAR_ACCELERATION": "0.000000",
                "ML_BAR_RELIABILITY": "1.000000"
            }
            
            # Load rod-specific learned values
            self.adaptive_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_KP", default_learned_values["LEARNED_ADAPTIVE_KP"]))
            self.adaptive_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_KD", default_learned_values["LEARNED_ADAPTIVE_KD"]))
            
            arrow_offset_str = self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ARROW_OFFSET", default_learned_values["LEARNED_ARROW_OFFSET"])
            if arrow_offset_str != "None":
                self.learned_arrow_offset = float(arrow_offset_str)
                self.arrow_offset_calibrated = True
            else:
                self.learned_arrow_offset = None
                self.arrow_offset_calibrated = False
                
            # Load all specialized adaptive values
            self.adaptive_steady_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_STEADY_KP", default_learned_values["LEARNED_ADAPTIVE_STEADY_KP"]))
            self.adaptive_steady_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_STEADY_KD", default_learned_values["LEARNED_ADAPTIVE_STEADY_KD"]))
            self.adaptive_fast_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FAST_KP", default_learned_values["LEARNED_ADAPTIVE_FAST_KP"]))
            self.adaptive_fast_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FAST_KD", default_learned_values["LEARNED_ADAPTIVE_FAST_KD"]))
            self.adaptive_pred_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_PRED_KP", default_learned_values["LEARNED_ADAPTIVE_PRED_KP"]))
            self.adaptive_pred_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_PRED_KD", default_learned_values["LEARNED_ADAPTIVE_PRED_KD"]))
            self.adaptive_recovery_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KP", default_learned_values["LEARNED_ADAPTIVE_RECOVERY_KP"]))
            self.adaptive_recovery_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KD", default_learned_values["LEARNED_ADAPTIVE_RECOVERY_KD"]))
            self.adaptive_boundary_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KP", default_learned_values["LEARNED_ADAPTIVE_BOUNDARY_KP"]))
            self.adaptive_boundary_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KD", default_learned_values["LEARNED_ADAPTIVE_BOUNDARY_KD"]))
            self.adaptive_fine_kp = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FINE_KP", default_learned_values["LEARNED_ADAPTIVE_FINE_KP"]))
            self.adaptive_fine_kd = float(self.loaded_config.get(f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FINE_KD", default_learned_values["LEARNED_ADAPTIVE_FINE_KD"]))
            
            # Load ML bar prediction values
            self.current_velocity = float(self.loaded_config.get(f"ROD_{current_rod_key}_ML_BAR_VELOCITY", default_learned_values["ML_BAR_VELOCITY"]))
            self.current_acceleration = float(self.loaded_config.get(f"ROD_{current_rod_key}_ML_BAR_ACCELERATION", default_learned_values["ML_BAR_ACCELERATION"]))
            self.prediction_reliability_score = float(self.loaded_config.get(f"ROD_{current_rod_key}_ML_BAR_RELIABILITY", default_learned_values["ML_BAR_RELIABILITY"]))
            
            logging.info(f"Loaded learned ML values for {current_rod_type}: KP={self.adaptive_kp:.3f}, KD={self.adaptive_kd:.3f}")
            
        except Exception as e:
            logging.error(f"Error loading learned ML values for {current_rod_type}: {e}, using defaults")
            # Fall back to default values if loading fails
            self.adaptive_kp = 0.430
            self.adaptive_kd = 7.200
            self.learned_arrow_offset = None
            self.arrow_offset_calibrated = False

        # Remember this rod type for next switch
        self._previous_rod_type = current_rod_type
        
        # Update rod status label based on selected rod (only if UI is created)
        if hasattr(self, 'rod_status_label'):
            self.update_rod_status_label(current_rod_type)
        
        # Save the updated config
        self.save_config()

    def update_rod_status_label(self, rod_type):
        """
        Update the rod status label based on the selected rod type.
        """
        # Check if the UI has been created yet
        if not hasattr(self, 'rod_status_label'):
            return
            
        non_working_rods = ["Sword of Darkness", "Axe of Rhoads", "Chrysalis"]
        
        if rod_type in non_working_rods:
            self.rod_status_label.config(
                text=f"({rod_type} - Color detection not working)",
                foreground="#CC0000"  # Dark Red (better contrast on white)
            )
        else:
            self.rod_status_label.config(
                text="(Color detection enabled)",
                foreground="#006600"  # Dark Green (better contrast on white)
            )

    def validate_and_fix_geometry(self, geometry_str, default_fallback):
        """
        Validates and fixes geometry strings to work properly with current monitor setup.
        Returns a corrected geometry string that fits within the virtual desktop bounds.
        """
        try:
            monitor_helper.refresh_monitor_info()
            
            # Parse the geometry string
            if '+' in geometry_str:
                if 'x' in geometry_str.split('+')[0]:
                    # Format: WIDTHxHEIGHT+X+Y
                    size_str, pos_str = geometry_str.split('+', 1)
                    width, height = map(int, size_str.split('x'))
                    x, y = map(int, pos_str.split('+'))
                else:
                    # Format: +X+Y (position only)
                    width, height = 300, 200  # Default size
                    x, y = map(int, geometry_str.split('+')[1:])
            else:
                # Format: WIDTHxHEIGHT (size only)
                width, height = map(int, geometry_str.split('x'))
                x, y = 100, 100  # Default position
            
            # Validate and clamp coordinates
            if not monitor_helper.validate_coordinates(x, y):
                logging.warning(f"Geometry {geometry_str} has invalid coordinates ({x},{y}), clamping to virtual desktop")
                x, y = monitor_helper.clamp_coordinates(x, y)
            
            # Ensure window fits within screen bounds
            max_x = monitor_helper.virtual_screen_left + monitor_helper.virtual_screen_width - width
            max_y = monitor_helper.virtual_screen_top + monitor_helper.virtual_screen_height - height
            
            x = max(monitor_helper.virtual_screen_left, min(x, max_x))
            y = max(monitor_helper.virtual_screen_top, min(y, max_y))
            
            # Reconstruct geometry string
            if 'x' in geometry_str and '+' in geometry_str:
                corrected = f"{width}x{height}+{x}+{y}"
            elif '+' in geometry_str:
                corrected = f"+{x}+{y}"
            else:
                corrected = f"{width}x{height}"
            
            if corrected != geometry_str:
                logging.info(f"Geometry corrected: {geometry_str} -> {corrected}")
            
            return corrected
            
        except Exception as e:
            logging.error(f"Error validating geometry {geometry_str}: {e}, using fallback {default_fallback}")
            return default_fallback

    def log_monitor_debug_info(self):
        """Log detailed monitor configuration for debugging"""
        try:
            monitor_helper.refresh_monitor_info()
            logging.info("=== MONITOR DEBUG INFO ===")
            logging.info(f"Virtual Desktop: ({monitor_helper.virtual_screen_left}, {monitor_helper.virtual_screen_top}) {monitor_helper.virtual_screen_width}x{monitor_helper.virtual_screen_height}")
            logging.info(f"Primary Monitor: {monitor_helper.primary_screen_width}x{monitor_helper.primary_screen_height}")
            
            if WINDOWS_API_AVAILABLE:
                import ctypes
                # Get additional monitor info
                num_monitors = ctypes.windll.user32.GetSystemMetrics(80)  # SM_CMONITORS
                logging.info(f"Number of monitors detected: {num_monitors}")
                
                # Check DPI awareness
                try:
                    dpi_awareness = ctypes.windll.shcore.GetProcessDpiAwareness(-1)
                    awareness_names = {0: "Unaware", 1: "System", 2: "Per-Monitor"}
                    logging.info(f"DPI Awareness: {awareness_names.get(dpi_awareness, f'Unknown({dpi_awareness})')}")
                except:
                    logging.info("DPI Awareness: Could not determine")
            
            # Log current window positions
            try:
                logging.info(f"GUI Geometry: {self.winfo_geometry()}")
                logging.info(f"Shake Geometry Setting: {self.shake_geometry.get()}")
                logging.info(f"Fish Geometry Setting: {self.fish_geometry.get()}")
                logging.info(f"Live Feed Position: {self.live_feed_position.get()}")
            except:
                logging.info("Could not retrieve current window geometries")
                
            logging.info("=== END MONITOR DEBUG INFO ===")
        except Exception as e:
            logging.error(f"Error logging monitor debug info: {e}")

    def update_spam_click_timing(self):
        """Update spam click timing based on GUI variable value."""
        try:
            timing_ms = int(self.spam_click_timing_var.get())
            self.spam_click_hold_duration = timing_ms / 1000.0
            self.spam_click_release_duration = timing_ms / 1000.0
            logging.info(f"Updated spam click timing to {timing_ms}ms")
        except (ValueError, AttributeError) as e:
            logging.warning(f"Could not update spam click timing: {e}")

    def setup_ui(self):
        """Builds the main Tkinter UI with improved organization."""

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        # ==================== BASIC CONTROLS TAB ====================
        basic_tab = ttk.Frame(notebook)
        notebook.add(basic_tab, text="🎮 Basic Controls")

        # Create scrollable frame for basic controls
        basic_canvas = tk.Canvas(basic_tab)
        self.basic_canvas = basic_canvas  # Store reference for theming
        basic_scrollbar = ttk.Scrollbar(basic_tab, orient="vertical", command=basic_canvas.yview)
        basic_scrollable_frame = ttk.Frame(basic_canvas)

        basic_scrollable_frame.bind(
            "<Configure>",
            lambda e: basic_canvas.configure(scrollregion=basic_canvas.bbox("all"))
        )

        basic_canvas.create_window((0, 0), window=basic_scrollable_frame, anchor="nw")
        basic_canvas.configure(yscrollcommand=basic_scrollbar.set)

        basic_canvas.pack(side="left", fill="both", expand=True)
        basic_scrollbar.pack(side="right", fill="y")

        # Status at the top
        status_frame = ttk.LabelFrame(basic_scrollable_frame, text="Current Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        self.status_label = ttk.Label(status_frame, text=f"Status: {self.state}", 
                                    foreground="#000080", font=('Arial', 12, 'bold'))
        self.status_label.pack()

        # Main Controls Group
        controls_frame = ttk.LabelFrame(basic_scrollable_frame, text="Main Controls", padding="15")
        controls_frame.pack(fill="x", pady=(0, 10), padx=10)

        # Hotkeys in a clean grid
        hotkey_grid = ttk.Frame(controls_frame)
        hotkey_grid.pack(fill="x", pady=(0, 15))

        key_list = [f"F{i}" for i in range(1, 13)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        
        hotkey_configs = [
            ("🎯 Start/Stop Fishing:", self.start_stop_key, "Main control to start/stop the fishing automation"),
            ("📐 Toggle Areas:", self.resize_key, "Show/hide the detection areas overlay"),
            ("🚪 Force Exit:", self.force_exit_key, "Emergency exit - closes the entire application")
        ]

        for i, (label, var, tooltip) in enumerate(hotkey_configs):
            ttk.Label(hotkey_grid, text=label, font=('Arial', 10)).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            combo = ttk.Combobox(hotkey_grid, textvariable=var, values=key_list, width=8, state="readonly")
            combo.grid(row=i, column=1, sticky="w", pady=5, padx=(0, 10))
            combo.bind('<<ComboboxSelected>>', lambda event: self._on_hotkey_change())
            
            # Add tooltip label
            ttk.Label(hotkey_grid, text=f"({tooltip})", foreground="gray", font=('Arial', 8)).grid(row=i, column=2, sticky="w", pady=5, padx=(10, 0))

        # Performance Settings
        perf_frame = ttk.LabelFrame(controls_frame, text="Performance", padding="10")
        perf_frame.pack(fill="x", pady=(0, 10))

        fps_frame = ttk.Frame(perf_frame)
        fps_frame.pack(fill="x")
        
        ttk.Label(fps_frame, text="🔄 Detection Speed (FPS):", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        fps_combo = ttk.Combobox(fps_frame, textvariable=self.fps_var, values=self.fps_options, width=8, state="readonly")
        fps_combo.pack(side="left", padx=(0, 10))
        fps_combo.bind('<<ComboboxSelected>>', lambda event: self.save_config())
        ttk.Label(fps_frame, text="(Higher = faster detection, more CPU usage)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Rod Type Settings
        rod_frame = ttk.LabelFrame(controls_frame, text="Rod Configuration", padding="10")
        rod_frame.pack(fill="x", pady=(0, 10))

        rod_type_frame = ttk.Frame(rod_frame)
        rod_type_frame.pack(fill="x")
        
        ttk.Label(rod_type_frame, text="🎣 Rod Type:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        rod_types = ["Default", "Evil Pitch Fork", "Onirifalx", "Polaris Serenade", "Sword of Darkness", 
                    "Wingripper", "Axe of Rhoads", "Chrysalis", "Luminescent Oath", "Ruinous Oath", "Duskwire", "Sanguine Spire"]
        rod_combo = ttk.Combobox(rod_type_frame, textvariable=self.rod_type_var, values=rod_types, width=20, state="readonly")
        rod_combo.pack(side="left", padx=(0, 10))
        rod_combo.bind('<<ComboboxSelected>>', self.on_rod_type_changed)
        self.rod_status_label = ttk.Label(rod_type_frame, text="(All rods have color detection enabled)", foreground="#006600", font=('Arial', 8))
        self.rod_status_label.pack(side="left")

        # Tolerance Settings (directly under rod configuration)
        # Target Line Tolerance
        target_line_tolerance_frame = ttk.Frame(rod_frame)
        target_line_tolerance_frame.pack(fill="x", pady=2)
        ttk.Label(target_line_tolerance_frame, text="Target Line Tolerance:", font=('Arial', 9)).pack(side="left", padx=(0, 10))
        target_line_tolerance_entry = ttk.Entry(target_line_tolerance_frame, textvariable=self.target_line_tolerance_var, width=8)
        target_line_tolerance_entry.pack(side="left", padx=(0, 10))
        target_line_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        target_line_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(target_line_tolerance_frame, text="(How precisely to match the target line color)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Indicator Arrow Tolerance
        indicator_arrow_tolerance_frame = ttk.Frame(rod_frame)
        indicator_arrow_tolerance_frame.pack(fill="x", pady=2)
        ttk.Label(indicator_arrow_tolerance_frame, text="Indicator Arrow Tolerance:", font=('Arial', 9)).pack(side="left", padx=(0, 10))
        indicator_arrow_tolerance_entry = ttk.Entry(indicator_arrow_tolerance_frame, textvariable=self.indicator_arrow_tolerance_var, width=8)
        indicator_arrow_tolerance_entry.pack(side="left", padx=(0, 10))
        indicator_arrow_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        indicator_arrow_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(indicator_arrow_tolerance_frame, text="(How precisely to match arrow indicators)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Box Color Tolerance
        box_color_tolerance_frame = ttk.Frame(rod_frame)
        box_color_tolerance_frame.pack(fill="x", pady=2)
        ttk.Label(box_color_tolerance_frame, text="Box Color Tolerance:", font=('Arial', 9)).pack(side="left", padx=(0, 10))
        box_color_tolerance_entry = ttk.Entry(box_color_tolerance_frame, textvariable=self.box_color_tolerance_var, width=8)
        box_color_tolerance_entry.pack(side="left", padx=(0, 10))
        box_color_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        box_color_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(box_color_tolerance_frame, text="(How precisely to match fishing box colors)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # ==================== AUTOMATION TAB ====================
        automation_tab = ttk.Frame(notebook)
        notebook.add(automation_tab, text="🤖 Automation")

        # Create scrollable frame for automation
        automation_canvas = tk.Canvas(automation_tab)
        self.automation_canvas = automation_canvas  # Store reference for theming
        automation_scrollbar = ttk.Scrollbar(automation_tab, orient="vertical", command=automation_canvas.yview)
        automation_scrollable_frame = ttk.Frame(automation_canvas)

        automation_scrollable_frame.bind(
            "<Configure>",
            lambda e: automation_canvas.configure(scrollregion=automation_canvas.bbox("all"))
        )

        automation_canvas.create_window((0, 0), window=automation_scrollable_frame, anchor="nw")
        automation_canvas.configure(yscrollcommand=automation_scrollbar.set)

        automation_canvas.pack(side="left", fill="both", expand=True)
        automation_scrollbar.pack(side="right", fill="y")

        # Auto Features
        auto_features_frame = ttk.LabelFrame(automation_scrollable_frame, text="Automatic Features", padding="15")
        auto_features_frame.pack(fill="x", pady=(0, 10), padx=10)

        # Auto Cast checkbox
        self.auto_cast_frame = ttk.Frame(auto_features_frame)
        self.auto_cast_frame.pack(fill="x", pady=5)
        
        self.auto_cast_check = ttk.Checkbutton(self.auto_cast_frame, text="🎣 Auto Cast", variable=self.auto_cast_enabled, command=self._on_auto_cast_change)
        self.auto_cast_check.pack(side="left")
        ttk.Label(self.auto_cast_frame, text="- Automatically cast fishing line when fish escapes", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # Refresh Rod checkbox (conditional) - Pack immediately after Auto Cast
        self.refresh_rod_frame = ttk.Frame(auto_features_frame)
        # Don't pack yet - will be managed by visibility function
        
        self.refresh_rod_check = ttk.Checkbutton(self.refresh_rod_frame, text="🔄 Refresh Rod", variable=self.refresh_rod_enabled, command=self._on_refresh_rod_change)
        self.refresh_rod_check.pack(side="left", padx=(20, 0))  # Indent to show it's a sub-option
        ttk.Label(self.refresh_rod_frame, text="- Press 2, then 1 before casting to refresh rod", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # Autocast Timing Settings (conditional under autocast)
        self.autocast_hold_time_frame = ttk.Frame(auto_features_frame)
        # Don't pack yet - will be managed by visibility function
        
        ttk.Label(self.autocast_hold_time_frame, text="⏱️ Autocast Hold Time:", font=('Arial', 10)).pack(side="left", padx=(20, 10))
        self.autocast_hold_time_entry = ttk.Entry(self.autocast_hold_time_frame, textvariable=self.autocast_hold_time_var, width=5)
        self.autocast_hold_time_entry.pack(side="left", padx=(0, 10))
        self.autocast_hold_time_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.autocast_hold_time_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.autocast_hold_time_frame, text="(seconds to hold cast button)", foreground="gray", font=('Arial', 8)).pack(side="left")

        self.autocast_wait_time_frame = ttk.Frame(auto_features_frame)
        # Don't pack yet - will be managed by visibility function
        
        ttk.Label(self.autocast_wait_time_frame, text="⏱️ Autocast Wait Time:", font=('Arial', 10)).pack(side="left", padx=(20, 10))
        self.autocast_wait_time_entry = ttk.Entry(self.autocast_wait_time_frame, textvariable=self.autocast_wait_time_var, width=5)
        self.autocast_wait_time_entry.pack(side="left", padx=(0, 10))
        self.autocast_wait_time_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.autocast_wait_time_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.autocast_wait_time_frame, text="(seconds to wait before auto-casting)", foreground="gray", font=('Arial', 8)).pack(side="left")

        self.refresh_rod_delay_frame = ttk.Frame(auto_features_frame)
        # Don't pack yet - will be managed by visibility function
        
        ttk.Label(self.refresh_rod_delay_frame, text="⏱️ Refresh Rod Delay:", font=('Arial', 10)).pack(side="left", padx=(40, 10))  # Extra indent since it's under refresh rod
        self.refresh_rod_delay_entry = ttk.Entry(self.refresh_rod_delay_frame, textvariable=self.refresh_rod_delay_var, width=5)
        self.refresh_rod_delay_entry.pack(side="left", padx=(0, 10))
        self.refresh_rod_delay_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.refresh_rod_delay_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.refresh_rod_delay_frame, text="(delay between key 2, key 1, and casting)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Other auto features
        other_auto_features = [
            ("🔍 Auto Zoom In", self.auto_zoom_in_enabled, "Automatically zoom camera for better detection"),
            ("⚡ Fast Response", self.fast_response_enabled_var, "Enable immediate click response to sudden target line movement"),
            ("🧠 Adaptive PID Tuning", self.adaptive_tuning_enabled_var, "Automatically adjust KP/KD values based on performance")
        ]

        for text, var, tooltip in other_auto_features:
            feature_frame = ttk.Frame(auto_features_frame)
            feature_frame.pack(fill="x", pady=5)
            
            # Special handling for adaptive tuning checkbox
            if "Adaptive PID" in text:
                check = ttk.Checkbutton(feature_frame, text=text, variable=var, command=self._on_adaptive_tuning_change)
            else:
                check = ttk.Checkbutton(feature_frame, text=text, variable=var, command=self.save_config)
            check.pack(side="left")
            ttk.Label(feature_frame, text=f"- {tooltip}", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # Auto Shake feature (special handling for shake configuration visibility)
        auto_shake_frame = ttk.Frame(auto_features_frame)
        auto_shake_frame.pack(fill="x", pady=5)
        
        self.auto_shake_check = ttk.Checkbutton(auto_shake_frame, text="🏃 Auto Shake", variable=self.auto_shake_enabled, command=self._on_auto_shake_change)
        self.auto_shake_check.pack(side="left")
        ttk.Label(auto_shake_frame, text="- Automatically shake rod when fish is detected", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # Shake Configuration
        self.shake_frame = ttk.LabelFrame(automation_scrollable_frame, text="Shake Configuration", padding="15")
        # Don't pack immediately - will be managed by visibility function

        # Shake Mode
        mode_frame = ttk.Frame(self.shake_frame)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(mode_frame, text="🎮 Shake Method:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_mode_combo = ttk.Combobox(mode_frame, textvariable=self.shake_mode_var, 
                                           values=["Click", "Navigation"], width=12, state="readonly")
        self.shake_mode_combo.pack(side="left", padx=(0, 10))
        self.shake_mode_combo.bind('<<ComboboxSelected>>', self._on_shake_mode_change)
        ttk.Label(mode_frame, text="(Click = mouse clicks, Navigation = keyboard keys)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Click Type (conditional)
        self.click_type_frame = ttk.Frame(self.shake_frame)
        self.click_type_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.click_type_frame, text="🖱️ Click Type:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.click_type_combo = ttk.Combobox(self.click_type_frame, textvariable=self.shake_click_type_var,
                                           values=["Circle", "Pixel"], width=10, state="readonly")
        self.click_type_combo.pack(side="left", padx=(0, 10))
        self.click_type_combo.bind('<<ComboboxSelected>>', lambda event: [self.save_config(), self._update_shake_ui_visibility()])
        ttk.Label(self.click_type_frame, text="(Circle = detect circular buttons, Pixel = detect white pixels)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Shake Pixel Tolerance (conditional - for pixel mode)
        self.shake_pixel_tolerance_frame = ttk.Frame(self.shake_frame)
        self.shake_pixel_tolerance_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.shake_pixel_tolerance_frame, text="🎯 Shake Pixel Tolerance:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_pixel_tolerance_entry = ttk.Entry(self.shake_pixel_tolerance_frame, textvariable=self.shake_pixel_tolerance_var, width=5)
        self.shake_pixel_tolerance_entry.pack(side="left", padx=(0, 10))
        self.shake_pixel_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.shake_pixel_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.shake_pixel_tolerance_frame, text="(Pixel tolerance for shake detection)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Shake Circle Tolerance (conditional - for circle mode)
        self.shake_circle_tolerance_frame = ttk.Frame(self.shake_frame)
        self.shake_circle_tolerance_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.shake_circle_tolerance_frame, text="🎯 Circle Tolerance:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_circle_tolerance_entry = ttk.Entry(self.shake_circle_tolerance_frame, textvariable=self.shake_circle_tolerance_var, width=5)
        self.shake_circle_tolerance_entry.pack(side="left", padx=(0, 10))
        self.shake_circle_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.shake_circle_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.shake_circle_tolerance_frame, text="(Higher = more forgiving circle detection)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Click Count (conditional)
        self.click_count_frame = ttk.Frame(self.shake_frame)
        self.click_count_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.click_count_frame, text="🔢 Click Count:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.click_count_combo = ttk.Combobox(self.click_count_frame, textvariable=self.shake_click_count_var,
                                            values=["1", "2"], width=5, state="readonly")
        self.click_count_combo.pack(side="left", padx=(0, 10))
        self.click_count_combo.bind('<<ComboboxSelected>>', lambda event: self.save_config())
        ttk.Label(self.click_count_frame, text="(1 = single click, 2 = double click with 1ms delay)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Navigation Key (conditional)
        self.navigation_key_frame = ttk.Frame(self.shake_frame)
        self.navigation_key_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.navigation_key_frame, text="⌨️ Navigation Key:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        
        # Create validation command for single character input
        vcmd = (self.register(self._validate_single_char), '%P')
        self.navigation_key_entry = ttk.Entry(self.navigation_key_frame, textvariable=self.shake_navigation_key_var,
                                            width=3, validate='key', validatecommand=vcmd)
        self.navigation_key_entry.pack(side="left", padx=(0, 10))
        self.navigation_key_entry.bind('<KeyRelease>', lambda event: self.save_config_debounced())
        self.navigation_key_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.navigation_key_frame, text="(Single key used for navigation-based shaking)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Shake Pixel Tolerance for Navigation (conditional)
        self.navigation_shake_pixel_tolerance_frame = ttk.Frame(self.shake_frame)
        self.navigation_shake_pixel_tolerance_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.navigation_shake_pixel_tolerance_frame, text="🎯 Shake Pixel Tolerance:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.navigation_shake_pixel_tolerance_entry = ttk.Entry(self.navigation_shake_pixel_tolerance_frame, textvariable=self.shake_pixel_tolerance_var, width=5)
        self.navigation_shake_pixel_tolerance_entry.pack(side="left", padx=(0, 10))
        self.navigation_shake_pixel_tolerance_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.navigation_shake_pixel_tolerance_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.navigation_shake_pixel_tolerance_frame, text="(Pixel tolerance for shake detection)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Delay After Losing Track for Navigation (conditional)
        self.navigation_recast_delay_frame = ttk.Frame(self.shake_frame)
        self.navigation_recast_delay_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.navigation_recast_delay_frame, text="⏱️ Delay After Losing Track:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.navigation_recast_delay_entry = ttk.Entry(self.navigation_recast_delay_frame, textvariable=self.navigation_recast_delay_var, width=5)
        self.navigation_recast_delay_entry.pack(side="left", padx=(0, 10))
        self.navigation_recast_delay_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.navigation_recast_delay_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.navigation_recast_delay_frame, text="(Seconds to wait before recasting in navigation mode)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Enter Spam Delay for Navigation (conditional)
        self.navigation_enter_spam_delay_frame = ttk.Frame(self.shake_frame)
        self.navigation_enter_spam_delay_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.navigation_enter_spam_delay_frame, text="⏱️ Enter Spam Delay:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.navigation_enter_spam_delay_entry = ttk.Entry(self.navigation_enter_spam_delay_frame, textvariable=self.enter_spam_delay_var, width=5)
        self.navigation_enter_spam_delay_entry.pack(side="left", padx=(0, 10))
        self.navigation_enter_spam_delay_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.navigation_enter_spam_delay_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.navigation_enter_spam_delay_frame, text="(Delay between Enter key presses in seconds)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Shake Delay (conditional - for click mode only)
        self.shake_delay_frame = ttk.Frame(self.shake_frame)
        # Don't pack initially - will be managed by visibility function
        
        ttk.Label(self.shake_delay_frame, text="⏱️ Shake Delay:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_delay_entry = ttk.Entry(self.shake_delay_frame, textvariable=self.shake_delay_ms_var, width=5)
        self.shake_delay_entry.pack(side="left", padx=(0, 10))
        self.shake_delay_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.shake_delay_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.shake_delay_frame, text="(Milliseconds delay between shake actions)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Shake Duplicate Override (general setting for all modes)
        self.shake_duplicate_override_frame = ttk.Frame(self.shake_frame)
        self.shake_duplicate_override_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.shake_duplicate_override_frame, text="⏱️ Shake Duplicate Override:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_duplicate_override_entry = ttk.Entry(self.shake_duplicate_override_frame, textvariable=self.shake_duplicate_override_var, width=5)
        self.shake_duplicate_override_entry.pack(side="left", padx=(0, 10))
        self.shake_duplicate_override_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.shake_duplicate_override_entry.bind('<FocusOut>', lambda event: self.save_config())
        ttk.Label(self.shake_duplicate_override_frame, text="(Override time for duplicate shake detection in milliseconds)", foreground="gray", font=('Arial', 8)).pack(side="left")

        self._update_shake_ui_visibility()
        self._update_refresh_rod_visibility()
        self._update_shake_configuration_visibility()

        # Control Settings
        control_settings_frame = ttk.LabelFrame(automation_scrollable_frame, text="Control Settings", padding="15")
        control_settings_frame.pack(fill="x", pady=(10, 0), padx=10)

        control_vars = {
            "Initial Box Length": (self.fishing_box_initial_length_var, "Starting size of fishing detection box"),
            "KP (Proportional Gain)": (self.kp_var, "How aggressively to respond to current error"),
            "KD (Derivative Gain)": (self.kd_var, "How much to dampen based on error change rate"),
            "Target Tolerance (Pixels)": (self.target_tolerance_pixels_var, "Acceptable distance from target"),
            "PD Clamp (+/-)": (self.pd_clamp_var, "Maximum control output limit"),
            "Boundary Margin Factor": (self.boundary_margin_factor_var, "Safety margin from screen edges"),
            "Min Contour Area": (self.min_contour_area_var, "Minimum size for detected objects"),
            "Target Idle Threshold": (self.target_line_idle_pixel_threshold_var, "Pixels moved to consider target active"),
            "Spam Click Timing (ms)": (self.spam_click_timing_var, "Hold/Release time in milliseconds for critical spam click"),
            "Sudden Movement Threshold": (self.sudden_movement_threshold_var, "Pixel distance for sudden movement detection (triggers fast response)"),
        }

        self._create_settings_grid(control_settings_frame, control_vars)

        # ==================== DISPLAY TAB ====================
        display_tab = ttk.Frame(notebook)
        notebook.add(display_tab, text="🖥️ Display")

        # Create scrollable frame for display options
        display_canvas = tk.Canvas(display_tab)
        self.display_canvas = display_canvas  # Store reference for theming
        display_scrollbar = ttk.Scrollbar(display_tab, orient="vertical", command=display_canvas.yview)
        display_scrollable_frame = ttk.Frame(display_canvas)

        display_scrollable_frame.bind(
            "<Configure>",
            lambda e: display_canvas.configure(scrollregion=display_canvas.bbox("all"))
        )

        display_canvas.create_window((0, 0), window=display_scrollable_frame, anchor="nw")
        display_canvas.configure(yscrollcommand=display_scrollbar.set)

        display_canvas.pack(side="left", fill="both", expand=True)
        display_scrollbar.pack(side="right", fill="y")

        display_options_frame = ttk.LabelFrame(display_scrollable_frame, text="Display Options", padding="15")
        display_options_frame.pack(fill="x", pady=(0, 10), padx=10)

        display_features = [
            ("📌 GUI Always On Top", self.topmost_var, self.toggle_topmost, "Keep this window above all other windows"),
            ("📹 Show Live Feed", self.show_live_feed, self._handle_live_feed_toggle, "Show real-time detection overlay window"),
            ("🐛 Output Debug.txt", self.output_debug_enabled, self._handle_debug_output_toggle, "Generate debug.txt file with detailed logging information")
        ]

        for text, var, command, tooltip in display_features:
            feature_frame = ttk.Frame(display_options_frame)
            feature_frame.pack(fill="x", pady=5)
            
            check = ttk.Checkbutton(feature_frame, text=text, variable=var, command=command)
            check.pack(side="left")
            ttk.Label(feature_frame, text=f"- {tooltip}", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # ==================== ADVANCED TAB ====================
        advanced_tab = ttk.Frame(notebook)
        notebook.add(advanced_tab, text="⚙️ Advanced")
        
        # Create scrollable frame for Advanced options
        advanced_canvas = tk.Canvas(advanced_tab)
        self.advanced_canvas = advanced_canvas  # Store reference for theming
        advanced_scrollbar = ttk.Scrollbar(advanced_tab, orient="vertical", command=advanced_canvas.yview)
        advanced_scrollable_frame = ttk.Frame(advanced_canvas)

        advanced_scrollable_frame.bind(
            "<Configure>",
            lambda e: advanced_canvas.configure(scrollregion=advanced_canvas.bbox("all"))
        )

        advanced_canvas.create_window((0, 0), window=advanced_scrollable_frame, anchor="nw")
        advanced_canvas.configure(yscrollcommand=advanced_scrollbar.set)

        advanced_canvas.pack(side="left", fill="both", expand=True)
        advanced_scrollbar.pack(side="right", fill="y")
        
        self._create_advanced_tab_content(advanced_scrollable_frame)

        # ==================== DISCORD TAB ====================
        discord_tab = ttk.Frame(notebook)
        notebook.add(discord_tab, text="💬 Discord")

        # Create scrollable frame for Discord options
        discord_canvas = tk.Canvas(discord_tab)
        self.discord_canvas = discord_canvas  # Store reference for theming
        discord_scrollbar = ttk.Scrollbar(discord_tab, orient="vertical", command=discord_canvas.yview)
        discord_scrollable_frame = ttk.Frame(discord_canvas)

        discord_scrollable_frame.bind(
            "<Configure>",
            lambda e: discord_canvas.configure(scrollregion=discord_canvas.bbox("all"))
        )

        discord_canvas.create_window((0, 0), window=discord_scrollable_frame, anchor="nw")
        discord_canvas.configure(yscrollcommand=discord_scrollbar.set)

        discord_canvas.pack(side="left", fill="both", expand=True)
        discord_scrollbar.pack(side="right", fill="y")

        # Discord Configuration Frame
        discord_config_frame = ttk.LabelFrame(discord_scrollable_frame, text="Discord Configuration", padding="15")
        discord_config_frame.pack(fill="x", pady=(0, 10), padx=10)

        # Webhook URL Input
        webhook_frame = ttk.Frame(discord_config_frame)
        webhook_frame.pack(fill="x", pady=5)
        
        ttk.Label(webhook_frame, text="🔗 Discord Webhook URL:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.discord_webhook_entry = ttk.Entry(webhook_frame, textvariable=self.discord_webhook_url, width=50)
        self.discord_webhook_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.discord_webhook_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.discord_webhook_entry.bind('<FocusOut>', lambda event: self.save_config())
        
        # Test button
        self.discord_test_btn = ttk.Button(webhook_frame, text="Test", command=self.test_discord_webhook)
        self.discord_test_btn.pack(side="right")

        # Help text for webhook
        ttk.Label(discord_config_frame, text="Paste your Discord webhook URL above. Create one in Discord: Server Settings > Integrations > Webhooks", 
                 foreground="gray", font=('Arial', 8)).pack(fill="x", pady=(0, 10))

        # Loops Per Screenshot Input
        loops_frame = ttk.Frame(discord_config_frame)
        loops_frame.pack(fill="x", pady=5)
        
        ttk.Label(loops_frame, text="📸 Loops Per Screenshot:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        
        # Validation for numbers only
        vcmd = (self.register(self._validate_number), '%P')
        self.discord_loops_entry = ttk.Entry(loops_frame, textvariable=self.discord_loops_per_screenshot, 
                                           width=10, validate='key', validatecommand=vcmd)
        self.discord_loops_entry.pack(side="left", padx=(0, 10))
        self.discord_loops_entry.bind('<KeyRelease>', lambda event: self.save_config())
        self.discord_loops_entry.bind('<FocusOut>', lambda event: self.save_config())
        
        ttk.Label(loops_frame, text="(Send screenshot every X fishing loops)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Discord Status Frame
        discord_status_frame = ttk.LabelFrame(discord_scrollable_frame, text="Discord Status", padding="15")
        discord_status_frame.pack(fill="x", pady=(0, 10), padx=10)

        self.discord_status_label = ttk.Label(discord_status_frame, text="Status: Not configured", 
                                            foreground="orange", font=('Arial', 10))
        self.discord_status_label.pack(fill="x", pady=5)

        self.discord_loop_status_label = ttk.Label(discord_status_frame, text="Loop Count: 0 / 0", 
                                                  foreground="gray", font=('Arial', 9))
        self.discord_loop_status_label.pack(fill="x", pady=2)

    # ==================== DISCORD INTEGRATION METHODS ====================
    
    def _validate_number(self, value):
        """Validate that input is a number"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def capture_screen_win32(self, x, y, width, height):
        """Capture screen using Windows API - more reliable for multi-monitor"""
        try:
            # Get desktop device context
            desktop_dc = win32gui.GetDC(0)
            
            # Create compatible device context and bitmap
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            # Create bitmap object
            screenshot_bmp = win32ui.CreateBitmap()
            screenshot_bmp.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot_bmp)
            
            # Copy screen area to bitmap
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (x, y), win32con.SRCCOPY)
            
            # Get bitmap info
            bmp_info = screenshot_bmp.GetInfo()
            bmp_str = screenshot_bmp.GetBitmapBits(True)
            
            # Convert to PIL Image
            screenshot = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_str, 'raw', 'BGRX', 0, 1
            )
            
            # Clean up
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot_bmp.GetHandle())
            win32gui.ReleaseDC(0, desktop_dc)
            
            return screenshot
            
        except Exception as e:
            logging.error(f"Windows API capture error: {e}")
            return None
    
    def get_active_monitor(self):
        """Get the monitor where the currently focused window is located"""
        try:
            # Get the handle of the currently active window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get the window rectangle
            window_rect = win32gui.GetWindowRect(hwnd)
            window_x, window_y, window_right, window_bottom = window_rect
            window_center_x = (window_x + window_right) // 2
            window_center_y = (window_y + window_bottom) // 2
            
            # Get all monitors
            monitors = win32api.EnumDisplayMonitors()
            
            # Find which monitor contains the active window (use center point for better detection)
            for i, (hmon, hdc, monitor_rect) in enumerate(monitors):
                left, top, right, bottom = monitor_rect
                
                # Check if the window's center is within this monitor
                if left <= window_center_x < right and top <= window_center_y < bottom:
                    return monitor_rect, i + 1
            
            # If not found, return the primary monitor
            return monitors[0][2], 1
            
        except Exception as e:
            logging.error(f"Error detecting active monitor: {e}")
            # Fallback to full screen
            return None, 0
    
    async def send_discord_screenshot(self, message="Screenshot"):
        """Capture and send screenshot to Discord webhook"""
        if not self.discord_enabled or not self.discord_webhook_url.get().strip():
            return False
            
        try:
            # Get the monitor where the active window is located
            monitor_rect, monitor_num = self.get_active_monitor()
            
            if monitor_rect:
                left, top, right, bottom = monitor_rect
                width = right - left
                height = bottom - top
                
                # Try Windows API capture first
                screenshot = self.capture_screen_win32(left, top, width, height)
                
                # Fallback to pyautogui if Windows API fails
                if screenshot is None:
                    import pyautogui
                    screenshot = pyautogui.screenshot()
            else:
                import pyautogui
                screenshot = pyautogui.screenshot()
            
            # Convert PIL image to bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Send to Discord webhook
            from aiohttp import FormData
            data = FormData()
            data.add_field('file', img_buffer.getvalue(), filename='fisch_screenshot.png', content_type='image/png')
            data.add_field('payload_json', json.dumps({
                "content": message,
                "username": "IRUS V6 Fisch Bot"
            }))
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook_url.get().strip(), data=data) as response:
                    if response.status in [200, 204]:
                        logging.info("Discord screenshot sent successfully")
                        return True
                    else:
                        logging.error(f"Discord webhook failed with status {response.status}")
                        return False
                        
        except Exception as e:
            logging.error(f"Error sending Discord screenshot: {e}")
            return False
    
    async def send_discord_message(self, message):
        """Send text message to Discord webhook"""
        if not self.discord_enabled or not self.discord_webhook_url.get().strip():
            return False
            
        try:
            payload = {
                "content": message,
                "username": "IRUS V6 Fisch Bot"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook_url.get().strip(), json=payload) as response:
                    if response.status in [200, 204]:
                        logging.info(f"Discord message sent: {message}")
                        return True
                    else:
                        logging.error(f"Discord webhook failed with status {response.status}")
                        return False
                        
        except Exception as e:
            logging.error(f"Error sending Discord message: {e}")
            return False
    
    def test_discord_webhook(self):
        """Test Discord webhook with a simple message"""
        def run_test():
            try:
                webhook_url = self.discord_webhook_url.get().strip()
                if not webhook_url:
                    self.after(0, lambda: self.update_discord_status("❌ No webhook URL provided", "red"))
                    return
                
                if not webhook_url.startswith("https://discord.com/api/webhooks/"):
                    self.after(0, lambda: self.update_discord_status("❌ Invalid webhook URL format", "red"))
                    return
                
                # Use requests for simpler synchronous HTTP call
                import requests
                data = {"content": "🧪 Test message from IRUS V6"}
                response = requests.post(webhook_url, json=data, timeout=10)
                
                if response.status_code == 204:
                    self.after(0, lambda: self.update_discord_status("✅ Test successful!", "green"))
                else:
                    self.after(0, lambda: self.update_discord_status(f"❌ Test failed - HTTP {response.status_code}", "red"))
                    
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.update_discord_status("❌ Connection timeout - check network", "red"))
            except requests.exceptions.ConnectionError:
                self.after(0, lambda: self.update_discord_status("❌ Connection failed - check network/URL", "red"))
            except requests.exceptions.SSLError:
                self.after(0, lambda: self.update_discord_status("❌ SSL error - check internet connection", "red"))
            except Exception as e:
                error_msg = str(e)[:50]  # Truncate long error messages
                self.after(0, lambda: self.update_discord_status(f"❌ Test error: {error_msg}", "red"))
                logging.error(f"Discord webhook test failed: {e}")
        
        # Prevent multiple simultaneous tests
        if hasattr(self, '_discord_test_running') and self._discord_test_running:
            self.update_discord_status("⚠️ Test already in progress...", "orange")
            return
        
        # Update status to testing
        self.update_discord_status("🔄 Testing webhook...", "orange")
        self._discord_test_running = True
        
        def wrapped_test():
            try:
                run_test()
            finally:
                self._discord_test_running = False
        
        # Run test in background thread
        thread = threading.Thread(target=wrapped_test, daemon=True)
        thread.start()
    
    def update_discord_status(self, message, color="black"):
        """Update Discord status label"""
        self.discord_status_label.config(text=f"Status: {message}", foreground=color)
    
    def update_discord_enabled_status(self):
        """Update Discord enabled status based on webhook URL"""
        webhook_url = self.discord_webhook_url.get().strip()
        if webhook_url and webhook_url.startswith("https://discord.com/api/webhooks/"):
            self.discord_enabled = True
            if "Test" not in self.discord_status_label.cget("text"):
                self.update_discord_status("✅ Ready", "green")
        else:
            self.discord_enabled = False
            if webhook_url:
                self.update_discord_status("⚠️ Invalid webhook URL", "orange")
            else:
                self.update_discord_status("❌ Not configured", "red")
    
    def notify_fishing_started(self):
        """Send Discord notification when fishing starts"""
        if not self.discord_enabled:
            return
            
        def send_notification():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.send_discord_message("🎣 Fisch Macro Started"))
                loop.run_until_complete(self.send_discord_screenshot("🎣 Fisch Macro Started - Initial Screenshot"))
                self.discord_screenshot_sent = True
            except Exception as e:
                logging.error(f"Error sending Discord start notification: {e}")
            finally:
                loop.close()
        
        threading.Thread(target=send_notification, daemon=True).start()
    
    def notify_fishing_loop(self):
        """Handle Discord notification for fishing loops"""
        current_time = time.time()
        
        # Prevent multiple notifications within 2 seconds (debounce)
        if current_time - self._last_loop_notification_time < 2.0:
            conditional_logger.debug("Fishing loop notification skipped (too recent)")
            return
            
        # Increment main fishing loop counter (always, regardless of Discord)
        self.main_fishing_loop_count += 1
        self._last_loop_notification_time = current_time
        conditional_logger.info(f"Starting Fishing Loop {self.main_fishing_loop_count}")
        
        # Handle Discord notifications if enabled
        if not self.discord_enabled:
            return
            
        try:
            loops_per_screenshot = int(self.discord_loops_per_screenshot.get() or "10")
        except ValueError:
            loops_per_screenshot = 10
        
        self.discord_loop_count += 1
        
        # Update loop status
        self.discord_loop_status_label.config(
            text=f"Loop Count: {self.discord_loop_count} / {loops_per_screenshot}"
        )
        
        # Send screenshot if we've reached the loop count
        if self.discord_loop_count >= loops_per_screenshot:
            def send_screenshot():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        self.send_discord_screenshot(f"🐟 Fishing Loop {self.main_fishing_loop_count} - Screenshot")
                    )
                except Exception as e:
                    logging.error(f"Error sending Discord loop screenshot: {e}")
                finally:
                    loop.close()
            
            # Reset counter
            self.discord_loop_count = 0
            self.discord_loop_status_label.config(text=f"Loop Count: 0 / {loops_per_screenshot}")
            
            # Send screenshot in separate thread
            threading.Thread(target=send_screenshot, daemon=True).start()


    def _create_settings_grid(self, parent, settings_dict):
        """Helper to create a grid of settings with labels and entries."""
        try:
            cfg = self.loaded_config
            learned_kp = cfg.get("LEARNED_ADAPTIVE_KP", "0.35")
            learned_kd = cfg.get("LEARNED_ADAPTIVE_KD", "6.0")
            learned_offset = cfg.get("LEARNED_ARROW_OFFSET", "None")

            self.adaptive_kp = float(learned_kp)
            self.adaptive_kd = float(learned_kd)

            # Load all specialized adaptive KP/KD values
            self.adaptive_steady_kp = float(cfg.get("LEARNED_ADAPTIVE_STEADY_KP", "0.35"))
            self.adaptive_steady_kd = float(cfg.get("LEARNED_ADAPTIVE_STEADY_KD", "6.0"))
            self.adaptive_fast_kp = float(cfg.get("LEARNED_ADAPTIVE_FAST_KP", "0.45"))
            self.adaptive_fast_kd = float(cfg.get("LEARNED_ADAPTIVE_FAST_KD", "4.0"))
            self.adaptive_pred_kp = float(cfg.get("LEARNED_ADAPTIVE_PRED_KP", "0.30"))
            self.adaptive_pred_kd = float(cfg.get("LEARNED_ADAPTIVE_PRED_KD", "7.0"))
            self.adaptive_recovery_kp = float(cfg.get("LEARNED_ADAPTIVE_RECOVERY_KP", "0.25"))
            self.adaptive_recovery_kd = float(cfg.get("LEARNED_ADAPTIVE_RECOVERY_KD", "8.0"))
            self.adaptive_boundary_kp = float(cfg.get("LEARNED_ADAPTIVE_BOUNDARY_KP", "0.40"))
            self.adaptive_boundary_kd = float(cfg.get("LEARNED_ADAPTIVE_BOUNDARY_KD", "5.0"))
            self.adaptive_fine_kp = float(cfg.get("LEARNED_ADAPTIVE_FINE_KP", "0.20"))
            self.adaptive_fine_kd = float(cfg.get("LEARNED_ADAPTIVE_FINE_KD", "9.0"))

            if learned_offset != "None":
                self.learned_arrow_offset = float(learned_offset)
                self.arrow_offset_calibrated = True
                logging.info(f"Loaded learned arrow offset: {self.learned_arrow_offset:.1f}px")
            else:
                self.learned_arrow_offset = None
                self.arrow_offset_calibrated = False

            logging.info(f"Loaded adaptive PID values: KP={self.adaptive_kp:.3f}, KD={self.adaptive_kd:.3f}")
            logging.info(f"Loaded specialized adaptive PID values: "
                         f"steady_kp={self.adaptive_steady_kp:.3f}, steady_kd={self.adaptive_steady_kd:.3f}, "
                         f"fast_kp={self.adaptive_fast_kp:.3f}, fast_kd={self.adaptive_fast_kd:.3f}, "
                         f"pred_kp={self.adaptive_pred_kp:.3f}, pred_kd={self.adaptive_pred_kd:.3f}, "
                         f"recovery_kp={self.adaptive_recovery_kp:.3f}, recovery_kd={self.adaptive_recovery_kd:.3f}, "
                         f"boundary_kp={self.adaptive_boundary_kp:.3f}, boundary_kd={self.adaptive_boundary_kd:.3f}, "
                         f"fine_kp={self.adaptive_fine_kp:.3f}, fine_kd={self.adaptive_fine_kd:.3f}")
        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to load learned values, using defaults: {e}")
            self.adaptive_kp = 0.35
            self.adaptive_kd = 6.0
            self.adaptive_steady_kp = 0.35
            self.adaptive_steady_kd = 6.0
            self.adaptive_fast_kp = 0.45
            self.adaptive_fast_kd = 4.0
            self.adaptive_pred_kp = 0.30
            self.adaptive_pred_kd = 7.0
            self.adaptive_recovery_kp = 0.25
            self.adaptive_recovery_kd = 8.0
            self.adaptive_boundary_kp = 0.40
            self.adaptive_boundary_kd = 5.0
            self.adaptive_fine_kp = 0.20
            self.adaptive_fine_kd = 9.0
            self.learned_arrow_offset = None
            self.arrow_offset_calibrated = False

    def _handle_live_feed_toggle(self):
        """Handles live feed window visibility - show when checked, hide when unchecked."""
        if self.show_live_feed.get():
            # Checkbox is checked - show live feed window if not already shown
            if self.feedback_window is None or not self.feedback_window.winfo_exists():
                # Get current geometry values
                fish_geom_value = self.fish_geometry.get()
                live_feed_pos_value = self.live_feed_position.get()
                target_fps = max(1, int(self.fps_var.get()))
                
                logging.info("Live Feed toggle: Creating live feed window.")
                self.feedback_window = LiveFeedbackWindow(self, fish_geom_value, live_feed_pos_value, target_fps)
        else:
            # Checkbox is unchecked - close live feed window
            if self.feedback_window:
                logging.info("Live Feed toggle: Closing feedback window.")
                self.feedback_window.close()
                self.feedback_window = None
        self.save_config()

    def _handle_debug_output_toggle(self):
        """Handles enabling/disabling debug output logging."""
        debug_enabled = self.output_debug_enabled.get()
        if debug_enabled:
            # Enable all logging and file logging
            _enable_logging()
            _setup_debug_logging()
            conditional_logger.info("Debug output enabled - logging to Debug.txt")
        else:
            # Disable file logging and all logging to prevent performance overhead
            _disable_debug_logging()
            _disable_all_logging()
            print("Debug output disabled - all logging stopped to prevent lag")
        self.save_config()

    def _setup_debug_logging(self):
        """Enable debug logging to file (instance method wrapper)."""
        _setup_debug_logging()

    def is_logging_enabled(self):
        """Check if logging is enabled - convenience method for any remaining direct logging calls."""
        return self.output_debug_enabled.get()

    def _create_advanced_tab_content(self, parent):
        """Create the Advanced tab with all advanced settings not available in other tabs."""
        
        # ==================== PID TUNING SECTION ====================
        pid_frame = ttk.LabelFrame(parent, text="🎛️ PID Controller Tuning", padding="15")
        pid_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Main PID values
        main_pid_frame = ttk.Frame(pid_frame)
        main_pid_frame.pack(fill="x", pady=5)
        ttk.Label(main_pid_frame, text="🎯 Main PID Values:", font=('Arial', 10, 'bold')).pack(anchor="w")
        
        kp_frame = ttk.Frame(main_pid_frame)
        kp_frame.pack(fill="x", pady=2)
        ttk.Label(kp_frame, text="KP (Proportional):", width=20).pack(side="left")
        ttk.Entry(kp_frame, textvariable=self.kp_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(kp_frame, text="Controls responsiveness to current error", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        kd_frame = ttk.Frame(main_pid_frame)
        kd_frame.pack(fill="x", pady=2)
        ttk.Label(kd_frame, text="KD (Derivative):", width=20).pack(side="left")
        ttk.Entry(kd_frame, textvariable=self.kd_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(kd_frame, text="Controls response to rate of change", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Target tolerance
        tolerance_frame = ttk.Frame(main_pid_frame)
        tolerance_frame.pack(fill="x", pady=2)
        ttk.Label(tolerance_frame, text="Target Tolerance:", width=20).pack(side="left")
        ttk.Entry(tolerance_frame, textvariable=self.target_tolerance_pixels_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(tolerance_frame, text="Acceptable error range in pixels", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # PD Clamp
        clamp_frame = ttk.Frame(main_pid_frame)
        clamp_frame.pack(fill="x", pady=2)
        ttk.Label(clamp_frame, text="PD Clamp:", width=20).pack(side="left")
        ttk.Entry(clamp_frame, textvariable=self.pd_clamp_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(clamp_frame, text="Maximum control signal limit", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # ==================== MACHINE LEARNING SECTION ====================
        ml_frame = ttk.LabelFrame(parent, text="🤖 Machine Learning Parameters", padding="15")
        ml_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Bar prediction settings
        bar_pred_frame = ttk.Frame(ml_frame)
        bar_pred_frame.pack(fill="x", pady=5)
        ttk.Label(bar_pred_frame, text="🎯 Bar Movement Prediction:", font=('Arial', 10, 'bold')).pack(anchor="w")
        
        # Current velocity
        vel_frame = ttk.Frame(bar_pred_frame)
        vel_frame.pack(fill="x", pady=2)
        ttk.Label(vel_frame, text="Current Velocity:", width=20).pack(side="left")
        vel_label = ttk.Label(vel_frame, text=f"{self.current_velocity:.3f}", foreground="blue")
        vel_label.pack(side="left", padx=(0, 10))
        ttk.Label(vel_frame, text="Pixels per frame movement", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Smoothing factor
        smooth_frame = ttk.Frame(bar_pred_frame)
        smooth_frame.pack(fill="x", pady=2)
        ttk.Label(smooth_frame, text="Smoothing Factor:", width=20).pack(side="left")
        ttk.Entry(smooth_frame, textvariable=self.velocity_smoothing_factor_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(smooth_frame, text="0.0-1.0, higher = more smoothing", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Min velocity threshold
        min_vel_frame = ttk.Frame(bar_pred_frame)
        min_vel_frame.pack(fill="x", pady=2)
        ttk.Label(min_vel_frame, text="Min Velocity Threshold:", width=20).pack(side="left")
        ttk.Entry(min_vel_frame, textvariable=self.min_velocity_threshold_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(min_vel_frame, text="Minimum movement to predict", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Max prediction distance
        max_dist_frame = ttk.Frame(bar_pred_frame)
        max_dist_frame.pack(fill="x", pady=2)
        ttk.Label(max_dist_frame, text="Max Prediction Distance:", width=20).pack(side="left")
        ttk.Entry(max_dist_frame, textvariable=self.max_prediction_distance_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(max_dist_frame, text="Maximum pixels to predict ahead", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # ==================== DETECTION TOLERANCES SECTION ====================
        detection_frame = ttk.LabelFrame(parent, text="🎨 Detection Tolerances", padding="15")
        detection_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Target line tolerance
        target_tol_frame = ttk.Frame(detection_frame)
        target_tol_frame.pack(fill="x", pady=2)
        ttk.Label(target_tol_frame, text="Target Line Tolerance:", width=20).pack(side="left")
        ttk.Entry(target_tol_frame, textvariable=self.target_line_tolerance_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(target_tol_frame, text="Color tolerance for target line detection", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Arrow tolerance
        arrow_tol_frame = ttk.Frame(detection_frame)
        arrow_tol_frame.pack(fill="x", pady=2)
        ttk.Label(arrow_tol_frame, text="Arrow Tolerance:", width=20).pack(side="left")
        ttk.Entry(arrow_tol_frame, textvariable=self.indicator_arrow_tolerance_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(arrow_tol_frame, text="Color tolerance for arrow detection", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Box color tolerance
        box_tol_frame = ttk.Frame(detection_frame)
        box_tol_frame.pack(fill="x", pady=2)
        ttk.Label(box_tol_frame, text="Box Color Tolerance:", width=20).pack(side="left")
        ttk.Entry(box_tol_frame, textvariable=self.box_color_tolerance_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(box_tol_frame, text="Color tolerance for fishing box detection", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Min contour area
        contour_frame = ttk.Frame(detection_frame)
        contour_frame.pack(fill="x", pady=2)
        ttk.Label(contour_frame, text="Min Contour Area:", width=20).pack(side="left")
        ttk.Entry(contour_frame, textvariable=self.min_contour_area_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(contour_frame, text="Minimum area for contour detection", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Target line idle threshold
        idle_thresh_frame = ttk.Frame(detection_frame)
        idle_thresh_frame.pack(fill="x", pady=2)
        ttk.Label(idle_thresh_frame, text="Idle Pixel Threshold:", width=20).pack(side="left")
        ttk.Entry(idle_thresh_frame, textvariable=self.target_line_idle_pixel_threshold_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(idle_thresh_frame, text="Pixels needed to transition from IDLE", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # ==================== TIMING PARAMETERS SECTION ====================
        timing_frame = ttk.LabelFrame(parent, text="⏱️ Timing Parameters", padding="15")
        timing_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Boundary margin factor
        boundary_frame = ttk.Frame(timing_frame)
        boundary_frame.pack(fill="x", pady=2)
        ttk.Label(boundary_frame, text="Boundary Margin Factor:", width=20).pack(side="left")
        ttk.Entry(boundary_frame, textvariable=self.boundary_margin_factor_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(boundary_frame, text="Safety margin for boundary detection", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Fishing box initial length
        box_length_frame = ttk.Frame(timing_frame)
        box_length_frame.pack(fill="x", pady=2)
        ttk.Label(box_length_frame, text="Box Initial Length:", width=20).pack(side="left")
        ttk.Entry(box_length_frame, textvariable=self.fishing_box_initial_length_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(box_length_frame, text="Initial fishing box width in pixels", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Sudden movement threshold
        sudden_frame = ttk.Frame(timing_frame)
        sudden_frame.pack(fill="x", pady=2)
        ttk.Label(sudden_frame, text="Sudden Movement Threshold:", width=20).pack(side="left")
        ttk.Entry(sudden_frame, textvariable=self.sudden_movement_threshold_var, width=10).pack(side="left", padx=(0, 10))
        ttk.Label(sudden_frame, text="Pixels for fast response trigger", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # ==================== ADAPTIVE LEARNING SECTION ====================
        adaptive_frame = ttk.LabelFrame(parent, text="🧠 Adaptive Learning System", padding="15")
        adaptive_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Show current learned values (read-only)
        ttk.Label(adaptive_frame, text="📚 Current Learned Values (Auto-updated):", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        
        learned_info_frame = ttk.Frame(adaptive_frame)
        learned_info_frame.pack(fill="x", pady=5)
        
        learned_kp_frame = ttk.Frame(learned_info_frame)
        learned_kp_frame.pack(fill="x", pady=1)
        ttk.Label(learned_kp_frame, text="Adaptive KP:", width=20).pack(side="left")
        learned_kp_label = ttk.Label(learned_kp_frame, text=f"{self.adaptive_kp:.3f}", foreground="green")
        learned_kp_label.pack(side="left", padx=(0, 10))
        ttk.Label(learned_kp_frame, text="System-learned proportional gain", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        learned_kd_frame = ttk.Frame(learned_info_frame)
        learned_kd_frame.pack(fill="x", pady=1)
        ttk.Label(learned_kd_frame, text="Adaptive KD:", width=20).pack(side="left")
        learned_kd_label = ttk.Label(learned_kd_frame, text=f"{self.adaptive_kd:.3f}", foreground="green")
        learned_kd_label.pack(side="left", padx=(0, 10))
        ttk.Label(learned_kd_frame, text="System-learned derivative gain", foreground="gray", font=('Arial', 8)).pack(side="left")
        
        # Note about rod-specific learning
        note_frame = ttk.Frame(adaptive_frame)
        note_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(note_frame, text="� Note: Learning values are saved per rod type", 
                 foreground="blue", font=('Arial', 9)).pack(side="left")



    def _on_ml_params_changed(self, *args):
        """Callback when ML parameter GUI variables are changed."""
        try:
            # Update the actual values from GUI variables
            self.velocity_smoothing_factor = float(self.velocity_smoothing_factor_var.get())
        except ValueError:
            self.velocity_smoothing_factor = 0.8
            
        try:
            self.min_velocity_threshold = float(self.min_velocity_threshold_var.get())
        except ValueError:
            self.min_velocity_threshold = 3.0
            
        try:
            self.max_prediction_distance = float(self.max_prediction_distance_var.get())
        except ValueError:
            self.max_prediction_distance = 20.0
            
        # Save config when changed
        self.save_config_debounced()

    def _save_current_rod_ml_values(self):
        """Save current rod's ML values to loaded_config before saving to file."""
        try:
            current_rod_type = self.rod_type_var.get()
            current_rod_key = current_rod_type.replace(' ', '_').upper()
            
            # Save current ML values to loaded_config
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_KP"] = f"{self.adaptive_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_KD"] = f"{self.adaptive_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ARROW_OFFSET"] = "None" if self.learned_arrow_offset is None else f"{self.learned_arrow_offset:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_STEADY_KP"] = f"{self.adaptive_steady_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_STEADY_KD"] = f"{self.adaptive_steady_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FAST_KP"] = f"{self.adaptive_fast_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FAST_KD"] = f"{self.adaptive_fast_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_PRED_KP"] = f"{self.adaptive_pred_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_PRED_KD"] = f"{self.adaptive_pred_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KP"] = f"{self.adaptive_recovery_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_RECOVERY_KD"] = f"{self.adaptive_recovery_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KP"] = f"{self.adaptive_boundary_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_BOUNDARY_KD"] = f"{self.adaptive_boundary_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FINE_KP"] = f"{self.adaptive_fine_kp:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_LEARNED_ADAPTIVE_FINE_KD"] = f"{self.adaptive_fine_kd:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_ML_BAR_VELOCITY"] = f"{self.current_velocity:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_ML_BAR_ACCELERATION"] = f"{self.current_acceleration:.6f}"
            self.loaded_config[f"ROD_{current_rod_key}_ML_BAR_RELIABILITY"] = f"{self.prediction_reliability_score:.6f}"
            
            logging.debug(f"Saved current ML values for rod {current_rod_type}")
        except Exception as e:
            logging.error(f"Error saving current rod ML values: {e}")

    def _disable_debug_logging(self):
        """Disable debug logging to file (instance method wrapper)."""
        _disable_debug_logging()

    def _on_shake_mode_change(self, event=None):
        """Called when shake mode is changed - save config and update shake UI visibility."""
        self.save_config()
        self._update_shake_ui_visibility()

    def _update_shake_ui_visibility(self):
        """Shows or hides the click type, click count, and navigation key dropdowns based on shake mode."""
        if self.shake_mode_var.get() == "Click":
            self.click_type_frame.pack(fill="x", pady=5)
            # Show pixel tolerance only if pixel mode is selected
            if self.shake_click_type_var.get() == "Pixel":
                self.shake_pixel_tolerance_frame.pack(fill="x", pady=5)
                self.shake_circle_tolerance_frame.pack_forget()
            elif self.shake_click_type_var.get() == "Circle":
                self.shake_pixel_tolerance_frame.pack_forget()
                self.shake_circle_tolerance_frame.pack(fill="x", pady=5)
            else:
                self.shake_pixel_tolerance_frame.pack_forget()
                self.shake_circle_tolerance_frame.pack_forget()
            self.click_count_frame.pack(fill="x", pady=5)
            self.navigation_key_frame.pack_forget()
            self.navigation_shake_pixel_tolerance_frame.pack_forget()
            self.navigation_recast_delay_frame.pack_forget()
            self.navigation_enter_spam_delay_frame.pack_forget()
            # Show shake delay for click mode
            self.shake_delay_frame.pack(fill="x", pady=5)
        elif self.shake_mode_var.get() == "Navigation":
            self.click_type_frame.pack_forget()
            self.shake_pixel_tolerance_frame.pack_forget()
            self.shake_circle_tolerance_frame.pack_forget()
            self.click_count_frame.pack_forget()
            self.navigation_key_frame.pack(fill="x", pady=5)
            self.navigation_shake_pixel_tolerance_frame.pack(fill="x", pady=5)
            self.navigation_recast_delay_frame.pack(fill="x", pady=5)
            self.navigation_enter_spam_delay_frame.pack(fill="x", pady=5)
            # Hide shake delay for navigation mode since it uses separate timing controls
            self.shake_delay_frame.pack_forget()
        else:
            self.click_type_frame.pack_forget()
            self.shake_pixel_tolerance_frame.pack_forget()
            self.shake_circle_tolerance_frame.pack_forget()
            self.click_count_frame.pack_forget()
            self.navigation_key_frame.pack_forget()
            self.navigation_shake_pixel_tolerance_frame.pack_forget()
            self.navigation_recast_delay_frame.pack_forget()
            self.navigation_enter_spam_delay_frame.pack_forget()
            # Hide shake delay for unknown modes
            self.shake_delay_frame.pack_forget()

    def _on_auto_cast_change(self):
        """Called when auto cast checkbox is changed - save config and update refresh rod visibility."""
        self.save_config()
        self._update_refresh_rod_visibility()

    def _on_refresh_rod_change(self):
        """Called when refresh rod checkbox is changed - save config and update refresh rod delay visibility."""
        self.save_config()
        self._update_refresh_rod_visibility()

    def _on_adaptive_tuning_change(self):
        """Called when adaptive tuning checkbox is changed - update adaptive enabled flag and save config."""
        self.adaptive_enabled = self.adaptive_tuning_enabled_var.get()
        self.save_config()
        logging.info(f"Adaptive PID tuning {'enabled' if self.adaptive_enabled else 'disabled'}")

    def _update_refresh_rod_visibility(self):
        """Shows or hides the autocast-related settings based on auto cast and refresh rod state."""
        if self.auto_cast_enabled.get():
            # Show autocast timing settings
            self.refresh_rod_frame.pack(fill="x", pady=5, after=self.auto_cast_frame)
            self.autocast_hold_time_frame.pack(fill="x", pady=5, after=self.refresh_rod_frame)
            self.autocast_wait_time_frame.pack(fill="x", pady=5, after=self.autocast_hold_time_frame)
            
            # Show refresh rod delay only if refresh rod is enabled
            if self.refresh_rod_enabled.get():
                self.refresh_rod_delay_frame.pack(fill="x", pady=5, after=self.autocast_wait_time_frame)
            else:
                self.refresh_rod_delay_frame.pack_forget()
        else:
            # Hide all autocast-related frames
            self.refresh_rod_frame.pack_forget()
            self.autocast_hold_time_frame.pack_forget()
            self.autocast_wait_time_frame.pack_forget()
            self.refresh_rod_delay_frame.pack_forget()

    def _on_auto_shake_change(self):
        """Called when auto shake checkbox is changed - save config and update shake configuration visibility."""
        self.save_config()
        self._update_shake_configuration_visibility()

    def _update_shake_configuration_visibility(self):
        """Shows or hides the entire Shake Configuration section based on Auto Shake state."""
        if self.auto_shake_enabled.get():
            # Show the shake configuration section
            self.shake_frame.pack(fill="x", pady=(0, 10), padx=10)
        else:
            # Hide the shake configuration section
            self.shake_frame.pack_forget()

    def _validate_single_char(self, value):
        """Validation function to allow only 1 character in navigation key entry."""
        return len(value) <= 1

    # --- Other Helper Methods ---

    def _get_control_delay_s(self):
        """Calculates the control loop delay in seconds based on the user's selected FPS."""
        try:
            fps = int(self.fps_var.get())
            if fps <= 0: return 0.033 # Safety default to 30 FPS
            delay = 1.0 / fps
            # Allow very high FPS - minimum delay of 0.0001s (10,000 FPS theoretical max)
            return max(0.0001, delay)
        except ValueError:
            return 0.033 # Default to 30 FPS

    def on_close(self):
        logging.info("Application closing...")
        self._stop_automation(exit_clean=True)
        self.save_config()
        if self.feedback_window:
            self.feedback_window.close()
        self.destroy()

    def on_main_window_configure(self, event):
        """Handle main window move/resize events to save position."""
        # Only trigger for the main window itself, not child widgets
        if event.widget == self:
            # Use debounced save to avoid excessive config writes during dragging
            self.save_config_debounced()

    def save_live_feed_position(self):
        if self.feedback_window:
            try:
                geom = self.feedback_window.winfo_geometry()
                _, pos_str = geom.split('+', 1)
                self.live_feed_position.set("+" + pos_str)
            except Exception:
                pass

    def toggle_topmost(self):
        state = self.topmost_var.get()
        self.wm_attributes("-topmost", state)

    def setup_hotkeys(self):
        global GLOBAL_HOTKEYS_AVAILABLE

        if GLOBAL_HOTKEYS_AVAILABLE:
            try:
                # Unhook all previous keys before setting new ones to prevent duplicates
                keyboard.unhook_all()

                key_map = {
                    self.start_stop_key.get().lower(): 'START/STOP',
                    self.resize_key.get().lower(): 'RESIZE',
                    self.force_exit_key.get().lower(): 'EXIT'
                }

                for key, action in key_map.items():
                    # Use self.after to ensure action happens on the main Tkinter thread
                    keyboard.add_hotkey(key, self.after, args=(0, self.handle_hotkey_action, action))

                logging.info("Global Hotkeys Initialized and Active.")
            except Exception as e:
                logging.error(f"Error binding global hotkeys: {e}")
                GLOBAL_HOTKEYS_AVAILABLE = False
        else:
            logging.warning("Global hotkeys disabled.")

    def handle_hotkey_action(self, action_type, event=None):
        """Centralized logic for all hotkey actions (executed in the main thread)."""

        key_map_reverse = {
            'START/STOP': self.start_stop_key.get(),
            'RESIZE': self.resize_key.get(),
            'EXIT': self.force_exit_key.get()
        }
        pressed_key_sym = key_map_reverse.get(action_type, 'UNKNOWN').upper()

        logging.info(f"Hotkey '{pressed_key_sym}' pressed for action: {action_type}.")

        if action_type == 'EXIT':
            self.on_close()

        elif action_type == 'RESIZE':
            self.is_resizing_active = not self.is_resizing_active

            if self.shake_window is None:
                self.shake_window = FloatingArea(self, self.shake_geometry, "ShakeArea", "#e03b3b") # Red color
                self.fish_window = FloatingArea(self, self.fish_geometry, "FishBarArea", "#3b5de0") # Blue color

            self.shake_window.toggle_visibility(self.is_resizing_active)
            self.fish_window.toggle_visibility(self.is_resizing_active)

            if not self.is_resizing_active:
                self.save_config()

        elif action_type == 'START/STOP':
            if not self.is_active:
                logging.info(f"Script Start triggered. Initial state: {self.state}")
                self._start_automation()
            else:
                logging.info("Script Stop triggered.")
                self._stop_automation()

    def _perform_auto_zoom_in(self):
        """
        Performs the auto zoom in sequence: scroll up 10 times, then down 1 time.
        Uses proper coordinate validation for multi-monitor setups.
        """
        if not self.auto_zoom_in_enabled.get():
            return
        
        logging.info("Auto Zoom In: Starting zoom sequence (10 up, 1 down)")
        
        try:
            # Refresh monitor info in case setup changed
            monitor_helper.refresh_monitor_info()
            # Get a safe scroll position - prefer current mouse position if valid
            try:
                current_x, current_y = pyautogui.position()
                if monitor_helper.validate_coordinates(current_x, current_y):
                    scroll_x, scroll_y = current_x, current_y
                    logging.info(f"Auto Zoom In: Using current mouse position ({current_x}, {current_y})")
                else:
                    scroll_x, scroll_y = monitor_helper.get_safe_scroll_position()
                    logging.info(f"Auto Zoom In: Mouse outside bounds, using safe position ({scroll_x}, {scroll_y})")
            except:
                # Fallback to safe position
                scroll_x, scroll_y = monitor_helper.get_safe_scroll_position()
                logging.info(f"Auto Zoom In: Using fallback safe position ({scroll_x}, {scroll_y})")

            logging.info(f"Auto Zoom In: Scrolling at position ({scroll_x}, {scroll_y})")

            # Move mouse to scroll position
            if MOUSE_CONTROL_AVAILABLE:
                pyautogui.moveTo(scroll_x, scroll_y)

            # Try to use Windows API for physical scroll
            used_physical_scroll = False
            try:
                if WINDOWS_API_AVAILABLE:
                    MOUSEEVENTF_WHEEL = 0x0800
                    for i in range(10):
                        windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, 120, 0)  # 120 is one notch up
                        time.sleep(0.05)
                        logging.info(f"Auto Zoom In: Physical scroll up {i+1}/10")
                    time.sleep(0.2)
                    windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, -120, 0)  # 1 notch down
                    time.sleep(0.05)
                    logging.info("Auto Zoom In: Physical scroll down 1/1")
                    used_physical_scroll = True
            except Exception as e:
                logging.warning(f"Auto Zoom In: Physical scroll failed, falling back to pyautogui: {e}")

            if not used_physical_scroll:
                # Fallback to pyautogui.scroll
                for i in range(10):
                    if MOUSE_CONTROL_AVAILABLE:
                        pyautogui.scroll(3, x=scroll_x, y=scroll_y)
                    time.sleep(0.05)
                    logging.info(f"Auto Zoom In: Fallback scroll up {i+1}/10")
                time.sleep(0.2)
                if MOUSE_CONTROL_AVAILABLE:
                    pyautogui.scroll(-3, x=scroll_x, y=scroll_y)
                time.sleep(0.05)
                logging.info("Auto Zoom In: Fallback scroll down 1/1")

            logging.info("Auto Zoom In: Zoom sequence completed successfully")
            
            # NEW: If Navigation mode and first time, perform navigation sequence immediately after zoom
            if self.shake_mode_var.get() == "Navigation" and not self.navigation_has_run_once:
                logging.info("IMMEDIATE NAVIGATION: Performing navigation sequence right after zoom completion")
                self._perform_navigation_sequence()
                self.navigation_has_run_once = True
                logging.info("IMMEDIATE NAVIGATION: Navigation sequence completed, ready for auto-cast")

        except Exception as e:
            logging.error(f"Auto Zoom In: Error during zoom sequence: {e}")
            # Try to continue anyway
            try:
                monitor_helper.refresh_monitor_info()
                logging.info("Auto Zoom In: Monitor info refreshed after error")
            except Exception as refresh_error:
                logging.error(f"Auto Zoom In: Failed to refresh monitor info: {refresh_error}")

    # --- THREADING METHODS ---
    def _start_automation(self):
        """
        Initiates the visual feedback (on main thread) and the automation thread.
        """
        fish_geom_value = self.fish_geometry.get()
        live_feed_pos_value = self.live_feed_position.get()
        target_fps = self.fps_var.get()

        # REFRESH MONITOR INFO FOR CURRENT SESSION
        monitor_helper.refresh_monitor_info()
        self.log_monitor_debug_info()
        logging.info("Monitor configuration refreshed for new automation session")

        # RESET INITIALIZATION STATE
        self.state = "IDLE" # START IN IDLE
        self.initialization_stage = 0
        self.initial_anchor_x = None
        self.has_calculated_length_once = False
        self.is_holding_click = False
        self.last_target_x_for_move_check = None
        
        # Reset navigation flag when starting automation
        self.navigation_has_run_once = False
        
        # Reset fishing loop counter and debounce timer
        self.main_fishing_loop_count = 0
        self._last_loop_notification_time = 0.0
        
        # Log configuration at automation start
        logging.info("=== AUTOMATION START DEBUG ===")
        logging.info(f"Initial state: {self.state}")
        logging.info(f"Shake mode: {self.shake_mode_var.get()}")
        logging.info(f"Auto cast enabled: {self.auto_cast_enabled.get()}")
        logging.info(f"Auto shake enabled: {self.auto_shake_enabled.get()}")
        logging.info(f"Navigation has run once: {self.navigation_has_run_once}")
        logging.info("=== END AUTOMATION START DEBUG ===")

        # RESET CONTROL STATE
        self.last_error = 0.0
        self.last_target_x = None
        self.last_time = time.perf_counter() # Reset time anchor for time_delta calculation

        # RESET COOLDOWN TIMER
        self.lost_target_line_time = 0.0
        self.tracking_lost_time = 0.0 # RESET NEW TIMER
        self.spam_click_next_toggle_time = 0.0  # RESET SPAM CLICK TIMER

        # RESET AUTO CAST TIMER
        # The auto-cast logic will handle the timer reset if enabled

        # Update main status label
        self.status_label.config(text=f"Status: {self.state} (FPS: {target_fps})", foreground="#000080")

        # --- NEW LIVE FEED TOGGLE LOGIC ---
        if self.show_live_feed.get():
            if self.feedback_window is None or not self.feedback_window.winfo_exists():
                self.feedback_window = LiveFeedbackWindow(self, fish_geom_value, live_feed_pos_value, target_fps)
        else:
            # If the user started the script while the checkbox was unchecked, ensure the window is closed
            if self.feedback_window:
                self.feedback_window.close()
                self.feedback_window = None
        # ----------------------------------

        # --- PERFORM AUTO ZOOM IN SEQUENCE ---
        self._perform_auto_zoom_in()

        # Start the background thread for CV and control logic
        self.is_active = True
        self.control_thread = threading.Thread(target=self._control_thread_run, daemon=True)
        self.control_thread.start()
        logging.info(f"Control thread started successfully at {target_fps} FPS.")
        
        # Send Discord notification that fishing has started
        self.notify_fishing_started()

    def _return_to_idle(self):
        """Resets variables and moves the state back to IDLE to wait for the next session."""
        self.state = "IDLE"
        self.last_left_x = None
        self.last_right_x = None
        self.box_center_x = None
        try:
            self.estimated_box_length = int(self.fishing_box_initial_length_var.get())
        except (ValueError, AttributeError):
            self.estimated_box_length = 50
        self.has_calculated_length_once = False
        self.initialization_stage = 0
        self.last_holding_state = False # Reset to RELEASE
        self.last_error = 0.0
        self.last_target_x = None

        # Reset the fishing cooldown timers
        self.lost_target_line_time = 0.0
        self.tracking_lost_time = 0.0 # RESET NEW TIMER
        self.spam_click_next_toggle_time = 0.0  # RESET SPAM CLICK TIMER

        # Ensure mouse is released if control ended abruptly
        if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
            pyautogui.mouseUp(button='left')
            self.is_holding_click = False

        # Reset auto cast timer to start a new sequence immediately
        self.auto_cast_next_action_time = time.perf_counter()
        self.last_rod_cast_time = 0.0  # Reset rod cast timer on state reset
        self.navigation_enter_next_time = 0.0  # Reset navigation enter timing
        # Reset navigation rod cast flag
        if hasattr(self, 'navigation_rod_cast_done'):
            delattr(self, 'navigation_rod_cast_done')

        # Update GUI to show IDLE status
        display_text = "Status: IDLE (AutoCast Enabled)" if self.auto_cast_enabled.get() else "Status: IDLE (AutoCast Disabled)"
        self.after(0, self.status_label.config, {'text': display_text, 'foreground': '#000080'})
        logging.info("Session end. Returning to IDLE scanning mode.")

    def _stop_automation(self, exit_clean=False):
        """
        Stops the background thread and releases the mouse click.
        """
        # Set flag to False to break the thread's while loop
        self.is_active = False
        self.state = "IDLE" # Ensure state is reset on stop
        self.initialization_stage = 0 # Ensure state is reset on stop
        self.lost_target_line_time = 0.0 # Reset cooldown timer
        self.tracking_lost_time = 0.0 # Reset new timer
        self.spam_click_next_toggle_time = 0.0  # Reset spam click timer
        self.last_rod_cast_time = 0.0 # Reset rod cast timer
        self.navigation_enter_next_time = 0.0 # Reset navigation enter timing
        
        # Reset navigation flag when stopping automation
        self.navigation_has_run_once = False
        # Reset navigation rod cast flag
        if hasattr(self, 'navigation_rod_cast_done'):
            delattr(self, 'navigation_rod_cast_done')

        if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
            pyautogui.mouseUp(button='left')
            self.is_holding_click = False
            logging.info("Mouse click RELEASED upon script stop.")

        # Wait for the thread to join/stop cleanly (up to 0.5 seconds)
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=0.5)

        # --- UPDATE LIVE FEED STOP LOGIC ---
        # Only close live feed if checkbox is unchecked - otherwise keep it visible
        if self.feedback_window and not self.show_live_feed.get():
            self.feedback_window.close()
            self.feedback_window = None
        # -----------------------------------

        # Update main status label
        self.status_label.config(text="Status: IDLE", foreground="#000080")
        logging.info("Automation stopped.")

    def _control_thread_run(self):
        """
        The heavy-duty control loop run in a separate thread.
        This handles CV, analysis, and clicking at the target FPS rate.
        """
        sct_thread_local = mss.mss() if SCREEN_CAPTURE_AVAILABLE else None

        while self.is_active:
            current_time = time.perf_counter()
            time_delta = current_time - self.last_time
            self.last_time = current_time

            try:
                # Primary logic to process screen and control mouse
                self._process_and_control(sct_thread_local, time_delta, current_time)

                # Auto-Cast logic runs only if in IDLE state AND the feature is enabled
                if self.state == "IDLE" and self.auto_cast_enabled.get(): # CHECK FOR TOGGLE STATE
                    # Use completely separate logic based on shake mode
                    if self.shake_mode_var.get() == "Click":
                        self._click_mode_logic(current_time)
                    elif self.shake_mode_var.get() == "Navigation":
                        self._navigation_mode_autocast_logic(current_time)
                    
                # Navigation mode logic (runs in specific states and only in Navigation mode)
                if self.state in ["NAVIGATION", "RECAST_WAIT"] and self.shake_mode_var.get() == "Navigation":
                    self._navigation_mode_logic(current_time)
                    
                # Auto Shake logic (runs in IDLE regardless of AutoCast, but ONLY in Click mode)
                if self.state == "IDLE" and self.shake_mode_var.get() == "Click":
                    self._idle_auto_shake(sct_thread_local, current_time)
                elif self.state == "IDLE" and self.shake_mode_var.get() == "Navigation":
                    # In Navigation mode, auto-shake is completely disabled
                    logging.debug("CONTROL_THREAD: Auto-shake disabled for Navigation mode in IDLE state")
                    pass  # Auto-shake disabled for Navigation mode

            except Exception as e:
                # Catch *any* exception inside the loop to prevent thread termination
                logging.critical(f"CRITICAL ERROR in control thread: {e}", exc_info=True)
                self.after(0, self.status_label.config, {'text': "Status: CRITICAL ERROR", 'foreground': '#CC0000'})
                self._stop_automation() # Stop on error
                break

            # Calculate sleep time to match the target FPS
            elapsed_time = time.perf_counter() - current_time
            delay_s = self._get_control_delay_s()
            sleep_time = delay_s - elapsed_time

            if sleep_time > 0:
                time.sleep(sleep_time)

    # ----------------------------------

    def _click_mode_logic(self, current_time):
        """
        Handles Click Mode: Simple cycle of cast → scan for target line → fish → repeat
        This is the original auto-cast logic for Click mode only.
        """
        # Note: A check for self.auto_cast_enabled is done in the calling function (_control_thread_run)
        if not MOUSE_CONTROL_AVAILABLE:
            return
            
        # SAFETY CHECK: This function should only run in IDLE state
        if self.state != "IDLE":
            logging.warning(f"CLICK_MODE DEBUG: click_mode_logic called but state is {self.state}, not IDLE. Skipping.")
            return

        try:
            hold_time = float(self.autocast_hold_time_var.get())
            wait_time = float(self.autocast_wait_time_var.get())
        except ValueError:
            logging.warning("Invalid auto-cast time values, using defaults.")
            hold_time, wait_time = 0.5, 2.5

        # 1) Auto zoom check (if enabled)
        if self.auto_zoom_in_enabled.get():
            # Auto zoom logic here (if implemented)
            pass

        # Rate-limited debug logging (only log every 5 seconds to avoid spam)
        if not hasattr(self, '_last_click_mode_debug_time'):
            self._last_click_mode_debug_time = 0
        
        if current_time - self._last_click_mode_debug_time >= 5.0:
            logging.info(f"CLICK_MODE DEBUG: Current state=IDLE, using Click mode flow")
            self._last_click_mode_debug_time = current_time
        
        # Click mode: Simple cast rod cycle
        # Check if it's time for the next action
        if current_time >= self.auto_cast_next_action_time:

            if not self.is_holding_click:
                # Action: Perform rod refresh sequence (if enabled) then HOLD LEFT CLICK (Cast)
                if self.refresh_rod_enabled.get():
                    self._perform_rod_refresh_sequence()
                
                pyautogui.mouseDown(button='left')
                self.is_holding_click = True
                self.last_rod_cast_time = current_time  # Track when rod was cast
                self.auto_cast_next_action_time = current_time + hold_time
                refresh_status = " (with rod refresh)" if self.refresh_rod_enabled.get() else ""
                logging.info(f"CLICK_MODE: HOLD ({hold_time}s){refresh_status}")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode: HOLD)", 'foreground': '#CC6600'})

            else:
                # Action: RELEASE LEFT CLICK
                pyautogui.mouseUp(button='left')
                self.is_holding_click = False
                self.auto_cast_next_action_time = current_time + wait_time
                logging.info(f"CLICK_MODE: RELEASE ({wait_time}s wait) - rod cast time recorded")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode: WAIT {wait_time}s)", 'foreground': '#000080'})
                
        # SAFETY AUTO-RECAST: Ensure we always recast after a maximum timeout (Click mode only)
        if self.last_rod_cast_time > 0 and self.state == "IDLE":
            max_wait_time = wait_time + 10.0  # Add 10 second safety buffer
            time_since_cast = current_time - self.last_rod_cast_time
            
            if time_since_cast >= max_wait_time:
                logging.warning(f"CLICK_MODE SAFETY AUTO-RECAST: {time_since_cast:.1f}s since last cast (max {max_wait_time:.1f}s), forcing recast in IDLE state")
                self.auto_cast_next_action_time = 0.0  # Force immediate recast
                self.last_rod_cast_time = 0.0  # Reset timer
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode Safety Auto-Recast)", 'foreground': '#CC6600'})

    def _perform_rod_refresh_sequence(self):
        """
        Perform the rod refresh sequence: press 2, wait, press 1, wait
        """
        try:
            import time
            from pynput import keyboard
            
            # Create keyboard controller
            kb = keyboard.Controller()
            
            # Get refresh rod delay
            try:
                refresh_delay = float(self.refresh_rod_delay_var.get())
            except ValueError:
                refresh_delay = 0.2  # Default 200ms
            
            logging.info(f"Rod Refresh: Starting sequence with {refresh_delay}s delays")
            
            # Press 2
            logging.info("Rod Refresh: Pressing key '2'")
            kb.press('2')
            time.sleep(0.05)  # Short press duration
            kb.release('2')
            
            # Wait configurable delay
            time.sleep(refresh_delay)
            
            # Press 1
            logging.info("Rod Refresh: Pressing key '1'")
            kb.press('1')
            time.sleep(0.05)  # Short press duration
            kb.release('1')
            
            # Wait configurable delay before casting
            time.sleep(refresh_delay)
            
            logging.info("Rod Refresh: Sequence completed")
            
        except Exception as e:
            logging.error(f"Error performing rod refresh sequence: {e}")

    def _navigation_mode_autocast_logic(self, current_time):
        """
        Handles Navigation Mode auto-cast in IDLE state:
        - First run: Transition to NAVIGATION state for setup
        - Subsequent runs: Cast rod and go to RECAST_WAIT
        """
        if not MOUSE_CONTROL_AVAILABLE:
            return
            
        # SAFETY CHECK: This function should only run in IDLE state
        if self.state != "IDLE":
            logging.warning(f"NAV_MODE DEBUG: navigation_mode_autocast_logic called but state is {self.state}, not IDLE. Skipping.")
            return

        try:
            hold_time = float(self.autocast_hold_time_var.get())
            wait_time = float(self.autocast_wait_time_var.get())
        except ValueError:
            logging.warning("Invalid auto-cast time values, using defaults.")
            hold_time, wait_time = 0.5, 2.5

        logging.info(f"NAV_MODE DEBUG: Current state=IDLE, using Navigation mode flow")
        
        # Check if navigation setup has been done
        if not self.navigation_has_run_once:
            # First run: Go to NAVIGATION state for setup
            logging.info("NAV_MODE: First run - transitioning to NAVIGATION state for setup")
            self.state = "NAVIGATION"
            self.after(0, self.status_label.config, {'text': f"Status: NAVIGATION (Setting up)", 'foreground': '#8B008B'})
            return
            
        # Navigation setup done, now cast rod and go to RECAST_WAIT
        if current_time >= self.auto_cast_next_action_time:
            if not self.is_holding_click:
                # Action: HOLD LEFT CLICK (Cast rod)
                logging.info(f"NAV_MODE: About to HOLD mouse for rod cast")
                pyautogui.mouseDown(button='left')
                self.is_holding_click = True
                self.last_rod_cast_time = current_time  # Track when rod was cast
                self.auto_cast_next_action_time = current_time + hold_time
                logging.info(f"NAV_MODE: HOLDING rod cast for {hold_time}s")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (NavMode: Casting rod)", 'foreground': '#CC6600'})
            else:
                # Action: RELEASE LEFT CLICK and transition to RECAST_WAIT
                logging.info(f"NAV_MODE: About to RELEASE mouse for rod cast completion")
                pyautogui.mouseUp(button='left')
                self.is_holding_click = False
                self.state = "RECAST_WAIT"
                self.navigation_recast_start_time = current_time
                logging.info("NAV_MODE: Rod cast complete (mouse released) -> RECAST_WAIT (scanning for white pixels)")
                self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Scanning for 0xFFFFFF)", 'foreground': '#008B8B'})

    def _navigation_mode_logic(self, current_time):
        """
        Handles the navigation mode logic for states NAVIGATION and RECAST_WAIT.
        """
        if not SCREEN_CAPTURE_AVAILABLE or not CV_AVAILABLE:
            logging.warning("Navigation mode logic skipped: Screen capture or CV not available")
            return
            
        logging.info(f"NAVIGATION_MODE_LOGIC DEBUG: Current state={self.state}")
            
        if self.state == "NAVIGATION":
            # 3) Navigation mode: immediately send navigation key, up/right arrows, and enter
            # (runs once per restart)
            logging.info("NAVIGATION_MODE_LOGIC DEBUG: In NAVIGATION state, calling _perform_immediate_navigation")
            self._perform_immediate_navigation(current_time)
            
        elif self.state == "RECAST_WAIT":
            # 4) After rod cast, check for white pixel in red area, if found, spam enter with delay configurable 
            # in advanced tuning GUI, while also searching for target line pixel, if no white pixel found, 
            # and no target line pixel found, FOR configurable delay (Navigation Recast Delay), then recast.
            logging.info("NAVIGATION_MODE_LOGIC DEBUG: In RECAST_WAIT state, calling _handle_recast_wait_logic")
            self._handle_recast_wait_logic(current_time)

    def _perform_immediate_navigation(self, current_time):
        """
        Immediately perform navigation sequence without any checks.
        For convenience, the bottom middle check has been removed.
        """
        try:
            # Directly perform navigation sequence
            logging.info("Navigation: Performing navigation sequence immediately")
            self._perform_navigation_sequence()
            # Transition to RECAST_WAIT state
            self.state = "RECAST_WAIT"
            self.navigation_recast_start_time = current_time
            self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Navigation complete)", 'foreground': '#008B8B'})
                    
        except Exception as e:
            logging.error(f"Error in navigation: {e}")
            # Fallback to RECAST_WAIT if there's an error
            self.state = "RECAST_WAIT"
            self.navigation_recast_start_time = current_time

    def _perform_navigation_sequence(self):
        """
        Perform the navigation key sequence: navigation key ONCE only.
        """
        if not MOUSE_CONTROL_AVAILABLE:
            logging.warning("Navigation sequence skipped: Mouse control not available")
            return
            
        try:
            import time
            from pynput.keyboard import Key
            from pynput import keyboard
            
            # Create keyboard controller (using pynput - the method that works with Roblox!)
            kb = keyboard.Controller()
            
            # Get navigation key
            nav_key = self.shake_navigation_key_var.get()
            
            logging.info(f"Navigation: Starting simplified navigation sequence - navigation key only")
            
            # Add a pause before starting to ensure game is ready
            time.sleep(0.2)
            
            # Send navigation key ONCE (using pynput)
            logging.info(f"Navigation: About to press navigation key '{nav_key}' with pynput")
            kb.press(nav_key)
            time.sleep(0.1)
            kb.release(nav_key)
            logging.info(f"Navigation: Pressed navigation key '{nav_key}' (pynput)")
            time.sleep(0.3)
            
            logging.info("Navigation: Completed navigation sequence")
                    
        except Exception as e:
            logging.error(f"Error performing navigation sequence: {e}")

    def _handle_recast_wait_logic(self, current_time):
        """
        Handle the RECAST_WAIT state logic: check for white pixel in red area (fish area),
        if found spam enter while searching for target line, if not found within delay, recast.
        """
        try:
            import time  # For human-like key timing
            logging.info(f"RECAST_WAIT DEBUG: Checking red area for white pixels")
            
            # Get the area to scan - in navigation mode, use SHAKE area, in click mode use FISH area
            if self.shake_mode_var.get() == "Navigation":
                # Navigation mode: scan SHAKE area for white pixels
                geom = self.shake_geometry.get()
                area_name = "shake"
                logging.info(f"RECAST_WAIT DEBUG: Using SHAKE area for white pixel detection in Navigation mode")
            else:
                # Click mode: scan FISH area for white pixels  
                geom = self.fish_geometry.get()
                area_name = "fish"
                logging.info(f"RECAST_WAIT DEBUG: Using FISH area for white pixel detection in Click mode")
            
            size_str, pos_str = geom.split('+', 1)
            fw, fh = map(int, size_str.split('x'))
            fx, fy = map(int, pos_str.split('+'))
            
            logging.info(f"RECAST_WAIT DEBUG: {area_name.capitalize()} area geometry - {fw}x{fh} at ({fx},{fy})")
            
            # Capture the fish area
            import mss
            with mss.mss() as sct:
                monitor = {"top": fy, "left": fx, "width": fw, "height": fh}
                sct_img = sct.grab(monitor)
                
                from PIL import Image
                pil_img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                cv_img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
                # Check for white pixels in the fish area
                lower_white = np.array([250, 250, 250], dtype=np.uint8)  # Allow slight tolerance
                upper_white = np.array([255, 255, 255], dtype=np.uint8)
                white_mask = cv2.inRange(cv_img_bgr, lower_white, upper_white)
                white_pixels = np.sum(white_mask > 0)
                
                # Also check for target line in the fish area
                rod_type = self.rod_type_var.get()
                rod_colors = get_rod_colors(rod_type, self.loaded_config)
                
                target_pixels = 0
                if rod_colors["target_line"] is not None:
                    target_line_bgr = hex_to_bgr(rod_colors["target_line"])
                    try:
                        target_line_tol = int(self.target_line_tolerance_var.get())
                    except ValueError:
                        target_line_tol = 2
                    lower_target, upper_target = _get_bgr_bounds(target_line_bgr, target_line_tol)
                    target_mask = cv2.inRange(cv_img_bgr, lower_target, upper_target)
                    target_pixels = np.sum(target_mask > 0)
                
                logging.info(f"RECAST_WAIT DEBUG: Found {white_pixels} white pixels, {target_pixels} target pixels")
                
                # Add detailed color debugging - sample pixels to see what colors are actually there
                if white_pixels == 0:
                    # Sample some pixels to see what colors we're actually getting
                    sample_pixels = []
                    for y in range(0, fh, max(1, fh//3)):  # Sample 3 rows
                        for x in range(0, fw, max(1, fw//5)):  # Sample 5 columns per row
                            if y < cv_img_bgr.shape[0] and x < cv_img_bgr.shape[1]:
                                pixel_bgr = cv_img_bgr[y, x]
                                pixel_rgb = (int(pixel_bgr[2]), int(pixel_bgr[1]), int(pixel_bgr[0]))  # BGR to RGB
                                sample_pixels.append(f"({x},{y}):{pixel_rgb}")
                    
                    if len(sample_pixels) > 0:
                        sample_str = " | ".join(sample_pixels[:8])  # Show first 8 samples
                        logging.info(f"RECAST_WAIT DEBUG: Sample pixel colors: {sample_str}")
                
                # Check for exact white pixels (255,255,255)
                exact_white_mask = cv2.inRange(cv_img_bgr, (255, 255, 255), (255, 255, 255))
                exact_white_pixels = np.sum(exact_white_mask > 0)
                if exact_white_pixels != white_pixels:
                    logging.info(f"RECAST_WAIT DEBUG: Exact white (255,255,255): {exact_white_pixels}, Tolerance white (250-255): {white_pixels}")
                
                # Check if we're scanning the wrong area - compare with shake area
                shake_geom = self.shake_geometry.get()
                logging.info(f"RECAST_WAIT DEBUG: Note - Shake area is: {shake_geom}, Fish area is: {geom}")
                
                if white_pixels > 5:  # Found white pixel in red area
                    # NAVIGATION MODE: ONLY SPAM ENTER - NEVER CLICK ON WHITE PIXELS
                    # This is the correct behavior for navigation mode
                    # Spam enter with configurable delay while checking for target line
                    if current_time >= self.navigation_enter_next_time:
                        if MOUSE_CONTROL_AVAILABLE:
                            # pynput enter press (Roblox-compatible method)
                            try:
                                from pynput.keyboard import Key
                                from pynput import keyboard
                                kb = keyboard.Controller()
                                
                                kb.press(Key.enter)
                                time.sleep(0.05)
                                kb.release(Key.enter)
                                
                                try:
                                    enter_delay = float(self.enter_spam_delay_var.get())
                                except ValueError:
                                    enter_delay = 0.1
                                self.navigation_enter_next_time = current_time + enter_delay
                                logging.info("RECAST_WAIT: Spamming enter (white pixel found) - pynput - NO CLICKING")
                            except ImportError:
                                logging.error("RECAST_WAIT: pynput not available, enter spam failed")
                        else:
                            logging.warning("Enter spam skipped: Mouse control not available")
                    
                    # Check if target line found - if so, transition to FISHING
                    if target_pixels > 10:
                        conditional_logger.info("RECAST_WAIT: Target line found, transitioning to FISHING")
                        self.state = "FISHING"
                        self.last_rod_cast_time = 0.0  # Reset rod cast timer since we're fishing
                        self._reset_movement_tracking()  # Reset intelligent search system
                        self.notify_fishing_loop()  # Send Discord notification for fishing loop
                        self.after(0, self.status_label.config, {'text': f"Status: FISHING (Target line detected)", 'foreground': '#006600'})
                        return
                        
                    # CRITICAL: Reset the recast timer while white pixels are present
                    # This prevents automatic recasting while fish is hooked
                    self.navigation_recast_start_time = current_time
                    self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Spamming Enter)", 'foreground': '#B8860B'})
                    return # Exit early to prevent recast timeout check
                    
                else:
                    # No white pixel found, check recast delay
                    try:
                        recast_delay = float(self.navigation_recast_delay_var.get())
                    except ValueError:
                        recast_delay = 1.0
                        
                    elapsed_time = current_time - self.navigation_recast_start_time
                    
                    logging.info(f"RECAST_WAIT DEBUG: No white pixels found, elapsed={elapsed_time:.2f}s, delay={recast_delay}s")
                    
                    if elapsed_time >= recast_delay:
                        # Recast delay exceeded, return to IDLE for recast
                        conditional_logger.info("RECAST_WAIT: Recast delay exceeded, returning to IDLE")
                        self.state = "IDLE"
                        self.auto_cast_next_action_time = 0.0  # Immediate recast
                        self.last_rod_cast_time = 0.0  # Reset rod cast timer to allow immediate recast
                        # Reset navigation rod cast flag so it can cast again
                        if hasattr(self, 'navigation_rod_cast_done'):
                            delattr(self, 'navigation_rod_cast_done')
                            logging.info("RECAST_WAIT: Reset navigation_rod_cast_done flag for new cast cycle")
                        self.after(0, self.status_label.config, {'text': f"Status: IDLE (Recasting)", 'foreground': '#000080'})
                    else:
                        # Still waiting
                        remaining_time = recast_delay - elapsed_time
                        self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (No white pixel, {remaining_time:.1f}s remaining)", 'foreground': 'cyan'})
                        
        except Exception as e:
            logging.error(f"Error in recast wait logic: {e}")
            # Fallback to IDLE if there's an error
            self.state = "IDLE"

    def _detect_shake_circles(self, cv_img_bgr):
        """Detect circular shapes (SHAKE button) in the shake area image - STRICT detection"""
        try:
            import cv2
            import numpy as np
            # Convert to grayscale
            gray = cv2.cvtColor(cv_img_bgr, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            # Get circle tolerance setting (inverted scale: higher tolerance = more forgiving)
            circle_tolerance = int(self.shake_circle_tolerance_var.get())
            param2_value = 100 - circle_tolerance  # Invert scale so higher tolerance = lower param2
            # Use HoughCircles with parameters matching the working version
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=80,
                param1=100,
                param2=param2_value,
                minRadius=50,
                maxRadius=120
            )
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                good_circles = []
                for (x, y, r) in circles:
                    if 50 <= r <= 120:
                        good_circles.append((x, y, r))
                if good_circles:
                    largest_circle = max(good_circles, key=lambda c: c[2])
                    x, y, r = largest_circle
                    logging.info(f"AutoShake: Found STRICT circle at local ({x}, {y}) with radius {r}")
                    return x, y
            # Remove backup contour detection - too prone to false positives
            # Only use the strict HoughCircles detection
            return None, None
        except Exception as e:
            logging.error(f"Circle detection error: {e}")
            return None, None

    def _detect_shake_pixels(self, cv_img_bgr):
        """Detect white pixels (0xFFFFFF) in the shake area image - similar to AutoHotkey PixelSearch"""
        try:
            import cv2
            import numpy as np
            
            # Get pixel tolerance from shake settings (similar to AutoHotkey ColorTolerance)
            try:
                pixel_tolerance = int(self.shake_pixel_tolerance_var.get())
            except (ValueError, AttributeError):
                pixel_tolerance = 2  # Default tolerance
            
            # Convert 0xFFFFFF (white) to BGR format for OpenCV
            target_white_bgr = (255, 255, 255)  # BGR format
            
            # Create color range with tolerance
            lower_bound = np.array([max(0, 255 - pixel_tolerance), 
                                   max(0, 255 - pixel_tolerance), 
                                   max(0, 255 - pixel_tolerance)], dtype=np.uint8)
            upper_bound = np.array([255, 255, 255], dtype=np.uint8)
            
            # Create mask for white pixels within tolerance
            white_mask = cv2.inRange(cv_img_bgr, lower_bound, upper_bound)
            
            # Find white pixels
            white_coords = np.where(white_mask > 0)
            
            if len(white_coords[0]) > 0:
                # Get first white pixel found (similar to AutoHotkey PixelSearch behavior)
                y = white_coords[0][0]  # First row index
                x = white_coords[1][0]  # First column index
                
                logging.info(f"AutoShake: Found white pixel at local ({x}, {y}) with tolerance {pixel_tolerance}")
                return x, y
            
            return None, None
            
        except Exception as e:
            logging.error(f"Pixel detection error: {e}")
            return None, None

    def _idle_auto_shake(self, sct_instance, current_time):
        """When IDLE, scan the ShakeArea for near-white pixels and move to the first found (AHK-like)."""
        
        # CRITICAL SAFEGUARD: Never run auto-shake in Navigation mode to prevent clicking when white pixels found
        if self.shake_mode_var.get() == "Navigation":
            logging.debug("AUTO_SHAKE: Skipped - Navigation mode detected (no clicking allowed)")
            return
            
        # ADDITIONAL SAFEGUARD: Only run in IDLE state
        if self.state != "IDLE":
            logging.warning(f"AUTO_SHAKE: Skipped - Wrong state {self.state} (should only run in IDLE)")
            return
            
        global SCREEN_CAPTURE_AVAILABLE, CV_AVAILABLE, MOUSE_CONTROL_AVAILABLE
        try:
            enabled = self.auto_shake_enabled.get()
        except Exception:
            enabled = False
        if not (enabled and SCREEN_CAPTURE_AVAILABLE and CV_AVAILABLE and sct_instance and MOUSE_CONTROL_AVAILABLE):
            return
        # Respect action rate limit
        try:
            delay_ms = max(0, int(self.shake_delay_ms_var.get()))
        except Exception:
            delay_ms = 500
        
        # Allow user's desired speed - no artificial minimum for different circles
        # Duplicate detection will handle same-spot prevention
        
        if current_time < getattr(self, 'auto_shake_next_action_time', 0.0):
            return
        # Parse shake geometry
        geom = self.shake_geometry.get()
        try:
            size_str, pos_str = geom.split('+', 1)
            sw, sh = map(int, size_str.split('x'))
            sx, sy = map(int, pos_str.split('+'))
        except Exception:
            logging.error(f"Invalid shake geometry: {geom}")
            return
        if sw <= 0 or sh <= 0:
            return
        # Capture shake region
        try:
            monitor = {"top": sy, "left": sx, "width": sw, "height": sh}
            sct_img = sct_instance.grab(monitor)
            from PIL import Image
            pil_img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        except Exception as e:
            logging.error(f"AutoShake capture error: {e}")
            return
        try:
            import cv2
            cv_img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # Check click type to determine detection method
            click_type = self.shake_click_type_var.get()
            
            if click_type == "Circle":
                # Use circle detection (existing logic)
                col, row = self._detect_shake_circles(cv_img_bgr)
            elif click_type == "Pixel":
                # Use white pixel detection (new logic)
                col, row = self._detect_shake_pixels(cv_img_bgr)
            else:
                # Default to circle detection
                col, row = self._detect_shake_circles(cv_img_bgr)
            
            if col is None or row is None:
                # No targets found
                return
                
            # Calculate absolute screen coordinates (multi-monitor aware)
            click_x = sx + int(col)
            click_y = sy + int(row)
            
            # Debug multi-monitor coordinates
            logging.info(f"AutoShake Debug: ShakeArea at ({sx},{sy}) size {sw}x{sh}")
            logging.info(f"AutoShake Debug: Using {click_type} detection mode")
            logging.info(f"AutoShake Debug: Found target at local ({col},{row}) -> screen ({click_x},{click_y})")
            
            # Validate coordinates using the monitor helper
            monitor_helper.refresh_monitor_info()
            if not monitor_helper.validate_coordinates(click_x, click_y):
                logging.warning(f"AutoShake: Calculated coordinates ({click_x},{click_y}) are outside virtual desktop bounds!")
                # Try to clamp coordinates to safe bounds
                click_x, click_y = monitor_helper.clamp_coordinates(click_x, click_y)
                logging.info(f"AutoShake: Clamped coordinates to ({click_x},{click_y})")
            
            logging.info(f"AutoShake Debug: Virtual desktop bounds: left={monitor_helper.virtual_screen_left}, top={monitor_helper.virtual_screen_top}, width={monitor_helper.virtual_screen_width}, height={monitor_helper.virtual_screen_height}")
                
            # Enhanced memory logic to avoid immediate repeat spam at exact same pixel
            # NOTE: Duplicate detection disabled for Navigation mode (user request)
            should_click = True
            
            # Skip duplicate detection for Navigation mode as requested
            navigation_mode = self.shake_mode_var.get() == "Navigation"
            
            if not navigation_mode and self._shake_memory_xy is not None:
                lastx, lasty = self._shake_memory_xy
                # Calculate where mouse will ACTUALLY end up (target + 1px down for anti-Roblox movement)
                predicted_final_x = click_x
                predicted_final_y = click_y + 1
                
                # Tolerance based on detection method:
                # Circle detection: ±10 pixels (circles can have variations)
                # Pixel detection: ±1 pixel (should be exact pixel locations)
                click_type = self.shake_click_type_var.get()
                tolerance = 1 if click_type == "Pixel" else 10
                
                is_same_spot = abs(predicted_final_x - lastx) <= tolerance and abs(predicted_final_y - lasty) <= tolerance
                
                if is_same_spot:
                    # We're detecting the same spot again
                    if self._shake_same_spot_start_time is None:
                        # First time detecting this spot, record the time
                        self._shake_same_spot_start_time = current_time
                        should_click = False
                        logging.info(f"AutoShake: Same spot detected at ({click_x},{click_y}), starting duplicate timer")
                    else:
                        # Check if enough time has passed to override duplicate protection
                        try:
                            override_time_ms = max(0, int(self.shake_duplicate_override_var.get()))
                        except Exception:
                            override_time_ms = 1000  # Default 1000ms
                        
                        time_elapsed_ms = (current_time - self._shake_same_spot_start_time) * 1000
                        
                        if time_elapsed_ms >= override_time_ms:
                            # Enough time has passed, allow the click
                            should_click = True
                            logging.info(f"AutoShake: Override activated after {time_elapsed_ms:.0f}ms, clicking same spot at ({click_x},{click_y})")
                        else:
                            # Not enough time has passed, skip this click
                            should_click = False
                            remaining_ms = override_time_ms - time_elapsed_ms
                            logging.info(f"AutoShake: Skipping duplicate click at ({click_x},{click_y}), {remaining_ms:.0f}ms remaining until override")
                else:
                    # Different spot detected, reset the duplicate timer
                    self._shake_same_spot_start_time = None
                    self._shake_repeat_count = 0
            elif not navigation_mode:
                # No previous memory (and not navigation mode), reset the duplicate timer
                self._shake_same_spot_start_time = None
            
            # For navigation mode, always allow clicking (no duplicate detection)
            if navigation_mode:
                logging.info(f"AutoShake: Navigation mode - duplicate detection disabled, clicking at ({click_x},{click_y})")
                
            # Only proceed with clicking if we should click
            if not should_click:
                return
                
            # FINAL SAFETY CHECK: Double-check timing just before clicking to prevent race conditions
            if current_time < getattr(self, 'auto_shake_next_action_time', 0.0):
                logging.info(f"AutoShake: Race condition prevented - still in cooldown period")
                return
                
            # INSTANT TELEPORT + 1 pixel movement for Roblox compatibility
            try:
                import ctypes
                from ctypes import windll
                import time
                import pyautogui
                
                logging.info(f"AutoShake: Teleporting to ({click_x},{click_y}) then moving 1px down")
                
                # STEP 1: Teleport mouse directly to the circle position
                windll.user32.SetCursorPos(click_x, click_y)
                time.sleep(0.002)  # 2ms settling time after teleport
                
                # Verify teleport position
                teleport_x, teleport_y = pyautogui.position()
                logging.info(f"AutoShake: Teleported to ({teleport_x}, {teleport_y})")
                
                # STEP 2: Use anti-Roblox relative movement to move 1 pixel down
                MOUSEEVENTF_MOVE = 0x0001
                
                # Move 1 pixel down using relative movement (this makes Roblox register the click)
                windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                time.sleep(0.002)  # 2ms settling time after movement
                
                # Verify final position after relative movement
                final_x, final_y = pyautogui.position()
                logging.info(f"AutoShake: After anti-Roblox movement: ({final_x}, {final_y})")
                
                # STEP 3: Now click at current position (hardware cursor should be synced)
                MOUSEEVENTF_LEFTDOWN = 0x0002
                MOUSEEVENTF_LEFTUP = 0x0004
                
                # Get click count from settings
                try:
                    click_count = int(self.shake_click_count_var.get())
                except (ValueError, AttributeError):
                    click_count = 1  # Default to single click
                
                # Perform clicks based on count setting
                for click_num in range(click_count):
                    if click_num > 0:
                        # Add 1ms delay between clicks for double-click
                        time.sleep(0.001)
                        logging.info(f"AutoShake: Click {click_num + 1} of {click_count}")
                    
                    # Send mouse down event (hardware level)
                    windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    
                    # Brief hold time (like human click)
                    time.sleep(0.015)  # 15ms hold time
                    
                    # Send mouse up event (hardware level)
                    windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                
                click_type_desc = "double-click" if click_count == 2 else "single click"
                logging.info(f"AutoShake: Instant teleport + {click_type_desc} complete at ({final_x}, {final_y})")
                
                # Update memory with ACTUAL final position (including the +1px movement)
                # This prevents race conditions and ensures duplicate detection works correctly
                self._shake_memory_xy = (final_x, final_y)
                self.auto_shake_next_action_time = current_time + (delay_ms / 1000.0)
                # Briefly pause AutoCast to avoid overlap
                self.auto_cast_next_action_time = max(self.auto_cast_next_action_time, current_time + 1.0)
                logging.info(f"AutoShake: Physical mouse movement + click at ({click_x},{click_y}) delay={delay_ms}ms")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (AutoShake Physical)", 'foreground': 'magenta'})
            except Exception as e:
                logging.error(f"AutoShake physical movement failed: {e}")
                # Fallback to pyautogui
                try:
                    import pyautogui
                    # Get click count for fallback too
                    try:
                        click_count = int(self.shake_click_count_var.get())
                    except (ValueError, AttributeError):
                        click_count = 1
                    
                    # Perform clicks with pyautogui
                    for click_num in range(click_count):
                        if click_num > 0:
                            time.sleep(0.001)  # 1ms delay between clicks
                        pyautogui.click(x=click_x, y=click_y)
                    
                    click_type_desc = "double-click" if click_count == 2 else "single click"
                    logging.info(f"AutoShake: Fallback pyautogui {click_type_desc} at ({click_x},{click_y})")
                except Exception as e2:
                    logging.error(f"AutoShake click completely failed: {e2}")
                try:
                    import pyautogui
                    pyautogui.moveTo(x=click_x, y=click_y)
                    logging.info(f"AutoShake: Fallback pyautogui to ({click_x},{click_y})")
                except Exception as e2:
                    logging.error(f"AutoShake move completely failed: {e2}")
        except Exception as e:
            logging.error(f"AutoShake processing error: {e}")
            return

    def _find_avg_x_position(self, mask):
        """Finds the average horizontal position of non-zero pixels in a mask."""
        y_coords, x_coords = np.where(mask > 0)
        return np.mean(x_coords) if len(x_coords) > 0 else None

    def _count_pixels(self, mask):
        """Counts the number of non-zero pixels in a mask."""
        return np.sum(mask > 0)

    def _find_indicator_centroids(self, mask):
        """
        Finds the centroid of the single largest contour (arrow tip) in the indicator mask.
        Returns the X coordinate or None.
        """
        try:
            min_area = int(self.min_contour_area_var.get())
        except (ValueError, AttributeError):
            min_area = 5

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest_contour) < min_area:
            return None

        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            return cX

        return None

    def _update_box_estimation(self, indicator_centroid_x, width):
        """
        Implements the 'Size-Swap-Anchor' logic with arrow offset compensation.
        """

        # Determine if the holding state has just changed (a 'swap' event)
        holding_swapped = (self.is_holding_click != self.last_holding_state)

        # --- PHASE 1: Handle Missing Indicator / Box Reset ---
        if indicator_centroid_x is None:
            # We ONLY reset last_indicator_x, but keep last_left_x/right_x for the drawing simulation
            # Box Center will be None, which handles control failure.
            self.box_center_x = None
            self.last_indicator_x = None
            self.last_holding_state = self.is_holding_click
            return

        # --- PHASE 2: State Swap (Calculate Box Size with Offset Compensation) ---
        if holding_swapped and self.last_indicator_x is not None:

            # This block is used both in initialization and after.
            if self.has_calculated_length_once:
                # Normal Operation: Calculate length accounting for arrow offset
                
                # Get compensated box estimates for both arrow positions
                last_left_est, last_right_est = self._get_compensated_arrow_box_estimate(self.last_indicator_x, width)
                curr_left_est, curr_right_est = self._get_compensated_arrow_box_estimate(indicator_centroid_x, width)
                
                if last_left_est is not None and curr_left_est is not None:
                    if not self.is_holding_click:
                        # Swapped to RELEASE: Current arrow should be near left, last arrow was near right
                        new_length = abs(last_right_est - curr_left_est)
                        if 10 < new_length < width:
                            self.estimated_box_length = new_length
                            logging.info(f"Arrow Fallback: Box size re-measured at {new_length:.1f}px (Hold->Release swap, offset compensated).")
                        
                        # Set compensated anchor points
                        self.last_left_x = curr_left_est
                        self.last_right_x = curr_left_est + self.estimated_box_length

                    else: # self.is_holding_click is True: Swapped to HOLDING (Indicator now on RIGHT edge). Last indicator was LEFT edge.
                        # Swapped to HOLD: Current arrow should be near right, last arrow was near left
                        new_length = abs(curr_right_est - last_left_est)
                        if 10 < new_length < width:
                            self.estimated_box_length = new_length
                            logging.info(f"Arrow Fallback: Box size re-measured at {new_length:.1f}px (Release->Hold swap, offset compensated).")
                        
                        # Set compensated anchor points
                        self.last_right_x = curr_right_est
                        self.last_left_x = curr_right_est - self.estimated_box_length

        # --- PHASE 3: No State Swap (Move Fixed-Size Box with Offset Compensation) ---
        elif self.has_calculated_length_once:

            # The box keeps its fixed self.estimated_box_length and moves with the current anchor
            # Use compensated arrow position estimates
            left_est, right_est = self._get_compensated_arrow_box_estimate(indicator_centroid_x, width)
            
            if left_est is not None and right_est is not None:
                if not self.is_holding_click:
                    # Indicator is on the LEFT side. Use left estimate as anchor.
                    self.last_left_x = left_est
                    self.last_right_x = self.last_left_x + self.estimated_box_length
                else: # self.is_holding_click is True
                    # Indicator is on the RIGHT side. Use right estimate as anchor.
                    self.last_right_x = right_est
                    self.last_left_x = self.last_right_x - self.estimated_box_length

        # --- PHASE 4: Final Update
        if self.last_left_x is not None and self.last_right_x is not None:
            # Recalculate Center X for control logic
            self.box_center_x = (self.last_left_x + self.last_right_x) / 2.0

            # Clamp to prevent floating outside the capture area
            self.last_left_x = max(0.0, self.last_left_x)
            self.last_right_x = min(float(width), self.last_right_x)
            # Recalculate center after clamping
            self.box_center_x = (self.last_left_x + self.last_right_x) / 2.0
            
            # Update movement tracking for intelligent search system
            try:
                self._update_movement_tracking(self.box_center_x)
            except Exception:
                pass  # Silent fail to prevent spam
            
            # Force immediate overlay update for responsive visual feedback
            if hasattr(self, 'live_feed_window') and self.live_feed_window:
                try:
                    self.live_feed_window.force_overlay_update()
                except Exception:
                    pass  # Silent fail to prevent spam

        # Update last known states for the next loop
        self.last_indicator_x = indicator_centroid_x
        self.last_holding_state = self.is_holding_click

    def _process_and_control(self, sct_instance, time_delta, current_time):
        """
        The control loop executed by the background thread. Handles screen capture,
        CV processing, tracking, initialization, and control based on the STATE MACHINE.
        """
        global SCREEN_CAPTURE_AVAILABLE, CV_AVAILABLE, MOUSE_CONTROL_AVAILABLE

        # --- FIX: Initialize status_color_mode HERE to prevent UnboundLocalError ---
        status_color_mode = "N/A (State Inactive/Transition)"
        status_suffix = "" # Initialize suffix for consistency

        # 1. Parse capture area geometry
        geom = self.fish_geometry.get()
        try:
            size_str, pos_str = geom.split('+', 1)
            width, height = map(int, size_str.split('x'))
            x, y = map(int, pos_str.split('+'))
        except ValueError:
            logging.error(f"Invalid fish geometry: {geom}")
            return

        # 2. Screen Capture and CV Check
        if not (SCREEN_CAPTURE_AVAILABLE and CV_AVAILABLE and width > 0 and height > 0 and sct_instance):
            self.after(0, self.status_label.config, {'text': f"Status: {self.state} (CV/Capture Unavailable)", 'foreground': 'red'})
            return

        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct_instance.grab(monitor)
        pil_img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        cv_img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


        # Get rod-specific colors and tolerances
        rod_type = self.rod_type_var.get()
        rod_colors = get_rod_colors(rod_type, self.loaded_config)
        
        # Use rod-specific tolerances
        target_line_tol = rod_colors.get("target_line_tolerance", 2)
        indicator_arrow_tol = rod_colors.get("indicator_arrow_tolerance", 3)
        box_color_tol = rod_colors.get("box_color_tolerance", 1)

        # Get other tuning parameters safely
        try:
            idle_threshold = int(self.target_line_idle_pixel_threshold_var.get())
            KP = float(self.kp_var.get())
            KD = float(self.kd_var.get())
            target_tol_px = float(self.target_tolerance_pixels_var.get())
            boundary_factor = float(self.boundary_margin_factor_var.get())
            pd_clamp = float(self.pd_clamp_var.get())
        except (ValueError, AttributeError):
            logging.error("Invalid non-numeric value in tuning parameters. Using defaults for this frame.")
            idle_threshold = 50
            KP, KD, target_tol_px, boundary_factor, pd_clamp = 0.5, 10.0, 2.0, 0.6, 50.0

        # 3. Color Detection (Using Rod-Specific Tolerances)

        # Initialize masks and counts to zero
        target_line_mask = np.zeros((height, width), dtype=np.uint8)
        target_line_pixel_count = 0
        target_line_x = None
        
        indicator_arrow_mask = np.zeros((height, width), dtype=np.uint8)
        indicator_pixel_count = 0
        indicator_centroid_x = None
        
        combined_box_mask = np.zeros((height, width), dtype=np.uint8)
        box_pixel_count = 0

        # Only perform color detection if rod type has colors configured
        if rod_colors["target_line"] is not None:
            # Target Line Color (Primary)
            color1_bgr = hex_to_bgr(rod_colors["target_line"])
            lower1, upper1 = _get_bgr_bounds(color1_bgr, target_line_tol)
            mask_primary = cv2.inRange(cv_img_bgr, lower1, upper1)
            target_line_mask = cv2.bitwise_or(target_line_mask, mask_primary)

        # Calculate target line stats if any mask was created
        if rod_colors["target_line"] is not None:
            target_line_pixel_count = self._count_pixels(target_line_mask)
            target_line_x = self._find_avg_x_position(target_line_mask)

        # Indicator Arrow Color (For Fallback/Initialization)
        if rod_colors["indicator_arrow"] is not None:
            color2_bgr = hex_to_bgr(rod_colors["indicator_arrow"])
            lower2, upper2 = _get_bgr_bounds(color2_bgr, indicator_arrow_tol)
            indicator_arrow_mask = cv2.inRange(cv_img_bgr, lower2, upper2)
            indicator_pixel_count = self._count_pixels(indicator_arrow_mask)
            indicator_centroid_x = self._find_indicator_centroids(indicator_arrow_mask)

        # Box Color Detection (For Direct Tracking)
        if rod_colors["box_color_1"] is not None:
            color3_bgr = hex_to_bgr(rod_colors["box_color_1"])
            lower3, upper3 = _get_bgr_bounds(color3_bgr, box_color_tol)
            box_mask_1 = cv2.inRange(cv_img_bgr, lower3, upper3)
            combined_box_mask = cv2.bitwise_or(combined_box_mask, box_mask_1)

        if rod_colors["box_color_2"] is not None:
            color4_bgr = hex_to_bgr(rod_colors["box_color_2"])
            lower4, upper4 = _get_bgr_bounds(color4_bgr, box_color_tol)
            box_mask_2 = cv2.inRange(cv_img_bgr, lower4, upper4)
            combined_box_mask = cv2.bitwise_or(combined_box_mask, box_mask_2)

        # Additional box colors for rods like Duskwire
        for i in range(3, 7):  # box_color_3 through box_color_6
            color_key = f"box_color_{i}"
            if rod_colors.get(color_key) is not None:
                color_bgr = hex_to_bgr(rod_colors[color_key])
                lower_bound, upper_bound = _get_bgr_bounds(color_bgr, box_color_tol)
                box_mask = cv2.inRange(cv_img_bgr, lower_bound, upper_bound)
                combined_box_mask = cv2.bitwise_or(combined_box_mask, box_mask)

        # Calculate box stats if any mask was created
        box_y_coords = np.array([])
        box_x_coords = np.array([])
        has_box_colors = (rod_colors["box_color_1"] is not None or 
                         rod_colors["box_color_2"] is not None or
                         any(rod_colors.get(f"box_color_{i}") is not None for i in range(3, 7)))
        if has_box_colors:
            box_y_coords, box_x_coords = np.where(combined_box_mask > 0)
            box_pixel_count = len(box_x_coords)

        # 4. State Machine Logic

        if self.state == "IDLE":
            # Reset tracking variables
            self.last_left_x = None; self.last_right_x = None; self.box_center_x = None

            # Transition to FISHING if Target Line (blob) AND Fishing Bar Color (pixels) are found
            if (target_line_pixel_count >= idle_threshold) and (box_pixel_count > 100):

                self.state = "FISHING"
                conditional_logger.info(f"IDLE -> FISHING. Target line and box color found.")
                self.notify_fishing_loop()  # Send Discord notification for fishing loop

                # Initialize fast response system
                self.last_target_line_x = target_line_x
                self.last_mouse_action_time = current_time
                
                # Start new adaptive PID session
                self._start_new_adaptive_session()
                
                # Reset intelligent search system for new fishing session
                self._reset_movement_tracking()
                
                # Initialize predictive velocity tracking system
                self._reset_velocity_tracking()
                
                # Initialize adaptive tuning system
                self._reset_adaptive_tuning()
                
                # Initialize arrow offset calibration
                self._reset_arrow_offset_calibration()

                # Ensure mouse is released before starting fishing control
                if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                    pyautogui.mouseUp(button='left')
                    self.is_holding_click = False

                # Calculate initial length using the detected box for best starting estimate
                if len(box_x_coords) > 0:
                    actual_box_left_x = np.min(box_x_coords)
                    actual_box_right_x = np.max(box_x_coords)
                    new_length = actual_box_right_x - actual_box_left_x
                    if 10 < new_length < width:
                        self.estimated_box_length = new_length
                        self.has_calculated_length_once = True
                        logging.info(f"Initial Box Length calculated: {new_length:.1f}px.")

                self.after(0, self.status_label.config, {'text': f"Status: {self.state} (Control Active)", 'foreground': 'green'})
                # FALL THROUGH to FISHING state logic below

            else:
                # If we are IDLE, the auto_cast_logic handles the GUI update if enabled
                # If AutoCast is disabled, we need to update the status here.
                if not self.auto_cast_enabled.get():
                    self.after(0, self.status_label.config, {'text': f"Status: {self.state} (AutoCast Disabled)", 'foreground': 'blue'})
                return

        elif self.state in ["NAVIGATION", "RECAST_WAIT"]:
            # For NAVIGATION and RECAST_WAIT states, check if we should transition to FISHING
            if (target_line_pixel_count >= idle_threshold) and (box_pixel_count > 100):
                prev_state = self.state
                self.state = "FISHING"
                conditional_logger.info(f"{prev_state} -> FISHING. Target line and box color found.")
                self.notify_fishing_loop()  # Send Discord notification for fishing loop

                # Initialize fast response system
                self.last_target_line_x = target_line_x
                self.last_mouse_action_time = current_time
                
                # Reset intelligent search system for new fishing session
                self._reset_movement_tracking()
                
                # Initialize predictive velocity tracking system
                self._reset_velocity_tracking()
                
                # Initialize adaptive tuning system
                self._reset_adaptive_tuning()
                
                # Initialize arrow offset calibration
                self._reset_arrow_offset_calibration()

                # Ensure mouse is released before starting fishing control
                if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                    pyautogui.mouseUp(button='left')
                    self.is_holding_click = False

                # Calculate initial length using the detected box for best starting estimate
                if len(box_x_coords) > 0:
                    actual_box_left_x = np.min(box_x_coords)
                    actual_box_right_x = np.max(box_x_coords)
                    new_length = actual_box_right_x - actual_box_left_x
                    if 10 < new_length < width:
                        self.estimated_box_length = new_length
                        self.has_calculated_length_once = True
                        logging.info(f"Initial Box Length calculated: {new_length:.1f}px.")

                self.after(0, self.status_label.config, {'text': f"Status: {self.state} (Control Active)", 'foreground': 'green'})
                # FALL THROUGH to FISHING state logic below
            else:
                # Not ready for fishing yet, continue with navigation/recast logic
                return

        # --- FISHING state starts here ---
        if self.state == "FISHING":

            # --- 4a. Target Line LOST Cooldown (target_line_x is None) ---
            if target_line_x is None:
                # Target line is lost, start or continue the cooldown timer
                if self.lost_target_line_time == 0.0:
                    self.lost_target_line_time = current_time
                    conditional_logger.info(f"Target line lost. Starting {self.fishing_cooldown_duration}s cooldown.")

                # Check if the cooldown has expired
                if current_time - self.lost_target_line_time >= self.fishing_cooldown_duration:
                    self.state = "IDLE"
                    conditional_logger.warning("FISHING -> IDLE. Target line lost for too long.")
                    
                    # End current adaptive PID session
                    self._end_adaptive_session()
                    
                    # Reset fast response system when returning to IDLE
                    self.last_target_line_x = None
                    self.last_mouse_action_time = 0.0
                    self.after(0, self._return_to_idle) # <-- Auto-restart scanning
                    return # Exit processing for this frame

                # If target is lost but cooldown is active, release the mouse and update status
                if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                    pyautogui.mouseUp(button='left')
                    self.is_holding_click = False

                status_color_mode = "Line Lost Cooldown"
                time_left = self.fishing_cooldown_duration - (current_time - self.lost_target_line_time)
                status_suffix = f" | Time Left: {time_left:.2f}s"

                # Update GUI Status immediately for cooldown
                control_state = "HOLD" if self.is_holding_click else "RELEASE"
                box_len = f"{self.estimated_box_length:.1f}" if self.has_calculated_length_once else "..."
                display_status = f"Status: {self.state} | {status_color_mode}{status_suffix} | Ctrl: {control_state} | Box Len: {box_len}px"
                self.after(0, self.status_label.config, {'text': display_status, 'foreground': 'orange'})

                # Reset PD state since no control is happening
                self.last_target_x = None
                self.last_error = 0.0

                return # Skip the rest of tracking and control for this frame

            else:
                # Target line found, reset the lost line cooldown timer
                self.lost_target_line_time = 0.0
                self.spam_click_next_toggle_time = 0.0  # Reset spam click timer when target line is found

            # --- Tracking and Control Logic starts here (target_line_x is not None) ---

            color_tracking_successful = False
            previous_box_center = self.box_center_x  # Store previous position for smoothing
            current_tracking_mode = None  # Track which mode we're using this frame

            # 1. Try Direct Color Tracking (Fishing Box)
            if box_pixel_count > 100:
                actual_box_left_x = np.min(box_x_coords)
                actual_box_right_x = np.max(box_x_coords)

                new_length = actual_box_right_x - actual_box_left_x

                if 10 < new_length < width:
                    current_tracking_mode = "direct_color"
                    self.estimated_box_length = new_length
                    new_box_center = (actual_box_left_x + actual_box_right_x) / 2.0
                    
                    # Smooth transition from previous tracking mode
                    if previous_box_center is not None and self.last_tracking_mode != "direct_color":
                        # Limit sudden jumps to prevent jerky control
                        max_jump = self.estimated_box_length * 0.5  # Allow half-box-width jumps max
                        if abs(new_box_center - previous_box_center) > max_jump:
                            # Gradually move toward the new position instead of jumping
                            direction = 1 if new_box_center > previous_box_center else -1
                            new_box_center = previous_box_center + (direction * max_jump)
                            conditional_logger.debug(f"Smoothing box center transition: {previous_box_center:.1f} -> {new_box_center:.1f}")
                    
                    self.last_left_x = new_box_center - (new_length / 2.0)
                    self.last_right_x = new_box_center + (new_length / 2.0)
                    self.box_center_x = new_box_center
                    self.has_calculated_length_once = True
                    color_tracking_successful = True
                    status_color_mode = "Direct Color Tracking"
                    
                    # Update movement tracking for intelligent search system
                    try:
                        self._update_movement_tracking(self.box_center_x)
                    except Exception:
                        pass  # Silent fail to prevent spam
                    
                    # Force immediate overlay update for responsive visual feedback
                    if hasattr(self, 'live_feed_window') and self.live_feed_window:
                        try:
                            self.live_feed_window.force_overlay_update()
                        except Exception:
                            pass  # Silent fail to prevent spam
                    
                    # Calibrate arrow offset if we have both box edges and arrow detection
                    if indicator_pixel_count > 0 and indicator_centroid_x is not None:
                        self._calibrate_arrow_offset(actual_box_left_x, actual_box_right_x, indicator_centroid_x)
                else:
                    status_color_mode = "Color Tracking Failed (Bad Size)"
            else:
                status_color_mode = "Color Tracking Failed (No Box Pixels)"

            # 2. Fallback to Arrow Tracking/Estimation (Single Pixel Sensitive)
            if not color_tracking_successful and indicator_pixel_count > 0:

                # If the specialized centroid function failed, but we know pixels exist, calculate a simple average
                if indicator_centroid_x is None:
                    arrow_x_coords = np.where(indicator_arrow_mask > 0)[1]
                    if len(arrow_x_coords) > 0:
                        indicator_centroid_x = np.mean(arrow_x_coords)

                # Proceed only if we successfully found a centroid
                if indicator_centroid_x is not None:
                    current_tracking_mode = "arrow_fallback"

                    if not self.has_calculated_length_once:
                        self._handle_initialization(indicator_centroid_x, width, target_line_x)
                        if self.initialization_stage < INIT_CLICKS_REQUIRED:
                            status_color_mode = "Arrow Fallback (Init)"
                            return
                        self._update_box_estimation(indicator_centroid_x, width)

                    else:
                        # Store previous center before updating
                        pre_update_center = self.box_center_x
                        self._update_box_estimation(indicator_centroid_x, width)
                        
                        # Apply smoothing if transitioning from direct color tracking
                        if (pre_update_center is not None and self.box_center_x is not None and 
                            self.last_tracking_mode == "direct_color"):
                            max_jump = self.estimated_box_length * 0.5
                            if abs(self.box_center_x - pre_update_center) > max_jump:
                                direction = 1 if self.box_center_x > pre_update_center else -1
                                smoothed_center = pre_update_center + (direction * max_jump)
                                
                                # Update left/right positions to match smoothed center
                                half_length = self.estimated_box_length / 2.0
                                self.last_left_x = smoothed_center - half_length
                                self.last_right_x = smoothed_center + half_length
                                self.box_center_x = smoothed_center
                                conditional_logger.debug(f"Smoothing arrow estimation transition: {pre_update_center:.1f} -> {smoothed_center:.1f}")

                    calibration_status = "Calibrated" if self.arrow_offset_calibrated else f"Learning({len(self.arrow_offset_samples)}/5)"
                    status_color_mode = f"Arrow Estimation ({calibration_status})"
                else:
                    status_color_mode = "Arrow Tracking Failed (Centroid error)"

            # 3. CRITICAL FALLBACK / GRACE PERIOD (New Logic for Spam Click Delay)
            tracking_fully_lost = (target_line_x is not None and not color_tracking_successful and indicator_pixel_count == 0)

            if not tracking_fully_lost:
                # Tracking is back (or was never fully lost), reset the timer
                self.tracking_lost_time = 0.0
                self.spam_click_next_toggle_time = 0.0  # Reset spam click timer
                self.white_line_search_active = False  # Reset intelligent search flag

            if tracking_fully_lost:
                # --- Enhanced ML-based bar reacquisition when target line is detected but bar is lost ---
                prediction_used = False
                # If the target line is present and has moved rapidly (dashed), use ML to estimate bar movement
                if self._is_prediction_reliable() and target_line_x is not None:
                    # Estimate bar movement needed to reach the target line using ML velocity/acceleration
                    predicted_bar_x = self._predict_target_position(self.prediction_frames, time_delta)
                    # If the target line has moved a significant distance, bias the prediction toward it
                    if self.last_target_line_x is not None:
                        target_line_delta = target_line_x - self.last_target_line_x
                        # If the target line dashes (large delta), use ML to move bar in that direction
                        dash_threshold = self.estimated_box_length * 0.3
                        if abs(target_line_delta) > dash_threshold:
                            # Move bar in the direction of the target line dash, using ML velocity/accel
                            direction = 1 if target_line_delta > 0 else -1
                            ml_speed = max(abs(self.current_velocity), self.min_velocity_threshold)
                            if self.box_center_x is not None:
                                self.box_center_x += direction * ml_speed * time_delta
                            else:
                                self.box_center_x = target_line_x - direction * self.estimated_box_length * 0.5
                            prediction_used = True
                            status_color_mode = "ML Bar Seek (Target Dashed)"
                            status_suffix = f" | ML speed: {ml_speed:.2f}, Δtarget: {target_line_delta:.1f}"
                    # If not a dash, use normal prediction
                    if not prediction_used and predicted_bar_x is not None:
                        if self.box_center_x is not None:
                            alignment_speed = self.estimated_box_length * 0.15
                            if abs(predicted_bar_x - self.box_center_x) > alignment_speed:
                                direction = 1 if predicted_bar_x > self.box_center_x else -1
                                self.box_center_x += direction * alignment_speed
                            else:
                                self.box_center_x = predicted_bar_x
                        else:
                            self.box_center_x = predicted_bar_x
                        prediction_used = True
                        status_color_mode = "Predictive Bar Reacquisition"
                        status_suffix = " | Using ML velocity/accel prediction"
                    if prediction_used:
                        if hasattr(self, 'live_feed_window') and self.live_feed_window:
                            try:
                                self.live_feed_window.force_overlay_update()
                            except Exception:
                                pass
                        tracking_fully_lost = False

                # If prediction not used or not reliable, try intelligent search
                if not prediction_used and self.search_enabled and not self.white_line_search_active:
                    try:
                        intelligent_x = self._intelligent_white_line_search(cv_img_bgr, width, height, rod_colors, target_line_tol)
                        if intelligent_x is not None:
                            target_line_x = intelligent_x
                            current_tracking_mode = "intelligent_search"
                            self.white_line_search_active = True
                            if self.box_center_x is not None:
                                alignment_speed = self.estimated_box_length * 0.15
                                if abs(target_line_x - self.box_center_x) > alignment_speed:
                                    direction = 1 if target_line_x > self.box_center_x else -1
                                    self.box_center_x += direction * alignment_speed
                                else:
                                    self.box_center_x = target_line_x
                            else:
                                self.box_center_x = target_line_x
                            self.last_left_x = None; self.last_right_x = None
                            self.tracking_lost_time = 0.0
                            self.spam_click_next_toggle_time = 0.0
                            if hasattr(self, 'live_feed_window') and self.live_feed_window:
                                try:
                                    self.live_feed_window.force_overlay_update()
                                except Exception:
                                    pass
                            status_color_mode = "Intelligent Search (Active)"
                            status_suffix = " | Found white line via directional search"
                            tracking_fully_lost = False
                    except Exception as e:
                        logging.debug(f"Error in intelligent search: {e}")

                # If still fully lost, fall back to spam mode
                if tracking_fully_lost:
                    current_tracking_mode = "critical_spam"
                    if self.tracking_lost_time == 0.0:
                        self.tracking_lost_time = current_time
                        self.spam_click_next_toggle_time = current_time
                        logging.info(f"Critical tracking lost (Line present). Starting spam click with gradual alignment.")
                    self.update_spam_click_timing()
                    if self.box_center_x is not None:
                        alignment_speed = self.estimated_box_length * 0.1
                        if abs(target_line_x - self.box_center_x) > alignment_speed:
                            direction = 1 if target_line_x > self.box_center_x else -1
                            self.box_center_x += direction * alignment_speed
                        else:
                            self.box_center_x = target_line_x
                    else:
                        self.box_center_x = target_line_x
                    self.last_left_x = None; self.last_right_x = None
                    time_in_spam = current_time - self.tracking_lost_time
                    if time_in_spam > 0.1:
                        self.last_error = 0.0
                        self.last_target_x = None
                    if current_time >= self.spam_click_next_toggle_time:
                        if MOUSE_CONTROL_AVAILABLE:
                            if not self.is_holding_click:
                                pyautogui.mouseDown(button='left')
                                self.is_holding_click = True
                                self.spam_click_next_toggle_time = current_time + self.spam_click_hold_duration
                            else:
                                pyautogui.mouseUp(button='left')
                                self.is_holding_click = False
                                self.spam_click_next_toggle_time = current_time + self.spam_click_release_duration
                    status_color_mode = "CRITICAL SPAM (Smooth Align)"
                    status_suffix = f" | Duration: {time_in_spam:.1f}s"
                    status = f"{self.state} | {status_color_mode}{status_suffix}"
                    control_state = "HOLD" if self.is_holding_click else "RELEASE"
                    box_len = f"{self.estimated_box_length:.1f}" if self.has_calculated_length_once else "..."
                    self.after(0, self.status_label.config, {'text': f"Status: {status} | Ctrl: {control_state} | Box Len: {box_len}px", 'foreground': 'purple'})
                    return

        # --- 5. Control Logic (PD Controller & Boundary Override) - Runs ONLY IF self.state == "FISHING" ---

            # We must have both the target line and the box center estimated
            if target_line_x is not None and self.box_center_x is not None and self.has_calculated_length_once:

                # --- A. Update Predictive Velocity Tracking ---
                self._update_target_position_history(target_line_x, current_time)
                
                # --- B. Get Predicted Target Position (with reliability check) ---
                use_prediction = self._is_prediction_reliable()
                if use_prediction:
                    predicted_target_x = self._predict_target_position(self.prediction_frames, time_delta)
                    if predicted_target_x is None:
                        predicted_target_x = target_line_x  # Fallback to current position
                        use_prediction = False
                else:
                    predicted_target_x = target_line_x  # Use current position if prediction is unreliable
                
                # Use predicted position for control calculation
                control_target_x = predicted_target_x
                error = control_target_x - self.box_center_x # Positive error means target is to the RIGHT (needs HOLD/UP)

                # Define the boundary margin in pixels
                boundary_px_margin = self.estimated_box_length * boundary_factor

                # --- C. Boundary Override Check (using predicted position) ---
                is_near_left_boundary = (control_target_x < boundary_px_margin)
                is_near_right_boundary = (control_target_x > width - boundary_px_margin)

                if is_near_left_boundary:
                    control_signal = -100.0 # Max Release
                    status_suffix = " | Boundary Override: Max RELEASE"
                    should_hold = False
                elif is_near_right_boundary:
                    control_signal = 100.0  # Max Hold
                    status_suffix = " | Boundary Override: Max HOLD"
                    should_hold = True
                else:
                    # --- B. INTELLIGENT ADAPTIVE PD CONTROL CALCULATION ---
                    # Select appropriate control parameters based on current scenario
                    adaptive_kp, adaptive_kd, control_mode = self._select_control_parameters(
                        error, abs(error), use_prediction, self.tracking_lost_time > 0.0,
                        is_near_left_boundary or is_near_right_boundary, current_time
                    )
                    
                    # Store the control mode for learning purposes
                    self.current_control_mode = control_mode
                    self.control_mode_history.append((current_time, control_mode))
                    
                    # Keep only recent control mode history (last 60 seconds)
                    cutoff_time = current_time - 60.0
                    self.control_mode_history = [entry for entry in self.control_mode_history if entry[0] > cutoff_time]
                    
                    P_term = adaptive_kp * error
                    D_term = 0.0

                    # Smooth PD control transitions when recovering from tracking loss
                    if self.last_error is not None and time_delta > 0.001:
                        error_rate = (error - self.last_error) / time_delta
                        D_term = adaptive_kd * error_rate
                    elif self.tracking_lost_time > 0.0:
                        # Just recovered from tracking loss, apply recovery mode smoothing
                        P_term = P_term * 0.6  # More conservative smoothing for recovery
                        logging.debug(f"Recovery mode: Reduced P-term to {P_term:.2f}")

                    control_signal = P_term + D_term
                    control_signal = np.clip(control_signal, -pd_clamp, pd_clamp)
                    
                    # Update performance tracking for adaptive tuning (with control mode context)
                    self._update_performance_history(error, control_signal)
                    self._perform_adaptive_tuning_analysis(current_time)
                    
                    # Add prediction and adaptive info to status
                    prediction_offset = predicted_target_x - target_line_x
                    adaptive_status = f"A-{control_mode.upper()}:{adaptive_kp:.2f}/{adaptive_kd:.1f}" if self.adaptive_enabled else "Manual PID"
                    
                    if use_prediction and abs(prediction_offset) > 0.5:  # Only show if prediction is significant and used
                        status_suffix = f" | {adaptive_status} | Signal={control_signal:+.2f} | Pred: {prediction_offset:+.1f}px | Vel: {self.current_velocity:+.1f}px/s"
                    elif use_prediction:
                        status_suffix = f" | {adaptive_status} | Signal={control_signal:+.2f} | Predictive Mode"
                    else:
                        status_suffix = f" | {adaptive_status} | Signal={control_signal:+.2f} | {control_mode.title()} Mode"

                    # Update PD state for the next loop
                    self.last_error = error
                    self.last_target_x = target_line_x

                    # --- C. Convert Control Signal to Mouse Action (Dead Zone = Spam Click) ---
                    action_threshold = target_tol_px # Dead zone size in pixels

                    if control_signal > action_threshold:
                        # Target is far right/above threshold, NEEDS HOLD
                        should_hold = True
                    elif control_signal < -action_threshold:
                        # Target is far left/below threshold, NEEDS RELEASE
                        should_hold = False
                    else:
                        # Within the dead zone: Spam Click (alternate hold state)
                        should_hold = not self.is_holding_click
                        status_color_mode = "Dead Zone SPAM"
                        status_suffix = f" | Dead Zone SPAM"

                # --- D. Fast Response System for Sudden Target Movement ---
                fast_response_triggered = False
                
                if (self.fast_response_enabled_var.get() and self.last_target_line_x is not None and 
                    target_line_x is not None and MOUSE_CONTROL_AVAILABLE):
                    
                    # Check for sudden target line movement
                    movement = abs(target_line_x - self.last_target_line_x)
                    time_since_last_action = current_time - self.last_mouse_action_time
                    
                    # Get threshold from GUI variable
                    try:
                        movement_threshold = float(self.sudden_movement_threshold_var.get())
                    except (ValueError, AttributeError):
                        movement_threshold = 10.0  # Default fallback
                    
                    if (movement > movement_threshold and 
                        time_since_last_action >= self.min_action_interval):
                        
                        # Recalculate what action we should take based on new position
                        fast_error = target_line_x - self.box_center_x
                        fast_control_signal = KP * fast_error  # Quick P-only control
                        fast_control_signal = np.clip(fast_control_signal, -pd_clamp, pd_clamp)
                        
                        # Determine fast response action
                        fast_should_hold = None
                        if is_near_left_boundary:
                            fast_should_hold = False
                        elif is_near_right_boundary:
                            fast_should_hold = True
                        elif fast_control_signal > action_threshold:
                            fast_should_hold = True
                        elif fast_control_signal < -action_threshold:
                            fast_should_hold = False
                        
                        # Execute fast response if different from current state
                        if (fast_should_hold is not None and 
                            fast_should_hold != self.is_holding_click):
                            
                            if fast_should_hold:
                                pyautogui.mouseDown(button='left')
                                self.is_holding_click = True
                                conditional_logger.debug(f"FAST RESPONSE: Hold (movement: {movement:.1f}px)")
                            else:
                                pyautogui.mouseUp(button='left')
                                self.is_holding_click = False
                                conditional_logger.debug(f"FAST RESPONSE: Release (movement: {movement:.1f}px)")
                            
                            self.last_mouse_action_time = current_time
                            fast_response_triggered = True
                            status_suffix += f" | FAST: {movement:.1f}px"

                # Update target line tracking for next frame
                if target_line_x is not None:
                    self.last_target_line_x = target_line_x

                # --- E. Execute Normal Mouse Action (if fast response didn't trigger)
                if MOUSE_CONTROL_AVAILABLE and not fast_response_triggered:
                    time_since_last_action = current_time - self.last_mouse_action_time
                    
                    if time_since_last_action >= self.min_action_interval:
                        if should_hold and not self.is_holding_click:
                            pyautogui.mouseDown(button='left')
                            self.is_holding_click = True
                            self.last_mouse_action_time = current_time
                        elif not should_hold and self.is_holding_click:
                            pyautogui.mouseUp(button='left')
                            self.is_holding_click = False
                            self.last_mouse_action_time = current_time
                            conditional_logger.debug("Mouse Up (RELEASE/SPAM)")


            else:
                # Fallback state if tracking data is lost during control mode (but not fully lost, e.g., only box center is None)
                if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                    pyautogui.mouseUp(button='left')
                    self.is_holding_click = False
                status_color_mode = f"Tracking Lost/Waiting"
                status_suffix = ""

                # Reset PD state if tracking is lost
                self.last_target_x = None
                self.last_error = 0.0

            # 6. Update GUI Status
            status = f"{self.state} | {status_color_mode}{status_suffix}"
            control_state = "HOLD" if self.is_holding_click else "RELEASE"
            box_len = f"{self.estimated_box_length:.1f}" if self.has_calculated_length_once else "..."

            if "Boundary Override" in status:
                color = '#CC3300' # Dark Red-Orange (better contrast on white)
            elif "Dead Zone SPAM" in status:
                color = '#B8860B' # Dark Golden Rod (much better than yellow on white)
            elif "PD Control" in status or "Direct Color Tracking" in status:
                color = '#006600' # Dark Green (better contrast than light green)
            elif "Tracking Lost/Waiting" in status:
                color = '#008B8B' # Dark Cyan (much better than light cyan on white)
            else:
                color = '#008B8B' # Dark Cyan (much better than light cyan on white)

            display_status = f"Status: {status} | Ctrl: {control_state} | Box Len: {box_len}px"

            self.after(0, self.status_label.config, {'text': display_status, 'foreground': color})

            # Update tracking mode for next frame's transition smoothing
            if current_tracking_mode is not None:
                self.last_tracking_mode = current_tracking_mode
            elif tracking_fully_lost:
                self.last_tracking_mode = "critical_spam"
            else:
                self.last_tracking_mode = "lost"

    def _handle_initialization(self, indicator_centroid_x, width, target_line_x):
        """
        Manages the forced hold/release clicks to measure the box size (Fallback Only).
        """
        global INIT_CLICKS_REQUIRED

        status = "Initializing (Arrow Fallback)"

        # Clear box coords during initialization since size is not final
        self.last_left_x = None
        self.last_right_x = None
        self.box_center_x = None

        if indicator_centroid_x is None:
            # Wait until the arrow is visible
            status = "Waiting for arrow..."
            if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                pyautogui.mouseUp(button='left')
                self.is_holding_click = False

        else:
            # Stage 0: First arrow detected. Anchor initial point and start the first click.
            if self.initialization_stage == 0:
                self.initial_anchor_x = indicator_centroid_x # This is the first edge (e.g., Left)

                # Start the first click to swap the arrow to the other side (e.g., Right)
                if MOUSE_CONTROL_AVAILABLE and not self.is_holding_click:
                    pyautogui.mouseDown(button='left')
                    self.is_holding_click = True
                    self.initialization_stage = 1
                    status = "Init: Forcing HOLD"
                    logging.info(f"Init: Stage 0 -> 1. Anchor set to {self.initial_anchor_x:.1f}. Forcing HOLD.")
                else:
                    status = "Init: Ready to start HOLD"

            # Stage 1: Waiting for the hold to register and arrow to move.
            elif self.initialization_stage == 1:
                if self.is_holding_click:
                    # Arrow is now on the opposite side (e.g., Right edge)
                    if self.initial_anchor_x is not None:
                        new_length = abs(indicator_centroid_x - self.initial_anchor_x)

                        if 10 < new_length < width:
                            self.estimated_box_length = new_length
                            self.has_calculated_length_once = True

                            # Release the click to swap the arrow back
                            if MOUSE_CONTROL_AVAILABLE:
                                pyautogui.mouseUp(button='left')
                                self.is_holding_click = False

                            self.initialization_stage = 2
                            logging.info(f"Init: Stage 1 -> 2. Box size measured at {new_length:.1f}px. Forcing RELEASE.")
                            status = "Init: Measured, Forcing RELEASE"
                        else:
                            status = f"Init: Measurement failed ({new_length:.1f}px), restarting."
                            if MOUSE_CONTROL_AVAILABLE:
                                pyautogui.mouseUp(button='left')
                                self.is_holding_click = False
                            self.initialization_stage = 0
                            self.initial_anchor_x = None
                            logging.warning("Init: Measurement failed, restarting initialization.")


            # Stage 2: Initialization complete (already swapped back to RELEASE)
            elif self.initialization_stage == INIT_CLICKS_REQUIRED:
                if not self.is_holding_click:
                    # Finalize initial state (RELEASE)
                    self.last_holding_state = self.is_holding_click
                    self.initialization_stage += 1 # Set stage to 3 (beyond required count)
                    conditional_logger.info("Init: Stage 2 -> Complete. Entering control mode with arrow logic.")
                    status = "Initialization complete. Entering Control Mode."
                else:
                    status = "Init: Waiting for stable release state."

        # Update GUI status during initialization
        len_str = f"({self.estimated_box_length:.1f}px)" if self.has_calculated_length_once else ""
        display_status = f"Status: {status} {len_str}"
        self.after(0, self.status_label.config, {'text': display_status, 'foreground': '#CC6600'})

    # --- PREDICTIVE VELOCITY TRACKING FUNCTIONS ---
    
    def _update_target_position_history(self, target_x, current_time):
        """Update position history and calculate velocity/acceleration"""
        if target_x is None:
            return
            
        # Add new position and time to history
        self.target_position_history.append(target_x)
        self.target_time_history.append(current_time)
        
        # Keep only the last N entries
        if len(self.target_position_history) > self.history_size:
            self.target_position_history.pop(0)
            self.target_time_history.pop(0)
        
        # Calculate velocity and acceleration if we have enough data
        if len(self.target_position_history) >= 2:
            self._calculate_velocity_and_acceleration()
    
    def _calculate_velocity_and_acceleration(self):
        """Calculate current velocity and acceleration from position history"""
        if len(self.target_position_history) < 2:
            self.current_velocity = 0.0
            self.current_acceleration = 0.0
            return
        
        # Calculate velocity using linear regression for smoother results
        positions = self.target_position_history
        times = self.target_time_history
        
        # Simple velocity calculation (last two points)
        dt = times[-1] - times[-2]
        if dt > 0.001:  # Avoid division by very small time differences
            new_velocity = (positions[-1] - positions[-2]) / dt
            
            # Smooth velocity using exponential moving average
            if hasattr(self, 'current_velocity'):
                self.current_velocity = (self.velocity_smoothing_factor * self.current_velocity + 
                                       (1 - self.velocity_smoothing_factor) * new_velocity)
            else:
                self.current_velocity = new_velocity
        
        # Calculate acceleration if we have enough history
        if len(self.target_position_history) >= 3:
            # Use last 3 points to calculate acceleration
            dt1 = times[-2] - times[-3]
            dt2 = times[-1] - times[-2]
            
            if dt1 > 0.001 and dt2 > 0.001:
                v1 = (positions[-2] - positions[-3]) / dt1
                v2 = (positions[-1] - positions[-2]) / dt2
                avg_dt = (dt1 + dt2) / 2
                self.current_acceleration = (v2 - v1) / avg_dt
            else:
                self.current_acceleration = 0.0
        else:
            self.current_acceleration = 0.0
    
    def _predict_target_position(self, frames_ahead, time_delta):
        """Predict future target position based on current velocity and acceleration with reliability checks"""
        if not hasattr(self, 'target_position_history') or len(self.target_position_history) == 0:
            return None
            
        current_position = self.target_position_history[-1]
        
        # Only use prediction if we have enough reliable data
        if len(self.target_position_history) < 3:
            return current_position  # Not enough data for reliable prediction
        
        # Check for consistency in recent positions (detect jittery/unreliable tracking)
        if len(self.target_position_history) >= 3:
            recent_positions = self.target_position_history[-3:]
            position_variance = np.var(recent_positions)
            
            # If positions are too jittery, reduce prediction confidence
            if position_variance > 15.0:  # Reduced from 25.0 - more conservative
                # Use only current position for high-variance situations
                return current_position
        
        # Only use prediction if velocity is significant and reasonable
        if abs(self.current_velocity) < self.min_velocity_threshold:
            return current_position
            
        # Clamp unreasonable velocities (likely detection errors)
        max_reasonable_velocity = 200.0  # pixels per second
        if abs(self.current_velocity) > max_reasonable_velocity:
            return current_position
        
        # Calculate prediction time
        prediction_time = frames_ahead * time_delta
        
        # Kinematic equation: position = current_pos + velocity*time + 0.5*acceleration*time²
        # But limit acceleration influence to prevent wild overshoots
        limited_acceleration = np.clip(self.current_acceleration, -200.0, 200.0)  # Reduced from 500
        
        # Reduce acceleration influence further
        acceleration_factor = 0.3  # Only use 30% of acceleration
        
        predicted_position = (current_position + 
                            self.current_velocity * prediction_time + 
                            0.5 * limited_acceleration * acceleration_factor * prediction_time * prediction_time)
        
        # Limit prediction distance to prevent wild overshoots
        max_distance = self.max_prediction_distance
        position_change = predicted_position - current_position
        
        if abs(position_change) > max_distance:
            direction = 1 if position_change > 0 else -1
            predicted_position = current_position + (direction * max_distance)
        
        return predicted_position
    
    def _reset_velocity_tracking(self):
        """Reset velocity tracking when starting new fishing session"""
        self.target_position_history.clear()
        self.target_time_history.clear()
        self.current_velocity = 0.0
        self.current_acceleration = 0.0
        self.prediction_reliability_score = 1.0
        self.prediction_error_history.clear()
    
    def _is_prediction_reliable(self):
        """Check if prediction system is currently reliable enough to use"""
        # Consider prediction reliable if:
        # 1. We have enough data
        # 2. Reliability score is good
        # 3. Velocity is reasonable and significant
        # 4. Recent positions show consistent movement pattern
        if not (len(self.target_position_history) >= 4 and  # Need more data points
                self.prediction_reliability_score > 0.7 and   # Higher reliability threshold
                abs(self.current_velocity) >= self.min_velocity_threshold and
                abs(self.current_velocity) < 150.0):  # Lower max velocity threshold
            return False
        
        # Additional check: ensure recent movement is consistent
        if len(self.target_position_history) >= 4:
            recent_positions = self.target_position_history[-4:]
            # Check if movement direction is consistent
            movements = [recent_positions[i] - recent_positions[i-1] for i in range(1, len(recent_positions))]
            
            # If movements change direction too much, don't use prediction
            direction_changes = 0
            for i in range(1, len(movements)):
                if (movements[i] > 0) != (movements[i-1] > 0):  # Direction change
                    direction_changes += 1
            
            # Allow max 1 direction change in recent history
            if direction_changes > 1:
                return False
        
        return True

    # --- MULTI-PARAMETER ADAPTIVE CONTROL FUNCTIONS ---
    
    def _select_control_parameters(self, error, abs_error, using_prediction, in_recovery, near_boundary, current_time):
        """Select appropriate KP/KD parameters based on current control scenario"""
        
        # Determine control mode based on current conditions (priority order)
        if in_recovery:
            # Recently recovered from tracking loss - use gentle parameters
            control_mode = "recovery"
            kp = self.adaptive_recovery_kp if self.adaptive_enabled else 0.25
            kd = self.adaptive_recovery_kd if self.adaptive_enabled else 8.0
            
        elif near_boundary:
            # Near box boundary - use strong parameters to prevent violations
            control_mode = "boundary"
            kp = self.adaptive_boundary_kp if self.adaptive_enabled else 0.40
            kd = self.adaptive_boundary_kd if self.adaptive_enabled else 5.0
            
        elif abs_error <= 2.0:
            # Very small error - use fine-tuning parameters
            control_mode = "fine"
            kp = self.adaptive_fine_kp if self.adaptive_enabled else 0.20
            kd = self.adaptive_fine_kd if self.adaptive_enabled else 9.0
            
        elif using_prediction:
            # Using velocity prediction - adjust for predictive compensation
            control_mode = "predictive"
            kp = self.adaptive_pred_kp if self.adaptive_enabled else 0.30
            kd = self.adaptive_pred_kd if self.adaptive_enabled else 7.0
            
        elif hasattr(self, 'fast_response_triggered') and self.fast_response_triggered:
            # Fast response to sudden movement - use quick parameters
            control_mode = "fast"
            kp = self.adaptive_fast_kp if self.adaptive_enabled else 0.45
            kd = self.adaptive_fast_kd if self.adaptive_enabled else 4.0
            
        else:
            # Normal steady-state control
            control_mode = "steady"
            kp = self.adaptive_steady_kp if self.adaptive_enabled else 0.35
            kd = self.adaptive_steady_kd if self.adaptive_enabled else 6.0
        
        # Update legacy parameters for compatibility (weighted average of specialized parameters)
        if self.adaptive_enabled:
            self._update_legacy_parameters()
        
        return kp, kd, control_mode
    
    def _update_legacy_parameters(self):
        """Update legacy KP/KD as weighted average of specialized parameters"""
        # Weight parameters based on recent usage
        mode_weights = self._calculate_mode_usage_weights()
        
        # Calculate weighted averages
        self.adaptive_kp = (
            mode_weights.get('steady', 0.3) * self.adaptive_steady_kp +
            mode_weights.get('fast', 0.1) * self.adaptive_fast_kp +
            mode_weights.get('predictive', 0.2) * self.adaptive_pred_kp +
            mode_weights.get('recovery', 0.1) * self.adaptive_recovery_kp +
            mode_weights.get('boundary', 0.1) * self.adaptive_boundary_kp +
            mode_weights.get('fine', 0.2) * self.adaptive_fine_kp
        )
        
        self.adaptive_kd = (
            mode_weights.get('steady', 0.3) * self.adaptive_steady_kd +
            mode_weights.get('fast', 0.1) * self.adaptive_fast_kd +
            mode_weights.get('predictive', 0.2) * self.adaptive_pred_kd +
            mode_weights.get('recovery', 0.1) * self.adaptive_recovery_kd +
            mode_weights.get('boundary', 0.1) * self.adaptive_boundary_kd +
            mode_weights.get('fine', 0.2) * self.adaptive_fine_kd
        )
    
    def _calculate_mode_usage_weights(self):
        """Calculate weights based on recent control mode usage"""
        if not self.control_mode_history:
            # Default weights if no history
            return {'steady': 0.4, 'fast': 0.1, 'predictive': 0.2, 'recovery': 0.1, 'boundary': 0.1, 'fine': 0.1}
        
        # Count recent mode usage (last 30 seconds)
        current_time = time.time()
        recent_modes = [mode for timestamp, mode in self.control_mode_history if current_time - timestamp <= 30.0]
        
        if not recent_modes:
            return {'steady': 0.4, 'fast': 0.1, 'predictive': 0.2, 'recovery': 0.1, 'boundary': 0.1, 'fine': 0.1}
        
        mode_counts = {}
        for mode in recent_modes:
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        total_count = len(recent_modes)
        return {mode: count / total_count for mode, count in mode_counts.items()}
    
    def _update_performance_history(self, error, control_signal):
        """Update performance tracking history with current control data"""
        self.error_history.append(error)
        self.control_signal_history.append(control_signal)
        
        # Also update current session data
        self.current_session_data['errors'].append(error)
        
        # Keep only recent history
        if len(self.error_history) > self.performance_window_size:
            self.error_history.pop(0)
        if len(self.control_signal_history) > self.performance_window_size:
            self.control_signal_history.pop(0)
    
    def _analyze_control_performance(self):
        """Analyze recent control performance and detect issues"""
        if len(self.error_history) < 10:  # Need minimum data
            return {}
        
        errors = np.array(self.error_history[-20:])  # Last 20 data points
        control_signals = np.array(self.control_signal_history[-20:])
        
        analysis = {}
        
        # 1. Detect Overshooting (error changes sign frequently)
        error_sign_changes = 0
        for i in range(1, len(errors)):
            if (errors[i] > 0) != (errors[i-1] > 0) and abs(errors[i]) > 1.0:
                error_sign_changes += 1
        
        analysis['overshooting'] = error_sign_changes > 3  # More than 3 sign changes = oscillation
        analysis['oscillation_severity'] = error_sign_changes
        
        # 2. Detect Undershooting (consistently large errors)
        avg_abs_error = np.mean(np.abs(errors))
        analysis['undershooting'] = avg_abs_error > 8.0  # Average error > 8 pixels
        analysis['avg_error'] = avg_abs_error
        
        # 3. Measure Response Time (time to get within tolerance)
        tolerance = 3.0
        settling_frames = 0
        for i in range(len(errors)):
            if abs(errors[i]) <= tolerance:
                settling_frames = len(errors) - i
                break
        
        analysis['slow_response'] = settling_frames < 5  # Taking too long to settle
        analysis['settling_frames'] = settling_frames
        
        # 4. Measure Error Variance (stability)
        self.recent_error_variance = np.var(errors)
        analysis['unstable'] = self.recent_error_variance > 25.0
        analysis['error_variance'] = self.recent_error_variance
        
        # 5. Control Signal Analysis
        control_variance = np.var(control_signals)
        analysis['control_thrashing'] = control_variance > 1000.0
        
        return analysis
    
    def _adjust_pid_parameters(self, analysis):
        """Adjust specialized KP and KD parameters based on performance analysis and current control mode"""
        if not self.adaptive_enabled:
            return
        
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_adjustment_time < self.adjustment_cooldown:
            return
        
        # Check if we have enough session data
        if len(self.current_session_data['errors']) < self.min_session_data_size:
            return
        
        # Detect oscillation in recent adjustments
        if self._is_oscillating():
            logging.info("Adaptive PID: Oscillation detected, skipping adjustment and increasing cooldown")
            self.adjustment_cooldown = min(self.adjustment_cooldown * 1.5, 30.0)  # Increase cooldown
            return
        
        # Determine which parameter set to adjust based on recent control mode usage
        mode_weights = self._calculate_mode_usage_weights()
        primary_mode = max(mode_weights.items(), key=lambda x: x[1])[0]
        
        # Get adjustment parameters for the primary mode
        adjustment_info = self._get_mode_adjustment_info(primary_mode)
        if not adjustment_info:
            return
        
        kp_adjustment = 0.0
        kd_adjustment = 0.0
        adjustment_reason = ""
        
        # Reduce adjustment rate if confidence is low
        confidence_factor = max(0.3, self.tuning_confidence)
        kp_rate = adjustment_info['kp_rate'] * confidence_factor
        kd_rate = adjustment_info['kd_rate'] * confidence_factor
        
        # Rule-based tuning adjustments (more conservative)
        if analysis.get('overshooting', False) and analysis.get('oscillation_severity', 0) > 2:
            # Only adjust for significant overshooting
            kp_adjustment = -kp_rate
            kd_adjustment = +kd_rate
            adjustment_reason = f"overshooting in {primary_mode} mode"
            
        elif analysis.get('undershooting', False) and analysis.get('avg_error', 0) > 10.0:
            # Only adjust for significant undershooting
            kp_adjustment = +kp_rate
            adjustment_reason = f"undershooting in {primary_mode} mode"
            
        elif analysis.get('slow_response', False) and analysis.get('settling_frames', 0) < 3:
            # Only adjust for very slow response
            kp_adjustment = +kp_rate * 0.5  # Smaller adjustment
            adjustment_reason = f"slow_response in {primary_mode} mode"
            
        elif analysis.get('unstable', False) and analysis.get('error_variance', 0) > 35.0:
            # Only adjust for significant instability
            kd_adjustment = +kd_rate
            adjustment_reason = f"instability in {primary_mode} mode"
            
        elif analysis.get('control_thrashing', False):
            # Reduce both gains to smooth control
            kp_adjustment = -kp_rate * 0.5
            kd_adjustment = -kd_rate * 0.5
            adjustment_reason = f"control_thrashing in {primary_mode} mode"
        
        # Skip very small adjustments (convergence detection)
        if abs(kp_adjustment) < self.convergence_threshold and abs(kd_adjustment) < self.convergence_threshold:
            return
        
        # Store old values
        old_kp = adjustment_info['current_kp']
        old_kd = adjustment_info['current_kd']
        
        # Apply adjustments with limits
        new_kp = np.clip(old_kp + kp_adjustment, adjustment_info['min_kp'], adjustment_info['max_kp'])
        new_kd = np.clip(old_kd + kd_adjustment, adjustment_info['min_kd'], adjustment_info['max_kd'])
        
        # Update the specific parameter set
        self._update_mode_parameters(primary_mode, new_kp, new_kd)
        
        # Record this adjustment
        self.adjustment_history.append((current_time, kp_adjustment, kd_adjustment, adjustment_reason))
        self.last_adjustment_time = current_time
        self.current_session_data['adjustments'] += 1
        
        # Keep only recent adjustment history
        cutoff_time = current_time - 120.0  # Keep 2 minutes of history
        self.adjustment_history = [adj for adj in self.adjustment_history if adj[0] > cutoff_time]
        
        # Update confidence based on adjustment magnitude and frequency
        total_adjustment = abs(kp_adjustment) + abs(kd_adjustment)
        if total_adjustment > 0.05:  # Large adjustment
            self.tuning_confidence = max(0.4, self.tuning_confidence - 0.15)
        else:  # Small adjustment
            self.tuning_confidence = max(0.6, self.tuning_confidence - 0.05)
        
        # Reset cooldown to base value after successful adjustment
        self.adjustment_cooldown = 8.0
        
        logging.info(f"Adaptive PID: {adjustment_reason}, KP: {old_kp:.3f}→{new_kp:.3f}, KD: {old_kd:.3f}→{new_kd:.3f}")
    
    def _get_mode_adjustment_info(self, mode):
        """Get adjustment parameters for a specific control mode"""
        mode_params = {
            'steady': {
                'current_kp': self.adaptive_steady_kp, 'current_kd': self.adaptive_steady_kd,
                'kp_rate': self.steady_kp_adjustment_rate, 'kd_rate': self.steady_kd_adjustment_rate,
                'min_kp': self.min_steady_kp, 'max_kp': self.max_steady_kp,
                'min_kd': self.min_steady_kd, 'max_kd': self.max_steady_kd
            },
            'fast': {
                'current_kp': self.adaptive_fast_kp, 'current_kd': self.adaptive_fast_kd,
                'kp_rate': self.fast_kp_adjustment_rate, 'kd_rate': self.fast_kd_adjustment_rate,
                'min_kp': self.min_fast_kp, 'max_kp': self.max_fast_kp,
                'min_kd': self.min_fast_kd, 'max_kd': self.max_fast_kd
            },
            'predictive': {
                'current_kp': self.adaptive_pred_kp, 'current_kd': self.adaptive_pred_kd,
                'kp_rate': self.pred_kp_adjustment_rate, 'kd_rate': self.pred_kd_adjustment_rate,
                'min_kp': self.min_pred_kp, 'max_kp': self.max_pred_kp,
                'min_kd': self.min_pred_kd, 'max_kd': self.max_pred_kd
            },
            'recovery': {
                'current_kp': self.adaptive_recovery_kp, 'current_kd': self.adaptive_recovery_kd,
                'kp_rate': self.recovery_kp_adjustment_rate, 'kd_rate': self.recovery_kd_adjustment_rate,
                'min_kp': self.min_recovery_kp, 'max_kp': self.max_recovery_kp,
                'min_kd': self.min_recovery_kd, 'max_kd': self.max_recovery_kd
            },
            'boundary': {
                'current_kp': self.adaptive_boundary_kp, 'current_kd': self.adaptive_boundary_kd,
                'kp_rate': self.boundary_kp_adjustment_rate, 'kd_rate': self.boundary_kd_adjustment_rate,
                'min_kp': self.min_boundary_kp, 'max_kp': self.max_boundary_kp,
                'min_kd': self.min_boundary_kd, 'max_kd': self.max_boundary_kd
            },
            'fine': {
                'current_kp': self.adaptive_fine_kp, 'current_kd': self.adaptive_fine_kd,
                'kp_rate': self.fine_kp_adjustment_rate, 'kd_rate': self.fine_kd_adjustment_rate,
                'min_kp': self.min_fine_kp, 'max_kp': self.max_fine_kp,
                'min_kd': self.min_fine_kd, 'max_kd': self.max_fine_kd
            }
        }
        return mode_params.get(mode)
    
    def _update_mode_parameters(self, mode, new_kp, new_kd):
        """Update parameters for a specific control mode"""
        if mode == 'steady':
            self.adaptive_steady_kp = new_kp
            self.adaptive_steady_kd = new_kd
        elif mode == 'fast':
            self.adaptive_fast_kp = new_kp
            self.adaptive_fast_kd = new_kd
        elif mode == 'predictive':
            self.adaptive_pred_kp = new_kp
            self.adaptive_pred_kd = new_kd
        elif mode == 'recovery':
            self.adaptive_recovery_kp = new_kp
            self.adaptive_recovery_kd = new_kd
        elif mode == 'boundary':
            self.adaptive_boundary_kp = new_kp
            self.adaptive_boundary_kd = new_kd
        elif mode == 'fine':
            self.adaptive_fine_kp = new_kp
            self.adaptive_fine_kd = new_kd
    
    def _is_oscillating(self):
        """Detect if the PID adjustments are oscillating"""
        if len(self.adjustment_history) < 4:
            return False
        
        # Look for alternating KP adjustments (up, down, up, down pattern)
        recent_kp_adjustments = [adj[1] for adj in self.adjustment_history[-4:]]
        
        # Check for sign changes in KP adjustments
        sign_changes = 0
        for i in range(1, len(recent_kp_adjustments)):
            if recent_kp_adjustments[i] != 0 and recent_kp_adjustments[i-1] != 0:
                if (recent_kp_adjustments[i] > 0) != (recent_kp_adjustments[i-1] > 0):
                    sign_changes += 1
        
        return sign_changes >= self.oscillation_threshold
    
    def _perform_adaptive_tuning_analysis(self, current_time):
        """Perform periodic analysis and tuning adjustment with enhanced oscillation prevention"""
        if current_time - self.last_performance_analysis < self.analysis_interval:
            return  # Not time for analysis yet
        
        self.last_performance_analysis = current_time
        
        # Need sufficient data from both general history and current session
        if len(self.error_history) < 15 or len(self.current_session_data['errors']) < self.min_session_data_size:
            return  # Not enough data
        
        # Analyze performance
        analysis = self._analyze_control_performance()
        
        # Store old values to detect changes
        old_kp, old_kd = self.adaptive_kp, self.adaptive_kd
        
        # Adjust parameters based on analysis (with enhanced safeguards)
        self._adjust_pid_parameters(analysis)
        
        # Auto-save learned values if they changed significantly
        if abs(self.adaptive_kp - old_kp) > 0.005 or abs(self.adaptive_kd - old_kd) > 0.05:
            try:
                self.save_config_debounced()  # Save learned values for persistence
                logging.info(f"Adaptive PID: Auto-saved learned values KP={self.adaptive_kp:.3f}, KD={self.adaptive_kd:.3f}")
            except Exception as e:
                logging.warning(f"Error saving adaptive PID values: {e}")
        
        # Log adaptive tuning status (only when there are issues or changes)
        active_issues = [k for k, v in analysis.items() if v and k in ['overshooting', 'undershooting', 'slow_response', 'unstable']]
        if active_issues or abs(self.adaptive_kp - old_kp) > 0.001 or abs(self.adaptive_kd - old_kd) > 0.01:
            logging.info(f"Adaptive PID: KP={self.adaptive_kp:.3f}, KD={self.adaptive_kd:.3f}, Issues: {active_issues}, Confidence: {self.tuning_confidence:.2f}")
        
        # Gradually increase confidence if no adjustments were needed
        if abs(self.adaptive_kp - old_kp) < 0.001 and abs(self.adaptive_kd - old_kd) < 0.01:
            self.tuning_confidence = min(1.0, self.tuning_confidence + 0.02)
    
    def _reset_adaptive_tuning(self):
        """Reset adaptive tuning when starting new fishing session"""
        self.error_history.clear()
        self.control_signal_history.clear()
        self.overshoot_count = 0
        self.oscillation_count = 0
        self.tuning_confidence = 1.0
        self.recent_error_variance = 0.0
        # Keep learned KP/KD values - don't reset to default

    def _start_new_adaptive_session(self):
        """Start a new adaptive PID learning session"""
        current_time = time.time()
        
        # End previous session if it exists
        if self.current_session_data['start_time'] > 0:
            self._end_adaptive_session()
        
        # Initialize new session
        self.current_session_data = {
            'errors': [],
            'start_time': current_time,
            'adjustments': 0
        }
        
        # Slightly increase tuning confidence for new session
        self.tuning_confidence = min(1.0, self.tuning_confidence + 0.1)
        
        logging.info(f"Adaptive PID: Started new learning session")

    def _end_adaptive_session(self):
        """End current adaptive PID session and analyze performance"""
        if self.current_session_data['start_time'] == 0:
            return  # No active session
        
        session_duration = time.time() - self.current_session_data['start_time']
        error_count = len(self.current_session_data['errors'])
        
        # Store session performance for future reference
        if error_count > 10:  # Only store sessions with meaningful data
            avg_error = np.mean(np.abs(self.current_session_data['errors']))
            session_performance = {
                'duration': session_duration,
                'avg_error': avg_error,
                'error_count': error_count,
                'adjustments': self.current_session_data['adjustments'],
                'kp': self.adaptive_kp,
                'kd': self.adaptive_kd
            }
            
            self.performance_sessions.append(session_performance)
            
            # Keep only recent sessions (last 10)
            if len(self.performance_sessions) > 10:
                self.performance_sessions.pop(0)
            
            # Boost confidence if this was a good session with few adjustments
            if self.current_session_data['adjustments'] == 0 and avg_error < 5.0:
                self.tuning_confidence = min(1.0, self.tuning_confidence + 0.05)
            
            logging.info(f"Adaptive PID: Session ended - Duration: {session_duration:.1f}s, Avg Error: {avg_error:.1f}px, Adjustments: {self.current_session_data['adjustments']}")
        
        # Reset session data
        self.current_session_data = {'errors': [], 'start_time': 0, 'adjustments': 0}

    # --- ARROW OFFSET COMPENSATION FUNCTIONS ---
    
    def _calibrate_arrow_offset(self, box_left, box_right, arrow_x):
        """Learn the offset between arrow position and box edges during direct color tracking"""
        if box_left is None or box_right is None or arrow_x is None:
            return
        
        box_center = (box_left + box_right) / 2.0
        box_half_width = (box_right - box_left) / 2.0
        
        # Determine which side the arrow is on
        if arrow_x < box_center:
            # Arrow is on left side, calculate offset from left edge
            offset_from_edge = arrow_x - box_left
        else:
            # Arrow is on right side, calculate offset from right edge
            offset_from_edge = box_right - arrow_x
        
        # Only accept reasonable offsets (arrows should be inside the box)
        if 2.0 <= offset_from_edge <= 25.0:
            self.arrow_offset_samples.append(offset_from_edge)
            
            # Keep only recent samples
            if len(self.arrow_offset_samples) > 10:
                self.arrow_offset_samples.pop(0)
            
            # Calculate learned offset as median of samples
            if len(self.arrow_offset_samples) >= 5:
                old_offset = self.learned_arrow_offset
                self.learned_arrow_offset = np.median(self.arrow_offset_samples)
                self.arrow_offset_calibrated = True
                
                # Auto-save learned arrow offset if it changed significantly or is newly calibrated
                if old_offset is None or abs(self.learned_arrow_offset - old_offset) > 1.0:
                    try:
                        self.save_config_debounced()  # Save learned values for persistence
                        logging.info(f"Arrow offset calibrated and saved: {self.learned_arrow_offset:.1f}px from {len(self.arrow_offset_samples)} samples")
                    except Exception as e:
                        logging.warning(f"Error saving arrow offset: {e}")
                        logging.info(f"Arrow offset calibrated: {self.learned_arrow_offset:.1f}px from {len(self.arrow_offset_samples)} samples")
                else:
                    logging.debug(f"Arrow offset calibrated: {self.learned_arrow_offset:.1f}px from {len(self.arrow_offset_samples)} samples")
    
    def _get_compensated_arrow_box_estimate(self, arrow_x, width):
        """Estimate box edges from arrow position with offset compensation"""
        if arrow_x is None:
            return None, None
        
        # Use learned offset if available, otherwise use default
        offset = self.learned_arrow_offset if self.arrow_offset_calibrated else self.arrow_to_edge_offset
        
        # Estimate box edges by adding offset in both directions
        estimated_left = arrow_x - offset
        estimated_right = arrow_x + offset
        estimated_length = estimated_right - estimated_left
        
        # Sanity check the estimation
        if estimated_length < 10 or estimated_length > width * 0.8:
            # If estimation seems wrong, use current box length if available
            if hasattr(self, 'estimated_box_length') and self.estimated_box_length > 10:
                half_length = self.estimated_box_length / 2.0
                estimated_left = arrow_x - half_length
                estimated_right = arrow_x + half_length
            else:
                # Last resort: use default box size
                default_half_length = 25.0
                estimated_left = arrow_x - default_half_length
                estimated_right = arrow_x + default_half_length
        
        return estimated_left, estimated_right
    
    def _reset_arrow_offset_calibration(self):
        """Reset arrow offset calibration when starting new fishing session"""
        self.arrow_offset_samples.clear()
        self.learned_arrow_offset = None
        self.arrow_offset_calibrated = False

    # --- INTELLIGENT SEARCH SYSTEM FUNCTIONS ---
    
    def _update_movement_tracking(self, box_center_x):
        """Track box center movement to determine direction trends"""
        if box_center_x is None:
            return
        
        # Add current position to history
        self.last_box_center_positions.append(box_center_x)
        
        # Keep only recent history
        if len(self.last_box_center_positions) > self.movement_history_size:
            self.last_box_center_positions.pop(0)
        
        # Calculate movement direction if we have enough data
        if len(self.last_box_center_positions) >= 3:
            # Look at the trend over the last few positions
            recent_positions = self.last_box_center_positions[-3:]
            total_movement = recent_positions[-1] - recent_positions[0]
            
            # Only update direction if movement is significant (>2 pixels)
            if abs(total_movement) > 2.0:
                self.last_movement_direction = 1 if total_movement > 0 else -1
            # Keep previous direction if movement is minimal
    
    def _intelligent_white_line_search(self, cv_img_bgr, width, height, rod_colors, target_line_tol):
        """
        Search for white line in the opposite direction of last known movement
        when bar tracking is completely lost
        """
        if not self.search_enabled or self.last_movement_direction == 0:
            return None
        
        # Define search region based on last movement direction
        if self.last_movement_direction > 0:
            # Bar was moving right, search on the left side
            search_start = max(0, int(width * 0.1))  # Start from 10% from left
            search_end = min(width, search_start + self.search_region_size)
            search_direction = "left"
        else:
            # Bar was moving left, search on the right side
            search_end = min(width, int(width * 0.9))  # End at 90% from left
            search_start = max(0, search_end - self.search_region_size)
            search_direction = "right"
        
        # Create a mask for the search region
        search_mask = np.zeros((height, width), dtype=np.uint8)
        search_mask[:, search_start:search_end] = 255
        
        # Search for target line (white line) in the region
        if rod_colors["target_line"] is not None:
            color_bgr = hex_to_bgr(rod_colors["target_line"])
            lower, upper = _get_bgr_bounds(color_bgr, target_line_tol)
            target_mask = cv2.inRange(cv_img_bgr, lower, upper)
            
            # Apply search region mask
            target_mask = cv2.bitwise_and(target_mask, search_mask)
            
            # Find the target line position
            target_pixel_count = self._count_pixels(target_mask)
            if target_pixel_count > 20:  # Need significant detection
                target_x = self._find_avg_x_position(target_mask)
                if target_x is not None:
                    logging.info(f"Intelligent search found white line at {target_x:.1f}px (searching {search_direction})")
                    return target_x
        
        return None
    
    def _reset_movement_tracking(self):
        """Reset movement tracking when starting new fishing session"""
        self.last_box_center_positions.clear()
        self.last_movement_direction = 0
        self.white_line_search_active = False


if __name__ == '__main__':
    # DPI awareness is already set at the top of the file
    app = Application()
    app.mainloop()