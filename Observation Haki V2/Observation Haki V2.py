import tkinter as tk
from tkinter import messagebox
import keyboard
import json
import threading
import sys
import os
from pathlib import Path
import ctypes
import mss
import numpy as np
import cv2
import time
import win32api
import win32con

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

class ObservationHakiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Observation Haki V2")
        self.root.geometry("350x250")
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        
        # Get screen resolution
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # State variables
        self.is_running = False
        self.loop_thread = None
        self.should_exit = False
        self.area_selector_window = None
        
        # Circle tracking
        self.detected_circles = {}  # {circle_id: {"center": (x,y), "detected_time": timestamp, "clicked": False}}
        self.next_circle_id = 0
        self.click_delay = 0.7  # Delay before clicking detected circles (in seconds)
        
        # Default area - 80% of screen size, centered
        area_width = int(self.screen_width * 0.8)
        area_height = int(self.screen_height * 0.8)
        start_x = (self.screen_width - area_width) // 2
        start_y = (self.screen_height - area_height) // 2
        
        self.area = {
            "x1": start_x,
            "y1": start_y,
            "x2": start_x + area_width,
            "y2": start_y + area_height
        }
        
        # Default hotkeys
        self.hotkeys = {
            "start_stop": "f1",
            "change_area": "f2",
            "exit": "f3"
        }
        
        # Load saved hotkeys if they exist
        self.load_hotkeys()
        
        # Setup GUI
        self.setup_gui()
        
        # Register global hotkeys
        self.register_hotkeys()
        
        # Prevent window close from exiting app
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def setup_gui(self):
        """Create the GUI layout"""
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="Observation Haki V2", font=("Arial", 12, "bold"))
        title.pack(pady=(0, 2))
        
        # Credits
        credits = tk.Label(main_frame, text="By AsphaltCake", font=("Arial", 8), fg="gray")
        credits.pack(pady=(0, 8))
        
        # Start/Stop Section
        self.create_control_section(
            main_frame,
            "Start/Stop",
            "start_stop",
            self.toggle_start_stop,
            self.rebind_start_stop
        )
        
        # Change Area Section
        self.create_control_section(
            main_frame,
            "Change Area",
            "change_area",
            self.change_area,
            self.rebind_change_area
        )
        
        # Exit Section
        self.create_control_section(
            main_frame,
            "Exit",
            "exit",
            self.exit_app,
            self.rebind_exit
        )
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Status: Stopped", fg="red", font=("Arial", 9))
        self.status_label.pack(pady=(8, 0))
        
        # Area info label
        self.area_label = tk.Label(main_frame, text=self.get_area_text(), font=("Arial", 8))
        self.area_label.pack(pady=(3, 0))
        
        # Click Delay Section
        delay_frame = tk.Frame(main_frame)
        delay_frame.pack(fill=tk.X, pady=4)
        
        tk.Label(delay_frame, text="Delay (sec):", font=("Arial", 8), width=12, anchor="w").pack(side=tk.LEFT)
        self.click_delay_entry = tk.Entry(delay_frame, width=6, font=("Arial", 8))
        self.click_delay_entry.insert(0, str(self.click_delay))
        self.click_delay_entry.pack(side=tk.LEFT, padx=2)
        
        # Bind entry to update on change
        self.click_delay_entry.bind('<KeyRelease>', self.update_click_delay)
    
    def create_control_section(self, parent, label, key_type, action_func, rebind_func):
        """Create a control section with button and rebind button"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=4)
        
        # Label
        label_widget = tk.Label(frame, text=f"{label}:", font=("Arial", 9), width=12, anchor="w")
        label_widget.pack(side=tk.LEFT)
        
        # Hotkey display button
        hotkey_button = tk.Button(
            frame,
            text=self.hotkeys[key_type].upper(),
            font=("Arial", 8),
            width=6,
            state=tk.DISABLED,
            bg="#cccccc"
        )
        hotkey_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Store reference for updates
        if key_type == "start_stop":
            self.start_stop_button = hotkey_button
        elif key_type == "change_area":
            self.change_area_button = hotkey_button
        elif key_type == "exit":
            self.exit_button = hotkey_button
        
        # Action button
        action_button = tk.Button(
            frame,
            text="Trigger",
            font=("Arial", 8),
            width=7,
            command=action_func
        )
        action_button.pack(side=tk.LEFT, padx=2)
        
        # Rebind button
        rebind_button = tk.Button(
            frame,
            text="Rebind",
            font=("Arial", 8),
            width=7,
            command=rebind_func,
            bg="#ffffcc"
        )
        rebind_button.pack(side=tk.LEFT)
    
    def register_hotkeys(self):
        """Register all global hotkeys"""
        try:
            keyboard.add_hotkey(self.hotkeys["start_stop"], self.toggle_start_stop)
            keyboard.add_hotkey(self.hotkeys["change_area"], self.change_area)
            keyboard.add_hotkey(self.hotkeys["exit"], self.exit_app)
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Failed to register hotkeys: {e}")
    
    def unregister_hotkeys(self):
        """Unregister all global hotkeys"""
        try:
            keyboard.remove_hotkey(self.hotkeys["start_stop"])
            keyboard.remove_hotkey(self.hotkeys["change_area"])
            keyboard.remove_hotkey(self.hotkeys["exit"])
        except:
            pass
    
    def rebind_start_stop(self):
        """Rebind the start/stop hotkey"""
        self.rebind_hotkey("start_stop", "Start/Stop")
    
    def rebind_change_area(self):
        """Rebind the change area hotkey"""
        self.rebind_hotkey("change_area", "Change Area")
    
    def rebind_exit(self):
        """Rebind the exit hotkey"""
        self.rebind_hotkey("exit", "Exit")
    
    def rebind_hotkey(self, key_type, label):
        """Generic hotkey rebinding"""
        result = messagebox.showinfo(
            "Rebind Hotkey",
            f"Press the new key for '{label}'.\n(Press ESC to cancel)"
        )
        
        # Show a temporary window to capture key press
        capture_window = tk.Toplevel(self.root)
        capture_window.title(f"Rebinding {label}")
        capture_window.geometry("300x100")
        capture_window.attributes('-topmost', True)
        
        tk.Label(capture_window, text=f"Press new key for {label}...", font=("Arial", 12)).pack(pady=20)
        
        captured_key = [None]
        
        def capture_key(event):
            try:
                key_name = event.keysym.lower()
                if key_name == 'escape':
                    capture_window.destroy()
                    return
                
                captured_key[0] = key_name
                
                # Remove old hotkey
                try:
                    keyboard.remove_hotkey(self.hotkeys[key_type])
                except:
                    pass
                
                # Update hotkey
                self.hotkeys[key_type] = key_name
                self.save_hotkeys()
                
                # Register new hotkey
                if key_type == "start_stop":
                    keyboard.add_hotkey(key_name, self.toggle_start_stop)
                    self.start_stop_button.config(text=key_name.upper())
                elif key_type == "change_area":
                    keyboard.add_hotkey(key_name, self.change_area)
                    self.change_area_button.config(text=key_name.upper())
                elif key_type == "exit":
                    keyboard.add_hotkey(key_name, self.exit_app)
                    self.exit_button.config(text=key_name.upper())
                
                capture_window.destroy()
                messagebox.showinfo("Success", f"Hotkey rebound to {key_name.upper()}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rebind hotkey: {e}")
                capture_window.destroy()
        
        capture_window.bind('<Key>', capture_key)
        capture_window.focus()
    
    def toggle_start_stop(self):
        """Toggle the main loop on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.status_label.config(text="Status: Running", fg="green")
            self.start_loop()
        else:
            self.status_label.config(text="Status: Stopped", fg="red")
    
    def start_loop(self):
        """Start the main loop in a separate thread"""
        if self.loop_thread and self.loop_thread.is_alive():
            return
        
        self.loop_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.loop_thread.start()
    
    def main_loop(self):
        """Main processing loop - detect circles and click them"""
        sct = mss.mss()
        
        while self.is_running and not self.should_exit:
            try:
                # Capture the selected area
                monitor = {
                    "top": self.area["y1"],
                    "left": self.area["x1"],
                    "width": self.area["x2"] - self.area["x1"],
                    "height": self.area["y2"] - self.area["y1"]
                }
                
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                
                # Convert BGRA to BGR
                frame = frame[:, :, :3]
                
                # Find pure white pixels (255, 255, 255)
                white_mask = cv2.inRange(frame, (255, 255, 255), (255, 255, 255))
                
                # Find contours (circles)
                contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                current_circles = {}
                
                # Process detected contours
                for contour in contours:
                    # Filter small contours
                    area = cv2.contourArea(contour)
                    if area < 50:  # Minimum area threshold
                        continue
                    
                    # Get circle center and radius
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    
                    if radius < 5:  # Minimum radius
                        continue
                    
                    # Convert to screen coordinates
                    screen_x = int(x + self.area["x1"])
                    screen_y = int(y + self.area["y1"])
                    
                    # Create a unique ID for this circle based on position
                    circle_key = (round(screen_x / 10) * 10, round(screen_y / 10) * 10)
                    current_circles[circle_key] = {
                        "center": (screen_x, screen_y),
                        "radius": radius
                    }
                
                # Check for new circles
                current_time = time.time()
                for circle_key, circle_data in current_circles.items():
                    if circle_key not in self.detected_circles:
                        # New circle detected
                        self.detected_circles[circle_key] = {
                            "center": circle_data["center"],
                            "detected_time": current_time,
                            "clicked": False
                        }
                
                # Click circles that have been visible for the configured delay
                circles_to_click = []
                for circle_key, circle_info in self.detected_circles.items():
                    if not circle_info["clicked"]:
                        time_elapsed = current_time - circle_info["detected_time"]
                        if time_elapsed >= self.click_delay:  # Wait for configured delay before clicking
                            circles_to_click.append(circle_key)
                
                # Click circles in order of detection
                for circle_key in circles_to_click:
                    circle_info = self.detected_circles[circle_key]
                    x, y = circle_info["center"]
                    
                    # Use NewForge method: SetCursorPos + 1px relative move
                    win32api.SetCursorPos((x, y))
                    time.sleep(0.005)
                    
                    # Roblox mouse register
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                    time.sleep(0.005)
                    
                    # Click
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.005)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                    circle_info["clicked"] = True
                
                # Remove circles that are no longer visible
                circles_to_remove = []
                for circle_key in self.detected_circles.keys():
                    if circle_key not in current_circles and self.detected_circles[circle_key]["clicked"]:
                        circles_to_remove.append(circle_key)
                
                for circle_key in circles_to_remove:
                    del self.detected_circles[circle_key]
                
                time.sleep(0.05)  # Check every 50ms
                
            except Exception as e:
                print(f"Loop error: {e}")
                self.is_running = False
    
    def change_area(self):
        """Toggle area selector on/off"""
        if not hasattr(self, 'area_selector_window') or self.area_selector_window is None:
            # Turn on - open area selector
            if self.is_running:
                messagebox.showwarning("Warning", "Please stop the loop before changing area")
                return
            
            try:
                self.area_selector_window = AreaSelector(self.root, self.area, self.on_area_selected, "Select Area")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open area selector: {e}")
                self.area_selector_window = None
        else:
            # Turn off - close area selector and update display
            try:
                if self.area_selector_window.window.winfo_exists():
                    # Get the current coordinates before closing
                    self.area = self.area_selector_window.get_coordinates()
                    self.area_selector_window.window.destroy()
                self.area_selector_window = None
                self.area_label.config(text=self.get_area_text())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to close area selector: {e}")
                self.area_selector_window = None
    
    def on_area_selected(self, area):
        """Callback when area is selected"""
        self.area = area
    
    def get_area_text(self):
        """Get formatted area text"""
        return f"Area: ({self.area['x1']}, {self.area['y1']}) to ({self.area['x2']}, {self.area['y2']})"
    
    def update_click_delay(self, event=None):
        """Update click delay as user types"""
        try:
            delay = float(self.click_delay_entry.get())
            if delay >= 0:
                self.click_delay = delay
        except ValueError:
            pass  # Ignore invalid input while typing
    
    def save_hotkeys(self):
        """Save hotkeys to file"""
        try:
            with open("hotkeys.json", "w") as f:
                json.dump(self.hotkeys, f)
        except Exception as e:
            print(f"Failed to save hotkeys: {e}")
    
    def load_hotkeys(self):
        """Load hotkeys from file"""
        try:
            if os.path.exists("hotkeys.json"):
                with open("hotkeys.json", "r") as f:
                    self.hotkeys = json.load(f)
        except Exception as e:
            print(f"Failed to load hotkeys: {e}")
    
    def hide_window(self):
        """Hide window instead of closing"""
        self.root.withdraw()
    
    def exit_app(self):
        """Exit the entire application"""
        self.should_exit = True
        self.is_running = False
        
        # Unregister hotkeys
        self.unregister_hotkeys()
        
        # Cleanup
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

def main():
    root = tk.Tk()
    app = ObservationHakiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
