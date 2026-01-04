import tkinter as tk
from tkinter import messagebox, simpledialog
import keyboard
import json
from pathlib import Path
import mss
from PIL import Image
import numpy as np
import ctypes
import win32api
import win32con
import win32gui
import cv2
import threading
import time
import random
import sys
import os
import webbrowser


class AreaSelector:
    """Transparent draggable and resizable area selector box"""
    
    def __init__(self, parent, initial_box, callback, title="Area"):
        self.callback = callback
        self.parent = parent
        self.title = title
        
        # Create transparent window
        self.window = tk.Toplevel(parent)
        self.window.attributes('-alpha', 0.6)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        
        # Set initial position and size
        self.x1, self.y1 = initial_box["x1"], initial_box["y1"]
        self.x2, self.y2 = initial_box["x2"], initial_box["y2"]
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        self.window.geometry(f"{width}x{height}+{self.x1}+{self.y1}")
        self.window.configure(bg='green')
        
        # Create canvas for border
        self.canvas = tk.Canvas(self.window, bg='green', highlightthickness=3, 
                               highlightbackground='lime')
        self.canvas.pack(fill='both', expand=True)
        
        # Mouse state
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        # Smaller resize threshold for small boxes
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        self.resize_threshold = min(10, width // 4, height // 4)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
    def on_mouse_move(self, event):
        """Change cursor based on position"""
        x, y = event.x, event.y
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Check if near edges for resizing
        at_left = x < self.resize_threshold
        at_right = x > width - self.resize_threshold
        at_top = y < self.resize_threshold
        at_bottom = y > height - self.resize_threshold
        
        if at_left and at_top:
            self.canvas.config(cursor='top_left_corner')
        elif at_right and at_top:
            self.canvas.config(cursor='top_right_corner')
        elif at_left and at_bottom:
            self.canvas.config(cursor='bottom_left_corner')
        elif at_right and at_bottom:
            self.canvas.config(cursor='bottom_right_corner')
        elif at_left or at_right:
            self.canvas.config(cursor='sb_h_double_arrow')
        elif at_top or at_bottom:
            self.canvas.config(cursor='sb_v_double_arrow')
        else:
            self.canvas.config(cursor='fleur')
    
    def on_mouse_down(self, event):
        """Start dragging or resizing"""
        self.start_x = event.x
        self.start_y = event.y
        
        x, y = event.x, event.y
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Check if clicking near edges for resizing
        at_left = x < self.resize_threshold
        at_right = x > width - self.resize_threshold
        at_top = y < self.resize_threshold
        at_bottom = y > height - self.resize_threshold
        
        if at_left or at_right or at_top or at_bottom:
            self.resizing = True
            self.resize_edge = {
                'left': at_left,
                'right': at_right,
                'top': at_top,
                'bottom': at_bottom
            }
        else:
            self.dragging = True
    
    def on_mouse_drag(self, event):
        """Handle dragging or resizing"""
        if self.dragging:
            # Move window
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            
            new_x = self.window.winfo_x() + dx
            new_y = self.window.winfo_y() + dy
            
            self.window.geometry(f"+{new_x}+{new_y}")
            
        elif self.resizing:
            # Resize window
            current_x = self.window.winfo_x()
            current_y = self.window.winfo_y()
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            
            new_x = current_x
            new_y = current_y
            new_width = current_width
            new_height = current_height
            
            if self.resize_edge['left']:
                dx = event.x - self.start_x
                new_x = current_x + dx
                new_width = current_width - dx
            elif self.resize_edge['right']:
                new_width = event.x
            
            if self.resize_edge['top']:
                dy = event.y - self.start_y
                new_y = current_y + dy
                new_height = current_height - dy
            elif self.resize_edge['bottom']:
                new_height = event.y
            
            # Minimum size
            if new_width < 50:
                new_width = 50
                new_x = current_x
            if new_height < 50:
                new_height = 50
                new_y = current_y
            
            self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    
    def on_mouse_up(self, event):
        """Stop dragging or resizing"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
    
    def get_coordinates(self):
        """Get current coordinates"""
        x1 = self.window.winfo_x()
        y1 = self.window.winfo_y()
        x2 = x1 + self.window.winfo_width()
        y2 = y1 + self.window.winfo_height()
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    
    def close(self):
        """Close the area selector"""
        coords = self.get_coordinates()
        self.window.destroy()
        return coords


class SimpleForgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FORGE Macro 3 - By AsphaltCake")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Get base directory (works for both .py and .exe)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = Path(sys.executable).parent
        else:
            # Running as script
            base_dir = Path(__file__).parent
        
        # Settings file and ore images directory
        self.settings_file = base_dir / "AutoForgeSettings.json"
        self.ore_images_dir = base_dir / "OreImages"
        self.ore_images_dir.mkdir(exist_ok=True)
        
        # Get screen resolution and scale factors
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        self.reference_width = 2560
        self.reference_height = 1440
        self.scale_x = self.screen_width / self.reference_width
        self.scale_y = self.screen_height / self.reference_height
        
        # Default keybindings
        self.default_keybindings = {
            "start_stop": "F1",
            "change_area": "F2",
            "exit": "F3"
        }
        
        # Default area boxes (for 2560x1440 reference resolution)
        self.default_areas_reference = {
            "inventory": {"x1": 1876, "y1": 431, "x2": 2453, "y2": 1021},
            "fill": {"x1": 389, "y1": 472, "x2": 592, "y2": 992},
            "pour": {"x1": 2269, "y1": 240, "x2": 2405, "y2": 1204},
            "forge": {"x1": 403, "y1": 240, "x2": 2271, "y2": 1204}
        }
        
        # Scale default areas to current resolution
        self.default_areas = self.scale_areas(self.default_areas_reference)
        
        # Load settings
        self.keybindings, self.areas = self.load_settings()
        
        # Ore settings
        self.enabled_ores = self.load_enabled_ores()
        self.ore_amount = self.load_ore_amount()
        self.forge_click_distance_multiplier = self.load_forge_click_distance_multiplier()
        
        # Timing settings
        self.timing_settings = self.load_timing_settings()
        
        # Fast forge gamepass
        self.fast_forge_gamepass = self.load_fast_forge_gamepass()
        
        # Manual select ores
        self.manual_select_ores = self.load_manual_select_ores()
        
        # Save settings if this is first run (to create file with scaled defaults)
        if not self.settings_file.exists():
            self.save_settings()
        
        # Running state
        self.is_running = False
        self.rebinding = None  # Track which key is being rebound
        self.area_selectors = []  # Track active area selectors
        self.area_selection_active = False  # Track if area selection is active
        self.ore_selector = None  # Track ore selection window
        
        # Create GUI
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
    
    def scale_areas(self, areas):
        """Scale area coordinates based on current resolution"""
        if self.scale_x == 1.0 and self.scale_y == 1.0:
            return areas.copy()
        
        scaled_areas = {}
        for area_name, coords in areas.items():
            scaled_areas[area_name] = {
                "x1": int(coords["x1"] * self.scale_x),
                "y1": int(coords["y1"] * self.scale_y),
                "x2": int(coords["x2"] * self.scale_x),
                "y2": int(coords["y2"] * self.scale_y)
            }
        return scaled_areas
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    keybindings = settings.get("keybindings", self.default_keybindings)
                    areas = settings.get("areas", self.default_areas)
                    print(f"Settings loaded from {self.settings_file.name}")
                    return keybindings, areas
        except Exception as e:
            print(f"Could not load settings: {e}")
        
        return self.default_keybindings.copy(), self.default_areas.copy()
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            settings = {
                "keybindings": self.keybindings,
                "areas": self.areas,
                "enabled_ores": self.enabled_ores,
                "ore_amount": self.ore_amount,
                "forge_click_distance_multiplier": self.forge_click_distance_multiplier,
                "timing_settings": self.timing_settings,
                "fast_forge_gamepass": self.fast_forge_gamepass,
                "manual_select_ores": self.manual_select_ores
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Settings saved to {self.settings_file.name}")
            return True
        except Exception as e:
            print(f"Could not save settings: {e}")
            return False
    
    def load_enabled_ores(self):
        """Load enabled ores from settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("enabled_ores", {})
        except:
            pass
        return {}
    
    def load_ore_amount(self):
        """Load ore amount from settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("ore_amount", 3)
        except:
            pass
        return 3
    
    def load_forge_click_distance_multiplier(self):
        """Load forge click distance multiplier from settings (1.0 = 170px at 2560x1440)"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Support old 'forge_click_distance' for backward compatibility
                    if "forge_click_distance_multiplier" in settings:
                        return settings.get("forge_click_distance_multiplier", 1.0)
                    elif "forge_click_distance" in settings:
                        # Convert old px value to multiplier (old default was 150)
                        old_px = settings.get("forge_click_distance", 150)
                        return old_px / 170.0
        except:
            pass
        return 1.0
    
    def load_timing_settings(self):
        """Load timing settings from file"""
        defaults = {
            "ore_check_wait": 1.0,
            "pre_fill_wait": 4.0,
            "pre_pour_wait": 5.0,
            "pre_forge_wait": 2.5,
            "cycle_restart_wait": 5.0
        }
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("timing_settings", defaults)
        except:
            pass
        return defaults
    
    def load_fast_forge_gamepass(self):
        """Load fast forge gamepass setting"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("fast_forge_gamepass", False)
        except:
            pass
        return False
    
    def load_manual_select_ores(self):
        """Load manual select ores setting"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("manual_select_ores", False)
        except:
            pass
        return False
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Title
        title = tk.Label(self.root, text="FORGE Macro", font=("Arial", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=8, padx=20)
        
        # Configure grid weights for dynamic sizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        
        # Start/Stop button
        self.start_stop_label = tk.Label(self.root, text=f"Start/Stop: {self.keybindings['start_stop']}", 
                                          font=("Arial", 8), anchor="w")
        self.start_stop_label.grid(row=1, column=0, sticky="ew", padx=(20, 5), pady=2)
        tk.Button(self.root, text="Rebind", command=lambda: self.rebind_key("start_stop"), 
                 width=8, font=("Arial", 8)).grid(row=1, column=1, padx=(5, 20), pady=2)
        
        # Change Area button
        self.change_area_label = tk.Label(self.root, text=f"Change Area: {self.keybindings['change_area']}", 
                                           font=("Arial", 8), anchor="w")
        self.change_area_label.grid(row=2, column=0, sticky="ew", padx=(20, 5), pady=2)
        tk.Button(self.root, text="Rebind", command=lambda: self.rebind_key("change_area"), 
                 width=8, font=("Arial", 8)).grid(row=2, column=1, padx=(5, 20), pady=2)
        
        # Exit button
        self.exit_label = tk.Label(self.root, text=f"Exit: {self.keybindings['exit']}", 
                                    font=("Arial", 8), anchor="w")
        self.exit_label.grid(row=3, column=0, sticky="ew", padx=(20, 5), pady=2)
        tk.Button(self.root, text="Rebind", command=lambda: self.rebind_key("exit"), 
                 width=8, font=("Arial", 8)).grid(row=3, column=1, padx=(5, 20), pady=2)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Stopped", 
                                      font=("Arial", 9, "bold"), fg="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=8, padx=20)
        
        # Separator
        separator = tk.Frame(self.root, height=2, bd=1, relief="sunken")
        separator.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        
        # Ore Settings Section
        ore_title = tk.Label(self.root, text="Ore Settings", font=("Arial", 10, "bold"))
        ore_title.grid(row=6, column=0, columnspan=2, pady=(5, 3), padx=20)
        
        # Ore Amount setting
        ore_amount_frame = tk.Frame(self.root)
        ore_amount_frame.grid(row=7, column=0, columnspan=2, pady=2, padx=20)
        tk.Label(ore_amount_frame, text="Ore Amt:", font=("Arial", 8)).pack(side="left", padx=3)
        self.ore_amount_entry = tk.Entry(ore_amount_frame, width=6, font=("Arial", 8))
        self.ore_amount_entry.insert(0, str(self.ore_amount))
        self.ore_amount_entry.pack(side="left", padx=3)
        tk.Button(ore_amount_frame, text="Save", command=self.save_ore_amount, 
                 width=6, font=("Arial", 7)).pack(side="left", padx=3)
        
        # Forge Click Distance Multiplier setting
        forge_distance_frame = tk.Frame(self.root)
        forge_distance_frame.grid(row=8, column=0, columnspan=2, pady=2, padx=20)
        tk.Label(forge_distance_frame, text="Forge Dist Mult:", font=("Arial", 8)).pack(side="left", padx=3)
        self.forge_distance_entry = tk.Entry(forge_distance_frame, width=6, font=("Arial", 8))
        self.forge_distance_entry.insert(0, str(self.forge_click_distance_multiplier))
        self.forge_distance_entry.pack(side="left", padx=3)
        tk.Button(forge_distance_frame, text="Save", command=self.save_forge_distance, 
                 width=6, font=("Arial", 7)).pack(side="left", padx=3)
        
        # Fast Forge Gamepass checkbox
        fast_forge_frame = tk.Frame(self.root)
        fast_forge_frame.grid(row=9, column=0, columnspan=2, pady=2, padx=20)
        self.fast_forge_var = tk.BooleanVar(value=self.fast_forge_gamepass)
        tk.Checkbutton(fast_forge_frame, text="Fast Forge Gamepass", variable=self.fast_forge_var,
                      command=self.toggle_fast_forge_gamepass, font=("Arial", 8)).pack(side="left", padx=5)
        
        # Manual Select Ores checkbox
        self.manual_select_var = tk.BooleanVar(value=self.manual_select_ores)
        tk.Checkbutton(fast_forge_frame, text="Manual Select Ores", variable=self.manual_select_var,
                      command=self.toggle_manual_select_ores, font=("Arial", 8)).pack(side="left", padx=5)
        
        # Separator
        separator2 = tk.Frame(self.root, height=2, bd=1, relief="sunken")
        separator2.grid(row=10, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        
        # Add Ore Button
        tk.Button(self.root, text="Add Ore", command=self.add_ore, 
                 width=15, font=("Arial", 8)).grid(row=10, column=0, columnspan=2, pady=3, padx=20)
        
        # Ore list frame with scrollbar
        self.ore_list_frame = tk.Frame(self.root)
        self.ore_list_frame.grid(row=11, column=0, columnspan=2, pady=3, padx=20, sticky="ew")
        
        self.ore_canvas = tk.Canvas(self.ore_list_frame, height=120)
        self.ore_scrollbar = tk.Scrollbar(self.ore_list_frame, orient="vertical", command=self.ore_canvas.yview)
        self.ore_inner_frame = tk.Frame(self.ore_canvas)
        
        self.ore_inner_frame.bind("<Configure>", lambda e: self.ore_canvas.configure(scrollregion=self.ore_canvas.bbox("all")))
        
        self.ore_canvas.create_window((0, 0), window=self.ore_inner_frame, anchor="nw")
        self.ore_canvas.configure(yscrollcommand=self.ore_scrollbar.set)
        
        self.ore_canvas.pack(side="left", fill="both", expand=True)
        self.ore_scrollbar.pack(side="right", fill="y")
        
        # Populate ore list
        self.refresh_ore_list()
        
        # Separator
        separator3 = tk.Frame(self.root, height=2, bd=1, relief="sunken")
        separator3.grid(row=13, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        
        # Timing Settings Section
        timing_title = tk.Label(self.root, text="Timing Settings (seconds)", font=("Arial", 10, "bold"))
        timing_title.grid(row=14, column=0, columnspan=2, pady=(5, 3), padx=20)
        
        # Timing entries in 2 columns within frames
        self.timing_entries = {}
        timing_configs = [
            ("ore_check_wait", "Ore check"),
            ("pre_fill_wait", "Pre-fill"),
            ("pre_pour_wait", "Pre-pour"),
            ("pre_forge_wait", "Pre-forge"),
            ("cycle_restart_wait", "Cycle restart")
        ]
        
        for idx, (key, label) in enumerate(timing_configs):
            row = 15 + idx
            
            frame = tk.Frame(self.root)
            frame.grid(row=row, column=0, columnspan=2, pady=1, padx=20, sticky="ew")
            
            tk.Label(frame, text=f"{label}:", font=("Arial", 8), width=12, anchor="w").pack(side="left", padx=(0, 3))
            entry = tk.Entry(frame, width=6, font=("Arial", 8))
            entry.insert(0, str(self.timing_settings[key]))
            entry.pack(side="left")
            self.timing_entries[key] = entry
        
        # Save Timing button
        tk.Button(self.root, text="Save Timing", command=self.save_timing_settings, 
                 width=15, font=("Arial", 8)).grid(row=20, column=0, columnspan=2, pady=5, padx=20)
        
        # Update window to fit content
        self.root.update_idletasks()
        self.root.geometry("")
    
    def setup_hotkeys(self):
        """Setup keyboard hotkeys"""
        try:
            keyboard.add_hotkey(self.keybindings['start_stop'], self.toggle_start_stop)
            keyboard.add_hotkey(self.keybindings['change_area'], self.change_area)
            keyboard.add_hotkey(self.keybindings['exit'], self.exit_app)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup hotkeys: {e}")
    
    def clear_hotkeys(self):
        """Clear all hotkeys"""
        try:
            keyboard.unhook_all_hotkeys()
        except:
            pass
    
    def toggle_start_stop(self):
        """Toggle start/stop"""
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running", fg="green")
            print("Macro started")
            # Minimize the GUI
            self.root.iconify()
            # Start macro in separate thread
            self.macro_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.macro_thread.start()
        else:
            self.status_label.config(text="Status: Stopped", fg="red")
            print("Macro stopped")
            # Restore the GUI
            self.root.deiconify()
    
    def change_area(self):
        """Toggle area selector boxes"""
        if self.area_selection_active:
            # Close selectors
            print("Change area triggered - closing selectors")
            self.close_area_selectors()
        else:
            # Open selectors
            print("Change area triggered - opening selectors")
            self.area_selection_active = True
            
            # Create area selectors for each area
            self.area_selectors = []
            
            inventory_selector = AreaSelector(self.root, self.areas["inventory"], 
                                             lambda coords: self.update_area("inventory", coords), 
                                             "Inventory")
            self.area_selectors.append(inventory_selector)
            
            fill_selector = AreaSelector(self.root, self.areas["fill"], 
                                        lambda coords: self.update_area("fill", coords), 
                                        "Fill")
            self.area_selectors.append(fill_selector)
            
            pour_selector = AreaSelector(self.root, self.areas["pour"], 
                                        lambda coords: self.update_area("pour", coords), 
                                        "Pour")
            self.area_selectors.append(pour_selector)
            
            forge_selector = AreaSelector(self.root, self.areas["forge"], 
                                         lambda coords: self.update_area("forge", coords), 
                                         "Forge")
            self.area_selectors.append(forge_selector)
    
    def update_area(self, area_name, coords):
        """Update area coordinates (called during dragging/resizing)"""
        self.areas[area_name] = coords
    
    def close_area_selectors(self):
        """Close all area selector windows"""
        for selector in self.area_selectors:
            try:
                coords = selector.get_coordinates()
                # Get the area name from the selector title
                area_name = selector.title.lower()
                self.areas[area_name] = coords
                print(f"{area_name} area saved: {coords}")
                selector.window.destroy()
            except:
                pass
        self.area_selectors = []
        self.area_selection_active = False
        
        # Save settings after closing selectors
        self.save_settings()
    
    def add_ore(self):
        """Start ore selection process"""
        if self.ore_selector:
            return  # Already selecting
        
        # Scaled size for current resolution
        scaled_width = int(80 * self.scale_x)
        scaled_height = int(35 * self.scale_y)
        
        # Create initial box in center of screen
        x1 = (self.screen_width - scaled_width) // 2
        y1 = (self.screen_height - scaled_height) // 2
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        
        initial_box = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        
        # Create selector
        self.ore_selector = AreaSelector(self.root, initial_box, 
                                         self.capture_ore_image, "Select Ore Area")
        
        # Create instruction window
        self.create_ore_instruction_window()
    
    def create_ore_instruction_window(self):
        """Create instruction window for ore selection"""
        self.ore_instruction_window = tk.Toplevel(self.root)
        self.ore_instruction_window.title("Ore Capture")
        self.ore_instruction_window.attributes('-topmost', True)
        self.ore_instruction_window.resizable(False, False)
        self.ore_instruction_window.configure(bg='white')
        
        # Make window more solid and visible
        frame = tk.Frame(self.ore_instruction_window, bg='white', relief='solid', borderwidth=2)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        tk.Button(frame, text="Capture", 
                 command=self.finish_ore_capture, 
                 width=20, height=2, font=("Arial", 12, "bold"),
                 bg='#4CAF50', fg='white', activebackground='#45a049',
                 relief='raised', borderwidth=3).pack(padx=30, pady=20)
    
    def finish_ore_capture(self):
        """Finish capturing the ore image"""
        if self.ore_selector:
            coords = self.ore_selector.get_coordinates()
            self.ore_selector.window.destroy()
            self.ore_selector = None
            
            # Close instruction window
            if hasattr(self, 'ore_instruction_window'):
                self.ore_instruction_window.destroy()
            
            # Capture image at coordinates
            self.capture_ore_image(coords)
    
    def capture_ore_image(self, coords):
        """Capture screenshot of ore area and save it"""
        # Ask for ore name
        ore_name = simpledialog.askstring("Ore Name", "Enter ore name:")
        
        if not ore_name:
            return
        
        # Clean up the name
        ore_name = ore_name.strip()
        
        # Capture screenshot
        try:
            with mss.mss() as sct:
                monitor = {
                    "top": coords["y1"],
                    "left": coords["x1"],
                    "width": coords["x2"] - coords["x1"],
                    "height": coords["y2"] - coords["y1"]
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Save image
                image_path = self.ore_images_dir / f"{ore_name}.png"
                img.save(image_path)
                
                # Enable by default
                self.enabled_ores[ore_name] = True
                self.save_settings()
                
                # Refresh ore list
                self.refresh_ore_list()
                
                print(f"Ore '{ore_name}' saved to {image_path}")
        except Exception as e:
            print(f"Error capturing ore image: {e}")
    
    def refresh_ore_list(self):
        """Refresh the list of ores"""
        # Clear existing widgets
        for widget in self.ore_inner_frame.winfo_children():
            widget.destroy()
        
        # Get all ore images
        ore_files = sorted(self.ore_images_dir.glob("*.png"))
        
        if not ore_files:
            label = tk.Label(self.ore_inner_frame, text="No ores added yet", 
                           font=("Arial", 9), fg="gray")
            label.pack(pady=10)
            return
        
        # Create checkbox for each ore
        for ore_file in ore_files:
            ore_name = ore_file.stem
            
            # Ensure ore is in enabled_ores dict
            if ore_name not in self.enabled_ores:
                self.enabled_ores[ore_name] = True
            
            frame = tk.Frame(self.ore_inner_frame)
            frame.pack(fill="x", pady=2)
            
            var = tk.BooleanVar(value=self.enabled_ores[ore_name])
            
            checkbox = tk.Checkbutton(frame, text=ore_name, variable=var,
                                     command=lambda n=ore_name, v=var: self.toggle_ore(n, v),
                                     font=("Arial", 9))
            checkbox.pack(side="left", padx=5)
            
            # Delete button
            delete_btn = tk.Button(frame, text="Delete", 
                                  command=lambda n=ore_name: self.delete_ore(n),
                                  width=8, font=("Arial", 8))
            delete_btn.pack(side="right", padx=5)
    
    def toggle_ore(self, ore_name, var):
        """Toggle ore enabled state"""
        self.enabled_ores[ore_name] = var.get()
        self.save_settings()
        print(f"Ore '{ore_name}' {'enabled' if var.get() else 'disabled'}")
    
    def delete_ore(self, ore_name):
        """Delete an ore image"""
        try:
            image_path = self.ore_images_dir / f"{ore_name}.png"
            if image_path.exists():
                image_path.unlink()
            
            if ore_name in self.enabled_ores:
                del self.enabled_ores[ore_name]
            
            self.save_settings()
            self.refresh_ore_list()
            print(f"Ore '{ore_name}' deleted")
        except Exception as e:
            print(f"Error deleting ore: {e}")
    
    def save_ore_amount(self):
        """Save the ore amount value"""
        try:
            amount = int(self.ore_amount_entry.get())
            if amount < 3:
                print("Error: Ore amount must be at least 3")
                self.ore_amount_entry.delete(0, tk.END)
                self.ore_amount_entry.insert(0, str(self.ore_amount))
                return
            self.ore_amount = amount
            self.save_settings()
            print(f"Ore amount set to {amount}")
        except ValueError:
            print("Error: Please enter a valid number")
            self.ore_amount_entry.delete(0, tk.END)
            self.ore_amount_entry.insert(0, str(self.ore_amount))
    
    def save_forge_distance(self):
        """Save the forge click distance multiplier (1.0 = 170px at reference resolution)"""
        try:
            multiplier = float(self.forge_distance_entry.get())
            if multiplier <= 0:
                print("Error: Forge distance multiplier must be positive")
                self.forge_distance_entry.delete(0, tk.END)
                self.forge_distance_entry.insert(0, str(self.forge_click_distance_multiplier))
                return
            self.forge_click_distance_multiplier = multiplier
            self.save_settings()
            base_px = int(170 * multiplier * self.scale_y)
            print(f"Forge distance multiplier set to {multiplier} ({base_px}px at current resolution)")
        except ValueError:
            print("Error: Please enter a valid number")
            self.forge_distance_entry.delete(0, tk.END)
            self.forge_distance_entry.insert(0, str(self.forge_click_distance_multiplier))
    
    def save_timing_settings(self):
        """Save all timing settings"""
        try:
            for key, entry in self.timing_entries.items():
                value = float(entry.get())
                if value < 0:
                    print(f"Error: {key} must be non-negative")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(self.timing_settings[key]))
                    return
                self.timing_settings[key] = value
            self.save_settings()
            print("Timing settings saved")
        except ValueError:
            print("Error: Please enter valid numbers for all timing settings")
    
    def toggle_fast_forge_gamepass(self):
        """Toggle fast forge gamepass setting"""
        self.fast_forge_gamepass = self.fast_forge_var.get()
        self.save_settings()
        print(f"Fast Forge Gamepass {'enabled' if self.fast_forge_gamepass else 'disabled'}")
    
    def toggle_manual_select_ores(self):
        """Toggle manual select ores setting"""
        self.manual_select_ores = self.manual_select_var.get()
        self.save_settings()
        print(f"Manual Select Ores {'enabled' if self.manual_select_ores else 'disabled'}")
    
    def focus_roblox(self):
        """Focus on Roblox window"""
        try:
            # Find Roblox window
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if "Roblox" in window_text:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                # Focus the first Roblox window found
                roblox_hwnd = windows[0]
                win32gui.SetForegroundWindow(roblox_hwnd)
                print("Focused on Roblox window")
                time.sleep(0.2)  # Give it time to focus
            else:
                print("Warning: Roblox window not found")
        except Exception as e:
            print(f"Error focusing Roblox: {e}")
    
    def main_loop(self):
        """Main macro loop - runs continuously until stopped"""
        # Focus on Roblox before starting
        self.focus_roblox()
        
        # Main loop - keep repeating until user stops
        while self.is_running:
            self.run_forge_cycle()
            
            # Check if still running after cycle
            if not self.is_running:
                break
                
            # Wait before restarting
            print(f"Waiting {self.timing_settings['cycle_restart_wait']} seconds before restarting cycle...")
            time.sleep(self.timing_settings['cycle_restart_wait'])
        
        # Clean up when stopped
        self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
        self.root.after(0, lambda: self.root.deiconify())
    
    def run_forge_cycle(self):
        """Run a single forge cycle"""
        print(f"\n=== Starting forge cycle - will collect {self.ore_amount} ores per attempt ===")
        
        # Check if Manual Select Ores is enabled - skip ore collection
        if self.manual_select_ores:
            print("Manual Select Ores enabled - skipping ore collection, going straight to forge button")
            
            # Click forge button at 1280, 1200
            scaled_x = int(1280 * self.scale_x)
            scaled_y = int(1200 * self.scale_y)
            
            win32api.SetCursorPos((scaled_x, scaled_y))
            time.sleep(0.005)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
            time.sleep(0.005)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.005)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            print("Clicked forge button - skipping ore check wait")
        else:
            # Get list of enabled ores (sequential, not random)
            enabled_ore_names = [name for name, enabled in self.enabled_ores.items() if enabled]
            
            if not enabled_ore_names:
                print("Error: No ores enabled!")
                self.is_running = False
                self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                return
            
            inventory_coords = self.areas["inventory"]
            monitor = {
                "top": inventory_coords["y1"],
                "left": inventory_coords["x1"],
                "width": inventory_coords["x2"] - inventory_coords["x1"],
                "height": inventory_coords["y2"] - inventory_coords["y1"]
            }
            
            with mss.mss() as sct:
                # Try each ore sequentially until one succeeds
                for ore_name in enabled_ore_names:
                    if not self.is_running:
                        print("Macro stopped by user")
                        self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                        self.root.after(0, lambda: self.root.deiconify())
                        return
                    
                    print(f"\n=== Attempting ore: {ore_name} ===")
                    
                    ore_img_path = self.ore_images_dir / f"{ore_name}.png"
                    if not ore_img_path.exists():
                        print(f"Ore image not found: {ore_name}")
                        continue
                    
                    # Load ore template
                    ore_template = cv2.imread(str(ore_img_path))
                    if ore_template is None:
                        print(f"Could not load ore template: {ore_name}")
                        continue
                    
                    # Collect ore_amount of this ore
                    collected = 0
                    while self.is_running and collected < self.ore_amount:
                        # Take screenshot of inventory
                        screenshot = sct.grab(monitor)
                        inventory_img = np.array(screenshot)
                        inventory_img = cv2.cvtColor(inventory_img, cv2.COLOR_BGRA2BGR)
                        
                        # Match template
                        result = cv2.matchTemplate(inventory_img, ore_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        
                        # Threshold for match
                        if max_val >= 0.8:
                            # Calculate center of found ore
                            ore_h, ore_w = ore_template.shape[:2]
                            center_x = inventory_coords["x1"] + max_loc[0] + ore_w // 2
                            center_y = inventory_coords["y1"] + max_loc[1] + ore_h // 2
                            
                            # Move cursor to ore
                            win32api.SetCursorPos((center_x, center_y))
                            time.sleep(0.005)
                            
                            # Roblox mouse register
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            time.sleep(0.005)
                            
                            # Click
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            time.sleep(0.005)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            
                            # Move mouse to bottom right of inventory to not block other ores
                            win32api.SetCursorPos((inventory_coords["x2"], inventory_coords["y2"]))
                            time.sleep(0.005)
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            
                            collected += 1
                            print(f"Collected {ore_name} ({collected}/{self.ore_amount})")
                            
                            time.sleep(0.005)
                        else:
                            print(f"Ore {ore_name} not found in inventory - cannot collect {self.ore_amount}")
                            break
                    
                    # Check if we collected the required amount
                    if collected < self.ore_amount:
                        print(f"Failed to collect {self.ore_amount} of {ore_name} - trying next ore")
                        continue
                    
                    # Check if stopped
                    if not self.is_running:
                        print("Macro stopped by user")
                        self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                        self.root.after(0, lambda: self.root.deiconify())
                        return
                    
                    print(f"Collected {collected} {ore_name} - clicking forge button")
                    
                    # Click forge button at 1280, 1200
                    scaled_x = int(1280 * self.scale_x)
                    scaled_y = int(1200 * self.scale_y)
                    
                    win32api.SetCursorPos((scaled_x, scaled_y))
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                    # Wait to check if ore was consumed
                    print(f"Waiting {self.timing_settings['ore_check_wait']} second(s) to check if ore was consumed...")
                    time.sleep(self.timing_settings['ore_check_wait'])
                    
                    # Check if ore still exists
                    screenshot = sct.grab(monitor)
                    inventory_img = np.array(screenshot)
                    inventory_img = cv2.cvtColor(inventory_img, cv2.COLOR_BGRA2BGR)
                    
                    result = cv2.matchTemplate(inventory_img, ore_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= 0.8:
                        # Ore still found - not enough to forge!
                        print(f"Ore {ore_name} still found after forge - not enough ore to complete!")
                        print(f"Disabling {ore_name} and trying next ore...")
                        
                        # Disable this ore permanently
                        self.enabled_ores[ore_name] = False
                        self.save_settings()
                        
                        # Continue to next ore
                        continue
                    else:
                        # Ore not found - success!
                        print(f"Ore {ore_name} consumed successfully - forging succeeded!")
                        
                        # Only wait before fill stage if NOT using Fast Forge Gamepass
                        if not self.fast_forge_gamepass:
                            print(f"Waiting {self.timing_settings['pre_fill_wait']} more seconds before fill stage...")
                            time.sleep(self.timing_settings['pre_fill_wait'])
                        
                        # Break out of ore loop and proceed to next stage
                        break
                else:
                    # All ores exhausted or disabled
                    print("All ores exhausted or disabled - no successful forge!")
                    self.is_running = False
                    self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                    self.root.after(0, lambda: self.root.deiconify())
                    self.root.after(0, lambda: messagebox.showinfo("All Ores Exhausted", "All ores failed to forge or were disabled!"))
                    return
        
        # Check if stopped
        if not self.is_running:
            print("Macro stopped by user")
            self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
            self.root.after(0, lambda: self.root.deiconify())
            return
        
        # Check if Fast Forge Gamepass is enabled
        if self.fast_forge_gamepass:
            print("Fast Forge Gamepass enabled - skipping Fill and Pour stages")
            print("Waiting 2.5 seconds before forge stage...")
            time.sleep(2.5)
        else:
            # Fill stage - search for green color (109, 174, 32)
            print("Starting fill stage - searching for green color...")
            self.fill_stage()
            
            # Check if stopped
            if not self.is_running:
                print("Macro stopped by user")
                self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                self.root.after(0, lambda: self.root.deiconify())
                return
            
            # Wait before pour stage
            print(f"Waiting {self.timing_settings['pre_pour_wait']} seconds before pour stage...")
            time.sleep(self.timing_settings['pre_pour_wait'])
            
            # Check if stopped
            if not self.is_running:
                print("Macro stopped by user")
                self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                self.root.after(0, lambda: self.root.deiconify())
                return
            
            # Pour stage
            print("Starting pour stage...")
            self.pour_stage()
            
            # Check if stopped
            if not self.is_running:
                print("Macro stopped by user")
                self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
                self.root.after(0, lambda: self.root.deiconify())
                return
            
            # Wait before forge stage
            print(f"Waiting {self.timing_settings['pre_forge_wait']} seconds before forge stage...")
            time.sleep(self.timing_settings['pre_forge_wait'])
        
        # Check if stopped
        if not self.is_running:
            print("Macro stopped by user")
            self.root.after(0, lambda: self.status_label.config(text="Status: Stopped", fg="red"))
            self.root.after(0, lambda: self.root.deiconify())
            return
        
        # Forge stage
        print("Starting forge stage...")
        self.forge_stage()
        
        print("=== Forge cycle complete ===")
        
        # If Manual Select Ores is enabled, stop after one cycle
        if self.manual_select_ores:
            print("Manual Select Ores enabled - stopping after one cycle")
            self.is_running = False
    
    def fill_stage(self):
        """Fill stage - alternate clicking top and bottom of fill area when green color found"""
        # Target color RGB (109, 174, 32)
        target_r, target_g, target_b = 109, 174, 32
        tolerance = 10
        click_top = True  # Alternate between top and bottom
        last_found_time = time.time()
        
        fill_coords = self.areas["fill"]
        top_middle_x = (fill_coords["x1"] + fill_coords["x2"]) // 2
        top_middle_y = fill_coords["y1"]
        bottom_middle_x = (fill_coords["x1"] + fill_coords["x2"]) // 2
        bottom_middle_y = fill_coords["y2"]
        
        with mss.mss() as sct:
            while self.is_running:
                # Take screenshot of fill area
                monitor = {
                    "top": fill_coords["y1"],
                    "left": fill_coords["x1"],
                    "width": fill_coords["x2"] - fill_coords["x1"],
                    "height": fill_coords["y2"] - fill_coords["y1"]
                }
                
                screenshot = sct.grab(monitor)
                # Convert to numpy array (BGRA format from mss)
                img_array = np.array(screenshot)
                
                # Create a mask where the color matches (Note: mss uses BGRA, so indices are [2]=R, [1]=G, [0]=B)
                mask = (np.abs(img_array[:, :, 2] - target_r) <= tolerance) & \
                       (np.abs(img_array[:, :, 1] - target_g) <= tolerance) & \
                       (np.abs(img_array[:, :, 0] - target_b) <= tolerance)
                
                # Check if color found
                color_found = np.any(mask)
                
                if color_found:
                    last_found_time = time.time()
                    print("Green color found in Fill area!")
                    
                    # Find first position of green
                    positions = np.argwhere(mask)
                    first_pos = positions[0]
                    
                    # Calculate screen coordinates of green
                    green_x = fill_coords["x1"] + first_pos[1]
                    green_y = fill_coords["y1"] + first_pos[0]
                    
                    # Move cursor to green position
                    win32api.SetCursorPos((green_x, green_y))
                    time.sleep(0.005)
                    
                    # Roblox mouse register
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.005)
                    
                    # Hold left click DOWN (don't release yet)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    print("Holding left click - alternating between top and bottom...")
                    
                    # Alternate between top and bottom until green disappears
                    at_top = True
                    while self.is_running:
                        # Check for green again
                        screenshot = sct.grab(monitor)
                        img_array = np.array(screenshot)
                        
                        mask = (np.abs(img_array[:, :, 2] - target_r) <= tolerance) & \
                               (np.abs(img_array[:, :, 1] - target_g) <= tolerance) & \
                               (np.abs(img_array[:, :, 0] - target_b) <= tolerance)
                        
                        # If green is gone, break
                        if not np.any(mask):
                            print("Green disappeared!")
                            break
                        
                        # Alternate between top and bottom
                        if at_top:
                            win32api.SetCursorPos((bottom_middle_x, bottom_middle_y))
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            at_top = False
                        else:
                            win32api.SetCursorPos((top_middle_x, top_middle_y))
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                            at_top = True
                        
                        time.sleep(0.005)
                    
                    # Release left click
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    print("Released click! Fill stage complete.")
                    return
                else:
                    # Check if color not found for 5 seconds
                    if time.time() - last_found_time >= 5:
                        print("Green color not found for 5 seconds - exiting fill stage")
                        break
                    
                    time.sleep(0.005)
    
    def pour_stage(self):
        """Pour stage - keep white color between top and bottom of yellow color"""
        # Target colors: Yellow (183, 164, 74) and White (207, 207, 207)
        yellow_r, yellow_g, yellow_b = 183, 164, 74
        white_r, white_g, white_b = 207, 207, 207
        yellow_tolerance = 10
        white_tolerance = 10
        
        pour_coords = self.areas["pour"]
        
        with mss.mss() as sct:
            monitor = {
                "top": pour_coords["y1"],
                "left": pour_coords["x1"],
                "width": pour_coords["x2"] - pour_coords["x1"],
                "height": pour_coords["y2"] - pour_coords["y1"]
            }
            
            # Wait for yellow to appear
            print("Waiting for yellow in Pour area...")
            yellow_found = False
            while self.is_running and not yellow_found:
                screenshot = sct.grab(monitor)
                img_array = np.array(screenshot)
                
                yellow_mask = (np.abs(img_array[:, :, 2] - yellow_r) <= yellow_tolerance) & \
                             (np.abs(img_array[:, :, 1] - yellow_g) <= yellow_tolerance) & \
                             (np.abs(img_array[:, :, 0] - yellow_b) <= yellow_tolerance)
                
                if np.any(yellow_mask):
                    print("Yellow found in Pour area!")
                    yellow_found = True
                    break
                
                time.sleep(0.005)
            
            if not self.is_running:
                return
            
            # Pour stage: keep white between top and bottom of yellow
            click_held = False
            print("Starting pour control - keeping white between yellow boundaries...")
            
            while self.is_running:
                screenshot = sct.grab(monitor)
                img_array = np.array(screenshot)
                
                # Check for yellow
                yellow_mask = (np.abs(img_array[:, :, 2] - yellow_r) <= yellow_tolerance) & \
                             (np.abs(img_array[:, :, 1] - yellow_g) <= yellow_tolerance) & \
                             (np.abs(img_array[:, :, 0] - yellow_b) <= yellow_tolerance)
                
                # If yellow disappeared, pour is complete
                if not np.any(yellow_mask):
                    print("Yellow disappeared! Pour stage complete.")
                    # Release click if held
                    if click_held:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    break
                
                # Find middle Y position of yellow
                yellow_positions = np.argwhere(yellow_mask)
                yellow_middle_y = int(np.mean(yellow_positions[:, 0]))
                
                # Check for white
                white_mask = (np.abs(img_array[:, :, 2] - white_r) <= white_tolerance) & \
                            (np.abs(img_array[:, :, 1] - white_g) <= white_tolerance) & \
                            (np.abs(img_array[:, :, 0] - white_b) <= white_tolerance)
                
                if np.any(white_mask):
                    # Find middle Y position of white
                    white_positions = np.argwhere(white_mask)
                    white_middle_y = int(np.mean(white_positions[:, 0]))
                    
                    # Compare Y coordinates
                    if white_middle_y > yellow_middle_y:
                        # White is below yellow - hold left click
                        if not click_held:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            click_held = True
                            print("Holding click - white below yellow")
                    else:
                        # White is above yellow - release left click
                        if click_held:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            click_held = False
                            print("Released click - white above yellow")
                
                time.sleep(0.005)
    
    def forge_stage(self):
        """Forge stage - flowing pattern clicks for 4 seconds, then watch for white circles"""
        # Pattern points (reference 2560x1440)
        print("Starting 4-second flowing pattern clicks...")
        
        # Pattern points (reference 2560x1440)
        pattern_points = [
            (1800, 900),
            (1600, 500),
            (1400, 900),
            (1200, 500),
            (1000, 900),
            (1200, 500),
            (1400, 900),
            (1600, 500),
            (1800, 900)
        ]
        
        # Scale pattern points to current resolution
        scaled_pattern = [
            (int(x * self.scale_x), int(y * self.scale_y))
            for x, y in pattern_points
        ]
        
        # Calculate time per point (4 seconds / 8 segments between 9 points)
        total_duration = 4.0
        num_segments = len(scaled_pattern) - 1
        time_per_segment = total_duration / num_segments
        
        start_time = time.time()
        current_point_index = 0
        
        while time.time() - start_time < total_duration and self.is_running:
            # Calculate progress through current segment
            elapsed = time.time() - start_time
            current_segment = int(elapsed / time_per_segment)
            
            if current_segment >= num_segments:
                current_segment = num_segments - 1
            
            # Get start and end points for current segment
            start_point = scaled_pattern[current_segment]
            end_point = scaled_pattern[current_segment + 1]
            
            # Calculate progress within this segment (0.0 to 1.0)
            segment_progress = (elapsed - (current_segment * time_per_segment)) / time_per_segment
            segment_progress = min(1.0, segment_progress)
            
            # Interpolate between start and end points
            current_x = int(start_point[0] + (end_point[0] - start_point[0]) * segment_progress)
            current_y = int(start_point[1] + (end_point[1] - start_point[1]) * segment_progress)
            
            # Move cursor and click
            win32api.SetCursorPos((current_x, current_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
            time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            time.sleep(0.01)  # Small delay between clicks for smooth movement
        
        print("Flowing pattern clicks complete!")
        
        if not self.is_running:
            return
        
        # Move cursor to bottom middle of forge area
        forge_coords = self.areas["forge"]
        bottom_middle_x = (forge_coords["x1"] + forge_coords["x2"]) // 2
        bottom_middle_y = forge_coords["y2"]
        win32api.SetCursorPos((bottom_middle_x, bottom_middle_y))
        time.sleep(0.005)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
        print(f"Cursor moved to bottom middle: ({bottom_middle_x}, {bottom_middle_y})")
        
        # Watch for white circles (255, 255, 255) with 15 second timeout
        print("Watching for white circles - 15 second countdown...")
        
        # Target white color RGB(255, 255, 255)
        white_r, white_g, white_b = 255, 255, 255
        white_tolerance = 10
        
        # Track when white detection state changes
        last_state_change_time = time.time()
        white_detected_last_frame = False
        
        # Track last distance to detect shrinking circles
        last_distance = None
        circle_exceeded_threshold = False  # Track if current circle ever exceeded threshold
        
        with mss.mss() as sct:
            monitor = {
                "top": forge_coords["y1"],
                "left": forge_coords["x1"],
                "width": forge_coords["x2"] - forge_coords["x1"],
                "height": forge_coords["y2"] - forge_coords["y1"]
            }
            
            while self.is_running:
                # Check if 5 seconds have passed without state change (stuck condition)
                if time.time() - last_state_change_time > 5:
                    print("No state change for 5 seconds (stuck) - searching for green (69, 200, 60)...")
                    
                    # Search for green RGB(69, 200, 60) with 0 tolerance
                    green_r, green_g, green_b = 69, 200, 60
                    green_tolerance = 0
                    
                    print("Searching for green color before final click...")
                    green_found = False
                    
                    while self.is_running and not green_found:
                        # Take screenshot of forge area
                        screenshot = sct.grab(monitor)
                        img_array = np.array(screenshot)
                        
                        # Check for green color (mss uses BGRA format)
                        green_mask = (img_array[:, :, 2] == green_r) & \
                                    (img_array[:, :, 1] == green_g) & \
                                    (img_array[:, :, 0] == green_b)
                        
                        if np.any(green_mask):
                            print("Green (69, 200, 60) found!")
                            green_found = True
                            break
                        
                        time.sleep(0.005)
                    
                    if not self.is_running:
                        return
                    
                    # Scale position to current resolution (reference 2560x1440)
                    scaled_x = int(1304 * self.scale_x)
                    scaled_y = int(1026 * self.scale_y)
                    
                    # Click at position
                    win32api.SetCursorPos((scaled_x, scaled_y))
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                    print(f"Clicked final position at ({scaled_x}, {scaled_y})")
                    break
                
                # Take screenshot of forge area
                screenshot = sct.grab(monitor)
                img_array = np.array(screenshot)
                
                # Check for white color (mss uses BGRA format, so [0]=B, [1]=G, [2]=R, [3]=A)
                # For white (255,255,255), all RGB channels should be within tolerance of 255
                # Ensure values are at least (255 - tolerance) to avoid matching dark colors
                white_mask = (img_array[:, :, 2] >= 255 - white_tolerance) & (img_array[:, :, 2] <= 255) & \
                            (img_array[:, :, 1] >= 255 - white_tolerance) & (img_array[:, :, 1] <= 255) & \
                            (img_array[:, :, 0] >= 255 - white_tolerance) & (img_array[:, :, 0] <= 255)
                
                if np.any(white_mask):
                    # White found - check if state changed
                    if not white_detected_last_frame:
                        # State changed from not detected to detected (new circle appeared)
                        last_state_change_time = time.time()
                        print("State change: White detected")
                        # Reset threshold flag for new circle
                        circle_exceeded_threshold = False
                    white_detected_last_frame = True
                    
                    # Get top and bottom Y coordinates (vertical positions)
                    white_positions = np.argwhere(white_mask)
                    min_y = white_positions[:, 0].min()  # Top (smallest Y)
                    max_y = white_positions[:, 0].max()  # Bottom (largest Y)
                    
                    # Get X coordinate at min_y and max_y positions
                    min_y_positions = white_positions[white_positions[:, 0] == min_y]
                    max_y_positions = white_positions[white_positions[:, 0] == max_y]
                    min_y_x = int(np.mean(min_y_positions[:, 1]))
                    max_y_x = int(np.mean(max_y_positions[:, 1]))
                    
                    # Debug: Show actual RGB values at detected positions (use first actual white pixel)
                    sample_pixel = img_array[min_y_positions[0][0], min_y_positions[0][1]]
                    actual_r = sample_pixel[2]
                    actual_g = sample_pixel[1]
                    actual_b = sample_pixel[0]
                    
                    # Calculate distance
                    distance = max_y - min_y
                    
                    # Convert to screen coordinates
                    top_x = forge_coords["x1"] + min_y_x
                    top_y = forge_coords["y1"] + min_y
                    bottom_x = forge_coords["x1"] + max_y_x
                    bottom_y = forge_coords["y1"] + max_y
                    
                    print(f"White detected - RGB({actual_r},{actual_g},{actual_b}) - Top Y: {top_y}, Bottom Y: {bottom_y}, Distance: {distance}px")
                    
                    # Calculate the forge click distance: base 170px * multiplier * resolution scale
                    scaled_click_distance = int(170 * self.forge_click_distance_multiplier * self.scale_y)
                    
                    # Check if circle has exceeded threshold (mark it for this circle's lifetime)
                    if distance > scaled_click_distance:
                        circle_exceeded_threshold = True
                    
                    # Check if circle is shrinking (to prevent clicking growing circles)
                    is_shrinking = False
                    if last_distance is not None and distance < last_distance:
                        is_shrinking = True
                    
                    # Update last distance
                    last_distance = distance
                    
                    # Only click if:
                    # 1. Distance is below threshold (but not 0)
                    # 2. Circle has exceeded threshold at some point in its lifetime
                    # 3. Circle is currently shrinking (not growing)
                    if distance > 0 and distance < scaled_click_distance and circle_exceeded_threshold and is_shrinking:
                        # Calculate center point
                        center_x = (top_x + bottom_x) // 2
                        center_y = (top_y + bottom_y) // 2
                        
                        # Move cursor to bottom middle of forge area first (to not block pixels)
                        bottom_middle_x = (forge_coords["x1"] + forge_coords["x2"]) // 2
                        bottom_middle_y = forge_coords["y2"]
                        win32api.SetCursorPos((bottom_middle_x, bottom_middle_y))
                        time.sleep(0.005)
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        time.sleep(0.005)
                        
                        # Move cursor to center
                        win32api.SetCursorPos((center_x, center_y))
                        time.sleep(0.005)
                        
                        # Roblox mouse register (anti-detection)
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        time.sleep(0.005)
                        
                        # Click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.005)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        
                        print(f"Distance {distance}px < {scaled_click_distance}px - Clicked center at ({center_x}, {center_y})")
                        
                        # Move cursor back to bottom middle after click
                        win32api.SetCursorPos((bottom_middle_x, bottom_middle_y))
                        time.sleep(0.005)
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        
                        # Reset tracking after click
                        last_distance = None
                        circle_exceeded_threshold = False
                        
                        # Wait 500ms after click to avoid clicking the same circle twice
                        time.sleep(0.5)
                        
                        # Reset state change time after click
                        last_state_change_time = time.time()
                        continue
                else:
                    # No white detected - check if state changed
                    if white_detected_last_frame:
                        # State changed from detected to not detected
                        last_state_change_time = time.time()
                        print("State change: White not detected")
                    white_detected_last_frame = False
                
                time.sleep(0.005)
    
    def exit_app(self):
        """Exit the application"""
        self.clear_hotkeys()
        self.root.destroy()
    
    def rebind_key(self, action):
        """Rebind a key"""
        if self.rebinding:
            return  # Already rebinding something
        
        self.rebinding = action
        
        # Update label to show waiting state
        if action == "start_stop":
            self.start_stop_label.config(text="Press new key...", fg="blue")
        elif action == "change_area":
            self.change_area_label.config(text="Press new key...", fg="blue")
        elif action == "exit":
            self.exit_label.config(text="Press new key...", fg="blue")
        
        # Listen for key press
        keyboard.on_press(self.on_key_press)
    
    def on_key_press(self, event):
        """Handle key press during rebinding"""
        if not self.rebinding:
            return
        
        # Get the key name
        new_key = event.name.upper()
        
        # Remove the listener
        keyboard.unhook_all()
        
        # Clear old hotkey
        old_key = self.keybindings[self.rebinding]
        
        # Update keybinding
        self.keybindings[self.rebinding] = new_key
        
        # Update label
        if self.rebinding == "start_stop":
            self.start_stop_label.config(text=f"Start/Stop: {new_key}", fg="black")
        elif self.rebinding == "change_area":
            self.change_area_label.config(text=f"Change Area: {new_key}", fg="black")
        elif self.rebinding == "exit":
            self.exit_label.config(text=f"Exit: {new_key}", fg="black")
        
        self.rebinding = None
        
        # Re-setup all hotkeys
        self.setup_hotkeys()
        
        # Save settings after rebinding
        self.save_settings()
        
        print(f"Key rebound to {new_key}")


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
                def window_enum_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        browser_keywords = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave', 'YouTube']
                        if any(keyword.lower() in window_text.lower() for keyword in browser_keywords):
                            windows.append((hwnd, window_text))
                    return True
                
                windows = []
                win32gui.EnumWindows(window_enum_callback, windows)
                
                if windows:
                    browser_found = True
                    print(f"✅ Browser window found: {windows[0][1]}")
                    break
                
                time.sleep(0.2)
            except Exception as e:
                print(f"⚠️ Error checking for browser: {e}")
                break
        
        if not browser_found:
            print("⚠️ Browser window not detected, continuing anyway...")
            time.sleep(3)
            return False
        
        # Wait for YouTube page to load
        print("⏳ Waiting for YouTube page to load...")
        time.sleep(3.5)
        
        # Try to focus browser window
        print("🖱️ Attempting to focus browser...")
        try:
            if windows:
                hwnd = windows[0][0]
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
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
            print(f"⚠️ Error during navigation: {e}")
        
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


def show_terms_and_conditions():
    """Show terms of use dialog on first launch - must accept to continue"""
    # Create temporary root for dialog
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    # Message text
    message = """═════════════════════════════════════════════════════
           FORGE MACRO 3 - TERMS OF USE
                    by AsphaltCake
═════════════════════════════════════════════════════

⚠️ IMPORTANT NOTICE ⚠️

This application is NOT a virus or malware!
  • Automation tool for Roblox Game "THE FORGE"
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
        "Terms of Use - FORGE Macro 3",
        message,
        icon='info'
    )
    
    temp_root.destroy()
    return result


def main():
    # Check if settings file exists
    if getattr(sys, 'frozen', False):
        settings_dir = Path(sys.executable).parent
    else:
        settings_dir = Path(__file__).parent
    
    settings_file = settings_dir / "AutoForgeSettings.json"
    
    # If settings don't exist, show terms and do auto-subscribe
    if not settings_file.exists():
        print("\n🎉 First launch detected - showing terms...")
        
        # Show terms dialog - must accept to continue
        if not show_terms_and_conditions():
            print("User declined terms - exiting application...")
            sys.exit(0)  # Exit if they decline
        
        print("Terms accepted - proceeding with auto-subscribe...")
        try:
            auto_subscribe_to_youtube()
        except Exception as e:
            print(f"Auto-subscribe error (non-critical): {e}")
        
        # Small delay before launching main app
        time.sleep(0.5)
    
    # Create and run the app
    root = tk.Tk()
    app = SimpleForgeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
