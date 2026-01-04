import os
import json
import cv2
import numpy as np
import mss
import keyboard
import time

# Color constants from v4.py
TARGET_LINE_COLOR_HEX = "0x434B5B"       # The moving line that must be followed
TARGET_LINE_COLOR_ALTERNATIVE_HEX = "0x151567"  # Alternative target line color
INDICATOR_ARROW_COLOR_HEX = "0xF1A81B"  # Indicator arrow color
BOX_COLOR_1_HEX = "0xF1F1F1"            # Box color 1
BOX_COLOR_2_HEX = "0xFFFFFF"            # Box color 2 (white)

def hex_to_bgr(hex_str):
    """Convert hex string (e.g., '0x434B5B') to BGR tuple for OpenCV"""
    hex_str = hex_str.replace('0x', '')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (b, g, r)  # OpenCV uses BGR

def get_bgr_bounds(bgr_color, tolerance):
    """Get lower and upper bounds for color matching with tolerance"""
    lower = np.array([max(0, c - tolerance) for c in bgr_color], dtype=np.uint8)
    upper = np.array([min(255, c + tolerance) for c in bgr_color], dtype=np.uint8)
    return lower, upper

class ColorScanTester:
    def __init__(self):
        # Load configuration
        self.config_file = os.path.join(os.path.dirname(__file__), "Config.txt")
        self.config = self.load_config()

        # Get fish_box coordinates
        self.fish_box = self.config.get("fish_box", {"x1": 100, "y1": 100, "x2": 300, "y2": 300})
        self.x1 = self.fish_box["x1"]
        self.y1 = self.fish_box["y1"]
        self.x2 = self.fish_box["x2"]
        self.y2 = self.fish_box["y2"]

        # Tolerances (from v4.py defaults)
        self.target_line_tol = 2
        self.indicator_arrow_tol = 5
        self.box_color_tol = 1

        # State
        self.should_exit = False
        self.show_masks = True  # Toggle to show individual masks (press 'M' to toggle)
        
        # Initialize mss for faster screen capture
        self.sct = mss.mss()

        print("=" * 60)
        print("Color Scan System - Live Detection (v4.py method)")
        print("=" * 60)
        print(f"Fish Box Area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print(f"Target Line Tolerance: {self.target_line_tol}")
        print(f"Indicator Arrow Tolerance: {self.indicator_arrow_tol}")
        print(f"Box Color Tolerance: {self.box_color_tol}")

    def load_config(self):
        """Load configuration from Config.txt"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"fish_box": {"x1": 100, "y1": 100, "x2": 300, "y2": 300}}

    def capture_screen_area(self):
        """Capture the fish_box area from screen using mss"""
        try:
            # Define monitor region
            monitor = {
                "top": self.y1,
                "left": self.x1,
                "width": self.x2 - self.x1,
                "height": self.y2 - self.y1
            }
            
            # Capture using mss
            sct_img = self.sct.grab(monitor)
            
            # Convert to numpy array and BGR format for OpenCV
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            return frame
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def process_color_detection(self, frame):
        """Process color detection using v4.py method with multiple masks"""
        height, width = frame.shape[:2]
        
        # Create empty combined mask
        combined_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Individual masks for counting pixels
        masks = {}
        
        # Mask 1: Target Line Color (Primary)
        color1_bgr = hex_to_bgr(TARGET_LINE_COLOR_HEX)
        lower1, upper1 = get_bgr_bounds(color1_bgr, self.target_line_tol)
        mask1 = cv2.inRange(frame, lower1, upper1)
        combined_mask = cv2.bitwise_or(combined_mask, mask1)
        masks['Target Line (Primary)'] = mask1
        
        # Mask 1 Alt: Target Line Color (Alternative)
        color1_alt_bgr = hex_to_bgr(TARGET_LINE_COLOR_ALTERNATIVE_HEX)
        lower1_alt, upper1_alt = get_bgr_bounds(color1_alt_bgr, self.target_line_tol)
        mask1_alt = cv2.inRange(frame, lower1_alt, upper1_alt)
        combined_mask = cv2.bitwise_or(combined_mask, mask1_alt)
        masks['Target Line (Alt)'] = mask1_alt
        
        # Mask 2: Indicator Arrow Color
        color2_bgr = hex_to_bgr(INDICATOR_ARROW_COLOR_HEX)
        lower2, upper2 = get_bgr_bounds(color2_bgr, self.indicator_arrow_tol)
        mask2 = cv2.inRange(frame, lower2, upper2)
        combined_mask = cv2.bitwise_or(combined_mask, mask2)
        masks['Indicator Arrow'] = mask2
        
        # Mask 3: Box Color 1 (0xF1F1F1)
        color3_bgr = hex_to_bgr(BOX_COLOR_1_HEX)
        lower3, upper3 = get_bgr_bounds(color3_bgr, self.box_color_tol)
        mask3 = cv2.inRange(frame, lower3, upper3)
        combined_mask = cv2.bitwise_or(combined_mask, mask3)
        masks['Box Color 1'] = mask3
        
        # Mask 4: Box Color 2 (0xFFFFFF - white)
        color4_bgr = hex_to_bgr(BOX_COLOR_2_HEX)
        lower4, upper4 = get_bgr_bounds(color4_bgr, self.box_color_tol)
        mask4 = cv2.inRange(frame, lower4, upper4)
        combined_mask = cv2.bitwise_or(combined_mask, mask4)
        masks['Box Color 2 (White)'] = mask4
        
        # Apply combined mask to show only detected colors
        masked_output = cv2.bitwise_and(frame, frame, mask=combined_mask)
        
        return masked_output, combined_mask, masks

    def run_live_detection(self):
        """Run live color detection on the fish_box area"""
        print("\n" + "=" * 60)
        print("Starting Live Color Detection")
        print("=" * 60)
        print("\nControls:")
        print("  M - Toggle mask display (show individual color masks)")
        print("  ESC or Q - Exit live detection")
        print(f"\nMonitoring area: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        print("\nStarting in 3 seconds...")
        time.sleep(3)

        fps = 0
        
        # Timing variables
        capture_time = 0
        color_detect_time = 0
        draw_time = 0

        try:
            while not self.should_exit:
                loop_start = time.time()
                
                # Capture screen area
                t1 = time.time()
                frame = self.capture_screen_area()
                if frame is None:
                    continue
                capture_time = (time.time() - t1) * 1000  # ms

                # Process color detection
                t2 = time.time()
                masked_output, combined_mask, individual_masks = self.process_color_detection(frame)
                color_detect_time = (time.time() - t2) * 1000  # ms
                
                t3 = time.time()
                
                # Count pixels for each mask
                pixel_counts = {}
                for name, mask in individual_masks.items():
                    pixel_counts[name] = np.sum(mask > 0)
                
                total_detected_pixels = np.sum(combined_mask > 0)
                
                # Draw information on the masked output
                cv2.putText(masked_output, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(masked_output, f"Total Detected: {total_detected_pixels} px", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                # Draw timing info
                y_offset = 80
                cv2.putText(masked_output, f"Capture: {capture_time:.1f}ms", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20
                cv2.putText(masked_output, f"Color Detect: {color_detect_time:.1f}ms", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                y_offset += 20
                cv2.putText(masked_output, f"Draw: {draw_time:.1f}ms", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Draw pixel counts for each color
                y_offset += 30
                for name, count in pixel_counts.items():
                    if count > 0:  # Only show colors that were detected
                        cv2.putText(masked_output, f"{name}: {count} px", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
                        y_offset += 18
                
                draw_time = (time.time() - t3) * 1000  # ms
                
                # Calculate FPS
                fps = 1.0 / (time.time() - loop_start)

                # Print timing to terminal
                total_time = capture_time + color_detect_time + draw_time
                
                # Build pixel count string for terminal output
                detected_colors = [f"{name}:{count}" for name, count in pixel_counts.items() if count > 0]
                pixel_info = " | ".join(detected_colors) if detected_colors else "None detected"
                
                print(f"FPS: {fps:5.1f} | Total: {total_time:5.1f}ms | Capture: {capture_time:4.1f}ms | Color: {color_detect_time:4.1f}ms | Draw: {draw_time:4.1f}ms | Pixels: {pixel_info}")

                # Display the masked output
                cv2.imshow('Color Scan Detection - Masked Output', masked_output)
                
                # Optionally show individual masks side-by-side
                if self.show_masks:
                    # Create a grid of individual masks
                    mask_list = []
                    for name, mask in individual_masks.items():
                        # Convert single-channel mask to 3-channel for display
                        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                        # Add label
                        cv2.putText(mask_colored, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                        cv2.putText(mask_colored, f"{pixel_counts[name]} px", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                        mask_list.append(mask_colored)
                    
                    # Stack masks in a 2x3 grid
                    if len(mask_list) >= 3:
                        row1 = np.hstack(mask_list[:3])
                        row2 = np.hstack(mask_list[3:] + [np.zeros_like(mask_list[0])] * (3 - len(mask_list[3:])))
                        mask_grid = np.vstack([row1, row2])
                        cv2.imshow('Individual Color Masks', mask_grid)

                # Set windows to always on top
                cv2.setWindowProperty('Color Scan Detection - Masked Output', cv2.WND_PROP_TOPMOST, 1)
                if self.show_masks:
                    cv2.setWindowProperty('Individual Color Masks', cv2.WND_PROP_TOPMOST, 1)

                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # Q or ESC
                    break
                elif key == ord('m') or key == ord('M'):  # M to toggle mask display
                    self.show_masks = not self.show_masks
                    if not self.show_masks:
                        cv2.destroyWindow('Individual Color Masks')
                    print(f"\n{'Enabled' if self.show_masks else 'Disabled'} individual mask display")

                # Check for keyboard interrupt
                if keyboard.is_pressed('esc'):
                    break

        except KeyboardInterrupt:
            print("\n\nDetection interrupted by user")
        finally:
            cv2.destroyAllWindows()
            self.sct.close()
            print("\n✓ Live detection stopped")

    def run(self):
        """Main execution flow"""
        print("\n✓ Starting color scan tester...")
        
        # Start live detection
        self.run_live_detection()

        print("\n" + "=" * 60)
        print("Program terminated")
        print("=" * 60)

def main():
    tester = ColorScanTester()
    tester.run()

if __name__ == "__main__":
    main()
