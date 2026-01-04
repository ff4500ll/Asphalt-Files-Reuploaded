import json
from PIL import ImageGrab
from datetime import datetime

# Load config
with open('irus_config.json', 'r') as f:
    config = json.load(f)

# Get fish_box coordinates
fish_box = config['quad_boxes']['fish_box']
x1, y1 = fish_box['x1'], fish_box['y1']
x2, y2 = fish_box['x2'], fish_box['y2']

# Take screenshot of the fish_box area
screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

# Save with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"fish_box_screenshot_{timestamp}.png"
screenshot.save(filename)

print(f"Screenshot saved as: {filename}")
print(f"Captured area: ({x1}, {y1}) to ({x2}, {y2})")
print(f"Size: {x2-x1}x{y2-y1} pixels")
