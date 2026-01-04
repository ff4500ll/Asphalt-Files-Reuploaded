import tkinter as tk
from tkinter import filedialog, messagebox
import keyboard
import threading
import os
import sys
import webbrowser
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import mss
import time
import win32api
import win32con
import re
import numpy as np

# Fix for PyInstaller to find tessdata
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Safe print function for --noconsole mode
def safe_print(*args, **kwargs):
    """Print function that won't crash in --noconsole mode"""
    try:
        print(*args, **kwargs)
    except:
        pass

class AutoEnchantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Enchant - Made by AsphaltCake")
        self.root.geometry("600x750")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)
        
        # State variables
        self.is_running = False
        self.area_mode = False
        self.folder_path = tk.StringVar(value="C:/Program Files/Tesseract-OCR")
        
        # Screen coordinates for OCR area
        self.area_x1 = tk.IntVar(value=0)
        self.area_y1 = tk.IntVar(value=0)
        self.area_x2 = tk.IntVar(value=300)
        self.area_y2 = tk.IntVar(value=200)
        
        # Area selection window
        self.selection_window = None
        
        # Stored words list
        self.stored_words = []
        
        # OCR thread
        self.ocr_thread = None
        self.ocr_running = False
        
        # Timing variables
        self.after_e_delay = tk.IntVar(value=1000)
        self.after_click_delay = tk.IntVar(value=2500)
        self.after_ocr_delay = tk.IntVar(value=3500)
        
        # Check Tesseract on startup
        self.check_tesseract_on_startup()
        
        # Keybind variables
        self.key_start_stop = tk.StringVar(value="F1")
        self.key_change_area = tk.StringVar(value="F3")
        self.key_exit = tk.StringVar(value="F4")
        
        self.setup_ui()
        self.setup_hotkeys()
        
    def setup_ui(self):
        # Create a main canvas with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mouse wheel to scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now add all content to scrollable_frame instead of self.root
        # Title label
        title_label = tk.Label(scrollable_frame, text="Auto Enchant - Made by AsphaltCake", 
                              font=("Arial", 14, "bold"), fg="#2c3e50")
        title_label.pack(pady=10)
        
        # Folder directory section
        folder_frame = tk.LabelFrame(scrollable_frame, text="Folder Directory", padx=10, pady=10)
        folder_frame.pack(padx=20, pady=10, fill="x")
        
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=40)
        folder_entry.pack(side="left", padx=5)
        
        browse_btn = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="left")
        
        # Register validation command for integer-only input (for timing fields)
        vcmd = (self.root.register(self.validate_integer), '%P')
        
        # Keybinds section
        keybind_frame = tk.LabelFrame(scrollable_frame, text="Keybinds", padx=10, pady=10)
        keybind_frame.pack(padx=20, pady=10, fill="x")
        
        # Start/Stop keybind
        tk.Label(keybind_frame, text="Start/Stop:", width=15, anchor="w").grid(row=0, column=0, pady=5)
        start_stop_entry = tk.Entry(keybind_frame, textvariable=self.key_start_stop, width=10)
        start_stop_entry.grid(row=0, column=1, padx=5)
        tk.Button(keybind_frame, text="Rebind", command=lambda: self.rebind_key("start_stop")).grid(row=0, column=2)
        
        # Change Area keybind
        tk.Label(keybind_frame, text="Change Area:", width=15, anchor="w").grid(row=1, column=0, pady=5)
        change_area_entry = tk.Entry(keybind_frame, textvariable=self.key_change_area, width=10)
        change_area_entry.grid(row=1, column=1, padx=5)
        tk.Button(keybind_frame, text="Rebind", command=lambda: self.rebind_key("change_area")).grid(row=1, column=2)
        
        # Exit keybind
        tk.Label(keybind_frame, text="Exit:", width=15, anchor="w").grid(row=2, column=0, pady=5)
        exit_entry = tk.Entry(keybind_frame, textvariable=self.key_exit, width=10)
        exit_entry.grid(row=2, column=1, padx=5)
        tk.Button(keybind_frame, text="Rebind", command=lambda: self.rebind_key("exit")).grid(row=2, column=2)
        
        # Timing section
        timing_frame = tk.LabelFrame(scrollable_frame, text="Timing", padx=10, pady=10)
        timing_frame.pack(padx=20, pady=10, fill="x")
        
        # After E Delay
        e_delay_frame = tk.Frame(timing_frame)
        e_delay_frame.pack(fill="x", pady=2)
        tk.Label(e_delay_frame, text="After E Delay:", width=18, anchor="w").pack(side="left")
        tk.Entry(e_delay_frame, textvariable=self.after_e_delay, width=10, validate='key', validatecommand=vcmd).pack(side="left", padx=5)
        tk.Label(e_delay_frame, text="ms").pack(side="left")
        
        # After Click Delay
        click_delay_frame = tk.Frame(timing_frame)
        click_delay_frame.pack(fill="x", pady=2)
        tk.Label(click_delay_frame, text="After Click Delay:", width=18, anchor="w").pack(side="left")
        tk.Entry(click_delay_frame, textvariable=self.after_click_delay, width=10, validate='key', validatecommand=vcmd).pack(side="left", padx=5)
        tk.Label(click_delay_frame, text="ms").pack(side="left")
        
        # After OCR Delay
        ocr_delay_frame = tk.Frame(timing_frame)
        ocr_delay_frame.pack(fill="x", pady=2)
        tk.Label(ocr_delay_frame, text="After OCR Delay:", width=18, anchor="w").pack(side="left")
        tk.Entry(ocr_delay_frame, textvariable=self.after_ocr_delay, width=10, validate='key', validatecommand=vcmd).pack(side="left", padx=5)
        tk.Label(ocr_delay_frame, text="ms").pack(side="left")
        
        # Status section
        status_frame = tk.Frame(scrollable_frame)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Status: Stopped", 
                                     font=("Arial", 10), fg="red")
        self.status_label.pack()
        
        self.area_label = tk.Label(status_frame, text="Area Mode: Off", 
                                   font=("Arial", 10), fg="gray")
        self.area_label.pack()
        
        # Word Storage section
        word_frame = tk.LabelFrame(scrollable_frame, text="Stored Words", padx=10, pady=10)
        word_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Input area for new words
        input_frame = tk.Frame(word_frame)
        input_frame.pack(fill="x", pady=(0, 10))
        
        self.word_entry = tk.Entry(input_frame, width=30)
        self.word_entry.pack(side="left", padx=5)
        
        add_btn = tk.Button(input_frame, text="Add", command=self.add_word, bg="#4CAF50", fg="white")
        add_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(input_frame, text="Delete", command=self.delete_word, bg="#f44336", fg="white")
        delete_btn.pack(side="left", padx=5)
        
        # Listbox with scrollbar for stored words
        list_frame = tk.Frame(word_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.word_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=6)
        self.word_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.word_listbox.yview)
    
    def validate_integer(self, value):
        """Validate that input is a valid integer or empty"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def get_safe_int(self, int_var, default=0):
        """Safely get integer value from IntVar, return default if invalid"""
        try:
            return int_var.get()
        except:
            return default
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            # Validate the selected folder
            tesseract_exe = os.path.join(folder, "tesseract.exe")
            if not os.path.exists(tesseract_exe):
                messagebox.showerror("Error", "Tesseract.exe not found in the specified directory")
                self.folder_path.set("")
    
    def check_tesseract_on_startup(self):
        """Check if tesseract.exe exists on startup and prompt user if not found"""
        path = self.folder_path.get()
        tesseract_exe = os.path.join(path, "tesseract.exe")
        
        if not os.path.exists(tesseract_exe):
            # Ask user if they want to download
            response = messagebox.askyesno(
                "Tesseract Not Found",
                "Tesseract not found, would you like to download?"
            )
            
            if response:  # User clicked Yes
                webbrowser.open("https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe")
                messagebox.showinfo(
                    "Download Started",
                    "Tesseract installer download started. Please install it and restart the application."
                )
            else:  # User clicked No
                messagebox.showwarning(
                    "Tesseract Required",
                    "This macro uses Tesseract OCR, please point to correct directory or download"
                )
            
            # Clear the invalid path
            self.folder_path.set("")
    
    def validate_tesseract_path(self):
        """Check if tesseract.exe exists in the specified path"""
        path = self.folder_path.get()
        if path:
            tesseract_exe = os.path.join(path, "tesseract.exe")
            if not os.path.exists(tesseract_exe):
                messagebox.showerror("Error", "Tesseract.exe not found in the specified directory")
                self.folder_path.set("")
            else:
                # Valid path found
                return tesseract_exe
        return None
    
    def rebind_key(self, action):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Rebind {action.replace('_', ' ').title()}")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Press any key...", font=("Arial", 12)).pack(pady=20)
        
        def on_key_press(event):
            new_key = event.keysym
            if action == "start_stop":
                self.key_start_stop.set(new_key)
            elif action == "change_area":
                self.key_change_area.set(new_key)
            elif action == "exit":
                self.key_exit.set(new_key)
            
            dialog.destroy()
            self.update_hotkeys()
        
        dialog.bind("<Key>", on_key_press)
        dialog.focus_set()
    
    def setup_hotkeys(self):
        keyboard.add_hotkey(self.key_start_stop.get().lower(), self.toggle_start_stop)
        keyboard.add_hotkey(self.key_change_area.get().lower(), self.toggle_area)
        keyboard.add_hotkey(self.key_exit.get().lower(), self.exit_app)
    
    def update_hotkeys(self):
        keyboard.unhook_all_hotkeys()
        self.setup_hotkeys()
    
    def toggle_start_stop(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running", fg="green")
            # Start OCR thread
            self.start_ocr()
        else:
            self.status_label.config(text="Status: Stopped", fg="red")
            # Stop OCR thread
            self.stop_ocr()
    
    def start_ocr(self):
        """Start the OCR scanning thread"""
        # Validate tesseract path
        tesseract_path = self.validate_tesseract_path()
        if not tesseract_path:
            messagebox.showerror("Error", "Please specify a valid Tesseract directory")
            self.is_running = False
            self.status_label.config(text="Status: Stopped", fg="red")
            return
        
        # Set tesseract command
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Start OCR thread
        self.ocr_running = True
        self.ocr_thread = threading.Thread(target=self.ocr_loop, daemon=True)
        self.ocr_thread.start()
    
    def stop_ocr(self):
        """Stop the OCR scanning thread"""
        self.ocr_running = False
    
    def preprocess_for_dark_text(self, img):
        """Multiple preprocessing methods for dark colored text"""
        processed_images = []
        
        try:
            # Method 1: Just upscale
            width, height = img.size
            img_upscaled = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
            processed_images.append(("upscaled", img_upscaled))
            
            # Method 2: Grayscale + high contrast + upscale
            img_gray = img.convert('L')
            enhancer = ImageEnhance.Contrast(img_gray)
            img_contrast = enhancer.enhance(3.0)
            img_contrast = img_contrast.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
            processed_images.append(("grayscale+contrast", img_contrast))
            
            # Method 3: Invert colors + upscale (for dark text on light bg)
            img_inverted = img.convert('L')
            img_inverted = img_inverted.point(lambda p: 255 - p)
            img_inverted = img_inverted.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
            processed_images.append(("inverted", img_inverted))
            
            # Method 4: Extract blue channel (for dark blue text)
            if img.mode == 'RGB':
                r, g, b = img.split()
                # Invert blue channel to make dark blue text bright
                b_inverted = b.point(lambda p: 255 - p)
                b_upscaled = b_inverted.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                processed_images.append(("blue_channel_inverted", b_upscaled))
            
            # Method 5: Extract red channel (for dark red text)
            if img.mode == 'RGB':
                r, g, b = img.split()
                # Invert red channel to make dark red text bright
                r_inverted = r.point(lambda p: 255 - p)
                r_upscaled = r_inverted.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                processed_images.append(("red_channel_inverted", r_upscaled))
            
            # Method 6: Red channel with high contrast (for dark red)
            if img.mode == 'RGB':
                r, g, b = img.split()
                r_inverted = r.point(lambda p: 255 - p)
                enhancer = ImageEnhance.Contrast(r_inverted)
                r_contrast = enhancer.enhance(3.0)
                r_upscaled = r_contrast.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                processed_images.append(("red_channel_inverted_contrast", r_upscaled))
            
            # Method 7: Red channel only (not inverted) with contrast boost
            if img.mode == 'RGB':
                r, g, b = img.split()
                enhancer = ImageEnhance.Contrast(r)
                r_contrast = enhancer.enhance(4.0)
                r_upscaled = r_contrast.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                processed_images.append(("red_channel_contrast_only", r_upscaled))
            
            # Method 8: Red minus green/blue (isolate red text)
            if img.mode == 'RGB':
                r, g, b = img.split()
                # Subtract other channels to isolate red
                import numpy as np
                r_array = np.array(r, dtype=np.int16)
                g_array = np.array(g, dtype=np.int16)
                b_array = np.array(b, dtype=np.int16)
                
                # Red minus average of green and blue
                red_isolated = r_array - ((g_array + b_array) // 2)
                red_isolated = np.clip(red_isolated, 0, 255).astype(np.uint8)
                
                # Invert and enhance
                red_img = Image.fromarray(red_isolated)
                red_img = red_img.point(lambda p: 255 - p)
                enhancer = ImageEnhance.Contrast(red_img)
                red_img = enhancer.enhance(3.0)
                red_upscaled = red_img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
                processed_images.append(("red_isolated", red_upscaled))
            
            return processed_images
        except Exception as e:
            safe_print(f"Preprocessing error: {e}")
            # Return just upscaled original as fallback
            width, height = img.size
            return [("fallback", img.resize((width * 3, height * 3), Image.Resampling.LANCZOS))]
    
    def press_e_key(self):
        """Simulate pressing the E key"""
        keyboard.press_and_release('e')
    
    def left_click(self):
        """Simulate a left mouse click using win32api"""
        # Get current mouse position
        x, y = win32api.GetCursorPos()
        # Perform click at current position
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    
    def perform_ocr_check(self, sct):
        """Perform OCR and check for word match using simple approach"""
        # Get the screen coordinates (with safe getters)
        x1 = self.get_safe_int(self.area_x1, 0)
        y1 = self.get_safe_int(self.area_y1, 0)
        x2 = self.get_safe_int(self.area_x2, 300)
        y2 = self.get_safe_int(self.area_y2, 200)
        
        # Define the monitor region to capture
        monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
        
        # Capture the screen area using MSS
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image
        img_original = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Get multiple preprocessed versions
        processed_images = self.preprocess_for_dark_text(img_original)
        
        # Try OCR on each preprocessed version
        for method_name, img_to_test in processed_images:
            safe_print(f"\n=== Trying method: {method_name} ===")
            try:
                text = pytesseract.image_to_string(img_to_test)
                text_lower = text.lower()
                
                # Print extracted text for debugging
                safe_print(f"OCR Text:\n{text[:300]}")
                
                # Remove all non-alphabetic characters for matching
                text_clean = re.sub(r'[^a-z]', '', text_lower)
                safe_print(f"Cleaned: {text_clean[:150]}")
                
                # Check for exact matches
                for word in self.stored_words:
                    word_lower = word.lower()
                    safe_print(f"  Checking if '{word_lower}' in '{text_clean[:100]}'...")
                    if word_lower in text_clean:
                        safe_print(f"✓ Match found with {method_name}: {word}")
                        return word
                    else:
                        safe_print(f"  No match for '{word_lower}'")
            except Exception as e:
                safe_print(f"OCR error with {method_name}: {e}")
        
        return None
    
    def ocr_loop(self):
        """Main OCR loop that runs in a separate thread"""
        with mss.mss() as sct:
            while self.ocr_running:
                try:
                    # Step 1: Press E key
                    safe_print("Pressing E...")
                    self.press_e_key()
                    
                    # Step 2: Delay for "After E Delay" (with safe getter)
                    e_delay = self.get_safe_int(self.after_e_delay, 500) / 1000.0  # Convert ms to seconds
                    time.sleep(e_delay)
                    
                    # Step 3: Left click
                    safe_print("Left clicking...")
                    self.left_click()
                    
                    # Step 4: Delay for "After Click Delay" (with safe getter)
                    click_delay = self.get_safe_int(self.after_click_delay, 3000) / 1000.0  # Convert ms to seconds
                    time.sleep(click_delay)
                    
                    # Step 5: Perform OCR search and check if match
                    safe_print("Checking OCR...")
                    matched_word = self.perform_ocr_check(sct)
                    
                    if matched_word:
                        # Word found! Stop the loop
                        self.ocr_running = False
                        self.is_running = False
                        # Update status label
                        self.status_label.config(text=f"Successfully Found: {matched_word}", fg="blue")
                        safe_print(f"\n*** Successfully Found: {matched_word} ***")
                        return
                    else:
                        safe_print("No match found, continuing...")
                    
                    # Step 6: Delay for "After OCR Delay" before repeating
                    ocr_delay = self.get_safe_int(self.after_ocr_delay, 3500) / 1000.0  # Convert ms to seconds
                    safe_print(f"Waiting {ocr_delay}s before next cycle...\n")
                    time.sleep(ocr_delay)
                    
                except Exception as e:
                    safe_print(f"OCR Error: {e}")
                    time.sleep(1)
    
    def validate_tesseract_path(self):
        """Check if tesseract.exe exists in the specified path and return full path"""
        path = self.folder_path.get()
        if path:
            tesseract_exe = os.path.join(path, "tesseract.exe")
            if os.path.exists(tesseract_exe):
                return tesseract_exe
        return None
    
    def toggle_area(self):
        self.area_mode = not self.area_mode
        if self.area_mode:
            self.area_label.config(text="Area Mode: Selecting...", fg="orange")
            self.show_selection_window()
        else:
            self.area_label.config(text="Area Mode: Off", fg="gray")
            self.hide_selection_window()
    
    def show_selection_window(self):
        """Create a resizable, moveable transparent window for area selection"""
        if self.selection_window is not None:
            return
        
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-alpha', 0.5)  # Semi-transparent for dragging
        self.selection_window.attributes('-topmost', True)  # Always on top
        self.selection_window.overrideredirect(True)  # Remove window decorations
        
        # Set initial position and size from saved coordinates (with safe getters)
        x1 = self.get_safe_int(self.area_x1, 0)
        y1 = self.get_safe_int(self.area_y1, 0)
        x2 = self.get_safe_int(self.area_x2, 300)
        y2 = self.get_safe_int(self.area_y2, 200)
        width = x2 - x1
        height = y2 - y1
        
        self.selection_window.geometry(f"{width}x{height}+{x1}+{y1}")
        self.selection_window.configure(bg='white')
        
        # Create a canvas for the border
        self.canvas = tk.Canvas(self.selection_window, bg='white', highlightthickness=3, 
                          highlightbackground='red', highlightcolor='red')
        self.canvas.pack(fill='both', expand=True)
        
        # Create a label with instructions in the center (draggable area)
        self.label = tk.Label(self.canvas, text="Drag here to move\nResize from edges\nPress F2 to save", 
                        bg='white', fg='red', font=("Arial", 10, "bold"), cursor='fleur')
        self.label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Variables for dragging and resizing
        self.resize_data = {"edge": None, "x": 0, "y": 0, "start_w": 0, "start_h": 0, 
                           "start_x": 0, "start_y": 0, "dragging": False, "resizing": False}
        
        # Bind events for dragging from center
        self.label.bind("<Button-1>", self.on_center_press)
        self.label.bind("<B1-Motion>", self.on_center_drag)
        self.label.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind events for resizing from edges on the window itself
        self.selection_window.bind("<Motion>", self.update_cursor)
        self.selection_window.bind("<Button-1>", self.on_edge_press)
        self.selection_window.bind("<B1-Motion>", self.on_edge_drag)
        self.selection_window.bind("<ButtonRelease-1>", self.on_release)
    
    def hide_selection_window(self):
        """Save coordinates and destroy the selection window"""
        if self.selection_window is not None:
            # Get final position and size
            geometry = self.selection_window.geometry()
            # Parse geometry string: WIDTHxHEIGHT+X+Y
            parts = geometry.split('+')
            size_parts = parts[0].split('x')
            width = int(size_parts[0])
            height = int(size_parts[1])
            x = int(parts[1])
            y = int(parts[2])
            
            # Save coordinates
            self.area_x1.set(x)
            self.area_y1.set(y)
            self.area_x2.set(x + width)
            self.area_y2.set(y + height)
            
            self.selection_window.destroy()
            self.selection_window = None
            self.area_label.config(text="Area Mode: Saved", fg="blue")
    
    def on_center_press(self, event):
        """Start dragging the window from center"""
        self.resize_data["dragging"] = True
        self.resize_data["x"] = event.x_root
        self.resize_data["y"] = event.y_root
    
    def on_center_drag(self, event):
        """Move the window"""
        if self.resize_data["dragging"]:
            dx = event.x_root - self.resize_data["x"]
            dy = event.y_root - self.resize_data["y"]
            x = self.selection_window.winfo_x() + dx
            y = self.selection_window.winfo_y() + dy
            self.selection_window.geometry(f"+{x}+{y}")
            self.resize_data["x"] = event.x_root
            self.resize_data["y"] = event.y_root
    
    def on_release(self, event):
        """Stop dragging or resizing"""
        self.resize_data["dragging"] = False
        self.resize_data["resizing"] = False
    
    def update_cursor(self, event):
        """Update cursor based on position (edge detection for resizing)"""
        if self.resize_data["resizing"] or self.resize_data["dragging"]:
            return
        
        w = self.selection_window.winfo_width()
        h = self.selection_window.winfo_height()
        edge_size = 15
        
        # Check which edge/corner the mouse is near
        if event.x < edge_size and event.y < edge_size:
            self.selection_window.config(cursor="top_left_corner")
            self.resize_data["edge"] = "nw"
        elif event.x > w - edge_size and event.y < edge_size:
            self.selection_window.config(cursor="top_right_corner")
            self.resize_data["edge"] = "ne"
        elif event.x < edge_size and event.y > h - edge_size:
            self.selection_window.config(cursor="bottom_left_corner")
            self.resize_data["edge"] = "sw"
        elif event.x > w - edge_size and event.y > h - edge_size:
            self.selection_window.config(cursor="bottom_right_corner")
            self.resize_data["edge"] = "se"
        elif event.x < edge_size:
            self.selection_window.config(cursor="left_side")
            self.resize_data["edge"] = "w"
        elif event.x > w - edge_size:
            self.selection_window.config(cursor="right_side")
            self.resize_data["edge"] = "e"
        elif event.y < edge_size:
            self.selection_window.config(cursor="top_side")
            self.resize_data["edge"] = "n"
        elif event.y > h - edge_size:
            self.selection_window.config(cursor="bottom_side")
            self.resize_data["edge"] = "s"
        else:
            self.selection_window.config(cursor="")
            self.resize_data["edge"] = None
    
    def on_edge_press(self, event):
        """Start resizing from edge"""
        if self.resize_data["edge"]:
            self.resize_data["resizing"] = True
            self.resize_data["x"] = event.x_root
            self.resize_data["y"] = event.y_root
            self.resize_data["start_w"] = self.selection_window.winfo_width()
            self.resize_data["start_h"] = self.selection_window.winfo_height()
            self.resize_data["start_x"] = self.selection_window.winfo_x()
            self.resize_data["start_y"] = self.selection_window.winfo_y()
    
    def on_edge_drag(self, event):
        """Resize from edge"""
        if self.resize_data["resizing"]:
            edge = self.resize_data["edge"]
            dx = event.x_root - self.resize_data["x"]
            dy = event.y_root - self.resize_data["y"]
            
            new_w = self.resize_data["start_w"]
            new_h = self.resize_data["start_h"]
            new_x = self.resize_data["start_x"]
            new_y = self.resize_data["start_y"]
            
            # Handle resizing based on edge
            if 'e' in edge:
                new_w = max(50, self.resize_data["start_w"] + dx)
            if 'w' in edge:
                new_w = max(50, self.resize_data["start_w"] - dx)
                if new_w > 50:
                    new_x = self.resize_data["start_x"] + dx
            if 's' in edge:
                new_h = max(50, self.resize_data["start_h"] + dy)
            if 'n' in edge:
                new_h = max(50, self.resize_data["start_h"] - dy)
                if new_h > 50:
                    new_y = self.resize_data["start_y"] + dy
            
            self.selection_window.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
    
    def add_word(self):
        """Add a word to the stored words list (removes spaces)"""
        word = self.word_entry.get().strip()
        if word:
            # Remove all spaces from the word
            word_no_spaces = word.replace(" ", "")
            
            # Check if word already exists
            if word_no_spaces not in self.stored_words:
                self.stored_words.append(word_no_spaces)
                self.word_listbox.insert(tk.END, word_no_spaces)
                self.word_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Duplicate", f"'{word_no_spaces}' is already in the list")
    
    def delete_word(self):
        """Delete the selected word from the list"""
        selection = self.word_listbox.curselection()
        if selection:
            index = selection[0]
            self.stored_words.pop(index)
            self.word_listbox.delete(index)
        else:
            messagebox.showwarning("No Selection", "Please select a word to delete")
    
    def exit_app(self):
        keyboard.unhook_all_hotkeys()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoEnchantGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
