import sys
import keyboard
import threading
import pydirectinput

# Flag to control script execution
running = True

# Setup pydirectinput with zero pause (Method 8)
pydirectinput.PAUSE = 0

def exit_handler():
    """Listen for ESC key to exit"""
    global running
    keyboard.wait('esc')
    print("\n[ESC PRESSED] Exiting script...")
    running = False
    sys.exit(0)

def move_mouse_right():
    """Move mouse 500px right using Method 8 (pydirectinput)"""
    try:
        print("[F1 PRESSED] Moving mouse 500px right using Method 8 (pydirectinput)...")
        pydirectinput.moveRel(500, 0, relative=True)
        print("Movement complete!")
    except Exception as e:
        print(f"[ERROR] Failed to move mouse: {e}")

# Start ESC listener in background thread
exit_thread = threading.Thread(target=exit_handler, daemon=True)
exit_thread.start()

print("=" * 60)
print("ROBLOX FIRST PERSON CAMERA - F1 TEST")
print("=" * 60)
print("Press F1 to move mouse 500px right (Method 8: pydirectinput)")
print("Press ESC to exit")
print("=" * 60)

# Register F1 hotkey
keyboard.add_hotkey('f1', move_mouse_right)

# Keep script running
try:
    while running:
        keyboard.wait()
except KeyboardInterrupt:
    print("\nScript interrupted")
    sys.exit(0)
