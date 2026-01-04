import time
import numpy as np
import mss
import win32api
import win32con
import tkinter as tk


def z():
    """Scans for color #434b5b and returns x coordinate if found"""
    
    # ============================================================================
    # MANUAL CONFIGURATION - EDIT THESE VALUES AS NEEDED
    # ============================================================================
    
    # Fish area coordinates (adjust for your screen resolution/game window position)
    fish_area = {"x": 765, "y": 1217, "width": 1032, "height": 38}
    
    # Target line colors (add more colors if needed)
    target_colors = [
        (0x5b, 0x4b, 0x43),  # #434b5b in BGR
    ]
    target_tolerance = 0  # Increase if target color varies slightly
    
    # Bar colors (add more colors if needed)
    bar_colors = [
        (0xf1, 0xf1, 0xf1),  # #f1f1f1 in BGR
        (0xff, 0xff, 0xff),  # #ffffff in BGR
    ]
    bar_tolerance = 0  # Increase if bar color varies slightly
    
    # Arrow colors (add more colors if needed)
    arrow_colors = [
        (0x87, 0x85, 0x84),  # #848587 in BGR
    ]
    arrow_tolerance = 0  # Increase if arrow color varies slightly
    
    # Green check settings (entry/exit condition)
    green_check_color = (155, 255, 155)  # RGB #9bff9b
    green_tolerance = 0  # Increase if green color varies slightly
    safety_top_percent = 0.85  # Check bottom 15% of screen
    safety_right_percent = 0.20  # Check left 20% of screen
    
    # Move check stabilization (loop 2)
    move_check_stabilize_threshold = 10  # Frames needed before considering positions stable
    
    # Controller tuning parameters (loop 3)
    stopping_distance_multiplier = 3.0  # Higher = brake earlier (reduce if too slow, increase if overshooting)
    deadband = 0  # Pixels around target considered "on target" (increase if oscillating)
    velocity_smoothing = 0.7  # Velocity smoothing (0.7 = 70% current, 30% previous)
    panic_speed_multiplier = 2.0  # Target speed multiplier that triggers panic mode
    panic_large_error = 50  # Distance (px) considered "far from target" for panic
    panic_high_velocity = 800  # Velocity threshold to keep panic active
    
    # Visual overlay
    show_overlay = True  # Set to False to disable visual arrows
    
    # ============================================================================
    # INTERNAL STATE VARIABLES - DO NOT EDIT
    # ============================================================================
    
    # Output logging
    output_log = []
    log_sequence = 0
    last_logged_state = None
    
    # State tracking
    green_found_ready = False
    move_check_ready = False
    
    # Move check tracking
    move_check_initial_target = None
    move_check_initial_bar = None
    move_check_stable_count = 0
    move_check_click_state = False
    move_check_last_target = None
    move_check_last_bar = None
    
    # Color check (loop 3) tracking controller variables
    color_check_click_state = False
    color_check_previous_bar = None
    color_check_previous_target = None
    color_check_previous_time = None
    color_check_bar_velocity = 0.0
    color_check_target_velocity = 0.0
    color_check_bar_left = None
    color_check_bar_right = None
    color_check_min_reachable = None
    color_check_max_reachable = None
    color_check_bar_width = None
    color_check_was_in_arrow_mode = False
    
    # Arrow-based virtual bar tracking
    arrow_previous_position = None
    arrow_previous_side = None
    arrow_estimated_bar_left = None
    arrow_estimated_bar_right = None
    arrow_previous_click_state = None
    
    # Visual overlay
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    overlay = None
    canvas = None
    arrow_ids = {}
    
    # Create overlay window only if enabled
    if show_overlay:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        overlay = tk.Toplevel(root)
        overlay.attributes('-topmost', True)
        overlay.attributes('-transparentcolor', 'black')
        overlay.attributes('-fullscreen', True)
        overlay.overrideredirect(True)
        overlay.configure(bg='black')
        
        canvas = tk.Canvas(overlay, width=screen_width, height=screen_height, 
                          bg='black', highlightthickness=0)
        canvas.pack()
    else:
        root = None
    
    def get_arrow_coords_down(x, y):
        """Get coordinates for downward pointing arrow"""
        size = 15
        return [x, y+size, x-size//2, y, x+size//2, y]
    
    def update_or_create_arrow(arrow_id, coords, color):
        """Update existing arrow or create new one"""
        if arrow_id:
            try:
                canvas.coords(arrow_id, *coords)
                return arrow_id
            except:
                return canvas.create_polygon(coords, fill=color, outline=color)
        else:
            return canvas.create_polygon(coords, fill=color, outline=color)
    
    # Result storage
    result = {"found": False, "x": None, "timing_ms": 0}
    start_time = time.perf_counter()
    
    # Create MSS instance for screen capture
    sct = mss.mss()
    
    # Get screen dimensions for green check area
    monitor = sct.monitors[1]  # Primary monitor
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    
    # Calculate green check region (bottom-left corner)
    safety_top = int(screen_height * safety_top_percent)
    safety_right = int(screen_width * safety_right_percent)
    green_check_region = {
        "left": 0,
        "top": safety_top,
        "width": safety_right,
        "height": screen_height - safety_top
    }
    
    # Fish area region for MSS capture
    fish_region = {
        "left": fish_area["x"],
        "top": fish_area["y"],
        "width": fish_area["width"],
        "height": fish_area["height"]
    }
    
    # Main capture loop
    running = True
    while running:
        frame_start = time.perf_counter()
        
        # Capture green check area
        green_screenshot = sct.grab(green_check_region)
        green_array = np.array(green_screenshot, dtype=np.uint8)[:, :, :3]  # Remove alpha channel, keep BGR
        
        # Check if green pixel exists (MSS uses BGRA, so B=0, G=1, R=2)
        b_match = np.abs(green_array[:, :, 0].astype(np.int16) - green_check_color[2]) <= green_tolerance
        g_match = np.abs(green_array[:, :, 1].astype(np.int16) - green_check_color[1]) <= green_tolerance
        r_match = np.abs(green_array[:, :, 2].astype(np.int16) - green_check_color[0]) <= green_tolerance
        green_present = np.any(b_match & g_match & r_match)
        
        # First loop: Wait for green to disappear, then exit to next loop
        if not green_found_ready:
            if not green_present:
                # Green disappeared, exit this loop and proceed to move check
                green_found_ready = True
                print("Green check: Green disappeared, starting move check")
            # Keep scanning for green to disappear
            continue
        
        # Second loop: Move check - scan for target and bar, exit if they move more than 5 pixels
        if not move_check_ready:
            # Check if green reappeared - exit immediately
            if green_present:
                # Release mouse if holding before exiting
                if move_check_click_state:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    move_check_click_state = False
                print("Move check: Green reappeared, exiting")
                running = False
                break
            
            # Spam left click - alternate between press and release
            if move_check_click_state:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                move_check_click_state = False
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                move_check_click_state = True
            
            # Capture fish area directly
            fish_screenshot = sct.grab(fish_region)
            cropped = np.array(fish_screenshot, dtype=np.uint8)[:, :, :3]  # Remove alpha channel, keep BGR
            
            # Get dimensions
            height, width = cropped.shape[:2]
            
            left_x = None
            right_x = None
            
            # Scan left to right, row by row for leftmost
            for y in range(height):
                for x in range(width):
                    pixel = cropped[y, x]
                    # Check if pixel matches target colors with tolerance
                    for target_color in target_colors:
                        if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                            abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                            abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                            # Found leftmost!
                            left_x = fish_area["x"] + x
                            break
                    if left_x is not None:
                        break
                if left_x is not None:
                    break
            
            # If found, scan right to left for rightmost
            if left_x is not None:
                for y in range(height):
                    for x in range(width - 1, -1, -1):
                        pixel = cropped[y, x]
                        # Check if pixel matches target colors with tolerance
                        for target_color in target_colors:
                            if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                                abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                                abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                                # Found rightmost!
                                right_x = fish_area["x"] + x
                                break
                        if right_x is not None:
                            break
                    if right_x is not None:
                        break
                
                # Calculate middle
                middle_x = (left_x + right_x) // 2
                
                # Now scan from left to right for Bar Left colors
                bar_left_found = False
                bar_left_x = None
                for y in range(height):
                    for x in range(width):  # Scan entire width left to right
                        pixel = cropped[y, x]
                        # Check against all Bar colors with tolerance
                        for bar_color in bar_colors:
                            if (abs(int(pixel[0]) - bar_color[0]) <= bar_tolerance and 
                                abs(int(pixel[1]) - bar_color[1]) <= bar_tolerance and 
                                abs(int(pixel[2]) - bar_color[2]) <= bar_tolerance):
                                bar_left_found = True
                                bar_left_x = fish_area["x"] + x
                                break
                        if bar_left_found:
                            break
                    if bar_left_found:
                        break
                
                # Now scan from right to left for Bar Right colors
                bar_right_found = False
                bar_right_x = None
                if bar_left_found:
                    for y in range(height):
                        for x in range(width - 1, -1, -1):  # Scan right to left
                            pixel = cropped[y, x]
                            # Check against all Bar colors with tolerance
                            for bar_color in bar_colors:
                                if (abs(int(pixel[0]) - bar_color[0]) <= bar_tolerance and 
                                    abs(int(pixel[1]) - bar_color[1]) <= bar_tolerance and 
                                    abs(int(pixel[2]) - bar_color[2]) <= bar_tolerance):
                                    bar_right_found = True
                                    bar_right_x = fish_area["x"] + x
                                    break
                            if bar_right_found:
                                break
                        if bar_right_found:
                            break
                
                # Check if we have valid target and bar readings
                if bar_left_found and bar_right_found:
                    bar_middle = (bar_left_x + bar_right_x) // 2
                    
                    # Update overlay arrows (loop 2 - move check)
                    if show_overlay:
                        arrow_y = fish_area["y"] - 20
                        # Target middle (green)
                        arrow_ids['target'] = update_or_create_arrow(
                            arrow_ids.get('target'), 
                            get_arrow_coords_down(middle_x, arrow_y), 
                            '#00ff00'
                        )
                        # Bar left edge (blue)
                        arrow_ids['bar_left'] = update_or_create_arrow(
                            arrow_ids.get('bar_left'), 
                            get_arrow_coords_down(bar_left_x, arrow_y), 
                            '#0000ff'
                        )
                        # Bar right edge (blue)
                        arrow_ids['bar_right'] = update_or_create_arrow(
                            arrow_ids.get('bar_right'), 
                            get_arrow_coords_down(bar_right_x, arrow_y), 
                            '#0000ff'
                        )
                        # Bar middle (lighter blue)
                        arrow_ids['bar_middle'] = update_or_create_arrow(
                            arrow_ids.get('bar_middle'), 
                            get_arrow_coords_down(bar_middle, arrow_y), 
                            '#87CEEB'
                        )
                        canvas.update()
                    
                    # Stabilization phase - need 10 stable readings before setting initial positions
                    if move_check_initial_target is None:
                        bar_middle = (bar_left_x + bar_right_x) // 2
                        
                        # Check if positions match the last reading
                        if move_check_last_target is not None and move_check_last_bar is not None:
                            if middle_x == move_check_last_target and bar_middle == move_check_last_bar:
                                # Positions match, increment counter
                                move_check_stable_count += 1
                            else:
                                # Positions changed, reset counter
                                move_check_stable_count = 1
                        else:
                            # First reading, start counter
                            move_check_stable_count = 1
                        
                        # Update last positions
                        move_check_last_target = middle_x
                        move_check_last_bar = bar_middle
                        
                        if move_check_stable_count >= move_check_stabilize_threshold:
                            # Set initial positions after stabilization
                            move_check_initial_target = middle_x
                            move_check_initial_bar = bar_middle
                            print(f"Move check: Stabilized! Initial positions - T: {middle_x} | B: {bar_middle}")
                        else:
                            timing = (time.perf_counter() - frame_start) * 1000
                            print(f"Move check - Stabilizing ({move_check_stable_count}/{move_check_stabilize_threshold}) T: {middle_x} | B: {bar_middle} | {timing:.2f}ms")
                    else:
                        # Check if movement exceeded threshold
                        bar_middle = (bar_left_x + bar_right_x) // 2
                        target_moved = abs(middle_x - move_check_initial_target) > 5
                        bar_moved = abs(bar_middle - move_check_initial_bar) > 5
                        
                        if target_moved or bar_moved:
                            # Release mouse before exiting
                            if move_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                move_check_click_state = False
                            move_check_ready = True
                            output_log.append(f"{log_sequence}|TRANSITION|MoveCheck->ColorCheck")
                            log_sequence += 1
                            print(f"Move check: Movement detected (>5 pixels), starting color check")
                            continue
                        
                        timing = (time.perf_counter() - frame_start) * 1000
                        print(f"Move check - T: {middle_x} | B: {bar_middle} | {timing:.2f}ms")
                else:
                    # No valid bar found, reset stabilization count
                    move_check_stable_count = 0
                    timing = (time.perf_counter() - frame_start) * 1000
                    print(f"Move check - T: {middle_x} | B: N/A | {timing:.2f}ms")
            else:
                # No target found, reset stabilization count
                move_check_stable_count = 0
                timing = (time.perf_counter() - frame_start) * 1000
                print(f"Move check - T: N/A | B: N/A | {timing:.2f}ms")
            
            continue
        
        # Third loop: Color check - Scan for target and bar
        # Release mouse if it's still pressed from loop 2 and sync color_check_click_state
        if move_check_click_state:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            move_check_click_state = False
            color_check_click_state = False  # Sync the color check state to match
        # Ensure mouse is actually released at start of color check (safety check)
        elif color_check_previous_bar is None:
            # First frame of color check - ensure mouse is released
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            color_check_click_state = False
        
        # Capture fish area directly
        fish_screenshot = sct.grab(fish_region)
        cropped = np.array(fish_screenshot, dtype=np.uint8)[:, :, :3]  # Remove alpha channel, keep BGR
        
        # Get dimensions
        height, width = cropped.shape[:2]
        
        left_x = None
        right_x = None
        
        # Scan left to right, row by row for leftmost
        for y in range(height):
            for x in range(width):
                pixel = cropped[y, x]
                # Check if pixel matches target colors with tolerance
                for target_color in target_colors:
                    if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                        abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                        abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                        # Found leftmost!
                        left_x = fish_area["x"] + x
                        break
                if left_x is not None:
                    break
            if left_x is not None:
                break
        
        # If found, scan right to left for rightmost
        if left_x is not None:
            for y in range(height):
                for x in range(width - 1, -1, -1):
                    pixel = cropped[y, x]
                    # Check if pixel matches target colors with tolerance
                    for target_color in target_colors:
                        if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                            abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                            abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                            # Found rightmost!
                            right_x = fish_area["x"] + x
                            break
                    if right_x is not None:
                        break
                if right_x is not None:
                    break
            
            # Calculate middle
            middle_x = (left_x + right_x) // 2
            
            # Now scan from left to right for Bar Left colors
            bar_left_found = False
            bar_left_x = None
            for y in range(height):
                for x in range(width):  # Scan entire width left to right
                    pixel = cropped[y, x]
                    # Check against all Bar colors with tolerance
                    for bar_color in bar_colors:
                        if (abs(int(pixel[0]) - bar_color[0]) <= bar_tolerance and 
                            abs(int(pixel[1]) - bar_color[1]) <= bar_tolerance and 
                            abs(int(pixel[2]) - bar_color[2]) <= bar_tolerance):
                            bar_left_found = True
                            bar_left_x = fish_area["x"] + x
                            break
                    if bar_left_found:
                        break
                if bar_left_found:
                    break
            
            # Now scan from right to left for Bar Right colors
            bar_right_found = False
            bar_right_x = None
            if bar_left_found:
                for y in range(height):
                    for x in range(width - 1, -1, -1):  # Scan right to left
                        pixel = cropped[y, x]
                        # Check against all Bar colors with tolerance
                        for bar_color in bar_colors:
                            if (abs(int(pixel[0]) - bar_color[0]) <= bar_tolerance and 
                                abs(int(pixel[1]) - bar_color[1]) <= bar_tolerance and 
                                abs(int(pixel[2]) - bar_color[2]) <= bar_tolerance):
                                bar_right_found = True
                                bar_right_x = fish_area["x"] + x
                                break
                        if bar_right_found:
                            break
                    if bar_right_found:
                        break
            
            timing = (time.perf_counter() - frame_start) * 1000
            if bar_left_found and bar_right_found:
                bar_middle = (bar_left_x + bar_right_x) // 2
                
                # Check if we just transitioned from arrow mode to bar mode
                skip_velocity_this_frame = color_check_was_in_arrow_mode
                color_check_was_in_arrow_mode = False  # We're in bar mode now
                
                # Calculate bar width and reachable bounds (only once)
                if color_check_min_reachable is None:
                    bar_width = bar_right_x - bar_left_x
                    color_check_bar_width = bar_width  # Store for arrow-based estimation
                    color_check_bar_left = bar_left_x
                    color_check_bar_right = bar_right_x
                    # Min reachable = left edge of area + half bar width
                    color_check_min_reachable = fish_area["x"] + bar_width // 2
                    # Max reachable = right edge of area - half bar width
                    color_check_max_reachable = fish_area["x"] + fish_area["width"] - bar_width // 2
                    print(f"Color check: Bar width = {bar_width}, Reachable range = [{color_check_min_reachable}, {color_check_max_reachable}]")
                
                # Update overlay arrows (bar mode)
                if show_overlay:
                    arrow_y = fish_area["y"] - 20
                    # Target middle (green)
                    arrow_ids['target'] = update_or_create_arrow(
                        arrow_ids.get('target'), 
                        get_arrow_coords_down(middle_x, arrow_y), 
                        '#00ff00'
                    )
                    # Bar left edge (blue)
                    arrow_ids['bar_left'] = update_or_create_arrow(
                        arrow_ids.get('bar_left'), 
                        get_arrow_coords_down(bar_left_x, arrow_y), 
                        '#0000ff'
                    )
                    # Bar right edge (blue)
                    arrow_ids['bar_right'] = update_or_create_arrow(
                        arrow_ids.get('bar_right'), 
                        get_arrow_coords_down(bar_right_x, arrow_y), 
                        '#0000ff'
                    )
                    # Bar middle (lighter blue)
                    arrow_ids['bar_middle'] = update_or_create_arrow(
                        arrow_ids.get('bar_middle'), 
                        get_arrow_coords_down(bar_middle, arrow_y), 
                        '#87CEEB'
                    )
                    # Min reachable threshold (yellow)
                    arrow_ids['min_reach'] = update_or_create_arrow(
                        arrow_ids.get('min_reach'), 
                        get_arrow_coords_down(color_check_min_reachable, arrow_y), 
                        '#ffff00'
                    )
                    # Max reachable threshold (yellow)
                    arrow_ids['max_reach'] = update_or_create_arrow(
                        arrow_ids.get('max_reach'), 
                        get_arrow_coords_down(color_check_max_reachable, arrow_y), 
                        '#ffff00'
                    )
                    canvas.update()
                
                # Calculate velocities (skip if we just transitioned from arrow mode)
                current_time = time.perf_counter()
                if color_check_previous_bar is not None and color_check_previous_target is not None and not skip_velocity_this_frame:
                    delta_time = current_time - color_check_previous_time
                    if delta_time > 0:
                        # Calculate raw velocities
                        raw_bar_velocity = (bar_middle - color_check_previous_bar) / delta_time
                        raw_target_velocity = (middle_x - color_check_previous_target) / delta_time
                        
                        # Smooth velocities
                        color_check_bar_velocity = (velocity_smoothing * raw_bar_velocity + 
                                                    (1 - velocity_smoothing) * color_check_bar_velocity)
                        color_check_target_velocity = (velocity_smoothing * raw_target_velocity + 
                                                       (1 - velocity_smoothing) * color_check_target_velocity)
                
                # Update previous values
                color_check_previous_bar = bar_middle
                color_check_previous_target = middle_x
                color_check_previous_time = current_time
                
                # Calculate error and relative velocity
                error = bar_middle - middle_x  # Positive = bar is right of target
                relative_velocity = color_check_bar_velocity - color_check_target_velocity
                
                # Calculate stopping distance based on relative velocity
                stopping_distance = abs(relative_velocity) * stopping_distance_multiplier
                
                # Detect if target made a sudden jump (panic mode for fast reaction)
                target_speed = abs(color_check_target_velocity)
                bar_speed = abs(color_check_bar_velocity)
                panic_mode = target_speed > bar_speed * panic_speed_multiplier
                large_error = abs(error) > panic_large_error
                
                # Determine action based on bang-bang controller with velocity prediction
                action = "NONE"
                
                # Check if target is unreachable at edges
                if middle_x < color_check_min_reachable:
                    # Target is too far left, rest at left edge
                    if not color_check_click_state:
                        action = "RELEASE (target unreachable left)"
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        color_check_click_state = False
                        action = "RELEASE (target unreachable left)"
                elif middle_x > color_check_max_reachable:
                    # Target is too far right, rest at right edge
                    if color_check_click_state:
                        action = "HOLD (target unreachable right)"
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        color_check_click_state = True
                        action = "HOLD (target unreachable right)"
                elif abs(error) <= deadband and abs(relative_velocity) < 50:
                    # In deadband and moving slow - rapid alternating to hover
                    if color_check_click_state:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        color_check_click_state = False
                        action = "HOVER-RELEASE"
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        color_check_click_state = True
                        action = "HOVER-HOLD"
                elif (panic_mode and large_error) or (large_error and abs(relative_velocity) > panic_high_velocity):
                    # PANIC MODE: Stay in panic if:
                    # 1. Target moving fast AND we're far away, OR
                    # 2. We're far away AND moving too fast (prevents overshoot during tween deceleration)
                    if error < 0:
                        # Target jumped right, hold to chase it
                        if not color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            color_check_click_state = True
                            action = "PANIC HOLD (chase right)"
                        else:
                            action = "PANIC HOLD (chasing right)"
                    else:
                        # Target jumped left, release to chase it
                        if color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            color_check_click_state = False
                            action = "PANIC RELEASE (chase left)"
                        else:
                            action = "PANIC RELEASE (chasing left)"
                else:
                    # Outside deadband - use bang-bang with stopping distance
                    if error < -stopping_distance:
                        # Bar is left of target (beyond stopping distance), need to move right
                        if not color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            color_check_click_state = True
                            action = "HOLD (accelerate right)"
                        else:
                            action = "HOLD (continue right)"
                    elif error > stopping_distance:
                        # Bar is right of target (beyond stopping distance), need to move left
                        if color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            color_check_click_state = False
                            action = "RELEASE (accelerate left)"
                        else:
                            action = "RELEASE (continue left)"
                    else:
                        # Within stopping distance - counter-thrust to slow down
                        if relative_velocity > 0:
                            # Moving right relative to target, apply left thrust
                            if color_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                color_check_click_state = False
                                action = "RELEASE (brake right)"
                            else:
                                action = "RELEASE (braking)"
                        else:
                            # Moving left relative to target, apply right thrust
                            if not color_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                color_check_click_state = True
                                action = "HOLD (brake left)"
                            else:
                                action = "HOLD (braking)"
                
                # Structured logging: Only log state changes, transitions, or significant events
                current_state = f"BAR|T{middle_x}|B{bar_middle}|E{error:+.0f}|V{relative_velocity:+.0f}|{action}"
                if current_state != last_logged_state or abs(error) > 100 or panic_mode:
                    output_log.append(f"{log_sequence}|{current_state}|SD{stopping_distance:.0f}|{timing:.1f}ms")
                    last_logged_state = current_state
                log_sequence += 1
                print(f"Color check - T: {middle_x} | B: {bar_middle} | E: {error:+.0f} | V: {relative_velocity:+.0f} | SD: {stopping_distance:.0f} | {action} | {timing:.2f}ms")
            else:
                # Bar not found - scan for arrow colors instead (only if arrow_colors is not empty)
                color_check_was_in_arrow_mode = True  # Mark that we're in arrow mode
                if arrow_colors and color_check_bar_width is not None:
                    arrow_left_found = False
                    arrow_left_x = None
                    for y in range(height):
                        for x in range(width):  # Scan entire width left to right
                            pixel = cropped[y, x]
                            # Check against all Arrow colors with tolerance
                            for arrow_color in arrow_colors:
                                if (abs(int(pixel[0]) - arrow_color[0]) <= arrow_tolerance and 
                                    abs(int(pixel[1]) - arrow_color[1]) <= arrow_tolerance and 
                                    abs(int(pixel[2]) - arrow_color[2]) <= arrow_tolerance):
                                    arrow_left_found = True
                                    arrow_left_x = fish_area["x"] + x
                                    break
                            if arrow_left_found:
                                break
                        if arrow_left_found:
                            break
                    
                    # Now scan from right to left for Arrow Right colors
                    arrow_right_found = False
                    arrow_right_x = None
                    if arrow_left_found:
                        for y in range(height):
                            for x in range(width - 1, -1, -1):  # Scan right to left
                                pixel = cropped[y, x]
                                # Check against all Arrow colors with tolerance
                                for arrow_color in arrow_colors:
                                    if (abs(int(pixel[0]) - arrow_color[0]) <= arrow_tolerance and 
                                        abs(int(pixel[1]) - arrow_color[1]) <= arrow_tolerance and 
                                        abs(int(pixel[2]) - arrow_color[2]) <= arrow_tolerance):
                                        arrow_right_found = True
                                        arrow_right_x = fish_area["x"] + x
                                        break
                                if arrow_right_found:
                                    break
                            if arrow_right_found:
                                break
                    
                    if arrow_left_found and arrow_right_found:
                        arrow_middle = (arrow_left_x + arrow_right_x) // 2
                        arrow_side_switched = False  # Initialize at the start of arrow tracking
                        
                        # Virtual bar tracking using arrow position
                        if arrow_estimated_bar_left is None or arrow_estimated_bar_right is None:
                            # First time arrow is detected, initialize estimated bar position
                            # Determine which side arrow is closer to
                            if color_check_bar_left is not None and color_check_bar_right is not None:
                                dist_to_left = abs(arrow_middle - color_check_bar_left)
                                dist_to_right = abs(arrow_middle - color_check_bar_right)
                                
                                if dist_to_left < dist_to_right:
                                    # Arrow is on left side
                                    arrow_previous_side = "left"
                                    arrow_estimated_bar_left = arrow_middle
                                    arrow_estimated_bar_right = arrow_middle + color_check_bar_width
                                else:
                                    # Arrow is on right side
                                    arrow_previous_side = "right"
                                    arrow_estimated_bar_right = arrow_middle
                                    arrow_estimated_bar_left = arrow_middle - color_check_bar_width
                            else:
                                # No previous bar info, just guess based on middle of area
                                area_middle = fish_area["x"] + fish_area["width"] // 2
                                if arrow_middle < area_middle:
                                    arrow_previous_side = "left"
                                    arrow_estimated_bar_left = arrow_middle
                                    arrow_estimated_bar_right = arrow_middle + color_check_bar_width
                                else:
                                    arrow_previous_side = "right"
                                    arrow_estimated_bar_right = arrow_middle
                                    arrow_estimated_bar_left = arrow_middle - color_check_bar_width
                            
                            arrow_previous_position = arrow_middle
                            bar_middle = (arrow_estimated_bar_left + arrow_estimated_bar_right) // 2
                            
                            # When transitioning to arrow mode, ensure mouse state matches the side we're on
                            # Left side = released, Right side = held
                            expected_state = (arrow_previous_side == "right")
                            if color_check_click_state != expected_state:
                                if expected_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                            
                            arrow_previous_click_state = color_check_click_state  # Track initial state
                            output_log.append(f"{log_sequence}|TRANSITION|Bar->Arrow|Side{arrow_previous_side}|W{color_check_bar_width}|State{color_check_click_state}")
                            log_sequence += 1
                            
                            # Initialize previous values for velocity calculation
                            color_check_previous_bar = bar_middle
                            color_check_previous_target = middle_x
                            color_check_previous_time = time.perf_counter()
                            
                            print(f"Color check - T: {middle_x} | B(arrow-init): {bar_middle} | Side: {arrow_previous_side} | {timing:.2f}ms")
                            
                            # arrow_side_switched already initialized above - continue to controller logic
                        
                        if arrow_estimated_bar_left is not None and arrow_estimated_bar_right is not None:
                            # Calculate bar_middle from estimated edges (needed for both init and tracking)
                            bar_middle = (arrow_estimated_bar_left + arrow_estimated_bar_right) // 2
                            
                            # Only update tracking if not initialization frame
                            if color_check_previous_bar is not None and arrow_previous_position != arrow_middle:
                                # Check if button state changed
                                button_state_changed = (arrow_previous_click_state is not None and 
                                                       color_check_click_state != arrow_previous_click_state)
                                
                                # Determine current side
                                if button_state_changed:
                                    # Button state changed - determine side from the NEW button state
                                    # Release (False) = left side, Hold (True) = right side
                                    current_side = "right" if color_check_click_state else "left"
                                else:
                                    # No button state change - determine side from distance to estimated edges
                                    dist_to_est_left = abs(arrow_middle - arrow_estimated_bar_left)
                                    dist_to_est_right = abs(arrow_middle - arrow_estimated_bar_right)
                                    
                                    if dist_to_est_left < dist_to_est_right:
                                        current_side = "left"
                                    else:
                                        current_side = "right"
                            
                                # Check if arrow switched sides
                                arrow_side_switched = False
                                if current_side != arrow_previous_side and arrow_previous_position is not None:
                                    # Recalculate bar width ONLY if switch was due to distance (physical jump)
                                    # Button state changes should NOT recalculate width
                                    if not button_state_changed:
                                        # Arrow physically jumped to other side - recalculate bar width
                                        new_bar_width = abs(arrow_middle - arrow_previous_position)
                                        color_check_bar_width = new_bar_width
                                        output_log.append(f"{log_sequence}|ARROW_SWITCH|{arrow_previous_side}->{current_side}|W{new_bar_width}|Reason:distance")
                                        log_sequence += 1
                                        print(f"Color check - Arrow switched from {arrow_previous_side} to {current_side} (reason: distance), new width: {new_bar_width}")
                                    else:
                                        # Button state changed - just update side tracking, keep existing width
                                        state_info = f"({arrow_previous_click_state}->{color_check_click_state})"
                                        output_log.append(f"{log_sequence}|ARROW_SWITCH|{arrow_previous_side}->{current_side}|W{color_check_bar_width}|Reason:button_state{state_info}")
                                        log_sequence += 1
                                        print(f"Color check - Arrow switched from {arrow_previous_side} to {current_side} (reason: button_state{state_info}), width unchanged: {color_check_bar_width}")
                                    
                                    # Update estimated bar edges based on new side
                                    if current_side == "left":
                                        arrow_estimated_bar_left = arrow_middle
                                        arrow_estimated_bar_right = arrow_middle + color_check_bar_width
                                    else:
                                        arrow_estimated_bar_right = arrow_middle
                                        arrow_estimated_bar_left = arrow_middle - color_check_bar_width
                                    
                                    arrow_previous_side = current_side
                                    arrow_side_switched = True  # Flag to skip velocity update
                                else:
                                    # Same side, bar is moving - drag bar along with arrow
                                    arrow_movement = arrow_middle - arrow_previous_position
                                    arrow_estimated_bar_left += arrow_movement
                                    arrow_estimated_bar_right += arrow_movement
                                    bar_middle = (arrow_estimated_bar_left + arrow_estimated_bar_right) // 2
                                
                                arrow_previous_position = arrow_middle
                                arrow_previous_click_state = color_check_click_state  # Update tracked state
                            
                            # Now run the controller with estimated bar position
                            # Calculate velocities (skip if arrow just switched sides)
                            current_time = time.perf_counter()
                            if color_check_previous_bar is not None and color_check_previous_target is not None and not arrow_side_switched:
                                delta_time = current_time - color_check_previous_time
                                if delta_time > 0:
                                    # Calculate raw velocities
                                    raw_bar_velocity = (bar_middle - color_check_previous_bar) / delta_time
                                    raw_target_velocity = (middle_x - color_check_previous_target) / delta_time
                                    
                                    # Smooth velocities
                                    color_check_bar_velocity = (velocity_smoothing * raw_bar_velocity + 
                                                                (1 - velocity_smoothing) * color_check_bar_velocity)
                                    color_check_target_velocity = (velocity_smoothing * raw_target_velocity + 
                                                                   (1 - velocity_smoothing) * color_check_target_velocity)
                            
                            # Update previous values
                            color_check_previous_bar = bar_middle
                            color_check_previous_target = middle_x
                            color_check_previous_time = current_time
                            
                            # Calculate error and relative velocity
                            error = bar_middle - middle_x  # Positive = bar is right of target
                            relative_velocity = color_check_bar_velocity - color_check_target_velocity
                            
                            # Calculate stopping distance based on relative velocity
                            stopping_distance = abs(relative_velocity) * stopping_distance_multiplier
                            
                            # Update overlay arrows (arrow mode)
                            if show_overlay:
                                arrow_y = fish_area["y"] - 20
                                # Target middle (green)
                                arrow_ids['target'] = update_or_create_arrow(
                                    arrow_ids.get('target'), 
                                    get_arrow_coords_down(middle_x, arrow_y), 
                                    '#00ff00'
                                )
                                # Arrow left edge (purple)
                                arrow_ids['arrow_left'] = update_or_create_arrow(
                                    arrow_ids.get('arrow_left'), 
                                    get_arrow_coords_down(arrow_left_x, arrow_y), 
                                    '#ff00ff'
                                )
                                # Arrow right edge (purple)
                                arrow_ids['arrow_right'] = update_or_create_arrow(
                                    arrow_ids.get('arrow_right'), 
                                    get_arrow_coords_down(arrow_right_x, arrow_y), 
                                    '#ff00ff'
                                )
                                # Arrow middle (magenta)
                                arrow_ids['arrow_middle'] = update_or_create_arrow(
                                    arrow_ids.get('arrow_middle'), 
                                    get_arrow_coords_down(arrow_middle, arrow_y), 
                                    '#ff0088'
                                )
                                # Estimated bar left (cyan)
                                arrow_ids['bar_left'] = update_or_create_arrow(
                                    arrow_ids.get('bar_left'), 
                                    get_arrow_coords_down(arrow_estimated_bar_left, arrow_y), 
                                    '#00ffff'
                                )
                                # Estimated bar right (cyan)
                                arrow_ids['bar_right'] = update_or_create_arrow(
                                    arrow_ids.get('bar_right'), 
                                    get_arrow_coords_down(arrow_estimated_bar_right, arrow_y), 
                                    '#00ffff'
                                )
                                # Estimated bar middle (lighter cyan)
                                arrow_ids['bar_middle'] = update_or_create_arrow(
                                    arrow_ids.get('bar_middle'), 
                                    get_arrow_coords_down(bar_middle, arrow_y), 
                                    '#88ffff'
                                )
                                # Min/Max reachable (yellow)
                                arrow_ids['min_reach'] = update_or_create_arrow(
                                    arrow_ids.get('min_reach'), 
                                    get_arrow_coords_down(color_check_min_reachable, arrow_y), 
                                    '#ffff00'
                                )
                                arrow_ids['max_reach'] = update_or_create_arrow(
                                    arrow_ids.get('max_reach'), 
                                    get_arrow_coords_down(color_check_max_reachable, arrow_y), 
                                    '#ffff00'
                                )
                                canvas.update()
                            
                            # Detect if target made a sudden jump (panic mode for fast reaction)
                            target_speed = abs(color_check_target_velocity)
                            bar_speed = abs(color_check_bar_velocity)
                            panic_mode = target_speed > bar_speed * panic_speed_multiplier
                            large_error = abs(error) > panic_large_error
                            
                            # Determine action based on bang-bang controller with velocity prediction
                            action = "NONE"
                            
                            # Check if target is unreachable at edges
                            if middle_x < color_check_min_reachable:
                                # Target is too far left, rest at left edge
                                if not color_check_click_state:
                                    action = "RELEASE (target unreachable left)"
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                                    action = "RELEASE (target unreachable left)"
                            elif middle_x > color_check_max_reachable:
                                # Target is too far right, rest at right edge
                                if color_check_click_state:
                                    action = "HOLD (target unreachable right)"
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                                    action = "HOLD (target unreachable right)"
                            elif abs(error) <= deadband and abs(relative_velocity) < 50:
                                # In deadband and moving slow - rapid alternating to hover
                                if color_check_click_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                                    action = "HOVER-RELEASE"
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                                    action = "HOVER-HOLD"
                            elif (panic_mode and large_error) or (large_error and abs(relative_velocity) > panic_high_velocity):
                                # PANIC MODE: Stay in panic if:
                                # 1. Target moving fast AND we're far away, OR
                                # 2. We're far away AND moving too fast (prevents overshoot during tween deceleration)
                                if error < 0:
                                    # Target jumped right, hold to chase it
                                    if not color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        color_check_click_state = True
                                        action = "PANIC HOLD (chase right)"
                                    else:
                                        action = "PANIC HOLD (chasing right)"
                                else:
                                    # Target jumped left, release to chase it
                                    if color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        color_check_click_state = False
                                        action = "PANIC RELEASE (chase left)"
                                    else:
                                        action = "PANIC RELEASE (chasing left)"
                            else:
                                # Outside deadband - use bang-bang with stopping distance
                                if error < -stopping_distance:
                                    # Bar is left of target, need to move right
                                    if not color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        color_check_click_state = True
                                        action = "HOLD (accelerate right)"
                                    else:
                                        action = "HOLD (continue right)"
                                elif error > stopping_distance:
                                    # Bar is right of target, need to move left
                                    if color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        color_check_click_state = False
                                        action = "RELEASE (accelerate left)"
                                    else:
                                        action = "RELEASE (continue left)"
                                else:
                                    # Within stopping distance - counter-thrust to slow down
                                    if relative_velocity > 0:
                                        # Moving right relative to target, apply left thrust
                                        if color_check_click_state:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                            color_check_click_state = False
                                            action = "RELEASE (brake right)"
                                        else:
                                            action = "RELEASE (braking)"
                                    else:
                                        # Moving left relative to target, apply right thrust
                                        if not color_check_click_state:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                            color_check_click_state = True
                                            action = "HOLD (brake left)"
                                        else:
                                            action = "HOLD (braking)"
                            
                            # Structured logging for arrow mode: Always log (arrow mode is critical)
                            current_state = f"ARROW|T{middle_x}|B{bar_middle}|E{error:+.0f}|V{relative_velocity:+.0f}|{action}"
                            output_log.append(f"{log_sequence}|{current_state}|SD{stopping_distance:.0f}|{timing:.1f}ms")
                            last_logged_state = current_state
                            log_sequence += 1
                            print(f"Color check - T: {middle_x} | B(arrow): {bar_middle} | E: {error:+.0f} | V: {relative_velocity:+.0f} | SD: {stopping_distance:.0f} | {action} | {timing:.2f}ms")
                    elif arrow_left_found:
                        print(f"Color check - T: {middle_x} | B: N/A | A: Left only | {timing:.2f}ms")
                    else:
                        print(f"Color check - T: {middle_x} | B: N/A | {timing:.2f}ms")
                else:
                    # arrow_colors is empty, just print bar not found
                    print(f"Color check - T: {middle_x} | B: N/A | {timing:.2f}ms")
        else:
            # Target not found - check for green to exit
            if green_present:
                # Release mouse if holding before exiting
                if color_check_click_state:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    color_check_click_state = False
                print("Color check: Green reappeared, exiting")
                running = False
                break
            
            # Green not found, continue looping
            timing = (time.perf_counter() - frame_start) * 1000
            print(f"Color check - T: N/A | B: N/A | {timing:.2f}ms")
    
    # Clean up
    try:
        sct.close()
    except:
        pass
    
    # Write output log to file
    with open('zOUTPUT.txt', 'w') as f:
        f.write('\n'.join(output_log))
    print(f"\nLogged {len(output_log)} entries to zOUTPUT.txt")


if __name__ == "__main__":
    z()
