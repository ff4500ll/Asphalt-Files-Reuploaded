import tkinter as tk
from tkinter import messagebox
import json
import sys
from pathlib import Path
import keyboard  # pip install keyboard
import threading
import time
import mss
import numpy as np
import cv2
import os
import win32api
import win32con
import win32gui
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


class SellMacro:
    def __init__(self, root):
        self.root = root
        self.root.title("Sell Macro")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Determine the correct settings path for both dev and exe
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.settings_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.settings_dir = Path(__file__).parent
        
        self.settings_file = self.settings_dir / "SELLsettings.json"

        # Default keybindings
        self.default_bindings = {
            "start_stop": "F1",
            "change_area": "F2",
            "exit": "F3"
        }
        
        # Area box for Stash Box - default scaled to resolution
        self.area_selector = None
        # Calculate default area as percentage of screen (centered, ~22% width, 32% height)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Default area dimensions based on 2560x1440 reference
        # Original: x1=681, y1=437, x2=1254, y2=902 (573x465 pixels)
        # As percentages: x1=26.6%, y1=30.3%, width=22.4%, height=32.3%
        default_x1 = int(screen_width * 0.266)
        default_y1 = int(screen_height * 0.303)
        default_x2 = int(screen_width * 0.490)  # 0.266 + 0.224
        default_y2 = int(screen_height * 0.626)  # 0.303 + 0.323
        
        self.area = {"x1": default_x1, "y1": default_y1, "x2": default_x2, "y2": default_y2}
        
        # Image selector for adding images
        self.image_selector = None
        self.image_instruction_window = None
        
        # Keep amounts for each image (default 0)
        self.keep_amounts = {}
        
        # UI button positions (will be set during setup)
        self.ui_positions = {
            'max_button': None,
            'minus_5_button': None,
            'select_button': None,
            'accept_button': None,
            'yes_button': None,
            'mine_position': None
        }
        
        # Load settings
        self.keybindings = self.load_settings()
        
        # Running state
        self.is_running = False
        self.area_change_enabled = False
        self.main_thread = None
        
        # Load settings (before creating widgets)
        self.load_settings()
        
        # Mining wait time (loaded from settings, default 30 minutes)
        if not hasattr(self, 'mining_wait_minutes'):
            self.mining_wait_minutes = 30
        
        # Create GUI elements
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
    def load_settings(self):
        """Load keybindings and area from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Load area if exists
                    if 'area' in settings:
                        self.area = settings['area']
                    # Load keep amounts if exists
                    if 'keep_amounts' in settings:
                        self.keep_amounts = settings['keep_amounts']
                    # Load mining wait time if exists
                    if 'mining_wait_minutes' in settings:
                        self.mining_wait_minutes = settings['mining_wait_minutes']
                    # Load UI positions if exists
                    if 'ui_positions' in settings:
                        self.ui_positions = settings['ui_positions']
                    return settings.get("keybindings", self.default_bindings)
        except Exception as e:
            messagebox.showwarning("Settings", f"Could not load settings: {e}\nUsing defaults.")
        return self.default_bindings.copy()
    
    def save_settings(self):
        """Save keybindings and area to JSON file"""
        try:
            settings = {
                "keybindings": self.keybindings,
                "area": self.area,
                "keep_amounts": self.keep_amounts,
                "mining_wait_minutes": self.mining_wait_minutes,
                "ui_positions": self.ui_positions
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")
            return False
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Title
        tk.Label(self.root, text="Sell Macro", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Start/Stop
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=2)
        tk.Button(frame1, text=f"Start/Stop ({self.keybindings['start_stop']})", 
                 command=self.toggle_start_stop, width=20).pack(side="left", padx=2)
        tk.Button(frame1, text="Rebind", command=lambda: self.rebind_key("start_stop"), 
                 width=8).pack(side="left")
        
        # Change Area
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=2)
        tk.Button(frame2, text=f"Change Area ({self.keybindings['change_area']})", 
                 command=self.change_area, width=20).pack(side="left", padx=2)
        tk.Button(frame2, text="Rebind", command=lambda: self.rebind_key("change_area"), 
                 width=8).pack(side="left")
        
        # Exit
        frame3 = tk.Frame(self.root)
        frame3.pack(pady=2)
        tk.Button(frame3, text=f"Exit ({self.keybindings['exit']})", 
                 command=self.exit_app, width=20).pack(side="left", padx=2)
        tk.Button(frame3, text="Rebind", command=lambda: self.rebind_key("exit"), 
                 width=8).pack(side="left")
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=10)
        
        # Keep Amounts section
        tk.Label(self.root, text="Keep Amounts (multiple of 5):", font=("Arial", 10, "bold")).pack(pady=(10,5))
        
        # Scrollable frame for keep amounts
        amounts_container = tk.Frame(self.root)
        amounts_container.pack(pady=5, fill="both", expand=True)
        
        canvas = tk.Canvas(amounts_container, height=150)
        scrollbar = tk.Scrollbar(amounts_container, orient="vertical", command=canvas.yview)
        self.amounts_frame = tk.Frame(canvas)
        
        self.amounts_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.amounts_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame for Add and Refresh
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Add Image", command=self.add_image, width=15).pack(side="left", padx=2)
        tk.Button(button_frame, text="Refresh Images", command=self.refresh_keep_amounts, width=15).pack(side="left", padx=2)
        
        # Setup UI Positions button
        tk.Button(self.root, text="Setup UI Positions", command=self.setup_ui_positions, 
                 width=30, bg='#FF9800', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Mining wait time setting
        tk.Label(self.root, text="Mining Wait Time (minutes):", font=("Arial", 10, "bold")).pack(pady=(10,5))
        mining_frame = tk.Frame(self.root)
        mining_frame.pack(pady=5)
        self.mining_wait_entry = tk.Entry(mining_frame, width=10)
        self.mining_wait_entry.insert(0, str(self.mining_wait_minutes))
        self.mining_wait_entry.pack(side="left", padx=5)
        tk.Button(mining_frame, text="Save", command=self.save_mining_wait, width=10).pack(side="left", padx=5)
        
        # Load and display keep amounts
        self.refresh_keep_amounts()
    
    def refresh_keep_amounts(self):
        """Scan Sell Images folder and create keep amount entries"""
        # Clear existing entries
        for widget in self.amounts_frame.winfo_children():
            widget.destroy()
        
        # Get Sell Images folder path
        images_folder = self.settings_dir / "Sell Images"
        
        if not images_folder.exists():
            tk.Label(self.amounts_frame, text="No 'Sell Images' folder found", fg="red").pack()
            return
        
        # Get all image files
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp']:
            image_files.extend(images_folder.glob(ext))
        
        if not image_files:
            tk.Label(self.amounts_frame, text="No images found in folder", fg="orange").pack()
            return
        
        # Create entry for each image
        self.keep_amount_entries = {}
        for img_file in sorted(image_files, key=lambda x: x.name):
            img_name = img_file.name
            
            # Initialize keep amount to 0 if not exists
            if img_name not in self.keep_amounts:
                self.keep_amounts[img_name] = 0
            
            frame = tk.Frame(self.amounts_frame)
            frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(frame, text=img_name, width=20, anchor="w").pack(side="left", padx=5)
            
            entry = tk.Entry(frame, width=8)
            entry.insert(0, str(self.keep_amounts[img_name]))
            entry.pack(side="left", padx=5)
            
            # Save button for this entry
            tk.Button(frame, text="Save", 
                     command=lambda n=img_name, e=entry: self.save_keep_amount(n, e),
                     width=6).pack(side="left", padx=2)
            
            # Delete button
            tk.Button(frame, text="Delete",
                     command=lambda n=img_name: self.delete_image(n),
                     width=6).pack(side="left", padx=2)
            
            self.keep_amount_entries[img_name] = entry
    
    def save_keep_amount(self, img_name, entry):
        """Save a specific keep amount"""
        try:
            amount = int(entry.get())
            if amount < 0:
                messagebox.showerror("Error", "Amount must be 0 or greater")
                return
            self.keep_amounts[img_name] = amount
            self.save_settings()
            print(f"Keep amount for {img_name}: {amount}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def save_mining_wait(self):
        """Save mining wait time"""
        try:
            minutes = int(self.mining_wait_entry.get())
            if minutes < 1:
                messagebox.showerror("Error", "Mining wait time must be at least 1 minute")
                return
            self.mining_wait_minutes = minutes
            self.save_settings()
            print(f"Mining wait time set to {minutes} minutes")
            messagebox.showinfo("Success", f"Mining wait time updated to {minutes} minutes")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_image(self):
        """Save mining wait time"""
        try:
            minutes = int(self.mining_wait_entry.get())
            if minutes < 1:
                messagebox.showerror("Error", "Mining wait time must be at least 1 minute")
                return
            self.mining_wait_minutes = minutes
            self.save_settings()
            print(f"Mining wait time set to {minutes} minutes")
            messagebox.showinfo("Success", f"Mining wait time updated to {minutes} minutes")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_image(self):
        """Start image selection process"""
        if self.image_selector:
            return  # Already selecting
        
        # Create initial box in center of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        initial_width = 80
        initial_height = 35
        x1 = (screen_width - initial_width) // 2
        y1 = (screen_height - initial_height) // 2
        x2 = x1 + initial_width
        y2 = y1 + initial_height
        
        initial_box = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        
        # Create selector
        self.image_selector = AreaSelector(self.root, initial_box,
                                          self.capture_image, "Select Image Area")
        
        # Create instruction window
        self.create_image_instruction_window()
    
    def create_image_instruction_window(self):
        """Create instruction window for image selection"""
        self.image_instruction_window = tk.Toplevel(self.root)
        self.image_instruction_window.title("Image Capture")
        self.image_instruction_window.attributes('-topmost', True)
        self.image_instruction_window.resizable(False, False)
        self.image_instruction_window.configure(bg='white')
        
        frame = tk.Frame(self.image_instruction_window, bg='white', relief='solid', borderwidth=2)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        tk.Button(frame, text="Capture",
                 command=self.finish_image_capture,
                 width=20, height=2, font=("Arial", 12, "bold"),
                 bg='#4CAF50', fg='white', activebackground='#45a049',
                 relief='raised', borderwidth=3).pack(padx=30, pady=20)
    
    def finish_image_capture(self):
        """Finish capturing the image"""
        if self.image_selector:
            coords = self.image_selector.get_coordinates()
            self.image_selector.window.destroy()
            self.image_selector = None
            
            # Close instruction window
            if self.image_instruction_window:
                self.image_instruction_window.destroy()
            
            # Capture image at coordinates
            self.capture_image(coords)
    
    def capture_image(self, coords):
        """Capture screenshot of area and save it"""
        from tkinter import simpledialog
        
        # Ask for image name
        image_name = simpledialog.askstring("Image Name", "Enter image name:")
        
        if not image_name:
            return
        
        # Clean up the name and add .png extension if not present
        image_name = image_name.strip()
        if not image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_name += '.png'
        
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
                
                # Convert to numpy array then save with cv2
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Save image to Sell Images folder
                images_folder = self.settings_dir / "Sell Images"
                images_folder.mkdir(exist_ok=True)
                image_path = images_folder / image_name
                
                cv2.imwrite(str(image_path), img)
                
                # Initialize keep amount to 0
                self.keep_amounts[image_name] = 0
                self.save_settings()
                
                # Refresh image list
                self.refresh_keep_amounts()
                
                print(f"Image '{image_name}' saved to {image_path}")
                messagebox.showinfo("Success", f"Image '{image_name}' saved successfully!")
        except Exception as e:
            print(f"Error capturing image: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {e}")
    
    def delete_image(self, img_name):
        """Delete an image file"""
        if messagebox.askyesno("Confirm Delete", f"Delete '{img_name}'?"):
            try:
                images_folder = self.settings_dir / "Sell Images"
                image_path = images_folder / img_name
                
                if image_path.exists():
                    image_path.unlink()
                    
                    # Remove from keep_amounts
                    if img_name in self.keep_amounts:
                        del self.keep_amounts[img_name]
                    self.save_settings()
                    
                    # Refresh list
                    self.refresh_keep_amounts()
                    
                    print(f"Image '{img_name}' deleted")
                else:
                    messagebox.showerror("Error", f"Image file not found: {img_name}")
            except Exception as e:
                print(f"Error deleting image: {e}")
                messagebox.showerror("Error", f"Failed to delete image: {e}")
    
    def toggle_start_stop(self):
        """Toggle the start/stop state"""
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running", fg="green")
            print("Macro started!")
            # Start the main loop in a separate thread
            self.main_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.main_thread.start()
        else:
            self.status_label.config(text="Status: Stopped", fg="red")
            print("Macro stopped!")
    
    def main_loop(self):
        """Main macro loop - runs continuously when is_running is True"""
        # Get Sell Images folder path
        images_folder = self.settings_dir / "Sell Images"
        
        with mss.mss() as sct:
            while self.is_running:
                try:
                    print("\n" + "="*50)
                    print("Starting image search cycle...")
                    print("="*50)
                    
                    # Check if Sell Images folder exists
                    if not images_folder.exists():
                        print(f"⚠️ Sell Images folder not found at: {images_folder}")
                        print("Creating folder...")
                        images_folder.mkdir(exist_ok=True)
                        print("Please add image files to the Sell Images folder.")
                        time.sleep(5)
                        continue
                    
                    # Get all image files from Sell Images folder
                    image_files = []
                    for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp']:
                        image_files.extend(images_folder.glob(ext))
                    
                    if not image_files:
                        print(f"⚠️ No images found in {images_folder}")
                        print("Please add image files to search for.")
                        time.sleep(5)
                        continue
                    
                    print(f"Found {len(image_files)} images to search for:")
                    for img_file in image_files:
                        print(f"  - {img_file.name}")
                    
                    # Get Stash Box area coordinates
                    x1 = self.area["x1"]
                    y1 = self.area["y1"]
                    x2 = self.area["x2"]
                    y2 = self.area["y2"]
                    
                    # Define the screen region to capture
                    monitor = {
                        "top": y1,
                        "left": x1,
                        "width": x2 - x1,
                        "height": y2 - y1
                    }
                    
                    # Search for each image
                    print("\nSearching for images in Stash Box area...")
                    for img_file in image_files:
                        try:
                            # RETAKE SCREENSHOT FOR EACH IMAGE (items move after each sell)
                            screenshot = sct.grab(monitor)
                            screenshot_np = np.array(screenshot)
                            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_BGRA2BGR)
                            
                            # Load template image
                            template = cv2.imread(str(img_file))
                            if template is None:
                                print(f"❌ Could not load image: {img_file.name}")
                                continue
                            
                            h, w = template.shape[:2]
                            
                            # Template matching
                            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            
                            if max_val >= 0.8:
                                print(f"✅ FOUND: {img_file.name}")
                                
                                # Get keep amount for this image
                                img_name = img_file.name
                                keep_amount = self.keep_amounts.get(img_name, 0)
                                
                                # Calculate center of found image in screen coordinates
                                center_x = x1 + max_loc[0] + w // 2
                                center_y = y1 + max_loc[1] + h // 2
                                
                                # 1) Click on the image
                                win32api.SetCursorPos((center_x, center_y))
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                time.sleep(0.2)
                                
                                # 2) Click on Max Position
                                if self.ui_positions['max_button']:
                                    win32api.SetCursorPos(self.ui_positions['max_button'])
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    time.sleep(0.2)
                                else:
                                    print("⚠️ Max button position not set! Use 'Setup UI Positions'")
                                    continue
                                
                                # 3) Click keep_amount times on Minus 5 Position
                                if self.ui_positions['minus_5_button']:
                                    for i in range(keep_amount):
                                        win32api.SetCursorPos(self.ui_positions['minus_5_button'])
                                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        time.sleep(0.2)
                                else:
                                    print("⚠️ Minus 5 button position not set! Use 'Setup UI Positions'")
                                
                                if keep_amount == 0:
                                    time.sleep(0.2)
                                
                                # 4) Click on Select Position
                                if self.ui_positions['select_button']:
                                    win32api.SetCursorPos(self.ui_positions['select_button'])
                                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    time.sleep(0.2)
                                else:
                                    print("⚠️ Select button position not set! Use 'Setup UI Positions'")
                            else:
                                print(f"❌ NOT FOUND: {img_file.name}")
                        
                        except Exception as e:
                            print(f"❌ Error processing {img_file.name}: {e}")
                    
                    # After checking all images, do final clicks
                    print("\n" + "="*50)
                    print("All images checked. Starting final sequence...")
                    print("="*50)
                    
                    # Click Accept Position
                    if self.ui_positions['accept_button']:
                        print("Clicking Accept Position...")
                        win32api.SetCursorPos(self.ui_positions['accept_button'])
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(1)
                    else:
                        print("⚠️ Accept button position not set! Use 'Setup UI Positions'")
                    
                    # Click Yes Position
                    if self.ui_positions['yes_button']:
                        print("Clicking Yes Position...")
                        win32api.SetCursorPos(self.ui_positions['yes_button'])
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(2)
                    else:
                        print("⚠️ Yes button position not set! Use 'Setup UI Positions'")
                    
                    # Wait with constant key press and click loop
                    print("\n" + "="*50)
                    print(f"Cycle complete. Starting {self.mining_wait_minutes} minute mining wait...")
                    print("="*50 + "\n")
                    
                    # Move cursor to mine position
                    if self.ui_positions['mine_position']:
                        print("Moving cursor to mine position...")
                        win32api.SetCursorPos(self.ui_positions['mine_position'])
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                        time.sleep(0.5)
                    else:
                        print("⚠️ Mine position not set! Use 'Setup UI Positions'")
                    
                    # Calculate wait time in seconds
                    wait_seconds = self.mining_wait_minutes * 60
                    start_time = time.time()
                    end_time = start_time + wait_seconds
                    
                    while self.is_running and time.time() < end_time:
                        remaining = int(end_time - time.time())
                        minutes = remaining // 60
                        secs = remaining % 60
                        self.status_label.config(text=f"Mining: {minutes}m {secs}s")
                        
                        # Press 1
                        keyboard.press_and_release('1')
                        time.sleep(0.05)
                        
                        # Left click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(0.05)
                        
                        # Press 2
                        keyboard.press_and_release('2')
                        time.sleep(0.05)
                        
                        # Left click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(0.05)
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(5)
    
    def change_area(self):
        """Toggle area selector on/off"""
        if self.area_selector is None:
            # Open area selector
            self.area_change_enabled = True
            self.status_label.config(text="Drag area box (Press F2 to save)")
            
            # Create selector for Stash Box
            self.area_selector = AreaSelector(
                self.root, 
                self.area, 
                lambda coords: self.on_area_selected(coords), 
                "Stash Box"
            )
        else:
            # Close area selector
            self.area_selector.close()
            self.area_selector = None
            self.area_change_enabled = False
            self.status_label.config(text="Area saved!")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Running" if self.is_running else "Status: Stopped",
                fg="green" if self.is_running else "red"
            ))
    
    def on_area_selected(self, coords):
        """Called when area selection is complete"""
        self.area = coords
        self.save_settings()
        print(f"Stash Box area saved: {coords}")
    
    def setup_ui_positions(self):
        """Guide user through setting up UI button positions"""
        instructions = [
            ("Max Button", "Click on the MAX button in the sell dialog"),
            ("Minus 5 Button", "Click on the MINUS 5 button"),
            ("Select Button", "Click on the SELECT button"),
            ("Accept Button", "Click on the ACCEPT button (bottom of screen)"),
            ("Yes Button", "Click on the YES confirmation button"),
            ("Mine Position", "Click where you want to mine (cursor will stay here)")
        ]
        
        position_keys = ['max_button', 'minus_5_button', 'select_button', 
                        'accept_button', 'yes_button', 'mine_position']
        
        messagebox.showinfo("Setup UI Positions", 
                           "You will now set up 6 button positions.\n\n"
                           "For each button, click on its location on screen.\n"
                           "Make sure the game UI is visible!")
        
        for i, (name, instruction) in enumerate(instructions):
            # Show instruction
            result = messagebox.askokcancel("Position Setup", 
                                           f"Step {i+1}/6: {name}\n\n{instruction}\n\n"
                                           "Click OK, then click on the button location.")
            if not result:
                return  # User cancelled
            
            # Wait for click
            self.status_label.config(text=f"Click on: {name}", fg="blue")
            from pynput import mouse
            
            clicked_pos = {'x': None, 'y': None}
            
            def on_click(x, y, button, pressed):
                if pressed:
                    clicked_pos['x'] = x
                    clicked_pos['y'] = y
                    return False  # Stop listener
            
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()
            
            # Save position
            self.ui_positions[position_keys[i]] = (clicked_pos['x'], clicked_pos['y'])
            print(f"{name} set to: ({clicked_pos['x']}, {clicked_pos['y']})")
        
        # Save all positions
        self.save_settings()
        self.status_label.config(text="UI Positions saved!", fg="green")
        messagebox.showinfo("Success", "All UI positions have been saved!\n\n"
                                      "The macro will now use these positions.")
        
        # Reset status after 2 seconds
        self.root.after(2000, lambda: self.status_label.config(
            text="Status: Running" if self.is_running else "Status: Stopped",
            fg="green" if self.is_running else "red"
        ))
    
    def exit_app(self):
        """Exit the application"""
        self.is_running = False  # Stop any running loops
        keyboard.unhook_all()  # Remove all hotkeys
        self.root.quit()  # Stop the mainloop
        self.root.destroy()  # Destroy the window
        sys.exit(0)  # Exit the program completely
    
    def rebind_key(self, action):
        """Rebind a key for an action"""
        self.status_label.config(text=f"Press a key for {action.replace('_', ' ').title()}...", fg="blue")
        
        def on_key_event(event):
            new_key = event.name.upper()
            # Update the keybinding
            self.keybindings[action] = new_key
            if self.save_settings():
                self.status_label.config(text=f"Rebound to {new_key}", fg="green")
                self.update_button_labels()
                self.refresh_hotkeys()  # Refresh hotkeys with new binding
                
                # Clear message after 2 seconds
                self.root.after(2000, lambda: self.status_label.config(
                    text="Status: Running" if self.is_running else "Status: Stopped",
                    fg="green" if self.is_running else "red"
                ))
            
            # Unhook this temporary listener
            keyboard.unhook(hook)
        
        # Hook to capture the next key press
        hook = keyboard.on_press(on_key_event, suppress=False)
    
    def update_button_labels(self):
        """Update GUI after rebinding - recreate widgets"""
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        # Recreate widgets with new keybindings
        self.create_widgets()
    
    def setup_hotkeys(self):
        """Setup global hotkeys that work even when minimized"""
        try:
            # Remove any existing hotkeys first
            keyboard.unhook_all()
            
            # Add hotkeys
            keyboard.add_hotkey(self.keybindings['start_stop'].lower(), self.toggle_start_stop)
            keyboard.add_hotkey(self.keybindings['change_area'].lower(), self.change_area)
            keyboard.add_hotkey(self.keybindings['exit'].lower(), self.exit_app)
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def refresh_hotkeys(self):
        """Refresh hotkeys after rebinding"""
        self.setup_hotkeys()


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
           AUTO SELL MACRO - TERMS OF USE
                    by AsphaltCake
═════════════════════════════════════════════════════

⚠️ IMPORTANT NOTICE ⚠️

This application is NOT a virus or malware!
  • Automation tool for Roblox Game "THE FORGE"
  • Antivirus may flag it (automates mouse/keyboard - this is normal)
  • Safe to use - built with Python & PyInstaller
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
        "Terms of Use - Auto Sell Macro",
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
    
    settings_file = settings_dir / "SELLsettings.json"
    
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
    app = SellMacro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
