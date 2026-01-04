import pygetwindow as gw
import time
import win32gui
import win32con
import win32api
import keyboard


def setup_roblox():
    """Move Roblox to monitor 1, maximize it, and enter fullscreen if needed"""
    try:
        # Find Roblox window
        roblox_windows = gw.getWindowsWithTitle('Roblox')
        
        if not roblox_windows:
            print("Roblox window not found")
            return False
        
        # Get the first Roblox window
        roblox = roblox_windows[0]
        print(f"Found '{roblox.title}'")
        
        # Move to monitor 1 (position 0, 0 is top-left of primary monitor)
        roblox.moveTo(0, 0)
        time.sleep(0.1)
        
        # Maximize the window
        roblox.maximize()
        print("Moved to monitor 1 and maximized")
        
        time.sleep(0.3)  # Wait for window to settle
        
        # Check if it's already fullscreen
        hwnd = roblox._hWnd
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        
        is_fullscreen = (width >= screen_width and height >= screen_height)
        
        if is_fullscreen:
            print("Already in fullscreen mode")
        else:
            print("Entering fullscreen mode (pressing F11)...")
            roblox.activate()
            time.sleep(0.2)
            keyboard.press_and_release('f11')
            print("Pressed F11")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("Setting up Roblox...")
    success = setup_roblox()
    
    if success:
        print("\nDone!")
    else:
        print("\nFailed!")
    
    input("\nPress Enter to exit...")