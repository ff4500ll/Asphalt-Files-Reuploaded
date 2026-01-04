"""
Bar Physics Measurement Tool
Captures bar movement during hold/release cycles to measure acceleration rates.
Press Z to start recording.
"""

import json
import time
import mss
import keyboard
import win32api
import win32con
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox


def load_fish_box():
    """Load fish_box coordinates from irus_config.json"""
    try:
        with open("irus_config.json", "r") as f:
            config = json.load(f)
        
        fish_box = config["quad_boxes"]["fish_box"]
        return {
            "top": fish_box["y1"],
            "left": fish_box["x1"],
            "width": fish_box["x2"] - fish_box["x1"],
            "height": fish_box["y2"] - fish_box["y1"]
        }
    except Exception as e:
        print(f"ERROR: Could not load fish_box from irus_config.json: {e}")
        return None


def hold_left_click():
    """Press and hold left mouse button"""
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    print("[Input] Left mouse button pressed")


def release_left_click():
    """Release left mouse button"""
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("[Input] Left mouse button released")


def capture_frames(fish_box, duration_ms, action_name):
    """
    Capture frames from fish_box for specified duration.
    
    Args:
        fish_box: Dict with top, left, width, height
        duration_ms: How long to capture (milliseconds)
        action_name: Description for logging (e.g., "HOLD" or "RELEASE")
    
    Returns:
        List of (PIL.Image, timestamp) tuples
    """
    frames = []
    start_time = time.perf_counter()
    duration_sec = duration_ms / 1000.0
    
    print(f"[Capture] Recording {action_name} for {duration_ms}ms...")
    
    with mss.mss() as sct:
        while True:
            current_time = time.perf_counter()
            elapsed = current_time - start_time
            
            if elapsed >= duration_sec:
                break
            
            # Capture frame as fast as possible (no artificial delay)
            img = sct.grab(fish_box)
            pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
            frames.append((pil_img.copy(), current_time))
    
    print(f"[Capture] Captured {len(frames)} frames for {action_name}")
    return frames


def record_full_cycle(fish_box):
    """
    Record full hold/release cycle.
    
    Returns:
        Tuple of (hold_frames, release_frames)
    """
    print("\n" + "="*60)
    print("STARTING RECORDING CYCLE")
    print("="*60)
    
    # Phase 1: Hold for 700ms
    print("\n[Phase 1] Holding left click...")
    hold_left_click()
    hold_frames = capture_frames(fish_box, 700, "HOLD")
    release_left_click()
    
    time.sleep(0.1)  # Brief pause between phases
    
    # Phase 2: Release for 700ms
    print("\n[Phase 2] Releasing left click...")
    release_frames = capture_frames(fish_box, 700, "RELEASE")
    
    print("\n" + "="*60)
    print("RECORDING COMPLETE")
    print("="*60 + "\n")
    
    return hold_frames, release_frames


class FramePickerWindow:
    """Window for picking bar position in each frame"""
    
    def __init__(self, frames, phase_name):
        """
        Args:
            frames: List of (PIL.Image, timestamp) tuples
            phase_name: "HOLD" or "RELEASE"
        """
        self.frames = frames
        self.phase_name = phase_name
        self.current_frame_idx = 0
        self.bar_positions = []  # List of (frame_idx, timestamp, x_position)
        
        # Create window
        self.root = tk.Tk()
        self.root.title(f"Bar Position Picker - {phase_name} Phase")
        self.root.geometry("1200x600")
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text=f"Click on the LEFT EDGE of the bar in each frame\n"
                 f"Frame {self.current_frame_idx + 1} / {len(frames)} | Phase: {phase_name}\n"
                 f"Press 'N' to skip frame | Press 'Q' to quit",
            font=("Arial", 12),
            pady=10
        )
        instructions.pack()
        
        # Canvas for displaying frame
        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("n", lambda e: self.skip_frame())
        self.root.bind("q", lambda e: self.quit())
        
        # Display first frame
        self.show_current_frame()
        
        self.root.mainloop()
    
    def show_current_frame(self):
        """Display current frame on canvas"""
        if self.current_frame_idx >= len(self.frames):
            self.finish()
            return
        
        frame_img, timestamp = self.frames[self.current_frame_idx]
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(frame_img)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update title
        self.root.title(
            f"Bar Position Picker - {self.phase_name} Phase - "
            f"Frame {self.current_frame_idx + 1}/{len(self.frames)}"
        )
    
    def on_click(self, event):
        """Handle click on canvas"""
        x_position = event.x
        _, timestamp = self.frames[self.current_frame_idx]
        
        # Record position
        self.bar_positions.append((self.current_frame_idx, timestamp, x_position))
        print(f"[Pick] Frame {self.current_frame_idx}: Bar at x={x_position}")
        
        # Move to next frame
        self.current_frame_idx += 1
        self.show_current_frame()
    
    def skip_frame(self):
        """Skip current frame without recording position"""
        print(f"[Pick] Frame {self.current_frame_idx}: SKIPPED")
        self.current_frame_idx += 1
        self.show_current_frame()
    
    def quit(self):
        """Quit early"""
        print(f"[Pick] Quit early at frame {self.current_frame_idx}")
        self.root.quit()
        self.root.destroy()
    
    def finish(self):
        """All frames processed"""
        print(f"\n[Pick] {self.phase_name} phase complete: {len(self.bar_positions)} positions recorded")
        self.root.quit()
        self.root.destroy()
    
    def get_positions(self):
        """Return recorded positions"""
        return self.bar_positions


def calculate_physics(hold_positions, release_positions, start_timestamp):
    """
    Calculate acceleration from position data using kinematic curve fitting.
    
    For constant acceleration motion: x(t) = x0 + v0*t + 0.5*a*t²
    We fit this equation to the position data to extract acceleration.
    
    Args:
        hold_positions: List of (frame_idx, timestamp, x_position) for hold phase
        release_positions: List of (frame_idx, timestamp, x_position) for release phase
        start_timestamp: Timestamp of first hold frame
    
    Returns:
        Dict with calculated physics
    """
    print("\n" + "="*60)
    print("CALCULATING PHYSICS")
    print("="*60)
    
    results = {}
    
    # Process HOLD phase - use kinematic fitting
    if len(hold_positions) >= 3:
        print(f"\n[HOLD Phase] Analyzing {len(hold_positions)} positions...")
        
        # Extract time and position data
        times = []
        positions = []
        first_t = hold_positions[0][1]
        x0 = hold_positions[0][2]
        
        for frame_idx, timestamp, x_pos in hold_positions:
            t = timestamp - first_t  # Relative time
            times.append(t)
            positions.append(x_pos)
        
        print(f"  Start position: {x0:.1f}px")
        print(f"  End position: {positions[-1]:.1f}px")
        print(f"  Total displacement: {positions[-1] - x0:.1f}px")
        print(f"  Total time: {times[-1]*1000:.1f}ms")
        
        # Method 1: Use first and last position to estimate average acceleration
        # x = x0 + v0*t + 0.5*a*t²
        # Assuming v0 ≈ 0 (starting from rest or near-rest)
        # a ≈ 2*(x - x0) / t²
        total_displacement = positions[-1] - x0
        total_time = times[-1]
        
        if total_time > 0 and abs(total_displacement) > 5:  # Significant movement
            estimated_accel = 2 * total_displacement / (total_time ** 2)
            results['hold_acceleration'] = estimated_accel
            print(f"\n  HOLD ACCELERATION (from kinematics): {estimated_accel:.1f} px/s²")
        else:
            print(f"\n  HOLD Phase: Insufficient movement or time")
    else:
        print(f"\n[HOLD Phase] Not enough data points ({len(hold_positions)})")
    
    # Process RELEASE phase - measure leftward acceleration
    # Note: Release applies leftward acceleration while bar is still moving right
    # The bar slows down (rightward velocity decreases) then eventually moves left
    if len(release_positions) >= 3:
        print(f"\n[RELEASE Phase] Analyzing {len(release_positions)} positions...")
        
        # Extract time and position data
        times = []
        positions = []
        first_t = release_positions[0][1]
        x0 = release_positions[0][2]
        v0_estimated = 0  # Initial velocity from hold phase
        
        # Estimate initial velocity from hold phase
        if 'hold_acceleration' in results and len(hold_positions) > 0:
            hold_duration = hold_positions[-1][1] - hold_positions[0][1]
            v0_estimated = results['hold_acceleration'] * hold_duration
            print(f"  Estimated initial velocity (from hold): {v0_estimated:.1f} px/s (rightward)")
        
        for frame_idx, timestamp, x_pos in release_positions:
            t = timestamp - first_t  # Relative time
            times.append(t)
            positions.append(x_pos)
        
        print(f"  Start position: {x0:.1f}px")
        print(f"  End position: {positions[-1]:.1f}px")
        print(f"  Total displacement: {positions[-1] - x0:.1f}px")
        print(f"  Total time: {times[-1]*1000:.1f}ms")
        
        # The bar has initial rightward velocity, but leftward (negative) acceleration
        # x = x0 + v0*t + 0.5*a*t²
        # Solve for a: a = 2*(x - x0 - v0*t) / t²
        total_displacement = positions[-1] - x0
        total_time = times[-1]
        
        if total_time > 0:
            # This gives the leftward acceleration (should be negative)
            estimated_accel = 2 * (total_displacement - v0_estimated * total_time) / (total_time ** 2)
            results['release_acceleration'] = estimated_accel
            print(f"\n  RELEASE ACCELERATION (from kinematics): {estimated_accel:.1f} px/s²")
            print(f"  This is leftward acceleration (negative = accelerating left)")
            
            # For symmetric physics, magnitude should match hold acceleration
            if 'hold_acceleration' in results:
                hold_mag = abs(results['hold_acceleration'])
                release_mag = abs(estimated_accel)
                print(f"\n  Symmetry check:")
                print(f"    Hold magnitude:    {hold_mag:.1f} px/s²")
                print(f"    Release magnitude: {release_mag:.1f} px/s²")
                print(f"    Difference:        {abs(hold_mag - release_mag):.1f} px/s² ({abs(hold_mag - release_mag)/hold_mag*100:.1f}%)")
                
                # Use hold acceleration magnitude for both (assuming symmetric physics)
                results['release_acceleration'] = -hold_mag
                print(f"\n  Using symmetric physics assumption:")
                print(f"    Final release acceleration: {-hold_mag:.1f} px/s²")
        else:
            print(f"\n  RELEASE Phase: Insufficient time")
    else:
        print(f"\n[RELEASE Phase] Not enough data points ({len(release_positions)})")
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    if 'hold_acceleration' in results:
        print(f"Hold Acceleration:    {results['hold_acceleration']:>10.1f} px/s²")
    else:
        print("Hold Acceleration:    INSUFFICIENT DATA")
    
    if 'release_acceleration' in results:
        print(f"Release Acceleration: {results['release_acceleration']:>10.1f} px/s²")
    else:
        print("Release Acceleration: INSUFFICIENT DATA")
    print("="*60 + "\n")
    
    return results


def main():
    print("="*60)
    print("BAR PHYSICS MEASUREMENT TOOL")
    print("="*60)
    print("\nThis tool will:")
    print("1. Wait for you to press Z")
    print("2. Hold left click for 700ms and capture frames")
    print("3. Release left click for 700ms and capture frames")
    print("4. Let you click on each frame to mark the bar position")
    print("5. Calculate acceleration/deceleration rates")
    print("\nMake sure:")
    print("- Roblox is open and visible")
    print("- You're in the fishing minigame (or ready to start)")
    print("- fish_box is configured in irus_config.json")
    print("\nPress Z when ready...")
    print("="*60 + "\n")
    
    # Load fish box
    fish_box = load_fish_box()
    if fish_box is None:
        return
    
    print(f"Loaded fish_box: {fish_box}")
    
    # Wait for Z key
    print("\nWaiting for Z key press...")
    keyboard.wait('z')
    print("[Input] Z pressed! Starting NOW...")
    
    # Record frames
    hold_frames, release_frames = record_full_cycle(fish_box)
    
    # Get start timestamp for relative time calculations
    start_timestamp = hold_frames[0][1] if hold_frames else time.perf_counter()
    
    # Let user pick positions in HOLD frames
    print("\n" + "="*60)
    print("PHASE 1: MARKING HOLD FRAMES")
    print("="*60)
    print("Click on the LEFT EDGE of the bar in each frame.")
    print("The bar should be moving RIGHT (positive direction).")
    print("="*60 + "\n")
    
    hold_picker = FramePickerWindow(hold_frames, "HOLD")
    hold_positions = hold_picker.get_positions()
    
    # Let user pick positions in RELEASE frames
    print("\n" + "="*60)
    print("PHASE 2: MARKING RELEASE FRAMES")
    print("="*60)
    print("Click on the LEFT EDGE of the bar in each frame.")
    print("The bar should be moving LEFT (negative direction).")
    print("="*60 + "\n")
    
    release_picker = FramePickerWindow(release_frames, "RELEASE")
    release_positions = release_picker.get_positions()
    
    # Calculate physics
    results = calculate_physics(hold_positions, release_positions, start_timestamp)
    
    # Save results
    output_file = "bar_physics_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
