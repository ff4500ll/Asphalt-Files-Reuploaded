import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import keyboard
import sys
import os
import threading
import numpy as np
from ultralytics import YOLO
import time
import mss
from PIL import Image, ImageTk, ImageDraw
import pydirectinput
import ctypes
import win32api
import win32con
from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse
import json
import webbrowser

# Set DPI awareness for Windows to handle scaling correctly
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
    except:
        pass


class GPOSantaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPO Santa")
        self.root.minsize(220, 100)
        self.root.protocol("WM_DELETE_WINDOW", self.force_exit)
        
        # Load settings first before anything else
        self.settings = self._load_settings()
        
        # State variables
        self.is_running = False
        self.hotkeys = self.settings.get('hotkeys', {
            'start_stop': 'F1',
            'exit': 'F2',
            'record': 'F3'
        })
        self.rebinding = None  # Track which hotkey is being rebound
        self.selected_model = self.settings.get('selected_model', None)
        self.pt_files = []
        self.always_on_top = tk.BooleanVar(value=self.settings.get('always_on_top', True))
        self.auto_minimize = tk.BooleanVar(value=self.settings.get('auto_minimize', False))
        self.show_visualization = tk.BooleanVar(value=self.settings.get('show_visualization', False))
        self.first_person_mode = tk.BooleanVar(value=self.settings.get('first_person_mode', False))
        self.use_gpu = tk.BooleanVar(value=self.settings.get('use_gpu', True))
        self.icon_confidence = tk.DoubleVar(value=self.settings.get('icon_confidence', 0.5))
        self.santa_confidence = tk.DoubleVar(value=self.settings.get('santa_confidence', 0.5))
        self.is_recording = False
        self.end_delay = tk.DoubleVar(value=self.settings.get('end_delay', 99.9))
        self.main_tool = tk.StringVar(value=self.settings.get('main_tool', '1'))
        self.anything_else = tk.StringVar(value=self.settings.get('anything_else', '2'))
        self.recorded_actions = self.settings.get('recorded_actions', [])
        self.recording_start_time = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self.showing_record_dialog = False  # Prevent multiple dialogs
        self.main_loop_thread = None
        self.playback_thread = None
        self.model = None
        self.overlay_window = None
        self.latest_detections = []  # Store latest detections for visualization
        self.latest_frame = None  # Store latest frame for visualization
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Icon tracking state
        self.icon_state = "searching_left"  # States: "searching_left", "searching_right", "tracking"
        self.icon_last_side = "left"  # "left" or "right" - which side icon was last seen
        self.is_holding_arrow = False
        self.last_arrow_burst_time = 0  # Track when last burst was sent
        
        # Santa tracking state
        self.santa_prev_center = None  # Previous Santa center position (x, y)
        
        # Threading lock for arrow key control
        self.arrow_lock = threading.Lock()
        
        # Track currently pressed keys for cleanup on stop
        self.pressed_keys = set()
        self.keys_lock = threading.Lock()
        
        # First person mode adaptive sensitivity
        self.fp_sensitivity = 1.0  # Adaptive sensitivity multiplier
        self.fp_last_error = 0  # Track last error for adaptive adjustment
        self.both_detected = False  # Track if both icon and santa detected for playback
        
        # Scan for .pt files
        self._scan_pt_files()
        
        # Setup GUI
        self._create_gui()
        
        # Setup hotkeys
        self._setup_hotkeys()
        
        # Apply always on top setting
        self._toggle_always_on_top()
        
        # Create visualization window if checkbox is checked
        if self.show_visualization.get():
            self._create_overlay()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def _get_current_monitor(self):
        """Get the monitor number where the window is located"""
        try:
            # Get window position
            window_x = self.root.winfo_x()
            window_y = self.root.winfo_y()
            
            # Get all monitors
            with mss.mss() as sct:
                for i, monitor in enumerate(sct.monitors[1:], 1):  # Skip monitors[0] (all monitors)
                    if (monitor['left'] <= window_x < monitor['left'] + monitor['width'] and
                        monitor['top'] <= window_y < monitor['top'] + monitor['height']):
                        return i
            
            # Default to monitor 1 if not found
            return 1
        except:
            return 1
    
    def _get_settings_path(self):
        """Get the path to the settings file"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(app_dir, "GPOSantaSettings.json")
    
    def _load_settings(self):
        """Load settings from JSON file"""
        settings_path = self._get_settings_path()
        default_settings = {
            'selected_model': None,
            'always_on_top': True,
            'auto_minimize': True,
            'show_visualization': False,
            'first_person_mode': False,
            'use_gpu': True,
            'icon_confidence': 0.5,
            'santa_confidence': 0.5,
            'end_delay': 99.9,
            'main_tool': '1',
            'anything_else': '2',
            'hotkeys': {
                'start_stop': 'F1',
                'exit': 'F2',
                'record': 'F3'
            },
            'recorded_actions': []
        }
        
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded_settings)
                    print(f"Settings loaded from {settings_path}")
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """Save settings to JSON file"""
        settings_path = self._get_settings_path()
        try:
            settings_to_save = {
                'selected_model': self.selected_model,
                'always_on_top': self.always_on_top.get(),
                'auto_minimize': self.auto_minimize.get(),
                'show_visualization': self.show_visualization.get(),
                'first_person_mode': self.first_person_mode.get(),
                'use_gpu': self.use_gpu.get(),
                'icon_confidence': self.icon_confidence.get(),
                'santa_confidence': self.santa_confidence.get(),
                'end_delay': self.end_delay.get(),
                'main_tool': self.main_tool.get(),
                'anything_else': self.anything_else.get(),
                'hotkeys': self.hotkeys.copy(),
                'recorded_actions': self.recorded_actions
            }
            
            with open(settings_path, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            print(f"Settings saved to {settings_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _scan_pt_files(self):
        """Scan current directory for .pt files"""
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                current_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                current_dir = os.path.dirname(os.path.abspath(__file__))
            self.pt_files = [f for f in os.listdir(current_dir) if f.endswith('.pt')]
            self.pt_files.sort()
        except Exception as e:
            print(f"Error scanning for .pt files: {e}")
            self.pt_files = []
    
    def _create_gui(self):
        """Create the GUI elements"""
        # Main frame with minimal padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack()
        
        # Model selection frame
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=0, column=0, pady=(0, 8), sticky='ew')
        
        ttk.Label(model_frame, text="Model:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Dropdown for .pt files
        self.model_dropdown = ttk.Combobox(model_frame, width=15, state='readonly')
        if self.pt_files:
            self.model_dropdown['values'] = self.pt_files
            self.model_dropdown.current(0)
            self.selected_model = self.pt_files[0]
        else:
            self.model_dropdown['values'] = ["no .pt files found"]
            self.model_dropdown.current(0)
        self.model_dropdown.bind('<<ComboboxSelected>>', self._on_model_selected)
        self.model_dropdown.bind('<Button-1>', self._refresh_pt_files)
        self.model_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        
        # Manual selection button
        browse_button = ttk.Button(model_frame, text="Browse", 
                                   command=self._browse_model, width=7)
        browse_button.pack(side=tk.LEFT)
        
        # Start/Stop button row
        start_frame = ttk.Frame(main_frame)
        start_frame.grid(row=1, column=0, pady=3)
        
        self.start_button = ttk.Button(start_frame, text="Start (F1)", 
                                        command=self.toggle_start_stop, width=12)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.rebind_start_button = ttk.Button(start_frame, text="Rebind", 
                                               command=lambda: self.start_rebinding('start_stop'),
                                               width=7)
        self.rebind_start_button.pack(side=tk.LEFT)
        
        # Exit button row
        exit_frame = ttk.Frame(main_frame)
        exit_frame.grid(row=2, column=0, pady=3)
        
        self.exit_button = ttk.Button(exit_frame, text="Exit (F2)", 
                                       command=self.force_exit, width=12)
        self.exit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.rebind_exit_button = ttk.Button(exit_frame, text="Rebind", 
                                              command=lambda: self.start_rebinding('exit'),
                                              width=7)
        self.rebind_exit_button.pack(side=tk.LEFT)
        
        # Hotkey Settings frame
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=3, column=0, pady=(8, 0))
        
        ttk.Label(hotkey_frame, text="Hotkeys:", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 3))
        
        # Main Tool hotkey
        ttk.Label(hotkey_frame, text="Main Tool:", font=('Arial', 8)).grid(row=1, column=0, padx=(0, 5), sticky=tk.W)
        self.main_tool_dropdown = ttk.Combobox(hotkey_frame, textvariable=self.main_tool, 
                                               state="readonly", width=5,
                                               values=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        self.main_tool_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        self.main_tool_dropdown.bind('<<ComboboxSelected>>', lambda e: self._save_settings())
        
        # ANYTHING ELSE hotkey
        ttk.Label(hotkey_frame, text="ANYTHING ELSE:", font=('Arial', 8)).grid(row=2, column=0, padx=(0, 5), sticky=tk.W)
        self.anything_else_dropdown = ttk.Combobox(hotkey_frame, textvariable=self.anything_else, 
                                                    state="readonly", width=5,
                                                    values=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        self.anything_else_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        self.anything_else_dropdown.bind('<<ComboboxSelected>>', lambda e: self._save_settings())
        ttk.Label(hotkey_frame, text="⚠ Must be set to something in-game", 
                  foreground="red", font=('Arial', 7)).grid(row=2, column=2, padx=5, sticky=tk.W)
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=4, column=0, pady=(8, 0))
        
        self.always_on_top_check = ttk.Checkbutton(options_frame, text="Always On Top",
                                                    variable=self.always_on_top,
                                                    command=self._toggle_always_on_top)
        self.always_on_top_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_minimize_check = ttk.Checkbutton(options_frame, text="Auto Minimize",
                                                    variable=self.auto_minimize,
                                                    command=self._save_settings)
        self.auto_minimize_check.pack(side=tk.LEFT)
        
        self.show_viz_check = ttk.Checkbutton(options_frame, text="Show Visualization",
                                              variable=self.show_visualization,
                                              command=self._toggle_visualization)
        self.show_viz_check.pack(side=tk.LEFT, padx=(10, 0))
        
        self.first_person_check = ttk.Checkbutton(options_frame, text="First Person Mode",
                                                  variable=self.first_person_mode,
                                                  command=self._save_settings)
        self.first_person_check.pack(side=tk.LEFT, padx=(10, 0))
        
        self.use_gpu_check = ttk.Checkbutton(options_frame, text="Use GPU",
                                             variable=self.use_gpu,
                                             command=self._save_settings)
        self.use_gpu_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # Confidence thresholds frame
        confidence_frame = ttk.Frame(main_frame)
        confidence_frame.grid(row=5, column=0, pady=(8, 0))
        
        # Icon confidence
        ttk.Label(confidence_frame, text="Icon Conf:", font=('Arial', 8)).pack(side=tk.LEFT, padx=(0, 3))
        self.icon_conf_spinbox = ttk.Spinbox(confidence_frame, from_=0.0, to=1.0, increment=0.05,
                                              textvariable=self.icon_confidence, width=6,
                                              command=self._save_settings)
        self.icon_conf_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        self.icon_confidence.trace_add('write', lambda *args: self._save_settings())
        
        # Santa confidence
        ttk.Label(confidence_frame, text="Santa Conf:", font=('Arial', 8)).pack(side=tk.LEFT, padx=(0, 3))
        self.santa_conf_spinbox = ttk.Spinbox(confidence_frame, from_=0.0, to=1.0, increment=0.05,
                                               textvariable=self.santa_confidence, width=6,
                                               command=self._save_settings)
        self.santa_conf_spinbox.pack(side=tk.LEFT)
        self.santa_confidence.trace_add('write', lambda *args: self._save_settings())
        
        # Actions frame
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=6, column=0, pady=(8, 0))
        
        ttk.Label(actions_frame, text="Actions:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Record button
        self.record_button = ttk.Button(actions_frame, text="Record (F3)", 
                                        command=self._toggle_record, width=12)
        self.record_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.rebind_record_button = ttk.Button(actions_frame, text="Rebind", 
                                               command=lambda: self.start_rebinding('record'),
                                               width=7)
        self.rebind_record_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # End delay with warning
        delay_container = ttk.Frame(actions_frame)
        delay_container.pack(side=tk.LEFT)
        
        delay_input_frame = ttk.Frame(delay_container)
        delay_input_frame.pack()
        ttk.Label(delay_input_frame, text="End Delay (s):", font=('Arial', 8)).pack(side=tk.LEFT, padx=(0, 3))
        self.end_delay_spinbox = ttk.Spinbox(delay_input_frame, from_=0.0, to=999.9, increment=0.1,
                                              textvariable=self.end_delay, width=6,
                                              command=self._save_settings)
        self.end_delay_spinbox.pack(side=tk.LEFT)
        self.end_delay.trace_add('write', lambda *args: self._save_settings())
        
        # Warning label
        warning_label = ttk.Label(delay_container, text="⚠️ SET TO SKILL COOLDOWN ⚠️", 
                                 font=('Arial', 7, 'bold'), foreground='red')
        warning_label.pack()
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Stopped", 
                                      font=('Arial', 9))
        self.status_label.grid(row=7, column=0, pady=(8, 0))
        
        # Rebind instruction label (hidden by default)
        self.rebind_label = ttk.Label(main_frame, text="", 
                                      font=('Arial', 8),
                                      foreground='blue')
        self.rebind_label.grid(row=8, column=0, pady=(3, 0))
    
    def _setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        try:
            keyboard.unhook_all()
            keyboard.on_press_key(self.hotkeys['start_stop'], 
                                 lambda _: self.root.after(0, self.toggle_start_stop))
            keyboard.on_press_key(self.hotkeys['exit'], 
                                 lambda _: self.root.after(0, self.force_exit))
            keyboard.on_press_key(self.hotkeys['record'], 
                                 lambda _: self.root.after(0, self._toggle_record_with_confirmation))
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def _toggle_always_on_top(self):
        """Toggle always on top setting"""
        self.root.attributes('-topmost', self.always_on_top.get())
        self._save_settings()
    
    def _toggle_visualization(self):
        """Toggle visualization window visibility"""
        if self.show_visualization.get():
            self._create_overlay()
        else:
            self._destroy_overlay()
        self._save_settings()
    
    def _toggle_record(self):
        """Toggle recording state"""
        self.is_recording = not self.is_recording
        
        if self.is_recording:
            self.record_button.config(text=f"Stop ({self.hotkeys['record']})")
            self._start_recording()
            print(">>> RECORDING STARTED")
        else:
            self.record_button.config(text=f"Record ({self.hotkeys['record']})")
            self._stop_recording()
            print(">>> RECORDING STOPPED")
    
    def _toggle_record_with_confirmation(self):
        """Toggle recording with confirmation dialog"""
        if not self.is_recording:
            # Prevent multiple dialogs
            if self.showing_record_dialog:
                return
            
            self.showing_record_dialog = True
            # Ask for confirmation before starting
            response = messagebox.askyesno("Start Recording", 
                                          "Start recording keyboard and mouse inputs?\n\nPress F3 again to stop.")
            self.showing_record_dialog = False
            
            if response:
                self._toggle_record()
                # Focus on Roblox after confirming
                self.root.after(100, self._focus_roblox)  # Small delay to ensure recording starts first
        else:
            # Stop recording without confirmation
            self._toggle_record()
    
    def _start_recording(self):
        """Start recording keyboard and mouse inputs"""
        self.recorded_actions = []
        self.recording_start_time = time.time()
        self.keys_held = set()  # Track which keys are currently held down
        
        # Start keyboard listener
        def on_press(key):
            if self.is_recording:
                elapsed = time.time() - self.recording_start_time
                try:
                    key_char = key.char
                except AttributeError:
                    key_char = str(key)
                
                # Don't record the record hotkey itself
                record_key = self.hotkeys.get('record', 'F3').lower()
                key_lower = key_char.lower() if isinstance(key_char, str) else str(key).lower()
                
                # Check if this is the record hotkey (handle both 'f3' and 'Key.f3' formats)
                if record_key in key_lower or key_lower.endswith(record_key):
                    return  # Skip recording this key
                
                # Only record if this is the first press (ignore auto-repeat)
                if key_char not in self.keys_held:
                    self.keys_held.add(key_char)
                    self.recorded_actions.append((elapsed, 'key_press', key_char))
                    print(f"Recorded: key_press {key_char} at {elapsed:.3f}s")
        
        def on_release(key):
            if self.is_recording:
                elapsed = time.time() - self.recording_start_time
                try:
                    key_char = key.char
                except AttributeError:
                    key_char = str(key)
                
                # Remove from held keys set
                self.keys_held.discard(key_char)
                self.recorded_actions.append((elapsed, 'key_release', key_char))
                print(f"Recorded: key_release {key_char} at {elapsed:.3f}s")
        
        # Start mouse listener
        def on_click(x, y, button, pressed):
            if self.is_recording:
                elapsed = time.time() - self.recording_start_time
                action = 'mouse_press' if pressed else 'mouse_release'
                button_name = str(button).replace('Button.', '')
                self.recorded_actions.append((elapsed, action, button_name))
                print(f"Recorded: {action} {button_name} at {elapsed:.3f}s")
        
        self.keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        self.mouse_listener = pynput_mouse.Listener(on_click=on_click)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
    
    def _stop_recording(self):
        """Stop recording and save actions"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # Add final delay marker to capture time after last action
        if self.recording_start_time and self.recorded_actions:
            stop_time = time.time() - self.recording_start_time
            # Add a marker for the end of recording (won't be executed, just for delay calculation)
            self.recorded_actions.append((stop_time, 'end_marker', None))
            print(f"Final delay: {stop_time - self.recorded_actions[-2][0]:.3f}s")
        
        print(f">>> Recording stopped. Total actions: {len(self.recorded_actions)}")
        self._save_settings()
    
    def _focus_roblox(self):
        """Focus on Roblox window"""
        try:
            # Try using pygetwindow first
            import pygetwindow as gw
            roblox_windows = gw.getWindowsWithTitle('Roblox')
            if roblox_windows:
                roblox_window = roblox_windows[0]
                roblox_window.activate()
                print("✓ Roblox window focused")
                return
        except ImportError:
            pass
        except Exception as e:
            print(f"pygetwindow focus failed: {e}")
        
        # Fallback: use ctypes to focus window by title
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Roblox")
            if hwnd:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                print("✓ Roblox window focused (ctypes)")
            else:
                print("⚠️ Roblox window not found")
        except Exception as e:
            print(f"⚠️ Could not focus Roblox window: {e}")
    
    def _zoom_in_first_person(self):
        """Zoom in by scrolling up 20 times for first person mode"""
        try:
            print("🔍 Zooming in for first person mode...")
            for i in range(20):
                # Scroll up using mouse_event
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, 120, 0)  # MOUSEEVENTF_WHEEL, WHEEL_DELTA=120
                time.sleep(0.05)  # Small delay between scrolls
            print("✓ Zoom complete")
        except Exception as e:
            print(f"⚠️ Error zooming in: {e}")
    
    def _playback_loop(self):
        """Play back recorded actions in a loop with end delay"""
        try:
            # Give a brief moment for everything to initialize on first start
            time.sleep(0.5)
            
            # Initial setup sequence (runs only once)
            print("[PLAYBACK] Running initial setup...")
            anything_else_key = self.anything_else.get()
            main_tool_key = self.main_tool.get()
            
            # Press ANYTHING ELSE
            pydirectinput.press(anything_else_key)
            print(f"[PLAYBACK] Initial: Pressed {anything_else_key}")
            time.sleep(0.5)
            
            # Press ANYTHING ELSE again
            pydirectinput.press(anything_else_key)
            print(f"[PLAYBACK] Initial: Pressed {anything_else_key}")
            time.sleep(0.5)
            
            # Press MAIN TOOL
            pydirectinput.press(main_tool_key)
            print(f"[PLAYBACK] Initial: Pressed {main_tool_key}")
            time.sleep(0.5)
            
            print("[PLAYBACK] Initial setup complete, starting main sequence loop")
            
            while self.is_running:
                if not self.recorded_actions:
                    print("No recorded actions to play back")
                    break
                
                # Wait for both icon AND santa to be detected before starting sequence
                while self.is_running and not self.both_detected:
                    print("[PLAYBACK] Waiting for both Icon AND Santa to be detected...")
                    time.sleep(0.5)
                
                if not self.is_running:
                    break
                
                print(f"[PLAYBACK] Both detected! Starting sequence ({len(self.recorded_actions)} actions)")
                sequence_start = time.time()
                
                # Get the first action timestamp to normalize delays (remove initial delay)
                first_timestamp = self.recorded_actions[0][0] if self.recorded_actions else 0
                last_action_time = first_timestamp
                
                for timestamp, action_type, action_data in self.recorded_actions:
                    if not self.is_running:
                        break
                    
                    # Wait for the delay between actions (relative to first action)
                    delay = timestamp - last_action_time
                    if delay > 0:
                        time.sleep(delay)
                    last_action_time = timestamp
                    
                    # Execute the action
                    try:
                        if action_type == 'end_marker':
                            # Don't execute anything, just marks the end for delay calculation
                            print(f"[PLAYBACK] Final delay processed")
                        elif action_type == 'key_press':
                            # Use pydirectinput for key press (hold down)
                            if action_data.startswith('Key.'):
                                key_name = action_data.replace('Key.', '')
                            else:
                                key_name = action_data
                            
                            # Track pressed key
                            with self.keys_lock:
                                self.pressed_keys.add(key_name.lower())
                            
                            # Use lock for arrow keys
                            if key_name.lower() in ['left', 'right']:
                                with self.arrow_lock:
                                    pydirectinput.keyDown(key_name)
                            else:
                                pydirectinput.keyDown(key_name)
                        elif action_type == 'key_release':
                            # Use pydirectinput for key release
                            if action_data.startswith('Key.'):
                                key_name = action_data.replace('Key.', '')
                            else:
                                key_name = action_data
                            
                            # Remove from tracked keys
                            with self.keys_lock:
                                self.pressed_keys.discard(key_name.lower())
                            
                            # Use lock for arrow keys
                            if key_name.lower() in ['left', 'right']:
                                with self.arrow_lock:
                                    pydirectinput.keyUp(key_name)
                            else:
                                pydirectinput.keyUp(key_name)
                        elif action_type == 'mouse_press':
                            if action_data == 'left':
                                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                            elif action_data == 'right':
                                ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
                            elif action_data == 'middle':
                                ctypes.windll.user32.mouse_event(0x0020, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEDOWN
                        elif action_type == 'mouse_release':
                            if action_data == 'left':
                                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
                            elif action_data == 'right':
                                ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
                            elif action_data == 'middle':
                                ctypes.windll.user32.mouse_event(0x0040, 0, 0, 0, 0)  # MOUSEEVENTF_MIDDLEUP
                    except Exception as e:
                        print(f"[PLAYBACK] Error executing {action_type} {action_data}: {e}")
                
                sequence_duration = time.time() - sequence_start
                print(f"[PLAYBACK] Sequence complete ({sequence_duration:.2f}s)")
                
                # Post-sequence actions
                if not self.is_running:
                    break
                
                # Press "anything else" hotkey
                anything_else_key = self.anything_else.get()
                print(f"[PLAYBACK] Pressing anything else key: {anything_else_key}")
                pydirectinput.press(anything_else_key)
                
                # Wait 500ms
                if not self.is_running:
                    break
                time.sleep(0.5)
                
                # Press "anything else" hotkey again
                print(f"[PLAYBACK] Pressing anything else key: {anything_else_key}")
                pydirectinput.press(anything_else_key)
                
                # Wait 500ms
                if not self.is_running:
                    break
                time.sleep(0.5)
                
                # Spam 'e' for the entire end delay duration
                end_delay = self.end_delay.get()
                if end_delay > 0:
                    print(f"[PLAYBACK] Spamming 'e' for {end_delay}s (100ms intervals)")
                    spam_start = time.time()
                    while (time.time() - spam_start) < end_delay:
                        if not self.is_running:
                            break
                        pydirectinput.press('e')
                        time.sleep(0.1)  # 100ms between each 'e' press
                
                if not self.is_running:
                    break
                
                # Wait 500ms after end delay
                time.sleep(0.5)
                
                # Press "main tool" hotkey
                main_tool_key = self.main_tool.get()
                print(f"[PLAYBACK] Pressing main tool key: {main_tool_key}")
                pydirectinput.press(main_tool_key)
                
                # Wait 500ms
                if not self.is_running:
                    break
                time.sleep(0.5)
                    
        except Exception as e:
            print(f"Error in playback loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("[PLAYBACK] Playback loop ended")
    
    def _create_overlay(self):
        """Create a preview window for visualizations (doesn't interfere with mss)"""
        if self.overlay_window:
            return
        
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("Detection Preview")
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.geometry("800x600+100+100")
        self.overlay_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing
        
        # Create canvas for drawing preview
        self.overlay_canvas = tk.Canvas(self.overlay_window, 
                                        bg='black',
                                        highlightthickness=0)
        self.overlay_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Start the visualization update loop
        self._update_visualization()
    
    def _destroy_overlay(self):
        """Destroy the overlay window"""
        if self.overlay_window:
            try:
                self.overlay_window.destroy()
            except:
                pass
            self.overlay_window = None
    
    def _update_visualization(self):
        """Update the preview window with latest detections"""
        if not self.overlay_window:
            return
        
        try:
            # Only update with new data if running
            if self.is_running and hasattr(self, 'latest_frame') and self.latest_frame is not None:
                # Draw on the captured frame
                img = self.latest_frame.copy()
                draw = ImageDraw.Draw(img)
                
                # Draw bounding boxes for latest detections
                for detection in self.latest_detections:
                    x1, y1, x2, y2 = detection['box']
                    class_name = detection['class']
                    confidence = detection['confidence']
                    
                    # Choose color based on class
                    color = 'green' if class_name == 'Icon' else 'red'
                    
                    # Draw rectangle
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                    
                    # Draw label
                    label = f"{class_name} {confidence:.2f}"
                    draw.text((x1, y1 - 15), label, fill=color)
                
                # Resize to fit preview window
                canvas_width = self.overlay_canvas.winfo_width()
                canvas_height = self.overlay_canvas.winfo_height()
                if canvas_width > 1 and canvas_height > 1:
                    img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage and display
                    photo = ImageTk.PhotoImage(img)
                    self.overlay_canvas.delete('all')
                    self.overlay_canvas.create_image(canvas_width//2, canvas_height//2, 
                                                     image=photo, anchor='center')
                    # Keep reference to prevent garbage collection
                    self.overlay_canvas.image = photo
            
            # Schedule next update (30 FPS for preview)
            self.root.after(33, self._update_visualization)
        except Exception as e:
            print(f"Error updating visualization: {e}")
    
    def toggle_start_stop(self):
        """Toggle between start and stop states"""
        if self.rebinding:
            return  # Ignore if we're rebinding
        
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_button.config(text=f"Stop ({self.hotkeys['start_stop']})")
            self.status_label.config(text="Running", foreground='green')
            print(">>> STARTED")
            
            # Focus Roblox window
            self.root.after(100, self._focus_roblox)
            
            # Zoom in if first person mode is enabled
            if self.first_person_mode.get():
                self.root.after(300, self._zoom_in_first_person)
            
            # Auto minimize GUI if enabled
            if self.auto_minimize.get():
                self.root.after(200, lambda: self.root.iconify())
                print("GUI minimized")
            
            # Start the main loop in a separate thread
            self.main_loop_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_loop_thread.start()
            
            # Start the playback loop in a separate thread if there are recorded actions
            if self.recorded_actions:
                self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
                self.playback_thread.start()
                print(f">>> PLAYBACK STARTED: {len(self.recorded_actions)} actions, {self.end_delay.get()}s end delay")
        else:
            self.start_button.config(text=f"Start ({self.hotkeys['start_stop']})")
            self.status_label.config(text="Stopped", foreground='red')
            print(">>> STOPPED")
            
            # Restore GUI if it was minimized
            if self.auto_minimize.get():
                self.root.deiconify()
                self.root.lift()
                print("GUI restored")
            
            # Release all tracked pressed keys
            try:
                with self.keys_lock:
                    keys_to_release = list(self.pressed_keys)
                    self.pressed_keys.clear()
                
                for key in keys_to_release:
                    try:
                        pydirectinput.keyUp(key)
                        print(f"Released key: {key}")
                    except Exception as e:
                        print(f"Error releasing key {key}: {e}")
                
                self.is_holding_arrow = False
            except Exception as e:
                print(f"Error releasing keys: {e}")
    
    def _main_loop(self):
        """Main loop that runs when started"""
        try:
            # Load the YOLO model
            if not self.selected_model:
                print("No model selected!")
                self.is_running = False
                # Update UI from thread
                self.root.after(0, lambda: self.start_button.config(text=f"Start ({self.hotkeys['start_stop']})"))
                self.root.after(0, lambda: self.status_label.config(text="Stopped", foreground='red'))
                return
            
            model_path = self.selected_model
            # If it's just a filename, construct full path
            if not os.path.isabs(model_path):
                if getattr(sys, 'frozen', False):
                    # Running as compiled exe
                    base_dir = os.path.dirname(sys.executable)
                else:
                    # Running as script
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(base_dir, model_path)
            
            print(f"Loading model: {model_path}")
            
            # Determine device based on user setting
            if self.use_gpu.get():
                try:
                    # Try to load with GPU
                    self.model = YOLO(model_path)
                    # Try to move to GPU to verify it works
                    self.model.to('cuda')
                    print("Model loaded successfully on GPU")
                except Exception as e:
                    print(f"GPU failed ({e}), falling back to CPU")
                    try:
                        self.model = YOLO(model_path)
                        self.model.to('cpu')
                        print("Model loaded successfully on CPU (GPU fallback)")
                    except Exception as e2:
                        print(f"Failed to load model on CPU: {e2}")
                        raise
            else:
                # User selected CPU
                self.model = YOLO(model_path)
                self.model.to('cpu')
                print("Model loaded successfully on CPU")
            
            # Create mss instance for faster screen capture
            sct = mss.mss()
            
            # Get the monitor where the window is located
            monitor_number = self._get_current_monitor()
            monitor = sct.monitors[monitor_number]
            print(f"Capturing monitor {monitor_number}: {monitor['width']}x{monitor['height']}")
            
            while self.is_running:
                # Capture the entire screen using mss (much faster than ImageGrab)
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array (drop alpha channel - only use RGB)
                screen_np = np.array(screenshot)[:, :, :3]
                
                # Store frame for visualization (convert to PIL Image)
                if self.show_visualization.get():
                    self.latest_frame = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                
                # Run YOLO detection
                results = self.model(screen_np, verbose=False)
                
                # Process detections
                detections = []
                icon_found = False
                best_icon = None  # Track the highest confidence Icon
                best_santa = None  # Track the highest confidence Santa
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Get class name
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        confidence = float(box.conf[0])
                        
                        # Check if it's Icon or Santa and meets confidence threshold
                        if class_name == 'Icon' and confidence >= self.icon_confidence.get():
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            # Track the best Icon (highest confidence)
                            if best_icon is None or confidence > best_icon['confidence']:
                                best_icon = {
                                    'box': (x1, y1, x2, y2),
                                    'confidence': confidence
                                }
                        elif class_name == 'Santa' and confidence >= self.santa_confidence.get():
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            # Track the best Santa (highest confidence)
                            if best_santa is None or confidence > best_santa['confidence']:
                                best_santa = {
                                    'box': (x1, y1, x2, y2),
                                    'confidence': confidence
                                }
                        else:
                            continue
                        
                        # Store detection for visualization
                        detections.append({
                            'box': (x1, y1, x2, y2),
                            'class': class_name,
                            'confidence': confidence
                        })
                
                # Check if both icon and santa are detected (for playback)
                self.both_detected = (best_icon is not None) and (best_santa is not None)
                
                # FIRST PERSON MODE LOGIC
                if self.first_person_mode.get():
                    # Set pydirectinput pause to 0 for Method 8
                    pydirectinput.PAUSE = 0
                    
                    # Get current cursor position
                    current_x, current_y = win32api.GetCursorPos()
                    screen_center_x = monitor['width'] / 2
                    screen_center_y = monitor['height'] / 2
                    
                    # Scenario 1: No icon, no santa - Do nothing
                    if best_icon is None and best_santa is None:
                        pass
                    
                    # Scenario 2: Yes icon, no santa - Center icon (X-axis only)
                    elif best_icon is not None and best_santa is None:
                        x1, y1, x2, y2 = best_icon['box']
                        icon_center_x = (x1 + x2) / 2
                        
                        # Calculate error from screen center
                        error_x = icon_center_x - screen_center_x
                        deadzone = 30  # pixels
                        
                        if abs(error_x) > deadzone:
                            # Adaptive movement: start small, increase if error persists
                            base_movement = 5
                            
                            # Adaptive sensitivity based on error magnitude
                            if abs(error_x) > 200:
                                movement_scale = 3.0
                            elif abs(error_x) > 100:
                                movement_scale = 2.0
                            else:
                                movement_scale = 1.0
                            
                            # Calculate movement (proportional to error, capped)
                            move_x = int(error_x * 0.1 * movement_scale)
                            move_x = max(-50, min(50, move_x))  # Cap at ±50 pixels
                            
                            # Apply movement (X-axis only, Y=0)
                            pydirectinput.moveRel(move_x, 0, relative=True)
                            print(f"FP: Centering icon, error={error_x:.0f}px, move={move_x}px")
                    
                    # Scenario 3: No icon, yes santa - Track santa (X and Y axis)
                    elif best_icon is None and best_santa is not None:
                        x1, y1, x2, y2 = best_santa['box']
                        santa_center_x = int((x1 + x2) / 2)
                        santa_center_y = int((y1 + y2) / 2)
                        
                        # Determine target based on movement
                        is_moving = False
                        if self.santa_prev_center is not None:
                            prev_x, prev_y = self.santa_prev_center
                            delta_x = abs(santa_center_x - prev_x)
                            delta_y = abs(santa_center_y - prev_y)
                            if delta_x > 5 or delta_y > 5:
                                is_moving = True
                        
                        # Choose target
                        if is_moving:
                            target_x = int(x1)  # Left edge
                            target_y = santa_center_y
                        else:
                            target_x = santa_center_x
                            target_y = santa_center_y
                        
                        # Calculate error from current cursor position
                        error_x = target_x - current_x
                        error_y = target_y - current_y
                        
                        # Adaptive sensitivity based on error magnitude
                        error_magnitude = (error_x**2 + error_y**2)**0.5
                        
                        if error_magnitude > 100:
                            sensitivity = 0.3  # Fast for large errors
                        elif error_magnitude > 50:
                            sensitivity = 0.2  # Medium
                        else:
                            sensitivity = 0.1  # Slow for precise tracking
                        
                        # Calculate movement with adaptive sensitivity
                        move_x = int(error_x * sensitivity * self.fp_sensitivity)
                        move_y = int(error_y * sensitivity * self.fp_sensitivity)
                        
                        # Cap movement to prevent overshooting
                        move_x = max(-50, min(50, move_x))
                        move_y = max(-50, min(50, move_y))
                        
                        # Apply movement
                        if abs(move_x) > 1 or abs(move_y) > 1:
                            pydirectinput.moveRel(move_x, move_y, relative=True)
                            print(f"FP: Track santa, error=({error_x:.0f},{error_y:.0f}), move=({move_x},{move_y})")
                        
                        # Update sensitivity based on tracking performance
                        if abs(error_magnitude - self.fp_last_error) < 5:
                            # Error not decreasing much, increase sensitivity
                            self.fp_sensitivity = min(2.0, self.fp_sensitivity * 1.02)
                        else:
                            # Error decreasing, maintain or slightly reduce
                            self.fp_sensitivity = max(0.5, self.fp_sensitivity * 0.99)
                        
                        self.fp_last_error = error_magnitude
                        self.santa_prev_center = (santa_center_x, santa_center_y)
                    
                    # Scenario 4: Yes icon, yes santa - Ignore icon, track santa
                    elif best_icon is not None and best_santa is not None:
                        x1, y1, x2, y2 = best_santa['box']
                        santa_center_x = int((x1 + x2) / 2)
                        santa_center_y = int((y1 + y2) / 2)
                        
                        # Same tracking logic as Scenario 3
                        is_moving = False
                        if self.santa_prev_center is not None:
                            prev_x, prev_y = self.santa_prev_center
                            delta_x = abs(santa_center_x - prev_x)
                            delta_y = abs(santa_center_y - prev_y)
                            if delta_x > 5 or delta_y > 5:
                                is_moving = True
                        
                        if is_moving:
                            target_x = int(x1)
                            target_y = santa_center_y
                        else:
                            target_x = santa_center_x
                            target_y = santa_center_y
                        
                        error_x = target_x - current_x
                        error_y = target_y - current_y
                        error_magnitude = (error_x**2 + error_y**2)**0.5
                        
                        if error_magnitude > 100:
                            sensitivity = 0.3
                        elif error_magnitude > 50:
                            sensitivity = 0.2
                        else:
                            sensitivity = 0.1
                        
                        move_x = int(error_x * sensitivity * self.fp_sensitivity)
                        move_y = int(error_y * sensitivity * self.fp_sensitivity)
                        move_x = max(-50, min(50, move_x))
                        move_y = max(-50, min(50, move_y))
                        
                        if abs(move_x) > 1 or abs(move_y) > 1:
                            pydirectinput.moveRel(move_x, move_y, relative=True)
                            print(f"FP: Track santa (icon ignored), move=({move_x},{move_y})")
                        
                        if abs(error_magnitude - self.fp_last_error) < 5:
                            self.fp_sensitivity = min(2.0, self.fp_sensitivity * 1.02)
                        else:
                            self.fp_sensitivity = max(0.5, self.fp_sensitivity * 0.99)
                        
                        self.fp_last_error = error_magnitude
                        self.santa_prev_center = (santa_center_x, santa_center_y)
                
                # NORMAL MODE LOGIC (Original arrow key control)
                else:
                    # Process the best Icon (highest confidence) if found
                    if best_icon is not None:
                        icon_found = True
                        x1, y1, x2, y2 = best_icon['box']
                        icon_center_x = (x1 + x2) / 2
                        screen_center = monitor['width'] / 2
                        
                        # Determine which side the icon is on
                        if icon_center_x < screen_center:
                            icon_side = "left"
                        else:
                            icon_side = "right"
                        
                        # State machine logic
                        if self.icon_state == "searching_left" or self.icon_state == "searching_right":
                            # Found icon, start tracking
                            print(f"Icon found at x={icon_center_x:.0f}, conf={best_icon['confidence']:.2f}, switching to tracking mode")
                            self.icon_state = "tracking"
                            self.icon_last_side = icon_side
                            
                        elif self.icon_state == "tracking":
                            # Update last known side
                            self.icon_last_side = icon_side
                            
                            # Check if icon is off-center and needs adjustment
                            screen_center = monitor['width'] / 2
                            distance_from_center = abs(icon_center_x - screen_center)
                            center_tolerance = monitor['width'] * 0.1  # 10% of screen width
                            
                            # If icon is off-center, send burst movements to center it
                            current_time = time.time()
                            if distance_from_center > center_tolerance:
                                # Only send burst if enough time has passed (200ms)
                                if current_time - self.last_arrow_burst_time >= 0.2:
                                    if icon_center_x < screen_center:
                                        # Icon is to the left, hold left arrow for 200ms
                                        pydirectinput.keyDown('left')
                                        time.sleep(0.2)
                                        pydirectinput.keyUp('left')
                                        print(f"Centering: Icon at {icon_center_x:.0f}, HOLD LEFT 200ms")
                                    else:
                                        # Icon is to the right, hold right arrow for 200ms
                                        pydirectinput.keyDown('right')
                                        time.sleep(0.2)
                                        pydirectinput.keyUp('right')
                                        print(f"Centering: Icon at {icon_center_x:.0f}, HOLD RIGHT 200ms")
                                    self.last_arrow_burst_time = current_time
                    
                    # Move cursor to the best Santa (highest confidence) if found
                    if best_santa is not None:
                        x1, y1, x2, y2 = best_santa['box']
                        santa_center_x = int((x1 + x2) / 2)
                        santa_center_y = int((y1 + y2) / 2)
                        
                        # Determine if Santa is moving
                        is_moving = False
                        if self.santa_prev_center is not None:
                            prev_x, prev_y = self.santa_prev_center
                            delta_x = abs(santa_center_x - prev_x)
                            delta_y = abs(santa_center_y - prev_y)
                            # Consider moving if delta is more than 5 pixels
                            if delta_x > 5 or delta_y > 5:
                                is_moving = True
                        
                        # Choose target based on movement
                        if is_moving:
                            # Moving: aim at leftmost edge (middle-left)
                            target_x = int(x1)
                            target_y = santa_center_y
                        else:
                            # Still: aim at center
                            target_x = santa_center_x
                            target_y = santa_center_y
                        
                        # Limit cursor to never go within 10px of the very top of screen
                        if target_y < 10:
                            target_y = 10
                        
                        # Update previous center for next frame
                        self.santa_prev_center = (santa_center_x, santa_center_y)
                        
                        # Move cursor to target using Roblox-compatible technique
                        # 1. Move cursor to position
                        ctypes.windll.user32.SetCursorPos(target_x, target_y)
                        # 2. Move cursor down by 1 pixel relatively to register with Roblox
                        ctypes.windll.user32.mouse_event(0x0001, 0, 1, 0, 0)  # MOUSEEVENTF_MOVE
                        print(f"Santa at ({santa_center_x}, {santa_center_y}), conf={best_santa['confidence']:.2f}, cursor->({target_x}, {target_y})")
                    else:
                        # No Santa found, reset tracking
                        self.santa_prev_center = None
                    
                    # Handle icon not found - only switch to searching if currently tracking
                    if not icon_found and self.icon_state == "tracking":
                        # Icon disappeared, switch to searching based on last known side
                        if self.icon_last_side == "left":
                            self.icon_state = "searching_left"
                            print(f"Icon lost (last seen: left), searching left...")
                        else:
                            self.icon_state = "searching_right"
                            print(f"Icon lost (last seen: right), searching right...")
                    
                    # Execute searching movements (only when icon is NOT found and we're searching)
                    if not icon_found:
                        current_time = time.time()
                        if self.icon_state == "searching_left":
                            # Hold left arrow for 200ms
                            if current_time - self.last_arrow_burst_time >= 0.2:
                                pydirectinput.keyDown('left')
                                time.sleep(0.2)
                                pydirectinput.keyUp('left')
                                self.last_arrow_burst_time = current_time
                                print("Searching: HOLD LEFT 200ms")
                            
                        elif self.icon_state == "searching_right":
                            # Hold right arrow for 200ms
                            if current_time - self.last_arrow_burst_time >= 0.2:
                                pydirectinput.keyDown('right')
                                time.sleep(0.2)
                                pydirectinput.keyUp('right')
                                self.last_arrow_burst_time = current_time
                                print("Searching: HOLD RIGHT 200ms")
                
                # Update latest detections for visualization (thread-safe)
                self.latest_detections = detections
                
                # Check if we should stop
                if not self.is_running:
                    break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False
            # Update UI from thread
            self.root.after(0, lambda: self.start_button.config(text=f"Start ({self.hotkeys['start_stop']})"))
            self.root.after(0, lambda: self.status_label.config(text="Stopped", foreground='red'))
        finally:
            # No need to release arrow keys since we're using bursts now
            self.model = None
            print("Main loop ended")
    
    def start_rebinding(self, hotkey_name):
        """Start the rebinding process for a hotkey"""
        if self.rebinding:
            return  # Already rebinding
        
        self.rebinding = hotkey_name
        
        # Update UI
        if hotkey_name == 'start_stop':
            button = self.rebind_start_button
            button_text = "Start/Stop"
        elif hotkey_name == 'record':
            button = self.rebind_record_button
            button_text = "Record"
        else:
            button = self.rebind_exit_button
            button_text = "Exit"
        
        button.config(state='disabled')
        self.rebind_label.config(text=f"Press key for {button_text} (ESC=cancel)")
        
        # Unhook current hotkeys
        keyboard.unhook_all()
        
        # Setup temporary hook for rebinding
        keyboard.on_press(self._on_rebind_key)
    
    def _on_rebind_key(self, event):
        """Handle key press during rebinding"""
        key = event.name.upper()
        
        # Cancel on ESC
        if key == 'ESC':
            self.cancel_rebinding()
            return
        
        # Update the hotkey
        old_key = self.hotkeys[self.rebinding]
        self.hotkeys[self.rebinding] = key
        
        # Update button text
        if self.rebinding == 'start_stop':
            if self.is_running:
                self.start_button.config(text=f"Stop ({key})")
            else:
                self.start_button.config(text=f"Start ({key})")
            self.rebind_start_button.config(state='normal')
        elif self.rebinding == 'record':
            if self.is_recording:
                self.record_button.config(text=f"Stop ({key})")
            else:
                self.record_button.config(text=f"Record ({key})")
            self.rebind_record_button.config(state='normal')
        else:
            self.exit_button.config(text=f"Exit ({key})")
            self.rebind_exit_button.config(state='normal')
        
        # Clear rebinding state
        self.rebinding = None
        self.rebind_label.config(text=f"{old_key} → {key}")
        
        # Re-setup hotkeys
        self._setup_hotkeys()
        
        # Save settings
        self._save_settings()
        
        # Clear the message after 2 seconds
        self.root.after(2000, lambda: self.rebind_label.config(text=""))
    
    def cancel_rebinding(self):
        """Cancel the rebinding process"""
        if self.rebinding == 'start_stop':
            self.rebind_start_button.config(state='normal')
        elif self.rebinding == 'record':
            self.rebind_record_button.config(state='normal')
        else:
            self.rebind_exit_button.config(state='normal')
        
        self.rebinding = None
        self.rebind_label.config(text="Cancelled")
        
        # Re-setup hotkeys
        self._setup_hotkeys()
        
        # Clear the message after 2 seconds
        self.root.after(2000, lambda: self.rebind_label.config(text=""))
    
    def _refresh_pt_files(self, event):
        """Refresh the list of .pt files when dropdown is clicked"""
        current_selection = self.model_dropdown.get()
        
        # Rescan for .pt files
        self._scan_pt_files()
        
        # Update dropdown values
        if self.pt_files:
            self.model_dropdown['values'] = self.pt_files
            # Try to maintain current selection if it still exists
            if current_selection in self.pt_files:
                self.model_dropdown.set(current_selection)
            else:
                self.model_dropdown.current(0)
                self.selected_model = self.pt_files[0]
        else:
            self.model_dropdown['values'] = ["no .pt files found"]
            self.model_dropdown.current(0)
            self.selected_model = None
    
    def _on_model_selected(self, event):
        """Handle model selection from dropdown"""
        selected = self.model_dropdown.get()
        if selected != "no .pt files found":
            self.selected_model = selected
            print(f"Selected model: {selected}")
            self._save_settings()
    
    def _browse_model(self):
        """Open file browser to manually select a .pt file"""
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = filedialog.askopenfilename(
            title="Select Model File",
            initialdir=initial_dir,
            filetypes=[("PyTorch Model", "*.pt"), ("All Files", "*.*")]
        )
        
        if filepath:
            # Get just the filename
            filename = os.path.basename(filepath)
            self.selected_model = filepath
            
            # Update dropdown
            current_values = list(self.model_dropdown['values'])
            if "no .pt files found" in current_values:
                current_values = []
            
            if filename not in current_values:
                current_values.append(filename)
                self.model_dropdown['values'] = current_values
            
            # Set the selected value
            self.model_dropdown.set(filename)
            print(f"Manually selected model: {filepath}")
            self._save_settings()
    
    def force_exit(self):
        """Force close the application"""
        print(">>> FORCE EXITING...")
        try:
            keyboard.unhook_all()
        except:
            pass
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        # Force terminate the process
        os._exit(0)
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.force_exit()
        except Exception as e:
            print(f"Error: {e}")
            self.force_exit()


def show_terms_and_conditions():
    """Show terms of use dialog on first launch - must accept to continue"""
    # Create temporary root for dialog
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    # Message text
    message = """═════════════════════════════════════════════════════
           GPO SANTA - TERMS OF USE
                    by AsphaltCake
═════════════════════════════════════════════════════

⚠️ IMPORTANT NOTICE ⚠️

This application is NOT a virus or malware!
  • Santa detection automation tool for Roblox GPO
  • Antivirus may flag it (automates mouse/keyboard - this is normal)
  • Safe to use - built with Python 3.14 & PyInstaller
  • You can decompile it if you want to verify the code
  • No data collection or malicious behavior

═════════════════════════════════════════════════════

BY USING THIS SOFTWARE:
  ✓ You understand this is automation software
  ✓ You will NOT redistribute as your own work
  ✓ You will credit AsphaltCake if sharing/modifying

═════════════════════════════════════════════════════

ON FIRST LAUNCH:
  • Opens YouTube (AsphaltCake's channel) in browser
  • Auto-clicks Subscribe button to support the creator
  • Closes browser tab automatically

═════════════════════════════════════════════════════

ACCEPT: Agree to terms & continue (auto-subscribes)
DECLINE: Exit application

Creator: AsphaltCake (@AsphaltCake on YouTube)"""
    
    # Show messagebox with Yes/No
    result = messagebox.askyesno(
        "Terms of Use - GPO Santa",
        message,
        icon='info'
    )
    
    temp_root.destroy()
    return result


def auto_subscribe_to_youtube():
    """
    Attempt to auto-subscribe to YouTube channel.
    Opens browser with subscribe link and attempts automated subscription.
    """
    YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@AsphaltCake?sub_confirmation=1"
    
    print("\n" + "="*50)
    print("AUTO-SUBSCRIBE TO YOUTUBE CHANNEL")
    print("="*50)
    
    try:
        # Open YouTube channel with subscribe confirmation
        print(f"🌐 Opening YouTube channel in browser...")
        webbrowser.open(YOUTUBE_CHANNEL_URL)
        
        # Wait for browser to load
        print("⏳ Waiting for browser to load...")
        start_time = time.time()
        browser_found = False
        
        # Try to find browser window (timeout after a few seconds)
        while time.time() - start_time < 5:
            try:
                import pygetwindow as gw
                windows = gw.getAllTitles()
                for title in windows:
                    if any(browser in title.lower() for browser in ['chrome', 'firefox', 'edge', 'opera', 'brave']):
                        browser_found = True
                        print(f"✅ Browser window found: {title}")
                        break
                if browser_found:
                    break
            except:
                pass
            time.sleep(0.5)
        
        if not browser_found:
            print("⚠️ Could not detect browser window, continuing anyway...")
            print("Please manually subscribe if the page opened!")
        
        # Wait for YouTube page to load
        print("⏳ Waiting for YouTube page to load...")
        time.sleep(3.5)
        
        # Try to focus browser window
        print("🖱️ Attempting to focus browser...")
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('AsphaltCake')
            if windows:
                windows[0].activate()
        except Exception as e:
            print(f"⚠️ Could not focus browser: {e}")
        
        # Navigate to subscribe button using Tab and Enter
        print("🧭 Navigating to Subscribe button...")
        try:
            keyboard.press_and_release('tab')
            time.sleep(0.2)
            keyboard.press_and_release('tab')
            time.sleep(0.2)
            keyboard.press_and_release('enter')
            time.sleep(0.5)
            
            print("✅ Subscribe sequence executed!")
        except Exception as e:
            print(f"⚠️ Could not navigate: {e}")
        
        # Close the tab
        print("❌ Closing YouTube tab...")
        try:
            keyboard.press_and_release('ctrl+w')
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ Error closing tab: {e}")
        
        print("✅ Auto-subscribe sequence completed!")
        print("="*50 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Auto-subscribe failed: {e}")
        print("Continuing to main application...")
        return False


def main():
    # Check if settings file exists
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    settings_file = os.path.join(application_path, "GPOSantaSettings.json")
    
    # If settings don't exist, show terms and do auto-subscribe
    first_launch = not os.path.exists(settings_file)
    
    if first_launch:
        print("\n🎉 First launch detected - showing terms...")
        
        # Show terms dialog - must accept to continue
        if not show_terms_and_conditions():
            print("❌ Terms declined - exiting...")
            sys.exit(0)
        
        print("Terms accepted - proceeding with auto-subscribe...")
        try:
            auto_subscribe_to_youtube()
        except Exception as e:
            print(f"Auto-subscribe error: {e}")
        
        # Small delay before launching main app
        time.sleep(0.5)
    
    # Create and run the app
    app = GPOSantaApp()
    
    # Save settings after first launch to create the file
    if first_launch:
        app._save_settings()
        print("✅ Settings file created - Terms of Use won't show again")
    
    app.run()


if __name__ == "__main__":
    main()
