import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import threading
import time
import json
import os
import sys
import webbrowser
import pyautogui


class DreambreakerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dreambreaker")
        self.root.geometry("400x600")
        self.root.attributes("-topmost", True)
        
        # Get screen resolution
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Settings file path - handle PyInstaller's temp folder
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            application_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        self.settings_path = os.path.join(application_path, "DreamSettings.txt")
        
        # Load settings from file
        self._load_settings()
        
        self.rebinding_key = None
        self.area_selector = None
        
        # Friend color for detection
        self.friend_color = [155, 255, 155]
        self.friend_color_tolerance = 5
        
        # Fish detection colors (white variants)
        self.fish_colors = [[255, 255, 255], [241, 241, 241]]  # FFFFFF and F1F1F1
        self.fish_color_tolerance = 5
        
        # Bot state
        self.bot_running = False
        self.bot_thread = None
        self.bot_stop_event = threading.Event()
        self.fish_state = "release"  # "release" or "hold"
        
        # Camera instances (reuse to avoid conflicts)
        self.friend_camera = None
        self.fish_camera = None
        
        # Create UI
        self._create_widgets()
        
        # Setup keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _scale_coords_from_reference(self, coords):
        """Scale coordinates from 2560x1440 reference resolution to current resolution"""
        ref_width = 2560
        ref_height = 1440
        
        scaled = {
            "x1": int(coords["x1"] * self.screen_width / ref_width),
            "y1": int(coords["y1"] * self.screen_height / ref_height),
            "x2": int(coords["x2"] * self.screen_width / ref_width),
            "y2": int(coords["y2"] * self.screen_height / ref_height)
        }
        return scaled
    
    def _load_settings(self):
        """Load settings from DreamSettings.txt"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Load box coordinates (will be in user's actual resolution)
                self.friend_box = settings.get("friend_box")
                self.fish_box = settings.get("fish_box")
                
                # If no saved coordinates, use scaled defaults from 2560x1440
                if not self.friend_box:
                    self.friend_box = self._scale_coords_from_reference({"x1": 39, "y1": 1329, "x2": 95, "y2": 1382})
                if not self.fish_box:
                    self.fish_box = self._scale_coords_from_reference({"x1": 764, "y1": 1217, "x2": 1795, "y2": 1256})
                
                # Load cast settings
                self.cast_settings = settings.get("cast_settings", {
                    "delay_before_click": 0.0,
                    "delay_hold_duration": 0.5,
                    "delay_after_release": 0.5,
                    "anti_nuke": True,
                    "anti_nuke_delay_before": 0.0,
                    "anti_nuke_bag_slot": 2,
                    "anti_nuke_delay_after_bag": 0.5,
                    "anti_nuke_rod_slot": 1,
                    "anti_nuke_delay_after_rod": 0.5,
                    "after_fish_delay": 1.0
                })
                
                # Load hotkeys
                hotkey_settings = settings.get("hotkeys", {
                    "start_stop": "f3",
                    "change_area": "f1",
                    "exit": "f4"
                })
                self.hotkeys = {
                    "start_stop": self._string_to_key(hotkey_settings["start_stop"]),
                    "change_area": self._string_to_key(hotkey_settings["change_area"]),
                    "exit": self._string_to_key(hotkey_settings["exit"])
                }
                
                print(f"Settings loaded from {self.settings_path}")
            else:
                # Use scaled defaults from 2560x1440
                self.friend_box = self._scale_coords_from_reference({"x1": 39, "y1": 1329, "x2": 95, "y2": 1382})
                self.fish_box = self._scale_coords_from_reference({"x1": 764, "y1": 1217, "x2": 1795, "y2": 1256})
                self.cast_settings = {
                    "delay_before_click": 0.0,
                    "delay_hold_duration": 0.5,
                    "delay_after_release": 0.5,
                    "anti_nuke": False,
                    "anti_nuke_delay_before": 0.0,
                    "anti_nuke_bag_slot": 2,
                    "anti_nuke_delay_after_bag": 0.5,
                    "anti_nuke_rod_slot": 1,
                    "anti_nuke_delay_after_rod": 0.5,
                    "after_fish_delay": 1.0
                }
                self.hotkeys = {
                    "start_stop": keyboard.Key.f3,
                    "change_area": keyboard.Key.f1,
                    "exit": keyboard.Key.f4
                }
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Use scaled defaults on error from 2560x1440
            self.friend_box = self._scale_coords_from_reference({"x1": 39, "y1": 1329, "x2": 95, "y2": 1382})
            self.fish_box = self._scale_coords_from_reference({"x1": 764, "y1": 1217, "x2": 1795, "y2": 1256})
            self.cast_settings = {
                "delay_before_click": 0.0,
                "delay_hold_duration": 0.5,
                "delay_after_release": 0.5,
                "anti_nuke": True,
                "anti_nuke_delay_before": 0.0,
                "anti_nuke_bag_slot": 2,
                "anti_nuke_delay_after_bag": 0.5,
                "anti_nuke_rod_slot": 1,
                "anti_nuke_delay_after_rod": 0.5,
                "after_fish_delay": 1.0
            }
            self.hotkeys = {
                "start_stop": keyboard.Key.f3,
                "change_area": keyboard.Key.f1,
                "exit": keyboard.Key.f4
            }
    
    def _save_settings(self):
        """Save settings to DreamSettings.txt"""
        try:
            settings = {
                "terms_accepted": True,
                "friend_box": self.friend_box,
                "fish_box": self.fish_box,
                "cast_settings": self.cast_settings,
                "hotkeys": {
                    "start_stop": self._key_to_string(self.hotkeys["start_stop"]).lower(),
                    "change_area": self._key_to_string(self.hotkeys["change_area"]).lower(),
                    "exit": self._key_to_string(self.hotkeys["exit"]).lower()
                }
            }
            
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"Settings saved to {self.settings_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _string_to_key(self, key_str):
        """Convert string to keyboard key"""
        key_str = key_str.lower()
        if key_str.startswith('f') and key_str[1:].isdigit():
            # F-keys
            return getattr(keyboard.Key, key_str)
        elif len(key_str) == 1:
            # Single character
            return keyboard.KeyCode.from_char(key_str)
        else:
            # Try to get from Key enum
            try:
                return getattr(keyboard.Key, key_str)
            except:
                return keyboard.Key.f3  # Default fallback
    
    def _create_widgets(self):
        """Create the UI elements"""
        # Hotkeys section
        hotkey_frame = tk.LabelFrame(self.root, text="Hotkeys", padx=10, pady=10)
        hotkey_frame.pack(pady=10, padx=10, fill="x")
        
        # Start/Stop
        frame1 = tk.Frame(hotkey_frame)
        frame1.pack(pady=2, fill="x")
        tk.Label(frame1, text="Start/Stop:", width=12, anchor="w").pack(side="left")
        self.start_stop_label = tk.Label(frame1, text=self._key_to_string(self.hotkeys["start_stop"]), 
                                         width=8, relief="solid", borderwidth=1)
        self.start_stop_label.pack(side="left", padx=5)
        tk.Button(frame1, text="Rebind", command=lambda: self._start_rebind("start_stop")).pack(side="left")
        
        # Change Area
        frame2 = tk.Frame(hotkey_frame)
        frame2.pack(pady=2, fill="x")
        tk.Label(frame2, text="Change Area:", width=12, anchor="w").pack(side="left")
        self.change_area_label = tk.Label(frame2, text=self._key_to_string(self.hotkeys["change_area"]), 
                                          width=8, relief="solid", borderwidth=1)
        self.change_area_label.pack(side="left", padx=5)
        tk.Button(frame2, text="Rebind", command=lambda: self._start_rebind("change_area")).pack(side="left")
        
        # Exit
        frame3 = tk.Frame(hotkey_frame)
        frame3.pack(pady=2, fill="x")
        tk.Label(frame3, text="Exit:", width=12, anchor="w").pack(side="left")
        self.exit_label = tk.Label(frame3, text=self._key_to_string(self.hotkeys["exit"]), 
                                   width=8, relief="solid", borderwidth=1)
        self.exit_label.pack(side="left", padx=5)
        tk.Button(frame3, text="Rebind", command=lambda: self._start_rebind("exit")).pack(side="left")
        
        # Cast settings section
        cast_frame = tk.LabelFrame(self.root, text="Cast Settings", padx=10, pady=10)
        cast_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Anti-nuke settings (first)
        self.anti_nuke_var = tk.BooleanVar(value=self.cast_settings["anti_nuke"])
        tk.Checkbutton(cast_frame, text="Enable Anti-Nuke", variable=self.anti_nuke_var,
                      command=self._update_cast_settings).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        
        tk.Label(cast_frame, text="Anti-Nuke Delay Before:", anchor="w").grid(row=1, column=0, sticky="w", pady=2)
        self.anti_nuke_delay_before_var = tk.DoubleVar(value=self.cast_settings["anti_nuke_delay_before"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.anti_nuke_delay_before_var, 
                   width=10, command=self._update_cast_settings).grid(row=1, column=1, pady=2)
        
        tk.Label(cast_frame, text="Bag Slot:", anchor="w").grid(row=2, column=0, sticky="w", pady=2)
        self.bag_slot_var = tk.IntVar(value=self.cast_settings["anti_nuke_bag_slot"])
        tk.Spinbox(cast_frame, from_=1, to=9, textvariable=self.bag_slot_var, 
                   width=10, command=self._update_cast_settings).grid(row=2, column=1, pady=2)
        
        tk.Label(cast_frame, text="Delay After Bag:", anchor="w").grid(row=3, column=0, sticky="w", pady=2)
        self.delay_after_bag_var = tk.DoubleVar(value=self.cast_settings["anti_nuke_delay_after_bag"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.delay_after_bag_var, 
                   width=10, command=self._update_cast_settings).grid(row=3, column=1, pady=2)
        
        tk.Label(cast_frame, text="Rod Slot:", anchor="w").grid(row=4, column=0, sticky="w", pady=2)
        self.rod_slot_var = tk.IntVar(value=self.cast_settings["anti_nuke_rod_slot"])
        tk.Spinbox(cast_frame, from_=1, to=9, textvariable=self.rod_slot_var, 
                   width=10, command=self._update_cast_settings).grid(row=4, column=1, pady=2)
        
        tk.Label(cast_frame, text="Delay After Rod:", anchor="w").grid(row=5, column=0, sticky="w", pady=2)
        self.delay_after_rod_var = tk.DoubleVar(value=self.cast_settings["anti_nuke_delay_after_rod"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.delay_after_rod_var, 
                   width=10, command=self._update_cast_settings).grid(row=5, column=1, pady=2)
        
        # Spacer
        tk.Label(cast_frame, text="", anchor="w").grid(row=6, column=0, pady=5)
        
        # Regular cast settings (second)
        tk.Label(cast_frame, text="Delay Before Click:", anchor="w").grid(row=7, column=0, sticky="w", pady=2)
        self.delay_before_var = tk.DoubleVar(value=self.cast_settings["delay_before_click"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.delay_before_var, 
                   width=10, command=self._update_cast_settings).grid(row=7, column=1, pady=2)
        
        tk.Label(cast_frame, text="Hold Duration:", anchor="w").grid(row=8, column=0, sticky="w", pady=2)
        self.delay_hold_var = tk.DoubleVar(value=self.cast_settings["delay_hold_duration"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.delay_hold_var, 
                   width=10, command=self._update_cast_settings).grid(row=8, column=1, pady=2)
        
        tk.Label(cast_frame, text="Delay After Release:", anchor="w").grid(row=9, column=0, sticky="w", pady=2)
        self.delay_after_var = tk.DoubleVar(value=self.cast_settings["delay_after_release"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.delay_after_var, 
                   width=10, command=self._update_cast_settings).grid(row=9, column=1, pady=2)
        
        # Spacer
        tk.Label(cast_frame, text="", anchor="w").grid(row=10, column=0, pady=5)
        
        # After fish delay (third)
        tk.Label(cast_frame, text="After Fish Delay:", anchor="w").grid(row=11, column=0, sticky="w", pady=2)
        self.after_fish_delay_var = tk.DoubleVar(value=self.cast_settings["after_fish_delay"])
        tk.Spinbox(cast_frame, from_=0, to=10, increment=0.1, textvariable=self.after_fish_delay_var, 
                   width=10, command=self._update_cast_settings).grid(row=11, column=1, pady=2)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready", fg="blue", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)
    
    def _update_cast_settings(self):
        """Update cast settings from GUI values"""
        self.cast_settings["delay_before_click"] = self.delay_before_var.get()
        self.cast_settings["delay_hold_duration"] = self.delay_hold_var.get()
        self.cast_settings["delay_after_release"] = self.delay_after_var.get()
        self.cast_settings["anti_nuke"] = self.anti_nuke_var.get()
        self.cast_settings["anti_nuke_delay_before"] = self.anti_nuke_delay_before_var.get()
        self.cast_settings["anti_nuke_bag_slot"] = self.bag_slot_var.get()
        self.cast_settings["anti_nuke_delay_after_bag"] = self.delay_after_bag_var.get()
        self.cast_settings["anti_nuke_rod_slot"] = self.rod_slot_var.get()
        self.cast_settings["anti_nuke_delay_after_rod"] = self.delay_after_rod_var.get()
        self.cast_settings["after_fish_delay"] = self.after_fish_delay_var.get()
    
    def _start_rebind(self, key_name):
        """Start rebinding a hotkey"""
        self.rebinding_key = key_name
        self.status_label.config(text=f"Press a key to rebind {key_name.replace('_', ' ')}...", fg="orange")
    
    def _key_to_string(self, key):
        """Convert key object to string"""
        if hasattr(key, 'name'):
            return key.name.upper()
        elif hasattr(key, 'char') and key.char:
            return key.char.upper()
        else:
            return str(key).upper()
    
    def _on_key_press(self, key):
        """Handle global keyboard events"""
        # If rebinding, set the new key
        if self.rebinding_key:
            self.hotkeys[self.rebinding_key] = key
            
            # Update the corresponding label
            key_str = self._key_to_string(key)
            if self.rebinding_key == "start_stop":
                self.start_stop_label.config(text=key_str)
            elif self.rebinding_key == "change_area":
                self.change_area_label.config(text=key_str)
            elif self.rebinding_key == "exit":
                self.exit_label.config(text=key_str)
            
            self.status_label.config(text=f"{self.rebinding_key.replace('_', ' ')} rebound to {key_str}", fg="green")
            self.rebinding_key = None
            return
        
        # Check for hotkey presses
        try:
            if key == self.hotkeys["start_stop"]:
                self.root.after(0, self._toggle_bot)
            
            elif key == self.hotkeys["change_area"]:
                self.root.after(0, self._toggle_area_selector)
            
            elif key == self.hotkeys["exit"]:
                print("Exit pressed")
                self._on_closing()
        except:
            pass
    
    def _toggle_bot(self):
        """Start or stop the bot loop"""
        if self.bot_running:
            self._stop_bot()
        else:
            self._start_bot()
    
    def _start_bot(self):
        """Start the bot loop"""
        if not self.bot_running:
            self.bot_running = True
            self.bot_stop_event.clear()
            self.status_label.config(text="Running...", fg="green")
            print("[Bot] Starting...")
            
            # Initialize cameras
            self._init_cameras()
            
            self.bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
            self.bot_thread.start()
    
    def _stop_bot(self):
        """Stop the bot loop"""
        if self.bot_running:
            self.bot_running = False
            self.bot_stop_event.set()
            self.status_label.config(text="Stopped", fg="red")
            print("[Bot] Stopping...")
            
            # Release mouse if held
            if self.fish_state == "hold":
                try:
                    self._mouse_up()
                except:
                    pass
            
            if self.bot_thread:
                self.bot_thread.join(timeout=2)
            
            # Clean up cameras
            self._cleanup_cameras()
    
    def _init_cameras(self):
        """Initialize camera instances"""
        try:
            import dxcam
            
            print("[Camera] Initializing single shared camera...")
            
            # Create ONE shared camera instance for both regions
            # We'll use get_latest_frame() which works even if we only capture once
            self.shared_camera = dxcam.create(output_color="BGR")
            screen_width = self.shared_camera.width
            screen_height = self.shared_camera.height
            
            print(f"[Camera] Detected DXCam output resolution: {screen_width}x{screen_height}")
            
            # Store the box coordinates for later cropping
            self.friend_box_tuple = (
                max(0, min(self.friend_box["x1"], screen_width - 1)),
                max(0, min(self.friend_box["y1"], screen_height - 1)),
                max(0, min(self.friend_box["x2"], screen_width)),
                max(0, min(self.friend_box["y2"], screen_height))
            )
            
            self.fish_box_tuple = (
                max(0, min(self.fish_box["x1"], screen_width - 1)),
                max(0, min(self.fish_box["y1"], screen_height - 1)),
                max(0, min(self.fish_box["x2"], screen_width)),
                max(0, min(self.fish_box["y2"], screen_height))
            )
            
            print(f"[Camera] Friend box: {self.friend_box_tuple}")
            print(f"[Camera] Fish box: {self.fish_box_tuple}")
            
            # Start capturing the full screen
            self.shared_camera.start(target_fps=120)
            
            # Set camera references (both point to the same camera)
            self.friend_camera = self.shared_camera
            self.fish_camera = self.shared_camera
            
            print("[Camera] Camera initialized successfully")
        except Exception as e:
            print(f"[Camera] Error initializing cameras: {e}")
            import traceback
            traceback.print_exc()
    
    def _cleanup_cameras(self):
        """Clean up camera instances"""
        try:
            if hasattr(self, 'shared_camera') and self.shared_camera:
                self.shared_camera.stop()
                del self.shared_camera
                self.shared_camera = None
            self.friend_camera = None
            self.fish_camera = None
            print("[Camera] Camera cleaned up")
        except Exception as e:
            print(f"[Camera] Error cleaning up cameras: {e}")
    
    def _get_friend_frame(self):
        """Get the friend box region from the full screen capture"""
        if not self.shared_camera:
            return None
        full_frame = self.shared_camera.get_latest_frame()
        if full_frame is None:
            return None
        x1, y1, x2, y2 = self.friend_box_tuple
        return full_frame[y1:y2, x1:x2]
    
    def _get_fish_frame(self):
        """Get the fish box region from the full screen capture"""
        if not self.shared_camera:
            return None
        full_frame = self.shared_camera.get_latest_frame()
        if full_frame is None:
            return None
        x1, y1, x2, y2 = self.fish_box_tuple
        return full_frame[y1:y2, x1:x2]
    
    def _bot_loop(self):
        """Main bot loop - continuously casts"""
        try:
            while self.bot_running:
                print("\n[Bot] ========== Starting cast cycle ==========")
                
                # Execute anti-nuke and cast
                if self.cast_settings["anti_nuke"]:
                    self._execute_cast_anti_nuke()
                
                if not self.bot_running:
                    break
                    
                self._execute_cast_regular()
                
                if not self.bot_running:
                    break
                
                # Wait for friend color to disappear (5 second timeout)
                print("\n[Bot] Waiting for friend color to disappear...")
                friend_disappeared = self._wait_for_friend_disappear(timeout=5.0)
                
                if not self.bot_running:
                    break
                
                if not friend_disappeared:
                    print("[Bot] Friend color didn't disappear in 5 seconds - recasting")
                    continue
                
                # Friend disappeared, now do fish monitoring
                print("\n[Bot] Friend color disappeared - starting fish monitoring...")
                self._monitor_fish_until_friend_returns()
                
                if not self.bot_running:
                    break
                
                # Wait after fish delay
                after_fish_delay = self.cast_settings["after_fish_delay"]
                if after_fish_delay > 0:
                    print(f"[Bot] Waiting {after_fish_delay:.1f}s after fish (After Fish Delay)...")
                    time.sleep(after_fish_delay)
                    
                print("[Bot] ========== Cast cycle completed ==========\n")
        except Exception as e:
            print(f"[Bot] Error in bot loop: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.status_label.config(text="Error!", fg="red"))
    
    def _execute_cast(self):
        """Execute the full cast sequence"""
        self._wait_for_friend_color()
        
        if self.cast_settings["anti_nuke"]:
            self._execute_cast_anti_nuke()
        
        self._execute_cast_regular()
    
    def _monitor_fish_until_friend_returns(self):
        """Monitor fish box for white colors, hold/release mouse based on detection. Exit when friend color returns."""
        print("[Fish] Starting fish monitoring...")
        
        try:
            import numpy as np
            
            if not self.shared_camera:
                print("[Fish] ERROR: Camera not initialized")
                return
            
            # Use 0 tolerance for exact white pixel matching
            fish_colors_np = [np.array(color, dtype=np.uint8) for color in self.fish_colors]
            fish_tolerance = 0  # Changed to 0 tolerance
            
            friend_color_np = np.array(self.friend_color, dtype=np.uint8)
            friend_tolerance = self.friend_color_tolerance
            
            print(f"[Fish] Waiting for white to appear (0 tolerance)...")
            
            # Wait for white to appear before starting state machine
            white_appeared = False
            while self.bot_running and not white_appeared:
                # Check if friend color returned early
                friend_frame = self._get_friend_frame()
                if friend_frame is not None:
                    friend_color_found = np.any(
                        np.all(np.abs(friend_frame - friend_color_np) <= friend_tolerance, axis=-1)
                    )
                    if friend_color_found:
                        print("[Fish] Friend color detected before white appeared - ending")
                        return
                
                # Check for white pixels
                fish_frame = self._get_fish_frame()
                if fish_frame is not None:
                    for fish_color in fish_colors_np:
                        color_match = np.any(
                            np.all(np.abs(fish_frame - fish_color) <= fish_tolerance, axis=-1)
                        )
                        if color_match:
                            print(f"[Fish] White detected - starting state machine")
                            white_appeared = True
                            break
                
                time.sleep(1/120)
            
            # Initialize state machine after white is found
            self.fish_state = "release"  # Start in release state
            previous_white_state = True  # We just found white, so previous state is True
            
            while self.bot_running:
                # Check if friend color is back (exit monitoring)
                friend_frame = self._get_friend_frame()
                if friend_frame is not None:
                    friend_color_found = np.any(
                        np.all(np.abs(friend_frame - friend_color_np) <= friend_tolerance, axis=-1)
                    )
                    if friend_color_found:
                        print("[Fish] Friend color reappeared - exiting fish monitoring")
                        if self.fish_state == "hold":
                            self._mouse_up()
                            self.fish_state = "release"
                        break
                
                # Check fish box for white colors
                fish_frame = self._get_fish_frame()
                if fish_frame is not None:
                    # Check if white is currently found
                    white_found = False
                    for fish_color in fish_colors_np:
                        color_match = np.any(
                            np.all(np.abs(fish_frame - fish_color) <= fish_tolerance, axis=-1)
                        )
                        if color_match:
                            white_found = True
                            break
                    
                    # Only switch state on transition from "found" to "lost"
                    if previous_white_state and not white_found:
                        # Transition from white found to white lost
                        if self.fish_state == "release":
                            print(f"[Fish] White lost - switching to HOLD")
                            self.fish_state = "hold"
                            self._mouse_down()
                        elif self.fish_state == "hold":
                            print(f"[Fish] White lost again - switching to RELEASE")
                            self.fish_state = "release"
                            self._mouse_up()
                    
                    previous_white_state = white_found
                
                time.sleep(1/120)  # 120 fps monitoring
            
        except ImportError:
            print("[Fish] WARNING: dxcam not installed - skipping fish monitoring")
        except Exception as e:
            print(f"[Fish] ERROR during fish monitoring: {e}")
            import traceback
            traceback.print_exc()
    
    def _wait_for_friend_color(self):
        """Wait for friend color to appear before casting"""
        print("[Cast] Checking for friend color before casting...")
        
        try:
            import numpy as np
            
            if not self.friend_camera or not self.fish_camera:
                print("[Cast] ERROR: Cameras not initialized")
                return
            
            friend_color = np.array(self.friend_color, dtype=np.uint8)
            friend_tolerance = self.friend_color_tolerance
            
            fish_colors_np = [np.array(color, dtype=np.uint8) for color in self.fish_colors]
            fish_tolerance = self.fish_color_tolerance
            
            print(f"[Cast] Waiting for friend color RGB{tuple(friend_color)} with tolerance {friend_tolerance}...")
            print(f"[Cast] Also monitoring fish box during wait...")
            
            self.fish_state = "release"
            
            while self.bot_running:
                # Check for friend color
                friend_frame = self.friend_camera.get_latest_frame()
                if friend_frame is not None:
                    friend_color_found = np.any(
                        np.all(np.abs(friend_frame - friend_color) <= friend_tolerance, axis=-1)
                    )
                    
                    if friend_color_found:
                        print("[Cast] Friend color detected - proceeding with cast")
                        if self.fish_state == "hold":
                            self._mouse_up()
                            self.fish_state = "release"
                        break
                
                # Monitor fish box while waiting
                fish_frame = self.fish_camera.get_latest_frame()
                if fish_frame is not None:
                    fish_found = False
                    
                    for fish_color in fish_colors_np:
                        color_match = np.any(
                            np.all(np.abs(fish_frame - fish_color) <= fish_tolerance, axis=-1)
                        )
                        if color_match:
                            fish_found = True
                            break
                    
                    # State machine logic
                    if self.fish_state == "release":
                        if not fish_found:
                            print("[Cast Wait] Fish disappeared - switching to HOLD state")
                            self.fish_state = "hold"
                            self._mouse_down()
                    
                    elif self.fish_state == "hold":
                        if fish_found:
                            print("[Cast Wait] Fish reappeared - switching to RELEASE state")
                            self.fish_state = "release"
                            self._mouse_up()
                
                time.sleep(0.01)
            
        except ImportError:
            print("[Cast] WARNING: dxcam not installed - skipping friend color check")
        except Exception as e:
            print(f"[Cast] ERROR during friend color check: {e}")
            import traceback
            traceback.print_exc()
    
    def _execute_cast_anti_nuke(self):
        """Execute anti-nuke sequence"""
        if not self.bot_running:
            return
            
        print("[Cast] Anti Nuke is enabled - Executing Anti Nuke sequence")
        
        delay_before = self.cast_settings["anti_nuke_delay_before"]
        bag_slot = self.cast_settings["anti_nuke_bag_slot"]
        delay_after_bag = self.cast_settings["anti_nuke_delay_after_bag"]
        rod_slot = self.cast_settings["anti_nuke_rod_slot"]
        delay_after_rod = self.cast_settings["anti_nuke_delay_after_rod"]
        
        if delay_before > 0:
            print(f"[Cast] Anti Nuke: Waiting {delay_before:.1f}s before selecting bag")
            time.sleep(delay_before)
        
        if not self.bot_running:
            return
        print(f"[Cast] Anti Nuke: Pressing key '{bag_slot}' (Bag slot)")
        self._press_key(str(bag_slot))
        
        if delay_after_bag > 0:
            print(f"[Cast] Anti Nuke: Waiting {delay_after_bag:.1f}s after bag selection")
            time.sleep(delay_after_bag)
        
        if not self.bot_running:
            return
        print(f"[Cast] Anti Nuke: Pressing key '{rod_slot}' (Rod slot)")
        self._press_key(str(rod_slot))
        
        if delay_after_rod > 0:
            print(f"[Cast] Anti Nuke: Waiting {delay_after_rod:.1f}s after rod selection")
            time.sleep(delay_after_rod)
        
        print("[Cast] Anti Nuke sequence completed")
    
    def _execute_cast_regular(self):
        """Execute regular cast sequence"""
        if not self.bot_running:
            return
            
        print("[Cast] Executing regular cast sequence")
        
        delay_before = self.cast_settings["delay_before_click"]
        delay_hold = self.cast_settings["delay_hold_duration"]
        delay_after = self.cast_settings["delay_after_release"]
        
        if delay_before > 0:
            print(f"[Cast] Waiting {delay_before:.1f}s before clicking")
            time.sleep(delay_before)
        
        if not self.bot_running:
            return
        print("[Cast] Holding left mouse button")
        self._mouse_down()
        
        if delay_hold > 0:
            print(f"[Cast] Holding for {delay_hold:.1f}s")
            time.sleep(delay_hold)
        
        if not self.bot_running:
            return
        print("[Cast] Releasing left mouse button")
        self._mouse_up()
        
        if delay_after > 0:
            print(f"[Cast] Waiting {delay_after:.1f}s after release")
            time.sleep(delay_after)
        
        print("[Cast] Cast sequence completed")
    
    def _wait_for_friend_disappear(self, timeout=5.0):
        """Wait for friend color to disappear with timeout. Returns True if disappeared, False if timeout"""
        try:
            import numpy as np
            
            if not self.friend_camera:
                print("[Wait] ERROR: Friend camera not initialized")
                return False
            
            friend_color = np.array(self.friend_color, dtype=np.uint8)
            friend_tolerance = self.friend_color_tolerance
            
            print(f"[Wait] Looking for friend color RGB{tuple(friend_color)} to disappear (tolerance {friend_tolerance})")
            
            start_time = time.time()
            frame_count = 0
            none_count = 0
            
            while self.bot_running and (time.time() - start_time) < timeout:
                friend_frame = self._get_friend_frame()
                frame_count += 1
                
                if friend_frame is not None:
                    friend_color_found = np.any(
                        np.all(np.abs(friend_frame - friend_color) <= friend_tolerance, axis=-1)
                    )
                    
                    if not friend_color_found:
                        print(f"[Wait] Friend color disappeared! (checked {frame_count} frames)")
                        return True
                else:
                    none_count += 1
                    if none_count % 20 == 0:
                        print(f"[Wait] Warning: {none_count} frames returned None")
                
                time.sleep(0.05)
            
            elapsed = time.time() - start_time
            print(f"[Wait] Timeout reached ({elapsed:.1f}s) - friend color still present (checked {frame_count} frames, {none_count} were None)")
            return False
            
        except Exception as e:
            print(f"[Wait] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _press_key(self, key_char):
        """Press a keyboard key"""
        from pynput.keyboard import Controller
        keyboard_controller = Controller()
        
        try:
            keyboard_controller.press(key_char)
            keyboard_controller.release(key_char)
            print(f"[Input] Key '{key_char}' pressed and released")
        except Exception as e:
            print(f"[Input] Error pressing key '{key_char}': {e}")
    
    def _mouse_down(self):
        """Press left mouse button"""
        from pynput.mouse import Controller, Button
        mouse_controller = Controller()
        
        try:
            mouse_controller.press(Button.left)
            print("[Input] Left mouse button pressed")
            time.sleep(0.005)
        except Exception as e:
            print(f"[Input] Error pressing mouse button: {e}")
    
    def _mouse_up(self):
        """Release left mouse button"""
        from pynput.mouse import Controller, Button
        mouse_controller = Controller()
        
        try:
            mouse_controller.release(Button.left)
            print("[Input] Left mouse button released")
            time.sleep(0.005)
        except Exception as e:
            print(f"[Input] Error releasing mouse button: {e}")
    
    def _toggle_area_selector(self):
        """Toggle the area selector on/off"""
        if self.area_selector is not None:
            self._save_and_close_area_selector()
        else:
            self._open_area_selector()
    
    def _open_area_selector(self):
        """Open the area selector window"""
        try:
            # Minimize main window
            self.root.iconify()
            self.root.after(200, self._create_area_selector)
        except Exception as e:
            print(f"Error opening area selector: {e}")
    
    def _create_area_selector(self):
        """Create the area selector after minimizing"""
        try:
            screenshot = ImageGrab.grab()
            self.area_selector = AreaSelector(
                self.root,
                screenshot,
                self.friend_box,
                self.fish_box
            )
            print("Area selector opened - Use mouse to adjust boxes, press F1 again to save and close")
        except Exception as e:
            print(f"Error creating area selector: {e}")
    
    def _save_and_close_area_selector(self):
        """Save the selected areas and close the selector"""
        if self.area_selector is not None:
            try:
                self.friend_box = self.area_selector.friend_box.copy()
                self.fish_box = self.area_selector.fish_box.copy()
                
                self.area_selector.window.destroy()
                self.area_selector = None
                
                print("Areas saved and closed!")
                print(f"FriendBox: {self.friend_box}")
                print(f"FishBox: {self.fish_box}")
                
                # Save settings immediately
                self._save_settings()
                
                # Restore main window
                self.root.deiconify()
                self.root.lift()
                self.status_label.config(text="Areas saved!", fg="green")
            except Exception as e:
                print(f"Error saving areas: {e}")
                self.area_selector = None
                self.root.deiconify()
    
    def _on_closing(self):
        """Clean up and close the application"""
        if self.bot_running:
            self._stop_bot()
        
        # Save settings before closing
        self._save_settings()
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.root.destroy()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


class AreaSelector:
    """Fullscreen area selector for friend_box and fish_box"""
    def __init__(self, parent, screenshot, friend_box, fish_box):
        self.screenshot = screenshot
        
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.configure(cursor='cross')
        
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        self.photo = ImageTk.PhotoImage(screenshot)
        
        self.canvas = tk.Canvas(self.window, width=self.screen_width, height=self.screen_height, highlightthickness=0)
        self.canvas.pack()
        
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        
        # Box data
        self.friend_box = friend_box.copy()
        self.fish_box = fish_box.copy()
        
        self.boxes = {
            'friend': {'coords': self.friend_box, 'color': '#00ff00', 'name': 'FriendBox'},
            'fish': {'coords': self.fish_box, 'color': '#0000ff', 'name': 'FishBox'}
        }
        
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
        self.resize_threshold = 10
        
        self.rects = {}
        self.labels = {}
        self.handles = {}
        
        for box_id in self.boxes.keys():
            self.create_box(box_id)
        
        # Zoom window
        self.zoom_window_size = 150
        self.zoom_factor = 4
        self.zoom_rect = None
        self.zoom_image_id = None
        self.zoom_photo = None
        
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
    
    def create_box(self, box_id):
        """Create a box with handles"""
        box_data = self.boxes[box_id]
        coords = box_data['coords']
        color = box_data['color']
        name = box_data['name']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=3,
            fill=color,
            stipple='gray50'
        )
        self.rects[box_id] = rect
        
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        label = self.canvas.create_text(
            label_x, label_y,
            text=name,
            font=("Arial", 14, "bold"),
            fill=color
        )
        self.labels[box_id] = label
        
        self.create_handles(box_id)
    
    def create_handles(self, box_id):
        """Create corner handles for a box"""
        handle_size = 12
        corner_marker_size = 3
        
        coords = self.boxes[box_id]['coords']
        color = self.boxes[box_id]['color']
        
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        if box_id in self.handles:
            for handle in self.handles[box_id]:
                self.canvas.delete(handle)
        
        self.handles[box_id] = []
        
        corners = [(x1, y1, 'nw'), (x2, y1, 'ne'), (x1, y2, 'sw'), (x2, y2, 'se')]
        
        for x, y, corner in corners:
            handle = self.canvas.create_rectangle(
                x - handle_size, y - handle_size,
                x + handle_size, y + handle_size,
                fill='',
                outline=color,
                width=2
            )
            self.handles[box_id].append(handle)
            
            marker = self.canvas.create_rectangle(
                x - corner_marker_size, y - corner_marker_size,
                x + corner_marker_size, y + corner_marker_size,
                fill='white',
                outline=color,
                width=1
            )
            self.handles[box_id].append(marker)
            
            line1 = self.canvas.create_line(x - handle_size, y, x + handle_size, y, fill='white', width=1)
            line2 = self.canvas.create_line(x, y - handle_size, x, y + handle_size, fill='white', width=1)
            self.handles[box_id].append(line1)
            self.handles[box_id].append(line2)
    
    def get_corner_at_position(self, x, y, box_id):
        """Check if mouse is near a corner"""
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        corners = {
            'nw': (x1, y1), 'ne': (x2, y1),
            'sw': (x1, y2), 'se': (x2, y2)
        }
        
        for corner, (cx, cy) in corners.items():
            if abs(x - cx) < self.resize_threshold and abs(y - cy) < self.resize_threshold:
                return corner
        return None
    
    def is_inside_box(self, x, y, box_id):
        """Check if mouse is inside a box"""
        coords = self.boxes[box_id]['coords']
        return coords['x1'] < x < coords['x2'] and coords['y1'] < y < coords['y2']
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = corner
                return
            
            if self.is_inside_box(event.x, event.y, box_id):
                self.dragging = True
                self.active_box = box_id
                self.drag_corner = 'move'
                return
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.dragging or not self.active_box:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        coords = self.boxes[self.active_box]['coords']
        
        if self.drag_corner == 'move':
            coords['x1'] += dx
            coords['y1'] += dy
            coords['x2'] += dx
            coords['y2'] += dy
        else:
            if self.drag_corner == 'nw':
                coords['x1'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'ne':
                coords['x2'] = event.x
                coords['y1'] = event.y
            elif self.drag_corner == 'sw':
                coords['x1'] = event.x
                coords['y2'] = event.y
            elif self.drag_corner == 'se':
                coords['x2'] = event.x
                coords['y2'] = event.y
            
            if coords['x1'] > coords['x2']:
                coords['x1'], coords['x2'] = coords['x2'], coords['x1']
            if coords['y1'] > coords['y2']:
                coords['y1'], coords['y2'] = coords['y2'], coords['y1']
        
        self.update_box(self.active_box)
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.show_zoom(event.x, event.y)
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.dragging = False
        self.active_box = None
        self.drag_corner = None
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        cursor = 'cross'
        
        for box_id in self.boxes.keys():
            corner = self.get_corner_at_position(event.x, event.y, box_id)
            if corner:
                cursor_map = {
                    'nw': 'size_nw_se', 'ne': 'size_ne_sw',
                    'sw': 'size_ne_sw', 'se': 'size_nw_se'
                }
                cursor = cursor_map[corner]
                break
            elif self.is_inside_box(event.x, event.y, box_id):
                cursor = 'fleur'
                break
        
        self.window.configure(cursor=cursor)
        self.show_zoom(event.x, event.y)
    
    def update_box(self, box_id):
        """Update box position and handles"""
        coords = self.boxes[box_id]['coords']
        x1, y1, x2, y2 = coords['x1'], coords['y1'], coords['x2'], coords['y2']
        
        self.canvas.coords(self.rects[box_id], x1, y1, x2, y2)
        
        label_x = x1 + (x2 - x1) // 2
        label_y = y1 - 20
        self.canvas.coords(self.labels[box_id], label_x, label_y)
        
        self.create_handles(box_id)
    
    def show_zoom(self, x, y):
        """Show zoom window at mouse position"""
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


def check_settings_and_show_terms():
    """Check for DreamSettings.txt and show Terms of Use if needed"""
    # Handle PyInstaller's temp folder
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    settings_path = os.path.join(script_dir, "DreamSettings.txt")
    
    # If settings exist, we're good to go
    if os.path.exists(settings_path):
        print(f"Settings found: {settings_path}")
        return True
    
    # Settings don't exist - show Terms of Use
    print("DreamSettings.txt not found. Showing Terms of Use...")
    
    # Create a simple root window for the dialog
    terms_root = tk.Tk()
    terms_root.withdraw()
    
    # Create the dialog
    dialog = tk.Toplevel(terms_root)
    dialog.title("Dreambreaker - Terms of Use")
    dialog.geometry("800x700")
    dialog.resizable(True, True)
    
    # Center the dialog
    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - 800) // 2
    y = (screen_height - 700) // 2
    dialog.geometry(f"800x700+{x}+{y}")
    
    # Make dialog modal
    dialog.transient(terms_root)
    dialog.grab_set()
    
    # Result variable
    accepted = [False]
    
    def close_dialog(accept_status):
        """Helper to properly close the dialog"""
        accepted[0] = accept_status
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
    
    # Title
    title_label = tk.Label(dialog, text="Dreambreaker - Terms of Use", font=("Arial", 18, "bold"))
    title_label.pack(pady=15)
    
    # Terms text (scrollable)
    text_frame = tk.Frame(dialog)
    text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    
    terms_text = tk.Text(text_frame, wrap="word", font=("Consolas", 11), yscrollcommand=scrollbar.set)
    terms_text.pack(fill="both", expand=True)
    scrollbar.config(command=terms_text.yview)
    
    # Terms content
    terms_content = """═══════════════════════════════════════════════════════════════════════
                    DREAMBREAKER - TERMS OF USE
                          by AsphaltCake
═══════════════════════════════════════════════════════════════════════

By using DREAMBREAKER, you agree to the following terms and conditions.


1. USAGE RIGHTS
───────────────────────────────────────────────────────────────────────

YOU ARE ALLOWED TO:
  • Use DREAMBREAKER for personal purposes
  • Study and reverse engineer the code for educational purposes
  • Modify the code for your own personal use
  • Share your modifications with proper attribution

YOU ARE NOT ALLOWED TO:
  • Repackage or redistribute this software as your own
  • Remove or modify credits to the original author (AsphaltCake)
  • Sell or monetize this software or its derivatives
  • Claim ownership of the original codebase

IF YOU SHARE MODIFICATIONS:
  • You MUST credit AsphaltCake as the original author
  • You MUST link to the original source (YouTube channel)
  • You MUST clearly indicate what changes you made
  • You may NOT claim the entire work as your own creation


2. INTENDED USE & GAME COMPLIANCE
───────────────────────────────────────────────────────────────────────

  • This software is designed for ROBLOX FISCH
  
  • You are responsible for ensuring your use complies with the game's 
    Terms of Service and any applicable rules
    
  • The author is NOT responsible for any account actions (bans, 
    suspensions) resulting from your use of this software
    
  • Use at your own risk - automation is allowed by the game rules


3. YOUTUBE CHANNEL SUBSCRIPTION
───────────────────────────────────────────────────────────────────────

By using DREAMBREAKER, you agree that:
  • This software will automatically subscribe to my YouTube channel
  • This is a form of support for the free software you're receiving
  • You are encouraged (but not required) to support the channel
  • YouTube Channel: https://www.youtube.com/@AsphaltCake


4. LIABILITY DISCLAIMER
───────────────────────────────────────────────────────────────────────

  • The author is NOT liable for any damages or account issues
  
  • No guarantee of functionality, compatibility, or performance
  
  • Use of this software is entirely at your own risk


5. PRIVACY & DATA COLLECTION
───────────────────────────────────────────────────────────────────────

  • This software stores configuration data locally on your device
  
  • No personal data is collected or transmitted to external servers
  
  • Your settings and preferences are stored in a local config file only


6. CREDITS & ATTRIBUTION
───────────────────────────────────────────────────────────────────────

Original Author: AsphaltCake
YouTube: https://www.youtube.com/@AsphaltCake
Discord: https://discord.gg/vKVBbyfHTD

If you share, modify, or redistribute this software:
  • REQUIRED: Credit "AsphaltCake" as the original creator
  • REQUIRED: Link to the original source
  • REQUIRED: Indicate any changes you made
  • FORBIDDEN: Claim the entire work as your own


7. TERMS UPDATES
───────────────────────────────────────────────────────────────────────

  • These terms may be updated at any time
  
  • Continued use of the software constitutes acceptance of updated terms


8. ACCEPTANCE
───────────────────────────────────────────────────────────────────────

By clicking "Accept" below, you acknowledge that you have read, 
understood, and agree to these Terms of Use.

If you do not agree to these terms, click "Decline" and do not use 
this software.


═══════════════════════════════════════════════════════════════════════
                  Thank you for using DREAMBREAKER!
═══════════════════════════════════════════════════════════════════════
"""
    
    terms_text.insert("1.0", terms_content)
    terms_text.configure(state="disabled")
    
    # Bottom frame with checkbox and buttons
    bottom_frame = tk.Frame(dialog)
    bottom_frame.pack(pady=15, padx=20)
    
    # Checkbox
    agree_var = tk.BooleanVar()
    agree_checkbox = tk.Checkbutton(bottom_frame, text="I have read and agree to the Terms of Use", 
                                   variable=agree_var, font=("Arial", 13))
    agree_checkbox.pack(pady=8)
    
    # Buttons frame
    button_frame = tk.Frame(bottom_frame)
    button_frame.pack(pady=8)
    
    def on_accept():
        if agree_var.get():
            close_dialog(True)
        else:
            tk.messagebox.showwarning("Terms Required", 
                                     "Please check the box to accept the Terms of Use.",
                                     parent=dialog)
    
    def on_decline():
        close_dialog(False)
    
    accept_button = tk.Button(button_frame, text="Accept", width=20, height=2, command=on_accept,
                             bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    accept_button.pack(side="left", padx=10)
    
    decline_button = tk.Button(button_frame, text="Decline", width=20, height=2, command=on_decline,
                              bg="#f44336", fg="white", font=("Arial", 12, "bold"))
    decline_button.pack(side="left", padx=10)
    
    # Handle window close (X button) - treat as decline
    dialog.protocol("WM_DELETE_WINDOW", on_decline)
    
    # Make sure dialog is visible before waiting
    dialog.deiconify()
    dialog.update()
    
    # Wait for dialog to be closed
    terms_root.wait_window(dialog)
    
    # Clean up root
    try:
        terms_root.destroy()
    except:
        pass
    
    if accepted[0]:
        print("Terms accepted. Creating settings file...")
        
        # Auto-subscribe to YouTube
        try:
            print("Opening YouTube channel for auto-subscribe...")
            webbrowser.open("https://www.youtube.com/@AsphaltCake/?sub_confirmation=1")
            time.sleep(3)
            
            # Try to press Tab and Enter to auto-subscribe
            try:
                pyautogui.press('tab')
                time.sleep(0.2)
                pyautogui.press('tab')
                time.sleep(0.2)
                pyautogui.press('enter')
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'w')  # Close tab
            except:
                pass  # If automation fails, user can manually subscribe
        except:
            pass
        
        # Create default settings with scaled coordinates
        # Get screen resolution for scaling
        temp_root = tk.Tk()
        screen_width = temp_root.winfo_screenwidth()
        screen_height = temp_root.winfo_screenheight()
        temp_root.destroy()
        
        # Scale from 2560x1440 reference
        ref_width = 2560
        ref_height = 1440
        
        friend_box_scaled = {
            "x1": int(39 * screen_width / ref_width),
            "y1": int(1329 * screen_height / ref_height),
            "x2": int(95 * screen_width / ref_width),
            "y2": int(1382 * screen_height / ref_height)
        }
        
        fish_box_scaled = {
            "x1": int(764 * screen_width / ref_width),
            "y1": int(1217 * screen_height / ref_height),
            "x2": int(1795 * screen_width / ref_width),
            "y2": int(1256 * screen_height / ref_height)
        }
        
        default_settings = {
            "terms_accepted": True,
            "friend_box": friend_box_scaled,
            "fish_box": fish_box_scaled,
            "cast_settings": {
                "delay_before_click": 0.0,
                "delay_hold_duration": 0.5,
                "delay_after_release": 0.5,
                "anti_nuke": False,
                "anti_nuke_delay_before": 0.0,
                "anti_nuke_bag_slot": 2,
                "anti_nuke_delay_after_bag": 0.5,
                "anti_nuke_rod_slot": 1,
                "anti_nuke_delay_after_rod": 0.5,
                "after_fish_delay": 1.0
            },
            "hotkeys": {
                "start_stop": "f3",
                "change_area": "f1",
                "exit": "f4"
            }
        }
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(default_settings, f, indent=2)
            print(f"Settings file created: {settings_path}")
        except Exception as e:
            print(f"Error creating settings file: {e}")
        
        return True
    else:
        print("Terms declined - exiting")
        return False


if __name__ == "__main__":
    print("Starting Dreambreaker...")
    
    # Check settings and show terms if needed
    if not check_settings_and_show_terms():
        print("Exiting - Terms not accepted")
        exit(0)
    
    # Launch main app
    app = DreambreakerGUI()
    app.run()
