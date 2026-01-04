import win32api
import win32con
import win32gui
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
from pathlib import Path
from PIL import Image, ImageTk
import sys
import os
from pynput import mouse
import keyboard


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
        
        # Create canvas for border and title
        self.canvas = tk.Canvas(self.window, bg='green', highlightthickness=3, 
                               highlightbackground='lime')
        self.canvas.pack(fill='both', expand=True)
        
        # Add title label
        self.title_label = tk.Label(self.window, text=title, bg='green', fg='white', 
                                    font=('Arial', 14, 'bold'))
        self.title_label.place(x=10, y=10)
        
        # Mouse state
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        self.resize_threshold = 20
        
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
        """Get current coordinates of the selector"""
        x1 = self.window.winfo_x()
        y1 = self.window.winfo_y()
        x2 = x1 + self.window.winfo_width()
        y2 = y1 + self.window.winfo_height()
        return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
    
    def close(self):
        """Close the area selector and return coordinates"""
        coords = self.get_coordinates()
        self.callback(coords)
        self.window.destroy()


def focus_roblox():
    """Find and focus Roblox window"""
    def window_enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if 'roblox' in window_text.lower():
                windows.append((hwnd, window_text))
        return True
    
    windows = []
    win32gui.EnumWindows(window_enum_callback, windows)
    
    if windows:
        hwnd = windows[0][0]
        window_name = windows[0][1]
        print(f"Found Roblox window: {window_name}")
        
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Bring to foreground
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    else:
        print("⚠️ Roblox window not found!")
        return False


class GoToSellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Go To Sell - Recorder")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Get script directory
        if getattr(sys, 'frozen', False):
            self.script_dir = Path(sys.executable).parent
        else:
            self.script_dir = Path(__file__).parent
        
        self.settings_file = self.script_dir / "TestInputSettings.json"
        
        # Default keybindings
        self.default_bindings = {
            "start_stop": "F1",
            "change_area": "F2",
            "exit": "F3",
            "next_step": "F4"
        }
        
        # Load or use default keybindings
        self.keybindings = self.load_settings()
        
        # State
        self.is_recording = False
        self.is_running = False
        self.area = {"x1": 100, "y1": 100, "x2": 300, "y2": 300}  # Default area
        self.area_selector = None
        self.area_change_enabled = False
        self.recordings = {
            "sell": [],
            "cannon": [],
            "mine": []
        }
        self.recording_start_time = None
        self.last_click_time = None
        self.mouse_listener = None
        
        # Recording wizard state
        self.recording_step = 0  # 0=not recording, 1=sell, 2=cannon, 3=mine
        
        # Walk settings
        self.w_duration = 7  # Default 7 seconds
        self.s_duration = 3  # Default 3 seconds
        
        # Create GUI
        self.create_widgets()
        
        # Update area label with loaded area
        area_text = f"Area: [{self.area['x1']}, {self.area['y1']}] to [{self.area['x2']}, {self.area['y2']}]"
        self.area_label.config(text=area_text)
        
        # Update walk duration entry fields with loaded values
        self.w_duration_var.set(str(self.w_duration))
        self.s_duration_var.set(str(self.s_duration))
        
        # Update recording info
        self.update_recording_info()
        
        # Setup hotkeys
        self.setup_hotkeys()
    
    def create_widgets(self):
        # Create main container with left and right columns
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Left column for main content
        left_frame = tk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        # Right column for image
        right_frame = tk.Frame(main_container)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        # Load and display Lapis Lazuli image in right column
        try:
            image_path = self.script_dir / "OreImages" / "Lapis Lazuli.png"
            if image_path.exists():
                img = Image.open(image_path)
                # Resize to reasonable size (e.g., 150x150)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(right_frame, image=self.photo)
                img_label.pack(pady=5)
        except Exception as e:
            print(f"Could not load image: {e}")
        
        # Title
        tk.Label(left_frame, text="GPO Automation Recorder", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Current Area Display
        area_text = f"Area: [{self.area['x1']}, {self.area['y1']}] to [{self.area['x2']}, {self.area['y2']}]"
        self.area_label = tk.Label(left_frame, text=area_text, 
                                   font=("Arial", 9), fg="blue")
        self.area_label.pack(pady=5)
        
        # Compact hotkey buttons with rebind (4-stack like AutoSell)
        # Start/Stop
        frame1 = tk.Frame(left_frame)
        frame1.pack(pady=2)
        tk.Button(frame1, text=f"Start/Stop ({self.keybindings['start_stop']})", 
                 command=self.toggle_script, width=25).pack(side="left", padx=2)
        tk.Button(frame1, text="Rebind", command=lambda: self.rebind_key("start_stop"), 
                 width=8).pack(side="left")
        
        # Change Area
        frame2 = tk.Frame(left_frame)
        frame2.pack(pady=2)
        tk.Button(frame2, text=f"Change Area ({self.keybindings['change_area']})", 
                 command=self.change_area, width=25).pack(side="left", padx=2)
        tk.Button(frame2, text="Rebind", command=lambda: self.rebind_key("change_area"), 
                 width=8).pack(side="left")
        
        # Exit
        frame3 = tk.Frame(left_frame)
        frame3.pack(pady=2)
        tk.Button(frame3, text=f"Exit ({self.keybindings['exit']})", 
                 command=self.exit_program, width=25).pack(side="left", padx=2)
        tk.Button(frame3, text="Rebind", command=lambda: self.rebind_key("exit"), 
                 width=8).pack(side="left")
        
        # Next Step
        frame4 = tk.Frame(left_frame)
        frame4.pack(pady=2)
        tk.Button(frame4, text=f"Next Recording Step ({self.keybindings['next_step']})", 
                 command=self.next_recording_step, width=25).pack(side="left", padx=2)
        tk.Button(frame4, text="Rebind", command=lambda: self.rebind_key("next_step"), 
                 width=8).pack(side="left")
        
        # Status
        self.status_label = tk.Label(left_frame, text="Status: Idle", 
                                     font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)
        
        # Recording info
        self.recording_info = tk.Label(left_frame, text="No recordings loaded", 
                                       font=("Arial", 9), fg="gray")
        self.recording_info.pack(pady=5)
        
        # Recording instruction label (hidden by default)
        self.instruction_label = tk.Label(left_frame, text="", 
                                         font=("Arial", 10, "bold"), fg="red")
        self.instruction_label.pack(pady=5)
        
        # Record button
        tk.Button(left_frame, text="🔴 Start Recording Wizard", 
                 command=self.start_recording_wizard, width=30, 
                 font=("Arial", 10, "bold"), bg="#ff4444", fg="white").pack(pady=10)
        
        # Walk duration settings
        tk.Label(left_frame, text="Walk Duration (Step 6):", font=("Arial", 10, "bold")).pack(pady=(10,2))
        
        walk_frame = tk.Frame(left_frame)
        walk_frame.pack(pady=5)
        
        tk.Label(walk_frame, text="W Key (seconds):", font=("Arial", 9)).grid(row=0, column=0, padx=5, pady=2)
        self.w_duration_var = tk.StringVar(value="7")
        tk.Entry(walk_frame, textvariable=self.w_duration_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(walk_frame, text="S Key (seconds):", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=2)
        self.s_duration_var = tk.StringVar(value="3")
        tk.Entry(walk_frame, textvariable=self.s_duration_var, width=10).grid(row=1, column=1, padx=5, pady=2)
    
    def setup_hotkeys(self):
        """Setup global hotkeys that work even when minimized"""
        try:
            # Remove any existing hotkeys first
            keyboard.unhook_all()
            
            # Add hotkeys
            keyboard.add_hotkey(self.keybindings['start_stop'].lower(), self.toggle_script, suppress=True)
            keyboard.add_hotkey(self.keybindings['change_area'].lower(), self.change_area, suppress=True)
            keyboard.add_hotkey(self.keybindings['exit'].lower(), self.exit_program, suppress=True)
            keyboard.add_hotkey(self.keybindings['next_step'].lower(), self.next_recording_step, suppress=True)
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def refresh_hotkeys(self):
        """Refresh hotkeys after rebinding"""
        self.setup_hotkeys()
    
    def change_area(self):
        """Toggle area selector on/off"""
        if self.area_selector is None:
            # Open area selector
            self.area_change_enabled = True
            self.status_label.config(text="Drag area box (Press F2 to save)", fg="orange")
            
            # Create selector
            self.area_selector = AreaSelector(
                self.root, 
                self.area, 
                lambda coords: self.on_area_selected(coords), 
                "Detection Area"
            )
        else:
            # Close area selector
            self.area_selector.close()
            self.area_selector = None
            self.area_change_enabled = False
            self.status_label.config(text="Area saved!", fg="green")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Idle",
                fg="green" if self.is_running else "blue"
            ))
    
    def on_area_selected(self, coords):
        """Called when area selection is complete"""
        self.area = coords
        area_text = f"Area: [{coords['x1']}, {coords['y1']}] to [{coords['x2']}, {coords['y2']}]"
        self.area_label.config(text=area_text)
        self.save_recording()  # Save area to settings
        print(f"Detection area saved: {coords}")
    
    def rebind_key(self, action):
        """Rebind a hotkey"""
        action_names = {
            "start_stop": "Start/Stop",
            "change_area": "Change Area",
            "exit": "Exit",
            "next_step": "Next Recording Step"
        }
        
        response = tk.simpledialog.askstring(
            "Rebind Key",
            f"Press a key for {action_names[action]}\n(e.g., F1, F2, ctrl+s)",
            parent=self.root
        )
        
        if response:
            response = response.strip()
            if response:
                self.keybindings[action] = response
                if self.save_recording():
                    # Update button text
                    self.root.destroy()
                    self.__init__(tk.Tk())
                    self.refresh_hotkeys()  # Refresh hotkeys with new binding
    
    def exit_program(self):
        """Exit the program"""
        keyboard.unhook_all()  # Remove all hotkeys
        self.root.quit()
    
    def update_recording_info(self):
        """Update the recording info label"""
        info_text = []
        for rec_type, clicks in self.recordings.items():
            count = len(clicks)
            if count > 0:
                info_text.append(f"{rec_type.capitalize()}: {count} clicks")
        
        if info_text:
            self.recording_info.config(text=" | ".join(info_text), fg="green")
        else:
            self.recording_info.config(text="No recordings loaded", fg="gray")
    
    def load_settings(self):
        """Load keybindings, area, and recordings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    # Load recordings
                    self.recordings = data.get("recordings", {
                        "sell": [],
                        "cannon": [],
                        "mine": []
                    })
                    # Load area if it exists
                    if "area" in data:
                        self.area = data["area"]
                    # Load walk durations
                    if "w_duration" in data:
                        self.w_duration = data["w_duration"]
                    if "s_duration" in data:
                        self.s_duration = data["s_duration"]
                    
                    print(f"Loaded recordings: Sell={len(self.recordings['sell'])}, "
                          f"Cannon={len(self.recordings['cannon'])}, Mine={len(self.recordings['mine'])}")
                    return data.get("keybindings", self.default_bindings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.default_bindings.copy()
    
    def save_recording(self):
        """Save recordings, keybindings, area, and walk durations to JSON file"""
        try:
            data = {
                "keybindings": self.keybindings,
                "recordings": self.recordings,
                "area": self.area,
                "w_duration": self.w_duration,
                "s_duration": self.s_duration
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved all settings to {self.settings_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False
    
    def start_recording_wizard(self):
        """Start the recording wizard"""
        if self.is_recording:
            messagebox.showwarning("Already Recording", "Recording wizard is already in progress!")
            return
        
        if self.is_running:
            messagebox.showwarning("Script Running", "Stop the running script first!")
            return
        
        # Clear all recordings
        self.recordings = {
            "sell": [],
            "cannon": [],
            "mine": []
        }
        
        # Start wizard
        self.recording_step = 1
        self.is_recording = True
        
        # Run wizard in thread
        import threading
        threading.Thread(target=self._recording_wizard_thread, daemon=True).start()
    
    def next_recording_step(self):
        """Called when F4 is pressed to move to next step"""
        if not self.is_recording:
            return
        
        # Only allow steps 1-3
        if self.recording_step < 1 or self.recording_step > 3:
            print(f"F4 ignored - invalid step: {self.recording_step}")
            return
        
        # Stop current mouse listener
        if self.mouse_listener:
            # Add final delay
            if self.last_click_time is not None:
                final_delay = time.time() - self.last_click_time
                current_type = ["sell", "cannon", "mine"][self.recording_step - 1]
                self.recordings[current_type].append({
                    "x": None,
                    "y": None,
                    "delay": final_delay,
                    "is_final_delay": True
                })
                print(f"Added final delay: {final_delay:.2f}s")
            
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # Release Shift after stopping listener (in case it was held during recording)
        shift_scan = win32api.MapVirtualKey(0x10, 0)
        win32api.keybd_event(0x10, shift_scan, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        # Move to next step
        self.recording_step += 1
        print(f"\n>>> F4 PRESSED - Moving to step {self.recording_step}")
    
    def _recording_wizard_thread(self):
        """Recording wizard that guides through all steps"""
        try:
            # === STEP 1: ESC + R + ENTER + LOOK DOWN + RECORD SELL ===
            self.status_label.config(text="Recording: Initializing...", fg="red")
            self.instruction_label.config(text="")
            
            print("\n" + "="*60)
            print("RECORDING WIZARD STARTED")
            print("="*60)
            
            # Focus Roblox
            print("\nFocusing Roblox window...")
            if not focus_roblox():
                messagebox.showerror("Error", "Roblox window not found!")
                self.is_recording = False
                self.recording_step = 0
                return
            
            # ESC + R
            print("Sending ESC+R...")
            esc_scan = win32api.MapVirtualKey(0x1B, 0)
            win32api.keybd_event(0x1B, esc_scan, 0, 0)
            win32api.keybd_event(0x1B, esc_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            r_scan = win32api.MapVirtualKey(0x52, 0)
            win32api.keybd_event(0x52, r_scan, 0, 0)
            win32api.keybd_event(0x52, r_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(2.0)
            
            # Enter
            print("Sending Enter...")
            enter_scan = win32api.MapVirtualKey(0x0D, 0)
            win32api.keybd_event(0x0D, enter_scan, 0, 0)
            win32api.keybd_event(0x0D, enter_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(6.0)
            
            # Look down
            print("Looking down...")
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            for i in range(10):
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 250, 0, 0)
                time.sleep(0.001)
            time.sleep(1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            
            # Start recording SELL
            print("\n>>> STEP 1: RECORD GO TO SELL")
            self.status_label.config(text="Recording: GO TO SELL", fg="red")
            self.instruction_label.config(text="▶ Right-click to navigate to SELL | Press F4 when done", fg="red")
            
            self.recordings["sell"] = []
            self.last_click_time = None
            
            # Hold Shift and start listener
            shift_scan = win32api.MapVirtualKey(0x10, 0)
            win32api.keybd_event(0x10, shift_scan, 0, 0)
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            
            # Wait for F4 (check more frequently)
            while self.recording_step == 1 and self.is_recording:
                time.sleep(0.05)
            
            if not self.is_recording:
                return
            
            # === STEP 2: SELL FUNCTION + RESET + RECORD CANNON ===
            print("\n>>> STEP 2: SELL FUNCTION")
            self.status_label.config(text="Recording: Sell Function...", fg="orange")
            self.instruction_label.config(text="⏳ Executing sell function...", fg="orange")
            
            # Focus and press E
            focus_roblox()
            time.sleep(0.2)
            e_scan = win32api.MapVirtualKey(0x45, 0)
            win32api.keybd_event(0x45, e_scan, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(0x45, e_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)
            
            # Left click twice
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.5)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(2)
            
            # Click at (1507, 839)
            win32api.SetCursorPos((1507, 839))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(2)
            
            # ESC + R + Enter + Look down again
            print("Resetting...")
            esc_scan = win32api.MapVirtualKey(0x1B, 0)
            win32api.keybd_event(0x1B, esc_scan, 0, 0)
            win32api.keybd_event(0x1B, esc_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            r_scan = win32api.MapVirtualKey(0x52, 0)
            win32api.keybd_event(0x52, r_scan, 0, 0)
            win32api.keybd_event(0x52, r_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(2.0)
            enter_scan = win32api.MapVirtualKey(0x0D, 0)
            win32api.keybd_event(0x0D, enter_scan, 0, 0)
            win32api.keybd_event(0x0D, enter_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(6.0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            for i in range(10):
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 250, 0, 0)
                time.sleep(0.001)
            time.sleep(1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            
            # Start recording CANNON
            print("\n>>> STEP 2: RECORD GO TO CANNON")
            self.status_label.config(text="Recording: GO TO CANNON", fg="red")
            self.instruction_label.config(text="▶ Right-click to navigate to CANNON | Press F4 when done", fg="red")
            
            self.recordings["cannon"] = []
            self.last_click_time = None
            
            shift_scan = win32api.MapVirtualKey(0x10, 0)
            win32api.keybd_event(0x10, shift_scan, 0, 0)
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            
            # Wait for F4 (check more frequently)
            while self.recording_step == 2 and self.is_recording:
                time.sleep(0.05)
            
            if not self.is_recording:
                return
            
            # === STEP 3: WALK FUNCTION + RECORD MINE ===
            print("\n>>> STEP 3: WALK FUNCTION")
            self.status_label.config(text="Recording: Walk Function...", fg="orange")
            self.instruction_label.config(text="⏳ Executing walk function...", fg="orange")
            
            # Get durations
            try:
                w_duration = float(self.w_duration_var.get())
                s_duration = float(self.s_duration_var.get())
            except:
                w_duration = 7
                s_duration = 3
            
            # Press E
            focus_roblox()
            time.sleep(0.2)
            e_scan = win32api.MapVirtualKey(0x45, 0)
            win32api.keybd_event(0x45, e_scan, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(0x45, e_scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)
            
            # Hold W
            print(f"Holding W for {w_duration}s...")
            w_scan = win32api.MapVirtualKey(0x57, 0)
            win32api.keybd_event(0x57, w_scan, 0, 0)
            time.sleep(w_duration)
            win32api.keybd_event(0x57, w_scan, win32con.KEYEVENTF_KEYUP, 0)
            
            # Hold S
            print(f"Holding S for {s_duration}s...")
            s_scan = win32api.MapVirtualKey(0x53, 0)
            win32api.keybd_event(0x53, s_scan, 0, 0)
            time.sleep(s_duration)
            win32api.keybd_event(0x53, s_scan, win32con.KEYEVENTF_KEYUP, 0)
            
            # Start recording MINE
            print("\n>>> STEP 3: RECORD GO TO MINE")
            self.status_label.config(text="Recording: GO TO MINE", fg="red")
            self.instruction_label.config(text="▶ Right-click to navigate to MINE | Press F4 when done", fg="red")
            
            self.recordings["mine"] = []
            self.last_click_time = None
            
            shift_scan = win32api.MapVirtualKey(0x10, 0)
            win32api.keybd_event(0x10, shift_scan, 0, 0)
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            
            # Wait for F4 (check more frequently)
            while self.recording_step == 3 and self.is_recording:
                time.sleep(0.05)
            
            # === COMPLETE ===
            print("\n" + "="*60)
            print("RECORDING WIZARD COMPLETE!")
            print("="*60)
            
            self.save_recording()
            self.update_recording_info()
            self.status_label.config(text="Status: Recording Complete!", fg="green")
            self.instruction_label.config(text="✓ All steps recorded successfully!", fg="green")
            
            messagebox.showinfo("Recording Complete", 
                              f"All 3 routes recorded!\n"
                              f"Sell: {len(self.recordings['sell'])} clicks\n"
                              f"Cannon: {len(self.recordings['cannon'])} clicks\n"
                              f"Mine: {len(self.recordings['mine'])} clicks")
            
            self.is_recording = False
            self.recording_step = 0
            
            # Clear instruction after delay
            time.sleep(3)
            self.instruction_label.config(text="")
            
        except Exception as e:
            print(f"Recording wizard error: {e}")
            messagebox.showerror("Error", f"Recording failed: {e}")
            self.is_recording = False
            self.recording_step = 0
            self.instruction_label.config(text="")
    
    def on_click(self, x, y, button, pressed):
        if not self.is_recording or self.recording_step == 0:
            return
        
        # Only record right button release
        if button == mouse.Button.right and not pressed:
            current_time = time.time()
            
            if self.last_click_time is None:
                delay = 0
            else:
                delay = current_time - self.last_click_time
            
            self.last_click_time = current_time
            
            # Determine which recording to add to
            rec_types = ["sell", "cannon", "mine"]
            current_type = rec_types[self.recording_step - 1]
            
            click_data = {
                "x": x,
                "y": y,
                "delay": delay
            }
            self.recordings[current_type].append(click_data)
            
            count = len(self.recordings[current_type])
            print(f"Recorded {current_type.upper()} click #{count}: ({x}, {y}) - Delay: {delay:.2f}s")
    
    def toggle_script(self):
        """Toggle script start/stop (F1)"""
        if self.is_recording:
            return
        
        if self.is_running:
            # Stop the script
            self.is_running = False
            self.status_label.config(text="Status: Stopped", fg="red")
            print("\n" + "="*50)
            print("SCRIPT STOPPED BY USER")
            print("="*50)
            return
        
        # Start the script
        self.is_running = True
        self.status_label.config(text="Status: Running Script...", fg="green")
        print("\n" + "="*50)
        print("RUNNING SCRIPT")
        print("="*50)
        
        # Run in separate thread
        import threading
        threading.Thread(target=self._run_script_thread, daemon=True).start()
    
    def _run_script_thread(self):
        try:
            # === STEP 1: ESC + R + ENTER + LOOK DOWN ===
            if not self.is_running: return
            print("\n[STEP 1] ESC + R + ENTER + LOOK DOWN")
            print("="*50)
            
            # Focus Roblox window
            print("Focusing Roblox window...")
            if not focus_roblox():
                print("Failed to find Roblox window.")
                self.status_label.config(text="Status: Failed - No Roblox", fg="red")
                self.is_running = False
                return
            
            # Send ESC + R
            print("Sending ESC+R...")
            esc_scan = win32api.MapVirtualKey(0x1B, 0)
            win32api.keybd_event(0x1B, esc_scan, 0, 0)  # ESC down
            win32api.keybd_event(0x1B, esc_scan, win32con.KEYEVENTF_KEYUP, 0)  # ESC up
            time.sleep(0.1)
            r_scan = win32api.MapVirtualKey(0x52, 0)
            win32api.keybd_event(0x52, r_scan, 0, 0)  # R down
            win32api.keybd_event(0x52, r_scan, win32con.KEYEVENTF_KEYUP, 0)  # R up
            time.sleep(2.0)
            
            if not self.is_running: return
            
            # Send Enter
            print("Sending Enter...")
            enter_scan = win32api.MapVirtualKey(0x0D, 0)
            win32api.keybd_event(0x0D, enter_scan, 0, 0)  # Enter down
            win32api.keybd_event(0x0D, enter_scan, win32con.KEYEVENTF_KEYUP, 0)  # Enter up
            time.sleep(6.0)
            
            if not self.is_running: return
            
            # Look down
            print("Looking down...")
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            
            for i in range(10):
                if not self.is_running:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                    return
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 250, 0, 0)
                time.sleep(0.001)
            
            time.sleep(1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            
            # === STEP 2: GO TO SELL ===
            if not self.is_running: return
            print("\n[STEP 2] GO TO SELL")
            print("="*50)
            
            recorded_clicks = self.recordings.get("sell", [])
            if recorded_clicks:
                print(f"Executing {len(recorded_clicks)} recorded entries for SELL...")
                
                # Hold Shift before clicking
                print("Holding Shift...")
                shift_scan = win32api.MapVirtualKey(0x10, 0)
                win32api.keybd_event(0x10, shift_scan, 0, 0)  # Shift down
                time.sleep(0.1)
                
                for i, click in enumerate(recorded_clicks):
                    if not self.is_running: break
                    
                    if click["delay"] > 0:
                        print(f"Waiting {click['delay']:.2f}s...")
                        time.sleep(click["delay"])
                    
                    if not self.is_running: break
                    
                    # Check if this is a final delay marker
                    if click.get("is_final_delay", False):
                        print("Final delay reached")
                        break
                    
                    print(f"Right-clicking at ({click['x']}, {click['y']})...")
                    win32api.SetCursorPos((click['x'], click['y']))
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                
                # Release Shift after clicking
                print("Releasing Shift...")
                win32api.keybd_event(0x10, shift_scan, win32con.KEYEVENTF_KEYUP, 0)  # Shift up
                time.sleep(0.1)
                
                if not self.is_running: return
            else:
                print("No recorded clicks for SELL - skipping")
            
            if not self.is_running: return
            
            # === STEP 3: SELL FUNCTION (NOT ADDED) ===
            if not self.is_running: return
            print("\n[STEP 3] SELL FUNCTION")
            print("="*50)
            
            # Ensure Roblox is focused before pressing E
            if not focus_roblox():
                print("Warning: Could not focus Roblox window")
            time.sleep(0.2)
            
            # Press E (hold and release for Roblox reliability)
            print("Pressing E (hold)...")
            e_scan = win32api.MapVirtualKey(0x45, 0)
            win32api.keybd_event(0x45, e_scan, 0, 0)  # E down
            time.sleep(0.1)
            win32api.keybd_event(0x45, e_scan, win32con.KEYEVENTF_KEYUP, 0)  # E up
            time.sleep(0.5)
            
            if not self.is_running: return
            
            # Click (left click)
            print("Left-clicking...")
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.5)
            
            if not self.is_running: return
            
            # Click (left click again)
            print("Left-clicking again...")
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(2)
            
            if not self.is_running: return
            
            # Click at position (1507, 839)
            print("Clicking at (1507, 839)...")
            win32api.SetCursorPos((1507, 839))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(2)
            
            # === STEP 4: ESC + R + ENTER + LOOK DOWN ===
            if not self.is_running: return
            print("\n[STEP 4] ESC + R + ENTER + LOOK DOWN")
            print("="*50)
            
            # Send ESC + R
            print("Sending ESC+R...")
            esc_scan = win32api.MapVirtualKey(0x1B, 0)
            win32api.keybd_event(0x1B, esc_scan, 0, 0)  # ESC down
            win32api.keybd_event(0x1B, esc_scan, win32con.KEYEVENTF_KEYUP, 0)  # ESC up
            time.sleep(0.1)
            r_scan = win32api.MapVirtualKey(0x52, 0)
            win32api.keybd_event(0x52, r_scan, 0, 0)  # R down
            win32api.keybd_event(0x52, r_scan, win32con.KEYEVENTF_KEYUP, 0)  # R up
            time.sleep(2.0)
            
            if not self.is_running: return
            
            # Send Enter
            print("Sending Enter...")
            enter_scan = win32api.MapVirtualKey(0x0D, 0)
            win32api.keybd_event(0x0D, enter_scan, 0, 0)  # Enter down
            win32api.keybd_event(0x0D, enter_scan, win32con.KEYEVENTF_KEYUP, 0)  # Enter up
            time.sleep(6.0)
            
            if not self.is_running: return
            
            # Look down
            print("Looking down...")
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            
            for i in range(10):
                if not self.is_running:
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                    return
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 250, 0, 0)
                time.sleep(0.001)
            
            time.sleep(1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            
            # === STEP 5: GO TO CANNON ===
            if not self.is_running: return
            print("\n[STEP 5] GO TO CANNON")
            print("="*50)
            
            recorded_clicks = self.recordings.get("cannon", [])
            if recorded_clicks:
                print(f"Executing {len(recorded_clicks)} recorded entries for CANNON...")
                
                # Hold Shift before clicking
                print("Holding Shift...")
                shift_scan = win32api.MapVirtualKey(0x10, 0)
                win32api.keybd_event(0x10, shift_scan, 0, 0)  # Shift down
                time.sleep(0.1)
                
                for i, click in enumerate(recorded_clicks):
                    if not self.is_running: break
                    
                    if click["delay"] > 0:
                        print(f"Waiting {click['delay']:.2f}s...")
                        time.sleep(click["delay"])
                    
                    if not self.is_running: break
                    
                    # Check if this is a final delay marker
                    if click.get("is_final_delay", False):
                        print("Final delay reached")
                        break
                    
                    print(f"Right-clicking at ({click['x']}, {click['y']})...")
                    win32api.SetCursorPos((click['x'], click['y']))
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                
                # Release Shift after clicking
                print("Releasing Shift...")
                win32api.keybd_event(0x10, shift_scan, win32con.KEYEVENTF_KEYUP, 0)  # Shift up
                time.sleep(0.1)
                
                if not self.is_running: return
            else:
                print("No recorded clicks for CANNON - skipping")
            
            if not self.is_running: return
            
            # === STEP 6: WALK FUNCTION ===
            if not self.is_running: return
            print("\n[STEP 6] WALK FUNCTION")
            print("="*50)
            
            # Ensure Roblox is focused before pressing E
            if not focus_roblox():
                print("Warning: Could not focus Roblox window")
            time.sleep(0.2)
            
            # Press E (hold and release for Roblox reliability)
            print("Pressing E (hold)...")
            e_scan = win32api.MapVirtualKey(0x45, 0)
            win32api.keybd_event(0x45, e_scan, 0, 0)  # E down
            time.sleep(0.1)
            win32api.keybd_event(0x45, e_scan, win32con.KEYEVENTF_KEYUP, 0)  # E up
            time.sleep(0.5)
            
            if not self.is_running: return
            
            # Get walk durations from GUI
            try:
                w_duration = float(self.w_duration_var.get())
                s_duration = float(self.s_duration_var.get())
            except:
                w_duration = 7
                s_duration = 3
            
            # Hold W key
            print(f"Holding W key for {w_duration} seconds...")
            w_scan = win32api.MapVirtualKey(0x57, 0)
            win32api.keybd_event(0x57, w_scan, 0, 0)  # W down
            
            # Check every 0.5 seconds if we should stop
            w_checks = int(w_duration / 0.5)
            for i in range(w_checks):
                if not self.is_running:
                    win32api.keybd_event(0x57, w_scan, win32con.KEYEVENTF_KEYUP, 0)  # W up
                    return
                time.sleep(0.5)
            
            win32api.keybd_event(0x57, w_scan, win32con.KEYEVENTF_KEYUP, 0)  # W up
            print("Released W key")
            
            if not self.is_running: return
            
            # Hold S key
            print(f"Holding S key for {s_duration} seconds...")
            s_scan = win32api.MapVirtualKey(0x53, 0)
            win32api.keybd_event(0x53, s_scan, 0, 0)  # S down
            
            # Check every 0.5 seconds if we should stop
            s_checks = int(s_duration / 0.5)
            for i in range(s_checks):
                if not self.is_running:
                    win32api.keybd_event(0x53, s_scan, win32con.KEYEVENTF_KEYUP, 0)  # S up
                    return
                time.sleep(0.5)
            
            win32api.keybd_event(0x53, s_scan, win32con.KEYEVENTF_KEYUP, 0)  # S up
            print("Released S key")
            
            # === STEP 7: GO TO MINE ===
            if not self.is_running: return
            print("\n[STEP 7] GO TO MINE")
            print("="*50)
            
            recorded_clicks = self.recordings.get("mine", [])
            if recorded_clicks:
                print(f"Executing {len(recorded_clicks)} recorded entries for MINE...")
                
                # Hold Shift before clicking
                print("Holding Shift...")
                shift_scan = win32api.MapVirtualKey(0x10, 0)
                win32api.keybd_event(0x10, shift_scan, 0, 0)  # Shift down
                time.sleep(0.1)
                
                for i, click in enumerate(recorded_clicks):
                    if not self.is_running: break
                    
                    if click["delay"] > 0:
                        print(f"Waiting {click['delay']:.2f}s...")
                        time.sleep(click["delay"])
                    
                    if not self.is_running: break
                    
                    # Check if this is a final delay marker
                    if click.get("is_final_delay", False):
                        print("Final delay reached")
                        break
                    
                    print(f"Right-clicking at ({click['x']}, {click['y']})...")
                    win32api.SetCursorPos((click['x'], click['y']))
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                
                # Release Shift after clicking
                print("Releasing Shift...")
                win32api.keybd_event(0x10, shift_scan, win32con.KEYEVENTF_KEYUP, 0)  # Shift up
                time.sleep(0.1)
                
                if not self.is_running: return
            else:
                print("No recorded clicks for MINE - skipping")
            
            if not self.is_running: return
            
            print("\n" + "="*50)
            print("SCRIPT COMPLETE!")
            print("="*50)
            
            self.status_label.config(text="Status: Script Complete", fg="blue")
            
        except Exception as e:
            print(f"Error running script: {e}")
            self.status_label.config(text=f"Status: Error - {e}", fg="red")
        finally:
            self.is_running = False


def main():
    root = tk.Tk()
    app = GoToSellGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
