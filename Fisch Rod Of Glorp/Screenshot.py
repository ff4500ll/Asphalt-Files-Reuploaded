import json
import os
import time
from PIL import ImageGrab
from datetime import datetime

def take_screenshot():
    # Load settings
    settings_file = os.path.join(os.path.dirname(__file__), 'GlorpSettings.json')
    
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                area_coords = settings.get('area_coords', {'x': 100, 'y': 100, 'width': 300, 'height': 200})
        else:
            print("GlorpSettings.json not found. Using default area.")
            area_coords = {'x': 100, 'y': 100, 'width': 300, 'height': 200}
        
        # Wait 1 second
        print("Waiting 1 second before taking screenshot...")
        time.sleep(1)
        
        # Calculate bounding box (left, top, right, bottom)
        x = area_coords['x']
        y = area_coords['y']
        width = area_coords['width']
        height = area_coords['height']
        
        bbox = (x, y, x + width, y + height)
        
        # Take screenshot of the specified area
        print(f"Taking screenshot of area: x={x}, y={y}, width={width}, height={height}")
        screenshot = ImageGrab.grab(bbox=bbox)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        
        print(f"Screenshot saved as: {filename}")
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")

if __name__ == "__main__":
    take_screenshot()
