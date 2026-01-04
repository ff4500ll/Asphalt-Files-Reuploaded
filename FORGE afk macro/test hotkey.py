import time
import win32api
import win32con
import ctypes

print("="*50)
print("E Key Test Script - Testing Different Methods")
print("="*50)
print("\nThis script will test different methods of sending the E key.")
print("Each method will be tested with a 3 second delay between them.")
print("Press Ctrl+C to stop at any time.\n")

time.sleep(2)

try:
    # Method 1: win32api.keybd_event with direct key code
    print("\n[Method 1] win32api.keybd_event - Direct key code (0x45)")
    print("Pressing E...")
    win32api.keybd_event(0x45, 0, 0, 0)  # E down
    time.sleep(0.1)
    win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E up
    print("Done!")
    time.sleep(3)
    
    # Method 2: win32api.keybd_event with scan code
    print("\n[Method 2] win32api.keybd_event - With scan code")
    print("Pressing E...")
    scan_code = win32api.MapVirtualKey(0x45, 0)
    win32api.keybd_event(0x45, scan_code, 0, 0)  # E down
    time.sleep(0.1)
    win32api.keybd_event(0x45, scan_code, win32con.KEYEVENTF_KEYUP, 0)  # E up
    print("Done!")
    time.sleep(3)
    
    # Method 3: win32api.keybd_event with EXTENDEDKEY flag
    print("\n[Method 3] win32api.keybd_event - With EXTENDEDKEY flag")
    print("Pressing E...")
    win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)  # E down
    time.sleep(0.1)
    win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)  # E up
    print("Done!")
    time.sleep(3)
    
    # Method 4: SendInput using ctypes
    print("\n[Method 4] SendInput via ctypes")
    print("Pressing E...")
    
    # Define structures for SendInput
    PUL = ctypes.POINTER(ctypes.c_ulong)
    
    class KeyBdInput(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort),
                    ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", PUL)]
    
    class HardwareInput(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_ulong),
                    ("wParamL", ctypes.c_short),
                    ("wParamH", ctypes.c_ushort)]
    
    class MouseInput(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", PUL)]
    
    class Input_I(ctypes.Union):
        _fields_ = [("ki", KeyBdInput),
                    ("mi", MouseInput),
                    ("hi", HardwareInput)]
    
    class Input(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("ii", Input_I)]
    
    # Press E
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0x45, 0, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    time.sleep(0.1)
    
    # Release E
    ii_.ki = KeyBdInput(0x45, 0, win32con.KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    print("Done!")
    time.sleep(3)
    
    # Method 5: SendInput with scan code
    print("\n[Method 5] SendInput via ctypes - With scan code")
    print("Pressing E...")
    
    scan_code = win32api.MapVirtualKey(0x45, 0)
    extra = ctypes.c_ulong(0)
    
    # Press E
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, scan_code, 0x0008, 0, ctypes.pointer(extra))  # KEYEVENTF_SCANCODE = 0x0008
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    time.sleep(0.1)
    
    # Release E
    ii_.ki = KeyBdInput(0, scan_code, 0x0008 | win32con.KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    print("Done!")
    time.sleep(3)
    
    # Method 6: Longer hold time (0.5 seconds)
    print("\n[Method 6] win32api.keybd_event - Longer hold (0.5s)")
    print("Pressing E...")
    win32api.keybd_event(0x45, 0, 0, 0)  # E down
    time.sleep(0.5)
    win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E up
    print("Done!")
    time.sleep(3)
    
    # Method 7: Multiple rapid presses
    print("\n[Method 7] win32api.keybd_event - Multiple rapid presses (3x)")
    print("Pressing E 3 times rapidly...")
    for i in range(3):
        win32api.keybd_event(0x45, 0, 0, 0)  # E down
        time.sleep(0.05)
        win32api.keybd_event(0x45, 0, win32con.KEYEVENTF_KEYUP, 0)  # E up
        time.sleep(0.05)
    print("Done!")
    time.sleep(3)
    
    print("\n" + "="*50)
    print("All methods tested!")
    print("="*50)
    print("\nWhich method(s) worked for you?")
    
except KeyboardInterrupt:
    print("\n\nTest interrupted by user.")
except Exception as e:
    print(f"\n\nError occurred: {e}")

print("\nScript finished. Press Enter to exit...")
input()
