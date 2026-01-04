import tkinter as tk
from tkinter import ttk
import os
import time
import numpy as np
import threading
import sys
import logging

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
TARGET_LINE_COLOR_ALTERNATIVE_HEX = "0x151567" # New alternative target line color
INDICATOR_ARROW_COLOR_HEX = "0x848587"   # The arrows on the player-controlled rectangle
BOX_COLOR_1_HEX = "0xF1F1F1" # Used in Initializing and Fishing (Direct Track)
BOX_COLOR_2_HEX = "0xFFFFFF" # Used in Initializing and Fishing (Direct Track)
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
                
                logging.info(f"Monitor Info - Virtual: {self.virtual_screen_left},{self.virtual_screen_top} {self.virtual_screen_width}x{self.virtual_screen_height}")
                logging.info(f"Monitor Info - Primary: {self.primary_screen_width}x{self.primary_screen_height}")
            else:
                # Fallback to PyAutoGUI
                import pyautogui
                self.primary_screen_width, self.primary_screen_height = pyautogui.size()
                self.virtual_screen_left = 0
                self.virtual_screen_top = 0
                self.virtual_screen_width = self.primary_screen_width
                self.virtual_screen_height = self.primary_screen_height
                logging.warning("Using PyAutoGUI fallback for monitor detection")
                
        except Exception as e:
            logging.error(f"Failed to get monitor info: {e}")
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
            # FIX 1: Set a safer max FPS (30 FPS) to reduce memory pressure
            self.update_delay_ms = int(1000 / min(fps, 30))
            # Enforce a minimum 20ms delay (50 FPS max) to prevent racing the GC
            if self.update_delay_ms < 20: self.update_delay_ms = 20
        except (ValueError, ZeroDivisionError):
            # Fallback to a safe 15 FPS
            self.update_delay_ms = 66

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
        """
        # Retrieve the latest estimated edges from the main application state
        x0 = self.master_app.last_left_x
        x1 = self.master_app.last_right_x
        center_x = self.master_app.box_center_x

        # If any position is None, skip drawing the box.
        if x0 is None or x1 is None or center_x is None:
             return

        # Define box vertical position (positioned in the middle area like the actual game bar)
        # Make it a smaller, more realistic bar height - around 20% of total height, centered
        bar_height = capture_height * 0.2  # 20% of the total height
        box_y_top = (capture_height - bar_height) / 2  # Center it vertically
        box_y_bottom = box_y_top + bar_height

        # Ensure coordinates are integers and clamped to the canvas bounds
        x0_int = max(0, min(capture_width, int(x0)))
        x1_int = max(0, min(capture_width, int(x1)))
        center_x_int = max(0, min(capture_width, int(center_x)))

        # Draw the RED simulated box
        self.canvas.create_rectangle(
            x0_int, box_y_top,
            x1_int, box_y_bottom,
            outline="#FF0000",
            width=2,
            tags="simulated_box"
        )

        # Draw the box center line for reference (Pink)
        self.canvas.create_line(
            center_x_int, box_y_top,
            center_x_int, box_y_bottom,
            fill="#FFC0CB",
            width=1,
            dash=(3, 3),
            tags="simulated_box_center"
        )

        # Draw the target line overlay (Blue)
        target_x = self.master_app.last_target_x
        if target_x is not None:
            target_x_int = max(0, min(capture_width, int(target_x)))
            self.canvas.create_line(
                target_x_int, 0,
                target_x_int, capture_height,
                fill="#00BFFF",  # Deep sky blue
                width=3,
                tags="target_line"
            )


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

        # FIX: Only delete the transient drawings (simulated box), NOT the main image tag or "all"
        self.canvas.delete("simulated_box")
        self.canvas.delete("simulated_box_center")
        self.canvas.delete("target_line")

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

                    # Get tolerances from main app variables
                    try:
                        target_line_tol = int(self.master_app.target_line_tolerance_var.get())
                        indicator_arrow_tol = int(self.master_app.indicator_arrow_tolerance_var.get())
                        box_color_tol = int(self.master_app.box_color_tolerance_var.get())
                    except (ValueError, AttributeError): # Added AttributeError for safety during startup
                        target_line_tol, indicator_arrow_tol, box_color_tol = 1, 5, 1


                    # Mask 1: Target Line Color (Primary)
                    color1_bgr = hex_to_bgr(TARGET_LINE_COLOR_HEX)
                    lower1, upper1 = _get_bgr_bounds(color1_bgr, target_line_tol)
                    mask1 = cv2.inRange(cv_img_bgr, lower1, upper1)
                    combined_mask = cv2.bitwise_or(combined_mask, mask1)

                    # Mask 1 Alt: Target Line Color (Alternative)
                    color1_alt_bgr = hex_to_bgr(TARGET_LINE_COLOR_ALTERNATIVE_HEX)
                    lower1_alt, upper1_alt = _get_bgr_bounds(color1_alt_bgr, target_line_tol)
                    mask1_alt = cv2.inRange(cv_img_bgr, lower1_alt, upper1_alt)
                    combined_mask = cv2.bitwise_or(combined_mask, mask1_alt)

                    # Mask 2: Indicator Arrow Color
                    color2_bgr = hex_to_bgr(INDICATOR_ARROW_COLOR_HEX)
                    lower2, upper2 = _get_bgr_bounds(color2_bgr, indicator_arrow_tol)
                    mask2 = cv2.inRange(cv_img_bgr, lower2, upper2)
                    combined_mask = cv2.bitwise_or(combined_mask, mask2)

                    # --- NEW: Box Color 1 (0xF1F1F1) ---
                    color3_bgr = hex_to_bgr(BOX_COLOR_1_HEX)
                    lower3, upper3 = _get_bgr_bounds(color3_bgr, box_color_tol)
                    mask3 = cv2.inRange(cv_img_bgr, lower3, upper3)
                    combined_mask = cv2.bitwise_or(combined_mask, mask3)

                    # --- NEW: Box Color 2 (0xFFFFFF) ---
                    color4_bgr = hex_to_bgr(BOX_COLOR_2_HEX)
                    lower4, upper4 = _get_bgr_bounds(color4_bgr, box_color_tol)
                    mask4 = cv2.inRange(cv_img_bgr, lower4, upper4)
                    combined_mask = cv2.bitwise_or(combined_mask, mask4)

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
            # Delete the image item if it exists to show only the black background
            if self.canvas_image_id is not None:
                self.canvas.delete(self.canvas_image_id)
                self.canvas_image_id = None
                self.photo = None # Also clear the reference to allow GC

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

        # FIX 3: Explicitly delete the canvas image item before destroying the window
        # This breaks the final reference chain between the PhotoImage and the Canvas
        if self.canvas_image_id is not None and self.canvas.winfo_exists():
            self.canvas.delete(self.canvas_image_id)
            self.canvas_image_id = None
            self.photo = None # Clear Python reference too

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
        self.title("IRUS V4 - Terms of Use")
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
        
        terms_text = f"""IRUS V4 - Terms of Use

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

        # Initialize and validate monitor setup early
        monitor_helper.refresh_monitor_info()
        logging.info("Application starting - monitor configuration initialized")

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
        self.output_debug_enabled = tk.BooleanVar(value=False) # NEW: Debug Output Toggle

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
        self.pd_clamp_var = tk.StringVar()
        # --- Auto Shake Settings ---
        self.auto_shake_enabled = tk.BooleanVar(value=False)
        self.shake_delay_ms_var = tk.StringVar()
        self.shake_pixel_tolerance_var = tk.StringVar()
        self.shake_movement_speed_var = tk.StringVar()  # pixels per step
        self.shake_movement_delay_var = tk.StringVar()  # ms between steps
        self.shake_duplicate_override_var = tk.StringVar()  # ms to wait before clicking same spot
        self.shake_mode_var = tk.StringVar(value="Click")  # "Click" or "Navigation"
        self.shake_navigation_key_var = tk.StringVar()  # "\", "#", or "]"
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

        self.load_config()

        # Setup debug logging based on configuration
        if self.output_debug_enabled.get():
            self._setup_debug_logging()
            logging.info("Application startup - debug logging enabled")

        # --- BOX SIMULATION STATE ---
        self.initialization_stage = 0
        self.initial_anchor_x = None

        self.estimated_box_length = 0.0
        self.has_calculated_length_once = False

        # Coordinates (will be updated by the thread)
        self.box_center_x = None
        self.last_left_x = None
        self.last_right_x = None

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

        self.title("IRUS V4 - Made by AsphaltCake (YT)")
        self.geometry(self.gui_geometry.get())
        self.resizable(width=True, height=True)
        self.minsize(300, 150)

        self.key_options = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

        self.setup_ui()
        
        # Check for Terms of Service acceptance (first-time startup)
        if not self.check_and_handle_terms_of_service():
            # User declined TOS, exit application
            self.destroy()
            return
            
        self.toggle_topmost()
        self.setup_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- UI, Hotkey, Config, Geometry Methods ---
    def load_config(self):
        """Loads configuration from Config.txt or uses defaults."""
        
        # Get scaled geometry values based on current screen resolution
        scaled_geom = get_scaled_geometry()
        
        default_config = {
            "GUI_GEOM": scaled_geom['GUI_GEOM'],
            "SHAKE_GEOM": scaled_geom['SHAKE_GEOM'],
            "FISH_GEOM": scaled_geom['FISH_GEOM'],
            "LIVE_FEED_POS": scaled_geom['LIVE_FEED_POS'],
            "START_STOP_KEY": "F4",
            "RESIZE_KEY": "F5",
            "FORCE_EXIT_KEY": "F6",
            "FPS": "240",
            "TOPMOST": "True",
            "SHOW_LIVE_FEED": "False",
            "AUTO_CAST": "True", # NEW CONFIG KEY
            "OUTPUT_DEBUG": "False", # NEW: Debug output configuration

            # --- NEW DEFAULTS ---
            "TARGET_LINE_TOLERANCE": "2",
            "INDICATOR_ARROW_TOLERANCE": "3",  # Updated from 2 to 3
            "BOX_COLOR_TOLERANCE": "1",
            "MIN_CONTOUR_AREA": "5",
            "TARGET_LINE_IDLE_PIXEL_THRESHOLD": "50",
            "KP": "60",
            "KD": "30",
            "TARGET_TOLERANCE_PIXELS": "2",
            "BOUNDARY_MARGIN_FACTOR": "0.6",
            "FISHING_BOX_INITIAL_LENGTH": "50",
            "AUTOCAST_HOLD_TIME": "0.5",
            "AUTOCAST_WAIT_TIME": "3",
            "PD_CLAMP": "50.0",
            # Auto Shake defaults
            "AUTO_SHAKE": "True",
            "SHAKE_DELAY": "10",
            "SHAKE_PIXEL_TOLERANCE": "2",  # Updated from 0 to 2
            "SHAKE_MOVEMENT_SPEED": "50",
            "SHAKE_MOVEMENT_DELAY": "1",
            "SHAKE_DUPLICATE_OVERRIDE": "1000",
            "SHAKE_MODE": "Click",
            "SHAKE_NAVIGATION_KEY": "\\",
            # Auto Zoom In defaults
            "AUTO_ZOOM_IN": "True",
            # Navigation mode defaults
            "NAVIGATION_RECAST_DELAY": "3.0",
            "ENTER_SPAM_DELAY": "0.1",
            "NAVIGATION_UP_DELAY": "0",
            "NAVIGATION_RIGHT_DELAY": "0",
            "NAVIGATION_ENTER_DELAY": "0"
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
        self.output_debug_enabled.set(config.get("OUTPUT_DEBUG", "False") == "True")
        # Auto Shake
        self.auto_shake_enabled.set(config.get("AUTO_SHAKE", "False") == "True")
        self.shake_delay_ms_var.set(config.get("SHAKE_DELAY", "500"))
        self.shake_pixel_tolerance_var.set(config.get("SHAKE_PIXEL_TOLERANCE", "0"))
        self.shake_movement_speed_var.set(config.get("SHAKE_MOVEMENT_SPEED", "10"))
        self.shake_movement_delay_var.set(config.get("SHAKE_MOVEMENT_DELAY", "1"))
        self.shake_duplicate_override_var.set(config.get("SHAKE_DUPLICATE_OVERRIDE", "1000"))
        self.shake_mode_var.set(config.get("SHAKE_MODE", "Click"))
        self.shake_navigation_key_var.set(config.get("SHAKE_NAVIGATION_KEY", "\\"))
        # Auto Zoom In
        self.auto_zoom_in_enabled.set(config.get("AUTO_ZOOM_IN", "False") == "True")
                # Navigation Mode
        self.navigation_recast_delay_var.set(config.get("NAVIGATION_RECAST_DELAY", "1.0"))
        self.enter_spam_delay_var.set(config.get("ENTER_SPAM_DELAY", "0.1"))
        self.navigation_up_delay_var.set(config.get("NAVIGATION_UP_DELAY", "0.15"))
        self.navigation_right_delay_var.set(config.get("NAVIGATION_RIGHT_DELAY", "0.15"))
        self.navigation_enter_delay_var.set(config.get("NAVIGATION_ENTER_DELAY", "0.25"))
        
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
        self.pd_clamp_var.set(config["PD_CLAMP"])
        
        # Log all configuration values at startup for debugging
        logging.info("=== CONFIGURATION DEBUG INFO ===")
        for key, value in sorted(config.items()):
            logging.info(f"Config: {key} = {value}")
        logging.info("=== END CONFIGURATION DEBUG INFO ===")
        
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
            "SHAKE_MOVEMENT_SPEED": self.shake_movement_speed_var.get(),
            "SHAKE_MOVEMENT_DELAY": self.shake_movement_delay_var.get(),
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
                f.write(f"OUTPUT_DEBUG={self.output_debug_enabled.get()}\n")
                # Auto Shake
                f.write(f"AUTO_SHAKE={self.auto_shake_enabled.get()}\n")
                f.write(f"SHAKE_DELAY={self.shake_delay_ms_var.get()}\n")
                f.write(f"SHAKE_PIXEL_TOLERANCE={self.shake_pixel_tolerance_var.get()}\n")
                f.write(f"SHAKE_MOVEMENT_SPEED={self.shake_movement_speed_var.get()}\n")
                f.write(f"SHAKE_MOVEMENT_DELAY={self.shake_movement_delay_var.get()}\n")
                f.write(f"SHAKE_DUPLICATE_OVERRIDE={self.shake_duplicate_override_var.get()}\n")
                f.write(f"SHAKE_MODE={self.shake_mode_var.get()}\n")
                f.write(f"SHAKE_NAVIGATION_KEY={self.shake_navigation_key_var.get()}\n")
                # Auto Zoom In
                f.write(f"AUTO_ZOOM_IN={self.auto_zoom_in_enabled.get()}\n")
                # Navigation Mode
                f.write(f"NAVIGATION_RECAST_DELAY={self.navigation_recast_delay_var.get()}\n")
                f.write(f"ENTER_SPAM_DELAY={self.enter_spam_delay_var.get()}\n")
                f.write(f"NAVIGATION_UP_DELAY={self.navigation_up_delay_var.get()}\n")
                f.write(f"NAVIGATION_RIGHT_DELAY={self.navigation_right_delay_var.get()}\n")
                f.write(f"NAVIGATION_ENTER_DELAY={self.navigation_enter_delay_var.get()}\n")

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
                f.write(f"PD_CLAMP={self.pd_clamp_var.get()}\n")

            self.gui_geometry.set(self.winfo_geometry())
            logging.info(f"Configuration saved to {CONFIG_FILE}.")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

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

        # Status at the top
        status_frame = ttk.LabelFrame(basic_tab, text="Current Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text=f"Status: {self.state}", 
                                    foreground="blue", font=('Arial', 12, 'bold'))
        self.status_label.pack()

        # Main Controls Group
        controls_frame = ttk.LabelFrame(basic_tab, text="Main Controls", padding="15")
        controls_frame.pack(fill="x", pady=(0, 10))

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

        # ==================== AUTOMATION TAB ====================
        automation_tab = ttk.Frame(notebook)
        notebook.add(automation_tab, text="🤖 Automation")

        # Auto Features
        auto_features_frame = ttk.LabelFrame(automation_tab, text="Automatic Features", padding="15")
        auto_features_frame.pack(fill="x", pady=(0, 10))

        auto_features = [
            ("🎣 Auto Cast", self.auto_cast_enabled, "Automatically cast fishing line when fish escapes"),
            ("🏃 Auto Shake", self.auto_shake_enabled, "Automatically shake rod when fish is detected"),
            ("🔍 Auto Zoom In", self.auto_zoom_in_enabled, "Automatically zoom camera for better detection")
        ]

        for text, var, tooltip in auto_features:
            feature_frame = ttk.Frame(auto_features_frame)
            feature_frame.pack(fill="x", pady=5)
            
            check = ttk.Checkbutton(feature_frame, text=text, variable=var, command=self.save_config)
            check.pack(side="left")
            ttk.Label(feature_frame, text=f"- {tooltip}", foreground="gray", font=('Arial', 8)).pack(side="left", padx=(10, 0))

        # Shake Configuration
        shake_frame = ttk.LabelFrame(automation_tab, text="Shake Configuration", padding="15")
        shake_frame.pack(fill="x", pady=(0, 10))

        # Shake Mode
        mode_frame = ttk.Frame(shake_frame)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(mode_frame, text="🎮 Shake Method:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.shake_mode_combo = ttk.Combobox(mode_frame, textvariable=self.shake_mode_var, 
                                           values=["Click", "Navigation"], width=12, state="readonly")
        self.shake_mode_combo.pack(side="left", padx=(0, 10))
        self.shake_mode_combo.bind('<<ComboboxSelected>>', self._on_shake_mode_change)
        ttk.Label(mode_frame, text="(Click = mouse clicks, Navigation = keyboard keys)", foreground="gray", font=('Arial', 8)).pack(side="left")

        # Navigation Key (conditional)
        self.navigation_key_frame = ttk.Frame(shake_frame)
        self.navigation_key_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.navigation_key_frame, text="⌨️ Navigation Key:", font=('Arial', 10)).pack(side="left", padx=(0, 10))
        self.navigation_key_combo = ttk.Combobox(self.navigation_key_frame, textvariable=self.shake_navigation_key_var,
                                               values=["\\", "#", "]"], width=5, state="readonly")
        self.navigation_key_combo.pack(side="left", padx=(0, 10))
        self.navigation_key_combo.bind('<<ComboboxSelected>>', lambda event: self.save_config())
        ttk.Label(self.navigation_key_frame, text="(Key used for navigation-based shaking)", foreground="gray", font=('Arial', 8)).pack(side="left")

        self._update_navigation_key_visibility()

        # ==================== DISPLAY TAB ====================
        display_tab = ttk.Frame(notebook)
        notebook.add(display_tab, text="🖥️ Display")

        display_options_frame = ttk.LabelFrame(display_tab, text="Display Options", padding="15")
        display_options_frame.pack(fill="x", pady=(0, 10))

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

        # Warning at the top
        warning_frame = ttk.Frame(advanced_tab)
        warning_frame.pack(fill="x", pady=(0, 10))
        warning_label = ttk.Label(warning_frame, text="⚠️ WARNING: Only modify these if you understand what they do!", 
                                foreground="red", font=('Arial', 10, 'bold'))
        warning_label.pack()

        # Create scrollable frame for advanced options
        canvas = tk.Canvas(advanced_tab)
        scrollbar = ttk.Scrollbar(advanced_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Detection Settings
        detection_frame = ttk.LabelFrame(scrollable_frame, text="Detection Settings", padding="10")
        detection_frame.pack(fill="x", pady=(0, 10), padx=10)

        detection_vars = {
            "Target Line Tolerance": (self.target_line_tolerance_var, "How precisely to match the target line color"),
            "Indicator Arrow Tolerance": (self.indicator_arrow_tolerance_var, "How precisely to match arrow indicators"),
            "Box Color Tolerance": (self.box_color_tolerance_var, "How precisely to match fishing box colors"),
            "Min Contour Area": (self.min_contour_area_var, "Minimum size for detected objects"),
            "Target Idle Threshold": (self.target_line_idle_pixel_threshold_var, "Pixels moved to consider target active"),
        }

        self._create_settings_grid(detection_frame, detection_vars)

        # Control Settings
        control_frame = ttk.LabelFrame(scrollable_frame, text="Control Settings", padding="10")
        control_frame.pack(fill="x", pady=(0, 10), padx=10)

        control_vars = {
            "Initial Box Length": (self.fishing_box_initial_length_var, "Starting size of fishing detection box"),
            "KP (Proportional Gain)": (self.kp_var, "How aggressively to respond to current error"),
            "KD (Derivative Gain)": (self.kd_var, "How much to dampen based on error change rate"),
            "Target Tolerance (Pixels)": (self.target_tolerance_pixels_var, "Acceptable distance from target"),
            "PD Clamp (+/-)": (self.pd_clamp_var, "Maximum control output limit"),
            "Boundary Margin Factor": (self.boundary_margin_factor_var, "Safety margin from screen edges"),
        }

        self._create_settings_grid(control_frame, control_vars)

        # Timing Settings
        timing_frame = ttk.LabelFrame(scrollable_frame, text="Timing Settings", padding="10")
        timing_frame.pack(fill="x", pady=(0, 10), padx=10)

        timing_vars = {
            "Autocast Hold Time (s)": (self.autocast_hold_time_var, "How long to hold cast button"),
            "Autocast Wait Time (s)": (self.autocast_wait_time_var, "Wait time before auto-casting"),
            "Shake Delay (ms)": (self.shake_delay_ms_var, "Delay between shake actions"),
            "Shake Movement Speed (px)": (self.shake_movement_speed_var, "Speed of shake mouse movements"),
            "Shake Movement Delay (ms)": (self.shake_movement_delay_var, "Delay between shake movements"),
            "Shake Duplicate Override (ms)": (self.shake_duplicate_override_var, "Override time for duplicate shake detection"),
        }

        self._create_settings_grid(timing_frame, timing_vars)

        # Navigation Settings
        nav_frame = ttk.LabelFrame(scrollable_frame, text="Navigation Settings", padding="10")
        nav_frame.pack(fill="x", pady=(0, 10), padx=10)

        nav_vars = {
            "Navigation Recast Delay (s)": (self.navigation_recast_delay_var, "Delay before recasting in navigation mode"),
            "Enter Spam Delay (s)": (self.enter_spam_delay_var, "Delay between Enter key presses"),
            "Up Arrow Delay (s)": (self.navigation_up_delay_var, "Delay for up arrow navigation"),
            "Right Arrow Delay (s)": (self.navigation_right_delay_var, "Delay for right arrow navigation"), 
            "Enter Key Delay (s)": (self.navigation_enter_delay_var, "Delay for enter key navigation"),
            "Shake Pixel Tolerance": (self.shake_pixel_tolerance_var, "Pixel tolerance for shake detection"),
        }

        self._create_settings_grid(nav_frame, nav_vars)

    def _create_settings_grid(self, parent, settings_dict):
        """Helper to create a grid of settings with labels and entries."""
        row = 0
        for label_text, (var, tooltip) in settings_dict.items():
            # Setting label
            ttk.Label(parent, text=f"{label_text}:", font=('Arial', 9)).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Setting entry
            entry = ttk.Entry(parent, textvariable=var, width=12)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            var.trace_add('write', lambda *args: self.save_config())
            
            # Tooltip
            ttk.Label(parent, text=f"({tooltip})", foreground="gray", font=('Arial', 7)).grid(
                row=row, column=2, sticky="w", padx=5, pady=2)
            
            row += 1

        parent.columnconfigure(2, weight=1)

    def _on_hotkey_change(self):
        """Called when hotkeys are changed - save config and update hotkeys immediately."""
        self.save_config()
        self.setup_hotkeys()  # Re-setup hotkeys with new values

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
            # Enable file logging
            _setup_debug_logging()
            logging.info("Debug output enabled - logging to Debug.txt")
        else:
            # Disable file logging by removing the file handler
            _disable_debug_logging()
            print("Debug output disabled - logging to Debug.txt stopped")
        self.save_config()

    def _setup_debug_logging(self):
        """Enable debug logging to file (instance method wrapper)."""
        _setup_debug_logging()

    def _disable_debug_logging(self):
        """Disable debug logging to file (instance method wrapper)."""
        _disable_debug_logging()

    def _on_shake_mode_change(self, event=None):
        """Called when shake mode is changed - save config and update navigation key visibility."""
        self.save_config()
        self._update_navigation_key_visibility()

    def _update_navigation_key_visibility(self):
        """Shows or hides the navigation key dropdown based on shake mode."""
        if self.shake_mode_var.get() == "Navigation":
            self.navigation_key_frame.pack(fill="x", pady=5)
        else:
            self.navigation_key_frame.pack_forget()

    # --- Other Helper Methods ---

    def _get_control_delay_s(self):
        """Calculates the control loop delay in seconds based on the user's selected FPS."""
        try:
            fps = int(self.fps_var.get())
            if fps <= 0: return 0.033 # Safety default to 30 FPS
            delay = 1.0 / fps
            return max(0.001, delay) # Ensure a minimum 1ms delay (0.001 seconds)
        except ValueError:
            return 0.033 # Default to 30 FPS

    def on_close(self):
        logging.info("Application closing...")
        self._stop_automation(exit_clean=True)
        self.save_config()
        if self.feedback_window:
            self.feedback_window.close()
        self.destroy()

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

        # RESET AUTO CAST TIMER
        # The auto-cast logic will handle the timer reset if enabled

        # Update main status label
        self.status_label.config(text=f"Status: {self.state} (FPS: {target_fps})", foreground="blue")

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
        self.after(0, self.status_label.config, {'text': display_text, 'foreground': 'blue'})
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
        self.status_label.config(text="Status: IDLE", foreground="blue")
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
                self.after(0, self.status_label.config, {'text': "Status: CRITICAL ERROR", 'foreground': 'red'})
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
                # Action: HOLD LEFT CLICK (Cast)
                pyautogui.mouseDown(button='left')
                self.is_holding_click = True
                self.last_rod_cast_time = current_time  # Track when rod was cast
                self.auto_cast_next_action_time = current_time + hold_time
                logging.info(f"CLICK_MODE: HOLD ({hold_time}s)")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode: HOLD)", 'foreground': 'orange'})

            else:
                # Action: RELEASE LEFT CLICK
                pyautogui.mouseUp(button='left')
                self.is_holding_click = False
                self.auto_cast_next_action_time = current_time + wait_time
                logging.info(f"CLICK_MODE: RELEASE ({wait_time}s wait) - rod cast time recorded")
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode: WAIT {wait_time}s)", 'foreground': 'blue'})
                
        # SAFETY AUTO-RECAST: Ensure we always recast after a maximum timeout (Click mode only)
        if self.last_rod_cast_time > 0 and self.state == "IDLE":
            max_wait_time = wait_time + 10.0  # Add 10 second safety buffer
            time_since_cast = current_time - self.last_rod_cast_time
            
            if time_since_cast >= max_wait_time:
                logging.warning(f"CLICK_MODE SAFETY AUTO-RECAST: {time_since_cast:.1f}s since last cast (max {max_wait_time:.1f}s), forcing recast in IDLE state")
                self.auto_cast_next_action_time = 0.0  # Force immediate recast
                self.last_rod_cast_time = 0.0  # Reset timer
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (ClickMode Safety Auto-Recast)", 'foreground': 'orange'})

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
            self.after(0, self.status_label.config, {'text': f"Status: NAVIGATION (Setting up)", 'foreground': 'magenta'})
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
                self.after(0, self.status_label.config, {'text': f"Status: IDLE (NavMode: Casting rod)", 'foreground': 'orange'})
            else:
                # Action: RELEASE LEFT CLICK and transition to RECAST_WAIT
                logging.info(f"NAV_MODE: About to RELEASE mouse for rod cast completion")
                pyautogui.mouseUp(button='left')
                self.is_holding_click = False
                self.state = "RECAST_WAIT"
                self.navigation_recast_start_time = current_time
                logging.info("NAV_MODE: Rod cast complete (mouse released) -> RECAST_WAIT (scanning for white pixels)")
                self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Scanning for 0xFFFFFF)", 'foreground': 'cyan'})

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
            self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Navigation complete)", 'foreground': 'cyan'})
                    
        except Exception as e:
            logging.error(f"Error in navigation: {e}")
            # Fallback to RECAST_WAIT if there's an error
            self.state = "RECAST_WAIT"
            self.navigation_recast_start_time = current_time

    def _perform_navigation_sequence(self):
        """
        Perform the navigation key sequence: navigation key ONCE, up 5 times, right 5 times, enter ONCE.
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
            
            # Get navigation key and delays
            nav_key = self.shake_navigation_key_var.get()
            
            try:
                up_delay = float(self.navigation_up_delay_var.get())
            except ValueError:
                up_delay = 0.15
                
            try:
                right_delay = float(self.navigation_right_delay_var.get())
            except ValueError:
                right_delay = 0.15
                
            try:
                enter_delay = float(self.navigation_enter_delay_var.get())
            except ValueError:
                enter_delay = 0.25
            
            logging.info(f"Navigation: Starting pynput key sequence (Roblox-compatible) with up_delay={up_delay}s, right_delay={right_delay}s, enter_delay={enter_delay}s...")
            
            # Add a pause before starting to ensure game is ready
            time.sleep(0.2)
            
            # Send navigation key ONCE (using pynput)
            logging.info(f"Navigation: About to press navigation key '{nav_key}' with pynput")
            kb.press(nav_key)
            time.sleep(0.1)
            kb.release(nav_key)
            logging.info(f"Navigation: Pressed navigation key '{nav_key}' (pynput)")
            time.sleep(0.3)
            
            # Send up arrow 5 times (using pynput)
            logging.info("Navigation: About to press up arrow 5 times with pynput")
            for i in range(5):
                kb.press(Key.up)
                time.sleep(0.1)
                kb.release(Key.up)
                logging.info(f"Navigation: Pressed up arrow {i+1}/5 (pynput)")
                time.sleep(up_delay)
            logging.info("Navigation: Completed up arrow 5 times (pynput)")
            
            time.sleep(0.2)
            
            # Send right arrow 5 times (using pynput)  
            logging.info("Navigation: About to press right arrow 5 times with pynput")
            for i in range(5):
                kb.press(Key.right)
                time.sleep(0.1)
                kb.release(Key.right)
                logging.info(f"Navigation: Pressed right arrow {i+1}/5 (pynput)")
                time.sleep(right_delay)
            logging.info("Navigation: Completed right arrow 5 times (pynput)")
            
            time.sleep(0.3)
            
            # Send enter ONCE (using pynput)
            logging.info("Navigation: About to press enter with pynput")
            kb.press(Key.enter)
            time.sleep(0.1)
            kb.release(Key.enter)
            logging.info("Navigation: Pressed enter (pynput)")
            
            # Add configurable delay after enter
            time.sleep(enter_delay)
            logging.info(f"Navigation: Completed enter delay ({enter_delay}s)")
            
        except Exception as e:
            logging.error(f"Error performing navigation sequence: {e}")
            time.sleep(0.1)
            kb.release(Key.enter)
            logging.info("Navigation: Pressed enter (pynput)")
            
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
                target_line_bgr = hex_to_bgr(TARGET_LINE_COLOR_HEX)
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
                        logging.info("RECAST_WAIT: Target line found, transitioning to FISHING")
                        self.state = "FISHING"
                        self.last_rod_cast_time = 0.0  # Reset rod cast timer since we're fishing
                        self.after(0, self.status_label.config, {'text': f"Status: FISHING (Target line detected)", 'foreground': 'green'})
                        return
                        
                    # CRITICAL: Reset the recast timer while white pixels are present
                    # This prevents automatic recasting while fish is hooked
                    self.navigation_recast_start_time = current_time
                    self.after(0, self.status_label.config, {'text': f"Status: RECAST_WAIT (Spamming Enter)", 'foreground': 'yellow'})
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
                        logging.info("RECAST_WAIT: Recast delay exceeded, returning to IDLE")
                        self.state = "IDLE"
                        self.auto_cast_next_action_time = 0.0  # Immediate recast
                        self.last_rod_cast_time = 0.0  # Reset rod cast timer to allow immediate recast
                        # Reset navigation rod cast flag so it can cast again
                        if hasattr(self, 'navigation_rod_cast_done'):
                            delattr(self, 'navigation_rod_cast_done')
                            logging.info("RECAST_WAIT: Reset navigation_rod_cast_done flag for new cast cycle")
                        self.after(0, self.status_label.config, {'text': f"Status: IDLE (Recasting)", 'foreground': 'blue'})
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
            
            # Use HoughCircles with STRICTER parameters to reduce false positives
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,           # Inverse ratio of accumulator resolution
                minDist=80,     # INCREASED: Minimum distance between circle centers (was 50)
                param1=100,     # INCREASED: Upper threshold for edge detection (was 50)
                param2=50,      # INCREASED: Accumulator threshold for center detection (was 30)
                minRadius=50,   # INCREASED: Minimum circle radius (was 20) - SHAKE buttons are substantial
                maxRadius=120   # DECREASED: Maximum circle radius (was 200) - focus on SHAKE button size
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                # Additional filtering: Only accept circles with good radius range for SHAKE buttons
                good_circles = []
                for (x, y, r) in circles:
                    # SHAKE buttons are typically 50-120 pixels radius
                    if 50 <= r <= 120:
                        good_circles.append((x, y, r))
                
                if good_circles:
                    # Return the largest good circle (most likely to be SHAKE button)
                    largest_circle = max(good_circles, key=lambda c: c[2])
                    x, y, r = largest_circle
                    logging.info(f"AutoShake: Found STRICT circle at local ({x}, {y}) with radius {r}")
                    return x, y
            
            # Remove backup contour detection - too prone to false positives
            # Only use the strict HoughCircles detection
            return None, None
            
            for contour in contours:
                # Calculate contour area and perimeter
                area = cv2.contourArea(contour)
                if area < 100:  # Skip very small contours
                    continue
                    
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                # Calculate circularity (4π * area / perimeter²)
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # If circularity is close to 1.0, it's likely a circle
                if 0.7 <= circularity <= 1.3:
                    # Get centroid of the contour
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        logging.info(f"AutoShake: Found circular contour at local ({cx}, {cy})")
                        return cx, cy
            
            return None, None
            
        except Exception as e:
            logging.error(f"Circle detection error: {e}")
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
            
            # NEW: Use circle detection instead of white pixel detection
            col, row = self._detect_shake_circles(cv_img_bgr)
            
            if col is None or row is None:
                # No circles found
                return
                
            # Calculate absolute screen coordinates (multi-monitor aware)
            click_x = sx + int(col)
            click_y = sy + int(row)
            
            # Debug multi-monitor coordinates
            logging.info(f"AutoShake Debug: ShakeArea at ({sx},{sy}) size {sw}x{sh}")
            logging.info(f"AutoShake Debug: Found circle at local ({col},{row}) -> screen ({click_x},{click_y})")
            
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
                
                # Increased tolerance for circle detection (was ±5, now ±10 pixels)
                # Circle detection can have variations, but we have SHAKE_DUPLICATE_OVERRIDE failsafe
                is_same_spot = abs(predicted_final_x - lastx) <= 10 and abs(predicted_final_y - lasty) <= 10
                
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
                
                # Send mouse down event (hardware level)
                windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                
                # Brief hold time (like human click)
                time.sleep(0.015)  # 15ms hold time
                
                # Send mouse up event (hardware level)
                windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                
                logging.info(f"AutoShake: Instant teleport + click complete at ({final_x}, {final_y})")
                
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
                    pyautogui.click(x=click_x, y=click_y)
                    logging.info(f"AutoShake: Fallback pyautogui click at ({click_x},{click_y})")
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
        Implements the 'Size-Swap-Anchor' logic, used when direct color tracking fails.
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

        # --- PHASE 2: State Swap (Calculate Box Size) ---
        if holding_swapped and self.last_indicator_x is not None:

            # This block is used both in initialization and after.
            if self.has_calculated_length_once:
                # Normal Operation: Calculate length and set new anchor

                if not self.is_holding_click:
                    # Swapped to RELEASE (Indicator now on LEFT edge). Last indicator was RIGHT edge.
                    new_length = abs(self.last_indicator_x - indicator_centroid_x)

                    if 10 < new_length < width:
                        self.estimated_box_length = new_length
                        logging.info(f"Arrow Fallback: Box size re-measured at {new_length:.1f}px (Hold->Release swap).")

                    # Set new anchor point
                    self.last_left_x = indicator_centroid_x
                    self.last_right_x = self.last_left_x + self.estimated_box_length

                else: # self.is_holding_click is True: Swapped to HOLDING (Indicator now on RIGHT edge). Last indicator was LEFT edge.
                    new_length = abs(indicator_centroid_x - self.last_indicator_x)

                    if 10 < new_length < width:
                        self.estimated_box_length = new_length
                        logging.info(f"Arrow Fallback: Box size re-measured at {new_length:.1f}px (Release->Hold swap).")

                    # Set new anchor point
                    self.last_right_x = indicator_centroid_x
                    self.last_left_x = self.last_right_x - self.estimated_box_length

        # --- PHASE 3: No State Swap (Move Fixed-Size Box) ---
        elif self.has_calculated_length_once:

            # The box keeps its fixed self.estimated_box_length and moves with the current anchor

            if not self.is_holding_click:
                # Indicator is on the LEFT edge. Anchor the left side to the arrow.
                self.last_left_x = indicator_centroid_x
                self.last_right_x = self.last_left_x + self.estimated_box_length

            else: # self.is_holding_click is True
                # Indicator is on the RIGHT edge. Anchor the right side to the arrow.
                self.last_right_x = indicator_centroid_x
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


        # Get tuning parameters safely
        try:
            target_line_tol = int(self.target_line_tolerance_var.get())
            indicator_arrow_tol = int(self.indicator_arrow_tolerance_var.get())
            box_color_tol = int(self.box_color_tolerance_var.get())
            idle_threshold = int(self.target_line_idle_pixel_threshold_var.get())
            KP = float(self.kp_var.get())
            KD = float(self.kd_var.get())
            target_tol_px = float(self.target_tolerance_pixels_var.get())
            boundary_factor = float(self.boundary_margin_factor_var.get())
            pd_clamp = float(self.pd_clamp_var.get())
        except (ValueError, AttributeError):
            logging.error("Invalid non-numeric value in tuning parameters. Using defaults for this frame.")
            target_line_tol, indicator_arrow_tol, box_color_tol, idle_threshold = 1, 5, 1, 50
            KP, KD, target_tol_px, boundary_factor, pd_clamp = 0.5, 10.0, 2.0, 0.6, 50.0

        # 3. Color Detection (Using Specific Tolerances)

        # Target Line Color (Primary & Alternative)
        color1_bgr = hex_to_bgr(TARGET_LINE_COLOR_HEX)
        lower1, upper1 = _get_bgr_bounds(color1_bgr, target_line_tol)
        mask_primary = cv2.inRange(cv_img_bgr, lower1, upper1)

        color1_alt_bgr = hex_to_bgr(TARGET_LINE_COLOR_ALTERNATIVE_HEX)
        lower1_alt, upper1_alt = _get_bgr_bounds(color1_alt_bgr, target_line_tol)
        mask_alternative = cv2.inRange(cv_img_bgr, lower1_alt, upper1_alt)

        target_line_mask = cv2.bitwise_or(mask_primary, mask_alternative)
        target_line_pixel_count = self._count_pixels(target_line_mask)
        target_line_x = self._find_avg_x_position(target_line_mask)

        # Indicator Arrow Color (For Fallback/Initialization)
        color2_bgr = hex_to_bgr(INDICATOR_ARROW_COLOR_HEX)
        lower2, upper2 = _get_bgr_bounds(color2_bgr, indicator_arrow_tol)
        indicator_arrow_mask = cv2.inRange(cv_img_bgr, lower2, upper2)

        indicator_pixel_count = self._count_pixels(indicator_arrow_mask)
        indicator_centroid_x = self._find_indicator_centroids(indicator_arrow_mask)

        # Box Color Detection (For Direct Tracking)
        color3_bgr = hex_to_bgr(BOX_COLOR_1_HEX)
        lower3, upper3 = _get_bgr_bounds(color3_bgr, box_color_tol)
        box_mask_1 = cv2.inRange(cv_img_bgr, lower3, upper3)

        color4_bgr = hex_to_bgr(BOX_COLOR_2_HEX)
        lower4, upper4 = _get_bgr_bounds(color4_bgr, box_color_tol)
        box_mask_2 = cv2.inRange(cv_img_bgr, lower4, upper4)

        combined_box_mask = cv2.bitwise_or(box_mask_1, box_mask_2)
        box_y_coords, box_x_coords = np.where(combined_box_mask > 0)
        box_pixel_count = len(box_x_coords)

        # 4. State Machine Logic

        if self.state == "IDLE":
            # Reset tracking variables
            self.last_left_x = None; self.last_right_x = None; self.box_center_x = None

            # Transition to FISHING if Target Line (blob) AND Fishing Bar Color (pixels) are found
            if (target_line_pixel_count >= idle_threshold) and (box_pixel_count > 100):

                self.state = "FISHING"
                logging.info(f"IDLE -> FISHING. Target line and box color found.")

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
                self.state = "FISHING"
                logging.info(f"{self.state} -> FISHING. Target line and box color found.")

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
                    logging.info(f"Target line lost. Starting {self.fishing_cooldown_duration}s cooldown.")

                # Check if the cooldown has expired
                if current_time - self.lost_target_line_time >= self.fishing_cooldown_duration:
                    self.state = "IDLE"
                    logging.warning("FISHING -> IDLE. Target line lost for too long.")
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

            # --- Tracking and Control Logic starts here (target_line_x is not None) ---

            color_tracking_successful = False

            # 1. Try Direct Color Tracking (Fishing Box)
            if box_pixel_count > 100:
                actual_box_left_x = np.min(box_x_coords)
                actual_box_right_x = np.max(box_x_coords)

                new_length = actual_box_right_x - actual_box_left_x

                if 10 < new_length < width:
                    self.estimated_box_length = new_length
                    self.last_left_x = float(actual_box_left_x)
                    self.last_right_x = float(actual_box_right_x)
                    self.box_center_x = (self.last_left_x + self.last_right_x) / 2.0
                    self.has_calculated_length_once = True
                    color_tracking_successful = True
                    status_color_mode = "Direct Color Tracking"
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

                    if not self.has_calculated_length_once:
                        self._handle_initialization(indicator_centroid_x, width, target_line_x)
                        if self.initialization_stage < INIT_CLICKS_REQUIRED:
                            status_color_mode = "Arrow Fallback (Init)"
                            return
                        self._update_box_estimation(indicator_centroid_x, width)

                    else:
                        self._update_box_estimation(indicator_centroid_x, width)

                    status_color_mode = "Arrow Estimation (Fallback)"
                else:
                    status_color_mode = "Arrow Tracking Failed (Centroid error)"

            # 3. CRITICAL FALLBACK / GRACE PERIOD (New Logic for Spam Click Delay)
            tracking_fully_lost = (target_line_x is not None and not color_tracking_successful and indicator_pixel_count == 0)

            if not tracking_fully_lost:
                # Tracking is back (or was never fully lost), reset the timer
                self.tracking_lost_time = 0.0

            if tracking_fully_lost:

                if self.tracking_lost_time == 0.0:
                    self.tracking_lost_time = current_time
                    logging.info(f"Critical tracking lost (Line present). Starting {self.fishing_cooldown_duration}s grace period.")

                # --- 3a. GRACE PERIOD ACTIVE (No Spam Click - Release Mouse) ---
                if current_time - self.tracking_lost_time < self.fishing_cooldown_duration:

                    if self.is_holding_click and MOUSE_CONTROL_AVAILABLE:
                        pyautogui.mouseUp(button='left')
                        self.is_holding_click = False

                    # Reset PD state
                    self.last_error = 0.0
                    self.last_target_x = None

                    status_color_mode = "Tracking Lost (Grace Period)"
                    time_left = self.fishing_cooldown_duration - (current_time - self.tracking_lost_time)
                    status_suffix = f" | Time Left: {time_left:.2f}s"

                    # Update GUI Status for Grace Period
                    status = f"{self.state} | {status_color_mode}{status_suffix}"
                    self.after(0, self.status_label.config, {'text': f"Status: {status} | Ctrl: RELEASE | Box Len: ...px", 'foreground': 'orange'})

                    return # Skip PD control and subsequent logic

                # --- 3b. GRACE PERIOD EXPIRED (Engage Spam Click) ---
                else:
                    # Toggle the hold state every frame for spam-clicking
                    should_hold = not self.is_holding_click

                    # Set tracking to be aligned to prevent PD control runaway if it ran
                    self.box_center_x = target_line_x
                    self.last_left_x = None; self.last_right_x = None

                    # Reset PD state to prepare for recovery
                    self.last_error = 0.0
                    self.last_target_x = None

                    status_color_mode = "CRITICAL SPAM (Grace Expired)"
                    status_suffix = ""

                    # Execute Mouse Action
                    if MOUSE_CONTROL_AVAILABLE:
                        if should_hold and not self.is_holding_click:
                            pyautogui.mouseDown(button='left')
                            self.is_holding_click = True

                        elif not should_hold and self.is_holding_click:
                            pyautogui.mouseUp(button='left')
                            self.is_holding_click = False

                    # Update GUI Status for this specific fallback
                    status = f"{self.state} | {status_color_mode}{status_suffix}"
                    control_state = "HOLD" if self.is_holding_click else "RELEASE"
                    box_len = f"{self.estimated_box_length:.1f}" if self.has_calculated_length_once else "..."

                    self.after(0, self.status_label.config, {'text': f"Status: {status} | Ctrl: {control_state} | Box Len: {box_len}px", 'foreground': 'purple'})

                    return # Skip the standard PD control (Point 5)

        # --- 5. Control Logic (PD Controller & Boundary Override) - Runs ONLY IF self.state == "FISHING" ---

            # We must have both the target line and the box center estimated
            if target_line_x is not None and self.box_center_x is not None and self.has_calculated_length_once:

                error = target_line_x - self.box_center_x # Positive error means target is to the RIGHT (needs HOLD/UP)

                # Define the boundary margin in pixels
                boundary_px_margin = self.estimated_box_length * boundary_factor

                # --- A. Boundary Override Check ---
                is_near_left_boundary = (target_line_x < boundary_px_margin)
                is_near_right_boundary = (target_line_x > width - boundary_px_margin)

                if is_near_left_boundary:
                    control_signal = -100.0 # Max Release
                    status_suffix = " | Boundary Override: Max RELEASE"
                    should_hold = False
                elif is_near_right_boundary:
                    control_signal = 100.0  # Max Hold
                    status_suffix = " | Boundary Override: Max HOLD"
                    should_hold = True
                else:
                    # --- B. PD Control Calculation ---
                    P_term = KP * error
                    D_term = 0.0

                    if self.last_error is not None and time_delta > 0.001:
                        error_rate = (error - self.last_error) / time_delta
                        D_term = KD * error_rate

                    control_signal = P_term + D_term
                    control_signal = np.clip(control_signal, -pd_clamp, pd_clamp)
                    status_suffix = f" | PD Control: Signal={control_signal:+.2f}"

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

                # --- D. Execute Mouse Action
                if MOUSE_CONTROL_AVAILABLE:
                    if should_hold and not self.is_holding_click:
                        pyautogui.mouseDown(button='left')
                        self.is_holding_click = True
                    elif not should_hold and self.is_holding_click:
                        pyautogui.mouseUp(button='left')
                        self.is_holding_click = False
                        logging.debug("Mouse Up (RELEASE/SPAM)")


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
                color = '#FF4500' # Orange-Red
            elif "Dead Zone SPAM" in status:
                color = 'yellow' # Highlight spam mode
            elif "PD Control" in status or "Direct Color Tracking" in status:
                color = 'green'
            elif "Tracking Lost/Waiting" in status:
                color = 'cyan'
            else:
                color = 'cyan'

            display_status = f"Status: {status} | Ctrl: {control_state} | Box Len: {box_len}px"

            self.after(0, self.status_label.config, {'text': display_status, 'foreground': color})

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
                    logging.info("Init: Stage 2 -> Complete. Entering control mode with arrow logic.")
                    status = "Initialization complete. Entering Control Mode."
                else:
                    status = "Init: Waiting for stable release state."

        # Update GUI status during initialization
        len_str = f"({self.estimated_box_length:.1f}px)" if self.has_calculated_length_once else ""
        display_status = f"Status: {status} {len_str}"
        self.after(0, self.status_label.config, {'text': display_status, 'foreground': 'orange'})


if __name__ == '__main__':
    # DPI awareness is already set at the top of the file
    app = Application()
    app.mainloop()