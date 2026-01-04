import json
import mss
from PIL import Image
from datetime import datetime

# Load config
with open("irus_config.json", 'r') as f:
    config = json.load(f)

# Get fish_box coordinates
fish_box = config["quad_boxes"]["fish_box"]

print(f"Taking screenshot of fish_box: {fish_box}")

# Capture screenshot
with mss.mss() as sct:
    region = {
        "top": fish_box["y1"],
        "left": fish_box["x1"],
        "width": fish_box["x2"] - fish_box["x1"],
        "height": fish_box["y2"] - fish_box["y1"]
    }
    
    screenshot = sct.grab(region)
    img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fish_box_screenshot_{timestamp}.png"
    img.save(filename)
    
    print(f"Screenshot saved as: {filename}")
    print(f"Size: {img.width}x{img.height} pixels")
