import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
from datetime import datetime
from PIL import ImageGrab


class ScreenshotCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Collector for YOLO")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self.is_running = False
        self.screenshot_thread = None
        self.screenshot_count = 0
        self.model_folder = None
        
        # Bind keyboard shortcuts
        self.root.bind('<F1>', lambda e: self.toggle_capture())
        self.root.bind('<F2>', lambda e: self.stop_capture() if self.is_running else None)
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Model Name
        ttk.Label(main_frame, text="Model Name:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.model_name_var = tk.StringVar()
        self.model_name_entry = ttk.Entry(
            main_frame, textvariable=self.model_name_var, width=30, font=("Arial", 10)
        )
        self.model_name_entry.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Interval
        ttk.Label(main_frame, text="Interval (seconds):", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.interval_var = tk.StringVar(value="5")
        self.interval_entry = ttk.Entry(
            main_frame, textvariable=self.interval_var, width=30, font=("Arial", 10)
        )
        self.interval_entry.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Start/Stop Button
        self.start_button = ttk.Button(
            main_frame, text="Start (F1)", command=self.toggle_capture, width=20
        )
        self.start_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready | F1: Start | F2: Stop")
        self.status_label = ttk.Label(
            main_frame, textvariable=self.status_var, font=("Arial", 9), foreground="blue"
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
    
    def toggle_capture(self):
        if not self.is_running:
            self.start_capture()
        else:
            self.stop_capture()
    
    def start_capture(self):
        model_name = self.model_name_var.get().strip()
        
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name!")
            return
        
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for interval!")
            return
        
        # Create folder
        self.model_folder = os.path.join(os.getcwd(), model_name)
        if not os.path.exists(self.model_folder):
            os.makedirs(self.model_folder)
        
        # Find the last screenshot number in the folder to continue from
        existing_files = []
        if os.path.exists(self.model_folder):
            for filename in os.listdir(self.model_folder):
                if filename.endswith('.png'):
                    try:
                        num = int(filename[:-4])  # Remove .png and convert to int
                        existing_files.append(num)
                    except ValueError:
                        pass
        
        # Start from the next number after the highest existing
        self.screenshot_count = max(existing_files) if existing_files else 0
        
        # Update UI
        self.is_running = True
        self.start_button.config(text="Stop (F2)")
        self.model_name_entry.config(state="disabled")
        self.interval_entry.config(state="disabled")
        self.status_var.set(f"Capturing screenshots to '{model_name}' folder...")
        
        # Minimize the window
        self.root.iconify()
        
        # Start screenshot thread
        self.screenshot_thread = threading.Thread(
            target=self.capture_loop, args=(interval,), daemon=True
        )
        self.screenshot_thread.start()
    
    def stop_capture(self):
        self.is_running = False
        self.start_button.config(text="Start (F1)")
        self.model_name_entry.config(state="normal")
        self.interval_entry.config(state="normal")
        self.status_var.set(f"Stopped. Total screenshots: {self.screenshot_count}")
    
    def capture_loop(self, interval):
        while self.is_running:
            try:
                # Take screenshot
                screenshot = ImageGrab.grab()
                
                # Increment counter
                self.screenshot_count += 1
                
                # Save screenshot
                filename = f"{self.screenshot_count}.png"
                filepath = os.path.join(self.model_folder, filename)
                screenshot.save(filepath)
                
                # Update status
                self.status_var.set(
                    f"Captured {self.screenshot_count} screenshots | Last: {filename}"
                )
                
                # Wait for interval
                time.sleep(interval)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Screenshot failed: {str(e)}"))
                self.is_running = False
                break
        
        # Update UI when stopped
        if not self.is_running:
            self.root.after(0, self.stop_capture)


def main():
    root = tk.Tk()
    app = ScreenshotCollector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
