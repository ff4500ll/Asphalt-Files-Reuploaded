import tkinter as tk
from tkinter import ttk
import os
import keyboard
import webbrowser
import threading
import time
from datetime import datetime
import logging
try:
    import pyautogui
    import mss
    import cv2
    import numpy as np
    from PIL import Image, ImageTk
    YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE = False

# =============================================================================
# DEBUG LOGGING SETUP
# =============================================================================
def setup_debug_logging():
    """Setup comprehensive debug logging to Debug.txt"""
    # Remove existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create Debug.txt logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d | %(levelname)8s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler('Debug.txt', mode='w', encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    logging.info("=== DEBUG LOGGING INITIALIZED ===")

# Global debug state
DEBUG_ENABLED = True

def debug_log(message, category="GENERAL"):
    """Enhanced debug logging with categories"""
    if DEBUG_ENABLED:
        logging.info(f"[{category:12}] {message}")

# =============================================================================
# GLOBAL VARIABLES FOR FISH STATE
# =============================================================================
ShakePass = False
FishingOngoing = False
NumFishLines = 0  # Number of fish lines detected (for ShakeStage)

# Middle X coordinate of the fish bar play area
MiddleOfPlayArea = 0

# Target line separation detection (set once when first valid state is detected)
TargetLineSeperation = False

# Last known bar positions (updated during detection)
LastKnownLeftBar = 0
LastKnownRightBar = 0

# Initial target calculation toggle (runs special logic only on first calculation)
InitialTargetCalculation = False

# First run target and bar line positions (set once during FirstRunUpdateFishState)
LeftTargetLine = 0
RightTargetLine = 0
LeftBar = 0
RightBar = 0

# Target line pixel gap (distance between left and right target lines in pixels)
TargetLinePixelGap = 0

# Middle positions for target lines and bars
TargetLineMiddle = 0
TargetBarMiddle = 0

# Line bar pixel difference (resolution normalized)
LineBarPixelDifference = 0

# From Side Bar Ratio (0-1 range for bar positioning)
FromSideBarRatio = 0.5

def update_middle_of_play_area():
    """
    Calculate and update the global MiddleOfPlayArea based on current fish_bar_area geometry.
    This function extracts the X coordinate and width from fish_bar_area and calculates the middle point.
    """
    global MiddleOfPlayArea
    
    try:
        # Get fish bar area from active settings
        fish_bar_area = ACTIVE_SETTINGS.get('fish_bar_area', '')
        if not fish_bar_area:
            print("⚠️ No fish_bar_area in settings, MiddleOfPlayArea remains 0")
            MiddleOfPlayArea = 0
            return
        
        # Parse geometry string format: WIDTHxHEIGHT+X+Y
        parts = fish_bar_area.replace('+', 'x').split('x')
        if len(parts) != 4:
            print(f"⚠️ Invalid fish_bar_area format: {fish_bar_area}")
            MiddleOfPlayArea = 0
            return
        
        width, height, x, y = map(int, parts)
        
        # Calculate middle X coordinate (left edge + half width)
        MiddleOfPlayArea = x + (width // 2)
        
        print(f"✅ MiddleOfPlayArea updated to: {MiddleOfPlayArea} (from area: {fish_bar_area})")
        
    except Exception as e:
        print(f"❌ Error updating MiddleOfPlayArea: {e}")
        MiddleOfPlayArea = 0

# =============================================================================
# FIRST LAUNCH CONFIG - [AI_REF:first_launch_config]
# Default values that are generated when Config.txt doesn't exist
# =============================================================================
FIRST_LAUNCH_CONFIG = {
    'hotkey_start': 'F3',
    'hotkey_stop': 'F4',
    'hotkey_change_area': 'F5',
    'hotkey_exit': 'F6',
    'always_on_top': True,
    'shake_area': '1495x796+540+287',
    'fish_bar_area': '1033x40+763+1177',
    'stage_one_time_run': True,
    'stage_first_stage': True,
    'stage_shake_stage': True,
    'stage_fish_stage': True,
    'scan_fps': 60,
    'scan_shake_fps': 10,
    'shake_timer': 1.0,  # Duplicate Circle Timeout (renamed from Failed Shake Timeout)
    'no_circle_timeout': 3.0,  # No Circle Found Timeout (new setting)
    'shake_min_radius': 50,
    'from_side_bar_ratio': 0.5,
    'fish_lost_timeout': 1.0,
    # Casting Flow Control Settings (Branch 2 enabled by default)
    'casting_enable_first_stage': True,
    'casting_delay1_enabled': False,
    'casting_delay1_duration': 0.5,
    'casting_perfect_cast_enabled': False,
    'casting_delay2_enabled': False,
    'casting_delay2_duration': 0.5,
    'casting_delay3_enabled': True,
    'casting_delay3_duration': 0.5,
    'casting_hold_enabled': True,
    'casting_delay4_enabled': True,
    'casting_delay4_duration': 0.5,
    'casting_release_enabled': True,
    'casting_delay5_enabled': True,
    'casting_delay5_duration': 0.5
}

def update_first_launch_config():  # [AI_REF:first_launch_config_scaling]
    """
    Scale FIRST_LAUNCH_CONFIG area coordinates based on current screen resolution.
    This function processes shake_area and fish_bar_area coordinates to adapt
    from the original 2560x1440 reference resolution to current screen size.
    
    Called once at application startup before any usage of FIRST_LAUNCH_CONFIG.
    """
    global FIRST_LAUNCH_CONFIG
    
    try:
        import tkinter as tk_temp
        temp_root = tk_temp.Tk()
        temp_root.withdraw()  # Hide the temporary window
        
        # Get current screen dimensions
        current_width = temp_root.winfo_screenwidth()
        current_height = temp_root.winfo_screenheight()
        
        temp_root.destroy()  # Clean up temporary window
        
        # Reference resolution (original design resolution)
        ref_width = 2560
        ref_height = 1440
        
        # Calculate scaling factors
        width_scale = current_width / ref_width
        height_scale = current_height / ref_height
        
        print(f"Screen scaling: {current_width}x{current_height} (scale factors: {width_scale:.3f}x, {height_scale:.3f}y)")
        
        # Process shake_area and fish_bar_area
        for area_key in ['shake_area', 'fish_bar_area']:
            if area_key in FIRST_LAUNCH_CONFIG:
                geometry = FIRST_LAUNCH_CONFIG[area_key]
                
                # Parse geometry string (e.g., "800x400+100+100")
                try:
                    # Split into size and position parts
                    size_pos = geometry.split('+')
                    if len(size_pos) >= 3:  # Format: "WxH+X+Y"
                        size_part = size_pos[0]  # "800x400"
                        x_pos = int(size_pos[1])  # 100
                        y_pos = int(size_pos[2])  # 100
                        
                        # Parse width and height
                        width_height = size_part.split('x')
                        if len(width_height) == 2:
                            width = int(width_height[0])
                            height = int(width_height[1])
                            
                            # Scale coordinates
                            scaled_width = int(width * width_scale)
                            scaled_height = int(height * height_scale)
                            scaled_x = int(x_pos * width_scale)
                            scaled_y = int(y_pos * height_scale)
                            
                            # Reconstruct geometry string
                            scaled_geometry = f"{scaled_width}x{scaled_height}+{scaled_x}+{scaled_y}"
                            
                            print(f"Scaled {area_key}: {geometry} → {scaled_geometry}")
                            FIRST_LAUNCH_CONFIG[area_key] = scaled_geometry
                        
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse {area_key} geometry '{geometry}': {e}")
                    # Keep original value if parsing fails
        
        # Scale shake_min_radius based on screen width (2560 reference)
        if 'shake_min_radius' in FIRST_LAUNCH_CONFIG:
            original_radius = FIRST_LAUNCH_CONFIG['shake_min_radius']
            scaled_radius = int(original_radius * width_scale)
            print(f"Scaled shake_min_radius: {original_radius} → {scaled_radius}")
            FIRST_LAUNCH_CONFIG['shake_min_radius'] = scaled_radius
        
    except Exception as e:
        print(f"Warning: Screen scaling failed, using original coordinates: {e}")
        # Continue with original FIRST_LAUNCH_CONFIG if scaling fails

# Available keyboard keys for hotkey selection - [AI_REF:keyboard_keys]
KEYBOARD_KEYS = [
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "Space", "Enter", "Esc", "Tab", "Backspace",
    "Insert", "Delete", "Home", "End", "Page Up", "Page Down",
    "Left", "Right", "Up", "Down",
]


# =============================================================================


# =============================================================================
# ACTIVE SETTINGS
# Live in-memory configuration that updates from GUI changes
# Saved to Config.txt only when application closes
# =============================================================================

# Global active settings dictionary - updated in real-time by GUI - [AI_REF:active_settings]
ACTIVE_SETTINGS = {
    'hotkey_start': 'f1',
    'hotkey_stop': 'f2', 
    'hotkey_change_area': 'f3',
    'hotkey_exit': 'f4',
    'always_on_top': True,
    'shake_area': '800x400+100+100',
    'fish_bar_area': '600x50+200+500',
    'stage_one_time_run': True,
    'stage_first_stage': True,
    'stage_shake_stage': True,
    'stage_fish_stage': True,
    'scan_fps': 60,
    'scan_shake_fps': 10,
    'shake_timer': 1.0,  # Duplicate Circle Timeout (renamed from Failed Shake Timeout)
    'no_circle_timeout': 3.0,  # No Circle Found Timeout (new setting)
    'shake_min_radius': 10,
    'from_side_bar_ratio': 0.5,
    'fish_lost_timeout': 1.0,
    # Casting Flow Control Settings (Branch 2 enabled by default)
    'casting_enable_first_stage': True,
    'casting_delay1_enabled': False,
    'casting_delay1_duration': 0.5,
    'casting_perfect_cast_enabled': False,
    'casting_delay2_enabled': False,
    'casting_delay2_duration': 0.5,
    'casting_delay3_enabled': True,
    'casting_delay3_duration': 0.5,
    'casting_hold_enabled': True,
    'casting_delay4_enabled': True,
    'casting_delay4_duration': 0.5,
    'casting_release_enabled': True,
    'casting_delay5_enabled': True,
    'casting_delay5_duration': 0.5
}

def load_config():  # [AI_REF:load_config]
    """Load configuration from Config.txt into ACTIVE_SETTINGS.
    Returns True if config exists (normal launch).
    Returns False if config does not exist (first launch - show Terms of Use)."""
    global ACTIVE_SETTINGS
    config_file = "Config.txt"
    
    if not os.path.exists(config_file):
        # First launch - initialize with defaults but don't save yet
        ACTIVE_SETTINGS = FIRST_LAUNCH_CONFIG.copy()
        # Update MiddleOfPlayArea for first launch
        update_middle_of_play_area()
        return False  # Indicates first launch
    
    # Start with defaults, then load existing config from file
    ACTIVE_SETTINGS = FIRST_LAUNCH_CONFIG.copy()
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    # Convert boolean strings back to booleans
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    ACTIVE_SETTINGS[key] = value
    except Exception as e:
        print(f"Error loading config, using defaults: {e}")
        ACTIVE_SETTINGS = FIRST_LAUNCH_CONFIG.copy()
    
    # Update MiddleOfPlayArea after loading config
    update_middle_of_play_area()
    
    return True  # Normal launch


def save_config():  # [AI_REF:save_config]
    """Save ACTIVE_SETTINGS to Config.txt. Called when application closes."""
    config_file = "Config.txt"
    
    try:
        with open(config_file, 'w') as f:
            for key, value in ACTIVE_SETTINGS.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        pass


# =============================================================================
# FIRST LAUNCH WORKFLOW
# Modular system for first-launch processes (Terms of Use, etc.)
# Easy to extend: Add more steps by calling additional functions in sequence
# =============================================================================

def run_first_launch_workflow(root_window, on_complete_callback):
    """
    Run all first-launch processes in sequence
    To add more steps: Call additional functions before final callback
    """
    # Step 1: Terms of Use - show directly
    TermsOfUseWindow(root_window, on_complete_callback)
    
    # Future steps can be added here by calling additional classes before on_complete_callback


class TermsOfUseWindow(tk.Toplevel):
    """
    Terms of Use window - shown only on first launch
    Resolution-adaptive design for compatibility with all monitor sizes
    """
    
    def __init__(self, parent, on_accept_callback):
        super().__init__(parent)
        
        self.on_accept_callback = on_accept_callback
        
        # Window configuration - simple and big enough for all content
        self.title("Terms of Use - First Launch")
        self.geometry("800x650")  # Fixed size big enough for all elements
        self.resizable(True, True)  # Allow resize
        self.minsize(400, 250)  # Minimum size to ensure bottom section is always visible
        
        # Make this window modal (block interaction with parent)
        self.transient(parent)
        self.grab_set()
        
        # Ensure window appears on top and is visible - ALWAYS stay on top
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)  # Stay on top permanently
        
        self._create_gui()
        
        # Prevent closing without accepting/declining
        self.protocol("WM_DELETE_WINDOW", self._on_decline)
    
    def _create_gui(self):
        """
        Create modern, visually appealing Terms of Use GUI
        Uses fixed bottom section to ensure buttons are always visible
        """
        # Configure main window style
        self.configure(bg='#f0f0f0')
        
        # === BOTTOM SECTION (Pack first for priority - always visible) ===
        bottom_frame = tk.Frame(self, bg='#ecf0f1', height=140)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        bottom_frame.pack_propagate(False)  # Maintain fixed height - always visible
        
        # === HEADER SECTION (Fixed at top) ===
        header_frame = tk.Frame(self, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)  # Maintain fixed height
        
        # Main title with modern styling
        title_label = tk.Label(
            header_frame,
            text="IRUS V7",
            font=('Segoe UI', 18, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Terms of Use Agreement",
            font=('Segoe UI', 11),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitle_label.pack()
        
        # === CONTENT SECTION (Expandable - will shrink if needed) ===
        content_frame = tk.Frame(self, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        # Content container with modern styling
        content_container = tk.Frame(content_frame, bg='white', relief='ridge', bd=1)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar with custom styling
        scrollbar = tk.Scrollbar(content_container, bg='#ecf0f1', troughcolor='#bdc3c7')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)
        
        # Text widget with modern appearance
        self.content_text = tk.Text(
            content_container,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 10),
            bg='white',
            fg='#2c3e50',
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=15,
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=2)
        scrollbar.config(command=self.content_text.yview)
        
        # Insert Terms of Use content
        terms_content = """IRUS V7 - Terms of Use

By using this software, you agree to the following:



1. SUPPORT THE CREATOR

    • Please consider subscribing to AsphaltCake to support 
      continued development

    • Your support helps keep this project alive and improving

    • Upon clicking "Accept", your browser will open ONCE to 
      AsphaltCake's YouTube subscribe page

    • This will only happen when you first accept these terms, 
      not on future program launches



2. RESPECT OWNERSHIP & CREDITS

    • This software belongs to AsphaltCake - you cannot claim 
      it as your own

    • Do not remove or change the creator credits anywhere 
      in the software

    • You MAY redistribute or share this software IF you give 
      proper credit to AsphaltCake

    • When sharing, clearly state that the original creator 
      is AsphaltCake



3. NO COPY-CAT MODIFICATIONS

    • You cannot make small changes and then claim ownership

    • Changing a few lines of code doesn't make it yours

    • Do not redistribute modified versions as if you created them, you can if you credit AsphaltCake



4. USE AT YOUR OWN RISK

    • You are responsible for any consequences of using 
      this software

    • The creator (AsphaltCake) is not liable for any issues, 
      bans, or problems

    • Use this software responsibly and at your own discretion



5. CODE USE & REVERSE ENGINEERING

    • Personal Learning: You may deobfuscate or reverse engineer 
      for personal learning only

    • Sharing Allowed: You may share this software IF you credit AsphaltCake

    • Platform Sharing: When posting on any platform, forum, or 
      website, you must credit AsphaltCake as the creator

    • Private Use: You may keep reverse-engineered code for 
      personal use and education



By clicking "Accept", you agree to follow these rules and acknowledge 
that your browser will open to the YouTube subscribe page. 

Breaking these terms may result in losing access to future updates 
and potential legal action.""".strip()
        
        self.content_text.insert('1.0', terms_content)
        self.content_text.config(state='disabled')  # Read-only
        
        # Checkbox section with modern styling
        checkbox_frame = tk.Frame(bottom_frame, bg='#ecf0f1')
        checkbox_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.accept_var = tk.BooleanVar(value=False)
        self.agree_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="I have read and accept the Terms of Use",
            variable=self.accept_var,
            command=self._update_accept_button,
            font=('Segoe UI', 10, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            activebackground='#ecf0f1',
            activeforeground='#2c3e50',
            selectcolor='white'
        )
        self.agree_checkbox.pack(anchor=tk.CENTER)
        
        # Button section with modern styling
        button_frame = tk.Frame(bottom_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Modern button styling
        button_style = {
            'font': ('Segoe UI', 11, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'padx': 30,
            'pady': 8,
            'cursor': 'hand2'
        }
        
        # Decline button with red theme
        self.decline_button = tk.Button(
            button_frame,
            text="Decline",
            command=self._on_decline,
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            **button_style
        )
        self.decline_button.pack(side=tk.LEFT, padx=(20, 5))
        
        # Accept button with green theme (disabled initially)
        self.accept_button = tk.Button(
            button_frame,
            text="Accept",
            command=self._on_accept,
            bg='#95a5a6',
            fg='#7f8c8d',
            state='disabled',
            **button_style
        )
        self.accept_button.pack(side=tk.RIGHT, padx=(5, 20))
    
    def _update_accept_button(self):
        """Enable Accept button only when checkbox is checked - with modern styling"""
        if self.accept_var.get():
            self.accept_button.config(
                state='normal',
                bg='#27ae60',
                fg='white',
                activebackground='#229954',
                activeforeground='white'
            )
        else:
            self.accept_button.config(
                state='disabled',
                bg='#95a5a6',
                fg='#7f8c8d',
                activebackground='#95a5a6',
                activeforeground='#7f8c8d'
            )
    
    def _auto_subscribe_youtube(self):  # [AI_REF:youtube_subscribe]
        """Open YouTube channel and search for subscribe button"""
        if not YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE:
            self._finish_accept()
            return
        
        try:
            # Open YouTube channel (same as p.py - no window manipulation)
            youtube_url = "https://www.youtube.com/@AsphaltCake?sub_confirmation=1"
            webbrowser.open(youtube_url)
            
            # Wait for page to load properly (same as p.py)
            time.sleep(3)
            
            # Search for subscribe button for 3 seconds (using p.py working logic)
            target_color_bgr = (255, 166, 62)  # Orange subscribe button color (from p.py)
            tolerance = 0
            search_start_time = time.time()
            found_button = False
            
            while time.time() - search_start_time < 3.0 and not found_button:
                try:
                    with mss.mss() as sct:
                        monitors = sct.monitors[1:]  # All monitors
                        for monitor in monitors:
                            # Calculate middle area coordinates first (35% margin from each edge)
                            full_width = monitor['width']
                            full_height = monitor['height']
                            
                            margin_x = int(full_width * 0.35)  # 35% margin from left and right
                            margin_y = int(full_height * 0.35)  # 35% margin from top and bottom
                            
                            # Define middle section area to capture
                            middle_area = {
                                'left': monitor['left'] + margin_x,
                                'top': monitor['top'] + margin_y,
                                'width': full_width - (margin_x * 2),
                                'height': full_height - (margin_y * 2)
                            }
                            
                            print(f"Scanning middle section: {middle_area['width']}x{middle_area['height']} of {full_width}x{full_height}")
                            
                            # Capture only the middle section directly
                            screenshot = sct.grab(middle_area)
                            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                            cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            
                            # Color detection with tolerance
                            lower_bound = np.array([max(0, c - tolerance) for c in target_color_bgr])
                            upper_bound = np.array([min(255, c + tolerance) for c in target_color_bgr])
                            mask = cv2.inRange(cv_img, lower_bound, upper_bound)
                            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            # Accept all contours, even 1 pixel areas
                            
                            if contours:
                                largest_contour = max(contours, key=cv2.contourArea)
                                x, y, w, h = cv2.boundingRect(largest_contour)
                                center_x = x + w // 2
                                center_y = y + h // 2
                                
                                # Convert to global coordinates (add middle area offset)
                                global_x = center_x + middle_area['left']
                                global_y = center_y + middle_area['top']
                                
                                if global_x > 0 and global_y > 0:
                                    pyautogui.click(global_x, global_y)
                                    found_button = True
                                    time.sleep(0.5)  # Brief pause after clicking
                                    break
                        
                        if found_button:
                            break
                            
                except Exception as e:
                    pass
                
                if not found_button:
                    time.sleep(0.1)  # Small delay between checks
            
        except Exception as e:
            pass
        finally:
            # Always continue to GUI
            self._finish_accept()
    
    def _finish_accept(self):
        """Complete the accept process and show main GUI"""
        save_config()  # Save initial config to create Config.txt
        self.grab_release()
        self.destroy()
        
        # Call the callback to continue (next step or show main GUI)
        if self.on_accept_callback:
            self.on_accept_callback()
    
    def _on_accept(self):
        """Handle Accept button - close window immediately and run process in background"""
        # Close the Terms of Use window immediately
        self.grab_release()
        self.destroy()
        
        # Run auto-subscribe in separate thread in background
        subscribe_thread = threading.Thread(target=self._auto_subscribe_youtube, daemon=True)
        subscribe_thread.start()
    
    def _on_decline(self):
        """Handle Decline button - close entire application"""
        self.grab_release()
        self.destroy()
        self.master.quit()  # Exit the application


# =============================================================================
# AREA OVERLAY SYSTEM - [AI_REF:area_overlay_system]
# Draggable, resizable transparent overlay windows for area visualization
# =============================================================================
class AreaOverlay(tk.Toplevel):
    """
    Transparent overlay window for visualizing areas (ShakeArea, FishBarArea)
    Features: Draggable, resizable from all edges/corners, always on top, transparent
    """
    
    def __init__(self, geometry="100x100+100+100", color="red", title="Area", alpha=0.3, on_close_callback=None, freeze_overlay=None):
        super().__init__()
        
        self.on_close_callback = on_close_callback
        self.color = color
        self.alpha = alpha
        self.freeze_overlay = freeze_overlay
        
        # Window configuration
        self.title(title)
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Always on top
        self.attributes('-alpha', alpha)  # Transparency
        
        # Parse and set geometry
        self.geometry(geometry)
        
        # Configure background color
        self.configure(bg=color)
        
        # Dragging variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragging = False
        
        # Resizing variables
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0
        self.resize_start_window_x = 0
        self.resize_start_window_y = 0
        self.resizing = False
        self.resize_mode = None  # 'corner', 'edge_top', 'edge_bottom', 'edge_left', 'edge_right'
        
        # Edge/corner detection margins (pixels from edge)
        self.edge_margin = 10
        
        # Screen freeze variables
        self.frozen_screen = None
        self.freeze_overlay = None
        
        # Bind mouse events for dragging and resizing
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)  # Will be overridden during resize
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Motion>', self._on_motion)
        # Mouse events bound for area interaction
        
        # Create border indicators (small labels at edges/corners for visual feedback)
        self._create_border_indicators()
        
        # Update initial cursor
        self.update_idletasks()
        self._update_cursor(None)
    
    def _create_border_indicators(self):
        """Create small visual indicators at edges only"""
        # Edge indicators (small rectangles at middle of each edge)
        edges = [
            ('top', 0.5, 0, tk.N),    # Top edge center
            ('bottom', 0.5, 1.0, tk.S), # Bottom edge center
            ('left', 0, 0.5, tk.W),   # Left edge center
            ('right', 1.0, 0.5, tk.E) # Right edge center
        ]
        
        for edge_name, relx, rely, anchor in edges:
            indicator = tk.Label(
                self,
                text='▬' if edge_name in ['top', 'bottom'] else '▮',
                fg=self.color,
                bg=self.color,
                font=('Arial', 6),
                borderwidth=0,
                highlightthickness=0
            )
            indicator.place(relx=relx, rely=rely, anchor=anchor)
    
    def _get_resize_mode(self, x, y):
        """Determine resize mode based on mouse position - edges only, no corners"""
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Check edges only (no corner detection)
        # Top edge
        if y <= self.edge_margin:
            return 'n'
        # Bottom edge
        elif y >= height - self.edge_margin:
            return 's'
        # Left edge
        elif x <= self.edge_margin:
            return 'w'
        # Right edge
        elif x >= width - self.edge_margin:
            return 'e'
        
        # Center area (dragging)
        return 'move'
    
    def _get_cursor_for_mode(self, mode):
        """Get appropriate cursor for resize mode - edges only"""
        cursors = {
            'n': 'size_ns',
            's': 'size_ns',
            'w': 'size_we',
            'e': 'size_we',
            'move': 'fleur'
        }
        return cursors.get(mode, 'arrow')
    
    def _on_motion(self, event):
        """Handle mouse motion for cursor updates"""
        if not self.dragging and not self.resizing:
            mode = self._get_resize_mode(event.x, event.y)
            cursor = self._get_cursor_for_mode(mode)
            try:
                self.config(cursor=cursor)
            except:
                pass  # Ignore cursor errors
    
    def _update_cursor(self, mode):
        """Update cursor based on mode"""
        if mode:
            cursor = self._get_cursor_for_mode(mode)
            try:
                self.config(cursor=cursor)
            except:
                pass  # Ignore cursor errors
    
    def _on_click(self, event):
        """Handle mouse click - start drag or resize"""
        mode = self._get_resize_mode(event.x, event.y)
        
        if mode == 'move':
            # Start dragging
            self.dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        else:
            # Start resizing with frozen screen
            self.resizing = True
            self.resize_mode = mode
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_width = self.winfo_width()
            self.resize_start_height = self.winfo_height()
            self.resize_start_window_x = self.winfo_x()
            self.resize_start_window_y = self.winfo_y()
            
            # Debug print
            print(f"Starting resize mode: {mode} at {event.x_root}, {event.y_root}")
            
            # Screen is frozen, no zoom window needed
            
        self._update_cursor(mode)
    
    def _on_drag(self, event):
        """Handle mouse drag - perform drag or resize"""
        if self.dragging:
            # Calculate new position with pixel snapping
            new_x = self.winfo_x() + (event.x - self.drag_start_x)
            new_y = self.winfo_y() + (event.y - self.drag_start_y)
            
            # Snap to pixel grid (round to nearest pixel)
            new_x = round(new_x)
            new_y = round(new_y)
            
            # Move window
            self.geometry(f"+{new_x}+{new_y}")
            
        elif self.resizing:
            # Calculate deltas from resize start point
            dx = event.x_root - self.resize_start_x
            dy = event.y_root - self.resize_start_y
            
            # Start with original position and size
            new_x = self.resize_start_window_x
            new_y = self.resize_start_window_y
            new_width = self.resize_start_width
            new_height = self.resize_start_height
            
            # Apply resize based on mode (edges only)
            if self.resize_mode == 'n':  # North (top)
                new_y = self.resize_start_window_y + dy
                new_height = self.resize_start_height - dy
            elif self.resize_mode == 's':  # South (bottom) 
                new_height = self.resize_start_height + dy
            elif self.resize_mode == 'w':  # West (left)
                new_x = self.resize_start_window_x + dx
                new_width = self.resize_start_width - dx
            elif self.resize_mode == 'e':  # East (right)
                new_width = self.resize_start_width + dx
            
            # Enforce smaller minimum size and snap to pixels
            min_size = 20  # Smaller minimum size for better flexibility
            if new_width < min_size:
                if self.resize_mode == 'w':
                    new_x = self.resize_start_window_x + (self.resize_start_width - min_size)
                new_width = min_size
            if new_height < min_size:
                if self.resize_mode == 'n':
                    new_y = self.resize_start_window_y + (self.resize_start_height - min_size)
                new_height = min_size
            
            # Snap all values to pixel grid
            new_x = round(new_x)
            new_y = round(new_y)
            new_width = round(new_width)
            new_height = round(new_height)
            
            # Apply new geometry
            self.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            
            # Resizing without zoom
    
    def _on_release(self, event):
        """Handle mouse release - stop drag or resize"""
        if self.dragging:
            self.dragging = False
            
        elif self.resizing:
            self.resizing = False
            self.resize_mode = None
            # Resize complete
            # Restore normal drag binding
            self.bind('<B1-Motion>', self._on_drag)
            
        # Reset cursor
        try:
            self.config(cursor='arrow')
        except:
            pass
        
        # Call callback to save geometry if provided
        if self.on_close_callback:
            self.on_close_callback()
    
    def _freeze_screen(self):
        """Capture and freeze the current screen with full-screen overlay (p.py method)"""
        if not YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE:
            print("Screen capture libraries not available - skipping freeze")
            return
            
        try:
            # Get cursor position to determine which monitor to capture (like p.py)
            cursor_x = self.winfo_pointerx()
            cursor_y = self.winfo_pointery()
            
            with mss.mss() as sct:
                # Find which monitor the cursor is on (like p.py)
                current_monitor = None
                for i, monitor in enumerate(sct.monitors[1:], 1):  # Skip first monitor (all monitors combined)
                    if (monitor["left"] <= cursor_x < monitor["left"] + monitor["width"] and
                        monitor["top"] <= cursor_y < monitor["top"] + monitor["height"]):
                        current_monitor = monitor
                        print(f"Cursor found on monitor {i}: {monitor}")
                        break
                
                # Fallback to primary monitor if cursor position detection fails
                if current_monitor is None:
                    current_monitor = sct.monitors[1]  # Primary monitor
                    print(f"Using primary monitor as fallback: {current_monitor}")
                
                print(f"Capturing freeze frame: {current_monitor}")
                screenshot = sct.grab(current_monitor)
                
                # Convert to PIL Image
                self.frozen_screen = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
                # Store monitor info for proper positioning
                self.freeze_frame_offset_x = current_monitor["left"]
                self.freeze_frame_offset_y = current_monitor["top"]
                self.freeze_frame_width = current_monitor["width"]
                self.freeze_frame_height = current_monitor["height"]
                
                # Create full-screen freeze overlay (like p.py)
                self.freeze_overlay = tk.Toplevel()
                self.freeze_overlay.title("Screen Frozen - Resizing Mode")
                self.freeze_overlay.overrideredirect(True)  # No window decorations
                self.freeze_overlay.attributes('-topmost', True)  # Stay on top
                
                # Position on the current monitor (like p.py)
                self.freeze_overlay.geometry(f"{self.freeze_frame_width}x{self.freeze_frame_height}+{self.freeze_frame_offset_x}+{self.freeze_frame_offset_y}")
                
                # Create canvas to display the frozen image (like p.py)
                self.freeze_canvas = tk.Canvas(
                    self.freeze_overlay, 
                    width=self.freeze_frame_width, 
                    height=self.freeze_frame_height,
                    highlightthickness=0,
                    bg="black"
                )
                self.freeze_canvas.pack(fill="both", expand=True)
                
                # Convert to PhotoImage and display (like p.py)
                self.frozen_photo = ImageTk.PhotoImage(self.frozen_screen)
                self.freeze_canvas.create_image(0, 0, image=self.frozen_photo, anchor="nw")
                
                # Make sure our area overlay stays on top of the freeze
                self.lift()  # Bring this area overlay to front
                
                print("Freeze frame overlay created successfully")
                
        except Exception as e:
            print(f"Error freezing screen: {e}")
    

# =============================================================================
# MAIN APPLICATION
# =============================================================================
class Application(tk.Tk):
    """Main application window - Shows only after first-launch workflow completes"""
    
    def __init__(self):
        super().__init__()
        
        # Load configuration FIRST to determine launch type
        is_normal_launch = load_config()
        
        # Window configuration
        self.title("IRUS V7 - Clean Architecture")
        self.geometry("800x600")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Set minimum window size to ensure buttons stay visible
        self.minsize(600, 450)
        
        # Setup StringVars for hotkeys and BooleanVars for checkboxes (linked to ACTIVE_SETTINGS)
        self.hotkey_start = tk.StringVar(value=ACTIVE_SETTINGS['hotkey_start'])
        self.hotkey_stop = tk.StringVar(value=ACTIVE_SETTINGS['hotkey_stop'])
        self.hotkey_change_area = tk.StringVar(value=ACTIVE_SETTINGS['hotkey_change_area'])
        self.hotkey_exit = tk.StringVar(value=ACTIVE_SETTINGS['hotkey_exit'])
        self.always_on_top = tk.BooleanVar(value=ACTIVE_SETTINGS['always_on_top'])
        
        # Setup BooleanVars for stage checkboxes - [AI_REF:stage_checkboxes]
        self.stage_one_time_run = tk.BooleanVar(value=ACTIVE_SETTINGS['stage_one_time_run'])
        self.stage_first_stage = tk.BooleanVar(value=ACTIVE_SETTINGS['stage_first_stage'])
        self.stage_shake_stage = tk.BooleanVar(value=ACTIVE_SETTINGS['stage_shake_stage'])
        self.stage_fish_stage = tk.BooleanVar(value=ACTIVE_SETTINGS['stage_fish_stage'])
        
        # Setup StringVar for scan FPS - [AI_REF:scan_fps]
        self.scan_fps = tk.StringVar(value=str(ACTIVE_SETTINGS['scan_fps']))
        
        # Setup StringVar for scan shake FPS
        self.scan_shake_fps = tk.StringVar(value=str(ACTIVE_SETTINGS['scan_shake_fps']))
        
        # Setup DoubleVar for shake timer - [AI_REF:shake_timer] (renamed to Duplicate Circle Timeout)
        self.shake_timer = tk.DoubleVar(value=ACTIVE_SETTINGS['shake_timer'])
        
        # Setup DoubleVar for no circle timeout - [AI_REF:no_circle_timeout]
        self.no_circle_timeout = tk.DoubleVar(value=ACTIVE_SETTINGS['no_circle_timeout'])
        
        # Setup IntVar for shake minimum radius
        self.shake_min_radius = tk.IntVar(value=ACTIVE_SETTINGS['shake_min_radius'])
        
        # Setup DoubleVar for from side bar ratio - [AI_REF:from_side_bar_ratio]
        self.from_side_bar_ratio = tk.DoubleVar(value=ACTIVE_SETTINGS['from_side_bar_ratio'])
        
        # Setup DoubleVar for fish lost timeout - [AI_REF:fish_lost_timeout]
        self.fish_lost_timeout = tk.DoubleVar(value=ACTIVE_SETTINGS['fish_lost_timeout'])
        
        # Setup Casting Flow Control variables
        self.casting_enable_first_stage = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_enable_first_stage'])
        self.casting_delay1_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_delay1_enabled'])
        self.casting_delay1_duration = tk.DoubleVar(value=ACTIVE_SETTINGS['casting_delay1_duration'])
        self.casting_perfect_cast_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_perfect_cast_enabled'])
        self.casting_delay2_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_delay2_enabled'])
        self.casting_delay2_duration = tk.DoubleVar(value=ACTIVE_SETTINGS['casting_delay2_duration'])
        self.casting_delay3_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_delay3_enabled'])
        self.casting_delay3_duration = tk.DoubleVar(value=ACTIVE_SETTINGS['casting_delay3_duration'])
        self.casting_hold_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_hold_enabled'])
        self.casting_delay4_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_delay4_enabled'])
        self.casting_delay4_duration = tk.DoubleVar(value=ACTIVE_SETTINGS['casting_delay4_duration'])
        self.casting_release_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_release_enabled'])
        self.casting_delay5_enabled = tk.BooleanVar(value=ACTIVE_SETTINGS['casting_delay5_enabled'])
        self.casting_delay5_duration = tk.DoubleVar(value=ACTIVE_SETTINGS['casting_delay5_duration'])
        
        # Setup traces to update ACTIVE_SETTINGS when GUI changes
        self.hotkey_start.trace_add('write', lambda *args: self._update_active_setting('hotkey_start', self.hotkey_start))
        self.hotkey_stop.trace_add('write', lambda *args: self._update_active_setting('hotkey_stop', self.hotkey_stop))
        self.hotkey_change_area.trace_add('write', lambda *args: self._update_active_setting('hotkey_change_area', self.hotkey_change_area))
        self.hotkey_exit.trace_add('write', lambda *args: self._update_active_setting('hotkey_exit', self.hotkey_exit))
        self.always_on_top.trace_add('write', lambda *args: self._update_always_on_top())
        
        # Setup traces for stage checkboxes
        self.stage_one_time_run.trace_add('write', lambda *args: self._update_active_setting('stage_one_time_run', self.stage_one_time_run))
        self.stage_first_stage.trace_add('write', lambda *args: self._update_active_setting('stage_first_stage', self.stage_first_stage))
        self.stage_shake_stage.trace_add('write', lambda *args: self._update_active_setting('stage_shake_stage', self.stage_shake_stage))
        self.stage_fish_stage.trace_add('write', lambda *args: self._update_active_setting('stage_fish_stage', self.stage_fish_stage))
        
        # Setup trace for scan FPS
        self.scan_fps.trace_add('write', lambda *args: self._update_scan_fps())
        
        # Setup trace for scan shake FPS
        self.scan_shake_fps.trace_add('write', lambda *args: self._update_scan_shake_fps())
        
        # Setup trace for shake timer (Duplicate Circle Timeout)
        self.shake_timer.trace_add('write', lambda *args: self._update_active_setting('shake_timer', self.shake_timer))
        
        # Setup trace for no circle timeout
        self.no_circle_timeout.trace_add('write', lambda *args: self._update_active_setting('no_circle_timeout', self.no_circle_timeout))
        
        # Setup trace for shake minimum radius
        self.shake_min_radius.trace_add('write', lambda *args: self._update_active_setting('shake_min_radius', self.shake_min_radius))
        
        # Setup trace for from side bar ratio
        self.from_side_bar_ratio.trace_add('write', lambda *args: self._update_active_setting('from_side_bar_ratio', self.from_side_bar_ratio))
        
        # Setup trace for fish lost timeout
        self.fish_lost_timeout.trace_add('write', lambda *args: self._update_active_setting('fish_lost_timeout', self.fish_lost_timeout))
        
        # Setup traces for casting flow control with mutual exclusivity
        self.casting_enable_first_stage.trace_add('write', lambda *args: self._update_active_setting('casting_enable_first_stage', self.casting_enable_first_stage))
        
        # Branch 1 traces (Perfect Cast Flow) - disable Branch 2 when any are enabled
        self.casting_delay1_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch1', 'casting_delay1_enabled', self.casting_delay1_enabled))
        self.casting_delay1_duration.trace_add('write', lambda *args: self._update_active_setting('casting_delay1_duration', self.casting_delay1_duration))
        self.casting_perfect_cast_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch1', 'casting_perfect_cast_enabled', self.casting_perfect_cast_enabled))
        self.casting_delay2_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch1', 'casting_delay2_enabled', self.casting_delay2_enabled))
        self.casting_delay2_duration.trace_add('write', lambda *args: self._update_active_setting('casting_delay2_duration', self.casting_delay2_duration))
        
        # Branch 2 traces (Hold & Release Flow) - disable Branch 1 when any are enabled
        self.casting_delay3_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch2', 'casting_delay3_enabled', self.casting_delay3_enabled))
        self.casting_delay3_duration.trace_add('write', lambda *args: self._update_active_setting('casting_delay3_duration', self.casting_delay3_duration))
        self.casting_hold_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch2', 'casting_hold_enabled', self.casting_hold_enabled))
        self.casting_delay4_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch2', 'casting_delay4_enabled', self.casting_delay4_enabled))
        self.casting_delay4_duration.trace_add('write', lambda *args: self._update_active_setting('casting_delay4_duration', self.casting_delay4_duration))
        self.casting_release_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch2', 'casting_release_enabled', self.casting_release_enabled))
        self.casting_delay5_enabled.trace_add('write', lambda *args: self._handle_casting_branch_exclusivity('branch2', 'casting_delay5_enabled', self.casting_delay5_enabled))
        self.casting_delay5_duration.trace_add('write', lambda *args: self._update_active_setting('casting_delay5_duration', self.casting_delay5_duration))
        
        # Track the currently registered hotkeys
        self.current_start_hotkey = None
        self.current_stop_hotkey = None
        self.current_exit_hotkey = None
        self.current_change_area_hotkey = None
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # === FIRST LAUNCH vs NORMAL LAUNCH ===
        if not is_normal_launch:
            # First launch: Keep main window empty, show Terms of Use on top
            self.title("IRUS V7 - Loading...")
            # Make the window very small and invisible-looking
            self.geometry("1x1+0+0")
            self.attributes('-alpha', 0.0)  # Make completely transparent
            self.after(100, lambda: run_first_launch_workflow(self, self._on_first_launch_complete))
        else:
            # Normal launch: Show main GUI immediately
            self._initialize_main_gui()
    
    def _on_first_launch_complete(self):
        """
        Called after all first-launch processes complete
        Shows the main GUI for the first time
        """
        # Restore window visibility and size
        self.attributes('-alpha', 1.0)  # Make fully opaque
        self.geometry("800x600")
        # Show main window and initialize GUI
        self._initialize_main_gui()
    
    def _initialize_main_gui(self):
        """
        Initialize the main GUI components
        Called after first-launch workflow OR immediately on normal launch
        """
        # Build GUI
        self._create_gui()
        
        # Setup global hotkeys (initially bind exit hotkey)
        self._setup_global_hotkeys()
        
        # Bind hotkey dropdowns to update functions (in addition to ACTIVE_SETTINGS update)
        self.hotkey_start.trace_add('write', lambda *args: self._update_start_hotkey())
        self.hotkey_stop.trace_add('write', lambda *args: self._update_stop_hotkey())
        self.hotkey_exit.trace_add('write', lambda *args: self._update_exit_hotkey())
        self.hotkey_change_area.trace_add('write', lambda *args: self._update_change_area_hotkey())
        
        # Apply initial always on top setting from ACTIVE_SETTINGS
        always_on_top_value = ACTIVE_SETTINGS.get('always_on_top', True)
        self.always_on_top.set(always_on_top_value)  # Ensure checkbox reflects the setting
        self.wm_attributes('-topmost', always_on_top_value)
        print(f"Applied always on top setting: {always_on_top_value}")
    
    def _create_gui(self):  # [AI_REF:create_gui]
        """Create the modern main GUI structure"""
        
        # Configure main window style
        self.configure(bg='#f0f0f0')
        
        # === HEADER SECTION (Fixed at top) ===
        header_frame = tk.Frame(self, bg='#2c3e50', height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)  # Maintain fixed height
        
        # Main title with modern styling
        title_label = tk.Label(
            header_frame,
            text="IRUS V7",
            font=('Segoe UI', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=(20, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Fishing Bot - Clean Architecture",
            font=('Segoe UI', 11),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=(10, 20))
        
        # === MAIN CONTENT AREA ===
        content_frame = tk.Frame(self, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create notebook (tab container) with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs (store as instance variables for easy reference)
        # Using tk.Frame instead of ttk.Frame to support background colors
        self.tab1 = tk.Frame(notebook, bg='white')  # Basic Settings
        self.tab2 = tk.Frame(notebook, bg='white')  # Initial Setup
        self.tab3 = tk.Frame(notebook, bg='white')  # Casting
        self.tab4 = tk.Frame(notebook, bg='white')  # Shake Minigame
        self.tab5 = tk.Frame(notebook, bg='white')  # Fish Bar Minigame
        self.tab6 = tk.Frame(notebook, bg='white')  # Discord
        self.tab7 = tk.Frame(notebook, bg='white')  # Support The Creator
        
        # Add tabs to notebook in correct order
        notebook.add(self.tab1, text="Basic Settings")
        notebook.add(self.tab2, text="Initial Setup")
        notebook.add(self.tab3, text="Casting")
        notebook.add(self.tab4, text="Shake Minigame")
        notebook.add(self.tab5, text="Fish Bar Minigame")
        notebook.add(self.tab6, text="Discord")
        notebook.add(self.tab7, text="Support The Creator")
        
        # Setup tab contents
        self._setup_tab1_controls()    # Basic Settings
        self._setup_tab2_controls()    # Initial Setup - OneTimeRun checkbox
        self._setup_tab3_controls()    # Casting - FirstStage checkbox  
        self._setup_tab4_controls()    # Shake Minigame - ShakeStage checkbox
        self._setup_tab5_controls()    # Fish Bar Minigame - FishStage checkbox
        
        # Add modern placeholder content to remaining tabs
        tab_info = [
            ("💬", "Discord", "Discord integration and notifications.\nWebhook settings and bot status updates."),
            ("❤️", "Support The Creator", "Show appreciation for AsphaltCake.\nLinks and ways to support development.")
        ]
        
        tabs = [self.tab6, self.tab7]
        
        for i, ((icon_text, title_text, desc_text), tab) in enumerate(zip(tab_info, tabs)):
            # Create scrollable content area for tabs 6 and 7  # [AI_REF:universal_tab_scrolling]
            canvas = tk.Canvas(tab, bg='white')
            scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Create centered content frame within scrollable area
            tab_content = tk.Frame(scrollable_frame, bg='white')
            tab_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
            
            # Icon placeholder with emoji
            icon_frame = tk.Frame(tab_content, bg='#ecf0f1', width=80, height=80)
            icon_frame.pack(pady=(50, 20))
            icon_frame.pack_propagate(False)
            
            icon_label = tk.Label(
                icon_frame,
                text=icon_text,
                font=('Segoe UI', 32),
                bg='#ecf0f1',
                fg='#2c3e50'
            )
            icon_label.pack(expand=True)
            
            # Tab title
            title_label = tk.Label(
                tab_content,
                text=title_text,
                font=('Segoe UI', 16, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            title_label.pack(pady=(0, 10))
            
            # Description
            desc_label = tk.Label(
                tab_content,
                text=desc_text,
                font=('Segoe UI', 10),
                bg='white',
                fg='#7f8c8d',
                justify=tk.CENTER
            )
            desc_label.pack()
        
        # === BOTTOM SECTION (Fixed at bottom - always visible) ===
        bottom_frame = tk.Frame(self, bg='#ecf0f1', height=60)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_frame.pack_propagate(False)  # Maintain fixed height
        
        # Status and button section
        bottom_inner = tk.Frame(bottom_frame, bg='#ecf0f1')
        bottom_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status label (left side)
        status_label = tk.Label(
            bottom_inner,
            text="Ready",
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#27ae60'
        )
        status_label.pack(side=tk.LEFT, pady=10)
        
        # Modern exit button (right side)
        exit_button = tk.Button(
            bottom_inner,
            text="Exit",
            command=self._on_close,
            font=('Segoe UI', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=25,
            pady=8,
            cursor='hand2'
        )
        exit_button.pack(side=tk.RIGHT, pady=10)
        
        # Setup mouse wheel scrolling for all tabs after GUI creation
        self._setup_mouse_wheel_scrolling()
    
    def _setup_mouse_wheel_scrolling(self):  # [AI_REF:universal_tab_scrolling]
        """Setup mouse wheel scrolling for all canvas elements in tabs"""
        def _bind_mousewheel(canvas):
            """Bind mouse wheel events to canvas"""
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            def _bind_to_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            def _unbind_from_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            
            canvas.bind('<Enter>', _bind_to_mousewheel)
            canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Find all canvas widgets in tabs and bind mouse wheel
        for tab in [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6, self.tab7]:
            for widget in tab.winfo_children():
                if isinstance(widget, tk.Canvas):
                    _bind_mousewheel(widget)
    
    def _setup_tab1_controls(self):  # [AI_REF:setup_basic_settings_tab]
        """
        Basic Settings Tab: Hotkey Configuration + App Preferences with Scrolling
        Contains hotkey dropdown selectors and application preferences (no buttons - hotkeys only)
        """
        # Create canvas and scrollbar for scrolling functionality
        canvas = tk.Canvas(self.tab1, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.tab1, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas for scrollable content
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas for scroll wheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Main content frame (now inside scrollable_frame instead of directly in tab1)
        main_frame = tk.Frame(scrollable_frame, bg='white', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(
            title_frame,
            text="Basic Settings",
            font=('Segoe UI', 18, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Configure hotkeys and application preferences",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d'
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ===== RESET SETTINGS SECTION =====
        reset_section = tk.Frame(main_frame, bg='white', pady=15)
        reset_section.pack(fill=tk.X)
        
        reset_button = tk.Button(
            reset_section,
            text="Reset All Settings",
            command=self._reset_all_settings,
            font=('Segoe UI', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        reset_button.pack(anchor=tk.W)
        
        # ===== HOTKEY CONFIGURATION SECTION =====
        hotkey_section = tk.Frame(main_frame, bg='white', relief='ridge', bd=1, padx=25, pady=20)
        hotkey_section.pack(fill=tk.X, pady=(10, 0))
        
        # Configure grid columns for alignment
        hotkey_section.columnconfigure(1, weight=1)
        
        # Modern hotkey rows with better styling
        hotkey_rows = [
            ("Start Bot:", self.hotkey_start, "start_hotkey_dropdown"),
            ("Stop Bot:", self.hotkey_stop, "stop_hotkey_dropdown"), 
            ("Change Area:", self.hotkey_change_area, "change_area_hotkey_dropdown"),
            ("Exit Application:", self.hotkey_exit, "exit_hotkey_dropdown")
        ]
        
        for i, (label_text, variable, attr_name) in enumerate(hotkey_rows):
            # Label with modern styling
            label = tk.Label(
                hotkey_section,
                text=label_text,
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg='#2c3e50',
                width=15,
                anchor='w'
            )
            label.grid(row=i, column=0, padx=(0, 15), pady=8, sticky='w')
            
            # Modern dropdown styling
            style = ttk.Style()
            style.configure('Modern.TCombobox', fieldbackground='white', borderwidth=1)
            
            dropdown = ttk.Combobox(
                hotkey_section,
                textvariable=variable,
                values=KEYBOARD_KEYS,
                state='readonly',
                width=25,
                font=('Segoe UI', 10),
                style='Modern.TCombobox'
            )
            dropdown.grid(row=i, column=1, padx=5, pady=8, sticky='w')
            
            # Store dropdown reference
            setattr(self, attr_name, dropdown)
        
        # Always On Top setting - continue grid layout (row 4)
        always_label = tk.Label(
            hotkey_section,
            text="Always On Top:",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#2c3e50',
            width=15,
            anchor='w'
        )
        always_label.grid(row=4, column=0, padx=(0, 15), pady=(18, 8), sticky='w')
        
        self.always_on_top_checkbox = tk.Checkbutton(
            hotkey_section,
            text="Keep application window always on top",
            variable=self.always_on_top,
            font=('Segoe UI', 10),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            activeforeground='#2c3e50'
        )
        self.always_on_top_checkbox.grid(row=4, column=1, padx=5, pady=(18, 8), sticky='w')
        
        # Bot Flow Control section - [AI_REF:program_flow_control]
        flow_section = tk.LabelFrame(
            scrollable_frame,
            text="Bot Flow Control",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        flow_section.pack(fill='x', padx=30, pady=(30, 20))
        
        # Flow diagram title
        flow_title = tk.Label(
            flow_section,
            text="Bot Execution Flow (Enable/Disable Stages)",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        flow_title.pack(anchor='w', pady=(0, 15))
        
        # Create flow diagram frame
        flow_frame = tk.Frame(flow_section, bg='white')
        flow_frame.pack(fill='x', pady=10)
        
        # Configure grid weights for proper spacing
        for i in range(7):  # 4 stages + 3 arrows
            flow_frame.grid_columnconfigure(i, weight=1 if i % 2 == 0 else 0)
        
        # Stage 1: OneTimeRun
        stage1_frame = tk.Frame(flow_frame, bg='#e8f4fd', relief='ridge', bd=1)
        stage1_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        tk.Label(stage1_frame, text="OneTimeRun", font=('Segoe UI', 9, 'bold'), bg='#e8f4fd', fg='#2c3e50').pack(pady=2)
        self.flow_checkbox_1 = tk.Checkbutton(
            stage1_frame, text="Enable", variable=self.stage_one_time_run,
            font=('Segoe UI', 8), bg='#e8f4fd', fg='#2c3e50', activebackground='#e8f4fd'
        )
        self.flow_checkbox_1.pack(pady=2)
        
        # Arrow 1
        tk.Label(flow_frame, text="→", font=('Segoe UI', 16, 'bold'), bg='white', fg='#3498db').grid(row=0, column=1, padx=5)
        
        # Stage 2: FirstStage
        stage2_frame = tk.Frame(flow_frame, bg='#e8f6e8', relief='ridge', bd=1)
        stage2_frame.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        tk.Label(stage2_frame, text="FirstStage", font=('Segoe UI', 9, 'bold'), bg='#e8f6e8', fg='#2c3e50').pack(pady=2)
        self.flow_checkbox_2 = tk.Checkbutton(
            stage2_frame, text="Enable", variable=self.stage_first_stage,
            font=('Segoe UI', 8), bg='#e8f6e8', fg='#2c3e50', activebackground='#e8f6e8'
        )
        self.flow_checkbox_2.pack(pady=2)
        
        # Arrow 2
        tk.Label(flow_frame, text="→", font=('Segoe UI', 16, 'bold'), bg='white', fg='#3498db').grid(row=0, column=3, padx=5)
        
        # Stage 3: ShakeStage
        stage3_frame = tk.Frame(flow_frame, bg='#fff3e0', relief='ridge', bd=1)
        stage3_frame.grid(row=0, column=4, padx=5, pady=5, sticky='ew')
        
        tk.Label(stage3_frame, text="ShakeStage", font=('Segoe UI', 9, 'bold'), bg='#fff3e0', fg='#2c3e50').pack(pady=2)
        self.flow_checkbox_3 = tk.Checkbutton(
            stage3_frame, text="Enable", variable=self.stage_shake_stage,
            font=('Segoe UI', 8), bg='#fff3e0', fg='#2c3e50', activebackground='#fff3e0'
        )
        self.flow_checkbox_3.pack(pady=2)
        
        # Arrow 3
        tk.Label(flow_frame, text="→", font=('Segoe UI', 16, 'bold'), bg='white', fg='#3498db').grid(row=0, column=5, padx=5)
        
        # Stage 4: FishStage
        stage4_frame = tk.Frame(flow_frame, bg='#fce4ec', relief='ridge', bd=1)
        stage4_frame.grid(row=0, column=6, padx=5, pady=5, sticky='ew')
        
        tk.Label(stage4_frame, text="FishStage", font=('Segoe UI', 9, 'bold'), bg='#fce4ec', fg='#2c3e50').pack(pady=2)
        self.flow_checkbox_4 = tk.Checkbutton(
            stage4_frame, text="Enable", variable=self.stage_fish_stage,
            font=('Segoe UI', 8), bg='#fce4ec', fg='#2c3e50', activebackground='#fce4ec'
        )
        self.flow_checkbox_4.pack(pady=2)
        
        # Flow description
        flow_desc = tk.Label(
            flow_section,
            text="Bot executes enabled stages in order. Disabled stages are skipped.\nConfigure individual stages in their respective tabs (Initial Setup, Casting, etc.)",
            font=('Segoe UI', 9),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        flow_desc.pack(anchor='w', pady=(15, 5))
    
    def _setup_tab2_controls(self):  # [AI_REF:program_flow_control]
        """Setup Initial Setup tab - OneTimeRun stage checkbox"""
        # Create scrollable content area
        canvas = tk.Canvas(self.tab2, bg='white')
        scrollbar = tk.Scrollbar(self.tab2, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tab header
        header_frame = tk.Frame(scrollable_frame, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🚀 Initial Setup",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            header_frame,
            text="Configure initial bot setup and preparation stage",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d'
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # OneTimeRun Stage Control
        stage_frame = tk.LabelFrame(
            scrollable_frame,
            text="OneTimeRun Stage",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        stage_frame.pack(fill='x', padx=30, pady=20)
        
        self.one_time_run_checkbox = tk.Checkbutton(
            stage_frame,
            text="Enable OneTimeRun stage (Initial bot setup and preparation)",
            variable=self.stage_one_time_run,
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            activeforeground='#2c3e50'
        )
        self.one_time_run_checkbox.pack(anchor='w', pady=10)
        
        desc_text = tk.Label(
            stage_frame,
            text="This stage runs once at the start of each bot cycle.\nUsed for initial positioning, UI detection, and setup tasks.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        desc_text.pack(anchor='w', pady=(0, 10))
    
    def _setup_tab3_controls(self):
        """Setup Casting tab with flow control"""
        # Create scrollable content area
        canvas = tk.Canvas(self.tab3, bg='white')
        scrollbar = tk.Scrollbar(self.tab3, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tab header
        header_frame = tk.Frame(scrollable_frame, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🎣 Casting",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            header_frame,
            text="Configure fishing cast detection, timing, and flow control",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d'
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # FirstStage Control
        stage_frame = tk.LabelFrame(
            scrollable_frame,
            text="FirstStage (Casting)",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        stage_frame.pack(fill='x', padx=30, pady=20)
        
        self.first_stage_checkbox = tk.Checkbutton(
            stage_frame,
            text="Enable FirstStage (Cast detection and initial fishing)",
            variable=self.stage_first_stage,
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            activeforeground='#2c3e50'
        )
        self.first_stage_checkbox.pack(anchor='w', pady=10)
        
        desc_text = tk.Label(
            stage_frame,
            text="This stage handles the initial fishing cast and waits for fish bite detection.\nMonitors for fishing line tension and bite indicators.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        desc_text.pack(anchor='w', pady=(0, 10))
        
        # Casting Flow Control section
        flow_section = tk.LabelFrame(
            scrollable_frame,
            text="Casting Flow Control",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        flow_section.pack(fill='x', padx=30, pady=(30, 20))
        
        # Flow diagram title
        flow_title = tk.Label(
            flow_section,
            text="Casting Execution Flow (Choose ONE Branch - Mutually Exclusive)",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        flow_title.pack(anchor='w', pady=(0, 5))
        
        # Mutual exclusivity warning
        warning_label = tk.Label(
            flow_section,
            text="⚠️ Only one branch can be active at a time. When switching branches, ALL components in the new branch are enabled. Within the same branch, components can be toggled individually.",
            font=('Segoe UI', 9),
            bg='white',
            fg='#e74c3c',
            wraplength=600,
            justify='left'
        )
        warning_label.pack(anchor='w', pady=(0, 15))
        
        # Create main flow frame
        main_flow_frame = tk.Frame(flow_section, bg='white')
        main_flow_frame.pack(fill='x', pady=10)
        
        # Enable First Stage checkbox
        enable_frame = tk.Frame(main_flow_frame, bg='#e8f4fd', relief='ridge', bd=1)
        enable_frame.pack(fill='x', pady=5)
        
        tk.Label(enable_frame, text="Enable First Stage", font=('Segoe UI', 9, 'bold'), bg='#e8f4fd', fg='#2c3e50').pack(pady=5)
        self.casting_enable_checkbox = tk.Checkbutton(
            enable_frame, text="Enable", variable=self.casting_enable_first_stage,
            font=('Segoe UI', 8), bg='#e8f4fd', fg='#2c3e50', activebackground='#e8f4fd'
        )
        self.casting_enable_checkbox.pack(pady=2)
        
        # Flow branch frame
        branch_frame = tk.Frame(main_flow_frame, bg='white')
        branch_frame.pack(fill='x', pady=10)
        
        # Configure grid for branches
        branch_frame.grid_columnconfigure(0, weight=1)
        branch_frame.grid_columnconfigure(1, weight=1)
        
        # First Branch (Delay -> Perfect Cast -> Delay -> Exit)
        branch1_frame = tk.LabelFrame(branch_frame, text="Branch 1: Perfect Cast Flow", bg='white', fg='#2c3e50', font=('Segoe UI', 10, 'bold'))
        branch1_frame.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        self._create_flow_component(branch1_frame, "Delay 1", self.casting_delay1_enabled, self.casting_delay1_duration, '#e8f6e8')
        self._create_flow_component(branch1_frame, "Perfect Cast", self.casting_perfect_cast_enabled, None, '#fff3e0', show_duration=False)
        self._create_flow_component(branch1_frame, "Delay 2", self.casting_delay2_enabled, self.casting_delay2_duration, '#fce4ec')
        self._create_exit_component(branch1_frame, "Exit", '#f0f0f0')
        
        # Second Branch (Delay -> Hold -> Delay -> Release -> Delay -> Exit)
        branch2_frame = tk.LabelFrame(branch_frame, text="Branch 2: Hold & Release Flow", bg='white', fg='#2c3e50', font=('Segoe UI', 10, 'bold'))
        branch2_frame.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        self._create_flow_component(branch2_frame, "Delay 3", self.casting_delay3_enabled, self.casting_delay3_duration, '#e8f6e8')
        self._create_flow_component(branch2_frame, "Hold", self.casting_hold_enabled, None, '#fff3e0', show_duration=False)
        self._create_flow_component(branch2_frame, "Delay 4", self.casting_delay4_enabled, self.casting_delay4_duration, '#fce4ec')
        self._create_flow_component(branch2_frame, "Release", self.casting_release_enabled, None, '#e8f4fd', show_duration=False)
        self._create_flow_component(branch2_frame, "Delay 5", self.casting_delay5_enabled, self.casting_delay5_duration, '#f3e5f5')
        self._create_exit_component(branch2_frame, "Exit", '#f0f0f0')
        
        # Flow description
        desc_frame = tk.Frame(flow_section, bg='white')
        desc_frame.pack(fill='x', pady=(15, 0))
        
        desc_text = tk.Label(
            desc_frame,
            text="Flow executes enabled components in order. Disabled components are skipped.\n" +
                 "Each delay is configurable (0.1s intervals). Hold = left click down, Release = left click up.\n" +
                 "SMART BRANCH SWITCHING: When switching branches, all components in new branch are enabled. Within same branch, toggle individually.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        desc_text.pack(anchor='w')
    
    def _create_flow_component(self, parent, name, enable_var, duration_var, color, show_duration=True):
        """Create a flow component with checkbox and optional duration setting"""
        component_frame = tk.Frame(parent, bg=color, relief='ridge', bd=1)
        component_frame.pack(fill='x', padx=2, pady=2)
        
        # Component name
        tk.Label(component_frame, text=name, font=('Segoe UI', 9, 'bold'), bg=color, fg='#2c3e50').pack(pady=2)
        
        # Enable checkbox
        enable_checkbox = tk.Checkbutton(
            component_frame, text="Enable", variable=enable_var,
            font=('Segoe UI', 8), bg=color, fg='#2c3e50', activebackground=color
        )
        enable_checkbox.pack(pady=1)
        
        # Duration setting (only for delays)
        if show_duration and duration_var:
            duration_frame = tk.Frame(component_frame, bg=color)
            duration_frame.pack(pady=2)
            
            tk.Label(duration_frame, text="Duration:", font=('Segoe UI', 8), bg=color, fg='#2c3e50').pack(side='left')
            
            duration_spinbox = tk.Spinbox(
                duration_frame, textvariable=duration_var, from_=0.1, to=10.0, increment=0.1,
                width=6, font=('Segoe UI', 8), format="%.1f"
            )
            duration_spinbox.pack(side='left', padx=(5, 0))
            
            tk.Label(duration_frame, text="s", font=('Segoe UI', 8), bg=color, fg='#2c3e50').pack(side='left')
    
    def _create_exit_component(self, parent, name, color):
        """Create an exit component (no controls, just indicator)"""
        component_frame = tk.Frame(parent, bg=color, relief='ridge', bd=1)
        component_frame.pack(fill='x', padx=2, pady=2)
        
        tk.Label(component_frame, text=name, font=('Segoe UI', 9, 'bold'), bg=color, fg='#2c3e50').pack(pady=5)
        tk.Label(component_frame, text="(End of flow)", font=('Segoe UI', 7), bg=color, fg='#7f8c8d').pack(pady=(0, 5))
    
    def _setup_tab4_controls(self):
        """Setup Shake Minigame tab - ShakeStage checkbox"""
        # Create scrollable content area
        canvas = tk.Canvas(self.tab4, bg='white')
        scrollbar = tk.Scrollbar(self.tab4, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tab header
        header_frame = tk.Frame(scrollable_frame, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🎯 Shake Minigame",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            header_frame,
            text="Configure shake fishing detection and automation",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d'
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # ShakeStage Control
        stage_frame = tk.LabelFrame(
            scrollable_frame,
            text="ShakeStage Control",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        stage_frame.pack(fill='x', padx=30, pady=20)
        
        self.shake_stage_checkbox = tk.Checkbutton(
            stage_frame,
            text="Enable ShakeStage (Shake minigame automation)",
            variable=self.stage_shake_stage,
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            activeforeground='#2c3e50'
        )
        self.shake_stage_checkbox.pack(anchor='w', pady=10)
        
        desc_text = tk.Label(
            stage_frame,
            text="This stage handles shake-based fishing minigames.\nDetects shake prompts and performs automated shaking actions.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        desc_text.pack(anchor='w', pady=(0, 10))
        
        # Scan Shake FPS Settings
        shake_fps_frame = tk.LabelFrame(
            scrollable_frame,
            text="Performance Settings",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        shake_fps_frame.pack(fill='x', padx=30, pady=20)
        
        # Scan Shake FPS dropdown
        shake_fps_control_frame = tk.Frame(shake_fps_frame, bg='white')
        shake_fps_control_frame.pack(fill='x', pady=10)
        
        shake_fps_label = tk.Label(
            shake_fps_control_frame,
            text="Scan Shake FPS:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        shake_fps_label.pack(side='left')
        
        shake_fps_dropdown = ttk.Combobox(
            shake_fps_control_frame,
            textvariable=self.scan_shake_fps,
            values=['10', '20'],
            state='readonly',
            font=('Segoe UI', 10),
            width=10
        )
        shake_fps_dropdown.pack(side='left', padx=(10, 0))
        
        shake_fps_desc = tk.Label(
            shake_fps_frame,
            text="Controls image processing speed for shake detection.\n10 FPS: Conservative performance (recommended)\n20 FPS: Higher responsiveness for fast reactions",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        shake_fps_desc.pack(anchor='w', pady=(0, 10))
        
        # Shake Timer Settings - [AI_REF:shake_timer]
        timer_frame = tk.LabelFrame(
            scrollable_frame,
            text="Shake Detection Timeout",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        timer_frame.pack(fill='x', padx=30, pady=20)
        
        # Shake timer control
        timer_control_frame = tk.Frame(timer_frame, bg='white')
        timer_control_frame.pack(fill='x', pady=10)
        
        timer_label = tk.Label(
            timer_control_frame,
            text="Duplicate Circle Timeout:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        timer_label.pack(side='left')
        
        timer_spinbox = tk.Spinbox(
            timer_control_frame,
            textvariable=self.shake_timer,
            from_=0.5,
            to=10.0,
            increment=0.5,
            width=10,
            font=('Segoe UI', 10)
        )
        timer_spinbox.pack(side='left', padx=(10, 5))
        
        timer_unit_label = tk.Label(
            timer_control_frame,
            text="seconds",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d'
        )
        timer_unit_label.pack(side='left')
        
        timer_desc = tk.Label(
            timer_frame,
            text="Time to wait when same circle detected repeatedly.\nAfter timeout, will click the circle anyway.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        timer_desc.pack(anchor='w', pady=(0, 10))
        
        # No Circle Found Timeout control
        no_circle_control_frame = tk.Frame(timer_frame, bg='white')
        no_circle_control_frame.pack(fill='x', pady=10)
        
        no_circle_label = tk.Label(
            no_circle_control_frame,
            text="No Circle Found Timeout:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        no_circle_label.pack(side='left')
        
        no_circle_spinbox = tk.Spinbox(
            no_circle_control_frame,
            textvariable=self.no_circle_timeout,
            from_=1.0,
            to=10.0,
            increment=0.5,
            width=10,
            font=('Segoe UI', 10)
        )
        no_circle_spinbox.pack(side='left', padx=(10, 5))
        
        no_circle_unit_label = tk.Label(
            no_circle_control_frame,
            text="seconds",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d'
        )
        no_circle_unit_label.pack(side='left')
        
        no_circle_desc = tk.Label(
            timer_frame,
            text="Time to wait for circles in shake minigame.\nIf timer expires without clicking a circle, returns to FirstStage.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        no_circle_desc.pack(anchor='w', pady=(0, 10))
        
        # Circle Detection Settings
        circle_frame = tk.LabelFrame(
            scrollable_frame,
            text="Circle Detection Parameters",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        circle_frame.pack(fill='x', padx=30, pady=20)
        
        # Minimum radius control
        radius_control_frame = tk.Frame(circle_frame, bg='white')
        radius_control_frame.pack(fill='x', pady=10)
        
        radius_label = tk.Label(
            radius_control_frame,
            text="Minimum Circle Radius:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        radius_label.pack(side='left')
        
        radius_spinbox = tk.Spinbox(
            radius_control_frame,
            textvariable=self.shake_min_radius,
            from_=1,
            to=50,
            increment=1,
            width=10,
            font=('Segoe UI', 10)
        )
        radius_spinbox.pack(side='left', padx=(10, 5))
        
        radius_unit_label = tk.Label(
            radius_control_frame,
            text="pixels",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d'
        )
        radius_unit_label.pack(side='left')
        
        radius_desc = tk.Label(
            circle_frame,
            text="Minimum radius (in pixels) for a detected shape to be considered a valid circle.\nSmaller values detect more circles but may include noise. Larger values are more selective.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        radius_desc.pack(anchor='w', pady=(0, 10))
        
        # Test Processing Section
        test_frame = tk.LabelFrame(
            scrollable_frame,
            text="Development Testing",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        test_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        test_button = tk.Button(
            test_frame,
            text="🎯 Test Shake Processing",
            command=self._test_shake_processing,
            font=('Segoe UI', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8
        )
        test_button.pack(anchor='w', pady=10)
        
        test_desc = tk.Label(
            test_frame,
            text="Run shake circle detection on current screen and save debug images.\nResults and images will be saved to project folder for analysis.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        test_desc.pack(anchor='w', pady=(0, 10))
    
    def _setup_tab5_controls(self):
        """Setup Fish Bar Minigame tab - FishStage checkbox"""
        # Create scrollable content area
        canvas = tk.Canvas(self.tab5, bg='white')
        scrollbar = tk.Scrollbar(self.tab5, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tab header
        header_frame = tk.Frame(scrollable_frame, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🐟 Fish Bar Minigame",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            header_frame,
            text="Configure fish bar minigame detection and automation",
            font=('Segoe UI', 11),
            bg='white',
            fg='#7f8c8d'
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # FishStage Control
        stage_frame = tk.LabelFrame(
            scrollable_frame,
            text="FishStage Control",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        stage_frame.pack(fill='x', padx=30, pady=20)
        
        self.fish_stage_checkbox = tk.Checkbutton(
            stage_frame,
            text="Enable FishStage (Fish bar minigame automation)",
            variable=self.stage_fish_stage,
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50',
            activebackground='white',
            activeforeground='#2c3e50'
        )
        self.fish_stage_checkbox.pack(anchor='w', pady=10)
        
        desc_text = tk.Label(
            stage_frame,
            text="This stage handles fish bar minigames using vertical edge detection.\nDetects user bar and target positions for precise timing.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        desc_text.pack(anchor='w', pady=(0, 10))
        
        # From Side Bar Ratio Control Section
        ratio_frame = tk.LabelFrame(
            scrollable_frame,
            text="Bar Positioning Parameters",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        ratio_frame.pack(fill='x', padx=30, pady=20)
        
        # From Side Bar Ratio Label and Scale
        ratio_label = tk.Label(
            ratio_frame,
            text="From Side Bar Ratio (0.0 - 1.0):",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        ratio_label.pack(anchor='w', pady=(10, 5))
        
        self.ratio_scale = tk.Scale(
            ratio_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient='horizontal',
            variable=self.from_side_bar_ratio,
            font=('Segoe UI', 10),
            bg='white',
            fg='#2c3e50',
            activebackground='#3498db',
            highlightthickness=0,
            length=300
        )
        self.ratio_scale.pack(anchor='w', pady=(0, 5))
        
        ratio_desc = tk.Label(
            ratio_frame,
            text="0 = 0% Disabled\n50% = Half Bar Length From Sides\n100% = Full Bar Length From Sides",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        ratio_desc.pack(anchor='w', pady=(0, 10))
        
        # Scan FPS Settings
        fps_frame = tk.LabelFrame(
            scrollable_frame,
            text="Performance Settings",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        fps_frame.pack(fill='x', padx=30, pady=20)
        
        # Scan FPS dropdown
        fps_control_frame = tk.Frame(fps_frame, bg='white')
        fps_control_frame.pack(fill='x', pady=10)
        
        fps_label = tk.Label(
            fps_control_frame,
            text="Scan Fish FPS:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        fps_label.pack(side='left')
        
        fps_dropdown = ttk.Combobox(
            fps_control_frame,
            textvariable=self.scan_fps,
            values=['60', '120'],
            state='readonly',
            font=('Segoe UI', 10),
            width=10
        )
        fps_dropdown.pack(side='left', padx=(10, 0))
        
        fps_desc = tk.Label(
            fps_frame,
            text="Controls image processing speed for fish bar detection.\n60 FPS: Balanced performance and compatibility\n120 FPS: Maximum responsiveness (high-end systems only)",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        fps_desc.pack(anchor='w', pady=(0, 10))
        
        # Fish Lost Timeout Settings - [AI_REF:fish_lost_timeout]
        timeout_frame = tk.LabelFrame(
            scrollable_frame,
            text="Fish Detection Timeout",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        timeout_frame.pack(fill='x', padx=30, pady=20)
        
        # Fish lost timeout control
        timeout_control_frame = tk.Frame(timeout_frame, bg='white')
        timeout_control_frame.pack(fill='x', pady=10)
        
        timeout_label = tk.Label(
            timeout_control_frame,
            text="Fish Lost Timeout:",
            font=('Segoe UI', 11),
            bg='white',
            fg='#2c3e50'
        )
        timeout_label.pack(side='left')
        
        timeout_spinbox = tk.Spinbox(
            timeout_control_frame,
            textvariable=self.fish_lost_timeout,
            from_=0.5,
            to=10.0,
            increment=0.5,
            width=10,
            font=('Segoe UI', 10)
        )
        timeout_spinbox.pack(side='left', padx=(10, 5))
        
        timeout_unit_label = tk.Label(
            timeout_control_frame,
            text="seconds",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d'
        )
        timeout_unit_label.pack(side='left')
        
        timeout_desc = tk.Label(
            timeout_frame,
            text="Time to wait when FishingOngoing becomes False before exiting fish stage.\nIf fishing resumes within timeout, timer resets. If timeout expires, bot continues to next stage.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        timeout_desc.pack(anchor='w', pady=(0, 10))
        
        # Test Processing Section
        test_frame = tk.LabelFrame(
            scrollable_frame,
            text="Development Testing",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        test_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        test_button = tk.Button(
            test_frame,
            text="🔧 Test Processing",
            command=self._test_fish_processing,
            font=('Segoe UI', 11, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            relief='flat',
            padx=20,
            pady=8
        )
        test_button.pack(anchor='w', pady=10)
        
        test_desc = tk.Label(
            test_frame,
            text="Run fish bar processing on current screen and save debug images.\nResults and images will be saved to project folder for analysis.",
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        test_desc.pack(anchor='w', pady=(0, 10))
        
        # Technical Info
        tech_frame = tk.LabelFrame(
            scrollable_frame,
            text="Technical Details",
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg='#34495e',
            padx=15,
            pady=10
        )
        tech_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tech_text = tk.Label(
            tech_frame,
            text="• Uses advanced vertical edge detection from fish_bar_area\n• Detects user controlled bar and target line positions\n• Calculates optimal timing for minigame success\n• Integrates with area visualization system (F3 hotkey)",
            font=('Segoe UI', 9),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        tech_text.pack(anchor='w', pady=5)
    
    def _setup_global_hotkeys(self):
        """Setup global keyboard hotkeys - bind start, stop, exit and change area hotkeys"""
        self._update_start_hotkey()
        self._update_stop_hotkey()
        self._update_exit_hotkey()
        self._update_change_area_hotkey()
        
        # Initialize area overlay tracking
        self.area_overlays_visible = False
        self.shake_area_window = None
        self.fish_bar_area_window = None
        
        # Bot loop control variables
        self.bot_running = False
        self.bot_thread = None
        self.current_stage = None
    
    def _update_start_hotkey(self):
        """Update the start hotkey when dropdown selection changes"""
        # Remove old start hotkey if it exists
        if hasattr(self, 'current_start_hotkey') and self.current_start_hotkey:
            try:
                keyboard.remove_hotkey(self.current_start_hotkey)
            except:
                pass  # Silently fail if hotkey removal fails
        
        # Register new start hotkey
        new_hotkey = self.hotkey_start.get().lower()
        try:
            keyboard.add_hotkey(new_hotkey, self._start_bot)
            self.current_start_hotkey = new_hotkey
        except:
            pass  # Silently fail if hotkey registration fails

    def _update_stop_hotkey(self):
        """Update the stop hotkey when dropdown selection changes"""
        # Remove old stop hotkey if it exists
        if hasattr(self, 'current_stop_hotkey') and self.current_stop_hotkey:
            try:
                keyboard.remove_hotkey(self.current_stop_hotkey)
            except:
                pass  # Silently fail if hotkey removal fails
        
        # Register new stop hotkey
        new_hotkey = self.hotkey_stop.get().lower()
        try:
            keyboard.add_hotkey(new_hotkey, self._stop_bot)
            self.current_stop_hotkey = new_hotkey
        except:
            pass  # Silently fail if hotkey registration fails

    def _update_exit_hotkey(self):
        """Update the exit hotkey when dropdown selection changes"""
        # Remove old exit hotkey if it exists
        if self.current_exit_hotkey:
            try:
                keyboard.remove_hotkey(self.current_exit_hotkey)
            except:
                pass  # Silently fail if hotkey removal fails
        
        # Register new exit hotkey
        new_hotkey = self.hotkey_exit.get().lower()
        try:
            keyboard.add_hotkey(new_hotkey, self._on_close)
            self.current_exit_hotkey = new_hotkey
        except:
            pass  # Silently fail if hotkey registration fails
    
    def _update_change_area_hotkey(self):  # [AI_REF:change_area_hotkey_handler]
        """Update the change area hotkey when dropdown selection changes"""
        # Remove old change area hotkey if it exists
        if hasattr(self, 'current_change_area_hotkey') and self.current_change_area_hotkey:
            try:
                keyboard.remove_hotkey(self.current_change_area_hotkey)
            except:
                pass  # Silently fail if hotkey removal fails
        
        # Register new change area hotkey
        new_hotkey = self.hotkey_change_area.get().lower()
        try:
            keyboard.add_hotkey(new_hotkey, self._toggle_area_overlays)
            self.current_change_area_hotkey = new_hotkey
        except:
            pass  # Silently fail if hotkey registration fails
    
    def _toggle_area_overlays(self):  # [AI_REF:toggle_area_overlays] [AI_REF:area_adjustment_gui_hide]
        """Toggle the visibility of area overlays (ShakeArea = RED, FishBarArea = BLUE) with GUI hide/show"""
        if not self.area_overlays_visible:
            # Hide GUI when entering area adjustment mode
            print("Hiding GUI for area adjustment mode...")
            self.withdraw()
            self._show_area_overlays()
        else:
            self._hide_area_overlays()
            # Show GUI when exiting area adjustment mode
            print("Showing GUI after area adjustment...")
            self.deiconify()
            
            # Restore always-on-top setting if enabled
            if ACTIVE_SETTINGS.get('always_on_top', False):
                self.attributes('-topmost', True)
    
    def _show_area_overlays(self):  # [AI_REF:show_area_overlays]
        """Show draggable, resizable area overlays on screen with immediate screen freeze"""
        try:
            # Freeze screen immediately when areas are shown
            self._freeze_screen_for_areas()
            
            # Get geometries directly from ACTIVE_SETTINGS (no scaling)
            shake_geom = ACTIVE_SETTINGS.get('shake_area', '1336x796+614+287')
            fish_bar_geom = ACTIVE_SETTINGS.get('fish_bar_area', '1034x48+763+1213')
            
            # Create ShakeArea overlay (RED) - pass freeze overlay reference
            self.shake_area_window = AreaOverlay(
                geometry=shake_geom,
                color='red',
                title='ShakeArea',
                alpha=0.3,
                on_close_callback=lambda: self._update_area_geometry('shake_area', self.shake_area_window),
                freeze_overlay=self.freeze_overlay
            )
            
            # Create FishBarArea overlay (BLUE) - pass freeze overlay reference
            self.fish_bar_area_window = AreaOverlay(
                geometry=fish_bar_geom,
                color='blue', 
                title='FishBarArea',
                alpha=0.3,
                on_close_callback=lambda: self._update_area_geometry('fish_bar_area', self.fish_bar_area_window),
                freeze_overlay=self.freeze_overlay
            )
            
            self.area_overlays_visible = True
            
        except Exception as e:
            print(f"Error showing area overlays: {e}")
    
    def _hide_area_overlays(self):  # [AI_REF:hide_area_overlays]
        """Hide area overlays, save their positions to ACTIVE_SETTINGS, and unfreeze screen"""
        try:
            # Save ShakeArea geometry before closing
            if self.shake_area_window:
                self._update_area_geometry('shake_area', self.shake_area_window)
                self.shake_area_window.destroy()
                self.shake_area_window = None
            
            # Save FishBarArea geometry before closing
            if self.fish_bar_area_window:
                self._update_area_geometry('fish_bar_area', self.fish_bar_area_window)
                self.fish_bar_area_window.destroy()
                self.fish_bar_area_window = None
            
            # Unfreeze screen when areas are hidden
            self._unfreeze_screen_for_areas()
            
            self.area_overlays_visible = False
            
        except Exception as e:
            print(f"Error hiding area overlays: {e}")
    
    def _update_area_geometry(self, area_key, overlay_window):  # [AI_REF:update_area_geometry]
        """Update ACTIVE_SETTINGS with current overlay geometry - converts screen coords back to base resolution"""
        try:
            if overlay_window and overlay_window.winfo_exists():
                # Get current coordinates from overlay window
                width = overlay_window.winfo_width()
                height = overlay_window.winfo_height()
                x = overlay_window.winfo_x()
                y = overlay_window.winfo_y()
                
                # Format as geometry string and save directly
                geometry = f"{width}x{height}+{x}+{y}"
                ACTIVE_SETTINGS[area_key] = geometry
                
                # Update MiddleOfPlayArea if fish_bar_area was changed
                if area_key == 'fish_bar_area':
                    update_middle_of_play_area()
                
        except Exception as e:
            print(f"Error updating area geometry for {area_key}: {e}")
    
    def _freeze_screen_for_areas(self):  # [AI_REF:screen_freeze_fix]
        """Freeze screen for area configuration mode with enhanced reliability"""
        if not YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE:
            print("Screen capture libraries not available - skipping freeze")
            return
            
        # Clean up any existing freeze overlay first
        self._cleanup_freeze_overlay()
            
        try:
            # Get cursor position to determine which monitor to capture
            cursor_x = self.winfo_pointerx()
            cursor_y = self.winfo_pointery()
            
            with mss.mss() as sct:
                # Find which monitor the cursor is on
                current_monitor = None
                for i, monitor in enumerate(sct.monitors[1:], 1):
                    if (monitor["left"] <= cursor_x < monitor["left"] + monitor["width"] and
                        monitor["top"] <= cursor_y < monitor["top"] + monitor["height"]):
                        current_monitor = monitor
                        print(f"Area mode: Cursor found on monitor {i}: {monitor}")
                        break
                
                # Fallback to primary monitor if cursor position detection fails
                if current_monitor is None:
                    current_monitor = sct.monitors[1]  # Primary monitor
                    print(f"Area mode: Using primary monitor as fallback: {current_monitor}")
                
                print(f"Area mode: Capturing freeze frame: {current_monitor}")
                screenshot = sct.grab(current_monitor)
                
                # Convert to PIL Image
                self.frozen_screen = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
                # Store monitor info for proper positioning
                self.freeze_frame_offset_x = current_monitor["left"]
                self.freeze_frame_offset_y = current_monitor["top"]
                self.freeze_frame_width = current_monitor["width"]
                self.freeze_frame_height = current_monitor["height"]
                
                # Create full-screen freeze overlay
                self.freeze_overlay = tk.Toplevel()
                self.freeze_overlay.title("Screen Frozen - Area Configuration Mode")
                self.freeze_overlay.overrideredirect(True)  # No window decorations
                self.freeze_overlay.attributes('-topmost', False)  # Don't stay on top of overlays
                
                # Position on the current monitor
                self.freeze_overlay.geometry(f"{self.freeze_frame_width}x{self.freeze_frame_height}+{self.freeze_frame_offset_x}+{self.freeze_frame_offset_y}")
                
                # Create canvas to display the frozen image
                self.freeze_canvas = tk.Canvas(
                    self.freeze_overlay, 
                    width=self.freeze_frame_width, 
                    height=self.freeze_frame_height,
                    highlightthickness=0,
                    bg="black"
                )
                self.freeze_canvas.pack(fill="both", expand=True)
                
                # Convert to PhotoImage and display
                self.frozen_photo = ImageTk.PhotoImage(self.frozen_screen)
                self.freeze_canvas.create_image(0, 0, image=self.frozen_photo, anchor="nw")
                
                print("Area mode: Freeze frame overlay created successfully")
                
        except Exception as e:
            print(f"Error freezing screen for areas: {e}")
            self._cleanup_freeze_overlay()  # Clean up on error
    
    def _cleanup_freeze_overlay(self):  # [AI_REF:screen_freeze_fix]
        """Clean up freeze overlay and related resources"""
        try:
            if hasattr(self, 'freeze_overlay') and self.freeze_overlay:
                self.freeze_overlay.destroy()
                self.freeze_overlay = None
        except:
            pass
            
        # Clean up freeze frame data
        if hasattr(self, 'frozen_screen'):
            self.frozen_screen = None
        if hasattr(self, 'freeze_canvas'):
            self.freeze_canvas = None
        if hasattr(self, 'frozen_photo'):
            self.frozen_photo = None
    
    def _unfreeze_screen_for_areas(self):  # [AI_REF:screen_freeze_fix]
        """Unfreeze screen when exiting area configuration mode"""        
        self._cleanup_freeze_overlay()
        print("Area mode: Screen unfrozen")
    
    def _start_bot(self):  # [AI_REF:gui_auto_hide]
        """Start the fishing bot loop and hide GUI"""
        if self.bot_running:
            return  # Already running
            
        print("Starting fishing bot...")
        
        # Initialize debug logging
        setup_debug_logging()
        debug_log("BOT STARTING - Debug logging initialized", "SYSTEM")
        
        self.bot_running = True
        
        # Hide GUI for distraction-free automation
        print("Hiding GUI for distraction-free automation...")
        self.withdraw()
        
        # Start bot loop in separate thread to prevent GUI freezing
        self.bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
        self.bot_thread.start()
        
        # Update status in GUI (even though hidden)
        self.after(0, self._update_status, "Bot Running", "green")
    
    def _stop_bot(self):  # [AI_REF:gui_auto_hide]
        """Stop the fishing bot loop and show GUI"""
        if not self.bot_running:
            print("Bot is already stopped")
            return  # Already stopped
            
        print("Stopping fishing bot...")
        self.bot_running = False
        self.current_stage = None
        
        # Clean up line indicators when bot stops
        self.clear_line_indicators()
        
        # Show GUI when bot stops
        print("Showing GUI after bot stop...")
        self.deiconify()
        
        # Restore always-on-top setting if enabled
        if ACTIVE_SETTINGS.get('always_on_top', False):
            self.attributes('-topmost', True)
        
        # Wait for bot thread to finish (with timeout)
        if self.bot_thread and self.bot_thread.is_alive():
            print("Waiting for bot thread to stop...")
            self.bot_thread.join(timeout=3)  # Wait up to 3 seconds
            if self.bot_thread.is_alive():
                print("Warning: Bot thread did not stop within timeout")
            else:
                print("Bot thread stopped successfully")
        
        # Update status in GUI
        self.after(0, self._update_status, "Bot Stopped", "red")
    
    def _ensure_gui_visible(self):  # [AI_REF:gui_auto_hide]
        """Utility method to ensure GUI is visible - used for safety in edge cases"""
        try:
            self.deiconify()
            # Restore always-on-top setting if enabled
            if ACTIVE_SETTINGS.get('always_on_top', False):
                self.attributes('-topmost', True)
            print("GUI restored to visible state")
        except Exception as e:
            print(f"Error restoring GUI visibility: {e}")
    
    def _reset_fishing_states(self):
        """Reset all fishing-related global variables and states to default values"""
        global InitialTargetCalculation, LeftTargetLine, RightTargetLine, LeftBar, RightBar
        global FishingOngoing, TargetLinePixelGap, ShakePass, NumFishLines
        global TargetLineMiddle, TargetBarMiddle
        global LineBarPixelDifference
        
        print("🔄 Resetting all fishing states to default values...")
        
        # Reset fish state variables
        InitialTargetCalculation = False
        LeftTargetLine = 0
        RightTargetLine = 0
        LeftBar = 0
        RightBar = 0
        FishingOngoing = False
        TargetLinePixelGap = 0
        TargetLineMiddle = 0
        TargetBarMiddle = 0
        LineBarPixelDifference = 0
        
        # Reset shake state variables
        ShakePass = False
        NumFishLines = 0
        
        # Reset control system state
        if hasattr(self, 'fishing_last_error'):
            self.fishing_last_error = 0.0
        if hasattr(self, 'current_mouse_state'):
            self.current_mouse_state = False
        if hasattr(self, 'last_debug_time'):
            delattr(self, 'last_debug_time')
        
        # Clear visual indicators
        self.clear_line_indicators()
        
        print("✅ All fishing states reset successfully")

    def _bot_loop(self):  # [AI_REF:program_flow_control]
        """Main bot loop: OneTimeRun > FirstStage > ShakeStage > FishStage (based on checkbox states)"""
        try:
            print("Bot loop started - checking enabled stages")
            
            # One-time initialization (if enabled)
            if self.bot_running and ACTIVE_SETTINGS.get('stage_one_time_run', True):
                print("OneTimeRun stage enabled - executing")
                self.current_stage = "OneTimeRun"
                self.after(0, self._update_status, f"Running: {self.current_stage}", "orange")
                self._one_time_run()
            else:
                print("OneTimeRun stage disabled - skipping")
            
            # Main loop
            while self.bot_running:
                try:
                    # Reset all fishing states at the beginning of each cycle
                    self._reset_fishing_states()
                    
                    # Stage 1: First Stage (if enabled)
                    if not self.bot_running:
                        print("Bot stopped during FirstStage check")
                        break
                        
                    if ACTIVE_SETTINGS.get('stage_first_stage', True):
                        print("FirstStage enabled - executing")
                        self.current_stage = "FirstStage"
                        self.after(0, self._update_status, f"Running: {self.current_stage}", "orange")
                        self._first_stage()
                    else:
                        print("FirstStage disabled - skipping")
                    
                    # Stage 2: Shake Stage (if enabled)
                    if not self.bot_running:
                        print("Bot stopped during ShakeStage check")
                        break
                        
                    if ACTIVE_SETTINGS.get('stage_shake_stage', True):
                        print("ShakeStage enabled - executing")
                        self.current_stage = "ShakeStage"
                        self.after(0, self._update_status, f"Running: {self.current_stage}", "orange")
                        shake_result = self._shake_stage()
                        
                        # If shake stage timed out, restart the loop
                        if shake_result == "timeout":
                            print("🔄 ShakeStage timeout - restarting bot loop")
                            continue  # Skip remaining stages and restart loop
                    else:
                        print("ShakeStage disabled - skipping")
                    
                    # Stage 3: Fish Stage (if enabled)
                    if not self.bot_running:
                        print("Bot stopped during FishStage check")
                        break
                        
                    if ACTIVE_SETTINGS.get('stage_fish_stage', True):
                        print("FishStage enabled - executing")
                        self.current_stage = "FishStage"
                        self.after(0, self._update_status, f"Running: {self.current_stage}", "orange")
                        self._fish_stage()
                    else:
                        print("FishStage disabled - skipping")
                    
                    # Brief pause between cycles with running check
                    for i in range(10):  # Check 10 times over 1 second
                        if not self.bot_running:
                            print("Bot stopped during cycle pause")
                            break
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"Error in bot loop: {e}")
                    # Continue the loop unless bot is stopped
                    if self.bot_running:
                        time.sleep(1)  # Wait a bit before retrying
            
            print("Bot loop ended normally")
                    
        except Exception as e:
            print(f"Fatal error in bot loop: {e}")
            self.bot_running = False
            
            # Show GUI on error (safety measure)
            print("Showing GUI due to bot error...")
            self.after(0, self.deiconify)
            
            # Restore always-on-top setting if enabled
            if ACTIVE_SETTINGS.get('always_on_top', False):
                self.after(0, lambda: self.attributes('-topmost', True))
            
            self.after(0, self._update_status, "Bot Error", "red")
    
    def _one_time_run(self):
        """One-time initialization - EMPTY"""
        print("OneTimeRun: EMPTY - doing nothing")
        pass
    
    def _first_stage(self):
        """First stage - Casting Flow Control"""
        print("FirstStage: Starting casting flow control...")
        
        # Check if casting flow control is enabled
        if not ACTIVE_SETTINGS.get('casting_enable_first_stage', True):
            print("FirstStage: Casting flow control disabled - skipping")
            return
        
        print("FirstStage: Casting flow control enabled - executing branch logic")
        
        # Determine which branch is active
        branch1_active = (ACTIVE_SETTINGS.get('casting_delay1_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_perfect_cast_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_delay2_enabled', False))
        
        branch2_active = (ACTIVE_SETTINGS.get('casting_delay3_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_hold_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_delay4_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_release_enabled', False) or 
                         ACTIVE_SETTINGS.get('casting_delay5_enabled', False))
        
        if branch1_active and not branch2_active:
            print("FirstStage: Executing Branch 1 (Perfect Cast Flow)")
            self._execute_casting_branch1()
        elif branch2_active and not branch1_active:
            print("FirstStage: Executing Branch 2 (Hold & Release Flow)")
            self._execute_casting_branch2()
        elif branch1_active and branch2_active:
            print("FirstStage: WARNING - Both branches active, defaulting to Branch 1")
            self._execute_casting_branch1()
        else:
            print("FirstStage: No casting branch active - skipping casting flow")
        
        print("FirstStage: Casting flow control completed")
    
    def _execute_casting_branch1(self):
        """Execute Branch 1: Perfect Cast Flow (Delay 1 -> Perfect Cast -> Delay 2 -> Exit)"""
        print("Branch 1: Starting Perfect Cast Flow")
        
        # Delay 1
        if ACTIVE_SETTINGS.get('casting_delay1_enabled', False):
            delay_duration = ACTIVE_SETTINGS.get('casting_delay1_duration', 0.5)
            print(f"Branch 1: Executing Delay 1 ({delay_duration}s)")
            self._casting_delay(delay_duration, "Delay 1")
        else:
            print("Branch 1: Delay 1 disabled - skipping")
        
        # Perfect Cast (placeholder for future implementation)
        if ACTIVE_SETTINGS.get('casting_perfect_cast_enabled', False):
            print("Branch 1: Executing Perfect Cast (placeholder - no action)")
            self._casting_perfect_cast()
        else:
            print("Branch 1: Perfect Cast disabled - skipping")
        
        # Delay 2
        if ACTIVE_SETTINGS.get('casting_delay2_enabled', False):
            delay_duration = ACTIVE_SETTINGS.get('casting_delay2_duration', 0.5)
            print(f"Branch 1: Executing Delay 2 ({delay_duration}s)")
            self._casting_delay(delay_duration, "Delay 2")
        else:
            print("Branch 1: Delay 2 disabled - skipping")
        
        # Exit (implicit - just log completion)
        print("Branch 1: Perfect Cast Flow completed - Exit")
    
    def _execute_casting_branch2(self):
        """Execute Branch 2: Hold & Release Flow (Delay 3 -> Hold -> Delay 4 -> Release -> Delay 5 -> Exit)"""
        print("Branch 2: Starting Hold & Release Flow")
        
        # Delay 3
        if ACTIVE_SETTINGS.get('casting_delay3_enabled', False):
            delay_duration = ACTIVE_SETTINGS.get('casting_delay3_duration', 0.5)
            print(f"Branch 2: Executing Delay 3 ({delay_duration}s)")
            self._casting_delay(delay_duration, "Delay 3")
        else:
            print("Branch 2: Delay 3 disabled - skipping")
        
        # Hold (left click down)
        if ACTIVE_SETTINGS.get('casting_hold_enabled', False):
            print("Branch 2: Executing Hold (left click down)")
            self._casting_hold()
        else:
            print("Branch 2: Hold disabled - skipping")
        
        # Delay 4
        if ACTIVE_SETTINGS.get('casting_delay4_enabled', False):
            delay_duration = ACTIVE_SETTINGS.get('casting_delay4_duration', 0.5)
            print(f"Branch 2: Executing Delay 4 ({delay_duration}s)")
            self._casting_delay(delay_duration, "Delay 4")
        else:
            print("Branch 2: Delay 4 disabled - skipping")
        
        # Release (left click up)
        if ACTIVE_SETTINGS.get('casting_release_enabled', False):
            print("Branch 2: Executing Release (left click up)")
            self._casting_release()
        else:
            print("Branch 2: Release disabled - skipping")
        
        # Delay 5
        if ACTIVE_SETTINGS.get('casting_delay5_enabled', False):
            delay_duration = ACTIVE_SETTINGS.get('casting_delay5_duration', 0.5)
            print(f"Branch 2: Executing Delay 5 ({delay_duration}s)")
            self._casting_delay(delay_duration, "Delay 5")
        else:
            print("Branch 2: Delay 5 disabled - skipping")
        
        # Exit (implicit - just log completion)
        print("Branch 2: Hold & Release Flow completed - Exit")
    
    def _casting_delay(self, duration, name):
        """Execute a configurable delay with bot running check"""
        if not self.bot_running:
            print(f"Casting {name}: Bot stopped during delay - aborting")
            return
            
        print(f"Casting {name}: Waiting {duration}s...")
        
        # Break delay into small chunks to allow for bot stop detection
        total_time = 0
        chunk_size = 0.1  # 100ms chunks
        
        while total_time < duration and self.bot_running:
            time.sleep(min(chunk_size, duration - total_time))
            total_time += chunk_size
        
        if not self.bot_running:
            print(f"Casting {name}: Bot stopped during delay")
        else:
            print(f"Casting {name}: Delay completed")
    
    def _casting_perfect_cast(self):
        """Perfect Cast placeholder - for future implementation"""
        print("Perfect Cast: Placeholder function - no action taken")
        # TODO: Implement perfect cast logic in the future
        pass
    
    def _casting_hold(self):
        """Execute left click down (hold)"""
        try:
            if not self.bot_running:
                print("Casting Hold: Bot stopped - aborting")
                return
                
            print("Casting Hold: Pressing and holding left mouse button")
            # Use pyautogui to press and hold left mouse button
            pyautogui.mouseDown(button='left')
            print("Casting Hold: Left mouse button is now held down")
            
        except Exception as e:
            print(f"Casting Hold: Error - {e}")
    
    def _casting_release(self):
        """Execute left click up (release)"""
        try:
            if not self.bot_running:
                print("Casting Release: Bot stopped - aborting")
                return
                
            print("Casting Release: Releasing left mouse button")
            # Use pyautogui to release left mouse button
            pyautogui.mouseUp(button='left')
            print("Casting Release: Left mouse button released")
            
        except Exception as e:
            print(f"Casting Release: Error - {e}")
    
    def _shake_stage(self):
        """
        ShakeStage Logic (Updated):
        - Activate Update_Fish_Status at 10/20 FPS (scan_fps setting)
        - Activate Update_Shake_Status at 10/20 FPS (scan_shake_fps setting)  
        - Start "No Circle Found Timeout" timer (3 seconds default)
        - Duplicate circle detection with "Duplicate Circle Timeout"
        - If Update_Shake_Status clicks circle -> reset No Circle Found timer
        - If Update_Fish_Status shows "4 lines" -> pass to FishStage
        - If No Circle Found timer expires -> exit to FirstStage
        """
        global NumFishLines, ShakePass
        
        print("🎯 ShakeStage: Starting shake minigame...")
        
        # Get FPS settings for both update functions
        try:
            fish_fps = int(ACTIVE_SETTINGS.get('scan_fps', '60'))  # Update_Fish_Status FPS
            if fish_fps not in [10, 20]:
                fish_fps = 10  # Default to 10 if not 10 or 20
            # Reduce fish detection frequency during ShakeStage to reduce log spam
            fish_fps = min(fish_fps, 5)  # Cap at 5 FPS during ShakeStage
        except (ValueError, TypeError):
            fish_fps = 5  # Use lower default for ShakeStage
            
        try:
            shake_fps = int(ACTIVE_SETTINGS.get('scan_shake_fps', '10'))  # Update_Shake_Status FPS
            if shake_fps not in [10, 20]:
                shake_fps = 10  # Default to 10 if not 10 or 20
        except (ValueError, TypeError):
            shake_fps = 10
            
        # Get timer duration settings
        try:
            no_circle_timeout = float(ACTIVE_SETTINGS.get('no_circle_timeout', '3.0'))  # No Circle Found Timeout
        except (ValueError, TypeError):
            no_circle_timeout = 3.0
            
        try:
            duplicate_circle_timeout = float(ACTIVE_SETTINGS.get('shake_timer', '1.0'))  # Duplicate Circle Timeout (renamed)
        except (ValueError, TypeError):
            duplicate_circle_timeout = 1.0
            
        # Calculate intervals
        fish_interval = 1.0 / fish_fps
        shake_interval = 1.0 / shake_fps
        
        print(f"🎯 ShakeStage: Fish FPS={fish_fps} (interval={fish_interval:.3f}s)")
        print(f"🎯 ShakeStage: Shake FPS={shake_fps} (interval={shake_interval:.3f}s)")
        print(f"🎯 ShakeStage: No Circle Found Timeout={no_circle_timeout}s")
        print(f"🎯 ShakeStage: Duplicate Circle Timeout={duplicate_circle_timeout}s")
        
        # Initialize timing variables
        no_circle_timer_start = time.time()
        last_fish_scan = 0
        last_shake_scan = 0
        
        # Initialize duplicate circle detection
        last_circle_position = None
        duplicate_timer_start = None
        duplicate_timer_active = False
        
        # Reset shake state at the start
        self.reset_shake_clicked_locations()

        ShakePass = False

        # Main loop
        while self.bot_running:
            current_time = time.time()
            
            # Update_Fish_Status at specified FPS rate
            if current_time - last_fish_scan >= fish_interval:
                last_fish_scan = current_time
                
                try:
                    # Activate Update_Fish_Status (suppress logs during ShakeStage for performance)
                    self.update_fish_state(suppress_verbose_logs=True)
                    
                    # Check if ShakePass is True (success condition for advancing to FishStage)
                    if ShakePass:
                        print("✅ ShakeStage: ShakePass=True - passing to FishStage!")
                        return None  # Pass to next stage (FishStage)
                        
                except Exception as e:
                    print(f"❌ ShakeStage: Error in Update_Fish_Status: {e}")
            
            # Update_Shake_Status at specified FPS rate
            if current_time - last_shake_scan >= shake_interval:
                last_shake_scan = current_time
                
                try:
                    # Simply call update_shake_state() which handles both detection AND clicking with built-in duplicate prevention
                    clicked_circles = self.update_shake_state()
                    
                    if clicked_circles:
                        print(f"🎯 ShakeStage: Found and clicked {len(clicked_circles)} circles")
                        # Reset No Circle Found timer since we clicked a circle
                        no_circle_timer_start = current_time
                        
                        # Update last circle position for duplicate timer logic
                        first_circle = clicked_circles[0]
                        current_position = (first_circle['screen_x'], first_circle['screen_y'])
                        
                        # Check if same as previous circle (within 20px tolerance)
                        is_same_circle = False
                        if last_circle_position:
                            distance = ((current_position[0] - last_circle_position[0])**2 + 
                                      (current_position[1] - last_circle_position[1])**2)**0.5
                            if distance <= 20:  # Same circle if within 20px
                                is_same_circle = True
                        
                        if is_same_circle and not duplicate_timer_active:
                            # Start duplicate circle timer
                            print(f"🔄 ShakeStage: Same circle clicked - starting Duplicate Circle Timer ({duplicate_circle_timeout}s)")
                            duplicate_timer_start = current_time
                            duplicate_timer_active = True
                        elif not is_same_circle:
                            # Different circle - reset duplicate timer
                            duplicate_timer_active = False
                            duplicate_timer_start = None
                        
                        # Update last circle position
                        last_circle_position = current_position
                    else:
                        print("🔍 ShakeStage: No circles found")
                        
                    # Check if duplicate timer expired
                    if duplicate_timer_active and duplicate_timer_start:
                        duplicate_elapsed = current_time - duplicate_timer_start
                        if duplicate_elapsed >= duplicate_circle_timeout:
                            print(f"⏰ ShakeStage: Duplicate Circle Timer expired - resetting clicked locations")
                            # Reset the "previous area" by clearing clicked locations
                            self.reset_shake_clicked_locations()
                            
                            # Reset duplicate tracking
                            last_circle_position = None
                            duplicate_timer_active = False
                            duplicate_timer_start = None
                        
                except Exception as e:
                    print(f"❌ ShakeStage: Error in Update_Shake_Status: {e}")
            
            # Check if No Circle Found timer has expired
            no_circle_elapsed = current_time - no_circle_timer_start
            if no_circle_elapsed >= no_circle_timeout:
                print(f"⏰ ShakeStage: No Circle Found Timer expired ({no_circle_timeout}s) - exiting to FirstStage")
                return "timeout"  # Exit 3-stage loop and return to FirstStage
            
            # Brief sleep to prevent excessive CPU usage
            time.sleep(0.01)  # 10ms sleep
            
            # Check if bot should stop
            if not self.bot_running:
                print("🛑 ShakeStage: Bot stopped")
                return None
        
        print("✅ ShakeStage: Completed (should not reach here)")
        return None
    
    def _detect_circles_without_clicking(self):
        """
        Detect circles using the SAME sophisticated logic as update_shake_state but WITHOUT clicking
        Returns list of circles found, using exact same detection algorithms
        """
        try:
            # Get shake area from settings (SAME as original)
            shake_area = ACTIVE_SETTINGS.get('shake_area', '')
            if not shake_area:
                return []
            
            # Parse area string format: WIDTHxHEIGHT+X+Y (SAME as original)
            try:
                parts = shake_area.replace('x', '+').replace('+', ' ').split()
                width, height, x, y = map(int, parts)
            except (ValueError, IndexError):
                return []
            
            # Take screenshot (SAME as original)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # EXACT SAME processing as update_shake_state
            blurred = cv2.GaussianBlur(frame, (9, 9), 2)
            gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (SAME as original)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # SAME circle detection logic as original
            big_circles = []
            
            # Get minimum radius (SAME as original)
            try:
                min_radius = int(ACTIVE_SETTINGS.get('shake_min_radius', '10'))
            except (ValueError, TypeError):
                min_radius = 10
            
            # HoughCircles detection (EXACT SAME parameters as original)
            hough_circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=37, param1=75, param2=42, minRadius=min_radius, maxRadius=170)
            if hough_circles is not None:
                hough_circles = np.round(hough_circles[0, :]).astype("int")
                for (cx, cy, r) in hough_circles:
                    # SAME validation as original
                    edge_points_found = 0
                    total_sample_points = 16
                    for i in range(total_sample_points):
                        angle = (2 * np.pi * i) / total_sample_points
                        sample_x = int(cx + r * np.cos(angle))
                        sample_y = int(cy + r * np.sin(angle))
                        if 0 <= sample_x < gray.shape[1] and 0 <= sample_y < gray.shape[0]:
                            if edges[sample_y, sample_x] > 0:
                                edge_points_found += 1
                    
                    if edge_points_found / total_sample_points > 0.38:
                        big_circles.append({'center': (cx, cy), 'radius': r})
            
            # Contour-based detection (EXACT SAME logic as original)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < (min_radius * min_radius):
                    continue
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if not (0.7 < circularity < 1.3):
                    continue
                
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                
                if radius < min_radius:
                    continue
                
                fitted_circle_area = np.pi * radius * radius
                area_ratio = area / fitted_circle_area
                if not (0.7 < area_ratio < 1.3):
                    continue
                
                center = np.array([cx, cy])
                distances = [np.linalg.norm(point[0] - center) for point in contour]
                if len(distances) < 8:
                    continue
                
                distances = np.array(distances)
                coefficient_of_variation = np.std(distances) / np.mean(distances) if np.mean(distances) > 0 else float('inf')
                if coefficient_of_variation > 0.22:
                    continue
                
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                convexity = area / hull_area if hull_area > 0 else 0
                if convexity < 0.78:
                    continue
                
                big_circles.append({'center': (int(cx), int(cy)), 'radius': int(radius)})
            
            # Convert to screen coordinates (SAME as original)
            result = []
            for circle in big_circles:
                screen_x = x + circle['center'][0]
                screen_y = y + circle['center'][1]
                result.append({
                    'screen_x': screen_x,
                    'screen_y': screen_y,
                    'radius': circle['radius'],
                    'type': 'BIG'
                })
            
            return result
            
        except Exception as e:
            print(f"❌ Error in _detect_circles_without_clicking: {e}")
            return []
    

    def _fish_stage(self):
        """
        Fish stage - Automated fish bar minigame handling
        Uses FPS-controlled fish state monitoring with timeout on FishingOngoing = False
        """
        global FishingOngoing, LineBarPixelDifference
        
        print("🐟 FishStage: Starting fish bar minigame detection...")
        
        # Get settings from ACTIVE_SETTINGS with safe conversion
        try:
            scan_fps = int(ACTIVE_SETTINGS.get('scan_fps', '60'))
        except (ValueError, TypeError):
            scan_fps = 60
            print(f"⚠️ Warning: Invalid scan_fps, using default 60 FPS")
            
        try:
            fish_lost_timeout = float(ACTIVE_SETTINGS.get('fish_lost_timeout', '1.0'))
        except (ValueError, TypeError):
            fish_lost_timeout = 1.0
            print(f"⚠️ Warning: Invalid fish_lost_timeout, using default 1.0s")
            
        scan_interval = 1.0 / scan_fps  # Calculate interval between scans
        
        print(f"🐟 FishStage: Scan FPS={scan_fps} (interval={scan_interval:.3f}s), Fish Lost Timeout={fish_lost_timeout}s")
        
        # Initialize timer variables
        last_scan_time = 0
        timeout_timer_active = False
        timeout_start_time = 0
        
        # Main fish detection loop
        while self.bot_running:
            current_time = time.time()
            
            # Check if it's time for next scan based on FPS
            if current_time - last_scan_time >= scan_interval:
                last_scan_time = current_time
                
                # Perform fish state update (suppress verbose logs for performance)
                try:
                    self.update_fish_state(suppress_verbose_logs=True)
                    
                    # Check FishingOngoing status
                    if FishingOngoing:
                        # Fishing is active - reset/disable timeout timer
                        if timeout_timer_active:
                            timeout_timer_active = False
                            timeout_start_time = 0
                        
                        # Access global variables for processing (available after update_fish_state)
                        # These variables are updated by update_fish_state() and can be used for logic
                        try:
                            if 'LineBarPixelDifference' in globals() and LineBarPixelDifference is not None:
                                # Fishing Control System - Roblox acceleration formula
                                self.fishing_control_system(LineBarPixelDifference, current_time)
                                
                        except NameError:
                            # Variables not yet initialized - this is normal on first run
                            pass
                        
                    else:
                        # Fishing is not active - start/continue timeout timer
                        if not timeout_timer_active:
                            timeout_timer_active = True
                            timeout_start_time = current_time
                        else:
                            # Check if timeout has expired
                            elapsed_timeout = current_time - timeout_start_time
                            if elapsed_timeout >= fish_lost_timeout:
                                print(f"⏰ FishStage: Fish lost timeout reached ({fish_lost_timeout}s) - exiting to next stage")
                                # Clean up line indicators when exiting fish stage
                                self.clear_line_indicators()
                                print("🧹 Cleared line indicators on timeout exit")
                                return  # Exit function, continue to next stage
                    
                except Exception as e:
                    print(f"❌ FishStage: Error during fish state update: {e}")
            
            # Brief sleep to prevent excessive CPU usage
            time.sleep(0.01)  # 10ms sleep
            
            # Check if bot should stop
            if not self.bot_running:
                print("🛑 FishStage: Bot stopped during fish detection")
                # Clean up line indicators when bot stops
                self.clear_line_indicators()
                print("🧹 Cleared line indicators on bot stop")
                return
        
        # Clean up line indicators when exiting fish stage
        self.clear_line_indicators()
        print("🧹 Cleared line indicators on normal exit")
        print("✅ FishStage: Completed successfully")
    
    def fishing_control_system(self, unused_pixel_diff, current_time):
        """
        SIMPLIFIED Fishing Control System - Move bar towards target line
        Basic PD controller: just KP, KD, and clamp
        """
        global TargetLineMiddle, TargetBarMiddle
        
        # Initialize if first run
        if not hasattr(self, 'fishing_last_error'):
            self.fishing_last_error = 0.0
            self.current_mouse_state = False  # False = released, True = held
        
        # Get positions - exit if invalid
        target_x = TargetLineMiddle
        bar_x = TargetBarMiddle
        if not target_x or not bar_x:
            return
        
        # Simple PD Control Parameters
        KP = 0.5      # Proportional gain
        KD = 10.0     # Derivative gain  
        CLAMP = 10.0  # Signal clamp limit
        DEAD_ZONE = 5.0  # Dead zone for spam clicking
        
        # Calculate error (positive = target is right of bar)
        error = target_x - bar_x
        
        # Calculate derivative (rate of error change)
        derivative = (error - self.fishing_last_error) if self.fishing_last_error is not None else 0.0
        
        # PD Control Signal
        signal = (KP * error) + (KD * derivative)
        signal = max(-CLAMP, min(CLAMP, signal))  # Clamp signal
        
        # Update state
        self.fishing_last_error = error
        
        # Control Logic: Hold mouse if signal > dead zone, Release if < -dead zone, Spam in dead zone
        if signal > DEAD_ZONE:
            # Target is right, hold mouse to move bar right
            if not self.current_mouse_state:
                self.fishing_mouse_down()
                self.current_mouse_state = True
        elif signal < -DEAD_ZONE:
            # Target is left, release mouse to move bar left
            if self.current_mouse_state:
                self.fishing_mouse_up()
                self.current_mouse_state = False
        else:
            # Dead zone - spam click (alternate state)
            if self.current_mouse_state:
                self.fishing_mouse_up()
                self.current_mouse_state = False
            else:
                self.fishing_mouse_down()
                self.current_mouse_state = True
        
        # Simple debug (every 200ms)
        if not hasattr(self, 'last_debug_time') or (current_time - self.last_debug_time > 0.2):
            print(f"🎯 Error: {error:.1f}px | Signal: {signal:+.1f} | Hold: {self.current_mouse_state}")
            self.last_debug_time = current_time

        # Debug output (reduced frequency)
        if hasattr(self, 'last_debug_time'):
            if current_time - self.last_debug_time > 0.2:  # Debug every 200ms
                print(f"� Pixel: {error:.1f}px | Signal: {signal:+.2f} | Hold: {self.current_mouse_state} | Target: {target_x} | Bar: {bar_x}")
                self.last_debug_time = current_time
        else:
            self.last_debug_time = current_time
    
    def fishing_mouse_down(self):
        """Hold left mouse button down for fishing"""
        try:
            import ctypes
            from ctypes import windll
            # Send mouse down event (WM_LBUTTONDOWN)
            windll.user32.mouse_event(2, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN = 2
        except Exception as e:
            print(f"❌ Error holding mouse: {e}")
    
    def fishing_mouse_up(self):
        """Release left mouse button for fishing"""
        try:
            import ctypes
            from ctypes import windll
            # Send mouse up event (WM_LBUTTONUP)
            windll.user32.mouse_event(4, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP = 4
        except Exception as e:
            print(f"❌ Error releasing mouse: {e}")

    def FirstRunUpdateFishState(self, line_coordinates, geom_width):
        """
        FirstRunUpdateFishState: Process initial 4 lines
        - Find 2 lines closest to middle as target lines
        - Calculate TargetLineGap between target lines
        - Set LeftBar as most left line, RightBar as most right line
        """
        global InitialTargetCalculation, LeftTargetLine, RightTargetLine, LeftBar, RightBar, FishingOngoing, TargetLinePixelGap, ShakePass
        print("🎯 FirstRunUpdateFishState: Executing initial target calculation...")

        ShakePass = True
        
        # Sort lines by x-coordinate
        sorted_lines = sorted(line_coordinates)
        
        # Calculate middle position of geometry
        geometry_middle = geom_width / 2
        
        # Find the 2 lines closest to the middle
        distances_to_middle = [(abs(line - geometry_middle), line) for line in sorted_lines]
        distances_to_middle.sort(key=lambda x: x[0])  # Sort by distance to middle
        
        # The 2 lines with smallest distances to middle are target lines
        closest_to_middle = [distances_to_middle[0][1], distances_to_middle[1][1]]
        closest_to_middle.sort()  # Sort by x-coordinate
        
        # Set target lines (left is smaller x, right is larger x)
        LeftTargetLine = closest_to_middle[0]
        RightTargetLine = closest_to_middle[1]
        
        # Calculate the pixel gap between target lines (TargetLineGap)
        TargetLinePixelGap = RightTargetLine - LeftTargetLine
        
        # Set bars to the most left and most right lines
        LeftBar = sorted_lines[0]   # Most left line
        RightBar = sorted_lines[-1] # Most right line

        # Set the flags
        InitialTargetCalculation = True
        FishingOngoing = True
        
        print(f"✅ FirstRunUpdateFishState: Completed successfully")
        print(f"   Sorted lines: {sorted_lines}")
        print(f"   LeftTargetLine: {LeftTargetLine}")
        print(f"   RightTargetLine: {RightTargetLine}")
        print(f"   TargetLinePixelGap: {TargetLinePixelGap} pixels")
        print(f"   LeftBar: {LeftBar}")
        print(f"   RightBar: {RightBar}")
        print("✅ FirstRunUpdateFishState: InitialTargetCalculation set to True")
        print("✅ FirstRunUpdateFishState: FishingOngoing set to True")
        
        # Create line indicators when entering fish state
        try:
            fish_bar_area = ACTIVE_SETTINGS.get('fish_bar_area', '')
            if fish_bar_area:
                # Parse area string format: WIDTHxHEIGHT+X+Y
                try:
                    if 'x' in fish_bar_area and '+' in fish_bar_area:
                        parts = fish_bar_area.replace('+', 'x').split('x')
                        width, height, x, y = map(int, parts)
                        monitor = {'left': x, 'top': y, 'width': width, 'height': height}
                        
                        # Create line indicators for initial detected lines
                        self.create_line_indicators(line_coordinates, monitor)
                        print(f"✅ Created line indicators for {len(line_coordinates)} lines")
                    else:
                        print(f"❌ Invalid fish_bar_area format: '{fish_bar_area}'")
                except ValueError as ve:
                    print(f"❌ Error parsing fish_bar_area: {ve}")
            else:
                print(f"⚠️ No fish_bar_area configured - skipping line indicators")
        except Exception as e:
            print(f"❌ Error creating line indicators: {e}")
    
    def SubsequentRunUpdateFishState(self, total_lines, line_coordinates, geom_width):
        """
        FAST STREAMLINED VERSION - Essential systems only
        Finds target pair with fixed gap, updates coordinates, moves indicators
        """
        global FishingOngoing, LeftTargetLine, RightTargetLine, LeftBar, RightBar, TargetLineMiddle, TargetBarMiddle, TargetLinePixelGap

        # Quick validation
        if total_lines < 2 or total_lines > 6:
            FishingOngoing = False
            return
        
        # Sort lines and get safe fallbacks
        sorted_lines = sorted(line_coordinates)
        old_left_target = LeftTargetLine if LeftTargetLine != 0 else geom_width * 0.4
        old_right_target = RightTargetLine if RightTargetLine != 0 else geom_width * 0.6
        old_left_bar = LeftBar if LeftBar != 0 else geom_width * 0.1
        old_right_bar = RightBar if RightBar != 0 else geom_width * 0.9
        
        # Find best target pair with fixed gap
        best_gap_diff = float('inf')
        best_left_target = None
        best_right_target = None
        
        for i in range(len(sorted_lines)):
            for j in range(i + 1, len(sorted_lines)):
                gap_diff = abs((sorted_lines[j] - sorted_lines[i]) - TargetLinePixelGap)
                if gap_diff < best_gap_diff:
                    best_gap_diff = gap_diff
                    best_left_target = sorted_lines[i]
                    best_right_target = sorted_lines[j]
        
        # Use target pair if good match, otherwise fallback to closest lines
        if best_gap_diff <= TargetLinePixelGap * 0.4 and best_left_target is not None:
            LeftTargetLine = best_left_target
            RightTargetLine = best_right_target
            remaining_lines = [x for x in sorted_lines if x != LeftTargetLine and x != RightTargetLine]
            
            if len(remaining_lines) >= 2:
                LeftBar = min(remaining_lines)
                RightBar = max(remaining_lines)
            elif len(remaining_lines) == 1:
                if abs(remaining_lines[0] - old_left_bar) < abs(remaining_lines[0] - old_right_bar):
                    LeftBar = remaining_lines[0]
                    RightBar = old_right_bar
                else:
                    LeftBar = old_left_bar
                    RightBar = remaining_lines[0]
            else:
                LeftBar = old_left_bar
                RightBar = old_right_bar
        else:
            # Fallback: use closest lines to previous positions
            LeftTargetLine = min(sorted_lines, key=lambda x: abs(x - old_left_target))
            RightTargetLine = LeftTargetLine + TargetLinePixelGap
            LeftBar = min(sorted_lines, key=lambda x: abs(x - old_left_bar))
            RightBar = min(sorted_lines, key=lambda x: abs(x - old_right_bar))
        
        # Safety checks - never allow zero
        if LeftTargetLine == 0 or LeftTargetLine is None: LeftTargetLine = geom_width * 0.4
        if RightTargetLine == 0 or RightTargetLine is None: RightTargetLine = geom_width * 0.6
        if LeftBar == 0 or LeftBar is None: LeftBar = geom_width * 0.1
        if RightBar == 0 or RightBar is None: RightBar = geom_width * 0.9
        
        # Calculate control coordinates
        TargetLineMiddle = (LeftTargetLine + RightTargetLine) / 2
        TargetBarMiddle = (LeftBar + RightBar) / 2
        
        # Final safety for middle coordinates
        if TargetLineMiddle == 0: TargetLineMiddle = geom_width * 0.5
        if TargetBarMiddle == 0: TargetBarMiddle = geom_width * 0.5
        
        # Move line indicators (fast version)
        fish_bar_area = ACTIVE_SETTINGS.get('fish_bar_area', '')
        if fish_bar_area and 'x' in fish_bar_area and '+' in fish_bar_area:
            try:
                parts = fish_bar_area.replace('+', 'x').split('x')
                width, height, x, y = map(int, parts)
                monitor = {'left': x, 'top': y, 'width': width, 'height': height}
                self.move_line_indicators(line_coordinates, monitor)
            except:
                pass  # Silently fail to avoid lag
    

    
    def update_fish_state(self, save_debug_images=False, suppress_verbose_logs=False):
        """
        SINGLE FUNCTION: Complete fish processing pipeline from b.py
        Takes snapshot, processes it step-by-step, shows screenshots, analyzes results
        save_debug_images: If True, saves debug images to disk (only for testing)
        suppress_verbose_logs: If True, reduces debug log verbosity (used during ShakeStage)
        """
        global ShakePass, TargetLineSeperation, MiddleOfPlayArea, LastKnownLeftBar, LastKnownRightBar, InitialTargetCalculation, LeftTargetLine, RightTargetLine, LeftBar, RightBar, FishingOngoing, NumFishLines
        
        # Local x coordinate variables
        x1, x2, x3, x4 = 0, 0, 0, 0
        
        # Initialize target line separation variable
        target_line_separation_pixels = 0
        
        try:
            # Cache screen resolution - only calculate once per session
            if not hasattr(self, '_cached_screen_params'):
                current_width = self.winfo_screenwidth()
                current_height = self.winfo_screenheight()
                
                # Reference resolution (original design resolution)  
                ref_width = 2560
                ref_height = 1440
                
                # Cache calculated parameters to avoid recalculation every frame
                self._cached_screen_params = {
                    'gap_tolerance': int(7 * ref_width / current_width),
                    'min_height': int(10 * ref_height / current_height)
                }
                print(f"📊 Cached screen params: gap_tolerance={self._cached_screen_params['gap_tolerance']}, min_height={self._cached_screen_params['min_height']}")
            
            gap_tolerance = self._cached_screen_params['gap_tolerance']
            min_height = self._cached_screen_params['min_height']
            
            # Get fish bar area from settings
            fish_bar_area = ACTIVE_SETTINGS.get('fish_bar_area', '')
            if not fish_bar_area:
                print("❌ No fish_bar_area configured in settings!")
                return
            
            # Parse area string format: WIDTHxHEIGHT+X+Y
            try:
                parts = fish_bar_area.replace('+', 'x').split('x')
                if len(parts) != 4:
                    print(f"❌ Invalid area format: {fish_bar_area}")
                    return
                
                width, height, x, y = map(int, parts)
                monitor = {
                    "left": x,
                    "top": y,
                    "width": width,
                    "height": height
                }
                
            except Exception as e:
                print(f"❌ Error parsing area: {e}")
                return
            
            # Generate timestamp for debug files (only if saving)
            if save_debug_images:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # STEP: Take screenshot
            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                # Convert PIL to numpy array for OpenCV
                img_array = np.array(img)
            
            # Save original image (only for testing)
            if save_debug_images:
                original_filename = f"fish_bar_capture_{timestamp}.png"
                img.save(original_filename)
            
            # STEP 1: Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            if save_debug_images:
                step1_filename = f"step1_grayscale_{timestamp}.png"
                cv2.imwrite(step1_filename, gray)
            
            # STEP 2: Apply dual vertical edge kernels
            # Detect left edges (dark-to-light)
            left_kernel = np.array([[-2, 2]], dtype=np.float32)
            left_edges = cv2.filter2D(gray, -1, left_kernel)
            
            # Detect right edges (light-to-dark)
            right_kernel = np.array([[2, -2]], dtype=np.float32)
            right_edges = cv2.filter2D(gray, -1, right_kernel)
            
            # Combine both edge directions and amplify
            vertical_edges = np.maximum(np.abs(left_edges), np.abs(right_edges))
            vertical_edges = vertical_edges * 2
            
            if save_debug_images:
                step2_filename = f"step2_kernel_edges_{timestamp}.png"
                cv2.imwrite(step2_filename, vertical_edges)
            # Step 2: Applied dual vertical edge kernels
            
            # STEP 3: Threshold to get strong vertical edges
            _, thresh = cv2.threshold(vertical_edges, 35, 255, cv2.THRESH_BINARY)
            if save_debug_images:
                step3_filename = f"step3_threshold_{timestamp}.png"
                cv2.imwrite(step3_filename, thresh)
            # Step 3: Applied threshold (35)
            
            # STEP 4: OPTIMIZED Filter for valid vertical lines 
            def filter_top_to_bottom_lines(thresh_image):
                """
                PERFORMANCE OPTIMIZED: Vectorized vertical line filtering
                Same logic but 5x faster using numpy vectorization
                """
                img_height, img_width = thresh_image.shape
                result = np.zeros_like(thresh_image)
                
                # Find all columns with any white pixels (vectorized)
                column_sums = np.sum(thresh_image, axis=0)
                active_columns = np.where(column_sums > 0)[0]
                
                # Process only active columns (much faster)
                for col_x in active_columns:
                    column = thresh_image[:, col_x]
                    white_pixels = np.where(column == 255)[0]
                    
                    if len(white_pixels) == 0:
                        continue
                    
                    # Fast edge touch check
                    touches_top = (white_pixels[0] == 0)
                    touches_bottom = (white_pixels[-1] == (img_height - 1))
                    
                    if not (touches_top or touches_bottom):
                        continue
                    
                    # Vectorized gap checking (faster than loop)
                    if len(white_pixels) > 1:
                        gaps = np.diff(white_pixels) - 1
                        if np.any(gaps > gap_tolerance):
                            continue
                    
                    # Fast edge gap checks
                    if not touches_top and white_pixels[0] > gap_tolerance:
                        continue
                    if not touches_bottom and (img_height - 1 - white_pixels[-1]) > gap_tolerance:
                        continue
                    
                    # Fast coverage check (60% threshold)
                    if (len(white_pixels) / img_height) <= 0.6:
                        continue
                    
                    # Keep this column (passed all tests)
                    result[:, col_x] = column
                
                return result
            
            vertical_lines = filter_top_to_bottom_lines(thresh)
            if save_debug_images:
                step4_filename = f"step4_morphology_{timestamp}.png"
                cv2.imwrite(step4_filename, vertical_lines)
            
            # Count lines by grouping consecutive x-coordinates as single lines
            img_height, img_width = vertical_lines.shape
            
            # Find all x coordinates with white pixels
            x_coordinates_with_pixels = []
            for col_x in range(img_width):
                column = vertical_lines[:, col_x]
                white_pixels = np.where(column == 255)[0]
                
                if len(white_pixels) > 0:
                    x_coordinates_with_pixels.append(col_x)
            
            # Group consecutive x-coordinates into single lines
            line_groups = []
            if x_coordinates_with_pixels:
                current_group = [x_coordinates_with_pixels[0]]
                
                for i in range(1, len(x_coordinates_with_pixels)):
                    current_x = x_coordinates_with_pixels[i]
                    previous_x = x_coordinates_with_pixels[i-1]
                    
                    # If consecutive (touching), add to current group
                    if current_x == previous_x + 1:
                        current_group.append(current_x)
                    else:
                        # Gap found, save current group and start new one
                        line_groups.append(current_group)
                        current_group = [current_x]
                
                # Add the last group
                line_groups.append(current_group)
            
            # Calculate line count and representative coordinates
            total_lines = len(line_groups)
            NumFishLines = total_lines  # Set global variable for ShakeStage
            line_coordinates = []
            for group in line_groups:
                # Use middle coordinate of each group as representative
                middle_x = group[len(group) // 2]
                line_coordinates.append(middle_x)
            
            # Reduced debug logging for performance (only log when suppress_verbose_logs=False)
            if not suppress_verbose_logs:
                debug_log(f"LINE DETECTION: total_lines={total_lines}, coordinates={line_coordinates}", "LINES")
            
            # STEP 5: Final output (only save if debug mode)
            if save_debug_images:
                step5_filename = f"step5_final_output_{timestamp}.png"
                cv2.imwrite(step5_filename, vertical_lines)
            
            # REMOVED REDUNDANT ANALYSIS - We already have line_coordinates from grouping
            # The contour analysis was duplicate work and not used in final logic
            
            # FirstRunUpdateFishState: requires exactly 4 lines and no initial calculation done yet
            if total_lines == 4 and not InitialTargetCalculation:
                # First run - process the initial 4 lines
                if not suppress_verbose_logs:
                    print("🎯 Running FirstRunUpdateFishState...")
                    debug_log(f"CALLING FirstRunUpdateFishState with {len(line_coordinates)} coordinates", "FISHRUNS")
                self.FirstRunUpdateFishState(line_coordinates, width)
                if not suppress_verbose_logs:
                    print("✅ FirstRunUpdateFishState completed")
                return  # Exit after first run setup
            
            # SubsequentRunUpdateFishState: requires InitialTargetCalculation done and valid line count (2-6)
            if InitialTargetCalculation and FishingOngoing == True and 2 <= total_lines <= 6:
                if not suppress_verbose_logs:
                    debug_log(f"CALLING SubsequentRunUpdateFishState with {total_lines} lines", "FISHRUNS")
                try:
                    self.SubsequentRunUpdateFishState(total_lines, line_coordinates, width)
                except Exception as e:
                    print(f"❌ ERROR in SubsequentRunUpdateFishState: {e}")
                    debug_log(f"ERROR in SubsequentRunUpdateFishState: {e}", "ERROR")
                    import traceback
                    traceback.print_exc()
                return  # Exit after subsequent run processing

            # Invalid conditions - silent return for performance
            if InitialTargetCalculation and FishingOngoing == False:
                return
            elif not InitialTargetCalculation and total_lines != 4:
                if not suppress_verbose_logs:
                    debug_log(f"SKIPPED: Waiting for initial 4 lines, got {total_lines}", "LINES")
                return
            elif InitialTargetCalculation and not (2 <= total_lines <= 6):
                FishingOngoing = False
                return
            
        except Exception as e:
            print(f"❌ Error in complete fish processing: {e}")
            import traceback
            traceback.print_exc()

    def show_line_indicators(self, line_coordinates, monitor):
        """
        Show visual indicators (arrows) pointing down to detected line positions
        Updates existing indicators instead of recreating them to prevent flickering
        """
        try:
            print(f"🎯 show_line_indicators CALLED: {len(line_coordinates)} coordinates: {line_coordinates}")
            print(f"🎯 Monitor: {monitor}")
            
            # Initialize indicators list if not exists
            if not hasattr(self, 'line_indicator_windows'):
                self.line_indicator_windows = []
                print(f"🎯 Created new line_indicator_windows list")
            
            # Update existing indicators or create new ones
            for i, line_x in enumerate(line_coordinates):
                # Calculate screen position (convert from relative to absolute)
                screen_x = monitor['left'] + line_x
                screen_y = monitor['top'] - 30  # Position arrows above the fish bar area
                
                print(f"🎯 Processing line {i+1}: line_x={line_x}, screen_x={screen_x}, screen_y={screen_y}")
                
                # Update existing indicator or create new one
                if i < len(self.line_indicator_windows) and self.line_indicator_windows[i]:
                    # Update existing indicator position
                    try:
                        indicator = self.line_indicator_windows[i]
                        indicator.geometry(f"20x30+{screen_x-10}+{screen_y}")
                        # Update label text
                        for child in indicator.winfo_children():
                            if isinstance(child, tk.Label):
                                child.config(text=f"L{i + 1}\n↓")
                        print(f"🎯 Updated existing indicator {i+1}")
                    except tk.TclError:
                        # Indicator was destroyed, create new one
                        indicator = self.create_arrow_indicator(screen_x, screen_y, 'line', i)
                        self.line_indicator_windows[i] = indicator
                        print(f"🎯 Recreated destroyed indicator {i+1}")
                else:
                    # Create new indicator
                    indicator = self.create_arrow_indicator(screen_x, screen_y, 'line', i)
                    if i < len(self.line_indicator_windows):
                        self.line_indicator_windows[i] = indicator
                    else:
                        self.line_indicator_windows.append(indicator)
                    print(f"🎯 Created new indicator {i+1}")
            
            # Remove extra indicators if we have fewer lines now
            while len(self.line_indicator_windows) > len(line_coordinates):
                extra_indicator = self.line_indicator_windows.pop()
                if extra_indicator:
                    try:
                        extra_indicator.destroy()
                    except:
                        pass
            
        except Exception as e:
            print(f"❌ Error showing line indicators: {e}")
    
    def create_arrow_indicator(self, x, y, indicator_type, line_index=None):
        """
        Create a single arrow indicator window at specified screen position
        indicator_type: 'line', 'target', or 'bar'
        Returns the window object for later cleanup
        """
        try:
            import tkinter as tk
            
            # Configure indicator based on type
            if indicator_type == 'line':
                color = 'red'
                label_text = f"L{line_index + 1}"
                arrow_text = "↓"
                print_text = f"L{line_index+1}"
            elif indicator_type == 'target':
                color = 'green'
                label_text = "TGT"
                arrow_text = "↓"
                print_text = "TARGET"
            elif indicator_type == 'bar':
                color = 'blue' 
                label_text = "BAR"
                arrow_text = "↓"
                print_text = "BAR"
            else:
                color = 'red'
                label_text = "???"
                arrow_text = "↓"
                print_text = "UNKNOWN"
            
            print(f"🏗️ Creating {print_text} arrow indicator at screen position ({x}, {y})")
            
            # Create a small topmost window
            indicator = tk.Toplevel()
            indicator.overrideredirect(True)  # Remove window decorations
            indicator.attributes('-topmost', True)  # Always on top
            indicator.attributes('-alpha', 0.8)  # Semi-transparent
            indicator.configure(bg=color)
            
            # Position the window
            geometry_str = f"20x30+{x-10}+{y}"
            indicator.geometry(geometry_str)  # 20x30 pixels, centered on line
            print(f"🏗️ {print_text} arrow indicator geometry set to: {geometry_str}")
            
            # Create arrow text (pointing down)
            label = tk.Label(
                indicator, 
                text=f"{label_text}\n{arrow_text}",
                font=('Arial', 8, 'bold'),
                fg='white',
                bg=color,
                justify='center'
            )
            label.pack(expand=True, fill='both')
            
            print(f"✅ {print_text} arrow indicator created successfully")
            return indicator
            
        except Exception as e:
            print(f"❌ Error creating arrow indicator: {e}")
            return None
    
    def clear_line_indicators(self):
        """Clear all line indicator windows and fish state indicators"""
        try:
            # Clear line indicator windows (RED arrows)
            if hasattr(self, 'line_indicator_windows'):
                for window in self.line_indicator_windows:
                    try:
                        if window and window.winfo_exists():
                            window.destroy()
                    except:
                        pass  # Window might already be destroyed
                self.line_indicator_windows = []
            
            # Clear target indicator window (GREEN arrow)
            if hasattr(self, 'target_indicator_window') and self.target_indicator_window:
                try:
                    if self.target_indicator_window.winfo_exists():
                        self.target_indicator_window.destroy()
                except:
                    pass
                self.target_indicator_window = None
            
            # Clear bar indicator window (BLUE arrow)
            if hasattr(self, 'bar_indicator_window') and self.bar_indicator_window:
                try:
                    if self.bar_indicator_window.winfo_exists():
                        self.bar_indicator_window.destroy()
                except:
                    pass
                self.bar_indicator_window = None
            
            # Clear fish state indicators (legacy)
            if hasattr(self, 'fish_state_indicators'):
                for window in self.fish_state_indicators:
                    try:
                        if window and window.winfo_exists():
                            window.destroy()
                    except:
                        pass  # Window might already be destroyed
                self.fish_state_indicators = []
                
        except Exception as e:
            print(f"❌ Error clearing indicators: {e}")
    
    def hide_line_indicators(self):
        """Hide line indicators without destroying them"""
        try:
            if hasattr(self, 'line_indicator_windows'):
                for window in self.line_indicator_windows:
                    try:
                        if window and window.winfo_exists():
                            window.withdraw()  # Hide instead of destroy
                    except:
                        pass
        except Exception as e:
            print(f"❌ Error hiding indicators: {e}")
    
    def show_existing_indicators(self):
        """Show previously hidden indicators"""
        try:
            if hasattr(self, 'line_indicator_windows'):
                for window in self.line_indicator_windows:
                    try:
                        if window and window.winfo_exists():
                            window.deiconify()  # Show hidden window
                    except:
                        pass
        except Exception as e:
            print(f"❌ Error showing indicators: {e}")
    
    def create_line_indicators(self, line_coordinates, monitor):
        """
        Create line indicators once when entering fish state
        Creates 4 red line arrows + 1 green target arrow + 1 blue bar arrow
        Only creates them, doesn't recreate if they already exist
        """
        try:
            global TargetLineMiddle, TargetBarMiddle
            print(f"🏗️ Creating line indicators for {len(line_coordinates)} lines + target + bar")
            
            # Clear any existing indicators first
            self.clear_line_indicators()
            
            # Initialize indicators lists
            self.line_indicator_windows = []
            self.target_indicator_window = None
            self.bar_indicator_window = None
            
            # Create indicators for each detected line (RED arrows)
            for i, line_x in enumerate(line_coordinates):
                # Calculate screen position (convert from relative to absolute)
                screen_x = monitor['left'] + line_x
                screen_y = monitor['top'] - 30  # Position arrows above the fish bar area
                
                # Create new line indicator
                indicator = self.create_arrow_indicator(screen_x, screen_y, 'line', i)
                self.line_indicator_windows.append(indicator)
                print(f"✅ Created indicator L{i+1} at screen position ({screen_x}, {screen_y})")
            
            # Create TARGET middle indicator (GREEN arrow)
            if TargetLineMiddle > 0:
                target_screen_x = monitor['left'] + int(TargetLineMiddle)
                target_screen_y = monitor['top'] - 60  # Position above line arrows
                self.target_indicator_window = self.create_arrow_indicator(target_screen_x, target_screen_y, 'target')
                print(f"✅ Created TARGET indicator at screen position ({target_screen_x}, {target_screen_y})")
            
            # Create BAR middle indicator (BLUE arrow)  
            if TargetBarMiddle > 0:
                bar_screen_x = monitor['left'] + int(TargetBarMiddle)
                bar_screen_y = monitor['top'] + monitor['height'] + 10  # Position below fish bar area
                self.bar_indicator_window = self.create_arrow_indicator(bar_screen_x, bar_screen_y, 'bar')
                print(f"✅ Created BAR indicator at screen position ({bar_screen_x}, {bar_screen_y})")
            
            print(f"✅ Successfully created {len(self.line_indicator_windows)} line indicators + target + bar")
                
        except Exception as e:
            print(f"❌ Error creating line indicators: {e}")
    
    def move_line_indicators(self, line_coordinates, monitor):
        """
        Move existing line indicators to new positions
        Moves line arrows + updates target and bar arrows based on current calculations
        Does not create or destroy, only moves existing ones
        """
        try:
            global TargetLineMiddle, TargetBarMiddle
            
            if not hasattr(self, 'line_indicator_windows') or not self.line_indicator_windows:
                print("⚠️ No existing line indicators to move")
                return
            
            # Move existing LINE indicators to new positions (RED arrows)
            for i, line_x in enumerate(line_coordinates):
                if i < len(self.line_indicator_windows) and self.line_indicator_windows[i]:
                    try:
                        # Calculate new screen position
                        screen_x = monitor['left'] + line_x
                        screen_y = monitor['top'] - 30  # Position arrows above the fish bar area
                        
                        # Move existing indicator
                        indicator = self.line_indicator_windows[i]
                        if indicator and indicator.winfo_exists():
                            indicator.geometry(f"20x30+{screen_x-10}+{screen_y}")
                            # Update label text
                            for child in indicator.winfo_children():
                                if isinstance(child, tk.Label):
                                    child.config(text=f"L{i + 1}\n↓")
                        
                    except tk.TclError:
                        # Indicator was destroyed, skip it
                        print(f"⚠️ Indicator {i+1} no longer exists, skipping")
                        pass
            
            # Move TARGET indicator (GREEN arrow)
            if hasattr(self, 'target_indicator_window') and self.target_indicator_window and TargetLineMiddle > 0:
                try:
                    target_screen_x = monitor['left'] + int(TargetLineMiddle)
                    target_screen_y = monitor['top'] - 60  # Position above line arrows
                    if self.target_indicator_window.winfo_exists():
                        self.target_indicator_window.geometry(f"20x30+{target_screen_x-10}+{target_screen_y}")
                        print(f"🎯 Moved TARGET indicator to ({target_screen_x}, {target_screen_y})")
                except tk.TclError:
                    print(f"⚠️ TARGET indicator no longer exists")
                    pass
            
            # Move BAR indicator (BLUE arrow)
            if hasattr(self, 'bar_indicator_window') and self.bar_indicator_window and TargetBarMiddle > 0:
                try:
                    bar_screen_x = monitor['left'] + int(TargetBarMiddle)
                    bar_screen_y = monitor['top'] + monitor['height'] + 10  # Position below fish bar area
                    if self.bar_indicator_window.winfo_exists():
                        self.bar_indicator_window.geometry(f"20x30+{bar_screen_x-10}+{bar_screen_y}")
                        print(f"🎯 Moved BAR indicator to ({bar_screen_x}, {bar_screen_y})")
                except tk.TclError:
                    print(f"⚠️ BAR indicator no longer exists")
                    pass
                        
        except Exception as e:
            print(f"❌ Error moving line indicators: {e}")

    def update_shake_state(self, save_debug_images=False):
        """
        SINGLE FUNCTION: Complete shake processing pipeline for circle detection
        Takes snapshot of shake area, processes it step-by-step, detects circles, returns coordinates
        Automatically moves cursor to found circle, moves down 1px, and clicks
        Tracks clicked locations to prevent duplicate clicks
        save_debug_images: If True, saves debug images to disk (only for testing)
        
        Returns:
            list of dict: [{'screen_x': int, 'screen_y': int, 'radius': int, 'type': str}, ...]
        """
        # Initialize clicked locations tracking if not exists
        if not hasattr(self, 'clicked_shake_locations'):
            self.clicked_shake_locations = set()
        
        try:
            # Get shake area from settings
            shake_area = ACTIVE_SETTINGS.get('shake_area', '')
            if not shake_area:
                print("❌ No shake_area configured in settings!")
                return []
            
            # Parse area string format: WIDTHxHEIGHT+X+Y
            try:
                parts = shake_area.replace('+', 'x').split('x')
                if len(parts) != 4:
                    print(f"❌ Invalid shake area format: {shake_area}")
                    return []
                
                width, height, x, y = map(int, parts)
                monitor = {
                    "left": x,
                    "top": y,
                    "width": width,
                    "height": height
                }
                
            except Exception as e:
                print(f"❌ Error parsing shake area: {e}")
                return []
            
            # Generate timestamp for debug files (only if saving)
            if save_debug_images:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # STEP: Take screenshot of shake area
            with mss.mss() as sct:
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img_array = np.array(img)
            
            # Save original image (only for testing)
            if save_debug_images:
                img.save(f"shake_step0_original_{timestamp}.png")
            
            # STEP 1: Apply blur to reduce noise
            blurred = cv2.GaussianBlur(img_array, (5, 5), 0)
            blurred_bgr = cv2.cvtColor(blurred, cv2.COLOR_RGB2BGR)
            if save_debug_images:
                cv2.imwrite(f"shake_step1_blur_{timestamp}.png", blurred_bgr)
            
            # STEP 2: Convert to grayscale
            gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
            if save_debug_images:
                cv2.imwrite(f"shake_step2_grayscale_{timestamp}.png", gray)
            
            # STEP 3: Apply edge detection (Canny)
            edges = cv2.Canny(gray, 50, 150)
            if save_debug_images:
                cv2.imwrite(f"shake_step3_edges_{timestamp}.png", edges)
            
            # STEP 4: Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if save_debug_images:
                contour_image = blurred_bgr.copy()
                cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
                cv2.imwrite(f"shake_step4_contours_{timestamp}.png", contour_image)
            
            # STEP 5: Detect BIG circles with DEDUPLICATION to prevent double-clicking
            big_circles = []
            
            # Get minimum radius from settings with safe conversion
            try:
                min_radius = int(ACTIVE_SETTINGS.get('shake_min_radius', '10'))
            except (ValueError, TypeError):
                min_radius = 10
                print(f"⚠️ Warning: Invalid shake_min_radius, using default 10")
            
            # Helper function to check if circle already exists (prevent duplicates)
            def is_duplicate_circle(new_cx, new_cy, new_r, existing_circles, tolerance=15):
                """Check if circle is too close to existing circles (prevent double detection)"""
                for existing in existing_circles:
                    ex_cx, ex_cy, ex_r = existing['center'][0], existing['center'][1], existing['radius']
                    # Calculate distance between centers
                    distance = np.sqrt((new_cx - ex_cx)**2 + (new_cy - ex_cy)**2)
                    # If centers are close and radii are similar, it's likely the same circle
                    if distance < tolerance and abs(new_r - ex_r) < tolerance:
                        return True
                return False
            
            # Method 1: HoughCircles for rings - slightly more perfect circles
            hough_circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=37, param1=75, param2=42, minRadius=min_radius, maxRadius=170)
            if hough_circles is not None:
                hough_circles = np.round(hough_circles[0, :]).astype("int")
                for (cx, cy, r) in hough_circles:
                    # Skip if duplicate
                    if is_duplicate_circle(cx, cy, r, big_circles):
                        continue
                        
                    # Validate circle by checking edge points
                    edge_points_found = 0
                    total_sample_points = 16
                    for i in range(total_sample_points):
                        angle = (2 * np.pi * i) / total_sample_points
                        sample_x = int(cx + r * np.cos(angle))
                        sample_y = int(cy + r * np.sin(angle))
                        if 0 <= sample_x < gray.shape[1] and 0 <= sample_y < gray.shape[0]:
                            if edges[sample_y, sample_x] > 0:
                                edge_points_found += 1
                    
                    if edge_points_found / total_sample_points > 0.38:  # Slightly more perfect circle edges
                        big_circles.append({'center': (cx, cy), 'radius': r, 'method': 'HoughCircles'})
            
            # Method 2: Contour-based perfect circles (with deduplication)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < (min_radius * min_radius):
                    continue
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if not (0.7 < circularity < 1.3):  # Slightly more perfect circularity
                    continue
                
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                cx, cy, radius = int(cx), int(cy), int(radius)
                
                # Skip if duplicate
                if is_duplicate_circle(cx, cy, radius, big_circles):
                    continue
                
                # Check minimum radius requirement
                if radius < min_radius:
                    continue
                
                fitted_circle_area = np.pi * radius * radius
                area_ratio = area / fitted_circle_area
                if not (0.7 < area_ratio < 1.3):  # Slightly more perfect area ratio
                    continue
                
                # Check radius consistency
                center = np.array([cx, cy])
                distances = [np.linalg.norm(point[0] - center) for point in contour]
                if len(distances) < 8:
                    continue
                
                distances = np.array(distances)
                coefficient_of_variation = np.std(distances) / np.mean(distances) if np.mean(distances) > 0 else float('inf')
                if coefficient_of_variation > 0.22:  # Slightly more consistent radius
                    continue
                
                # Convexity check
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                convexity = area / hull_area if hull_area > 0 else 0
                if convexity < 0.78:  # Slightly more perfect convexity
                    continue
                
                big_circles.append({'center': (cx, cy), 'radius': radius, 'method': 'Contour'})
            
            # Save final circles image (only for testing)
            if save_debug_images:
                big_circles_image = blurred_bgr.copy()
                for circle in big_circles:
                    cx, cy, r = circle['center'][0], circle['center'][1], circle['radius']
                    cv2.circle(big_circles_image, (cx, cy), r, (0, 255, 0), 2)
                    cv2.circle(big_circles_image, (cx, cy), 2, (0, 0, 255), 3)
                cv2.imwrite(f"shake_step5_final_circles_{timestamp}.png", big_circles_image)
            
            # Convert to screen coordinates and preserve detection method info
            result = []
            for circle in big_circles:
                screen_x = x + circle['center'][0]
                screen_y = y + circle['center'][1]
                result.append({
                    'screen_x': screen_x,
                    'screen_y': screen_y,
                    'radius': circle['radius'],
                    'type': 'BIG',
                    'method': circle.get('method', 'Unknown')
                })
            
            # Output results with detection method info
            print(f"Shake circles detected: {len(result)} (after deduplication)")
            if result:
                print("Circle positions:")
                for i, circle in enumerate(result, 1):
                    method = circle.get('method', 'Unknown')
                    print(f"  Circle {i}: Screen ({circle['screen_x']}, {circle['screen_y']}) radius={circle['radius']}px [{method}]")
                
                # ADVANCED: Find first circle that hasn't been clicked yet
                clicked_circle = None
                for circle in result:
                    # Check if this circle is too close to any previously clicked circle
                    is_duplicate = False
                    current_pos = (circle['screen_x'], circle['screen_y'])
                    
                    # Check against all previously clicked locations with distance-based detection
                    for clicked_pos in self.clicked_shake_locations:
                        distance = ((current_pos[0] - clicked_pos[0])**2 + (current_pos[1] - clicked_pos[1])**2)**0.5
                        if distance <= 15:  # 15px radius around clicked locations
                            is_duplicate = True
                            print(f"⏭️ SKIP: Circle at {current_pos} too close to clicked {clicked_pos} (distance: {distance:.1f}px)")
                            break
                    
                    if not is_duplicate:
                        clicked_circle = circle
                        self.clicked_shake_locations.add(current_pos)
                        print(f"🎯 FAST CLICK: {current_pos} (radius: {circle['radius']}px)")
                        break
                
                if clicked_circle:
                    # MAXIMUM SPEED MODE - No cooldown, just prevent same spot clicking
                    cursor_x = clicked_circle['screen_x']
                    cursor_y = clicked_circle['screen_y']
                    
                    # Move cursor down by 1 pixel
                    cursor_y += 1
                    
                    # Anti-Roblox teleport and click method - MUST NOT FAIL
                    if YOUTUBE_AUTO_SUBSCRIBE_AVAILABLE:
                        import ctypes
                        from ctypes import windll, c_int, c_uint, c_ulong, POINTER
                        import time
                        
                        # Ensure coordinates are integers
                        cursor_x = int(cursor_x)
                        cursor_y = int(cursor_y)
                        
                        print(f"🎯 Anti-Roblox teleport to ({cursor_x}, {cursor_y})")
                        
                        # STEP 1: Teleport mouse directly to the circle position
                        windll.user32.SetCursorPos(c_int(cursor_x), c_int(cursor_y))
                        
                        # STEP 2: Use anti-Roblox relative movement to move 1 pixel down
                        # Define constants
                        MOUSEEVENTF_MOVE = 0x0001
                        
                        # Ensure all parameters are proper ctypes
                        windll.user32.mouse_event(
                            c_uint(MOUSEEVENTF_MOVE),  # dwFlags
                            c_int(0),                   # dx (relative)
                            c_int(1),                   # dy (relative) - 1 pixel down
                            c_ulong(0),                 # dwData
                            POINTER(c_ulong)()          # dwExtraInfo (null pointer)
                        )
                        # REMOVED: Movement settling time for maximum speed
                        
                        # STEP 3: ULTRA-FAST Hardware-level click
                        MOUSEEVENTF_LEFTDOWN = 0x0002
                        MOUSEEVENTF_LEFTUP = 0x0004
                        
                        # Send mouse down event
                        windll.user32.mouse_event(
                            c_uint(MOUSEEVENTF_LEFTDOWN),
                            c_int(0),
                            c_int(0),
                            c_ulong(0),
                            POINTER(c_ulong)()
                        )
                        # ULTRA-FAST: Minimal hold time for maximum speed
                        time.sleep(0.001)  # 1ms hold time (minimum for recognition)
                        
                        # Send mouse up event
                        windll.user32.mouse_event(
                            c_uint(MOUSEEVENTF_LEFTUP),
                            c_int(0),
                            c_int(0),
                            c_ulong(0),
                            POINTER(c_ulong)()
                        )
                        
                        print(f"🎯 Anti-Roblox click complete at ({cursor_x}, {cursor_y + 1})")
                    else:
                        print(f"🎯 Would anti-Roblox click on circle at ({cursor_x}, {cursor_y}) - libraries not available")
                else:
                    print("🔄 All detected circles have been clicked before - no action taken")
            else:
                print("🔍 No circles found - no action taken")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in shake processing: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _test_fish_processing(self):
        """Test button - calls the complete fish processing function with debug image saving"""
        self.update_fish_state(save_debug_images=True)
    
    def reset_shake_clicked_locations(self):
        """Reset the clicked shake locations tracking - call when starting new shake minigame"""
        if hasattr(self, 'clicked_shake_locations'):
            self.clicked_shake_locations.clear()
            print("🔄 Shake clicked locations reset")
        else:
            self.clicked_shake_locations = set()
            print("🔄 Shake clicked locations initialized")
    
    def _test_shake_processing(self):
        """Test button - calls the complete shake processing function with debug image saving"""
        self.update_shake_state(save_debug_images=True)
    
    def _update_status(self, text, color="black"):
        """Update the status label in the GUI"""
        try:
            # Find the status label (it should be in the bottom frame)
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, tk.Label) and "Status:" in grandchild.cget("text"):
                                    grandchild.config(text=f"Status: {text}", fg=color)
                                    return
        except:
            pass  # Silently fail if status update fails
    
    def _update_active_setting(self, key, var):
        """Update ACTIVE_SETTINGS when a variable changes"""
        try:
            value = var.get()
            # Handle empty values for numeric types
            if isinstance(var, tk.DoubleVar) and value == "":
                value = 0.0
            elif isinstance(var, tk.IntVar) and value == "":
                value = 0
            ACTIVE_SETTINGS[key] = value
        except (tk.TclError, ValueError) as e:
            # Handle empty or invalid values gracefully
            if isinstance(var, tk.DoubleVar):
                ACTIVE_SETTINGS[key] = 0.0
            elif isinstance(var, tk.IntVar):
                ACTIVE_SETTINGS[key] = 0
            else:
                ACTIVE_SETTINGS[key] = ""
            print(f"⚠️ Warning: Invalid value for {key}, using default: {ACTIVE_SETTINGS[key]}")
    
    def _update_scan_fps(self):
        """Update scan FPS setting and convert to integer"""
        try:
            value = self.scan_fps.get()
            if value == "":
                value = "60"  # Default value
            ACTIVE_SETTINGS['scan_fps'] = int(value)
        except (ValueError, tk.TclError):
            ACTIVE_SETTINGS['scan_fps'] = 60  # Default fallback
            print("⚠️ Warning: Invalid scan_fps value, using default: 60")
    
    def _update_scan_shake_fps(self):
        """Update scan shake FPS setting and convert to integer"""
        try:
            value = self.scan_shake_fps.get()
            if value == "":
                value = "10"  # Default value
            ACTIVE_SETTINGS['scan_shake_fps'] = int(value)
        except (ValueError, tk.TclError):
            ACTIVE_SETTINGS['scan_shake_fps'] = 10  # Default fallback
            print("⚠️ Warning: Invalid scan_shake_fps value, using default: 10")
    
    def _update_always_on_top(self):  # [AI_REF:always_on_top_handler]
        """Update always on top setting and apply it to the window"""
        self._update_active_setting('always_on_top', self.always_on_top)
        # Apply the setting immediately to the current window
        self.wm_attributes('-topmost', self.always_on_top.get())
    
    def _handle_casting_branch_exclusivity(self, branch, setting_key, var):
        """Handle mutual exclusivity between casting flow branches"""
        # First update the setting normally
        self._update_active_setting(setting_key, var)
        
        # If this checkbox was just enabled, check if we need to switch branches
        if var.get():  # If the checkbox was just enabled
            # Check which branch was active BEFORE this change (excluding the current checkbox)
            if branch == 'branch1':
                # Check if branch 2 was active before this change
                branch2_was_active = (self.casting_delay3_enabled.get() or 
                                    self.casting_hold_enabled.get() or 
                                    self.casting_delay4_enabled.get() or 
                                    self.casting_release_enabled.get() or 
                                    self.casting_delay5_enabled.get())
                
                # Check if any other branch 1 checkboxes were already enabled
                other_branch1_active = False
                if setting_key != 'casting_delay1_enabled' and self.casting_delay1_enabled.get():
                    other_branch1_active = True
                if setting_key != 'casting_perfect_cast_enabled' and self.casting_perfect_cast_enabled.get():
                    other_branch1_active = True
                if setting_key != 'casting_delay2_enabled' and self.casting_delay2_enabled.get():
                    other_branch1_active = True
                
                # If switching from branch 2 to branch 1 (branch 2 was active, branch 1 wasn't)
                if branch2_was_active and not other_branch1_active:
                    # Enable all Branch 1 checkboxes
                    self.casting_delay1_enabled.set(True)
                    self.casting_perfect_cast_enabled.set(True)
                    self.casting_delay2_enabled.set(True)
                    
                    # Disable all Branch 2 checkboxes
                    self.casting_delay3_enabled.set(False)
                    self.casting_hold_enabled.set(False)
                    self.casting_delay4_enabled.set(False)
                    self.casting_release_enabled.set(False)
                    self.casting_delay5_enabled.set(False)
                elif branch2_was_active:
                    # Just switching branches, disable branch 2
                    self.casting_delay3_enabled.set(False)
                    self.casting_hold_enabled.set(False)
                    self.casting_delay4_enabled.set(False)
                    self.casting_release_enabled.set(False)
                    self.casting_delay5_enabled.set(False)
                    
            elif branch == 'branch2':
                # Check if branch 1 was active before this change
                branch1_was_active = (self.casting_delay1_enabled.get() or 
                                    self.casting_perfect_cast_enabled.get() or 
                                    self.casting_delay2_enabled.get())
                
                # Check if any other branch 2 checkboxes were already enabled
                other_branch2_active = False
                if setting_key != 'casting_delay3_enabled' and self.casting_delay3_enabled.get():
                    other_branch2_active = True
                if setting_key != 'casting_hold_enabled' and self.casting_hold_enabled.get():
                    other_branch2_active = True
                if setting_key != 'casting_delay4_enabled' and self.casting_delay4_enabled.get():
                    other_branch2_active = True
                if setting_key != 'casting_release_enabled' and self.casting_release_enabled.get():
                    other_branch2_active = True
                if setting_key != 'casting_delay5_enabled' and self.casting_delay5_enabled.get():
                    other_branch2_active = True
                
                # If switching from branch 1 to branch 2 (branch 1 was active, branch 2 wasn't)
                if branch1_was_active and not other_branch2_active:
                    # Enable all Branch 2 checkboxes
                    self.casting_delay3_enabled.set(True)
                    self.casting_hold_enabled.set(True)
                    self.casting_delay4_enabled.set(True)
                    self.casting_release_enabled.set(True)
                    self.casting_delay5_enabled.set(True)
                    
                    # Disable all Branch 1 checkboxes
                    self.casting_delay1_enabled.set(False)
                    self.casting_perfect_cast_enabled.set(False)
                    self.casting_delay2_enabled.set(False)
                elif branch1_was_active:
                    # Just switching branches, disable branch 1
                    self.casting_delay1_enabled.set(False)
                    self.casting_perfect_cast_enabled.set(False)
                    self.casting_delay2_enabled.set(False)
    
    def _reset_all_settings(self):
        """Reset all settings to default values from FIRST_LAUNCH_CONFIG"""
        try:
            print("Resetting all settings to defaults...")
            
            # Update ACTIVE_SETTINGS with default values
            global ACTIVE_SETTINGS
            ACTIVE_SETTINGS = FIRST_LAUNCH_CONFIG.copy()
            
            # Update GUI elements to reflect the reset values
            self.hotkey_start.set(ACTIVE_SETTINGS['hotkey_start'])
            self.hotkey_stop.set(ACTIVE_SETTINGS['hotkey_stop'])
            self.hotkey_change_area.set(ACTIVE_SETTINGS['hotkey_change_area'])
            self.hotkey_exit.set(ACTIVE_SETTINGS['hotkey_exit'])
            self.always_on_top.set(ACTIVE_SETTINGS['always_on_top'])
            self.scan_fps.set(str(ACTIVE_SETTINGS['scan_fps']))
            self.scan_shake_fps.set(str(ACTIVE_SETTINGS['scan_shake_fps']))
            self.shake_timer.set(ACTIVE_SETTINGS['shake_timer'])
            self.no_circle_timeout.set(ACTIVE_SETTINGS['no_circle_timeout'])
            self.shake_min_radius.set(ACTIVE_SETTINGS['shake_min_radius'])
            self.fish_lost_timeout.set(ACTIVE_SETTINGS['fish_lost_timeout'])
            self.from_side_bar_ratio.set(ACTIVE_SETTINGS['from_side_bar_ratio'])
            
            # Apply always on top setting immediately
            self.wm_attributes('-topmost', ACTIVE_SETTINGS['always_on_top'])
            
            # Update hotkey bindings
            self._update_start_hotkey()
            self._update_stop_hotkey()
            self._update_exit_hotkey()
            self._update_change_area_hotkey()
            
            print("All settings have been reset to defaults")
            
        except Exception as e:
            print(f"Error resetting settings: {e}")
    
    def _on_close(self):
        """Handle window close - save config before exiting"""
        # Ensure GUI is visible during close process
        self.deiconify()
        
        # Stop bot if running
        if hasattr(self, 'bot_running') and self.bot_running:
            self._stop_bot()
            # Give bot thread time to stop
            if self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=2)
        
        # Hide area overlays if they're visible (this saves their positions)
        if hasattr(self, 'area_overlays_visible') and self.area_overlays_visible:
            self._hide_area_overlays()
        
        # Save ACTIVE_SETTINGS to Config.txt
        save_config()
        
        # Unhook all keyboard hotkeys
        try:
            keyboard.unhook_all()
        except:
            pass
        
        self.destroy()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    # Update FIRST_LAUNCH_CONFIG based on current screen resolution
    update_first_launch_config()
    
    try:
        app = Application()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user (Ctrl+C)")
        print("Exiting gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Application closed.")
