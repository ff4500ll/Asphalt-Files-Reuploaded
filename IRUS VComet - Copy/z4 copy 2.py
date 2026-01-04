import time
import numpy as np
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import win32api
import win32con
import tkinter as tk


def fish_bot():
    """Automated fishing minigame controller"""
    
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
    
    # Create capture instance
    capture = WindowsCapture(
        cursor_capture=False,
        draw_border=True,
        monitor_index=None,
        window_name=None,
    )
    
    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        nonlocal green_found_ready, move_check_ready, move_check_initial_target, move_check_initial_bar
        nonlocal move_check_stable_count, move_check_click_state, move_check_last_target, move_check_last_bar
        nonlocal color_check_click_state, color_check_previous_bar, color_check_previous_target
        nonlocal color_check_previous_time, color_check_bar_velocity, color_check_target_velocity
        nonlocal color_check_bar_left, color_check_bar_right
        nonlocal color_check_min_reachable, color_check_max_reachable, color_check_bar_width
        nonlocal color_check_was_in_arrow_mode
        nonlocal arrow_previous_position, arrow_previous_side
        nonlocal arrow_estimated_bar_left, arrow_estimated_bar_right
        nonlocal arrow_previous_click_state
        
        # Convert frame to numpy array
        frame_array = np.array(frame.frame_buffer, dtype=np.uint8)
        
        # Check for green pixel in bottom-left corner
        frame_height, frame_width = frame_array.shape[:2]
        safety_top = int(frame_height * safety_top_percent)
        safety_right = int(frame_width * safety_right_percent)
        safety_box = frame_array[safety_top:frame_height, 0:safety_right, :3]
        
        # Check if green pixel exists
        b_match = np.abs(safety_box[:, :, 0].astype(np.int16) - green_check_color[2]) <= green_tolerance
        g_match = np.abs(safety_box[:, :, 1].astype(np.int16) - green_check_color[1]) <= green_tolerance
        r_match = np.abs(safety_box[:, :, 2].astype(np.int16) - green_check_color[0]) <= green_tolerance
        green_present = np.any(b_match & g_match & r_match)
        
        # Loop 1: Wait for green to disappear
        if not green_found_ready:
            if not green_present:
                green_found_ready = True
            return
        
        # Loop 2: Move check - scan for target and bar, exit if they move more than 5 pixels
        if not move_check_ready:
            # Check if green reappeared - exit immediately
            if green_present:
                if move_check_click_state:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    move_check_click_state = False
                capture_control.stop()
                return
            
            # Spam left click
            if move_check_click_state:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                move_check_click_state = False
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                move_check_click_state = True
            
            # Crop to fish area
            cropped = frame_array[
                fish_area["y"]:fish_area["y"] + fish_area["height"],
                fish_area["x"]:fish_area["x"] + fish_area["width"]
            ]
            
            height, width = cropped.shape[:2]
            
            left_x = None
            right_x = None
            
            # Scan for leftmost target pixel
            for y in range(height):
                for x in range(width):
                    pixel = cropped[y, x]
                    for target_color in target_colors:
                        if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                            abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                            abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                            left_x = fish_area["x"] + x
                            break
                    if left_x is not None:
                        break
                if left_x is not None:
                    break
            
            # Scan for rightmost target pixel
            if left_x is not None:
                for y in range(height):
                    for x in range(width - 1, -1, -1):
                        pixel = cropped[y, x]
                        for target_color in target_colors:
                            if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                                abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                                abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                                right_x = fish_area["x"] + x
                                break
                        if right_x is not None:
                            break
                    if right_x is not None:
                        break
                
                middle_x = (left_x + right_x) // 2
                
                # Scan for bar left edge
                bar_left_found = False
                bar_left_x = None
                for y in range(height):
                    for x in range(width):
                        pixel = cropped[y, x]
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
                
                # Scan for bar right edge
                bar_right_found = False
                bar_right_x = None
                if bar_left_found:
                    for y in range(height):
                        for x in range(width - 1, -1, -1):
                            pixel = cropped[y, x]
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
                    
                    # Stabilization phase
                    if move_check_initial_target is None:
                        if move_check_last_target is not None and move_check_last_bar is not None:
                            if middle_x == move_check_last_target and bar_middle == move_check_last_bar:
                                move_check_stable_count += 1
                            else:
                                move_check_stable_count = 1
                        else:
                            move_check_stable_count = 1
                        
                        move_check_last_target = middle_x
                        move_check_last_bar = bar_middle
                        
                        if move_check_stable_count >= move_check_stabilize_threshold:
                            move_check_initial_target = middle_x
                            move_check_initial_bar = bar_middle
                    else:
                        # Check if movement exceeded threshold
                        target_moved = abs(middle_x - move_check_initial_target) > 5
                        bar_moved = abs(bar_middle - move_check_initial_bar) > 5
                        
                        if target_moved or bar_moved:
                            if move_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                move_check_click_state = False
                            move_check_ready = True
                            return
                else:
                    move_check_stable_count = 0
            else:
                move_check_stable_count = 0
            
            return
        
        # Loop 3: Color check - Scan for target and bar
        # Release mouse if it's still pressed from loop 2
        if move_check_click_state:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            move_check_click_state = False
            color_check_click_state = False
        elif color_check_previous_bar is None:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            color_check_click_state = False
        
        # Crop to fish area
        cropped = frame_array[
            fish_area["y"]:fish_area["y"] + fish_area["height"],
            fish_area["x"]:fish_area["x"] + fish_area["width"]
        ]
        
        height, width = cropped.shape[:2]
        
        left_x = None
        right_x = None
        
        # Scan for leftmost target pixel
        for y in range(height):
            for x in range(width):
                pixel = cropped[y, x]
                for target_color in target_colors:
                    if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                        abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                        abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                        left_x = fish_area["x"] + x
                        break
                if left_x is not None:
                    break
            if left_x is not None:
                break
        
        # Scan for rightmost target pixel
        if left_x is not None:
            for y in range(height):
                for x in range(width - 1, -1, -1):
                    pixel = cropped[y, x]
                    for target_color in target_colors:
                        if (abs(int(pixel[0]) - target_color[0]) <= target_tolerance and 
                            abs(int(pixel[1]) - target_color[1]) <= target_tolerance and 
                            abs(int(pixel[2]) - target_color[2]) <= target_tolerance):
                            right_x = fish_area["x"] + x
                            break
                    if right_x is not None:
                        break
                if right_x is not None:
                    break
            
            middle_x = (left_x + right_x) // 2
            
            # Scan for bar left edge
            bar_left_found = False
            bar_left_x = None
            for y in range(height):
                for x in range(width):
                    pixel = cropped[y, x]
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
            
            # Scan for bar right edge
            bar_right_found = False
            bar_right_x = None
            if bar_left_found:
                for y in range(height):
                    for x in range(width - 1, -1, -1):
                        pixel = cropped[y, x]
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
            
            if bar_left_found and bar_right_found:
                bar_middle = (bar_left_x + bar_right_x) // 2
                
                # Check if we just transitioned from arrow mode
                skip_velocity_this_frame = color_check_was_in_arrow_mode
                color_check_was_in_arrow_mode = False
                
                # Calculate bar width and reachable bounds
                if color_check_min_reachable is None:
                    bar_width = bar_right_x - bar_left_x
                    color_check_bar_width = bar_width
                    color_check_bar_left = bar_left_x
                    color_check_bar_right = bar_right_x
                    color_check_min_reachable = fish_area["x"] + bar_width // 2
                    color_check_max_reachable = fish_area["x"] + fish_area["width"] - bar_width // 2
                
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
                
                # Calculate velocities
                current_time = time.perf_counter()
                if color_check_previous_bar is not None and color_check_previous_target is not None and not skip_velocity_this_frame:
                    delta_time = current_time - color_check_previous_time
                    if delta_time > 0:
                        raw_bar_velocity = (bar_middle - color_check_previous_bar) / delta_time
                        raw_target_velocity = (middle_x - color_check_previous_target) / delta_time
                        
                        color_check_bar_velocity = (velocity_smoothing * raw_bar_velocity + 
                                                    (1 - velocity_smoothing) * color_check_bar_velocity)
                        color_check_target_velocity = (velocity_smoothing * raw_target_velocity + 
                                                       (1 - velocity_smoothing) * color_check_target_velocity)
                
                # Update previous values
                color_check_previous_bar = bar_middle
                color_check_previous_target = middle_x
                color_check_previous_time = current_time
                
                # Calculate error and relative velocity
                error = bar_middle - middle_x
                relative_velocity = color_check_bar_velocity - color_check_target_velocity
                
                # Calculate stopping distance
                stopping_distance = abs(relative_velocity) * stopping_distance_multiplier
                
                # Detect panic mode
                target_speed = abs(color_check_target_velocity)
                bar_speed = abs(color_check_bar_velocity)
                panic_mode = target_speed > bar_speed * panic_speed_multiplier
                large_error = abs(error) > panic_large_error
                
                # Controller logic
                if middle_x < color_check_min_reachable:
                    # Target unreachable left
                    if color_check_click_state:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        color_check_click_state = False
                elif middle_x > color_check_max_reachable:
                    # Target unreachable right
                    if not color_check_click_state:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        color_check_click_state = True
                elif abs(error) <= deadband and abs(relative_velocity) < 50:
                    # In deadband - hover
                    if color_check_click_state:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        color_check_click_state = False
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        color_check_click_state = True
                elif (panic_mode and large_error) or (large_error and abs(relative_velocity) > panic_high_velocity):
                    # Panic mode
                    if error < 0:
                        if not color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            color_check_click_state = True
                    else:
                        if color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            color_check_click_state = False
                else:
                    # Bang-bang with stopping distance
                    if error < -stopping_distance:
                        if not color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            color_check_click_state = True
                    elif error > stopping_distance:
                        if color_check_click_state:
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            color_check_click_state = False
                    else:
                        # Within stopping distance - counter-thrust
                        if relative_velocity > 0:
                            if color_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                color_check_click_state = False
                        else:
                            if not color_check_click_state:
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                color_check_click_state = True
            else:
                # Bar not found - scan for arrow
                color_check_was_in_arrow_mode = True
                if arrow_colors and color_check_bar_width is not None:
                    arrow_left_found = False
                    arrow_left_x = None
                    for y in range(height):
                        for x in range(width):
                            pixel = cropped[y, x]
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
                    
                    arrow_right_found = False
                    arrow_right_x = None
                    if arrow_left_found:
                        for y in range(height):
                            for x in range(width - 1, -1, -1):
                                pixel = cropped[y, x]
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
                        arrow_side_switched = False
                        
                        # Virtual bar tracking using arrow position
                        if arrow_estimated_bar_left is None or arrow_estimated_bar_right is None:
                            # Initialize
                            if color_check_bar_left is not None and color_check_bar_right is not None:
                                dist_to_left = abs(arrow_middle - color_check_bar_left)
                                dist_to_right = abs(arrow_middle - color_check_bar_right)
                                
                                if dist_to_left < dist_to_right:
                                    arrow_previous_side = "left"
                                    arrow_estimated_bar_left = arrow_middle
                                    arrow_estimated_bar_right = arrow_middle + color_check_bar_width
                                else:
                                    arrow_previous_side = "right"
                                    arrow_estimated_bar_right = arrow_middle
                                    arrow_estimated_bar_left = arrow_middle - color_check_bar_width
                            else:
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
                            
                            # Update overlay arrows (arrow mode initialization)
                            if show_overlay:
                                arrow_y = fish_area["y"] - 20
                                # Target middle (green)
                                arrow_ids['target'] = update_or_create_arrow(
                                    arrow_ids.get('target'), 
                                    get_arrow_coords_down(middle_x, arrow_y), 
                                    '#00ff00'
                                )
                                # Arrow position (red)
                                arrow_ids['arrow'] = update_or_create_arrow(
                                    arrow_ids.get('arrow'), 
                                    get_arrow_coords_down(arrow_middle, arrow_y), 
                                    '#ff0000'
                                )
                                # Estimated bar edges (blue)
                                arrow_ids['bar_left'] = update_or_create_arrow(
                                    arrow_ids.get('bar_left'), 
                                    get_arrow_coords_down(arrow_estimated_bar_left, arrow_y), 
                                    '#0000ff'
                                )
                                arrow_ids['bar_right'] = update_or_create_arrow(
                                    arrow_ids.get('bar_right'), 
                                    get_arrow_coords_down(arrow_estimated_bar_right, arrow_y), 
                                    '#0000ff'
                                )
                                # Bar middle (lighter blue)
                                arrow_ids['bar_middle'] = update_or_create_arrow(
                                    arrow_ids.get('bar_middle'), 
                                    get_arrow_coords_down(bar_middle, arrow_y), 
                                    '#87CEEB'
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
                            
                            # Ensure mouse state matches the side
                            expected_state = (arrow_previous_side == "right")
                            if color_check_click_state != expected_state:
                                if expected_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                            
                            arrow_previous_click_state = color_check_click_state
                            
                            color_check_previous_bar = bar_middle
                            color_check_previous_target = middle_x
                            color_check_previous_time = time.perf_counter()
                        
                        if arrow_estimated_bar_left is not None and arrow_estimated_bar_right is not None:
                            bar_middle = (arrow_estimated_bar_left + arrow_estimated_bar_right) // 2
                            
                            # Update tracking if not initialization frame
                            if color_check_previous_bar is not None and arrow_previous_position != arrow_middle:
                                button_state_changed = (arrow_previous_click_state is not None and 
                                                       color_check_click_state != arrow_previous_click_state)
                                
                                # Determine current side
                                if button_state_changed:
                                    current_side = "right" if color_check_click_state else "left"
                                else:
                                    dist_to_est_left = abs(arrow_middle - arrow_estimated_bar_left)
                                    dist_to_est_right = abs(arrow_middle - arrow_estimated_bar_right)
                                    
                                    if dist_to_est_left < dist_to_est_right:
                                        current_side = "left"
                                    else:
                                        current_side = "right"
                                
                                # Check if arrow switched sides
                                arrow_side_switched = False
                                if current_side != arrow_previous_side and arrow_previous_position is not None:
                                    # Recalculate bar width only if distance-based switch
                                    if not button_state_changed:
                                        new_bar_width = abs(arrow_middle - arrow_previous_position)
                                        color_check_bar_width = new_bar_width
                                    
                                    # Update estimated bar edges
                                    if current_side == "left":
                                        arrow_estimated_bar_left = arrow_middle
                                        arrow_estimated_bar_right = arrow_middle + color_check_bar_width
                                    else:
                                        arrow_estimated_bar_right = arrow_middle
                                        arrow_estimated_bar_left = arrow_middle - color_check_bar_width
                                    
                                    arrow_previous_side = current_side
                                    arrow_side_switched = True
                                else:
                                    # Same side - drag bar with arrow
                                    arrow_movement = arrow_middle - arrow_previous_position
                                    arrow_estimated_bar_left += arrow_movement
                                    arrow_estimated_bar_right += arrow_movement
                                    bar_middle = (arrow_estimated_bar_left + arrow_estimated_bar_right) // 2
                                
                                arrow_previous_position = arrow_middle
                                arrow_previous_click_state = color_check_click_state
                            
                            # Update overlay arrows (arrow mode tracking)
                            if show_overlay:
                                arrow_y = fish_area["y"] - 20
                                # Target middle (green)
                                arrow_ids['target'] = update_or_create_arrow(
                                    arrow_ids.get('target'), 
                                    get_arrow_coords_down(middle_x, arrow_y), 
                                    '#00ff00'
                                )
                                # Arrow position (red)
                                arrow_ids['arrow'] = update_or_create_arrow(
                                    arrow_ids.get('arrow'), 
                                    get_arrow_coords_down(arrow_middle, arrow_y), 
                                    '#ff0000'
                                )
                                # Estimated bar edges (blue)
                                arrow_ids['bar_left'] = update_or_create_arrow(
                                    arrow_ids.get('bar_left'), 
                                    get_arrow_coords_down(arrow_estimated_bar_left, arrow_y), 
                                    '#0000ff'
                                )
                                arrow_ids['bar_right'] = update_or_create_arrow(
                                    arrow_ids.get('bar_right'), 
                                    get_arrow_coords_down(arrow_estimated_bar_right, arrow_y), 
                                    '#0000ff'
                                )
                                # Bar middle (lighter blue)
                                arrow_ids['bar_middle'] = update_or_create_arrow(
                                    arrow_ids.get('bar_middle'), 
                                    get_arrow_coords_down(bar_middle, arrow_y), 
                                    '#87CEEB'
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
                            
                            # Controller logic for arrow mode
                            current_time = time.perf_counter()
                            if color_check_previous_bar is not None and color_check_previous_target is not None and not arrow_side_switched:
                                delta_time = current_time - color_check_previous_time
                                if delta_time > 0:
                                    raw_bar_velocity = (bar_middle - color_check_previous_bar) / delta_time
                                    raw_target_velocity = (middle_x - color_check_previous_target) / delta_time
                                    
                                    color_check_bar_velocity = (velocity_smoothing * raw_bar_velocity + 
                                                                (1 - velocity_smoothing) * color_check_bar_velocity)
                                    color_check_target_velocity = (velocity_smoothing * raw_target_velocity + 
                                                                   (1 - velocity_smoothing) * color_check_target_velocity)
                            
                            color_check_previous_bar = bar_middle
                            color_check_previous_target = middle_x
                            color_check_previous_time = current_time
                            
                            error = bar_middle - middle_x
                            relative_velocity = color_check_bar_velocity - color_check_target_velocity
                            stopping_distance = abs(relative_velocity) * stopping_distance_multiplier
                            
                            target_speed = abs(color_check_target_velocity)
                            bar_speed = abs(color_check_bar_velocity)
                            panic_mode = target_speed > bar_speed * panic_speed_multiplier
                            large_error = abs(error) > panic_large_error
                            
                            # Controller logic (same as bar mode)
                            if middle_x < color_check_min_reachable:
                                if color_check_click_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                            elif middle_x > color_check_max_reachable:
                                if not color_check_click_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                            elif abs(error) <= deadband and abs(relative_velocity) < 50:
                                if color_check_click_state:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    color_check_click_state = False
                                else:
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    color_check_click_state = True
                            elif (panic_mode and large_error) or (large_error and abs(relative_velocity) > panic_high_velocity):
                                if error < 0:
                                    if not color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        color_check_click_state = True
                                else:
                                    if color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        color_check_click_state = False
                            else:
                                if error < -stopping_distance:
                                    if not color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                        color_check_click_state = True
                                elif error > stopping_distance:
                                    if color_check_click_state:
                                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                        color_check_click_state = False
                                else:
                                    if relative_velocity > 0:
                                        if color_check_click_state:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                            color_check_click_state = False
                                    else:
                                        if not color_check_click_state:
                                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                            color_check_click_state = True
        else:
            # Target not found - check for green to exit
            if green_present:
                if color_check_click_state:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    color_check_click_state = False
                capture_control.stop()
                return
    
    @capture.event
    def on_closed():
        # Cleanup overlay
        if overlay:
            try:
                overlay.destroy()
            except:
                pass
        if root:
            try:
                root.destroy()
            except:
                pass
    
    # Start capture
    try:
        capture.start()
    finally:
        # Cleanup overlay on exit
        if overlay:
            try:
                overlay.destroy()
            except:
                pass
        if root:
            try:
                root.destroy()
            except:
                pass


if __name__ == "__main__":
    fish_bot()
